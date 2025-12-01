from web.backend import app


def test_backend_status_route():
    client = app.test_client()
    response = client.get("/api/status")

    assert response.status_code == 200
    payload = response.get_json() or {}
    assert payload.get("status") == "ok"
    assert payload.get("component") == "web-backend"
