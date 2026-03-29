# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_phase_3_integration.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_phase_3_integration.py


"""
Phase 3 Integration Test - Self-Driving Labs
"""

import sys
import os

# Ensure the library is in path
sys.path.append(os.getcwd())

from project_ai.engine.capabilities.capability_invoker import CapabilityInvoker

def test_lab_integration():
    print("--- STARTING PHASE 3 INTEGRATION TEST ---")
    
    # 1. Initialize Invoker (Mocking dependencies)
    class MockPolicy:
        def is_capability_allowed(self, cap): return True
        def get_policy_context(self): return {"rules": {"max_capability_risk": 5}, "mode": "STRICT"}
    
    class MockState:
        def load_state(self, key): return None
        def save_state(self, key, val): pass

    invoker = CapabilityInvoker(MockPolicy(), MockState(), {})
    
    # 2. Invoke Robotic Synthesis
    inputs = {
        "lab_id": "RESEARCH_CORE_01",
        "name": "SuperHydride_V2",
        "composition": {"Hydrogen": 80.0, "Lanthanum": 20.0},
        "predicted_properties": {"conductivity": 92.0}
    }
    
    print(f"Invoking Discovery Cycle for {inputs['name']}...")
    result = invoker.invoke("robotic_synthesis", inputs)
    
    print(f"Discovery Result: {result}")
    
    # 3. Verify Feedback Loop
    if "feedback_delta" in result and result.get("status") == "SUCCESS":
        print(f"RL Feedback Delta: {result['feedback_delta']:.4f}")
        print("--- TEST SUCCESS: CLOSED-LOOP DISCOVERY VERIFIED ---")
    else:
        print("--- TEST FAILED: FEEDBACK LOOP INCOMPLETE ---")

if __name__ == "__main__":
    test_lab_integration()
