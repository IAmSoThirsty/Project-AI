"""
atlas.audit — Immutable audit trail with hash chain (explanation chain).

Production-grade audit logging for all decisions affecting reality.
Implements the **explanation chain**:

- **Explain** — every record carries a rationale (level, category, actor,
  action, resource, outcome, evidence).
- **Prove** — every record is hash-chained via SHA-256 over canonical JSON.
  Tampering with any record invalidates the chain from that point.
- **Replay** — given the chain, every event is reconstructable from
  immutable records. verify_chain() returns detailed issues for audit.

SUBORDINATION: This module records decisions, it does not make them.
Each record includes the canonical SUBORDINATION_NOTICE field, bound
to the record hash so tampering invalidates the digest.

Architectural invariants (AGENTS.md v3):
- Downward-only deps: atlas imports only kernel + stdlib. No upward.
- Canonical types: kernel.JsonScalar, kernel.JsonValue for JSON.
- Fail-closed: AuditTrailError on invalid input.
- Pluggable seams: storage backend can be swapped (in-memory, JSONL).
- Deterministic: same events produce same hashes.
- Strict typing: mypy --strict clean.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol

from atlas.analysis import SUBORDINATION_NOTICE

logger = logging.getLogger(__name__)


class AuditTrailError(Exception):
    """Raised when audit trail operations fail."""


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class AuditLevel(StrEnum):
    """Audit event severity levels."""

    INFORMATIONAL = "informational"
    STANDARD = "standard"
    HIGH_PRIORITY = "high_priority"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AuditCategory(StrEnum):
    """Categories of audit events."""

    SYSTEM = "system"
    DATA = "data"
    GOVERNANCE = "governance"
    SECURITY = "security"
    OPERATION = "operation"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    STACK = "stack"


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AuditEvent:
    """Immutable audit event record.

    Attributes:
        sequence: Monotonic sequence number (0-indexed).
        timestamp: ISO 8601 UTC timestamp string.
        level: Severity level.
        category: Event category.
        actor: Subject that initiated the action (subject from capability).
        action: The operation identifier (e.g. 'atlas.projection.record').
        resource: The resource the action targeted.
        outcome: The decision outcome (e.g. 'ALLOW', 'DENY', 'INFO').
        rationale: Human-readable rationale for the decision.
        evidence: Dict of supporting evidence (e.g. rule_id, posterior).
        prev_hash: SHA-256 of the previous event (or genesis hash for #0).
        record_hash: SHA-256 of this event's canonical content.
        subordination_notice: Bound to record hash; tampering invalidates.
    """

    sequence: int
    timestamp: str
    level: AuditLevel
    category: AuditCategory
    actor: str
    action: str
    resource: str
    outcome: str
    rationale: str
    evidence: tuple[tuple[str, str], ...]
    prev_hash: str
    record_hash: str
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.sequence, int) or self.sequence < 0:
            raise AuditTrailError(f"sequence must be non-negative int, got {self.sequence!r}")
        if not isinstance(self.timestamp, str) or not self.timestamp.strip():
            raise AuditTrailError(f"timestamp must be non-empty string, got {self.timestamp!r}")
        # Validate ISO 8601 format
        try:
            datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise AuditTrailError(
                f"timestamp must be ISO 8601, got {self.timestamp!r}: {exc}"
            ) from exc
        if not isinstance(self.level, AuditLevel):
            raise AuditTrailError(f"level must be AuditLevel, got {type(self.level).__name__}")
        if not isinstance(self.category, AuditCategory):
            raise AuditTrailError(
                f"category must be AuditCategory, got {type(self.category).__name__}"
            )
        if not isinstance(self.actor, str) or not self.actor.strip():
            raise AuditTrailError(f"actor must be non-empty string, got {self.actor!r}")
        if not isinstance(self.action, str) or not self.action.strip():
            raise AuditTrailError(f"action must be non-empty string, got {self.action!r}")
        if not isinstance(self.resource, str) or not self.resource.strip():
            raise AuditTrailError(f"resource must be non-empty string, got {self.resource!r}")
        if not isinstance(self.outcome, str) or not self.outcome.strip():
            raise AuditTrailError(f"outcome must be non-empty string, got {self.outcome!r}")
        if not isinstance(self.rationale, str):
            raise AuditTrailError(f"rationale must be string, got {type(self.rationale).__name__}")
        if not isinstance(self.evidence, tuple):
            raise AuditTrailError(f"evidence must be tuple, got {type(self.evidence).__name__}")
        for i, item in enumerate(self.evidence):
            if not isinstance(item, tuple) or len(item) != 2:
                raise AuditTrailError(f"evidence[{i}] must be (str, str) tuple, got {item!r}")
            if not isinstance(item[0], str) or not isinstance(item[1], str):
                raise AuditTrailError(
                    f"evidence[{i}] must be (str, str), got ({type(item[0]).__name__}, "
                    f"{type(item[1]).__name__})"
                )
        for hash_name in ("prev_hash", "record_hash"):
            value = getattr(self, hash_name)
            if not isinstance(value, str) or len(value) != 64:
                raise AuditTrailError(f"{hash_name} must be 64-char hex, got {value!r}")
            for code in range(64):
                if value[code] not in "0123456789abcdef":
                    raise AuditTrailError(f"{hash_name} must be hex, got {value!r}")


@dataclass(frozen=True)
class AuditChainVerification:
    """Result of chain verification.

    Attributes:
        is_valid: True if chain passes integrity check.
        events_checked: Number of events verified.
        issues: Tuple of (event_index, reason) pairs describing any issues.
        subordination_notice: Bound to verification result.
    """

    is_valid: bool
    events_checked: int
    issues: tuple[tuple[int, str], ...]
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.is_valid, bool):
            raise AuditTrailError(f"is_valid must be bool, got {type(self.is_valid).__name__}")
        if not isinstance(self.events_checked, int) or self.events_checked < 0:
            raise AuditTrailError(
                f"events_checked must be non-negative int, got {self.events_checked!r}"
            )
        if not isinstance(self.issues, tuple):
            raise AuditTrailError(f"issues must be tuple, got {type(self.issues).__name__}")
        for i, issue in enumerate(self.issues):
            if not isinstance(issue, tuple) or len(issue) != 2:
                raise AuditTrailError(f"issues[{i}] must be (int, str) tuple, got {issue!r}")
            if not isinstance(issue[0], int) or not isinstance(issue[1], str):
                raise AuditTrailError(
                    f"issues[{i}] must be (int, str), got "
                    f"({type(issue[0]).__name__}, {type(issue[1]).__name__})"
                )


# ---------------------------------------------------------------------------
# Hash computation
# ---------------------------------------------------------------------------


GENESIS_HASH = "0" * 64


def _canonicalize(event_data: dict[str, Any]) -> str:
    """Produce canonical JSON for hash computation."""
    return json.dumps(event_data, sort_keys=True, separators=(",", ":"))


def compute_record_hash(
    sequence: int,
    timestamp: str,
    level: AuditLevel,
    category: AuditCategory,
    actor: str,
    action: str,
    resource: str,
    outcome: str,
    rationale: str,
    evidence: dict[str, str],
    prev_hash: str,
) -> str:
    """Compute the SHA-256 record hash for an event.

    The hash covers all fields except record_hash itself (which would be
    a circular dependency).
    """
    evidence_sorted = sorted(evidence.items())
    body: dict[str, Any] = {
        "sequence": sequence,
        "timestamp": timestamp,
        "level": level.value,
        "category": category.value,
        "actor": actor,
        "action": action,
        "resource": resource,
        "outcome": outcome,
        "rationale": rationale,
        "evidence": evidence_sorted,
        "prev_hash": prev_hash,
        "subordination_notice": SUBORDINATION_NOTICE,
    }
    return hashlib.sha256(_canonicalize(body).encode()).hexdigest()


# ---------------------------------------------------------------------------
# Storage backend Protocol
# ---------------------------------------------------------------------------


class StorageBackend(Protocol):
    """Pluggable storage backend for audit events."""

    def append(self, event: AuditEvent) -> None: ...

    def load(self) -> tuple[AuditEvent, ...]: ...


# ---------------------------------------------------------------------------
# In-memory storage backend
# ---------------------------------------------------------------------------


class InMemoryStorage:
    """In-memory storage backend (default)."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def append(self, event: AuditEvent) -> None:
        self._events.append(event)

    def load(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)


# ---------------------------------------------------------------------------
# JSONL storage backend
# ---------------------------------------------------------------------------


class JsonlStorage:
    """JSONL file storage backend (append-friendly, line-oriented)."""

    def __init__(self, path: Path) -> None:
        if not isinstance(path, Path):
            raise AuditTrailError(f"path must be Path, got {type(path).__name__}")
        self._path = path

    def append(self, event: AuditEvent) -> None:
        body: dict[str, Any] = {
            "sequence": event.sequence,
            "timestamp": event.timestamp,
            "level": event.level.value,
            "category": event.category.value,
            "actor": event.actor,
            "action": event.action,
            "resource": event.resource,
            "outcome": event.outcome,
            "rationale": event.rationale,
            "evidence": dict(event.evidence),
            "prev_hash": event.prev_hash,
            "record_hash": event.record_hash,
            "subordination_notice": event.subordination_notice,
        }
        line = json.dumps(body, sort_keys=True, separators=(",", ":"))
        with self._path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def load(self) -> tuple[AuditEvent, ...]:
        if not self._path.exists():
            return ()
        events: list[AuditEvent] = []
        with self._path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    body = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise AuditTrailError(f"failed to parse line {line_num}: {exc}") from exc
                evidence_dict = body.get("evidence", {})
                evidence_tuple = tuple(sorted(evidence_dict.items()))
                events.append(
                    AuditEvent(
                        sequence=body["sequence"],
                        timestamp=body["timestamp"],
                        level=AuditLevel(body["level"]),
                        category=AuditCategory(body["category"]),
                        actor=body["actor"],
                        action=body["action"],
                        resource=body["resource"],
                        outcome=body["outcome"],
                        rationale=body["rationale"],
                        evidence=evidence_tuple,
                        prev_hash=body["prev_hash"],
                        record_hash=body["record_hash"],
                        subordination_notice=body.get("subordination_notice", SUBORDINATION_NOTICE),
                    )
                )
        return tuple(events)


# ---------------------------------------------------------------------------
# AuditTrail
# ---------------------------------------------------------------------------


class AuditTrail:
    """Append-only audit ledger with hash chain.

    Each event links to the previous via prev_hash. verify_chain()
    walks the chain and reports any issues.

    Thread-safe: append and verify are guarded by a lock.
    """

    def __init__(
        self,
        storage: InMemoryStorage | JsonlStorage | None = None,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if storage is None:
            storage = InMemoryStorage()
        self._storage = storage
        self._lock = threading.Lock()
        self._clock = clock or (lambda: datetime.now(UTC))
        # Load existing events (so JSONL-backed trails pick up persisted state)
        self._events: list[AuditEvent] = list(storage.load())

    def __len__(self) -> int:
        return len(self._events)

    @property
    def events(self) -> tuple[AuditEvent, ...]:
        """Return all events as an immutable tuple (read-only view)."""
        with self._lock:
            return tuple(self._events)

    def append(
        self,
        *,
        level: AuditLevel | str,
        category: AuditCategory | str,
        actor: str,
        action: str,
        resource: str,
        outcome: str,
        rationale: str,
        evidence: dict[str, str] | None = None,
        timestamp: str | None = None,
    ) -> AuditEvent:
        """Append a new event to the chain.

        Returns the constructed event with computed prev_hash + record_hash.
        """
        # Coerce string enums
        if isinstance(level, str):
            try:
                level = AuditLevel(level)
            except ValueError as exc:
                raise AuditTrailError(
                    f"level must be AuditLevel or valid string, got {level!r}: {exc}"
                ) from exc
        if isinstance(category, str):
            try:
                category = AuditCategory(category)
            except ValueError as exc:
                raise AuditTrailError(
                    f"category must be AuditCategory or valid string, got {category!r}: {exc}"
                ) from exc

        if not isinstance(actor, str) or not actor.strip():
            raise AuditTrailError(f"actor must be non-empty string, got {actor!r}")
        if not isinstance(action, str) or not action.strip():
            raise AuditTrailError(f"action must be non-empty string, got {action!r}")
        if not isinstance(resource, str) or not resource.strip():
            raise AuditTrailError(f"resource must be non-empty string, got {resource!r}")
        if not isinstance(outcome, str) or not outcome.strip():
            raise AuditTrailError(f"outcome must be non-empty string, got {outcome!r}")
        if not isinstance(rationale, str):
            raise AuditTrailError(f"rationale must be string, got {type(rationale).__name__}")
        if evidence is not None and not isinstance(evidence, dict):
            raise AuditTrailError(f"evidence must be dict or None, got {type(evidence).__name__}")
        evidence_dict: dict[str, str] = evidence or {}

        # Validate evidence values
        for k, v in evidence_dict.items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise AuditTrailError(
                    f"evidence keys+values must be strings, "
                    f"got ({type(k).__name__}, {type(v).__name__})"
                )

        ts = timestamp if timestamp is not None else self._clock().isoformat()

        with self._lock:
            sequence = len(self._events)
            prev_hash = GENESIS_HASH if sequence == 0 else self._events[-1].record_hash
            record_hash = compute_record_hash(
                sequence=sequence,
                timestamp=ts,
                level=level,
                category=category,
                actor=actor,
                action=action,
                resource=resource,
                outcome=outcome,
                rationale=rationale,
                evidence=evidence_dict,
                prev_hash=prev_hash,
            )
            event = AuditEvent(
                sequence=sequence,
                timestamp=ts,
                level=level,
                category=category,
                actor=actor,
                action=action,
                resource=resource,
                outcome=outcome,
                rationale=rationale,
                evidence=tuple(sorted(evidence_dict.items())),
                prev_hash=prev_hash,
                record_hash=record_hash,
            )
            self._storage.append(event)
            self._events.append(event)
            return event

    def verify_chain(self) -> AuditChainVerification:
        """Walk the chain and verify each record hash + linkage.

        Returns:
            AuditChainVerification with is_valid + tuple of issues.
        """
        with self._lock:
            events = list(self._events)

        issues: list[tuple[int, str]] = []
        for i, event in enumerate(events):
            # Check prev_hash linkage
            expected_prev = GENESIS_HASH if i == 0 else events[i - 1].record_hash
            if event.prev_hash != expected_prev:
                issues.append(
                    (
                        i,
                        f"prev_hash mismatch: expected {expected_prev}, got {event.prev_hash}",
                    )
                )

            # Recompute record_hash and compare
            evidence_dict = dict(event.evidence)
            computed = compute_record_hash(
                sequence=event.sequence,
                timestamp=event.timestamp,
                level=event.level,
                category=event.category,
                actor=event.actor,
                action=event.action,
                resource=event.resource,
                outcome=event.outcome,
                rationale=event.rationale,
                evidence=evidence_dict,
                prev_hash=event.prev_hash,
            )
            if computed != event.record_hash:
                issues.append(
                    (
                        i,
                        f"record_hash mismatch: expected {computed}, got {event.record_hash}",
                    )
                )

            # Check sequence monotonicity
            if event.sequence != i:
                issues.append(
                    (
                        i,
                        f"sequence mismatch: expected {i}, got {event.sequence}",
                    )
                )

            # Check subordination notice
            if event.subordination_notice != SUBORDINATION_NOTICE:
                issues.append(
                    (i, f"subordination_notice tampered: got {event.subordination_notice!r}")
                )

        return AuditChainVerification(
            is_valid=len(issues) == 0,
            events_checked=len(events),
            issues=tuple(issues),
        )

    def save(self, path: Path) -> None:
        """Save current chain to JSONL file (overwrites existing)."""
        if not isinstance(path, Path):
            raise AuditTrailError(f"path must be Path, got {type(path).__name__}")
        with self._lock:
            events = list(self._events)
        # Write atomically: write to .tmp then rename
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            for event in events:
                body: dict[str, Any] = {
                    "sequence": event.sequence,
                    "timestamp": event.timestamp,
                    "level": event.level.value,
                    "category": event.category.value,
                    "actor": event.actor,
                    "action": event.action,
                    "resource": event.resource,
                    "outcome": event.outcome,
                    "rationale": event.rationale,
                    "evidence": dict(event.evidence),
                    "prev_hash": event.prev_hash,
                    "record_hash": event.record_hash,
                    "subordination_notice": event.subordination_notice,
                }
                line = json.dumps(body, sort_keys=True, separators=(",", ":"))
                f.write(line + "\n")
        tmp_path.replace(path)

    @classmethod
    def load(cls, path: Path) -> AuditTrail:
        """Load a chain from JSONL file."""
        if not isinstance(path, Path):
            raise AuditTrailError(f"path must be Path, got {type(path).__name__}")
        storage = JsonlStorage(path)
        return cls(storage=storage)

    def replay(self, callback: Callable[[AuditEvent], None]) -> int:
        """Replay each event in order via callback.

        Useful for reconstructing decision sequences without mutating
        the trail. Returns the number of events replayed.
        """
        if not callable(callback):
            raise AuditTrailError(f"callback must be callable, got {type(callback).__name__}")
        with self._lock:
            events = list(self._events)
        for event in events:
            callback(event)
        return len(events)


# ---------------------------------------------------------------------------
# Factory function
# ---------------------------------------------------------------------------


def get_audit_trail(
    storage: InMemoryStorage | JsonlStorage | None = None,
    *,
    clock: Callable[[], datetime] | None = None,
) -> AuditTrail:
    """Factory function for AuditTrail.

    Backward-compatible with legacy `atlas.audit.trail.get_audit_trail`.
    """
    return AuditTrail(storage=storage, clock=clock)


# ---------------------------------------------------------------------------
# Protocol definition (after classes for forward refs)
# ---------------------------------------------------------------------------


__all__ = [
    "GENESIS_HASH",
    "AuditCategory",
    "AuditChainVerification",
    "AuditEvent",
    "AuditLevel",
    "AuditTrail",
    "AuditTrailError",
    "InMemoryStorage",
    "JsonlStorage",
    "StorageBackend",
    "compute_record_hash",
    "get_audit_trail",
]
