"""
End-to-End Integration tests that span multiple system components.
Tests complete workflows across the entire Project-AI system.
"""

import pytest
import requests

from web.backend.app import app as flask_app

# Configuration
GOVERNANCE_API_URL = "http://localhost:8001"
TIMEOUT = 10


@pytest.fixture
def flask_client():
    """Create Flask test client."""
    flask_app.config.update({"TESTING": True})
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def governance_api_available():
    """Check if governance API is running."""
    try:
        response = requests.get(f"{GOVERNANCE_API_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        pass
    pytest.skip("Governance API not running. Start with: python start_api.py")


@pytest.fixture
def authenticated_flask_admin(flask_client):
    """Create authenticated admin session in Flask backend."""
    login_payload = {"username": "admin", "password": "open-sesame"}
    response = flask_client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.get_json()
    return {"client": flask_client, "token": data["token"], "user": data["user"]}


class TestCrossComponentIntegration:
    """Test workflows that span multiple components."""

    def test_e2e_web_to_governance_flow(
        self, authenticated_flask_admin, governance_api_available
    ):
        """
        Test complete flow: User authenticates in web backend,
        then submits governed intent.
        """
        # Step 1: User is authenticated in Flask backend
        client = authenticated_flask_admin["client"]
        token = authenticated_flask_admin["token"]

        # Step 2: Verify Flask auth works
        profile_response = client.get(
            "/api/auth/profile", headers={"X-Auth-Token": token}
        )
        assert profile_response.status_code == 200
        user_data = profile_response.get_json()["user"]
        username = user_data["username"]

        # Step 3: User submits intent to governance API
        # (Simulating web frontend making request)
        intent = {
            "actor": "human",
            "action": "read",
            "target": f"/data/{username}/profile.json",
            "origin": "web-frontend",
            "context": {"authenticated_user": username},
        }

        gov_response = requests.post(
            f"{GOVERNANCE_API_URL}/intent", json=intent, timeout=TIMEOUT
        )

        # Step 4: Verify governance approved request
        assert gov_response.status_code == 200
        gov_data = gov_response.json()
        assert gov_data["governance"]["final_verdict"] == "allow"

        # Step 5: Verify audit trail
        audit_response = requests.get(f"{GOVERNANCE_API_URL}/audit", timeout=TIMEOUT)
        assert audit_response.status_code == 200
        audit_data = audit_response.json()

        # Find our intent in audit
        intent_hash = gov_data["governance"]["intent_hash"]
        audit_hashes = [r["intent_hash"] for r in audit_data["records"]]
        assert intent_hash in audit_hashes

    def test_e2e_multi_user_governance_isolation(
        self, flask_client, governance_api_available
    ):
        """
        Test that multiple authenticated users can submit
        governed intents independently.
        """
        # Step 1: Create two user sessions
        admin_login = flask_client.post(
            "/api/auth/login", json={"username": "admin", "password": "open-sesame"}
        )
        admin_token = admin_login.get_json()["token"]

        guest_login = flask_client.post(
            "/api/auth/login", json={"username": "guest", "password": "letmein"}
        )
        guest_token = guest_login.get_json()["token"]

        # Step 2: Each user submits their own intent
        admin_intent = {
            "actor": "human",
            "action": "read",
            "target": "/data/admin/config.json",
            "origin": "web-frontend",
            "context": {"user": "admin"},
        }

        guest_intent = {
            "actor": "human",
            "action": "read",
            "target": "/data/guest/data.json",
            "origin": "web-frontend",
            "context": {"user": "guest"},
        }

        admin_response = requests.post(
            f"{GOVERNANCE_API_URL}/intent", json=admin_intent, timeout=TIMEOUT
        )

        guest_response = requests.post(
            f"{GOVERNANCE_API_URL}/intent", json=guest_intent, timeout=TIMEOUT
        )

        # Step 3: Verify both intents processed independently
        assert admin_response.status_code == 200
        assert guest_response.status_code == 200

        admin_hash = admin_response.json()["governance"]["intent_hash"]
        guest_hash = guest_response.json()["governance"]["intent_hash"]

        # Hashes should be different (different intents)
        assert admin_hash != guest_hash

    def test_e2e_role_based_governance(self, flask_client, governance_api_available):
        """
        Test that user roles affect governance decisions.
        """
        # Step 1: Login as admin
        admin_login = flask_client.post(
            "/api/auth/login", json={"username": "admin", "password": "open-sesame"}
        )
        admin_user = admin_login.get_json()["user"]
        assert admin_user["role"] == "superuser"

        # Step 2: Login as guest
        guest_login = flask_client.post(
            "/api/auth/login", json={"username": "guest", "password": "letmein"}
        )
        guest_user = guest_login.get_json()["user"]
        assert guest_user["role"] == "viewer"

        # Step 3: Both submit read intents (should be allowed)
        admin_intent = {
            "actor": "human",
            "action": "read",
            "target": "/data/file.json",
            "origin": "web-frontend",
            "context": {"role": "superuser"},
        }

        guest_intent = {
            "actor": "human",
            "action": "read",
            "target": "/data/file.json",
            "origin": "web-frontend",
            "context": {"role": "viewer"},
        }

        admin_response = requests.post(
            f"{GOVERNANCE_API_URL}/intent", json=admin_intent, timeout=TIMEOUT
        )

        guest_response = requests.post(
            f"{GOVERNANCE_API_URL}/intent", json=guest_intent, timeout=TIMEOUT
        )

        # Both should be allowed to read
        assert admin_response.status_code == 200
        assert guest_response.status_code == 200


class TestSystemHealthAndMonitoring:
    """Test system-wide health and monitoring workflows."""

    def test_e2e_complete_system_health_check(
        self, flask_client, governance_api_available
    ):
        """
        Test complete system health across all components.
        """
        # Step 1: Check Flask backend health
        flask_status = flask_client.get("/api/status")
        assert flask_status.status_code == 200
        flask_data = flask_status.get_json()
        assert flask_data["status"] == "ok"

        # Step 2: Check Governance API health
        gov_health = requests.get(f"{GOVERNANCE_API_URL}/health", timeout=TIMEOUT)
        assert gov_health.status_code == 200
        gov_data = gov_health.json()
        assert gov_data["status"] == "governance-online"

        # Step 3: Verify TARL version
        tarl_response = requests.get(f"{GOVERNANCE_API_URL}/tarl", timeout=TIMEOUT)
        assert tarl_response.status_code == 200
        tarl_data = tarl_response.json()
        assert "version" in tarl_data
        assert tarl_data["version"] == gov_data["tarl"]

    def test_e2e_system_availability_under_load(
        self, flask_client, governance_api_available
    ):
        """
        Test system remains available under concurrent load.
        """
        import concurrent.futures

        def check_flask_health():
            return flask_client.get("/api/status")

        def check_gov_health():
            return requests.get(f"{GOVERNANCE_API_URL}/health", timeout=TIMEOUT)

        # Step 1: Concurrent health checks
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            flask_futures = [executor.submit(check_flask_health) for _ in range(10)]
            gov_futures = [executor.submit(check_gov_health) for _ in range(10)]

            flask_results = [f.result() for f in flask_futures]
            gov_results = [f.result() for f in gov_futures]

        # Step 2: Verify all health checks succeeded
        for response in flask_results:
            assert response.status_code == 200

        for response in gov_results:
            assert response.status_code == 200


class TestCompleteUserJourneys:
    """Test complete end-to-end user journeys through the entire system."""

    def test_e2e_new_user_onboarding_and_first_action(
        self, flask_client, governance_api_available
    ):
        """
        Test complete journey: New user login -> authenticate -> perform action.
        """
        # Step 1: User logs into web backend
        login_response = flask_client.post(
            "/api/auth/login", json={"username": "guest", "password": "letmein"}
        )
        assert login_response.status_code == 200
        login_data = login_response.get_json()
        token = login_data["token"]
        username = login_data["user"]["username"]

        # Step 2: User verifies their profile
        profile_response = flask_client.get(
            "/api/auth/profile", headers={"X-Auth-Token": token}
        )
        assert profile_response.status_code == 200
        profile_data = profile_response.get_json()
        assert profile_data["user"]["username"] == username

        # Step 3: User performs first governed action
        intent = {
            "actor": "human",
            "action": "read",
            "target": f"/data/{username}/welcome.json",
            "origin": "web-frontend",
            "context": {"first_action": True, "user": username},
        }

        gov_response = requests.post(
            f"{GOVERNANCE_API_URL}/intent", json=intent, timeout=TIMEOUT
        )

        # Step 4: Verify action was governed and allowed
        assert gov_response.status_code == 200
        gov_data = gov_response.json()
        assert gov_data["governance"]["final_verdict"] == "allow"

        # Step 5: Verify action appears in audit log
        audit_response = requests.get(
            f"{GOVERNANCE_API_URL}/audit?limit=50", timeout=TIMEOUT
        )
        assert audit_response.status_code == 200
        audit_data = audit_response.json()

        intent_hash = gov_data["governance"]["intent_hash"]
        audit_hashes = [r["intent_hash"] for r in audit_data["records"]]
        assert intent_hash in audit_hashes

    def test_e2e_admin_privileged_workflow(
        self, flask_client, governance_api_available
    ):
        """
        Test complete admin workflow with multiple operations.
        """
        # Step 1: Admin logs in
        login_response = flask_client.post(
            "/api/auth/login", json={"username": "admin", "password": "open-sesame"}
        )
        assert login_response.status_code == 200
        admin_data = login_response.get_json()
        token = admin_data["token"]

        # Step 2: Admin verifies superuser role
        profile_response = flask_client.get(
            "/api/auth/profile", headers={"X-Auth-Token": token}
        )
        assert profile_response.status_code == 200
        assert profile_response.get_json()["user"]["role"] == "superuser"

        # Step 3: Admin performs multiple governed operations
        operations = [
            {
                "actor": "human",
                "action": "read",
                "target": "/data/system/logs.json",
                "origin": "admin-panel",
            },
            {
                "actor": "human",
                "action": "read",
                "target": "/data/system/config.json",
                "origin": "admin-panel",
            },
            {
                "actor": "human",
                "action": "write",
                "target": "/data/system/settings.json",
                "origin": "admin-panel",
            },
        ]

        results = []
        for op in operations:
            response = requests.post(
                f"{GOVERNANCE_API_URL}/intent", json=op, timeout=TIMEOUT
            )
            results.append(response)

        # Step 4: Verify all operations were processed
        # (read should be allowed, write might be degraded)
        assert all(r.status_code in [200, 403] for r in results)

        # At least reads should be allowed
        read_results = [r for r in results[:2]]
        assert all(r.status_code == 200 for r in read_results)

    def test_e2e_security_denial_workflow(self, flask_client, governance_api_available):
        """
        Test complete workflow when security denies an action.
        """
        # Step 1: User authenticates
        login_response = flask_client.post(
            "/api/auth/login", json={"username": "guest", "password": "letmein"}
        )
        assert login_response.status_code == 200

        # Step 2: User attempts high-risk action
        dangerous_intent = {
            "actor": "system",  # Attempting to impersonate system
            "action": "execute",
            "target": "/bin/dangerous_script.sh",
            "origin": "web-frontend",
        }

        response = requests.post(
            f"{GOVERNANCE_API_URL}/intent", json=dangerous_intent, timeout=TIMEOUT
        )

        # Step 3: Verify governance denied the action
        assert response.status_code == 403
        data = response.json()
        assert "denied" in data["detail"]["message"].lower()

        # Step 4: Verify denial was logged in audit
        governance = data["detail"]["governance"]
        assert governance["final_verdict"] == "deny"

        # Step 5: Check audit log contains the denial
        audit_response = requests.get(
            f"{GOVERNANCE_API_URL}/audit?limit=50", timeout=TIMEOUT
        )
        assert audit_response.status_code == 200
        audit_data = audit_response.json()

        # Find the denied intent
        denied_records = [
            r for r in audit_data["records"] if r["final_verdict"] == "deny"
        ]
        assert len(denied_records) > 0


class TestSystemResilienceE2E:
    """Test system resilience and error recovery."""

    def test_e2e_partial_system_degradation(self, flask_client):
        """
        Test Flask backend continues operating even if governance API is down.
        """
        # Step 1: Flask backend operations should work independently
        login_response = flask_client.post(
            "/api/auth/login", json={"username": "admin", "password": "open-sesame"}
        )
        assert login_response.status_code == 200
        token = login_response.get_json()["token"]

        # Step 2: Profile access should work
        profile_response = flask_client.get(
            "/api/auth/profile", headers={"X-Auth-Token": token}
        )
        assert profile_response.status_code == 200

        # Step 3: Status check should work
        status_response = flask_client.get("/api/status")
        assert status_response.status_code == 200

    def test_e2e_error_recovery_workflow(self, flask_client, governance_api_available):
        """
        Test system recovers from errors and continues operating.
        """
        # Step 1: Trigger error in Flask backend
        error_response = flask_client.get("/api/debug/force-error")
        assert error_response.status_code == 500

        # Step 2: Verify system still operational after error
        status_response = flask_client.get("/api/status")
        assert status_response.status_code == 200

        # Step 3: Verify governance API still operational
        gov_health = requests.get(f"{GOVERNANCE_API_URL}/health", timeout=TIMEOUT)
        assert gov_health.status_code == 200

        # Step 4: Verify normal operations work after error
        login_response = flask_client.post(
            "/api/auth/login", json={"username": "admin", "password": "open-sesame"}
        )
        assert login_response.status_code == 200


class TestAuditAndCompliance:
    """Test audit trail and compliance across system."""

    def test_e2e_complete_audit_trail(self, flask_client, governance_api_available):
        """
        Test that all user actions create proper audit trail.
        """
        # Step 1: User logs in (Flask audit point)
        login_response = flask_client.post(
            "/api/auth/login", json={"username": "admin", "password": "open-sesame"}
        )
        assert login_response.status_code == 200
        token = login_response.get_json()["token"]

        # Step 2: User accesses profile (Flask audit point)
        profile_response = flask_client.get(
            "/api/auth/profile", headers={"X-Auth-Token": token}
        )
        assert profile_response.status_code == 200

        # Step 3: Get initial governance audit count
        audit1 = requests.get(f"{GOVERNANCE_API_URL}/audit?limit=1000", timeout=TIMEOUT)
        initial_count = len(audit1.json()["records"])

        # Step 4: User performs governed actions
        intents = [
            {
                "actor": "human",
                "action": "read",
                "target": f"/data/file{i}.json",
                "origin": "test",
            }
            for i in range(3)
        ]

        for intent in intents:
            requests.post(f"{GOVERNANCE_API_URL}/intent", json=intent, timeout=TIMEOUT)

        # Step 5: Verify all actions in governance audit
        audit2 = requests.get(f"{GOVERNANCE_API_URL}/audit?limit=1000", timeout=TIMEOUT)
        final_count = len(audit2.json()["records"])

        # Should have at least 3 new records
        assert final_count >= initial_count + 3

    def test_e2e_tarl_immutability(self, governance_api_available):
        """
        Test that TARL governance rules are immutable.
        """
        # Step 1: Get TARL definition
        tarl1 = requests.get(f"{GOVERNANCE_API_URL}/tarl", timeout=TIMEOUT)
        assert tarl1.status_code == 200
        tarl1_data = tarl1.json()

        # Step 2: Submit multiple intents
        for i in range(5):
            intent = {
                "actor": "human",
                "action": "read",
                "target": f"/data/test{i}.json",
                "origin": "immutability-test",
            }
            requests.post(f"{GOVERNANCE_API_URL}/intent", json=intent, timeout=TIMEOUT)

        # Step 3: Get TARL definition again
        tarl2 = requests.get(f"{GOVERNANCE_API_URL}/tarl", timeout=TIMEOUT)
        assert tarl2.status_code == 200
        tarl2_data = tarl2.json()

        # Step 4: Verify TARL hasn't changed
        assert tarl1_data == tarl2_data

        # Step 5: Verify TARL signature is consistent
        audit = requests.get(f"{GOVERNANCE_API_URL}/audit", timeout=TIMEOUT)
        audit_data = audit.json()
        assert "tarl_signature" in audit_data
        # Signature should be deterministic
        assert len(audit_data["tarl_signature"]) == 64  # SHA-256 hex
