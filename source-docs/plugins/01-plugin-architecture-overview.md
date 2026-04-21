---
type: guide
guide_type: architecture
area: plugin-system
audience: [developer, architect]
prerequisites:
  - Python 3.11+
  - Understanding of process isolation
  - Familiarity with JSON-RPC protocols
tags:
  - plugin/architecture
  - extensibility
  - system-design
  - process-isolation
related_docs:
  - 02-plugin-api-reference.md
  - 03-plugin-loading-lifecycle.md
  - ../architecture/ARCHITECTURE_OVERVIEW.md
last_updated: 2026-04-20
version: 1.0.0
---

# Plugin Architecture Overview

**Project-AI Plugin System Architecture**  
**Version:** 1.0.0  
**Last Updated:** 2026-04-20

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architectural Overview](#architectural-overview)
3. [Four Plugin Systems](#four-plugin-systems)
4. [Design Principles](#design-principles)
5. [Security Model](#security-model)
6. [Integration Points](#integration-points)
7. [Evolution Roadmap](#evolution-roadmap)

---

## Executive Summary

The Project-AI plugin system provides a flexible, secure extensibility framework that allows developers to add functionality without modifying core code. The architecture employs **four distinct plugin systems**, each optimized for different use cases:

1. **Simple Plugin System** - In-memory enable/disable (ai_systems.py)
2. **PluginInterface System** - Full-featured abstract interface (interfaces.py)
3. **Process-Isolated Runner** - Subprocess execution with JSONL IPC (plugin_runner.py)
4. **Security Isolation Layer** - Multiprocessing-based hostile plugin containment (agent_security.py)

### Key Features

- ✅ **Process Isolation** - Plugins run in separate processes for security
- ✅ **Four Laws Integration** - All plugins validated against Asimov's Laws
- ✅ **JSON-RPC Protocol** - JSONL over stdin/stdout for IPC
- ✅ **Timeout Protection** - Configurable execution time limits
- ✅ **Observability Hooks** - Telemetry emission for monitoring
- ✅ **Plugin Manifests** - JSON metadata with capabilities and safety flags

### Current Status

⚠️ **Status:** Multi-system fragmentation (consolidation recommended)  
✅ **Security:** Process isolation implemented  
⚠️ **Persistence:** Limited (no plugin state persistence in System A)  
✅ **Testing:** Comprehensive test coverage (156+ lines of tests)

---

## Architectural Overview

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Core Application                        │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │ FourLaws   │  │ AIPersona  │  │  Intelligence Engine │  │
│  │ Validator  │  │            │  │                      │  │
│  └─────┬──────┘  └────────────┘  └──────────────────────┘  │
│        │                                                     │
│        │ validates                                           │
│        ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Plugin Manager / Registry                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │ System A    │  │ System B    │  │ System C/D │  │   │
│  │  │ (Simple)    │  │ (Interface) │  │ (Isolated) │  │   │
│  │  └─────────────┘  └─────────────┘  └────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│        │            │            │                          │
└────────┼────────────┼────────────┼──────────────────────────┘
         │            │            │
         ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌──────────────┐
    │In-Proc │  │In-Proc │  │  Subprocess  │
    │Plugin  │  │Plugin  │  │  ┌────────┐  │
    │        │  │        │  │  │ Plugin │  │
    └────────┘  └────────┘  │  │Process │  │
                            │  └────────┘  │
                            │   (JSONL IPC) │
                            └──────────────┘
```

### Component Responsibilities

| Component | Responsibility | Location |
|-----------|---------------|----------|
| **Plugin (Base)** | Simple enable/disable interface | `src/app/core/ai_systems.py:991-1013` |
| **PluginManager** | Load and track simple plugins | `src/app/core/ai_systems.py:1015-1038` |
| **PluginInterface** | Abstract base for full plugins | `src/app/core/interfaces.py:218-296` |
| **PluginRegistry** | Register and execute full plugins | `src/app/core/interfaces.py:297-389` |
| **PluginRunner** | Subprocess execution with JSONL | `src/app/plugins/plugin_runner.py:11-105` |
| **PluginIsolation** | Multiprocessing security layer | `src/app/security/agent_security.py` |
| **FourLaws** | Ethics validation for all plugins | `src/app/core/ai_systems.py:293-351` |

---

## Four Plugin Systems

### System A: Simple Plugin (In-Memory)

**Location:** `src/app/core/ai_systems.py:991-1038`

**Purpose:** Lightweight enable/disable toggle for simple extensions

**Class Hierarchy:**
```python
class Plugin:
    def __init__(name: str, version: str = "1.0.0")
    def initialize(context: Any) -> bool
    def enable() -> bool
    def disable() -> bool

class PluginManager:
    plugins: dict[str, Plugin]
    def load_plugin(plugin: Plugin) -> bool
    def get_statistics() -> dict
```

**Use Cases:**
- Quick feature toggles
- In-memory state only
- No external dependencies
- Trusted internal plugins

**Limitations:**
- ❌ No persistence (state lost on restart)
- ❌ No isolation (runs in main process)
- ❌ No versioning or dependency management
- ❌ No context validation

---

### System B: PluginInterface (Full-Featured)

**Location:** `src/app/core/interfaces.py:218-389`

**Purpose:** Full-featured plugin execution with abstract interface

**Class Hierarchy:**
```python
class PluginInterface(ABC):
    @abstractmethod
    def get_name() -> str
    @abstractmethod
    def get_version() -> str
    @abstractmethod
    def execute(context: dict) -> dict
    @abstractmethod
    def validate_context(context: dict) -> bool
    @abstractmethod
    def get_metadata() -> dict
    def initialize() -> None
    def shutdown() -> None

class PluginRegistry:
    plugins: dict[str, PluginInterface]
    def register(plugin: PluginInterface) -> None
    def unregister(name: str) -> None
    def execute_plugin(name: str, context: dict) -> dict
    def list_plugins() -> list[dict]
    def get_plugin_metadata(name: str) -> dict
```

**Use Cases:**
- Complex plugins with context validation
- Plugins requiring metadata and lifecycle hooks
- Integration with external systems
- Production-grade plugins

**Features:**
- ✅ Abstract base class for type safety
- ✅ Context validation before execution
- ✅ Metadata and versioning support
- ✅ Initialize/shutdown lifecycle hooks
- ✅ Duplicate prevention in registry
- ✅ Comprehensive test coverage (156 lines)

**Limitations:**
- ❌ No process isolation (runs in-process)
- ❌ No timeout protection
- ❌ No resource limits
- ❌ Vulnerable to malicious plugins

---

### System C: Process-Isolated Runner

**Location:** `src/app/plugins/plugin_runner.py:11-105`

**Purpose:** Execute plugins in isolated subprocesses with JSONL protocol

**Architecture:**
```python
class PluginRunner:
    def __init__(plugin_script: str, timeout: float = 5.0)
    def start() -> None           # subprocess.Popen
    def stop() -> None            # SIGTERM/SIGKILL cleanup
    def call_init(params: dict) -> dict  # JSON-RPC call
    def _readline_nonblocking(timeout: float) -> str | None
```

**Protocol:** JSON-RPC over JSONL (JSON Lines)
```json
// Host -> Plugin
{"id": "init-1", "method": "init", "params": {"example": true}}

// Plugin -> Host
{"id": "init-1", "result": {"status": "initialized"}}
// or
{"id": "init-1", "error": "Initialization failed"}
```

**Security Features:**
- ✅ Process boundaries (OS-level isolation)
- ✅ Timeout enforcement (default 5 seconds)
- ✅ Graceful termination (SIGTERM → SIGKILL)
- ✅ Non-blocking readline with timeout
- ✅ Error handling and cleanup

**Use Cases:**
- Untrusted or third-party plugins
- Long-running operations
- Plugins with external dependencies
- Marketplace plugins

**Limitations:**
- ❌ No resource limits (CPU, memory, I/O)
- ❌ No capability manifest enforcement
- ❌ No sandboxing beyond process boundaries
- ❌ Limited to init-only protocol

---

### System D: Security Isolation Layer

**Location:** `src/app/security/agent_security.py`

**Purpose:** Execute hostile plugins with multiprocessing isolation

**Architecture:**
```python
class PluginIsolation:
    @staticmethod
    def execute_isolated(
        plugin_func: Callable,
        *args,
        timeout: int = 30,
        **kwargs
    ) -> Any:
        # Uses multiprocessing.Process + Queue
        # Enforces timeout via process.join()
        # Cleanup with SIGTERM/SIGKILL
```

**Security Features:**
- ✅ Memory space isolation (separate process)
- ✅ Timeout enforcement with process termination
- ✅ Result passing via multiprocessing.Queue
- ✅ Exception capture and propagation
- ✅ Resource cleanup on timeout/error

**Use Cases:**
- Untrusted plugin code
- High-risk operations
- Sandbox testing
- Security-critical validations

**Limitations:**
- ❌ No filesystem isolation
- ❌ No network isolation
- ❌ Limited to function execution (not full plugin lifecycle)
- ❌ No capability restrictions

---

## Design Principles

### 1. Security First

**All plugins must validate against Four Laws before execution:**

```python
from app.core.ai_systems import FourLaws

class SafePlugin(Plugin):
    def initialize(self, context: dict) -> bool:
        allowed, reason = FourLaws.validate_action(
            "Initialize plugin",
            context=context
        )
        if not allowed:
            logger.warning("Plugin blocked: %s", reason)
            return False
        
        self.enabled = True
        return True
```

**Four Laws Hierarchy:**
1. **First Law:** Don't harm humans or allow harm through inaction
2. **Second Law:** Follow user orders (unless conflicts with First)
3. **Third Law:** Self-preservation (unless conflicts with First/Second)

### 2. Fail-Safe Defaults

- Plugins start **disabled** by default
- Validation failures block execution
- Timeouts kill processes (no zombie processes)
- Errors propagate with context

### 3. Observability

All plugin operations emit telemetry events:

```python
from app.core.observability import emit_event

class ObservablePlugin(Plugin):
    def initialize(self, context: dict) -> bool:
        emit_event("plugin.initialized", {
            "name": self.name,
            "version": self.version,
            "context": context
        })
        return True
```

### 4. Explicit Over Implicit

- Plugins declare capabilities in `plugin.json` manifest
- Context validation is mandatory (PluginInterface)
- Resource requirements specified upfront
- Errors are descriptive, not silent

---

## Security Model

### Threat Model

The plugin system protects against:

| Threat | Mitigation |
|--------|------------|
| **Malicious code execution** | Process isolation (System C/D) |
| **Resource exhaustion** | Timeout enforcement, process limits |
| **Data exfiltration** | No network/filesystem isolation (TODO) |
| **Privilege escalation** | Four Laws validation, no sudo/admin |
| **Zombie processes** | SIGTERM → SIGKILL cleanup |
| **State corruption** | Separate process memory (System C/D) |

### Not Protected (Known Limitations)

⚠️ **Current system does NOT isolate:**
- Filesystem access (plugins can read/write host filesystem)
- Network access (plugins can make HTTP requests)
- System calls (no seccomp/AppArmor sandboxing)
- Shared resources (databases, config files)

**Recommendation:** Use System C/D for untrusted plugins, System A/B for trusted internal plugins only.

### Plugin Trust Levels

| Level | Trust | Allowed System | Validation |
|-------|-------|----------------|------------|
| **Level 0 (Trusted)** | Internal team | System A/B | Four Laws only |
| **Level 1 (Verified)** | Marketplace verified | System B + isolation | Four Laws + manifest |
| **Level 2 (Sandbox)** | Third-party | System C | Four Laws + timeout |
| **Level 3 (Hostile)** | Untrusted/testing | System D | Four Laws + full isolation |

---

## Integration Points

### 1. Core Application Integration

Plugins integrate with core systems through defined interfaces:

```python
# ai_systems.py
from app.plugins.sample_plugin import MarketplaceSamplePlugin

plugin_manager = PluginManager(plugins_dir="plugins")
plugin = MarketplaceSamplePlugin()
plugin_manager.load_plugin(plugin)

# Plugin now available to core systems
stats = plugin_manager.get_statistics()
```

### 2. GUI Integration

Plugins can expose UI components via the dashboard:

```python
# leather_book_dashboard.py
def register_plugin_actions(self):
    """Register plugin actions in dashboard."""
    for plugin in plugin_manager.plugins.values():
        if plugin.enabled and hasattr(plugin, "get_ui_actions"):
            actions = plugin.get_ui_actions()
            self.actions_panel.add_plugin_actions(actions)
```

### 3. Intelligence Engine Integration

Plugins can process AI responses:

```python
# intelligence_engine.py
def process_with_plugins(response: str) -> str:
    """Apply plugin transformations to AI response."""
    for plugin in plugin_registry.list_plugins():
        if plugin.get("capabilities", {}).get("response_processing"):
            response = plugin_registry.execute_plugin(
                plugin["name"],
                context={"response": response, "action": "process"}
            )["result"]
    return response
```

### 4. Learning System Integration

Plugins can provide learning resources:

```python
# learning_paths.py
def get_plugin_learning_resources() -> list[dict]:
    """Get learning resources from plugins."""
    resources = []
    for plugin in plugin_registry.list_plugins():
        if "learning" in plugin.get("capabilities", []):
            result = plugin_registry.execute_plugin(
                plugin["name"],
                context={"action": "get_learning_resources"}
            )
            resources.extend(result.get("resources", []))
    return resources
```

---

## Evolution Roadmap

### Phase 1: Consolidation (Current Priority)

**Goal:** Unify four systems into cohesive architecture

1. **Define canonical plugin API** - Choose between System A or System B as base
2. **Add isolation to PluginInterface** - Integrate System C/D into System B
3. **Implement plugin persistence** - Save plugin state across restarts
4. **Create unified plugin loader** - Single entry point for all plugin types

### Phase 2: Security Hardening

**Goal:** Full sandboxing and capability restrictions

1. **Implement capability manifest enforcement** - Plugins declare required permissions
2. **Add filesystem isolation** - Restrict file access to plugin directories
3. **Add network isolation** - Control HTTP/socket access per plugin
4. **Implement resource limits** - CPU, memory, I/O quotas

### Phase 3: Marketplace Support

**Goal:** Enable plugin distribution and discovery

1. **Plugin signing and verification** - GPG/RSA signatures for trust
2. **Dependency management** - Resolve and install plugin dependencies
3. **Versioning and upgrades** - Semantic versioning, automatic updates
4. **Plugin marketplace API** - Publish, search, install plugins

### Phase 4: Advanced Features

**Goal:** Enterprise-grade plugin ecosystem

1. **Hot reloading** - Update plugins without restart
2. **Plugin orchestration** - Chain plugins into workflows
3. **Distributed plugins** - Remote plugin execution via gRPC
4. **Plugin telemetry** - Metrics, logging, tracing per plugin

---

## References

### Internal Documentation

- [Plugin API Reference](./02-plugin-api-reference.md)
- [Plugin Loading Lifecycle](./03-plugin-loading-lifecycle.md)
- [Plugin Security Guide](./04-plugin-security-guide.md)
- [Creating Your First Plugin](./05-plugin-development-guide.md)

### Source Code

- `src/app/core/ai_systems.py:991-1038` - Simple Plugin & PluginManager
- `src/app/core/interfaces.py:218-389` - PluginInterface & PluginRegistry
- `src/app/plugins/plugin_runner.py` - Process-isolated runner
- `src/app/security/agent_security.py` - PluginIsolation

### External References

- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [Python multiprocessing](https://docs.python.org/3/library/multiprocessing.html)
- [Subprocess Management](https://docs.python.org/3/library/subprocess.html)

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-20 | Initial architecture documentation |

---

**Author:** AGENT-046 (Plugin System Documentation Specialist)  
**Review Status:** 📝 Draft (awaiting architecture team review)  
**Next Review:** Phase 1 consolidation completion
