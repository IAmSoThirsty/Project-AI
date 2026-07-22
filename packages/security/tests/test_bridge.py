from __future__ import annotations

from pathlib import Path

from security import (
    receive_canary_hit,
    receive_verdict,
    report_governance_denial,
    start_audit_relay,
)


def test_bridge_records_and_verifies_chain_without_raw_canary(tmp_path: Path) -> None:
    path = tmp_path / "chimera-audit.jsonl"
    relay = start_audit_relay(path)

    receive_verdict(relay, action_id="act-1", verdict="ALLOW")
    receive_canary_hit(relay, canary_value="private-canary", context="test")
    report_governance_denial(relay, action_id="act-2", reason="scope")

    assert relay.verify() == (True, 3)
    valid, count, records = relay.verified_snapshot()
    assert (valid, count) == (True, 3)
    assert records[0]["event"] == "chimera.verdict"
    assert records[0]["hash"]
    assert "private-canary" not in path.read_text(encoding="utf-8")


def test_bridge_materializes_a_valid_empty_genesis_chain(tmp_path: Path) -> None:
    path = tmp_path / "chimera-audit.jsonl"

    relay = start_audit_relay(path)

    assert path.is_file()
    assert path.read_text(encoding="utf-8") == ""
    assert relay.verify() == (True, 0)


def test_bridge_detects_tampering(tmp_path: Path) -> None:
    path = tmp_path / "chimera-audit.jsonl"
    relay = start_audit_relay(path)
    receive_verdict(relay, action_id="act-1", verdict="DENY")
    path.write_text(path.read_text(encoding="utf-8").replace("act-1", "act-9"), encoding="utf-8")

    assert relay.verify() == (False, 1)
    assert relay.verified_snapshot() == (False, 1, ())
