from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from kernel.version import PROJECT_AI_VERSION
from knowledge.repository import RepositoryIndex
from project_ai_services import create_app


@pytest.mark.parametrize(
    ("role", "modules", "maturity"),
    [
        ("swr", ["swr"], "development"),
        ("atlas", ["atlas"], "development"),
        ("arbiter-rlp", ["arbiter", "rlp"], "experimental"),
    ],
)
def test_service_roles_are_live_and_authority_free(
    role: str, modules: list[str], maturity: str
) -> None:
    client = TestClient(create_app(role))
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {
        "status": "live",
        "service": role,
        "version": PROJECT_AI_VERSION,
        "maturity": maturity,
        "modules": modules,
        "authority": "none",
    }
    assert client.get("/service/info").json() == response.json()
    paths = set(client.get("/openapi.json").json()["paths"])
    assert {"/health/live", "/service/info"}.issubset(paths)
    assert {
        "/repository-intelligence/status",
        "/repository-intelligence/search",
    }.issubset(paths)


def test_repository_intelligence_routes_are_read_only_and_grounded(tmp_path, monkeypatch) -> None:
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    (root / "README.md").write_text(
        "# Fixture repository\n\nRepository search documentation.\n", encoding="utf-8"
    )
    (root / "src" / "service.py").write_text(
        "def health_service():\n    return 'service health'\n", encoding="utf-8"
    )
    output = tmp_path / "index"
    RepositoryIndex.build(root, excluded_paths=(output,)).save(output)
    monkeypatch.setenv("PROJECT_AI_REPOSITORY_ROOT", str(root))
    monkeypatch.setenv("PROJECT_AI_REPOSITORY_INDEX", str(output))

    client = TestClient(create_app("swr"))
    status = client.get("/repository-intelligence/status")
    assert status.status_code == 200
    status_body = status.json()
    assert status_body["state"] == "ready"
    assert status_body["indexed_files"] == 2
    assert status_body["indexed_chunks"] > 0
    assert status_body["stale"] is False

    search = client.get("/repository-intelligence/search", params={"query": "health service"})
    assert search.status_code == 200
    body = search.json()
    assert body["query"] == "health service"
    assert body["results"]
    result = body["results"][0]
    assert result["path"] == "src/service.py"
    assert result["start_line"] >= 1
    assert result["end_line"] >= result["start_line"]
    assert result["excerpt"]
    assert len(result["sha256"]) == 64

    assert client.get("/health/live").json()["status"] == "live"
    assert client.get("/service/info").json()["authority"] == "none"


def test_unknown_service_role_fails_startup() -> None:
    with pytest.raises(ValueError, match="Unsupported service role"):
        create_app("execution")
