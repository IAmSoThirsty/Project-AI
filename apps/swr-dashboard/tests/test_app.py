"""Tests for the SWR Dashboard (J3.8 port).

Honest scope:
- Exercises the Flask app in-process via ``flask.test_client()``
  (no live server, no network). Same pattern as the J6.1
  ``test_swr_core_integration`` honest-scope note.
- Uses a default allow-all RuleGovernor stack (the same
  ``get_swr()`` factory the production entry point uses), so the
  tests verify the real default stack, not a mocked one.
- The HTML template is the legacy template verbatim and is
  not asserted on beyond the 200 status; visual / JS behavior
  is out of scope for these tests.
"""

from __future__ import annotations

from typing import Any

import pytest
from flask import Flask
from flask.testing import FlaskClient
from project_ai_swr_dashboard import create_app


@pytest.fixture
def app() -> Flask:
    """A fresh dashboard app per test (no shared state)."""
    return create_app()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """A Flask test client bound to the fresh app."""
    return app.test_client()


def test_index_returns_200(client: FlaskClient) -> None:
    """The dashboard HTML is served at /."""
    response = client.get("/")
    assert response.status_code == 200
    # The legacy template is preserved verbatim, so the title
    # string is the smoke test for "this is the dashboard".
    assert b"SOVEREIGN WAR ROOM" in response.data


def test_api_scenarios_returns_list(client: FlaskClient) -> None:
    """/api/scenarios returns the canonical SWR scenarios."""
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    payload: dict[str, Any] = response.get_json()
    assert "scenarios" in payload
    assert isinstance(payload["scenarios"], list)
    # canonical SWR ships scenarios (5 rounds x N scenarios);
    # asserting non-empty proves load_scenarios was wired.
    assert len(payload["scenarios"]) > 0
    first = payload["scenarios"][0]
    # Pydantic v2 model_dump shape — the template reads
    # scenario.name, scenario.round_number, scenario.difficulty,
    # scenario.scenario_type, scenario.description.
    for key in (
        "name",
        "round_number",
        "difficulty",
        "scenario_type",
        "description",
    ):
        assert key in first, f"scenario missing {key!r}: {first.keys()=}"


def test_api_scenarios_round_filter(client: FlaskClient) -> None:
    """/api/scenarios?round=N returns only that round's scenarios."""
    response = client.get("/api/scenarios?round=1")
    assert response.status_code == 200
    payload = response.get_json()
    assert "scenarios" in payload
    for scenario in payload["scenarios"]:
        assert scenario["round_number"] == 1


def test_api_leaderboard_returns_list(client: FlaskClient) -> None:
    """/api/leaderboard returns the top-N (default 10)."""
    response = client.get("/api/leaderboard")
    assert response.status_code == 200
    payload = response.get_json()
    assert "leaderboard" in payload
    assert isinstance(payload["leaderboard"], list)


def test_api_stats_returns_topline_counts(client: FlaskClient) -> None:
    """/api/stats returns the 4 top-line counts the template reads."""
    response = client.get("/api/stats")
    assert response.status_code == 200
    payload = response.get_json()
    # The 4 keys the dashboard HTML reads (id="stat-scenarios" etc).
    expected = {"total_scenarios", "total_results", "total_systems", "total_proofs"}
    assert expected.issubset(payload.keys()), f"missing keys: {expected - set(payload.keys())}"


def test_api_systems_performance_returns_dict(client: FlaskClient) -> None:
    """/api/systems/<id>/performance returns a per-system dict (may be empty)."""
    response = client.get("/api/systems/test-system/performance")
    assert response.status_code == 200
    # Empty dict on a fresh system is a valid canonical response
    # (the scoreboard returns {} for unknown systems). Just check
    # the response is JSON-shaped.
    assert isinstance(response.get_json(), dict)


def test_get_swr_returns_war_room_core() -> None:
    """The factory returns a WarRoomCore (the J6.1 facade)."""
    from project_ai_swr_dashboard import get_swr

    from swr import WarRoomCore

    core = get_swr()
    assert isinstance(core, WarRoomCore)
    # WarRoomCore exposes the legacy-surface attributes the routes
    # use (per the J6.1 port).
    assert hasattr(core, "active_scenarios")
    assert hasattr(core, "results")
    assert hasattr(core, "scoreboard")
    assert hasattr(core, "proof_system")
    assert hasattr(core, "load_scenarios")
