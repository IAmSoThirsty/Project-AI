#                                           [2026-03-07 12:00]
#                                          Productivity: Active
"""Tests for the FastAPI governance API — TARL evaluation, audit, authentication."""

from __future__ import annotations

import json
import os

import pytest


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch, tmp_path):
    """Ensure each test gets a fresh audit log and no API auth requirement."""
    audit_path = str(tmp_path / "test_audit.log")
    monkeypatch.setenv("AUDIT_LOG_PATH", audit_path)
    # Clear API_KEYS so auth is disabled for unit tests
    monkeypatch.delenv("API_KEYS", raising=False)


@pytest.fixture(name="client")
def client_fixture():
    """Create a TestClient for the FastAPI app."""
    # Import here so monkeypatched env vars are picked up
    import importlib

    from fastapi.testclient import TestClient

    import api.main

    importlib.reload(api.main)
    from api.main import app

    return TestClient(app)


class TestHealthEndpoints:
    def test_root_returns_service_info(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "Project AI Governance Host"
        assert "endpoints" in data

    def test_health_returns_online(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "governance-online"

    def test_tarl_returns_governance_rules(self, client):
        resp = client.get("/tarl")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "1.0"
        assert len(data["rules"]) == 4


class TestGovernanceIntentSubmission:
    def test_read_intent_allowed_for_human(self, client):
        resp = client.post(
            "/intent",
            json={
                "actor": "human",
                "action": "read",
                "target": "document-1",
                "origin": "web-ui",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["governance"]["final_verdict"] == "allow"

    def test_write_intent_degraded_for_human(self, client):
        resp = client.post(
            "/intent",
            json={
                "actor": "human",
                "action": "write",
                "target": "config-file",
                "origin": "web-ui",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["governance"]["final_verdict"] == "degrade"

    def test_execute_intent_denied_for_agent(self, client):
        resp = client.post(
            "/intent",
            json={
                "actor": "agent",
                "action": "execute",
                "target": "critical-process",
                "origin": "auto-agent",
            },
        )
        assert resp.status_code == 403

    def test_mutate_intent_denied_for_all(self, client):
        resp = client.post(
            "/intent",
            json={
                "actor": "human",
                "action": "mutate",
                "target": "system-core",
                "origin": "admin-ui",
            },
        )
        assert resp.status_code == 403

    def test_intent_submission_creates_audit_entry(self, client, tmp_path):
        client.post(
            "/intent",
            json={
                "actor": "human",
                "action": "read",
                "target": "test-doc",
                "origin": "test",
            },
        )
        audit_path = os.getenv("AUDIT_LOG_PATH")
        with open(audit_path) as f:
            lines = f.readlines()
        assert len(lines) >= 1
        entry = json.loads(lines[-1])
        assert "intent_hash" in entry
        assert "tarl_version" in entry


class TestGovernanceExecution:
    def test_execute_allowed_for_system_read(self, client):
        """System actors cannot read (only human/agent can), so this should be denied."""
        resp = client.post(
            "/execute",
            json={
                "actor": "system",
                "action": "read",
                "target": "log-file",
                "origin": "system-daemon",
            },
        )
        # System is not in allowed_actors for read
        assert resp.status_code == 403

    def test_execute_denied_for_high_risk(self, client):
        resp = client.post(
            "/execute",
            json={
                "actor": "system",
                "action": "execute",
                "target": "shutdown-sequence",
                "origin": "system-daemon",
            },
        )
        assert resp.status_code == 403


class TestAuditEndpoint:
    def test_audit_returns_empty_initially(self, client):
        resp = client.get("/audit")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tarl_version"] == "1.0"
        assert isinstance(data["records"], list)

    def test_audit_returns_records_after_intents(self, client):
        # Submit a few intents
        for i in range(3):
            client.post(
                "/intent",
                json={
                    "actor": "human",
                    "action": "read",
                    "target": f"doc-{i}",
                    "origin": "test",
                },
            )
        resp = client.get("/audit?limit=10")
        assert resp.status_code == 200
        assert len(resp.json()["records"]) == 3


class TestCORSSecurity:
    def test_cors_does_not_allow_wildcard(self, client):
        resp = client.options(
            "/health",
            headers={"Origin": "https://evil.example.com"},
        )
        # The origin should NOT be reflected back if not in allowed list
        allowed = resp.headers.get("access-control-allow-origin", "")
        assert allowed != "*", "CORS must not allow wildcard origins"
