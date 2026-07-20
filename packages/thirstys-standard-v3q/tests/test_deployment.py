from __future__ import annotations

import json
from pathlib import Path

import pytest
from thirstys_standard_runtime.deployment import (
    V3QConfigurationError,
    load_gate_config,
)


def _write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_development_without_registry_remains_dormant(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("THIRSTYS_V3Q_REQUIRED", raising=False)
    monkeypatch.delenv("THIRSTYS_V3Q_REGISTRY", raising=False)

    assert load_gate_config() is None


def test_required_mode_loads_packaged_public_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("THIRSTYS_V3Q_REQUIRED", "true")
    monkeypatch.delenv("THIRSTYS_V3Q_REGISTRY", raising=False)

    config = load_gate_config()

    assert config is not None
    assert config.trusted_keys["keys"]


def test_required_mode_rejects_invalid_registry(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    registry = _write_json(
        tmp_path / "registry.json",
        {"keys": []},
    )
    monkeypatch.setenv("THIRSTYS_V3Q_REQUIRED", "true")
    monkeypatch.setenv("THIRSTYS_V3Q_REGISTRY", str(registry))

    with pytest.raises(V3QConfigurationError, match="unreadable or empty"):
        load_gate_config()


def test_required_mode_loads_configured_public_registry(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    registry = _write_json(
        tmp_path / "registry.json",
        {"keys": [{"key_id": "owner-current"}]},
    )
    monkeypatch.setenv("THIRSTYS_V3Q_REQUIRED", "true")
    monkeypatch.setenv("THIRSTYS_V3Q_REGISTRY", str(registry))

    config = load_gate_config()

    assert config is not None
    assert config.trusted_keys["keys"][0]["key_id"] == "owner-current"
