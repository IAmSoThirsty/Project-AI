"""
Health Check Utilities for E2E Tests

Provides health check functionality for all services in the E2E test environment.
"""

from __future__ import annotations

import logging
import time
from typing import Callable

import requests

from e2e.config.e2e_config import ServiceConfig, get_config

logger = logging.getLogger(__name__)


class HealthChecker:
    """Performs health checks on services."""

    def __init__(self):
        """Initialize health checker."""
        self.config = get_config()

    def check_service_health(
        self,
        service: ServiceConfig,
        timeout: float | None = None,
    ) -> tuple[bool, str]:
        """Check the health of a single service.

        Args:
            service: Service configuration
            timeout: Request timeout in seconds

        Returns:
            Tuple of (is_healthy, message)
        """
        if not service.enabled:
            return True, "Service is disabled"

        timeout = timeout or self.config.api_request_timeout

        try:
            response = requests.get(service.health_url, timeout=timeout)
            if response.status_code == 200:
                return True, "Service is healthy"
            else:
                return (
                    False,
                    f"Health check failed with status {response.status_code}",
                )
        except requests.RequestException as e:
            return False, f"Health check failed: {e}"

    def check_all_services_health(self) -> dict[str, tuple[bool, str]]:
        """Check the health of all enabled services.

        Returns:
            Dictionary mapping service names to (is_healthy, message) tuples
        """
        results = {}
        enabled_services = self.config.enabled_services()

        for service in enabled_services:
            is_healthy, message = self.check_service_health(service)
            results[service.name] = (is_healthy, message)
            logger.info(f"{service.name}: {message}")

        return results

    def wait_for_all_services_healthy(
        self,
        timeout: float | None = None,
        check_interval: float = 1.0,
    ) -> bool:
        """Wait for all enabled services to become healthy.

        Args:
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks in seconds

        Returns:
            True if all services are healthy, False if timeout
        """
        timeout = timeout or self.config.service_startup_timeout
        start_time = time.time()

        logger.info("Waiting for all services to become healthy")

        while time.time() - start_time < timeout:
            results = self.check_all_services_health()
            all_healthy = all(is_healthy for is_healthy, _ in results.values())

            if all_healthy:
                logger.info("All services are healthy")
                return True

            time.sleep(check_interval)

        logger.error(f"Services did not become healthy within {timeout}s")
        return False

    def retry_until_healthy(
        self,
        service: ServiceConfig,
        max_retries: int = 5,
        retry_delay: float = 2.0,
    ) -> bool:
        """Retry health check until service is healthy or max retries reached.

        Args:
            service: Service configuration
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds

        Returns:
            True if service is healthy, False if max retries reached
        """
        for attempt in range(max_retries):
            is_healthy, message = self.check_service_health(service)
            if is_healthy:
                logger.info(
                    f"{service.name} is healthy after {attempt + 1} attempt(s)"
                )
                return True

            logger.warning(
                f"Attempt {attempt + 1}/{max_retries} failed: {message}"
            )
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

        logger.error(f"{service.name} did not become healthy after {max_retries} attempts")
        return False


def wait_for_condition(
    condition: Callable[[], bool],
    timeout: float = 30.0,
    check_interval: float = 0.5,
    error_message: str = "Condition not met within timeout",
) -> bool:
    """Wait for a condition to become true.

    Args:
        condition: Callable that returns True when condition is met
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        error_message: Error message to log if timeout

    Returns:
        True if condition was met, False if timeout
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        if condition():
            return True
        time.sleep(check_interval)

    logger.error(error_message)
    return False
