"""PSIA safe halt controller — halt trigger, write blocking, in-flight tracking."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class HaltReason(str, Enum):
    INVARIANT_VIOLATION = "invariant_violation"
    SECURITY_INCIDENT = "security_incident"
    ADMINISTRATIVE = "administrative"
    CHAIN_CORRUPTION = "chain_corruption"
    UNRECOVERABLE_ERROR = "unrecoverable_error"
    KEY_COMPROMISE = "key_compromise"


class SafeHaltError(RuntimeError):
    pass


@dataclass
class HaltEvent:
    reason: HaltReason
    details: str = ""
    triggered_by: str = ""
    in_flight_aborted: int = 0


class SafeHaltController:
    def __init__(
        self,
        node_id: str = "",
        on_halt: Callable[[HaltEvent], None] | None = None,
        on_reset: Callable[[], None] | None = None,
    ) -> None:
        self._node_id = node_id
        self._on_halt = on_halt
        self._on_reset = on_reset
        self._halted = False
        self._halt_events: list[HaltEvent] = []
        self._in_flight = 0

    @property
    def node_id(self) -> str:
        return self._node_id

    @property
    def is_halted(self) -> bool:
        return self._halted

    @property
    def halt_count(self) -> int:
        return len(self._halt_events)

    @property
    def in_flight_count(self) -> int:
        return self._in_flight

    @property
    def halt_events(self) -> list[HaltEvent]:
        return list(self._halt_events)

    def trigger_halt(
        self,
        reason: HaltReason,
        details: str = "",
        triggered_by: str = "",
    ) -> HaltEvent:
        aborted = self._in_flight
        self._in_flight = 0
        self._halted = True
        event = HaltEvent(
            reason=reason,
            details=details,
            triggered_by=triggered_by,
            in_flight_aborted=aborted,
        )
        self._halt_events.append(event)
        if self._on_halt is not None:
            self._on_halt(event)
        return event

    def check_write_allowed(self) -> None:
        if self._halted:
            raise SafeHaltError("SAFE-HALT: write operations are blocked")

    def check_read_allowed(self) -> None:
        pass

    def reset(self, authorized_by: str = "") -> bool:
        if not self._halted:
            return False
        self._halted = False
        if self._on_reset is not None:
            self._on_reset()
        return True

    def register_in_flight(self) -> None:
        self._in_flight += 1

    def complete_in_flight(self) -> None:
        if self._in_flight > 0:
            self._in_flight -= 1
