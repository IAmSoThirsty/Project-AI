from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "scripts" / "verify_heart_restore_map.py"


def run_verifier(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(PROJECT_ROOT), *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_heart_restore_verifier_passes_with_warnings_allowed() -> None:
    result = run_verifier("--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert payload["counts"]["fail"] == 0


def test_heart_restore_verifier_checks_git_library_and_branches() -> None:
    result = run_verifier("--json")
    payload = json.loads(result.stdout)
    scopes = {check["scope"] for check in payload["checks"]}

    assert "repo-scan-contract" in scopes
    assert "git" in scopes
    assert "repo-library" in scopes
    assert "git-branches" in scopes
    assert any(
        check["scope"] == "repo-scan-contract"
        and "tracked -> branches -> untracked-git" in check["message"]
        for check in payload["checks"]
    )
    assert any(
        check["scope"] == "git-branches" and "surveyed" in check["message"]
        for check in payload["checks"]
    )
