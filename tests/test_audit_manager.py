import json
from types import SimpleNamespace

from app.governance.audit_manager import AuditManager


def test_governance_decision_operational_routes_through_audit_log(
    monkeypatch, tmp_path
):
    import app.governance.audit_manager as audit_manager

    calls = []

    class FakeAuditLog:
        def log_event(
            self,
            event_type,
            data=None,
            actor="system",
            description="",
        ):
            calls.append(
                {
                    "event_type": event_type,
                    "data": data,
                    "actor": actor,
                    "description": description,
                }
            )
            return True

    monkeypatch.setattr(audit_manager, "AuditLog", FakeAuditLog)

    manager = AuditManager(data_dir=tmp_path)

    assert manager.log_governance_decision(
        event_type="governance_approved",
        domain="governance",
        action="approve_action",
        decision_id="decision-1",
        actor="governance",
        description="approve_action approved for governance",
    )

    assert calls == [
        {
            "event_type": "governance_approved",
            "data": {
                "domain": "governance",
                "action": "approve_action",
                "decision_id": "decision-1",
            },
            "actor": "governance",
            "description": "approve_action approved for governance",
        }
    ]
    assert manager.get_statistics()["main_log"]["total_events"] == 1


def test_governance_decision_sovereign_reaches_sovereign_audit_log(
    monkeypatch, tmp_path
):
    monkeypatch.setenv(
        "PROJECT_AI_GENESIS_CONTINUITY_LOG",
        str(tmp_path / "continuity_log.json"),
    )
    manager = AuditManager(data_dir=tmp_path / "audit", sovereign_mode=True)

    assert manager.log_governance_decision(
        event_type="governance_denied",
        domain="governance",
        action="dangerous_action",
        decision_id="decision-2",
        actor="governance",
        description="dangerous_action denied for governance: test denial",
    )

    sovereign_events = [
        event
        for event in manager.audit_log.operational_log.get_events()
        if event.get("event_type") == "sovereign.governance_denied"
    ]
    assert sovereign_events

    event_data = sovereign_events[-1]["data"]
    assert event_data["actor"] == "governance"
    assert json.loads(event_data["user_data"]) == {
        "domain": "governance",
        "action": "dangerous_action",
        "decision_id": "decision-2",
    }

    stats = manager.get_statistics()
    assert stats["mode"] == "sovereign"
    assert stats["main_log"]["signature_count"] >= 1


def test_governance_kernel_decisions_use_audit_manager(monkeypatch):
    import app.core.governance_kernel as governance_kernel
    import app.governance.audit_manager as audit_manager

    calls = []

    class FakeAuditManager:
        def log_governance_decision(self, **kwargs):
            calls.append(kwargs)
            return True

    monkeypatch.setattr(audit_manager, "get_audit_manager", lambda: FakeAuditManager())
    monkeypatch.setattr(
        governance_kernel,
        "get_fates",
        lambda: SimpleNamespace(remember=lambda **_kwargs: None),
    )
    monkeypatch.setattr(
        governance_kernel,
        "get_ledger",
        lambda: SimpleNamespace(attest=lambda _record: None),
    )

    kernel = governance_kernel.GovernanceKernel.__new__(
        governance_kernel.GovernanceKernel
    )

    approved, approval_record = kernel._approve(
        "decision-3", "governance", "read", {}
    )
    denied, denial_record = kernel._reject(
        "decision-4", "governance", "write", {}, "test denial"
    )

    assert approved is True
    assert approval_record.approved is True
    assert denied is False
    assert denial_record.approved is False
    assert [call["event_type"] for call in calls] == [
        "governance_approved",
        "governance_denied",
    ]
