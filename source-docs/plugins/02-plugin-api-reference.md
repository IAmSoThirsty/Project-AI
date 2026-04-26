---
type: reference
reference_type: api
area: plugin-system
audience: [developer]
prerequisites:
  - 01-plugin-architecture-overview.md
  - Python 3.11+ knowledge
  - Understanding of abstract base classes
tags:
  - plugin/api
  - reference
  - development
related_docs:
  - 01-plugin-architecture-overview.md
  - 05-plugin-development-guide.md
  - 03-plugin-loading-lifecycle.md
last_updated: 2026-04-20
version: 1.0.0
---

# Plugin API Reference

**Complete API documentation for Project-AI plugin systems**  
**Version:** 1.0.0  
**Last Updated:** 2026-04-20

---

## Table of Contents

1. [System A: Simple Plugin API](#system-a-simple-plugin-api)
2. [System B: PluginInterface API](#system-b-plugininterface-api)
3. [System C: PluginRunner API](#system-c-pluginrunner-api)
4. [System D: PluginIsolation API](#system-d-pluginisolation-api)
5. [Manifest Schema](#manifest-schema)
6. [Four Laws Validation API](#four-laws-validation-api)
7. [Observability API](#observability-api)
8. [Example Plugins](#example-plugins)

---

## System A: Simple Plugin API

**Location:** `src/app/core/ai_systems.py:991-1038`

### Plugin Base Class

```python
class Plugin:
    """Base plugin class for simple enable/disable plugins."""
    
    def __init__(self, name: str, version: str = "1.0.0") -> None:
        """Initialize plugin.
        
        Args:
            name: Unique plugin identifier (lowercase, alphanumeric + underscore)
            version: Semantic version (e.g., "1.2.3")
        
        Attributes:
            name (str): Plugin identifier
            version (str): Plugin version
            enabled (bool): Whether plugin is enabled (default: False)
        """
        self.name = name
        self.version = version
        self.enabled = False
    
    def initialize(self, context: Any) -> bool:
        """Initialize plugin with context.
        
        Called once during plugin loading. Override to add custom initialization logic.
        
        Args:
            context: Initialization context (can be any type, typically dict)
        
        Returns:
            True if initialization succeeded, False otherwise
        
        Example:
            >>> class MyPlugin(Plugin):
            ...     def initialize(self, context):
            ...         self.config = context.get("config", {})
            ...         return True
        """
        return True
    
    def enable(self) -> bool:
        """Enable the plugin.
        
        Returns:
            True if enabled successfully
        
        Example:
            >>> plugin = Plugin("my_plugin")
            >>> plugin.enable()
            True
            >>> assert plugin.enabled == True
        """
        self.enabled = True
        return True
    
    def disable(self) -> bool:
        """Disable the plugin.
        
        Returns:
            True if disabled successfully
        
        Example:
            >>> plugin = Plugin("my_plugin")
            >>> plugin.enable()
            >>> plugin.disable()
            True
            >>> assert plugin.enabled == False
        """
        self.enabled = False
        return True
```

### PluginManager Class

**Source**: [[src/app/core/ai_systems.py]]


```python
class PluginManager:
    """Manager for simple plugins."""
    
    def __init__(self, plugins_dir: str = "plugins") -> None:
        """Initialize plugin manager.
        
        Args:
            plugins_dir: Directory to store plugin data (created if missing)
        
        Attributes:
            plugins_dir (str): Plugin data directory
            plugins (dict[str, Plugin]): Loaded plugins by name
        """
        self.plugins_dir = plugins_dir
        self.plugins: dict[str, Plugin] = {}
        os.makedirs(plugins_dir, exist_ok=True)
    
    def load_plugin(self, plugin: Plugin) -> bool:
        """Load and enable a plugin.
        
        If plugin with same name already exists, it is replaced.
        
        Args:
            plugin: Plugin instance to load
        
        Returns:
            True if plugin enabled successfully
        
        Example:
            >>> manager = PluginManager()
            >>> plugin = Plugin("test_plugin", "1.0.0")
            >>> manager.load_plugin(plugin)
            True
            >>> assert "test_plugin" in manager.plugins
        """
        if plugin.name in self.plugins:
            logger.warning(
                "Plugin %s already loaded; replacing with new instance",
                plugin.name
            )
        self.plugins[plugin.name] = plugin
        return plugin.enable()
    
    def get_statistics(self) -> dict[str, Any]:
        """Get plugin manager statistics.
        
        Returns:
            Dictionary with 'total' and 'enabled' plugin counts
        
        Example:
            >>> manager = PluginManager()
            >>> plugin1 = Plugin("plugin1")
            >>> plugin2 = Plugin("plugin2")
            >>> manager.load_plugin(plugin1)
            >>> manager.load_plugin(plugin2)
            >>> plugin2.disable()
            >>> stats = manager.get_statistics()
            >>> assert stats == {"total": 2, "enabled": 1}
        """
        return {
            "total": len(self.plugins),
            "enabled": len([p for p in self.plugins.values() if p.enabled]),
        }
```

### Usage Example

```python
from app.core.ai_systems import Plugin, PluginManager

# Create custom plugin
class GreetingPlugin(Plugin):
    def __init__(self):
        super().__init__(name="greeting_plugin", version="1.0.0")
        self.greetings = []
    
    def initialize(self, context: dict) -> bool:
        self.greetings = context.get("greetings", ["Hello"])
        return True
    
    def greet(self, name: str) -> str:
        if not self.enabled:
            raise RuntimeError("Plugin not enabled")
        return f"{self.greetings[0]}, {name}!"

# Load plugin
manager = PluginManager(plugins_dir="data/plugins")
plugin = GreetingPlugin()
plugin.initialize(context={"greetings": ["Hi", "Hello"]})
manager.load_plugin(plugin)

# Use plugin
print(plugin.greet("Alice"))  # Output: "Hi, Alice!"
```

---

## System B: PluginInterface API

**Location:** `src/app/core/interfaces.py:218-389`

### PluginInterface Abstract Base Class

```python
from abc import ABC, abstractmethod
from typing import Any

class PluginInterface(ABC):
    """Abstract interface for full-featured plugins."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get unique plugin identifier.
        
        Returns:
            Plugin name (lowercase, alphanumeric + underscore)
        
        Example:
            >>> def get_name(self) -> str:
            ...     return "my_custom_plugin"
        """
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Get plugin version.
        
        Returns:
            Semantic version string (e.g., "1.2.3")
        
        Example:
            >>> def get_version(self) -> str:
            ...     return "2.1.0"
        """
        pass
    
    @abstractmethod
    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute plugin with given context.
        
        Args:
            context: Execution context with input data
        
        Returns:
            Result dictionary with output data
        
        Raises:
            ValueError: If context validation fails
            RuntimeError: If execution fails
        
        Example:
            >>> def execute(self, context: dict) -> dict:
            ...     input_data = context["input"]
            ...     result = self.process(input_data)
            ...     return {"status": "success", "output": result}
        """
        pass
    
    @abstractmethod
    def validate_context(self, context: dict[str, Any]) -> bool:
        """Validate execution context before running.
        
        Args:
            context: Context to validate
        
        Returns:
            True if context is valid, False otherwise
        
        Example:
            >>> def validate_context(self, context: dict) -> bool:
            ...     required_keys = ["input", "action"]
            ...     return all(key in context for key in required_keys)
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> dict[str, Any]:
        """Get plugin metadata.
        
        Returns:
            Dictionary with plugin information:
            - name: Plugin identifier
            - version: Semantic version
            - description: Human-readable description
            - author: Plugin author
            - capabilities: List of supported capabilities
            - dependencies: List of required dependencies
        
        Example:
            >>> def get_metadata(self) -> dict:
            ...     return {
            ...         "name": "data_processor",
            ...         "version": "1.0.0",
            ...         "description": "Process CSV data",
            ...         "author": "Data Team",
            ...         "capabilities": ["csv_processing", "data_validation"],
            ...         "dependencies": ["pandas>=2.0"]
            ...     }
        """
        pass
    
    def initialize(self) -> None:
        """Initialize plugin (optional lifecycle hook).
        
        Called once when plugin is registered. Override for setup logic.
        
        Example:
            >>> def initialize(self) -> None:
            ...     self.cache = {}
            ...     self.load_config()
        """
        pass
    
    def shutdown(self) -> None:
        """Shutdown plugin (optional lifecycle hook).
        
        Called when plugin is unregistered. Override for cleanup logic.
        
        Example:
            >>> def shutdown(self) -> None:
            ...     self.save_state()
            ...     self.close_connections()
        """
        pass
```

### PluginRegistry Class

```python
class PluginRegistry:
    """Registry for managing PluginInterface implementations."""
    
    def __init__(self) -> None:
        """Initialize empty registry."""
        self._plugins: dict[str, PluginInterface] = {}
    
    def register(self, plugin: PluginInterface) -> None:
        """Register a plugin.
        
        Args:
            plugin: Plugin implementing PluginInterface
        
        Raises:
            ValueError: If plugin with same name already registered
        
        Example:
            >>> registry = PluginRegistry()
            >>> plugin = MyPlugin()
            >>> registry.register(plugin)
        """
        name = plugin.get_name()
        if name in self._plugins:
            raise ValueError(f"Plugin '{name}' already registered")
        
        plugin.initialize()
        self._plugins[name] = plugin
        logger.info("Registered plugin: %s v%s", name, plugin.get_version())
    
    def unregister(self, name: str) -> None:
        """Unregister a plugin.
        
        Args:
            name: Name of plugin to unregister
        
        Raises:
            KeyError: If plugin not found
        
        Example:
            >>> registry.unregister("my_plugin")
        """
        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' not found")
        
        plugin = self._plugins[name]
        plugin.shutdown()
        del self._plugins[name]
        logger.info("Unregistered plugin: %s", name)
    
    def execute_plugin(
        self,
        name: str,
        context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a registered plugin.
        
        Args:
            name: Plugin name
            context: Execution context
        
        Returns:
            Plugin execution result
        
        Raises:
            KeyError: If plugin not found
            ValueError: If context validation fails
        
        Example:
            >>> result = registry.execute_plugin(
            ...     "my_plugin",
            ...     context={"action": "process", "data": [1, 2, 3]}
            ... )
        """
        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' not found")
        
        plugin = self._plugins[name]
        
        if not plugin.validate_context(context):
            raise ValueError(f"Invalid context for plugin '{name}'")
        
        logger.debug("Executing plugin: %s", name)
        return plugin.execute(context)
    
    def list_plugins(self) -> list[dict[str, Any]]:
        """List all registered plugins.
        
        Returns:
            List of plugin metadata dictionaries
        
        Example:
            >>> plugins = registry.list_plugins()
            >>> for plugin in plugins:
            ...     print(f"{plugin['name']} v{plugin['version']}")
        """
        return [plugin.get_metadata() for plugin in self._plugins.values()]
    
    def get_plugin_metadata(self, name: str) -> dict[str, Any]:
        """Get metadata for specific plugin.
        
        Args:
            name: Plugin name
        
        Returns:
            Plugin metadata dictionary
        
        Raises:
            KeyError: If plugin not found
        """
        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' not found")
        return self._plugins[name].get_metadata()
```

### Usage Example

```python
from app.core.interfaces import PluginInterface, PluginRegistry

class DataProcessorPlugin(PluginInterface):
    def get_name(self) -> str:
        return "data_processor"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def validate_context(self, context: dict) -> bool:
        return "data" in context and "action" in context
    
    def execute(self, context: dict) -> dict:
        data = context["data"]
        action = context["action"]
        
        if action == "sum":
            result = sum(data)
        elif action == "average":
            result = sum(data) / len(data)
        else:
            raise ValueError(f"Unknown action: {action}")
        
        return {"result": result, "status": "success"}
    
    def get_metadata(self) -> dict:
        return {
            "name": "data_processor",
            "version": "1.0.0",
            "description": "Process numerical data",
            "author": "Data Team",
            "capabilities": ["sum", "average"]
        }

# Register and use
registry = PluginRegistry()
plugin = DataProcessorPlugin()
registry.register(plugin)

result = registry.execute_plugin(
    "data_processor",
    context={"data": [1, 2, 3, 4, 5], "action": "average"}
)
print(result)  # {"result": 3.0, "status": "success"}
```

---

## System C: PluginRunner API

**Location:** `src/app/plugins/plugin_runner.py:11-105`

### PluginRunner Class

```python
class PluginRunner:
    """Subprocess-based plugin runner using JSONL protocol."""
    
    def __init__(
        self,
        plugin_script: str,
        timeout: float = 5.0
    ) -> None:
        """Initialize plugin runner.
        
        Args:
            plugin_script: Path to plugin Python script
            timeout: Maximum execution time in seconds (default: 5.0)
        
        Attributes:
            plugin_script (Path): Plugin script path
            timeout (float): Execution timeout
            proc (Popen | None): Subprocess handle
        """
        self.plugin_script = Path(plugin_script)
        self.timeout = timeout
        self.proc: subprocess.Popen | None = None
    
    def start(self) -> None:
        """Start plugin subprocess.
        
        Raises:
            FileNotFoundError: If plugin script doesn't exist
        
        Example:
            >>> runner = PluginRunner("plugins/my_plugin.py")
            >>> runner.start()
        """
        if not self.plugin_script.exists():
            raise FileNotFoundError(f"Plugin script not found: {self.plugin_script}")
        
        cmd = [sys.executable, str(self.plugin_script)]
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
    
    def stop(self) -> None:
        """Stop plugin subprocess.
        
        Attempts graceful termination (SIGTERM) followed by kill (SIGKILL).
        
        Example:
            >>> runner.stop()
        """
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=1.0)
            except Exception:
                try:
                    self.proc.kill()
                except Exception as e:
                    logger.warning("Failed to kill plugin process: %s", e)
        self.proc = None
    
    def call_init(self, params: dict[str, Any]) -> dict[str, Any]:
        """Call init method on plugin subprocess.
        
        Sends JSON-RPC request and waits for response.
        
        Args:
            params: Initialization parameters
        
        Returns:
            Plugin response dictionary with 'result' or 'error' key
        
        Raises:
            RuntimeError: If process not initialized
            TimeoutError: If plugin doesn't respond within timeout
        
        Example:
            >>> runner = PluginRunner("plugins/my_plugin.py", timeout=10.0)
            >>> response = runner.call_init({"config": {"debug": True}})
            >>> print(response)
            {"id": "init-1", "result": {"status": "initialized"}}
        """
        if not self.proc:
            self.start()
        
        if not (self.proc and self.proc.stdin and self.proc.stdout):
            raise RuntimeError("Plugin process not properly initialized")
        
        # Send JSON-RPC request
        msg = {"id": "init-1", "method": "init", "params": params}
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        
        # Wait for response
        start = time.time()
        buffer = ""
        while time.time() - start < self.timeout:
            line = self._readline_nonblocking(timeout=0.1)
            if line is None:
                continue
            buffer = line
            try:
                obj = json.loads(buffer)
                if obj.get("id") == msg["id"]:
                    return obj
            except Exception:
                continue
        
        raise TimeoutError("Plugin did not respond to init within timeout")
    
    def _readline_nonblocking(
        self,
        timeout: float = 0.1
    ) -> str | None:
        """Read line from subprocess with timeout.
        
        Args:
            timeout: Read timeout in seconds
        
        Returns:
            Line without newline, or None if timeout
        """
        if not self.proc or not self.proc.stdout:
            return None
        
        end = time.time() + timeout
        while time.time() < end:
            line = self.proc.stdout.readline()
            if line:
                return line.rstrip("\n")
            time.sleep(0.01)
        return None
```

### JSONL Protocol

**Request Format:**
```json
{
  "id": "<unique-request-id>",
  "method": "<method-name>",
  "params": {<parameters>}
}
```

**Response Format (Success):**
```json
{
  "id": "<matching-request-id>",
  "result": {<result-data>}
}
```

**Response Format (Error):**
```json
{
  "id": "<matching-request-id>",
  "error": "<error-message>"
}
```

### Example Plugin Script

```python
#!/usr/bin/env python3
"""Example subprocess plugin using JSONL protocol."""

import json
import sys

def handle_init(params):
    """Handle init method call."""
    config = params.get("config", {})
    return {"status": "initialized", "config": config}

def main():
    """Main loop: read JSONL from stdin, write responses to stdout."""
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            request_id = request["id"]
            method = request["method"]
            params = request.get("params", {})
            
            if method == "init":
                result = handle_init(params)
                response = {"id": request_id, "result": result}
            else:
                response = {"id": request_id, "error": f"Unknown method: {method}"}
            
            print(json.dumps(response), flush=True)
        except Exception as e:
            error_response = {
                "id": request.get("id", "unknown"),
                "error": str(e)
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    main()
```

### Usage Example

```python
from app.plugins.plugin_runner import PluginRunner

# Create and run plugin
runner = PluginRunner("plugins/data_processor.py", timeout=10.0)
try:
    response = runner.call_init({
        "config": {"debug": True},
        "action": "process_data"
    })
    
    if "result" in response:
        print("Success:", response["result"])
    elif "error" in response:
        print("Error:", response["error"])
finally:
    runner.stop()
```

---

## System D: PluginIsolation API

**Location:** `src/app/security/agent_security.py`

### PluginIsolation Class

```python
from multiprocessing import Process, Queue

class PluginIsolation:
    """Execute plugins with multiprocessing isolation."""
    
    @staticmethod
    def execute_isolated(
        plugin_func: Callable,
        *args,
        timeout: int = 30,
        **kwargs
    ) -> Any:
        """Execute plugin function in isolated process.
        
        Args:
            plugin_func: Function to execute
            *args: Positional arguments for function
            timeout: Maximum execution time in seconds (default: 30)
            **kwargs: Keyword arguments for function
        
        Returns:
            Function result
        
        Raises:
            TimeoutError: If execution exceeds timeout
            RuntimeError: If function raises exception
        
        Example:
            >>> def risky_operation(x, y):
            ...     return x / y
            >>> 
            >>> result = PluginIsolation.execute_isolated(
            ...     risky_operation,
            ...     10, 2,
            ...     timeout=5
            ... )
            >>> print(result)  # 5.0
        """
        queue = Queue()
        
        def wrapper():
            try:
                result = plugin_func(*args, **kwargs)
                queue.put(("success", result))
            except Exception as e:
                queue.put(("error", str(e)))
        
        process = Process(target=wrapper)
        process.start()
        process.join(timeout=timeout)
        
        if process.is_alive():
            process.terminate()
            process.join(timeout=1)
            if process.is_alive():
                process.kill()
            raise TimeoutError(f"Plugin execution exceeded {timeout} seconds")
        
        if not queue.empty():
            status, value = queue.get()
            if status == "success":
                return value
            else:
                raise RuntimeError(f"Plugin error: {value}")
        
        raise RuntimeError("Plugin process terminated without result")
```

### Usage Example

```python
from app.security.agent_security import PluginIsolation

def untrusted_plugin(data: list[int]) -> int:
    """Untrusted plugin that might hang or crash."""
    import time
    time.sleep(2)  # Simulate slow operation
    return sum(data)

# Execute with isolation and timeout
try:
    result = PluginIsolation.execute_isolated(
        untrusted_plugin,
        [1, 2, 3, 4, 5],
        timeout=5
    )
    print(f"Result: {result}")  # 15
except TimeoutError as e:
    print(f"Plugin timed out: {e}")
except RuntimeError as e:
    print(f"Plugin failed: {e}")
```

---

## Manifest Schema

**Location:** `src/app/plugins/plugin.json`

### Plugin Manifest Structure

```json
{
  "name": "plugin_name",
  "version": "1.0.0",
  "author": "Plugin Author",
  "description": "Human-readable plugin description",
  "hooks": ["before_action", "after_action", "on_error"],
  "four_laws_safe": true,
  "safe_for_learning": false,
  "capabilities": ["data_processing", "file_io"],
  "dependencies": ["pandas>=2.0", "requests>=2.28"],
  "resource_limits": {
    "max_memory_mb": 512,
    "max_cpu_percent": 50,
    "max_execution_seconds": 30
  },
  "permissions": {
    "filesystem": ["read", "write"],
    "network": ["http", "https"],
    "system": []
  }
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Unique plugin identifier (lowercase, alphanumeric + underscore) |
| `version` | string | ✅ | Semantic version (e.g., "1.2.3") |
| `author` | string | ✅ | Plugin author name or organization |
| `description` | string | ✅ | Human-readable description (max 500 chars) |
| `hooks` | string[] | ❌ | Lifecycle hooks to register |
| `four_laws_safe` | boolean | ✅ | Whether plugin respects Four Laws |
| `safe_for_learning` | boolean | ✅ | Whether plugin can be used for learning requests |
| `capabilities` | string[] | ❌ | List of capabilities provided |
| `dependencies` | string[] | ❌ | Python dependencies (pip format) |
| `resource_limits` | object | ❌ | Resource consumption limits |
| `permissions` | object | ❌ | Required permissions |

---

## Four Laws Validation API

**Location:** `src/app/core/ai_systems.py:293-351`

### FourLaws Class

**Source**: [[src/app/core/ai_systems.py]]


```python
class FourLaws:
    """Asimov's Laws validator for plugin actions."""
    
    @staticmethod
    def validate_action(
        action: str,
        context: dict[str, Any]
    ) -> tuple[bool, str]:
        """Validate action against Four Laws.
        
        Args:
            action: Action description
            context: Validation context with keys:
                - harms_human: bool
                - allows_harm_by_inaction: bool
                - is_user_order: bool
                - protects_human: bool
                - endangers_self: bool
                - protect_self_conflicts_with_first: bool
                - protect_self_conflicts_with_second: bool
        
        Returns:
            Tuple of (allowed, reason)
        
        Example:
            >>> allowed, reason = FourLaws.validate_action(
            ...     "Delete user data",
            ...     context={
            ...         "is_user_order": True,
            ...         "harms_human": False
            ...     }
            ... )
            >>> print(f"Allowed: {allowed}, Reason: {reason}")
        """
        # First Law: Don't harm humans
        if context.get("harms_human") or context.get("allows_harm_by_inaction"):
            return False, "Blocked: First Law prohibits harming humans"
        
        # Second Law: Obey orders (unless conflicts with First)
        if context.get("is_user_order"):
            if context.get("protects_human"):
                return True, "Allowed: Order protects humans"
            return True, "Allowed: Following user order"
        
        # Third Law: Self-preservation (unless conflicts with First/Second)
        if context.get("endangers_self"):
            if context.get("protect_self_conflicts_with_first") or \
               context.get("protect_self_conflicts_with_second"):
                return False, "Self-protection conflicts with higher law"
            return True, "Allowed: Third Law permits protecting existence"
        
        return True, "Allowed: No law violations detected"
```

### Usage in Plugins

```python
from app.core.ai_systems import FourLaws, Plugin

class SafePlugin(Plugin):
    def initialize(self, context: dict) -> bool:
        # Validate against Four Laws
        allowed, reason = FourLaws.validate_action(
            f"Initialize {self.name}",
            context=context
        )
        
        if not allowed:
            logger.warning("Plugin blocked: %s", reason)
            return False
        
        logger.info("Plugin allowed: %s", reason)
        self.enabled = True
        return True
```

---

## Observability API

### emit_event Function

```python
from app.core.observability import emit_event

def emit_event(event_name: str, metadata: dict[str, Any] | None = None) -> None:
    """Emit telemetry event.
    
    Args:
        event_name: Event identifier (dot-separated, e.g., "plugin.initialized")
        metadata: Optional event metadata
    
    Example:
        >>> emit_event("plugin.data_processor.executed", {
        ...     "duration_ms": 150,
        ...     "records_processed": 1000
        ... })
    """
    pass
```

### Plugin Event Naming Convention

- `plugin.<name>.initialized` - Plugin initialization
- `plugin.<name>.executed` - Plugin execution
- `plugin.<name>.blocked` - Plugin blocked by Four Laws
- `plugin.<name>.error` - Plugin error
- `plugin.<name>.disabled` - Plugin disabled

---

## Example Plugins

### Example 1: Simple Greeting Plugin

```python
from app.core.ai_systems import Plugin

class GreetingPlugin(Plugin):
    def __init__(self):
        super().__init__(name="greeting", version="1.0.0")
        self.greetings = ["Hello"]
    
    def initialize(self, context: dict) -> bool:
        self.greetings = context.get("greetings", ["Hello"])
        return True
    
    def greet(self, name: str) -> str:
        return f"{self.greetings[0]}, {name}!"
```

### Example 2: Full-Featured Data Plugin

```python
from app.core.interfaces import PluginInterface

class DataPlugin(PluginInterface):
    def get_name(self) -> str:
        return "data_analyzer"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def validate_context(self, context: dict) -> bool:
        return "data" in context and "operation" in context
    
    def execute(self, context: dict) -> dict:
        data = context["data"]
        operation = context["operation"]
        
        if operation == "mean":
            result = sum(data) / len(data)
        elif operation == "median":
            sorted_data = sorted(data)
            n = len(sorted_data)
            result = sorted_data[n // 2]
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        return {"result": result}
    
    def get_metadata(self) -> dict:
        return {
            "name": "data_analyzer",
            "version": "1.0.0",
            "description": "Statistical data analysis",
            "capabilities": ["mean", "median"]
        }
```

### Example 3: Subprocess Plugin

```python
#!/usr/bin/env python3
"""Subprocess plugin using JSONL protocol."""

import json
import sys

def process_request(method, params):
    if method == "init":
        return {"status": "initialized"}
    elif method == "process":
        data = params.get("data", [])
        return {"result": sum(data)}
    else:
        raise ValueError(f"Unknown method: {method}")

def main():
    for line in sys.stdin:
        request = json.loads(line)
        try:
            result = process_request(
                request["method"],
                request.get("params", {})
            )
            response = {"id": request["id"], "result": result}
        except Exception as e:
            response = {"id": request["id"], "error": str(e)}
        
        print(json.dumps(response), flush=True)

if __name__ == "__main__":
    main()
```

---

## References

- [Plugin Architecture Overview](./01-plugin-architecture-overview.md)
- [Plugin Development Guide](./05-plugin-development-guide.md)
- [Plugin Security Guide](./04-plugin-security-guide.md)

---

**Author:** AGENT-046 (Plugin System Documentation Specialist)  
**Review Status:** 📝 Draft  
**Next Review:** After developer testing
