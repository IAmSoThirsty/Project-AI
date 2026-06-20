"""Governance vote and result types."""

from __future__ import annotations

from dataclasses import dataclass

from kernel import Decision, EvidenceBundle, InvariantViolation, Outcome


@dataclass(frozen=True)
class Vote:
    governor: str
    outcome: Outcome
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.governor.strip():
            raise ValueError("governor must not be empty")
        if self.outcome is not Outcome.ALLOW and not self.reason.strip():
            raise ValueError("non-ALLOW votes require a reason")


@dataclass(frozen=True)
class GovernanceResult:
    decision: Decision
    votes: tuple[Vote, ...]
    violations: tuple[InvariantViolation, ...]
    evidence: EvidenceBundle
