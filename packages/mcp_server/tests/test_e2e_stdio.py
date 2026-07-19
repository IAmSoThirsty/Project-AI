"""End-to-end: real MCP server subprocess against a real local gateway.

Honest scope: spawns the actual ``python -m mcp_server.server`` process
and the actual ``python -m project_ai_api.server`` gateway on a loopback
port, then drives initialize -> initialized -> tools/list -> tools/call
over real stdio pipes and asserts live gateway data (health, dashboard,
and a bearer-authenticated audit write/read) comes back through the
protocol. What this cannot prove: behavior of third-party MCP clients
(Claude Desktop, Cursor) — verifying that requires a machine with one of
those clients installed and configured against this server.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from queue import Empty, Queue
from threading import Thread
from typing import IO, Any
from urllib.request import urlopen

from kernel.version import PROJECT_AI_VERSION

TOKEN = "mcp-e2e-test-token"


def _wait_for_port_file(port_file: Path, *, timeout: float = 15.0) -> int:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if port_file.exists():
            content = port_file.read_text(encoding="utf-8").strip()
            if content:
                return int(content)
        time.sleep(0.05)
    raise TimeoutError(f"port file {port_file} was not written within {timeout}s")


def _wait_for_health(port: int, *, timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urlopen(f"http://127.0.0.1:{port}/health/live", timeout=1.0) as response:
                assert response.status == 200
                return
        except OSError as error:
            last_error = error
            time.sleep(0.1)
    raise AssertionError(f"gateway health never succeeded: {last_error}")


class StdioSession:
    """Line-oriented JSON-RPC exchange with a subprocess over pipes."""

    def __init__(self, process: subprocess.Popen[str]) -> None:
        self._process = process
        self._lines: Queue[str] = Queue()
        stdout = process.stdout
        assert stdout is not None
        self._reader = Thread(target=self._pump, args=(stdout,), daemon=True)
        self._reader.start()

    def _pump(self, stream: IO[str]) -> None:
        for line in stream:
            stripped = line.strip()
            if stripped:
                self._lines.put(stripped)

    def send(self, message: dict[str, Any]) -> None:
        stdin = self._process.stdin
        assert stdin is not None
        stdin.write(json.dumps(message) + "\n")
        stdin.flush()

    def receive(self, *, timeout: float = 15.0) -> dict[str, Any]:
        try:
            line = self._lines.get(timeout=timeout)
        except Empty as error:
            raise AssertionError("no MCP response within timeout") from error
        payload = json.loads(line)
        assert isinstance(payload, dict)
        return payload

    def request(self, message_id: int, method: str, **params: Any) -> dict[str, Any]:
        body: dict[str, Any] = {"jsonrpc": "2.0", "id": message_id, "method": method}
        if params:
            body["params"] = params
        self.send(body)
        response = self.receive()
        assert response.get("id") == message_id, response
        return response


def _tool_payload(response: dict[str, Any]) -> dict[str, Any]:
    result = response["result"]
    assert result["isError"] is False, result
    payload = json.loads(result["content"][0]["text"])
    assert isinstance(payload, dict)
    return payload


def test_real_mcp_subprocess_against_real_gateway(tmp_path: Path) -> None:
    port_file = tmp_path / "api.port"
    audit_path = tmp_path / "audit.jsonl"
    gateway_env = {
        **os.environ,
        "PROJECT_AI_API_TOKEN": TOKEN,
        "PROJECT_AI_AUDIT_PATH": str(audit_path),
    }
    gateway = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "project_ai_api.server",
            "--host",
            "127.0.0.1",
            "--port",
            "0",
            "--port-file",
            str(port_file),
        ],
        env=gateway_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    mcp: subprocess.Popen[str] | None = None
    try:
        port = _wait_for_port_file(port_file)
        _wait_for_health(port)

        mcp = subprocess.Popen(
            [sys.executable, "-m", "mcp_server.server"],
            env={
                **os.environ,
                "PROJECT_AI_MCP_API_URL": f"http://127.0.0.1:{port}",
                "PROJECT_AI_MCP_TOKEN": TOKEN,
            },
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        session = StdioSession(mcp)

        initialized = session.request(1, "initialize", protocolVersion="2025-06-18")
        assert initialized["result"]["protocolVersion"] == "2025-06-18"
        assert initialized["result"]["serverInfo"]["name"] == "project-ai-mcp-server"
        session.send({"jsonrpc": "2.0", "method": "notifications/initialized"})

        listing = session.request(2, "tools/list")
        tool_names = [tool["name"] for tool in listing["result"]["tools"]]
        assert "project_ai_health" in tool_names
        assert "project_ai_audit_query" in tool_names

        health = _tool_payload(session.request(3, "tools/call", name="project_ai_health"))
        assert health == {"status": "live", "version": PROJECT_AI_VERSION}

        dashboard = _tool_payload(session.request(4, "tools/call", name="project_ai_dashboard"))
        surface_ids = [surface["id"] for surface in dashboard["surfaces"]]
        assert {"gateway", "replay", "audit_chain", "evidence"} <= set(surface_ids)

        verdict = _tool_payload(
            session.request(
                5,
                "tools/call",
                name="project_ai_record_verdict",
                arguments={"action_id": "mcp-e2e-1", "verdict": "DENY"},
            )
        )
        assert verdict["accepted"] is True
        assert len(verdict["hash"]) == 64

        audit = _tool_payload(
            session.request(
                6,
                "tools/call",
                name="project_ai_audit_query",
                arguments={"limit": 10, "event": "chimera.verdict"},
            )
        )
        assert audit["chain_valid"] is True
        assert audit["filtered_count"] == 1
        assert audit["records"][0]["action_id"] == "mcp-e2e-1"

        stdin = mcp.stdin
        assert stdin is not None
        stdin.close()
        assert mcp.wait(timeout=10.0) == 0
    finally:
        if mcp is not None and mcp.poll() is None:
            mcp.kill()
            mcp.wait(timeout=5.0)
        gateway.terminate()
        try:
            gateway.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            gateway.kill()
            gateway.wait(timeout=5.0)
