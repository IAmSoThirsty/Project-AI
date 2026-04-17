#!/usr/bin/env python3
"""Shared local repository scan contract.

All repo database scans must gather local state in this order:

1. tracked paths
2. local and remote branch refs
3. untracked/ignored paths plus required .git metadata
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCAN_PHASES = ("tracked", "branches", "untracked-git")


@dataclass(frozen=True)
class RepoScanSnapshot:
    root: Path
    phases: tuple[str, ...]
    tracked: set[str]
    branches: list[dict[str, str]]
    untracked: set[str]
    ignored: set[str]
    head: str
    branch: str
    status_short: str
    status_lines: list[str]
    git_dir_raw: str
    git_dir_exists: bool
    git_metadata: dict[str, bool]
    branch_tree_survey: dict[str, Any] = field(default_factory=dict)


def run_git(
    root: Path, args: list[str], check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def git_text(root: Path, args: list[str], check: bool = True) -> str:
    return run_git(root, args, check=check).stdout


def git_lines(root: Path, args: list[str], check: bool = True) -> list[str]:
    return [line for line in git_text(root, args, check=check).splitlines() if line]


def git_z(root: Path, args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace')}"
        )
    return sorted(
        item.decode("utf-8", errors="replace")
        for item in result.stdout.split(b"\0")
        if item
    )


def branch_rows(root: Path) -> list[dict[str, str]]:
    fmt = "%(refname)%00%(refname:short)%00%(objectname:short)%00%(upstream:short)%00%(contents:subject)%00%(HEAD)"
    rows: list[dict[str, str]] = []
    for line in git_lines(
        root, ["for-each-ref", f"--format={fmt}", "refs/heads", "refs/remotes"]
    ):
        parts = line.split("\0")
        if len(parts) != 6:
            continue
        full_ref, short, commit, upstream, subject, head = parts
        if full_ref.endswith("/HEAD"):
            kind = "remote-head"
        elif full_ref.startswith("refs/remotes/"):
            kind = "remote"
        else:
            kind = "local"
        rows.append(
            {
                "kind": kind,
                "name": short,
                "commit": commit,
                "upstream": upstream,
                "subject": subject,
                "current": "yes" if head == "*" else "",
            }
        )
    return rows


def branch_tree_survey(
    root: Path,
    required_paths: set[str],
    branches: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    rows = branches if branches is not None else branch_rows(root)
    refs = [
        ref["name"]
        for ref in rows
        if ref["kind"] != "remote-head" and not ref["name"].endswith("/HEAD")
    ]
    missing_by_ref: list[dict[str, Any]] = []
    unreadable_refs: list[str] = []
    for ref in refs:
        result = run_git(root, ["ls-tree", "-r", "--name-only", ref], check=False)
        if result.returncode != 0:
            unreadable_refs.append(ref)
            continue
        tree_paths = set(result.stdout.splitlines())
        missing = sorted(required_paths - tree_paths)
        if missing:
            missing_by_ref.append({"ref": ref, "missing": missing})
    return {
        "refs": refs,
        "refs_count": len(refs),
        "missing_by_ref": missing_by_ref,
        "unreadable_refs": unreadable_refs,
    }


def git_metadata_state(root: Path) -> tuple[str, bool, dict[str, bool]]:
    git_dir_raw = git_text(root, ["rev-parse", "--git-dir"]).strip()
    git_dir = Path(git_dir_raw)
    if not git_dir.is_absolute():
        git_dir = root / git_dir
    metadata = {
        name: (git_dir / name).exists()
        for name in ("HEAD", "config", "index", "objects", "refs")
    }
    return git_dir_raw, git_dir.exists(), metadata


def collect_repo_scan(
    root: Path, branch_required_paths: set[str] | None = None
) -> RepoScanSnapshot:
    root = root.resolve()
    phases: list[str] = []

    tracked = set(git_z(root, ["ls-files", "-z"]))
    phases.append("tracked")

    branches = branch_rows(root)
    survey = (
        branch_tree_survey(root, branch_required_paths, branches=branches)
        if branch_required_paths
        else {"refs": [row["name"] for row in branches], "refs_count": len(branches)}
    )
    phases.append("branches")

    untracked = set(git_z(root, ["ls-files", "--others", "--exclude-standard", "-z"]))
    ignored = set(
        git_z(root, ["ls-files", "--others", "--ignored", "--exclude-standard", "-z"])
    )
    git_dir_raw, git_dir_exists, git_metadata = git_metadata_state(root)
    status_short = git_text(root, ["status", "--short", "--branch"]).rstrip()
    status_lines = git_text(root, ["status", "--porcelain=v1", "-uall"]).splitlines()
    head = git_text(root, ["rev-parse", "HEAD"]).strip()
    branch = git_text(root, ["branch", "--show-current"]).strip() or "(detached)"
    phases.append("untracked-git")

    return RepoScanSnapshot(
        root=root,
        phases=tuple(phases),
        tracked=tracked,
        branches=branches,
        untracked=untracked,
        ignored=ignored,
        head=head,
        branch=branch,
        status_short=status_short,
        status_lines=status_lines,
        git_dir_raw=git_dir_raw,
        git_dir_exists=git_dir_exists,
        git_metadata=git_metadata,
        branch_tree_survey=survey,
    )


def scan_phase_for_path(path: str, snapshot: RepoScanSnapshot) -> str:
    if path in snapshot.tracked:
        return "tracked"
    if path in snapshot.untracked or path in snapshot.ignored:
        return "untracked-git"
    return "untracked-git"


def scan_order_for_path(path: str, snapshot: RepoScanSnapshot) -> int:
    phase = scan_phase_for_path(path, snapshot)
    return SCAN_PHASES.index(phase)


def ordered_file_paths(local_paths: list[str], snapshot: RepoScanSnapshot) -> list[str]:
    all_paths = (
        set(local_paths) | snapshot.tracked | snapshot.untracked | snapshot.ignored
    )
    return sorted(
        all_paths,
        key=lambda path: (
            scan_order_for_path(path, snapshot),
            path.lower(),
        ),
    )
