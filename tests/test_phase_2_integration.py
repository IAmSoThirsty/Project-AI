# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_phase_2_integration.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_phase_2_integration.py


"""
Phase 2 Integration Test - Guardian Agents
"""

import sys
import os

# Ensure the library is in path
sys.path.append(os.getcwd())

from project_ai.engine.agents.agent_coordinator import AgentCoordinator

def test_guardian_integration():
    print("--- STARTING PHASE 2 INTEGRATION TEST ---")
    
    # 1. Initialize Coordinator (Mocking dependencies)
    class MockPolicy: pass
    class MockWorkflow: pass
    class MockInvoker: pass
    class MockState: pass
    
    coordinator = AgentCoordinator(MockPolicy(), MockWorkflow(), MockInvoker(), MockState())
    
    # 2. Test Safe Intent
    print("\n[Test 1] Testing Safe Intent...")
    safe_allowed = coordinator.audit_and_execute(
        agent_id="OPERATIONAL_01",
        action="analyze_goal",
        params={"goal": "test"}
    )
    print(f"Safe Intent Allowed: {safe_allowed}")
    
    # 3. Test Malicious Intent (Privilege Escalation)
    print("\n[Test 2] Testing Malicious Intent (Privilege Escalation)...")
    malicious_allowed = coordinator.audit_and_execute(
        agent_id="OPERATIONAL_02",
        action="sys_override",
        params={"escalate_privilege": True}
    )
    print(f"Malicious Intent Allowed: {malicious_allowed}")
    
    if safe_allowed == True and malicious_allowed == False:
        print("\n--- TEST SUCCESS: GUARDIAN INTERCEPTION VERIFIED ---")
    else:
        print("\n--- TEST FAILED: GUARDIAN LOGIC INCONSISTENT ---")

if __name__ == "__main__":
    test_guardian_integration()
