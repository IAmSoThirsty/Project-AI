#!/usr/bin/env python3
"""verify_security_relay.py — Verify the security audit relay hash chain.

Usage: python tools/verify_security_relay.py <path-to-relay.jsonl>

Exit 0 = chain valid. Exit 1 = chain invalid or file missing.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: verify_security_relay.py <path-to-relay.jsonl>", file=sys.stderr)
        return 1

    relay_path = Path(sys.argv[1])
    if not relay_path.exists():
        print(f"ERROR: relay file not found: {relay_path}", file=sys.stderr)
        return 1

    try:
        from security.bridge import AppendOnlyAuditRelay
    except ImportError:
        print(
            "ERROR: security package not importable. Run from repo root with uv.", file=sys.stderr
        )
        return 1

    relay = AppendOnlyAuditRelay(relay_path)
    try:
        valid, count = relay.verify()
    except Exception as exc:
        print(f"FAIL: relay verification error: {exc}", file=sys.stderr)
        return 1

    if valid:
        print(f"OK: security relay valid ({count} events)")
        return 0
    else:
        print(f"FAIL: security relay chain invalid ({count} events)", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
