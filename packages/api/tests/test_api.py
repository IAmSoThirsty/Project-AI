from __future__ import annotations

import hashlib
from pathlib import Path

from project_ai_api import DoiRecord, ReplayStatus, create_app, load_doi_registry
from starlette.testclient import TestClient

TOKEN = "stage-12-test-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


def _client(tmp_path: Path) -> TestClient:
    return TestClient(
        create_app(
            api_token=TOKEN,
            audit_path=tmp_path / "audit.jsonl",
            dois=(
                DoiRecord(
                    title="Paper-01",
                    doi="10.1/example",
                    domain="security",
                    url="https://doi.org/10.1/example",
                ),
            ),
            replay_status=ReplayStatus(
                status="pass",
                invariants_passed=5,
                invariants_total=5,
                updated_at="2026-06-21T00:00:00Z",
            ),
        )
    )


def test_public_health_doi_and_replay_routes(tmp_path: Path) -> None:
    client = _client(tmp_path)
    assert client.get("/health/live").json() == {
        "status": "live",
        "version": "0.0.0.dev0",
    }
    assert client.get("/dois").json()["dois"][0]["doi"] == "10.1/example"
    assert client.get("/replay/status").json()["invariants_passed"] == 5


def test_registry_reads_only_complete_catalog() -> None:
    root = Path(__file__).resolve().parents[3]
    records = load_doi_registry(root / "docs" / "reference" / "DOI_REGISTRY.md")
    assert len(records) == 21
    assert records[0].title == "Paper-01"
    assert records[-1].doi == "10.5281/zenodo.19592336"


def test_protected_routes_fail_closed_without_configuration() -> None:
    client = TestClient(create_app(dois=()))
    response = client.get("/audit")
    assert response.status_code == 503
    assert response.json()["detail"] == "Protected API surfaces are not configured"


def test_protected_routes_reject_missing_or_invalid_bearer(tmp_path: Path) -> None:
    client = _client(tmp_path)
    assert client.get("/audit").status_code == 401
    assert client.get("/audit", headers={"Authorization": "Bearer wrong"}).status_code == 401
    response = client.get("/audit", headers={"Authorization": "Basic token"})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_verdict_and_audit_routes_preserve_canonical_outcome(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.post(
        "/chimera/verdict",
        headers=AUTH,
        json={"action_id": "action-12", "verdict": "DENY", "source": "test"},
    )
    assert response.status_code == 202
    assert response.json()["event"] == "chimera.verdict"

    audit = client.get("/audit?limit=1", headers=AUTH).json()
    assert audit["chain_valid"] is True
    assert audit["count"] == 1
    assert audit["records"][0]["verdict"] == "DENY"


def test_canary_route_never_persists_raw_canary(tmp_path: Path) -> None:
    client = _client(tmp_path)
    raw_canary = "CHIMERA-CANARY-stage-12-private"
    response = client.post(
        "/chimera/canary",
        headers=AUTH,
        json={"canary_value": raw_canary, "context": "gateway-test"},
    )
    assert response.status_code == 202
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert raw_canary not in audit_text
    assert hashlib.sha256(raw_canary.encode()).hexdigest() in audit_text


def test_invalid_verdict_and_audit_limit_are_rejected(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.post(
        "/chimera/verdict",
        headers=AUTH,
        json={"action_id": "action-12", "verdict": "APPROVE"},
    )
    assert response.status_code == 422
    assert client.get("/audit?limit=0", headers=AUTH).status_code == 422


def test_corrupt_audit_chain_fails_closed(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.post(
        "/chimera/verdict",
        headers=AUTH,
        json={"action_id": "action-12", "verdict": "ALLOW"},
    )
    assert response.status_code == 202
    path = tmp_path / "audit.jsonl"
    path.write_text(path.read_text(encoding="utf-8").replace("ALLOW", "DENY"), encoding="utf-8")
    response = client.get("/audit", headers=AUTH)
    assert response.status_code == 503
    assert response.json()["detail"] == "Audit hash chain verification failed"


def test_malformed_audit_json_fails_closed(tmp_path: Path) -> None:
    client = _client(tmp_path)
    (tmp_path / "audit.jsonl").write_text("{not-json}\n", encoding="utf-8")
    response = client.get("/audit", headers=AUTH)
    assert response.status_code == 503
    assert response.json()["detail"] == "Audit hash chain verification failed"
