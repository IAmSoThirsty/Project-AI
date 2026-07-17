# Project-AI Extensions & Plugins Framework

## Overview

Project-AI supports community-contributed extensions and plugins through a secure, governed framework that maintains constitutional integrity while enabling extensibility.

## Plugin Architecture

All plugins operate within the Constitutional Governance framework:

```
User Request
    ↓
Plugin Interface (MCP / REST)
    ↓
Galahad (legitimacy check)
    ↓
Cerberus (security boundary)
    ↓
Codex (constitutional policy)
    ↓
Plugin Execution (sandboxed)
    ↓
Audit Trail
```

## Creating a Plugin

### 1. Plugin Manifest (`plugin.yaml`)

```yaml
name: plugin-awesome-tool
version: 1.0.0
author: Your Name
description: Does awesome things within Project-AI
publisher: ghcr.io/yourorg

capabilities:
  - governance:read
  - memory:read-write
  - audit:read
  - execution:sandbox

constraints:
  - max_memory_mb: 256
  - max_execution_time_sec: 30
  - no_external_network: true
  - no_file_system_write: true

permissions_required:
  - from: galahad
  - from: cerberus

dependencies:
  - project-ai-api >= 0.0.0
```

### 2. Plugin Implementation

**Python Plugin:**

```python
# plugin/awesome_tool.py
from project_ai.extensions import ProjectAIPlugin, capability, governed

class AwesomeTool(ProjectAIPlugin):
    """Your plugin class."""

    manifest_path = "plugin.yaml"

    @governed(capabilities=["memory:read-write"], authority="galahad")
    async def process(self, input_data):
        """Process data through the governance framework."""
        # Your implementation here
        return result

    @capability("execution:sandbox")
    async def execute_safe(self, code):
        """Execute code in sandboxed environment."""
        # Safely execute user code
        pass
```

**REST Plugin:**

```bash
# Your plugin runs as a separate service
# Project-AI communicates via REST with governance headers

POST /plugin/awesome-tool/process
Headers:
  Authorization: Bearer <capability-token>
  X-Governance-Mode: strict
  X-Audit-ID: <transaction-id>
Body:
  {"data": ...}
```

### 3. Registering a Plugin

```bash
# Register locally during development
project-ai plugin register ./plugin/

# Publish to registry
project-ai plugin publish ghcr.io/yourorg/plugin-awesome-tool:1.0.0

# Install from registry
project-ai plugin install ghcr.io/yourorg/plugin-awesome-tool:1.0.0
```

## Built-in Plugin Categories

### Memory Plugins
- Extend CCMA memory system
- Read/write to memory domains
- Transform memory representation
- Example: `plugin-memory-export` (export to external DB)

### Governance Plugins
- Extend Constitutional policy
- Add custom verdicts
- Modify deliberation logic
- Example: `plugin-governance-audit-webhook` (push audit events)

### Integration Plugins
- Connect to external systems
- API adapters
- Data pipeline connectors
- Example: `plugin-slack-alerts` (send governance events to Slack)

### Analytics Plugins
- Query governance data
- Generate reports
- Visualize decision patterns
- Example: `plugin-analytics-dashboard` (custom Grafana integration)

## Plugin Security

### Sandboxing
- Each plugin runs in isolated container
- Resource limits enforced (CPU, memory, time)
- Network isolation by default
- File system access restricted to plugin's `/data` directory

### Governance
- All plugin calls require capability tokens
- Tokens expire after execution
- Audit trail records all plugin activity
- Galahad verifies legitimacy
- Cerberus enforces security boundaries

### Code Review
- Manual review for first-time publishers
- Automated scanning for CVEs
- Signature verification
- Rollback capability if security issues found

## Publishing Guidelines

### Code Quality
- 80% test coverage minimum
- Linting passes (`ruff check`)
- Type checking passes (`mypy --strict`)
- Security scanning passes (`bandit`)

### Documentation
- README with examples
- API documentation
- Configuration guide
- Troubleshooting section

### Compliance
- No hardcoded secrets
- No external network calls without consent
- No persistence outside `/data` directory
- Licensing compatible with MIT

## Example Plugins

### 1. Memory Export Plugin

```python
# Export memory to PostgreSQL
class MemoryExportPlugin(ProjectAIPlugin):
    @governed(capabilities=["memory:read"])
    async def export_memory(self, domain):
        """Export a memory domain to Postgres."""
        memory = await self.api.memory.query(domain)
        for record in memory:
            await self.postgres.insert("memory", record)
        return {"exported": len(memory)}
```

### 2. Slack Integration Plugin

```python
# Send audit events to Slack
class SlackAlertsPlugin(ProjectAIPlugin):
    @governed(capabilities=["audit:read"])
    async def on_verdict(self, verdict):
        """Forward governance verdicts to Slack."""
        if verdict["status"] == "DENY":
            await self.slack.post(
                channel="#security-alerts",
                text=f"🚫 Verdict DENIED: {verdict['reason']}"
            )
```

### 3. Custom Dashboard Plugin

```python
# Grafana dashboard for governance metrics
class GovernanceDashboardPlugin(ProjectAIPlugin):
    @governed(capabilities=["governance:read"])
    async def get_metrics(self):
        """Get governance metrics for visualization."""
        return {
            "verdicts_today": await self.api.governance.verdicts_count(),
            "avg_verdict_time_ms": await self.api.governance.avg_latency(),
            "policy_violations": await self.api.governance.violations_count()
        }
```

## Plugin Lifecycle

1. **Development**: Build locally, test against test API
2. **Testing**: Run security scans, code quality checks
3. **Publishing**: Push to registry, submit for review
4. **Review**: Automated + manual security review
5. **Approval**: Certificate signed, added to trust anchor
6. **Installation**: Users install from verified registry
7. **Execution**: Runs under governance + audit trail
8. **Monitoring**: Metrics and logs captured
9. **Deprecation**: Version sunset with 90-day notice

## API Reference

### Plugin Base Class

```python
class ProjectAIPlugin:
    # Read governance configuration
    async def get_constitution() -> dict

    # Query memory system
    async def memory.query(domain: str, filter: dict) -> list
    async def memory.store(domain: str, content: dict) -> str

    # Verify audit trail
    async def audit.query(filter: dict) -> list
    async def audit.verify_chain() -> bool

    # Get current capabilities
    async def get_capabilities() -> list[str]

    # Log events to audit trail
    async def audit_log(event: dict) -> None
```

### Governance Context

Every plugin call receives:

```python
context = {
    "request_id": "req_xxx",
    "actor": "human|ai|system",
    "capabilities": ["memory:read", ...],
    "authority": "galahad|cerberus|codex",
    "timestamp": "2026-01-01T00:00:00Z",
    "audit_id": "audit_xxx"
}
```

## Contributing Plugins

To contribute to the official plugin registry:

1. Fork the plugin template
2. Implement your plugin
3. Create pull request with:
   - Code review checklist
   - Security scan results
   - Testing evidence
   - Documentation
4. Core team reviews and approves
5. Merged to plugin registry

## Support

- **Documentation**: https://docs.project-ai.github.io/plugins
- **Examples**: https://github.com/project-ai/plugin-examples
- **Security Issues**: security@project-ai.dev
- **Community**: https://discussions.project-ai.github.io
