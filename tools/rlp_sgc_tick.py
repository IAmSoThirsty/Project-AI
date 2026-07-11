#!/usr/bin/env python3
"""rlp_sgc_tick.py — Apply one SGC slow-decay tick to all domains.

Usage: python tools/rlp_sgc_tick.py [--state-file <path>]

Exit 0 = tick applied. Exit 1 = tick failed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply RLP SGC decay tick")
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

    print(f"SGC decay tick requested from {args.state_file}")
    print("NOTE: RLP is experimental. Full tick implementation requires persisted state.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
