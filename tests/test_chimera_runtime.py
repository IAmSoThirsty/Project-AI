import os
import subprocess
import sys


def _run_chimera_script(tmp_path, script: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CHIMERA_DB"] = str(tmp_path / "chimera.db")
    env["CHIMERA_AUDIT"] = str(tmp_path / "audit.jsonl")
    env["CHIMERA_GOVERNANCE_DENY_DIR"] = str(tmp_path / "denials")
    env["CHIMERA_SECRET"] = "test-secret"
    env["CHIMERA_ENV"] = "dev"
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
