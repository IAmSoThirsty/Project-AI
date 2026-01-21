"""
Temporal.io Configuration File for Project-AI.

Contains settings for Temporal server connection, worker configuration,
and workflow/activity parameters.
"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class TemporalConfig(BaseSettings):
    """Temporal.io configuration settings."""

    # Server Connection
    host: str = Field(
        default="localhost:7233",
        description="Temporal server address",
    )
    namespace: str = Field(
        default="default",
        description="Temporal namespace",
    )
    task_queue: str = Field(
        default="project-ai-tasks",
        description="Task queue name for workers",
    )

    # Cloud Configuration
    cloud_namespace: str | None = Field(
        default=None,
        description="Temporal Cloud namespace (e.g., my-namespace.a2b3c)",
    )
    cloud_cert_path: Path | None = Field(
        default=None,
        description="Path to client certificate for Temporal Cloud",
    )
    cloud_key_path: Path | None = Field(
        default=None,
        description="Path to client private key for Temporal Cloud",
    )
    cloud_api_key: str | None = Field(
        default=None,
        description="API key for Temporal Cloud",
    )

    # Worker Configuration
    max_concurrent_activities: int = Field(
        default=50,
        description="Maximum number of concurrent activity executions",
    )
    max_concurrent_workflows: int = Field(
        default=50,
        description="Maximum number of concurrent workflow tasks",
    )
    worker_identity: str = Field(
        default="project-ai-worker",
        description="Worker identity for logging and monitoring",
    )

    # Timeout Configuration (in seconds)
    workflow_execution_timeout: int = Field(
        default=3600,
        description="Maximum time for entire workflow execution",
    )
    workflow_run_timeout: int = Field(
        default=1800,
        description="Maximum time for a single workflow run",
    )
    activity_start_to_close_timeout: int = Field(
        default=300,
        description="Maximum time for activity execution",
    )

    # Retry Policy
    max_retry_attempts: int = Field(
        default=3,
        description="Maximum number of retry attempts",
    )
    initial_retry_interval: int = Field(
        default=1,
        description="Initial retry interval in seconds",
    )
    max_retry_interval: int = Field(
        default=30,
        description="Maximum retry interval in seconds",
    )

    class Config:
        """Pydantic config."""

        env_prefix = "TEMPORAL_"
        env_file = ".env.temporal"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def is_cloud(self) -> bool:
        """Check if using Temporal Cloud."""
        return bool(self.cloud_namespace)

    def get_connection_string(self) -> str:
        """Get connection string for logging."""
        if self.is_cloud:
            return f"Temporal Cloud: {self.cloud_namespace}"
        return f"Temporal Server: {self.host}"


# Global configuration instance
_config: TemporalConfig | None = None


def get_temporal_config() -> TemporalConfig:
    """
    Get the Temporal configuration instance.

    Returns:
        TemporalConfig instance
    """
    global _config
    if _config is None:
        _config = TemporalConfig()
    return _config


def reload_temporal_config():
    """Reload the Temporal configuration from environment."""
    global _config
    _config = TemporalConfig()
    return _config
