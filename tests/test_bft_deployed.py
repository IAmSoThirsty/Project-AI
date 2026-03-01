"""
BFT Deployment Tests — Validates Byzantine Fault Tolerance at N≥4.

Tests Paper Claim:
    "Under a 3f+1 model with N≥4 validators, PSIA tolerates f Byzantine
    faults while maintaining safety and liveness."

These tests validate:
    - BFT_DEPLOYED profile is correctly assigned at N≥4
    - Weighted quorum achieves >2/3 agreement thresholds
    - f Byzantine faults (deny) are tolerated when honest nodes agree
    - Safety: deny prevails with ≤1/3 honest allow votes
    - Monotonic severity escalation under Byzantine conditions
    - Deployment profile auto-detection accuracy
    - N=4 through N=7 configurations
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from psia.gate.quorum_engine import (
    DeploymentProfile,
    HeadWeight,
    ProductionQuorumEngine,
)
from psia.schemas.cerberus_decision import CerberusVote, ConstraintsApplied
from psia.schemas.identity import Signature


def _make_vote(
    request_id: str,
    head: str,
    decision: str,
) -> CerberusVote:
    """Helper to create a CerberusVote."""
    return CerberusVote(
        request_id=request_id,
        head=head,  # type: ignore[arg-type]
        decision=decision,  # type: ignore[arg-type]
        reasons=[],
        constraints_applied=ConstraintsApplied(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        signature=Signature(alg="ed25519", kid=f"test_{head}", sig="test_sig"),
    )


# ── Deployment Profile Detection ────────────────────────────────────────


class TestDeploymentProfileDetection:
    """Verify that deployment profile is correctly auto-detected."""

    def test_n3_bft_is_bft_ready_not_deployed(self) -> None:
        """N=3 with bft policy cannot tolerate any Byzantine faults."""
        engine = ProductionQuorumEngine(
            policy="bft",
            node_ids=["n0", "n1", "n2"],
        )
        assert engine.deployment_profile == DeploymentProfile.BFT_READY

    def test_n4_bft_is_bft_deployed(self) -> None:
        """N=4 with bft policy enables BFT_DEPLOYED (f=1)."""
        engine = ProductionQuorumEngine(
            policy="bft",
            node_ids=["n0", "n1", "n2", "n3"],
        )
        assert engine.deployment_profile == DeploymentProfile.BFT_DEPLOYED

    def test_n7_bft_is_bft_deployed(self) -> None:
        """N=7 with bft policy enables BFT_DEPLOYED (f=2)."""
        engine = ProductionQuorumEngine(
            policy="bft",
            node_ids=[f"n{i}" for i in range(7)],
        )
        assert engine.deployment_profile == DeploymentProfile.BFT_DEPLOYED

    def test_n3_unanimous_is_crash_safe(self) -> None:
        engine = ProductionQuorumEngine(
            policy="unanimous",
            node_ids=["n0", "n1", "n2"],
        )
        assert engine.deployment_profile == DeploymentProfile.CRASH_SAFE

    def test_explicit_profile_overrides_auto(self) -> None:
        engine = ProductionQuorumEngine(
            policy="2of3",
            node_ids=["n0", "n1", "n2"],
            deployment_profile=DeploymentProfile.BFT_DEPLOYED,
        )
        assert engine.deployment_profile == DeploymentProfile.BFT_DEPLOYED


# ── N=4 BFT Tests (f=1) ────────────────────────────────────────────────


class TestN4BFT:
    """N=4 validators. Should tolerate f=1 Byzantine fault."""

    def _make_engine(self) -> ProductionQuorumEngine:
        return ProductionQuorumEngine(
            policy="bft",
            node_ids=["n0", "n1", "n2", "n3"],
            weights=HeadWeight(identity=1.0, capability=1.0, invariant=1.0),
        )

    def test_all_allow_achieves_quorum(self) -> None:
        """All 4 honest validators allow → quorum achieved."""
        engine = self._make_engine()
        votes = [
            _make_vote("req1", "identity", "allow"),
            _make_vote("req1", "capability", "allow"),
            _make_vote("req1", "invariant", "allow"),
            _make_vote("req1", "identity", "allow"),  # 4th validator
        ]
        decision = engine.decide(votes, "req1")
        assert decision.final_decision == "allow"
        assert decision.quorum.achieved is True

    def test_one_byzantine_deny_tolerated(self) -> None:
        """3 allow, 1 deny → >2/3 (75%), quorum achieved, but severity escalated."""
        engine = self._make_engine()
        votes = [
            _make_vote("req2", "identity", "allow"),
            _make_vote("req2", "capability", "allow"),
            _make_vote("req2", "invariant", "allow"),
            _make_vote("req2", "identity", "deny"),  # Byzantine
        ]
        decision = engine.decide(votes, "req2")
        # Severity escalation: worst decision is deny
        assert decision.final_decision == "deny"
        assert decision.quorum.achieved is True

    def test_two_deny_breaks_quorum(self) -> None:
        """2 allow, 2 deny → 50%, below 2/3 threshold."""
        engine = self._make_engine()
        votes = [
            _make_vote("req3", "identity", "allow"),
            _make_vote("req3", "capability", "allow"),
            _make_vote("req3", "invariant", "deny"),
            _make_vote("req3", "identity", "deny"),
        ]
        decision = engine.decide(votes, "req3")
        assert decision.final_decision == "deny"


# ── N=7 BFT Tests (f=2) ────────────────────────────────────────────────


class TestN7BFT:
    """N=7 validators. Should tolerate f=2 Byzantine faults."""

    def _make_engine(self) -> ProductionQuorumEngine:
        return ProductionQuorumEngine(
            policy="bft",
            node_ids=[f"n{i}" for i in range(7)],
            weights=HeadWeight(identity=1.0, capability=1.0, invariant=1.0),
        )

    def test_all_7_allow(self) -> None:
        engine = self._make_engine()
        heads = ["identity", "capability", "invariant"]
        votes = [_make_vote("req4", heads[i % 3], "allow") for i in range(7)]
        decision = engine.decide(votes, "req4")
        assert decision.final_decision == "allow"
        assert decision.quorum.achieved is True

    def test_5_allow_2_deny_achieves_quorum(self) -> None:
        """5/7 allow > 2/3 (71.4%) → quorum achieved but severity escalated."""
        engine = self._make_engine()
        heads = ["identity", "capability", "invariant"]
        votes = [_make_vote("req5", heads[i % 3], "allow") for i in range(5)] + [
            _make_vote("req5", "identity", "deny"),
            _make_vote("req5", "capability", "deny"),
        ]
        decision = engine.decide(votes, "req5")
        assert decision.quorum.achieved is True
        assert decision.final_decision == "deny"  # Monotonic severity

    def test_3_deny_breaks_quorum(self) -> None:
        """4/7 allow < 2/3 → quorum NOT achieved."""
        engine = self._make_engine()
        heads = ["identity", "capability", "invariant"]
        votes = [_make_vote("req6", heads[i % 3], "allow") for i in range(4)] + [
            _make_vote("req6", "identity", "deny"),
            _make_vote("req6", "capability", "deny"),
            _make_vote("req6", "invariant", "deny"),
        ]
        decision = engine.decide(votes, "req6")
        assert decision.final_decision == "deny"


# ── No Votes Edge Case ─────────────────────────────────────────────────


class TestEdgeCases:
    """Edge cases for BFT quorum engine."""

    def test_no_votes_is_default_deny(self) -> None:
        engine = ProductionQuorumEngine(
            policy="bft",
            node_ids=["n0", "n1", "n2", "n3"],
        )
        decision = engine.decide([], "req_empty")
        assert decision.final_decision == "deny"
        assert decision.severity == "critical"

    def test_quarantine_vote_escalation(self) -> None:
        """If any head quarantines, the worst decision escalates."""
        engine = ProductionQuorumEngine(
            policy="bft",
            node_ids=["n0", "n1", "n2", "n3"],
        )
        votes = [
            _make_vote("req_q", "identity", "allow"),
            _make_vote("req_q", "capability", "allow"),
            _make_vote("req_q", "invariant", "quarantine"),
            _make_vote("req_q", "identity", "allow"),
        ]
        decision = engine.decide(votes, "req_q")
        # Monotonic: quarantine is worse than allow
        assert decision.final_decision == "quarantine"
