#!/usr/bin/env python3
"""
Per-Service Retry Tracker with Granular Control
Enhanced global retry system with service-specific limits and monitoring

Production-ready retry management with detailed observability.
"""

import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class ServiceRetryConfig:
    """Configuration for per-service retry limits."""

    max_retries: int = 3
    max_per_minute: int = 100
    timeout_seconds: int = 30
    backoff_multiplier: float = 2.0
    circuit_breaker_threshold: int = 5


class PerServiceRetryTracker:
    """
    Granular retry tracker with per-service limits and monitoring.

    Features:
    - Per-service retry tracking
    - Global retry limit
    - Automatic reset every minute
    - Thread-safe operations
    - Detailed statistics
    - Circuit breaker integration
    """

    def __init__(self, global_limit: int = 50):
        """
        Initialize per-service retry tracker.

        Args:
            global_limit: Maximum total retries per minute across all services
        """
        self.global_limit = global_limit

        # Service-specific counters
        self.service_counters: Dict[str, int] = defaultdict(int)
        self.global_counter = 0

        # Service configurations
        self.service_configs: Dict[str, ServiceRetryConfig] = {}

        # Circuit breaker states
        self.circuit_breaker_failures: Dict[str, int] = defaultdict(int)
        self.circuit_breaker_states: Dict[str, str] = defaultdict(lambda: "CLOSED")

        # Thread safety
        self.lock = threading.Lock()

        # Statistics
        self.stats = {
            "reset_count": 0,
            "last_reset": datetime.now(),
            "total_retries": 0,
            "throttled_count": 0,
        }

        # Start reset thread
        self._start_reset_thread()

    def register_service(self, service_name: str, config: ServiceRetryConfig):
        """
        Register a service with specific retry configuration.

        Args:
            service_name: Name of the service
            config: Retry configuration for the service
        """
        with self.lock:
            self.service_configs[service_name] = config
            logger.info(f"Registered service '{service_name}' with config: {config}")

    def can_retry(self, service_name: str) -> tuple[bool, str]:
        """
        Check if a service can retry based on limits.

        Args:
            service_name: Name of the service

        Returns:
            Tuple of (can_retry, reason)
        """
        with self.lock:
            # Check circuit breaker
            if self.circuit_breaker_states[service_name] == "OPEN":
                return False, f"Circuit breaker OPEN for service '{service_name}'"

            # Check global limit
            if self.global_counter >= self.global_limit:
                self.stats["throttled_count"] += 1
                return (
                    False,
                    f"Global retry limit exceeded ({self.global_counter}/{self.global_limit})",
                )

            # Check service-specific limit
            if service_name in self.service_configs:
                config = self.service_configs[service_name]
                service_count = self.service_counters[service_name]

                if service_count >= config.max_per_minute:
                    self.stats["throttled_count"] += 1
                    return (
                        False,
                        f"Service '{service_name}' retry limit exceeded ({service_count}/{config.max_per_minute})",
                    )

            return True, "OK"

    def record_retry(self, service_name: str) -> bool:
        """
        Record a retry attempt for a service.

        Args:
            service_name: Name of the service

        Returns:
            True if retry was recorded, False if limit exceeded
        """
        can_retry, reason = self.can_retry(service_name)

        if not can_retry:
            logger.warning(f"Retry blocked: {reason}")
            return False

        with self.lock:
            self.service_counters[service_name] += 1
            self.global_counter += 1
            self.stats["total_retries"] += 1

            logger.debug(
                f"Retry recorded for '{service_name}': "
                f"service={self.service_counters[service_name]}, "
                f"global={self.global_counter}"
            )

            return True

    def record_failure(self, service_name: str):
        """
        Record a failure for circuit breaker tracking.

        Args:
            service_name: Name of the service
        """
        with self.lock:
            self.circuit_breaker_failures[service_name] += 1

            # Check if circuit breaker should open
            if service_name in self.service_configs:
                config = self.service_configs[service_name]
                failures = self.circuit_breaker_failures[service_name]

                if failures >= config.circuit_breaker_threshold:
                    self.circuit_breaker_states[service_name] = "OPEN"
                    logger.warning(
                        f"Circuit breaker OPEN for '{service_name}' "
                        f"after {failures} failures"
                    )

    def record_success(self, service_name: str):
        """
        Record a success for circuit breaker recovery.

        Args:
            service_name: Name of the service
        """
        with self.lock:
            # Reset failure count
            self.circuit_breaker_failures[service_name] = 0

            # Close circuit breaker if it was open
            if self.circuit_breaker_states[service_name] == "OPEN":
                self.circuit_breaker_states[service_name] = "CLOSED"
                logger.info(f"Circuit breaker CLOSED for '{service_name}' (success)")

    def get_service_stats(self, service_name: str) -> Dict:
        """
        Get statistics for a specific service.

        Args:
            service_name: Name of the service

        Returns:
            Dictionary with service statistics
        """
        with self.lock:
            config = self.service_configs.get(service_name)

            return {
                "service_name": service_name,
                "current_retries": self.service_counters[service_name],
                "max_per_minute": config.max_per_minute if config else None,
                "utilization_pct": (
                    (self.service_counters[service_name] / config.max_per_minute * 100)
                    if config and config.max_per_minute > 0
                    else 0
                ),
                "circuit_breaker_state": self.circuit_breaker_states[service_name],
                "circuit_breaker_failures": self.circuit_breaker_failures[service_name],
                "config": config.__dict__ if config else None,
            }

    def get_global_stats(self) -> Dict:
        """
        Get global retry statistics.

        Returns:
            Dictionary with global statistics
        """
        with self.lock:
            return {
                "global_retries_current_minute": self.global_counter,
                "global_limit": self.global_limit,
                "utilization_pct": (self.global_counter / self.global_limit * 100),
                "registered_services": len(self.service_configs),
                "active_services": len(
                    [s for s, c in self.service_counters.items() if c > 0]
                ),
                "open_circuit_breakers": len(
                    [
                        s
                        for s, state in self.circuit_breaker_states.items()
                        if state == "OPEN"
                    ]
                ),
                "total_retries_lifetime": self.stats["total_retries"],
                "throttled_count_lifetime": self.stats["throttled_count"],
                "reset_count": self.stats["reset_count"],
                "last_reset": self.stats["last_reset"].isoformat(),
                "service_breakdown": {
                    name: count
                    for name, count in self.service_counters.items()
                    if count > 0
                },
            }

    def reset_counters(self):
        """Reset all retry counters (called every minute)."""
        with self.lock:
            self.service_counters.clear()
            self.global_counter = 0
            self.stats["reset_count"] += 1
            self.stats["last_reset"] = datetime.now()

            logger.debug(f"Retry counters reset (count: {self.stats['reset_count']})")

    def _start_reset_thread(self):
        """Start background thread to reset counters every minute."""

        def reset_loop():
            while True:
                time.sleep(60)
                self.reset_counters()

        thread = threading.Thread(
            target=reset_loop, daemon=True, name="retry_tracker_reset"
        )
        thread.start()
        logger.info("Retry tracker reset thread started")


# Global instance
_global_retry_tracker: Optional[PerServiceRetryTracker] = None


def get_retry_tracker() -> PerServiceRetryTracker:
    """Get the global per-service retry tracker instance."""
    global _global_retry_tracker

    if _global_retry_tracker is None:
        _global_retry_tracker = PerServiceRetryTracker()

        # Register default services
        _global_retry_tracker.register_service(
            "vault_access",
            ServiceRetryConfig(
                max_retries=3,
                max_per_minute=20,
                timeout_seconds=10,
                backoff_multiplier=2.0,
                circuit_breaker_threshold=5,
            ),
        )

        _global_retry_tracker.register_service(
            "pii_redaction",
            ServiceRetryConfig(
                max_retries=2,
                max_per_minute=100,
                timeout_seconds=5,
                backoff_multiplier=1.5,
                circuit_breaker_threshold=10,
            ),
        )

        _global_retry_tracker.register_service(
            "signal_processing",
            ServiceRetryConfig(
                max_retries=5,
                max_per_minute=200,
                timeout_seconds=30,
                backoff_multiplier=2.0,
                circuit_breaker_threshold=20,
            ),
        )

        _global_retry_tracker.register_service(
            "transcription",
            ServiceRetryConfig(
                max_retries=3,
                max_per_minute=10,
                timeout_seconds=60,
                backoff_multiplier=2.5,
                circuit_breaker_threshold=5,
            ),
        )

        _global_retry_tracker.register_service(
            "audit_logging",
            ServiceRetryConfig(
                max_retries=10,
                max_per_minute=500,
                timeout_seconds=60,
                backoff_multiplier=1.5,
                circuit_breaker_threshold=50,
            ),
        )

    return _global_retry_tracker


if __name__ == "__main__":
    # Test per-service retry tracker
    import json

    tracker = get_retry_tracker()

    # Test retries for different services
    print("Testing vault_access service:")
    for i in range(25):
        can_retry, reason = tracker.can_retry("vault_access")
        if can_retry:
            tracker.record_retry("vault_access")
        else:
            print(f"  Blocked at retry {i}: {reason}")
            break

    print("\nTesting signal_processing service:")
    for i in range(205):
        can_retry, reason = tracker.can_retry("signal_processing")
        if can_retry:
            tracker.record_retry("signal_processing")
        else:
            print(f"  Blocked at retry {i}: {reason}")
            break

    # Get statistics
    print("\nGlobal statistics:")
    print(json.dumps(tracker.get_global_stats(), indent=2))

    print("\nVault access statistics:")
    print(json.dumps(tracker.get_service_stats("vault_access"), indent=2))

    print("\nSignal processing statistics:")
    print(json.dumps(tracker.get_service_stats("signal_processing"), indent=2))
