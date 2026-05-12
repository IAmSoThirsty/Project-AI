"""
Thirsty-Lang JavaScript conformance runner.

Runs conformance test descriptors against the JS implementation at
src/thirsty_lang/src/cli.js using Node.js.

Usage:
    python conformance/runner_js.py [--suite SUITE] [--all]

Requirements:
    - Node.js must be installed and on PATH
    - src/thirsty_lang/src/cli.js must exist

The JS implementation (src/thirsty_lang/) is a separate independent
interpreter. Tests that pass here confirm cross-implementation conformance.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
JS_CLI = REPO_ROOT / "src" / "thirsty_lang" / "src" / "cli.js"

SUITE_FILES = [
    "syntax.json",
    "types.json",
    "errors.json",
    "stdlib.json",
    "modules.json",
    "advanced.json",
    "security.json",
    "governance.json",
    "shadow_mutation.json",
]


def node_available() -> bool:
    try:
        r = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            timeout=5,
        )
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def run_test_js(test: dict) -> tuple[bool, str]:
    """Run a single test against the JS implementation.

    Returns (passed: bool, detail: str).
    """
    source = test["source"]
    expected_stdout = test.get("expected_stdout", "")
    expected_exit = test.get("expected_exit_code", 0)

    # Write source to a temp file — JS CLI reads from disk
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".thirsty", delete=False, encoding="utf-8"
    ) as f:
        f.write(source)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["node", str(JS_CLI), tmp_path],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(REPO_ROOT),
        )
        actual_stdout = result.stdout
        actual_exit = result.returncode

        if actual_exit == expected_exit and actual_stdout == expected_stdout:
            return True, ""
        detail_parts = []
        if actual_stdout != expected_stdout:
            detail_parts.append(
                f"stdout expected={expected_stdout!r} got={actual_stdout!r}"
            )
        if actual_exit != expected_exit:
            detail_parts.append(
                f"exit expected={expected_exit} got={actual_exit}"
            )
        return False, "; ".join(detail_parts)
    except subprocess.TimeoutExpired:
        return False, "timeout"
    finally:
        os.unlink(tmp_path)


def run_suite(suite_file: Path) -> tuple[int, int]:
    """Run all tests in a JSON suite file. Returns (passed, total)."""
    tests = json.loads(suite_file.read_text(encoding="utf-8"))
    passed = failed = 0
    for test in tests:
        tid = test.get("id", "?")
        desc = test.get("description", "")
        ok, detail = run_test_js(test)
        if ok:
            print(f"  PASS  {tid}  {desc}")
            passed += 1
        else:
            print(f"  FAIL  {tid}  {desc}  — {detail}")
            failed += 1
    return passed, passed + failed


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Run Thirsty conformance tests against the JS implementation"
    )
    parser.add_argument("--suite", help="single suite file to run (e.g. syntax.json)")
    parser.add_argument("--all", action="store_true", help="run all suites")
    args = parser.parse_args(argv)

    if not JS_CLI.exists():
        print(f"ERROR: JS CLI not found at {JS_CLI}", file=sys.stderr)
        return 2

    if not node_available():
        print("ERROR: node not found on PATH — install Node.js to run JS conformance", file=sys.stderr)
        return 2

    conformance_dir = Path(__file__).parent

    suites: list[Path] = []
    if args.suite:
        suites = [conformance_dir / args.suite]
    elif args.all:
        suites = [conformance_dir / s for s in SUITE_FILES if (conformance_dir / s).exists()]
    else:
        # Default: run all available suites
        suites = [conformance_dir / s for s in SUITE_FILES if (conformance_dir / s).exists()]

    total_pass = total_tests = 0
    for suite_path in suites:
        if not suite_path.exists():
            print(f"WARNING: suite not found: {suite_path}", file=sys.stderr)
            continue
        print(f"\n=== {suite_path.name} ===")
        p, t = run_suite(suite_path)
        total_pass += p
        total_tests += t

    print(f"\n{'='*50}")
    print(f"JS conformance: {total_pass}/{total_tests} passed")
    return 0 if total_pass == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())
