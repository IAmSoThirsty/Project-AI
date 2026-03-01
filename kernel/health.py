"""
Thirsty's Kernel - Health Monitoring System

Production-grade health monitoring with:
- Liveness probes
- Readiness probes
- Startup probes
- Dependency health checks
- Self-healing capabilities
- Graceful degradation
- Circuit breakers
- Health aggregation across components

Thirst of Gods Level Architecture
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status values"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ProbeType(Enum):
    """Health probe types"""

    LIVENESS = "liveness"  # Is the component alive?
    READINESS = "readiness"  # Is the component ready to serve traffic?
    STARTUP = "startup"  # Has the component finished starting?


@dataclass
class HealthCheck:
    """Health check definition"""

    name: str
    probe_type: ProbeType
    check_func: Callable[[], bool]  # Returns True if healthy
    interval_seconds: float = 10.0
    timeout_seconds: float = 5.0
    failure_threshold: int = 3  # Consecutive failures before unhealthy
    success_threshold: int = 1  # Consecutive successes to become healthy

    # State
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_check_time: Optional[float] = None
    last_status: HealthStatus = HealthStatus.UNKNOWN
    last_error: Optional[str] = None


@dataclass
class DependencyHealth:
    """Health of a dependency"""

    name: str
    status: HealthStatus
    last_checked: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CircuitBreaker:
    """Circuit breaker for dependency"""

    name: str
    failure_threshold: int = 5
    timeout_seconds: float = 60.0

    # State
    failures: int = 0
    state: str = "closed"  # closed, open, half-open
    opened_at: Optional[float] = None


class HealthMonitor:
    """
    Production-grade health monitoring system

    Features:
    - Multiple probe types (liveness, readiness, startup)
    - Dependency health tracking
    - Self-healing via callbacks
    - Circuit breakers
    - Graceful degradation
    - Aggregated health reporting
    """

    def __init__(self):
        # Health checks
        self.health_checks: Dict[str, HealthCheck] = {}

        # Dependency health
        self.dependencies: Dict[str, DependencyHealth] = {}

        # Circuit breakers
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

        # Component status overrides (for graceful degradation)
        self.status_overrides: Dict[str, HealthStatus] = {}

        # Self-healing callbacks
        self.healing_callbacks: Dict[str, List[Callable]] = {}

        # Thread safety
        self.lock = threading.RLock()

        # Monitoring thread
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None

        # Statistics
        self.stats = {
            "total_checks": 0,
            "failed_checks": 0,
            "healings_triggered": 0,
            "circuit_breaker_trips": 0,
        }

        logger.info("Health monitor initialized")

    def register_health_check(
        self,
        name: str,
        probe_type: ProbeType,
        check_func: Callable[[], bool],
        interval_seconds: float = 10.0,
        failure_threshold: int = 3,
    ):
        """Register a health check"""
        with self.lock:
            check = HealthCheck(
                name=name,
                probe_type=probe_type,
                check_func=check_func,
                interval_seconds=interval_seconds,
                failure_threshold=failure_threshold,
            )

            self.health_checks[name] = check
            logger.debug(f"Registered {probe_type.value} health check: {name}")

    def register_dependency(
        self, name: str, check_func: Callable[[], bool], critical: bool = True
    ):
        """Register dependent service/component"""
        with self.lock:
            # Register as readiness check
            self.register_health_check(
                name=f"dependency_{name}",
                probe_type=ProbeType.READINESS,
                check_func=check_func,
            )

            # Initialize dependency health
            self.dependencies[name] = DependencyHealth(
                name=name,
                status=HealthStatus.UNKNOWN,
                last_checked=time.time(),
                metadata={"critical": critical},
            )

            logger.debug(f"Registered dependency: {name} (critical={critical})")

    def register_circuit_breaker(
        self, name: str, failure_threshold: int = 5, timeout_seconds: float = 60.0
    ):
        """Register circuit breaker for dependency"""
        with self.lock:
            cb = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                timeout_seconds=timeout_seconds,
            )

            self.circuit_breakers[name] = cb
            logger.debug(f"Registered circuit breaker: {name}")

    def check_circuit_breaker(self, name: str) -> bool:
        """
        Check if circuit breaker allows operation

        Returns True if operation allowed, False if circuit open
        """
        with self.lock:
            if name not in self.circuit_breakers:
                return True  # No circuit breaker = allow

            cb = self.circuit_breakers[name]

            if cb.state == "closed":
                return True  # Normal operation

            if cb.state == "open":
                # Check if timeout expired
                if cb.opened_at and (time.time() - cb.opened_at) > cb.timeout_seconds:
                    # Move to half-open
                    cb.state = "half-open"
                    logger.info(f"Circuit breaker {name} moved to half-open")
                    return True
                else:
                    return False  # Still open

            if cb.state == "half-open":
                return True  # Allow one request to test

            return False

    def record_circuit_breaker_result(self, name: str, success: bool):
        """Record result of operation protected by circuit breaker"""
        with self.lock:
            if name not in self.circuit_breakers:
                return

            cb = self.circuit_breakers[name]

            if success:
                cb.failures = 0
                if cb.state == "half-open":
                    cb.state = "closed"
                    logger.info(f"Circuit breaker {name} closed (recovered)")
            else:
                cb.failures += 1

                if cb.failures >= cb.failure_threshold:
                    if cb.state != "open":
                        cb.state = "open"
                        cb.opened_at = time.time()
                        self.stats["circuit_breaker_trips"] += 1
                        logger.warning(
                            f"Circuit breaker {name} opened (threshold exceeded)"
                        )

    def run_check(self, name: str) -> HealthStatus:
        """Run a single health check"""
        with self.lock:
            if name not in self.health_checks:
                return HealthStatus.UNKNOWN

            check = self.health_checks[name]

            try:
                # Run check with timeout (simplified - use threading.Timer in production)
                result = check.check_func()

                if result:
                    check.consecutive_successes += 1
                    check.consecutive_failures = 0

                    if check.consecutive_successes >= check.success_threshold:
                        check.last_status = HealthStatus.HEALTHY
                else:
                    check.consecutive_failures += 1
                    check.consecutive_successes = 0

                    if check.consecutive_failures >= check.failure_threshold:
                        check.last_status = HealthStatus.UNHEALTHY
                        self.stats["failed_checks"] += 1

                        # Trigger self-healing
                        self._trigger_healing(name)

                check.last_check_time = time.time()
                check.last_error = None

            except Exception as e:
                check.consecutive_failures += 1
                check.consecutive_successes = 0
                check.last_status = HealthStatus.UNHEALTHY
                check.last_error = str(e)
                check.last_check_time = time.time()

                self.stats["failed_checks"] += 1
                logger.error(f"Health check {name} failed: {e}")

            self.stats["total_checks"] += 1
            return check.last_status

    def get_health_status(self, probe_type: Optional[ProbeType] = None) -> HealthStatus:
        """
        Get aggregated health status

        Args:
            probe_type: Filter by probe type (None = all probes)

        Returns:
            Aggregated health status
        """
        with self.lock:
            # Check for status overrides (graceful degradation)
            if "system" in self.status_overrides:
                return self.status_overrides["system"]

            checks = self.health_checks.values()

            if probe_type:
                checks = [c for c in checks if c.probe_type == probe_type]

            if not checks:
                return HealthStatus.UNKNOWN

            # Aggregate: UNHEALTHY if any unhealthy, DEGRADED if any degraded, else HEALTHY
            statuses = [c.last_status for c in checks]

            if HealthStatus.UNHEALTHY in statuses:
                return HealthStatus.UNHEALTHY
            if HealthStatus.DEGRADED in statuses:
                return HealthStatus.DEGRADED
            if HealthStatus.UNKNOWN in statuses:
                return HealthStatus.UNKNOWN

            return HealthStatus.HEALTHY

    def get_dependency_health(self, name: str) -> Optional[DependencyHealth]:
        """Get health of specific dependency"""
        with self.lock:
            return self.dependencies.get(name)

    def set_graceful_degradation(self, component: str, status: HealthStatus):
        """
        Set graceful degradation status for component

        Useful for planned maintenance or known issues
        """
        with self.lock:
            self.status_overrides[component] = status
            logger.info(f"Set graceful degradation: {component} -> {status.value}")

    def register_healing_callback(self, check_name: str, callback: Callable[[], None]):
        """
        Register self-healing callback

        Called when health check fails threshold
        """
        with self.lock:
            if check_name not in self.healing_callbacks:
                self.healing_callbacks[check_name] = []

            self.healing_callbacks[check_name].append(callback)
            logger.debug(f"Registered healing callback for {check_name}")

    def _trigger_healing(self, check_name: str):
        """Trigger self-healing callbacks for failed check"""
        if check_name not in self.healing_callbacks:
            return

        logger.warning(f"Triggering self-healing for {check_name}")

        for callback in self.healing_callbacks[check_name]:
            try:
                callback()
                self.stats["healings_triggered"] += 1
            except Exception as e:
                logger.error(f"Healing callback failed for {check_name}: {e}")

    def start_monitoring(self):
        """Start background health monitoring"""
        if self.monitoring_active:
            logger.warning("Health monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitoring_thread.start()

        logger.info("Started health monitoring")

    def stop_monitoring(self):
        """Stop background health monitoring"""
        self.monitoring_active = False

        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)

        logger.info("Stopped health monitoring")

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Run all checks that are due
                now = time.time()

                with self.lock:
                    for name, check in self.health_checks.items():
                        # Check if due
                        if (
                            check.last_check_time is None
                            or (now - check.last_check_time) >= check.interval_seconds
                        ):
                            self.run_check(name)

                # Sleep briefly
                time.sleep(1.0)

            except Exception as e:
                logger.error(f"Health monitoring error: {e}")

    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        with self.lock:
            checks_by_type = {}
            for probe_type in ProbeType:
                checks = [
                    c for c in self.health_checks.values() if c.probe_type == probe_type
                ]
                checks_by_type[probe_type.value] = {
                    "status": self.get_health_status(probe_type).value,
                    "checks": [
                        {
                            "name": c.name,
                            "status": c.last_status.value,
                            "last_check": c.last_check_time,
                            "error": c.last_error,
                        }
                        for c in checks
                    ],
                }

            return {
                "overall_status": self.get_health_status().value,
                "timestamp": time.time(),
                "probes": checks_by_type,
                "dependencies": {
                    name: {
                        "status": dep.status.value,
                        "last_checked": dep.last_checked,
                        "critical": dep.metadata.get("critical", False),
                        "error": dep.error_message,
                    }
                    for name, dep in self.dependencies.items()
                },
                "circuit_breakers": {
                    name: {
                        "state": cb.state,
                        "failures": cb.failures,
                        "opened_at": cb.opened_at,
                    }
                    for name, cb in self.circuit_breakers.items()
                },
                "stats": self.stats,
            }


# Public API
__all__ = [
    "HealthMonitor",
    "HealthStatus",
    "ProbeType",
    "HealthCheck",
    "DependencyHealth",
    "CircuitBreaker",
]
