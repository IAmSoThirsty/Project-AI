from app.agents.metrics import MetricsAgent


def test_record_query():
    m = MetricsAgent()
    m.record("latency", 123.4, {"route": "/"})
    q = m.query("latency")
    assert isinstance(q, list)
    assert q and q[0]["value"] == 123.4
