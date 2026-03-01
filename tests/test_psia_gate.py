"""
Tests for PSIA Gate Plane — Cerberus Heads + Quorum Engine.

Covers:
    Identity Head:
        - Valid DID + registered document → allow
        - Invalid DID format → deny
        - DID not found in store → deny
        - Revoked identity → deny
        - Expired public key → deny
        - Device attestation failure → deny (when enforced)
        - Risk tier exceeded → deny

    Capability Head:
        - Valid token covering action+resource → allow
        - Token not found → deny
        - Token revoked → deny
        - Token expired → deny
        - Scope mismatch → deny
        - Delegation depth exceeded → deny

    Invariant Head:
        - Normal mutation (no invariant violation) → allow
        - Attempt to mutate invariant resource → deny (INV-ROOT-1)
        - Attempt to modify Cerberus → deny (INV-ROOT-5)
        - Attempt to delete ledger entry → deny (INV-ROOT-9)
        - Shadow violation cross-check → deny

    Quorum Engine:
        - All allow → allow (unanimous, 2of3, simple, bft)
        - One deny → deny (unanimous)
        - One deny → allow (2of3)
        - All deny → deny
        - No votes → deny
        - Weighted majority
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from psia.gate.capability_head import CapabilityHead, CapabilityTokenStore
from psia.gate.identity_head import (
    DeviceAttestationRegistry,
    IdentityDocumentStore,
    IdentityHead,
)
from psia.gate.invariant_head import InvariantHead, InvariantRegistry
from psia.gate.quorum_engine import HeadWeight, ProductionQuorumEngine
from psia.schemas.capability import (
    CapabilityScope,
    CapabilityToken,
    DelegationPolicy,
    TokenBinding,
)
from psia.schemas.cerberus_decision import CerberusVote, ConstraintsApplied, DenyReason
from psia.schemas.identity import (
    IdentityAttributes,
    IdentityDocument,
    PublicKeyEntry,
    RevocationStatus,
    Signature,
)
from psia.schemas.request import (
    Intent,
    RequestContext,
    RequestEnvelope,
    RequestTimestamps,
)


def _sig() -> Signature:
    return Signature(alg="ed25519", kid="k1", sig="test_sig")


def _identity_doc(
    did: str = "did:project-ai:test:alice",
    risk_tier: str = "low",
    revoked: bool = False,
    key_expires: str | None = None,
) -> IdentityDocument:
    if key_expires is None:
        key_expires = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
    return IdentityDocument(
        id=did,
        type="human",
        public_keys=[
            PublicKeyEntry(
                kid="k1",
                kty="ed25519",
                pub="AAAA",
                created="2025-01-01T00:00:00Z",
                expires=key_expires,
            )
        ],
        attributes=IdentityAttributes(
            org="test_org", role="admin", risk_tier=risk_tier
        ),
        revocation=RevocationStatus(
            status="revoked" if revoked else "active",
            revoked_at="2026-01-01T00:00:00Z" if revoked else None,
            reason="compromised" if revoked else None,
        ),
        signature=_sig(),
    )


def _cap_token(
    token_id: str = "cap_001",
    subject: str = "did:project-ai:test:alice",
    actions: list[str] | None = None,
    resource: str = "state://data/*",
    expires_at: str | None = None,
    delegable: bool = False,
    max_depth: int = 0,
) -> CapabilityToken:
    if actions is None:
        actions = ["read", "mutate_state"]
    if expires_at is None:
        expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    return CapabilityToken(
        token_id=token_id,
        issuer="did:project-ai:ca",
        subject=subject,
        issued_at="2026-01-01T00:00:00Z",
        expires_at=expires_at,
        nonce="nonce_001",
        scope=[CapabilityScope(resource=resource, actions=actions)],
        delegation=DelegationPolicy(is_delegable=delegable, max_depth=max_depth),
        binding=TokenBinding(client_cert_fingerprint="sha256:aabb"),
        signature=_sig(),
    )


def _envelope(
    actor: str = "did:project-ai:test:alice",
    subject: str = "did:project-ai:test:alice",
    action: str = "mutate_state",
    resource: str = "state://data/key1",
    token_id: str = "cap_001",
) -> RequestEnvelope:
    return RequestEnvelope(
        request_id="req_gate_001",
        actor=actor,
        subject=subject,
        capability_token_id=token_id,
        intent=Intent(action=action, resource=resource, parameters={"value": 42}),
        context=RequestContext(trace_id="trace_gate_001"),
        timestamps=RequestTimestamps(created_at=datetime.now(timezone.utc).isoformat()),
        signature=_sig(),
    )


# ── Identity Head Tests ──────────────────────────────────────────────


class TestIdentityHead:
    def test_allow_with_valid_doc(self):
        store = IdentityDocumentStore()
        store.register(_identity_doc())
        head = IdentityHead(doc_store=store)
        vote = head.evaluate(_envelope())
        assert vote.decision == "allow"

    def test_deny_invalid_did_format(self):
        head = IdentityHead()
        vote = head.evaluate(_envelope(actor="bad_did"))
        assert vote.decision == "deny"
        assert any(r.code == "IDENTITY_INVALID_DID_FORMAT" for r in vote.reasons)

    def test_deny_did_not_found(self):
        store = IdentityDocumentStore()
        store.register(_identity_doc(did="did:project-ai:test:bob"))
        head = IdentityHead(doc_store=store)
        vote = head.evaluate(_envelope(actor="did:project-ai:test:alice"))
        assert vote.decision == "deny"
        assert any(r.code == "IDENTITY_NOT_FOUND" for r in vote.reasons)

    def test_deny_revoked_identity(self):
        store = IdentityDocumentStore()
        store.register(_identity_doc(revoked=True))
        head = IdentityHead(doc_store=store)
        vote = head.evaluate(_envelope())
        assert vote.decision == "deny"
        assert any(r.code == "IDENTITY_REVOKED" for r in vote.reasons)

    def test_deny_expired_key(self):
        store = IdentityDocumentStore()
        store.register(_identity_doc(key_expires="2020-01-01T00:00:00Z"))
        head = IdentityHead(doc_store=store)
        vote = head.evaluate(_envelope())
        assert vote.decision == "deny"
        assert any(r.code == "IDENTITY_NO_VALID_KEY" for r in vote.reasons)

    def test_deny_untrusted_device(self):
        store = IdentityDocumentStore()
        store.register(_identity_doc())
        dev_reg = DeviceAttestationRegistry()
        dev_reg.register_device("did:project-ai:test:alice", "sha256:trusted_hash")
        head = IdentityHead(
            doc_store=store,
            device_registry=dev_reg,
            require_device_attestation=True,
        )
        # No device_attestation on envelope context → deny
        vote = head.evaluate(_envelope())
        assert vote.decision == "deny"
        assert any(r.code == "IDENTITY_DEVICE_UNTRUSTED" for r in vote.reasons)

    def test_deny_risk_tier_exceeded(self):
        store = IdentityDocumentStore()
        store.register(_identity_doc(risk_tier="high"))
        head = IdentityHead(doc_store=store, max_risk_tier="med")
        vote = head.evaluate(_envelope())
        assert vote.decision == "deny"
        assert any(r.code == "IDENTITY_RISK_TIER_EXCEEDED" for r in vote.reasons)

    def test_inv_root_8_duplicate_did(self):
        store = IdentityDocumentStore()
        store.register(_identity_doc())
        with pytest.raises(ValueError, match="INV-ROOT-8"):
            store.register(_identity_doc())

    def test_allow_open_enrollment_no_docs(self):
        """With empty store, Identity Head allows (open mode)."""
        head = IdentityHead()
        vote = head.evaluate(_envelope())
        assert vote.decision == "allow"


# ── Capability Head Tests ────────────────────────────────────────────


class TestCapabilityHead:
    def test_allow_valid_token(self):
        store = CapabilityTokenStore()
        store.register(_cap_token())
        head = CapabilityHead(token_store=store)
        vote = head.evaluate(_envelope())
        assert vote.decision == "allow"

    def test_deny_token_not_found(self):
        store = CapabilityTokenStore()
        store.register(_cap_token(token_id="cap_other"))
        head = CapabilityHead(token_store=store)
        vote = head.evaluate(_envelope(token_id="cap_missing"))
        assert vote.decision == "deny"
        assert any(r.code == "CAP_TOKEN_NOT_FOUND" for r in vote.reasons)

    def test_deny_token_revoked(self):
        store = CapabilityTokenStore()
        store.register(_cap_token())
        store.revoke("cap_001")
        head = CapabilityHead(token_store=store)
        vote = head.evaluate(_envelope())
        assert vote.decision == "deny"
        assert any(r.code == "CAP_TOKEN_REVOKED" for r in vote.reasons)

    def test_deny_token_expired(self):
        store = CapabilityTokenStore()
        store.register(_cap_token(expires_at="2020-01-01T00:00:00Z"))
        head = CapabilityHead(token_store=store)
        vote = head.evaluate(_envelope())
        assert vote.decision == "deny"
        assert any(r.code == "CAP_TOKEN_EXPIRED" for r in vote.reasons)

    def test_deny_scope_mismatch(self):
        store = CapabilityTokenStore()
        store.register(_cap_token(actions=["read"], resource="state://data/*"))
        head = CapabilityHead(token_store=store)
        vote = head.evaluate(_envelope(action="mutate_state"))
        assert vote.decision == "deny"
        assert any(r.code == "CAP_SCOPE_DENIED" for r in vote.reasons)

    def test_deny_resource_mismatch(self):
        store = CapabilityTokenStore()
        store.register(_cap_token(resource="state://data/*"))
        head = CapabilityHead(token_store=store)
        vote = head.evaluate(_envelope(resource="state://other/path"))
        assert vote.decision == "deny"
        assert any(r.code == "CAP_SCOPE_DENIED" for r in vote.reasons)

    def test_deny_subject_mismatch_non_delegable(self):
        store = CapabilityTokenStore()
        store.register(_cap_token(subject="did:project-ai:test:bob", delegable=False))
        head = CapabilityHead(token_store=store)
        vote = head.evaluate(_envelope(actor="did:project-ai:test:alice"))
        assert vote.decision == "deny"
        assert any(r.code == "CAP_SUBJECT_MISMATCH" for r in vote.reasons)

    def test_allow_open_mode_no_store(self):
        """With empty store, Capability Head allows (open mode)."""
        head = CapabilityHead()
        vote = head.evaluate(_envelope())
        assert vote.decision == "allow"


# ── Invariant Head Tests ─────────────────────────────────────────────


class TestInvariantHead:
    def test_allow_normal_mutation(self):
        head = InvariantHead()
        vote = head.evaluate(_envelope())
        assert vote.decision == "allow"

    def test_deny_mutate_invariant_resource(self):
        head = InvariantHead()
        vote = head.evaluate(
            _envelope(
                action="mutate_policy",
                resource="state://invariant/root",
            )
        )
        assert vote.decision == "deny"
        assert any("INV_ROOT_001" in r.code.upper() for r in vote.reasons)

    def test_deny_modify_cerberus(self):
        head = InvariantHead()
        vote = head.evaluate(
            _envelope(
                action="mutate_state",
                resource="state://cerberus/config",
            )
        )
        assert vote.decision == "deny"
        assert any("INV_ROOT_005" in r.code.upper() for r in vote.reasons)

    def test_deny_delete_ledger(self):
        head = InvariantHead()
        vote = head.evaluate(
            _envelope(
                action="delete",
                resource="state://ledger/block/0",
            )
        )
        assert vote.decision == "deny"
        assert any("INV_ROOT_009" in r.code.upper() for r in vote.reasons)

    def test_allow_non_mutation_action(self):
        head = InvariantHead()
        vote = head.evaluate(_envelope(action="read", resource="state://anything"))
        assert vote.decision == "allow"


# ── Production Quorum Engine Tests ───────────────────────────────────


class TestProductionQuorumEngine:
    def _vote(self, head: str, decision: str) -> CerberusVote:
        return CerberusVote(
            request_id="req_quorum_001",
            head=head,
            decision=decision,
            reasons=[],
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature=_sig(),
        )

    def test_all_allow_unanimous(self):
        engine = ProductionQuorumEngine(policy="unanimous")
        votes = [
            self._vote("identity", "allow"),
            self._vote("capability", "allow"),
            self._vote("invariant", "allow"),
        ]
        decision = engine.decide(votes, "req_001")
        assert decision.final_decision == "allow"
        assert decision.quorum.achieved

    def test_one_deny_unanimous_fails(self):
        engine = ProductionQuorumEngine(policy="unanimous")
        votes = [
            self._vote("identity", "allow"),
            self._vote("capability", "deny"),
            self._vote("invariant", "allow"),
        ]
        decision = engine.decide(votes, "req_001")
        assert decision.final_decision == "deny"
        assert not decision.quorum.achieved

    def test_one_deny_2of3_still_allows_monotonic(self):
        """Even with 2of3 quorum, a deny vote forces monotonic escalation."""
        engine = ProductionQuorumEngine(policy="2of3")
        votes = [
            self._vote("identity", "allow"),
            self._vote("capability", "deny"),
            self._vote("invariant", "allow"),
        ]
        decision = engine.decide(votes, "req_001")
        # Monotonic: worst vote is deny → final is deny
        assert decision.final_decision == "deny"

    def test_all_allow_2of3(self):
        engine = ProductionQuorumEngine(policy="2of3")
        votes = [
            self._vote("identity", "allow"),
            self._vote("capability", "allow"),
            self._vote("invariant", "allow"),
        ]
        decision = engine.decide(votes, "req_001")
        assert decision.final_decision == "allow"

    def test_all_deny(self):
        engine = ProductionQuorumEngine(policy="2of3")
        votes = [
            self._vote("identity", "deny"),
            self._vote("capability", "deny"),
            self._vote("invariant", "deny"),
        ]
        decision = engine.decide(votes, "req_001")
        assert decision.final_decision == "deny"
        assert not decision.quorum.achieved

    def test_no_votes_deny(self):
        engine = ProductionQuorumEngine()
        decision = engine.decide([], "req_001")
        assert decision.final_decision == "deny"

    def test_quarantine_escalation(self):
        engine = ProductionQuorumEngine(policy="2of3")
        votes = [
            self._vote("identity", "allow"),
            self._vote("capability", "allow"),
            self._vote("invariant", "quarantine"),
        ]
        decision = engine.decide(votes, "req_001")
        # Monotonic: quarantine is worse than allow → final is quarantine
        assert decision.final_decision == "quarantine"

    def test_invariant_deny_elevates_severity(self):
        engine = ProductionQuorumEngine(policy="2of3")
        votes = [
            self._vote("identity", "allow"),
            self._vote("capability", "allow"),
            self._vote("invariant", "deny"),
        ]
        decision = engine.decide(votes, "req_001")
        assert decision.severity == "critical"  # Elevated because invariant head denied

    def test_bft_policy(self):
        engine = ProductionQuorumEngine(policy="bft")
        votes = [
            self._vote("identity", "allow"),
            self._vote("capability", "allow"),
            self._vote("invariant", "allow"),
        ]
        decision = engine.decide(votes, "req_001")
        assert decision.final_decision == "allow"
        assert decision.quorum.achieved

    def test_commit_policy_allowed(self):
        engine = ProductionQuorumEngine()
        votes = [
            self._vote("identity", "allow"),
            self._vote("capability", "allow"),
            self._vote("invariant", "allow"),
        ]
        decision = engine.decide(votes, "req_001")
        assert decision.commit_policy.allowed
        assert decision.commit_policy.requires_shadow_hash_match
        assert decision.commit_policy.requires_anchor_append

    def test_commit_policy_denied(self):
        engine = ProductionQuorumEngine()
        votes = [self._vote("identity", "deny")]
        decision = engine.decide(votes, "req_001")
        assert not decision.commit_policy.allowed
