#!/usr/bin/env python3
"""
Phase D1 — Repository hygiene verification
==========================================
Date: 2026-05-19

Checks that runtime artifacts, generated files, and large binaries are
properly excluded from git and Docker build context.

Exit 0: all checks pass.
Exit 1: one or more gaps remain.
"""

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent.parent
_GITIGNORE = _REPO_ROOT / ".gitignore"
_DOCKERIGNORE = _REPO_ROOT / ".dockerignore"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _git_ignores(path: str) -> bool:
    """Return True if git check-ignore considers the path ignored."""
    result = subprocess.run(
        ["git", "check-ignore", "-q", path],
        cwd=_REPO_ROOT,
        capture_output=True,
    )
    return result.returncode == 0


def _gitignore_contains(pattern: str) -> bool:
    text = _GITIGNORE.read_text(encoding="utf-8", errors="replace")
    return pattern in text


def _dockerignore_contains(pattern: str) -> bool:
    text = _DOCKERIGNORE.read_text(encoding="utf-8", errors="replace")
    return pattern in text


# ---------------------------------------------------------------------------
# Check tables
# ---------------------------------------------------------------------------

_GITIGNORE_PATTERN_CHECKS: list[tuple[str, str]] = [
    ("*.log",                 "Log files (*.log)"),
    ("*.log.*",               "Rotated logs (*.log.1, etc.)"),
    ("*.jsonl",               "JSON Lines runtime artifacts"),
    ("data/logs/",            "Data logs directory"),
    ("data/audit/",           "Data audit directory"),
    ("test-artifacts/",       "Test artifact outputs"),
    ("ci-reports/",           "CI report directory"),
    (".venv/",                "Primary venv (.venv/)"),
    (".venv_*/",              "All venv variants (.venv_airllm etc.)"),
    ("*.dll",                 "Windows DLL binaries"),
    ("*.lib",                 "Windows static libraries"),
    ("*.pdf",                 "Generated PDFs"),
    ("bundles/",              "BundleManager working directory"),
    ("execution_trace.json",  "Execution trace artifact"),
    ("tarl_os/tests/results/","TARL test result directory"),
    ("data/arch_angel/",      "Runtime arch_angel data"),
    ("data/savepoints/",      "Runtime savepoints"),
    ("shadow_test_output.txt","Shadow test output"),
    ("page1_preview.png",     "Preview PNG artifacts"),
]

_GIT_CHECK_IGNORE_PATHS: list[tuple[str, str]] = [
    ("data/logs/god_tier.log",            "god_tier.log"),
    ("data/logs/god_tier.log.1",          "rotated log (*.log.1)"),
    ("test-artifacts/test_run.jsonl",     "test artifact JSONL"),
    ("ci-reports/report.txt",             "CI report"),
    ("bundles/swr_scenarios.zip",         "SWR bundle"),
    ("execution_trace.json",              "execution trace"),
    ("data/audit/audit_20260101.jsonl",   "audit JSONL"),
    ("page1_preview.png",                 "preview PNG"),
    ("output.pdf",                        "generated PDF"),
    (".venv_airllm/lib/libpython.so",     ".venv_airllm directory"),
    (".venv_prod/bin/python",             ".venv_prod directory"),
    ("shadow_test_output.txt",            "shadow test output"),
    ("tarl_os/tests/results/run.json",   "TARL test result JSON"),
    ("data/arch_angel/state.json",        "arch_angel runtime data"),
]

_DOCKERIGNORE_PATTERN_CHECKS: list[tuple[str, str]] = [
    (".venv",          "Primary venv (docker)"),
    (".venv_*/",       "All venv variants (docker)"),
    ("*.log",          "Log files (docker)"),
    ("*.pyd",          "Windows .pyd (docker)"),
    ("*.dll",          "Windows DLL (docker)"),
    ("*.sqlite",       "SQLite databases (docker)"),
    ("*.jsonl",        "JSONL runtime artifacts (docker)"),
    ("test-artifacts/","Test artifacts (docker)"),
    ("ci-reports/",    "CI reports (docker)"),
    ("data/logs/",     "Data logs (docker)"),
    ("bundles/",       "BundleManager directory (docker)"),
    (".mypy_cache/",   "mypy cache (docker)"),
    (".obsidian/",     "Obsidian vault (docker)"),
]

_TRACKED_RUNTIME_FILES: list[tuple[str, str]] = [
    ("cognition/governance_audit.log",
     "Tracked runtime log — requires git rm --cached in a future phase"),
    ("docs/security_compliance/fourlaws-test-runs-latest.jsonl",
     "Tracked test run JSONL — intentional evidence record; size growth warrants LFS review"),
    ("tarl_os/tests/results/stress_test_results_1769808374.json",
     "Tracked 20MB test result — requires git rm --cached; gitignore rule now prevents re-add"),
    ("test-data/adversarial_stress_tests_2000.json",
     "Tracked 3.2MB test data — intentional test fixture; LFS recommended if growing"),
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("# Phase D1 Repository Hygiene Verification")
    print("# Date: 2026-05-19")
    print(f"# Repo: {_REPO_ROOT}")
    print()

    failures: list[str] = []

    # 1. gitignore pattern presence
    print("## .gitignore pattern checks")
    for pattern, description in _GITIGNORE_PATTERN_CHECKS:
        ok = _gitignore_contains(pattern)
        print(f"  {'PASS' if ok else 'FAIL'}: {description} ({pattern!r})")
        if not ok:
            failures.append(f".gitignore missing {pattern!r}")

    print()

    # 2. git check-ignore path checks
    print("## git check-ignore path checks")
    for path, description in _GIT_CHECK_IGNORE_PATHS:
        ok = _git_ignores(path)
        print(f"  {'PASS' if ok else 'FAIL'}: {description} ({path!r})")
        if not ok:
            failures.append(f"git does not ignore {path!r}")

    print()

    # 3. dockerignore pattern presence
    print("## .dockerignore pattern checks")
    for pattern, description in _DOCKERIGNORE_PATTERN_CHECKS:
        ok = _dockerignore_contains(pattern)
        print(f"  {'PASS' if ok else 'FAIL'}: {description} ({pattern!r})")
        if not ok:
            failures.append(f".dockerignore missing {pattern!r}")

    print()

    # 4. Already-tracked runtime files (documented, not errors)
    print("## Already-tracked runtime files (documented, require follow-up)")
    for path, note in _TRACKED_RUNTIME_FILES:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", path],
            cwd=_REPO_ROOT, capture_output=True,
        )
        tracked = result.returncode == 0
        ignored_now = _git_ignores(path)
        print(f"  {'TRACKED' if tracked else 'UNTRACKED'} / {'IGNORED' if ignored_now else 'NOT IGNORED'}: {path}")
        print(f"    Note: {note}")

    print()

    if failures:
        print(f"# RESULT: FAIL — {len(failures)} checks failed:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("# RESULT: PASS — all artifact categories properly excluded from git and Docker")
    return 0


if __name__ == "__main__":
    sys.exit(main())
