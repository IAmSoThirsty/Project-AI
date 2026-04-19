"""Tests for governed VR ingress routes."""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.vr_routes import MAX_QUEUE_SIZE, VRCommand, command_queue, send_command

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_command_queue():
    """Ensure test isolation for the in-memory command queue."""
    command_queue.clear()
    yield
    command_queue.clear()


def test_vr_policy_endpoint_exposes_required_sections():
    response = client.get("/vr/policy")
    assert response.status_code == 200

    data = response.json()
    assert "observer_only" in data
    assert "genesis_interaction" in data
    assert "requirements" in data


def test_observer_command_is_queued_without_governance_token():
    payload = {
        "type": "DisplayText",
        "params": {"Text": "Observer update"},
        "source": "host_operator",
        "channel": "observer",
    }

    response = client.post("/vr/command", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "queued"
    assert data["mode"] == "observation"
    assert data["queue_size"] == 1


def test_observer_command_type_is_normalized_before_queueing():
    payload = {
        "type": " Heartbeat ",
        "params": {"alive": True},
        "source": "system",
        "channel": "observer",
    }

    response = client.post("/vr/command", json=payload)
    assert response.status_code == 200

    queued = client.get("/vr/commands").json()
    assert queued[0]["type"] == "Heartbeat"


def test_genesis_interaction_requires_genesis_channel():
    payload = {
        "type": "MoveOrb",
        "params": {"x": 0.1, "y": 0.2, "z": 0.3},
        "source": "host_operator",
        "channel": "observer",
        "governance_token": {"final_verdict": "allow", "intent_hash": "abc123"},
    }

    response = client.post("/vr/command", json=payload)
    assert response.status_code == 403
    assert "genesis_entity" in response.json()["detail"]


def test_genesis_interaction_requires_governance_allow_token():
    payload = {
        "type": "MoveOrb",
        "params": {"x": 0.1, "y": 0.2, "z": 0.3},
        "source": "genesis_entity",
        "channel": "genesis_entity",
    }

    response = client.post("/vr/command", json=payload)
    assert response.status_code == 403
    assert "Governance approval token required" in response.json()["detail"]


def test_genesis_interaction_is_queued_with_valid_governance_token():
    payload = {
        "type": "PlayAnimation",
        "params": {"name": "genesis_wave"},
        "source": "genesis_entity",
        "channel": "genesis_entity",
        "governance_token": {"final_verdict": "allow", "intent_hash": "intent-42"},
    }

    response = client.post("/vr/command", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["mode"] == "genesis_interaction"
    assert data["queue_size"] == 1


def test_unknown_command_type_is_rejected_under_observer_policy():
    payload = {
        "type": "DeleteWorld",
        "params": {},
        "source": "host_operator",
        "channel": "observer",
    }

    response = client.post("/vr/command", json=payload)
    assert response.status_code == 400
    assert "not allowed under observer policy" in response.json()["detail"]


def test_commands_since_filters_older_entries():
    first = {
        "type": "DisplayText",
        "params": {"Text": "first"},
        "timestamp": 100.0,
        "source": "host_operator",
        "channel": "observer",
    }
    second = {
        "type": "Heartbeat",
        "params": {"alive": True},
        "timestamp": 200.0,
        "source": "system",
        "channel": "observer",
    }

    assert client.post("/vr/command", json=first).status_code == 200
    assert client.post("/vr/command", json=second).status_code == 200

    response = client.get("/vr/commands", params={"since": 150.0})
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "Heartbeat"
    assert data[0]["timestamp"] == 200.0


def test_command_queue_trims_oldest_entries_at_limit():
    for index in range(MAX_QUEUE_SIZE + 5):
        result = send_command(
            VRCommand(
                type="Heartbeat",
                params={"index": index},
                timestamp=float(index + 1),
                source="system",
                channel="observer",
            )
        )
        assert result["status"] == "queued"

    response = client.get("/vr/commands", params={"since": 0})
    assert response.status_code == 200

    data = response.json()
    assert len(data) == MAX_QUEUE_SIZE
    assert data[0]["params"]["index"] == 5
    assert data[-1]["params"]["index"] == MAX_QUEUE_SIZE + 4
