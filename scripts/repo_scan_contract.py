from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "SCAN_PHASES",
    "RepoScanSnapshot",
    "collect_repo_scan",
    "ordered_file_paths",
    "scan_phase_for_path",
    "scan_order_for_path",
]

# Priority order: tracked → untracked → ignored → anything else local.
SCAN_PHASES: tuple[str, ...] = (
    "tracked",
    "untracked",
    "ignored",
    "local-unclassified",
)


@dataclass
class RepoScanSnapshot:
    phases: tuple[str, ...]
    branch: str
    head: str
    status_short: str
    status_lines: list[str]
    tracked: set[str]
    untracked: set[str]
    ignored: set[str]
    branches: list[dict[str, str]]
    branch_tree_survey: dict[str, object]


# ── internal helpers ──────────────────────────────────────────────────────────

def _git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return result.stdout


def _path_set(raw: str) -> set[str]:
    return {line.replace("\\", "/") for line in raw.splitlines() if line.strip()}


# ── public API ────────────────────────────────────────────────────────────────

def collect_repo_scan(
    project_root: Path,
    branch_required_paths: set[str] | None = None,
) -> RepoScanSnapshot:
    root = Path(project_root)

    tracked = _path_set(_git(["ls-files"], root))
    untracked = _path_set(
        _git(["ls-files", "--others", "--exclude-standard"], root)
    )
    ignored = _path_set(
        _git(["ls-files", "--others", "--ignored", "--exclude-standard"], root)
    )

    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], root).strip() or "HEAD"
    head = _git(["rev-parse", "HEAD"], root).strip() or ""

    status_raw = _git(["status", "--short", "--porcelain"], root)
    status_lines = [line for line in status_raw.splitlines() if line]
    status_short = "\n".join(status_lines)

    # Branch list: local heads + remote refs, one record per ref.
    fmt = (
        "%(refname)\t%(refname:short)\t%(objectname:short)"
        "\t%(subject)\t%(upstream:short)\t%(HEAD)"
    )
    branch_raw = _git(
        ["for-each-ref", "--format", fmt, "refs/heads/", "refs/remotes/"],
        root,
    )
    branches: list[dict[str, str]] = []
    for line in branch_raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 5)
        if len(parts) < 6:
            parts += [""] * (6 - len(parts))
        full_ref, short_name, commit, subject, upstream, current_marker = parts
        if full_ref.startswith("refs/remotes/"):
            kind = "remote-head" if short_name.endswith("/HEAD") else "remote"
        else:
            kind = "local"
        branches.append(
            {
                "kind": kind,
                "name": short_name,
                "commit": commit,
                "subject": subject,
                "upstream": upstream,
                "current": "*" if current_marker.strip() == "*" else "",
            }
        )

    # Count all refs so callers can assert refs_count >= 1.
    refs_raw = _git(["for-each-ref", "--format", "%(refname)"], root)
    refs_count = len([ln for ln in refs_raw.splitlines() if ln.strip()])
    branch_tree_survey: dict[str, object] = {"refs_count": refs_count}

    return RepoScanSnapshot(
        phases=SCAN_PHASES,
        branch=branch,
        head=head,
        status_short=status_short,
        status_lines=status_lines,
        tracked=tracked,
        untracked=untracked,
        ignored=ignored,
        branches=branches,
        branch_tree_survey=branch_tree_survey,
    )


def scan_phase_for_path(path: str, snapshot: RepoScanSnapshot) -> str:
    norm = path.replace("\\", "/")
    if norm in snapshot.tracked:
        return "tracked"
    if norm in snapshot.untracked:
        return "untracked"
    if norm in snapshot.ignored:
        return "ignored"
    return "local-unclassified"


def scan_order_for_path(path: str, snapshot: RepoScanSnapshot) -> int:
    phase = scan_phase_for_path(path, snapshot)
    try:
        return SCAN_PHASES.index(phase)
    except ValueError:
        return len(SCAN_PHASES)


def ordered_file_paths(
    file_list: list[str], snapshot: RepoScanSnapshot
) -> list[str]:
    def sort_key(path: str) -> tuple[int, str]:
        return (scan_order_for_path(path, snapshot), path.lower())

    return sorted(file_list, key=sort_key)
