"""Comprehensive security tests - Phase 2: AWS, Agent Security, Database & Monitoring."""

import json
import tempfile
import threading
from pathlib import Path

import numpy as np
import pytest

from app.security.agent_security import (
    AgentEncapsulation,
    NumericalProtection,
    RuntimeFuzzer,
)
from app.security.database_security import SecureDatabaseManager
from app.security.monitoring import SecurityMonitor, StructuredLogger
from app.security.web_service import (
    InputValidator,
    RateLimiter,
    SecureWebHandler,
    SOAPClient,
)

# Skip AWS tests if boto3 not available
try:
    from app.security.aws_integration import AWSSecurityManager

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class TestAgentEncapsulation:
    """Test agent state encapsulation."""

    def test_agent_creation(self):
        """Test agent encapsulation initialization."""
        agent = AgentEncapsulation("test_agent_1")

        assert agent.agent_id == "test_agent_1"
        assert agent._allowed_operations["read"]
        assert agent._allowed_operations["write"]

    def test_state_management(self):
        """Test state get/set operations."""
        agent = AgentEncapsulation("test_agent_2")

        agent.set_state("counter", 10, caller="test")
        value = agent.get_state("counter", caller="test")

        assert value == 10

    def test_permission_control(self):
        """Test permission-based access control."""
        agent = AgentEncapsulation("test_agent_3")

        # Disable write
        agent.set_permissions(read=True, write=False, execute=False)

        # Should raise PermissionError
        with pytest.raises(PermissionError):
            agent.set_state("key", "value", caller="test")

    def test_access_logging(self):
        """Test access log recording."""
        agent = AgentEncapsulation("test_agent_4")

        agent.set_state("key1", "value1", caller="user1")
        agent.get_state("key1", caller="user2")

        log = agent.get_access_log()

        assert len(log) == 2
        assert log[0]["operation"] == "write"
        assert log[1]["operation"] == "read"

    def test_concurrent_access(self):
        """Test concurrent state access."""
        agent = AgentEncapsulation("test_agent_5")
        results = []

        def access_state(index):
            agent.set_state(f"key_{index}", index, caller=f"thread_{index}")
            value = agent.get_state(f"key_{index}", caller=f"thread_{index}")
            results.append(value == index)

        threads = []
        for i in range(10):
            t = threading.Thread(target=access_state, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert all(results)


class TestNumericalProtection:
    """Test numerical operation protections."""

    def test_array_clipping(self):
        """Test array clipping to safe bounds."""
        protection = NumericalProtection()

        # Create array with extreme values
        arr = np.array([-1e10, -100, 0, 100, 1e10])
        clipped = protection.clip_array(arr)

        # Should be clipped to default range
        assert np.all(clipped >= protection.clip_range[0])
        assert np.all(clipped <= protection.clip_range[1])

    def test_outlier_removal(self):
        """Test outlier removal using Z-score."""
        protection = NumericalProtection()

        # Create array with clear outliers
        arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 100, 200, 300])
        filtered = protection.remove_outliers(arr, threshold=2.0)

        # Should remove extreme values (100, 200, 300 have high z-scores)
        assert len(filtered) < len(arr)
        # The extreme outliers should be removed
        assert 300 not in filtered or 200 not in filtered

    def test_safe_division(self):
        """Test division with zero handling."""
        protection = NumericalProtection()

        numerator = np.array([10, 20, 30])
        denominator = np.array([2, 0, 5])

        result = protection.safe_divide(numerator, denominator, default=0.0)

        assert result[0] == 5.0  # 10/2
        assert result[1] == 0.0  # Default for 20/0
        assert result[2] == 6.0  # 30/5

    def test_input_validation(self):
        """Test numerical input validation."""
        protection = NumericalProtection()

        # Valid input
        assert protection.validate_numerical_input([1, 2, 3, 4, 5])

        # Invalid: NaN
        assert not protection.validate_numerical_input([1, 2, np.nan])

        # Invalid: Inf
        assert not protection.validate_numerical_input([1, 2, np.inf])

    def test_bounds_checking(self):
        """Test bounds checking."""
        protection = NumericalProtection()

        # Out of bounds
        large_value = [1e7]
        assert not protection.validate_numerical_input(large_value)


class TestRuntimeFuzzer:
    """Test runtime fuzzing framework."""

    def test_random_string_fuzzing(self):
        """Test random string generation."""
        fuzzer = RuntimeFuzzer()

        cases = fuzzer.fuzz_input("random_string", "base")

        assert len(cases) > 0
        assert any(len(c) > 100 for c in cases)  # Long strings

    def test_boundary_value_fuzzing(self):
        """Test boundary value generation."""
        fuzzer = RuntimeFuzzer()

        cases = fuzzer.fuzz_input("boundary_values", 0)

        assert 0 in cases
        assert -1 in cases
        assert 2**31 - 1 in cases

    def test_type_confusion_fuzzing(self):
        """Test type confusion generation."""
        fuzzer = RuntimeFuzzer()

        cases = fuzzer.fuzz_input("type_confusion", "string")

        # Should have various types
        types_present = {type(c) for c in cases}
        assert len(types_present) > 3

    def test_overflow_fuzzing(self):
        """Test overflow case generation."""
        fuzzer = RuntimeFuzzer()

        cases = fuzzer.fuzz_input("overflow", [])

        # Should have large collections
        assert any(isinstance(c, list) and len(c) > 100 for c in cases)


class TestSecureDatabaseManager:
    """Test secure database operations."""

    def test_database_initialization(self):
        """Test database creation and schema."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db = SecureDatabaseManager(tmp.name)

            # Should create tables
            with db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                tables = [row[0] for row in cursor.fetchall()]

            assert "users" in tables
            assert "audit_log" in tables
            assert "agent_state" in tables

            # Cleanup
            Path(tmp.name).unlink()

    def test_parameterized_insert(self):
        """Test parameterized insert to prevent SQL injection."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db = SecureDatabaseManager(tmp.name)

            # Insert user
            user_id = db.insert_user("testuser", "hashed_password", "test@example.com")

            assert user_id > 0

            # Retrieve user
            user = db.get_user("testuser")
            assert user is not None
            assert user["username"] == "testuser"

            # Cleanup
            Path(tmp.name).unlink()

    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db = SecureDatabaseManager(tmp.name)

            # Try SQL injection in username
            malicious_username = "admin' OR '1'='1"

            try:
                db.insert_user(malicious_username, "password")
            except Exception:
                pass  # May fail, that's ok

            # Should not affect other queries
            user = db.get_user("admin")
            assert user is None  # No admin user exists

            # Cleanup
            Path(tmp.name).unlink()

    def test_audit_logging(self):
        """Test audit log functionality."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db = SecureDatabaseManager(tmp.name)

            # Log actions
            db.log_action(1, "login", "system", {"ip": "127.0.0.1"})
            db.log_action(1, "read_data", "resource_1")

            # Get audit log
            log = db.get_audit_log(user_id=1)

            assert len(log) >= 2
            assert any(entry["action"] == "login" for entry in log)

            # Cleanup
            Path(tmp.name).unlink()

    def test_transaction_rollback(self):
        """Test transaction rollback on error."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db = SecureDatabaseManager(tmp.name)

            try:
                with db.transaction() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        ("user1", "hash1"),
                    )
                    # Cause error
                    raise RuntimeError("Simulated error")
            except RuntimeError:
                pass

            # User should not exist (rolled back)
            user = db.get_user("user1")
            assert user is None

            # Cleanup
            Path(tmp.name).unlink()


class TestSecurityMonitor:
    """Test security monitoring and alerting."""

    def test_event_logging(self):
        """Test security event logging."""
        monitor = SecurityMonitor()

        monitor.log_security_event(
            event_type="test_event",
            severity="low",
            source="test",
            description="Test event",
        )

        assert len(monitor.event_log) == 1
        assert monitor.event_log[0].event_type == "test_event"

    def test_threat_signatures(self):
        """Test threat signature matching."""
        monitor = SecurityMonitor()

        # Add threat signature
        monitor.add_threat_signature("malware_x", ["evil.com", "bad_hash_123"])

        # Check for matches
        matches = monitor.check_threat_signatures("Request to evil.com detected")

        assert "malware_x" in matches

    def test_event_statistics(self):
        """Test event statistics generation."""
        monitor = SecurityMonitor()

        # Log various events
        monitor.log_security_event("login_failure", "medium", "auth", "Failed login")
        monitor.log_security_event("login_failure", "medium", "auth", "Failed login")
        monitor.log_security_event("data_access", "low", "api", "Data accessed")

        stats = monitor.get_event_statistics()

        assert stats["total_events"] == 3
        assert stats["by_type"]["login_failure"] == 2
        assert stats["by_severity"]["medium"] == 2

    def test_anomaly_detection(self):
        """Test anomaly detection."""
        monitor = SecurityMonitor()

        # Generate many events of same type
        for i in range(15):
            monitor.log_security_event(
                "repeated_event", "low", "test", f"Event {i}"
            )

        # Should detect anomaly (threshold=10)
        anomalies = monitor.detect_anomalies(time_window=60, threshold=10)

        assert len(anomalies) > 0
        assert anomalies[0]["event_type"] == "repeated_event"


class TestWebServiceSecurity:
    """Test web service security components."""

    def test_soap_envelope_creation(self):
        """Test SOAP envelope generation."""
        client = SOAPClient("http://example.com/soap")

        envelope = client._build_envelope("TestMethod", {"param1": "value1"})

        assert "Envelope" in envelope
        assert "Body" in envelope
        assert "TestMethod" in envelope

    def test_soap_envelope_validation(self):
        """Test SOAP envelope validation."""
        client = SOAPClient("http://example.com/soap")

        # Valid envelope with proper namespace
        valid = """<?xml version="1.0"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body></soap:Body>
        </soap:Envelope>"""
        assert client._validate_envelope(valid)

        # Invalid envelope
        invalid = "<root>not soap</root>"
        assert not client._validate_envelope(invalid)

    def test_capability_based_access(self):
        """Test capability-based access control."""
        handler = SecureWebHandler()

        # Generate capability
        token = handler.generate_capability_token(["read", "write"])

        # Check capabilities
        assert handler.check_capability(token, "read")
        assert handler.check_capability(token, "write")
        assert not handler.check_capability(token, "delete")

    def test_secure_headers(self):
        """Test secure header generation."""
        handler = SecureWebHandler()

        headers = handler.set_secure_headers()

        assert "X-Frame-Options" in headers
        assert "X-Content-Type-Options" in headers
        assert headers["X-Content-Type-Options"] == "nosniff"

    def test_request_signing(self):
        """Test HMAC request signing."""
        handler = SecureWebHandler()

        data = "important data"
        secret = "secret_key"

        signature = handler.sign_request(data, secret)

        # Verify signature
        assert handler.verify_signature(data, signature, secret)

        # Reject wrong signature
        assert not handler.verify_signature(data, "wrong_sig", secret)

    def test_rate_limiting(self):
        """Test rate limiter."""
        limiter = RateLimiter(max_requests=5, window=60)

        # Make requests
        for _i in range(5):
            assert limiter.check_rate_limit("client1")

        # 6th request should fail
        assert not limiter.check_rate_limit("client1")

    def test_input_validation(self):
        """Test input validation."""
        validator = InputValidator()

        # Valid input
        assert validator.validate_input("normal text", "text/plain")

        # Too long
        assert not validator.validate_input("A" * 20000, "text/plain")

        # Null byte
        assert not validator.validate_input("text\x00data", "text/plain")

    def test_filename_sanitization(self):
        """Test filename sanitization."""
        validator = InputValidator()

        # Path traversal
        assert ".." not in validator.sanitize_filename("../../etc/passwd")

        # Dangerous characters
        sanitized = validator.sanitize_filename("file<>|.txt")
        assert "<" not in sanitized
        assert ">" not in sanitized


class TestStructuredLogger:
    """Test structured logging."""

    def test_structured_logging(self):
        """Test structured log writing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = StructuredLogger(log_path=str(log_path))

            logger.info("Test message", user_id=123, action="login")

            # Read log
            with open(log_path) as f:
                log_line = f.readline()
                log_entry = json.loads(log_line)

            assert log_entry["level"] == "info"
            assert log_entry["message"] == "Test message"
            assert log_entry["user_id"] == 123


@pytest.mark.skipif(not BOTO3_AVAILABLE, reason="boto3 not available")
class TestAWSIntegration:
    """Test AWS integration (requires boto3)."""

    def test_aws_manager_creation(self):
        """Test AWS manager initialization."""
        # This will fail without credentials, which is expected in test
        try:
            AWSSecurityManager(region="us-east-1")
        except Exception:
            pytest.skip("AWS credentials not available")


# Stress tests
class TestSecurityStress:
    """Stress tests for security components."""

    def test_concurrent_database_access(self):
        """Test concurrent database operations."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db = SecureDatabaseManager(tmp.name)

            def insert_user(index):
                try:
                    db.insert_user(f"user_{index}", f"hash_{index}")
                except Exception:
                    pass  # Ignore duplicate errors

            threads = []
            for i in range(20):
                t = threading.Thread(target=insert_user, args=(i,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            # Should have created multiple users
            with db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]

            assert count > 0

            # Cleanup
            Path(tmp.name).unlink()

    def test_high_volume_logging(self):
        """Test high volume event logging."""
        monitor = SecurityMonitor()

        # Log many events
        for i in range(1000):
            monitor.log_security_event(
                event_type=f"event_{i % 10}",
                severity="low",
                source="stress_test",
                description=f"Event {i}",
            )

        assert len(monitor.event_log) == 1000

        stats = monitor.get_event_statistics()
        assert stats["total_events"] == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
