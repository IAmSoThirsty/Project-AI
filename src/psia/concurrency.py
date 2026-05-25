"""PSIA linearizable canonical store — OCC, snapshot isolation, version vectors."""
from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class CommitOutcome(str, Enum):
    COMMITTED = "committed"
    CONFLICT = "conflict"
    ABORTED = "aborted"


@dataclass
class VersionedValue:
    value: Any
    version: int


@dataclass
class StateSnapshot:
    _data: dict[str, Any]          # key → raw value (frozen copy)
    _versions: dict[str, int]      # key → version at snapshot time

    def read(self, key: str) -> Any | None:
        return self._data.get(key)

    def version_of(self, key: str) -> int:
        return self._versions.get(key, 0)


@dataclass
class MutationIntent:
    request_id: str
    snapshot: StateSnapshot
    read_set: set[str]
    write_dict: dict[str, Any]


@dataclass
class CommitResult:
    outcome: CommitOutcome
    new_version: int = 0
    commit_hash: str = ""
    conflict_keys: list[str] = field(default_factory=list)
    error: str = ""


class LinearizableCanonicalStore:
    def __init__(self, max_retry: int = 3) -> None:
        self._max_retry = max_retry
        self._state: dict[str, VersionedValue] = {}
        self._global_version: int = 0
        self._lock = threading.Lock()
        self._commit_log: list[CommitResult] = []

    @property
    def global_version(self) -> int:
        return self._global_version

    @property
    def commit_log(self) -> list[CommitResult]:
        return list(self._commit_log)

    def create_snapshot(self) -> StateSnapshot:
        with self._lock:
            data = {k: v.value for k, v in self._state.items()}
            versions = {k: v.version for k, v in self._state.items()}
        return StateSnapshot(_data=data, _versions=versions)

    def read(self, key: str) -> VersionedValue | None:
        with self._lock:
            return self._state.get(key)

    def prepare_mutation(
        self,
        request_id: str,
        snapshot: StateSnapshot,
        read_set: set[str],
        write_dict: dict[str, Any],
    ) -> MutationIntent:
        return MutationIntent(
            request_id=request_id,
            snapshot=snapshot,
            read_set=read_set,
            write_dict=write_dict,
        )

    def commit(self, mutation: MutationIntent) -> CommitResult:
        with self._lock:
            # OCC: validate read-set
            conflict_keys = []
            for key in mutation.read_set:
                snap_ver = mutation.snapshot.version_of(key)
                live_ver = self._state[key].version if key in self._state else 0
                if live_ver != snap_ver:
                    conflict_keys.append(key)

            if conflict_keys:
                result = CommitResult(
                    outcome=CommitOutcome.CONFLICT,
                    conflict_keys=conflict_keys,
                )
                return result

            # Apply writes
            for key, value in mutation.write_dict.items():
                current_ver = self._state[key].version if key in self._state else 0
                self._state[key] = VersionedValue(value=value, version=current_ver + 1)

            self._global_version += 1

            commit_hash = hashlib.sha256(
                json.dumps(
                    {
                        "request_id": mutation.request_id,
                        "global_version": self._global_version,
                        "writes": {k: str(v) for k, v in mutation.write_dict.items()},
                    },
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()

            result = CommitResult(
                outcome=CommitOutcome.COMMITTED,
                new_version=self._global_version,
                commit_hash=commit_hash,
            )
            self._commit_log.append(result)
            return result

    def commit_with_retry(
        self,
        request_id: str,
        evaluate: Callable[[StateSnapshot], tuple[set, dict]],
        max_retries: int | None = None,
    ) -> CommitResult:
        attempts = max_retries if max_retries is not None else self._max_retry
        for _ in range(attempts + 1):
            snap = self.create_snapshot()
            read_set, write_dict = evaluate(snap)
            mutation = self.prepare_mutation(request_id, snap, read_set, write_dict)
            result = self.commit(mutation)
            if result.outcome == CommitOutcome.COMMITTED:
                return result
        return CommitResult(outcome=CommitOutcome.ABORTED)
