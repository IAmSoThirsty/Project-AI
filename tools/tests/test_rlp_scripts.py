"""Test RLP scripts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_probe_refresh_missing_state_exits_nonzero(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools" / "rlp_probe_refresh.py"),
            "--state-file",
            str(tmp_path / "nonexistent.json"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1


def test_sgc_tick_missing_state_exits_nonzero(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools" / "rlp_sgc_tick.py"),
            "--state-file",
            str(tmp_path / "nonexistent.json"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
