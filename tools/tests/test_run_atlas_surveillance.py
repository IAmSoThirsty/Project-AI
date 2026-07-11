"""Test run_atlas_surveillance.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "run_atlas_surveillance.py"


def test_missing_dir_exits_zero(tmp_path: Path) -> None:
    """Missing artifacts dir should warn and exit 0 (no anomalies)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--artifacts-dir", str(tmp_path / "nonexistent")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "No artifacts" in result.stdout or "not found" in result.stderr
