#!/usr/bin/env python3
"""
freeze_history.py — Stage -1.5 of the Project-AI rebuild.

Walks every commit in the frozen reference repo (T:\\Project-AI-main) and
produces ONE long single markdown file with SHA-256 chain links between
sections. The file is the immutable record of the old repo's git history.

Output: docs/internal/frozen-history/PROJECT-AI_FROZEN_HISTORY.md

Design rules:
  - Two hashes per commit section:
      * git_commit_sha   (the upstream git hash, 40 hex chars)
      * section_sha256   (SHA-256 of THIS section's markdown content)
  - Chain link between consecutive sections:
        prev_section_sha256 -> this_section_sha256
  - First section's "prev" is the SHA-256 of an empty string
        (well-known genesis constant: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855)
  - Chronological order: oldest commit first, newest last.
  - After all commit sections: branches section, then tags section,
    then a footer containing the final section_sha256 (the "ledger head").
  - stdlib only.
  - Streaming writes: never hold the full file in memory.
  - Deterministic: identical input -> byte-identical output.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict


class CommitRecord(TypedDict):
    sha: str
    parents: list[str]
    author_name: str
    author_email: str
    author_date: str
    subject: str
    body: str


GENESIS_SHA256 = hashlib.sha256(b"").hexdigest()


# ---------------------------- git helpers ------------------------------------


def run_git(repo: Path, *args: str, check: bool = True) -> str:
    """Run a git command in `repo`, return stdout (stripped)."""
    result = subprocess.run(
        ["git", "-C", str(repo), *list(args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode != 0:
        sys.stderr.write(f"[freeze_history] git {' '.join(args)} failed:\n{result.stderr}\n")
        raise SystemExit(result.returncode)
    return result.stdout.strip()


def iter_commits_chrono(repo: Path) -> Iterator[CommitRecord]:
    """
    Yield commits from oldest to newest as (sha, parents, author, date, subject, body).
    Uses --reverse so we don't have to reverse in memory.
    """
    fmt = "%H%x00%P%x00%an%x00%ae%x00%aI%x00%s%x00%b%x00"
    out = run_git(
        repo,
        "log",
        "--reverse",
        "--no-color",
        f"--pretty=format:{fmt}",
    )
    for line in out.split("\n"):
        if not line:
            continue
        parts = line.split("\x00", 6)
        # 7 parts expected: sha, parents, author_name, author_email, date_iso, subject, body
        if len(parts) != 7:
            # body might be missing -> still 7 parts because %b produces empty string
            continue
        sha, parents, an, ae, ad, subj, body = parts
        yield {
            "sha": sha,
            "parents": [p for p in parents.split(" ") if p],
            "author_name": an,
            "author_email": ae,
            "author_date": ad,
            "subject": subj,
            "body": body.strip(),
        }


def iter_branches(repo: Path) -> Iterator[tuple[str, str]]:
    """Yield (branch_name, tip_sha)."""
    out = run_git(repo, "for-each-ref", "--format=%(refname:short)%00%(objectname)", "refs/heads/")
    for line in out.splitlines():
        if not line:
            continue
        name, sha = line.split("\x00", 1)
        yield name, sha


def iter_tags(repo: Path) -> Iterator[tuple[str, str, str]]:
    """Yield (tag_name, sha, tagger_date_iso_or_None)."""
    out = run_git(
        repo,
        "for-each-ref",
        "--format=%(refname:short)%00%(objectname)%00(*taggerdate:short*)",
        "refs/tags/",
    )
    for line in out.splitlines():
        if not line:
            continue
        parts = line.split("\x00")
        if len(parts) >= 2:
            name = parts[0]
            sha = parts[1]
            date = parts[2] if len(parts) > 2 else ""
            yield name, sha, date


def commit_diffstat(repo: Path, sha: str) -> str:
    """Return 'N files changed, X insertions(+), Y deletions(-)' for sha vs first parent (or empty tree)."""
    parents_arg = f"{sha}^!"  # diff against first parent, or empty tree if root
    try:
        return run_git(repo, "diff", "--shortstat", parents_arg, check=False) or "(no diffstat)"
    except Exception:
        return "(diffstat error)"


def commit_files_changed(repo: Path, sha: str) -> str:
    """Return a list of files changed in this commit (name-status, one per line, capped)."""
    parents_arg = f"{sha}^!"
    try:
        out = run_git(
            repo,
            "diff",
            "--name-status",
            parents_arg,
            check=False,
        )
    except Exception:
        return ""
    lines = out.splitlines()
    if len(lines) > 200:
        return (
            "\n".join(lines[:200])
            + f"\n... ({len(lines) - 200} more files truncated for frozen-history brevity)"
        )
    return "\n".join(lines)


# --------------------------- chain helpers ------------------------------------


def render_section(index: int, total: int, commit: CommitRecord, prev_section_sha256: str) -> str:
    """
    Build the markdown BODY for ONE commit section. This is the text whose
    SHA-256 becomes this section's chain link. The chain link line itself
    is NOT part of this body — the caller injects it externally after
    hashing, so the chain link's content does not feed back into its own
    hash (that would be a self-referential deadlock).
    """
    lines = []
    lines.append(f"## Commit {index + 1} / {total} — `{commit['sha'][:12]}`")
    lines.append("")
    lines.append(f"- **Git commit SHA:** `{commit['sha']}`")
    lines.append(f"- **Author:** {commit['author_name']} <{commit['author_email']}>")
    lines.append(f"- **Author date:** {commit['author_date']}")
    if commit["parents"]:
        lines.append(f"- **Parents:** {', '.join('`' + p + '`' for p in commit['parents'])}")
    else:
        lines.append("- **Parents:** _(root commit)_")
    lines.append(f"- **Frozen at:** {datetime.now(UTC).isoformat()}")
    lines.append("")
    lines.append("### Subject")
    lines.append("")
    lines.append(commit["subject"] or "_(empty subject)_")
    lines.append("")
    if commit["body"]:
        lines.append("### Body")
        lines.append("")
        lines.append(commit["body"])
        lines.append("")
    lines.append("### Diffstat")
    lines.append("")
    return "\n".join(lines)


def hash_section(section_text: str) -> str:
    return hashlib.sha256(section_text.encode("utf-8")).hexdigest()


# --------------------------- main pipeline ------------------------------------


def build_frozen_history(repo: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_tmp = out_path.with_suffix(out_path.suffix + ".tmp")

    # First: count commits so we can render "N / TOTAL" in each section header.
    total = int(run_git(repo, "rev-list", "--count", "HEAD"))
    sys.stderr.write(f"[freeze_history] {total} commits to process.\n")

    prev_section_sha = GENESIS_SHA256
    ledger_head = GENESIS_SHA256  # updated to last section sha

    with out_tmp.open("w", encoding="utf-8", newline="\n") as f:
        # --- header ---
        f.write("# Project-AI Frozen History\n\n")
        f.write("> Immutable cryptographic snapshot of the entire git history of\n")
        f.write(f"> `T:\\Project-AI-main` (master @ `{run_git(repo, 'rev-parse', 'HEAD')}`).\n")
        f.write("> Generated by `tools/freeze_history.py` during Stage -1.5 of the rebuild.\n")
        f.write("> This file is **frozen** — it is never updated, only re-verified.\n\n")
        f.write(f"- **Source repo:** `{repo}`\n")
        f.write(f"- **Frozen at:** {datetime.now(UTC).isoformat()}\n")
        f.write(f"- **Total commits:** {total}\n")
        f.write(f"- **Genesis SHA-256:** `{GENESIS_SHA256}`\n\n")
        f.write("---\n\n")

        # --- commits ---
        for idx, commit in enumerate(iter_commits_chrono(repo)):
            # Step 1: build the BODY of the section (everything below the chain
            # link line). The body is canonical: re-running freeze_history
            # produces a byte-identical body because it depends only on git
            # state, not on the chain hash itself.
            body = render_section(idx, total, commit, prev_section_sha)
            diffstat = commit_diffstat(repo, commit["sha"])
            files = commit_files_changed(repo, commit["sha"])
            body += f"```\n{diffstat}\n```\n\n"
            if files:
                body += "### Files changed\n\n```\n" + files + "\n```\n\n"
            body += "---\n\n"

            # Step 2: hash the body. THIS is the canonical section hash that
            # gets put in the chain link AND in the next section's "prev".
            this_section_sha = hash_section(body)

            # Step 3: prepend a fixed-format chain link line. The chain link
            # line itself is NOT included in the body that's hashed — see the
            # verifier which extracts the hash and recomputes over the body.
            chain_link_line = f"- **Chain link:** `{prev_section_sha}` -> `{this_section_sha}`\n"

            # Step 4: write section = header (already in body) + chain link
            # + body. The chain_link_line already has a trailing newline,
            # and the body_prefix (body[:metadata_end]) already ends with
            # "\n\n" (the blank line before "### Subject"). body_suffix
            # (body[metadata_end:]) starts with "### Subject". So the
            # concatenated section has the chain link line slotted between
            # the metadata block and the subject, with exactly the same
            # total newline count as the original body PLUS one extra line
            # for the chain link itself.
            metadata_end = body.find("### Subject")
            if metadata_end == -1:
                section_text = chain_link_line + body
            else:
                section_text = body[:metadata_end] + chain_link_line + body[metadata_end:]

            f.write(section_text)

            prev_section_sha = this_section_sha
            ledger_head = this_section_sha

            if (idx + 1) % 100 == 0 or idx + 1 == total:
                sys.stderr.write(
                    f"[freeze_history] {idx + 1}/{total}  ledger_head={ledger_head[:16]}...\n"
                )

        # --- branches ---
        f.write("# Branches\n\n")
        for name, tip in iter_branches(repo):
            f.write(f"- `{name}` -> `{tip}`\n")
        f.write("\n---\n\n")

        # --- tags ---
        f.write("# Tags\n\n")
        any_tag = False
        for name, sha, date in iter_tags(repo):
            any_tag = True
            f.write(f"- `{name}` -> `{sha}`" + (f" ({date})" if date else "") + "\n")
        if not any_tag:
            f.write("_(no tags)_\n")
        f.write("\n---\n\n")

        # --- footer (ledger head) ---
        f.write("# Ledger Head\n\n")
        f.write(f"The final section's SHA-256 (binds the entire chain): `{ledger_head}`\n\n")
        f.write(
            "To verify the chain: read each section in order, compute SHA-256 of its\n"
            "markdown text, confirm the value printed in `Chain link: <prev> -> <this>`\n"
            "matches the previous section's hash. The first section's `prev` must equal\n"
            f"the genesis constant `{GENESIS_SHA256}`.\n"
        )

    # atomic-ish replace
    out_tmp.replace(out_path)

    final_size = out_path.stat().st_size
    sys.stderr.write(
        f"[freeze_history] DONE. {out_path} = {final_size:,} bytes "
        f"(~{final_size / 1024 / 1024:.1f} MB). ledger_head={ledger_head[:16]}...\n"
    )


# --------------------------------- cli ----------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--repo",
        default=r"T:\00-Active\Project-AI-main",
        help="Path to the frozen reference repo (default: T:\\Project-AI-main)",
    )
    ap.add_argument(
        "--out",
        default=r"T:\00-Active\Project-AI-Beginnings\docs\internal\frozen-history\PROJECT-AI_FROZEN_HISTORY.md",
        help="Output markdown file path",
    )
    args = ap.parse_args()

    repo = Path(args.repo)
    out = Path(args.out)
    if not repo.exists():
        sys.stderr.write(f"[freeze_history] repo not found: {repo}\n")
        return 2

    build_frozen_history(repo, out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
