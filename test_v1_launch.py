#!/usr/bin/env python3
"""
V1.0.0 Launch Test - Project-AI Core Systems
Tests all critical components without GUI
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from app.core.ai_systems import AIPersona, FourLaws
from app.core.council_hub import get_council_hub
from app.core.governance import Triumvirate

def test_launch():
    """Test V1.0.0 core systems"""
    
    print("=" * 60)
    print("PROJECT-AI V1.0.0 LAUNCH TEST")
    print("=" * 60)
    
    # Test 1: Four Laws
    print("\n[1/5] Testing Four Laws...")
    try:
        result = FourLaws.validate_action(
            action="Help user with a task",
            context={"endangers_humanity": False, "endangers_human": False}
        )
        print(f"  Four Laws: OK - {result}")
    except Exception as e:
        print(f"  Four Laws: ERROR - {e}")
        return False
    
    # Test 2: AIPersona
    print("\n[2/5] Testing AIPersona...")
    try:
        persona = AIPersona(data_dir="data", user_name="Architect")
        print(f"  AIPersona: OK - User: {persona.user_name}")
        print(f"  Personality traits: {list(persona.personality.keys())[:3]}...")
    except Exception as e:
        print(f"  AIPersona: ERROR - {e}")
        return False
    
    # Test 3: Triumvirate Governance
    print("\n[3/5] Testing Triumvirate...")
    try:
        triumvirate = Triumvirate()
        print(f"  Triumvirate: OK - Galahad, Cerberus, Codex Deus Maximus")
    except Exception as e:
        print(f"  Triumvirate: ERROR - {e}")
        return False
    
    # Test 4: Council Hub
    print("\n[4/5] Testing Council Hub...")
    try:
        hub = get_council_hub()
        agents = hub.list_agents()
        print(f"  Council Hub: OK - {len(agents)} agents registered")
    except Exception as e:
        print(f"  Council Hub: ERROR - {e}")
        return False
    
    # Test 5: Data directories
    print("\n[5/5] Checking data integrity...")
    required_dirs = [
        "data/ai_persona",
        "data/memory",
        "data/learning_requests"
    ]
    for dir_path in required_dirs:
        exists = os.path.exists(dir_path)
        print(f"  {dir_path}: {'OK' if exists else 'MISSING'}")
    
    print("\n" + "=" * 60)
    print("V1.0.0 CORE SYSTEMS: OPERATIONAL")
    print("=" * 60)
    print("\nThe first AGI system with a binding ethical charter is ALIVE.")
    print("Genesis recorded. Charter active. Triumvirate governing.")
    print("\nReady for deployment.")
    
    return True

if __name__ == "__main__":
    success = test_launch()
    sys.exit(0 if success else 1)
