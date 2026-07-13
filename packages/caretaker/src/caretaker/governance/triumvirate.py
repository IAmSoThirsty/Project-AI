"""
caretaker.governance.triumvirate — Multi-authority consultation.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/governance/triumvirate.py``. No single authority
can actuate a response alone; a DENY from any authority blocks actuation.
Namespace note: this is Caretaker's internal consultation body — distinct
from ``governance.triumvirate`` (canonical Project-AI authority).

The three authorities:
  1. Justice   — prioritizes correctness and loss prevention (λ_L)
  2. Order     — prioritizes redundancy reduction and structure (λ_R)
  3. Mercy     — prioritizes decision flexibility and pragmatism (λ_D)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from caretaker.constitution import ConstitutionalWeights
from caretaker.governance.actualizer import ActualizerReport


class Vote(Enum):
    APPROVE = "approve"
    DENY = "deny"
    ABSTAIN = "abstain"


@dataclass
class TriumvirateVote:
    """A single authority's vote."""

    authority: str
    vote: Vote
    reason: str


@dataclass
class Authority:
    """One of the three constitutional authorities."""

    name: str
    weight_key: str  # which λ this authority guards

    def evaluate(self, report: ActualizerReport, weights: ConstitutionalWeights) -> TriumvirateVote:
        """Evaluate a report and cast a vote."""
        _ = weights
        if self.name == "Justice":
            # Justice guards Loss — high loss is a hard deny
            if report.c_loss > 0.7:
                return TriumvirateVote(
                    authority=self.name,
                    vote=Vote.DENY,
                    reason=f"Loss too high: {report.c_loss:.4f}",
                )
            if report.c_loss > 0.4:
                return TriumvirateVote(
                    authority=self.name,
                    vote=Vote.ABSTAIN,
                    reason=f"Loss elevated: {report.c_loss:.4f}",
                )
            return TriumvirateVote(
                authority=self.name,
                vote=Vote.APPROVE,
                reason=f"Loss acceptable: {report.c_loss:.4f}",
            )

        if self.name == "Order":
            # Order guards Redundancy — high redundancy is a hard deny
            if report.c_redundancy > 0.5:
                return TriumvirateVote(
                    authority=self.name,
                    vote=Vote.DENY,
                    reason=f"Redundancy too high: {report.c_redundancy:.4f}",
                )
            return TriumvirateVote(
                authority=self.name,
                vote=Vote.APPROVE,
                reason=f"Redundancy acceptable: {report.c_redundancy:.4f}",
            )

        if self.name == "Mercy":
            # Mercy guards DecisionCost — high decision cost means ambiguity
            if report.c_decision > 0.6:
                return TriumvirateVote(
                    authority=self.name,
                    vote=Vote.DENY,
                    reason=f"Decision cost too high: {report.c_decision:.4f}",
                )
            return TriumvirateVote(
                authority=self.name,
                vote=Vote.APPROVE,
                reason=f"Decision cost acceptable: {report.c_decision:.4f}",
            )

        return TriumvirateVote(
            authority=self.name,
            vote=Vote.ABSTAIN,
            reason="Unknown authority",
        )


class Triumvirate:
    """The three-authority consultation body.

    A response is actuated only if NO authority denies; ABSTAIN does not
    block.
    """

    def __init__(self, weights: ConstitutionalWeights | None = None) -> None:
        self.weights = weights or ConstitutionalWeights()
        self.authorities = [
            Authority(name="Justice", weight_key="lambda_l"),
            Authority(name="Order", weight_key="lambda_r"),
            Authority(name="Mercy", weight_key="lambda_d"),
        ]

    def consult(self, report: ActualizerReport) -> list[TriumvirateVote]:
        """All three authorities evaluate the report."""
        return [auth.evaluate(report, self.weights) for auth in self.authorities]

    def is_approved(self, votes: list[TriumvirateVote]) -> bool:
        """True if no authority denied. ABSTAINs don't block."""
        return all(v.vote != Vote.DENY for v in votes)

    @property
    def is_deadlocked(self) -> bool:
        """Deadlock is impossible while ABSTAIN doesn't block; the
        interface exists for future unanimous-approval extensions."""
        return False


__all__ = ["Authority", "Triumvirate", "TriumvirateVote", "Vote"]
