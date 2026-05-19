from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "scripts/arch_angel_docs_guard.py"


def run_guard(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--root", str(PROJECT_ROOT)],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_cli_check_passes() -> None:
    result = run_guard("check")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Arch Angel status: ok" in result.stdout
    assert "Publications: 21" in result.stdout


def test_cli_repair_dry_run_reports_no_critical_failures() -> None:
    result = run_guard("repair", "--dry-run")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Publications: 21" in result.stdout


def test_cli_report_after_check() -> None:
    check = run_guard("check")
    assert check.returncode == 0, check.stdout + check.stderr

    report = run_guard("report")
    assert report.returncode == 0, report.stdout + report.stderr
    assert '"total_publications": 21' in report.stdout
