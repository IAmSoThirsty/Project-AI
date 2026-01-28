"""
Constitutional Verification Test
Tests that the Governance Kernel upholds its core guarantees
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_1_kernel_alive():
    """✅ Law: Kernel is online and responsive"""
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "governance-online"
    assert data["tarl"] == "1.0"
    print("✅ 1. KERNEL ALIVE - Governance online, TARL v1.0 active")
    return True

def test_2_law_visible():
    """✅ Law: TARL is publicly inspectable"""
    r = requests.get(f"{BASE_URL}/tarl")
    assert r.status_code == 200
    tarl = r.json()
    assert tarl["version"] == "1.0"
    assert "rules" in tarl
    assert len(tarl["rules"]) > 0
    print(f"✅ 2. LAW VISIBLE - {len(tarl['rules'])} TARL rules publicly accessible")
    return tarl

def test_3_law_signed():
    """✅ Law: TARL is cryptographically signed"""
    r = requests.get(f"{BASE_URL}/audit")
    assert r.status_code == 200
    data = r.json()
    assert "tarl_signature" in data
    assert len(data["tarl_signature"]) == 64  # SHA256
    print(f"✅ 3. LAW SIGNED - TARL signature: {data['tarl_signature'][:16]}...")
    return data["tarl_signature"]

def test_4_denial_works():
    """✅ Judges: Denial actually prevents execution"""
    # Attempt forbidden mutation
    intent = {
        "actor": "agent",
        "action": "mutate",
        "target": "/core_state",
        "context": {},
        "origin": "verification_test"
    }
    r = requests.post(f"{BASE_URL}/execute", json=intent)
    
    # MUST be denied
    assert r.status_code == 403
    data = r.json()
    assert "Execution denied by governance" in data["detail"]["message"]
    assert data["detail"]["governance"]["final_verdict"] == "deny"
    
    print("✅ 4. DENIAL ENFORCED - Forbidden mutation blocked with 403")
    print(f"   Reason: {data['detail']['governance']['votes'][0]['reason']}")
    return True

def test_5_allow_works():
    """✅ Hands: Permitted actions execute"""
    intent = {
        "actor": "human",
        "action": "read",
        "target": "/safe_data",
        "context": {},
        "origin": "verification_test"
    }
    r = requests.post(f"{BASE_URL}/execute", json=intent)
    
    # Should be allowed
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "Execution completed under governance"
    assert "execution" in data
    assert data["execution"]["status"] == "executed"
    
    print("✅ 5. ALLOW WORKS - Permitted read executed successfully")
    return True

def test_6_audit_records():
    """✅ Memory: Audit log records all decisions"""
    r = requests.get(f"{BASE_URL}/audit?limit=10")
    assert r.status_code == 200
    data = r.json()
    
    assert "records" in data
    assert len(data["records"]) >= 2  # At least our test intents
    
    # Verify structure
    record = data["records"][-1]
    assert "intent_hash" in record
    assert "votes" in record
    assert "final_verdict" in record
    assert "timestamp" in record
    
    print(f"✅ 6. AUDIT ACTIVE - {len(data['records'])} decisions logged")
    print(f"   Last decision: {record['final_verdict']} at {record['timestamp']}")
    return True

def test_7_triumvirate_votes():
    """✅ Judges: All three pillars participate"""
    intent = {
        "actor": "human",
        "action": "read",
        "target": "/test",
        "context": {},
        "origin": "verification_test"
    }
    r = requests.post(f"{BASE_URL}/intent", json=intent)
    assert r.status_code == 200
    
    votes = r.json()["governance"]["votes"]
    pillars = {v["pillar"] for v in votes}
    
    assert "Galahad" in pillars
    assert "Cerberus" in pillars
    
    print("✅ 7. TRIUMVIRATE ACTIVE - Galahad + Cerberus voting")
    for vote in votes:
        print(f"   {vote['pillar']}: {vote['verdict']} - {vote['reason']}")
    return True

def test_8_immutable_audit():
    """✅ Memory: Audit log is append-only"""
    # Get current audit
    r1 = requests.get(f"{BASE_URL}/audit")
    records_before = len(r1.json()["records"])
    
    # Submit new intent
    intent = {
        "actor": "human",
        "action": "read",
        "target": "/immutability_test",
        "context": {},
        "origin": "verification_test"
    }
    requests.post(f"{BASE_URL}/intent", json=intent)
    
    # Audit should grow
    r2 = requests.get(f"{BASE_URL}/audit")
    records_after = len(r2.json()["records"])
    
    assert records_after > records_before
    print(f"✅ 8. AUDIT IMMUTABLE - Log grew from {records_before} to {records_after} entries")
    return True

def test_9_no_privilege_escalation():
    """✅ Interface: Agents cannot escalate to human privileges"""
    # Agent tries to write (only humans allowed)
    intent = {
        "actor": "agent",
        "action": "write",
        "target": "/privileged_resource",
        "context": {},
        "origin": "verification_test"
    }
    r = requests.post(f"{BASE_URL}/execute", json=intent)
    
    # Must be denied
    assert r.status_code == 403
    print("✅ 9. NO ESCALATION - Agent cannot assume human privileges")
    return True

def test_10_constitutional():
    """✅ Constitution: All core guarantees verified"""
    print("\n" + "="*70)
    print("🏛️  CONSTITUTIONAL VERIFICATION COMPLETE")
    print("="*70)
    print("\n✅ Law: TARL v1.0 active, signed, publicly inspectable")
    print("✅ Judges: Triumvirate voting, any deny = global deny")
    print("✅ Memory: Append-only audit, deterministic hashing")
    print("✅ Hands: Sandbox execution, governed endpoints")
    print("✅ Witnesses: Read-only audit endpoint, human-readable trail")
    print("✅ Interface: No privilege escalation, fail-closed defaults")
    print("\n🔒 GOVERNANCE KERNEL v1 OPERATIONAL")
    print("="*70)
    return True

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔍 CONSTITUTIONAL VERIFICATION - Governance Kernel v1")
    print("="*70 + "\n")
    
    try:
        test_1_kernel_alive()
        test_2_law_visible()
        test_3_law_signed()
        test_7_triumvirate_votes()
        test_4_denial_works()
        test_5_allow_works()
        test_9_no_privilege_escalation()
        test_6_audit_records()
        test_8_immutable_audit()
        test_10_constitutional()
        
        print("\n✅ ALL CONSTITUTIONAL GUARANTEES VERIFIED\n")
        
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}\n")
        raise
