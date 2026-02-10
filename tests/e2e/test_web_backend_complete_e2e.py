"""
End-to-End tests for complete Flask Web Backend user flows.
Tests authentication, authorization, and session management workflows.
"""

import pytest

from web.backend.app import app as flask_app


@pytest.fixture
def client():
    """Create test client for Flask application."""
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def authenticated_admin(client):
    """Create authenticated admin session."""
    login_payload = {"username": "admin", "password": "open-sesame"}
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.get_json()
    return {"client": client, "token": data["token"], "user": data["user"]}


@pytest.fixture
def authenticated_guest(client):
    """Create authenticated guest session."""
    login_payload = {"username": "guest", "password": "letmein"}
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.get_json()
    return {"client": client, "token": data["token"], "user": data["user"]}


class TestWebBackendAuthenticationE2E:
    """End-to-end authentication workflows."""

    def test_e2e_complete_login_flow(self, client):
        """Test complete user login flow from start to finish."""
        # Step 1: User navigates to login
        # Step 2: User submits credentials
        login_payload = {"username": "admin", "password": "open-sesame"}

        response = client.post("/api/auth/login", json=login_payload)

        # Step 3: Verify successful authentication
        assert response.status_code == 200
        data = response.get_json()

        assert data["status"] == "ok"
        assert "token" in data
        assert data["user"]["username"] == "admin"
        assert data["user"]["role"] == "superuser"

        # Step 4: Verify token format
        token = data["token"]
        assert token.startswith("token-")
        assert "admin" in token

    def test_e2e_failed_login_invalid_password(self, client):
        """Test complete flow for failed login with wrong password."""
        # Step 1: User submits incorrect credentials
        login_payload = {"username": "admin", "password": "wrong-password"}

        response = client.post("/api/auth/login", json=login_payload)

        # Step 2: Verify authentication failed
        assert response.status_code == 401
        data = response.get_json()

        assert data["error"] == "invalid-credentials"
        assert "incorrect" in data["message"].lower()

        # Step 3: Verify no token was issued
        assert "token" not in data

    def test_e2e_failed_login_nonexistent_user(self, client):
        """Test complete flow for login with non-existent user."""
        login_payload = {"username": "nonexistent", "password": "anypassword"}

        response = client.post("/api/auth/login", json=login_payload)

        assert response.status_code == 401
        data = response.get_json()
        assert data["error"] == "invalid-credentials"

    def test_e2e_failed_login_missing_credentials(self, client):
        """Test complete flow for login with missing fields."""
        # Missing password
        login_payload = {"username": "admin"}

        response = client.post("/api/auth/login", json=login_payload)

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "missing-credentials"
        assert "required" in data["message"].lower()

    def test_e2e_failed_login_no_json_body(self, client):
        """Test complete flow for login without JSON body."""
        response = client.post("/api/auth/login", data="not json")

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "missing-json"

    def test_e2e_multiple_user_login_sessions(self, client):
        """Test multiple users can login simultaneously."""
        # User 1: Admin login
        admin_response = client.post(
            "/api/auth/login", json={"username": "admin", "password": "open-sesame"}
        )
        assert admin_response.status_code == 200
        admin_token = admin_response.get_json()["token"]

        # User 2: Guest login
        guest_response = client.post(
            "/api/auth/login", json={"username": "guest", "password": "letmein"}
        )
        assert guest_response.status_code == 200
        guest_token = guest_response.get_json()["token"]

        # Verify both tokens are different
        assert admin_token != guest_token

        # Verify both can access profile with their token
        admin_profile = client.get(
            "/api/auth/profile", headers={"X-Auth-Token": admin_token}
        )
        assert admin_profile.status_code == 200
        assert admin_profile.get_json()["user"]["username"] == "admin"

        guest_profile = client.get(
            "/api/auth/profile", headers={"X-Auth-Token": guest_token}
        )
        assert guest_profile.status_code == 200
        assert guest_profile.get_json()["user"]["username"] == "guest"


class TestWebBackendAuthorizationE2E:
    """End-to-end authorization and profile access workflows."""

    def test_e2e_authenticated_profile_access(self, authenticated_admin):
        """Test complete flow for accessing profile with valid token."""
        client = authenticated_admin["client"]
        token = authenticated_admin["token"]

        # Step 1: User requests their profile
        response = client.get("/api/auth/profile", headers={"X-Auth-Token": token})

        # Step 2: Verify profile data returned
        assert response.status_code == 200
        data = response.get_json()

        assert data["status"] == "ok"
        assert data["user"]["username"] == "admin"
        assert data["user"]["role"] == "superuser"

    def test_e2e_profile_access_without_token(self, client):
        """Test profile access fails without authentication token."""
        # Step 1: User tries to access profile without token
        response = client.get("/api/auth/profile")

        # Step 2: Verify access denied
        assert response.status_code == 401
        data = response.get_json()

        assert data["error"] == "missing-token"
        assert "required" in data["message"].lower()

    def test_e2e_profile_access_invalid_token(self, client):
        """Test profile access fails with invalid token."""
        # Step 1: User tries with invalid token
        response = client.get(
            "/api/auth/profile", headers={"X-Auth-Token": "invalid-token-12345"}
        )

        # Step 2: Verify access denied
        assert response.status_code == 403
        data = response.get_json()

        assert data["error"] == "invalid-token"
        assert "not recognized" in data["message"].lower()

    def test_e2e_role_based_access_control(
        self, authenticated_admin, authenticated_guest
    ):
        """Test different user roles have appropriate access."""
        # Admin user
        admin_client = authenticated_admin["client"]
        admin_token = authenticated_admin["token"]

        admin_response = admin_client.get(
            "/api/auth/profile", headers={"X-Auth-Token": admin_token}
        )
        assert admin_response.status_code == 200
        admin_data = admin_response.get_json()
        assert admin_data["user"]["role"] == "superuser"

        # Guest user
        guest_client = authenticated_guest["client"]
        guest_token = authenticated_guest["token"]

        guest_response = guest_client.get(
            "/api/auth/profile", headers={"X-Auth-Token": guest_token}
        )
        assert guest_response.status_code == 200
        guest_data = guest_response.get_json()
        assert guest_data["user"]["role"] == "viewer"

        # Verify roles are different
        assert admin_data["user"]["role"] != guest_data["user"]["role"]


class TestWebBackendCompleteUserJourneys:
    """End-to-end tests for complete user journeys through the system."""

    def test_e2e_new_user_first_session(self, client):
        """Test complete journey of a new user's first session."""
        # Step 1: Check system status before login
        status_response = client.get("/api/status")
        assert status_response.status_code == 200
        status_data = status_response.get_json()
        assert status_data["status"] == "ok"

        # Step 2: User logs in
        login_response = client.post(
            "/api/auth/login", json={"username": "guest", "password": "letmein"}
        )
        assert login_response.status_code == 200
        token = login_response.get_json()["token"]

        # Step 3: User accesses their profile
        profile_response = client.get(
            "/api/auth/profile", headers={"X-Auth-Token": token}
        )
        assert profile_response.status_code == 200
        profile_data = profile_response.get_json()
        assert profile_data["user"]["username"] == "guest"

        # Step 4: User verifies system status again
        status_response2 = client.get("/api/status")
        assert status_response2.status_code == 200

    def test_e2e_admin_workflow(self, client):
        """Test complete admin user workflow."""
        # Step 1: Admin logs in
        login_response = client.post(
            "/api/auth/login", json={"username": "admin", "password": "open-sesame"}
        )
        assert login_response.status_code == 200
        login_data = login_response.get_json()

        # Verify admin role
        assert login_data["user"]["role"] == "superuser"
        token = login_data["token"]

        # Step 2: Admin accesses profile multiple times
        for _ in range(3):
            profile_response = client.get(
                "/api/auth/profile", headers={"X-Auth-Token": token}
            )
            assert profile_response.status_code == 200
            profile_data = profile_response.get_json()
            assert profile_data["user"]["username"] == "admin"

    def test_e2e_session_persistence(self, authenticated_admin):
        """Test that session persists across multiple requests."""
        client = authenticated_admin["client"]
        token = authenticated_admin["token"]

        # Make multiple profile requests with same token
        for _i in range(5):
            response = client.get("/api/auth/profile", headers={"X-Auth-Token": token})
            assert response.status_code == 200
            data = response.get_json()
            assert data["user"]["username"] == "admin"
            # Role should remain consistent
            assert data["user"]["role"] == "superuser"

    def test_e2e_concurrent_user_sessions(self, client):
        """Test multiple users can work concurrently."""
        # User 1: Admin session
        admin_login = client.post(
            "/api/auth/login", json={"username": "admin", "password": "open-sesame"}
        )
        admin_token = admin_login.get_json()["token"]

        # User 2: Guest session
        guest_login = client.post(
            "/api/auth/login", json={"username": "guest", "password": "letmein"}
        )
        guest_token = guest_login.get_json()["token"]

        # Interleaved requests
        admin_profile1 = client.get(
            "/api/auth/profile", headers={"X-Auth-Token": admin_token}
        )
        guest_profile1 = client.get(
            "/api/auth/profile", headers={"X-Auth-Token": guest_token}
        )
        admin_profile2 = client.get(
            "/api/auth/profile", headers={"X-Auth-Token": admin_token}
        )

        # Verify correct data for each user
        assert admin_profile1.get_json()["user"]["username"] == "admin"
        assert guest_profile1.get_json()["user"]["username"] == "guest"
        assert admin_profile2.get_json()["user"]["username"] == "admin"


class TestWebBackendSystemIntegration:
    """End-to-end tests for system-level integration."""

    def test_e2e_status_endpoint_health(self, client):
        """Test complete health check workflow."""
        response = client.get("/api/status")

        assert response.status_code == 200
        data = response.get_json()

        assert data["status"] == "ok"
        assert data["component"] == "web-backend"

    def test_e2e_error_handling_workflow(self, client):
        """Test complete error handling and reporting."""
        # Trigger intentional error
        response = client.get("/api/debug/force-error")

        # Verify error is handled gracefully
        assert response.status_code == 500
        data = response.get_json()

        assert data["status"] == "error"
        assert "forced debug failure" in data["message"]

    def test_e2e_full_system_workflow_unauthenticated(self, client):
        """Test complete workflow for unauthenticated user."""
        # Step 1: Check system status (public)
        status = client.get("/api/status")
        assert status.status_code == 200

        # Step 2: Try to access profile (should fail)
        profile = client.get("/api/auth/profile")
        assert profile.status_code == 401

        # Step 3: Try to login with wrong credentials (should fail)
        bad_login = client.post(
            "/api/auth/login", json={"username": "admin", "password": "wrong"}
        )
        assert bad_login.status_code == 401

        # Step 4: Login with correct credentials (should succeed)
        good_login = client.post(
            "/api/auth/login", json={"username": "admin", "password": "open-sesame"}
        )
        assert good_login.status_code == 200
        token = good_login.get_json()["token"]

        # Step 5: Access profile with token (should succeed)
        profile = client.get("/api/auth/profile", headers={"X-Auth-Token": token})
        assert profile.status_code == 200

    def test_e2e_full_system_workflow_authenticated(self, authenticated_admin):
        """Test complete workflow for authenticated user."""
        client = authenticated_admin["client"]
        token = authenticated_admin["token"]

        # Step 1: Verify authentication state
        profile = client.get("/api/auth/profile", headers={"X-Auth-Token": token})
        assert profile.status_code == 200

        # Step 2: Check system status
        status = client.get("/api/status")
        assert status.status_code == 200

        # Step 3: Access profile again
        profile2 = client.get("/api/auth/profile", headers={"X-Auth-Token": token})
        assert profile2.status_code == 200

        # Verify data consistency
        assert profile.get_json()["user"] == profile2.get_json()["user"]


class TestWebBackendSecurityE2E:
    """End-to-end security workflow tests."""

    def test_e2e_token_isolation(self, client):
        """Test that tokens are properly isolated between users."""
        # Create two sessions
        admin_login = client.post(
            "/api/auth/login", json={"username": "admin", "password": "open-sesame"}
        )
        admin_token = admin_login.get_json()["token"]

        guest_login = client.post(
            "/api/auth/login", json={"username": "guest", "password": "letmein"}
        )
        guest_token = guest_login.get_json()["token"]

        # Verify admin token gives admin access
        admin_profile = client.get(
            "/api/auth/profile", headers={"X-Auth-Token": admin_token}
        )
        assert admin_profile.get_json()["user"]["username"] == "admin"

        # Verify guest token gives guest access (not admin)
        guest_profile = client.get(
            "/api/auth/profile", headers={"X-Auth-Token": guest_token}
        )
        assert guest_profile.get_json()["user"]["username"] == "guest"
        assert guest_profile.get_json()["user"]["username"] != "admin"

    def test_e2e_password_security(self, client):
        """Test that passwords are handled securely."""
        # Attempt login with various password permutations
        wrong_passwords = [
            "open-sesam",  # Missing last character
            "Open-sesame",  # Wrong case
            "open-sesame ",  # Trailing space
            " open-sesame",  # Leading space
        ]

        for password in wrong_passwords:
            response = client.post(
                "/api/auth/login", json={"username": "admin", "password": password}
            )
            # All should fail
            assert response.status_code == 401

        # Only exact password should work
        response = client.post(
            "/api/auth/login", json={"username": "admin", "password": "open-sesame"}
        )
        assert response.status_code == 200

    def test_e2e_unauthorized_access_attempts(self, client):
        """Test system properly denies unauthorized access."""
        # Attempt 1: No token
        r1 = client.get("/api/auth/profile")
        assert r1.status_code == 401

        # Attempt 2: Invalid token
        r2 = client.get("/api/auth/profile", headers={"X-Auth-Token": "fake-token"})
        assert r2.status_code == 403

        # Attempt 3: Empty token
        r3 = client.get("/api/auth/profile", headers={"X-Auth-Token": ""})
        assert r3.status_code == 401

        # All attempts should fail with appropriate errors
        assert r1.get_json()["error"] == "missing-token"
        assert r2.get_json()["error"] == "invalid-token"
        assert r3.get_json()["error"] == "missing-token"
