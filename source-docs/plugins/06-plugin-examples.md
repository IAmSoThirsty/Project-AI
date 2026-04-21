---
type: examples
examples_type: code-samples
area: plugin-system
audience: [developer]
prerequisites:
  - 05-plugin-development-guide.md
  - 02-plugin-api-reference.md
tags:
  - plugin/examples
  - code-samples
  - patterns
related_docs:
  - 05-plugin-development-guide.md
  - 07-plugin-extensibility-patterns.md
last_updated: 2026-04-20
version: 1.0.0
---

# Plugin Examples

**Real-world plugin implementations and design patterns**  
**Version:** 1.0.0  
**Last Updated:** 2026-04-20

---

## Table of Contents

1. [Excalidraw Plugin](#excalidraw-plugin)
2. [Graph Analysis Plugin](#graph-analysis-plugin)
3. [Marketplace Sample Plugin](#marketplace-sample-plugin)
4. [Custom Plugin Patterns](#custom-plugin-patterns)
5. [Advanced Examples](#advanced-examples)

---

## Excalidraw Plugin

**Source:** `src/app/plugins/excalidraw_plugin.py`

### Overview

The Excalidraw plugin provides visual diagramming capabilities, integrating with the Excalidraw web application for creating hand-drawn style diagrams.

### Key Features

- ✅ Diagram creation and metadata tracking
- ✅ File persistence with JSON storage
- ✅ Export tracking (PNG, SVG, JSON)
- ✅ Browser integration for diagram editing
- ✅ Configuration management
- ✅ Four Laws validation

### Architecture

```
ExcalidrawPlugin
├── Data Storage (data/excalidraw_diagrams/)
│   ├── config.json          # Plugin configuration
│   ├── metadata.json        # Diagram metadata
│   └── *.excalidraw         # Diagram files
├── Methods
│   ├── initialize()         # Four Laws check + setup
│   ├── create_diagram()     # New diagram entry
│   ├── save_diagram()       # Persist diagram content
│   ├── load_diagram()       # Load diagram from disk
│   ├── open_excalidraw()    # Open web interface
│   └── export_diagram()     # Track exports
└── Telemetry
    ├── plugin.excalidraw.initialized
    ├── plugin.excalidraw.diagram_created
    └── plugin.excalidraw.browser_opened
```

### Implementation Highlights

#### 1. Initialization with Four Laws

```python
def initialize(self, context: dict[str, Any] | None = None) -> bool:
    """Initialize plugin with safety validation."""
    context = context or {}
    
    # Validate against Four Laws
    allowed, reason = FourLaws.validate_action(
        "Initialize Excalidraw visual diagramming plugin",
        context,
    )
    
    if not allowed:
        logger.warning("Excalidraw plugin blocked: %s", reason)
        emit_event("plugin.excalidraw.blocked", {"reason": reason})
        return False
    
    # Enable plugin
    self.enabled = True
    
    # Update metadata
    self.metadata["last_accessed"] = datetime.now().isoformat()
    self._save_metadata()
    
    emit_event("plugin.excalidraw.initialized", {
        "name": self.name,
        "version": self.version,
        "diagrams_count": len(self.metadata["diagrams"]),
    })
    
    return True
```

#### 2. Diagram Creation with Metadata

```python
def create_diagram(self, name: str, description: str = "") -> dict[str, Any]:
    """Create a new diagram entry."""
    if not self.enabled:
        raise RuntimeError("Excalidraw plugin not enabled")
    
    # Generate unique ID with timestamp
    diagram_id = f"diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create diagram metadata
    diagram_data = {
        "id": diagram_id,
        "name": name,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "modified_at": datetime.now().isoformat(),
        "file_path": str(self.diagrams_dir / f"{diagram_id}.excalidraw"),
        "exports": [],
    }
    
    # Track in metadata
    self.metadata["diagrams"].append(diagram_data)
    self.metadata["total_created"] += 1
    self._save_metadata()
    
    emit_event("plugin.excalidraw.diagram_created", {"diagram": diagram_data})
    
    return diagram_data
```

#### 3. Persistent Configuration

```python
def _load_config(self) -> None:
    """Load configuration from disk."""
    if self.config_file.exists():
        try:
            with open(self.config_file, encoding="utf-8") as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
            logger.info("Loaded Excalidraw configuration")
        except Exception as e:
            logger.error("Failed to load Excalidraw config: %s", e)

def _save_config(self) -> None:
    """Save configuration to disk."""
    try:
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)
        logger.debug("Saved Excalidraw configuration")
    except Exception as e:
        logger.error("Failed to save Excalidraw config: %s", e)
```

#### 4. Browser Integration

```python
def open_excalidraw(self) -> bool:
    """Open Excalidraw web interface in default browser."""
    if not self.enabled:
        raise RuntimeError("Excalidraw plugin not enabled")
    
    try:
        webbrowser.open(self.EXCALIDRAW_URL)
        logger.info("Opened Excalidraw in browser: %s", self.EXCALIDRAW_URL)
        emit_event("plugin.excalidraw.browser_opened", {
            "url": self.EXCALIDRAW_URL
        })
        return True
    except Exception as e:
        logger.error("Failed to open Excalidraw: %s", e)
        return False
```

### Usage Example

```python
from app.plugins.excalidraw_plugin import ExcalidrawPlugin

# Initialize plugin
plugin = ExcalidrawPlugin(data_dir="data")
success = plugin.initialize({
    "is_user_order": True,
    "harms_human": False
})

if success:
    # Create diagram
    diagram = plugin.create_diagram(
        name="System Architecture",
        description="High-level system architecture diagram"
    )
    print(f"Created diagram: {diagram['id']}")
    
    # Save diagram content
    diagram_content = '{"elements":[],"appState":{}}'  # Excalidraw JSON
    plugin.save_diagram(diagram["id"], diagram_content)
    
    # Open in browser for editing
    plugin.open_excalidraw()
    
    # List all diagrams
    diagrams = plugin.list_diagrams()
    print(f"Total diagrams: {len(diagrams)}")
    
    # Get statistics
    stats = plugin.get_statistics()
    print(f"Stats: {stats}")
```

### Key Takeaways

- ✅ **Persistent metadata** - All diagram info saved to JSON
- ✅ **Four Laws integration** - Safety validation before initialization
- ✅ **Telemetry** - Events emitted for observability
- ✅ **Error handling** - Try/except blocks with logging
- ✅ **Browser integration** - Opens web UI for diagram editing

---

## Graph Analysis Plugin

**Source:** `src/app/plugins/graph_analysis_plugin.py`

### Overview

Sophisticated plugin for analyzing codebase structure using graph algorithms, providing insights into module dependencies, complexity, and code organization.

### Key Features

- ✅ Dependency graph analysis
- ✅ Cyclic dependency detection
- ✅ Centrality analysis (identify critical modules)
- ✅ Module clustering
- ✅ Comprehensive metrics (complexity, coupling, cohesion)
- ✅ JSON report generation

### Architecture

```
GraphAnalysisPlugin (PluginInterface)
├── Initialization
│   ├── Load configuration (graph_analysis_config.json)
│   ├── Initialize NetworkX graph
│   └── Setup metrics tracking
├── Graph Building
│   ├── scan_directory() - Walk file tree
│   ├── analyze_file() - Parse imports
│   └── build_dependency_graph() - Create graph
├── Analysis Algorithms
│   ├── find_cycles() - Detect circular dependencies
│   ├── calculate_centrality() - PageRank/betweenness
│   ├── detect_clusters() - Community detection
│   └── calculate_complexity() - Complexity metrics
└── Reporting
    ├── generate_report() - JSON report
    ├── visualize_graph() - Optional visualization
    └── export_metrics() - Metrics export
```

### Implementation Highlights

#### 1. Dependency Graph Construction

```python
def build_dependency_graph(self, root_dir: str) -> nx.DiGraph:
    """Build dependency graph from source files.
    
    Creates a directed graph where:
    - Nodes: Python modules/files
    - Edges: Import relationships (A imports B)
    """
    graph = nx.DiGraph()
    
    # Scan all Python files
    for file_path in Path(root_dir).rglob("*.py"):
        module = self._file_to_module(file_path, root_dir)
        graph.add_node(module, path=str(file_path))
        
        # Parse imports from file
        imports = self._extract_imports(file_path)
        for imported_module in imports:
            graph.add_edge(module, imported_module)
    
    return graph
```

#### 2. Cyclic Dependency Detection

```python
def find_cycles(self, graph: nx.DiGraph) -> list[list[str]]:
    """Find all cyclic dependencies in the graph.
    
    Returns:
        List of cycles, where each cycle is a list of module names
    """
    try:
        # NetworkX's cycle detection
        cycles = list(nx.simple_cycles(graph))
        
        # Filter out trivial cycles (self-imports)
        significant_cycles = [
            cycle for cycle in cycles if len(cycle) > 1
        ]
        
        return significant_cycles
    except Exception as e:
        logger.error("Cycle detection failed: %s", e)
        return []
```

#### 3. Centrality Analysis

```python
def calculate_centrality(self, graph: nx.DiGraph) -> dict[str, float]:
    """Calculate module centrality (importance in graph).
    
    Uses PageRank algorithm to identify critical modules that are
    heavily imported by other modules.
    
    Returns:
        Dictionary mapping module name to centrality score (0.0-1.0)
    """
    try:
        # PageRank centrality
        centrality = nx.pagerank(graph)
        
        # Sort by centrality score
        sorted_centrality = dict(
            sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        )
        
        return sorted_centrality
    except Exception as e:
        logger.error("Centrality calculation failed: %s", e)
        return {}
```

#### 4. Clustering Analysis

```python
def detect_clusters(self, graph: nx.DiGraph) -> dict[str, int]:
    """Detect module clusters using community detection.
    
    Groups related modules into clusters based on import patterns.
    
    Returns:
        Dictionary mapping module name to cluster ID
    """
    try:
        # Convert to undirected for community detection
        undirected = graph.to_undirected()
        
        # Louvain community detection
        import community as community_louvain
        clusters = community_louvain.best_partition(undirected)
        
        return clusters
    except ImportError:
        logger.warning("python-louvain not installed, using greedy")
        # Fallback to greedy modularity
        communities = nx.community.greedy_modularity_communities(
            graph.to_undirected()
        )
        
        # Convert to cluster mapping
        clusters = {}
        for i, community in enumerate(communities):
            for node in community:
                clusters[node] = i
        
        return clusters
```

#### 5. Comprehensive Report Generation

```python
def generate_report(self, graph: nx.DiGraph) -> dict[str, Any]:
    """Generate comprehensive analysis report.
    
    Returns:
        Dictionary with analysis results:
        - overview: Basic graph statistics
        - cycles: Cyclic dependencies
        - centrality: Module importance scores
        - clusters: Module groupings
        - metrics: Complexity/coupling metrics
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "overview": {
            "total_modules": graph.number_of_nodes(),
            "total_dependencies": graph.number_of_edges(),
            "average_dependencies": (
                graph.number_of_edges() / graph.number_of_nodes()
                if graph.number_of_nodes() > 0 else 0
            ),
        },
        "cycles": self.find_cycles(graph),
        "centrality": self.calculate_centrality(graph),
        "clusters": self.detect_clusters(graph),
        "metrics": self.calculate_metrics(graph),
    }
    
    return report
```

### Usage Example

```python
from app.core.interfaces import PluginRegistry
from app.plugins.graph_analysis_plugin import GraphAnalysisPlugin

# Register plugin
registry = PluginRegistry()
plugin = GraphAnalysisPlugin()
registry.register(plugin)

# Analyze codebase
result = registry.execute_plugin(
    "graph_analysis",
    context={
        "action": "analyze",
        "root_dir": "src/app",
        "output_file": "reports/graph_analysis.json"
    }
)

if result["status"] == "success":
    report = result["report"]
    
    # Print overview
    print(f"Total modules: {report['overview']['total_modules']}")
    print(f"Total dependencies: {report['overview']['total_dependencies']}")
    
    # Print cyclic dependencies
    if report["cycles"]:
        print("\nCyclic dependencies found:")
        for cycle in report["cycles"]:
            print(f"  {' -> '.join(cycle)}")
    
    # Print top 5 most central modules
    print("\nMost critical modules:")
    for module, score in list(report["centrality"].items())[:5]:
        print(f"  {module}: {score:.4f}")
```

### Key Takeaways

- ✅ **NetworkX integration** - Powerful graph algorithms
- ✅ **Multiple analysis types** - Cycles, centrality, clustering
- ✅ **Detailed metrics** - Complexity, coupling, cohesion
- ✅ **JSON reports** - Machine-readable output
- ✅ **Error handling** - Graceful degradation on missing dependencies

---

## Marketplace Sample Plugin

**Source:** `src/app/plugins/sample_plugin.py`

### Overview

Minimal plugin demonstrating marketplace integration, Four Laws validation, and telemetry.

### Implementation

```python
"""Sample marketplace plugin demonstrating metadata and safety checks."""

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


class MarketplaceSamplePlugin(Plugin):
    """A minimal plugin that shows how to validate actions against Four Laws."""
    
    def __init__(self) -> None:
        super().__init__(name="marketplace_sample_plugin", version="0.1.0")
    
    def _report_event(self, context: dict[str, Any]) -> None:
        emit_event(
            "plugin.marketplace_sample.initialize",
            {"name": self.name, "version": self.version, "context": context},
        )
    
    def initialize(self, context: dict[str, Any] | None = None) -> bool:
        """Validate context, emit telemetry, and enable plugin if allowed."""
        context = context or {}
        
        # Validate against Four Laws
        allowed, reason = FourLaws.validate_action(
            "Initialize marketplace sample plugin",
            context,
        )
        logger.info("Sample plugin validation result: %s", reason)
        
        if not allowed:
            emit_event("plugin.marketplace_sample.blocked", {"reason": reason})
            return False
        
        # Check explicit order requirement
        if context.get("requires_explicit_order") and not context.get("is_user_order"):
            emit_event(
                "plugin.marketplace_sample.blocked",
                {"reason": "requires_explicit_order without user order"},
            )
            return False
        
        # Enable plugin
        self.enabled = True
        self._report_event(context)
        return True


def initialize(context: dict[str, Any] | None = None) -> bool:
    """Entry point used by loaders that expect a plain function."""
    return MarketplaceSamplePlugin().initialize(context)
```

### Plugin Manifest

**File:** `src/app/plugins/plugin.json`

```json
{
  "name": "marketplace_sample_plugin",
  "version": "0.1.0",
  "author": "Project-AI Team",
  "description": "Demonstrates how to validate Four Laws before enabling a plugin",
  "hooks": ["before_action"],
  "four_laws_safe": true,
  "safe_for_learning": false
}
```

### Usage

```python
from app.plugins.sample_plugin import MarketplaceSamplePlugin

# Create plugin
plugin = MarketplaceSamplePlugin()

# Initialize with Four Laws context
success = plugin.initialize({
    "is_user_order": True,
    "harms_human": False,
    "requires_explicit_order": True
})

print(f"Plugin enabled: {plugin.enabled}")  # True
```

### Key Takeaways

- ✅ **Minimal implementation** - Shows essential patterns
- ✅ **Four Laws validation** - Security first
- ✅ **Telemetry** - Emit events on block/success
- ✅ **Entry point function** - `initialize()` for loaders

---

## Custom Plugin Patterns

### Pattern 1: Data Processing Pipeline

```python
from app.core.interfaces import PluginInterface
from typing import Any, Callable

class PipelinePlugin(PluginInterface):
    """Plugin that processes data through a pipeline of transformations."""
    
    def __init__(self):
        self.pipeline: list[Callable] = []
    
    def get_name(self) -> str:
        return "pipeline_processor"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def add_stage(self, transform: Callable[[Any], Any]) -> None:
        """Add transformation stage to pipeline."""
        self.pipeline.append(transform)
    
    def execute(self, context: dict) -> dict:
        """Execute pipeline on input data."""
        data = context["data"]
        
        # Run through pipeline
        for stage in self.pipeline:
            try:
                data = stage(data)
            except Exception as e:
                return {
                    "status": "error",
                    "error": f"Pipeline stage failed: {e}"
                }
        
        return {"status": "success", "result": data}
    
    def validate_context(self, context: dict) -> bool:
        return "data" in context
    
    def get_metadata(self) -> dict:
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "stages": len(self.pipeline)
        }

# Usage
plugin = PipelinePlugin()
plugin.add_stage(lambda x: [i * 2 for i in x])  # Double
plugin.add_stage(lambda x: [i + 1 for i in x])  # Increment
plugin.add_stage(lambda x: sum(x))               # Sum

result = plugin.execute({"data": [1, 2, 3, 4, 5]})
print(result)  # {"status": "success", "result": 41}
```

### Pattern 2: Async HTTP Plugin

```python
import asyncio
import aiohttp
from app.core.interfaces import PluginInterface

class AsyncHTTPPlugin(PluginInterface):
    """Plugin for making async HTTP requests."""
    
    def get_name(self) -> str:
        return "async_http"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    async def fetch_async(self, url: str) -> dict:
        """Fetch URL asynchronously."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return {
                    "status": response.status,
                    "content": await response.text()
                }
    
    def execute(self, context: dict) -> dict:
        """Execute async request synchronously."""
        url = context["url"]
        
        try:
            result = asyncio.run(self.fetch_async(url))
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def validate_context(self, context: dict) -> bool:
        return "url" in context and isinstance(context["url"], str)
    
    def get_metadata(self) -> dict:
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "capabilities": ["http_get", "async"]
        }

# Usage
plugin = AsyncHTTPPlugin()
result = plugin.execute({"url": "https://api.example.com/data"})
```

### Pattern 3: Database Plugin with Connection Pooling

```python
import sqlite3
from contextlib import contextmanager
from app.core.interfaces import PluginInterface

class DatabasePlugin(PluginInterface):
    """Plugin with database connection pooling."""
    
    def __init__(self, db_path: str = "data/plugins.db"):
        self.db_path = db_path
        self.connection = None
    
    def get_name(self) -> str:
        return "database"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def initialize(self) -> None:
        """Initialize database connection."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS plugin_data (
                key TEXT PRIMARY KEY,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()
    
    def shutdown(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        try:
            yield self.connection
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
    
    def execute(self, context: dict) -> dict:
        """Execute database operation."""
        operation = context["operation"]
        
        if operation == "set":
            with self.transaction() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO plugin_data (key, value) VALUES (?, ?)",
                    (context["key"], context["value"])
                )
            return {"status": "success"}
        
        elif operation == "get":
            cursor = self.connection.execute(
                "SELECT value FROM plugin_data WHERE key = ?",
                (context["key"],)
            )
            row = cursor.fetchone()
            return {
                "status": "success",
                "value": row[0] if row else None
            }
        
        else:
            return {"status": "error", "error": "Unknown operation"}
    
    def validate_context(self, context: dict) -> bool:
        return "operation" in context
    
    def get_metadata(self) -> dict:
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "capabilities": ["set", "get"],
            "database": self.db_path
        }

# Usage
plugin = DatabasePlugin()
plugin.initialize()

plugin.execute({"operation": "set", "key": "foo", "value": "bar"})
result = plugin.execute({"operation": "get", "key": "foo"})
print(result["value"])  # "bar"

plugin.shutdown()
```

### Pattern 4: Caching Plugin

```python
import time
from functools import wraps
from app.core.interfaces import PluginInterface

class CachingPlugin(PluginInterface):
    """Plugin with TTL-based caching."""
    
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl  # Time to live in seconds
    
    def get_name(self) -> str:
        return "caching"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def _cache_key(self, context: dict) -> str:
        """Generate cache key from context."""
        return str(sorted(context.items()))
    
    def _is_expired(self, timestamp: float) -> bool:
        """Check if cache entry is expired."""
        return time.time() - timestamp > self.ttl
    
    def execute(self, context: dict) -> dict:
        """Execute with caching."""
        operation = context.get("operation")
        
        if operation == "set":
            key = context["key"]
            value = context["value"]
            self.cache[key] = {
                "value": value,
                "timestamp": time.time()
            }
            return {"status": "success"}
        
        elif operation == "get":
            key = context["key"]
            if key in self.cache:
                entry = self.cache[key]
                if not self._is_expired(entry["timestamp"]):
                    return {
                        "status": "success",
                        "value": entry["value"],
                        "from_cache": True
                    }
                else:
                    # Expired, remove from cache
                    del self.cache[key]
            
            return {"status": "success", "value": None, "from_cache": False}
        
        elif operation == "clear":
            self.cache.clear()
            return {"status": "success"}
        
        else:
            return {"status": "error", "error": "Unknown operation"}
    
    def validate_context(self, context: dict) -> bool:
        return "operation" in context
    
    def get_metadata(self) -> dict:
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "cache_size": len(self.cache),
            "ttl": self.ttl
        }

# Usage
plugin = CachingPlugin(ttl=60)  # 60 second TTL

plugin.execute({"operation": "set", "key": "foo", "value": "bar"})
result = plugin.execute({"operation": "get", "key": "foo"})
print(result)  # {"status": "success", "value": "bar", "from_cache": True}

time.sleep(61)  # Wait for expiration
result = plugin.execute({"operation": "get", "key": "foo"})
print(result)  # {"status": "success", "value": None, "from_cache": False}
```

---

## Advanced Examples

### Example: Plugin with Subprocess Execution

```python
import subprocess
from app.plugins.plugin_runner import PluginRunner

class SubprocessPlugin:
    """Execute plugin in isolated subprocess."""
    
    def __init__(self, script_path: str):
        self.runner = PluginRunner(script_path, timeout=30.0)
    
    def execute(self, params: dict) -> dict:
        """Execute plugin with subprocess isolation."""
        try:
            response = self.runner.call_init(params)
            
            if "error" in response:
                return {"status": "error", "error": response["error"]}
            
            return {"status": "success", "result": response.get("result")}
        
        except TimeoutError:
            return {"status": "error", "error": "Plugin timeout"}
        
        except Exception as e:
            return {"status": "error", "error": str(e)}
        
        finally:
            self.runner.stop()

# Usage
plugin = SubprocessPlugin("plugins/data_processor.py")
result = plugin.execute({"action": "process", "data": [1, 2, 3]})
```

### Example: Plugin with Multiprocessing Isolation

```python
from app.security.agent_security import PluginIsolation

def risky_plugin_function(data: list) -> int:
    """Potentially risky plugin operation."""
    import time
    time.sleep(2)  # Simulate work
    return sum(data)

class IsolatedPlugin:
    """Execute plugin with full process isolation."""
    
    def execute(self, data: list) -> dict:
        """Execute with isolation and timeout."""
        try:
            result = PluginIsolation.execute_isolated(
                risky_plugin_function,
                data,
                timeout=5
            )
            return {"status": "success", "result": result}
        
        except TimeoutError:
            return {"status": "error", "error": "Plugin timeout"}
        
        except RuntimeError as e:
            return {"status": "error", "error": str(e)}

# Usage
plugin = IsolatedPlugin()
result = plugin.execute([1, 2, 3, 4, 5])
print(result)  # {"status": "success", "result": 15}
```

---

## References

- [Plugin Development Guide](./05-plugin-development-guide.md)
- [Plugin API Reference](./02-plugin-api-reference.md)
- [Plugin Security Guide](./04-plugin-security-guide.md)

---

**Author:** AGENT-046 (Plugin System Documentation Specialist)  
**Review Status:** 📝 Draft  
**Next Review:** After code review
