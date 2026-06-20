"""Deterministic verification and reconstruction of event chains."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from kernel.event_spine import GENESIS_HASH, Event, EventSpine, _hash_event


@dataclass(frozen=True)
class ReplayResult:
    valid: bool
    events_replayed: int
    error: str | None = None


def verify_event_chain(events: tuple[Event, ...]) -> ReplayResult:
    previous = GENESIS_HASH
    for expected_sequence, event in enumerate(events, start=1):
        if event.sequence != expected_sequence:
            return ReplayResult(False, expected_sequence - 1, "sequence mismatch")
        if event.previous_hash != previous:
            return ReplayResult(False, expected_sequence - 1, "previous hash mismatch")
        expected_hash = _hash_event(
            event.sequence,
            event.event_type,
            event.payload,
            event.timestamp,
            event.previous_hash,
        )
        if event.event_hash != expected_hash:
            return ReplayResult(False, expected_sequence - 1, "event hash mismatch")
        previous = event.event_hash
    return ReplayResult(True, len(events))


def replay(events: tuple[Event, ...]) -> tuple[EventSpine, ReplayResult]:
    verification = verify_event_chain(events)
    spine = EventSpine()
    if not verification.valid:
        return spine, verification
    for event in events:
        spine.append_at(event.event_type, event.payload, datetime.fromisoformat(event.timestamp))
    return spine, verification
