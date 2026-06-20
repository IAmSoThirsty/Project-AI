#!/usr/bin/env python3
"""Capture and verify the Stage 3 soft-freeze state without legacy writes."""

from __future__ import annotations

import json
from pathlib import Path

from legacy_source_guard import configured_guard, sha256

REPO = Path(__file__).resolve().parents[1]
FROZEN_HISTORY = REPO / "docs" / "internal" / "frozen-history" / "PROJECT-AI_FROZEN_HISTORY.md"
OUTPUT = REPO / "docs" / "internal" / "LEGACY_SOURCE_STATE.json"


def main() -> int:
    guard = configured_guard()
    before = guard.snapshot()
    frozen_text = FROZEN_HISTORY.read_text(encoding="utf-8")
    head = str(before["head"])
    if head not in frozen_text:
        raise RuntimeError(f"Frozen history does not contain legacy HEAD {head}")
    after = guard.snapshot()
    if before != after:
        raise RuntimeError("Legacy repository changed while its state was being captured")
    state = {
        **before,
        "frozen_history": {
            "bytes": FROZEN_HISTORY.stat().st_size,
            "contains_head": True,
            "path": str(FROZEN_HISTORY.relative_to(REPO)).replace("\\", "/"),
            "sections": frozen_text.count("\n## Commit "),
            "sha256": sha256(FROZEN_HISTORY),
        },
        "policy": "read-only input; no ACL, Git configuration, attribute, or source-file mutation",
    }
    OUTPUT.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"Captured unchanged legacy state at {state['head']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
