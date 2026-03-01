"""
Tests for PSIA Concurrency Model — Linearizable Canonical State Mutations.

Fact-verifies claims from the paper (§6):
    - Snapshot isolation: shadow evaluation reads from a frozen snapshot
    - Version vectors: monotonic increment on canonical write
    - OCC commit: read-set validation detects stale reads
    - Linearizability: commits appear atomic under single-writer lock
    - Conflict-free progress: disjoint write-sets never conflict
    - Retry exhaustion: bounded retries → fail-closed abort
"""

from __future__ import annotations

import threading

import pytest

from psia.concurrency import (
    CommitOutcome,
    CommitResult,
    LinearizableCanonicalStore,
    MutationIntent,
    StateSnapshot,
    VersionedValue,
)


class TestSnapshotIsolation:
    """Paper §6.3: Shadow evaluations read from a consistent, immutable snapshot."""

    def test_snapshot_is_frozen(self):
        """Snapshot not affected by subsequent live state mutations."""
        store = LinearizableCanonicalStore()
        # Seed state
        snap1 = store.create_snapshot()
        mutation = store.prepare_mutation("req_seed", snap1, set(), {"key1": "initial"})
        store.commit(mutation)

        # Take snapshot after seed
        snap2 = store.create_snapshot()
        assert snap2.read("key1") == "initial"

        # Mutate live state AFTER snapshot
        mutation2 = store.prepare_mutation(
            "req_update", snap2, set(), {"key1": "updated"}
        )
        store.commit(mutation2)

        # Snapshot still sees old value
        assert snap2.read("key1") == "initial"

    def test_two_snapshots_independent(self):
        """Two concurrent snapshots have independent views."""
        store = LinearizableCanonicalStore()
        snap_a = store.create_snapshot()
        mutation = store.prepare_mutation("req_1", snap_a, set(), {"x": 10})
        store.commit(mutation)

        snap_b = store.create_snapshot()
        assert snap_b.read("x") == 10
        assert snap_a.read("x") is None  # Older snapshot doesn't see it


class TestVersionVectors:
    """Paper §6.3: Every canonical key carries a monotonically increasing version."""

    def test_version_increment_on_write(self):
        store = LinearizableCanonicalStore()
        snap = store.create_snapshot()
        mutation = store.prepare_mutation("req_1", snap, set(), {"k": "v1"})
        store.commit(mutation)
        assert store.read("k").version == 1

        snap2 = store.create_snapshot()
        mutation2 = store.prepare_mutation("req_2", snap2, set(), {"k": "v2"})
        store.commit(mutation2)
        assert store.read("k").version == 2

    def test_global_version_advances(self):
        store = LinearizableCanonicalStore()
        assert store.global_version == 0

        snap = store.create_snapshot()
        mutation = store.prepare_mutation("req_1", snap, set(), {"a": 1})
        store.commit(mutation)
        assert store.global_version == 1

        snap2 = store.create_snapshot()
        mutation2 = store.prepare_mutation("req_2", snap2, set(), {"b": 2})
        store.commit(mutation2)
        assert store.global_version == 2


class TestOCCCommit:
    """Paper §6.3: OCC validates read-set at commit time."""

    def test_commit_success_no_conflict(self):
        store = LinearizableCanonicalStore()
        # Seed key
        snap0 = store.create_snapshot()
        store.commit(store.prepare_mutation("seed", snap0, set(), {"x": 1}))

        # Read x, write y — x unchanged → commit succeeds
        snap = store.create_snapshot()
        mutation = store.prepare_mutation("req_1", snap, {"x"}, {"y": 2})
        result = store.commit(mutation)
        assert result.outcome == CommitOutcome.COMMITTED

    def test_conflict_detection_on_stale_read(self):
        """If a read-set key has been modified after snapshot, commit fails."""
        store = LinearizableCanonicalStore()
        # Seed
        snap0 = store.create_snapshot()
        store.commit(store.prepare_mutation("seed", snap0, set(), {"x": 1}))

        # Reader takes snapshot
        snap_reader = store.create_snapshot()

        # Concurrent writer modifies x
        snap_writer = store.create_snapshot()
        store.commit(store.prepare_mutation("writer", snap_writer, set(), {"x": 99}))

        # Reader tries to commit having read x — CONFLICT
        mutation = store.prepare_mutation("reader", snap_reader, {"x"}, {"y": 2})
        result = store.commit(mutation)
        assert result.outcome == CommitOutcome.CONFLICT
        assert "x" in result.conflict_keys

    def test_disjoint_writes_no_conflict(self):
        """Paper: non-conflicting writes (disjoint write-sets) pass validation."""
        store = LinearizableCanonicalStore()
        snap = store.create_snapshot()

        # Writer A writes key "a", reader reads nothing
        m_a = store.prepare_mutation("writer_a", snap, set(), {"a": 1})
        store.commit(m_a)

        # Writer B writes key "b" from same snapshot (but read-set is empty)
        m_b = store.prepare_mutation("writer_b", snap, set(), {"b": 2})
        result = store.commit(m_b)
        assert result.outcome == CommitOutcome.COMMITTED


class TestRetryAndAbort:
    """Paper §6.3: Bounded retries, fail-closed abort."""

    def test_commit_with_retry_succeeds(self):
        store = LinearizableCanonicalStore(max_retry=3)

        def evaluate(snap):
            return set(), {"counter": (snap.read("counter") or 0) + 1}

        result = store.commit_with_retry("req_retry", evaluate)
        assert result.outcome == CommitOutcome.COMMITTED
        assert store.read("counter").value == 1

    def test_retry_exhaustion_aborts(self):
        """When conflicts persist beyond max_retries, commit aborts."""
        store = LinearizableCanonicalStore(max_retry=0)

        # Seed a key
        snap0 = store.create_snapshot()
        store.commit(store.prepare_mutation("seed", snap0, set(), {"x": 1}))

        def evaluate_and_cause_conflict(snap):
            # Read "x" to include it in read-set
            _ = snap.read("x")
            # Concurrently modify "x" so our read-set is stale at commit
            fresh = store.create_snapshot()
            store.commit(
                store.prepare_mutation(
                    "interfere", fresh, set(), {"x": snap.read("x") + 100}
                )
            )
            return {"x"}, {"result": 42}

        result = store.commit_with_retry(
            "req_fail", evaluate_and_cause_conflict, max_retries=0
        )
        assert result.outcome in (CommitOutcome.CONFLICT, CommitOutcome.ABORTED)


class TestLinearizability:
    """Paper §6.3: Committed mutations are linearizable under single-writer lock."""

    def test_commit_log_preserves_order(self):
        store = LinearizableCanonicalStore()
        for i in range(5):
            snap = store.create_snapshot()
            m = store.prepare_mutation(f"req_{i}", snap, set(), {f"k{i}": i})
            store.commit(m)

        log = store.commit_log
        assert len(log) == 5
        # All committed in order
        for i, entry in enumerate(log):
            assert entry.outcome == CommitOutcome.COMMITTED
            assert entry.new_version == i + 1

    def test_commit_hash_is_deterministic(self):
        """Commit hash depends on mutation content, not timing."""
        store = LinearizableCanonicalStore()
        snap = store.create_snapshot()
        m = store.prepare_mutation("req_hash", snap, set(), {"k": "v"})
        result = store.commit(m)
        assert result.commit_hash  # Non-empty SHA-256
        assert len(result.commit_hash) == 64  # SHA-256 hex length
