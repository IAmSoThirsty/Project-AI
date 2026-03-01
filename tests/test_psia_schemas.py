"""
Tests for PSIA Canonical Schemas — all 8 schema modules.

Covers:
    - Round-trip serialization (model → JSON → model)
    - Required field validation
    - compute_hash() determinism
    - Business logic (scope matching, revocation, Merkle root)
"""

from __future__ import annotations

import json

import pytest

from psia.schemas.capability import (
    CapabilityScope,
    CapabilityToken,
    DelegationPolicy,
    ScopeConstraints,
    TokenBinding,
)
from psia.schemas.cerberus_decision import (
    CerberusDecision,
    CerberusVote,
    CommitPolicy,
    ConstraintsApplied,
    DenyReason,
    QuorumInfo,
)
from psia.schemas.identity import (
    IdentityAttributes,
    IdentityDocument,
    PublicKeyEntry,
    RevocationStatus,
    Signature,
)
from psia.schemas.invariant import (
    InvariantDefinition,
    InvariantEnforcement,
    InvariantExpression,
    InvariantScope,
    InvariantSeverity,
    InvariantTestCase,
)
from psia.schemas.ledger import (
    ExecutionRecord,
    LedgerBlock,
    RecordTimestamps,
    TimeProof,
)
from psia.schemas.policy import PolicyEdge, PolicyGraph, PolicyNode
from psia.schemas.request import (
    Intent,
    RequestContext,
    RequestEnvelope,
    RequestTimestamps,
)
from psia.schemas.shadow_report import (
    DeterminismProof,
    InvariantViolation,
    ResourceEnvelope,
    ShadowReport,
    ShadowResults,
    SideEffectSummary,
)

# ── Fixtures ──────────────────────────────────────────────────────────


def _sig(kid: str = "k1") -> Signature:
    return Signature(alg="ed25519", kid=kid, sig="test_sig_base64")


def _identity_doc() -> IdentityDocument:
    return IdentityDocument(
        id="did:project-ai:alice",
        type="human",
        public_keys=[
            PublicKeyEntry(
                kid="k1",
                kty="ed25519",
                pub="AAAA",
                created="2026-01-01T00:00:00Z",
                expires="2027-01-01T00:00:00Z",
            )
        ],
        attributes=IdentityAttributes(org="test_org", role="admin", risk_tier="low"),
        revocation=RevocationStatus(status="active"),
        signature=_sig(),
    )


def _cap_token() -> CapabilityToken:
    return CapabilityToken(
        token_id="cap_001",
        issuer="did:project-ai:ca",
        subject="did:project-ai:alice",
        issued_at="2026-01-01T00:00:00Z",
        expires_at="2027-01-01T00:00:00Z",
        nonce="abcdef1234567890",
        scope=[CapabilityScope(resource="state://data/*", actions=["read", "write"])],
        delegation=DelegationPolicy(is_delegable=False, max_depth=0),
        binding=TokenBinding(client_cert_fingerprint="sha256:aabb"),
        signature=_sig(),
    )


def _request_envelope() -> RequestEnvelope:
    return RequestEnvelope(
        request_id="req_001",
        actor="did:project-ai:alice",
        subject="did:project-ai:alice",
        capability_token_id="cap_001",
        intent=Intent(
            action="mutate_state",
            resource="state://data/key1",
            parameters={"value": 42},
        ),
        context=RequestContext(trace_id="trace_001"),
        timestamps=RequestTimestamps(created_at="2026-01-01T00:00:00Z"),
        signature=_sig(),
    )


# ── Identity Schema Tests ────────────────────────────────────────────


class TestIdentityDocument:
    def test_round_trip(self):
        doc = _identity_doc()
        data = doc.model_dump()
        restored = IdentityDocument.model_validate(data)
        assert restored.id == doc.id
        assert len(restored.public_keys) == 1

    def test_compute_hash_determinism(self):
        doc = _identity_doc()
        h1 = doc.compute_hash()
        h2 = doc.compute_hash()
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex

    def test_hash_excludes_signature(self):
        doc1 = _identity_doc()
        data = doc1.model_dump()
        data["signature"]["sig"] = "different_sig"
        doc2 = IdentityDocument.model_validate(data)
        assert doc1.compute_hash() == doc2.compute_hash()

    def test_revocation_status(self):
        active = RevocationStatus(status="active")
        assert not active.is_revoked
        revoked = RevocationStatus(
            status="revoked", revoked_at="2026-06-01T00:00:00Z", reason="compromised"
        )
        assert revoked.is_revoked

    def test_min_one_public_key(self):
        with pytest.raises(Exception):  # Pydantic ValidationError
            IdentityDocument(
                id="did:project-ai:bob",
                type="human",
                public_keys=[],
                signature=_sig(),
            )


# ── Capability Token Tests ───────────────────────────────────────────


class TestCapabilityToken:
    def test_round_trip(self):
        tok = _cap_token()
        data = tok.model_dump()
        restored = CapabilityToken.model_validate(data)
        assert restored.token_id == tok.token_id

    def test_compute_hash_determinism(self):
        tok = _cap_token()
        assert tok.compute_hash() == tok.compute_hash()

    def test_scope_matching_action(self):
        scope = CapabilityScope(resource="state://data/*", actions=["read", "write"])
        assert scope.matches_action("read")
        assert scope.matches_action("write")
        assert not scope.matches_action("delete")

    def test_scope_matching_resource_glob(self):
        scope = CapabilityScope(resource="state://data/*", actions=["read"])
        assert scope.matches_resource("state://data/foo")
        assert scope.matches_resource("state://data/bar/baz")
        assert not scope.matches_resource("state://other/path")

    def test_scope_matching_resource_exact(self):
        scope = CapabilityScope(resource="state://data/exact", actions=["read"])
        assert scope.matches_resource("state://data/exact")
        assert not scope.matches_resource("state://data/exact/sub")

    def test_covers(self):
        tok = _cap_token()
        assert tok.covers("read", "state://data/key1")
        assert tok.covers("write", "state://data/key1")
        assert not tok.covers("delete", "state://data/key1")
        assert not tok.covers("read", "state://other/path")

    def test_non_delegable_default(self):
        tok = _cap_token()
        assert not tok.delegation.is_delegable
        assert tok.delegation.max_depth == 0


# ── Request Envelope Tests ───────────────────────────────────────────


class TestRequestEnvelope:
    def test_round_trip(self):
        env = _request_envelope()
        data = env.model_dump()
        restored = RequestEnvelope.model_validate(data)
        assert restored.request_id == env.request_id

    def test_compute_hash_determinism(self):
        env = _request_envelope()
        assert env.compute_hash() == env.compute_hash()

    def test_hash_excludes_signature(self):
        env1 = _request_envelope()
        data = env1.model_dump()
        data["signature"]["sig"] = "different_sig"
        env2 = RequestEnvelope.model_validate(data)
        assert env1.compute_hash() == env2.compute_hash()


# ── Policy Graph Tests ───────────────────────────────────────────────


class TestPolicyGraph:
    def test_round_trip(self):
        graph = PolicyGraph(
            policy_id="pol_001",
            version=1,
            hash="placeholder",
            nodes=[PolicyNode(id="n1", type="subject", value="did:project-ai:alice")],
            edges=[],
            signatures=[_sig()],
        )
        data = graph.model_dump()
        restored = PolicyGraph.model_validate(data)
        assert restored.policy_id == "pol_001"

    def test_compute_graph_hash(self):
        nodes = [PolicyNode(id="n1", type="subject", value="did:project-ai:alice")]
        graph = PolicyGraph(
            policy_id="pol_001",
            version=1,
            hash="placeholder",
            nodes=nodes,
            edges=[],
            signatures=[_sig()],
        )
        computed = graph.compute_graph_hash()
        assert len(computed) == 64

    def test_verify_hash(self):
        nodes = [PolicyNode(id="n1", type="action", value="read")]
        edges = []
        # First compute the real hash
        import hashlib

        body = {
            "nodes": [n.model_dump() for n in nodes],
            "edges": [],
        }
        real_hash = hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

        graph = PolicyGraph(
            policy_id="pol_002",
            version=1,
            hash=real_hash,
            nodes=nodes,
            edges=edges,
            signatures=[_sig()],
        )
        assert graph.verify_hash()


# ── Invariant Definition Tests ───────────────────────────────────────


class TestInvariantDefinition:
    def test_round_trip(self):
        inv = InvariantDefinition(
            invariant_id="inv_test_001",
            version=1,
            scope=InvariantScope.CONSTITUTIONAL,
            severity=InvariantSeverity.HIGH,
            enforcement=InvariantEnforcement.HARD_DENY,
            expression=InvariantExpression(
                language="first_order_logic", expr="forall x: true"
            ),
            tests=[InvariantTestCase(name="trivial", given={"x": 1}, expect="allow")],
            signature=_sig(),
        )
        data = inv.model_dump()
        restored = InvariantDefinition.model_validate(data)
        assert restored.invariant_id == "inv_test_001"

    def test_min_one_test_case(self):
        with pytest.raises(Exception):
            InvariantDefinition(
                invariant_id="inv_test_002",
                version=1,
                scope=InvariantScope.OPERATIONAL,
                severity=InvariantSeverity.LOW,
                enforcement=InvariantEnforcement.RATE_LIMIT,
                expression=InvariantExpression(expr="true"),
                tests=[],
                signature=_sig(),
            )


# ── Shadow Report Tests ──────────────────────────────────────────────


class TestShadowReport:
    def test_round_trip(self):
        report = ShadowReport(
            request_id="req_001",
            shadow_job_id="shj_001",
            snapshot_id="snap_001",
            determinism=DeterminismProof(
                seed="aabb", replay_hash="ccdd", replay_verified=True
            ),
            results=ShadowResults(divergence_score=0.05),
            timestamp="2026-01-01T00:00:00Z",
            signature=_sig(),
        )
        data = report.model_dump()
        restored = ShadowReport.model_validate(data)
        assert restored.shadow_job_id == "shj_001"

    def test_has_critical_violations_false(self):
        report = ShadowReport(
            request_id="req_001",
            shadow_job_id="shj_001",
            snapshot_id="snap_001",
            determinism=DeterminismProof(seed="aabb", replay_hash="ccdd"),
            results=ShadowResults(),
            timestamp="2026-01-01T00:00:00Z",
            signature=_sig(),
        )
        assert not report.has_critical_violations

    def test_has_critical_violations_true(self):
        report = ShadowReport(
            request_id="req_001",
            shadow_job_id="shj_001",
            snapshot_id="snap_001",
            determinism=DeterminismProof(seed="aa", replay_hash="cc"),
            results=ShadowResults(
                invariant_violations=[
                    InvariantViolation(invariant_id="inv_001", severity="critical")
                ]
            ),
            timestamp="2026-01-01T00:00:00Z",
            signature=_sig(),
        )
        assert report.has_critical_violations


# ── Cerberus Decision Tests ──────────────────────────────────────────


class TestCerberusDecision:
    def _make_vote(self, head, decision):
        return CerberusVote(
            request_id="req_001",
            head=head,
            decision=decision,
            reasons=[],
            timestamp="2026-01-01T00:00:00Z",
            signature=_sig(),
        )

    def test_is_allowed(self):
        decision = CerberusDecision(
            request_id="req_001",
            severity="low",
            final_decision="allow",
            votes=[
                self._make_vote("identity", "allow"),
                self._make_vote("capability", "allow"),
                self._make_vote("invariant", "allow"),
            ],
            quorum=QuorumInfo(
                required="2of3", achieved=True, voters=["n0", "n1", "n2"]
            ),
            timestamp="2026-01-01T00:00:00Z",
        )
        assert decision.is_allowed

    def test_is_not_allowed_when_denied(self):
        decision = CerberusDecision(
            request_id="req_001",
            severity="high",
            final_decision="deny",
            votes=[
                self._make_vote("identity", "deny"),
                self._make_vote("capability", "allow"),
                self._make_vote("invariant", "allow"),
            ],
            quorum=QuorumInfo(required="unanimous", achieved=False),
            timestamp="2026-01-01T00:00:00Z",
        )
        assert not decision.is_allowed

    def test_compute_hash_determinism(self):
        decision = CerberusDecision(
            request_id="req_001",
            severity="low",
            final_decision="allow",
            votes=[self._make_vote("identity", "allow")],
            quorum=QuorumInfo(required="simple", achieved=True),
            timestamp="2026-01-01T00:00:00Z",
        )
        assert decision.compute_hash() == decision.compute_hash()


# ── Ledger Tests ─────────────────────────────────────────────────────


class TestLedgerBlock:
    def test_merkle_root_single(self):
        hashes = ["a" * 64]
        root = LedgerBlock.compute_merkle_root(hashes)
        assert len(root) == 64

    def test_merkle_root_two(self):
        h1 = "a" * 64
        h2 = "b" * 64
        root = LedgerBlock.compute_merkle_root([h1, h2])
        assert len(root) == 64

    def test_merkle_root_empty(self):
        root = LedgerBlock.compute_merkle_root([])
        assert len(root) == 64

    def test_merkle_root_determinism(self):
        hashes = ["ab" * 32, "cd" * 32, "ef" * 32]
        r1 = LedgerBlock.compute_merkle_root(hashes)
        r2 = LedgerBlock.compute_merkle_root(hashes)
        assert r1 == r2

    def test_block_compute_hash(self):
        block = LedgerBlock(
            height=0,
            previous_block_hash="",
            merkle_root="aa" * 32,
            records=["aa" * 32],
        )
        h = block.compute_hash()
        assert len(h) == 64

    def test_execution_record_round_trip(self):
        record = ExecutionRecord(
            record_id="rec_001",
            request_id="req_001",
            actor="did:project-ai:alice",
            capability_token_id="cap_001",
            inputs_hash="aa" * 32,
            decision_hash="bb" * 32,
            result="allow",
            timestamps=RecordTimestamps(
                received_at="2026-01-01T00:00:00Z", decided_at="2026-01-01T00:00:01Z"
            ),
            signature=_sig(),
        )
        data = record.model_dump()
        restored = ExecutionRecord.model_validate(data)
        assert restored.record_id == "rec_001"


# ── Root Invariants Tests ────────────────────────────────────────────


class TestRootInvariants:
    def test_all_nine_exist(self):
        from psia.invariants import ROOT_INVARIANTS

        assert len(ROOT_INVARIANTS) == 9

    def test_all_immutable_fatal(self):
        from psia.invariants import ROOT_INVARIANTS

        for inv_id, inv in ROOT_INVARIANTS.items():
            assert inv.scope == InvariantScope.IMMUTABLE, f"{inv_id} not immutable"
            assert inv.severity == InvariantSeverity.FATAL, f"{inv_id} not fatal"

    def test_all_have_at_least_two_tests(self):
        from psia.invariants import ROOT_INVARIANTS

        for inv_id, inv in ROOT_INVARIANTS.items():
            assert len(inv.tests) >= 2, f"{inv_id} has fewer than 2 test cases"

    def test_ids_are_sequential(self):
        from psia.invariants import ROOT_INVARIANTS

        for i in range(1, 10):
            assert f"inv_root_{i:03d}" in ROOT_INVARIANTS


# ── Plane Contracts Tests ────────────────────────────────────────────


class TestPlaneContracts:
    def test_all_six_planes(self):
        from psia.planes import PLANE_CONTRACTS, Plane

        assert len(PLANE_CONTRACTS) == 6
        for p in Plane:
            assert p in PLANE_CONTRACTS

    def test_shadow_cannot_write_canonical(self):
        from psia.planes import Plane, PlaneCapability, validate_plane_action

        assert not validate_plane_action(Plane.SHADOW, PlaneCapability.WRITE_CANONICAL)

    def test_reflex_cannot_legislate(self):
        from psia.planes import Plane, PlaneCapability, validate_plane_action

        assert not validate_plane_action(Plane.REFLEX, PlaneCapability.EMIT_PROPOSAL)
        assert not validate_plane_action(Plane.REFLEX, PlaneCapability.COMPILE_POLICY)

    def test_canonical_can_write(self):
        from psia.planes import Plane, PlaneCapability, validate_plane_action

        assert validate_plane_action(Plane.CANONICAL, PlaneCapability.WRITE_CANONICAL)

    def test_ingress_can_accept_requests(self):
        from psia.planes import Plane, PlaneCapability, validate_plane_action

        assert validate_plane_action(Plane.INGRESS, PlaneCapability.ACCEPT_REQUEST)


# ── Event Bus Tests ──────────────────────────────────────────────────


class TestEventBus:
    def test_emit_and_subscribe(self):
        from psia.events import EventBus, EventType, create_event

        bus = EventBus()
        received = []
        bus.subscribe(EventType.WATERFALL_START, lambda e: received.append(e))
        evt = create_event(EventType.WATERFALL_START, trace_id="t1")
        bus.emit(evt)
        assert len(received) == 1
        assert received[0].event_type == EventType.WATERFALL_START

    def test_wildcard_subscriber(self):
        from psia.events import EventBus, EventType, create_event

        bus = EventBus()
        received = []
        bus.subscribe(None, lambda e: received.append(e))
        bus.emit(create_event(EventType.WATERFALL_START))
        bus.emit(create_event(EventType.STAGE_ENTER))
        assert len(received) == 2

    def test_drain(self):
        from psia.events import EventBus, EventType, create_event

        bus = EventBus()
        bus.emit(create_event(EventType.WATERFALL_START))
        bus.emit(create_event(EventType.STAGE_ENTER))
        events = bus.drain()
        assert len(events) == 2
        assert bus.event_count == 0

    def test_event_compute_hash(self):
        from psia.events import EventType, create_event

        evt = create_event(EventType.COMMIT_SUCCEEDED, trace_id="t1", request_id="r1")
        h1 = evt.compute_hash()
        h2 = evt.compute_hash()
        assert h1 == h2
        assert len(h1) == 64
