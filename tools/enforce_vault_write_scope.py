"""Enforce vault-only staged changes for this repository.

Default policy:
- Read access can be repository-wide (outside scope of this hook).
- Write/commit access is restricted to `.obsidian/**` and `wiki/**`.

Override:
- Set ALLOW_NON_VAULT_CHANGES=1 to bypass this guard for explicitly
  authorized non-vault edits.
"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Iterable

ALLOWED_PREFIXES: tuple[str, ...] = (
    ".obsidian/",
    "wiki/",
)

# Minimal maintenance allowlist so policy files themselves can be updated.
MAINTENANCE_ALLOWLIST: set[str] = {
    ".gitignore",
    ".githooks/pre-commit",
    ".github/instructions/obsidian-vault-write-boundary.instructions.md",
    "AGENTS.md",
    "tools/enforce_vault_write_scope.py",
}


def _normalize(path: str) -> str:
    normalized = path.replace("\\", "/").strip()
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _get_staged_paths() -> list[str]:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--cached",
            "--name-only",
            "--diff-filter=ACMRD",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        print("[vault-guard] Failed to query staged files.", file=sys.stderr)
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        return []

    return [_normalize(line) for line in result.stdout.splitlines() if line.strip()]


def _is_allowed(path: str) -> bool:
    if path in MAINTENANCE_ALLOWLIST:
        return True
    return path.startswith(ALLOWED_PREFIXES)


def _collect_blocked_paths(paths: Iterable[str]) -> list[str]:
    return [path for path in paths if not _is_allowed(path)]


def main() -> int:
    if os.getenv("ALLOW_NON_VAULT_CHANGES", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
    }:
        print("[vault-guard] Override enabled: ALLOW_NON_VAULT_CHANGES set.")
        return 0

    staged_paths = _get_staged_paths()
    if not staged_paths:
        return 0

    blocked = _collect_blocked_paths(staged_paths)
    if not blocked:
        return 0

    print("[vault-guard] Commit blocked: non-vault paths are staged.")
    print("[vault-guard] Allowed by default: .obsidian/**, wiki/**")
    print("[vault-guard] Maintenance allowlist:")
    for item in sorted(MAINTENANCE_ALLOWLIST):
        print(f"  - {item}")

    print("[vault-guard] Blocked staged paths:")
    for path in blocked:
        print(f"  - {path}")

    print(
        "[vault-guard] If this edit is explicitly authorized, rerun commit with "
        "ALLOW_NON_VAULT_CHANGES=1."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
