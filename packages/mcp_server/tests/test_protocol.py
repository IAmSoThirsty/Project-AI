"""MCP stdio protocol frame tests over in-memory streams.

Honest scope: proves the JSON-RPC 2.0 framing, the initialize handshake,
tools/list inventory, tools/call success and failure shapes, notification
silence, and malformed-input error codes — all against a stub executor.
Live third-party MCP clients (Claude Desktop, Cursor) are not exercised
here; test_e2e_stdio.py drives the real subprocess end-to-end.
"""

from __future__ import annotations

import io
import json
from typing import Any

from mcp_server.client import TOOL_SPECS, GatewayClientError, UnknownToolError
from mcp_server.protocol import SUPPORTED_PROTOCOL_VERSIONS, McpStdioServer


def stub_executor(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "explode":
        raise GatewayClientError("gateway returned 503: down")
    if name not in {spec.name for spec in TOOL_SPECS} and name != "echo":
        raise UnknownToolError(f"Unknown tool: {name}")
    return {"tool": name, "arguments": arguments}


def make_server(stdin_text: str = "") -> tuple[McpStdioServer, io.StringIO]:
    stdout = io.StringIO()
    server = McpStdioServer(stub_executor, stdin=io.StringIO(stdin_text), stdout=stdout)
    return server, stdout


def rpc(method: str, message_id: int | None = None, **params: Any) -> str:
    message: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
    if message_id is not None:
        message["id"] = message_id
    if params:
        message["params"] = params
    return json.dumps(message)


def test_initialize_handshake_echoes_supported_version() -> None:
    server, _ = make_server()
    response = server.handle_line(rpc("initialize", 1, protocolVersion="2025-03-26"))
    assert response is not None
    assert response["id"] == 1
    result = response["result"]
    assert result["protocolVersion"] == "2025-03-26"
    assert result["serverInfo"]["name"] == "project-ai-mcp-server"
    assert result["capabilities"]["tools"] == {"listChanged": False}


def test_initialize_falls_back_to_latest_supported_version() -> None:
    server, _ = make_server()
    response = server.handle_line(rpc("initialize", 1, protocolVersion="1999-01-01"))
    assert response is not None
    assert response["result"]["protocolVersion"] == SUPPORTED_PROTOCOL_VERSIONS[0]


def test_tools_list_matches_declared_inventory() -> None:
    server, _ = make_server()
    response = server.handle_line(rpc("tools/list", 2))
    assert response is not None
    tools = response["result"]["tools"]
    assert [tool["name"] for tool in tools] == [spec.name for spec in TOOL_SPECS]
    assert all(tool["description"] and tool["inputSchema"] for tool in tools)


def test_tools_call_round_trip_and_error_shapes() -> None:
    server, _ = make_server()
    ok = server.handle_line(rpc("tools/call", 3, name="echo", arguments={"a": 1}))
    assert ok is not None
    assert ok["result"]["isError"] is False
    assert json.loads(ok["result"]["content"][0]["text"]) == {
        "tool": "echo",
        "arguments": {"a": 1},
    }

    failed = server.handle_line(rpc("tools/call", 4, name="explode"))
    assert failed is not None
    assert failed["result"]["isError"] is True
    assert "503" in failed["result"]["content"][0]["text"]

    unknown = server.handle_line(rpc("tools/call", 5, name="not-a-tool"))
    assert unknown is not None
    assert unknown["error"]["code"] == -32602


def test_ping_unknown_method_and_malformed_input() -> None:
    server, _ = make_server()
    ping = server.handle_line(rpc("ping", 6))
    assert ping is not None and ping["result"] == {}

    unknown = server.handle_line(rpc("resources/list", 7))
    assert unknown is not None and unknown["error"]["code"] == -32601

    parse_error = server.handle_line("{not json")
    assert parse_error is not None and parse_error["error"]["code"] == -32700

    invalid = server.handle_line(json.dumps(["not", "an", "object"]))
    assert invalid is not None and invalid["error"]["code"] == -32600


def test_notifications_never_produce_responses() -> None:
    server, _ = make_server()
    assert server.handle_line(rpc("notifications/initialized")) is None
    assert server.handle_line(rpc("notifications/cancelled")) is None
    assert server.handle_line(rpc("tools/call", None, name="echo")) is None


def test_serve_forever_writes_newline_delimited_responses() -> None:
    lines = "\n".join(
        [
            rpc("initialize", 1, protocolVersion="2025-06-18"),
            rpc("notifications/initialized"),
            rpc("tools/list", 2),
            "",
        ]
    )
    server, stdout = make_server(lines)
    server.serve_forever()
    written = [json.loads(line) for line in stdout.getvalue().splitlines() if line]
    assert [message["id"] for message in written] == [1, 2]
