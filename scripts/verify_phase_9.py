# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / verify_phase_9.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / verify_phase_9.py

import sys
import os
import json
from pathlib import Path



               #
# COMPLIANCE: Regulator-Ready / UTF-8                                          #



def verify_orchestration():
    print("--- PROJECT-AI PHASE 9 VERIFICATION SWEEP ---")
    
    # 1. Check Service Mesh Sync
    print("[1/3] Verifying Service Mesh Synchronizer...")
    try:
        from src.orchestrator.service_mesh_sync import ServiceMeshSync
        syncer = ServiceMeshSync()
        syncer.sync()
        manifest_path = Path("docs/reports/SERVICE_MESH_MANIFEST.json")
        if manifest_path.exists():
            print(f"  SUCCESS: Service Mesh Manifest generated at {manifest_path}")
            with open(manifest_path, 'r', encoding='utf-8') as f:
                # Skip header
                lines = f.readlines()
                json_data = "".join(lines[4:])
                data = json.loads(json_data)
                print(f"  Services Discovered: {data.get('service_count', 0)}")
        else:
            print("  FAILURE: Service Mesh Manifest NOT found.")
    except Exception as e:
        print(f"  ERROR: Service Mesh Sync failed: {e}")

    # 2. Check Bootstrap Orchestrator (Subsystem Discovery)
    print("\n[2/3] Verifying Bootstrap Orchestrator Alignment...")
    try:
        from src.app.core.bootstrap_orchestrator import BootstrapOrchestrator
        orchestrator = BootstrapOrchestrator()
        # Verify thirsty bootstrap generation (relative to script)
        thirsty_path = Path("src/app/core/bootstrap.thirsty")
        if thirsty_path.exists():
            print(f"  SUCCESS: Sovereign Thirsty Bootstrap manifest found at {thirsty_path}")
        else:
            print(f"  FAILURE: {thirsty_path} NOT generated.")
    except Exception as e:
        print(f"  ERROR: Orchestrator check failed: {e}")

    # 3. Check Constitution S2S Rules
    print("\n[3/3] Verifying S2S Identity Enforcement Rules...")
    try:
        from src.security.thirstys_constitution import enforce
        # Test valid action
        res = enforce("ping", {"is_s2s": True, "s2s_verified": True})
        if res["allowed"]:
            print("  SUCCESS: Verified S2S signal allowed.")
        else:
            print("  FAILURE: Verified S2S signal blocked unexpectedly.")
            
        # Test violation
        res = enforce("ping", {"is_s2s": True, "s2s_verified": False})
        if not res["allowed"] and "verified S2S identity" in res["reason"]:
            print("  SUCCESS: Unverified S2S signal blocked as expected (Rule 005).")
        else:
            print("  FAILURE: Unverified S2S signal NOT correctly blocked.")
    except Exception as e:
        print(f"  ERROR: Constitution check failed: {e}")

    print("\n--- VERIFICATION SWEEP COMPLETE ---")

if __name__ == "__main__":
    # Add src to path
    sys.path.append(str(Path("src").resolve()))
    verify_orchestration()
