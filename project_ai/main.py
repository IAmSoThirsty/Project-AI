"""
Project-AI PACE Engine - Main Entry Point
==========================================

Simple runnable entrypoint demonstrating bonding and request handling.
"""

if __name__ == "__main__":
    from project_ai.engine import PACEEngine

    print("=" * 60)
    print("Project-AI PACE Engine - Starting")
    print("=" * 60)

    # Initialize engine
    engine = PACEEngine()
    print("\n✓ Engine initialized")

    # Example: run bonding protocol
    print("\n--- Running Bonding Protocol ---")
    bonding_profile = {
        "name": "Project-AI (Jeremy Bonded)",
        "values": {"safety": "high", "clarity": "high"},
        "temperament": {"direct": True, "verbose": False},
        "relationship": {"operator": "Jeremy"},
        "constraints": {"respect_operator": True},
    }
    identity = engine.run_bonding_protocol(bonding_profile)
    print(f"✓ Bonded identity: {identity['name']}")
    print(f"  Phase: {identity['phase']}")
    print(f"  Relationship: {identity['relationship']}")

    # Example: handle a generic request
    print("\n--- Handling Diagnostic Request ---")
    payload = {
        "type": "diagnostic",
        "message": "Check current state and summarize recent activity.",
    }
    response = engine.handle_input("cli", payload)
    
    print(f"\n✓ Response received:")
    print(f"  Identity Phase: {response['identity_phase']}")
    print(f"  Explanation: {response['explanation']}")
    print(f"  Result: {response['result']}")

    print("\n" + "=" * 60)
    print("Project-AI PACE Engine - Demo Complete")
    print("=" * 60)
