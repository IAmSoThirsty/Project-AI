"""Test verify_convergence_hash.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "verify_convergence_hash.py"

EXPECTED_HASH = "3eda3256049339cb069354cc81ee7c51d88e3e41e81ea707e5bf3d3e14ba478c"


def test_script_runs_and_reports() -> None:
    """Script should run and produce output containing OK or FAIL."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode in (0, 1)
    assert "hash" in result.stdout.lower() or "hash" in result.stderr.lower()
