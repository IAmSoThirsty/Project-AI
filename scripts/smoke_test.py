# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / smoke_test.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / smoke_test.py

#
# COMPLIANCE: Regulator-Ready / UTF-8                                          #


# SOVEREIGN SMOKE TEST
# Validation of Health & Security Enforcement

import requests
import json
import time
import os

# Sovereign Metadata
# Date: 2026-03-10 | Time: 19:35 | Status: Active | Tier: Master

def run_smoke_test():
    print("=== STARTING SOVEREIGN SMOKE TEST v2.6 ===")
    
    # 0. Boot Services (Trigger background Flask threads)
    print("\n[0] Booting Services...")
    try:
        # Importing the module triggers its background thread
        import src.services.TemporalDissonanceBridge as bridge_svc
        print("TemporalDissonanceBridge signal sent.")
    except Exception as e:
        print(f"FAILED TO BOOT SERVICES: {e}")

    # 1. Health Checks
    print("\n[1] Microservice Health Check (Waiting 3s for Flask boot)...")
    time.sleep(3)
    
    services = [
        ("temporal-dissonance-bridge", "http://localhost:8001/health")
    ]
    
    for name, url in services:
        try:
            r = requests.get(url, timeout=5)
            print(f"{name:25} -> {r.status_code} {r.json()}")
        except Exception as e:
            print(f"{name:25} -> DOWN/UNREACHABLE ({e})")

    # 2. Constitutional Enforcement & Forensic Test:
    print("\n[2] Constitutional Enforcement & Forensic Test:")
    
    # Simulate a violation
    payload = {
        "mutates_state": True,
        "trust_delta": -50,
        "is_agent": True,
        "audit_span_id": "audit_smoke_v28"
    }
    
    try:
        from src.security.thirstys_constitution import enforce
        
        print("Triggering intentional violation (Rule 001)...")
        result = enforce("critical_op", payload)
        
        print(f"Allowed: {result['allowed']}")
        print(f"Reason: {result['reason']}")
        print(f"Audit Hash: {result.get('audit_hash')}")

        # Check Audit Trail (Binary v2.8)
        print("\n[3] Verifying Binary Audit Trail (.tscgb):")
        if os.path.exists('audit_trail.tscgb'):
            from scripts.audit_decoder import decode_tscgb
            records = decode_tscgb('audit_trail.tscgb')
            
            if records:
                print(f"Records found in binary audit: {len(records)} [PASS]")
                violation_data = records[-1]
                if 'snapshot' in violation_data:
                    print("Snapshot found in binary record! [PASS]")
                    print(f"Snapshot Time: {violation_data['snapshot']['timestamp']}")
                    
                    # Storage Reduction Proxy Check
                    json_size = len(json.dumps(violation_data).encode())
                    binary_size = os.path.getsize('audit_trail.tscgb') # simplified for test
                    print(f"Simulated JSON Size: {json_size} bytes")
                    print(f"Binary Log File Size: {binary_size} bytes")
                else:
                    print("Snapshot MISSING from binary record! [FAIL]")
            else:
                print("No records decoded from binary log! [FAIL]")
        else:
            print("Binary audit trail file (.tscgb) NOT FOUND! [FAIL]")
            
    except ImportError as e:
        print(f"COULD NOT IMPORT COMPONENTS: {e} [FAIL]")
    except Exception as e:
        print(f"ERR IN TEST EXECUTION: {e}")

    # 4. Forensic Integrity Verification (v2.7/v2.8 Upgrade)
    print("\n[4] Verifying Audit Hash Integrity (from Binary):")
    import hashlib
    if 'violation_data' in locals() and 'audit_hash' in violation_data:
        snapshot_data = json.dumps(
            violation_data['snapshot'],
            sort_keys=True
        ).encode()

        computed_hash = hashlib.sha256(snapshot_data).hexdigest()

        if computed_hash == violation_data['audit_hash']:
            print("Audit hash VALID [PASS]")
        else:
            print(f"Audit hash MISMATCH [TAMPER DETECTED]")
            print(f"Computed: {computed_hash}")
            print(f"Recorded: {violation_data['audit_hash']}")
    else:
        print("Audit hash data unavailable for integrity check [FAIL]")

if __name__ == "__main__":
    run_smoke_test()
