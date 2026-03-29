# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_config.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_config.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""Tests for configuration management."""

import pytest
from pydantic import ValidationError

from cerberus.config import CerberusSettings


class TestConfiguration:
    """Tests for CerberusSettings configuration."""

    def test_default_values(self) -> None:
        """Configuration should have sensible defaults."""
        settings = CerberusSettings()

        assert settings.spawn_factor == 3
        assert settings.max_guardians == 27
        assert settings.spawn_cooldown_seconds == 1.0
        assert settings.spawn_rate_per_minute == 60
        assert settings.per_source_rate_limit_per_minute == 30
        assert settings.log_json is True
        assert settings.log_level == "INFO"
        assert settings.enable_audit_logging is True
        assert settings.enable_metrics is True

    def test_spawn_factor_validation(self) -> None:
        """Spawn factor should be validated to reasonable range."""
        # Valid values
        settings = CerberusSettings(spawn_factor=1)
        assert settings.spawn_factor == 1

        settings = CerberusSettings(spawn_factor=10)
        assert settings.spawn_factor == 10

        # Invalid values
        with pytest.raises(ValidationError):
            CerberusSettings(spawn_factor=0)  # Too low

        with pytest.raises(ValidationError):
            CerberusSettings(spawn_factor=11)  # Too high

    def test_max_guardians_validation(self) -> None:
        """Max guardians should be validated to reasonable range."""
        # Valid values (must also set spawn_factor to satisfy constraint)
        settings = CerberusSettings(spawn_factor=1, max_guardians=1)
        assert settings.max_guardians == 1

        settings = CerberusSettings(spawn_factor=1, max_guardians=1000)
        assert settings.max_guardians == 1000

        # Invalid values
        with pytest.raises(ValidationError):
            CerberusSettings(spawn_factor=1, max_guardians=0)  # Too low

        with pytest.raises(ValidationError):
            CerberusSettings(spawn_factor=1, max_guardians=1001)  # Too high

    def test_max_guardians_at_least_spawn_factor(self) -> None:
        """Max guardians must be at least spawn_factor."""
        # Valid: max >= spawn_factor
        settings = CerberusSettings(spawn_factor=3, max_guardians=3)
        assert settings.max_guardians == 3

        settings = CerberusSettings(spawn_factor=5, max_guardians=10)
        assert settings.max_guardians == 10

        # Invalid: max < spawn_factor
        with pytest.raises(ValidationError, match="max_guardians.*spawn_factor"):
            CerberusSettings(spawn_factor=5, max_guardians=4)

    def test_spawn_cooldown_validation(self) -> None:
        """Spawn cooldown should be validated."""
        # Valid values
        settings = CerberusSettings(spawn_cooldown_seconds=0.0)
        assert settings.spawn_cooldown_seconds == 0.0

        settings = CerberusSettings(spawn_cooldown_seconds=60.0)
        assert settings.spawn_cooldown_seconds == 60.0

        # Invalid values
        with pytest.raises(ValidationError):
            CerberusSettings(spawn_cooldown_seconds=-1.0)  # Negative

        with pytest.raises(ValidationError):
            CerberusSettings(spawn_cooldown_seconds=61.0)  # Too high

    def test_log_level_validation(self) -> None:
        """Log level should be validated to standard levels."""
        # Valid levels (case insensitive)
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = CerberusSettings(log_level=level)
            assert settings.log_level == level

            settings = CerberusSettings(log_level=level.lower())
            assert settings.log_level == level  # Should be uppercased

        # Invalid level
        with pytest.raises(ValidationError, match="log_level must be one of"):
            CerberusSettings(log_level="INVALID")

    def test_environment_variable_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Settings should be overridable via environment variables."""
        # Set environment variables
        monkeypatch.setenv("CERBERUS_SPAWN_FACTOR", "5")
        monkeypatch.setenv("CERBERUS_MAX_GUARDIANS", "50")
        monkeypatch.setenv("CERBERUS_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("CERBERUS_LOG_JSON", "false")

        # Create new settings instance (reads from env)
        settings = CerberusSettings()

        assert settings.spawn_factor == 5
        assert settings.max_guardians == 50
        assert settings.log_level == "DEBUG"
        assert settings.log_json is False

    def test_env_prefix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Environment variables should use CERBERUS_ prefix."""
        # Without prefix, should use defaults
        monkeypatch.setenv("SPAWN_FACTOR", "10")
        settings = CerberusSettings()
        assert settings.spawn_factor == 3  # Default, not 10

        # With prefix, should override
        monkeypatch.setenv("CERBERUS_SPAWN_FACTOR", "10")
        settings = CerberusSettings()
        assert settings.spawn_factor == 10

    def test_rate_limiting_settings(self) -> None:
        """Rate limiting settings should be configurable."""
        settings = CerberusSettings(
            spawn_rate_per_minute=120,
            per_source_rate_limit_per_minute=60,
            rate_limit_cleanup_interval_seconds=600,
        )

        assert settings.spawn_rate_per_minute == 120
        assert settings.per_source_rate_limit_per_minute == 60
        assert settings.rate_limit_cleanup_interval_seconds == 600

    def test_security_toggles(self) -> None:
        """Security feature toggles should be configurable."""
        settings = CerberusSettings(
            enable_audit_logging=False,
            enable_metrics=False,
        )

        assert settings.enable_audit_logging is False
        assert settings.enable_metrics is False
