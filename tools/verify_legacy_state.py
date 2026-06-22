#!/usr/bin/env python3
"""Verify the recorded legacy snapshot without writing to the legacy repository."""

from __future__ import annotations

import json
from pathlib import Path

from legacy_source_guard import configured_guard, sha256

REPO = Path(__file__).resolve().parents[1]
RECORDED_PATH = REPO / "docs" / "internal" / "LEGACY_SOURCE_STATE.json"
FROZEN_PATH = REPO / "docs" / "internal" / "frozen-history" / "PROJECT-AI_FROZEN_HISTORY.md"


def main() -> int:
    recorded = json.loads(RECORDED_PATH.read_text(encoding="utf-8"))
    before = configured_guard().snapshot()
    frozen_text = FROZEN_PATH.read_text(encoding="utf-8")
    checks = {
        "legacy_snapshot_matches": before == {key: recorded[key] for key in before},
        "frozen_history_contains_head": str(before["head"]) in frozen_text,
        "frozen_history_sections": frozen_text.count("\n## Commit ") == 2264,
        "frozen_history_sha256": sha256(FROZEN_PATH) == recorded["frozen_history"]["sha256"],
    }
    after = configured_guard().snapshot()
    checks["legacy_unchanged_during_verification"] = before == after
    for name, passed in checks.items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
    if not all(checks.values()):
        return 1
    print(f"legacy source unchanged at {before['head']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
