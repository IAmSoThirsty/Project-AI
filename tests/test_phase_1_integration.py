# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_phase_1_integration.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_phase_1_integration.py


"""
Phase 1 Integration Test - Quantum Bridge & SensorFusion
"""

import sys
import os

# Ensure the library is in path
sys.path.append(os.getcwd())

from project_ai.orchestrator.subsystems.quantum_bridge import QuantumBridge
from project_ai.engine.capabilities.capability_invoker import CapabilityInvoker

def test_quantum_integration():
    print("--- STARTING PHASE 1 INTEGRATION TEST ---")
    
    # 1. Initialize Quantum Bridge
    bridge = QuantumBridge("INTERNAL_TEST_NODE")
    
    # 2. Simulate QKD Handshake
    cid = bridge.simulate_qkd_handshake("REMOTE_PEER")
    print(f"QKD Established. CID: {cid}")
    
    # 3. Retrieve Quantum Telemetry
    q_telemetry = bridge.get_quantum_telemetry()
    print(f"Quantum Telemetry: {q_telemetry}")
    
    # 4. Invoke SensorFusion via Invoker (Mocking dependencies)
    class MockPolicy:
        def is_capability_allowed(self, cap): return True
        def get_policy_context(self): return {"rules": {"max_capability_risk": 5}, "mode": "STRICT"}
    
    class MockState:
        def load_state(self, key): return None
        def save_state(self, key, val): pass

    invoker = CapabilityInvoker(MockPolicy(), MockState(), {})
    
    inputs = {
        "optical": {"status": "ok"},
        "quantum": q_telemetry
    }
    
    result = invoker.invoke("sensor_fusion", inputs)
    
    print(f"SensorFusion Fused Result: {result}")
    
    if result.get("spoof_resistance") == "QUANTUM_LOCKED":
        print("--- TEST SUCCESS: QUANTUM LAYER VERIFIED ---")
    else:
        print("--- TEST FAILED: QUANTUM DATA NOT FUSED ---")

if __name__ == "__main__":
    test_quantum_integration()
