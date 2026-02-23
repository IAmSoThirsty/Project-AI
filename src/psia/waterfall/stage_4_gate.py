"""
Stage 4: Gate — Cerberus Triple-Head Evaluation.

Runs the three Cerberus heads (Identity, Capability, Invariant) and
collects their votes.  In Phase 1, heads are stubs that always allow.
In Phase 3, they will be replaced by real implementations wrapping
the existing ``src/cerberus/sase/governance/`` modules.

The QuorumEngine determines the final CerberusDecision based on the
configured quorum policy (unanimous, 2of3, simple).
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Protocol

from psia.schemas.cerberus_decision import (
    CerberusDecision,
    CerberusVote,
    CommitPolicy,
    ConstraintsApplied,
    DenyReason,
    QuorumInfo,
)
from psia.schemas.identity import Signature
from psia.waterfall.engine import StageDecision, StageResult, WaterfallStage

logger = logging.getLogger(__name__)


class CerberusHead(Protocol):
    """Protocol for a single Cerberus head."""

    def evaluate(self, envelope: Any) -> CerberusVote: ...


class StubIdentityHead:
    """Phase 1 stub — always allows after basic DID format check."""

    def evaluate(self, envelope: Any) -> CerberusVote:
        decision: Literal["allow", "deny", "quarantine"] = "allow"
        reasons: list[DenyReason] = []

        if not envelope.actor.startswith("did:project-ai:"):
            decision = "deny"
            reasons.append(DenyReason(code="IDENTITY_INVALID_DID", detail=f"actor DID '{envelope.actor}' is not did:project-ai:"))

        return CerberusVote(
            request_id=envelope.request_id,
            head="identity",
            decision=decision,
            reasons=reasons,
            constraints_applied=ConstraintsApplied(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature=Signature(alg="ed25519", kid="cerberus_id_k1", sig="stub_identity_sig"),
        )


class StubCapabilityHead:
    """Phase 1 stub — always allows (scope checking deferred to Phase 3)."""

    def evaluate(self, envelope: Any) -> CerberusVote:
        return CerberusVote(
            request_id=envelope.request_id,
            head="capability",
            decision="allow",
            reasons=[],
            constraints_applied=ConstraintsApplied(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature=Signature(alg="ed25519", kid="cerberus_cap_k1", sig="stub_capability_sig"),
        )


class StubInvariantHead:
    """Phase 1 stub — always allows (invariant checking deferred to Phase 3)."""

    def evaluate(self, envelope: Any) -> CerberusVote:
        return CerberusVote(
            request_id=envelope.request_id,
            head="invariant",
            decision="allow",
            reasons=[],
            constraints_applied=ConstraintsApplied(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature=Signature(alg="ed25519", kid="cerberus_inv_k1", sig="stub_invariant_sig"),
        )


class QuorumEngine:
    """Quorum decision engine for Cerberus votes.

    Supports three quorum policies:
    - ``unanimous``: all 3 heads must allow
    - ``2of3``: at least 2 of 3 heads must allow
    - ``simple``: majority wins (same as 2of3 for 3 heads)
    """

    def __init__(self, quorum_policy: str = "2of3") -> None:
        self.quorum_policy = quorum_policy

    def decide(self, votes: list[CerberusVote], request_id: str) -> CerberusDecision:
        """Produce a CerberusDecision from collected votes.

        Args:
            votes: List of CerberusVote from each head
            request_id: The request being decided

        Returns:
            Final CerberusDecision
        """
        allow_count = sum(1 for v in votes if v.decision == "allow")
        deny_count = sum(1 for v in votes if v.decision == "deny")
        quarantine_count = sum(1 for v in votes if v.decision == "quarantine")

        # Determine quorum achievement
        total = len(votes)
        if self.quorum_policy == "unanimous":
            quorum_achieved = allow_count == total
        elif self.quorum_policy in ("2of3", "simple"):
            quorum_achieved = allow_count >= 2
        else:
            quorum_achieved = allow_count > total // 2

        # Monotonic strictness: final decision is the most restrictive
        if deny_count > 0:
            final_decision: Literal["allow", "deny", "quarantine"] = "deny"
        elif quarantine_count > 0:
            final_decision = "quarantine"
        elif quorum_achieved:
            final_decision = "allow"
        else:
            final_decision = "deny"

        # Determine severity from votes
        if final_decision == "deny":
            severity: Literal["low", "med", "high", "critical", "fatal"] = "high"
        elif final_decision == "quarantine":
            severity = "med"
        else:
            severity = "low"

        return CerberusDecision(
            request_id=request_id,
            severity=severity,
            final_decision=final_decision,
            votes=votes,
            quorum=QuorumInfo(
                required=self.quorum_policy if self.quorum_policy in ("unanimous", "2of3", "simple") else "2of3",
                achieved=quorum_achieved,
                voters=[f"node_{i}" for i in range(total)],
            ),
            commit_policy=CommitPolicy(
                allowed=(final_decision == "allow"),
                requires_shadow_hash_match=True,
                requires_anchor_append=True,
            ),
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature_set=[
                Signature(alg="ed25519", kid=f"quorum_k{i}", sig=f"quorum_sig_{i}")
                for i in range(total)
            ],
        )


class GateStage:
    """Stage 4: Cerberus Gate evaluation.

    Runs three heads, collects votes, and uses the QuorumEngine
    to produce a final CerberusDecision.
    """

    def __init__(
        self,
        *,
        identity_head: CerberusHead | None = None,
        capability_head: CerberusHead | None = None,
        invariant_head: CerberusHead | None = None,
        quorum_engine: QuorumEngine | None = None,
    ) -> None:
        self.identity_head = identity_head or StubIdentityHead()
        self.capability_head = capability_head or StubCapabilityHead()
        self.invariant_head = invariant_head or StubInvariantHead()
        self.quorum_engine = quorum_engine or QuorumEngine()

    def evaluate(self, envelope, prior_results: list[StageResult]) -> StageResult:
        """Run all three Cerberus heads and produce a decision.

        Args:
            envelope: RequestEnvelope to evaluate
            prior_results: Results from prior stages

        Returns:
            StageResult with CerberusDecision in metadata
        """
        votes: list[CerberusVote] = []

        # Collect votes from each head
        for head_name, head_impl in [
            ("identity", self.identity_head),
            ("capability", self.capability_head),
            ("invariant", self.invariant_head),
        ]:
            try:
                vote = head_impl.evaluate(envelope)
                votes.append(vote)
            except Exception as exc:
                logger.exception("Cerberus %s head failed", head_name)
                votes.append(CerberusVote(
                    request_id=envelope.request_id,
                    head=head_name,
                    decision="deny",
                    reasons=[DenyReason(code="HEAD_EXCEPTION", detail=str(exc))],
                    constraints_applied=ConstraintsApplied(),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    signature=Signature(alg="ed25519", kid=f"cerberus_{head_name}_k1", sig="error_sig"),
                ))

        # Produce decision
        decision = self.quorum_engine.decide(votes, envelope.request_id)

        # Map to StageDecision
        stage_decision_map = {
            "allow": StageDecision.ALLOW,
            "deny": StageDecision.DENY,
            "quarantine": StageDecision.QUARANTINE,
        }
        stage_decision = stage_decision_map.get(decision.final_decision, StageDecision.DENY)

        reasons = [
            f"{v.head}={v.decision}"
            + (f" ({', '.join(r.code for r in v.reasons)})" if v.reasons else "")
            for v in votes
        ]
        reasons.append(f"quorum={decision.quorum.required} achieved={decision.quorum.achieved}")

        return StageResult(
            stage=WaterfallStage.GATE,
            decision=stage_decision,
            reasons=reasons,
            metadata={"cerberus_decision": decision},
        )


__all__ = [
    "CerberusHead",
    "StubIdentityHead",
    "StubCapabilityHead",
    "StubInvariantHead",
    "QuorumEngine",
    "GateStage",
]
