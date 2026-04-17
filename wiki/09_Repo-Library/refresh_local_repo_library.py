"""Build the local-first repository library inside the Obsidian wiki."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve()
LIB = SCRIPT.parent
WIKI = LIB.parent
ROOT = WIKI.parent
IGNORED_SHARDS = LIB / "Ignored-Files"

GENERATED = {
    "wiki/09_Repo-Library/Local-Repo-Library.md",
    "wiki/09_Repo-Library/Local-Git-State.md",
    "wiki/09_Repo-Library/Local-Working-Tree.md",
    "wiki/09_Repo-Library/Local-Folder-Library.md",
    "wiki/09_Repo-Library/Local-File-Library.md",
    "wiki/09_Repo-Library/Ignored-File-Library.md",
    "wiki/09_Repo-Library/local_file_manifest.jsonl",
    "wiki/09_Repo-Library/local_folder_manifest.jsonl",
    "wiki/09_Repo-Library/ignored_file_manifest.jsonl",
}

MAX_HASH_BYTES = 100 * 1024 * 1024
IGNORED_SHARD_SIZE = 2000


def run_git(args: list[str], check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def run_git_z(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace')}")
    return sorted(x.decode("utf-8", errors="replace") for x in result.stdout.split(b"\0") if x)


def repo_rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def git_status_map(lines: list[str]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for line in lines:
        if not line:
            continue
        code = line[:2]
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        path = path.strip('"').replace("\\", "/")
        result[path] = {"code": code, "index": code[0], "worktree": code[1]}
    return result


def local_files() -> list[str]:
    files: list[str] = []
    for path in ROOT.rglob("*"):
        if ".git" in path.relative_to(ROOT).parts:
            continue
        if path.is_file():
            files.append(repo_rel(path))
    return sorted(files)


def branch_rows() -> list[dict[str, str]]:
    fmt = "%(refname)%00%(refname:short)%00%(objectname:short)%00%(upstream:short)%00%(contents:subject)%00%(HEAD)"
    rows: list[dict[str, str]] = []
    for line in run_git(["for-each-ref", f"--format={fmt}", "refs/heads", "refs/remotes"]).splitlines():
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


def ignored_details(paths: list[str]) -> dict[str, dict[str, str]]:
    if not paths:
        return {}
    payload = ("\0".join(paths) + "\0").encode("utf-8")
    result = subprocess.run(
        ["git", "check-ignore", "-v", "-z", "--stdin"],
        cwd=ROOT,
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    parts = [p.decode("utf-8", errors="replace") for p in result.stdout.split(b"\0") if p]
    details: dict[str, dict[str, str]] = {}
    for index in range(0, len(parts), 4):
        if index + 3 >= len(parts):
            continue
        source, line, pattern, path = parts[index : index + 4]
        details[path] = {"ignore_source": source, "ignore_line": line, "ignore_pattern": pattern}
    return details


def top_root(rel: str) -> str:
    parts = Path(rel).parts
    return parts[0] if parts else "."


def ext_name(rel: str) -> str:
    suffix = Path(rel).suffix.lower()
    return suffix if suffix else "(none)"


def path_category(rel: str) -> str:
    p = rel.replace("\\", "/")
    lower = p.lower()
    suffix = Path(p).suffix.lower()
    if any(part in lower for part in ["/__pycache__/", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".gradle/"]):
        return "cache"
    if lower.startswith((".venv/", ".venv_airllm/", "venv/", "node_modules/")):
        return "dependency-environment"
    if lower.endswith(".env") or lower == ".env" or ".env." in lower:
        return "local-environment"
    if lower.endswith((".log", ".lock")):
        return "runtime-log-or-lock"
    if lower.startswith(("audit_reports/", "test-artifacts/", "ci-reports/")):
        return "generated-report"
    if lower.startswith("unity/") and any(part in lower for part in ["/library/", "/temp/", "/obj/", "/build/", "/logs/"]):
        return "unity-generated"
    if suffix in {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".kt", ".go", ".rs", ".c", ".h", ".cpp", ".cs", ".sh", ".ps1"}:
        return "code"
    if suffix in {".md", ".rst", ".txt"}:
        return "doc"
    if suffix in {".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".xml", ".csv", ".db"}:
        return "data"
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".exe", ".bin", ".class", ".pyc", ".jar"}:
        return "binary-or-build-artifact"
    return "repo-file"


def ignore_reason(rel: str, detail: dict[str, str] | None) -> str:
    if not detail:
        return "Ignored by Git, but no verbose rule was returned."
    pattern = detail.get("ignore_pattern", "")
    source = detail.get("ignore_source", "")
    line = detail.get("ignore_line", "")
    lower = f"{rel} {pattern}".lower()
    if "__pycache__" in lower or "*.pyc" in lower:
        reason = "Python bytecode cache."
    elif ".venv" in lower or "venv/" in lower:
        reason = "Local Python virtual environment or installed dependency tree."
    elif "node_modules" in lower:
        reason = "Local Node dependency tree."
    elif ".env" in lower:
        reason = "Local environment or secret-bearing configuration."
    elif ".gradle" in lower:
        reason = "Local Gradle cache/build state."
    elif ".pytest_cache" in lower or ".mypy_cache" in lower or ".ruff_cache" in lower:
        reason = "Local tool cache."
    elif "audit_reports" in lower or "test_audit" in lower:
        reason = "Generated audit/test output."
    elif "wiki/_scribe/project-ai" in lower:
        reason = "Personal scribe runtime data."
    elif "data/personal_agent" in lower:
        reason = "Personal agent runtime data."
    elif "unity/" in lower:
        reason = "Unity generated/cache/build artifact."
    elif "*.log" in lower or lower.endswith(".log"):
        reason = "Runtime log."
    elif "*.key" in lower or "cosign.key" in lower:
        reason = "Security key material."
    elif "*.exe" in lower or lower.endswith(".exe"):
        reason = "Local binary/installer artifact."
    elif ".coverage" in lower:
        reason = "Coverage output."
    else:
        reason = "Matched a repository ignore rule."
    return f"{reason} Rule: `{source}:{line}` pattern `{pattern}`."


def sha256(path: Path, rel: str, git_state: str) -> tuple[str | None, str]:
    if rel in GENERATED or rel.startswith("wiki/09_Repo-Library/Ignored-Files/"):
        return None, "generated_output"
    if git_state == "ignored":
        return None, "skipped_ignored"
    if not path.is_file():
        return None, "not_file"
    size = path.stat().st_size
    if size > MAX_HASH_BYTES:
        return None, "skipped_large_file"
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest(), "ok"


def file_record(
    rel: str,
    tracked: set[str],
    untracked: set[str],
    ignored: set[str],
    details: dict[str, dict[str, str]],
    statuses: dict[str, dict[str, str]],
    generated_at: str,
) -> dict[str, object]:
    path = ROOT / rel
    if rel in tracked:
        git_state = "tracked"
        reason = "Tracked by git."
    elif rel in untracked:
        git_state = "untracked"
        reason = "Present in local filesystem, not tracked by git, and not matched by ignore rules."
    elif rel in ignored:
        git_state = "ignored"
        reason = ignore_reason(rel, details.get(rel))
    else:
        git_state = "local-unclassified"
        reason = "Present on local filesystem but not returned by git tracked, untracked, or ignored queries."
    stat = path.stat()
    digest, digest_status = sha256(path, rel, git_state)
    detail = details.get(rel, {})
    return {
        "relative_path": rel,
        "absolute_path": str(path),
        "name": path.name,
        "extension": ext_name(rel),
        "top_root": top_root(rel),
        "category": path_category(rel),
        "git_state": git_state,
        "git_status": statuses.get(rel, {"code": "", "index": "", "worktree": ""}),
        "ignore_source": detail.get("ignore_source", ""),
        "ignore_line": detail.get("ignore_line", ""),
        "ignore_pattern": detail.get("ignore_pattern", ""),
        "why_untracked_or_ignored": reason,
        "size_bytes": None if rel in GENERATED else stat.st_size,
        "modified_at": generated_at
        if rel in GENERATED
        else datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds"),
        "sha256": digest,
        "sha256_status": digest_status,
    }


def folder_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    folders: dict[str, dict[str, object]] = {}

    def ensure(folder: str) -> dict[str, object]:
        if folder not in folders:
            folders[folder] = {
                "relative_path": folder,
                "tracked_files": 0,
                "untracked_files": 0,
                "ignored_files": 0,
                "local_unclassified_files": 0,
                "total_files": 0,
                "direct_files": 0,
                "subfolders": set(),
            }
        return folders[folder]

    ensure("")
    for record in records:
        rel = str(record["relative_path"])
        parts = Path(rel).parts
        parent = ""
        for idx, _part in enumerate(parts[:-1]):
            folder = "/".join(parts[: idx + 1])
            ensure(parent)["subfolders"].add(folder)
            ensure(folder)
            parent = folder
        ensure(parent)["direct_files"] += 1
        for idx in range(len(parts)):
            folder = "/".join(parts[:idx])
            item = ensure(folder)
            item["total_files"] += 1
            key = {
                "tracked": "tracked_files",
                "untracked": "untracked_files",
                "ignored": "ignored_files",
                "local-unclassified": "local_unclassified_files",
            }.get(str(record["git_state"]), "local_unclassified_files")
            item[key] += 1

    out: list[dict[str, object]] = []
    for folder, record in sorted(folders.items(), key=lambda item: item[0].lower()):
        clean = dict(record)
        clean["subfolders"] = sorted(record["subfolders"])
        clean["depth"] = 0 if folder == "" else len(Path(folder).parts)
        out.append(clean)
    return out


def md_escape(value: object) -> str:
    text = str(value).replace("\n", " ")
    return text.replace("|", "\\|")


def table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(md_escape(cell) for cell in row) + " |")
    return "\n".join(lines)


def bullets(counter: Counter[str], limit: int = 60) -> str:
    if not counter:
        return "- None"
    return "\n".join(f"- `{key}`: {count}" for key, count in counter.most_common(limit))


def shard_name(root: str, index: int) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", root).strip("-") or "root"
    safe = safe.replace(".", "dot-")
    return f"Ignored-{safe}-{index:03d}.md"


def ignored_shards(ignored_records: list[dict[str, object]], generated_at: str) -> list[str]:
    IGNORED_SHARDS.mkdir(parents=True, exist_ok=True)
    root_resolved = IGNORED_SHARDS.resolve()
    if not str(root_resolved).startswith(str(LIB.resolve())):
        raise RuntimeError(f"Refusing to clean unexpected path: {root_resolved}")
    for old in IGNORED_SHARDS.glob("Ignored-*.md"):
        old.unlink()

    shards: list[str] = []
    by_root: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in ignored_records:
        by_root[str(record["top_root"])].append(record)

    for root, records in sorted(by_root.items()):
        records = sorted(records, key=lambda item: str(item["relative_path"]).lower())
        for idx in range(0, len(records), IGNORED_SHARD_SIZE):
            chunk = records[idx : idx + IGNORED_SHARD_SIZE]
            page_index = idx // IGNORED_SHARD_SIZE + 1
            name = shard_name(root, page_index)
            rel = f"Ignored-Files/{name}"
            rows = [
                [
                    f"`{item['relative_path']}`",
                    item["category"],
                    item["ignore_source"],
                    item["ignore_line"],
                    f"`{item['ignore_pattern']}`",
                    item["why_untracked_or_ignored"],
                ]
                for item in chunk
            ]
            write_text(
                IGNORED_SHARDS / name,
                f"""---
agent: local-repo-library
generated_at: {generated_at}
source: ignored-files
root: {root}
---

# Ignored Files: {root} {page_index:03d}

This shard lists ignored local files and why git does not track them.

## Navigation

- [[Ignored-File-Library]]
- [[Local-Repo-Library]]

## Files

{table(["Path", "Category", "Ignore Source", "Line", "Pattern", "Why"], rows)}
""",
            )
            shards.append(rel)
    return shards


def link_health() -> tuple[int, int, int, int]:
    files = [p for p in WIKI.rglob("*") if p.is_file()]
    notes = [p for p in files if p.suffix.lower() in {".md", ".canvas"}]
    existing = {p.relative_to(WIKI).as_posix() for p in files}
    by_stem: dict[str, list[str]] = defaultdict(list)
    by_name: dict[str, list[str]] = defaultdict(list)
    for p in files:
        rel = p.relative_to(WIKI).as_posix()
        by_stem[p.stem].append(rel)
        by_name[p.name].append(rel)
    inbound: dict[str, set[str]] = defaultdict(set)
    unresolved = 0
    for note in notes:
        src = note.relative_to(WIKI).as_posix()
        text = note.read_text(encoding="utf-8", errors="ignore")
        for raw in re.findall(r"!?\[\[([^\]]+)\]\]", text):
            target = raw.split("|", 1)[0].split("#", 1)[0].strip()
            if not target:
                continue
            norm = target.replace("\\", "/")
            resolved = set(by_stem.get(target, []))
            resolved.update(by_name.get(target, []))
            for candidate in (norm, f"{norm}.md", f"{norm}.canvas"):
                if candidate in existing:
                    resolved.add(candidate)
            if resolved:
                for dst in resolved:
                    inbound[dst].add(src)
            else:
                unresolved += 1
    orphans = 0
    for note in notes:
        rel = note.relative_to(WIKI).as_posix()
        if rel.startswith(".obsidian/"):
            continue
        if rel not in inbound:
            orphans += 1
    return len(files), len(notes), unresolved, orphans


def local_repo_library(
    generated_at: str,
    branch: str,
    head: str,
    records: list[dict[str, object]],
    folders: list[dict[str, object]],
    shards: list[str],
    health: tuple[int, int, int, int],
) -> str:
    states = Counter(str(r["git_state"]) for r in records)
    categories = Counter(str(r["category"]) for r in records)
    return f"""---
agent: local-repo-library
generated_at: {generated_at}
source: local-filesystem-and-git
---

# Local Repo Library

This is the local-first library for `T:\\Project-AI-main`.

The local working copy is primary. GitHub/remotes are tracked as outside context, not as the source of truth.

## Local Position

- Branch: `{branch}`
- HEAD: `{head}`
- Total local filesystem files indexed, excluding `.git` internals: {len(records)}
- Folder records: {len(folders)}
- Ignored markdown shards: {len(shards)}

## Git State Counts

{bullets(states)}

## Category Counts

{bullets(categories)}

## Wiki Health

- Vault files: {health[0]}
- Vault Markdown/canvas notes: {health[1]}
- Unresolved wikilinks: {health[2]}
- Orphan notes: {health[3]}

## Library Shelves

- [[Local-Git-State]]
- [[Local-Working-Tree]]
- [[Local-Folder-Library]]
- [[Local-File-Library]]
- [[Ignored-File-Library]]

## Machine Manifests

- `wiki/09_Repo-Library/local_file_manifest.jsonl`
- `wiki/09_Repo-Library/local_folder_manifest.jsonl`
- `wiki/09_Repo-Library/ignored_file_manifest.jsonl`

## Refresh

- Refresh command: `python wiki/09_Repo-Library/refresh_local_repo_library.py`
"""


def git_state_page(generated_at: str, branch: str, head: str, status_short: str, branches: list[dict[str, str]]) -> str:
    local = [b for b in branches if b["kind"] == "local"]
    remote = [b for b in branches if b["kind"] in {"remote", "remote-head"}]
    local_rows = [[b["current"], f"`{b['name']}`", b["commit"], f"`{b['upstream']}`", b["subject"]] for b in local]
    remote_rows = [[b["kind"], f"`{b['name']}`", b["commit"], b["subject"]] for b in remote]
    remotes = run_git(["remote", "-v"]).splitlines()
    submodules = run_git(["submodule", "status", "--recursive"], check=False).splitlines()
    return f"""---
agent: local-repo-library
generated_at: {generated_at}
source: git-local-state
---

# Local Git State

Local branch: `{branch}`

Local HEAD: `{head}`

## Status

```text
{status_short}
```

## Local Branches

{table(["Current", "Branch", "Commit", "Upstream", "Subject"], local_rows)}

## Remote Context

{table(["Kind", "Ref", "Commit", "Subject"], remote_rows)}

## Remotes

{chr(10).join(f"- `{line}`" for line in remotes) if remotes else "- None"}

## Submodules

{chr(10).join(f"- `{line}`" for line in submodules) if submodules else "- None"}

## Connects

- [[Local-Repo-Library]]
- [[Local-Working-Tree]]
"""


def working_tree_page(generated_at: str, branch: str, head: str, status_short: str, status_lines: list[str]) -> str:
    modified = [[line[:2], f"`{line[3:]}`"] for line in status_lines if not line.startswith("??")]
    untracked = [[line[:2], f"`{line[3:]}`"] for line in status_lines if line.startswith("??")]
    return f"""---
agent: local-repo-library
generated_at: {generated_at}
source: git-working-tree
---

# Local Working Tree

Branch: `{branch}`

HEAD: `{head}`

## Status

```text
{status_short}
```

## Modified Tracked Paths

{table(["Status", "Path"], modified) if modified else "No modified tracked paths."}

## Untracked Non-Ignored Paths

{table(["Status", "Path"], untracked) if untracked else "No untracked non-ignored paths."}

## Connects

- [[Local-Repo-Library]]
- [[Ignored-File-Library]]
- [[Local-File-Library]]
"""


def file_library_page(generated_at: str, records: list[dict[str, object]]) -> str:
    states = Counter(str(r["git_state"]) for r in records)
    cats = Counter(str(r["category"]) for r in records)
    roots = Counter(str(r["top_root"]) for r in records)
    exts = Counter(str(r["extension"]) for r in records)
    return f"""---
agent: local-repo-library
generated_at: {generated_at}
source: local-file-library
---

# Local File Library

Every local file outside `.git` internals is represented in `local_file_manifest.jsonl`.

## Git States

{bullets(states)}

## Categories

{bullets(cats)}

## Top Roots

{bullets(roots, 100)}

## Extensions

{bullets(exts, 100)}

## Connects

- [[Local-Repo-Library]]
- [[Local-Folder-Library]]
- [[Ignored-File-Library]]
"""


def folder_library_page(generated_at: str, folders: list[dict[str, object]]) -> str:
    rows = []
    for folder in folders:
        if int(folder["depth"]) <= 2 and folder["relative_path"]:
            rows.append(
                [
                    folder["depth"],
                    f"`{folder['relative_path']}`",
                    folder["total_files"],
                    folder["tracked_files"],
                    folder["untracked_files"],
                    folder["ignored_files"],
                    folder["local_unclassified_files"],
                    len(folder["subfolders"]),
                ]
            )
    rows = sorted(rows, key=lambda row: (int(row[0]), str(row[1]).lower()))[:500]
    return f"""---
agent: local-repo-library
generated_at: {generated_at}
source: local-folder-library
---

# Local Folder Library

Every folder containing local files outside `.git` internals is represented in `local_folder_manifest.jsonl`.

## Folder Inventory

{table(["Depth", "Folder", "Total", "Tracked", "Untracked", "Ignored", "Other Local", "Subfolders"], rows)}

## Connects

- [[Local-Repo-Library]]
- [[Local-File-Library]]
"""


def ignored_library_page(generated_at: str, ignored_records: list[dict[str, object]], shards: list[str]) -> str:
    roots = Counter(str(r["top_root"]) for r in ignored_records)
    cats = Counter(str(r["category"]) for r in ignored_records)
    rules = Counter(f"{r['ignore_source']}:{r['ignore_line']} `{r['ignore_pattern']}`" for r in ignored_records)
    shard_links = "\n".join(f"- [[{Path(shard).stem}]]" for shard in shards)
    return f"""---
agent: local-repo-library
generated_at: {generated_at}
source: ignored-file-library
---

# Ignored File Library

Every ignored local file is recorded with the ignore source, line, pattern, category, and reason.

## Counts

- Ignored files: {len(ignored_records)}
- Markdown shards: {len(shards)}
- Manifest: `wiki/09_Repo-Library/ignored_file_manifest.jsonl`

## Ignored By Root

{bullets(roots, 100)}

## Ignored By Category

{bullets(cats, 100)}

## Top Ignore Rules

{bullets(rules, 120)}

## Shards

{shard_links}

## Connects

- [[Local-Repo-Library]]
- [[Local-Working-Tree]]
- [[Local-File-Library]]
"""


def main() -> None:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    LIB.mkdir(parents=True, exist_ok=True)

    branch = run_git(["branch", "--show-current"]).strip() or "(detached)"
    head = run_git(["rev-parse", "HEAD"]).strip()
    status_short = run_git(["status", "--short", "--branch"]).rstrip()
    status_lines = run_git(["status", "--porcelain=v1", "-uall"]).splitlines()
    statuses = git_status_map(status_lines)

    tracked = set(run_git_z(["ls-files", "-z"]))
    untracked = set(run_git_z(["ls-files", "--others", "--exclude-standard", "-z"]))
    ignored = set(run_git_z(["ls-files", "--others", "--ignored", "--exclude-standard", "-z"]))
    details = ignored_details(sorted(ignored))

    all_paths = sorted(set(local_files()) | tracked | untracked | ignored)
    records = [file_record(path, tracked, untracked, ignored, details, statuses, generated_at) for path in all_paths if (ROOT / path).exists()]
    records = sorted(records, key=lambda item: str(item["relative_path"]).lower())
    ignored_records = [record for record in records if record["git_state"] == "ignored"]
    folders = folder_records(records)

    write_jsonl(LIB / "local_file_manifest.jsonl", records)
    write_jsonl(LIB / "ignored_file_manifest.jsonl", ignored_records)
    write_jsonl(LIB / "local_folder_manifest.jsonl", folders)

    shards = ignored_shards(ignored_records, generated_at)
    health = link_health()
    branches = branch_rows()

    write_text(LIB / "Local-Repo-Library.md", local_repo_library(generated_at, branch, head, records, folders, shards, health))
    write_text(LIB / "Local-Git-State.md", git_state_page(generated_at, branch, head, status_short, branches))
    write_text(LIB / "Local-Working-Tree.md", working_tree_page(generated_at, branch, head, status_short, status_lines))
    write_text(LIB / "Local-File-Library.md", file_library_page(generated_at, records))
    write_text(LIB / "Local-Folder-Library.md", folder_library_page(generated_at, folders))
    write_text(LIB / "Ignored-File-Library.md", ignored_library_page(generated_at, ignored_records, shards))

    # Rebuild once more so generated library pages and shards are included as local files.
    all_paths = sorted(set(local_files()) | tracked | untracked | ignored)
    records = [file_record(path, tracked, untracked, ignored, details, statuses, generated_at) for path in all_paths if (ROOT / path).exists()]
    records = sorted(records, key=lambda item: str(item["relative_path"]).lower())
    ignored_records = [record for record in records if record["git_state"] == "ignored"]
    folders = folder_records(records)
    write_jsonl(LIB / "local_file_manifest.jsonl", records)
    write_jsonl(LIB / "ignored_file_manifest.jsonl", ignored_records)
    write_jsonl(LIB / "local_folder_manifest.jsonl", folders)
    health = link_health()
    write_text(LIB / "Local-Repo-Library.md", local_repo_library(generated_at, branch, head, records, folders, shards, health))
    write_text(LIB / "Local-File-Library.md", file_library_page(generated_at, records))
    write_text(LIB / "Local-Folder-Library.md", folder_library_page(generated_at, folders))
    write_text(LIB / "Ignored-File-Library.md", ignored_library_page(generated_at, ignored_records, shards))

    print(
        "LOCAL_LIBRARY_OK "
        f"files={len(records)} "
        f"tracked={sum(1 for r in records if r['git_state'] == 'tracked')} "
        f"untracked={sum(1 for r in records if r['git_state'] == 'untracked')} "
        f"ignored={sum(1 for r in records if r['git_state'] == 'ignored')} "
        f"folders={len(folders)} "
        f"wiki_files={health[0]} "
        f"wiki_notes={health[1]} "
        f"unresolved={health[2]} "
        f"orphans={health[3]}"
    )


if __name__ == "__main__":
    main()
