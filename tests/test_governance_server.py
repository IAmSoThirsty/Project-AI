"""
Tests for the PSIA Governance API Server.

Tests the FastAPI endpoints that bridge the desktop frontend to the
PSIA runtime, Triumvirate governance, and DurableLedger.

Usage:
    pytest tests/test_governance_server.py -v
"""

from __future__ import annotations

import sys
import os

# Ensure src/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from fastapi.testclient import TestClient

from psia.server.governance_server import create_app


@pytest.fixture(scope="module")
def client():
    """Create a test client with a fresh app instance."""
    app = create_app()
    with TestClient(app) as c:
        yield c


# --------------------------------------------------------------------------
# GET /health
# --------------------------------------------------------------------------


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, client: TestClient):
        """GET /health should return 200."""
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_has_status_field(self, client: TestClient):
        """Health response should include 'status' field."""
        data = client.get("/health").json()
        assert "status" in data
        assert data["status"] == "governance-online"

    def test_health_has_tarl_version(self, client: TestClient):
        """Health response should include TARL version."""
        data = client.get("/health").json()
        assert data["tarl"] == "TARL-v1.0"

    def test_health_has_node_id(self, client: TestClient):
        """Health response should include node_id."""
        data = client.get("/health").json()
        assert data["node_id"] == "project-ai-desktop-node"

    def test_health_has_boot_time(self, client: TestClient):
        """Health response should include boot_time."""
        data = client.get("/health").json()
        assert data["boot_time"] is not None

    def test_health_not_halted(self, client: TestClient):
        """Health response should show halted=False."""
        data = client.get("/health").json()
        assert data["halted"] is False


# --------------------------------------------------------------------------
# GET /tarl
# --------------------------------------------------------------------------


class TestTarlEndpoint:
    """Tests for the /tarl endpoint."""

    def test_tarl_returns_200(self, client: TestClient):
        """GET /tarl should return 200."""
        resp = client.get("/tarl")
        assert resp.status_code == 200

    def test_tarl_has_version(self, client: TestClient):
        """TARL response should include version."""
        data = client.get("/tarl").json()
        assert data["version"] == "TARL-v1.0"

    def test_tarl_has_rules(self, client: TestClient):
        """TARL response should include rules list."""
        data = client.get("/tarl").json()
        assert isinstance(data["rules"], list)
        assert len(data["rules"]) >= 8

    def test_tarl_rules_have_required_fields(self, client: TestClient):
        """Each rule should have action, allowed_actors, risk, default."""
        data = client.get("/tarl").json()
        for rule in data["rules"]:
            assert "action" in rule
            assert "allowed_actors" in rule
            assert "risk" in rule
            assert "default" in rule

    def test_tarl_critical_actions_deny_by_default(self, client: TestClient):
        """Critical actions (mutate, delete, deploy) should default to deny."""
        data = client.get("/tarl").json()
        critical_actions = {r["action"]: r for r in data["rules"] if r["risk"] == "critical"}
        assert "mutate" in critical_actions
        assert "delete" in critical_actions
        assert "deploy" in critical_actions
        for action, rule in critical_actions.items():
            assert rule["default"] == "deny", f"{action} should default to deny"


# --------------------------------------------------------------------------
# POST /intent
# --------------------------------------------------------------------------


class TestIntentEndpoint:
    """Tests for the /intent endpoint."""

    def test_intent_returns_200(self, client: TestClient):
        """POST /intent should return 200."""
        resp = client.post("/intent", json={
            "actor": "human",
            "action": "read",
            "target": "state://config",
            "origin": "test",
        })
        assert resp.status_code == 200

    def test_intent_returns_governance_object(self, client: TestClient):
        """Intent response should contain message and governance object."""
        data = client.post("/intent", json={
            "actor": "human",
            "action": "read",
            "target": "state://config",
            "origin": "test",
        }).json()
        assert "message" in data
        assert "governance" in data
        gov = data["governance"]
        assert "intent_hash" in gov
        assert "tarl_version" in gov
        assert "votes" in gov
        assert "final_verdict" in gov
        assert "timestamp" in gov

    def test_intent_has_three_pillar_votes(self, client: TestClient):
        """Governance should include votes from all 3 Triumvirate pillars."""
        data = client.post("/intent", json={
            "actor": "human",
            "action": "read",
            "target": "state://config",
            "origin": "test",
        }).json()
        votes = data["governance"]["votes"]
        assert len(votes) == 3
        pillar_names = {v["pillar"] for v in votes}
        assert "Galahad" in pillar_names
        assert "Cerberus" in pillar_names
        assert "Codex Deus" in pillar_names

    def test_intent_read_allowed(self, client: TestClient):
        """A simple read by human should be allowed."""
        data = client.post("/intent", json={
            "actor": "human",
            "action": "read",
            "target": "state://config",
            "origin": "test",
        }).json()
        assert data["governance"]["final_verdict"] == "allow"

    def test_intent_each_vote_has_required_fields(self, client: TestClient):
        """Each vote should have pillar, verdict, and reason."""
        data = client.post("/intent", json={
            "actor": "human",
            "action": "read",
            "target": "state://config",
            "origin": "test",
        }).json()
        for vote in data["governance"]["votes"]:
            assert "pillar" in vote
            assert "verdict" in vote
            assert "reason" in vote

    def test_intent_missing_actor_fails(self, client: TestClient):
        """Intent without required 'actor' field should return 422."""
        resp = client.post("/intent", json={
            "action": "read",
            "target": "state://config",
        })
        assert resp.status_code == 422

    def test_intent_increments_ledger(self, client: TestClient):
        """Each intent should increase the ledger_records count."""
        health_before = client.get("/health").json()
        count_before = health_before["intents_processed"]

        client.post("/intent", json={
            "actor": "human",
            "action": "write",
            "target": "state://data",
            "origin": "test",
        })

        health_after = client.get("/health").json()
        assert health_after["intents_processed"] > count_before


# --------------------------------------------------------------------------
# GET /audit
# --------------------------------------------------------------------------


class TestAuditEndpoint:
    """Tests for the /audit endpoint."""

    def test_audit_returns_200(self, client: TestClient):
        """GET /audit should return 200."""
        resp = client.get("/audit")
        assert resp.status_code == 200

    def test_audit_has_tarl_signature(self, client: TestClient):
        """Audit response should include TARL signature."""
        data = client.get("/audit").json()
        assert "tarl_version" in data
        assert "tarl_signature" in data
        assert data["tarl_version"] == "TARL-v1.0"

    def test_audit_has_records(self, client: TestClient):
        """Audit should have records (from intent tests above)."""
        # First submit an intent to ensure records exist
        client.post("/intent", json={
            "actor": "human",
            "action": "read",
            "target": "state://audit_test",
            "origin": "test",
        })
        data = client.get("/audit").json()
        assert isinstance(data["records"], list)
        assert len(data["records"]) >= 1

    def test_audit_records_have_governance_fields(self, client: TestClient):
        """Each audit record should match the GovernanceResult schema."""
        client.post("/intent", json={
            "actor": "human",
            "action": "execute",
            "target": "state://test",
            "origin": "test",
        })
        data = client.get("/audit").json()
        if data["records"]:
            rec = data["records"][-1]
            assert "intent_hash" in rec
            assert "final_verdict" in rec
            assert "timestamp" in rec
            assert "votes" in rec

    def test_audit_limit_parameter(self, client: TestClient):
        """Audit limit parameter should cap results."""
        resp = client.get("/audit?limit=1")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["records"]) <= 1
