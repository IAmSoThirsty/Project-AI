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

### 🧠 AI Ethics & Persona

- `validate_action` - Check if actions align with AI ethics
- `get_persona_state` - View AI personality and mood
- `adjust_persona_trait` - Modify personality traits

### 💾 Memory & Learning

- `add_memory` - Store information in knowledge base
- `search_memory` - Search stored knowledge
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

- Read full documentation: [docs/MCP_CONFIGURATION.md](MCP_CONFIGURATION.md)
- Explore example prompts: [examples/mcp_examples.md](../examples/mcp_examples.md)
- Add custom tools: See "Advanced Configuration" section
- Review security best practices: [SECURITY.md](../SECURITY.md)

## Support

- 📖 Documentation: `/docs/MCP_CONFIGURATION.md`
- 🐛 Issues: https://github.com/IAmSoThirsty/Project-AI/issues
- 💬 Discussions: https://github.com/IAmSoThirsty/Project-AI/discussions
- 📧 MCP Protocol: https://modelcontextprotocol.io/

---

**Ready to use Project-AI with your favorite AI assistant! 🚀**
