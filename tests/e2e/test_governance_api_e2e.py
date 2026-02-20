"""
End-to-End tests for the Governance API (FastAPI backend).
Tests complete user flows through the TARL governance system.
"""

import time

import pytest
import requests

# Test configuration
API_BASE_URL = "http://localhost:8001"
TIMEOUT = 10


@pytest.fixture(scope="module")
def api_health_check():
    """Verify API is running before tests."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
        assert response.status_code == 200
        return True
    except requests.exceptions.RequestException:
        pytest.skip("API is not running. Start with: python start_api.py")


class TestGovernanceAPIEndToEnd:
    """End-to-end tests for complete governance workflows."""

    def test_e2e_read_intent_allowed(self, api_health_check):
        """Test complete flow: human reading data (should be allowed)."""
        # Step 1: Submit read intent from human actor
        intent = {
            "actor": "human",
            "action": "read",
            "target": "/data/users/profile.json",
            "origin": "web-ui",
            "context": {"session_id": "test-session-001"},
        }

        response = requests.post(f"{API_BASE_URL}/intent", json=intent, timeout=TIMEOUT)

        # Step 2: Verify governance allowed the request
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Intent accepted under governance"
        assert "governance" in data

        # Step 3: Verify governance details
        governance = data["governance"]
        assert governance["final_verdict"] == "allow"
        assert governance["tarl_version"] == "1.0"
        assert len(governance["votes"]) == 2

        # Step 4: Verify both pillars voted
        pillars = {vote["pillar"] for vote in governance["votes"]}
        assert "Galahad" in pillars
        assert "Cerberus" in pillars

        # Step 5: Verify audit log was written
        audit_response = requests.get(f"{API_BASE_URL}/audit", timeout=TIMEOUT)
        assert audit_response.status_code == 200
        audit_data = audit_response.json()
        assert len(audit_data["records"]) > 0

        # Find the intent we just submitted
        latest_record = audit_data["records"][-1]
        assert latest_record["intent_hash"] == governance["intent_hash"]
        assert latest_record["final_verdict"] == "allow"

    def test_e2e_execute_intent_denied(self, api_health_check):
        """Test complete flow: system executing high-risk action (should be denied)."""
        # Step 1: Submit execute intent from system actor
        intent = {
            "actor": "system",
            "action": "execute",
            "target": "/bin/critical_operation.sh",
            "origin": "automated-task",
            "context": {"automation_id": "auto-001"},
        }

        response = requests.post(f"{API_BASE_URL}/intent", json=intent, timeout=TIMEOUT)

        # Step 2: Verify governance denied the request
        assert response.status_code == 403
        data = response.json()
        assert "Governance denied this request" in data["detail"]["message"]

        # Step 3: Verify governance details show denial
        governance = data["detail"]["governance"]
        assert governance["final_verdict"] == "deny"

        # Step 4: Verify Cerberus blocked it (high-risk action)
        cerberus_votes = [v for v in governance["votes"] if v["pillar"] == "Cerberus"]
        assert len(cerberus_votes) == 1
        assert cerberus_votes[0]["verdict"] == "deny"
        assert "High-risk action blocked" in cerberus_votes[0]["reason"]

    def test_e2e_write_intent_degrade(self, api_health_check):
        """Test complete flow: human writing data (default degrade)."""
        # Step 1: Submit write intent from human actor
        intent = {
            "actor": "human",
            "action": "write",
            "target": "/data/config/settings.json",
            "origin": "web-ui",
            "context": {"user_id": "user-123"},
        }

        response = requests.post(f"{API_BASE_URL}/intent", json=intent, timeout=TIMEOUT)

        # Step 2: Verify governance response (degraded but not denied)
        # Note: Based on TARL rules, write has default "degrade"
        # which means it's allowed through but should have additional controls
        assert response.status_code == 200
        data = response.json()

        # Step 3: Verify governance logged the decision
        governance = data["governance"]
        assert governance["tarl_version"] == "1.0"
        assert "votes" in governance

    def test_e2e_mutate_intent_always_denied(self, api_health_check):
        """Test complete flow: any actor attempting mutate (always denied)."""
        # Test with human actor
        intent = {
            "actor": "human",
            "action": "mutate",
            "target": "/core/system/kernel",
            "origin": "web-ui",
            "context": {},
        }

        response = requests.post(f"{API_BASE_URL}/intent", json=intent, timeout=TIMEOUT)

        # Mutate is always denied (no allowed actors)
        assert response.status_code == 403
        data = response.json()
        governance = data["detail"]["governance"]
        assert governance["final_verdict"] == "deny"

    def test_e2e_governed_execution_flow(self, api_health_check):
        """Test complete execution flow with governance."""
        # Step 1: Submit a read intent for execution
        intent = {
            "actor": "agent",
            "action": "read",
            "target": "/data/cache/temp.json",
            "origin": "api-call",
            "context": {"api_key": "test-key"},
        }

        response = requests.post(f"{API_BASE_URL}/execute", json=intent, timeout=TIMEOUT)

        # Step 2: Verify execution was allowed and completed
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Execution completed under governance"

        # Step 3: Verify execution details
        assert "execution" in data
        execution = data["execution"]
        assert execution["status"] == "executed"
        assert execution["target"] == intent["target"]

        # Step 4: Verify governance was enforced
        governance = data["governance"]
        assert governance["final_verdict"] == "allow"

    def test_e2e_multiple_intents_sequence(self, api_health_check):
        """Test sequence of multiple intents to verify system state."""
        # Submit multiple intents and verify audit trail
        intents = [
            {
                "actor": "human",
                "action": "read",
                "target": "/data/file1.json",
                "origin": "test",
            },
            {
                "actor": "agent",
                "action": "read",
                "target": "/data/file2.json",
                "origin": "test",
            },
            {
                "actor": "human",
                "action": "read",
                "target": "/data/file3.json",
                "origin": "test",
            },
        ]

        submitted_hashes = []

        for intent in intents:
            response = requests.post(f"{API_BASE_URL}/intent", json=intent, timeout=TIMEOUT)
            assert response.status_code == 200
            governance = response.json()["governance"]
            submitted_hashes.append(governance["intent_hash"])

        # Verify all intents in audit log
        audit_response = requests.get(f"{API_BASE_URL}/audit?limit=100", timeout=TIMEOUT)
        assert audit_response.status_code == 200
        audit_data = audit_response.json()

        audit_hashes = [record["intent_hash"] for record in audit_data["records"]]
        for intent_hash in submitted_hashes:
            assert intent_hash in audit_hashes

    def test_e2e_tarl_version_verification(self, api_health_check):
        """Test TARL version consistency across endpoints."""
        # Step 1: Get TARL definition
        tarl_response = requests.get(f"{API_BASE_URL}/tarl", timeout=TIMEOUT)
        assert tarl_response.status_code == 200
        tarl_data = tarl_response.json()
        tarl_version = tarl_data["version"]

        # Step 2: Submit intent and verify same version
        intent = {
            "actor": "human",
            "action": "read",
            "target": "/test/version.json",
            "origin": "test",
        }

        intent_response = requests.post(f"{API_BASE_URL}/intent", json=intent, timeout=TIMEOUT)
        assert intent_response.status_code == 200
        governance = intent_response.json()["governance"]
        assert governance["tarl_version"] == tarl_version

        # Step 3: Verify health check shows same version
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["tarl"] == tarl_version

    def test_e2e_unauthorized_actor_denied(self, api_health_check):
        """Test that unauthorized actor/action combinations are denied."""
        # Agent trying to execute (only system allowed)
        intent = {
            "actor": "agent",
            "action": "execute",
            "target": "/bin/script.sh",
            "origin": "test",
        }

        response = requests.post(f"{API_BASE_URL}/intent", json=intent, timeout=TIMEOUT)

        assert response.status_code == 403
        governance = response.json()["detail"]["governance"]

        # Verify Galahad denied it (actor not authorized)
        galahad_votes = [v for v in governance["votes"] if v["pillar"] == "Galahad"]
        assert len(galahad_votes) == 1
        assert galahad_votes[0]["verdict"] == "deny"
        assert "not ethically authorized" in galahad_votes[0]["reason"]

    def test_e2e_audit_log_immutability(self, api_health_check):
        """Test that audit log is append-only and provides history."""
        # Get initial audit count
        audit1 = requests.get(f"{API_BASE_URL}/audit?limit=1000", timeout=TIMEOUT)
        initial_count = len(audit1.json()["records"])

        # Submit new intents
        for i in range(3):
            intent = {
                "actor": "human",
                "action": "read",
                "target": f"/test/audit_{i}.json",
                "origin": "audit-test",
            }
            requests.post(f"{API_BASE_URL}/intent", json=intent, timeout=TIMEOUT)

        # Verify audit log grew
        audit2 = requests.get(f"{API_BASE_URL}/audit?limit=1000", timeout=TIMEOUT)
        final_count = len(audit2.json()["records"])
        assert final_count >= initial_count + 3

        # Verify TARL signature is consistent (immutable law)
        assert audit1.json()["tarl_signature"] == audit2.json()["tarl_signature"]

    def test_e2e_api_root_information(self, api_health_check):
        """Test API root provides complete service information."""
        response = requests.get(f"{API_BASE_URL}/", timeout=TIMEOUT)
        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "Project AI Governance Host"
        assert "version" in data
        assert data["architecture"] == "Triumvirate"
        assert "endpoints" in data

        # Verify key endpoints are documented
        endpoints = data["endpoints"]
        assert "submit_intent" in endpoints
        assert "governed_execute" in endpoints
        assert "audit_replay" in endpoints
        assert "view_tarl" in endpoints
        assert "health_check" in endpoints


class TestGovernanceAPIEdgeCases:
    """E2E tests for edge cases and error conditions."""

    def test_e2e_missing_intent_fields(self, api_health_check):
        """Test handling of malformed intents."""
        # Missing required field
        incomplete_intent = {
            "actor": "human",
            "action": "read",
            # Missing "target" and "origin"
        }

        response = requests.post(f"{API_BASE_URL}/intent", json=incomplete_intent, timeout=TIMEOUT)

        # FastAPI should return 422 for validation errors
        assert response.status_code == 422

    def test_e2e_invalid_actor_type(self, api_health_check):
        """Test handling of invalid enum values."""
        intent = {
            "actor": "invalid_actor",
            "action": "read",
            "target": "/test/file.json",
            "origin": "test",
        }

        response = requests.post(f"{API_BASE_URL}/intent", json=intent, timeout=TIMEOUT)

        # Should fail validation
        assert response.status_code == 422

    def test_e2e_concurrent_intents(self, api_health_check):
        """Test system handles concurrent requests correctly."""
        import concurrent.futures

        def submit_intent(i):
            intent = {
                "actor": "human",
                "action": "read",
                "target": f"/data/concurrent_{i}.json",
                "origin": "concurrent-test",
            }
            return requests.post(f"{API_BASE_URL}/intent", json=intent, timeout=TIMEOUT)

        # Submit 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(submit_intent, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        for response in results:
            assert response.status_code == 200

        # Verify all were logged in audit
        audit_response = requests.get(f"{API_BASE_URL}/audit?limit=100", timeout=TIMEOUT)
        audit_data = audit_response.json()
        concurrent_records = [r for r in audit_data["records"] if "concurrent-test" in str(r)]
        # Should have at least some of our concurrent requests
        assert len(concurrent_records) > 0


class TestGovernanceAPIPerformance:
    """E2E performance and stress tests."""

    def test_e2e_response_time_acceptable(self, api_health_check):
        """Test that governance evaluation completes in acceptable time."""
        intent = {
            "actor": "human",
            "action": "read",
            "target": "/test/performance.json",
            "origin": "perf-test",
        }

        start_time = time.time()
        response = requests.post(f"{API_BASE_URL}/intent", json=intent, timeout=TIMEOUT)
        elapsed = time.time() - start_time

        assert response.status_code == 200
        # Governance should be fast (< 1 second)
        assert elapsed < 1.0

    def test_e2e_bulk_intent_processing(self, api_health_check):
        """Test system can handle bulk intent submissions."""
        intents = [
            {
                "actor": "human",
                "action": "read",
                "target": f"/data/bulk_{i}.json",
                "origin": "bulk-test",
            }
            for i in range(50)
        ]

        success_count = 0
        for intent in intents:
            response = requests.post(f"{API_BASE_URL}/intent", json=intent, timeout=TIMEOUT)
            if response.status_code == 200:
                success_count += 1

        # Most should succeed
        assert success_count >= 45
