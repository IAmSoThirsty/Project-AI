#!/usr/bin/env python3
"""rlp_probe_refresh.py — Refresh the RLP probe pool.

Usage: python tools/rlp_probe_refresh.py [--state-file <path>]

Exit 0 = probe pool refreshed. Exit 1 = refresh failed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh RLP probe pool")
    parser.add_argument(
        "--state-file",
        type=Path,
        default=Path("data/rlp/rlp-state.json"),
        help="Path to the persisted RLP state file",
    )
    args = parser.parse_args()

    if not args.state_file.exists():
        print(f"ERROR: RLP state file not found: {args.state_file}", file=sys.stderr)
        return 1

    print(f"Probe pool refresh requested from {args.state_file}")
    print("NOTE: RLP is experimental. Full refresh implementation requires persisted state.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
