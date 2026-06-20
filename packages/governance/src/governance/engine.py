"""Fail-closed governance engine with invariant precedence and unilateral veto."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from governance.policy import Governor
from governance.types import GovernanceResult, Vote
from kernel import (
    ActionRequest,
    Decision,
    InvariantEngine,
    InvariantSeverity,
    Outcome,
    build_evidence_bundle,
)


class GovernanceEngine:
    def __init__(
        self,
        *,
        policy_version: str,
        governors: Sequence[Governor],
        invariants: InvariantEngine | None = None,
    ) -> None:
        if not policy_version.strip():
            raise ValueError("policy_version must not be empty")
        self._policy_version = policy_version
        self._governors = tuple(governors)
        self._invariants = invariants or InvariantEngine(())

    def decide(
        self,
        request: ActionRequest,
        state: Mapping[str, object] | None = None,
    ) -> GovernanceResult:
        current_state = state or {}
        violations = self._invariants.evaluate(request, current_state)
        blocking = tuple(
            violation
            for violation in violations
            if violation.severity >= InvariantSeverity.BLOCKING
        )
        if blocking:
            decision = Decision(
                Outcome.DENY,
                tuple(f"{item.invariant}: {item.reason}" for item in blocking),
                self._policy_version,
            )
            return GovernanceResult(
                decision,
                (),
                violations,
                build_evidence_bundle(request, decision),
            )

        votes = tuple(
            self._safe_vote(governor, request, current_state) for governor in self._governors
        )
        warnings = tuple(
            violation.reason
            for violation in violations
            if violation.severity == InvariantSeverity.WARNING
        )
        decision = self._resolve(votes, warnings)
        return GovernanceResult(
            decision,
            votes,
            violations,
            build_evidence_bundle(request, decision),
        )

    def _safe_vote(
        self,
        governor: Governor,
        request: ActionRequest,
        state: Mapping[str, object],
    ) -> Vote:
        try:
            vote = governor.evaluate(request, state)
        except Exception as error:
            return Vote(
                governor.name,
                Outcome.DENY,
                f"governor evaluator failed: {type(error).__name__}",
            )
        if vote.governor != governor.name:
            return Vote(governor.name, Outcome.DENY, "governor identity mismatch")
        return vote

    def _resolve(self, votes: tuple[Vote, ...], warnings: tuple[str, ...]) -> Decision:
        if not votes:
            return Decision(Outcome.DENY, ("no governors configured",), self._policy_version)
        denials = tuple(vote for vote in votes if vote.outcome is Outcome.DENY)
        if denials:
            return Decision(
                Outcome.DENY,
                tuple(f"{vote.governor}: {vote.reason}" for vote in denials),
                self._policy_version,
            )
        escalations = tuple(vote for vote in votes if vote.outcome is Outcome.ESCALATE)
        reasons = warnings + tuple(f"{vote.governor}: {vote.reason}" for vote in escalations)
        if reasons:
            return Decision(Outcome.ESCALATE, reasons, self._policy_version)
        return Decision(Outcome.ALLOW, (), self._policy_version)
