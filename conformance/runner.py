"""Thirsty-Lang Conformance Test Runner.

Usage:
    python conformance/runner.py [--all] [--category CATEGORY] [--verbose]

Invokes the interpreter via subprocess so no PATH installation is required.
Set PYTHONPATH=src/utf before running (or the runner does it automatically).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SUITE_DIR = Path(__file__).parent
REPO_ROOT = SUITE_DIR.parent
SRC_UTF = str(REPO_ROOT / "src" / "utf")

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
SKIP = "\033[93mSKIP\033[0m"


def run_test(case: dict[str, Any], verbose: bool = False) -> tuple[bool, str]:
    source: str = case.get("source", "")
    expected_stdout: str = case.get("expected_stdout", "")
    expected_exit: int = case.get("expected_exit_code", 0)
    expected_diag: list[dict] = case.get("expected_diagnostics", [])
    description: str = case.get("description", case.get("id", "?"))

    env = {**os.environ, "PYTHONPATH": SRC_UTF, "PYTHONIOENCODING": "utf-8"}

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".thirsty", encoding="utf-8", delete=False
    ) as f:
        f.write(source)
        tmp = f.name

    try:
        result = subprocess.run(
            [sys.executable, "-m", "thirsty_lang.cli", "run", tmp],
            capture_output=True,
            text=True,
            env=env,
        )
    finally:
        os.unlink(tmp)

    stdout = result.stdout
    stderr = result.stderr
    exit_code = result.returncode

    failures: list[str] = []

    if exit_code != expected_exit:
        failures.append(f"exit code: expected {expected_exit}, got {exit_code}")

    if stdout != expected_stdout:
        failures.append(
            f"stdout mismatch:\n  expected: {expected_stdout!r}\n  got:      {stdout!r}"
        )

    combined_output = stdout + stderr
    for diag in expected_diag:
        code = diag.get("code", "")
        if code and code not in combined_output:
            failures.append(f"missing diagnostic code: {code}")
        msg_contains = diag.get("message_contains", "")
        if msg_contains and msg_contains not in combined_output:
            failures.append(f"diagnostic message missing: {msg_contains!r}")

    passed = not failures
    if verbose and not passed:
        detail = "\n    ".join(failures)
        return False, f"  {FAIL} {description}\n    {detail}"
    if verbose:
        return True, f"  {PASS} {description}"
    return passed, description


def load_suites(category: str | None = None) -> list[tuple[str, dict]]:
    """Return list of (suite_name, test_case) from all JSON suite files."""
    cases: list[tuple[str, dict]] = []
    pattern = f"{category}.json" if category else "*.json"
    for json_file in sorted(SUITE_DIR.glob(pattern)):
        suite_name = json_file.stem
        data = json.loads(json_file.read_text(encoding="utf-8"))
        if isinstance(data, list):
            for case in data:
                cases.append((suite_name, case))
        elif isinstance(data, dict) and "tests" in data:
            for case in data["tests"]:
                cases.append((suite_name, case))
    return cases


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Thirsty conformance runner")
    parser.add_argument("--all", action="store_true", help="Run all suites")
    parser.add_argument("--category", help="Run a specific category (e.g. syntax)")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args(argv)

    cases = load_suites(args.category)
    if not cases:
        print("No test cases found. Did you specify a valid category?")
        return 1

    passed = 0
    failed = 0
    by_suite: dict[str, tuple[int, int]] = {}

    for suite_name, case in cases:
        ok, msg = run_test(case, verbose=args.verbose)
        p, f = by_suite.get(suite_name, (0, 0))
        if ok:
            passed += 1
            by_suite[suite_name] = (p + 1, f)
        else:
            failed += 1
            by_suite[suite_name] = (p, f + 1)
            if args.verbose:
                print(msg)
            elif args.fail_fast:
                print(f"FAIL: {case.get('description', case.get('id', '?'))} [{suite_name}]")
                print(f"  {msg}")
                break

    total = passed + failed
    print(f"\n{'─' * 50}")
    print(f"Results: {passed}/{total} passed")
    for suite, (p, f) in sorted(by_suite.items()):
        status = "✓" if f == 0 else "✗"
        print(f"  {status} {suite}: {p}/{p+f}")
    print(f"{'─' * 50}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
