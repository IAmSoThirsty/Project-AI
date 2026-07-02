"""Integration test: Atlas ConfigLoader (J5.2).

Per docs/internal/J5_DISCOVERY.md Phase J5.2: the
ConfigLoader is a production-grade configuration loader
for PROJECT ATLAS. It loads + validates + provides
access to all YAML configuration files with SHA-256 hash
verification, immutability enforcement, and audit logging.

6 YAML configs:
- stacks.yaml (RS, TS-0..3, SS stacks + transitions)
- drivers.yaml (influence drivers + weights)
- penalties.yaml (stack penalties)
- thresholds.yaml (operational thresholds)
- safety.yaml (safety rules, LOCKED)
- seeds.yaml (timeline seeds for divergence)

Honest scope:
- Tests the public surface: ConfigurationError,
  SafetyViolationError, ConfigLoader, get_config_loader,
  reset_config_loader.
- Tests config loading from default location.
- Tests get/get_hash/get_all_hashes for all 6 configs.
- Tests verify_integrity (passes when unchanged).
- Tests get_metadata (returns load_timestamp + config_dir
  + configs_loaded + hashes + versions).
- Tests export_audit_log (returns JSON string).
- Tests that get() returns a copy (mutation safety).
- Tests that unknown config raises ConfigurationError.
- Tests that unknown hash raises ConfigurationError.
- Tests singleton factory + reset.
- Does NOT test loading from a custom directory (would
  require creating temp YAML files - the canonical
  config location is always used in production).
- Does NOT test safety violation paths (would require
  modifying the canonical safety.yaml which is LOCKED).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from atlas.config.loader import (
    ConfigLoader,
    ConfigurationError,
    SafetyViolationError,
    get_config_loader,
    reset_config_loader,
)

# ── 1. Errors ───────────────────────────────────


def test_configuration_error_is_exception() -> None:
    """ConfigurationError inherits from Exception."""
    assert issubclass(ConfigurationError, Exception)


def test_safety_violation_error_is_exception() -> None:
    """SafetyViolationError inherits from Exception."""
    assert issubclass(SafetyViolationError, Exception)


# ── 2. ConfigLoader creation ────────────────────


def test_config_loader_creation_default_dir() -> None:
    """ConfigLoader can be created with default config dir."""
    loader = ConfigLoader()
    assert loader.config_dir.exists()
    # Should have loaded all 6 configs
    assert len(loader._configs) == 6


def test_config_loader_creation_with_custom_dir() -> None:
    """ConfigLoader can be created with a custom dir."""
    # Use the default config dir (already validated)
    default = Path(__file__).parent.parent / "packages" / "atlas" / "src" / "atlas" / "config"
    loader = ConfigLoader(config_dir=default)
    assert loader.config_dir == default


def test_config_loader_creation_missing_dir_raises() -> None:
    """ConfigLoader raises ConfigurationError on missing dir."""
    with pytest.raises(ConfigurationError, match="not found"):
        ConfigLoader(config_dir=Path("/nonexistent/path/xyz"))


# ── 3. Config loading ───────────────────────────


def test_config_loader_loads_all_6_configs() -> None:
    """ConfigLoader loads all 6 expected configs."""
    loader = ConfigLoader()
    expected = {
        "stacks",
        "drivers",
        "penalties",
        "thresholds",
        "safety",
        "seeds",
    }
    assert set(loader._configs.keys()) == expected


def test_config_loader_loads_stacks_config() -> None:
    """ConfigLoader loads stacks.yaml with stacks section."""
    loader = ConfigLoader()
    stacks = loader.get("stacks")
    assert "stacks" in stacks
    assert "version" in stacks
    assert len(stacks["stacks"]) == 6  # RS, TS-0..3, SS


def test_config_loader_loads_safety_config_locked() -> None:
    """ConfigLoader loads safety.yaml with locked=True."""
    loader = ConfigLoader()
    safety = loader.get("safety")
    assert safety["locked"] is True
    assert safety["modification_allowed"] is False


def test_config_loader_loads_drivers_config() -> None:
    """ConfigLoader loads drivers.yaml with influence_drivers."""
    loader = ConfigLoader()
    drivers = loader.get("drivers")
    assert "influence_drivers" in drivers
    # Weights should sum to 1.0 (validated in _validate_drivers)
    total = sum(
        d.get("weight", 0.0) for d in drivers["influence_drivers"].values() if isinstance(d, dict)
    )
    assert 0.99 <= total <= 1.01


# ── 4. get() ────────────────────────────────────


def test_get_returns_dict() -> None:
    """get() returns a dict for valid config name."""
    loader = ConfigLoader()
    s = loader.get("stacks")
    assert isinstance(s, dict)


def test_get_returns_copy() -> None:
    """get() returns a copy (mutation safe)."""
    loader = ConfigLoader()
    s1 = loader.get("stacks")
    s1["__mutated__"] = True
    s2 = loader.get("stacks")
    assert "__mutated__" not in s2


def test_get_unknown_raises() -> None:
    """get() raises ConfigurationError for unknown config."""
    loader = ConfigLoader()
    with pytest.raises(ConfigurationError, match="not found"):
        loader.get("nonexistent_config")


# ── 5. Hashes ───────────────────────────────────


def test_get_hash_returns_64_hex() -> None:
    """get_hash() returns 64-char hex string."""
    loader = ConfigLoader()
    h = loader.get_hash("stacks")
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_get_all_hashes_returns_all_6() -> None:
    """get_all_hashes() returns hashes for all 6 configs."""
    loader = ConfigLoader()
    hashes = loader.get_all_hashes()
    assert len(hashes) == 6
    assert set(hashes.keys()) == {
        "stacks",
        "drivers",
        "penalties",
        "thresholds",
        "safety",
        "seeds",
    }


def test_get_hash_unknown_raises() -> None:
    """get_hash() raises ConfigurationError for unknown config."""
    loader = ConfigLoader()
    with pytest.raises(ConfigurationError, match="not found"):
        loader.get_hash("nonexistent")


# ── 6. Integrity ────────────────────────────────


def test_verify_integrity_true() -> None:
    """verify_integrity() returns True when configs unchanged."""
    loader = ConfigLoader()
    assert loader.verify_integrity() is True


# ── 7. Metadata ─────────────────────────────────


def test_get_metadata_returns_dict() -> None:
    """get_metadata() returns a dict with expected keys."""
    loader = ConfigLoader()
    meta = loader.get_metadata()
    assert "load_timestamp" in meta
    assert "config_dir" in meta
    assert "configs_loaded" in meta
    assert "hashes" in meta
    assert "versions" in meta
    assert len(meta["configs_loaded"]) == 6
    assert len(meta["versions"]) == 6


def test_get_metadata_versions_are_strings() -> None:
    """get_metadata() returns all version strings."""
    loader = ConfigLoader()
    meta = loader.get_metadata()
    for _name, version in meta["versions"].items():
        assert isinstance(version, str)
        assert version != "unknown"


# ── 8. Audit log ────────────────────────────────


def test_export_audit_log_returns_json_string() -> None:
    """export_audit_log() returns a valid JSON string."""
    loader = ConfigLoader()
    log = loader.export_audit_log()
    parsed = json.loads(log)
    assert "timestamp" in parsed
    assert "metadata" in parsed
    assert "integrity_verified" in parsed
    assert "safety_status" in parsed
    assert parsed["integrity_verified"] is True
    assert parsed["safety_status"]["locked"] is True


# ── 9. Singleton factory ────────────────────────


def test_get_config_loader_singleton() -> None:
    """get_config_loader returns the same instance."""
    reset_config_loader()
    l1 = get_config_loader()
    l2 = get_config_loader()
    assert l1 is l2


def test_reset_config_loader() -> None:
    """reset_config_loader clears the singleton."""
    reset_config_loader()
    l1 = get_config_loader()
    reset_config_loader()
    l2 = get_config_loader()
    # After reset, a new instance is created
    assert l1 is not l2


# ── 10. Public surface completeness ─────────────


def test_public_surface_complete() -> None:
    """All 5 public symbols are exported."""
    import atlas.config.loader as m

    expected = {
        "ConfigurationError",
        "SafetyViolationError",
        "ConfigLoader",
        "get_config_loader",
        "reset_config_loader",
    }
    assert expected.issubset(set(m.__all__))
