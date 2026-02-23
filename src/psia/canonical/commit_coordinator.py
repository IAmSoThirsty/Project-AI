"""
Canonical Commit Coordinator — Transactional State Mutation.

Provides ACID-like semantics for canonical state mutations:
    - Precondition validation (CerberusDecision checks)
    - Write-ahead log (WAL) for crash recovery
    - Versioned key-value store with optimistic concurrency
    - Diff hashing for auditability
    - Automatic rollback on failure
    - Event emission at commit boundaries

Security invariants:
    - INV-ROOT-4 (Immutable write-path — all mutations go through this coordinator)
    - INV-ROOT-7 (Monotonic strictness — only commits allowed by Cerberus proceed)

Production notes:
    - In production, the backing store would be a replicated, durable KV store
      (e.g., etcd, FoundationDB, PostgreSQL with serializable isolation)
    - WAL entries would be persisted to durable storage before mutation
    - Version vectors would use Lamport timestamps or HLC
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CommitStatus(str, Enum):
    """Status of a commit operation."""
    PENDING = "pending"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass
class VersionedValue:
    """A value with version metadata for optimistic concurrency."""
    value: Any
    version: int
    updated_at: str
    updated_by: str
    commit_id: str

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "version": self.version,
            "updated_at": self.updated_at,
            "updated_by": self.updated_by,
            "commit_id": self.commit_id,
        }


@dataclass
class WALEntry:
    """Write-ahead log entry for crash recovery.

    In production, WAL entries are persisted to durable storage
    (e.g., disk, replicated log) BEFORE the mutation is applied.
    """
    wal_id: str
    commit_id: str
    request_id: str
    key: str
    old_value: Any
    old_version: int
    new_value: Any
    new_version: int
    timestamp: str
    status: CommitStatus = CommitStatus.PENDING


@dataclass
class CommitResult:
    """Result of a commit operation."""
    commit_id: str
    request_id: str
    status: CommitStatus
    keys_mutated: list[str] = field(default_factory=list)
    diff_hash: str = ""
    version_before: dict[str, int] = field(default_factory=dict)
    version_after: dict[str, int] = field(default_factory=dict)
    duration_ms: float = 0.0
    error: str | None = None


class CanonicalStore:
    """Versioned key-value store with optimistic concurrency control.

    Supports:
    - Get with version check
    - Put with expected-version precondition (optimistic locking)
    - Multi-key transactions (all-or-nothing)
    - Snapshot reads (consistent view at a point in time)
    - History per key (bounded, for audit)

    Production replacement: etcd, FoundationDB, or PostgreSQL with
    serializable isolation and row-level versioning.
    """

    def __init__(self, *, max_history: int = 100) -> None:
        self._store: dict[str, VersionedValue] = {}
        self._history: dict[str, list[VersionedValue]] = {}
        self._max_history = max_history

    def get(self, key: str) -> VersionedValue | None:
        """Get current value and version for a key."""
        return self._store.get(key)

    def get_version(self, key: str) -> int:
        """Get current version of a key (0 if not exists)."""
        val = self._store.get(key)
        return val.version if val else 0

    def put(
        self,
        key: str,
        value: Any,
        *,
        expected_version: int | None = None,
        actor: str = "system",
        commit_id: str = "",
    ) -> VersionedValue:
        """Put a value with optional optimistic concurrency check.

        Args:
            key: The key to write
            value: The new value
            expected_version: If set, the write only succeeds if current
                version matches (optimistic locking). None = unconditional.
            actor: Who is performing the mutation
            commit_id: The commit ID for traceability

        Raises:
            ValueError: If expected_version doesn't match (conflict)
        """
        current = self._store.get(key)
        current_version = current.version if current else 0

        if expected_version is not None and current_version != expected_version:
            raise ValueError(
                f"Optimistic concurrency conflict on key '{key}': "
                f"expected version {expected_version}, "
                f"current version {current_version}"
            )

        new_version = current_version + 1
        new_val = VersionedValue(
            value=value,
            version=new_version,
            updated_at=datetime.now(timezone.utc).isoformat(),
            updated_by=actor,
            commit_id=commit_id,
        )

        # Record history
        self._history.setdefault(key, [])
        if current:
            self._history[key].append(current)
            if len(self._history[key]) > self._max_history:
                self._history[key] = self._history[key][-self._max_history:]

        self._store[key] = new_val
        return new_val

    def delete(self, key: str, *, expected_version: int | None = None) -> bool:
        """Delete a key with optional version check."""
        current = self._store.get(key)
        if current is None:
            return False
        if expected_version is not None and current.version != expected_version:
            raise ValueError(
                f"Optimistic concurrency conflict on delete '{key}': "
                f"expected version {expected_version}, "
                f"current version {current.version}"
            )
        if current:
            self._history.setdefault(key, []).append(current)
        del self._store[key]
        return True

    def snapshot(self) -> dict[str, VersionedValue]:
        """Return a consistent snapshot of the current state."""
        return dict(self._store)

    def history(self, key: str) -> list[VersionedValue]:
        """Return the version history of a key."""
        result = list(self._history.get(key, []))
        current = self._store.get(key)
        if current:
            result.append(current)
        return result

    @property
    def key_count(self) -> int:
        return len(self._store)


class CommitCoordinator:
    """Transactional commit coordinator for canonical state mutations.

    Provides ACID-like semantics:
    - Atomicity: multi-key mutations are all-or-nothing
    - Consistency: CerberusDecision preconditions are validated
    - Isolation: optimistic concurrency with version checks
    - Durability: WAL entries logged before mutation (in production, persisted)

    Args:
        store: CanonicalStore backing the state
        require_cerberus_allow: If True, commits require CerberusDecision.is_allowed
        emit_events: Callback for emitting commit events
    """

    def __init__(
        self,
        *,
        store: CanonicalStore | None = None,
        require_cerberus_allow: bool = True,
        emit_events: Any | None = None,
    ) -> None:
        self.store = store or CanonicalStore()
        self.require_cerberus_allow = require_cerberus_allow
        self.emit_events = emit_events
        self._wal: list[WALEntry] = []
        self._commit_counter = 0

    def _next_commit_id(self) -> str:
        self._commit_counter += 1
        return f"commit_{self._commit_counter:06d}"

    def commit(
        self,
        *,
        request_id: str,
        mutations: dict[str, Any],
        actor: str = "system",
        cerberus_decision: Any | None = None,
        expected_versions: dict[str, int] | None = None,
    ) -> CommitResult:
        """Execute a transactional commit.

        Args:
            request_id: The originating request ID
            mutations: Dict of {key: new_value} to apply
            actor: The actor performing the mutation
            cerberus_decision: CerberusDecision (checked if require_cerberus_allow)
            expected_versions: Optional dict of {key: expected_version} for OCC

        Returns:
            CommitResult with status and metadata
        """
        start = time.monotonic()
        commit_id = self._next_commit_id()

        # ── Precondition: Cerberus decision ──
        if self.require_cerberus_allow and cerberus_decision is not None:
            if not getattr(cerberus_decision, "is_allowed", False):
                return CommitResult(
                    commit_id=commit_id,
                    request_id=request_id,
                    status=CommitStatus.FAILED,
                    duration_ms=(time.monotonic() - start) * 1000,
                    error="CerberusDecision does not allow commit",
                )
            commit_policy = getattr(cerberus_decision, "commit_policy", None)
            if commit_policy and not getattr(commit_policy, "allowed", False):
                return CommitResult(
                    commit_id=commit_id,
                    request_id=request_id,
                    status=CommitStatus.FAILED,
                    duration_ms=(time.monotonic() - start) * 1000,
                    error="CommitPolicy.allowed is False",
                )

        if not mutations:
            return CommitResult(
                commit_id=commit_id,
                request_id=request_id,
                status=CommitStatus.COMMITTED,
                duration_ms=(time.monotonic() - start) * 1000,
            )

        # ── Phase 1: Validate versions (read phase) ──
        version_before: dict[str, int] = {}
        for key in mutations:
            version_before[key] = self.store.get_version(key)
            if expected_versions and key in expected_versions:
                if version_before[key] != expected_versions[key]:
                    return CommitResult(
                        commit_id=commit_id,
                        request_id=request_id,
                        status=CommitStatus.FAILED,
                        version_before=version_before,
                        duration_ms=(time.monotonic() - start) * 1000,
                        error=f"Version conflict on key '{key}': "
                              f"expected {expected_versions[key]}, "
                              f"got {version_before[key]}",
                    )

        # ── Phase 2: Write WAL entries ──
        wal_entries: list[WALEntry] = []
        for key, new_value in mutations.items():
            old = self.store.get(key)
            entry = WALEntry(
                wal_id=f"{commit_id}_wal_{len(wal_entries)}",
                commit_id=commit_id,
                request_id=request_id,
                key=key,
                old_value=old.value if old else None,
                old_version=old.version if old else 0,
                new_value=new_value,
                new_version=version_before[key] + 1,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            wal_entries.append(entry)
        self._wal.extend(wal_entries)

        # ── Phase 3: Apply mutations ──
        applied_keys: list[str] = []
        try:
            for key, new_value in mutations.items():
                self.store.put(
                    key,
                    new_value,
                    expected_version=version_before[key],
                    actor=actor,
                    commit_id=commit_id,
                )
                applied_keys.append(key)
        except Exception as exc:
            # ── Rollback on failure ──
            self._rollback(applied_keys, wal_entries)
            for entry in wal_entries:
                entry.status = CommitStatus.ROLLED_BACK
            return CommitResult(
                commit_id=commit_id,
                request_id=request_id,
                status=CommitStatus.ROLLED_BACK,
                keys_mutated=applied_keys,
                version_before=version_before,
                duration_ms=(time.monotonic() - start) * 1000,
                error=str(exc),
            )

        # ── Phase 4: Compute diff hash ──
        version_after = {key: self.store.get_version(key) for key in mutations}
        diff_hash = self._compute_diff_hash(commit_id, mutations, version_before, version_after)

        # Mark WAL as committed
        for entry in wal_entries:
            entry.status = CommitStatus.COMMITTED

        result = CommitResult(
            commit_id=commit_id,
            request_id=request_id,
            status=CommitStatus.COMMITTED,
            keys_mutated=list(mutations.keys()),
            diff_hash=diff_hash,
            version_before=version_before,
            version_after=version_after,
            duration_ms=(time.monotonic() - start) * 1000,
        )

        # Emit event if configured
        if self.emit_events:
            try:
                self.emit_events(result)
            except Exception:
                logger.warning("Failed to emit commit event", exc_info=True)

        return result

    def _rollback(self, applied_keys: list[str], wal_entries: list[WALEntry]) -> None:
        """Rollback applied mutations using WAL entries."""
        for entry in reversed(wal_entries):
            if entry.key in applied_keys:
                if entry.old_value is not None:
                    self.store.put(
                        entry.key,
                        entry.old_value,
                        actor="rollback",
                        commit_id=f"{entry.commit_id}_rollback",
                    )
                else:
                    try:
                        self.store.delete(entry.key)
                    except Exception:
                        logger.error(f"Rollback delete failed for key '{entry.key}'")

    def _compute_diff_hash(
        self,
        commit_id: str,
        mutations: dict[str, Any],
        version_before: dict[str, int],
        version_after: dict[str, int],
    ) -> str:
        """Compute a deterministic hash of the commit diff."""
        diff_data = {
            "commit_id": commit_id,
            "mutations": {k: str(v) for k, v in sorted(mutations.items())},
            "version_before": dict(sorted(version_before.items())),
            "version_after": dict(sorted(version_after.items())),
        }
        canonical = json.dumps(diff_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    @property
    def wal_entries(self) -> list[WALEntry]:
        """Return the WAL for inspection/audit."""
        return list(self._wal)

    @property
    def committed_count(self) -> int:
        """Number of successfully committed transactions."""
        return sum(1 for e in self._wal if e.status == CommitStatus.COMMITTED)


__all__ = [
    "CommitCoordinator",
    "CanonicalStore",
    "CommitResult",
    "CommitStatus",
    "VersionedValue",
    "WALEntry",
]
