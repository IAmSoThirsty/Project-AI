"""
Basic end-to-end tests for web backend endpoints.
Tests fundamental endpoint functionality.
"""

from __future__ import annotations

import pytest

from web.backend.app import app as backend_app


@pytest.fixture
def client():
    """Create test client for Flask backend."""
    backend_app.config.update(TESTING=True)
    with backend_app.test_client() as client:
        yield client


class TestBasicEndpoints:
    """Basic endpoint functionality tests."""

    def test_status_endpoint(self, client):
        """Test health status endpoint returns correctly."""
        rv = client.get("/api/status")
        assert rv.status_code == 200
        data = rv.get_json()
        assert data["status"] == "ok"
        assert data["component"] == "web-backend"

    def test_login_and_profile_flow(self, client):
        """Test basic login and profile retrieval flow."""
        # Step 1: Login
        payload = {"username": "admin", "password": "open-sesame"}
        rv = client.post("/api/auth/login", json=payload)
        assert rv.status_code == 200
        data = rv.get_json()
        assert data["status"] == "ok"
        token = data["token"]

        # Step 2: Get profile with token
        rv2 = client.get("/api/auth/profile", headers={"X-Auth-Token": token})
        assert rv2.status_code == 200
        data2 = rv2.get_json()
        assert data2["user"]["username"] == "admin"

    def test_invalid_login(self, client):
        """Test that invalid credentials are rejected."""
        payload = {"username": "admin", "password": "wrong"}
        rv = client.post("/api/auth/login", json=payload)
        assert rv.status_code == 401

    def test_force_error_endpoint(self, client):
        """Test error handling endpoint."""
        rv = client.get("/api/debug/force-error")
        assert rv.status_code == 500
        data = rv.get_json()
        assert "forced debug failure" in data["message"]


class TestAuthenticationBasics:
    """Basic authentication workflow tests."""

    def test_guest_login(self, client):
        """Test guest user can login."""
        payload = {"username": "guest", "password": "letmein"}
        rv = client.post("/api/auth/login", json=payload)
        assert rv.status_code == 200
        data = rv.get_json()
        assert data["user"]["username"] == "guest"
        assert data["user"]["role"] == "viewer"

    def test_profile_requires_auth(self, client):
        """Test profile endpoint requires authentication."""
        rv = client.get("/api/auth/profile")
        assert rv.status_code == 401

    def test_token_authentication(self, client):
        """Test token-based authentication works."""
        # Login to get token
        login_payload = {"username": "admin", "password": "open-sesame"}
        login_rv = client.post("/api/auth/login", json=login_payload)
        token = login_rv.get_json()["token"]

        # Use token to access protected endpoint
        profile_rv = client.get("/api/auth/profile", headers={"X-Auth-Token": token})
        assert profile_rv.status_code == 200
