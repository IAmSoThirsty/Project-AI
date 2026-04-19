#!/usr/bin/env python3
"""Block non-doc commits on public docs-only branches.

This hook is intentionally conservative and only activates on configured branch names.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import PurePosixPath

DOCS_ONLY_BRANCHES = {
    "github/verified-poc-face",
}

# Allowlist for docs-only branch commits.
# Keep this explicit so policy remains tight.
ALLOWED_PREFIXES = (
    "wiki/",
    "docs/",
    ".github/ISSUE_TEMPLATE/",
)

ALLOWED_EXACT = {
    "README.md",
    ".github/pull_request_template.md",
}


def _run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _branch_name() -> str:
    return _run_git("branch", "--show-current")


def _staged_files() -> list[str]:
    out = _run_git("diff", "--cached", "--name-only")
    if not out:
        return []
    return [line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()]


def _is_allowed(path: str) -> bool:
    normalized = PurePosixPath(path).as_posix()
    if normalized in ALLOWED_EXACT:
        return True
    return any(normalized.startswith(prefix) for prefix in ALLOWED_PREFIXES)


def main() -> int:
    try:
        branch = _branch_name()
    except Exception as exc:  # pragma: no cover - git env specific
        print(f"[docs-only-guard] unable to determine branch: {exc}")
        return 0

    if branch not in DOCS_ONLY_BRANCHES:
        return 0

    try:
        staged = _staged_files()
    except Exception as exc:  # pragma: no cover - git env specific
        print(f"[docs-only-guard] unable to inspect staged files: {exc}")
        return 1

    blocked = [p for p in staged if not _is_allowed(p)]
    if not blocked:
        return 0

    print("\n[docs-only-guard] commit blocked on docs-only branch:")
    print(f"  branch: {branch}")
    print("  non-doc paths detected:")
    for path in blocked:
        print(f"    - {path}")

    print("\nAllowed paths are limited to:")
    for prefix in ALLOWED_PREFIXES:
        print(f"  - {prefix}*")
    for exact in sorted(ALLOWED_EXACT):
        print(f"  - {exact}")

    print("\nSwitch to 'main' for code/infrastructure changes.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
