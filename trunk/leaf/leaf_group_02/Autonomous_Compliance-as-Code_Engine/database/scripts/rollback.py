# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / rollback.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / rollback.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
#!/usr/bin/env python
"""
Database migration rollback script for Autonomous Compliance-as-Code Engine
"""
import asyncio
import sys

async def main():
    if len(sys.argv) < 2:
        print("Usage: python rollback.py <version>")
        print("  version 0: rollback all migrations")
        sys.exit(1)
    
    version = int(sys.argv[1])
    success = await rollback_migration(version)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
