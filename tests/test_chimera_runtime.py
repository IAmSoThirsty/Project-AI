import os
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest


def _run_chimera_script(tmp_path, script: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CHIMERA_DB"] = str(tmp_path / "chimera.db")
    env["CHIMERA_AUDIT"] = str(tmp_path / "audit.jsonl")
    env["CHIMERA_GOVERNANCE_DENY_DIR"] = str(tmp_path / "denials")
    env["CHIMERA_SECRET"] = "test-secret"
    env["CHIMERA_ENV"] = "dev"
    src_path = str(Path.cwd() / "src")
    env["PYTHONPATH"] = (
        src_path
        if not env.get("PYTHONPATH")
        else f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    )
    return subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        env=env,
        text=True,
    )


def test_governance_denial_boost_reads_signal_directory(tmp_path):
    script = r"""
import json
from pathlib import Path

from app.security.chimera import chimera

deny_dir = Path(chimera.GOVERNANCE_DENY_DIR)
deny_dir.mkdir(parents=True, exist_ok=True)
(deny_dir / "denial_1.json").write_text(json.dumps({"ip": "203.0.113.9"}), encoding="utf-8")
(deny_dir / "denial_2.json").write_text(json.dumps({"ip": "198.51.100.4"}), encoding="utf-8")

assert chimera._governance_denial_boost("203.0.113.9") == 1
assert chimera._governance_denial_boost("198.51.100.99") == 0
"""
    _run_chimera_script(tmp_path, script)


def test_canary_rotate_retires_old_manual_token_and_registers_new_one(tmp_path):
    script = r"""
from app.security.chimera import chimera

old_token = chimera.canary_register("unit-test")
new_token = chimera.canary_rotate("unit-test")

assert new_token != old_token
assert chimera.canary_scan(old_token) == []
hits = chimera.canary_scan(f"leaked {new_token}")
assert len(hits) == 1
assert hits[0]["token"] == new_token
assert hits[0]["kind"] == "unit-test"
"""
    _run_chimera_script(tmp_path, script)


def test_configured_upstream_proxy_decision_keeps_decoys_and_canaries_local(tmp_path):
    script = r"""
from app.security.chimera import chimera

assert chimera._should_proxy_request("GET", "/index.html", {"score": 0}, [], None)
assert not chimera._should_proxy_request("GET", "/index.html", {"score": 99}, [], None)
assert not chimera._should_proxy_request("GET", "/index.html", {"score": 0}, [{"token": "x"}], None)
assert not chimera._should_proxy_request("GET", "/.env", {"score": 0}, [], "env_leak")
"""
    _run_chimera_script(tmp_path, script)


def test_bridge_audit_relay_records_chimera_event(monkeypatch, tmp_path):
    import app.governance.acceptance_ledger as acceptance_ledger
    import app.security.chimera_bridge as bridge_module

    recorded = []

    class FakeLedger:
        def record_event(self, **kwargs):
            recorded.append(kwargs)

    monkeypatch.setattr(acceptance_ledger, "AcceptanceLedger", FakeLedger)
    monkeypatch.setattr(bridge_module, "_DRIFT_DIR", tmp_path / "drift")
    monkeypatch.setattr(bridge_module, "_DENY_DIR", tmp_path / "deny")

    bridge = bridge_module.ChimeraBridge()

    assert bridge._ship_to_ledger({"event": "proxy.pass", "ip": "203.0.113.9"})
    assert recorded == [
        {
            "event_type": "chimera.proxy.pass",
            "actor": "203.0.113.9",
            "metadata": {"event": "proxy.pass", "ip": "203.0.113.9"},
        }
    ]


def test_acceptance_ledger_record_event_appends_audit_lock(tmp_path):
    from app.governance.acceptance_ledger import AcceptanceLedger, AcceptanceType

    ledger = AcceptanceLedger(data_dir=str(tmp_path / "legal"))
    entry = ledger.record_event(
        event_type="chimera.proxy.pass",
        actor="203.0.113.9",
        metadata={"status": 200},
    )

    assert entry.acceptance_type == AcceptanceType.AUDIT_LOCK
    assert entry.user_id == "audit:203.0.113.9"
    assert entry.metadata["event_type"] == "chimera.proxy.pass"


def _install_bridge_dirs(monkeypatch, tmp_path):
    import app.security.chimera_bridge as bridge_module

    monkeypatch.setattr(bridge_module, "_DRIFT_DIR", tmp_path / "drift")
    monkeypatch.setattr(bridge_module, "_DENY_DIR", tmp_path / "deny")
    if hasattr(bridge_module, "_REPLAY_CACHE"):
        bridge_module._REPLAY_CACHE.clear()
    return bridge_module


def _verdict_event(event_id="evt-verdict-1", timestamp=None):
    return {
        "event_id": event_id,
        "timestamp": timestamp or time.time(),
        "event": "threat_verdict",
        "ip": "203.0.113.9",
        "verdict": "ATTACKER",
        "score": 42,
        "sid": "sid-1",
        "path": "/admin",
    }


def _canary_event(event_id="evt-canary-1", timestamp=None):
    return {
        "event_id": event_id,
        "timestamp": timestamp or time.time(),
        "event": "canary_hit",
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


def _signed(bridge_module, event, secret="phase7-secret"):
    return bridge_module.sign_webhook_event(event, secret=secret)


def test_unsigned_webhook_event_is_rejected(monkeypatch, tmp_path):
    bridge_module = _install_bridge_dirs(monkeypatch, tmp_path)
    bridge = bridge_module.ChimeraBridge(webhook_secret="phase7-secret")

    with pytest.raises(bridge_module.ChimeraWebhookAuthError):
        bridge.receive_authenticated_event(_verdict_event(), signature="")


def test_invalid_signature_is_rejected(monkeypatch, tmp_path):
    bridge_module = _install_bridge_dirs(monkeypatch, tmp_path)
    bridge = bridge_module.ChimeraBridge(webhook_secret="phase7-secret")

    with pytest.raises(bridge_module.ChimeraWebhookAuthError):
        bridge.receive_authenticated_event(
            _verdict_event(),
            signature="bad-signature",
        )


def test_stale_timestamp_is_rejected(monkeypatch, tmp_path):
    bridge_module = _install_bridge_dirs(monkeypatch, tmp_path)
    bridge = bridge_module.ChimeraBridge(webhook_secret="phase7-secret")
    event = _verdict_event(timestamp=time.time() - 301)

    with pytest.raises(bridge_module.ChimeraWebhookAuthError):
        bridge.receive_authenticated_event(event, signature=_signed(bridge_module, event))


def test_replayed_event_id_is_rejected(monkeypatch, tmp_path):
    bridge_module = _install_bridge_dirs(monkeypatch, tmp_path)
    bridge = bridge_module.ChimeraBridge(webhook_secret="phase7-secret")
    event = _verdict_event(event_id="evt-replay")
    signature = _signed(bridge_module, event)

    first = bridge.receive_authenticated_event(event, signature=signature)
    assert first["accepted"] is True

    with pytest.raises(bridge_module.ChimeraWebhookAuthError):
        bridge.receive_authenticated_event(event, signature=signature)


def test_valid_signed_event_is_accepted(monkeypatch, tmp_path):
    bridge_module = _install_bridge_dirs(monkeypatch, tmp_path)
    bridge = bridge_module.ChimeraBridge(webhook_secret="phase7-secret")
    event = _verdict_event()

    result = bridge.receive_authenticated_event(
        event,
        signature=_signed(bridge_module, event),
    )

    assert result["accepted"] is True
    assert result["event_hash"]
    assert result["non_authoritative"] is True


def test_valid_signed_drift_alert_preserves_compatibility_fields(monkeypatch, tmp_path):
    bridge_module = _install_bridge_dirs(monkeypatch, tmp_path)
    bridge = bridge_module.ChimeraBridge(webhook_secret="phase7-secret")
    event = _verdict_event()

    bridge.receive_authenticated_event(event, signature=_signed(bridge_module, event))

    files = list((tmp_path / "drift").glob("chimera_verdict_*.json"))
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
    assert alert["source"] == "chimera"
    assert alert["event"] == "threat_verdict"
    assert alert["target_member"] == "chimera_perimeter"
    assert alert["auth"]["authenticated"] is True
    assert alert["non_authoritative"] is True
    assert alert["event_hash"]


def test_accepted_event_emits_governance_observation(monkeypatch, tmp_path):
    from app.core.governance_observability import get_collector

    bridge_module = _install_bridge_dirs(monkeypatch, tmp_path)
    get_collector().clear()
    bridge = bridge_module.ChimeraBridge(webhook_secret="phase7-secret")
    event = _verdict_event()

    bridge.receive_authenticated_event(event, signature=_signed(bridge_module, event))

    latest = get_collector().get_latest(1)[0]
    assert latest["domain"] == "security.chimera"
    assert latest["metadata"]["source"] == "chimera"
    assert latest["metadata"]["event_hash"]
    assert latest["metadata"]["non_authoritative"] is True
    assert latest["final_outcome"] not in {"ALLOW", "DENY", "HALT"}


def test_accepted_event_relays_through_audit_manager(monkeypatch, tmp_path):
    import app.governance.audit_manager as audit_manager

    bridge_module = _install_bridge_dirs(monkeypatch, tmp_path)
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

    bridge = bridge_module.ChimeraBridge(webhook_secret="phase7-secret")
    event = _verdict_event()
    result = bridge.receive_authenticated_event(
        event,
        signature=_signed(bridge_module, event),
    )

    assert result["receipts"]["audit_manager"]["ok"] is True
    assert calls
    assert calls[0]["event_type"] == "chimera.threat_verdict"
    assert calls[0]["severity"] == "critical"
    assert calls[0]["data"]["event_hash"]
    assert calls[0]["data"]["non_authoritative"] is True


def test_receipt_degradation_is_marked_non_authoritative(monkeypatch, tmp_path):
    import app.governance.audit_manager as audit_manager

    bridge_module = _install_bridge_dirs(monkeypatch, tmp_path)

    class FailingAuditManager:
        def log_security_event(self, event_type, data=None, severity="info"):
            raise RuntimeError("audit offline")

    monkeypatch.setattr(audit_manager, "get_audit_manager", lambda: FailingAuditManager())

    bridge = bridge_module.ChimeraBridge(webhook_secret="phase7-secret")
    event = _verdict_event()
    result = bridge.receive_authenticated_event(
        event,
        signature=_signed(bridge_module, event),
    )

    assert result["accepted"] is True
    assert result["non_authoritative"] is True
    assert result["receipt_degraded"] is True
    assert result["receipts"]["audit_manager"]["ok"] is False


def test_chimera_never_emits_public_allow_deny_halt_decisions(monkeypatch, tmp_path):
    bridge_module = _install_bridge_dirs(monkeypatch, tmp_path)
    bridge = bridge_module.ChimeraBridge(webhook_secret="phase7-secret")
    event = _canary_event()

    result = bridge.receive_authenticated_event(
        event,
        signature=_signed(bridge_module, event),
    )

    assert result.get("public_decision") is None
    assert result.get("final_outcome") not in {"ALLOW", "DENY", "HALT"}


def test_canary_event_does_not_call_octoreflex_or_execution_gate(
    monkeypatch,
    tmp_path,
):
    import app.core.execution_gate as execution_gate
    import app.core.octoreflex as octoreflex

    bridge_module = _install_bridge_dirs(monkeypatch, tmp_path)
    called = {"octoreflex": 0, "gate": 0}

    class FakeOctoReflex:
        def validate_action(self, *args, **kwargs):
            called["octoreflex"] += 1
            return True, []

    monkeypatch.setattr(octoreflex, "get_octoreflex", lambda: FakeOctoReflex())

    def fake_get_execution_gate():
        called["gate"] += 1
        raise AssertionError("ExecutionGate must not be called by Chimera")

    monkeypatch.setattr(execution_gate, "get_execution_gate", fake_get_execution_gate)

    bridge = bridge_module.ChimeraBridge(webhook_secret="phase7-secret")
    event = _canary_event()
    bridge.receive_authenticated_event(event, signature=_signed(bridge_module, event))

    assert called == {"octoreflex": 0, "gate": 0}
