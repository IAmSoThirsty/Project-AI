"""
TAAR Change Detector — Git-aware file change detection.

Detects which files have changed since the last commit, last run, or
between arbitrary revisions. Supports both git-tracked changes and
untracked new files.
"""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ChangeSet:
    """A set of detected file changes."""

    modified: tuple[Path, ...]
    added: tuple[Path, ...]
    deleted: tuple[Path, ...]
    untracked: tuple[Path, ...]

    @property
    def all_changed(self) -> tuple[Path, ...]:
        """All files that exist and were modified or added."""
        return self.modified + self.added + self.untracked

    @property
    def is_empty(self) -> bool:
        """True if no changes were detected."""
        return not (self.modified or self.added or self.deleted or self.untracked)

    def __len__(self) -> int:
        return (
            len(self.modified)
            + len(self.added)
            + len(self.deleted)
            + len(self.untracked)
        )


def detect_uncommitted_changes(project_root: Path) -> ChangeSet:
    """
    Detect all uncommitted changes in the working tree.

    Combines staged, unstaged, and untracked files into a unified ChangeSet.
    This is the primary detection mode for `taar run`.
    """
    modified = []
    added = []
    deleted = []
    untracked = []

    # Staged changes
    staged = _git(project_root, ["diff", "--cached", "--name-status"])
    for line in staged:
        status, path = _parse_status_line(line)
        resolved = project_root / path
        if status == "M":
            modified.append(resolved)
        elif status == "A":
            added.append(resolved)
        elif status == "D":
            deleted.append(resolved)

    # Unstaged changes
    unstaged = _git(project_root, ["diff", "--name-status"])
    for line in unstaged:
        status, path = _parse_status_line(line)
        resolved = project_root / path
        if status == "M" and resolved not in modified:
            modified.append(resolved)
        elif status == "A" and resolved not in added:
            added.append(resolved)
        elif status == "D" and resolved not in deleted:
            deleted.append(resolved)

    # Untracked files
    untracked_output = _git(
        project_root, ["ls-files", "--others", "--exclude-standard"]
    )
    for line in untracked_output:
        path = project_root / line.strip()
        if path not in added:
            untracked.append(path)

    return ChangeSet(
        modified=tuple(modified),
        added=tuple(added),
        deleted=tuple(deleted),
        untracked=tuple(untracked),
    )


def detect_changes_since(project_root: Path, revision: str = "HEAD~1") -> ChangeSet:
    """
    Detect changes between a revision and the working tree.

    Useful for CI mode: `taar ci` can detect changes since the merge base.
    """
    modified = []
    added = []
    deleted = []

    output = _git(project_root, ["diff", "--name-status", revision])
    for line in output:
        status, path = _parse_status_line(line)
        resolved = project_root / path
        if status == "M":
            modified.append(resolved)
        elif status == "A":
            added.append(resolved)
        elif status == "D":
            deleted.append(resolved)

    return ChangeSet(
        modified=tuple(modified),
        added=tuple(added),
        deleted=tuple(deleted),
        untracked=(),
    )


def file_content_hash(path: Path) -> str:
    """Compute SHA-256 hash of a file's content."""
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (OSError, FileNotFoundError):
        return "MISSING"


def _git(cwd: Path, args: list[str]) -> list[str]:
    """Run a git command and return output lines."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        if result.returncode != 0:
            return []
        return [line for line in result.stdout.strip().split("\n") if line.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def _parse_status_line(line: str) -> tuple[str, str]:
    """Parse a git status line like 'M\tsrc/foo.py' into (status, path)."""
    parts = line.strip().split(maxsplit=1)
    if len(parts) == 2:
        return parts[0][0], parts[1]  # First char of status, full path
    return "?", line.strip()
