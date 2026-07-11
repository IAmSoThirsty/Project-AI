"""
cerberus.config — Typed runtime settings for the Cerberus guard surface.

Rebuilt from upstream ``IAmSoThirsty/Cerberus`` ``src/cerberus/config.py``
(pydantic-settings) as a stdlib frozen dataclass so the package adds no new
workspace dependencies. Environment overrides use the same ``CERBERUS_``
prefix and field names as upstream (e.g. ``CERBERUS_SPAWN_FACTOR=5``).

Architectural invariants (AGENTS.md):
- Fail-closed: any invalid value raises CerberusConfigError; there are no
  silent fallbacks to defaults on malformed input.
- Deterministic: settings are immutable after construction.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, fields

ENV_PREFIX = "CERBERUS_"

_VALID_LOG_LEVELS: frozenset[str] = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})

_TRUE_VALUES: frozenset[str] = frozenset({"1", "true", "yes", "on"})
_FALSE_VALUES: frozenset[str] = frozenset({"0", "false", "no", "off"})


class CerberusConfigError(ValueError):
    """Raised when a Cerberus setting is invalid or unparseable."""


def _parse_bool(name: str, raw: str) -> bool:
    lowered = raw.strip().lower()
    if lowered in _TRUE_VALUES:
        return True
    if lowered in _FALSE_VALUES:
        return False
    raise CerberusConfigError(f"{name} must be a boolean (true/false), got {raw!r}")


def _parse_int(name: str, raw: str) -> int:
    try:
        return int(raw.strip())
    except ValueError as exc:
        raise CerberusConfigError(f"{name} must be an integer, got {raw!r}") from exc


def _parse_float(name: str, raw: str) -> float:
    try:
        return float(raw.strip())
    except ValueError as exc:
        raise CerberusConfigError(f"{name} must be a number, got {raw!r}") from exc


def _require_range(name: str, value: float, low: float, high: float) -> None:
    if not low <= value <= high:
        raise CerberusConfigError(f"{name} must be within [{low}, {high}], got {value}")


@dataclass(frozen=True, slots=True)
class CerberusSettings:
    """Cerberus configuration settings (immutable, validated on construction).

    All settings can be overridden via environment variables with the
    ``CERBERUS_`` prefix (e.g. ``CERBERUS_SPAWN_FACTOR=5``) using
    :meth:`from_env`.
    """

    # Guardian spawn settings
    spawn_factor: int = 3
    max_guardians: int = 27
    spawn_cooldown_seconds: float = 1.0
    spawn_rate_per_minute: int = 60

    # Rate limiting settings
    per_source_rate_limit_per_minute: int = 30
    rate_limit_cleanup_interval_seconds: int = 300

    # Logging settings
    log_json: bool = True
    log_level: str = "INFO"

    # Security feature toggles
    enable_audit_logging: bool = True
    enable_metrics: bool = True

    def __post_init__(self) -> None:
        _require_range("spawn_factor", self.spawn_factor, 1, 10)
        _require_range("max_guardians", self.max_guardians, 1, 1000)
        _require_range("spawn_cooldown_seconds", self.spawn_cooldown_seconds, 0.0, 60.0)
        _require_range("spawn_rate_per_minute", self.spawn_rate_per_minute, 1, 1000)
        _require_range(
            "per_source_rate_limit_per_minute", self.per_source_rate_limit_per_minute, 1, 1000
        )
        _require_range(
            "rate_limit_cleanup_interval_seconds",
            self.rate_limit_cleanup_interval_seconds,
            60,
            3600,
        )
        if self.max_guardians < self.spawn_factor:
            raise CerberusConfigError(
                f"max_guardians ({self.max_guardians}) must be >= "
                f"spawn_factor ({self.spawn_factor})"
            )
        normalized_level = self.log_level.upper()
        if normalized_level not in _VALID_LOG_LEVELS:
            raise CerberusConfigError(
                f"log_level must be one of {sorted(_VALID_LOG_LEVELS)}, got {self.log_level!r}"
            )
        object.__setattr__(self, "log_level", normalized_level)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> CerberusSettings:
        """Build settings from ``CERBERUS_``-prefixed environment variables.

        Unset variables keep their defaults. Malformed or out-of-range values
        raise CerberusConfigError (fail-closed) rather than falling back.
        """
        source: Mapping[str, str] = os.environ if env is None else env
        overrides: dict[str, int | float | bool | str] = {}
        for field in fields(cls):
            raw = source.get(f"{ENV_PREFIX}{field.name.upper()}")
            if raw is None:
                continue
            if field.type in ("int", int):
                overrides[field.name] = _parse_int(field.name, raw)
            elif field.type in ("float", float):
                overrides[field.name] = _parse_float(field.name, raw)
            elif field.type in ("bool", bool):
                overrides[field.name] = _parse_bool(field.name, raw)
            else:
                overrides[field.name] = raw
        return cls(**overrides)  # type: ignore[arg-type]


_settings: CerberusSettings | None = None


def get_settings() -> CerberusSettings:
    """Return the process-wide settings, building from the environment once."""
    global _settings
    if _settings is None:
        _settings = CerberusSettings.from_env()
    return _settings


def set_settings(settings: CerberusSettings) -> None:
    """Replace the process-wide settings (primarily for tests)."""
    global _settings
    _settings = settings


def reset_settings() -> None:
    """Clear the cached settings so the next get_settings() re-reads the env."""
    global _settings
    _settings = None


__all__ = [
    "ENV_PREFIX",
    "CerberusConfigError",
    "CerberusSettings",
    "get_settings",
    "reset_settings",
    "set_settings",
]
