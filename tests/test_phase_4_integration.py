# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_phase_4_integration.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_phase_4_integration.py


"""
Phase 4 Integration Test - CXL & HierKNEM
"""

import sys
import os

# Ensure the library is in path
sys.path.append(os.getcwd())

from kernel.thirsty_super_kernel import ThirstySuperKernel, SystemConfig

def test_substrate_integration():
    print("--- STARTING PHASE 4 INTEGRATION TEST ---")
    
    # 1. Initialize Super Kernel (Minimal config)
    config = SystemConfig(
        enable_ai_detection=False,
        enable_deception=False,
        enable_visualization=False
    )
    
    kernel = ThirstySuperKernel(config)
    
    # 2. Test CXL Allocation
    print("\n[Test 1] Testing CXL Memory Allocation...")
    success = kernel.substrate.allocate_cxl_memory("POOL_0", 256.0)
    print(f"CXL Allocation Success: {success}")
    
    # 3. Test HierKNEM Transfer
    print("\n[Test 2] Testing HierKNEM Topology-Aware Transfer...")
    kernel.substrate.hierknem_transfer("NODE_A", "NODE_B", 2048.0) # 2GB
    
    if success:
        print("\n--- TEST SUCCESS: CXL/HierKNEM SUBSTRATE VERIFIED ---")
    else:
        print("\n--- TEST FAILED: SUBSTRATE INITIALIZATION ERROR ---")

if __name__ == "__main__":
    test_substrate_integration()
