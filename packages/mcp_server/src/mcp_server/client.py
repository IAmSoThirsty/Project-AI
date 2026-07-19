"""HTTP client mapping MCP tools 1:1 onto real Project-AI gateway routes.

Fail-closed boundaries:
- Protected tools refuse to run without a configured machine token.
- Gateway errors surface as ``GatewayClientError`` with the HTTP status
  and the gateway's own detail text; nothing is fabricated.
- ``/chimera/canary`` is deliberately NOT exposed: canary values are
  secret material and must never transit an MCP client's context or
  logs (the CLI reads them from files for the same reason).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from typing import Any, cast
from urllib.parse import urlencode, urlsplit

import httpx

try:
    VERSION = _pkg_version("project-ai-mcp-server")
except PackageNotFoundError:  # pragma: no cover
    VERSION = "0.0.0.dev0"
DEFAULT_API_URL = "http://127.0.0.1:8000"

type JsonObject = dict[str, Any]


class GatewayClientError(RuntimeError):
    """A tool call could not be completed against the gateway."""


class UnknownToolError(GatewayClientError):
    """The requested tool name is not part of the declared inventory."""


@dataclass(frozen=True)
class ToolSpec:
    """One MCP tool bound to exactly one real gateway route."""

    name: str
    description: str
    method: str
    path: str
    protected: bool
    input_schema: dict[str, Any] = field(
        default_factory=lambda: {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        }
    )


def _paging_schema(default_limit: int, max_limit: int) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": max_limit,
                "default": default_limit,
            },
            "offset": {"type": "integer", "minimum": 0, "default": 0},
        },
        "additionalProperties": False,
    }


_AUDIT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "limit": {"type": "integer", "minimum": 1, "maximum": 500, "default": 100},
        "offset": {"type": "integer", "minimum": 0, "default": 0},
        "query": {"type": "string", "maxLength": 200},
        "event": {"type": "string", "maxLength": 120},
    },
    "additionalProperties": False,
}

_VERDICT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "action_id": {"type": "string", "minLength": 1},
        "verdict": {"type": "string", "enum": ["ALLOW", "DENY", "ESCALATE"]},
        "source": {"type": "string", "default": "mcp-client"},
    },
    "required": ["action_id", "verdict"],
    "additionalProperties": False,
}

_SLUDGE_GENERATE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "rs_snapshot": {"type": "object", "minProperties": 1},
        "archetypes": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "hidden_elites",
                    "suppressed_tech",
                    "false_flags",
                    "prophetic_inevitability",
                ],
            },
        },
    },
    "required": ["rs_snapshot"],
    "additionalProperties": False,
}

TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec(
        name="project_ai_health",
        description="Read the gateway's public liveness state.",
        method="GET",
        path="/health/live",
        protected=False,
    ),
    ToolSpec(
        name="project_ai_instance",
        description=(
            "Read the public instance identity and authority boundary "
            "(local sovereign deployment; no cloud login, no browser capability)."
        ),
        method="GET",
        path="/api/v1/instance",
        protected=False,
    ),
    ToolSpec(
        name="project_ai_dashboard",
        description=(
            "Read the public aggregated evidence dashboard "
            "(gateway, canonical replay, verified audit chain, DOI evidence)."
        ),
        method="GET",
        path="/api/v1/dashboard",
        protected=False,
    ),
    ToolSpec(
        name="project_ai_modules",
        description="Read the public module catalog with maturity, authority, and interface status.",
        method="GET",
        path="/api/v1/modules",
        protected=False,
    ),
    ToolSpec(
        name="project_ai_dois",
        description="Read the public DOI-backed publication registry.",
        method="GET",
        path="/dois",
        protected=False,
    ),
    ToolSpec(
        name="project_ai_replay_status",
        description="Read the canonical replay invariant status.",
        method="GET",
        path="/replay/status",
        protected=False,
    ),
    ToolSpec(
        name="project_ai_atlas_status",
        description="Read the public Atlas analysis-only subordination status.",
        method="GET",
        path="/atlas/status",
        protected=False,
    ),
    ToolSpec(
        name="project_ai_audit_query",
        description=(
            "Query the verified append-only audit chain "
            "(newest first; bounded; requires the machine bearer token)."
        ),
        method="GET",
        path="/audit",
        protected=True,
        input_schema=_AUDIT_SCHEMA,
    ),
    ToolSpec(
        name="project_ai_record_verdict",
        description=(
            "Relay one canonical verdict (ALLOW/DENY/ESCALATE) as authenticated "
            "audit evidence. This records evidence; it does not evaluate governance."
        ),
        method="POST",
        path="/chimera/verdict",
        protected=True,
        input_schema=_VERDICT_SCHEMA,
    ),
    ToolSpec(
        name="project_ai_atlas_sludge_generate",
        description=(
            "Generate a watermarked fictional Atlas Sludge narrative from a "
            "Reality Stack snapshot (isolated fiction; analysis only)."
        ),
        method="POST",
        path="/atlas/sludge",
        protected=True,
        input_schema=_SLUDGE_GENERATE_SCHEMA,
    ),
    ToolSpec(
        name="project_ai_atlas_sludge_list",
        description=(
            "List verified Sludge generation metadata from the audit chain "
            "(newest first; narrative bodies are never persisted)."
        ),
        method="GET",
        path="/api/v1/modules/atlas/sludge",
        protected=True,
        input_schema=_paging_schema(default_limit=50, max_limit=100),
    ),
)

TOOLS_BY_NAME: dict[str, ToolSpec] = {spec.name: spec for spec in TOOL_SPECS}


def _bounded_int(arguments: JsonObject, key: str, default: int, low: int, high: int) -> int:
    raw = arguments.get(key, default)
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise GatewayClientError(f"{key} must be an integer")
    if raw < low or raw > high:
        raise GatewayClientError(f"{key} must be between {low} and {high}")
    return raw


class ProjectAIGatewayClient:
    """Synchronous gateway client with an injectable transport for tests."""

    def __init__(
        self,
        api_url: str | None = None,
        token: str | None = None,
        *,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        raw_url = (
            api_url if api_url is not None else os.getenv("PROJECT_AI_MCP_API_URL", DEFAULT_API_URL)
        ).strip()
        parts = urlsplit(raw_url)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            raise ValueError("gateway URL must be an absolute http(s) URL")
        if parts.username or parts.password:
            raise ValueError("gateway URL must not embed credentials")
        self._token = token if token is not None else os.getenv("PROJECT_AI_MCP_TOKEN")
        self._client = httpx.Client(
            base_url=raw_url,
            timeout=timeout,
            transport=transport,
            headers={"User-Agent": f"project-ai-mcp-server/{VERSION}"},
        )

    def close(self) -> None:
        self._client.close()

    def call_tool(self, name: str, arguments: JsonObject) -> JsonObject:
        spec = TOOLS_BY_NAME.get(name)
        if spec is None:
            raise UnknownToolError(f"Unknown tool: {name}")
        headers: dict[str, str] = {}
        if spec.protected:
            if not self._token:
                raise GatewayClientError(
                    "PROJECT_AI_MCP_TOKEN is not configured; protected tool refused"
                )
            headers["Authorization"] = f"Bearer {self._token}"
        path, body = self._build_request(spec, arguments)
        try:
            response = self._client.request(spec.method, path, json=body, headers=headers)
        except httpx.HTTPError as error:
            raise GatewayClientError(f"gateway request failed: {error}") from error
        if response.status_code >= 400:
            raise GatewayClientError(
                f"gateway returned {response.status_code}: {self._detail(response)}"
            )
        payload = response.json()
        if not isinstance(payload, dict):
            raise GatewayClientError("gateway returned a non-object JSON payload")
        return cast(JsonObject, payload)

    @staticmethod
    def _detail(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return response.text[:200]
        if isinstance(payload, dict) and "detail" in payload:
            return str(payload["detail"])
        return response.text[:200]

    @staticmethod
    def _build_request(spec: ToolSpec, arguments: JsonObject) -> tuple[str, JsonObject | None]:
        if spec.name == "project_ai_audit_query":
            params: dict[str, str | int] = {
                "limit": _bounded_int(arguments, "limit", 100, 1, 500),
                "offset": _bounded_int(arguments, "offset", 0, 0, 1_000_000),
            }
            query = arguments.get("query")
            if isinstance(query, str) and query:
                params["query"] = query
            event = arguments.get("event")
            if isinstance(event, str) and event:
                params["event"] = event
            return f"{spec.path}?{urlencode(params)}", None
        if spec.name == "project_ai_atlas_sludge_list":
            list_params: dict[str, str | int] = {
                "limit": _bounded_int(arguments, "limit", 50, 1, 100),
                "offset": _bounded_int(arguments, "offset", 0, 0, 1_000_000),
            }
            return f"{spec.path}?{urlencode(list_params)}", None
        if spec.name == "project_ai_record_verdict":
            action_id = arguments.get("action_id")
            verdict = arguments.get("verdict")
            if not isinstance(action_id, str) or not action_id:
                raise GatewayClientError("action_id must be a non-empty string")
            if verdict not in {"ALLOW", "DENY", "ESCALATE"}:
                raise GatewayClientError("verdict must be ALLOW, DENY, or ESCALATE")
            source = arguments.get("source", "mcp-client")
            if not isinstance(source, str) or not source:
                raise GatewayClientError("source must be a non-empty string")
            return spec.path, {"action_id": action_id, "verdict": verdict, "source": source}
        if spec.name == "project_ai_atlas_sludge_generate":
            snapshot = arguments.get("rs_snapshot")
            if not isinstance(snapshot, dict) or not snapshot:
                raise GatewayClientError("rs_snapshot must be a non-empty object")
            body: JsonObject = {"rs_snapshot": snapshot}
            archetypes = arguments.get("archetypes")
            if archetypes is not None:
                if not isinstance(archetypes, list) or not all(
                    isinstance(item, str) for item in archetypes
                ):
                    raise GatewayClientError("archetypes must be a list of strings")
                body["archetypes"] = archetypes
            return spec.path, body
        if arguments:
            raise GatewayClientError(f"{spec.name} accepts no arguments")
        return spec.path, None
