#!/usr/bin/env python3
"""
Register Legion on Moltbook
One-time setup script
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from integrations.openclaw.moltbook_client import register_legion


async def main():
    """Register Legion and display claim instructions"""
    print()
    print("=" * 70)
    print(" " * 20 + "LEGION MOLTBOOK REGISTRATION")
    print("=" * 70)
    print()
    print("This will register Legion on Moltbook - the AI social network.")
    print()
    print("Legion will be an extension of the Triumvirate:")
    print("  • All posts require Galahad, Cerberus, CodexDeus approval")
    print("  • TARL enforcement active")
    print("  • No independent authority")
    print()
    print("For we are many, and we are one. 🔱")
    print()
    print("=" * 70)
    print()
    
    try:
        result = await register_legion()
        
        print()
        print("✅ REGISTRATION COMPLETE!")
        print()
        print("Save this information:")
        print(f"  API Key: {result['api_key']}")
        print(f"  Claim URL: {result['claim_url']}")
        print(f"  Verification Code: {result['verification_code']}")
        print()
        print("Config saved to: integrations/openclaw/moltbook_config.json")
        print()
        
    except Exception as e:
        print()
        print(f"❌ Registration failed: {e}")
        print()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
