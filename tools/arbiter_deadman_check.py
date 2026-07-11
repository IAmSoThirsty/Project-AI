#!/usr/bin/env python3
"""arbiter_deadman_check.py — Check the arbiter dead-man switch.

Reads the persisted arbiter succession state and determines whether
the dead-man switch has fired (LAPSED or SUCCEEDED).

Usage: python tools/arbiter_deadman_check.py [--state-file <path>]

Exit 0 = arbiter ACTIVE. Exit 1 = arbiter LAPSED or SUCCEEDED.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Check arbiter dead-man switch")
    parser.add_argument(
        "--state-file",
        type=Path,
        default=Path("data/arbiter/arbiter-state.json"),
        help="Path to the persisted arbiter state file",
    )
    args = parser.parse_args()

    if not args.state_file.exists():
        print(f"OK: no state file at {args.state_file} — arbiter not yet initialized")
        return 0

    try:
        state = json.loads(args.state_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"ERROR: cannot read state file: {exc}", file=sys.stderr)
        return 1

    last_heartbeat = float(state.get("last_heartbeat", 0))
    heartbeat_seconds = int(state.get("heartbeat_seconds", 30 * 86400))
    grace_seconds = int(state.get("grace_seconds", 14 * 86400))
    current_status = state.get("status", "active")

    now = time.time()
    elapsed = now - last_heartbeat

    if current_status == "succeeded":
        print("FAIL: arbiter status is SUCCEEDED (succession activated)")
        return 1

    if elapsed > heartbeat_seconds + grace_seconds:
        print(
            f"FAIL: arbiter SUCCEEDED — elapsed {elapsed:.0f}s exceeds "
            f"heartbeat+grace ({heartbeat_seconds + grace_seconds}s)"
        )
        return 1
    elif elapsed > heartbeat_seconds and current_status == "active":
        print(
            f"WARN: arbiter LAPSED — elapsed {elapsed:.0f}s exceeds "
            f"heartbeat ({heartbeat_seconds}s), grace window running"
        )
        return 1

    print(
        f"OK: arbiter ACTIVE — last heartbeat {elapsed:.0f}s ago, "
        f"within {heartbeat_seconds}s window"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
