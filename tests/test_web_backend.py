#                                           [2026-03-07 12:00]
#                                          Productivity: Active
"""Tests for the Flask web backend."""

from __future__ import annotations

import importlib

import pytest


@pytest.fixture(autouse=True)
def _enable_demo_users(monkeypatch):
    """Enable demo users for testing."""
    monkeypatch.setenv("BACKEND_DEMO_USERS", "1")


@pytest.fixture(name="client")
def client_fixture():
    # Force re-import so _load_users() picks up BACKEND_DEMO_USERS=1
    backend_module = importlib.import_module("web.backend.app")
    importlib.reload(backend_module)
    backend_module._TOKENS.clear()
    test_client = backend_module.app.test_client()
    yield test_client
    backend_module._TOKENS.clear()


class TestStatusEndpoint:
    def test_status_returns_ok(self, client):
        response = client.get("/api/status")
        assert response.status_code == 200
        payload = response.get_json() or {}
        assert payload.get("status") == "ok"
        assert payload.get("component") == "web-backend"


class TestAuthLogin:
    def test_login_requires_json_body(self, client):
        response = client.post("/api/auth/login")
        assert response.status_code == 400
        payload = response.get_json() or {}
        assert payload.get("error") == "missing-json"

    def test_login_requires_username_and_password(self, client):
        response = client.post(
            "/api/auth/login",
            json={"username": "admin"},
        )
        assert response.status_code == 400
        assert (response.get_json() or {}).get("error") == "missing-credentials"

    def test_login_rejects_invalid_credentials(self, client):
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "wrong"},
        )
        assert response.status_code == 401
        payload = response.get_json() or {}
        assert payload.get("error") == "invalid-credentials"

    def test_login_success_with_demo_credentials(self, client):
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "change-me-immediately"},
        )
        assert login_resp.status_code == 200
        login_payload = login_resp.get_json() or {}
        assert login_payload.get("token")
        assert login_payload.get("user", {}).get("role") == "superuser"

    def test_login_token_is_random(self, client):
        """Tokens should be cryptographically random, not predictable."""
        resp1 = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "change-me-immediately"},
        )
        token1 = (resp1.get_json() or {}).get("token", "")
        assert not token1.startswith("token-"), "Tokens must not be predictable"
        assert len(token1) > 20, "Tokens must be sufficiently long"


class TestAuthProfile:
    def test_profile_requires_token_header(self, client):
        response = client.get("/api/auth/profile")
        assert response.status_code == 401
        assert (response.get_json() or {}).get("error") == "missing-token"

    def test_profile_rejects_invalid_token(self, client):
        response = client.get("/api/auth/profile", headers={"X-Auth-Token": "bogus"})
        assert response.status_code == 403
        assert (response.get_json() or {}).get("error") == "invalid-token"

    def test_profile_returns_user_on_valid_token(self, client):
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "change-me-immediately"},
        )
        token = (login_resp.get_json() or {}).get("token")
        profile_resp = client.get("/api/auth/profile", headers={"X-Auth-Token": token})
        assert profile_resp.status_code == 200
        assert (profile_resp.get_json() or {}).get("user", {}).get(
            "username"
        ) == "admin"


class TestDebugEndpoint:
    def test_force_error_disabled_in_production(self, client, monkeypatch):
        monkeypatch.delenv("FLASK_ENV", raising=False)
        response = client.get("/api/debug/force-error")
        assert response.status_code == 404

    def test_force_error_enabled_in_development(self, client, monkeypatch):
        monkeypatch.setenv("FLASK_ENV", "development")
        response = client.get("/api/debug/force-error")
        assert response.status_code == 500
        payload = response.get_json() or {}
        assert payload.get("status") == "error"
