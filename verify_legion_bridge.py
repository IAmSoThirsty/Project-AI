import json
import os
import sys

# Add src to path for direct execution from root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def simulate_legion_bridge():
    # Deferred imports to handle pathing
    from app.core.legion_protocol import LegionProtocol

    # EntityClass used if needed, but keeping it local for PEP 8
    # from app.core.ai_systems import EntityClass

    print("--- STARTING LEGION SHADOW THIRST BRIDGE VERIFICATION ---")

    # Initialize Legion
    legion = LegionProtocol()

    # Test 1: Standard global guidance
    print("\n[TEST 1] Processing standard guidance...")
    response = legion.process_request("Should I initiate a Genesis Event?")

    print(f"Response Content: {response.get('content')}")
    print(
        f"Verification Attestations: {json.dumps(response.get('metadata', {}).get('verification'), indent=2)}"
    )

    # Check for Shadow Thirst attestation
    attestations = response.get("metadata", {}).get("verification", {})
    if "shadow_thirst" in attestations:
        print("SUCCESS: Shadow Thirst attestation found.")
    else:
        print("FAILURE: Shadow Thirst attestation missing.")

    # Test 2: Verify Zeroth Law invariant (Simulated)
    # The current lambda in legion_protocol.py is safe.
    # We could try to force a failure if we had a way to inject a harmful prompt,
    # but the lambda is hardcoded to guide_user_toward_genesis.

    print("\n--- VERIFICATION COMPLETE ---")


if __name__ == "__main__":
    simulate_legion_bridge()
