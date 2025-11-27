import os

from app.core.ai_persona import AIPersona


def test_default_policy_created_and_audit(tmp_path):
    # tmp_path will be used as data_dir, persona_dir will be tmp_path / 'ai_persona'
    data_dir = str(tmp_path)
    persona = AIPersona(data_dir=data_dir)

    pdir = os.path.join(data_dir, "ai_persona")
    policy_path = os.path.join(pdir, "oversight_policy.json")
    assert os.path.exists(policy_path)

    # Save policy explicitly and ensure audit log recorded
    ok = persona.save_oversight_policy()
    assert ok

    event_log = os.path.join(pdir, "event_audit.log")
    assert os.path.exists(event_log)
    # check that at least one line contains the oversight.policy.saved event
    found = False
    with open(event_log, "r", encoding="utf-8") as f:
        for line in f:
            if "oversight.policy.saved" in line:
                found = True
                break
    assert found
