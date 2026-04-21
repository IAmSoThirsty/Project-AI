---
type: tutorial
tutorial_type: development
area: plugin-system
audience: [developer]
prerequisites:
  - Python 3.11+ installed
  - 01-plugin-architecture-overview.md
  - 02-plugin-api-reference.md
tags:
  - plugin/development
  - tutorial
  - getting-started
related_docs:
  - 06-plugin-examples.md
  - 04-plugin-security-guide.md
  - 03-plugin-loading-lifecycle.md
last_updated: 2026-04-20
version: 1.0.0
estimated_time: 30 minutes
---

# Plugin Development Guide

**Step-by-step tutorial for creating Project-AI plugins**  
**Version:** 1.0.0  
**Last Updated:** 2026-04-20  
**Estimated Time:** 30 minutes

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Tutorial 1: Simple Plugin](#tutorial-1-simple-plugin)
3. [Tutorial 2: Full-Featured Plugin](#tutorial-2-full-featured-plugin)
4. [Tutorial 3: Subprocess Plugin](#tutorial-3-subprocess-plugin)
5. [Testing Your Plugin](#testing-your-plugin)
6. [Debugging Plugins](#debugging-plugins)
7. [Publishing Plugins](#publishing-plugins)
8. [Common Patterns](#common-patterns)

---

## Getting Started

### Prerequisites

Before starting, ensure you have:

- ✅ Python 3.11 or higher installed
- ✅ Project-AI repository cloned
- ✅ Virtual environment activated
- ✅ Dependencies installed (`pip install -r requirements.txt`)
- ✅ Read [Plugin Architecture Overview](./01-plugin-architecture-overview.md)

### Development Environment Setup

```bash
# Navigate to project root
cd T:\Project-AI-main

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.venv\Scripts\activate.bat

# Verify Python version
python --version  # Should be 3.11+

# Create plugin directory
mkdir src\app\plugins\my_plugin
cd src\app\plugins\my_plugin
```

### Plugin Directory Structure

```
src/app/plugins/my_plugin/
├── __init__.py           # Package initialization
├── plugin.py             # Main plugin code
├── plugin.json           # Plugin manifest
├── README.md             # Plugin documentation
├── requirements.txt      # Plugin dependencies
└── tests/
    └── test_plugin.py    # Plugin tests
```

---

## Tutorial 1: Simple Plugin

**Goal:** Create a basic greeting plugin using System A (Simple Plugin)

**Time:** 10 minutes

### Step 1: Create Plugin Class

Create `src/app/plugins/greeting_plugin.py`:

```python
"""Simple greeting plugin demonstrating basic plugin structure."""

from __future__ import annotations

import logging
from typing import Any

from app.core.ai_systems import FourLaws, Plugin

logger = logging.getLogger(__name__)

try:
    from app.core.observability import emit_event
except ImportError:
    def emit_event(event_name: str, metadata: dict[str, Any] | None = None) -> None:
        logger.debug("Observability stub for %s: %s", event_name, metadata)


class GreetingPlugin(Plugin):
    """A simple plugin that provides greeting functionality.
    
    This plugin demonstrates:
    - Basic Plugin class inheritance
    - Four Laws validation
    - Context initialization
    - Telemetry emission
    """
    
    def __init__(self) -> None:
        """Initialize greeting plugin."""
        super().__init__(name="greeting_plugin", version="1.0.0")
        self.greetings = ["Hello"]
        self.greeting_count = 0
    
    def initialize(self, context: dict[str, Any] | None = None) -> bool:
        """Initialize plugin with context validation.
        
        Args:
            context: Initialization context with optional keys:
                - greetings: list[str] - Custom greeting messages
                - is_user_order: bool - Whether this is a user order
        
        Returns:
            True if initialization succeeded, False otherwise
        """
        context = context or {}
        
        # Step 1: Validate against Four Laws
        allowed, reason = FourLaws.validate_action(
            "Initialize greeting plugin",
            context=context
        )
        
        if not allowed:
            logger.warning("Greeting plugin blocked: %s", reason)
            emit_event("plugin.greeting.blocked", {"reason": reason})
            return False
        
        # Step 2: Load configuration from context
        self.greetings = context.get("greetings", ["Hello", "Hi", "Hey"])
        logger.info("Loaded %d greeting messages", len(self.greetings))
        
        # Step 3: Enable plugin
        self.enabled = True
        
        # Step 4: Emit telemetry
        emit_event("plugin.greeting.initialized", {
            "name": self.name,
            "version": self.version,
            "greeting_count": len(self.greetings)
        })
        
        logger.info("Greeting plugin initialized successfully")
        return True
    
    def greet(self, name: str) -> str:
        """Generate a greeting for the given name.
        
        Args:
            name: Name to greet
        
        Returns:
            Greeting message
        
        Raises:
            RuntimeError: If plugin not enabled
        
        Example:
            >>> plugin = GreetingPlugin()
            >>> plugin.initialize({"greetings": ["Hi", "Hello"]})
            >>> plugin.greet("Alice")
            "Hi, Alice!"
        """
        if not self.enabled:
            raise RuntimeError("Greeting plugin not enabled")
        
        # Select greeting (rotate through list)
        greeting = self.greetings[self.greeting_count % len(self.greetings)]
        self.greeting_count += 1
        
        message = f"{greeting}, {name}!"
        
        # Emit telemetry
        emit_event("plugin.greeting.generated", {
            "name": name,
            "greeting": greeting,
            "count": self.greeting_count
        })
        
        return message
    
    def get_statistics(self) -> dict[str, Any]:
        """Get plugin statistics.
        
        Returns:
            Statistics dictionary with greeting count
        """
        return {
            "enabled": self.enabled,
            "greeting_count": self.greeting_count,
            "available_greetings": len(self.greetings)
        }


def initialize(context: dict[str, Any] | None = None) -> bool:
    """Entry point for plugin loaders.
    
    Args:
        context: Initialization context
    
    Returns:
        True if initialization successful
    """
    plugin = GreetingPlugin()
    return plugin.initialize(context)


__all__ = ["GreetingPlugin", "initialize"]
```

### Step 2: Create Plugin Manifest

Create `src/app/plugins/greeting_plugin.json`:

```json
{
  "name": "greeting_plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Simple plugin that provides customizable greeting messages",
  "hooks": [],
  "four_laws_safe": true,
  "safe_for_learning": true,
  "capabilities": ["greeting", "message_generation"],
  "dependencies": [],
  "resource_limits": {
    "max_memory_mb": 10,
    "max_cpu_percent": 5,
    "max_execution_seconds": 1
  },
  "permissions": {
    "filesystem": [],
    "network": [],
    "system": []
  }
}
```

### Step 3: Test the Plugin

Create `tests/test_greeting_plugin.py`:

```python
"""Tests for greeting plugin."""

import pytest
from app.core.ai_systems import PluginManager
from app.plugins.greeting_plugin import GreetingPlugin


class TestGreetingPlugin:
    """Test suite for GreetingPlugin."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance for testing."""
        return GreetingPlugin()
    
    def test_initialization(self, plugin):
        """Test plugin initializes correctly."""
        context = {
            "greetings": ["Hi", "Hello"],
            "is_user_order": True,
            "harms_human": False
        }
        
        success = plugin.initialize(context)
        assert success is True
        assert plugin.enabled is True
        assert plugin.greetings == ["Hi", "Hello"]
    
    def test_greet(self, plugin):
        """Test greeting generation."""
        plugin.initialize({"greetings": ["Hello"]})
        
        message = plugin.greet("Alice")
        assert message == "Hello, Alice!"
        assert plugin.greeting_count == 1
    
    def test_greet_rotation(self, plugin):
        """Test greeting rotation."""
        plugin.initialize({"greetings": ["Hi", "Hello"]})
        
        msg1 = plugin.greet("Alice")
        msg2 = plugin.greet("Bob")
        
        assert msg1 == "Hi, Alice!"
        assert msg2 == "Hello, Bob!"
    
    def test_greet_not_enabled(self, plugin):
        """Test greeting fails when plugin not enabled."""
        with pytest.raises(RuntimeError, match="not enabled"):
            plugin.greet("Alice")
    
    def test_statistics(self, plugin):
        """Test statistics reporting."""
        plugin.initialize({"greetings": ["Hi"]})
        plugin.greet("Alice")
        
        stats = plugin.get_statistics()
        assert stats["enabled"] is True
        assert stats["greeting_count"] == 1
        assert stats["available_greetings"] == 1
    
    def test_plugin_manager_integration(self, plugin):
        """Test plugin works with PluginManager."""
        manager = PluginManager(plugins_dir="data/test_plugins")
        
        plugin.initialize({})
        loaded = manager.load_plugin(plugin)
        
        assert loaded is True
        assert "greeting_plugin" in manager.plugins
        assert manager.plugins["greeting_plugin"].enabled is True
```

### Step 4: Run Tests

```bash
# Run tests
pytest tests/test_greeting_plugin.py -v

# Run with coverage
pytest tests/test_greeting_plugin.py --cov=app.plugins.greeting_plugin --cov-report=term
```

### Step 5: Use the Plugin

Create `examples/use_greeting_plugin.py`:

```python
"""Example usage of greeting plugin."""

from app.core.ai_systems import PluginManager
from app.plugins.greeting_plugin import GreetingPlugin

# Create plugin manager
manager = PluginManager(plugins_dir="data/plugins")

# Create and initialize plugin
plugin = GreetingPlugin()
success = plugin.initialize({
    "greetings": ["Hello", "Hi", "Hey", "Greetings"],
    "is_user_order": True,
    "harms_human": False
})

if success:
    print("Plugin initialized successfully!")
    
    # Load into manager
    manager.load_plugin(plugin)
    
    # Use plugin
    print(plugin.greet("Alice"))    # "Hello, Alice!"
    print(plugin.greet("Bob"))      # "Hi, Bob!"
    print(plugin.greet("Charlie"))  # "Hey, Charlie!"
    
    # Get statistics
    stats = plugin.get_statistics()
    print(f"Total greetings: {stats['greeting_count']}")
else:
    print("Plugin initialization failed")
```

---

## Tutorial 2: Full-Featured Plugin

**Goal:** Create a data processing plugin using System B (PluginInterface)

**Time:** 15 minutes

### Step 1: Create Plugin Class

Create `src/app/plugins/data_processor_plugin.py`:

```python
"""Data processing plugin demonstrating PluginInterface."""

from __future__ import annotations

import logging
from typing import Any

from app.core.interfaces import PluginInterface

logger = logging.getLogger(__name__)


class DataProcessorPlugin(PluginInterface):
    """Plugin for processing numerical data.
    
    Supports operations:
    - sum: Calculate sum of numbers
    - average: Calculate average of numbers
    - median: Calculate median of numbers
    - stats: Calculate full statistics (min, max, mean, median)
    """
    
    def __init__(self) -> None:
        """Initialize data processor plugin."""
        self.operations_count = 0
        self.cache = {}
    
    def get_name(self) -> str:
        """Get plugin name."""
        return "data_processor"
    
    def get_version(self) -> str:
        """Get plugin version."""
        return "1.0.0"
    
    def validate_context(self, context: dict[str, Any]) -> bool:
        """Validate execution context.
        
        Required keys:
        - operation: str - Operation to perform (sum, average, median, stats)
        - data: list[int|float] - Numerical data to process
        
        Optional keys:
        - use_cache: bool - Whether to use cached results (default: False)
        """
        # Check required keys
        if "operation" not in context:
            logger.error("Missing required key: operation")
            return False
        
        if "data" not in context:
            logger.error("Missing required key: data")
            return False
        
        # Validate operation
        valid_operations = ["sum", "average", "median", "stats"]
        if context["operation"] not in valid_operations:
            logger.error("Invalid operation: %s", context["operation"])
            return False
        
        # Validate data
        data = context["data"]
        if not isinstance(data, list):
            logger.error("Data must be a list, got %s", type(data))
            return False
        
        if len(data) == 0:
            logger.error("Data list cannot be empty")
            return False
        
        if not all(isinstance(x, (int, float)) for x in data):
            logger.error("All data elements must be numbers")
            return False
        
        return True
    
    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute data processing operation.
        
        Args:
            context: Execution context
        
        Returns:
            Result dictionary with keys:
            - status: "success" or "error"
            - result: Operation result (if success)
            - error: Error message (if error)
        
        Raises:
            ValueError: If context validation fails
        """
        # Validate context
        if not self.validate_context(context):
            raise ValueError("Invalid execution context")
        
        operation = context["operation"]
        data = context["data"]
        use_cache = context.get("use_cache", False)
        
        # Check cache
        cache_key = (operation, tuple(data))
        if use_cache and cache_key in self.cache:
            logger.info("Returning cached result for %s", operation)
            return {
                "status": "success",
                "result": self.cache[cache_key],
                "from_cache": True
            }
        
        # Execute operation
        try:
            if operation == "sum":
                result = sum(data)
            elif operation == "average":
                result = sum(data) / len(data)
            elif operation == "median":
                sorted_data = sorted(data)
                n = len(sorted_data)
                if n % 2 == 0:
                    result = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
                else:
                    result = sorted_data[n//2]
            elif operation == "stats":
                result = {
                    "min": min(data),
                    "max": max(data),
                    "mean": sum(data) / len(data),
                    "median": self._calculate_median(data),
                    "count": len(data)
                }
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            # Cache result
            if use_cache:
                self.cache[cache_key] = result
            
            # Update counter
            self.operations_count += 1
            
            logger.info("Completed %s operation on %d elements", operation, len(data))
            
            return {
                "status": "success",
                "result": result,
                "from_cache": False
            }
            
        except Exception as e:
            logger.exception("Operation failed: %s", e)
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_median(self, data: list[float]) -> float:
        """Calculate median of data."""
        sorted_data = sorted(data)
        n = len(sorted_data)
        if n % 2 == 0:
            return (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
        else:
            return sorted_data[n//2]
    
    def get_metadata(self) -> dict[str, Any]:
        """Get plugin metadata."""
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "description": "Process numerical data with statistical operations",
            "author": "Project-AI Team",
            "capabilities": ["sum", "average", "median", "stats"],
            "dependencies": [],
            "operations_count": self.operations_count,
            "cache_size": len(self.cache)
        }
    
    def initialize(self) -> None:
        """Initialize plugin."""
        logger.info("Data processor plugin initialized")
        self.operations_count = 0
        self.cache = {}
    
    def shutdown(self) -> None:
        """Shutdown plugin."""
        logger.info("Data processor plugin shutting down")
        logger.info("Total operations: %d", self.operations_count)
        self.cache.clear()


__all__ = ["DataProcessorPlugin"]
```

### Step 2: Create Tests

Create `tests/test_data_processor_plugin.py`:

```python
"""Tests for data processor plugin."""

import pytest
from app.core.interfaces import PluginRegistry
from app.plugins.data_processor_plugin import DataProcessorPlugin


class TestDataProcessorPlugin:
    """Test suite for DataProcessorPlugin."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return DataProcessorPlugin()
    
    @pytest.fixture
    def registry(self, plugin):
        """Create registry with plugin."""
        registry = PluginRegistry()
        registry.register(plugin)
        return registry
    
    def test_sum_operation(self, registry):
        """Test sum operation."""
        result = registry.execute_plugin(
            "data_processor",
            context={"operation": "sum", "data": [1, 2, 3, 4, 5]}
        )
        
        assert result["status"] == "success"
        assert result["result"] == 15
    
    def test_average_operation(self, registry):
        """Test average operation."""
        result = registry.execute_plugin(
            "data_processor",
            context={"operation": "average", "data": [10, 20, 30]}
        )
        
        assert result["status"] == "success"
        assert result["result"] == 20.0
    
    def test_median_operation(self, registry):
        """Test median operation."""
        result = registry.execute_plugin(
            "data_processor",
            context={"operation": "median", "data": [1, 2, 3, 4, 5]}
        )
        
        assert result["status"] == "success"
        assert result["result"] == 3
    
    def test_stats_operation(self, registry):
        """Test stats operation."""
        result = registry.execute_plugin(
            "data_processor",
            context={"operation": "stats", "data": [1, 2, 3, 4, 5]}
        )
        
        assert result["status"] == "success"
        assert result["result"]["min"] == 1
        assert result["result"]["max"] == 5
        assert result["result"]["mean"] == 3.0
        assert result["result"]["count"] == 5
    
    def test_caching(self, registry):
        """Test result caching."""
        context = {
            "operation": "sum",
            "data": [1, 2, 3],
            "use_cache": True
        }
        
        # First call
        result1 = registry.execute_plugin("data_processor", context)
        assert result1["from_cache"] is False
        
        # Second call (should use cache)
        result2 = registry.execute_plugin("data_processor", context)
        assert result2["from_cache"] is True
        assert result2["result"] == result1["result"]
    
    def test_invalid_operation(self, registry):
        """Test invalid operation."""
        with pytest.raises(ValueError, match="Invalid execution context"):
            registry.execute_plugin(
                "data_processor",
                context={"operation": "invalid", "data": [1, 2, 3]}
            )
    
    def test_empty_data(self, registry):
        """Test empty data list."""
        with pytest.raises(ValueError, match="Invalid execution context"):
            registry.execute_plugin(
                "data_processor",
                context={"operation": "sum", "data": []}
            )
```

### Step 3: Use the Plugin

```python
from app.core.interfaces import PluginRegistry
from app.plugins.data_processor_plugin import DataProcessorPlugin

# Create registry and register plugin
registry = PluginRegistry()
plugin = DataProcessorPlugin()
registry.register(plugin)

# Execute operations
result = registry.execute_plugin(
    "data_processor",
    context={
        "operation": "stats",
        "data": [10, 20, 30, 40, 50],
        "use_cache": True
    }
)

print(result)
# {
#   "status": "success",
#   "result": {
#     "min": 10,
#     "max": 50,
#     "mean": 30.0,
#     "median": 30,
#     "count": 5
#   },
#   "from_cache": False
# }

# Get metadata
metadata = registry.get_plugin_metadata("data_processor")
print(f"Operations count: {metadata['operations_count']}")
```

---

## Tutorial 3: Subprocess Plugin

**Goal:** Create a plugin that runs in isolated subprocess

**Time:** 15 minutes

### Step 1: Create Plugin Script

Create `src/app/plugins/echo_plugin.py`:

```python
#!/usr/bin/env python3
"""Echo plugin using JSONL protocol for subprocess isolation."""

import json
import sys
import time
from typing import Any


def handle_init(params: dict[str, Any]) -> dict[str, Any]:
    """Handle init method call.
    
    Args:
        params: Initialization parameters
    
    Returns:
        Initialization result
    """
    config = params.get("config", {})
    return {
        "status": "initialized",
        "config": config,
        "timestamp": time.time()
    }


def handle_echo(params: dict[str, Any]) -> dict[str, Any]:
    """Handle echo method call.
    
    Args:
        params: Echo parameters with 'message' key
    
    Returns:
        Echo result
    """
    message = params.get("message", "")
    return {
        "echoed": message,
        "length": len(message),
        "timestamp": time.time()
    }


def main():
    """Main loop: read JSONL from stdin, write responses to stdout."""
    for line in sys.stdin:
        try:
            # Parse request
            request = json.loads(line.strip())
            request_id = request["id"]
            method = request["method"]
            params = request.get("params", {})
            
            # Dispatch to handler
            if method == "init":
                result = handle_init(params)
            elif method == "echo":
                result = handle_echo(params)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            # Send success response
            response = {"id": request_id, "result": result}
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            # Send error response
            error_response = {
                "id": request.get("id", "unknown"),
                "error": str(e)
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
```

### Step 2: Create Runner

Create `examples/use_echo_plugin.py`:

```python
"""Example usage of echo subprocess plugin."""

from app.plugins.plugin_runner import PluginRunner

# Create runner
runner = PluginRunner(
    plugin_script="src/app/plugins/echo_plugin.py",
    timeout=10.0
)

try:
    # Start subprocess
    runner.start()
    print("Plugin subprocess started")
    
    # Call init
    init_response = runner.call_init({
        "config": {"debug": True}
    })
    print(f"Init response: {init_response}")
    
    # Call echo (requires extending PluginRunner with generic call_method)
    # For now, only init is supported
    
finally:
    # Always cleanup
    runner.stop()
    print("Plugin subprocess stopped")
```

### Step 3: Test Manually

```bash
# Test plugin manually
echo '{"id":"test-1","method":"init","params":{"config":{"debug":true}}}' | python src/app/plugins/echo_plugin.py

# Expected output:
# {"id": "test-1", "result": {"status": "initialized", "config": {"debug": true}, "timestamp": 1713619200.0}}
```

---

## Testing Your Plugin

### Unit Testing

```python
import pytest
from app.plugins.my_plugin import MyPlugin

def test_plugin_initialization():
    """Test plugin initializes correctly."""
    plugin = MyPlugin()
    success = plugin.initialize({})
    assert success is True
    assert plugin.enabled is True

def test_plugin_validation():
    """Test context validation."""
    plugin = MyPlugin()
    plugin.initialize({})
    
    # Valid context
    assert plugin.validate_context({"action": "test", "data": []}) is True
    
    # Invalid context
    assert plugin.validate_context({}) is False
```

### Integration Testing

```python
def test_plugin_with_manager():
    """Test plugin works with PluginManager."""
    from app.core.ai_systems import PluginManager
    
    manager = PluginManager()
    plugin = MyPlugin()
    plugin.initialize({})
    
    manager.load_plugin(plugin)
    assert "my_plugin" in manager.plugins
```

### Run Tests

```bash
# Run all plugin tests
pytest tests/plugins/ -v

# Run with coverage
pytest tests/plugins/ --cov=app.plugins --cov-report=html

# Open coverage report
start htmlcov/index.html
```

---

## Debugging Plugins

### Enable Debug Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use plugin
plugin = MyPlugin()
plugin.initialize({})  # Will show debug logs
```

### Debug Subprocess Plugins

```python
# Check stderr for errors
runner = PluginRunner("plugins/my_plugin.py")
runner.start()

# Read stderr
if runner.proc and runner.proc.stderr:
    errors = runner.proc.stderr.read()
    print(f"Errors: {errors}")
```

### Common Issues

1. **Plugin won't initialize**
   - Check Four Laws validation context
   - Verify required context keys present
   - Review logs for error messages

2. **Subprocess timeout**
   - Increase timeout value
   - Check plugin script for infinite loops
   - Verify plugin writes to stdout

3. **Import errors**
   - Use `python -m` to run (not `python path/to/file.py`)
   - Verify PYTHONPATH includes `src/`
   - Check dependencies installed

---

## Publishing Plugins

### Step 1: Create README

```markdown
# My Plugin

Brief description of what your plugin does.

## Installation

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Usage

\`\`\`python
from app.plugins.my_plugin import MyPlugin

plugin = MyPlugin()
plugin.initialize({})
\`\`\`

## API Reference

### Methods

- `initialize(context)` - Initialize plugin
- `execute(context)` - Execute plugin logic

## License

MIT License
```

### Step 2: Version Your Plugin

Follow [Semantic Versioning](https://semver.org/):

- **1.0.0** - Initial release
- **1.1.0** - New feature (backward compatible)
- **1.0.1** - Bug fix (backward compatible)
- **2.0.0** - Breaking change

### Step 3: Document Examples

Create `examples/my_plugin_example.py` with usage examples.

---

## Common Patterns

### Pattern: Configuration Plugin

```python
class ConfigPlugin(Plugin):
    def __init__(self):
        super().__init__(name="config_plugin", version="1.0.0")
        self.config_file = "data/plugins/config.json"
    
    def initialize(self, context: dict) -> bool:
        with open(self.config_file, encoding="utf-8") as f:
            self.config = json.load(f)
        return True
```

### Pattern: Async Plugin

```python
import asyncio

class AsyncPlugin(PluginInterface):
    async def execute_async(self, context: dict) -> dict:
        """Async execution."""
        result = await self._fetch_data(context["url"])
        return {"result": result}
    
    def execute(self, context: dict) -> dict:
        """Sync wrapper for async execution."""
        return asyncio.run(self.execute_async(context))
```

### Pattern: Resource Pooling

```python
class PooledPlugin(Plugin):
    def initialize(self, context: dict) -> bool:
        import multiprocessing
        self.pool = multiprocessing.Pool(processes=4)
        return True
    
    def shutdown(self):
        self.pool.close()
        self.pool.join()
```

---

## Next Steps

- Read [Plugin Examples](./06-plugin-examples.md) for more patterns
- Review [Plugin Security Guide](./04-plugin-security-guide.md) for security best practices
- Explore existing plugins in `src/app/plugins/`

---

**Author:** AGENT-046 (Plugin System Documentation Specialist)  
**Review Status:** 📝 Draft  
**Next Review:** After developer testing
