"""
Service Manager for E2E Tests

Manages the lifecycle of services required for E2E testing including:
- Starting and stopping services
- Health check verification
- Service dependency management
- Resource cleanup
"""

from __future__ import annotations

import logging
import subprocess
import time

import requests

from e2e.config.e2e_config import E2EConfig, ServiceConfig, get_config

logger = logging.getLogger(__name__)


class ServiceManager:
    """Manages service lifecycle for E2E tests."""

    def __init__(self, config: E2EConfig | None = None):
        """Initialize the service manager.

        Args:
            config: E2E configuration. Uses global config if None.
        """
        self.config = config or get_config()
        self._processes: dict[str, subprocess.Popen] = {}
        self._started_services: list[str] = []

    def start_service(self, service_name: str, wait_for_health: bool = True) -> bool:
        """Start a single service.

        Args:
            service_name: Name of the service to start
            wait_for_health: Whether to wait for health check

        Returns:
            True if service started successfully, False otherwise
        """
        service = self.config.get_service(service_name)
        if not service:
            logger.error("Service %s not found in configuration", service_name)
            return False

        if not service.enabled:
            logger.info("Service %s is disabled, skipping", service_name)
            return True

        logger.info("Starting service: %s", service.name)

        try:
            # Start the service based on its type
            if service_name == "flask_api":
                process = self._start_flask_api(service)
            elif service_name == "fastapi_backend":
                process = self._start_fastapi_backend(service)
            elif service_name == "temporal_server":
                process = self._start_temporal_server(service)
            else:
                logger.warning("Unknown service type: %s", service_name)
                return False

            if process:
                self._processes[service_name] = process
                self._started_services.append(service_name)

                if wait_for_health:
                    return self._wait_for_health(service)

                return True

        except Exception as e:
            logger.error("Failed to start service %s: %s", service_name, e)
            return False

        return True

    def stop_service(self, service_name: str) -> bool:
        """Stop a single service.

        Args:
            service_name: Name of the service to stop

        Returns:
            True if service stopped successfully, False otherwise
        """
        if service_name not in self._processes:
            logger.warning("Service %s is not running", service_name)
            return True

        logger.info("Stopping service: %s", service_name)

        try:
            process = self._processes[service_name]
            process.terminate()
            process.wait(timeout=10)
            del self._processes[service_name]
            self._started_services.remove(service_name)
            return True
        except subprocess.TimeoutExpired:
            logger.warning("Service %s did not terminate, killing", service_name)
            process.kill()
            del self._processes[service_name]
            self._started_services.remove(service_name)
            return True
        except Exception as e:
            logger.error("Failed to stop service %s: %s", service_name, e)
            return False

    def start_all(self, wait_for_health: bool = True) -> bool:
        """Start all enabled services.

        Args:
            wait_for_health: Whether to wait for health checks

        Returns:
            True if all services started successfully, False otherwise
        """
        logger.info("Starting all enabled services")
        enabled_services = self.config.enabled_services()

        for service in enabled_services:
            if not self.start_service(service.name, wait_for_health):
                logger.error("Failed to start service: %s", service.name)
                self.stop_all()
                return False

        logger.info("Successfully started %s services", len(enabled_services))
        return True

    def stop_all(self) -> None:
        """Stop all running services."""
        logger.info("Stopping all services")

        # Stop services in reverse order
        for service_name in reversed(self._started_services.copy()):
            self.stop_service(service_name)

        logger.info("All services stopped")

    def is_healthy(self, service_name: str) -> bool:
        """Check if a service is healthy.

        Args:
            service_name: Name of the service to check

        Returns:
            True if service is healthy, False otherwise
        """
        service = self.config.get_service(service_name)
        if not service:
            return False

        try:
            response = requests.get(
                service.health_url,
                timeout=self.config.api_request_timeout,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _wait_for_health(self, service: ServiceConfig) -> bool:
        """Wait for a service to become healthy.

        Args:
            service: Service configuration

        Returns:
            True if service became healthy, False if timeout
        """
        logger.info("Waiting for %s to become healthy", service.name)
        start_time = time.time()
        max_wait = service.startup_timeout

        while time.time() - start_time < max_wait:
            try:
                response = requests.get(
                    service.health_url,
                    timeout=self.config.api_request_timeout,
                )
                if response.status_code == 200:
                    logger.info("%s is healthy", service.name)
                    return True
            except requests.RequestException:
                pass

            time.sleep(1)

        logger.error("%s did not become healthy within %ss", service.name, max_wait)
        return False

    def _start_flask_api(self, service: ServiceConfig) -> subprocess.Popen | None:
        """Start the Flask API service.

        Args:
            service: Service configuration

        Returns:
            Process handle or None if failed
        """
        try:
            # Start Flask app from web/backend
            process = subprocess.Popen(
                ["python", "-m", "flask", "run", "--host", service.host, "--port", str(service.port)],
                env={**subprocess.os.environ, "FLASK_APP": "web.backend.app"},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logger.info("Started Flask API on %s", service.base_url)
            return process
        except Exception as e:
            logger.error("Failed to start Flask API: %s", e)
            return None

    def _start_fastapi_backend(
        self, service: ServiceConfig
    ) -> subprocess.Popen | None:
        """Start the FastAPI backend service.

        Args:
            service: Service configuration

        Returns:
            Process handle or None if failed
        """
        try:
            # Start FastAPI with uvicorn
            process = subprocess.Popen(
                [
                    "uvicorn",
                    "api.main:app",
                    "--host",
                    service.host,
                    "--port",
                    str(service.port),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logger.info("Started FastAPI backend on %s", service.base_url)
            return process
        except Exception as e:
            logger.error("Failed to start FastAPI backend: %s", e)
            return None

    def _start_temporal_server(
        self, service: ServiceConfig
    ) -> subprocess.Popen | None:
        """Start the Temporal server.

        Args:
            service: Service configuration

        Returns:
            Process handle or None if failed
        """
        logger.info("Temporal server must be started externally")
        # Temporal is typically started via Docker Compose
        return None

    def __enter__(self):
        """Context manager entry."""
        self.start_all()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_all()
