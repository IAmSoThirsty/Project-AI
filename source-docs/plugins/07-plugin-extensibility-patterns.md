---
type: guide
guide_type: patterns
area: plugin-system
audience: [architect, senior-developer]
prerequisites:
  - 01-plugin-architecture-overview.md
  - 06-plugin-examples.md
tags:
  - plugin/patterns
  - extensibility
  - design-patterns
  - architecture
related_docs:
  - 01-plugin-architecture-overview.md
  - 08-plugin-integration-guide.md
last_updated: 2026-04-20
version: 1.0.0
---

# Plugin Extensibility Patterns

**Design patterns for building extensible plugin architectures**  
**Version:** 1.0.0  
**Last Updated:** 2026-04-20

---

## Table of Contents

1. [Extensibility Principles](#extensibility-principles)
2. [Core Patterns](#core-patterns)
3. [Lifecycle Patterns](#lifecycle-patterns)
4. [Communication Patterns](#communication-patterns)
5. [Security Patterns](#security-patterns)
6. [Performance Patterns](#performance-patterns)
7. [Integration Patterns](#integration-patterns)
8. [Anti-Patterns](#anti-patterns)

---

## Extensibility Principles

### 1. Open/Closed Principle

**Principle:** Plugins should be open for extension, closed for modification

**Implementation:**

```python
from abc import ABC, abstractmethod

# ✅ GOOD: Abstract interface allows extension without modification
class PluginInterface(ABC):
    @abstractmethod
    def execute(self, context: dict) -> dict:
        """Execute plugin - open for extension."""
        pass
    
    @abstractmethod
    def validate_context(self, context: dict) -> bool:
        """Validate context - closed for modification."""
        pass

# New plugin types extend without modifying interface
class DataPlugin(PluginInterface):
    def execute(self, context: dict) -> dict:
        return {"result": self.process_data(context["data"])}
    
    def validate_context(self, context: dict) -> bool:
        return "data" in context

class AIPlugin(PluginInterface):
    def execute(self, context: dict) -> dict:
        return {"result": self.generate_response(context["prompt"])}
    
    def validate_context(self, context: dict) -> bool:
        return "prompt" in context
```

### 2. Dependency Inversion

**Principle:** High-level modules depend on abstractions, not concrete implementations

**Implementation:**

```python
# ✅ GOOD: Core depends on interface, not concrete plugin
class PluginExecutor:
    def __init__(self, plugin: PluginInterface):
        self.plugin = plugin  # Depends on abstraction
    
    def run(self, context: dict) -> dict:
        if self.plugin.validate_context(context):
            return self.plugin.execute(context)
        raise ValueError("Invalid context")

# Any plugin implementing interface works
executor = PluginExecutor(DataPlugin())
executor = PluginExecutor(AIPlugin())

# ❌ BAD: Core depends on concrete implementation
class BadExecutor:
    def __init__(self, plugin: DataPlugin):  # Concrete dependency!
        self.plugin = plugin
```

### 3. Separation of Concerns

**Principle:** Separate plugin logic, validation, security, and lifecycle

**Implementation:**

```python
class WellDesignedPlugin(PluginInterface):
    # Concern 1: Core logic
    def execute(self, context: dict) -> dict:
        return self._process(context)
    
    # Concern 2: Validation
    def validate_context(self, context: dict) -> bool:
        return self._validator.validate(context)
    
    # Concern 3: Security
    def initialize(self, context: dict) -> bool:
        allowed, reason = FourLaws.validate_action(self.name, context)
        if not allowed:
            return False
        return self._initialize_resources()
    
    # Concern 4: Lifecycle
    def shutdown(self) -> None:
        self._cleanup_resources()
```

### 4. Fail-Safe Defaults

**Principle:** Plugins start in safe state, require explicit activation

**Implementation:**

```python
class SafePlugin(Plugin):
    def __init__(self):
        super().__init__(name="safe_plugin", version="1.0.0")
        self.enabled = False  # ✅ Disabled by default
    
    def initialize(self, context: dict) -> bool:
        # ✅ Validate before enabling
        allowed, reason = FourLaws.validate_action(self.name, context)
        if not allowed:
            return False  # ✅ Fail closed
        
        self.enabled = True
        return True
```

---

## Core Patterns

### Pattern 1: Plugin Registry

**Problem:** Need to manage multiple plugins with dynamic registration

**Solution:**

```python
class PluginRegistry:
    """Centralized registry for plugin management."""
    
    def __init__(self):
        self._plugins: dict[str, PluginInterface] = {}
        self._hooks: dict[str, list[PluginInterface]] = {}
    
    def register(self, plugin: PluginInterface) -> None:
        """Register plugin and its hooks."""
        name = plugin.get_name()
        
        # Store plugin
        self._plugins[name] = plugin
        
        # Register hooks
        for hook in plugin.get_hooks():
            if hook not in self._hooks:
                self._hooks[hook] = []
            self._hooks[hook].append(plugin)
        
        plugin.initialize()
    
    def execute_hook(self, hook: str, context: dict) -> list[dict]:
        """Execute all plugins registered for a hook."""
        results = []
        for plugin in self._hooks.get(hook, []):
            try:
                result = plugin.execute(context)
                results.append(result)
            except Exception as e:
                logger.error("Plugin %s failed on hook %s: %s", 
                           plugin.get_name(), hook, e)
        return results
    
    def get(self, name: str) -> PluginInterface | None:
        """Get plugin by name."""
        return self._plugins.get(name)

# Usage
registry = PluginRegistry()
registry.register(DataPlugin())
registry.register(AIPlugin())

# Execute all plugins for "before_action" hook
results = registry.execute_hook("before_action", {"action": "process"})
```

### Pattern 2: Plugin Factory

**Problem:** Need to create plugins dynamically based on configuration

**Solution:**

```python
class PluginFactory:
    """Factory for creating plugins from configuration."""
    
    def __init__(self):
        self._builders = {}
    
    def register_builder(self, plugin_type: str, builder: Callable):
        """Register plugin builder."""
        self._builders[plugin_type] = builder
    
    def create(self, config: dict) -> PluginInterface:
        """Create plugin from configuration."""
        plugin_type = config["type"]
        
        if plugin_type not in self._builders:
            raise ValueError(f"Unknown plugin type: {plugin_type}")
        
        builder = self._builders[plugin_type]
        return builder(config)

# Register builders
factory = PluginFactory()
factory.register_builder("data", lambda cfg: DataPlugin(**cfg))
factory.register_builder("ai", lambda cfg: AIPlugin(**cfg))

# Create from config
config = {
    "type": "data",
    "name": "csv_processor",
    "format": "csv"
}
plugin = factory.create(config)
```

### Pattern 3: Plugin Chain (Pipeline)

**Problem:** Need to process data through multiple plugins sequentially

**Solution:**

```python
class PluginChain:
    """Execute plugins in sequence, passing output to next plugin."""
    
    def __init__(self):
        self.plugins: list[PluginInterface] = []
    
    def add(self, plugin: PluginInterface) -> 'PluginChain':
        """Add plugin to chain (fluent interface)."""
        self.plugins.append(plugin)
        return self
    
    def execute(self, initial_context: dict) -> dict:
        """Execute chain, threading context through plugins."""
        context = initial_context
        
        for plugin in self.plugins:
            try:
                # Validate context
                if not plugin.validate_context(context):
                    raise ValueError(f"Invalid context for {plugin.get_name()}")
                
                # Execute and update context
                result = plugin.execute(context)
                context = {**context, **result}  # Merge results
                
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "failed_plugin": plugin.get_name()
                }
        
        return {"status": "success", "result": context}

# Usage
chain = PluginChain()
chain.add(ValidatorPlugin())     # Step 1: Validate
chain.add(TransformPlugin())     # Step 2: Transform
chain.add(EnrichPlugin())        # Step 3: Enrich
chain.add(PersistPlugin())       # Step 4: Persist

result = chain.execute({"data": raw_data})
```

### Pattern 4: Plugin Decorator

**Problem:** Need to add cross-cutting concerns (logging, caching, timing) to plugins

**Solution:**

```python
class PluginDecorator(PluginInterface):
    """Base decorator for adding behavior to plugins."""
    
    def __init__(self, plugin: PluginInterface):
        self.plugin = plugin
    
    def get_name(self) -> str:
        return self.plugin.get_name()
    
    def get_version(self) -> str:
        return self.plugin.get_version()
    
    def validate_context(self, context: dict) -> bool:
        return self.plugin.validate_context(context)
    
    def execute(self, context: dict) -> dict:
        return self.plugin.execute(context)
    
    def get_metadata(self) -> dict:
        return self.plugin.get_metadata()

class LoggingDecorator(PluginDecorator):
    """Add logging to plugin execution."""
    
    def execute(self, context: dict) -> dict:
        logger.info("Executing plugin: %s", self.plugin.get_name())
        start = time.time()
        
        try:
            result = self.plugin.execute(context)
            logger.info("Plugin %s completed in %.2fs", 
                       self.plugin.get_name(), time.time() - start)
            return result
        except Exception as e:
            logger.error("Plugin %s failed: %s", self.plugin.get_name(), e)
            raise

class CachingDecorator(PluginDecorator):
    """Add caching to plugin execution."""
    
    def __init__(self, plugin: PluginInterface):
        super().__init__(plugin)
        self.cache = {}
    
    def execute(self, context: dict) -> dict:
        cache_key = self._cache_key(context)
        
        if cache_key in self.cache:
            logger.info("Cache hit for %s", self.plugin.get_name())
            return self.cache[cache_key]
        
        result = self.plugin.execute(context)
        self.cache[cache_key] = result
        return result
    
    def _cache_key(self, context: dict) -> str:
        return str(sorted(context.items()))

# Usage: Stack decorators
plugin = DataPlugin()
plugin = LoggingDecorator(plugin)      # Add logging
plugin = CachingDecorator(plugin)      # Add caching
plugin = TimingDecorator(plugin)       # Add timing

result = plugin.execute(context)
```

---

## Lifecycle Patterns

### Pattern 5: Lazy Initialization

**Problem:** Plugin initialization is expensive, but plugin might not be used

**Solution:**

```python
class LazyPlugin(PluginInterface):
    """Plugin with lazy resource initialization."""
    
    def __init__(self):
        self._initialized = False
        self._heavy_resource = None
    
    def _ensure_initialized(self):
        """Initialize resources on first use."""
        if not self._initialized:
            logger.info("Lazy initializing %s", self.get_name())
            self._heavy_resource = self._load_heavy_resource()
            self._initialized = True
    
    def execute(self, context: dict) -> dict:
        self._ensure_initialized()  # Initialize only when needed
        return self._heavy_resource.process(context)
    
    def _load_heavy_resource(self):
        """Load expensive resource (database, model, etc.)."""
        import heavy_library
        return heavy_library.create_resource()
```

### Pattern 6: Resource Pooling

**Problem:** Creating new resources for each request is expensive

**Solution:**

```python
from queue import Queue
from contextlib import contextmanager

class PooledPlugin(PluginInterface):
    """Plugin with resource pooling."""
    
    def __init__(self, pool_size: int = 5):
        self.pool = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            self.pool.put(self._create_resource())
    
    @contextmanager
    def _get_resource(self):
        """Get resource from pool, return after use."""
        resource = self.pool.get()
        try:
            yield resource
        finally:
            self.pool.put(resource)
    
    def execute(self, context: dict) -> dict:
        with self._get_resource() as resource:
            return resource.process(context)
    
    def shutdown(self):
        """Close all pooled resources."""
        while not self.pool.empty():
            resource = self.pool.get()
            resource.close()
```

### Pattern 7: Plugin Lifecycle Manager

**Problem:** Need to manage plugin lifecycle consistently across all plugins

**Solution:**

```python
class PluginLifecycleManager:
    """Manage plugin lifecycle stages."""
    
    def __init__(self):
        self.plugins: dict[str, PluginInterface] = {}
        self.states: dict[str, str] = {}  # unloaded, loaded, initialized, started
    
    def load(self, plugin: PluginInterface) -> bool:
        """Load plugin."""
        name = plugin.get_name()
        
        try:
            # Store plugin
            self.plugins[name] = plugin
            self.states[name] = "loaded"
            
            emit_event("plugin.lifecycle.loaded", {"plugin": name})
            return True
        except Exception as e:
            logger.error("Failed to load plugin %s: %s", name, e)
            return False
    
    def initialize(self, name: str, context: dict = None) -> bool:
        """Initialize loaded plugin."""
        if self.states.get(name) != "loaded":
            logger.error("Plugin %s not in loaded state", name)
            return False
        
        plugin = self.plugins[name]
        
        try:
            plugin.initialize()
            self.states[name] = "initialized"
            
            emit_event("plugin.lifecycle.initialized", {"plugin": name})
            return True
        except Exception as e:
            logger.error("Failed to initialize plugin %s: %s", name, e)
            return False
    
    def start(self, name: str) -> bool:
        """Start initialized plugin."""
        if self.states.get(name) != "initialized":
            logger.error("Plugin %s not in initialized state", name)
            return False
        
        # Start plugin (if it has a start method)
        plugin = self.plugins[name]
        if hasattr(plugin, "start"):
            try:
                plugin.start()
                self.states[name] = "started"
                emit_event("plugin.lifecycle.started", {"plugin": name})
                return True
            except Exception as e:
                logger.error("Failed to start plugin %s: %s", name, e)
                return False
        
        # No start method, consider it started
        self.states[name] = "started"
        return True
    
    def stop(self, name: str) -> bool:
        """Stop running plugin."""
        if self.states.get(name) != "started":
            logger.error("Plugin %s not in started state", name)
            return False
        
        plugin = self.plugins[name]
        if hasattr(plugin, "stop"):
            try:
                plugin.stop()
                self.states[name] = "initialized"
                emit_event("plugin.lifecycle.stopped", {"plugin": name})
                return True
            except Exception as e:
                logger.error("Failed to stop plugin %s: %s", name, e)
                return False
        
        self.states[name] = "initialized"
        return True
    
    def unload(self, name: str) -> bool:
        """Unload plugin (cleanup)."""
        plugin = self.plugins.get(name)
        if not plugin:
            return False
        
        try:
            # Stop if running
            if self.states.get(name) == "started":
                self.stop(name)
            
            # Shutdown
            plugin.shutdown()
            
            # Remove from registry
            del self.plugins[name]
            del self.states[name]
            
            emit_event("plugin.lifecycle.unloaded", {"plugin": name})
            return True
        except Exception as e:
            logger.error("Failed to unload plugin %s: %s", name, e)
            return False
```

---

## Communication Patterns

### Pattern 8: Event Bus

**Problem:** Plugins need to communicate without direct coupling

**Solution:**

```python
class PluginEventBus:
    """Event bus for plugin communication."""
    
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}
    
    def subscribe(self, event: str, handler: Callable) -> None:
        """Subscribe to event."""
        if event not in self._subscribers:
            self._subscribers[event] = []
        self._subscribers[event].append(handler)
    
    def publish(self, event: str, data: dict) -> None:
        """Publish event to all subscribers."""
        for handler in self._subscribers.get(event, []):
            try:
                handler(data)
            except Exception as e:
                logger.error("Event handler failed for %s: %s", event, e)
    
    def unsubscribe(self, event: str, handler: Callable) -> None:
        """Unsubscribe from event."""
        if event in self._subscribers:
            self._subscribers[event].remove(handler)

# Usage
event_bus = PluginEventBus()

class PublisherPlugin(PluginInterface):
    def execute(self, context: dict) -> dict:
        result = self.process(context)
        event_bus.publish("data_processed", {"result": result})
        return {"status": "success"}

class SubscriberPlugin(PluginInterface):
    def initialize(self):
        event_bus.subscribe("data_processed", self.on_data_processed)
    
    def on_data_processed(self, data: dict):
        logger.info("Received processed data: %s", data)
```

### Pattern 9: Message Queue

**Problem:** Plugins need asynchronous, reliable communication

**Solution:**

```python
from queue import Queue, Empty
from threading import Thread

class PluginMessageQueue:
    """Message queue for plugin communication."""
    
    def __init__(self):
        self.queues: dict[str, Queue] = {}
        self.workers: dict[str, Thread] = {}
    
    def create_queue(self, name: str) -> None:
        """Create message queue for plugin."""
        self.queues[name] = Queue()
    
    def send(self, queue_name: str, message: dict) -> None:
        """Send message to queue."""
        if queue_name in self.queues:
            self.queues[queue_name].put(message)
    
    def start_worker(self, queue_name: str, handler: Callable) -> None:
        """Start worker thread for processing messages."""
        def worker():
            queue = self.queues[queue_name]
            while True:
                try:
                    message = queue.get(timeout=1)
                    handler(message)
                    queue.task_done()
                except Empty:
                    continue
                except Exception as e:
                    logger.error("Worker error: %s", e)
        
        thread = Thread(target=worker, daemon=True)
        thread.start()
        self.workers[queue_name] = thread

# Usage
mq = PluginMessageQueue()
mq.create_queue("data_processing")
mq.start_worker("data_processing", lambda msg: print(f"Processing: {msg}"))
mq.send("data_processing", {"action": "process", "data": [1, 2, 3]})
```

---

## Security Patterns

### Pattern 10: Capability-Based Security

**Problem:** Need fine-grained control over plugin permissions

**Solution:**

```python
class PluginCapability:
    """Represents a plugin capability/permission."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

class CapabilityManager:
    """Manage plugin capabilities."""
    
    def __init__(self):
        self.capabilities = {
            "filesystem_read": PluginCapability("filesystem_read", "Read files"),
            "filesystem_write": PluginCapability("filesystem_write", "Write files"),
            "network_http": PluginCapability("network_http", "HTTP requests"),
            "database_read": PluginCapability("database_read", "Read database"),
            "database_write": PluginCapability("database_write", "Write database"),
        }
        self.grants: dict[str, set[str]] = {}  # plugin -> capabilities
    
    def grant(self, plugin_name: str, capability: str) -> None:
        """Grant capability to plugin."""
        if capability not in self.capabilities:
            raise ValueError(f"Unknown capability: {capability}")
        
        if plugin_name not in self.grants:
            self.grants[plugin_name] = set()
        
        self.grants[plugin_name].add(capability)
        logger.info("Granted %s to plugin %s", capability, plugin_name)
    
    def check(self, plugin_name: str, capability: str) -> bool:
        """Check if plugin has capability."""
        return capability in self.grants.get(plugin_name, set())
    
    def require(self, plugin_name: str, capability: str) -> None:
        """Require capability or raise exception."""
        if not self.check(plugin_name, capability):
            raise PermissionError(
                f"Plugin {plugin_name} lacks capability: {capability}"
            )

# Usage
cap_mgr = CapabilityManager()
cap_mgr.grant("data_plugin", "filesystem_read")
cap_mgr.grant("data_plugin", "database_read")

class SecurePlugin(PluginInterface):
    def execute(self, context: dict) -> dict:
        # Check capability before operation
        cap_mgr.require(self.get_name(), "filesystem_read")
        
        # Proceed with file operation
        with open(context["file"], "r") as f:
            data = f.read()
        
        return {"data": data}
```

### Pattern 11: Sandbox Execution

**Problem:** Need to execute untrusted plugins safely

**Solution:**

```python
from app.security.agent_security import PluginIsolation

class SandboxedPluginExecutor:
    """Execute plugins in isolated sandbox."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    def execute(self, plugin_func: Callable, *args, **kwargs) -> dict:
        """Execute plugin function in sandbox."""
        try:
            # Execute in isolated process
            result = PluginIsolation.execute_isolated(
                plugin_func,
                *args,
                timeout=self.timeout,
                **kwargs
            )
            
            return {"status": "success", "result": result}
        
        except TimeoutError as e:
            logger.error("Plugin timeout: %s", e)
            return {"status": "error", "error": "timeout"}
        
        except RuntimeError as e:
            logger.error("Plugin error: %s", e)
            return {"status": "error", "error": str(e)}

# Usage
executor = SandboxedPluginExecutor(timeout=10)

def untrusted_plugin(x, y):
    return x + y

result = executor.execute(untrusted_plugin, 5, 10)
print(result)  # {"status": "success", "result": 15}
```

---

## Performance Patterns

### Pattern 12: Plugin Caching

**Problem:** Plugins execute same operations repeatedly

**Solution:**

```python
import hashlib
import pickle

class CachedPluginExecutor:
    """Execute plugins with result caching."""
    
    def __init__(self):
        self.cache = {}
    
    def _cache_key(self, plugin_name: str, context: dict) -> str:
        """Generate cache key from plugin name and context."""
        data = {"plugin": plugin_name, "context": context}
        serialized = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        return hashlib.sha256(serialized).hexdigest()
    
    def execute(self, plugin: PluginInterface, context: dict) -> dict:
        """Execute with caching."""
        cache_key = self._cache_key(plugin.get_name(), context)
        
        # Check cache
        if cache_key in self.cache:
            logger.info("Cache hit for %s", plugin.get_name())
            return self.cache[cache_key]
        
        # Execute plugin
        result = plugin.execute(context)
        
        # Cache result
        self.cache[cache_key] = result
        
        return result
```

### Pattern 13: Parallel Plugin Execution

**Problem:** Multiple plugins can execute concurrently

**Solution:**

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

class ParallelPluginExecutor:
    """Execute plugins in parallel."""
    
    def __init__(self, max_workers: int = 5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def execute_all(
        self,
        plugins: list[PluginInterface],
        context: dict
    ) -> dict[str, dict]:
        """Execute all plugins in parallel."""
        futures = {
            self.executor.submit(p.execute, context): p.get_name()
            for p in plugins
        }
        
        results = {}
        for future in as_completed(futures):
            plugin_name = futures[future]
            try:
                result = future.result()
                results[plugin_name] = result
            except Exception as e:
                logger.error("Plugin %s failed: %s", plugin_name, e)
                results[plugin_name] = {"status": "error", "error": str(e)}
        
        return results
    
    def shutdown(self):
        """Shutdown executor."""
        self.executor.shutdown(wait=True)

# Usage
executor = ParallelPluginExecutor(max_workers=10)
plugins = [DataPlugin(), AIPlugin(), AnalyticsPlugin()]

results = executor.execute_all(plugins, {"action": "process"})
executor.shutdown()
```

---

## Integration Patterns

### Pattern 14: Adapter Pattern

**Problem:** Need to integrate legacy plugins with new interface

**Solution:**

```python
class LegacyPlugin:
    """Old plugin with different interface."""
    
    def process(self, data):
        return data.upper()

class PluginAdapter(PluginInterface):
    """Adapt legacy plugin to new interface."""
    
    def __init__(self, legacy_plugin: LegacyPlugin):
        self.legacy = legacy_plugin
    
    def get_name(self) -> str:
        return "legacy_adapter"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def execute(self, context: dict) -> dict:
        # Adapt new context to legacy format
        data = context["data"]
        
        # Call legacy method
        result = self.legacy.process(data)
        
        # Adapt legacy result to new format
        return {"status": "success", "result": result}
    
    def validate_context(self, context: dict) -> bool:
        return "data" in context
    
    def get_metadata(self) -> dict:
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "legacy": True
        }

# Usage
legacy = LegacyPlugin()
adapted = PluginAdapter(legacy)
result = adapted.execute({"data": "hello"})
print(result)  # {"status": "success", "result": "HELLO"}
```

---

## Anti-Patterns

### Anti-Pattern 1: God Plugin

**Problem:** Plugin does too many unrelated things

```python
# ❌ BAD: Plugin with too many responsibilities
class GodPlugin(PluginInterface):
    def execute(self, context: dict) -> dict:
        action = context["action"]
        
        if action == "process_data":
            return self.process_data(context)
        elif action == "send_email":
            return self.send_email(context)
        elif action == "generate_report":
            return self.generate_report(context)
        elif action == "train_model":
            return self.train_model(context)
        # ... 50 more actions ...

# ✅ GOOD: Separate plugins for separate concerns
class DataProcessorPlugin(PluginInterface):
    def execute(self, context: dict) -> dict:
        return self.process_data(context)

class EmailPlugin(PluginInterface):
    def execute(self, context: dict) -> dict:
        return self.send_email(context)
```

### Anti-Pattern 2: Tight Coupling

**Problem:** Plugins directly depend on other plugins

```python
# ❌ BAD: Direct plugin dependency
class CoupledPlugin(PluginInterface):
    def __init__(self, other_plugin: DataPlugin):  # Hard dependency!
        self.other = other_plugin
    
    def execute(self, context: dict) -> dict:
        data = self.other.get_data()  # Tightly coupled!
        return self.process(data)

# ✅ GOOD: Communicate via events/interfaces
class DecoupledPlugin(PluginInterface):
    def execute(self, context: dict) -> dict:
        # Get data from context, not other plugin
        data = context.get("data")
        if not data:
            # Request data via event bus
            event_bus.publish("data_requested", {"requester": self.get_name()})
        return self.process(data)
```

### Anti-Pattern 3: No Validation

**Problem:** Plugin doesn't validate inputs

```python
# ❌ BAD: No validation
class UnsafePlugin(PluginInterface):
    def execute(self, context: dict) -> dict:
        # Assumes keys exist!
        data = context["data"]  # KeyError if missing!
        return self.process(data)

# ✅ GOOD: Always validate
class SafePlugin(PluginInterface):
    def validate_context(self, context: dict) -> bool:
        return "data" in context and isinstance(context["data"], list)
    
    def execute(self, context: dict) -> dict:
        if not self.validate_context(context):
            raise ValueError("Invalid context")
        data = context["data"]
        return self.process(data)
```

---

## References

- [Plugin Architecture Overview](./01-plugin-architecture-overview.md)
- [Plugin Examples](./06-plugin-examples.md)
- [Design Patterns: Elements of Reusable Object-Oriented Software](https://en.wikipedia.org/wiki/Design_Patterns)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

---

**Author:** AGENT-046 (Plugin System Documentation Specialist)  
**Review Status:** 📝 Draft  
**Next Review:** Architecture team review
