# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / completion_tracker_agent.py
# ============================================================================ #
#
# COMPLIANCE: Regulator-Ready / UTF-8                                          #



"""
Completion Tracker Agent
Diffs current state against the last architect manifest.
Shows what moved from STUB to EXECUTABLE, what regressed, what's new.
No interaction. Runs and exits.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Thirsty-Lang Metadata Integration
__PRODUCTIVITY_STATUS__ = "Active"
__LAST_UPDATE__ = "2026-03-13 00:51"

ROOT = Path(__file__).parent.parent.absolute()
CURRENT_MANIFEST = ROOT / "governance" / "ARCHITECT_MANIFEST.json"
HISTORY_DIR = ROOT / "governance" / "history"
OUTPUT_MD = ROOT / "governance" / "COMPLETION_TRACKER.md"
OUTPUT_JSON = ROOT / "governance" / "COMPLETION_TRACKER.json"


def load_manifest(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def get_previous_manifest() -> dict:
    """Find the most recent historical manifest."""
    if not HISTORY_DIR.exists():
        return {}
    histories = sorted(HISTORY_DIR.glob("ARCHITECT_MANIFEST_*.json"))
    if not histories:
        return {}
    return load_manifest(histories[-1])


def archive_current(current: dict):
    """Save current manifest to history."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = HISTORY_DIR / f"ARCHITECT_MANIFEST_{ts}.json"
    dest.write_text(json.dumps(current, indent=2), encoding="utf-8")


def diff_manifests(prev: dict, curr: dict) -> dict:
    prev_files = {f["path"]: f for f in prev.get("files", [])}
    curr_files = {f["path"]: f for f in curr.get("files", [])}

    promoted = []      # STUB/MOCK -> EXECUTABLE
    regressed = []     # EXECUTABLE -> STUB/MOCK
    improved = []      # completion % went up
    declined = []      # completion % went down
    new_files = []     # not in prev
    removed_files = [] # not in curr

    for path, curr_f in curr_files.items():
        if path not in prev_files:
            new_files.append(curr_f)
            continue

        prev_f = prev_files[path]

        # Category change
        if prev_f["category"] in {"STUB", "MOCK"} and curr_f["category"] == "EXECUTABLE":
            promoted.append({"path": path, "from": prev_f["category"], "to": curr_f["category"]})
        elif prev_f["category"] == "EXECUTABLE" and curr_f["category"] in {"STUB", "MOCK"}:
            regressed.append({"path": path, "from": prev_f["category"], "to": curr_f["category"]})

        # Completion change
        try:
            prev_pct = int(prev_f["completion"].replace("%", ""))
            curr_pct = int(curr_f["completion"].replace("%", ""))
            if curr_pct > prev_pct:
                improved.append({"path": path, "from": f"{prev_pct}%", "to": f"{curr_pct}%"})
            elif curr_pct < prev_pct:
                declined.append({"path": path, "from": f"{prev_pct}%", "to": f"{curr_pct}%"})
        except ValueError:
            pass

    for path in prev_files:
        if path not in curr_files:
            removed_files.append(path)

    return {
        "promoted": promoted,
        "regressed": regressed,
        "improved": improved,
        "declined": declined,
        "new_files": new_files,
        "removed_files": removed_files,
    }


def build_manifest():
    if not CURRENT_MANIFEST.exists():
        print("No ARCHITECT_MANIFEST.json found. Run architect_agent.py first.")
        sys.exit(1)

    current = load_manifest(CURRENT_MANIFEST)
    previous = get_previous_manifest()

    if not previous:
        print("No previous manifest found. Archiving current as baseline.")
        archive_current(current)
        print("Baseline archived. Run again after changes to see diff.")
        sys.exit(0)

    diff = diff_manifests(previous, current)
    archive_current(current)

    prev_completion = previous.get("summary", {}).get("estimated_completion", "?")
    curr_completion = current.get("summary", {}).get("estimated_completion", "?")

    result = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "completion": {"previous": prev_completion, "current": curr_completion},
        "diff": diff,
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Completion Tracker",
        f"Generated: {result['generated']}",
        f"Overall Completion: {prev_completion} → **{curr_completion}**",
        "",
        f"## Progress",
        f"- Promoted (stub→executable): **{len(diff['promoted'])}**",
        f"- Regressed (executable→stub): **{len(diff['regressed'])}**",
        f"- Improved completion %: {len(diff['improved'])}",
        f"- Declined completion %: {len(diff['declined'])}",
        f"- New files: {len(diff['new_files'])}",
        f"- Removed files: {len(diff['removed_files'])}",
    ]

    if diff["promoted"]:
        lines += ["", "## Promoted (Real Wins)", "| File | From | To |", "|------|------|----|"]
        for p in diff["promoted"]:
            lines.append(f"| `{p['path']}` | {p['from']} | {p['to']} |")

    if diff["regressed"]:
        lines += ["", "## Regressed (Needs Attention)", "| File | From | To |", "|------|------|----|"]
        for r in diff["regressed"]:
            lines.append(f"| `{r['path']}` | {r['from']} | {r['to']} |")

    if diff["improved"]:
        lines += ["", "## Improved Completion", "| File | From | To |", "|------|------|----|"]
        for i in diff["improved"]:
            lines.append(f"| `{i['path']}` | {i['from']} | {i['to']} |")

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"COMPLETION_TRACKER written. {prev_completion} -> {curr_completion}")


if __name__ == "__main__":
    build_manifest()
