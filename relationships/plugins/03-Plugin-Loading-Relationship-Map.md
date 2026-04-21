---
title: "Plugin Loading - Relationship Map"
agent: AGENT-067
mission: Plugin System Relationship Mapping
created: 2026-04-20
last_verified: 2026-04-20
status: Active
system: Plugin Loading & Discovery
source: src/app/plugins/plugin_runner.py, tests/plugins/test_plugin_load_flow.py
---

# Plugin Loading - Comprehensive Relationship Map

## Executive Summary

**Plugin Loading** encompasses the mechanisms for discovering, validating, and initializing plugins across all four plugin systems (A, B, C, D). This map documents the complete loading workflow from filesystem discovery to runtime initialization.

**Core Purpose:** Automate plugin discovery, manifest validation, dependency resolution, and safe loading into the plugin registry.

---

## 1. WHAT: Loading Mechanisms

### System A: Manual Loading

```python
# ai_systems.py - Manual instantiation required
manager = PluginManager(plugins_dir="plugins")
plugin = MarketplaceSamplePlugin()
manager.load_plugin(plugin)  # Direct registration
```

**Characteristics:**
- ❌ No auto-discovery
- ✅ Full control over load order
- ✅ Explicit dependency management
- ⚠️ Requires code changes to add plugins

### System B: Registry-Based Loading

```python
# interfaces.py - Manual registration with validation
registry = PluginRegistry()
plugin = GraphAnalysisPlugin()
registry.register(plugin)  # Validates + registers
```

**Characteristics:**
- ❌ No auto-discovery
- ✅ Duplicate prevention (ValueError)
- ✅ Abstract method enforcement (TypeError)
- ⚠️ Requires explicit registration calls

### System C: Subprocess Loading

```python
# plugin_runner.py - Script-based loading
runner = PluginRunner("path/to/plugin.py", timeout=5.0)
runner.start()  # subprocess.Popen
result = runner.call_init(params={"config": {...}})
```

**Characteristics:**
- ✅ Process isolation
- ✅ Timeout enforcement
- ✅ JSONL protocol validation
- ⚠️ Requires plugin script path

### Auto-Discovery Pattern (Future)

```python
def discover_plugins(plugins_dir: str) -> list[Plugin]:
    """Auto-discover plugins from directory."""
    discovered = []
    
    for file in Path(plugins_dir).glob("*.py"):
        # Import module
        spec = importlib.util.spec_from_file_location(file.stem, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find Plugin subclasses
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Plugin) and obj is not Plugin:
                try:
                    plugin = obj()  # Instantiate
                    discovered.append(plugin)
                except Exception as e:
                    logger.warning(f"Failed to load {name}: {e}")
    
    return discovered
```

---

## 2. Loading Workflow

### Complete Loading Sequence

```
1. Discovery
   ├─► Scan plugins directory for *.py files
   ├─► Parse plugin.json manifests (if present)
   └─► Build candidate list

2. Validation
   ├─► Check manifest schema
   ├─► Verify required fields (name, version, entry_point)
   ├─► Validate dependencies (all present?)
   └─► Security checks (capabilities, trust level)

3. Dependency Resolution
   ├─► Build dependency graph
   ├─► Topological sort (Kahn's algorithm)
   ├─► Detect circular dependencies
   └─► Determine load order

4. Initialization
   ├─► Import plugin module
   ├─► Instantiate plugin class
   ├─► Call plugin.initialize(context)
   └─► Validate initialization success

5. Registration
   ├─► Add to registry (PluginManager or PluginRegistry)
   ├─► Enable plugin (System A)
   ├─► Emit telemetry event
   └─► Update statistics

6. Post-Load Validation
   ├─► Verify all dependencies loaded
   ├─► Check for conflicts
   └─► Emit ready event
```

### State Machine

```
DISCOVERED → VALIDATED → DEPENDENCIES_RESOLVED → INITIALIZED → REGISTERED → READY
     │            │                │                    │             │
     ▼            ▼                ▼                    ▼             ▼
  INVALID   VALIDATION_FAILED   DEPENDENCY_MISSING   INIT_FAILED   REG_FAILED
```

---

## 3. Plugin Manifest Schema

### plugin.json Structure

```json
{
  "name": "graph_analysis_plugin",
  "version": "1.0.0",
  "description": "Network graph analysis and visualization",
  "author": "Project-AI Team",
  "entry_point": "graph_analysis_plugin.py",
  "class_name": "GraphAnalysisPlugin",
  
  "dependencies": {
    "plugins": [],  // Other plugins this depends on
    "packages": ["networkx>=3.0", "matplotlib>=3.5"]
  },
  
  "capabilities": [
    "graph_analysis",
    "data_visualization",
    "response_processing"
  ],
  
  "trust_level": 1,  // 0=trusted, 1=verified, 2=sandbox, 3=hostile
  
  "configuration": {
    "default_layout": "spring",
    "max_nodes": 1000,
    "timeout": 30
  },
  
  "metadata": {
    "homepage": "https://github.com/project-ai/plugins/graph-analysis",
    "documentation": "https://docs.project-ai.com/plugins/graph-analysis",
    "license": "MIT",
    "tags": ["graph", "visualization", "analysis"]
  }
}
```

### Manifest Validation

```python
def validate_manifest(manifest: dict) -> tuple[bool, str]:
    """Validate plugin manifest."""
    required_fields = ["name", "version", "entry_point"]
    
    # Check required fields
    for field in required_fields:
        if field not in manifest:
            return False, f"Missing required field: {field}"
    
    # Validate version format
    version = manifest["version"]
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"Invalid version format: {version}"
    
    # Validate trust level
    trust_level = manifest.get("trust_level", 0)
    if trust_level not in [0, 1, 2, 3]:
        return False, f"Invalid trust level: {trust_level}"
    
    # Validate capabilities
    capabilities = manifest.get("capabilities", [])
    if not isinstance(capabilities, list):
        return False, "Capabilities must be a list"
    
    return True, "Valid"
```

---

## 4. Dependency Resolution

### Dependency Graph Building

```python
class DependencyResolver:
    """Resolve plugin dependencies using topological sort."""
    
    def __init__(self):
        self.graph: dict[str, set[str]] = {}  # plugin -> dependencies
        self.reverse_graph: dict[str, set[str]] = {}  # dependency -> plugins
    
    def add_plugin(self, name: str, dependencies: list[str]):
        """Add plugin to dependency graph."""
        self.graph[name] = set(dependencies)
        
        # Build reverse graph
        for dep in dependencies:
            if dep not in self.reverse_graph:
                self.reverse_graph[dep] = set()
            self.reverse_graph[dep].add(name)
    
    def resolve(self) -> list[str]:
        """Return plugins in load order (topological sort)."""
        in_degree = {name: len(deps) for name, deps in self.graph.items()}
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            plugin = queue.pop(0)
            result.append(plugin)
            
            # Reduce in-degree for dependents
            for dependent in self.reverse_graph.get(plugin, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Check for circular dependencies
        if len(result) != len(self.graph):
            raise ValueError("Circular dependency detected")
        
        return result
    
    def detect_circular(self) -> list[str] | None:
        """Detect circular dependencies."""
        visited = set()
        rec_stack = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.graph:
            if node not in visited:
                if dfs(node):
                    return list(rec_stack)
        
        return None
```

### Example Dependency Resolution

```python
# Example: Plugin dependencies
plugins = {
    "plugin_a": [],  # No dependencies
    "plugin_b": ["plugin_a"],  # Depends on A
    "plugin_c": ["plugin_a", "plugin_b"],  # Depends on A and B
    "plugin_d": ["plugin_c"]  # Depends on C
}

resolver = DependencyResolver()
for name, deps in plugins.items():
    resolver.add_plugin(name, deps)

# Resolve load order
load_order = resolver.resolve()
# Result: ["plugin_a", "plugin_b", "plugin_c", "plugin_d"]

# Detect circular dependencies
plugins_circular = {
    "plugin_x": ["plugin_y"],
    "plugin_y": ["plugin_z"],
    "plugin_z": ["plugin_x"]  # Circular!
}

resolver2 = DependencyResolver()
for name, deps in plugins_circular.items():
    resolver2.add_plugin(name, deps)

circular = resolver2.detect_circular()
# Result: ["plugin_x", "plugin_y", "plugin_z"]
```

---

## 5. PluginRunner Loading (System C)

### Subprocess Initialization

```python
class PluginRunner:
    """Execute plugins in isolated subprocess."""
    
    def __init__(self, plugin_script: str, timeout: float = 5.0):
        self.plugin_script = Path(plugin_script)
        self.timeout = timeout
        self.proc: subprocess.Popen | None = None
    
    def start(self) -> None:
        """Start plugin subprocess."""
        if not self.plugin_script.exists():
            raise FileNotFoundError(f"Plugin script not found: {self.plugin_script}")
        
        cmd = [sys.executable, str(self.plugin_script)]
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
    
    def call_init(self, params: dict[str, Any]) -> dict[str, Any]:
        """Send init message to plugin."""
        if not self.proc:
            self.start()
        
        # Send JSONL message
        msg = {"id": "init-1", "method": "init", "params": params}
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        
        # Wait for response
        start = time.time()
        while time.time() - start < self.timeout:
            line = self._readline_nonblocking(timeout=0.1)
            if line:
                try:
                    obj = json.loads(line)
                    if obj.get("id") == msg["id"]:
                        return obj
                except Exception:
                    continue
        
        raise TimeoutError("Plugin did not respond to init within timeout")
```

### JSONL Protocol

```
Host → Plugin (stdin):
{"id": "init-1", "method": "init", "params": {"config": {...}}}

Plugin → Host (stdout):
{"id": "init-1", "result": {"status": "initialized", "version": "1.0.0"}}

OR (on error):
{"id": "init-1", "error": "Initialization failed: missing config"}
```

---

## 6. Integration with Core Systems

### GUI Integration (Future)

```python
class PluginLoaderPanel(QWidget):
    """GUI for plugin discovery and loading."""
    
    def __init__(self, registry: PluginRegistry):
        super().__init__()
        self.registry = registry
        self.setup_ui()
    
    def discover_plugins(self):
        """Scan plugins directory and populate UI."""
        plugins_dir = Path("plugins")
        discovered = []
        
        for manifest_file in plugins_dir.glob("**/plugin.json"):
            with open(manifest_file) as f:
                manifest = json.load(f)
            
            valid, reason = validate_manifest(manifest)
            discovered.append({
                "manifest": manifest,
                "valid": valid,
                "reason": reason,
                "path": manifest_file.parent
            })
        
        self.populate_plugin_list(discovered)
    
    def load_plugin(self, manifest: dict, path: Path):
        """Load plugin from manifest."""
        try:
            # Import plugin module
            entry_point = path / manifest["entry_point"]
            spec = importlib.util.spec_from_file_location(
                manifest["name"], entry_point
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get plugin class
            class_name = manifest.get("class_name", "Plugin")
            plugin_class = getattr(module, class_name)
            
            # Instantiate and register
            plugin = plugin_class()
            self.registry.register(plugin)
            
            QMessageBox.information(
                self, "Success", f"Loaded plugin: {manifest['name']}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load plugin: {e}"
            )
```

---

## 7. Testing Strategy

### Test Coverage

**File:** `tests/plugins/test_plugin_load_flow.py`

```python
def test_plugin_discovery():
    """Test auto-discovery of plugins."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test plugin
        plugin_dir = Path(tmpdir) / "test_plugin"
        plugin_dir.mkdir()
        
        # Write manifest
        manifest = {
            "name": "test_plugin",
            "version": "1.0.0",
            "entry_point": "plugin.py",
            "class_name": "TestPlugin"
        }
        with open(plugin_dir / "plugin.json", "w") as f:
            json.dump(manifest, f)
        
        # Write plugin code
        plugin_code = '''
from app.core.interfaces import PluginInterface

class TestPlugin(PluginInterface):
    def get_name(self) -> str:
        return "test_plugin"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def execute(self, context: dict) -> dict:
        return {"status": "success"}
'''
        with open(plugin_dir / "plugin.py", "w") as f:
            f.write(plugin_code)
        
        # Discover
        discovered = discover_plugins(tmpdir)
        assert len(discovered) == 1
        assert discovered[0].get_name() == "test_plugin"

def test_dependency_resolution():
    """Test topological sort of plugin dependencies."""
    resolver = DependencyResolver()
    resolver.add_plugin("a", [])
    resolver.add_plugin("b", ["a"])
    resolver.add_plugin("c", ["a", "b"])
    
    load_order = resolver.resolve()
    
    assert load_order.index("a") < load_order.index("b")
    assert load_order.index("b") < load_order.index("c")

def test_circular_dependency_detection():
    """Test detection of circular dependencies."""
    resolver = DependencyResolver()
    resolver.add_plugin("x", ["y"])
    resolver.add_plugin("y", ["z"])
    resolver.add_plugin("z", ["x"])
    
    with pytest.raises(ValueError, match="Circular dependency detected"):
        resolver.resolve()
```

---

## 8. Evolution & Roadmap

### Phase 1: Auto-Discovery (In Progress)

- Implement `discover_plugins()` for System A/B
- Add manifest parsing and validation
- Create GUI for plugin management

### Phase 2: Dependency Management

- Implement DependencyResolver
- Add topological sort to load order
- Detect and report circular dependencies

### Phase 3: Hot-Reload

```python
class HotReloadManager:
    """Support hot-reloading of plugins without restart."""
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.file_watchers: dict[str, FileWatcher] = {}
    
    def watch(self, plugin_name: str, file_path: Path):
        """Watch plugin file for changes."""
        watcher = FileWatcher(file_path)
        watcher.on_modified.connect(lambda: self.reload_plugin(plugin_name))
        self.file_watchers[plugin_name] = watcher
    
    def reload_plugin(self, plugin_name: str):
        """Reload plugin from disk."""
        # Unregister old version
        self.registry.unregister(plugin_name)
        
        # Re-import module (invalidate cache)
        importlib.invalidate_caches()
        
        # Re-register new version
        # (implementation details...)
```

---

## 9. References

### Internal Documentation

- **Architecture:** `source-docs/plugins/01-plugin-architecture-overview.md`
- **Lifecycle:** `source-docs/plugins/03-plugin-loading-lifecycle.md`

### Source Code

- **PluginRunner:** `src/app/plugins/plugin_runner.py`
- **Tests:** `tests/plugins/test_plugin_load_flow.py`

### Related Maps

- **Plugin Manager:** `./01-Plugin-Manager-Relationship-Map.md`
- **Plugin Interface:** `./02-Plugin-Interface-Relationship-Map.md`
- **Plugin Dependencies:** `./05-Plugin-Dependencies-Relationship-Map.md`

---

**Created by:** AGENT-067  
**Status:** ✅ Complete  
**Next Review:** 2026-07-20
