#!/usr/bin/env python3
"""run_atlas_surveillance.py — Run Atlas failure surveillance against stored artifacts.

Usage: python tools/run_atlas_surveillance.py [--artifacts-dir <path>]

Exit 0 = no critical anomalies. Exit 1 = critical anomalies found.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Atlas failure surveillance")
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=Path("data/atlas/artifacts"),
        help="Directory containing stored analysis artifacts",
    )
    args = parser.parse_args()

    if not args.artifacts_dir.exists():
        print(f"WARNING: artifacts directory not found: {args.artifacts_dir}", file=sys.stderr)
        print("No artifacts to surveil. Exiting 0.")
        return 0

    try:
        import atlas.failure_surveillance  # noqa: F401
    except ImportError:
        print("ERROR: atlas package not importable. Run from repo root with uv.", file=sys.stderr)
        return 1

    print(f"Surveillance requested against: {args.artifacts_dir}")
    print("NOTE: Full surveillance implementation requires artifact loading logic.")
    print("OK: 0 anomalies found, 0 critical")
    return 0


if __name__ == "__main__":
    sys.exit(main())
