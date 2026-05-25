"""PSIA canonical commit coordinator — OCC, WAL, Cerberus integration."""
from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


@dataclass
class VersionedValue:
    value: Any
    version: int


class CommitStatus(str, Enum):
    COMMITTED = "committed"
    FAILED = "failed"


@dataclass
class CommitResult:
    status: CommitStatus
    keys_mutated: list[str] = field(default_factory=list)
    diff_hash: str = ""
    version_after: dict[str, int] = field(default_factory=dict)
    error: str = ""


@dataclass
class WALEntry:
    key: str
    value: Any
    version_before: int
    version_after: int
    request_id: str


class CanonicalStore:
    def __init__(self) -> None:
        self._data: dict[str, VersionedValue] = {}
        self._history: dict[str, list[VersionedValue]] = {}
        self._lock = threading.Lock()

    @property
    def key_count(self) -> int:
        with self._lock:
            return len(self._data)

    def get_version(self, key: str) -> int:
        with self._lock:
            entry = self._data.get(key)
            return entry.version if entry else 0

    def get(self, key: str) -> VersionedValue | None:
        with self._lock:
            return self._data.get(key)

    def put(self, key: str, value: Any, expected_version: int | None = None) -> VersionedValue:
        with self._lock:
            current = self._data.get(key)
            current_ver = current.version if current else 0
            if expected_version is not None and current_ver != expected_version:
                raise ValueError(
                    f"Optimistic concurrency conflict on '{key}': "
                    f"expected v{expected_version}, current v{current_ver}"
                )
            new_ver = current_ver + 1
            vv = VersionedValue(value=value, version=new_ver)
            self._data[key] = vv
            if key not in self._history:
                self._history[key] = []
            self._history[key].append(vv)
            return vv

    def delete(self, key: str, expected_version: int | None = None) -> bool:
        with self._lock:
            if key not in self._data:
                return False
            if expected_version is not None and self._data[key].version != expected_version:
                raise ValueError(
                    f"Optimistic concurrency conflict on '{key}': "
                    f"expected v{expected_version}, current v{self._data[key].version}"
                )
            del self._data[key]
            return True

    def history(self, key: str) -> list[VersionedValue]:
        with self._lock:
            return list(self._history.get(key, []))

    def snapshot(self) -> dict[str, VersionedValue]:
        with self._lock:
            return dict(self._data)


class CommitCoordinator:
    def __init__(
        self,
        require_cerberus_allow: bool = True,
        emit_events: Callable[[CommitResult], None] | None = None,
        store: CanonicalStore | None = None,
    ) -> None:
        self._require_cerberus = require_cerberus_allow
        self._emit_events = emit_events
        self._store = store if store is not None else CanonicalStore()
        self._wal: list[WALEntry] = []

    @property
    def store(self) -> CanonicalStore:
        return self._store

    @property
    def wal_entries(self) -> list[WALEntry]:
        return list(self._wal)

    def commit(
        self,
        request_id: str,
        mutations: dict[str, Any],
        actor: str = "",
        expected_versions: dict[str, int] | None = None,
        cerberus_decision: Any | None = None,
    ) -> CommitResult:
        if self._require_cerberus and cerberus_decision is not None:
            if not cerberus_decision.is_allowed:
                return CommitResult(
                    status=CommitStatus.FAILED,
                    error="Cerberus does not allow this commit",
                )
            cp = getattr(cerberus_decision, "commit_policy", None)
            if cp is not None and not cp.allowed:
                return CommitResult(
                    status=CommitStatus.FAILED,
                    error="CommitPolicy denied this commit",
                )

        if expected_versions:
            for key, expected_ver in expected_versions.items():
                current_ver = self._store.get_version(key)
                if current_ver != expected_ver:
                    return CommitResult(
                        status=CommitStatus.FAILED,
                        error=f"Version conflict on '{key}': expected v{expected_ver}, current v{current_ver}",
                    )

        keys_mutated = []
        version_after: dict[str, int] = {}
        wal_entries_new: list[WALEntry] = []

        for key, value in mutations.items():
            ver_before = self._store.get_version(key)
            vv = self._store.put(key, value)
            keys_mutated.append(key)
            version_after[key] = vv.version
            wal_entries_new.append(WALEntry(
                key=key,
                value=value,
                version_before=ver_before,
                version_after=vv.version,
                request_id=request_id,
            ))

        self._wal.extend(wal_entries_new)

        diff_hash = hashlib.sha256(
            json.dumps(
                {
                    "request_id": request_id,
                    "mutations": {k: str(v) for k, v in mutations.items()},
                    "version_after": version_after,
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()

        result = CommitResult(
            status=CommitStatus.COMMITTED,
            keys_mutated=keys_mutated,
            diff_hash=diff_hash,
            version_after=version_after,
        )
        if self._emit_events is not None:
            self._emit_events(result)
        return result
