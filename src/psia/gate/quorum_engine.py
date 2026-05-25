"""PSIA quorum engine — monotonic vote aggregation, severity escalation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from psia.schemas.cerberus_decision import CommitPolicy, CerberusVote, QuorumInfo

_DECISION_ORDER = {"allow": 0, "quarantine": 1, "deny": 2}


class DeploymentProfile(str, Enum):
    CRASH_SAFE = "crash_safe"
    BFT_READY = "bft_ready"
    BFT_DEPLOYED = "bft_deployed"


@dataclass
class HeadWeight:
    identity: float = 1.0
    capability: float = 1.0
    invariant: float = 1.0


class ProductionQuorumEngine:
    def __init__(
        self,
        policy: str = "unanimous",
        node_ids: list[str] | None = None,
        weights: HeadWeight | None = None,
        deployment_profile: DeploymentProfile | None = None,
    ) -> None:
        self._policy = policy
        self._node_ids = list(node_ids) if node_ids is not None else ["node0", "node1", "node2"]
        self._weights = weights or HeadWeight()
        self._deployment_profile_override = deployment_profile

    @property
    def policy(self) -> str:
        return self._policy

    @property
    def node_ids(self) -> list[str]:
        return list(self._node_ids)

    @property
    def weights(self) -> HeadWeight:
        return self._weights

    @property
    def deployment_profile(self) -> DeploymentProfile:
        if self._deployment_profile_override is not None:
            return self._deployment_profile_override
        n = len(self._node_ids)
        if self._policy == "bft":
            if n >= 4:
                return DeploymentProfile.BFT_DEPLOYED
            return DeploymentProfile.BFT_READY
        return DeploymentProfile.CRASH_SAFE

    def decide(self, votes: list[CerberusVote], request_id: str) -> Any:
        if not votes:
            decision = "deny"
            quorum_achieved = False
        else:
            worst_rank = max(_DECISION_ORDER.get(v.decision, 2) for v in votes)
            decision = next(
                k for k, v in _DECISION_ORDER.items() if v == worst_rank
            )
            quorum_achieved = self._compute_quorum_achieved(decision, votes)

        severity = self._compute_severity(decision, votes, no_votes=(not votes))
        commit_policy = CommitPolicy(
            allowed=(decision == "allow"),
            requires_shadow_hash_match=True,
            requires_anchor_append=True,
        )

        return _QuorumDecision(
            request_id=request_id,
            final_decision=decision,
            severity=severity,
            votes=list(votes),
            quorum=QuorumInfo(
                required=self._policy,
                achieved=quorum_achieved,
                voters=[v.head for v in votes],
            ),
            commit_policy=commit_policy,
        )

    def _compute_quorum_achieved(self, decision: str, votes: list[CerberusVote]) -> bool:
        if self._policy == "bft":
            n = len(votes)
            if n == 0:
                return False
            allow_count = sum(1 for v in votes if v.decision == "allow")
            return (allow_count / n) >= (2 / 3)
        return decision == "allow"

    def _compute_severity(self, final: str, votes: list[CerberusVote], no_votes: bool = False) -> str:
        if no_votes:
            return "critical"
        if final == "allow":
            return "low"
        if final == "quarantine":
            return "medium"
        if any(v.head == "invariant" and v.decision == "deny" for v in votes):
            return "critical"
        return "high"


@dataclass
class _QuorumDecision:
    request_id: str
    final_decision: str
    severity: str
    votes: list[CerberusVote]
    quorum: QuorumInfo
    commit_policy: CommitPolicy

    @property
    def is_allowed(self) -> bool:
        return self.final_decision == "allow"

    @property
    def final_verdict(self) -> str:
        return self.final_decision
