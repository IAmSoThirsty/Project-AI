"""Test the audit chain verification script."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "verify_audit_chain.py"


def _run_script(audit_path: str) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), audit_path],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def test_valid_chain_exits_zero(tmp_path: Path) -> None:
    """A valid audit chain must exit 0."""
    from audit.chain import FileAuditLog

    log_path = tmp_path / "audit.jsonl"
    log = FileAuditLog(log_path)
    log.append_event(
        decision_id="d1",
        actor_id="agent1",
        action="test",
        resource="res",
        result="ALLOW",
        reason="test",
        event_type="governance",
    )
    code, out, err = _run_script(str(log_path))
    assert code == 0, f"Expected exit 0, got {code}: {err}"
    assert "valid" in out.lower()


def test_missing_file_exits_nonzero(tmp_path: Path) -> None:
    """A missing audit file must exit 1."""
    code, _out, _err = _run_script(str(tmp_path / "nonexistent.jsonl"))
    assert code == 1


def test_corrupted_chain_exits_nonzero(tmp_path: Path) -> None:
    """A corrupted chain must exit 1."""
    from audit.chain import FileAuditLog

    log_path = tmp_path / "audit.jsonl"
    log = FileAuditLog(log_path)
    log.append_event(
        decision_id="d1",
        actor_id="agent1",
        action="test",
        resource="res",
        result="ALLOW",
        reason="test",
        event_type="governance",
    )
    # Corrupt the last line
    lines = log_path.read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[-1])
    record["event_hash"] = "0" * 64
    lines[-1] = json.dumps(record, sort_keys=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    code, out, _err = _run_script(str(log_path))
    assert code == 1
    assert "mismatch" in out.lower() or "invalid" in out.lower()
