from __future__ import annotations

import json
from flask import Flask

import pytest

from web.backend.app import app as backend_app


@pytest.fixture
def client():
    backend_app.config.update(TESTING=True)
    with backend_app.test_client() as client:
        yield client


def test_status_endpoint(client):
    rv = client.get("/api/status")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == "ok"


def test_login_and_profile_flow(client):
    # login
    payload = {"username": "admin", "password": "open-sesame"}
    rv = client.post("/api/auth/login", json=payload)
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == "ok"
    token = data["token"]

    # profile
    rv2 = client.get("/api/auth/profile", headers={"X-Auth-Token": token})
    assert rv2.status_code == 200
    data2 = rv2.get_json()
    assert data2["user"]["username"] == "admin"


def test_invalid_login(client):
    payload = {"username": "admin", "password": "wrong"}
    rv = client.post("/api/auth/login", json=payload)
    assert rv.status_code == 401


def test_force_error_endpoint(client):
    rv = client.get("/api/debug/force-error")
    assert rv.status_code == 500
    data = rv.get_json()
    assert "forced debug failure" in data["message"]
