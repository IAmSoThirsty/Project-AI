"""Read-only access helpers for the frozen Project-AI legacy repository."""

from __future__ import annotations

import hashlib
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_LEGACY_ROOT = Path(r"T:\00-Active\Project-AI-main")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


@dataclass(frozen=True)
class LegacySourceGuard:
    """Resolve legacy inputs while rejecting all legacy destinations."""

    root: Path = DEFAULT_LEGACY_ROOT

    def source(self, relative_path: str | Path) -> Path:
        """Return an existing source path contained by the legacy root."""
        candidate = (self.root / relative_path).resolve()
        if not _inside(candidate, self.root):
            raise ValueError(f"Legacy source escapes root: {relative_path}")
        if not candidate.exists():
            raise FileNotFoundError(candidate)
        return candidate

    def destination(self, path: str | Path) -> Path:
        """Return a destination only when it is outside the legacy root."""
        candidate = Path(path).resolve()
        if _inside(candidate, self.root):
            raise PermissionError(f"Writes to the legacy repository are forbidden: {candidate}")
        return candidate

    def git(self, *arguments: str) -> str:
        """Run a Git query that cannot mutate the legacy repository."""
        if not arguments or arguments[0] not in {
            "branch",
            "diff",
            "ls-files",
            "rev-list",
            "rev-parse",
            "show",
            "status",
        }:
            raise PermissionError(f"Legacy Git command is not read-only: {arguments!r}")
        result = subprocess.run(
            ["git", "-C", str(self.root), *arguments],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.stdout

    def snapshot(self) -> dict[str, Any]:
        """Capture branch, revision, and dirty-file evidence."""
        head = self.git("rev-parse", "HEAD").strip()
        branch = self.git("branch", "--show-current").strip()
        origin = self.git("rev-parse", "origin/master").strip()
        ahead_behind = self.git("rev-list", "--left-right", "--count", "origin/master...HEAD")
        behind, ahead = (int(value) for value in ahead_behind.split())
        status_lines = [line for line in self.git("status", "--porcelain=v1").splitlines() if line]
        dirty: list[dict[str, Any]] = []
        for line in status_lines:
            relative = line[3:]
            if " -> " in relative:
                relative = relative.split(" -> ", 1)[1]
            candidate = self.root / relative
            record: dict[str, Any] = {"path": relative, "status": line[:2]}
            if candidate.is_file():
                record["bytes"] = candidate.stat().st_size
                record["sha256"] = sha256(candidate)
            else:
                record["kind"] = "missing-or-directory"
            dirty.append(record)
        return {
            "ahead_of_origin": ahead,
            "behind_origin": behind,
            "branch": branch,
            "dirty": dirty,
            "head": head,
            "origin_master": origin,
            "root": str(self.root.resolve()),
        }


def configured_guard() -> LegacySourceGuard:
    """Build the guard from the optional legacy-root environment override."""
    return LegacySourceGuard(Path(os.environ.get("PROJECT_AI_LEGACY_REPO", DEFAULT_LEGACY_ROOT)))
