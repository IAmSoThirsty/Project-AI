#!/usr/bin/env python3
"""verify_audit_chain.py — Verify the integrity of an audit chain file.

Usage: python tools/verify_audit_chain.py <path-to-audit.jsonl>

Exit 0 = chain valid. Exit 1 = chain invalid or file missing.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: verify_audit_chain.py <path-to-audit.jsonl>", file=sys.stderr)
        return 1

    audit_path = Path(sys.argv[1])
    if not audit_path.exists():
        print(f"ERROR: audit file not found: {audit_path}", file=sys.stderr)
        return 1

    try:
        from audit.chain import FileAuditLog
    except ImportError:
        print("ERROR: audit package not importable. Run from repo root with uv.", file=sys.stderr)
        return 1

    try:
        log = FileAuditLog(audit_path)
    except Exception as exc:
        print(f"FAIL: audit chain invalid on load: {exc}")
        return 1

    verification = log.verify_chain()
    if verification.valid:
        print(f"OK: audit chain valid ({len(log.events)} events)")
        return 0
    else:
        print(f"FAIL: {verification.reason}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
