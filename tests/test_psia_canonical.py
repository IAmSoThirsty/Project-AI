"""
Comprehensive test suite for PSIA Phase 4: Canonical Plane.

Covers:
    - CommitCoordinator: transactional commits, OCC, WAL, rollback, Cerberus checks
    - DurableLedger: append-only, block sealing, Merkle roots, chain verification
    - CapabilityAuthority: token issuance, revocation, rotation, invariant enforcement
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

import pytest

from psia.canonical.commit_coordinator import (
    CanonicalStore,
    CommitCoordinator,
    CommitStatus,
)
from psia.canonical.ledger import (
    DurableLedger,
    ExecutionRecord,
)
from psia.canonical.capability_authority import (
    CapabilityAuthority,
)
from psia.schemas.capability import CapabilityScope, ScopeConstraints


# ═══════════════════════════════════════════════════════════════════
#  CanonicalStore Tests
# ═══════════════════════════════════════════════════════════════════

class TestCanonicalStore:

    def test_put_and_get(self):
        store = CanonicalStore()
        val = store.put("key1", "value1")
        assert val.version == 1
        retrieved = store.get("key1")
        assert retrieved is not None
        assert retrieved.value == "value1"

    def test_get_nonexistent(self):
        store = CanonicalStore()
        assert store.get("missing") is None

    def test_version_increments(self):
        store = CanonicalStore()
        store.put("k", "v1")
        store.put("k", "v2")
        assert store.get_version("k") == 2

    def test_optimistic_concurrency_success(self):
        store = CanonicalStore()
        store.put("k", "v1")
        store.put("k", "v2", expected_version=1)
        assert store.get("k").value == "v2"

    def test_optimistic_concurrency_conflict(self):
        store = CanonicalStore()
        store.put("k", "v1")
        store.put("k", "v2")
        with pytest.raises(ValueError, match="Optimistic concurrency conflict"):
            store.put("k", "v3", expected_version=1)  # current=2, expected=1

    def test_delete(self):
        store = CanonicalStore()
        store.put("k", "v1")
        assert store.delete("k") is True
        assert store.get("k") is None

    def test_delete_nonexistent(self):
        store = CanonicalStore()
        assert store.delete("missing") is False

    def test_delete_version_conflict(self):
        store = CanonicalStore()
        store.put("k", "v1")
        store.put("k", "v2")
        with pytest.raises(ValueError, match="Optimistic concurrency conflict"):
            store.delete("k", expected_version=1)

    def test_history(self):
        store = CanonicalStore()
        store.put("k", "v1")
        store.put("k", "v2")
        store.put("k", "v3")
        history = store.history("k")
        assert len(history) == 3
        assert history[0].value == "v1"
        assert history[2].value == "v3"

    def test_snapshot(self):
        store = CanonicalStore()
        store.put("a", 1)
        store.put("b", 2)
        snap = store.snapshot()
        assert len(snap) == 2
        assert snap["a"].value == 1

    def test_key_count(self):
        store = CanonicalStore()
        assert store.key_count == 0
        store.put("a", 1)
        store.put("b", 2)
        assert store.key_count == 2


# ═══════════════════════════════════════════════════════════════════
#  CommitCoordinator Tests
# ═══════════════════════════════════════════════════════════════════

class TestCommitCoordinator:

    def test_basic_commit(self):
        coord = CommitCoordinator(require_cerberus_allow=False)
        result = coord.commit(
            request_id="req_1",
            mutations={"key1": "val1"},
            actor="alice",
        )
        assert result.status == CommitStatus.COMMITTED
        assert "key1" in result.keys_mutated
        assert result.diff_hash != ""

    def test_multi_key_commit(self):
        coord = CommitCoordinator(require_cerberus_allow=False)
        result = coord.commit(
            request_id="req_2",
            mutations={"a": 1, "b": 2, "c": 3},
        )
        assert result.status == CommitStatus.COMMITTED
        assert len(result.keys_mutated) == 3
        assert result.version_after["a"] == 1
        assert result.version_after["c"] == 1

    def test_empty_mutations_commit(self):
        coord = CommitCoordinator(require_cerberus_allow=False)
        result = coord.commit(request_id="req_3", mutations={})
        assert result.status == CommitStatus.COMMITTED
        assert len(result.keys_mutated) == 0

    def test_version_conflict_fails(self):
        coord = CommitCoordinator(require_cerberus_allow=False)
        coord.commit(request_id="r1", mutations={"k": "v1"})
        result = coord.commit(
            request_id="r2",
            mutations={"k": "v2"},
            expected_versions={"k": 0},  # wrong: current is 1
        )
        assert result.status == CommitStatus.FAILED
        assert "Version conflict" in result.error

    def test_cerberus_deny_blocks_commit(self):
        """When require_cerberus_allow is True, a deny decision blocks the commit."""

        class FakeDecision:
            is_allowed = False

        coord = CommitCoordinator(require_cerberus_allow=True)
        result = coord.commit(
            request_id="r1",
            mutations={"k": "v"},
            cerberus_decision=FakeDecision(),
        )
        assert result.status == CommitStatus.FAILED
        assert "does not allow" in result.error

    def test_cerberus_allow_permits_commit(self):
        class FakeDecision:
            is_allowed = True

            class commit_policy:
                allowed = True

        coord = CommitCoordinator(require_cerberus_allow=True)
        result = coord.commit(
            request_id="r1",
            mutations={"k": "v"},
            cerberus_decision=FakeDecision(),
        )
        assert result.status == CommitStatus.COMMITTED

    def test_commit_policy_denied(self):
        class FakeDecision:
            is_allowed = True

            class commit_policy:
                allowed = False

        coord = CommitCoordinator(require_cerberus_allow=True)
        result = coord.commit(
            request_id="r1",
            mutations={"k": "v"},
            cerberus_decision=FakeDecision(),
        )
        assert result.status == CommitStatus.FAILED
        assert "CommitPolicy" in result.error

    def test_wal_entries_created(self):
        coord = CommitCoordinator(require_cerberus_allow=False)
        coord.commit(request_id="r1", mutations={"a": 1, "b": 2})
        assert len(coord.wal_entries) == 2
        assert coord.wal_entries[0].key == "a"
        assert coord.wal_entries[1].key == "b"

    def test_sequential_commits_version_increments(self):
        coord = CommitCoordinator(require_cerberus_allow=False)
        coord.commit(request_id="r1", mutations={"k": "v1"})
        coord.commit(request_id="r2", mutations={"k": "v2"})
        val = coord.store.get("k")
        assert val.version == 2
        assert val.value == "v2"

    def test_diff_hash_deterministic(self):
        coord1 = CommitCoordinator(require_cerberus_allow=False)
        coord2 = CommitCoordinator(require_cerberus_allow=False)
        r1 = coord1.commit(request_id="r1", mutations={"k": "v"})
        r2 = coord2.commit(request_id="r1", mutations={"k": "v"})
        # Same commit_id, same mutations, same versions => same diff hash
        assert r1.diff_hash == r2.diff_hash

    def test_event_emission(self):
        events = []
        coord = CommitCoordinator(
            require_cerberus_allow=False,
            emit_events=lambda r: events.append(r),
        )
        coord.commit(request_id="r1", mutations={"k": "v"})
        assert len(events) == 1
        assert events[0].status == CommitStatus.COMMITTED


# ═══════════════════════════════════════════════════════════════════
#  DurableLedger Tests
# ═══════════════════════════════════════════════════════════════════

def _record(rid: str = "rec_1", req_id: str = "req_1") -> ExecutionRecord:
    return ExecutionRecord(
        record_id=rid,
        request_id=req_id,
        actor="did:project-ai:test:alice",
        action="execute",
        resource="/api/v1/test",
        decision="allow",
        commit_id="commit_000001",
    )


class TestDurableLedger:

    def test_append_record(self):
        ledger = DurableLedger()
        h = ledger.append(_record())
        assert isinstance(h, str)
        assert ledger.total_records == 1

    def test_duplicate_record_rejected(self):
        """INV-ROOT-9: no overwrites."""
        ledger = DurableLedger()
        ledger.append(_record("r1"))
        with pytest.raises(ValueError, match="INV-ROOT-9"):
            ledger.append(_record("r1"))

    def test_get_record(self):
        ledger = DurableLedger()
        ledger.append(_record("r1"))
        rec = ledger.get_record("r1")
        assert rec is not None
        assert rec.actor == "did:project-ai:test:alice"

    def test_get_records_by_request(self):
        ledger = DurableLedger()
        ledger.append(_record("r1", "req_A"))
        ledger.append(_record("r2", "req_A"))
        ledger.append(_record("r3", "req_B"))
        recs = ledger.get_records_by_request("req_A")
        assert len(recs) == 2

    def test_auto_seal_block(self):
        ledger = DurableLedger(block_size=4)
        for i in range(4):
            ledger.append(_record(f"r{i}", f"req_{i}"))
        assert ledger.sealed_block_count == 1
        assert ledger.pending_record_count == 0

    def test_force_seal(self):
        ledger = DurableLedger(block_size=100)
        ledger.append(_record("r1"))
        ledger.append(_record("r2"))
        block = ledger.force_seal()
        assert block is not None
        assert block.record_count == 2

    def test_force_seal_empty(self):
        ledger = DurableLedger()
        assert ledger.force_seal() is None

    def test_merkle_root_consistency(self):
        ledger = DurableLedger(block_size=2)
        ledger.append(_record("r1"))
        ledger.append(_record("r2"))
        block = ledger.get_block(0)
        assert block is not None
        assert len(block.merkle_root) == 64  # SHA-256 hex

    def test_block_chain_verification(self):
        ledger = DurableLedger(block_size=2)
        for i in range(6):
            ledger.append(_record(f"r{i}"))
        assert ledger.sealed_block_count == 3
        assert ledger.verify_chain() is True

    def test_anchor_block(self):
        ledger = DurableLedger(block_size=2)
        ledger.append(_record("r1"))
        ledger.append(_record("r2"))
        assert ledger.anchor_block(0, "anchor_hash_abc") is True
        block = ledger.get_block(0)
        assert block.anchor_hash == "anchor_hash_abc"

    def test_anchor_invalid_block(self):
        ledger = DurableLedger()
        assert ledger.anchor_block(99, "hash") is False

    def test_on_block_sealed_callback(self):
        sealed = []
        ledger = DurableLedger(block_size=2, on_block_sealed=lambda b: sealed.append(b))
        ledger.append(_record("r1"))
        ledger.append(_record("r2"))
        assert len(sealed) == 1

    def test_genesis_hash(self):
        ledger = DurableLedger(block_size=1)
        ledger.append(_record("r1"))
        block = ledger.get_block(0)
        assert block.previous_block_hash == DurableLedger.GENESIS_HASH


# ═══════════════════════════════════════════════════════════════════
#  CapabilityAuthority Tests
# ═══════════════════════════════════════════════════════════════════

def _scope(action: str = "execute", resource: str = "/api/v1/*") -> CapabilityScope:
    return CapabilityScope(
        actions=[action],
        resource=resource,
        constraints=ScopeConstraints(),
    )


class TestCapabilityAuthority:

    def test_issue_token(self):
        ca = CapabilityAuthority()
        token = ca.issue(
            subject="did:project-ai:test:alice",
            scopes=[_scope()],
        )
        assert token.issuer == ca.authority_did
        assert token.subject == "did:project-ai:test:alice"
        assert ca.issued_count == 1

    def test_self_issuance_blocked(self):
        """INV-ROOT-5: authority cannot issue to itself."""
        ca = CapabilityAuthority()
        with pytest.raises(ValueError, match="INV-ROOT-5"):
            ca.issue(subject=ca.authority_did, scopes=[_scope()])

    def test_excessive_scope_blocked(self):
        """INV-ROOT-6: too many actions per scope."""
        ca = CapabilityAuthority(max_scope_actions=2)
        wide_scope = CapabilityScope(
            actions=["read", "write", "delete"],
            resource="/api/*",
            constraints=ScopeConstraints(),
        )
        with pytest.raises(ValueError, match="INV-ROOT-6"):
            ca.issue(subject="did:project-ai:test:alice", scopes=[wide_scope])

    def test_revoke_token(self):
        ca = CapabilityAuthority()
        token = ca.issue(subject="did:project-ai:test:alice", scopes=[_scope()])
        assert ca.revoke(token.token_id) is True
        assert ca.is_revoked(token.token_id) is True
        assert ca.is_valid(token.token_id) is False

    def test_revoke_nonexistent(self):
        ca = CapabilityAuthority()
        assert ca.revoke("missing_id") is False

    def test_revoke_idempotent(self):
        ca = CapabilityAuthority()
        token = ca.issue(subject="did:project-ai:test:alice", scopes=[_scope()])
        ca.revoke(token.token_id)
        assert ca.revoke(token.token_id) is True  # already revoked, returns True

    def test_rotate_token(self):
        ca = CapabilityAuthority()
        old = ca.issue(subject="did:project-ai:test:alice", scopes=[_scope()])
        new = ca.rotate(old.token_id)
        assert new is not None
        assert new.token_id != old.token_id
        assert ca.is_revoked(old.token_id) is True
        assert ca.is_valid(new.token_id) is True

    def test_rotate_nonexistent(self):
        ca = CapabilityAuthority()
        assert ca.rotate("missing") is None

    def test_is_valid_expired(self):
        ca = CapabilityAuthority(default_ttl_hours=0)
        # TTL=0 means expires immediately at issued_at + 0h = now
        token = ca.issue(subject="did:project-ai:test:alice", scopes=[_scope()])
        # Token expires at issuance time, so it should be expired
        assert ca.is_valid(token.token_id) is False

    def test_active_count(self):
        ca = CapabilityAuthority()
        t1 = ca.issue(subject="did:project-ai:test:alice", scopes=[_scope()])
        t2 = ca.issue(subject="did:project-ai:test:bob", scopes=[_scope()])
        ca.revoke(t1.token_id)
        assert ca.active_count == 1

    def test_audit_log(self):
        ca = CapabilityAuthority()
        t = ca.issue(subject="did:project-ai:test:alice", scopes=[_scope()])
        ca.revoke(t.token_id)
        log = ca.audit_log
        assert len(log) == 2
        assert log[0].event_type == "issued"
        assert log[1].event_type == "revoked"

    def test_get_token(self):
        ca = CapabilityAuthority()
        t = ca.issue(subject="did:project-ai:test:alice", scopes=[_scope()])
        retrieved = ca.get_token(t.token_id)
        assert retrieved is not None
        assert retrieved.token_id == t.token_id

    def test_delegation_policy(self):
        ca = CapabilityAuthority(allow_delegation=True, max_delegation_depth=5)
        t = ca.issue(subject="did:project-ai:test:alice", scopes=[_scope()])
        assert t.delegation.is_delegable is True
        assert t.delegation.max_depth == 5

    def test_revocation_list(self):
        ca = CapabilityAuthority()
        t = ca.issue(subject="did:project-ai:test:alice", scopes=[_scope()])
        ca.revoke(t.token_id, reason="compromised")
        crl = ca.revocation_list
        assert len(crl) == 1
        assert crl[0].reason == "compromised"
