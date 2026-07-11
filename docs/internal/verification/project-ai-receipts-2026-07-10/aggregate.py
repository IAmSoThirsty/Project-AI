"""Authorship / activity aggregation from raw git-log captures (read-only).

Reads the git-log raw files produced by collect.ps1 and writes items
10, 13, 14, 15, 16, 17 plus git_activity.json. Identity grouping is rule-based
and every identity's assigned category is emitted for audit — no hidden merges.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

RECEIPT = Path(sys.argv[1]).resolve()
RAW = RECEIPT / "raw"
AUDIT_DATE = date(2026, 7, 10)


def read_lines(name: str) -> list[str]:
    p = RAW / name
    if not p.exists():
        return []
    return [ln for ln in p.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()]


def classify(name: str, email: str) -> str:
    n, e = name.lower(), email.lower()
    blob = f"{n} {e}"
    # AI coding agents FIRST — their identities carry "[bot]" but are distinct
    # from GitHub's own automation and must be counted separately (item 15).
    if "dependabot" in blob:
        return "Dependabot"
    if "anthropic" in blob or "claude" in blob:
        return "AI agent (Claude/Anthropic)"
    if "copilot" in blob:
        return "AI agent (GitHub Copilot)"
    if "google-labs-jules" in blob or "jules[bot]" in blob:
        return "AI agent (Google Jules)"
    if any(k in blob for k in ("cursor", "codex", "devin", "sweep", "gemini", "openai")):
        return "AI agent (other)"
    if "github-actions" in blob or e in ("actions@github.com",) or "web-flow" in blob \
            or e == "noreply@github.com":
        return "GitHub automation"
    if "[bot]" in blob:
        return "Other bot"
    owner_names = ("jeremy karrick", "iamsothirsty", "thirsty", "quencher")
    owner_emails = ("karrick1995@gmail.com",)
    if any(k in n for k in owner_names) or any(k in e for k in owner_emails):
        return "Owner (Jeremy Karrick / IAmSoThirsty / Thirsty / Quencher)"
    return "External / unclassified human"


# ---- HEAD history ----------------------------------------------------------
head = [ln.split("|") for ln in read_lines("_git_log_head.txt")]
# fields: H | an | ae | ad(iso) | cd(iso)
head_dates = [row[3][:10] for row in head if len(row) >= 4]
by_month: dict[str, int] = defaultdict(int)
by_day: dict[str, int] = defaultdict(int)
for d in head_dates:
    by_month[d[:7]] += 1
    by_day[d] += 1

first_date = min(head_dates) if head_dates else "n/a"
last_date = max(head_dates) if head_dates else "n/a"
elapsed = (AUDIT_DATE - date.fromisoformat(first_date)).days if head_dates else None

# ---- all-refs authorship ---------------------------------------------------
allrefs = [ln.split("|") for ln in read_lines("_git_log_all.txt")]
author_commits: dict[tuple[str, str], int] = defaultdict(int)
for row in allrefs:
    if len(row) >= 3:
        author_commits[(row[1], row[2])] += 1

cat_commits: dict[str, int] = defaultdict(int)
cat_identities: dict[str, set] = defaultdict(set)
for (name, email), c in author_commits.items():
    cat = classify(name, email)
    cat_commits[cat] += c
    cat_identities[cat].add(f"{name} <{email}>")

# ---- numstat by author (HEAD) ----------------------------------------------
add_by: dict[str, int] = defaultdict(int)
del_by: dict[str, int] = defaultdict(int)
files_by: dict[str, int] = defaultdict(int)
cur = None
for ln in read_lines("_git_numstat_head.txt"):
    if ln.startswith("@@@|"):
        parts = ln.split("|")
        cur = f"{parts[2]} <{parts[3]}>" if len(parts) >= 4 else "unknown"
    else:
        bits = ln.split("\t")
        if len(bits) == 3 and cur:
            a, d = bits[0], bits[1]
            if a.isdigit():
                add_by[cur] += int(a)
            if d.isdigit():
                del_by[cur] += int(d)
            files_by[cur] += 1

# ---- write outputs ---------------------------------------------------------
with (RAW / "13_commits_by_author.txt").open("w", encoding="utf-8") as f:
    f.write("Commit count by author (name <email>), across all reachable refs.\n")
    f.write(f"{'commits':>8}  author\n")
    for (name, email), c in sorted(author_commits.items(), key=lambda kv: -kv[1]):
        f.write(f"{c:>8}  {name} <{email}>\n")

with (RAW / "14_normalized_identities.txt").open("w", encoding="utf-8") as f:
    f.write("Rule-based identity grouping (all refs). Every identity's category is\n")
    f.write("listed so the grouping is auditable. Grouping uses name/email evidence only.\n\n")
    for cat in sorted(cat_identities, key=lambda k: -cat_commits[k]):
        f.write(f"== {cat}: {cat_commits[cat]} commits ==\n")
        for ident in sorted(cat_identities[cat]):
            f.write(f"    {ident}\n")
        f.write("\n")

with (RAW / "15_contribution_categories.txt").open("w", encoding="utf-8") as f:
    f.write("Contribution categories (all refs), by commit count.\n")
    f.write(f"{'commits':>8}  category\n")
    for cat, c in sorted(cat_commits.items(), key=lambda kv: -kv[1]):
        f.write(f"{c:>8}  {cat}\n")

with (RAW / "16_commits_by_month_day.txt").open("w", encoding="utf-8") as f:
    f.write("Commits by month (HEAD history):\n")
    for m in sorted(by_month):
        f.write(f"  {m}  {by_month[m]}\n")
    f.write(f"\nDistinct active days: {len(by_day)}\n")
    f.write("Top 20 busiest days:\n")
    for d, c in sorted(by_day.items(), key=lambda kv: -kv[1])[:20]:
        f.write(f"  {d}  {c}\n")

with (RAW / "17_numstat_by_author.txt").open("w", encoding="utf-8") as f:
    f.write("Additions/deletions by author (HEAD history, git numstat; binary files omitted).\n")
    f.write(f"{'+lines':>10} {'-lines':>10} {'files':>8}  author\n")
    for a in sorted(add_by, key=lambda k: -(add_by[k] + del_by[k])):
        f.write(f"{add_by[a]:>10} {del_by[a]:>10} {files_by[a]:>8}  {a}\n")

with (RAW / "10_elapsed_days.txt").open("w", encoding="utf-8") as f:
    f.write(f"first commit date (HEAD, author date): {first_date}\n")
    f.write(f"latest commit date (HEAD, author date): {last_date}\n")
    f.write(f"audit date: {AUDIT_DATE.isoformat()}\n")
    f.write(f"elapsed calendar days (first commit -> audit): {elapsed}\n")

activity = {
    "head_commit_count": len(head),
    "allrefs_commit_count": len(allrefs),
    "distinct_authors_allrefs": len(author_commits),
    "first_commit_date": first_date,
    "latest_commit_date": last_date,
    "elapsed_days": elapsed,
    "commits_by_category": dict(sorted(cat_commits.items(), key=lambda kv: -kv[1])),
    "identities_by_category": {k: sorted(v) for k, v in cat_identities.items()},
    "commits_by_month": dict(sorted(by_month.items())),
    "distinct_active_days": len(by_day),
    "numstat_by_author": {
        a: {"added": add_by[a], "deleted": del_by[a], "files": files_by[a]}
        for a in sorted(add_by, key=lambda k: -(add_by[k] + del_by[k]))
    },
}
(RECEIPT / "git_activity.json").write_text(json.dumps(activity, indent=2), encoding="utf-8")
print(f"HEAD commits={len(head)} allrefs={len(allrefs)} authors={len(author_commits)} "
      f"first={first_date} elapsed={elapsed}")
for cat, c in sorted(cat_commits.items(), key=lambda kv: -kv[1]):
    print(f"  {c:>6}  {cat}")
