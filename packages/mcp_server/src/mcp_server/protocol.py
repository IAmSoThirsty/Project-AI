"""Minimal typed MCP stdio protocol layer (JSON-RPC 2.0, newline-delimited).

Implements the MCP subset a tool-only server needs: ``initialize``,
``notifications/initialized``, ``ping``, ``tools/list``, and
``tools/call``. Messages are one JSON object per line over stdio, per
the MCP stdio transport. No third-party protocol dependency by design
(sovereign, auditable); if a future MCP revision outgrows this subset,
switching to the official SDK is the documented fallback.

Error contract:
- Malformed JSON -> JSON-RPC -32700; non-object messages -> -32600.
- Unknown methods on requests -> -32601; notifications are ignored.
- Unknown tool names -> -32602 (protocol-level: the tool does not exist).
- Tool execution failures -> a successful JSON-RPC response whose result
  carries ``isError: true`` with the failure text, so MCP clients can
  show the model what went wrong (per MCP tools semantics).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, TextIO

from mcp_server.client import (
    TOOL_SPECS,
    VERSION,
    GatewayClientError,
    UnknownToolError,
)

type JsonObject = dict[str, Any]
type ToolExecutor = Callable[[str, JsonObject], JsonObject]

SERVER_NAME = "project-ai-mcp-server"
SERVER_VERSION = VERSION
SUPPORTED_PROTOCOL_VERSIONS: tuple[str, ...] = ("2025-06-18", "2025-03-26", "2024-11-05")

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602


def _error(message_id: Any, code: int, message: str) -> JsonObject:
    return {
        "jsonrpc": "2.0",
        "id": message_id,
        "error": {"code": code, "message": message},
    }


def _result(message_id: Any, result: JsonObject) -> JsonObject:
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


class McpStdioServer:
    """Newline-delimited JSON-RPC loop bridging MCP clients to a tool executor."""

    def __init__(self, execute_tool: ToolExecutor, *, stdin: TextIO, stdout: TextIO) -> None:
        self._execute_tool = execute_tool
        self._stdin = stdin
        self._stdout = stdout

    def serve_forever(self) -> None:
        for raw_line in self._stdin:
            line = raw_line.strip()
            if not line:
                continue
            response = self.handle_line(line)
            if response is not None:
                self._stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
                self._stdout.flush()

    def handle_line(self, line: str) -> JsonObject | None:
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            return _error(None, PARSE_ERROR, "Parse error")
        if not isinstance(message, dict):
            return _error(None, INVALID_REQUEST, "Invalid Request")
        return self.handle_message(message)

    def handle_message(self, message: JsonObject) -> JsonObject | None:
        method = message.get("method")
        message_id = message.get("id")
        is_request = "id" in message
        if not isinstance(method, str) or not method:
            return _error(message_id, INVALID_REQUEST, "Invalid Request") if is_request else None
        params = message.get("params")
        arguments: JsonObject = params if isinstance(params, dict) else {}

        if method == "initialize":
            result = self._initialize(arguments)
        elif method == "notifications/initialized":
            return None
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = self._list_tools()
        elif method == "tools/call":
            outcome = self._call_tool(message_id, arguments)
            if not is_request:
                return None
            return outcome
        else:
            if not is_request:
                return None
            return _error(message_id, METHOD_NOT_FOUND, f"Method not found: {method}")

        if not is_request:
            return None
        return _result(message_id, result)

    def _initialize(self, params: JsonObject) -> JsonObject:
        requested = params.get("protocolVersion")
        version = (
            requested
            if isinstance(requested, str) and requested in SUPPORTED_PROTOCOL_VERSIONS
            else SUPPORTED_PROTOCOL_VERSIONS[0]
        )
        return {
            "protocolVersion": version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "instructions": (
                "Read-mostly bridge to a local Project-AI gateway. Every tool maps "
                "1:1 to a real gateway route; the server holds no governance "
                "authority and mints no capabilities."
            ),
        }

    @staticmethod
    def _list_tools() -> JsonObject:
        return {
            "tools": [
                {
                    "name": spec.name,
                    "description": spec.description,
                    "inputSchema": spec.input_schema,
                }
                for spec in TOOL_SPECS
            ]
        }

    def _call_tool(self, message_id: Any, params: JsonObject) -> JsonObject:
        name = params.get("name")
        if not isinstance(name, str) or not name:
            return _error(message_id, INVALID_PARAMS, "tools/call requires a tool name")
        raw_arguments = params.get("arguments")
        arguments: JsonObject = raw_arguments if isinstance(raw_arguments, dict) else {}
        try:
            payload = self._execute_tool(name, arguments)
        except UnknownToolError as error:
            return _error(message_id, INVALID_PARAMS, str(error))
        except (GatewayClientError, OSError, ValueError) as error:
            return _result(
                message_id,
                {
                    "content": [{"type": "text", "text": f"Error: {error}"}],
                    "isError": True,
                },
            )
        return _result(
            message_id,
            {
                "content": [
                    {"type": "text", "text": json.dumps(payload, indent=2, sort_keys=True)}
                ],
                "isError": False,
            },
        )
