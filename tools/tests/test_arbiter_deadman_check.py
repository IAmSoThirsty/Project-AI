"""Test arbiter_deadman_check.py."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "arbiter_deadman_check.py"


def _run(state_file: str) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--state-file", state_file],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def test_no_state_file_exits_zero(tmp_path: Path) -> None:
    """No state file means no arbiter active — exit 0 (informational)."""
    code, out, _ = _run(str(tmp_path / "nonexistent.json"))
    assert code == 0
    assert "no state" in out.lower() or "not found" in out.lower()


def test_active_arbiter_exits_zero(tmp_path: Path) -> None:
    """An active arbiter (recent heartbeat) should exit 0."""
    state_file = tmp_path / "arbiter-state.json"
    state = {
        "last_heartbeat": time.time(),
        "status": "active",
        "heartbeat_seconds": 2592000,
        "grace_seconds": 1209600,
    }
    state_file.write_text(json.dumps(state), encoding="utf-8")
    code, out, _ = _run(str(state_file))
    assert code == 0
    assert "active" in out.lower()


def test_lapsed_arbiter_exits_nonzero(tmp_path: Path) -> None:
    """A lapsed arbiter (heartbeat expired) should exit 1."""
    state_file = tmp_path / "arbiter-state.json"
    state = {
        "last_heartbeat": 0,
        "status": "active",
        "heartbeat_seconds": 1,
        "grace_seconds": 1,
    }
    state_file.write_text(json.dumps(state), encoding="utf-8")
    code, out, _ = _run(str(state_file))
    assert code == 1
    assert "lapsed" in out.lower() or "succeeded" in out.lower()
