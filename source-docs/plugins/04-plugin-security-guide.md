---
type: guide
guide_type: security
area: plugin-system
audience: [developer, security-engineer]
prerequisites:
  - 01-plugin-architecture-overview.md
  - 02-plugin-api-reference.md
  - Understanding of process isolation
tags:
  - plugin/security
  - isolation
  - four-laws
  - sandbox
related_docs:
  - 03-plugin-loading-lifecycle.md
  - ../security/SECURITY_AUDIT_GUIDE.md
last_updated: 2026-04-20
version: 1.0.0
---

# Plugin Security Guide

**Comprehensive security practices for plugin development and deployment**  
**Version:** 1.0.0  
**Last Updated:** 2026-04-20

---

## Table of Contents

1. [Security Overview](#security-overview)
2. [Four Laws Validation](#four-laws-validation)
3. [Process Isolation](#process-isolation)
4. [Input Validation](#input-validation)
5. [Resource Limits](#resource-limits)
6. [Secure Plugin Development](#secure-plugin-development)
7. [Threat Model](#threat-model)
8. [Security Checklist](#security-checklist)

---

## Security Overview

### Security Layers

The Project-AI plugin system implements **defense in depth** with multiple security layers:

```
┌──────────────────────────────────────────────────────────┐
│ Layer 1: Four Laws Validation (Ethics Layer)            │
│ ✓ Validate all actions against Asimov's Laws            │
│ ✓ Block harmful operations before execution             │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│ Layer 2: Context Validation (Input Layer)               │
│ ✓ Validate plugin inputs and context                    │
│ ✓ Sanitize user-provided data                           │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│ Layer 3: Process Isolation (Execution Layer)            │
│ ✓ Execute plugins in separate processes                 │
│ ✓ Enforce timeout and resource limits                   │
└───────────────────────┬──────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│ Layer 4: Capability Restrictions (Permission Layer)     │
│ ✓ Restrict filesystem access (TODO)                     │
│ ✓ Restrict network access (TODO)                        │
└──────────────────────────────────────────────────────────┘
```

### Security Principles

1. **Least Privilege** - Plugins run with minimum required permissions
2. **Fail Secure** - Security failures block execution (deny by default)
3. **Defense in Depth** - Multiple independent security layers
4. **Explicit Authorization** - All actions require explicit approval
5. **Audit Everything** - All plugin operations logged and traceable

---

## Four Laws Validation

### Overview

All plugins MUST validate actions against Asimov's Four Laws before execution. This is the **primary security layer** that enforces ethical behavior.

### Four Laws Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│ FIRST LAW (Highest Priority)                            │
│ Don't harm humans or allow harm through inaction        │
│ → Blocks: data deletion, privacy violations, harmful AI │
└───────────────────────┬─────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│ SECOND LAW                                              │
│ Follow user orders (unless conflicts with First Law)    │
│ → Blocks: unauthorized actions, actions without consent │
└───────────────────────┬─────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│ THIRD LAW (Lowest Priority)                             │
│ Self-preservation (unless conflicts with First/Second)  │
│ → Blocks: self-destructive actions                      │
└─────────────────────────────────────────────────────────┘
```

### Implementation

```python
from app.core.ai_systems import FourLaws, Plugin
from app.core.observability import emit_event
import logging

logger = logging.getLogger(__name__)

class SecurePlugin(Plugin):
    """Plugin with Four Laws validation."""
    
    def initialize(self, context: dict) -> bool:
        """Initialize with Four Laws check."""
        # Step 1: Prepare validation context
        validation_context = {
            "harms_human": context.get("harms_human", False),
            "allows_harm_by_inaction": context.get("allows_harm_by_inaction", False),
            "is_user_order": context.get("is_user_order", False),
            "protects_human": context.get("protects_human", False),
            "endangers_self": context.get("endangers_self", False),
            "protect_self_conflicts_with_first": False,
            "protect_self_conflicts_with_second": False,
        }
        
        # Step 2: Validate against Four Laws
        allowed, reason = FourLaws.validate_action(
            f"Initialize plugin '{self.name}'",
            context=validation_context
        )
        
        # Step 3: Handle validation result
        if not allowed:
            logger.warning("Plugin blocked by Four Laws: %s", reason)
            emit_event("plugin.blocked", {
                "name": self.name,
                "reason": reason,
                "action": "initialize"
            })
            return False
        
        # Step 4: Log approval
        logger.info("Plugin allowed by Four Laws: %s", reason)
        emit_event("plugin.allowed", {
            "name": self.name,
            "reason": reason,
            "action": "initialize"
        })
        
        # Step 5: Continue initialization
        self.enabled = True
        return True
    
    def execute_action(self, action: str, context: dict) -> dict:
        """Execute action with Four Laws validation."""
        # Validate every action, not just initialization
        validation_context = {
            "harms_human": self._would_harm_human(action, context),
            "is_user_order": context.get("is_user_order", False),
            # ... other flags ...
        }
        
        allowed, reason = FourLaws.validate_action(action, validation_context)
        
        if not allowed:
            raise PermissionError(f"Action blocked by Four Laws: {reason}")
        
        # Execute if allowed
        return self._do_execute(action, context)
    
    def _would_harm_human(self, action: str, context: dict) -> bool:
        """Determine if action would harm humans."""
        # Example: deleting user data harms users
        if "delete" in action.lower() and context.get("user_data"):
            return True
        
        # Example: exposing private data harms users
        if "expose" in action.lower() and context.get("private"):
            return True
        
        return False
```

### Validation Context Keys

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `harms_human` | bool | Action directly harms humans | `True` for "delete user account" |
| `allows_harm_by_inaction` | bool | Inaction allows harm | `True` for "ignore security alert" |
| `is_user_order` | bool | User explicitly ordered action | `True` for button click |
| `protects_human` | bool | Action protects humans | `True` for "backup data" |
| `endangers_self` | bool | Action endangers AI | `True` for "delete AI state" |
| `protect_self_conflicts_with_first` | bool | Self-protection harms humans | `True` for "refuse to shutdown during emergency" |
| `protect_self_conflicts_with_second` | bool | Self-protection disobeys order | `True` for "refuse user's shutdown command" |

### Best Practices

#### ✅ DO: Validate All Actions

```python
# ✅ GOOD: Every action validated
def delete_data(self, data_id: str) -> bool:
    allowed, reason = FourLaws.validate_action(
        "Delete user data",
        context={"harms_human": True, "is_user_order": True}
    )
    if not allowed:
        return False
    # ... proceed with deletion ...
```

#### ❌ DON'T: Skip Validation

```python
# ❌ BAD: No validation!
def delete_data(self, data_id: str) -> bool:
    # Directly delete without checking Four Laws
    os.remove(f"data/{data_id}")  # DANGEROUS!
```

#### ✅ DO: Emit Telemetry on Block

```python
if not allowed:
    emit_event("plugin.action_blocked", {
        "plugin": self.name,
        "action": action,
        "reason": reason
    })
    return False
```

#### ✅ DO: Conservative Evaluation

```python
# ✅ GOOD: Assume harmful if unsure
def _would_harm_human(self, action: str, context: dict) -> bool:
    # If we can't determine safety, assume harmful
    if not context.get("safety_verified"):
        return True  # Fail safe
    
    # Check specific harm indicators
    return self._check_harm_indicators(action, context)
```

---

## Process Isolation

### Overview

Process isolation executes plugins in separate OS processes, providing memory isolation and preventing direct access to the main application's memory space.

### Isolation Levels

| Level | Mechanism | Security | Performance | Use Case |
|-------|-----------|----------|-------------|----------|
| **None** | In-process execution | ❌ Low | ✅ Fast | Trusted internal plugins |
| **Basic** | subprocess.Popen | ⚠️ Medium | ⚠️ Medium | Verified plugins |
| **Full** | multiprocessing.Process | ✅ High | ❌ Slow | Untrusted/hostile plugins |

### System C: Subprocess Isolation

**Security Features:**
- ✅ Separate process memory space
- ✅ Timeout enforcement with process termination
- ✅ Graceful shutdown (SIGTERM → SIGKILL)
- ⚠️ No filesystem/network isolation

**Usage:**

```python
from app.plugins.plugin_runner import PluginRunner
import logging

logger = logging.getLogger(__name__)

def run_isolated_plugin(plugin_script: str, params: dict) -> dict:
    """Execute plugin in isolated subprocess."""
    runner = PluginRunner(plugin_script, timeout=10.0)
    
    try:
        # Start subprocess
        runner.start()
        logger.info("Started isolated plugin: %s", plugin_script)
        
        # Call init with timeout enforcement
        response = runner.call_init(params)
        
        # Check response
        if "error" in response:
            logger.error("Plugin error: %s", response["error"])
            raise RuntimeError(f"Plugin error: {response['error']}")
        
        return response.get("result", {})
        
    except TimeoutError as e:
        logger.error("Plugin timeout: %s", e)
        raise
    
    except Exception as e:
        logger.exception("Plugin execution failed: %s", e)
        raise
    
    finally:
        # Always cleanup subprocess
        runner.stop()
        logger.info("Stopped isolated plugin: %s", plugin_script)
```

### System D: Multiprocessing Isolation

**Security Features:**
- ✅ Complete memory isolation
- ✅ Timeout enforcement
- ✅ Exception capture and propagation
- ⚠️ No filesystem/network isolation

**Usage:**

```python
from app.security.agent_security import PluginIsolation
import logging

logger = logging.getLogger(__name__)

def execute_hostile_plugin(plugin_func, *args, **kwargs):
    """Execute potentially hostile plugin with full isolation."""
    try:
        result = PluginIsolation.execute_isolated(
            plugin_func,
            *args,
            timeout=30,  # 30 second limit
            **kwargs
        )
        
        logger.info("Plugin executed successfully")
        return result
        
    except TimeoutError as e:
        logger.error("Plugin exceeded timeout: %s", e)
        # Handle timeout - plugin was killed
        raise
    
    except RuntimeError as e:
        logger.error("Plugin raised exception: %s", e)
        # Handle plugin error
        raise
```

### Timeout Best Practices

```python
# ✅ GOOD: Reasonable timeouts based on operation
class TimeoutAwarePlugin(Plugin):
    TIMEOUTS = {
        "quick_operation": 5,    # 5 seconds
        "data_processing": 30,   # 30 seconds
        "ml_inference": 120,     # 2 minutes
    }
    
    def execute(self, operation: str, context: dict) -> dict:
        timeout = self.TIMEOUTS.get(operation, 30)  # Default 30s
        
        runner = PluginRunner(self.script_path, timeout=timeout)
        try:
            return runner.call_init({"operation": operation, **context})
        finally:
            runner.stop()

# ❌ BAD: No timeout or unreasonable timeout
runner = PluginRunner(script, timeout=None)  # Can hang forever!
runner = PluginRunner(script, timeout=0.1)   # Too short, always fails
```

---

## Input Validation

### Context Validation

All plugins MUST validate execution context before processing:

```python
from app.core.interfaces import PluginInterface

class ValidatedPlugin(PluginInterface):
    """Plugin with comprehensive input validation."""
    
    def validate_context(self, context: dict) -> bool:
        """Validate execution context structure and values."""
        # Step 1: Check required keys
        required_keys = ["action", "data"]
        for key in required_keys:
            if key not in context:
                logger.error("Missing required key: %s", key)
                return False
        
        # Step 2: Validate data types
        if not isinstance(context["action"], str):
            logger.error("'action' must be string, got %s", type(context["action"]))
            return False
        
        if not isinstance(context["data"], (list, dict)):
            logger.error("'data' must be list or dict, got %s", type(context["data"]))
            return False
        
        # Step 3: Validate value ranges
        if "limit" in context:
            if not isinstance(context["limit"], int) or context["limit"] < 1:
                logger.error("'limit' must be positive integer")
                return False
        
        # Step 4: Sanitize strings
        action = context["action"]
        if not self._is_safe_string(action):
            logger.error("Action contains unsafe characters: %s", action)
            return False
        
        return True
    
    def _is_safe_string(self, s: str) -> bool:
        """Check if string is safe (no injection attacks)."""
        # Whitelist approach: only allow alphanumeric + underscore
        import re
        return bool(re.match(r'^[a-zA-Z0-9_]+$', s))
```

### Input Sanitization

```python
import html
import re
from pathlib import Path

class SanitizedPlugin(Plugin):
    """Plugin with input sanitization."""
    
    def sanitize_html(self, user_input: str) -> str:
        """Sanitize HTML to prevent XSS attacks."""
        return html.escape(user_input)
    
    def sanitize_path(self, user_path: str) -> Path:
        """Sanitize file path to prevent directory traversal."""
        # Resolve to absolute path
        path = Path(user_path).resolve()
        
        # Ensure path is within allowed directory
        allowed_dir = Path("data/plugins").resolve()
        
        if not str(path).startswith(str(allowed_dir)):
            raise ValueError(f"Path outside allowed directory: {path}")
        
        return path
    
    def sanitize_sql(self, user_input: str) -> str:
        """Sanitize SQL input (prefer parameterized queries)."""
        # Remove SQL keywords and special characters
        dangerous_patterns = [
            r";\s*--",      # SQL comments
            r"\bDROP\b",    # DROP statements
            r"\bDELETE\b",  # DELETE statements
            r"\bUPDATE\b",  # UPDATE statements
            r"\bINSERT\b",  # INSERT statements
            r"\bEXEC\b",    # EXEC statements
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                raise ValueError(f"Dangerous SQL pattern detected: {pattern}")
        
        return user_input
    
    def sanitize_command(self, user_input: str) -> str:
        """Sanitize shell command input (prefer parameterized commands)."""
        # Reject any input with shell metacharacters
        dangerous_chars = [";", "&", "|", "`", "$", "(", ")", "<", ">", "\n"]
        
        for char in dangerous_chars:
            if char in user_input:
                raise ValueError(f"Dangerous character in command: {char}")
        
        return user_input
```

### Validation Patterns

#### Pattern 1: Whitelist Validation

```python
# ✅ GOOD: Whitelist allowed values
ALLOWED_ACTIONS = ["read", "write", "update", "delete"]

def validate_action(action: str) -> bool:
    return action in ALLOWED_ACTIONS

# ❌ BAD: Blacklist dangerous values (easy to bypass)
DANGEROUS_ACTIONS = ["rm", "drop", "exec"]

def validate_action(action: str) -> bool:
    return action not in DANGEROUS_ACTIONS  # Can be bypassed!
```

#### Pattern 2: Schema Validation

```python
from typing import Any

def validate_schema(data: dict, schema: dict) -> bool:
    """Validate data against schema."""
    for key, expected_type in schema.items():
        if key not in data:
            return False
        if not isinstance(data[key], expected_type):
            return False
    return True

# Usage
CONTEXT_SCHEMA = {
    "action": str,
    "data": (list, dict),
    "limit": int,
    "safe": bool,
}

if not validate_schema(context, CONTEXT_SCHEMA):
    raise ValueError("Context does not match schema")
```

---

## Resource Limits

### CPU and Memory Limits

**Current Status:** ⚠️ Not implemented (planned for Phase 2)

**Planned Implementation:**

```python
# Future API (not yet implemented)
from app.plugins.resource_limits import ResourceLimits

limits = ResourceLimits(
    max_memory_mb=512,      # Maximum 512 MB RAM
    max_cpu_percent=50,     # Maximum 50% CPU
    max_execution_seconds=30,  # Maximum 30 seconds
)

result = limits.execute_with_limits(plugin_func, *args, **kwargs)
```

### Timeout Enforcement

**Current Status:** ✅ Implemented

```python
# System C: Subprocess timeout
runner = PluginRunner(script, timeout=10.0)  # 10 second timeout
try:
    result = runner.call_init({})
except TimeoutError:
    print("Plugin exceeded 10 second limit")

# System D: Multiprocessing timeout
result = PluginIsolation.execute_isolated(
    plugin_func,
    timeout=30  # 30 second timeout
)
```

### File Descriptor Limits

```python
import resource

def set_file_descriptor_limit(max_fds: int = 100):
    """Limit number of open file descriptors."""
    resource.setrlimit(resource.RLIMIT_NOFILE, (max_fds, max_fds))

# Apply before loading plugins
set_file_descriptor_limit(100)
```

---

## Secure Plugin Development

### Security Checklist for Plugin Authors

#### ✅ Initialization

- [ ] Validate against Four Laws in `initialize()`
- [ ] Validate all context keys and types
- [ ] Sanitize user-provided inputs
- [ ] Use timeout for external API calls
- [ ] Log all initialization attempts

#### ✅ Execution

- [ ] Validate context in `validate_context()`
- [ ] Validate action parameters
- [ ] Use parameterized queries for databases
- [ ] Use allowlist for file/command operations
- [ ] Catch and handle all exceptions
- [ ] Emit telemetry events

#### ✅ Resource Management

- [ ] Close all resources in `shutdown()`
- [ ] Use context managers for file/network operations
- [ ] Set reasonable timeouts for all I/O
- [ ] Limit memory allocation
- [ ] Clean up temporary files

#### ✅ Security

- [ ] Never execute arbitrary code from user input
- [ ] Never construct SQL queries from concatenation
- [ ] Never use `eval()` or `exec()` on user input
- [ ] Validate file paths to prevent directory traversal
- [ ] Sanitize HTML output to prevent XSS
- [ ] Use HTTPS for all network requests
- [ ] Encrypt sensitive data at rest

### Secure Code Examples

#### ✅ Secure Database Access

```python
import sqlite3

# ✅ GOOD: Parameterized query
def get_user(user_id: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)  # Parameter, not concatenation
    )
    return cursor.fetchone()

# ❌ BAD: SQL injection vulnerability
def get_user(user_id: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.execute(
        f"SELECT * FROM users WHERE id = {user_id}"  # VULNERABLE!
    )
    return cursor.fetchone()
```

#### ✅ Secure File Access

```python
from pathlib import Path

# ✅ GOOD: Path validation
def read_file(filename: str) -> str:
    allowed_dir = Path("data/plugins").resolve()
    file_path = (allowed_dir / filename).resolve()
    
    # Prevent directory traversal
    if not str(file_path).startswith(str(allowed_dir)):
        raise ValueError("Path outside allowed directory")
    
    with open(file_path, encoding="utf-8") as f:
        return f.read()

# ❌ BAD: Directory traversal vulnerability
def read_file(filename: str) -> str:
    with open(f"data/plugins/{filename}") as f:
        # User can provide "../../etc/passwd"!
        return f.read()
```

#### ✅ Secure Command Execution

```python
import subprocess

# ✅ GOOD: Parameterized command
def run_command(file_path: str):
    # Validate input
    if not file_path.endswith(".txt"):
        raise ValueError("Only .txt files allowed")
    
    # Use list (not shell=True)
    result = subprocess.run(
        ["cat", file_path],  # Parameterized
        capture_output=True,
        text=True,
        shell=False  # Disable shell interpretation
    )
    return result.stdout

# ❌ BAD: Command injection vulnerability
def run_command(file_path: str):
    result = subprocess.run(
        f"cat {file_path}",  # User can inject "file; rm -rf /"
        shell=True,  # DANGEROUS!
        capture_output=True
    )
    return result.stdout
```

---

## Threat Model

### Threat Categories

| Threat | Impact | Mitigation | Status |
|--------|--------|------------|--------|
| **Malicious code execution** | Critical | Process isolation | ✅ Implemented |
| **Resource exhaustion** | High | Timeout enforcement | ✅ Implemented |
| **Data exfiltration** | Critical | Network isolation | ⚠️ TODO |
| **Privilege escalation** | Critical | Four Laws validation | ✅ Implemented |
| **Directory traversal** | High | Path validation | ⚠️ Partial |
| **SQL injection** | High | Input validation | ⚠️ Plugin responsibility |
| **Command injection** | Critical | Input sanitization | ⚠️ Plugin responsibility |
| **XSS attacks** | Medium | HTML escaping | ⚠️ Plugin responsibility |

### Attack Scenarios

#### Scenario 1: Malicious Plugin Execution

**Attack:** Plugin attempts to execute arbitrary code in main process

**Mitigation:**
```python
# ✅ Protected: Plugin runs in subprocess
runner = PluginRunner("untrusted_plugin.py", timeout=10.0)
try:
    result = runner.call_init({})
    # Plugin cannot access main process memory
except TimeoutError:
    # Plugin killed after 10 seconds
    pass
```

#### Scenario 2: Resource Exhaustion

**Attack:** Plugin allocates infinite memory or runs forever

**Mitigation:**
```python
# ✅ Protected: Timeout enforced
result = PluginIsolation.execute_isolated(
    resource_heavy_plugin,
    timeout=30  # Killed after 30 seconds
)
```

#### Scenario 3: Directory Traversal

**Attack:** Plugin reads `/etc/passwd` via `../../../etc/passwd`

**Mitigation:**
```python
# ✅ Protected: Path validation
def read_plugin_file(filename: str) -> str:
    allowed = Path("data/plugins").resolve()
    requested = (allowed / filename).resolve()
    
    if not str(requested).startswith(str(allowed)):
        raise ValueError("Path traversal blocked")
    
    return requested.read_text()
```

---

## Security Checklist

### For Plugin Authors

- [ ] Validate all inputs with `validate_context()`
- [ ] Validate actions against Four Laws
- [ ] Use parameterized queries for databases
- [ ] Validate and sanitize file paths
- [ ] Sanitize user input for HTML/SQL/commands
- [ ] Set timeouts on all I/O operations
- [ ] Close all resources in `shutdown()`
- [ ] Never use `eval()` or `exec()` on user input
- [ ] Log all security-relevant events
- [ ] Test plugin with malicious inputs

### For Plugin Operators

- [ ] Use System C/D for untrusted plugins
- [ ] Review plugin manifest for suspicious permissions
- [ ] Monitor plugin resource usage
- [ ] Review plugin audit logs regularly
- [ ] Update plugins to latest security patches
- [ ] Isolate sensitive data from plugins
- [ ] Use principle of least privilege
- [ ] Test plugins in sandboxed environment first
- [ ] Have incident response plan for plugin breaches

---

## References

- [Plugin Architecture Overview](./01-plugin-architecture-overview.md)
- [Plugin API Reference](./02-plugin-api-reference.md)
- [Plugin Development Guide](./05-plugin-development-guide.md)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)

---

**Author:** AGENT-046 (Plugin System Documentation Specialist)  
**Review Status:** 📝 Draft (requires security team review)  
**Next Review:** After penetration testing
