from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
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
        "version": "0.0.0.dev0",
        "maturity": maturity,
        "modules": modules,
        "authority": "none",
    }
    assert client.get("/service/info").json() == response.json()
    paths = set(client.get("/openapi.json").json()["paths"])
    assert paths == {"/health/live", "/service/info"}


def test_unknown_service_role_fails_startup() -> None:
    with pytest.raises(ValueError, match="Unsupported service role"):
        create_app("execution")
