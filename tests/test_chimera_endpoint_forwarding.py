import json
import time
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from governance.triumvirate_server import app


SECRET = "phase8-secret"


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def phase8_context(monkeypatch: pytest.MonkeyPatch, tmp_path):
    import app.security.chimera_bridge as bridge_module
    from app.core.governance_observability import get_collector

    monkeypatch.setenv("CHIMERA_WEBHOOK_SECRET", SECRET)
    monkeypatch.setattr(bridge_module, "_DRIFT_DIR", tmp_path / "drift")
    monkeypatch.setattr(bridge_module, "_DENY_DIR", tmp_path / "deny")
    bridge_module._REPLAY_CACHE.clear()
    bridge_module._bridge = None
    get_collector().clear()

    yield SimpleNamespace(bridge_module=bridge_module, tmp_path=tmp_path)

    bridge_module._REPLAY_CACHE.clear()
    bridge_module._bridge = None
    get_collector().clear()


def _verdict_event(event_id: str = "evt-verdict", timestamp: Any = None) -> dict[str, Any]:
    return {
        "event": "threat_verdict",
        "event_id": event_id,
        "timestamp": time.time() if timestamp is None else timestamp,
        "ip": "203.0.113.9",
        "verdict": "ATTACKER",
        "score": 42,
        "sid": "sid-1",
        "path": "/admin",
    }


def _canary_event(event_id: str = "evt-canary", timestamp: Any = None) -> dict[str, Any]:
    return {
        "event": "canary_hit",
        "event_id": event_id,
        "timestamp": time.time() if timestamp is None else timestamp,
        "ip": "203.0.113.9",
        "sid": "sid-1",
        "hits": [
            {
                "token": "secret-token-value-that-must-not-be-logged",
                "kind": "deploy-key",
                "form": "header",
            }
        ],
    }


def _signed_payload(
    bridge_module,
    event: dict[str, Any],
    *,
    body_signature: bool = True,
    header_signature: bool = True,
) -> tuple[dict[str, Any], dict[str, str], str]:
    signature = bridge_module.sign_webhook_event(event, secret=SECRET)
    body = dict(event)
    if body_signature:
        body["signature"] = signature

    headers: dict[str, str] = {}
    if header_signature:
        headers = {
            "X-Chimera-Signature": f"sha256={signature}",
            "X-Chimera-Event-Id": str(event.get("event_id") or event.get("nonce") or ""),
            "X-Chimera-Timestamp": str(event.get("timestamp") or event.get("ts") or ""),
        }
    return body, headers, signature


def _values(obj: Any) -> list[str]:
    if isinstance(obj, dict):
        found: list[str] = []
        for value in obj.values():
            found.extend(_values(value))
        return found
    if isinstance(obj, list):
        found = []
        for value in obj:
            found.extend(_values(value))
        return found
    return [str(obj)]


def test_verdict_rejects_missing_signature(client: TestClient, phase8_context):
    body, _, _ = _signed_payload(
        phase8_context.bridge_module,
        _verdict_event("evt-missing-verdict-sig"),
        body_signature=False,
        header_signature=False,
    )

    response = client.post("/chimera/verdict", json=body)

    assert response.status_code == 401


def test_canary_rejects_missing_signature(client: TestClient, phase8_context):
    body, _, _ = _signed_payload(
        phase8_context.bridge_module,
        _canary_event("evt-missing-canary-sig"),
        body_signature=False,
        header_signature=False,
    )

    response = client.post("/chimera/canary", json=body)

    assert response.status_code == 401


def test_invalid_signature_is_rejected(client: TestClient, phase8_context):
    body, headers, _ = _signed_payload(
        phase8_context.bridge_module,
        _verdict_event("evt-invalid-signature"),
        body_signature=False,
    )
    headers["X-Chimera-Signature"] = "sha256=bad-signature"

    response = client.post("/chimera/verdict", json=body, headers=headers)

    assert response.status_code == 401


def test_stale_timestamp_is_rejected(client: TestClient, phase8_context):
    event = _verdict_event("evt-stale", timestamp=time.time() - 301)
    body, headers, _ = _signed_payload(phase8_context.bridge_module, event)

    response = client.post("/chimera/verdict", json=body, headers=headers)

    assert response.status_code == 401


def test_missing_event_id_and_nonce_is_rejected(client: TestClient, phase8_context):
    event = _verdict_event("evt-unused")
    event.pop("event_id")
    body, headers, _ = _signed_payload(phase8_context.bridge_module, event)

    response = client.post("/chimera/verdict", json=body, headers=headers)

    assert response.status_code == 401


def test_replayed_event_id_is_rejected(client: TestClient, phase8_context):
    event = _verdict_event("evt-replay")
    body, headers, _ = _signed_payload(phase8_context.bridge_module, event)

    first = client.post("/chimera/verdict", json=body, headers=headers)
    second = client.post("/chimera/verdict", json=body, headers=headers)

    assert first.status_code == 200
    assert first.json()["status"] == "ok"
    assert second.status_code == 401


def test_header_body_signature_mismatch_is_rejected(client: TestClient, phase8_context):
    body, headers, _ = _signed_payload(
        phase8_context.bridge_module,
        _verdict_event("evt-signature-mismatch"),
    )
    headers["X-Chimera-Signature"] = "sha256=bad-signature"

    response = client.post("/chimera/verdict", json=body, headers=headers)

    assert response.status_code == 401


def test_header_body_event_id_mismatch_is_rejected(client: TestClient, phase8_context):
    body, headers, _ = _signed_payload(
        phase8_context.bridge_module,
        _verdict_event("evt-body-id"),
    )
    headers["X-Chimera-Event-Id"] = "evt-header-id"

    response = client.post("/chimera/verdict", json=body, headers=headers)

    assert response.status_code == 401


def test_header_body_timestamp_mismatch_is_rejected(client: TestClient, phase8_context):
    body, headers, _ = _signed_payload(
        phase8_context.bridge_module,
        _verdict_event("evt-timestamp-mismatch"),
    )
    headers["X-Chimera-Timestamp"] = str(float(headers["X-Chimera-Timestamp"]) + 1)

    response = client.post("/chimera/verdict", json=body, headers=headers)

    assert response.status_code == 401


def test_malformed_verdict_payload_returns_400(client: TestClient, phase8_context):
    event = _verdict_event("evt-malformed")
    event.pop("verdict")
    body, headers, _ = _signed_payload(phase8_context.bridge_module, event)

    response = client.post("/chimera/verdict", json=body, headers=headers)

    assert response.status_code == 400


def test_valid_signed_verdict_delegates_through_authenticated_event(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    phase8_context,
):
    import app.security.chimera_bridge as bridge_module

    calls = []

    class FakeBridge:
        def receive_authenticated_event(self, event, *, signature):
            calls.append({"event": event, "signature": signature})
            return {"accepted": True, "event": "threat_verdict"}

    monkeypatch.setattr(bridge_module, "get_bridge", lambda: FakeBridge())
    body, headers, signature = _signed_payload(
        phase8_context.bridge_module,
        _verdict_event("evt-delegate-verdict"),
        body_signature=False,
    )

    response = client.post("/chimera/verdict", json=body, headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "ip": "203.0.113.9",
        "verdict": "ATTACKER",
    }
    assert calls == [
        {
            "event": body,
            "signature": f"sha256={signature}",
        }
    ]


def test_valid_signed_canary_delegates_through_authenticated_event(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    phase8_context,
):
    import app.security.chimera_bridge as bridge_module

    calls = []

    class FakeBridge:
        def receive_authenticated_event(self, event, *, signature):
            calls.append({"event": event, "signature": signature})
            return {"accepted": True, "event": "canary_hit"}

    monkeypatch.setattr(bridge_module, "get_bridge", lambda: FakeBridge())
    body, headers, signature = _signed_payload(
        phase8_context.bridge_module,
        _canary_event("evt-delegate-canary"),
        body_signature=False,
    )

    response = client.post("/chimera/canary", json=body, headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "ip": "203.0.113.9",
        "hits": 1,
    }
    assert calls == [
        {
            "event": body,
            "signature": f"sha256={signature}",
        }
    ]


def test_valid_signed_verdict_preserves_drift_alert_compatibility_fields(
    client: TestClient,
    phase8_context,
):
    body, headers, _ = _signed_payload(
        phase8_context.bridge_module,
        _verdict_event("evt-drift-compat"),
    )

    response = client.post("/chimera/verdict", json=body, headers=headers)

    assert response.status_code == 200
    files = list((phase8_context.tmp_path / "drift").glob("chimera_verdict_*.json"))
    assert len(files) == 1
    alert = json.loads(files[0].read_text(encoding="utf-8"))
    for key in (
        "source",
        "event",
        "ip",
        "verdict",
        "score",
        "sid",
        "path",
        "timestamp",
        "target_member",
    ):
        assert key in alert
    assert alert["non_authoritative"] is True


def test_valid_signed_canary_preserves_alert_compatibility_fields(
    client: TestClient,
    phase8_context,
):
    body, headers, _ = _signed_payload(
        phase8_context.bridge_module,
        _canary_event("evt-canary-compat"),
    )

    response = client.post("/chimera/canary", json=body, headers=headers)

    assert response.status_code == 200
    files = list((phase8_context.tmp_path / "drift").glob("chimera_canary_*.json"))
    assert len(files) == 1
    alert = json.loads(files[0].read_text(encoding="utf-8"))
    for key in (
        "source",
        "event",
        "ip",
        "sid",
        "hits",
        "hit_count",
        "timestamp",
        "target_member",
        "severity",
    ):
        assert key in alert
    assert alert["non_authoritative"] is True


def test_accepted_endpoint_event_emits_governance_observation(
    client: TestClient,
    phase8_context,
):
    from app.core.governance_observability import get_collector

    body, headers, _ = _signed_payload(
        phase8_context.bridge_module,
        _verdict_event("evt-observation"),
    )

    response = client.post("/chimera/verdict", json=body, headers=headers)

    assert response.status_code == 200
    latest = get_collector().get_latest(1)[0]
    assert latest["domain"] == "security.chimera"
    assert latest["metadata"]["source"] == "chimera"
    assert latest["metadata"]["non_authoritative"] is True


def test_accepted_endpoint_event_relays_through_audit_manager(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    phase8_context,
):
    import app.governance.audit_manager as audit_manager

    calls = []

    class FakeAuditManager:
        def log_security_event(self, event_type, data=None, severity="info"):
            calls.append(
                {
                    "event_type": event_type,
                    "data": data,
                    "severity": severity,
                }
            )
            return True

    monkeypatch.setattr(audit_manager, "get_audit_manager", lambda: FakeAuditManager())
    body, headers, _ = _signed_payload(
        phase8_context.bridge_module,
        _verdict_event("evt-audit-manager"),
    )

    response = client.post("/chimera/verdict", json=body, headers=headers)

    assert response.status_code == 200
    assert calls
    assert calls[0]["event_type"] == "chimera.threat_verdict"
    assert calls[0]["data"]["non_authoritative"] is True


def test_receipt_degradation_remains_non_authoritative(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    phase8_context,
):
    import app.governance.audit_manager as audit_manager

    class FailingAuditManager:
        def log_security_event(self, event_type, data=None, severity="info"):
            raise RuntimeError("audit offline")

    monkeypatch.setattr(audit_manager, "get_audit_manager", lambda: FailingAuditManager())
    body, headers, _ = _signed_payload(
        phase8_context.bridge_module,
        _verdict_event("evt-degraded-receipt"),
    )

    response = client.post("/chimera/verdict", json=body, headers=headers)

    assert response.status_code == 200
    files = list((phase8_context.tmp_path / "drift").glob("chimera_verdict_*.json"))
    assert len(files) == 1
    alert = json.loads(files[0].read_text(encoding="utf-8"))
    assert alert["non_authoritative"] is True
    assert alert["receipt_degraded"] is True
    assert alert["receipts"]["audit_manager"]["ok"] is False


def test_endpoint_does_not_call_execution_gate_or_octoreflex(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    phase8_context,
):
    import app.core.execution_gate as execution_gate
    import app.core.octoreflex as octoreflex

    called = {"gate": 0, "octoreflex": 0}

    def fake_get_execution_gate():
        called["gate"] += 1
        raise AssertionError("ExecutionGate must not be called by Chimera endpoint")

    class FakeOctoReflex:
        def validate_action(self, *args, **kwargs):
            called["octoreflex"] += 1
            raise AssertionError("OctoReflex must not be called by Chimera endpoint")

    monkeypatch.setattr(execution_gate, "get_execution_gate", fake_get_execution_gate)
    monkeypatch.setattr(octoreflex, "get_octoreflex", lambda: FakeOctoReflex())
    body, headers, _ = _signed_payload(
        phase8_context.bridge_module,
        _canary_event("evt-no-gate-or-octo"),
    )

    response = client.post("/chimera/canary", json=body, headers=headers)

    assert response.status_code == 200
    assert called == {"gate": 0, "octoreflex": 0}


def test_endpoint_emits_no_public_allow_deny_halt(
    client: TestClient,
    phase8_context,
):
    body, headers, _ = _signed_payload(
        phase8_context.bridge_module,
        _canary_event("evt-no-public-decision"),
    )

    response = client.post("/chimera/canary", json=body, headers=headers)

    assert response.status_code == 200
    assert not {"ALLOW", "DENY", "HALT"}.intersection(_values(response.json()))


def test_endpoint_does_not_write_directly_to_sovereign_audit_log(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    phase8_context,
):
    import app.governance.sovereign_audit_log as sovereign_audit_log

    called = {"sovereign": 0}

    def fake_log_event(self, *args, **kwargs):
        called["sovereign"] += 1
        raise AssertionError("Endpoint must not write directly to SovereignAuditLog")

    monkeypatch.setattr(
        sovereign_audit_log.SovereignAuditLog,
        "log_event",
        fake_log_event,
    )
    body, headers, _ = _signed_payload(
        phase8_context.bridge_module,
        _verdict_event("evt-no-sovereign-direct"),
    )

    response = client.post("/chimera/verdict", json=body, headers=headers)

    assert response.status_code == 200
    assert called == {"sovereign": 0}
