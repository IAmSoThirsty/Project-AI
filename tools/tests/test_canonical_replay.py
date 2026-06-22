from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_canonical_replay_passes_all_five_invariants() -> None:
    tool = Path(__file__).parents[1] / "canonical_replay.py"
    result = subprocess.run(
        [sys.executable, str(tool)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "canonical replay: 5/5 invariants passed" in result.stdout
