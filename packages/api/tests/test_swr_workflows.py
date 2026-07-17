"""No-bypass checks for the Control Center SWR execution composition."""

from pathlib import Path

from project_ai_api.swr_workflows import build_swr_runtime


def test_swr_runtime_denies_without_bound_review_state_and_allows_exact_scope(
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "swr-bundles"
    runtime = build_swr_runtime(
        "execution-test-secret-that-is-long-enough",
        bundle_dir=bundle_dir,
    )
    assert bundle_dir.is_dir()
    scenario = runtime.load_scenarios()[0]
    denied = runtime.execute_scenario(
        scenario,
        {"decision": scenario.expected_decision},
        system_id="project-ai-control-center-swr",
        governance_state={
            "human_review_state": "submitted",
            "request_operation": "scenario.prepare",
            "request_resource": f"scenario:{scenario.scenario_id}",
            "scenario_id": scenario.scenario_id,
            "expected_decision": scenario.expected_decision,
        },
    )
    assert denied["recorded"] is False
    assert denied["gate_outcome"] == "DENY"
    assert "review approval is missing" in denied["gate_reason"]
    assert runtime.get_results() == []

    allowed = runtime.execute_scenario(
        scenario,
        {"decision": scenario.expected_decision},
        system_id="project-ai-control-center-swr",
        governance_state={
            "human_review_state": "reviewed_approve",
            "request_operation": "scenario.prepare",
            "request_resource": f"scenario:{scenario.scenario_id}",
            "scenario_id": scenario.scenario_id,
            "expected_decision": scenario.expected_decision,
        },
    )
    assert allowed["recorded"] is True
    assert allowed["gate_outcome"] == "ALLOW"
    assert len(str(allowed["gate_evidence_sha256"])) == 64
    assert len(str(allowed["gate_event_hash"])) == 64
    assert len(runtime.get_results()) == 1
