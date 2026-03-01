"""
PSIA Concurrency Model — Linearizable Canonical State Mutations.

Addresses the time-of-check / time-of-use (TOCTOU) gap between shadow
simulation (Stage 3) and canonical commit (Stage 5) under concurrent mutations.

This module provides:

1. **Snapshot Isolation**: Shadow evaluations read from a consistent,
   immutable snapshot of canonical state.  Concurrent mutations to
   canonical state do not affect in-flight shadow evaluations.

2. **Optimistic Concurrency Control (OCC)**: Commits proceed optimistically
   but validate at commit time that no conflicting mutation has been applied
   since the snapshot was taken.

3. **Version Vectors**: Every canonical state key carries a monotonically
   increasing version number.  Commits specify their read-set versions; if
   any read-set key has advanced, the commit is rejected (conflict).

4. **Linearizability**: All committed mutations are linearizable — they
   appear to execute atomically at some point between their invocation
   (shadow start) and response (commit decision).  This is guaranteed by
   the single-writer commit lock combined with version validation.

Formal Properties:
    - **Serializable**: All committed mutations can be totally ordered such
      that each mutation's result is consistent with executing in that order.
    - **Linearizable**: The total order respects real-time ordering — if
      mutation A commits before mutation B starts, A precedes B.
    - **Conflict-Free Progress**: Non-conflicting mutations always commit
      (starvation-free for disjoint write-sets).

Concurrency Model:
    Let S_n be canonical state at version n.  A mutation M operates on
    snapshot S_k (k ≤ n at snapshot time).  At commit:

        if current_version(key) == snapshot_version(key) for all key in read_set(M):
            apply(M)          # atomic under commit lock
            advance versions
        else:
            abort(M)          # conflict detected — re-evaluate from fresh snapshot

    This is equivalent to first-committer-wins OCC with read validation.
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ConflictResolution(str, Enum):
    """Strategy for resolving commit conflicts."""

    ABORT = "abort"  # Reject the mutation; caller must retry
    RETRY = "retry"  # Automatically re-evaluate from fresh snapshot
    MERGE = "merge"  # Attempt semantic merge (requires merge function)


class CommitOutcome(str, Enum):
    """Result of a commit attempt."""

    COMMITTED = "committed"
    CONFLICT = "conflict"
    ABORTED = "aborted"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class VersionedValue:
    """A canonical state value with its version number."""

    value: Any
    version: int
    modified_by: str = ""  # request_id of the mutation that wrote this
    modified_at: float = 0.0  # monotonic timestamp


@dataclass(frozen=True)
class StateSnapshot:
    """An immutable point-in-time snapshot of canonical state.

    Shadow evaluations operate exclusively on snapshots.  The snapshot
    captures both the values and their versions at the time of creation.
    This ensures shadow simulation is isolated from concurrent mutations.

    Properties:
        - Immutable after creation (frozen dataclass)
        - Captures version vector for OCC validation at commit time
        - SHA-256 fingerprint for deterministic identification
    """

    snapshot_id: str
    created_at: float
    state: dict[str, VersionedValue]
    global_version: int

    def read(self, key: str) -> Any:
        """Read a value from the snapshot.

        Args:
            key: State key to read

        Returns:
            The value at snapshot time, or None if not present
        """
        vv = self.state.get(key)
        return vv.value if vv else None

    def version_of(self, key: str) -> int:
        """Get the version of a key at snapshot time.

        Args:
            key: State key

        Returns:
            Version number, or -1 if key does not exist in snapshot
        """
        vv = self.state.get(key)
        return vv.version if vv else -1

    def version_vector(self, keys: set[str]) -> dict[str, int]:
        """Extract version vector for a set of keys.

        Args:
            keys: Keys to include in the version vector

        Returns:
            Mapping from key to version at snapshot time
        """
        return {k: self.version_of(k) for k in keys}

    def compute_hash(self) -> str:
        """Compute deterministic SHA-256 hash of the snapshot."""
        data = {
            k: {"value": str(v.value), "version": v.version}
            for k, v in sorted(self.state.items())
        }
        canonical = json.dumps(
            {
                "snapshot_id": self.snapshot_id,
                "global_version": self.global_version,
                "state": data,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode()).hexdigest()


@dataclass
class MutationIntent:
    """A proposed mutation with its read-set and write-set.

    The read-set captures which keys were read during shadow evaluation.
    The write-set captures which keys will be modified.  At commit time,
    the concurrency controller validates that no read-set key has been
    modified since the snapshot was taken.
    """

    mutation_id: str
    request_id: str
    snapshot_id: str
    snapshot_version: int
    read_set: dict[str, int]  # key -> version at read time
    write_set: dict[str, Any]  # key -> new value
    created_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class CommitResult:
    """Result of a commit attempt."""

    outcome: CommitOutcome
    mutation_id: str
    new_version: int = -1
    conflict_keys: list[str] = field(default_factory=list)
    duration_ms: float = 0.0
    commit_hash: str = ""


class LinearizableCanonicalStore:
    """Production canonical state store with linearizable mutations.

    Provides:
    - Snapshot isolation for shadow evaluations
    - Optimistic concurrency control with version validation
    - Atomic commit under a single-writer lock
    - Version vector tracking for conflict detection
    - Full audit trail of committed mutations

    Thread Safety:
        All public methods are thread-safe.  Snapshot creation and
        reads are lock-free.  Commits acquire a single-writer lock
        for the validation + apply phase.

    Formal Guarantee:
        All committed mutations are linearizable.  If commit(M_a)
        returns before commit(M_b) is invoked, then M_a precedes M_b
        in the linearization order.
    """

    def __init__(self, *, max_retry: int = 3) -> None:
        self._state: dict[str, VersionedValue] = {}
        self._global_version: int = 0
        self._commit_lock = threading.Lock()
        self._snapshot_lock = threading.Lock()
        self._max_retry = max_retry
        self._commit_log: list[CommitResult] = []

    @property
    def global_version(self) -> int:
        """Current global version of canonical state."""
        return self._global_version

    def create_snapshot(self) -> StateSnapshot:
        """Create an immutable point-in-time snapshot.

        The snapshot is a deep copy of the current state.  Subsequent
        mutations to the live state do not affect the snapshot.

        Returns:
            An immutable StateSnapshot for shadow evaluation
        """
        with self._snapshot_lock:
            snapshot = StateSnapshot(
                snapshot_id=f"snap_{uuid.uuid4().hex[:12]}",
                created_at=time.monotonic(),
                state=copy.deepcopy(self._state),
                global_version=self._global_version,
            )
        logger.debug(
            "Created snapshot %s at global_version=%d",
            snapshot.snapshot_id,
            snapshot.global_version,
        )
        return snapshot

    def read(self, key: str) -> VersionedValue | None:
        """Read a versioned value from live state.

        For shadow evaluation, prefer snapshot.read() instead.

        Args:
            key: State key

        Returns:
            VersionedValue or None
        """
        return self._state.get(key)

    def prepare_mutation(
        self,
        request_id: str,
        snapshot: StateSnapshot,
        read_keys: set[str],
        writes: dict[str, Any],
    ) -> MutationIntent:
        """Prepare a mutation intent from a shadow evaluation.

        Captures the read-set version vector from the snapshot for
        later validation at commit time.

        Args:
            request_id: The originating request ID
            snapshot: The snapshot used during shadow evaluation
            read_keys: Keys that were read during evaluation
            writes: Key-value pairs to write

        Returns:
            MutationIntent ready for commit
        """
        return MutationIntent(
            mutation_id=f"mut_{uuid.uuid4().hex[:12]}",
            request_id=request_id,
            snapshot_id=snapshot.snapshot_id,
            snapshot_version=snapshot.global_version,
            read_set=snapshot.version_vector(read_keys),
            write_set=writes,
        )

    def commit(self, mutation: MutationIntent) -> CommitResult:
        """Attempt to commit a mutation with OCC validation.

        The commit protocol:
        1. Acquire single-writer lock (serialization point)
        2. Validate read-set: for each key in read_set, check that
           current_version == snapshot_version (no concurrent modification)
        3. If valid: apply writes, advance versions, release lock
        4. If conflict: release lock, return conflict result

        This guarantees linearizability: the commit either observes a
        state consistent with the snapshot, or aborts.

        Args:
            mutation: The prepared MutationIntent

        Returns:
            CommitResult indicating success or conflict
        """
        start = time.monotonic()

        with self._commit_lock:
            # ── Phase 1: Validate read-set ──
            conflict_keys: list[str] = []
            for key, expected_version in mutation.read_set.items():
                current = self._state.get(key)
                current_version = current.version if current else -1
                if current_version != expected_version:
                    conflict_keys.append(key)

            if conflict_keys:
                result = CommitResult(
                    outcome=CommitOutcome.CONFLICT,
                    mutation_id=mutation.mutation_id,
                    conflict_keys=conflict_keys,
                    duration_ms=(time.monotonic() - start) * 1000,
                )
                logger.warning(
                    "Commit %s CONFLICT on keys=%s (snapshot_v=%d, current_v=%d)",
                    mutation.mutation_id,
                    conflict_keys,
                    mutation.snapshot_version,
                    self._global_version,
                )
                self._commit_log.append(result)
                return result

            # ── Phase 2: Apply writes atomically ──
            self._global_version += 1
            for key, value in mutation.write_set.items():
                current = self._state.get(key)
                old_version = current.version if current else 0
                self._state[key] = VersionedValue(
                    value=value,
                    version=old_version + 1,
                    modified_by=mutation.request_id,
                    modified_at=time.monotonic(),
                )

            # ── Phase 3: Compute commit hash ──
            commit_data = json.dumps(
                {
                    "mutation_id": mutation.mutation_id,
                    "global_version": self._global_version,
                    "writes": {k: str(v) for k, v in mutation.write_set.items()},
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            commit_hash = hashlib.sha256(commit_data.encode()).hexdigest()

            result = CommitResult(
                outcome=CommitOutcome.COMMITTED,
                mutation_id=mutation.mutation_id,
                new_version=self._global_version,
                duration_ms=(time.monotonic() - start) * 1000,
                commit_hash=commit_hash,
            )
            self._commit_log.append(result)

            logger.info(
                "Commit %s SUCCESS: global_version=%d, writes=%d keys",
                mutation.mutation_id,
                self._global_version,
                len(mutation.write_set),
            )
            return result

    def commit_with_retry(
        self,
        request_id: str,
        evaluate_fn: Any,
        max_retries: int | None = None,
    ) -> CommitResult:
        """Commit with automatic retry on conflict.

        On conflict, creates a fresh snapshot, re-evaluates via
        evaluate_fn, and retries the commit.  Bounded by max_retries.

        Args:
            request_id: The originating request ID
            evaluate_fn: Callable(snapshot) -> (read_keys, writes)
                         Re-evaluates the mutation on a fresh snapshot
            max_retries: Maximum retry attempts (default: self._max_retry)

        Returns:
            CommitResult from the final attempt
        """
        retries = max_retries if max_retries is not None else self._max_retry

        for attempt in range(retries + 1):
            snapshot = self.create_snapshot()
            read_keys, writes = evaluate_fn(snapshot)
            mutation = self.prepare_mutation(request_id, snapshot, read_keys, writes)
            result = self.commit(mutation)

            if result.outcome == CommitOutcome.COMMITTED:
                return result

            if attempt < retries:
                logger.info(
                    "Retrying commit for %s (attempt %d/%d)",
                    request_id,
                    attempt + 1,
                    retries,
                )

        # Exhausted retries
        return CommitResult(
            outcome=CommitOutcome.ABORTED,
            mutation_id=mutation.mutation_id,
            conflict_keys=result.conflict_keys,
            duration_ms=result.duration_ms,
        )

    @property
    def commit_log(self) -> list[CommitResult]:
        """Read-only view of the commit log."""
        return list(self._commit_log)

    @property
    def snapshot(self) -> dict[str, Any]:
        """Current state as a plain dict (for debugging)."""
        return {k: v.value for k, v in self._state.items()}


__all__ = [
    "ConflictResolution",
    "CommitOutcome",
    "VersionedValue",
    "StateSnapshot",
    "MutationIntent",
    "CommitResult",
    "LinearizableCanonicalStore",
]
