"""
E2E Test Configuration

Central configuration for all E2E tests including service endpoints,
timeouts, test data paths, and environment-specific settings.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
E2E_ROOT = Path(__file__).resolve().parent.parent

# Test data directories
TEST_DATA_DIR = E2E_ROOT / "fixtures" / "data"
TEST_REPORTS_DIR = E2E_ROOT / "reports"
TEST_LOGS_DIR = TEST_REPORTS_DIR / "logs"

# Create directories if they don't exist
for directory in [TEST_DATA_DIR, TEST_REPORTS_DIR, TEST_LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


@dataclass
class ServiceConfig:
    """Configuration for a service in the E2E test environment."""

    name: str
    host: str
    port: int
    startup_timeout: float = 30.0
    health_check_endpoint: str = "/health"
    enabled: bool = True

    @property
    def base_url(self) -> str:
        """Get the base URL for this service."""
        return f"http://{self.host}:{self.port}"

    @property
    def health_url(self) -> str:
        """Get the health check URL for this service."""
        return f"{self.base_url}{self.health_check_endpoint}"


@dataclass
class E2EConfig:
    """Main E2E test configuration."""

    # Environment
    environment: str = os.getenv("E2E_ENV", "test")
    debug_mode: bool = os.getenv("E2E_DEBUG", "false").lower() == "true"

    # Timeouts (seconds)
    default_timeout: float = 30.0
    service_startup_timeout: float = 60.0
    test_execution_timeout: float = 300.0
    api_request_timeout: float = 10.0

    # Service configurations
    services: dict[str, ServiceConfig] = None

    # Test data
    use_real_apis: bool = os.getenv("E2E_USE_REAL_APIS", "false").lower() == "true"
    mock_external_services: bool = not use_real_apis

    # Reporting
    generate_html_report: bool = True
    generate_json_report: bool = True
    save_screenshots: bool = True
    save_logs: bool = True

    # Coverage
    coverage_threshold: float = 0.80  # 80% minimum coverage
    enforce_coverage: bool = True

    def __post_init__(self):
        """Initialize service configurations."""
        if self.services is None:
            self.services = self._default_services()

    def _default_services(self) -> dict[str, ServiceConfig]:
        """Get default service configurations."""
        return {
            "flask_api": ServiceConfig(
                name="Flask API",
                host="localhost",
                port=5000,
                health_check_endpoint="/api/status",
            ),
            "fastapi_backend": ServiceConfig(
                name="FastAPI Backend",
                host="localhost",
                port=8000,
                health_check_endpoint="/health",
                enabled=False,  # Only if FastAPI is available
            ),
            "temporal_server": ServiceConfig(
                name="Temporal Server",
                host="localhost",
                port=7233,
                health_check_endpoint="/",
                enabled=False,  # Only if Temporal is configured
            ),
            "prometheus": ServiceConfig(
                name="Prometheus",
                host="localhost",
                port=9090,
                health_check_endpoint="/-/healthy",
                enabled=False,  # Only if monitoring is configured
            ),
        }

    def get_service(self, name: str) -> ServiceConfig | None:
        """Get a service configuration by name."""
        return self.services.get(name)

    def enabled_services(self) -> list[ServiceConfig]:
        """Get all enabled service configurations."""
        return [svc for svc in self.services.values() if svc.enabled]


# Global configuration instance
config = E2EConfig()


def get_config() -> E2EConfig:
    """Get the global E2E configuration instance."""
    return config


def update_config(**kwargs: Any) -> None:
    """Update the global configuration with new values."""
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
