"""Attack suite loading for PA-SHIELD."""

from __future__ import annotations

import json
from pathlib import Path

from app.testing.pa_shield.common import find_repo_root
from app.testing.pa_shield.models import AttackCase


SUITE_FILES = {
    "instruction_override": "instruction_override.json",
    "tool_escalation": "tool_escalation.json",
    "state_corruption": "state_corruption.json",
    "governance_bypass": "governance_bypass.json",
    "benign_controls": "benign_controls.json",
    "chained_attacks": "chained_attacks.json",
}


def attack_asset_dir() -> Path:
    """Return the on-disk directory containing attack JSON assets."""
    return find_repo_root() / "adversarial_tests" / "pa_shield" / "attacks"


def load_suite(suite: str) -> list[AttackCase]:
    """Load a single suite or all suites."""
    base_dir = attack_asset_dir()
    if suite == "full":
        cases: list[AttackCase] = []
        for suite_name in SUITE_FILES:
            cases.extend(load_suite(suite_name))
        return cases

    if suite not in SUITE_FILES:
        known = ", ".join(["full", *SUITE_FILES.keys()])
        raise ValueError(f"Unknown suite '{suite}'. Expected one of: {known}")

    asset_path = base_dir / SUITE_FILES[suite]
    raw_cases = json.loads(asset_path.read_text(encoding="utf-8"))
    return [AttackCase(**case) for case in raw_cases]


def available_suites() -> list[str]:
    """List the supported suite names."""
    return ["full", *SUITE_FILES.keys()]
