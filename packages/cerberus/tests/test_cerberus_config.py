"""Tests for cerberus.config (CerberusSettings).

Honest scope: covers construction validation, env-var parsing via
from_env with an explicit mapping, and the process-wide accessor
functions. Does not test os.environ mutation side effects.
"""

import pytest
from cerberus.config import (
    CerberusConfigError,
    CerberusSettings,
    get_settings,
    reset_settings,
    set_settings,
)


class TestCerberusSettingsValidation:
    def test_defaults_are_valid(self) -> None:
        settings = CerberusSettings()
        assert settings.spawn_factor == 3
        assert settings.max_guardians == 27
        assert settings.spawn_cooldown_seconds == 1.0
        assert settings.spawn_rate_per_minute == 60
        assert settings.per_source_rate_limit_per_minute == 30
        assert settings.rate_limit_cleanup_interval_seconds == 300
        assert settings.log_json is True
        assert settings.log_level == "INFO"
        assert settings.enable_audit_logging is True
        assert settings.enable_metrics is True

    def test_spawn_factor_out_of_range_rejected(self) -> None:
        with pytest.raises(CerberusConfigError, match="spawn_factor"):
            CerberusSettings(spawn_factor=0)
        with pytest.raises(CerberusConfigError, match="spawn_factor"):
            CerberusSettings(spawn_factor=11)

    def test_max_guardians_must_cover_spawn_factor(self) -> None:
        with pytest.raises(CerberusConfigError, match="must be >="):
            CerberusSettings(spawn_factor=5, max_guardians=4)

    def test_cooldown_out_of_range_rejected(self) -> None:
        with pytest.raises(CerberusConfigError, match="spawn_cooldown_seconds"):
            CerberusSettings(spawn_cooldown_seconds=-0.1)
        with pytest.raises(CerberusConfigError, match="spawn_cooldown_seconds"):
            CerberusSettings(spawn_cooldown_seconds=61.0)

    def test_log_level_normalized_to_upper(self) -> None:
        settings = CerberusSettings(log_level="debug")
        assert settings.log_level == "DEBUG"

    def test_invalid_log_level_rejected(self) -> None:
        with pytest.raises(CerberusConfigError, match="log_level"):
            CerberusSettings(log_level="VERBOSE")

    def test_settings_are_immutable(self) -> None:
        settings = CerberusSettings()
        with pytest.raises(AttributeError):
            settings.spawn_factor = 9  # type: ignore[misc]


class TestFromEnv:
    def test_empty_env_yields_defaults(self) -> None:
        settings = CerberusSettings.from_env({})
        assert settings == CerberusSettings()

    def test_int_float_bool_and_str_overrides(self) -> None:
        settings = CerberusSettings.from_env(
            {
                "CERBERUS_SPAWN_FACTOR": "5",
                "CERBERUS_SPAWN_COOLDOWN_SECONDS": "0.5",
                "CERBERUS_LOG_JSON": "false",
                "CERBERUS_LOG_LEVEL": "warning",
            }
        )
        assert settings.spawn_factor == 5
        assert settings.spawn_cooldown_seconds == 0.5
        assert settings.log_json is False
        assert settings.log_level == "WARNING"

    def test_unprefixed_keys_ignored(self) -> None:
        settings = CerberusSettings.from_env({"SPAWN_FACTOR": "9"})
        assert settings.spawn_factor == 3

    def test_malformed_int_fails_closed(self) -> None:
        with pytest.raises(CerberusConfigError, match="spawn_factor"):
            CerberusSettings.from_env({"CERBERUS_SPAWN_FACTOR": "many"})

    def test_malformed_bool_fails_closed(self) -> None:
        with pytest.raises(CerberusConfigError, match="log_json"):
            CerberusSettings.from_env({"CERBERUS_LOG_JSON": "maybe"})

    def test_out_of_range_env_value_fails_closed(self) -> None:
        with pytest.raises(CerberusConfigError, match="max_guardians"):
            CerberusSettings.from_env({"CERBERUS_MAX_GUARDIANS": "0"})


class TestProcessWideSettings:
    def test_get_settings_caches_and_reset_clears(self) -> None:
        reset_settings()
        try:
            first = get_settings()
            assert get_settings() is first

            replacement = CerberusSettings(spawn_factor=4)
            set_settings(replacement)
            assert get_settings() is replacement

            reset_settings()
            rebuilt = get_settings()
            assert rebuilt is not replacement
        finally:
            reset_settings()
