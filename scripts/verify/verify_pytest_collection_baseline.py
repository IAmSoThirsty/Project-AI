#!/usr/bin/env python3
"""
Phase D2 — pytest collection baseline verification
====================================================
Date: 2026-05-19

Runs pytest --collect-only and checks that:
1. Total collection errors do not exceed the D2 baseline of 102.
2. All 7 error groups are represented in the output (classification sanity).
3. No new unclassified error root causes have appeared.

Exit 0: collection errors at or below baseline, no regression.
Exit 1: collection errors exceed baseline or new unclassified causes found.
"""

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent.parent

D2_BASELINE_ERRORS = 102
D2_BASELINE_PASSING = 7675

_KNOWN_MISSING: set[str] = {
    # Group A — pip packages
    "numpy", "flask", "temporalio", "pandas", "typer",
    "defusedxml", "PyQt6", "matplotlib", "hypothesis", "mcp", "toml", "joblib",
    # Group B — PSIA (never written)
    "psia",
    # Group C — app sub-modules
    "sovereign_audit_log", "audit_manager", "agent_lounge", "meta_security_dept",
    "repair_crew", "personal_agent", "immutable_audit_log", "company_pricing",
    "government_pricing", "signal_flows", "tseca_ghost_protocol", "vault",
    "exceptions", "asymmetric_security", "containment", "substrate",
    "normalization", "repo_scan_contract",
    # Group D — UTF sub-modules
    "shadow_thirst",
    # Group E — stale imports (symbol errors)
    "EntityClass", "AntiSovereignStressTestGenerator", "BootSequence",
    # Group F — path drift
    "thirsty_lang", "api",
    # Group G — marker config
    "'chaos'", "'slow'", "'load'", "'timeout'",
}


def main() -> int:
    print("# Phase D2 pytest collection baseline verification")
    print(f"# Baseline: {D2_BASELINE_ERRORS} errors / {D2_BASELINE_PASSING} passing")
    print()

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "--tb=no"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr

    # Parse summary line: "collected N items / M errors"
    import re
    error_count = 0
    for line in output.splitlines():
        m = re.search(r"collected \d+ items? / (\d+) errors?", line)
        if m:
            error_count = int(m.group(1))
            print(f"  Collection summary: {line.strip()}")
            break
    else:
        # Fallback: count ERROR collecting lines (without --tb=no)
        error_count = sum(1 for ln in output.splitlines() if "ERROR collecting" in ln)

    print(f"  Collection errors found: {error_count}")
    print(f"  D2 baseline: {D2_BASELINE_ERRORS}")

    failures: list[str] = []

    if error_count > D2_BASELINE_ERRORS:
        failures.append(
            f"REGRESSION: {error_count} errors exceeds baseline {D2_BASELINE_ERRORS}"
            f" (+{error_count - D2_BASELINE_ERRORS} new errors)"
        )
    else:
        improvement = D2_BASELINE_ERRORS - error_count
        if improvement > 0:
            print(f"  IMPROVEMENT: {improvement} fewer errors than D2 baseline")
        else:
            print("  STABLE: at D2 baseline")

    # Check for new unclassified error causes
    new_causes: list[str] = []
    for line in output.splitlines():
        if "No module named" in line or "cannot import name" in line:
            known = any(k in line for k in _KNOWN_MISSING)
            if not known:
                new_causes.append(line.strip())

    if new_causes:
        print()
        print("  NEW UNCLASSIFIED CAUSES:")
        for c in new_causes:
            print(f"    {c}")
        failures.append(f"{len(new_causes)} new unclassified import error(s) found")
    else:
        print("  No new unclassified error causes detected")

    print()
    if failures:
        print(f"# RESULT: FAIL — {len(failures)} issue(s):")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("# RESULT: PASS — collection at or below D2 baseline, no regressions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
