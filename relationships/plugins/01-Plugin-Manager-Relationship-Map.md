---
title: "Plugin Manager - Relationship Map"
agent: AGENT-067
mission: Plugin System Relationship Mapping
created: 2026-04-20
last_verified: 2026-04-20
review_cycle: Quarterly
status: Active
system: Simple Plugin System (A)
source: src/app/core/ai_systems.py:991-1038
---

# Plugin Manager - Comprehensive Relationship Map

## Executive Summary

**PluginManager** is the lightweight plugin orchestration system in Project-AI's **System A** (Simple Plugin). It provides basic plugin loading, enable/disable lifecycle, and in-memory registry without persistence or sandboxing.

**Core Purpose:** Enable extensibility through loadable `Plugin` modules with minimal overhead.

---

## 1. WHAT: Component Functionality & Boundaries

### Core Classes

#### Plugin (Base Class)

**Location:** `src/app/core/ai_systems.py:991-1013`

```python
class Plugin:
    """Base plugin class."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name          # Unique identifier
        self.version = version    # Semantic version
        self.enabled = False      # Disabled by default
    
    def initialize(self, context: Any) -> bool:
        """Override in subclass for custom initialization."""
        return True
    
    def enable(self) -> bool:
        """Enable plugin."""
        self.enabled = True
        return True
    
    def disable(self) -> bool:
        """Disable plugin."""
        self.enabled = False
        return True
```

**Attributes:**
- `name`: Plugin identifier (string, unique across registry)
- `version`: Semantic version (default "1.0.0")
- `enabled`: Boolean state (False after init, True after load/enable)

**Methods:**
- `initialize(context)`: Subclass override point, returns bool
- `enable()`: Sets `enabled = True`
- `disable()`: Sets `enabled = False`

#### PluginManager (Registry)

**Location:** `src/app/core/ai_systems.py:1015-1038`

```python
class PluginManager:
    """Manage plugins."""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = plugins_dir
        self.plugins: dict[str, Plugin] = {}  # Registry
        os.makedirs(plugins_dir, exist_ok=True)
    
    def load_plugin(self, plugin: Plugin) -> bool:
        """Load and enable plugin."""
        if plugin.name in self.plugins:
            logger.warning("Plugin %s already loaded; replacing", plugin.name)
        self.plugins[plugin.name] = plugin
        return plugin.enable()
    
    def get_statistics(self) -> dict[str, Any]:
        """Get stats."""
        return {
            "total": len(self.plugins),
            "enabled": len([p for p in self.plugins.values() if p.enabled])
        }
```

**Attributes:**
- `plugins_dir`: Directory path (created if missing)
- `plugins`: Dict mapping plugin names to Plugin instances

**Methods:**
- `load_plugin(plugin)`: Registers + enables plugin (replaces if exists)
- `get_statistics()`: Returns `{total: int, enabled: int}`

### Boundaries & Limitations

**DOES:**
- ✅ Load plugins into in-memory registry
- ✅ Enable/disable plugins dynamically
- ✅ Track enabled vs. total plugin counts
- ✅ Warn on duplicate plugin names (then replace)
- ✅ Create plugins directory if missing

**DOES NOT:**
- ❌ Persist plugin state across restarts
- ❌ Validate plugin code or dependencies
- ❌ Provide sandboxing (runs in main process)
- ❌ Handle plugin versioning or compatibility
- ❌ Auto-discover plugins (manual instantiation required)
- ❌ Manage plugin configuration
- ❌ Implement hot-reload (must restart app)

---

## 2. WHO: Stakeholders & Decision-Makers

### Primary Stakeholders

| Stakeholder | Role | Authority | Decision Power |
|------------|------|-----------|----------------|
| **Security Team** | Plugin vetting | CRITICAL | Can block untrusted plugins |
| **Architecture Team** | API design | HIGH | Defines plugin contract |
| **Plugin Authors** | Extension devs | IMPLEMENTATION | Create plugins |
| **Core Developers** | Manager maintenance | IMPLEMENTATION | Bug fixes, API changes |
| **End Users** | Plugin consumers | EXPERIENCE | Enable/disable via GUI/CLI |

### User Classes

1. **Plugin Authors**
   - Internal: Create `sample_plugin.py`, `graph_analysis_plugin.py`
   - External: Community contributions
   - Vendors: Commercial plugins (NOT RECOMMENDED for System A due to no sandboxing)

2. **Plugin Consumers**
   - **End users:** Toggle plugins in GUI (future)
   - **Admins:** Configure via startup scripts
   - **Developers:** Load plugins programmatically

3. **Integration Points**
   - **GUI:** PersonaPanel → Plugin configuration tab (TODO)
   - **CLI:** `project_ai_cli.py --load-plugin <name>`
   - **Core Systems:** Intelligence engine, learning paths, observability

---

## 3. WHEN: Lifecycle Events & State Transitions

### Plugin State Machine

```
┌──────────┐
│  UNLOADED│ (initial state, plugin not in registry)
└────┬─────┘
     │ load_plugin(plugin)
     ▼
┌──────────┐
│  LOADED  │ (in registry, enabled = False)
└────┬─────┘
     │ plugin.enable()
     ▼
┌──────────┐
│ ENABLED  │ (enabled = True, operational)
└────┬─────┘
     │ plugin.disable()
     ▼
┌──────────┐
│ DISABLED │ (in registry, enabled = False)
└────┬─────┘
     │ del manager.plugins[name]
     ▼
┌──────────┐
│ UNLOADED │
└──────────┘
```

### State Transitions

| Transition | Trigger | Action | Side Effects |
|-----------|---------|--------|--------------|
| **UNLOADED → LOADED** | `manager.load_plugin(plugin)` | Add to registry | Creates plugins_dir if needed |
| **LOADED → ENABLED** | `plugin.enable()` | Set `enabled = True` | Plugin becomes active |
| **ENABLED → DISABLED** | `plugin.disable()` | Set `enabled = False` | Plugin stops executing |
| **DISABLED → ENABLED** | `plugin.enable()` | Set `enabled = True` | Plugin resumes |
| **LOADED/ENABLED/DISABLED → UNLOADED** | `del manager.plugins[name]` | Remove from registry | Memory freed |

### Event Timeline

```
App Startup
    │
    ├─► PluginManager.__init__("plugins")
    │   ├─► os.makedirs("plugins", exist_ok=True)
    │   └─► self.plugins = {}
    │
    ├─► plugin1 = MarketplaceSamplePlugin()
    │   └─► super().__init__("marketplace_sample_plugin", "0.1.0")
    │
    ├─► manager.load_plugin(plugin1)
    │   ├─► Check if name in registry (duplicate warning if exists)
    │   ├─► self.plugins[plugin1.name] = plugin1
    │   └─► plugin1.enable() → enabled = True
    │
    └─► Runtime: plugin1.enabled == True

User Action: Disable Plugin
    │
    └─► plugin1.disable() → enabled = False

App Shutdown
    │
    └─► (No cleanup - plugins garbage collected)
```

### Temporal Constraints

- **Load Time:** O(1) - simple dict insertion
- **Enable/Disable:** O(1) - boolean assignment
- **Statistics:** O(n) - iterates all plugins to count enabled
- **No Timeout:** Plugins run indefinitely (no process isolation)

---

## 4. WHERE: Integration Points & Data Flows

### System Context

```
┌─────────────────────────────────────────────────────────────┐
│                    Core Application                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐                                           │
│  │  FourLaws    │ (not enforced in System A - manual call) │
│  └──────────────┘                                           │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              PluginManager                          │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │ plugins: dict[str, Plugin]                     │ │  │
│  │  │   "sample_plugin"    → <Plugin object>         │ │  │
│  │  │   "graph_analysis"   → <Plugin object>         │ │  │
│  │  │   "marketplace_sample" → <Plugin object>       │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │                                                      │  │
│  │  load_plugin() ───► plugin.enable() ───► True      │  │
│  │  get_statistics() ───► {total: 3, enabled: 2}      │  │
│  └──────────────────────────────────────────────────────┘  │
│         │                                                   │
│         ├──► GUI Integration (dashboard panels)            │
│         ├──► Intelligence Engine (response processing)     │
│         └──► Observability (telemetry emission)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow: Load Plugin

```
User Code
    │
    ├─► plugin = MarketplaceSamplePlugin()
    │   └─► Plugin.__init__("marketplace_sample_plugin", "0.1.0")
    │       ├─► self.name = "marketplace_sample_plugin"
    │       ├─► self.version = "0.1.0"
    │       └─► self.enabled = False
    │
    ├─► manager.load_plugin(plugin)
    │   │
    │   ├─► Check: if "marketplace_sample_plugin" in self.plugins
    │   │   └─► Yes: logger.warning("Plugin %s already loaded; replacing")
    │   │   └─► No: (proceed)
    │   │
    │   ├─► self.plugins["marketplace_sample_plugin"] = plugin
    │   │
    │   └─► plugin.enable()
    │       ├─► self.enabled = True
    │       └─► return True
    │
    └─► Return: True (plugin enabled)
```

### Integration with Other Systems

#### FourLaws Integration (Manual)

System A does NOT enforce FourLaws automatically. Plugin authors must call manually:

```python
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

**Contrast with System B:** PluginInterface can enforce validation in `PluginRegistry.execute_plugin()`.

#### Observability Integration

Plugins can emit telemetry events:

```python
from app.core.observability import emit_event

class ObservablePlugin(Plugin):
    def enable(self) -> bool:
        self.enabled = True
        emit_event("plugin.enabled", {
            "name": self.name,
            "version": self.version
        })
        return True
```

#### GUI Integration (Future)

PersonaPanel could add plugin configuration:

```python
# gui/persona_panel.py (future)
def setup_plugin_tab(self):
    for name, plugin in plugin_manager.plugins.items():
        checkbox = QCheckBox(f"{name} ({plugin.version})")
        checkbox.setChecked(plugin.enabled)
        checkbox.toggled.connect(
            lambda checked, p=plugin: p.enable() if checked else p.disable()
        )
        self.plugin_layout.addWidget(checkbox)
```

---

## 5. WHY: Design Decisions & Rationale

### Why Simple Plugin System?

**Decision:** Create lightweight Plugin base class + PluginManager registry

**Rationale:**
1. **Minimize Overhead:** Simple use cases don't need full PluginInterface complexity
2. **Quick Prototyping:** Plugin authors can create minimal plugins in minutes
3. **In-Memory Only:** No persistence needed for ephemeral plugins
4. **No External Deps:** Runs entirely in Python stdlib (no subprocess, multiprocessing)

**Trade-offs:**
- ✅ **Pros:** Fast, simple, easy to understand
- ❌ **Cons:** No sandboxing, no persistence, vulnerable to malicious code

### Why No Sandboxing?

**Decision:** Plugins run in main process without isolation

**Rationale:**
- System A targets **trusted internal plugins** only
- Process isolation adds complexity (use System C/D for untrusted plugins)
- Performance: No IPC overhead

**Mitigation:**
- Document trust requirement prominently
- Provide System C/D for untrusted plugins
- Future: Add capability manifest checks

### Why Replace on Duplicate?

**Decision:** `load_plugin()` replaces existing plugin with same name

**Rationale:**
- Allows plugin hot-swap during development
- Warns user (logged at WARNING level)
- Prevents registry corruption (no duplicate keys)

**Alternative Considered:**
- Raise error on duplicate → Rejected (too strict for dev workflow)

### Why No Auto-Discovery?

**Decision:** Plugins must be manually instantiated and loaded

**Rationale:**
- System A is minimal (discovery adds complexity)
- Manual loading gives full control over plugin order
- See System B + PluginRunner for auto-discovery patterns

---

## 6. HOW: Implementation Details & Patterns

### Plugin Implementation Pattern

```python
from app.core.ai_systems import Plugin, FourLaws

class MyPlugin(Plugin):
    def __init__(self):
        super().__init__("my_plugin", "1.0.0")
        self.config = {}
    
    def initialize(self, context: dict) -> bool:
        # 1. Validate against FourLaws (manual)
        allowed, reason = FourLaws.validate_action(
            "Initialize my_plugin",
            context=context
        )
        if not allowed:
            logger.error("Plugin blocked: %s", reason)
            return False
        
        # 2. Load config
        self.config = context.get("config", {})
        
        # 3. Enable plugin
        self.enabled = True
        return True
    
    def process(self, data: str) -> str:
        """Custom plugin logic."""
        if not self.enabled:
            return data
        
        # Transform data
        return data.upper()
```

### Manager Usage Pattern

```python
from app.core.ai_systems import PluginManager

# Initialize manager
manager = PluginManager(plugins_dir="data/plugins")

# Load plugins
plugin1 = MyPlugin()
plugin1.initialize(context={"config": {"mode": "strict"}})
manager.load_plugin(plugin1)

# Check stats
stats = manager.get_statistics()
print(f"Total: {stats['total']}, Enabled: {stats['enabled']}")
# Output: Total: 1, Enabled: 1

# Use plugin
if manager.plugins["my_plugin"].enabled:
    result = manager.plugins["my_plugin"].process("hello")
    print(result)  # "HELLO"

# Disable plugin
manager.plugins["my_plugin"].disable()

# Stats updated
stats = manager.get_statistics()
print(f"Total: {stats['total']}, Enabled: {stats['enabled']}")
# Output: Total: 1, Enabled: 0
```

### Testing Pattern

```python
import pytest
import tempfile
from app.core.ai_systems import Plugin, PluginManager

def test_plugin_lifecycle():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = PluginManager(plugins_dir=tmpdir)
        plugin = Plugin("test_plugin", "1.0.0")
        
        # Act
        assert manager.load_plugin(plugin) is True
        
        # Assert
        assert plugin.enabled is True
        assert "test_plugin" in manager.plugins
        stats = manager.get_statistics()
        assert stats["total"] == 1
        assert stats["enabled"] == 1
        
        # Act: Disable
        plugin.disable()
        
        # Assert
        stats = manager.get_statistics()
        assert stats["enabled"] == 0

def test_duplicate_plugin_replacement():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = PluginManager(plugins_dir=tmpdir)
        plugin1 = Plugin("duplicate", "1.0.0")
        plugin2 = Plugin("duplicate", "2.0.0")
        
        # Act
        manager.load_plugin(plugin1)
        manager.load_plugin(plugin2)  # Should replace plugin1
        
        # Assert
        assert manager.plugins["duplicate"].version == "2.0.0"
        stats = manager.get_statistics()
        assert stats["total"] == 1  # Only 1 plugin (replaced)
```

---

## 7. Dependencies & Relationships

### Internal Dependencies

```
Plugin (base class)
    └─► No dependencies (standalone)

PluginManager
    ├─► Plugin (composition - stores Plugin instances)
    ├─► os.makedirs (filesystem)
    └─► logging (logger)

MarketplaceSamplePlugin (example)
    ├─► Plugin (inheritance)
    ├─► FourLaws (validation)
    └─► observability.emit_event (telemetry)
```

### Dependency Graph

```
┌────────────────────────────────────────────────────────┐
│                   Core Application                     │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────┐          ┌──────────────┐              │
│  │ FourLaws │◄─────────│ Plugin       │              │
│  └──────────┘ manual   │ (base class) │              │
│      △                 └──────┬───────┘              │
│      │                        │                       │
│      │ validates              │ inherits              │
│      │                        ▼                       │
│  ┌───┴────────────┐    ┌─────────────────────────┐  │
│  │ Plugin Authors │    │ MarketplaceSamplePlugin │  │
│  └────────────────┘    │ GraphAnalysisPlugin     │  │
│                        │ (subclasses)             │  │
│                        └────────┬─────────────────┘  │
│                                 │                     │
│                                 │ loaded by           │
│                                 ▼                     │
│                        ┌─────────────────┐           │
│                        │ PluginManager   │           │
│                        │ plugins: dict   │           │
│                        └─────────────────┘           │
│                                 │                     │
│                                 │ used by             │
│                                 ▼                     │
│                        ┌─────────────────┐           │
│                        │ Core Systems    │           │
│                        │ - GUI           │           │
│                        │ - Intelligence  │           │
│                        │ - Learning      │           │
│                        └─────────────────┘           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Relationship to Other Plugin Systems

| System | Relationship | Overlap |
|--------|-------------|---------|
| **System B (PluginInterface)** | Alternative | Both provide plugin loading, but B has ABC + registry execution |
| **System C (PluginRunner)** | Complementary | System C can wrap System A plugins for isolation |
| **System D (PluginIsolation)** | Complementary | System D can wrap System A plugins for hostile code |

**Recommendation:** Use System A for trusted internal plugins, System B for full-featured plugins, System C/D for untrusted plugins.

---

## 8. Security Considerations

### Threat Model

| Threat | Severity | Mitigation |
|--------|----------|------------|
| **Malicious code execution** | CRITICAL | None (in-process, no sandboxing) |
| **Resource exhaustion** | HIGH | None (no timeouts or limits) |
| **State corruption** | MEDIUM | In-memory only (restart clears) |
| **Privilege escalation** | HIGH | FourLaws validation (manual) |
| **Data exfiltration** | HIGH | None (filesystem/network access unrestricted) |

### Security Constraints

**System A is NOT SECURE for untrusted plugins:**

- ❌ No process isolation (runs in main process)
- ❌ No timeout enforcement (infinite loops possible)
- ❌ No resource limits (CPU, memory, I/O)
- ❌ No filesystem restrictions (can read/write anywhere)
- ❌ No network restrictions (can make HTTP requests)
- ❌ FourLaws validation optional (plugin author must call manually)

**Use Cases:**
- ✅ **SAFE:** Trusted internal plugins by core team
- ❌ **UNSAFE:** Marketplace plugins, community contributions, third-party vendors

**Recommendation:** For untrusted plugins, use:
- **System C (PluginRunner):** Subprocess isolation + timeout
- **System D (PluginIsolation):** Multiprocessing + memory isolation

### Best Practices

1. **Only load trusted plugins:**
   ```python
   # Good: Internal plugin
   plugin = InternalFeaturePlugin()
   manager.load_plugin(plugin)
   
   # Bad: External plugin without vetting
   plugin = download_from_marketplace("untrusted_plugin")  # DON'T DO THIS
   manager.load_plugin(plugin)  # SECURITY RISK
   ```

2. **Always call FourLaws validation:**
   ```python
   class SafePlugin(Plugin):
       def initialize(self, context: dict) -> bool:
           allowed, reason = FourLaws.validate_action(
               "Initialize plugin", context
           )
           if not allowed:
               return False  # Block unsafe actions
           self.enabled = True
           return True
   ```

3. **Monitor plugin statistics:**
   ```python
   stats = manager.get_statistics()
   if stats["enabled"] > expected_count:
       logger.warning("Unexpected plugins enabled: %d", stats["enabled"])
   ```

---

## 9. Testing Strategy

### Test Coverage

**File:** `tests/test_ai_systems.py` (lines 300-350)

**Scenarios Tested:**
1. Plugin initialization (name, version, enabled=False)
2. Enable/disable toggling
3. PluginManager loading
4. Duplicate plugin replacement (warning logged)
5. Statistics calculation (total vs. enabled)
6. Filesystem creation (plugins_dir)

### Example Test

```python
def test_plugin_manager_statistics(self):
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = PluginManager(plugins_dir=tmpdir)
        
        # No plugins
        stats = manager.get_statistics()
        assert stats["total"] == 0
        assert stats["enabled"] == 0
        
        # Add plugins
        p1 = Plugin("p1")
        p2 = Plugin("p2")
        manager.load_plugin(p1)
        manager.load_plugin(p2)
        
        # Both enabled
        stats = manager.get_statistics()
        assert stats["total"] == 2
        assert stats["enabled"] == 2
        
        # Disable one
        p1.disable()
        stats = manager.get_statistics()
        assert stats["total"] == 2
        assert stats["enabled"] == 1
```

### Test Data

```python
# Minimal plugin
class MinimalPlugin(Plugin):
    def __init__(self):
        super().__init__("minimal", "1.0.0")

# Plugin with initialization
class ConfigurablePlugin(Plugin):
    def initialize(self, context: dict) -> bool:
        self.config = context.get("config", {})
        return super().initialize(context)
```

---

## 10. Evolution & Roadmap

### Known Limitations

1. **No Persistence:** Plugin state lost on restart
2. **No Auto-Discovery:** Plugins must be manually loaded
3. **No Sandboxing:** Vulnerable to malicious code
4. **No Versioning:** No compatibility checks
5. **No Dependencies:** Plugins cannot declare dependencies

### Future Enhancements

#### Phase 1: Persistence

```python
class PluginManager:
    def save_state(self):
        """Save plugin enabled/disabled state to JSON."""
        state = {
            name: plugin.enabled
            for name, plugin in self.plugins.items()
        }
        with open(f"{self.plugins_dir}/state.json", "w") as f:
            json.dump(state, f)
    
    def load_state(self):
        """Restore plugin state from JSON."""
        state_file = f"{self.plugins_dir}/state.json"
        if os.path.exists(state_file):
            with open(state_file) as f:
                state = json.load(f)
            for name, enabled in state.items():
                if name in self.plugins:
                    if enabled:
                        self.plugins[name].enable()
                    else:
                        self.plugins[name].disable()
```

#### Phase 2: Auto-Discovery

```python
class PluginManager:
    def discover_plugins(self):
        """Auto-discover plugins from plugins_dir."""
        for file in Path(self.plugins_dir).glob("*.py"):
            spec = importlib.util.spec_from_file_location(file.stem, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for Plugin subclasses
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Plugin) and obj is not Plugin:
                    plugin = obj()
                    self.load_plugin(plugin)
```

#### Phase 3: Integration with System B

Unify with PluginInterface system:

```python
class UnifiedPlugin(Plugin, PluginInterface):
    """Plugin supporting both System A and System B APIs."""
    
    def get_name(self) -> str:
        return self.name
    
    def get_version(self) -> str:
        return self.version
    
    def execute(self, context: dict) -> dict:
        # PluginInterface execution logic
        pass
```

---

## 11. References

### Internal Documentation

- **Architecture:** `source-docs/plugins/01-plugin-architecture-overview.md`
- **API Reference:** `source-docs/plugins/02-plugin-api-reference.md`
- **Examples:** `source-docs/plugins/06-plugin-examples.md`

### Source Code

- **Plugin/PluginManager:** `src/app/core/ai_systems.py:991-1038`
- **Example Plugin:** `src/app/plugins/sample_plugin.py`
- **Tests:** `tests/test_ai_systems.py` (lines 300-350)

### Related Relationship Maps

- **PluginInterface:** `./02-Plugin-Interface-Relationship-Map.md`
- **Plugin Loading:** `./03-Plugin-Loading-Relationship-Map.md`
- **Plugin Lifecycle:** `./06-Plugin-Lifecycle-Relationship-Map.md`

---

**Created by:** AGENT-067 (Plugin System Relationship Mapping Specialist)  
**Status:** ✅ Complete  
**Next Review:** 2026-07-20
