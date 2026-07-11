#!/usr/bin/env python3
"""verify_convergence_hash.py — Verify the Thirsty-Lang convergence hash is unchanged.

Usage: python tools/verify_convergence_hash.py

Exit 0 = hash matches expected. Exit 1 = hash has changed.
"""

from __future__ import annotations

import sys

EXPECTED_HASH = "3eda3256049339cb069354cc81ee7c51d88e3e41e81ea707e5bf3d3e14ba478c"


def main() -> int:
    try:
        from convergence.shadow_thirst import run_convergence
    except ImportError:
        print(
            "ERROR: convergence package not importable. Run from repo root with uv.",
            file=sys.stderr,
        )
        return 1

    try:
        report = run_convergence()
    except Exception as exc:
        print(f"ERROR: convergence harness failed: {exc}", file=sys.stderr)
        return 1

    actual_hash = report.convergence_hash
    if actual_hash == EXPECTED_HASH:
        print(f"OK: convergence hash matches expected ({actual_hash[:16]}...)")
        print(f"  converged: {report.converged}")
        print(f"  tiers checked: {len(report.tier_witnesses)}")
        return 0
    else:
        print("FAIL: convergence hash has changed!", file=sys.stderr)
        print(f"  expected: {EXPECTED_HASH}", file=sys.stderr)
        print(f"  actual:   {actual_hash}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
