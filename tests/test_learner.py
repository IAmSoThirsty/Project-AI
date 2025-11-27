import json

from app.agents.learner import LearnerAgent


def test_curate_dataset(tmp_path):
    d = tmp_path / "examples"
    d.mkdir()
    sample = [{"text": "foo", "label": "zeroth"}, {"text": "bar", "label": "none"}]
    p = d / "ex.json"
    p.write_text(json.dumps(sample), encoding="utf-8")

    la = LearnerAgent()
    counts = la.curate_dataset(str(d))
    assert counts.get("zeroth", 0) == 1
    assert counts.get("none", 0) == 1


def test_schedule_retrain_calls_callback():
    called = {"ok": False}

    def cb():
        called["ok"] = True

    la = LearnerAgent()
    assert la.schedule_retrain(cb)
    assert called["ok"]
