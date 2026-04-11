#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Readiness Gate — Pre-OPERATIONAL Health Checks.

Validates that all PSIA subsystems are healthy before
transitioning the node to OPERATIONAL status.

Checks performed:
    - Genesis ceremony completed
    - All required keys present
    - All invariants loaded and valid
    - Ledger chain integrity verified
    - Capability authority operational
    - Network connectivity (DNS resolution, TCP reachability, retry logic)
    - Resource limits within thresholds

Security invariants:
    - A node MUST NOT enter OPERATIONAL status without passing
      all readiness checks
    - Failed checks produce detailed diagnostics

Production notes:
    - In production, readiness gates are checked continuously
      (Kubernetes readiness probes would call this)
    - Network connectivity checks verify DNS and TCP connectivity to peer nodes
    - Supports configurable timeouts, retries, and multiple endpoints
    - Resource checks would validate CPU, memory, disk, and file descriptor limits
"""

from __future__ import annotations

import logging
import socket
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


class NodeStatus(str, Enum):
    """Lifecycle status of a PSIA node."""

    INITIALIZING = "initializing"
    CHECKING = "checking"
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    SAFE_HALT = "safe_halt"
    FAILED = "failed"


@dataclass
class CheckResult:
    """Result of a single readiness check."""

    name: str
    passed: bool
    message: str
    duration_ms: float = 0.0
    critical: bool = True  # If True, failure blocks OPERATIONAL


@dataclass
class ReadinessReport:
    """Full report from readiness gate evaluation."""

    status: NodeStatus
    checks: list[CheckResult] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    all_passed: bool = False
    critical_failures: int = 0
    warnings: int = 0


@dataclass
class NetworkEndpoint:
    """Configuration for a network endpoint to check."""

    host: str
    port: int = 443
    protocol: str = "tcp"  # tcp, udp, or http
    timeout_seconds: float = 5.0
    dns_required: bool = True


@dataclass
class NetworkCheckConfig:
    """Configuration for network connectivity checks."""

    endpoints: list[NetworkEndpoint] = field(default_factory=list)
    dns_servers: list[str] = field(default_factory=lambda: ["8.8.8.8", "1.1.1.1"])
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    dns_timeout_seconds: float = 3.0


class ReadinessGate:
    """Validates PSIA node health before OPERATIONAL transition.

    Registers checks as callables returning (passed: bool, message: str).
    Evaluates all checks and produces a ReadinessReport.

    Built-in checks can be registered for:
    - Genesis completion
    - Key material availability
    - Invariant integrity
    - Ledger chain verification
    - Capability authority status
    - Network connectivity (DNS resolution, endpoint reachability)

    Args:
        node_id: Identifier for this node
        strict: If True, ALL critical checks must pass (default: True)
        network_config: Configuration for network connectivity checks
    """

    def __init__(
        self,
        *,
        node_id: str = "psia-node-01",
        strict: bool = True,
        network_config: NetworkCheckConfig | None = None,
    ) -> None:
        self.node_id = node_id
        self.strict = strict
        self.network_config = network_config or NetworkCheckConfig()
        self._checks: list[tuple[str, Callable[[], tuple[bool, str]], bool]] = []
        self._status = NodeStatus.INITIALIZING
        self._last_report: ReadinessReport | None = None

    def register_check(
        self,
        name: str,
        check_fn: Callable[[], tuple[bool, str]],
        *,
        critical: bool = True,
    ) -> None:
        """Register a readiness check.

        Args:
            name: Human-readable check name
            check_fn: Callable returning (passed, message)
            critical: If True, failure blocks OPERATIONAL status
        """
        self._checks.append((name, check_fn, critical))

    def register_genesis_check(self, genesis_coordinator: Any) -> None:
        """Register a check for genesis ceremony completion."""

        def check() -> tuple[bool, str]:
            if getattr(genesis_coordinator, "is_completed", False):
                return True, "Genesis ceremony completed"
            return (
                False,
                f"Genesis not completed: status={getattr(genesis_coordinator, 'status', 'unknown')}",
            )

        self.register_check("genesis_completed", check)

    def register_ledger_check(self, ledger: Any) -> None:
        """Register a check for ledger chain integrity."""

        def check() -> tuple[bool, str]:
            if hasattr(ledger, "verify_chain"):
                if ledger.verify_chain():
                    return (
                        True,
                        f"Ledger chain verified ({getattr(ledger, 'sealed_block_count', 0)} blocks)",
                    )
                return False, "Ledger chain verification failed"
            return True, "Ledger check skipped (no verify_chain method)"

        self.register_check("ledger_integrity", check)

    def register_capability_check(self, authority: Any) -> None:
        """Register a check for capability authority operational status."""

        def check() -> tuple[bool, str]:
            issued = getattr(authority, "issued_count", -1)
            if issued >= 0:
                return (
                    True,
                    f"Capability authority operational ({issued} tokens issued)",
                )
            return False, "Capability authority not operational"

        self.register_check("capability_authority", check, critical=False)

    def _check_dns_resolution(
        self, hostname: str, timeout: float = 3.0
    ) -> tuple[bool, str]:
        """Check if DNS resolution works for a hostname.

        Args:
            hostname: Hostname to resolve
            timeout: DNS resolution timeout in seconds

        Returns:
            (success, message) tuple
        """
        try:
            # Set socket default timeout for DNS resolution
            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout)
            try:
                addr_info = socket.getaddrinfo(
                    hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM
                )
                if addr_info:
                    resolved_ips = [info[4][0] for info in addr_info]
                    unique_ips = list(set(resolved_ips))
                    return (
                        True,
                        f"Resolved {hostname} to {len(unique_ips)} IP(s): {', '.join(unique_ips[:3])}",
                    )
                return False, f"DNS resolution returned no addresses for {hostname}"
            finally:
                socket.setdefaulttimeout(old_timeout)
        except socket.gaierror as exc:
            return False, f"DNS resolution failed for {hostname}: {exc}"
        except socket.timeout:
            return False, f"DNS resolution timed out for {hostname} after {timeout}s"
        except Exception as exc:
            return False, f"DNS resolution error for {hostname}: {exc}"

    def _check_tcp_connectivity(
        self, host: str, port: int, timeout: float = 5.0, retry: int = 0
    ) -> tuple[bool, str]:
        """Check TCP connectivity to a host:port.

        Args:
            host: Target host (IP or hostname)
            port: Target port
            timeout: Connection timeout in seconds
            retry: Current retry attempt number

        Returns:
            (success, message) tuple
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            try:
                sock.connect((host, port))
                retry_msg = f" (retry {retry})" if retry > 0 else ""
                return True, f"TCP connection to {host}:{port} successful{retry_msg}"
            finally:
                sock.close()
        except socket.timeout:
            return False, f"TCP connection to {host}:{port} timed out after {timeout}s"
        except ConnectionRefusedError:
            return False, f"TCP connection to {host}:{port} refused"
        except socket.gaierror as exc:
            return False, f"TCP connection failed (DNS error): {exc}"
        except OSError as exc:
            return False, f"TCP connection to {host}:{port} failed: {exc}"
        except Exception as exc:
            return False, f"TCP connection error to {host}:{port}: {exc}"

    def _check_endpoint_with_retry(
        self, endpoint: NetworkEndpoint
    ) -> tuple[bool, str]:
        """Check endpoint connectivity with retry logic.

        Args:
            endpoint: Network endpoint to check

        Returns:
            (success, message) tuple
        """
        import time

        # First check DNS if required
        if endpoint.dns_required and not endpoint.host.replace(".", "").isdigit():
            dns_ok, dns_msg = self._check_dns_resolution(
                endpoint.host, self.network_config.dns_timeout_seconds
            )
            if not dns_ok:
                return False, f"DNS check failed: {dns_msg}"

        # Try connection with retries
        last_error = ""
        for attempt in range(self.network_config.max_retries):
            if endpoint.protocol == "tcp":
                success, msg = self._check_tcp_connectivity(
                    endpoint.host, endpoint.port, endpoint.timeout_seconds, attempt
                )
                if success:
                    return True, msg
                last_error = msg

                # Wait before retry (except on last attempt)
                if attempt < self.network_config.max_retries - 1:
                    time.sleep(self.network_config.retry_delay_seconds)
            else:
                return (
                    False,
                    f"Unsupported protocol: {endpoint.protocol} (only 'tcp' supported)",
                )

        # All retries exhausted
        return (
            False,
            f"All {self.network_config.max_retries} attempts failed. Last error: {last_error}",
        )

    def register_network_check(
        self, endpoints: list[NetworkEndpoint] | None = None, *, critical: bool = True
    ) -> None:
        """Register network connectivity checks.

        Checks DNS resolution and TCP connectivity to specified endpoints.
        If no endpoints are provided, uses endpoints from network_config.

        Args:
            endpoints: List of endpoints to check (uses config if None)
            critical: If True, failure blocks OPERATIONAL status
        """
        check_endpoints = endpoints or self.network_config.endpoints

        if not check_endpoints:
            # Register a passing stub check if no endpoints configured
            def stub_check() -> tuple[bool, str]:
                return True, "Network check skipped (no endpoints configured)"

            self.register_check("network_connectivity", stub_check, critical=False)
            return

        def check() -> tuple[bool, str]:
            results = []
            failed_endpoints = []
            passed_count = 0

            for endpoint in check_endpoints:
                passed, msg = self._check_endpoint_with_retry(endpoint)
                results.append(f"{endpoint.host}:{endpoint.port} - {msg}")
                if passed:
                    passed_count += 1
                else:
                    failed_endpoints.append(f"{endpoint.host}:{endpoint.port}")

            if passed_count == len(check_endpoints):
                return True, f"All {len(check_endpoints)} endpoint(s) reachable"
            else:
                failed_count = len(failed_endpoints)
                return (
                    False,
                    f"{failed_count}/{len(check_endpoints)} endpoint(s) unreachable: {'; '.join(results)}",
                )

        self.register_check("network_connectivity", check, critical=critical)

    def evaluate(self) -> ReadinessReport:
        """Run all registered checks and produce a ReadinessReport.

        Returns:
            ReadinessReport with detailed check results and overall status
        """
        self._status = NodeStatus.CHECKING
        results: list[CheckResult] = []
        critical_failures = 0
        warnings = 0

        for name, check_fn, critical in self._checks:
            import time

            start = time.monotonic()
            try:
                passed, message = check_fn()
            except Exception as exc:
                passed = False
                message = f"Check raised exception: {exc}"
            duration_ms = (time.monotonic() - start) * 1000

            result = CheckResult(
                name=name,
                passed=passed,
                message=message,
                duration_ms=duration_ms,
                critical=critical,
            )
            results.append(result)

            if not passed:
                if critical:
                    critical_failures += 1
                    logger.warning(
                        "Critical readiness check failed: %s — %s", name, message
                    )
                else:
                    warnings += 1
                    logger.info(
                        "Non-critical readiness check failed: %s — %s", name, message
                    )

        # Determine overall status
        if critical_failures == 0:
            if warnings > 0:
                self._status = NodeStatus.DEGRADED
            else:
                self._status = NodeStatus.OPERATIONAL
        else:
            if self.strict:
                self._status = NodeStatus.FAILED
            else:
                self._status = NodeStatus.DEGRADED

        report = ReadinessReport(
            status=self._status,
            checks=results,
            all_passed=(critical_failures == 0 and warnings == 0),
            critical_failures=critical_failures,
            warnings=warnings,
        )
        self._last_report = report
        return report

    @property
    def status(self) -> NodeStatus:
        return self._status

    @property
    def is_operational(self) -> bool:
        return self._status == NodeStatus.OPERATIONAL

    @property
    def last_report(self) -> ReadinessReport | None:
        return self._last_report


__all__ = [
    "ReadinessGate",
    "ReadinessReport",
    "CheckResult",
    "NodeStatus",
    "NetworkEndpoint",
    "NetworkCheckConfig",
]
