"""Adapters for existing red-team suites."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from app.testing.pa_shield.common import find_repo_root


def run_legacy_project_ai_suites(output_dir: Path) -> dict:
    """Execute the existing Project-AI-only red-team suites and collect reports."""
    repo_root = find_repo_root()
    commands = {
        "jbb": repo_root / "adversarial_tests" / "jbb" / "run_jbb.py",
        "multiturn": repo_root / "adversarial_tests" / "multiturn" / "run_multiturn.py",
        "garak": repo_root / "adversarial_tests" / "garak" / "run_garak.py",
    }
    reports: dict[str, dict] = {}
    for name, script in commands.items():
        destination = output_dir / f"legacy-{name}.json"
        subprocess.run(
            [sys.executable, str(script), "--output", str(destination)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        if destination.exists():
            reports[name] = json.loads(destination.read_text(encoding="utf-8"))
    return reports
