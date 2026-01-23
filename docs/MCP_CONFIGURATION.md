# Model Context Protocol (MCP) Configuration for Project-AI

## Overview

Project-AI provides a comprehensive MCP (Model Context Protocol) server implementation that exposes its advanced AI capabilities to MCP-compatible clients like Claude Desktop, enabling seamless integration with AI assistants.

## Features

The Project-AI MCP server provides access to:

### 🧠 AI Systems

- **AI Ethics Framework (Asimov's Laws)**: Validate actions against ethical guidelines
- **AI Persona**: Manage personality traits and emotional states
- **Memory System**: Store and retrieve knowledge across sessions
- **Learning System**: Submit and approve autonomous learning requests

### 🛠️ Tools (14 Available)

1. **validate_action** - Validate actions against AI ethics framework
1. **get_persona_state** - Get current AI personality and mood
1. **adjust_persona_trait** - Modify personality traits (curiosity, empathy, patience, etc.)
1. **add_memory** - Add knowledge to the memory system
1. **search_memory** - Search the knowledge base
1. **submit_learning_request** - Request AI to learn new content
1. **approve_learning_request** - Approve pending learning requests
1. **analyze_data** - Analyze CSV, Excel, or JSON files
1. **track_location** - Get IP geolocation information
1. **send_emergency_alert** - Send emergency notifications
1. **generate_image** - Generate images using Stable Diffusion or DALL-E
1. **list_plugins** - List available plugins
1. **enable_plugin** - Enable a plugin
1. **disable_plugin** - Disable a plugin

### 📚 Resources (4 Available)

1. **persona://state** - Current AI persona configuration
1. **memory://knowledge** - Complete knowledge base
1. **learning://requests** - All learning requests
1. **plugins://list** - Plugin list and status

### 💬 Prompts (3 Available)

1. **analyze_with_ethics** - Ethical action analysis
1. **persona_interaction** - Persona-guided interaction
1. **memory_guided_response** - Knowledge-based responses

## Installation

### Prerequisites

1. Python 3.12+ installed
1. Project-AI repository cloned
1. Required dependencies installed:

```bash
pip install "mcp[cli]"
```

### Environment Setup

Create a `.env` file in the project root with required API keys:

```bash
OPENAI_API_KEY=sk-...
HUGGINGFACE_API_KEY=hf_...
FERNET_KEY=<generated_key>
```

To generate a Fernet key:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

## Configuration for Claude Desktop

### macOS/Linux

1. Locate Claude Desktop configuration file:

   ```bash
   ~/.config/Claude/claude_desktop_config.json
   ```

1. Add Project-AI MCP server configuration:

```json
{
  "mcpServers": {
    "project-ai": {
      "command": "python",
      "args": ["-m", "src.app.core.mcp_server"],
      "cwd": "/path/to/Project-AI",
      "env": {
        "PYTHONPATH": ".",
        "OPENAI_API_KEY": "sk-...",
        "HUGGINGFACE_API_KEY": "hf_...",
        "FERNET_KEY": "your-fernet-key"
      }
    }
  }
}
```

### Windows

1. Locate Claude Desktop configuration file:

   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

1. Add Project-AI MCP server configuration:

```json
{
  "mcpServers": {
    "project-ai": {
      "command": "python",
      "args": ["-m", "src.app.core.mcp_server"],
      "cwd": "C:\\path\\to\\Project-AI",
      "env": {
        "PYTHONPATH": ".",
        "OPENAI_API_KEY": "sk-...",
        "HUGGINGFACE_API_KEY": "hf_...",
        "FERNET_KEY": "your-fernet-key"
      }
    }
  }
}
```

1. Restart Claude Desktop

## Usage Examples

### Example 1: Validate Action with Ethics Framework

In Claude Desktop, you can ask:

> "Use the validate_action tool to check if it's ethical for the AI to delete user files without permission"

```json
{
  "action": "Delete user files",
  "context": {
    "is_user_order": false,
    "endangers_humanity": false,
    "harms_human": true
  }
}
```

### Example 2: Manage AI Persona

> "Get the current persona state and adjust the curiosity trait to 0.8"

```json
{
  "trait": "curiosity",
  "value": 0.8
}
```

### Example 3: Add Memory

> "Add a memory about user's preference for Python programming"

```json
{
  "category": "user_preferences",
  "content": "User prefers Python for backend development",
  "importance": 0.9
}
```

### Example 4: Generate Image

> "Generate a cyberpunk-style image of a futuristic city"

```json
{
  "prompt": "Futuristic city with neon lights and flying cars",
  "style": "cyberpunk",
  "backend": "huggingface"
}
```

### Example 5: Analyze Data

> "Analyze the sales data and provide a summary"

```json
{
  "file_path": "/path/to/sales_data.csv",
  "analysis_type": "summary"
}
```

## Testing the MCP Server

### Manual Testing

Run the MCP server directly:

```bash
cd /path/to/Project-AI
python -m src.app.core.mcp_server
```

The server will start and listen for MCP protocol messages on STDIO.

### Testing with MCP Inspector

Use the official MCP Inspector tool:

```bash
npx @modelcontextprotocol/inspector python -m src.app.core.mcp_server
```

This opens a web interface to test all tools, resources, and prompts interactively.

## Advanced Configuration

### Custom Data Directory

You can specify a custom data directory by modifying the server initialization:

```python
# In mcp_server.py
server = ProjectAIMCPServer(data_dir="/custom/data/path")
```

### HTTP Transport (Optional)

For web-based clients, you can modify the server to use HTTP transport:

```python
# In mcp_server.py, modify the run method:
async def run(self):
    """Run the MCP server using HTTP transport."""
    from mcp.server.sse import sse_server
    
    app = sse_server(self.server)
    # Run with uvicorn or another ASGI server
```

### Adding Custom Tools

To add custom tools to the MCP server:

1. Add tool definition in `_register_tools()`:

```python
Tool(
    name="custom_tool",
    description="Description of custom tool",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "Parameter"}
        },
        "required": ["param"]
    }
)
```

1. Add tool implementation:

```python
async def _custom_tool(self, args: Dict[str, Any]) -> List[TextContent]:
    """Custom tool implementation."""
    param = args.get("param")
    # Tool logic here
    result = {"result": "value"}
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
```

1. Add handler in `call_tool()`:

```python
elif name == "custom_tool":
    return await self._custom_tool(arguments)
```

## Security Considerations

### 1. API Key Protection

- Never commit API keys to version control
- Use environment variables or `.env` files
- Restrict file permissions on configuration files

```bash
chmod 600 ~/.config/Claude/claude_desktop_config.json
```

### 2. Data Access Control

- The MCP server has access to all Project-AI data
- Ensure proper file system permissions on the data directory
- Review tool access before deployment

### 3. Command Override System

The command override tool requires additional authentication:

```python
# Protected by master password
self.override.validate_override(password, action)
```

### 4. Learning Request Approval

All learning requests require human approval before execution:

```python
# Requires explicit approval
self.learning.approve_request(request_id)
```

## Troubleshooting

### Server Not Starting

**Issue**: MCP server fails to start

**Solutions**:

1. Check Python version: `python --version` (requires 3.12+)
1. Verify dependencies: `pip install "mcp[cli]"`
1. Check PYTHONPATH: Should include project root
1. Review logs in stderr

### Tool Execution Errors

**Issue**: Tools return errors

**Solutions**:

1. Verify environment variables are set correctly
1. Check data directory permissions
1. Ensure required API keys are valid
1. Review tool-specific error messages

### Claude Desktop Not Detecting Server

**Issue**: Claude Desktop doesn't show MCP tools

**Solutions**:

1. Verify configuration file path is correct
1. Check JSON syntax in `claude_desktop_config.json`
1. Restart Claude Desktop after configuration changes
1. Check server logs for initialization errors

### Import Errors

**Issue**: Python import errors for core systems

**Solutions**:

1. Ensure PYTHONPATH includes project root
1. Verify all dependencies are installed: `pip install -r requirements.txt`
1. Check that Project-AI is properly installed

## Performance Optimization

### 1. Lazy Loading

Core systems are initialized on first use to improve startup time:

```python
# Systems are initialized in __init__ but gracefully handle failures
try:
    from app.core.ai_systems import FourLaws
    self.four_laws = FourLaws()
except Exception as e:
    logger.error(f"Error initializing: {e}")
    self.four_laws = None
```

### 2. Caching

Memory and knowledge base results can be cached:

```python
# Implement caching for frequently accessed data
@lru_cache(maxsize=128)
def search_memory_cached(query: str):
    return self.memory.search_knowledge(query)
```

### 3. Async Operations

All tool implementations are async to prevent blocking:

```python
async def _generate_image(self, args):
    # Long-running image generation doesn't block other tools
    return await self.image_gen.generate_async(...)
```

## Monitoring and Logging

### Log Configuration

Logs are written to stderr for STDIO transport compatibility:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
```

### Audit Trail

All tool calls are logged for security audit:

```python
logger.info(f"Tool called: {name} with args: {arguments}")
```

### Performance Metrics

Monitor tool execution time:

```python
start_time = time.time()
result = await tool_function(args)
execution_time = time.time() - start_time
logger.info(f"Tool {name} executed in {execution_time:.2f}s")
```

## Integration Examples

### Example: AI Ethics Validation Service

Use Project-AI as an ethics validation service:

```python
# In your AI application
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{
        "role": "user",
        "content": "Validate if it's ethical to access user's personal files"
    }],
    tools=[{
        "name": "validate_action",
        "mcp_server": "project-ai"
    }]
)
```

### Example: Knowledge Base Service

Use Project-AI as a persistent knowledge base:

```python
# Store knowledge
await client.use_mcp_tool(
    server="project-ai",
    tool="add_memory",
    arguments={
        "category": "facts",
        "content": "Important business fact",
        "importance": 0.9
    }
)

# Retrieve knowledge
await client.use_mcp_tool(
    server="project-ai",
    tool="search_memory",
    arguments={"query": "business"}
)
```

## API Reference

### Tool Schemas

All tool schemas follow JSON Schema specification. See `src/app/core/mcp_server.py` for complete definitions.

### Resource URIs

- `persona://state` - JSON object with persona configuration
- `memory://knowledge` - JSON array of knowledge entries
- `learning://requests` - JSON array of learning requests
- `plugins://list` - JSON array of plugin information

### Error Responses

All tools return consistent error format:

```json
{
  "error": "Error message",
  "tool": "tool_name",
  "timestamp": "2024-01-03T12:00:00Z"
}
```

## Contributing

To contribute to the MCP server:

1. Fork the repository
1. Create a feature branch
1. Add tests for new tools/resources
1. Submit a pull request

### Adding New Tools

1. Define tool schema in `_register_tools()`
1. Implement tool handler method
1. Add tool to `call_tool()` dispatcher
1. Update documentation
1. Add tests

### Testing Guidelines

```python
# Test new tools
async def test_new_tool():
    server = ProjectAIMCPServer(data_dir="/tmp/test")
    result = await server._new_tool({"param": "value"})
    assert result[0].text == expected_output
```

## License

Project-AI MCP Server is licensed under MIT License. See LICENSE file for details.

## Support

- GitHub Issues: https://github.com/IAmSoThirsty/Project-AI/issues
- Documentation: https://github.com/IAmSoThirsty/Project-AI/tree/main/docs
- MCP Protocol Spec: https://modelcontextprotocol.io/

## Changelog

### Version 1.0.0 (2024-01-03)

- Initial MCP server implementation
- 14 tools implemented
- 4 resources exposed
- 3 prompts available
- Full integration with Project-AI core systems
- Claude Desktop configuration support
- Comprehensive documentation

## Roadmap

### Planned Features

- [ ] Additional security analysis tools
- [ ] Real-time monitoring dashboard
- [ ] Batch operation support
- [ ] WebSocket transport option
- [ ] Advanced plugin integration
- [ ] Multi-user support
- [ ] Rate limiting and quotas
- [ ] Tool chaining capabilities
- [ ] Custom prompt templates
- [ ] Enhanced error recovery

---

**Project-AI MCP Server** - Bringing ethical AI capabilities to your favorite AI assistants through the Model Context Protocol.
