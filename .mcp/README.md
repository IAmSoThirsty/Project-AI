# Project-AI MCP Toolkit (Optional Integration)

**IMPORTANT:** Project-AI is **LOCAL-FIRST**. MCP integration is **optional**.

The MCP server (`packages/mcp_server`, package `project-ai-mcp-server`) is an
in-house stdio bridge that lets MCP-compatible clients (Claude Desktop,
Cursor, ...) call the **local** Project-AI gateway. Every tool maps 1:1 to a
real gateway route; nothing goes online, no governance authority is held by
the bridge, and no capabilities are minted.

## Architecture

```
Project-AI gateway (http://127.0.0.1:8000, local)
    └── MCP stdio server (optional)
        python -m mcp_server.server
        └── forwards each tools/call to one real gateway route
```

## Tools (all local calls)

| Tool | Gateway route | Auth |
| --- | --- | --- |
| `project_ai_health` | `GET /health/live` | public |
| `project_ai_instance` | `GET /api/v1/instance` | public |
| `project_ai_dashboard` | `GET /api/v1/dashboard` | public |
| `project_ai_modules` | `GET /api/v1/modules` | public |
| `project_ai_dois` | `GET /dois` | public |
| `project_ai_replay_status` | `GET /replay/status` | public |
| `project_ai_atlas_status` | `GET /atlas/status` | public |
| `project_ai_audit_query` | `GET /audit` | machine bearer |
| `project_ai_record_verdict` | `POST /chimera/verdict` | machine bearer |
| `project_ai_atlas_sludge_generate` | `POST /atlas/sludge` | machine bearer |
| `project_ai_atlas_sludge_list` | `GET /api/v1/modules/atlas/sludge` | machine bearer |

Deliberate exclusions:

- `/chimera/canary` — canary values are secret material and must never
  transit an MCP client's context or logs (the CLI reads them from files for
  the same reason).
- Human-session routes (auth, work requests, module workflows) — those are
  browser session + CSRF surfaces, not machine-bearer surfaces.
- `project_ai_record_verdict` relays verdict **evidence** to the audit
  chain. It does not evaluate governance; canonical verdict authority stays
  in `packages/governance`.

## Installation (Optional)

Claude Desktop (`claude_desktop_config.json`) or any MCP client:

```json
{
  "mcpServers": {
    "project-ai": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_server.server"],
      "env": {
        "PROJECT_AI_MCP_API_URL": "http://127.0.0.1:8000",
        "PROJECT_AI_MCP_TOKEN": "<your PROJECT_AI_API_TOKEN>"
      }
    }
  }
}
```

Run the client with its working directory set to this repository (or use an
absolute `uv --directory` argument) so the workspace environment resolves.
`PROJECT_AI_MCP_TOKEN` is only required for the machine-bearer tools; the
public tools work without it.

Cursor: point its MCP configuration at `.mcp/mcp-toolkit.json`.

## Protocol

Minimal in-house JSON-RPC 2.0 over newline-delimited stdio implementing the
MCP subset a tool-only server needs (`initialize`,
`notifications/initialized`, `ping`, `tools/list`, `tools/call`). Supported
protocol revisions: `2025-06-18`, `2025-03-26`, `2024-11-05`.

## Verification status

- Proven by tests: exact tool-to-route mapping, fail-closed protected tools,
  protocol framing, and a real subprocess end-to-end run against a real
  loopback gateway (`packages/mcp_server/tests/`).
- Not verified: third-party MCP client behavior (Claude Desktop, Cursor).
  Verifying that requires a machine with one of those clients installed and
  configured against this server.

## The Bottom Line

Project-AI works completely without MCP: web portals, desktop app, CLI, and
REST API all talk to the same local gateway. MCP is one more optional local
interface — **the system is yours. Offline. Local. Always.**
