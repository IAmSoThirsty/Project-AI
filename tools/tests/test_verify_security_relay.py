"""Test the security relay verification script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "verify_security_relay.py"


def _run_script(relay_path: str) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), relay_path],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def test_valid_relay_exits_zero(tmp_path: Path) -> None:
    """A valid relay chain must exit 0."""
    from security.bridge import AppendOnlyAuditRelay

    relay_path = tmp_path / "chimera-audit.jsonl"
    relay = AppendOnlyAuditRelay(relay_path)
    relay.append("test_event", {"key": "value"})
    code, out, _ = _run_script(str(relay_path))
    assert code == 0
    assert "valid" in out.lower()


def test_missing_file_exits_nonzero(tmp_path: Path) -> None:
    code, _, _ = _run_script(str(tmp_path / "nonexistent.jsonl"))
    assert code == 1


def test_empty_file_exits_zero(tmp_path: Path) -> None:
    """An empty file (no events) should be valid — genesis state."""
    relay_path = tmp_path / "empty.jsonl"
    relay_path.write_text("", encoding="utf-8")
    code, _out, _ = _run_script(str(relay_path))
    assert code == 0
