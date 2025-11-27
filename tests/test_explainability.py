from app.agents.explainability import ExplainabilityAgent


def test_explain_format():
    e = ExplainabilityAgent()
    out = e.explain([("a", 1.0), ("b", 0.5)], top_n=2)
    assert "top" in out and out["top_n"] == 2
    assert isinstance(out["top"], list)
