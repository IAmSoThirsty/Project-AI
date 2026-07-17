"""In-house MCP stdio server for the Project-AI development gateway.

Optional machine-client bridge: an MCP-compatible client (Claude
Desktop, Cursor, ...) launches the stdio server, which forwards each
tool call to the local gateway over HTTP. Every tool maps 1:1 to a real
gateway route; the server holds no governance authority and mints no
capabilities.
"""

from mcp_server.client import (
    TOOL_SPECS,
    GatewayClientError,
    ProjectAIGatewayClient,
    ToolSpec,
    UnknownToolError,
)
from mcp_server.protocol import SUPPORTED_PROTOCOL_VERSIONS, McpStdioServer

__all__ = [
    "SUPPORTED_PROTOCOL_VERSIONS",
    "TOOL_SPECS",
    "GatewayClientError",
    "McpStdioServer",
    "ProjectAIGatewayClient",
    "ToolSpec",
    "UnknownToolError",
]
