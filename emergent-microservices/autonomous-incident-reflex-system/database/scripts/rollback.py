#!/usr/bin/env python
"""
Database migration rollback script for Autonomous Incident Reflex System
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
