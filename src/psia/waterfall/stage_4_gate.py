"""PSIA Waterfall Stage 4 — Cerberus gate (Identity, Capability, Invariant heads)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from psia.gate.capability_head import CapabilityHead
from psia.gate.identity_head import IdentityHead
from psia.gate.invariant_head import InvariantHead
from psia.gate.quorum_engine import ProductionQuorumEngine
from psia.schemas.cerberus_decision import CerberusVote
from psia.schemas.identity import Signature
from psia.waterfall.engine import StageDecision, StageResult, WaterfallStage


def _head_vote_to_cerberus_vote(head_name: str, gate_vote: Any, request_id: str) -> CerberusVote:
    return CerberusVote(
        request_id=request_id,
        head=head_name,
        decision=gate_vote.decision,
        reasons=[r.code for r in gate_vote.reasons],
        timestamp=datetime.now(timezone.utc).isoformat(),
        signature=Signature(alg="ed25519", kid="gate", sig="internal"),
    )


class QuorumEngine:
    def __init__(self, policy: str = "unanimous") -> None:
        self._engine = ProductionQuorumEngine(policy=policy)

    def decide(self, votes: list[CerberusVote], request_id: str) -> Any:
        return self._engine.decide(votes, request_id)


class GateStage:
    def __init__(
        self,
        identity_head: IdentityHead | None = None,
        capability_head: CapabilityHead | None = None,
        invariant_head: InvariantHead | None = None,
        quorum_engine: QuorumEngine | None = None,
    ) -> None:
        self._identity = identity_head or IdentityHead()
        self._capability = capability_head or CapabilityHead()
        self._invariant = invariant_head or InvariantHead()
        self._quorum = quorum_engine or QuorumEngine()

    def evaluate(self, envelope: Any, prior_results: list[StageResult]) -> StageResult:
        id_vote = self._identity.evaluate(envelope)
        cap_vote = self._capability.evaluate(envelope)
        inv_vote = self._invariant.evaluate(envelope)

        cerberus_votes = [
            _head_vote_to_cerberus_vote("identity", id_vote, envelope.request_id),
            _head_vote_to_cerberus_vote("capability", cap_vote, envelope.request_id),
            _head_vote_to_cerberus_vote("invariant", inv_vote, envelope.request_id),
        ]

        decision = self._quorum.decide(cerberus_votes, envelope.request_id)

        if decision.final_decision == "allow":
            stage_decision = StageDecision.ALLOW
        elif decision.final_decision == "quarantine":
            stage_decision = StageDecision.QUARANTINE
        else:
            stage_decision = StageDecision.DENY

        return StageResult(
            stage=WaterfallStage.GATE,
            decision=stage_decision,
            metadata={"cerberus_decision": decision},
        )
