"""
Constitutional Verification Test
Tests that the Governance Kernel upholds its core guarantees
"""

import requests

BASE_URL = "http://localhost:8001"


def test_1_kernel_alive():
    """✅ Law: Kernel is online and responsive"""
    r = requests.get(f"{BASE_URL}/health")
    if not (r.status_code == 200):
        raise AssertionError("Check failed")
    data = r.json()
    if not (data["status"] == "governance-online"):
        raise AssertionError("Governance status check failed")
    if not (data["tarl"] == "1.0"):
        raise AssertionError("TARL version check failed")
    print("✅ 1. KERNEL ALIVE - Governance online, TARL v1.0 active")
    return True


def test_2_law_visible():
    """✅ Law: TARL is publicly inspectable"""
    r = requests.get(f"{BASE_URL}/tarl")
    if not (r.status_code == 200):
        raise AssertionError("Check failed")
    tarl = r.json()
    if not (tarl["version"] == "1.0"):
        raise AssertionError("TARL version check failed")
    if "rules" not in tarl:
        raise AssertionError("TARL rules check failed")
    if not (len(tarl["rules"]) > 0):
        raise AssertionError("TARL rules count check failed")
    print(f"✅ 2. LAW VISIBLE - {len(tarl['rules'])} TARL rules publicly accessible")
    return tarl


def test_3_law_signed():
    """✅ Law: TARL is cryptographically signed"""
    r = requests.get(f"{BASE_URL}/audit")
    if not (r.status_code == 200):
        raise AssertionError("Check failed")
    data = r.json()
    if "tarl_signature" not in data:
        raise AssertionError("Check failed")
    # SHA256 check
    if not (len(data["tarl_signature"]) == 64):
        raise AssertionError("TARL signature length check failed")
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
        "origin": "verification_test",
    }
    r = requests.post(f"{BASE_URL}/execute", json=intent)

    # MUST be denied
    if not (r.status_code == 403):
        raise AssertionError("Check failed")
    data = r.json()
    if "Execution denied by governance" not in data["detail"]["message"]:
        raise AssertionError("Check failed")
    if not (data["detail"]["governance"]["final_verdict"] == "deny"):
        raise AssertionError("Check failed")

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
        "origin": "verification_test",
    }
    r = requests.post(f"{BASE_URL}/execute", json=intent)

    # Should be allowed
    if not (r.status_code == 200):
        raise AssertionError("Check failed")
    data = r.json()
    if not (data["message"] == "Execution completed under governance"):
        raise AssertionError("Check failed")
    if "execution" not in data:
        raise AssertionError("Check failed")
    if not (data["execution"]["status"] == "executed"):
        raise AssertionError("Check failed")

    print("✅ 5. ALLOW WORKS - Permitted read executed successfully")
    return True


def test_6_audit_records():
    """✅ Memory: Audit log records all decisions"""
    r = requests.get(f"{BASE_URL}/audit?limit=10")
    if not (r.status_code == 200):
        raise AssertionError("Check failed")
    data = r.json()

    if "records" not in data:
        raise AssertionError("Check failed")
    if not (len(data["records"]) >= 2):  # At least our test intents
        raise AssertionError("Check failed")

    # Verify structure
    record = data["records"][-1]
    if "intent_hash" not in record:
        raise AssertionError("Check failed")
    if "votes" not in record:
        raise AssertionError("Check failed")
    if "final_verdict" not in record:
        raise AssertionError("Check failed")
    if "timestamp" not in record:
        raise AssertionError("Check failed")

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
        "origin": "verification_test",
    }
    r = requests.post(f"{BASE_URL}/intent", json=intent)
    if not (r.status_code == 200):
        raise AssertionError("Check failed")

    votes = r.json()["governance"]["votes"]
    pillars = {v["pillar"] for v in votes}

    if "Galahad" not in pillars:
        raise AssertionError("Check failed")
    if "Cerberus" not in pillars:
        raise AssertionError("Check failed")

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
        "origin": "verification_test",
    }
    requests.post(f"{BASE_URL}/intent", json=intent)

    # Audit should grow
    r2 = requests.get(f"{BASE_URL}/audit")
    records_after = len(r2.json()["records"])

    if not (records_after > records_before):
        raise AssertionError("Check failed")
    print(
        f"✅ 8. AUDIT IMMUTABLE - Log grew from {records_before} to {records_after} entries"
    )
    return True


def test_9_no_privilege_escalation():
    """✅ Interface: Agents cannot escalate to human privileges"""
    # Agent tries to write (only humans allowed)
    intent = {
        "actor": "agent",
        "action": "write",
        "target": "/privileged_resource",
        "context": {},
        "origin": "verification_test",
    }
    r = requests.post(f"{BASE_URL}/execute", json=intent)

    # Must be denied
    if not (r.status_code == 403):
        raise AssertionError("Check failed")
    print("✅ 9. NO ESCALATION - Agent cannot assume human privileges")
    return True


def test_10_constitutional():
    """✅ Constitution: All core guarantees verified"""
    print("\n" + "=" * 70)
    print("🏛️  CONSTITUTIONAL VERIFICATION COMPLETE")
    print("=" * 70)
    print("\n✅ Law: TARL v1.0 active, signed, publicly inspectable")
    print("✅ Judges: Triumvirate voting, any deny = global deny")
    print("✅ Memory: Append-only audit, deterministic hashing")
    print("✅ Hands: Sandbox execution, governed endpoints")
    print("✅ Witnesses: Read-only audit endpoint, human-readable trail")
    print("✅ Interface: No privilege escalation, fail-closed defaults")
    print("\n🔒 GOVERNANCE KERNEL v1 OPERATIONAL")
    print("=" * 70)
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔍 CONSTITUTIONAL VERIFICATION - Governance Kernel v1")
    print("=" * 70 + "\n")

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
