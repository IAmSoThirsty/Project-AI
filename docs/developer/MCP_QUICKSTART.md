---
type: quickstart
tags: [p1-developer, mcp, model-context-protocol, integration, ai-assistants, protocol]
created: 2026-04-20
last_verified: 2026-04-20
status: current
related_systems: [mcp-server, mcp-integration, ai-capabilities, protocol-handlers]
stakeholders: [developers, integrators, mcp-users]
audience: beginner
prerequisites: [python-basics, pip-package-management, environment-variables]
estimated_time: 5 minutes
review_cycle: monthly
---
# MCP Quick Start Guide

## What is MCP?

Model Context Protocol (MCP) is an open protocol that enables AI assistants to securely connect to data sources, tools, and services. Project-AI implements an MCP server that exposes its advanced AI capabilities to MCP-compatible clients.

## Quick Setup (5 minutes)

### Step 1: Install MCP Dependencies

```bash
cd /path/to/Project-AI
pip install "mcp[cli]"
```

### Step 2: Set Environment Variables

Create or update `.env` in the project root:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key
HUGGINGFACE_API_KEY=hf_your-hf-key

# Optional
FERNET_KEY=your-encryption-key
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-email-password
```

### Step 3: Configure Claude Desktop

**macOS/Linux:**
```bash
# Edit configuration
nano ~/.config/Claude/claude_desktop_config.json
```

**Windows:**
```powershell
# Edit configuration
notepad %APPDATA%\Claude\claude_desktop_config.json
```

**Add this configuration:**

```json
{
  "mcpServers": {
    "project-ai": {
      "command": "python",
      "args": ["-m", "src.app.core.mcp_server"],
      "cwd": "/absolute/path/to/Project-AI",
      "env": {
        "PYTHONPATH": ".",
        "OPENAI_API_KEY": "your-key-here",
        "HUGGINGFACE_API_KEY": "your-key-here"
      }
    }
  }
}
```

### Step 4: Restart Claude Desktop

Close and reopen Claude Desktop. You should see "project-ai" listed in the MCP servers section.

### Step 5: Test the Connection

In Claude Desktop, try:

> "Use the get_persona_state tool to show me the AI's current personality"

You should see Project-AI's persona configuration!

## Available Tools

Project-AI exposes its core AI systems via MCP tools powered by [[API_QUICK_REFERENCE#core/ai_systems.py|ai_systems.py]] and [[API_QUICK_REFERENCE#core/mcp_server.py|mcp_server.py]].

### 🧠 AI Ethics & Persona

Powered by [[API_QUICK_REFERENCE#core/ai_systems.py|AIPersona]] and [[API_QUICK_REFERENCE#core/ai_systems.py|FourLaws]] classes:

- `validate_action` - Check if actions align with AI ethics ([[API_QUICK_REFERENCE#core/ai_systems.py|FourLaws.validate_action()]])
- `get_persona_state` - View AI personality and mood ([[API_QUICK_REFERENCE#core/ai_systems.py|AIPersona.get_state()]])
- `adjust_persona_trait` - Modify personality traits ([[API_QUICK_REFERENCE#core/ai_systems.py|AIPersona.update_trait()]])

### 💾 Memory & Learning

Powered by [[API_QUICK_REFERENCE#core/ai_systems.py|MemoryExpansionSystem]] and [[API_QUICK_REFERENCE#core/ai_systems.py|LearningRequestManager]]:

- `add_memory` - Store information in knowledge base ([[API_QUICK_REFERENCE#core/ai_systems.py|MemoryExpansionSystem.add_memory()]])
- `search_memory` - Search stored knowledge ([[API_QUICK_REFERENCE#core/ai_systems.py|MemoryExpansionSystem.search_memory()]])
- `submit_learning_request` - Request AI to learn new content
- `approve_learning_request` - Approve learning requests

### 🛠️ Utilities

- `analyze_data` - Analyze CSV/Excel/JSON files
- `track_location` - IP geolocation lookup
- `send_emergency_alert` - Send emergency notifications
- `generate_image` - Create AI-generated images

### 🔌 Plugin Management

- `list_plugins` - View available plugins
- `enable_plugin` / `disable_plugin` - Manage plugins

## Example Usage

### Ethics Validation

> "Validate if it's ethical to automatically post on social media without user consent"

Claude will use the `validate_action` tool:
```json
{
  "action": "Post on social media automatically",
  "context": {
    "is_user_order": false,
    "harms_human": false,
    "endangers_humanity": false
  }
}
```

### Knowledge Management

> "Add to memory that I prefer dark mode interfaces"

Claude will use the `add_memory` tool:
```json
{
  "category": "user_preferences",
  "content": "User prefers dark mode interfaces",
  "importance": 0.7
}
```

### Image Generation

> "Generate a watercolor painting of a sunset over mountains"

Claude will use the `generate_image` tool:
```json
{
  "prompt": "Sunset over mountains with vibrant colors",
  "style": "watercolor",
  "backend": "huggingface"
}
```

## Testing

### Test MCP Server Directly

```bash
# Run the server
python -m src.app.core.mcp_server

# In another terminal, test with MCP Inspector
npx @modelcontextprotocol/inspector python -m src.app.core.mcp_server
```

### Verify Installation

```python
# Test imports
python -c "from src.app.core.mcp_server import ProjectAIMCPServer; print('✓ MCP Server OK')"

# Test dependencies
python -c "import mcp; print('✓ MCP SDK OK')"
```

## Troubleshooting

### Server Not Found

**Problem:** Claude Desktop doesn't detect the server

**Solution:**

1. Check the `cwd` path is absolute and correct
1. Verify PYTHONPATH is set to "."
1. Restart Claude Desktop completely
1. Check Claude's logs (Help → View Logs)

### Import Errors

**Problem:** Python import errors when starting server

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Verify Python version (need 3.12+)
python --version

# Check PYTHONPATH
export PYTHONPATH=/path/to/Project-AI:$PYTHONPATH
```

### API Key Issues

**Problem:** Tools fail with API errors

**Solution:**

1. Verify API keys in `.env` file
1. Check keys are valid and have quota
1. Ensure environment variables are loaded

## Next Steps

- Read full documentation: [[MCP_CONFIGURATION]]
- Explore AI Persona: [[AI_PERSONA_IMPLEMENTATION]]
- Learn about learning system: [[LEARNING_REQUEST_IMPLEMENTATION]]
- Desktop app setup: [[DESKTOP_APP_QUICKSTART]]
- Review security: [[SECURITY]]

## Support

- 📖 Documentation: [[MCP_CONFIGURATION]]
- 🐛 Issues: <https://github.com/IAmSoThirsty/Project-AI/issues>
- 💬 Discussions: <https://github.com/IAmSoThirsty/Project-AI/discussions>
- 📧 MCP Protocol: <https://modelcontextprotocol.io/>

---

## API Reference

### MCP Server Module

**[[API_QUICK_REFERENCE#core/mcp_server.py|ProjectAIMCPServer]]** - MCP server implementation

Located in: `src/app/core/mcp_server.py`

#### Core Functionality

- **`ProjectAIMCPServer`** - Main MCP server class
  - Exposes Project-AI functionality via Model Context Protocol
  - Integrates with Claude Desktop, Copilot, and other MCP clients
  - Provides tools for AI ethics, memory, learning, utilities

#### Available MCP Tools

**Ethics & Persona Tools**:
- `validate_action` - Powered by [[API_QUICK_REFERENCE#core/ai_systems.py|FourLaws.validate_action()]]
- `get_persona_state` - Powered by [[API_QUICK_REFERENCE#core/ai_systems.py|AIPersona.get_state()]]
- `adjust_persona_trait` - Powered by [[API_QUICK_REFERENCE#core/ai_systems.py|AIPersona.update_trait()]]

**Memory & Learning Tools**:
- `add_memory` - Powered by [[API_QUICK_REFERENCE#core/ai_systems.py|MemoryExpansionSystem.add_memory()]]
- `search_memory` - Powered by [[API_QUICK_REFERENCE#core/ai_systems.py|MemoryExpansionSystem.search_memory()]]
- `submit_learning_request` - Powered by [[API_QUICK_REFERENCE#core/ai_systems.py|LearningRequestManager.request_learning()]]
- `approve_learning_request` - Powered by [[API_QUICK_REFERENCE#core/ai_systems.py|LearningRequestManager.approve_request()]]

**Utility Tools**:
- `analyze_data` - Powered by [[API_QUICK_REFERENCE#core/data_analysis.py|DataAnalyzer.analyze_file()]]
- `track_location` - Powered by [[API_QUICK_REFERENCE#core/location_tracker.py|LocationTracker.track_location()]]
- `send_emergency_alert` - Powered by [[API_QUICK_REFERENCE#core/emergency_alert.py|EmergencyAlert.send_alert()]]
- `generate_image` - Powered by [[API_QUICK_REFERENCE#core/image_generator.py|ImageGenerator.generate()]]

**Plugin Tools**:
- `list_plugins` - Powered by [[API_QUICK_REFERENCE#core/ai_systems.py|PluginManager.get_enabled_plugins()]]
- `enable_plugin` - Powered by [[API_QUICK_REFERENCE#core/ai_systems.py|PluginManager.enable_plugin()]]
- `disable_plugin` - Powered by [[API_QUICK_REFERENCE#core/ai_systems.py|PluginManager.disable_plugin()]]

### Core Dependencies

The MCP server integrates these core modules:

- **[[API_QUICK_REFERENCE#core/ai_systems.py|ai_systems.py]]** - Six AI systems (FourLaws, AIPersona, Memory, Learning, Override, Plugins)
- **[[API_QUICK_REFERENCE#core/intelligence_engine.py|intelligence_engine.py]]** - OpenAI integration
- **[[API_QUICK_REFERENCE#core/image_generator.py|image_generator.py]]** - Image generation backends
- **[[API_QUICK_REFERENCE#core/data_analysis.py|data_analysis.py]]** - Data analysis utilities
- **[[API_QUICK_REFERENCE#core/location_tracker.py|location_tracker.py]]** - Location tracking
- **[[API_QUICK_REFERENCE#core/emergency_alert.py|emergency_alert.py]]** - Emergency alerts

### Related Documentation

- **MCP Configuration**: [[MCP_CONFIGURATION]] (advanced MCP settings)
- **AI Persona Guide**: [[AI_PERSONA_IMPLEMENTATION]] (persona system deep-dive)
- **Learning System**: [[LEARNING_REQUEST_IMPLEMENTATION]] (learning workflow)
- **Desktop App**: [[DESKTOP_APP_QUICKSTART]] (full application setup)
- **API Reference**: [[API_QUICK_REFERENCE]] (339 modules)

---

**Ready to use Project-AI with your favorite AI assistant! 🚀**

---

**Quick Navigation**:
- [[#Quick Setup (5 minutes)|↑ Setup]]
- [[#Available Tools|↑ Tools]]
- [[#Troubleshooting|↑ Troubleshooting]]
- [[API_QUICK_REFERENCE|→ Full API Reference]]
- [[MCP_CONFIGURATION|→ Advanced Configuration]]
