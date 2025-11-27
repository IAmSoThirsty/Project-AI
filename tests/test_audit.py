import os

from app.agents.audit import AuditAgent


def test_audit_writes(tmp_path):
    d = str(tmp_path)
    a = AuditAgent(d)
    ok = a.record_event("unit.test", {"x": 1})
    assert ok
    assert os.path.exists(os.path.join(d, "event_audit.log"))

    ok2 = a.record_explainability(
        "model", [{"token": "a", "weight": 1.0}], meta={"k": "v"}
    )
    assert ok2
    assert os.path.exists(os.path.join(d, "explainability_audit.log"))
