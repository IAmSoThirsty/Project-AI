# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-10 | TIME: 21:02               #
# COMPLIANCE: Regulator-Ready / UTF-8                                          #
# ============================================================================ #

# Date: 2026-03-10 | Time: 20:37 | Status: Active | Tier: Master
#                                           [2026-03-10 18:58]
#                                          Productivity: Active
# ============================================================================ #
#                                                            DATE: 2026-03-10 #
#                                                          TIME: 15:01:55 PST #
#                                                        PRODUCTIVITY: Active #
# ============================================================================ #

#                                           [2026-03-03 13:45]
#                                          Productivity: Active
#!/usr/bin/env python
"""
Database migration rollback script for AI Mutation Governance Firewall
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
