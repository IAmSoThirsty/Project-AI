#!/usr/bin/env python3
"""Verify that the .venv entry-point launchers work on Windows.

Context (2026-07-11): launcher exes written by uv 0.11.22 failed on this host
with "uv trampoline failed to canonicalize script path", breaking every
`uv run <tool>` except native binaries (ruff) and `uv run python`. Healthy and
broken launchers are byte-size-identical (46,080 bytes), so the only reliable
check is functional: run each canary exe with --version. Regenerating the
launchers with a newer uv fixes the condition:

    uv sync --frozen --all-extras --all-packages --reinstall

If that reinstall fails with "Access is denied" on ruff.exe, an IDE ruff
server is holding it: rename ruff.exe aside (rename is allowed while running),
rerun the sync, then stop the stale process and delete the renamed file.

No-op success on non-Windows: POSIX entry points are scripts, not trampolines.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO / ".venv" / "Scripts"
PYVENV_CFG = REPO / ".venv" / "pyvenv.cfg"

# Entry-point launchers exercised by the acceptance gate and CLAUDE.md commands.
CANARY_TOOLS: tuple[str, ...] = ("pytest", "mypy", "pre-commit")

REMEDIATION = "uv sync --frozen --all-extras --all-packages --reinstall"


def _venv_uv_version() -> str:
    """Return the uv version recorded in pyvenv.cfg, or 'unknown'."""
    try:
        for line in PYVENV_CFG.read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition("=")
            if key.strip() == "uv":
                return value.strip()
    except OSError:
        pass
    return "unknown"


def _check_canary(tool: str) -> tuple[bool, str]:
    """Run one canary exe with --version; return (passed, detail)."""
    exe = SCRIPTS_DIR / f"{tool}.exe"
    if not exe.exists():
        return False, f"{exe} missing (venv not synced?)"
    try:
        result = subprocess.run(
            [str(exe), "--version"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"{tool}.exe failed to launch: {exc}"
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()
        first = detail[0] if detail else f"exit {result.returncode}"
        return False, f"{tool}.exe exit {result.returncode}: {first}"
    return True, (result.stdout or result.stderr).strip().splitlines()[0]


def main() -> int:
    if sys.platform != "win32":
        print("venv_trampolines: SKIP (non-Windows; entry points are scripts)")
        return 0

    print(f"venv created by uv {_venv_uv_version()}")
    failures: list[str] = []
    for tool in CANARY_TOOLS:
        passed, detail = _check_canary(tool)
        print(f"{tool}: {'PASS' if passed else 'FAIL'} ({detail})")
        if not passed:
            failures.append(tool)

    if failures:
        print(
            f"\n{len(failures)} launcher(s) broken ({', '.join(failures)}). "
            f"Regenerate them with:\n  {REMEDIATION}\n"
            "If ruff.exe is locked by an IDE server, rename it aside first "
            "(see this script's docstring)."
        )
        return 1

    print("all venv entry-point launchers healthy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
