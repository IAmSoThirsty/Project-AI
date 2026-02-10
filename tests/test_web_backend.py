"""Tests for the Flask web backend."""

from __future__ import annotations

import importlib

import pytest

from web.backend import app


@pytest.fixture(name="client")
def client_fixture():
    backend_module = importlib.import_module("web.backend.app")
    backend_module._TOKENS.clear()  # type: ignore[attr-defined]
    test_client = app.test_client()
    yield test_client
    backend_module._TOKENS.clear()  # type: ignore[attr-defined]


def test_backend_status_route(client):
    response = client.get("/api/status")

    assert response.status_code == 200
    payload = response.get_json() or {}
    assert payload.get("status") == "ok"
    assert payload.get("component") == "web-backend"


def test_login_requires_json_body(client):
    response = client.post("/api/auth/login")

    assert response.status_code == 400
    payload = response.get_json() or {}
    assert payload.get("error") == "missing-json"


def test_login_rejects_invalid_credentials(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "wrong"},
    )

    assert response.status_code == 401
    payload = response.get_json() or {}
    assert payload.get("error") == "invalid-credentials"


def test_login_success_then_profile_fetch(client):
    login_resp = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "open-sesame"},
    )

    assert login_resp.status_code == 200
    login_payload = login_resp.get_json() or {}
    token = login_payload.get("token")
    assert token
    assert login_payload.get("user", {}).get("role") == "superuser"

    profile_resp = client.get("/api/auth/profile", headers={"X-Auth-Token": token})
    assert profile_resp.status_code == 200
    profile_payload = profile_resp.get_json() or {}
    assert profile_payload.get("user", {}).get("username") == "admin"


def test_profile_requires_token_header(client):
    response = client.get("/api/auth/profile")
    assert response.status_code == 401
    assert (response.get_json() or {}).get("error") == "missing-token"


def test_profile_rejects_invalid_token(client):
    response = client.get("/api/auth/profile", headers={"X-Auth-Token": "bogus"})
    assert response.status_code == 403
    assert (response.get_json() or {}).get("error") == "invalid-token"


def test_debug_force_error_returns_json(client):
    response = client.get("/api/debug/force-error")
    assert response.status_code == 500
    payload = response.get_json() or {}
    assert payload.get("status") == "error"
