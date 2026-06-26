"""Tests for ``governance.triumvirate`` (three-vote consensus governor)."""

from __future__ import annotations

import pytest
from governance.triumvirate import TriumvirateGovernor

from governance import GovernanceEngine, Quorum, Rule, RuleGovernor, TriumvirateError
from kernel import ActionRequest, Outcome


def request() -> ActionRequest:
    return ActionRequest("a-1", "operator", "write", "record:1")


def sub(name: str, outcome: Outcome, reason: str = "") -> RuleGovernor:
    if outcome is Outcome.ALLOW:
        return RuleGovernor(name, ())
    return RuleGovernor(
        name,
        (Rule("rule", lambda _request, _state: False, outcome, reason or "failed"),),
    )


def test_triumvirate_requires_three_unique_subgovernors() -> None:
    a = sub("a", Outcome.ALLOW)
    b = sub("b", Outcome.ALLOW)
    with pytest.raises(TriumvirateError, match="exactly 3"):
        TriumvirateGovernor(name="t", governors=(a, b))
    with pytest.raises(TriumvirateError, match="unique"):
        TriumvirateGovernor(
            name="t",
            governors=(
                sub("dup", Outcome.ALLOW),
                sub("dup", Outcome.ALLOW),
                sub("dup", Outcome.ALLOW),
            ),
        )


def test_triumvirate_requires_nonempty_name() -> None:
    a = sub("a", Outcome.ALLOW)
    b = sub("b", Outcome.ALLOW)
    c = sub("c", Outcome.ALLOW)
    with pytest.raises(TriumvirateError, match="name"):
        TriumvirateGovernor(name="", governors=(a, b, c))


def test_majority_allows_when_two_of_three_allow() -> None:
    gov = TriumvirateGovernor(
        name="t",
        governors=(sub("a", Outcome.ALLOW), sub("b", Outcome.ALLOW), sub("c", Outcome.DENY, "x")),
        quorum=Quorum.MAJORITY,
    )
    vote = gov.evaluate(request(), state={})
    assert vote.governor == "t"
    assert vote.outcome is Outcome.DENY  # any DENY vetoes (fail-closed)


def test_majority_allows_two_allow_one_escalate() -> None:
    gov = TriumvirateGovernor(
        name="t",
        governors=(
            sub("a", Outcome.ALLOW),
            sub("b", Outcome.ALLOW),
            sub("c", Outcome.ESCALATE, "needs review"),
        ),
        quorum=Quorum.MAJORITY,
    )
    vote = gov.evaluate(request(), state={})
    assert vote.outcome is Outcome.ALLOW  # 2/3 allow passes majority


def test_majority_escalates_when_only_one_allows() -> None:
    gov = TriumvirateGovernor(
        name="t",
        governors=(
            sub("a", Outcome.ALLOW),
            sub("b", Outcome.ESCALATE, "review"),
            sub("c", Outcome.ESCALATE, "verify"),
        ),
        quorum=Quorum.MAJORITY,
    )
    vote = gov.evaluate(request(), state={})
    assert vote.outcome is Outcome.ESCALATE


def test_unanimous_requires_all_three_allows() -> None:
    gov = TriumvirateGovernor(
        name="t",
        governors=(
            sub("a", Outcome.ALLOW),
            sub("b", Outcome.ALLOW),
            sub("c", Outcome.ESCALATE, "x"),
        ),
        quorum=Quorum.UNANIMOUS,
    )
    vote = gov.evaluate(request(), state={})
    assert vote.outcome is Outcome.ESCALATE


def test_unanimous_allows_when_all_three_allow() -> None:
    gov = TriumvirateGovernor(
        name="t",
        governors=(sub("a", Outcome.ALLOW), sub("b", Outcome.ALLOW), sub("c", Outcome.ALLOW)),
        quorum=Quorum.UNANIMOUS,
    )
    vote = gov.evaluate(request(), state={})
    assert vote.outcome is Outcome.ALLOW


def test_supermajority_denies_when_zero_allows() -> None:
    gov = TriumvirateGovernor(
        name="t",
        governors=(
            sub("a", Outcome.ESCALATE, "x"),
            sub("b", Outcome.ESCALATE, "y"),
            sub("c", Outcome.ESCALATE, "z"),
        ),
        quorum=Quorum.SUPERMAJORITY,
    )
    vote = gov.evaluate(request(), state={})
    assert vote.outcome is Outcome.DENY


def test_supermajority_escalates_when_only_one_allows() -> None:
    gov = TriumvirateGovernor(
        name="t",
        governors=(
            sub("a", Outcome.ALLOW),
            sub("b", Outcome.ESCALATE, "x"),
            sub("c", Outcome.ESCALATE, "y"),
        ),
        quorum=Quorum.SUPERMAJORITY,
    )
    vote = gov.evaluate(request(), state={})
    assert vote.outcome is Outcome.ESCALATE


def test_vote_reason_includes_sub_vote_audit() -> None:
    gov = TriumvirateGovernor(
        name="audit-test",
        governors=(sub("a", Outcome.ALLOW), sub("b", Outcome.ALLOW), sub("c", Outcome.ALLOW)),
        quorum=Quorum.MAJORITY,
    )
    vote = gov.evaluate(request(), state={})
    assert "a:ALLOW" in vote.reason
    assert "b:ALLOW" in vote.reason
    assert "c:ALLOW" in vote.reason
    assert vote.governor == "audit-test"


def test_triumvirate_integrates_with_governance_engine() -> None:
    """Triumvirate wrapped in GovernanceEngine must obey fail-closed rules."""
    tri = TriumvirateGovernor(
        name="triumvirate",
        governors=(
            sub("safety", Outcome.ALLOW),
            sub("policy", Outcome.ALLOW),
            sub("capability", Outcome.ALLOW),
        ),
        quorum=Quorum.UNANIMOUS,
    )
    engine = GovernanceEngine(policy_version="v1", governors=(tri,))
    result = engine.decide(request())
    assert result.decision.outcome is Outcome.ALLOW
    assert len(result.votes) == 1
    assert result.votes[0].governor == "triumvirate"


def test_sub_governor_property_exposes_three_governors() -> None:
    a = sub("a", Outcome.ALLOW)
    b = sub("b", Outcome.ALLOW)
    c = sub("c", Outcome.ALLOW)
    gov = TriumvirateGovernor(name="t", governors=(a, b, c))
    assert gov.sub_governors == (a, b, c)
    assert gov.quorum is Quorum.MAJORITY  # default


def test_deny_veto_overrides_majority() -> None:
    """A single DENY must veto even with 2 ALLOW votes — fail-closed."""
    gov = TriumvirateGovernor(
        name="t",
        governors=(
            sub("a", Outcome.ALLOW),
            sub("b", Outcome.ALLOW),
            sub("c", Outcome.DENY, "hard rule violation"),
        ),
        quorum=Quorum.MAJORITY,
    )
    vote = gov.evaluate(request(), state={})
    assert vote.outcome is Outcome.DENY
    assert "hard rule violation" in vote.reason
