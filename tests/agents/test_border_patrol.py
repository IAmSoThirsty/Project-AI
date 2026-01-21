from __future__ import annotations

from pathlib import Path

from app.agents.border_patrol import GateGuardian, VerifierAgent, build_border_patrol


def test_quarantine_and_verify(tmp_path: Path):
    # create a harmless module
    mod = tmp_path / "safe_mod.py"
    mod.write_text('print("ok")\n')

    admins = build_border_patrol(1)
    pa = admins[0]
    wt = pa.towers[0]
    gate = GateGuardian(
        "test-gate", VerifierAgent("test-verifier", data_dir=str(tmp_path)), wt
    )

    box = gate.ingest(str(mod))
    assert box.sealed

    report = gate.process_next(str(mod))
    assert report.get("success") is True
    # persisted report exists
    reports = list(Path(str(tmp_path)).glob("sandbox_reports/*.json"))
    assert len(reports) >= 1


def test_emergency_path(tmp_path: Path):
    admins = build_border_patrol(1)
    pa = admins[0]
    wt = pa.towers[0]
    gate = GateGuardian(
        "test-gate-2", VerifierAgent("test-verifier-2", data_dir=str(tmp_path)), wt
    )

    # simulate emergency
    gate.activate_force_field()
    assert gate.force_field_active
    # ensure PortAdmin/Cerberus recorded lockdown when signaled
    # call port admin manually
    pa.handle_emergency(wt.tower_id, gate.gate_id)
    # there should be at least one incident recorded
    assert len(pa.command_center.incidents) >= 1
