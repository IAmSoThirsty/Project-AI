"""Repo-wide SAFE-HALT controller: monotonic write-block with authorized recovery.

Implements PSIA v1 §8.3 (SafeHaltController). An emergency stop that blocks
every write (each actuation routed through ``execution.ExecutionGate``) while
allowing reads, cleared only by an authorized manual ``reset()``. Every halt and
reset is recorded to the injected ``EventSpine`` (single audit chain) and to an
in-process history so the halt/reset trail is auditable.

Architectural invariants (AGENTS.md):
- Downward-only deps: imports only ``kernel.event_spine`` / ``kernel.types`` + stdlib.
- Fail-closed: ``reset`` requires a non-blank authorizing identity; a blank one
  raises ``SafeHaltError`` — never a silent clear.
- Monotonic: once halted, writes stay blocked until ``reset()``; re-triggering
  keeps the system halted and retains the original (active) halt.
- Deterministic: timestamps via an injectable clock; thread-safe via a lock.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from kernel.event_spine import EventSpine
from kernel.types import JsonValue

HALT_ENTERED_EVENT = "system.safe_halt.entered"
HALT_EXITED_EVENT = "system.safe_halt.exited"


class HaltReason(StrEnum):
    """Why the system entered SAFE-HALT (PSIA §8.3 reason table)."""

    INVARIANT_VIOLATION = "INVARIANT_VIOLATION"
    UNRECOVERABLE_ERROR = "UNRECOVERABLE_ERROR"
    ADMINISTRATIVE = "ADMINISTRATIVE"
    SECURITY_INCIDENT = "SECURITY_INCIDENT"
    CHAIN_CORRUPTION = "CHAIN_CORRUPTION"
    KEY_COMPROMISE = "KEY_COMPROMISE"


class SafeHaltError(RuntimeError):
    """Raised when a write is attempted while the system is in SAFE-HALT.

    Also raised by ``reset`` when the authorizing identity is blank (fail-closed).
    """


@dataclass(frozen=True)
class HaltEvent:
    """One halt or reset transition in the controller's history.

    ``kind`` is ``"entered"`` (a halt) or ``"exited"`` (a reset). ``reason`` is
    ``None`` for an ``"exited"`` event.
    """

    sequence: int
    kind: str
    reason: HaltReason | None
    details: str
    triggered_by: str
    timestamp: str  # ISO-8601 UTC


class SafeHaltController:
    """Monotonic write-block with authorized recovery (PSIA §8.3).

    Writes are gated by ``check_write_allowed`` (raises when halted); reads always
    pass via ``check_read_allowed``. The halt is cleared only by ``reset`` with a
    non-blank authorizing identity. When an ``EventSpine`` is injected, entering
    and exiting SAFE-HALT append ``system.safe_halt.entered`` / ``.exited`` to the
    single audit chain.
    """

    def __init__(
        self,
        node_id: str,
        *,
        events: EventSpine | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not node_id.strip():
            raise ValueError("node_id must not be empty")
        self._node_id = node_id
        self._events = events
        self._clock = clock or (lambda: datetime.now(UTC))
        self._lock = threading.Lock()
        self._active: HaltEvent | None = None
        self._history: list[HaltEvent] = []

    @property
    def node_id(self) -> str:
        return self._node_id

    @property
    def is_halted(self) -> bool:
        with self._lock:
            return self._active is not None

    @property
    def active_halt(self) -> HaltEvent | None:
        """The halt currently blocking writes, or ``None`` if not halted."""
        with self._lock:
            return self._active

    @property
    def history(self) -> tuple[HaltEvent, ...]:
        """Full ordered halt/reset trail (the in-process audit record)."""
        with self._lock:
            return tuple(self._history)

    def trigger_halt(self, reason: HaltReason, details: str, triggered_by: str) -> HaltEvent:
        """Enter SAFE-HALT. Monotonic: if already halted, records the trigger but
        keeps the original active halt in force. Returns the recorded event."""
        if not triggered_by.strip():
            raise ValueError("triggered_by must not be empty")
        with self._lock:
            already_halted = self._active is not None
            event = self._record("entered", reason, details, triggered_by)
            if not already_halted:
                self._active = event
        self._emit(HALT_ENTERED_EVENT, event, extra={"already_halted": already_halted})
        return event

    def check_write_allowed(self) -> None:
        """Raise ``SafeHaltError`` if the system is halted; otherwise return."""
        with self._lock:
            active = self._active
        if active is not None:
            raise SafeHaltError(
                f"{self._node_id} is in SAFE-HALT ({active.reason}): {active.details}"
            )

    def check_read_allowed(self) -> None:
        """Reads are always permitted, even in SAFE-HALT (read passthrough)."""

    def reset(self, authorized_by: str) -> bool:
        """Clear the halt and resume standard execution — the recovery sequence.

        Fail-closed: a blank ``authorized_by`` raises ``SafeHaltError``. Returns
        ``True`` when a halt was cleared, ``False`` if the system was not halted
        (idempotent). Emits ``system.safe_halt.exited`` when a halt is cleared.
        """
        if not authorized_by.strip():
            raise SafeHaltError("reset requires a non-blank authorizing identity")
        with self._lock:
            if self._active is None:
                return False
            prior = self._active
            event = self._record(
                "exited",
                None,
                f"cleared halt entered at seq {prior.sequence} ({prior.reason})",
                authorized_by,
            )
            self._active = None
        self._emit(HALT_EXITED_EVENT, event, extra={"cleared_sequence": prior.sequence})
        return True

    # -- internals -----------------------------------------------------------

    def _record(self, kind: str, reason: HaltReason | None, details: str, actor: str) -> HaltEvent:
        """Append a HaltEvent to history. Must be called while holding the lock."""
        event = HaltEvent(
            sequence=len(self._history) + 1,
            kind=kind,
            reason=reason,
            details=details,
            triggered_by=actor,
            timestamp=self._clock().astimezone(UTC).isoformat(),
        )
        self._history.append(event)
        return event

    def _emit(self, event_type: str, event: HaltEvent, *, extra: dict[str, JsonValue]) -> None:
        if self._events is None:
            return
        payload: dict[str, JsonValue] = {
            "node_id": self._node_id,
            "sequence": event.sequence,
            "kind": event.kind,
            "reason": event.reason.value if event.reason is not None else None,
            "details": event.details,
            "triggered_by": event.triggered_by,
            **extra,
        }
        self._events.append(event_type, payload)


__all__ = [
    "HALT_ENTERED_EVENT",
    "HALT_EXITED_EVENT",
    "HaltEvent",
    "HaltReason",
    "SafeHaltController",
    "SafeHaltError",
]
