from app.agents.webharvester import WebHarvester


def test_request_harvest():
    w = WebHarvester()
    r = w.request_harvest("http://example.com", depth=1)
    assert isinstance(r, dict)
    assert r["status"] == "queued"
