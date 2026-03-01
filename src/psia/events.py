"""
PSIA Event Taxonomy — structured, signed observability events.

Implements §8 of the PSIA v1.0 specification.

All PSIA operations emit structured events that are:
- Typed (30+ event types covering all planes and lifecycle phases)
- Linked to a trace and optional request
- Severity-classified
- Hashable for ledger anchoring
- Publishable via an in-memory event bus with subscriber registration
"""

from __future__ import annotations

import enum
import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

logger = logging.getLogger(__name__)


class EventType(str, enum.Enum):
    """Complete event taxonomy for PSIA observability."""

    # ── Waterfall lifecycle ───────────────────────────────
    WATERFALL_START = "waterfall.start"
    STAGE_ENTER = "waterfall.stage.enter"
    STAGE_EXIT = "waterfall.stage.exit"

    # ── Request decisions ─────────────────────────────────
    REQUEST_DENIED = "request.denied"
    REQUEST_ALLOWED = "request.allowed"
    REQUEST_QUARANTINED = "request.quarantined"

    # ── Shadow simulation ─────────────────────────────────
    SHADOW_JOB_STARTED = "shadow.job.started"
    SHADOW_JOB_COMPLETED = "shadow.job.completed"
    SHADOW_DETERMINISM_MISMATCH = "shadow.determinism.mismatch"
    SHADOW_INTEGRITY_EVENT = "shadow.integrity.event"

    # ── Cerberus gate ─────────────────────────────────────
    CERBERUS_VOTE_CAST = "cerberus.vote.cast"
    CERBERUS_DECISION_FINAL = "cerberus.decision.final"

    # ── Commit lifecycle ──────────────────────────────────
    COMMIT_STARTED = "commit.started"
    COMMIT_SUCCEEDED = "commit.succeeded"
    COMMIT_ROLLED_BACK = "commit.rolled_back"

    # ── Ledger ────────────────────────────────────────────
    LEDGER_APPEND_SUCCEEDED = "ledger.append.succeeded"
    LEDGER_APPEND_FAILED = "ledger.append.failed"
    ANCHOR_FAILED = "ledger.anchor.failed"
    BLOCK_SEALED = "ledger.block.sealed"

    # ── OctoReflex ────────────────────────────────────────
    OCTOREFLEX_TRIGGERED = "octoreflex.triggered"
    THROTTLE_APPLIED = "octoreflex.throttle.applied"
    PROCESS_FROZEN = "octoreflex.process.frozen"
    PROCESS_KILLED = "octoreflex.process.killed"

    # ── Identity / capability lifecycle ───────────────────
    KEY_ROTATED = "identity.key.rotated"
    IDENTITY_REVOKED = "identity.revoked"
    TOKEN_REVOKED = "capability.token.revoked"
    TOKEN_ISSUED = "capability.token.issued"

    # ── System mode ───────────────────────────────────────
    SAFE_HALT_ENTERED = "system.safe_halt.entered"
    SAFE_HALT_EXITED = "system.safe_halt.exited"

    # ── Governance evolution ──────────────────────────────
    PROPOSAL_SUBMITTED = "governance.proposal.submitted"
    PROPOSAL_APPROVED = "governance.proposal.approved"
    PROPOSAL_REJECTED = "governance.proposal.rejected"
    POLICY_ACTIVATED = "governance.policy.activated"
    POLICY_ROLLED_BACK = "governance.policy.rolled_back"

    # ── Behavioral analysis ───────────────────────────────
    BASELINE_UPDATED = "behavioral.baseline.updated"
    THREAT_FINGERPRINT_ADDED = "behavioral.threat.fingerprint.added"
    BEHAVIORAL_ANOMALY = "behavioral.anomaly"

    # ── Bootstrap ─────────────────────────────────────────
    GENESIS_ANCHOR_CREATED = "bootstrap.genesis.anchor.created"
    READINESS_GATE_PASSED = "bootstrap.readiness.gate.passed"
    NODE_JOINED = "bootstrap.node.joined"


class EventSeverity(str, enum.Enum):
    """Severity levels for PSIA events."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"


@dataclass(frozen=True)
class PSIAEvent:
    """A structured, hashable PSIA observability event.

    Every event is uniquely identified, linked to a trace, and includes
    artifact hashes for ledger anchoring.  Events are immutable once created.
    """

    event_id: str
    event_type: EventType
    trace_id: str
    request_id: str
    subject: str
    severity: EventSeverity
    timestamp: str
    payload: dict[str, Any] = field(default_factory=dict)
    artifact_hashes: dict[str, str] = field(default_factory=dict)

    def compute_hash(self) -> str:
        """Compute deterministic SHA-256 hash of the event."""
        body = {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "trace_id": self.trace_id,
            "request_id": self.request_id,
            "subject": self.subject,
            "severity": self.severity.value,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "artifact_hashes": self.artifact_hashes,
        }
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()


# Type alias for event subscribers
EventSubscriber = Callable[[PSIAEvent], None]


class EventBus:
    """In-memory pub/sub event bus for PSIA events.

    Subscribers register for specific event types or all events (wildcard).
    Events are delivered synchronously to all matching subscribers.
    All emitted events are retained in a ring buffer for replay/audit.

    Thread-safety: NOT thread-safe.  Production deployments should
    use a concurrent queue or external message broker.
    """

    def __init__(self, max_history: int = 10000) -> None:
        """Initialize the event bus.

        Args:
            max_history: Maximum number of events to retain in the ring buffer
        """
        self._subscribers: dict[EventType | None, list[EventSubscriber]] = {}
        self._history: list[PSIAEvent] = []
        self._max_history = max_history

    def subscribe(
        self,
        event_type: EventType | None,
        subscriber: EventSubscriber,
    ) -> None:
        """Register a subscriber for a specific event type.

        Args:
            event_type: Event type to subscribe to, or None for all events
            subscriber: Callable receiving PSIAEvent instances
        """
        self._subscribers.setdefault(event_type, []).append(subscriber)

    def unsubscribe(
        self,
        event_type: EventType | None,
        subscriber: EventSubscriber,
    ) -> None:
        """Remove a subscriber.

        Args:
            event_type: Event type to unsubscribe from
            subscriber: The subscriber callable to remove
        """
        subs = self._subscribers.get(event_type, [])
        if subscriber in subs:
            subs.remove(subscriber)

    def emit(self, event: PSIAEvent) -> None:
        """Emit an event to all matching subscribers.

        Delivers to:
        1. Subscribers registered for the specific event type
        2. Subscribers registered with event_type=None (wildcard)

        Failed subscriber calls are logged but do not prevent
        delivery to other subscribers.

        Args:
            event: The event to emit
        """
        # Retain in history (ring buffer)
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

        # Deliver to specific subscribers
        for subscriber in self._subscribers.get(event.event_type, []):
            try:
                subscriber(event)
            except Exception:
                logger.exception(
                    "Event subscriber failed: event=%s subscriber=%s",
                    event.event_type.value,
                    subscriber,
                )

        # Deliver to wildcard subscribers
        for subscriber in self._subscribers.get(None, []):
            try:
                subscriber(event)
            except Exception:
                logger.exception(
                    "Wildcard event subscriber failed: event=%s subscriber=%s",
                    event.event_type.value,
                    subscriber,
                )

    def drain(self, limit: int | None = None) -> list[PSIAEvent]:
        """Return and clear event history (or a slice of it).

        Args:
            limit: Maximum number of events to return (most recent).
                   None returns all.

        Returns:
            List of PSIAEvent instances in chronological order
        """
        if limit is not None:
            events = self._history[-limit:]
        else:
            events = list(self._history)
        self._history.clear()
        return events

    @property
    def history(self) -> list[PSIAEvent]:
        """Return a copy of the event history without clearing."""
        return list(self._history)

    @property
    def event_count(self) -> int:
        """Return the total number of events in history."""
        return len(self._history)


def create_event(
    event_type: EventType,
    *,
    trace_id: str = "",
    request_id: str = "",
    subject: str = "",
    severity: EventSeverity = EventSeverity.INFO,
    payload: dict[str, Any] | None = None,
    artifact_hashes: dict[str, str] | None = None,
) -> PSIAEvent:
    """Factory function for creating PSIA events with auto-generated ID and timestamp.

    Args:
        event_type: Type of event
        trace_id: Distributed trace ID
        request_id: Associated request ID (if applicable)
        subject: DID of the subject
        severity: Event severity
        payload: Event-specific payload
        artifact_hashes: Hash pointers to relevant artifacts

    Returns:
        A new PSIAEvent instance
    """
    return PSIAEvent(
        event_id=f"evt_{uuid.uuid4().hex[:16]}",
        event_type=event_type,
        trace_id=trace_id,
        request_id=request_id,
        subject=subject,
        severity=severity,
        timestamp=datetime.now(timezone.utc).isoformat(),
        payload=payload or {},
        artifact_hashes=artifact_hashes or {},
    )


__all__ = [
    "EventType",
    "EventSeverity",
    "PSIAEvent",
    "EventBus",
    "EventSubscriber",
    "create_event",
]
