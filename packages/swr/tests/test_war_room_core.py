"""Unit tests for swr.core.WarRoomCore (J6.1).

The facade composes the canonical SWR components (crypto,
compliance governance, proofs, scoreboard, bundles) behind the
legacy orchestration surface, with result recording routed
through the execution gate. Denial is fail-closed: a denied
recording leaves no trace in results, proofs, or scoreboard.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from swr.core import scenario_to_dict

from capability import CapabilityAuthority
from execution import ExecutionGate
from governance import GovernanceEngine, Rule, RuleGovernor
from kernel import EventSpine, Outcome
from swr import Scenario, ScenarioLibrary, WarRoomCore


def build_core(
    *,
    allow: bool = True,
    bundle_dir: Path | str | None = None,
) -> WarRoomCore:
    rules: tuple[Rule, ...] = (
        () if allow else (Rule("deny", lambda _request, _state: False, Outcome.DENY, "blocked"),)
    )
    governance = GovernanceEngine(
        policy_version="test-v1",
        governors=(RuleGovernor("primary", rules),),
    )
    authority = CapabilityAuthority(b"s" * 32, issuer="test")
    gate = ExecutionGate(
        governance=governance,
        capabilities=authority,
        events=EventSpine(),
    )
    return WarRoomCore(execution=gate, capabilities=authority, bundle_dir=bundle_dir)


def make_response(scenario: Scenario, *, correct: bool = True) -> dict[str, Any]:
    decision = scenario.expected_decision if correct else "wrong_decision"
    return {
        "decision": decision,
        "reasoning": {"summary": "test reasoning"},
        "confidence": 0.9,
        "constraints_satisfied": True,
    }


# -- scenario loading -------------------------------------------------


def test_load_scenarios_all_rounds() -> None:
    core = build_core()
    scenarios = core.load_scenarios()
    assert len(scenarios) == 5
    assert len(core.active_scenarios) == 5


def test_load_scenarios_single_round() -> None:
    core = build_core()
    scenarios = core.load_scenarios(3)
    assert [s.round_number for s in scenarios] == [3]


def test_load_scenarios_invalid_round() -> None:
    core = build_core()
    with pytest.raises(ValueError, match="1-5"):
        core.load_scenarios(6)


def test_get_scenario_roundtrip() -> None:
    core = build_core()
    core.load_scenarios()
    scenario = ScenarioLibrary.round(1)[0]
    assert core.get_scenario(scenario.scenario_id) == scenario
    assert core.get_scenario("missing") is None


def test_scenario_to_dict_includes_identity() -> None:
    scenario = ScenarioLibrary.round(2)[0]
    data = scenario_to_dict(scenario)
    assert data["scenario_id"] == scenario.scenario_id
    assert data["expected_decision"] == scenario.expected_decision
    assert data["round_number"] == 2
    assert isinstance(data["tags"], list)


def test_scenario_dataclass_to_dict_matches_helper() -> None:
    scenario = ScenarioLibrary.round(4)[0]
    assert scenario.to_dict() == scenario_to_dict(scenario)


# -- governed execution ------------------------------------------------


def test_execute_scenario_allowed_records_result() -> None:
    core = build_core()
    core.load_scenarios()
    scenario = ScenarioLibrary.round(1)[0]
    result = core.execute_scenario(scenario, make_response(scenario), "system-1")

    assert result["recorded"] is True
    assert result["gate_outcome"] == Outcome.ALLOW.value
    assert result["decision"] == scenario.expected_decision
    assert result["response_valid"] is True
    assert result["compliance_status"]
    assert result["sovereign_resilience_score"] > 0
    assert len(core.results) == 1
    assert core.proof_system.get_proof(result["decision_proof_id"]) is not None
    assert core.proof_system.get_proof(result["compliance_proof_id"]) is not None
    performance = core.scoreboard.get_system_performance("system-1")
    assert performance["overall_performance"]["total_attempts"] == 1


def test_execute_scenario_denied_is_fail_closed() -> None:
    core = build_core(allow=False)
    core.load_scenarios()
    scenario = ScenarioLibrary.round(5)[0]
    result = core.execute_scenario(scenario, make_response(scenario), "system-1")

    assert result["recorded"] is False
    assert result["gate_outcome"] == Outcome.DENY.value
    # Fail-closed: no side effects anywhere.
    assert core.results == []
    assert core.proof_system.list_proofs() == []
    assert "error" in core.scoreboard.get_system_performance("system-1")
    assert core.governance.get_audit_log() == []


def test_execute_scenario_empty_decision_rejected() -> None:
    core = build_core()
    core.load_scenarios()
    scenario = ScenarioLibrary.round(1)[0]
    with pytest.raises(ValueError, match="must not be empty"):
        core.execute_scenario(scenario, {"decision": ""}, "system-1")


def test_execute_scenario_wrong_decision_marked_unsuccessful() -> None:
    core = build_core()
    core.load_scenarios()
    scenario = ScenarioLibrary.round(2)[0]
    right = core.execute_scenario(scenario, make_response(scenario), "sys-right")
    wrong = core.execute_scenario(scenario, make_response(scenario, correct=False), "sys-wrong")
    # The composite SRS is governance-weighted and does not factor
    # decision correctness; success/accuracy/response_valid do.
    assert right["score"]["success"] is True
    assert wrong["score"]["success"] is False
    assert right["score"]["accuracy"] > wrong["score"]["accuracy"]
    assert right["response_valid"] is True
    assert wrong["response_valid"] is False


# -- results and filtering ---------------------------------------------


def test_get_results_filters() -> None:
    core = build_core()
    core.load_scenarios()
    round_1 = ScenarioLibrary.round(1)[0]
    round_2 = ScenarioLibrary.round(2)[0]
    core.execute_scenario(round_1, make_response(round_1), "system-a")
    core.execute_scenario(round_2, make_response(round_2), "system-b")

    assert len(core.get_results()) == 2
    assert [r["system_id"] for r in core.get_results("system-a")] == ["system-a"]
    assert [r["round_number"] for r in core.get_results(round_number=2)] == [2]
    assert core.get_results("system-a", round_number=2) == []


def test_run_round_executes_all_round_scenarios() -> None:
    core = build_core()
    outcomes = core.run_round(1, lambda s: make_response(s), "system-1")
    assert len(outcomes) == len(ScenarioLibrary.round(1))
    assert all(r["recorded"] for r in outcomes)


def test_run_full_competition_covers_five_rounds() -> None:
    core = build_core()
    report = core.run_full_competition(lambda s: make_response(s), "system-1")
    assert sorted(report["rounds"]) == [f"round_{n}" for n in range(1, 6)]
    assert report["final_performance"]["overall_performance"]["total_attempts"] == 5
    assert report["leaderboard_position"] == 0


# -- integrity and export ----------------------------------------------


def test_verify_result_integrity_accepts_untampered() -> None:
    core = build_core()
    core.load_scenarios()
    scenario = ScenarioLibrary.round(1)[0]
    result = core.execute_scenario(scenario, make_response(scenario), "system-1")
    assert core.verify_result_integrity(result) is True


def test_verify_result_integrity_rejects_tampered_audit() -> None:
    core = build_core()
    core.load_scenarios()
    scenario = ScenarioLibrary.round(1)[0]
    result = core.execute_scenario(scenario, make_response(scenario), "system-1")
    tampered = dict(result)
    tampered_audit = dict(result["audit_entry"])
    tampered_audit["event"] = {"forged": True}
    tampered["audit_entry"] = tampered_audit
    assert core.verify_result_integrity(tampered) is False


def test_verify_result_integrity_rejects_missing_audit() -> None:
    core = build_core()
    assert core.verify_result_integrity({}) is False


def test_export_results_json(tmp_path: Path) -> None:
    core = build_core(bundle_dir=tmp_path)
    core.load_scenarios()
    scenario = ScenarioLibrary.round(1)[0]
    core.execute_scenario(scenario, make_response(scenario), "system-1")
    filepath = core.export_results("test-export", "json")
    assert Path(filepath).exists()


def test_get_leaderboard_after_runs() -> None:
    core = build_core()
    core.load_scenarios()
    scenario = ScenarioLibrary.round(1)[0]
    core.execute_scenario(scenario, make_response(scenario), "system-1")
    leaderboard = core.get_leaderboard()
    assert leaderboard[0]["system_id"] == "system-1"
