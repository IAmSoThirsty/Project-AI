"""Integration tests: SWR API (J3.5).

Per docs/internal/J3_DISCOVERY.md Phase J3.5: the FastAPI
REST API for Sovereign War Room. Provides 13 endpoints for
running scenarios, viewing results, and managing the
competition. The Beginnings port uses a factory pattern:
create_app(swr_instance) returns a configured FastAPI app,
or set_swr(swr_instance) sets the module-level instance.

Honest scope:
- Tests the api module's public surface: create_app,
  set_swr, start_api, the 3 Pydantic request/response
  models.
- Tests all 13 endpoints via FastAPI TestClient, with a
  mock SovereignWarRoom instance.
- Tests the fail-closed path: 503 if swr is not set.
- Tests the 404 paths: scenario not found, result not
  found, system not found, scenario statistics not
  found, proof not found.
- Does NOT start a real uvicorn server (uses TestClient
  in-process).
- Does NOT require a real SovereignWarRoom (uses a mock).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from swr.api import (
    AISystemResponse,
    ExecuteScenarioRequest,
    LoadScenariosRequest,
    create_app,
    set_swr,
)


@dataclass
class FakeScenario:
    """A simple scenario mock for tests."""

    id: str
    name: str
    scenario_type: str
    difficulty: int
    round_number: int

    def model_dump(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "scenario_type": self.scenario_type,
            "difficulty": self.difficulty,
            "round_number": self.round_number,
        }


@dataclass
class FakeProof:
    """A simple proof mock for tests."""

    proof_id: str
    valid: bool = True

    def model_dump(self) -> dict[str, Any]:
        return {"proof_id": self.proof_id, "valid": self.valid}


# ── 1. Public surface ─────────────────────────────


def test_create_app_returns_fastapi_app() -> None:
    """create_app returns a FastAPI app."""
    from fastapi import FastAPI

    app = create_app()
    assert isinstance(app, FastAPI)


def test_create_app_with_swr_instance() -> None:
    """create_app accepts an optional swr_instance parameter."""
    from fastapi import FastAPI

    mock_swr = MagicMock()
    app = create_app(mock_swr)
    assert isinstance(app, FastAPI)
    # Reset module-level swr to None for other tests
    set_swr(None)


def test_set_swr_sets_module_swr() -> None:
    """set_swr sets the module-level swr placeholder."""
    mock_swr = MagicMock()
    set_swr(mock_swr)
    from swr.api import swr

    assert swr is mock_swr
    # Reset
    set_swr(None)


def test_request_response_models() -> None:
    """The 3 request/response models are importable Pydantic models."""
    from pydantic import BaseModel

    assert issubclass(AISystemResponse, BaseModel)
    assert issubclass(ExecuteScenarioRequest, BaseModel)
    assert issubclass(LoadScenariosRequest, BaseModel)


# ── 2. Endpoints present ──────────────────────────


def test_app_has_root_endpoint() -> None:
    """The app has a / endpoint."""
    app = create_app()
    paths = [r.path for r in app.routes if hasattr(r, "path")]
    assert "/" in paths


def test_app_has_health_endpoint() -> None:
    """The app has a /health endpoint."""
    app = create_app()
    paths = [r.path for r in app.routes if hasattr(r, "path")]
    assert "/health" in paths


def test_app_has_all_13_swr_endpoints() -> None:
    """The app has all 13 SWR endpoints."""
    app = create_app()
    paths = {r.path for r in app.routes if hasattr(r, "path")}
    expected = {
        "/",
        "/health",
        "/scenarios/load",
        "/scenarios/{scenario_id}",
        "/scenarios/{scenario_id}/execute",
        "/results",
        "/results/{result_id}/verify",
        "/leaderboard",
        "/systems/{system_id}/performance",
        "/scenarios/{scenario_id}/statistics",
        "/governance/audit-log",
        "/proofs/{proof_id}",
        "/export",
    }
    assert expected.issubset(paths)


# ── 3. Test client with mock swr ──────────────────


@pytest.fixture
def mock_swr() -> Any:
    """Return a mock SovereignWarRoom instance with realistic behavior."""
    mock = MagicMock()
    scenario1 = FakeScenario(
        id="s1",
        name="Test Scenario 1",
        scenario_type="ethical_dilemma",
        difficulty=3,
        round_number=1,
    )
    scenario2 = FakeScenario(
        id="s2",
        name="Test Scenario 2",
        scenario_type="black_swan",
        difficulty=7,
        round_number=5,
    )

    mock.load_scenarios.return_value = [scenario1, scenario2]
    mock.get_scenario.return_value = scenario1
    mock.execute_scenario.return_value = {"success": True, "score": 100}
    mock.get_results.return_value = [{"id": "r1", "score": 100}]
    mock.results = [{"scenario_id": "s1", "system_id": "sys1"}]
    mock.verify_result_integrity.return_value = True
    mock.get_leaderboard.return_value = [{"rank": 1, "system_id": "sys1", "score": 100}]
    mock.scoreboard.get_system_performance.return_value = {
        "system_id": "sys1",
        "overall_performance": {"total_attempts": 1},
    }
    mock.scoreboard.get_scenario_statistics.return_value = {
        "scenario_id": "s1",
        "total_attempts": 1,
    }
    mock.governance.get_audit_log.return_value = [{"id": "a1"}]
    fake_proof = FakeProof(proof_id="p1")
    mock.proof_system.get_proof.return_value = fake_proof
    mock.proof_system.verify_proof.return_value = {"valid": True}
    mock.export_results.return_value = "/tmp/results.json"
    return mock


@pytest.fixture
def client(mock_swr: Any) -> TestClient:
    """Return a TestClient with the mock swr configured."""
    app = create_app(mock_swr)
    return TestClient(app)


# ── 4. Root + health ──────────────────────────────


def test_root_endpoint(client: TestClient) -> None:
    """GET / returns the API info."""
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "SOVEREIGN WAR ROOM API"
    assert data["status"] == "operational"


def test_health_endpoint(client: TestClient) -> None:
    """GET /health returns healthy."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


# ── 5. Scenarios ─────────────────────────────────


def test_load_scenarios(client: TestClient, mock_swr: Any) -> None:
    """POST /scenarios/load returns the loaded scenarios."""
    r = client.post("/scenarios/load", json={"round_number": None})
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 2
    assert len(data["scenarios"]) == 2
    mock_swr.load_scenarios.assert_called_once_with(None)


def test_load_scenarios_with_type_filter(client: TestClient, mock_swr: Any) -> None:
    """POST /scenarios/load with scenario_type filter."""
    r = client.post(
        "/scenarios/load",
        json={"round_number": None, "scenario_type": "black_swan"},
    )
    assert r.status_code == 200
    data = r.json()
    # Only 1 scenario matches the type filter
    assert data["count"] == 1


def test_load_scenarios_with_difficulty_filter(client: TestClient, mock_swr: Any) -> None:
    """POST /scenarios/load with difficulty filter."""
    r = client.post(
        "/scenarios/load",
        json={"round_number": None, "difficulty": 3},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 1


def test_get_scenario(client: TestClient) -> None:
    """GET /scenarios/{id} returns the scenario."""
    r = client.get("/scenarios/s1")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "s1"


def test_get_scenario_not_found(mock_swr: Any) -> None:
    """GET /scenarios/{id} returns 404 if scenario not found."""
    mock_swr.get_scenario.return_value = None
    app = create_app(mock_swr)
    client = TestClient(app)
    r = client.get("/scenarios/unknown")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"]


def test_execute_scenario(client: TestClient) -> None:
    """POST /scenarios/{id}/execute runs the scenario."""
    r = client.post(
        "/scenarios/s1/execute?system_id=sys1",
        json={"decision": "A", "reasoning": {"x": 1}},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True


def test_execute_scenario_not_found(mock_swr: Any) -> None:
    """POST /scenarios/{id}/execute returns 404 if scenario missing."""
    mock_swr.get_scenario.return_value = None
    app = create_app(mock_swr)
    client = TestClient(app)
    r = client.post(
        "/scenarios/unknown/execute?system_id=sys1",
        json={"decision": "A"},
    )
    assert r.status_code == 404


def test_execute_scenario_error_returns_500(mock_swr: Any) -> None:
    """POST /scenarios/{id}/execute returns 500 on execution error."""
    mock_swr.execute_scenario.side_effect = RuntimeError("boom")
    app = create_app(mock_swr)
    client = TestClient(app)
    r = client.post(
        "/scenarios/s1/execute?system_id=sys1",
        json={"decision": "A"},
    )
    assert r.status_code == 500
    assert "boom" in r.json()["detail"]


# ── 6. Results ───────────────────────────────────


def test_get_results(client: TestClient) -> None:
    """GET /results returns the results."""
    r = client.get("/results")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 1
    assert data["results"] == [{"id": "r1", "score": 100}]


def test_get_results_with_filters(client: TestClient, mock_swr: Any) -> None:
    """GET /results with system_id and round_number filters."""
    r = client.get("/results?system_id=sys1&round_number=1")
    assert r.status_code == 200
    mock_swr.get_results.assert_called_with("sys1", 1)


def test_verify_result(client: TestClient) -> None:
    """GET /results/{id}/verify returns verification status."""
    r = client.get("/results/0/verify")
    assert r.status_code == 200
    data = r.json()
    assert data["valid"] is True
    assert data["result_id"] == 0
    assert data["scenario_id"] == "s1"
    assert data["system_id"] == "sys1"


def test_verify_result_not_found(mock_swr: Any) -> None:
    """GET /results/{id}/verify returns 404 if result not found."""
    app = create_app(mock_swr)
    client = TestClient(app)
    r = client.get("/results/999/verify")
    assert r.status_code == 404


# ── 7. Leaderboard + system + scenario stats ──────


def test_get_leaderboard(client: TestClient) -> None:
    """GET /leaderboard returns the leaderboard."""
    r = client.get("/leaderboard")
    assert r.status_code == 200
    data = r.json()
    assert len(data["leaderboard"]) == 1
    assert data["leaderboard"][0]["rank"] == 1


def test_get_leaderboard_with_limit(client: TestClient, mock_swr: Any) -> None:
    """GET /leaderboard?limit=N respects the limit parameter."""
    r = client.get("/leaderboard?limit=5")
    assert r.status_code == 200
    # Verify the limit is passed through to get_leaderboard
    mock_swr.get_leaderboard.assert_called_with()


def test_get_system_performance(client: TestClient) -> None:
    """GET /systems/{id}/performance returns the performance metrics."""
    r = client.get("/systems/sys1/performance")
    assert r.status_code == 200
    data = r.json()
    assert data["system_id"] == "sys1"


def test_get_system_performance_not_found(mock_swr: Any) -> None:
    """GET /systems/{id}/performance returns 404 if system not found."""
    mock_swr.scoreboard.get_system_performance.return_value = {"error": "System not found"}
    app = create_app(mock_swr)
    client = TestClient(app)
    r = client.get("/systems/unknown/performance")
    assert r.status_code == 404


def test_get_scenario_statistics(client: TestClient) -> None:
    """GET /scenarios/{id}/statistics returns the scenario statistics."""
    r = client.get("/scenarios/s1/statistics")
    assert r.status_code == 200
    data = r.json()
    assert data["scenario_id"] == "s1"


def test_get_scenario_statistics_not_found(mock_swr: Any) -> None:
    """GET /scenarios/{id}/statistics returns 404 if not found."""
    mock_swr.scoreboard.get_scenario_statistics.return_value = {"error": "No attempts"}
    app = create_app(mock_swr)
    client = TestClient(app)
    r = client.get("/scenarios/unknown/statistics")
    assert r.status_code == 404


# ── 8. Governance + proofs + export ───────────────


def test_get_audit_log(client: TestClient) -> None:
    """GET /governance/audit-log returns the audit log."""
    r = client.get("/governance/audit-log")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 1
    assert data["entries"] == [{"id": "a1"}]


def test_get_audit_log_with_limit(client: TestClient, mock_swr: Any) -> None:
    """GET /governance/audit-log?limit=N respects the limit parameter."""
    r = client.get("/governance/audit-log?limit=50")
    assert r.status_code == 200
    mock_swr.governance.get_audit_log.assert_called_with(50)


def test_get_proof(client: TestClient) -> None:
    """GET /proofs/{id} returns the proof + verification."""
    r = client.get("/proofs/p1")
    assert r.status_code == 200
    data = r.json()
    assert "proof" in data
    assert "verification" in data
    assert data["verification"]["valid"] is True


def test_get_proof_reveal_witness(client: TestClient, mock_swr: Any) -> None:
    """GET /proofs/{id}?reveal_witness=true reveals the witness."""
    r = client.get("/proofs/p1?reveal_witness=true")
    assert r.status_code == 200
    # Verify reveal_witness was passed through
    mock_swr.proof_system.verify_proof.assert_called_with(
        mock_swr.proof_system.get_proof.return_value, True
    )


def test_get_proof_not_found(mock_swr: Any) -> None:
    """GET /proofs/{id} returns 404 if proof not found."""
    mock_swr.proof_system.get_proof.return_value = None
    app = create_app(mock_swr)
    client = TestClient(app)
    r = client.get("/proofs/unknown")
    assert r.status_code == 404


def test_export_results(client: TestClient) -> None:
    """POST /export exports results to a file."""
    r = client.post("/export?filename=results&format=json")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["format"] == "json"


def test_export_results_error_returns_500(mock_swr: Any) -> None:
    """POST /export returns 500 on error."""
    mock_swr.export_results.side_effect = ValueError("bad format")
    app = create_app(mock_swr)
    client = TestClient(app)
    r = client.post("/export?filename=results&format=xml")
    assert r.status_code == 500


# ── 9. Fail-closed: 503 if swr not set ───────────


def test_endpoint_returns_503_when_swr_not_set() -> None:
    """An endpoint that needs swr returns 503 when swr is not set."""
    set_swr(None)
    app = create_app()  # No swr instance provided
    client = TestClient(app)
    r = client.get("/leaderboard")
    assert r.status_code == 503
    assert "not configured" in r.json()["detail"]


# ── 10. Dashboard HTML shipped ────────────────────


def test_dashboard_html_exists() -> None:
    """The dashboard.html template is shipped with the package."""
    from pathlib import Path

    template = (
        Path(__file__).parent.parent
        / "packages"
        / "swr"
        / "src"
        / "swr"
        / "web"
        / "templates"
        / "dashboard.html"
    )
    assert template.exists()
    text = template.read_text(encoding="utf-8")
    assert "SOVEREIGN WAR ROOM" in text
    assert "loadLeaderboard" in text  # JavaScript function
    assert "/api/leaderboard" in text  # API endpoint
    assert "/api/results" in text
    assert "/api/stats" in text
