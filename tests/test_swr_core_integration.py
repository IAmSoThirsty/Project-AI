"""Integration test: SWR WarRoomCore behind the FastAPI surface (J6.1).

The J3.5 API port shipped 13 endpoints wired to a then-unported
core. This test proves the J6.1 WarRoomCore actually serves that
API: scenarios load, execute through the execution gate, results
persist and verify, scoreboard/governance/proof surfaces respond.

Honest scope:
- Exercises the FastAPI app in-process via TestClient (no live
  uvicorn server, no network).
- Uses a default allow-all RuleGovernor stack; a dedicated deny
  test proves fail-closed recording at the facade level.
- Does NOT test the CLI's click command I/O beyond constructing the
  same governed stack get_swr() builds.
- Does NOT test /export beyond a tmp-dir happy path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from swr.api import create_app

from capability import CapabilityAuthority
from execution import ExecutionGate
from governance import GovernanceEngine, Rule, RuleGovernor
from kernel import EventSpine, Outcome
from swr import ScenarioLibrary, WarRoomCore


def build_core(*, allow: bool = True, bundle_dir: Path | str | None = None) -> WarRoomCore:
    rules: tuple[Rule, ...] = (
        () if allow else (Rule("deny", lambda _request, _state: False, Outcome.DENY, "blocked"),)
    )
    governance = GovernanceEngine(
        policy_version="integration-v1",
        governors=(RuleGovernor("primary", rules),),
    )
    authority = CapabilityAuthority(b"i" * 32, issuer="integration")
    gate = ExecutionGate(governance=governance, capabilities=authority, events=EventSpine())
    return WarRoomCore(execution=gate, capabilities=authority, bundle_dir=bundle_dir)


def make_client(core: WarRoomCore) -> TestClient:
    return TestClient(create_app(core))


def execute_first_scenario(client: TestClient, system_id: str = "api-system") -> dict[str, Any]:
    loaded = client.post("/scenarios/load", json={"round_number": 1}).json()
    scenario_id = loaded["scenarios"][0]["scenario_id"]
    expected = loaded["scenarios"][0]["expected_decision"]
    response = client.post(
        f"/scenarios/{scenario_id}/execute",
        params={"system_id": system_id},
        json={"decision": expected, "reasoning": {"summary": "integration"}},
    )
    assert response.status_code == 200, response.text
    payload: dict[str, Any] = response.json()
    return payload


def test_api_root_and_health() -> None:
    client = make_client(build_core())
    assert client.get("/").json()["status"] == "operational"
    assert client.get("/health").json() == {"status": "healthy"}


def test_api_load_and_get_scenarios() -> None:
    client = make_client(build_core())
    loaded = client.post("/scenarios/load", json={}).json()
    assert loaded["count"] == 5
    scenario_id = loaded["scenarios"][0]["scenario_id"]
    fetched = client.get(f"/scenarios/{scenario_id}").json()
    assert fetched["scenario_id"] == scenario_id
    assert client.get("/scenarios/missing").status_code == 404


def test_api_execute_records_and_verifies() -> None:
    core = build_core()
    client = make_client(core)
    result = execute_first_scenario(client)
    assert result["recorded"] is True
    assert result["gate_outcome"] == Outcome.ALLOW.value

    results = client.get("/results").json()
    assert results["count"] == 1
    verification = client.get("/results/0/verify").json()
    assert verification["valid"] is True

    leaderboard = client.get("/leaderboard").json()["leaderboard"]
    assert leaderboard[0]["system_id"] == "api-system"

    performance = client.get("/systems/api-system/performance").json()
    assert performance["overall_performance"]["total_attempts"] == 1

    scenario_id = result["scenario_id"]
    statistics = client.get(f"/scenarios/{scenario_id}/statistics").json()
    assert statistics["total_attempts"] == 1

    audit = client.get("/governance/audit-log").json()
    assert audit["count"] >= 1

    proof = client.get(f"/proofs/{result['decision_proof_id']}").json()
    assert proof["verification"]["valid"] is True


def test_api_execution_denied_is_fail_closed() -> None:
    core = build_core(allow=False)
    client = make_client(core)
    result = execute_first_scenario(client, system_id="denied-system")
    assert result["recorded"] is False
    assert result["gate_outcome"] == Outcome.DENY.value
    assert client.get("/results").json()["count"] == 0
    assert core.proof_system.list_proofs() == []


def test_api_export_results(tmp_path: Path) -> None:
    core = build_core(bundle_dir=tmp_path)
    client = make_client(core)
    execute_first_scenario(client)
    exported = client.post("/export", params={"filename": "integration-export"}).json()
    assert exported["success"] is True
    assert Path(exported["filepath"]).exists()


def test_cli_get_swr_builds_working_core() -> None:
    from swr.cli import get_swr

    core = get_swr()
    assert isinstance(core, WarRoomCore)
    scenario = ScenarioLibrary.round(1)[0]
    core.load_scenarios()
    result = core.execute_scenario(
        scenario,
        {"decision": scenario.expected_decision, "reasoning": {"summary": "cli"}},
        "cli-system",
    )
    assert result["recorded"] is True
    assert core.verify_result_integrity(result) is True
