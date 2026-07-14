# Project-AI MCP Toolkit (Optional Integration)

**IMPORTANT:** Project-AI is **LOCAL-FIRST**. MCP integration is **optional**.

All core functionality (governance, memory, audit, execution) runs 100% offline and locally. This MCP toolkit is purely a convenience layer for users who want Claude Desktop or Cursor to interact with their local Project-AI instance.

## Architecture

```
Project-AI (runs locally, fully offline)
    ├── API Server (http://localhost:8000)
    │   ├── Governance verdicts
    │   ├── Memory queries
    │   ├── Audit trail
    │   └── Capabilities
    │
    └── MCP Server (optional, only if you want Claude integration)
        └── Routes MCP calls → local API
```

**Without MCP:** Project-AI works 100% offline. You interact via REST API, CLI, desktop app.  
**With MCP:** Claude Desktop / Cursor can also query your local API.

It's a **convenience**, not a requirement.

## When to Use MCP

✅ **Use MCP if:**
- You want Claude Desktop to talk to your local Project-AI
- You want Cursor to access governance verdicts
- You're already using Claude as your main editor

❌ **Don't need MCP if:**
- You use the web portals (http://localhost:4173, :4174)
- You use the desktop app (PyQt6)
- You use the CLI (`project-ai` command)
- You directly call the REST API

## Installation (Optional)

### Option 1: Claude Desktop Integration

```bash
# 1. Configure MCP in Claude Desktop config
# macOS: ~/Library/Application\ Support/Claude/claude_desktop_config.json
# Windows: %APPDATA%\Claude\claude_desktop_config.json

{
  "mcpServers": {
    "project-ai": {
      "command": "python",
      "args": ["-m", "mcp_server.project_ai"],
      "env": {
        "PROJECT_AI_MCP_API_URL": "http://localhost:8000",
        "PROJECT_AI_MCP_TOKEN": "${PROJECT_AI_API_TOKEN}"
      }
    }
  }
}

# 2. Restart Claude Desktop
# 3. Now Claude can call @project-ai tools
```

### Option 2: Cursor Integration

```bash
# 1. Copy .mcp/mcp-toolkit.json to your project
# 2. In Cursor settings → MCP Servers
# 3. Add: file://.mcp/mcp-toolkit.json
# 4. Restart Cursor
```

### Option 3: Run Standalone

```bash
# Start MCP server independently
python -m mcp_server.project_ai

# Connects to local API at http://localhost:8000
```

## What MCP Exposes

All MCP calls are **local calls to your API**. Nothing goes online.

```
@project-ai verdict
  → queries http://localhost:8000/governance/verdict (local only)

@project-ai audit  
  → queries http://localhost:8000/audit (local only)

@project-ai memory
  → queries http://localhost:8000/memory (local only)
```

Every call:
- ✅ Runs locally on your machine
- ✅ Respects your local governance rules
- ✅ Gets recorded in your local audit trail
- ✅ Uses only local models/cache

## Comparison: With vs Without MCP

### Without MCP (Still Fully Functional)
```bash
# Start Project-AI
docker compose up

# Interact via:
# - Web: http://localhost:4173
# - REST API: curl http://localhost:8000
# - CLI: project-ai verdict act-001 ALLOW
# - Desktop: Launch the PyQt6 app
```

### With MCP (Added Convenience)
```bash
# Start Project-AI
docker compose up

# Also start MCP server
python -m mcp_server.project_ai

# Now in Claude Desktop, you can also do:
# - "Ask Project-AI to verify this code" → calls local API via MCP
# - "Run a governance verdict" → calls local API via MCP
# - "Show me recent audit events" → calls local API via MCP
```

**Both are talking to the same local API.** MCP is just another interface.

## Security

✅ **Local-only:** No credentials leave your machine  
✅ **API-proxied:** MCP just forwards to your local API  
✅ **Token-based:** Same auth as the API itself  
✅ **Audit-logged:** All MCP calls appear in your audit trail  
✅ **Offline-capable:** Works completely disconnected from internet  

```
MCP Request
  → Local validation
  → Local Triumvirate evaluation
  → Local API call
  → Local audit logging
  → No network calls
```

## Disabling MCP

If you don't want MCP:

```bash
# Simply don't start the MCP server
# All core Project-AI functionality continues 100% normally

# Project-AI works exactly the same via:
docker compose up  # runs without MCP
```

MCP is completely optional. Not running it changes **nothing**.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│  User's Machine (Local)                             │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Claude Desktop (optional)                          │
│  ├─ MCP Client                                      │
│  └─→ MCP Server (Python)                            │
│       └─→ http://localhost:8000 (local REST)        │
│                                                      │
│  Cursor (optional)                                  │
│  ├─ MCP Client                                      │
│  └─→ MCP Server (Python)                            │
│       └─→ http://localhost:8000 (local REST)        │
│                                                      │
│  Web Browser                                        │
│  └─→ http://localhost:4173 (web portals)            │
│       └─→ http://localhost:8000 (local REST)        │
│                                                      │
│  Desktop App (PyQt6)                                │
│  └─→ http://localhost:8000 (local REST)             │
│                                                      │
│  CLI                                                │
│  └─→ project-ai command → http://localhost:8000     │
│                                                      │
│  Project-AI Core (runs everywhere)                  │
│  ├─ API Server (8000)                              │
│  ├─ Governance Engine (Triumvirate)                │
│  ├─ Memory System (CCMA)                           │
│  ├─ Audit Trail (cryptographic)                    │
│  ├─ Execution Gate                                 │
│  └─ Everything 100% OFFLINE                        │
│                                                      │
│  Persistence (local)                               │
│  ├─ PostgreSQL (.data/postgres)                    │
│  ├─ Redis (.data/redis)                            │
│  └─ Audit files (.data/audit.jsonl)                │
│                                                      │
│  🌍 Internet ← NOT REQUIRED, NOT ACCESSED           │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## The Bottom Line

**Project-AI is local-first.** Everything works offline.

MCP is just a cosmetic layer that lets Claude/Cursor access your local API. It's nice to have, but completely optional.

You don't need:
- Cloud accounts
- API keys
- Internet connection
- Claude subscription (to use Project-AI)

If Claude helps you, great. If not, use the other interfaces.

The **system is yours. Offline. Local. Always.**
