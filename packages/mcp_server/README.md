# project-ai-mcp-server

In-house MCP (Model Context Protocol) stdio server exposing the Project-AI
development gateway's **real routes** to MCP-compatible clients (Claude
Desktop, Cursor, ...). Optional: the system is fully functional without it.

## Authority boundary

- Every tool maps 1:1 to an existing gateway route — nothing else.
- The server holds no governance authority, mints no capabilities, and
  cannot reach the execution gate; protected tools carry only the shared
  machine bearer token (`PROJECT_AI_MCP_TOKEN`) the gateway already accepts.
- `/chimera/canary` is deliberately not exposed: canary values are secret
  material and must never transit an MCP client's context or logs.

## Protocol

Minimal typed JSON-RPC 2.0 over newline-delimited stdio implementing the MCP
subset a tool-only server needs: `initialize`, `notifications/initialized`,
`ping`, `tools/list`, `tools/call`. Supported protocol revisions:
`2025-06-18`, `2025-03-26`, `2024-11-05`. No third-party protocol dependency
by design; if a future MCP revision outgrows this subset, switching to the
official SDK is the documented fallback.

## Tools

| Tool | Route | Auth |
| --- | --- | --- |
| `project_ai_health` | `GET /health/live` | public |
| `project_ai_instance` | `GET /api/v1/instance` | public |
| `project_ai_dashboard` | `GET /api/v1/dashboard` | public |
| `project_ai_modules` | `GET /api/v1/modules` | public |
| `project_ai_dois` | `GET /dois` | public |
| `project_ai_replay_status` | `GET /replay/status` | public |
| `project_ai_atlas_status` | `GET /atlas/status` | public |
| `project_ai_audit_query` | `GET /audit` | bearer |
| `project_ai_record_verdict` | `POST /chimera/verdict` | bearer |
| `project_ai_atlas_sludge_generate` | `POST /atlas/sludge` | bearer |
| `project_ai_atlas_sludge_list` | `GET /api/v1/modules/atlas/sludge` | bearer |

`project_ai_record_verdict` relays verdict **evidence** to the audit chain;
it does not evaluate governance.

## Run

```
uv run python -m mcp_server.server
```

Environment: `PROJECT_AI_MCP_API_URL` (default `http://127.0.0.1:8000`),
`PROJECT_AI_MCP_TOKEN` (only needed for the bearer tools; public tools work
without it). Client registration lives in `.mcp/mcp-toolkit.json`.

## Verification status

- Unit: every tool's exact route/method/auth is proven with
  `httpx.MockTransport`; protocol frames are proven over in-memory streams.
- End-to-end: `tests/test_e2e_stdio.py` spawns the real server subprocess
  against a real loopback gateway and drives the full handshake and tool
  calls over stdio pipes.
- Not verified: behavior of third-party MCP clients (Claude Desktop,
  Cursor). Verifying that requires a machine with one of those clients
  installed and configured against this server.
