"""PSIA event bus — typed events, publish/subscribe, drain."""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class EventType(str, Enum):
    WATERFALL_START = "waterfall_start"
    WATERFALL_END = "waterfall_end"
    STAGE_ENTER = "stage_enter"
    STAGE_EXIT = "stage_exit"
    COMMIT_SUCCEEDED = "commit_succeeded"
    COMMIT_FAILED = "commit_failed"
    CIRCUIT_OPENED = "circuit_opened"
    CASCADE_DETECTED = "cascade_detected"
    INVARIANT_VIOLATED = "invariant_violated"
    REQUEST_DENIED = "request_denied"
    REQUEST_ALLOWED = "request_allowed"


@dataclass
class PSIAEvent:
    event_id: str
    event_type: EventType
    timestamp: float
    payload: dict[str, Any] = field(default_factory=dict)

    def compute_hash(self) -> str:
        d = {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }
        return hashlib.sha256(
            json.dumps(d, sort_keys=True, default=str).encode()
        ).hexdigest()


def create_event(event_type: EventType, **kwargs: Any) -> PSIAEvent:
    return PSIAEvent(
        event_id=uuid.uuid4().hex,
        event_type=event_type,
        timestamp=time.monotonic(),
        payload=kwargs,
    )


class EventBus:
    def __init__(self) -> None:
        self._events: list[PSIAEvent] = []
        self._subscribers: list[tuple[EventType | None, Callable[[PSIAEvent], None]]] = []

    def subscribe(
        self,
        event_type: EventType | None,
        handler: Callable[[PSIAEvent], None],
    ) -> None:
        self._subscribers.append((event_type, handler))

    def emit(self, event: PSIAEvent) -> None:
        self._events.append(event)
        for et, handler in self._subscribers:
            if et is None or et == event.event_type:
                handler(event)

    def drain(self) -> list[PSIAEvent]:
        events = list(self._events)
        self._events.clear()
        return events

    @property
    def event_count(self) -> int:
        return len(self._events)
