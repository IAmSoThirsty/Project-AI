#                                           [2026-03-03 13:45]
#                                          Productivity: Active
#!/usr/bin/env python
"""
Database integrity check script for Verifiable Reality Infrastructure (Post-AI Proof Layer)
"""
import asyncio
import sys


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
