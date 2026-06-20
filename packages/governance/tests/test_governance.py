from __future__ import annotations

from collections.abc import Mapping

import pytest

from governance import GovernanceEngine, Rule, RuleGovernor, Vote
from kernel import (
    ActionRequest,
    InvariantEngine,
    InvariantSeverity,
    InvariantViolation,
    Outcome,
)


def request() -> ActionRequest:
    return ActionRequest("a-1", "operator", "write", "record:1")


def governor(name: str, outcome: Outcome, reason: str = "") -> RuleGovernor:
    if outcome is Outcome.ALLOW:
        return RuleGovernor(name, ())
    return RuleGovernor(
        name,
        (Rule("rule", lambda _request, _state: False, outcome, reason or "failed"),),
    )


def test_all_allow_produces_hash_bound_allow() -> None:
    result = GovernanceEngine(
        policy_version="v1",
        governors=(governor("one", Outcome.ALLOW), governor("two", Outcome.ALLOW)),
    ).decide(request())
    assert result.decision.outcome is Outcome.ALLOW
    assert result.evidence.action_id == "a-1"
    assert len(result.evidence.bundle_sha256) == 64


def test_unilateral_veto_overrides_allow_and_escalate() -> None:
    engine = GovernanceEngine(
        policy_version="v1",
        governors=(
            governor("allow", Outcome.ALLOW),
            governor("review", Outcome.ESCALATE, "human review"),
            governor("veto", Outcome.DENY, "unsafe"),
        ),
    )
    result = engine.decide(request())
    assert result.decision.outcome is Outcome.DENY
    assert result.decision.reasons == ("veto: unsafe",)


def test_escalation_and_warning_are_preserved() -> None:
    def warning(_request: ActionRequest, _state: Mapping[str, object]) -> InvariantViolation:
        return InvariantViolation("risk", "uncertain", InvariantSeverity.WARNING)

    result = GovernanceEngine(
        policy_version="v1",
        governors=(governor("review", Outcome.ESCALATE, "approval required"),),
        invariants=InvariantEngine((warning,)),
    ).decide(request())
    assert result.decision.outcome is Outcome.ESCALATE
    assert result.decision.reasons == ("uncertain", "review: approval required")


def test_blocking_invariant_runs_before_governors() -> None:
    called = False

    class TrackingGovernor:
        name = "tracking"

        def evaluate(self, _request: ActionRequest, _state: Mapping[str, object]) -> Vote:
            nonlocal called
            called = True
            return Vote(self.name, Outcome.ALLOW)

    def blocking(_request: ActionRequest, _state: Mapping[str, object]) -> InvariantViolation:
        return InvariantViolation("scope", "blocked", InvariantSeverity.BLOCKING)

    result = GovernanceEngine(
        policy_version="v1",
        governors=(TrackingGovernor(),),
        invariants=InvariantEngine((blocking,)),
    ).decide(request())
    assert result.decision.outcome is Outcome.DENY
    assert called is False
    assert result.votes == ()


def test_missing_broken_or_impersonating_governor_denies() -> None:
    assert (
        GovernanceEngine(policy_version="v1", governors=()).decide(request()).decision.outcome
        is Outcome.DENY
    )

    class BrokenGovernor:
        name = "broken"

        def evaluate(self, _request: ActionRequest, _state: Mapping[str, object]) -> Vote:
            raise RuntimeError("fault")

    class ImpersonatingGovernor:
        name = "expected"

        def evaluate(self, _request: ActionRequest, _state: Mapping[str, object]) -> Vote:
            return Vote("other", Outcome.ALLOW)

    broken = GovernanceEngine(policy_version="v1", governors=(BrokenGovernor(),)).decide(request())
    mismatch = GovernanceEngine(policy_version="v1", governors=(ImpersonatingGovernor(),)).decide(
        request()
    )
    assert broken.decision.outcome is Outcome.DENY
    assert mismatch.decision.reasons == ("expected: governor identity mismatch",)


def test_rule_and_vote_validation() -> None:
    with pytest.raises(ValueError, match="cannot be ALLOW"):
        Rule("bad", lambda _request, _state: False, Outcome.ALLOW, "bad")
    with pytest.raises(ValueError, match="name"):
        RuleGovernor("", ())
    with pytest.raises(ValueError, match="governor"):
        Vote("", Outcome.ALLOW)
    with pytest.raises(ValueError, match="reason"):
        Vote("one", Outcome.DENY)
    with pytest.raises(ValueError, match="policy_version"):
        GovernanceEngine(policy_version="", governors=())
