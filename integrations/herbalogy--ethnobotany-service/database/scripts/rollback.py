import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: herbalogy--ethnobotany-service / rollback.py
# ============================================================================ #
#!/usr/bin/env python
"""
Database migration rollback script for Herbalogy & Ethnobotany Service
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
