from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.app.governance import genesis_continuity
from src.app.governance.genesis_continuity import (
    GenesisContinuityGuard,
    GenesisDiscontinuityError,
)


def _repo_default_log() -> Path:
    return (
        Path(genesis_continuity.__file__).resolve().parents[3]
        / "data"
        / "genesis_pins"
        / "continuity_log.json"
    )


def _reset_genesis_state() -> None:
    with genesis_continuity._LOCK:
        genesis_continuity._KEY_DIR_PINS.clear()
        genesis_continuity._GENESIS_PINS.clear()
        genesis_continuity._VIOLATIONS.clear()


@pytest.fixture(autouse=True)
def reset_genesis_state() -> None:
    _reset_genesis_state()
    yield
    _reset_genesis_state()


def _trigger_discontinuity(guard: GenesisContinuityGuard, key_dir: Path) -> None:
    guard.check_or_pin(key_dir, "GENESIS-AAAA1111", b"first-public-key")
    with pytest.raises(GenesisDiscontinuityError):
        guard.check_or_pin(key_dir, "GENESIS-BBBB2222", b"second-public-key")


def test_custom_continuity_log_does_not_also_write_repo_default(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("PROJECT_AI_GENESIS_CONTINUITY_LOG", raising=False)
    repo_log = _repo_default_log()
    original = repo_log.read_text(encoding="utf-8") if repo_log.exists() else None
    custom_log = tmp_path / "genesis_pins" / "continuity_log.json"

    guard = GenesisContinuityGuard(continuity_log_file=custom_log)
    _trigger_discontinuity(guard, tmp_path / "genesis_keys")

    assert len(json.loads(custom_log.read_text(encoding="utf-8"))) == 1
    if original is None:
        assert not repo_log.exists()
    else:
        assert repo_log.read_text(encoding="utf-8") == original


def test_env_continuity_log_override_keeps_default_guard_out_of_repo_data(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_log = _repo_default_log()
    original = repo_log.read_text(encoding="utf-8") if repo_log.exists() else None
    override_log = tmp_path / "pytest_genesis_pins" / "continuity_log.json"
    monkeypatch.setenv("PROJECT_AI_GENESIS_CONTINUITY_LOG", str(override_log))

    guard = GenesisContinuityGuard()
    _trigger_discontinuity(guard, tmp_path / "genesis_keys")

    assert len(json.loads(override_log.read_text(encoding="utf-8"))) == 1
    if original is None:
        assert not repo_log.exists()
    else:
        assert repo_log.read_text(encoding="utf-8") == original
