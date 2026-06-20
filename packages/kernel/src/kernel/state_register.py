"""Revisioned state register with integrity-checked restoration."""

from __future__ import annotations

import hashlib
import json
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from kernel.types import JsonValue


class RevisionConflictError(RuntimeError):
    pass


@dataclass(frozen=True)
class StateSnapshot:
    revision: int
    values: Mapping[str, JsonValue]
    state_sha256: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))


def _state_hash(revision: int, values: Mapping[str, JsonValue]) -> str:
    content = json.dumps(
        {"revision": revision, "values": dict(values)},
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return hashlib.sha256(content).hexdigest()


class StateRegister:
    def __init__(self, initial: Mapping[str, JsonValue] | None = None) -> None:
        self._revision = 0
        self._values = dict(initial or {})
        self._lock = threading.Lock()

    def snapshot(self) -> StateSnapshot:
        with self._lock:
            values = dict(self._values)
            return StateSnapshot(self._revision, values, _state_hash(self._revision, values))

    def update(
        self,
        changes: Mapping[str, JsonValue],
        *,
        expected_revision: int,
    ) -> StateSnapshot:
        with self._lock:
            if expected_revision != self._revision:
                raise RevisionConflictError(
                    f"expected revision {expected_revision}, current revision {self._revision}"
                )
            self._values.update(changes)
            self._revision += 1
            values = dict(self._values)
            return StateSnapshot(self._revision, values, _state_hash(self._revision, values))

    def restore(self, snapshot: StateSnapshot) -> None:
        if snapshot.state_sha256 != _state_hash(snapshot.revision, snapshot.values):
            raise ValueError("state snapshot hash mismatch")
        with self._lock:
            self._revision = snapshot.revision
            self._values = dict(snapshot.values)
