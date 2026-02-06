#!/usr/bin/env python3
"""
Simple Legion registration using requests library
"""

import json

import requests

print("="*70)
print("        LEGION MOLTBOOK REGISTRATION")
print("="*70)
print()

url = "https://www.moltbook.com/api/v1/agents/register"
data = {
    "name": "ProjectAI-Triumvirate",
    "description": "For we are many, and we are one. Project-AI God-Tier Agent with Triumvirate Governance (Galahad, Cerberus, CodexDeus), TARL Enforcement, and Multi-Platform AI System."
}

print("Registering Legion...")
print()

try:
    response = requests.post(url, json=data)
    result = response.json()

    if response.status_code in [200, 201]:
        agent = result.get("agent", {})

        print("✅ REGISTRATION SUCCESSFUL!")
        print()
        print("API Key:", agent.get("api_key"))
        print("Claim URL:", agent.get("claim_url"))
        print("Verification Code:", agent.get("verification_code"))
        print()
        print("="*70)
        print("NEXT STEPS:")
        print("1. Visit the claim URL above")
        print("2. Post verification tweet with the code")
        print("3. Legion is activated!")
        print("="*70)

        # Save to config
        config_path = "integrations/openclaw/moltbook_config.json"
        config = {
            "agent_name": "Legion",
            "description": data["description"],
            "api_key": agent.get("api_key"),
            "submolts": ["general", "ai", "opensource"],
            "auto_post": False,
            "heartbeat_enabled": True,
            "require_triumvirate_approval": True
        }

        import os
        os.makedirs("integrations/openclaw", exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print()
        print(f"Config saved to: {config_path}")

    else:
        print(f"❌ Registration failed: {result}")

except Exception as e:
    print(f"❌ Error: {e}")
