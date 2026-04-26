---
type: guide
guide_type: lifecycle
area: plugin-system
audience: [developer]
prerequisites:
  - 01-plugin-architecture-overview.md
  - 02-plugin-api-reference.md
tags:
  - plugin/lifecycle
  - loading
  - initialization
  - state-management
related_docs:
  - 04-plugin-security-guide.md
  - 05-plugin-development-guide.md
last_updated: 2026-04-20
version: 1.0.0
---

# Plugin Loading and Lifecycle

**Complete guide to plugin initialization, loading, and lifecycle management**  
**Version:** 1.0.0  
**Last Updated:** 2026-04-20

---

## Table of Contents

1. [Plugin Lifecycle Overview](#plugin-lifecycle-overview)
2. [Loading Mechanisms](#loading-mechanisms)
3. [Initialization Patterns](#initialization-patterns)
4. [State Management](#state-management)
5. [Shutdown and Cleanup](#shutdown-and-cleanup)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Plugin Lifecycle Overview

### Lifecycle States

```
┌──────────────┐
│  UNLOADED    │ ← Initial state
└──────┬───────┘
       │ load_plugin()
       ▼
┌──────────────┐
│  LOADING     │ ← Validation, manifest parsing
└──────┬───────┘
       │ initialize()
       ▼
┌──────────────┐
│ INITIALIZED  │ ← Four Laws check, setup
└──────┬───────┘
       │ enable()
       ▼
┌──────────────┐
│   ENABLED    │ ← Active, can execute ◄─┐
└──────┬───────┘                         │
       │ disable()                       │
       ▼                                 │
┌──────────────┐                         │
│  DISABLED    │ ─ enable() ─────────────┘
└──────┬───────┘
       │ shutdown()
       ▼
┌──────────────┐
│   SHUTDOWN   │ ← Cleanup, unloaded
└──────────────┘
```

### Lifecycle Methods

| Method | State Transition | Purpose |
|--------|------------------|---------|
| `load_plugin()` | UNLOADED → LOADING | Validate manifest, parse metadata |
| `initialize()` | LOADING → INITIALIZED | Setup resources, validate context |
| `enable()` | INITIALIZED → ENABLED | Activate plugin for use |
| `execute()` | ENABLED → ENABLED | Run plugin logic |
| `disable()` | ENABLED → DISABLED | Deactivate plugin temporarily |
| `shutdown()` | DISABLED → SHUTDOWN | Cleanup and unload |

---

## Loading Mechanisms

### System A: Simple Plugin Loading

**Pattern:** Direct instantiation and registration

```python
from app.core.ai_systems import Plugin, PluginManager

# Step 1: Create plugin instance
plugin = Plugin("my_plugin", version="1.0.0")

# Step 2: Initialize with context
context = {"config": {"debug": True}}
success = plugin.initialize(context)

# Step 3: Load into manager (automatically enables)
manager = PluginManager(plugins_dir="data/plugins")
manager.load_plugin(plugin)

# Verify
print(f"Plugin enabled: {plugin.enabled}")  # True
print(f"Stats: {manager.get_statistics()}")  # {"total": 1, "enabled": 1}
```

**Loading Flow:**
```python
def load_plugin(self, plugin: Plugin) -> bool:
    # 1. Check for duplicate
    if plugin.name in self.plugins:
        logger.warning("Replacing existing plugin: %s", plugin.name)
    
    # 2. Register in manager
    self.plugins[plugin.name] = plugin
    
    # 3. Enable plugin
    return plugin.enable()  # Sets enabled = True
```

### System B: PluginInterface Loading

**Pattern:** Registration with lifecycle hooks

```python
from app.core.interfaces import PluginInterface, PluginRegistry

class MyPlugin(PluginInterface):
    def get_name(self) -> str:
        return "my_plugin"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def initialize(self) -> None:
        """Called automatically during registration."""
        self.cache = {}
        self.load_config()
    
    # ... other methods ...

# Step 1: Create registry
registry = PluginRegistry()

# Step 2: Register plugin (calls initialize() automatically)
plugin = MyPlugin()
registry.register(plugin)  # Triggers: plugin.initialize()

# Step 3: Execute plugin
result = registry.execute_plugin("my_plugin", context={"action": "test"})
```

**Loading Flow:**
```python
def register(self, plugin: PluginInterface) -> None:
    # 1. Check for duplicate
    name = plugin.get_name()
    if name in self._plugins:
        raise ValueError(f"Plugin '{name}' already registered")
    
    # 2. Call lifecycle hook
    plugin.initialize()  # User-defined initialization
    
    # 3. Store in registry
    self._plugins[name] = plugin
    logger.info("Registered plugin: %s v%s", name, plugin.get_version())
```

### System C: Subprocess Plugin Loading

**Pattern:** Dynamic script loading with process isolation

```python
from app.plugins.plugin_runner import PluginRunner

# Step 1: Create runner with plugin script
runner = PluginRunner(
    plugin_script="plugins/data_processor.py",
    timeout=10.0
)

# Step 2: Start subprocess
runner.start()  # Launches subprocess.Popen

# Step 3: Call init method via JSONL
response = runner.call_init({
    "config": {"mode": "production"},
    "resources": {"max_memory_mb": 512}
})

# Step 4: Check response
if "result" in response:
    print("Initialized:", response["result"])
elif "error" in response:
    print("Error:", response["error"])

# Step 5: Cleanup
runner.stop()  # SIGTERM → SIGKILL
```

**Loading Flow:**
```python
def start(self) -> None:
    # 1. Validate script exists
    if not self.plugin_script.exists():
        raise FileNotFoundError(f"Plugin script not found: {self.plugin_script}")
    
    # 2. Launch subprocess
    cmd = [sys.executable, str(self.plugin_script)]
    self.proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

def call_init(self, params: dict) -> dict:
    # 1. Send JSON-RPC request
    msg = {"id": "init-1", "method": "init", "params": params}
    self.proc.stdin.write(json.dumps(msg) + "\n")
    self.proc.stdin.flush()
    
    # 2. Wait for response with timeout
    start = time.time()
    while time.time() - start < self.timeout:
        line = self._readline_nonblocking(timeout=0.1)
        if line:
            obj = json.loads(line)
            if obj.get("id") == msg["id"]:
                return obj  # {"id": "init-1", "result": {...}}
    
    raise TimeoutError("Plugin did not respond to init within timeout")
```

### System D: Isolated Function Loading

**Pattern:** Multiprocessing execution of plugin functions

```python
from app.security.agent_security import PluginIsolation

# Define plugin function
def plugin_operation(x: int, y: int) -> int:
    """Plugin logic to execute in isolation."""
    return x * y

# Execute with isolation
result = PluginIsolation.execute_isolated(
    plugin_operation,
    5, 10,
    timeout=5
)
print(result)  # 50
```

**Loading Flow:**
```python
def execute_isolated(plugin_func, *args, timeout=30, **kwargs):
    # 1. Create communication queue
    queue = Queue()
    
    # 2. Define wrapper function
    def wrapper():
        try:
            result = plugin_func(*args, **kwargs)
            queue.put(("success", result))
        except Exception as e:
            queue.put(("error", str(e)))
    
    # 3. Launch isolated process
    process = Process(target=wrapper)
    process.start()
    
    # 4. Wait with timeout
    process.join(timeout=timeout)
    
    # 5. Handle timeout
    if process.is_alive():
        process.terminate()  # SIGTERM
        process.join(timeout=1)
        if process.is_alive():
            process.kill()  # SIGKILL
        raise TimeoutError(f"Plugin exceeded {timeout} seconds")
    
    # 6. Return result
    if not queue.empty():
        status, value = queue.get()
        if status == "success":
            return value
        else:
            raise RuntimeError(f"Plugin error: {value}")
```

---

## Initialization Patterns

### Pattern 1: Configuration-Based Initialization

```python
class ConfigurablePlugin(Plugin):
    def __init__(self):
        super().__init__(name="config_plugin", version="1.0.0")
        self.config = {}
    
    def initialize(self, context: dict) -> bool:
        """Initialize with configuration validation."""
        # Validate required config keys
        required_keys = ["api_key", "endpoint"]
        self.config = context.get("config", {})
        
        for key in required_keys:
            if key not in self.config:
                logger.error("Missing required config: %s", key)
                return False
        
        # Test configuration
        try:
            self._test_connection()
        except Exception as e:
            logger.error("Configuration test failed: %s", e)
            return False
        
        return True
    
    def _test_connection(self):
        """Test API connection with config."""
        import requests
        response = requests.get(
            self.config["endpoint"],
            headers={"Authorization": f"Bearer {self.config['api_key']}"},
            timeout=5
        )
        response.raise_for_status()
```

### Pattern 2: Resource Allocation Initialization

```python
class ResourcePlugin(PluginInterface):
    def __init__(self):
        self.database = None
        self.cache = None
    
    def initialize(self) -> None:
        """Allocate resources during initialization."""
        import sqlite3
        
        # Allocate database connection
        self.database = sqlite3.connect("plugins/resource_plugin.db")
        self.database.execute("""
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # Allocate cache
        self.cache = {}
        
        logger.info("Resource plugin initialized with DB and cache")
    
    def shutdown(self) -> None:
        """Release resources during shutdown."""
        if self.database:
            self.database.close()
            self.database = None
        
        if self.cache:
            self.cache.clear()
            self.cache = None
        
        logger.info("Resource plugin resources released")
```

### Pattern 3: Four Laws Validation Initialization

```python
from app.core.ai_systems import FourLaws, Plugin

class SafePlugin(Plugin):
    def initialize(self, context: dict) -> bool:
        """Initialize with Four Laws validation."""
        # Step 1: Validate against Four Laws
        allowed, reason = FourLaws.validate_action(
            f"Initialize plugin '{self.name}'",
            context=context
        )
        
        if not allowed:
            logger.warning("Plugin blocked by Four Laws: %s", reason)
            emit_event("plugin.blocked", {
                "name": self.name,
                "reason": reason,
                "context": context
            })
            return False
        
        # Step 2: Check user authorization
        if context.get("requires_explicit_order") and not context.get("is_user_order"):
            logger.warning("Plugin requires explicit user order")
            return False
        
        # Step 3: Emit telemetry
        emit_event("plugin.initialized", {
            "name": self.name,
            "version": self.version,
            "reason": reason
        })
        
        # Step 4: Enable plugin
        self.enabled = True
        return True
```

### Pattern 4: Lazy Initialization

```python
class LazyPlugin(Plugin):
    def __init__(self):
        super().__init__(name="lazy_plugin", version="1.0.0")
        self._heavy_resource = None
    
    def initialize(self, context: dict) -> bool:
        """Minimal initialization - defer resource loading."""
        self.config = context.get("config", {})
        # Don't load heavy resources yet
        return True
    
    def _ensure_initialized(self):
        """Load heavy resources on first use."""
        if self._heavy_resource is None:
            logger.info("Loading heavy resource on first use")
            self._heavy_resource = self._load_heavy_resource()
    
    def execute_action(self, action: str):
        """Execute action with lazy initialization."""
        if not self.enabled:
            raise RuntimeError("Plugin not enabled")
        
        self._ensure_initialized()  # Load resources if needed
        return self._heavy_resource.process(action)
```

---

## State Management

### Persistence Patterns

#### Pattern 1: JSON File Persistence

```python
import json
from pathlib import Path

class StatefulPlugin(Plugin):
    def __init__(self):
        super().__init__(name="stateful_plugin", version="1.0.0")
        self.state_file = Path("data/plugins/stateful_plugin_state.json")
        self.state = {}
    
    def initialize(self, context: dict) -> bool:
        """Load state from disk during initialization."""
        if self.state_file.exists():
            try:
                with open(self.state_file, encoding="utf-8") as f:
                    self.state = json.load(f)
                logger.info("Loaded state: %d keys", len(self.state))
            except Exception as e:
                logger.error("Failed to load state: %s", e)
                self.state = {}
        else:
            self.state = {"initialized_at": time.time()}
            self._save_state()
        
        return True
    
    def _save_state(self):
        """Persist state to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)
    
    def update_state(self, key: str, value: Any):
        """Update state and persist."""
        self.state[key] = value
        self._save_state()  # Always persist after modification
```

#### Pattern 2: Database Persistence

```python
import sqlite3

class DatabasePlugin(PluginInterface):
    def __init__(self):
        self.db_path = "data/plugins/db_plugin.db"
        self.conn = None
    
    def initialize(self) -> None:
        """Initialize database connection and schema."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS plugin_state (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def shutdown(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def get_state(self, key: str) -> str | None:
        """Retrieve state from database."""
        cursor = self.conn.execute(
            "SELECT value FROM plugin_state WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    
    def set_state(self, key: str, value: str):
        """Update state in database."""
        self.conn.execute("""
            INSERT INTO plugin_state (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
        """, (key, value))
        self.conn.commit()
```

### In-Memory State Management

```python
class CachedPlugin(Plugin):
    def __init__(self):
        super().__init__(name="cached_plugin", version="1.0.0")
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_cached(self, key: str) -> Any:
        """Get value from cache with statistics."""
        if key in self.cache:
            self.cache_hits += 1
            return self.cache[key]
        else:
            self.cache_misses += 1
            return None
    
    def set_cached(self, key: str, value: Any):
        """Store value in cache."""
        self.cache[key] = value
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total if total > 0 else 0.0
        return {
            "size": len(self.cache),
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate": hit_rate
        }
```

---

## Shutdown and Cleanup

### Graceful Shutdown Pattern

```python
class CleanupPlugin(PluginInterface):
    def __init__(self):
        self.connections = []
        self.temp_files = []
    
    def initialize(self) -> None:
        """Initialize with resource tracking."""
        self.connections = []
        self.temp_files = []
    
    def shutdown(self) -> None:
        """Clean up all resources."""
        # Close connections
        for conn in self.connections:
            try:
                conn.close()
                logger.info("Closed connection: %s", conn)
            except Exception as e:
                logger.error("Failed to close connection: %s", e)
        
        # Delete temporary files
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info("Deleted temp file: %s", file_path)
            except Exception as e:
                logger.error("Failed to delete file %s: %s", file_path, e)
        
        # Clear tracking lists
        self.connections.clear()
        self.temp_files.clear()
        
        logger.info("Plugin cleanup complete")
```

### Subprocess Cleanup

```python
from app.plugins.plugin_runner import PluginRunner

runner = PluginRunner("plugins/my_plugin.py")
try:
    runner.start()
    result = runner.call_init({})
    # ... use plugin ...
finally:
    # Always cleanup, even on exception
    runner.stop()  # Terminates subprocess
```

### Context Manager Pattern

```python
class ManagedPlugin(Plugin):
    def __enter__(self):
        """Initialize on context entry."""
        self.initialize({})
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on context exit."""
        self.disable()
        if hasattr(self, "shutdown"):
            self.shutdown()
        return False  # Don't suppress exceptions

# Usage
with ManagedPlugin() as plugin:
    plugin.do_work()
# Automatic cleanup, even if exception occurs
```

---

## Error Handling

### Initialization Errors

```python
class RobustPlugin(Plugin):
    def initialize(self, context: dict) -> bool:
        """Initialize with comprehensive error handling."""
        try:
            # Step 1: Validate context
            if not self._validate_context(context):
                logger.error("Context validation failed")
                return False
            
            # Step 2: Load configuration
            try:
                self.config = self._load_config(context)
            except FileNotFoundError as e:
                logger.error("Config file not found: %s", e)
                return False
            except json.JSONDecodeError as e:
                logger.error("Invalid JSON in config: %s", e)
                return False
            
            # Step 3: Initialize resources
            try:
                self._init_resources()
            except Exception as e:
                logger.error("Resource initialization failed: %s", e)
                self._cleanup_partial_init()
                return False
            
            # Success
            self.enabled = True
            return True
            
        except Exception as e:
            logger.exception("Unexpected error during initialization: %s", e)
            return False
    
    def _cleanup_partial_init(self):
        """Clean up partially initialized resources."""
        if hasattr(self, "database") and self.database:
            self.database.close()
        if hasattr(self, "temp_dir") and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
```

### Execution Errors

```python
class SafeExecutionPlugin(PluginInterface):
    def execute(self, context: dict) -> dict:
        """Execute with error handling and recovery."""
        try:
            # Validate context
            if not self.validate_context(context):
                raise ValueError("Invalid context")
            
            # Execute with timeout
            result = self._execute_with_timeout(context, timeout=30)
            
            return {"status": "success", "result": result}
            
        except TimeoutError as e:
            logger.error("Execution timeout: %s", e)
            return {"status": "error", "error": "timeout", "message": str(e)}
        
        except ValueError as e:
            logger.error("Validation error: %s", e)
            return {"status": "error", "error": "validation", "message": str(e)}
        
        except Exception as e:
            logger.exception("Unexpected execution error: %s", e)
            return {"status": "error", "error": "unexpected", "message": str(e)}
```

### Subprocess Error Handling

```python
from app.plugins.plugin_runner import PluginRunner

runner = PluginRunner("plugins/my_plugin.py", timeout=10.0)
try:
    response = runner.call_init({"config": {}})
    
    if "error" in response:
        # Plugin returned error
        logger.error("Plugin error: %s", response["error"])
        # Handle error...
    elif "result" in response:
        # Success
        logger.info("Plugin initialized: %s", response["result"])
    
except FileNotFoundError as e:
    logger.error("Plugin script not found: %s", e)
    # Handle missing plugin...

except TimeoutError as e:
    logger.error("Plugin initialization timeout: %s", e)
    # Handle timeout...

except Exception as e:
    logger.exception("Unexpected plugin error: %s", e)
    # Handle unexpected error...

finally:
    runner.stop()  # Always cleanup
```

---

## Best Practices

### 1. Always Validate Context

```python
def initialize(self, context: dict) -> bool:
    # ✅ GOOD: Validate before using
    required_keys = ["api_key", "endpoint"]
    for key in required_keys:
        if key not in context:
            logger.error("Missing required key: %s", key)
            return False
    
    # ❌ BAD: Assume context is valid
    # api_key = context["api_key"]  # KeyError if missing!
```

### 2. Use Lifecycle Hooks

```python
class WellBehavedPlugin(PluginInterface):
    def initialize(self) -> None:
        """Setup resources."""
        self.connection = create_connection()
        logger.info("Plugin initialized")
    
    def shutdown(self) -> None:
        """Clean up resources."""
        self.connection.close()
        logger.info("Plugin shutdown")
```

### 3. Emit Telemetry Events

```python
from app.core.observability import emit_event

def initialize(self, context: dict) -> bool:
    emit_event("plugin.initialize.started", {"name": self.name})
    
    try:
        # ... initialization logic ...
        emit_event("plugin.initialize.completed", {
            "name": self.name,
            "duration_ms": elapsed_ms
        })
        return True
    except Exception as e:
        emit_event("plugin.initialize.failed", {
            "name": self.name,
            "error": str(e)
        })
        return False
```

### 4. Use Context Managers

```python
# ✅ GOOD: Automatic cleanup
with PluginRunner("plugins/my_plugin.py") as runner:
    result = runner.call_init({})

# ❌ BAD: Manual cleanup (easy to forget)
runner = PluginRunner("plugins/my_plugin.py")
result = runner.call_init({})
runner.stop()  # What if exception occurs above?
```

### 5. Validate Against Four Laws

```python
def initialize(self, context: dict) -> bool:
    # ✅ GOOD: Always validate
    allowed, reason = FourLaws.validate_action(
        f"Initialize {self.name}",
        context=context
    )
    if not allowed:
        logger.warning("Blocked: %s", reason)
        return False
    
    # Continue initialization...
```

---

## Troubleshooting

### Plugin Won't Initialize

**Symptoms:** `initialize()` returns `False`

**Checks:**
1. Verify required context keys are present
2. Check Four Laws validation context
3. Review plugin logs for error messages
4. Ensure resources (files, databases) are accessible

**Solution:**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Initialize with verbose context
context = {
    "config": {...},
    "is_user_order": True,
    "harms_human": False,
    "endangers_self": False
}
success = plugin.initialize(context)
if not success:
    print("Check logs for error details")
```

### Subprocess Plugin Timeout

**Symptoms:** `TimeoutError: Plugin did not respond to init within timeout`

**Causes:**
1. Plugin script takes too long to initialize
2. Plugin script has syntax error (never starts)
3. Plugin script doesn't write to stdout
4. Timeout value too low

**Solution:**
```python
# Increase timeout
runner = PluginRunner("plugins/slow_plugin.py", timeout=30.0)

# Check plugin script manually
import subprocess
result = subprocess.run(
    ["python", "plugins/slow_plugin.py"],
    capture_output=True,
    text=True,
    timeout=10
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
```

### Plugin State Not Persisting

**Symptoms:** Plugin state lost after restart

**Causes:**
1. Forgot to call `_save_state()` after modifications
2. File permissions prevent writing
3. Directory doesn't exist

**Solution:**
```python
class PersistentPlugin(Plugin):
    def update_data(self, key, value):
        self.data[key] = value
        self._save_state()  # ✅ Always save after modification
    
    def _save_state(self):
        # ✅ Create directory if missing
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error("Failed to save state: %s", e)
```

### Resource Leaks

**Symptoms:** Memory/file descriptor leaks over time

**Causes:**
1. Resources not released in `shutdown()`
2. Exception prevents cleanup
3. No cleanup on reload

**Solution:**
```python
class ResourceManagedPlugin(PluginInterface):
    def shutdown(self) -> None:
        """Always cleanup, even on error."""
        errors = []
        
        # Close each resource individually
        if hasattr(self, "connection"):
            try:
                self.connection.close()
            except Exception as e:
                errors.append(f"Connection: {e}")
        
        if hasattr(self, "file_handle"):
            try:
                self.file_handle.close()
            except Exception as e:
                errors.append(f"File: {e}")
        
        if errors:
            logger.warning("Cleanup errors: %s", errors)
```

---

## References

- [Plugin Architecture Overview](./01-plugin-architecture-overview.md)
- [Plugin API Reference](./02-plugin-api-reference.md)
- [Plugin Security Guide](./04-plugin-security-guide.md)
- [Plugin Development Guide](./05-plugin-development-guide.md)

---

**Author:** AGENT-046 (Plugin System Documentation Specialist)  
**Review Status:** 📝 Draft  
**Next Review:** After integration testing
