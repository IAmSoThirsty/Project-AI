"""
SAFE-HALT Controller — Emergency Shutdown and Read-Only Mode.

Manages the transition of a PSIA node into SAFE-HALT mode when:
    - A critical invariant violation is detected
    - An unrecoverable error occurs
    - An administrative halt is requested
    - A security incident triggers automated shutdown

In SAFE-HALT mode:
    - All write operations are rejected
    - Read operations continue (for forensic analysis)
    - The ledger is sealed with a HALT anchor
    - Audit events are emitted
    - Recovery requires manual intervention (re-genesis or rollback)

Security invariants:
    - SAFE-HALT is monotonic: once entered, only manual intervention can restore
    - The halt reason and trigger are permanently recorded in the ledger
    - All in-flight transactions are aborted

Production notes:
    - In production, SAFE-HALT would:
      - Send alerts to PagerDuty/OpsGenie
      - Emit SNMP traps or CloudWatch alarms
      - Drain connections gracefully before halting writes
      - Notify peer nodes of the halt via gossip protocol
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


class HaltReason(str, Enum):
    """Reason for entering SAFE-HALT mode."""
    INVARIANT_VIOLATION = "invariant_violation"
    UNRECOVERABLE_ERROR = "unrecoverable_error"
    ADMINISTRATIVE = "administrative"
    SECURITY_INCIDENT = "security_incident"
    CHAIN_CORRUPTION = "chain_corruption"
    KEY_COMPROMISE = "key_compromise"


@dataclass
class HaltEvent:
    """Record of a SAFE-HALT transition."""
    reason: HaltReason
    details: str
    triggered_by: str
    timestamp: str
    halt_anchor_hash: str = ""
    in_flight_aborted: int = 0


class SafeHaltController:
    """Controls SAFE-HALT mode transitions for a PSIA node.

    Once SAFE-HALT is activated:
    - `is_halted` returns True
    - `check_write_allowed()` raises SafeHaltError
    - `check_read_allowed()` succeeds (reads are always allowed)
    - The halt is permanent until manual `reset()` is called

    Args:
        node_id: This node's identifier
        on_halt: Optional callback invoked when halt is triggered
        on_reset: Optional callback invoked on manual reset
    """

    def __init__(
        self,
        *,
        node_id: str = "psia-node-01",
        on_halt: Callable[[HaltEvent], None] | None = None,
        on_reset: Callable[[], None] | None = None,
    ) -> None:
        self.node_id = node_id
        self.on_halt = on_halt
        self.on_reset = on_reset
        self._halted = False
        self._halt_events: list[HaltEvent] = []
        self._in_flight_count = 0

    def trigger_halt(
        self,
        reason: HaltReason,
        *,
        details: str = "",
        triggered_by: str = "system",
    ) -> HaltEvent:
        """Trigger SAFE-HALT mode.

        This is idempotent — calling it when already halted adds
        a new event to the audit trail but does not change state.

        Args:
            reason: The reason for the halt
            details: Human-readable details
            triggered_by: The component/actor triggering the halt

        Returns:
            HaltEvent record
        """
        now = datetime.now(timezone.utc).isoformat()

        event = HaltEvent(
            reason=reason,
            details=details,
            triggered_by=triggered_by,
            timestamp=now,
            in_flight_aborted=self._in_flight_count,
        )

        if not self._halted:
            self._halted = True
            logger.critical(
                "SAFE-HALT triggered on node %s: reason=%s details=%s",
                self.node_id, reason.value, details,
            )

        self._halt_events.append(event)
        self._in_flight_count = 0

        if self.on_halt:
            try:
                self.on_halt(event)
            except Exception:
                logger.error("on_halt callback failed", exc_info=True)

        return event

    def check_write_allowed(self) -> None:
        """Check if write operations are allowed.

        Raises:
            SafeHaltError: If the node is in SAFE-HALT mode
        """
        if self._halted:
            last = self._halt_events[-1] if self._halt_events else None
            raise SafeHaltError(
                f"Node {self.node_id} is in SAFE-HALT mode. "
                f"Reason: {last.reason.value if last else 'unknown'}. "
                f"Writes are blocked."
            )

    def check_read_allowed(self) -> None:
        """Check if read operations are allowed.

        Reads are always allowed, even in SAFE-HALT mode.
        This method is provided for interface consistency.
        """
        pass  # Reads always allowed

    def register_in_flight(self) -> None:
        """Register an in-flight transaction (for abort counting)."""
        self._in_flight_count += 1

    def complete_in_flight(self) -> None:
        """Mark an in-flight transaction as completed."""
        if self._in_flight_count > 0:
            self._in_flight_count -= 1

    def reset(self, *, authorized_by: str = "admin") -> bool:
        """Manually reset from SAFE-HALT mode.

        This is an administrative action that resets the halt state.
        In production, this would require multi-party authorization.

        Args:
            authorized_by: Who authorized the reset

        Returns:
            True if the reset was successful
        """
        if not self._halted:
            return False

        logger.warning(
            "SAFE-HALT reset on node %s by %s",
            self.node_id, authorized_by,
        )
        self._halted = False

        if self.on_reset:
            try:
                self.on_reset()
            except Exception:
                logger.error("on_reset callback failed", exc_info=True)

        return True

    @property
    def is_halted(self) -> bool:
        return self._halted

    @property
    def halt_events(self) -> list[HaltEvent]:
        return list(self._halt_events)

    @property
    def halt_count(self) -> int:
        return len(self._halt_events)

    @property
    def in_flight_count(self) -> int:
        return self._in_flight_count


class SafeHaltError(Exception):
    """Raised when a write operation is attempted in SAFE-HALT mode."""
    pass


__all__ = [
    "SafeHaltController",
    "SafeHaltError",
    "HaltEvent",
    "HaltReason",
]
