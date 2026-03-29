import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: knowledge-decay-service / integrity_check.py
# ============================================================================ #
#!/usr/bin/env python
"""
Database integrity check script for Knowledge Decay Service
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
