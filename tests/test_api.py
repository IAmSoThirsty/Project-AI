"""
API Tests - Project AI Governance Backend
"""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "governance-online"


def test_tarl():
    """Test TARL rules endpoint"""
    response = client.get("/tarl")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0"
    assert "rules" in data


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Project AI Governance Host"


def test_intent_read_allow():
    """Test allowed read intent"""
    intent = {
        "actor": "human",
        "action": "read",
        "target": "/data",
        "context": {},
        "origin": "test",
    }
    response = client.post("/intent", json=intent)
    assert response.status_code == 200
    data = response.json()
    assert data["governance"]["final_verdict"] == "allow"


def test_intent_write_deny_agent():
    """Test denied write intent (agent not allowed)"""
    intent = {
        "actor": "agent",
        "action": "write",
        "target": "/data",
        "context": {},
        "origin": "test",
    }
    response = client.post("/intent", json=intent)
    assert response.status_code == 403


def test_intent_execute_deny():
    """Test denied execute intent (high risk)"""
    intent = {
        "actor": "system",
        "action": "execute",
        "target": "/code",
        "context": {},
        "origin": "test",
    }
    response = client.post("/intent", json=intent)
    assert response.status_code == 403


def test_intent_mutate_deny():
    """Test denied mutate intent (critical risk)"""
    intent = {
        "actor": "human",
        "action": "mutate",
        "target": "/governance",
        "context": {},
        "origin": "test",
    }
    response = client.post("/intent", json=intent)
    assert response.status_code == 403


def test_governance_result_structure():
    """Test governance result structure"""
    intent = {
        "actor": "human",
        "action": "read",
        "target": "/test",
        "context": {},
        "origin": "test",
    }
    response = client.post("/intent", json=intent)
    data = response.json()
    gov = data["governance"]

    assert "intent_hash" in gov
    assert "tarl_version" in gov
    assert "votes" in gov
    assert "final_verdict" in gov
    assert "timestamp" in gov
    assert len(gov["votes"]) == 2  # Galahad + Cerberus


def test_pillar_votes():
    """Test that both pillars vote"""
    intent = {
        "actor": "human",
        "action": "read",
        "target": "/test",
        "context": {},
        "origin": "test",
    }
    response = client.post("/intent", json=intent)
    votes = response.json()["governance"]["votes"]

    pillars = {v["pillar"] for v in votes}
    assert "Galahad" in pillars
    assert "Cerberus" in pillars


def test_audit_endpoint():
    """Test audit log retrieval"""
    # Submit an intent first to create audit entry
    intent = {
        "actor": "human",
        "action": "read",
        "target": "/audit_test",
        "context": {},
        "origin": "test",
    }
    client.post("/intent", json=intent)

    # Read audit log
    response = client.get("/audit")
    assert response.status_code == 200
    data = response.json()
    assert "tarl_version" in data
    assert "tarl_signature" in data
    assert "records" in data
    assert len(data["tarl_signature"]) == 64  # SHA256 hash


def test_tarl_signature():
    """Test TARL immutability signature"""
    response = client.get("/audit")
    data = response.json()
    # Signature should be consistent
    assert data["tarl_signature"] is not None
    assert isinstance(data["tarl_signature"], str)


def test_governed_execute_allow():
    """Test governed execution (allowed)"""
    intent = {
        "actor": "human",
        "action": "read",
        "target": "/execute_test",
        "context": {},
        "origin": "test",
    }
    response = client.post("/execute", json=intent)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Execution completed under governance"
    assert "governance" in data
    assert "execution" in data
    assert data["execution"]["status"] == "executed"


def test_governed_execute_deny():
    """Test governed execution (denied)"""
    intent = {
        "actor": "agent",
        "action": "mutate",
        "target": "/dangerous",
        "context": {},
        "origin": "test",
    }
    response = client.post("/execute", json=intent)
    assert response.status_code == 403
    data = response.json()
    assert "Execution denied by governance" in data["detail"]["message"]


def test_audit_persistence():
    """Test audit log persistence across requests"""
    # Submit multiple intents
    for i in range(3):
        intent = {
            "actor": "human",
            "action": "read",
            "target": f"/test_{i}",
            "context": {},
            "origin": "test",
        }
        client.post("/intent", json=intent)

    # Verify audit contains entries
    response = client.get("/audit?limit=10")
    data = response.json()
    assert len(data["records"]) >= 3


def test_sandbox_executor():
    """Test sandbox execution returns expected structure"""
    intent = {
        "actor": "human",
        "action": "read",
        "target": "/sandbox_test",
        "context": {},
        "origin": "test",
    }
    response = client.post("/execute", json=intent)
    execution = response.json()["execution"]

    assert execution["status"] == "executed"
    assert execution["note"] == "Sandbox execution completed"
    assert execution["target"] == "/sandbox_test"
