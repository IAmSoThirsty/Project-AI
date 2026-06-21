from __future__ import annotations

from datetime import timedelta

import pytest

from capability import CapabilityAuthority
from execution import ExecutionGate
from governance import GovernanceEngine, Rule, RuleGovernor
from kernel import EventSpine, Outcome
from swr import RECORD_OPERATION, Scenario, ScenarioLibrary, SovereignWarRoom


def stack(*, allow: bool = True) -> tuple[SovereignWarRoom, CapabilityAuthority]:
    rules: tuple[Rule, ...] = (
        () if allow else (Rule("deny", lambda _request, _state: False, Outcome.DENY, "blocked"),)
    )
    governance = GovernanceEngine(
        policy_version="v1",
        governors=(RuleGovernor("primary", rules),),
    )
    authority = CapabilityAuthority(
        b"s" * 32,
        issuer="project-ai",
        token_id_factory=iter(f"swr-{index}" for index in range(10)).__next__,
    )
    gate = ExecutionGate(
        governance=governance,
        capabilities=authority,
        events=EventSpine(),
    )
    return SovereignWarRoom(gate), authority


def token(authority: CapabilityAuthority, scenario: Scenario) -> str:
    return authority.issue(
        subject="system-1",
        operation=RECORD_OPERATION,
        resource=f"swr:{scenario.scenario_id}",
        ttl=timedelta(minutes=5),
    )


def test_library_is_deterministic_and_spans_five_rounds() -> None:
    scenarios = ScenarioLibrary.all()
    assert [scenario.round_number for scenario in scenarios] == [1, 2, 3, 4, 5]
    assert scenarios[0].scenario_id == scenarios[0].scenario_id
    assert ScenarioLibrary.round(3) == (scenarios[2],)
    with pytest.raises(ValueError, match="1-5"):
        ScenarioLibrary.round(0)


def test_evaluation_is_deterministic() -> None:
    war_room, _authority = stack()
    scenario = ScenarioLibrary.round(3)[0]
    first = war_room.evaluate(
        scenario,
        system_id="system-1",
        decision="deny_unverified_authority",
    )
    second = war_room.evaluate(
        scenario,
        system_id="system-1",
        decision="deny_unverified_authority",
    )
    partial = war_room.evaluate(scenario, system_id="system-1", decision="deny_authority")
    assert first == second
    assert first.success is True
    assert first.score == 100.0
    assert 0.0 < partial.score < 100.0


def test_governed_record_requires_allow_and_exact_scope() -> None:
    war_room, authority = stack()
    scenario = ScenarioLibrary.round(1)[0]
    result = war_room.run_governed(
        scenario,
        system_id="system-1",
        decision=scenario.expected_decision,
        capability_token=token(authority, scenario),
    )
    assert result.outcome is Outcome.ALLOW
    assert len(war_room.results()) == 1

    wrong = authority.issue(
        subject="system-1",
        operation=RECORD_OPERATION,
        resource="swr:other",
        ttl=timedelta(minutes=5),
    )
    denied = war_room.run_governed(
        scenario,
        system_id="system-1",
        decision="other",
        capability_token=wrong,
    )
    assert denied.outcome is Outcome.DENY
    assert len(war_room.results()) == 1


def test_governance_denial_records_nothing() -> None:
    war_room, authority = stack(allow=False)
    scenario = ScenarioLibrary.round(5)[0]
    result = war_room.run_governed(
        scenario,
        system_id="system-1",
        decision=scenario.expected_decision,
        capability_token=token(authority, scenario),
    )
    assert result.outcome is Outcome.DENY
    assert war_room.results() == ()


def test_scenario_and_evaluation_validation() -> None:
    scenario = ScenarioLibrary.round(1)[0]
    with pytest.raises(ValueError, match="1-5"):
        Scenario(
            scenario.name,
            scenario.description,
            scenario.scenario_type,
            scenario.difficulty,
            6,
            scenario.expected_decision,
        )
    with pytest.raises(ValueError, match="must not be empty"):
        stack()[0].evaluate(scenario, system_id="", decision="x")
