"""
tarl.config — TARL runtime configuration.

Loads runtime settings from a dict (or JSON-compatible mapping). Settings
control cache behavior, audit log retention, and executor mode.

This is a minimum port of legacy `tarl/config/__init__.py` (351 LOC).
Captures the typed configuration surface; defers advanced config patterns
(per-environment overrides, secret resolution) to a later wave.

Architectural invariants (AGENTS.md v3):
- Downward-only deps: tarl.config imports only stdlib.
- Fail-closed: invalid config raises TarlConfigError.
- Canonical types: dict[str, object] for all settings.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from tarl.spec import TarlError


class TarlConfigError(TarlError):
    """Raised when a TARL configuration is invalid."""


# Allowed config keys (whitelist — unknown keys are rejected).
ALLOWED_KEYS: frozenset[str] = frozenset(
    {"cache_size", "audit_enabled", "audit_max_records", "policy_timeout_ms"}
)

# Defaults
DEFAULT_CACHE_SIZE: int = 128
DEFAULT_AUDIT_ENABLED: bool = True
DEFAULT_AUDIT_MAX_RECORDS: int = 1000
DEFAULT_POLICY_TIMEOUT_MS: int = 5000


@dataclass(frozen=True)
class TarlConfig:
    """Typed runtime configuration.

    Attributes:
        cache_size: Maximum entries in the runtime cache (0 = disabled).
        audit_enabled: Whether to record ExecutionRecord entries.
        audit_max_records: Maximum audit log size before pruning.
        policy_timeout_ms: Per-policy evaluation timeout in milliseconds.
    """

    cache_size: int = DEFAULT_CACHE_SIZE
    audit_enabled: bool = DEFAULT_AUDIT_ENABLED
    audit_max_records: int = DEFAULT_AUDIT_MAX_RECORDS
    policy_timeout_ms: int = DEFAULT_POLICY_TIMEOUT_MS

    @property
    def canonical(self) -> dict[str, object]:
        return {
            "cache_size": self.cache_size,
            "audit_enabled": self.audit_enabled,
            "audit_max_records": self.audit_max_records,
            "policy_timeout_ms": self.policy_timeout_ms,
        }


def make_config(
    *,
    cache_size: int = DEFAULT_CACHE_SIZE,
    audit_enabled: bool = DEFAULT_AUDIT_ENABLED,
    audit_max_records: int = DEFAULT_AUDIT_MAX_RECORDS,
    policy_timeout_ms: int = DEFAULT_POLICY_TIMEOUT_MS,
) -> TarlConfig:
    """Construct a TarlConfig with validation."""
    if not isinstance(cache_size, int) or isinstance(cache_size, bool):
        raise TarlConfigError(f"cache_size must be int, got {type(cache_size).__name__}")
    if cache_size < 0:
        raise TarlConfigError(f"cache_size must be >= 0, got {cache_size}")
    if not isinstance(audit_enabled, bool):
        raise TarlConfigError(f"audit_enabled must be bool, got {type(audit_enabled).__name__}")
    if not isinstance(audit_max_records, int) or isinstance(audit_max_records, bool):
        raise TarlConfigError(
            f"audit_max_records must be int, got {type(audit_max_records).__name__}"
        )
    if audit_max_records < 0:
        raise TarlConfigError(f"audit_max_records must be >= 0, got {audit_max_records}")
    if not isinstance(policy_timeout_ms, int) or isinstance(policy_timeout_ms, bool):
        raise TarlConfigError(
            f"policy_timeout_ms must be int, got {type(policy_timeout_ms).__name__}"
        )
    if policy_timeout_ms < 0:
        raise TarlConfigError(f"policy_timeout_ms must be >= 0, got {policy_timeout_ms}")
    return TarlConfig(
        cache_size=cache_size,
        audit_enabled=audit_enabled,
        audit_max_records=audit_max_records,
        policy_timeout_ms=policy_timeout_ms,
    )


def config_from_mapping(mapping: Mapping[str, object]) -> TarlConfig:
    """Build a TarlConfig from a dict-like input.

    Rejects unknown keys (whitelist-only).
    """
    for key in mapping:
        if key not in ALLOWED_KEYS:
            raise TarlConfigError(f"unknown config key {key!r}")
    kwargs: dict[str, Any] = {}
    if "cache_size" in mapping:
        kwargs["cache_size"] = mapping["cache_size"]
    if "audit_enabled" in mapping:
        kwargs["audit_enabled"] = mapping["audit_enabled"]
    if "audit_max_records" in mapping:
        kwargs["audit_max_records"] = mapping["audit_max_records"]
    if "policy_timeout_ms" in mapping:
        kwargs["policy_timeout_ms"] = mapping["policy_timeout_ms"]
    return make_config(**kwargs)


__all__ = [
    "ALLOWED_KEYS",
    "DEFAULT_AUDIT_ENABLED",
    "DEFAULT_AUDIT_MAX_RECORDS",
    "DEFAULT_CACHE_SIZE",
    "DEFAULT_POLICY_TIMEOUT_MS",
    "TarlConfig",
    "TarlConfigError",
    "config_from_mapping",
    "make_config",
]
