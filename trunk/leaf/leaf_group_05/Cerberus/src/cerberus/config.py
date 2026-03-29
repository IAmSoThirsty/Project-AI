# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / config.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / config.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Configuration management for Cerberus.

Provides centralized configuration using Pydantic BaseSettings with
environment variable overrides and validation.
"""

from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CerberusSettings(BaseSettings):
    """
    Cerberus configuration settings.

    All settings can be overridden via environment variables with the
    CERBERUS_ prefix (e.g., CERBERUS_SPAWN_FACTOR=5).
    """

    model_config = SettingsConfigDict(
        env_prefix="CERBERUS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Guardian spawn settings
    spawn_factor: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of guardians to spawn per bypass attempt",
    )
    max_guardians: int = Field(
        default=27,
        ge=1,
        le=1000,
        description="Maximum number of guardians before triggering shutdown",
    )
    spawn_cooldown_seconds: float = Field(
        default=1.0,
        ge=0.0,
        le=60.0,
        description="Minimum seconds between spawn events",
    )
    spawn_rate_per_minute: int = Field(
        default=60,
        ge=1,
        le=1000,
        description="Maximum spawn events per minute (token bucket rate)",
    )

    # Rate limiting settings
    per_source_rate_limit_per_minute: int = Field(
        default=30,
        ge=1,
        le=1000,
        description="Maximum bypass attempts per source per minute",
    )
    rate_limit_cleanup_interval_seconds: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Interval for cleaning up expired rate limit entries",
    )

    # Logging settings
    log_json: bool = Field(
        default=True,
        description="Enable structured JSON logging",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Security settings
    enable_audit_logging: bool = Field(
        default=True,
        description="Enable audit logging for security events",
    )
    enable_metrics: bool = Field(
        default=True,
        description="Enable metrics collection for monitoring",
    )

    @field_validator("max_guardians")
    @classmethod
    def max_at_least_spawn(cls, v: int, info: Any) -> int:
        """Ensure max_guardians is at least spawn_factor."""
        spawn_factor = info.data.get("spawn_factor", 3)
        if v < spawn_factor:
            raise ValueError(
                f"max_guardians ({v}) must be >= spawn_factor ({spawn_factor})"
            )
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is a valid logging level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"log_level must be one of {valid_levels}, got {v}"
            )
        return v_upper


# Global settings instance
settings = CerberusSettings()
