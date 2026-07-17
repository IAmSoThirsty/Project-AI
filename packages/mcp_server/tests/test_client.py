"""Gateway client tests: exact route/method/auth mapping per tool.

Honest scope: proves each declared tool hits exactly one real gateway
route with the right method and auth header via httpx.MockTransport,
and that protected tools fail closed without a token. Does not start a
real gateway (see test_e2e_stdio.py for that).
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest
from mcp_server.client import (
    TOOL_SPECS,
    GatewayClientError,
    ProjectAIGatewayClient,
    UnknownToolError,
)


class Recorder:
    def __init__(self, status_code: int = 200, payload: dict[str, Any] | None = None) -> None:
        self.requests: list[httpx.Request] = []
        self.status_code = status_code
        self.payload = payload if payload is not None else {"status": "ok"}

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(self.status_code, json=self.payload)


def client_with(recorder: Recorder, token: str | None = None) -> ProjectAIGatewayClient:
    return ProjectAIGatewayClient(
        "http://gateway.test",
        token,
        transport=httpx.MockTransport(recorder.handler),
    )


PUBLIC_TOOL_PATHS = {
    "project_ai_health": "/health/live",
    "project_ai_instance": "/api/v1/instance",
    "project_ai_dashboard": "/api/v1/dashboard",
    "project_ai_modules": "/api/v1/modules",
    "project_ai_dois": "/dois",
    "project_ai_replay_status": "/replay/status",
    "project_ai_atlas_status": "/atlas/status",
}


@pytest.mark.parametrize(("tool", "path"), sorted(PUBLIC_TOOL_PATHS.items()))
def test_public_tools_hit_exact_route_without_auth_header(tool: str, path: str) -> None:
    recorder = Recorder()
    result = client_with(recorder).call_tool(tool, {})
    assert result == {"status": "ok"}
    (request,) = recorder.requests
    assert request.method == "GET"
    assert request.url.path == path
    assert "authorization" not in request.headers


def test_every_declared_tool_name_is_covered_by_tests() -> None:
    protected = {
        "project_ai_audit_query",
        "project_ai_record_verdict",
        "project_ai_atlas_sludge_generate",
        "project_ai_atlas_sludge_list",
    }
    assert {spec.name for spec in TOOL_SPECS} == set(PUBLIC_TOOL_PATHS) | protected


def test_protected_tool_fails_closed_without_token() -> None:
    recorder = Recorder()
    with pytest.raises(GatewayClientError, match="PROJECT_AI_MCP_TOKEN"):
        client_with(recorder).call_tool("project_ai_audit_query", {})
    assert recorder.requests == []


def test_audit_query_sends_bearer_and_bounded_parameters() -> None:
    recorder = Recorder()
    client_with(recorder, token="secret-token").call_tool(
        "project_ai_audit_query",
        {"limit": 5, "offset": 2, "event": "chimera.verdict", "query": "action-1"},
    )
    (request,) = recorder.requests
    assert request.headers["authorization"] == "Bearer secret-token"
    assert request.url.path == "/audit"
    assert dict(request.url.params) == {
        "limit": "5",
        "offset": "2",
        "query": "action-1",
        "event": "chimera.verdict",
    }


@pytest.mark.parametrize("bad", [{"limit": 0}, {"limit": 501}, {"offset": -1}, {"limit": True}])
def test_audit_query_rejects_out_of_bounds_before_any_request(bad: dict[str, Any]) -> None:
    recorder = Recorder()
    with pytest.raises(GatewayClientError):
        client_with(recorder, token="secret-token").call_tool("project_ai_audit_query", bad)
    assert recorder.requests == []


def test_record_verdict_posts_canonical_body() -> None:
    recorder = Recorder(status_code=202, payload={"accepted": True, "event": "x", "hash": "h"})
    client_with(recorder, token="secret-token").call_tool(
        "project_ai_record_verdict",
        {"action_id": "action-9", "verdict": "DENY"},
    )
    (request,) = recorder.requests
    assert request.method == "POST"
    assert request.url.path == "/chimera/verdict"
    assert json.loads(request.content) == {
        "action_id": "action-9",
        "verdict": "DENY",
        "source": "mcp-client",
    }


def test_record_verdict_rejects_non_canonical_outcome() -> None:
    recorder = Recorder()
    with pytest.raises(GatewayClientError, match="verdict"):
        client_with(recorder, token="t").call_tool(
            "project_ai_record_verdict", {"action_id": "a", "verdict": "APPROVE"}
        )
    assert recorder.requests == []


def test_sludge_generate_posts_snapshot_and_archetypes() -> None:
    recorder = Recorder(status_code=202, payload={"accepted": True})
    client_with(recorder, token="t").call_tool(
        "project_ai_atlas_sludge_generate",
        {"rs_snapshot": {"stack": "RS"}, "archetypes": ["hidden_elites"]},
    )
    (request,) = recorder.requests
    assert request.method == "POST"
    assert request.url.path == "/atlas/sludge"
    assert json.loads(request.content) == {
        "rs_snapshot": {"stack": "RS"},
        "archetypes": ["hidden_elites"],
    }


def test_sludge_list_uses_inspection_route() -> None:
    recorder = Recorder()
    client_with(recorder, token="t").call_tool(
        "project_ai_atlas_sludge_list", {"limit": 10, "offset": 3}
    )
    (request,) = recorder.requests
    assert request.url.path == "/api/v1/modules/atlas/sludge"
    assert dict(request.url.params) == {"limit": "10", "offset": "3"}


def test_gateway_error_surfaces_status_and_detail() -> None:
    recorder = Recorder(status_code=401, payload={"detail": "Invalid bearer token"})
    with pytest.raises(GatewayClientError, match=r"401.*Invalid bearer token"):
        client_with(recorder, token="wrong").call_tool("project_ai_audit_query", {})


def test_unknown_tool_and_unexpected_arguments_are_rejected() -> None:
    recorder = Recorder()
    with pytest.raises(UnknownToolError):
        client_with(recorder).call_tool("project_ai_memory_store", {})
    with pytest.raises(GatewayClientError, match="accepts no arguments"):
        client_with(recorder).call_tool("project_ai_health", {"unexpected": 1})
    assert recorder.requests == []


def test_url_validation_rejects_relative_and_credentialed_urls() -> None:
    with pytest.raises(ValueError):
        ProjectAIGatewayClient("gateway.test")
    with pytest.raises(ValueError):
        ProjectAIGatewayClient("http://user:pass@gateway.test")
