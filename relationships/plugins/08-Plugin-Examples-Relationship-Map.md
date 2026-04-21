---
title: "Plugin Examples - Relationship Map"
agent: AGENT-067
created: 2026-04-20
status: Active
---

# Plugin Examples - Comprehensive Relationship Map

## Executive Summary

Comprehensive documentation of real-world plugin implementations in Project-AI: MarketplaceSamplePlugin, GraphAnalysisPlugin, and ExcalidrawPlugin.

## 1. MarketplaceSamplePlugin

**Location:** `src/app/plugins/sample_plugin.py`

### Implementation

```python
from app.core.ai_systems import FourLaws, Plugin
from app.core.observability import emit_event

class MarketplaceSamplePlugin(Plugin):
    '''Example plugin with FourLaws validation.'''
    
    def __init__(self) -> None:
        super().__init__(name="marketplace_sample_plugin", version="0.1.0")
    
    def initialize(self, context: dict | None = None) -> bool:
        '''Validate against FourLaws before enabling.'''
        context = context or {}
        
        # FourLaws validation
        allowed, reason = FourLaws.validate_action(
            "Initialize marketplace sample plugin",
            context
        )
        
        if not allowed:
            emit_event("plugin.marketplace_sample.blocked", {"reason": reason})
            return False
        
        # Check explicit user order requirement
        if context.get("requires_explicit_order") and not context.get("is_user_order"):
            emit_event("plugin.marketplace_sample.blocked", {
                "reason": "requires_explicit_order without user order"
            })
            return False
        
        self.enabled = True
        emit_event("plugin.marketplace_sample.initialize", {
            "name": self.name,
            "version": self.version,
            "context": context
        })
        return True
```

### Key Features

- ✅ FourLaws validation integration
- ✅ Observability (emit_event)
- ✅ Context validation
- ✅ Explicit user order checks

### Usage

```python
plugin = MarketplaceSamplePlugin()
context = {"is_user_order": True, "endangers_humanity": False}
success = plugin.initialize(context)
manager.load_plugin(plugin)
```

## 2. GraphAnalysisPlugin

**Location:** `src/app/plugins/graph_analysis_plugin.py`

### Implementation (Excerpt)

```python
import networkx as nx
from app.core.interfaces import PluginInterface

class GraphAnalysisPlugin(PluginInterface):
    '''Network graph analysis and visualization.'''
    
    def get_name(self) -> str:
        return "graph_analysis"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_metadata(self) -> dict:
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "description": "Network graph analysis and visualization",
            "author": "Project-AI Team",
            "capabilities": ["graph_analysis", "data_visualization"],
            "requires_packages": ["networkx>=3.0", "matplotlib>=3.5"]
        }
    
    def validate_context(self, context: dict) -> bool:
        '''Validate context has graph data.'''
        return "action" in context and "data" in context
    
    def execute(self, context: dict) -> dict:
        '''Execute graph analysis.'''
        action = context["action"]
        data = context["data"]
        
        if action == "analyze":
            return self._analyze_graph(data)
        elif action == "visualize":
            return self._visualize_graph(data)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _analyze_graph(self, graph_data: dict) -> dict:
        '''Analyze graph structure.'''
        G = nx.Graph(graph_data.get("edges", []))
        
        return {
            "num_nodes": G.number_of_nodes(),
            "num_edges": G.number_of_edges(),
            "density": nx.density(G),
            "is_connected": nx.is_connected(G),
            "clustering_coefficient": nx.average_clustering(G)
        }
```

### Key Features

- ✅ PluginInterface implementation
- ✅ External dependencies (networkx, matplotlib)
- ✅ Multiple actions (analyze, visualize)
- ✅ Context validation
- ✅ Comprehensive metadata

### Usage

```python
registry = PluginRegistry()
plugin = GraphAnalysisPlugin()
registry.register(plugin)

context = {
    "action": "analyze",
    "data": {
        "edges": [(1, 2), (2, 3), (3, 1)]
    }
}
result = registry.execute_plugin("graph_analysis", context)
# Result: {"num_nodes": 3, "num_edges": 3, "density": 1.0, ...}
```

## 3. ExcalidrawPlugin

**Location:** `src/app/plugins/excalidraw_plugin.py`

### Implementation (Excerpt)

```python
from app.core.interfaces import PluginInterface

class ExcalidrawPlugin(PluginInterface):
    '''Excalidraw diagram generation and manipulation.'''
    
    def get_name(self) -> str:
        return "excalidraw"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_metadata(self) -> dict:
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "description": "Excalidraw diagram generation",
            "capabilities": ["diagram_generation", "export"],
            "supported_formats": ["json", "png", "svg"]
        }
    
    def validate_context(self, context: dict) -> bool:
        return "action" in context
    
    def execute(self, context: dict) -> dict:
        action = context["action"]
        
        if action == "create_diagram":
            return self._create_diagram(context.get("elements", []))
        elif action == "export":
            return self._export_diagram(
                context.get("diagram"),
                context.get("format", "json")
            )
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _create_diagram(self, elements: list) -> dict:
        '''Generate Excalidraw diagram JSON.'''
        diagram = {
            "type": "excalidraw",
            "version": 2,
            "source": "project-ai",
            "elements": elements,
            "appState": {
                "viewBackgroundColor": "#ffffff"
            }
        }
        return {"diagram": diagram, "status": "created"}
```

### Key Features

- ✅ Diagram generation
- ✅ Multiple export formats
- ✅ PluginInterface compliance
- ✅ Extensible element system

## Example Comparison Matrix

| Feature | MarketplaceSample | GraphAnalysis | Excalidraw |
|---------|------------------|---------------|------------|
| **Base Class** | Plugin (System A) | PluginInterface (B) | PluginInterface (B) |
| **FourLaws** | ✅ Explicit | ❌ Optional | ❌ Optional |
| **Observability** | ✅ emit_event | ⚠️ Optional | ⚠️ Optional |
| **External Deps** | ❌ None | ✅ networkx, matplotlib | ❌ None |
| **Actions** | 1 (initialize) | 2 (analyze, visualize) | 2 (create, export) |
| **Context Validation** | ✅ Custom | ✅ Required keys | ✅ Action check |
| **Trust Level** | 1 (verified) | 0 (trusted) | 0 (trusted) |

## References

- **Source:** `src/app/plugins/`
- **Tests:** `tests/test_plugin_sample.py`, `tests/test_graph_analysis_plugin.py`
- **Docs:** `source-docs/plugins/06-plugin-examples.md`

---
**Status:** ✅ Complete
