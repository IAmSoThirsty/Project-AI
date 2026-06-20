"""Append-only, hash-chained event spine with deterministic timestamp injection."""

from __future__ import annotations

import hashlib
import json
import threading
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from types import MappingProxyType

from kernel.types import JsonValue

GENESIS_HASH = "0" * 64


@dataclass(frozen=True)
class Event:
    sequence: int
    event_type: str
    payload: Mapping[str, JsonValue]
    timestamp: str
    previous_hash: str
    event_hash: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


def _hash_event(
    sequence: int,
    event_type: str,
    payload: Mapping[str, JsonValue],
    timestamp: str,
    previous_hash: str,
) -> str:
    content = json.dumps(
        {
            "event_type": event_type,
            "payload": dict(payload),
            "previous_hash": previous_hash,
            "sequence": sequence,
            "timestamp": timestamp,
        },
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return hashlib.sha256(content).hexdigest()


class EventSpine:
    def __init__(self, clock: Callable[[], datetime] | None = None) -> None:
        self._clock = clock or (lambda: datetime.now(UTC))
        self._events: list[Event] = []
        self._lock = threading.Lock()

    def append(self, event_type: str, payload: Mapping[str, JsonValue]) -> Event:
        return self.append_at(event_type, payload, self._clock())

    def append_at(
        self,
        event_type: str,
        payload: Mapping[str, JsonValue],
        timestamp: datetime,
    ) -> Event:
        if not event_type.strip():
            raise ValueError("event_type must not be empty")
        with self._lock:
            sequence = len(self._events) + 1
            previous = self._events[-1].event_hash if self._events else GENESIS_HASH
            normalized_time = timestamp.astimezone(UTC).isoformat()
            event = Event(
                sequence=sequence,
                event_type=event_type,
                payload=dict(payload),
                timestamp=normalized_time,
                previous_hash=previous,
                event_hash=_hash_event(sequence, event_type, payload, normalized_time, previous),
            )
            self._events.append(event)
            return event

    def events(self) -> tuple[Event, ...]:
        with self._lock:
            return tuple(self._events)
