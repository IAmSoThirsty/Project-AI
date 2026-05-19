"""
Phase D1 — Repository hygiene test suite
=========================================
Date: 2026-05-19

Verifies that .gitignore, .dockerignore, and git check-ignore
properly exclude runtime artifacts, venvs, logs, and large binaries
from the repository and Docker build context.
"""

import subprocess
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _git_ignores(path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", path],
        cwd=_REPO_ROOT,
        capture_output=True,
    )
    return result.returncode == 0


def _gitignore_contains(pattern: str) -> bool:
    text = (_REPO_ROOT / ".gitignore").read_text(encoding="utf-8", errors="replace")
    return pattern in text


def _dockerignore_contains(pattern: str) -> bool:
    text = (_REPO_ROOT / ".dockerignore").read_text(encoding="utf-8", errors="replace")
    return pattern in text


# ---------------------------------------------------------------------------
# .gitignore pattern presence
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("pattern,description", [
    ("*.log",                 "log files"),
    ("*.log.*",               "rotated logs"),
    ("*.jsonl",               "JSON Lines artifacts"),
    ("data/logs/",            "data logs directory"),
    ("data/audit/",           "data audit directory"),
    ("test-artifacts/",       "test artifact outputs"),
    ("ci-reports/",           "CI report directory"),
    (".venv/",                "primary venv"),
    (".venv_*/",              "venv variant glob"),
    ("*.dll",                 "Windows DLL binaries"),
    ("*.lib",                 "Windows static libraries"),
    ("*.pdf",                 "generated PDFs"),
    ("bundles/",              "BundleManager working directory"),
    ("execution_trace.json",  "execution trace artifact"),
    ("tarl_os/tests/results/","TARL test results directory"),
    ("data/arch_angel/",      "runtime arch_angel data"),
    ("data/savepoints/",      "runtime savepoints"),
    ("shadow_test_output.txt","shadow test output"),
    ("page1_preview.png",     "preview PNG artifact"),
])
def test_gitignore_contains_pattern(pattern: str, description: str) -> None:
    assert _gitignore_contains(pattern), (
        f".gitignore is missing pattern {pattern!r} ({description})"
    )


# ---------------------------------------------------------------------------
# git check-ignore path verification
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path,description", [
    ("data/logs/god_tier.log",            "god_tier.log"),
    ("data/logs/god_tier.log.1",          "rotated log"),
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
])
def test_git_ignores_path(path: str, description: str) -> None:
    assert _git_ignores(path), (
        f"git does not ignore {path!r} ({description}) — "
        f".gitignore rule missing or ineffective"
    )


# ---------------------------------------------------------------------------
# .dockerignore pattern presence
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("pattern,description", [
    (".venv",          "primary venv (docker)"),
    (".venv_*/",       "venv variants (docker)"),
    ("*.log",          "log files (docker)"),
    ("*.pyd",          "Windows .pyd (docker)"),
    ("*.dll",          "Windows DLL (docker)"),
    ("*.sqlite",       "SQLite databases (docker)"),
    ("*.jsonl",        "JSONL artifacts (docker)"),
    ("test-artifacts/","test artifacts (docker)"),
    ("ci-reports/",    "CI reports (docker)"),
    ("data/logs/",     "data logs (docker)"),
    ("bundles/",       "BundleManager directory (docker)"),
    (".mypy_cache/",   "mypy cache (docker)"),
    (".obsidian/",     "Obsidian vault (docker)"),
])
def test_dockerignore_contains_pattern(pattern: str, description: str) -> None:
    assert _dockerignore_contains(pattern), (
        f".dockerignore is missing pattern {pattern!r} ({description})"
    )


# ---------------------------------------------------------------------------
# Structural: verify script exists and is importable as a module
# ---------------------------------------------------------------------------

def test_verify_repo_hygiene_script_exists() -> None:
    script = _REPO_ROOT / "scripts" / "verify" / "verify_repo_hygiene.py"
    assert script.is_file(), "scripts/verify/verify_repo_hygiene.py does not exist"


def test_verify_repo_hygiene_script_is_valid_python() -> None:
    script = _REPO_ROOT / "scripts" / "verify" / "verify_repo_hygiene.py"
    result = subprocess.run(
        ["python", "-m", "py_compile", str(script)],
        capture_output=True,
    )
    assert result.returncode == 0, (
        f"verify_repo_hygiene.py has syntax errors:\n{result.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# .gitattributes: binary markers present
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("pattern,description", [
    ("*.dll binary",   "DLL binary marker"),
    ("*.lib binary",   "LIB binary marker"),
    ("*.pdf binary",   "PDF binary marker"),
    ("*.sqlite binary","SQLite binary marker"),
])
def test_gitattributes_binary_markers(pattern: str, description: str) -> None:
    text = (_REPO_ROOT / ".gitattributes").read_text(encoding="utf-8", errors="replace")
    assert pattern in text, (
        f".gitattributes is missing {pattern!r} ({description})"
    )
