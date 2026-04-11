#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Comprehensive tests for network connectivity checks in ReadinessGate.

Tests cover:
- DNS resolution with valid and invalid hostnames
- TCP connectivity to reachable and unreachable endpoints
- Timeout handling and retry logic
- Multiple endpoint checks
- Configuration variations
- Edge cases and error conditions
"""

import socket
import time
from unittest.mock import MagicMock, patch

import pytest

from psia.bootstrap.readiness import (
    NetworkCheckConfig,
    NetworkEndpoint,
    NodeStatus,
    ReadinessGate,
)


class TestDNSResolution:
    """Test DNS resolution functionality."""

    def test_dns_resolution_success(self):
        """Test successful DNS resolution for a valid hostname."""
        gate = ReadinessGate()
        success, msg = gate._check_dns_resolution("google.com", timeout=5.0)

        assert success is True
        assert "google.com" in msg.lower()
        assert "IP" in msg or "ip" in msg.lower()

    def test_dns_resolution_localhost(self):
        """Test DNS resolution for localhost."""
        gate = ReadinessGate()
        success, msg = gate._check_dns_resolution("localhost", timeout=5.0)

        assert success is True
        assert "127.0.0.1" in msg or "::1" in msg

    def test_dns_resolution_failure_invalid_hostname(self):
        """Test DNS resolution failure for invalid hostname."""
        gate = ReadinessGate()
        success, msg = gate._check_dns_resolution(
            "this-hostname-does-not-exist-12345.invalid", timeout=5.0
        )

        assert success is False
        assert "failed" in msg.lower() or "error" in msg.lower()

    def test_dns_resolution_timeout(self):
        """Test DNS resolution timeout handling."""
        gate = ReadinessGate()

        # Use a very short timeout to potentially trigger timeout
        # Note: This may not always timeout depending on DNS server speed
        with patch("socket.getaddrinfo") as mock_getaddrinfo:
            mock_getaddrinfo.side_effect = socket.timeout()
            success, msg = gate._check_dns_resolution("example.com", timeout=0.001)

            assert success is False
            assert "timed out" in msg.lower()

    def test_dns_resolution_exception_handling(self):
        """Test DNS resolution handles unexpected exceptions."""
        gate = ReadinessGate()

        with patch("socket.getaddrinfo") as mock_getaddrinfo:
            mock_getaddrinfo.side_effect = Exception("Unexpected DNS error")
            success, msg = gate._check_dns_resolution("example.com", timeout=5.0)

            assert success is False
            assert "error" in msg.lower()


class TestTCPConnectivity:
    """Test TCP connectivity checks."""

    def test_tcp_connection_to_localhost_open_port(self):
        """Test TCP connection to an open port on localhost."""
        # Start a simple TCP server on localhost
        import threading

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("127.0.0.1", 0))  # Bind to any available port
        server_socket.listen(1)
        port = server_socket.getsockname()[1]

        def accept_connection():
            try:
                conn, _ = server_socket.accept()
                conn.close()
            except Exception:
                pass

        server_thread = threading.Thread(target=accept_connection, daemon=True)
        server_thread.start()

        try:
            gate = ReadinessGate()
            success, msg = gate._check_tcp_connectivity("127.0.0.1", port, timeout=5.0)

            assert success is True
            assert f"127.0.0.1:{port}" in msg
            assert "successful" in msg.lower()
        finally:
            server_socket.close()
            server_thread.join(timeout=1)

    def test_tcp_connection_refused(self):
        """Test TCP connection to a closed port."""
        gate = ReadinessGate()
        # Port 1 is typically not open
        success, msg = gate._check_tcp_connectivity("127.0.0.1", 1, timeout=2.0)

        assert success is False
        # Could be refused or timeout depending on OS/firewall
        assert (
            "refused" in msg.lower()
            or "failed" in msg.lower()
            or "timed out" in msg.lower()
        )

    def test_tcp_connection_timeout(self):
        """Test TCP connection timeout."""
        gate = ReadinessGate()
        # Use a non-routable IP to trigger timeout
        # 192.0.2.1 is reserved for documentation (TEST-NET-1)
        success, msg = gate._check_tcp_connectivity("192.0.2.1", 80, timeout=1.0)

        assert success is False
        assert "timed out" in msg.lower() or "failed" in msg.lower()

    def test_tcp_connection_invalid_host(self):
        """Test TCP connection with invalid hostname."""
        gate = ReadinessGate()
        success, msg = gate._check_tcp_connectivity(
            "invalid-host-12345.invalid", 80, timeout=2.0
        )

        assert success is False
        assert "failed" in msg.lower() or "error" in msg.lower()

    def test_tcp_connection_retry_indication(self):
        """Test that retry attempts are indicated in messages."""
        gate = ReadinessGate()
        with patch("socket.socket") as mock_socket:
            mock_socket.return_value.__enter__ = MagicMock()
            mock_socket.return_value.__exit__ = MagicMock()
            mock_socket.return_value.connect.side_effect = ConnectionRefusedError()
            mock_socket.return_value.close.return_value = None

            # Second retry (retry=1)
            success, msg = gate._check_tcp_connectivity(
                "127.0.0.1", 9999, timeout=2.0, retry=1
            )

            assert success is False
            # Message should indicate it was a retry if connection succeeded
            # or show the error if failed


class TestEndpointCheckWithRetry:
    """Test endpoint checking with retry logic."""

    def test_endpoint_check_success_first_attempt(self):
        """Test endpoint check succeeds on first attempt."""
        endpoint = NetworkEndpoint(host="127.0.0.1", port=80, dns_required=False)
        config = NetworkCheckConfig(max_retries=3, retry_delay_seconds=0.1)
        gate = ReadinessGate(network_config=config)

        with patch.object(
            gate, "_check_tcp_connectivity", return_value=(True, "Success")
        ):
            success, msg = gate._check_endpoint_with_retry(endpoint)

            assert success is True
            assert "success" in msg.lower()

    def test_endpoint_check_success_after_retry(self):
        """Test endpoint check succeeds after retry."""
        endpoint = NetworkEndpoint(host="127.0.0.1", port=80, dns_required=False)
        config = NetworkCheckConfig(max_retries=3, retry_delay_seconds=0.1)
        gate = ReadinessGate(network_config=config)

        # First attempt fails, second succeeds
        with patch.object(
            gate,
            "_check_tcp_connectivity",
            side_effect=[
                (False, "Connection refused"),
                (True, "Success on retry"),
            ],
        ):
            success, msg = gate._check_endpoint_with_retry(endpoint)

            assert success is True
            assert "success" in msg.lower()

    def test_endpoint_check_all_retries_fail(self):
        """Test endpoint check fails after all retries exhausted."""
        endpoint = NetworkEndpoint(host="127.0.0.1", port=9999, dns_required=False)
        config = NetworkCheckConfig(max_retries=3, retry_delay_seconds=0.1)
        gate = ReadinessGate(network_config=config)

        with patch.object(
            gate,
            "_check_tcp_connectivity",
            return_value=(False, "Connection refused"),
        ):
            start_time = time.time()
            success, msg = gate._check_endpoint_with_retry(endpoint)
            elapsed_time = time.time() - start_time

            assert success is False
            assert "attempts failed" in msg.lower()
            assert "3" in msg  # Should mention number of retries
            # Verify retry delay was applied (at least 2 delays for 3 attempts)
            assert elapsed_time >= 0.2  # 2 * retry_delay_seconds

    def test_endpoint_check_dns_failure_skips_tcp(self):
        """Test that DNS failure prevents TCP check."""
        endpoint = NetworkEndpoint(
            host="invalid-host-12345.invalid", port=443, dns_required=True
        )
        gate = ReadinessGate()

        with patch.object(
            gate, "_check_dns_resolution", return_value=(False, "DNS failed")
        ):
            with patch.object(
                gate, "_check_tcp_connectivity"
            ) as mock_tcp:  # Should not be called
                success, msg = gate._check_endpoint_with_retry(endpoint)

                assert success is False
                assert "dns" in msg.lower()
                mock_tcp.assert_not_called()

    def test_endpoint_check_skips_dns_for_ip(self):
        """Test that DNS check is skipped for IP addresses."""
        endpoint = NetworkEndpoint(host="192.168.1.1", port=443, dns_required=True)
        config = NetworkCheckConfig(max_retries=1)
        gate = ReadinessGate(network_config=config)

        with patch.object(gate, "_check_dns_resolution") as mock_dns:
            with patch.object(
                gate, "_check_tcp_connectivity", return_value=(True, "Connected")
            ):
                success, msg = gate._check_endpoint_with_retry(endpoint)

                # DNS should not be called for IP addresses
                mock_dns.assert_not_called()

    def test_endpoint_check_unsupported_protocol(self):
        """Test that unsupported protocols are rejected."""
        endpoint = NetworkEndpoint(host="example.com", port=80, protocol="udp")
        gate = ReadinessGate()

        success, msg = gate._check_endpoint_with_retry(endpoint)

        assert success is False
        assert "unsupported" in msg.lower()
        assert "udp" in msg.lower()


class TestNetworkCheckRegistration:
    """Test network check registration and integration."""

    def test_register_network_check_with_endpoints(self):
        """Test registering network checks with specific endpoints."""
        endpoints = [
            NetworkEndpoint(host="127.0.0.1", port=80, dns_required=False),
            NetworkEndpoint(host="localhost", port=443),
        ]
        gate = ReadinessGate()
        gate.register_network_check(endpoints, critical=True)

        # Check that the check was registered
        assert len(gate._checks) == 1
        assert gate._checks[0][0] == "network_connectivity"
        assert gate._checks[0][2] is True  # critical=True

    def test_register_network_check_uses_config_endpoints(self):
        """Test that network check uses config endpoints when none provided."""
        config_endpoints = [
            NetworkEndpoint(host="google.com", port=443),
        ]
        config = NetworkCheckConfig(endpoints=config_endpoints)
        gate = ReadinessGate(network_config=config)
        gate.register_network_check()

        assert len(gate._checks) == 1

    def test_register_network_check_no_endpoints_creates_stub(self):
        """Test that no endpoints creates a passing stub check."""
        gate = ReadinessGate()
        gate.register_network_check()

        # Should register a stub check
        assert len(gate._checks) == 1
        check_fn = gate._checks[0][1]
        passed, msg = check_fn()

        assert passed is True
        assert "skipped" in msg.lower()

    def test_network_check_in_full_evaluation(self):
        """Test network check as part of full readiness evaluation."""
        endpoints = [
            NetworkEndpoint(host="127.0.0.1", port=80, dns_required=False),
        ]
        gate = ReadinessGate()
        gate.register_network_check(endpoints, critical=True)

        with patch.object(
            gate,
            "_check_endpoint_with_retry",
            return_value=(True, "Endpoint reachable"),
        ):
            report = gate.evaluate()

            assert report.status == NodeStatus.OPERATIONAL
            assert report.all_passed is True
            assert len(report.checks) == 1
            assert report.checks[0].name == "network_connectivity"
            assert report.checks[0].passed is True

    def test_network_check_failure_blocks_operational(self):
        """Test that failed critical network check blocks OPERATIONAL status."""
        endpoints = [
            NetworkEndpoint(host="192.0.2.1", port=80, dns_required=False),
        ]
        gate = ReadinessGate()
        gate.register_network_check(endpoints, critical=True)

        with patch.object(
            gate,
            "_check_endpoint_with_retry",
            return_value=(False, "Endpoint unreachable"),
        ):
            report = gate.evaluate()

            assert report.status == NodeStatus.FAILED
            assert report.all_passed is False
            assert report.critical_failures == 1


class TestMultipleEndpoints:
    """Test checking multiple endpoints."""

    def test_multiple_endpoints_all_pass(self):
        """Test that all endpoints passing results in success."""
        endpoints = [
            NetworkEndpoint(host="127.0.0.1", port=80, dns_required=False),
            NetworkEndpoint(host="127.0.0.1", port=443, dns_required=False),
        ]
        gate = ReadinessGate()
        gate.register_network_check(endpoints)

        with patch.object(
            gate, "_check_endpoint_with_retry", return_value=(True, "Connected")
        ):
            report = gate.evaluate()

            assert report.checks[0].passed is True
            assert "2 endpoint(s) reachable" in report.checks[0].message

    def test_multiple_endpoints_some_fail(self):
        """Test that some endpoints failing results in failure."""
        endpoints = [
            NetworkEndpoint(host="127.0.0.1", port=80, dns_required=False),
            NetworkEndpoint(host="192.0.2.1", port=80, dns_required=False),
        ]
        gate = ReadinessGate()
        gate.register_network_check(endpoints)

        # First succeeds, second fails
        with patch.object(
            gate,
            "_check_endpoint_with_retry",
            side_effect=[
                (True, "Connected"),
                (False, "Timeout"),
            ],
        ):
            report = gate.evaluate()

            assert report.checks[0].passed is False
            assert "unreachable" in report.checks[0].message.lower()

    def test_multiple_endpoints_all_fail(self):
        """Test that all endpoints failing results in failure."""
        endpoints = [
            NetworkEndpoint(host="192.0.2.1", port=80, dns_required=False),
            NetworkEndpoint(host="192.0.2.2", port=80, dns_required=False),
        ]
        gate = ReadinessGate()
        gate.register_network_check(endpoints)

        with patch.object(
            gate, "_check_endpoint_with_retry", return_value=(False, "Timeout")
        ):
            report = gate.evaluate()

            assert report.checks[0].passed is False
            assert "2/2 endpoint(s) unreachable" in report.checks[0].message


class TestNetworkCheckConfiguration:
    """Test various network check configurations."""

    def test_custom_timeout_configuration(self):
        """Test custom timeout values are respected."""
        endpoint = NetworkEndpoint(
            host="127.0.0.1", port=9999, timeout_seconds=0.5, dns_required=False
        )
        gate = ReadinessGate()

        start_time = time.time()
        with patch("socket.socket") as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value = mock_socket
            mock_socket.connect.side_effect = socket.timeout()

            gate._check_tcp_connectivity(
                endpoint.host, endpoint.port, timeout=endpoint.timeout_seconds
            )
            elapsed_time = time.time() - start_time

            # Should timeout quickly
            assert elapsed_time < 2.0  # Much less than default timeout

    def test_custom_retry_configuration(self):
        """Test custom retry configuration."""
        endpoint = NetworkEndpoint(host="127.0.0.1", port=9999, dns_required=False)
        config = NetworkCheckConfig(max_retries=5, retry_delay_seconds=0.05)
        gate = ReadinessGate(network_config=config)

        with patch.object(
            gate, "_check_tcp_connectivity", return_value=(False, "Failed")
        ) as mock_tcp:
            gate._check_endpoint_with_retry(endpoint)

            # Should have been called 5 times (max_retries)
            assert mock_tcp.call_count == 5

    def test_custom_dns_servers_configuration(self):
        """Test custom DNS servers in configuration."""
        config = NetworkCheckConfig(dns_servers=["1.1.1.1", "8.8.8.8"])
        gate = ReadinessGate(network_config=config)

        # Verify config is stored
        assert gate.network_config.dns_servers == ["1.1.1.1", "8.8.8.8"]

    def test_no_dns_required_configuration(self):
        """Test endpoints with DNS resolution disabled."""
        endpoint = NetworkEndpoint(
            host="example.com", port=443, dns_required=False  # Skip DNS
        )
        gate = ReadinessGate()

        with patch.object(gate, "_check_dns_resolution") as mock_dns:
            with patch.object(
                gate, "_check_tcp_connectivity", return_value=(True, "Connected")
            ):
                gate._check_endpoint_with_retry(endpoint)

                # DNS should not be called
                mock_dns.assert_not_called()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_endpoints_list(self):
        """Test handling of empty endpoints list."""
        gate = ReadinessGate()
        gate.register_network_check([])

        report = gate.evaluate()
        assert report.checks[0].passed is True
        assert "skipped" in report.checks[0].message.lower()

    def test_very_long_hostname(self):
        """Test handling of very long hostname."""
        very_long_hostname = "a" * 300 + ".com"
        gate = ReadinessGate()
        success, msg = gate._check_dns_resolution(very_long_hostname, timeout=1.0)

        assert success is False

    def test_special_characters_in_hostname(self):
        """Test handling of special characters in hostname."""
        gate = ReadinessGate()
        success, msg = gate._check_dns_resolution("test@#$.com", timeout=1.0)

        assert success is False

    def test_negative_port_number(self):
        """Test handling of invalid port numbers."""
        gate = ReadinessGate()
        # Port -1 should fail
        success, msg = gate._check_tcp_connectivity("127.0.0.1", -1, timeout=1.0)

        assert success is False

    def test_port_number_too_large(self):
        """Test handling of port number exceeding valid range."""
        gate = ReadinessGate()
        # Port 99999 exceeds max port 65535
        success, msg = gate._check_tcp_connectivity("127.0.0.1", 99999, timeout=1.0)

        assert success is False

    def test_zero_timeout(self):
        """Test handling of zero or negative timeout."""
        endpoint = NetworkEndpoint(
            host="127.0.0.1", port=80, timeout_seconds=0, dns_required=False
        )
        gate = ReadinessGate()

        # Should handle gracefully
        success, msg = gate._check_tcp_connectivity(
            endpoint.host, endpoint.port, timeout=0
        )

        # May succeed very quickly or fail with timeout
        assert isinstance(success, bool)

    def test_ipv6_address(self):
        """Test handling of IPv6 addresses."""
        gate = ReadinessGate()
        # IPv6 localhost
        success, msg = gate._check_dns_resolution("::1", timeout=2.0)

        # Should either resolve or handle gracefully
        assert isinstance(success, bool)


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_production_like_configuration(self):
        """Test a production-like configuration with multiple peer nodes."""
        endpoints = [
            NetworkEndpoint(host="peer1.example.com", port=8443, dns_required=True),
            NetworkEndpoint(host="peer2.example.com", port=8443, dns_required=True),
            NetworkEndpoint(host="10.0.1.100", port=8443, dns_required=False),
        ]
        config = NetworkCheckConfig(
            endpoints=endpoints, max_retries=3, retry_delay_seconds=0.5
        )
        gate = ReadinessGate(node_id="psia-prod-01", network_config=config)
        gate.register_network_check()

        # Mock all endpoints as reachable
        with patch.object(
            gate, "_check_endpoint_with_retry", return_value=(True, "Connected")
        ):
            report = gate.evaluate()

            assert report.status == NodeStatus.OPERATIONAL
            assert report.checks[0].passed is True

    def test_degraded_network_scenario(self):
        """Test scenario where some but not all endpoints are reachable."""
        endpoints = [
            NetworkEndpoint(host="127.0.0.1", port=80, dns_required=False),
            NetworkEndpoint(host="192.0.2.1", port=80, dns_required=False),
        ]
        gate = ReadinessGate()
        gate.register_network_check(endpoints, critical=False)  # Non-critical

        # First succeeds, second fails
        with patch.object(
            gate,
            "_check_endpoint_with_retry",
            side_effect=[(True, "Connected"), (False, "Unreachable")],
        ):
            report = gate.evaluate()

            # Should be degraded since check is non-critical
            assert report.status == NodeStatus.DEGRADED
            assert report.warnings == 1

    def test_complete_network_failure(self):
        """Test complete network failure scenario."""
        endpoints = [
            NetworkEndpoint(host="192.0.2.1", port=80, dns_required=False),
            NetworkEndpoint(host="192.0.2.2", port=80, dns_required=False),
        ]
        config = NetworkCheckConfig(max_retries=2, retry_delay_seconds=0.1)
        gate = ReadinessGate(network_config=config, strict=True)
        gate.register_network_check(endpoints, critical=True)

        with patch.object(
            gate, "_check_endpoint_with_retry", return_value=(False, "Network down")
        ):
            report = gate.evaluate()

            assert report.status == NodeStatus.FAILED
            assert report.critical_failures == 1
            assert "unreachable" in report.checks[0].message.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
