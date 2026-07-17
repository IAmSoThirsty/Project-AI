"""Entry point: run the MCP stdio server against the local gateway.

Launch with ``python -m mcp_server.server`` (or the installed
``project-ai-mcp-server`` script). Configuration comes from
``PROJECT_AI_MCP_API_URL`` (default ``http://127.0.0.1:8000``) and
``PROJECT_AI_MCP_TOKEN`` (required only for protected tools; public
tools work without it).
"""

from __future__ import annotations

import io
import sys

from mcp_server.client import ProjectAIGatewayClient
from mcp_server.protocol import McpStdioServer


def _configure_stdio() -> None:
    # Newline-delimited JSON must not gain Windows \r\n translation, and
    # payloads must survive non-ASCII regardless of console code page.
    if isinstance(sys.stdin, io.TextIOWrapper):
        sys.stdin.reconfigure(encoding="utf-8")
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")


def main() -> None:
    _configure_stdio()
    client = ProjectAIGatewayClient()
    try:
        McpStdioServer(client.call_tool, stdin=sys.stdin, stdout=sys.stdout).serve_forever()
    finally:
        client.close()


if __name__ == "__main__":
    main()
