# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / integrity_check.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / integrity_check.py


#!/usr/bin/env python
"""
Database integrity check script for Verifiable Reality Infrastructure (Post-AI Proof Layer)
"""
import asyncio
import sys
from typing import List, Tuple


async def main():
    print("Running database integrity checks...")

    errors = await check_integrity()

    if errors:
        print("\n❌ Integrity check FAILED:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("\n✅ Integrity check PASSED: No issues found")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
