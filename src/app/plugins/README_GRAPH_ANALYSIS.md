# Graph Analysis Plugin

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Category:** Development Tools, Visualization

## Overview

The Graph Analysis Plugin provides comprehensive graph-based visualization and navigation of Project-AI's architecture. It models the codebase as an interactive knowledge graph with optimized filters, preset views, and performance optimizations for up to 1000 nodes.

## Features

✅ **Six Preset Views**
- Constitutional AI View - Ethics and validation architecture
- Security View - Security enforcement and monitoring
- Agent Systems View - AI agent ecosystem
- AI Core View - Core AI capabilities
- Data Flow View - Data persistence patterns
- Full System View - Complete architecture overview

✅ **Advanced Filtering**
- Filter by node type (constitutional, security, agent, ai_system, knowledge, module, data)
- Filter by tags (four_laws, security, validation, learning, etc.)
- Filter by folder path (src/app/core, src/app/agents, etc.)
- Filter by link type (validates, enforces, uses, depends_on, stores, triggers)

✅ **Performance Optimized**
- Lazy loading and index-based filtering
- <2s render time for full system view (30-35 nodes, 40-50 links)
- Cached preset configurations
- Scales to 1000+ nodes with recommended optimizations

✅ **Export Capability**
- Export graphs to JSON format
- Support for filtered and preset-based exports
- Integration-ready for visualization libraries

## Installation

### 1. Plugin Files

The plugin is located in `src/app/plugins/graph_analysis_plugin.py` with configuration in `graph_analysis_config.json`.

### 2. Dependencies

No additional dependencies required beyond Project-AI core dependencies.

### 3. Data Directory

The plugin creates `data/graph_analysis/` for exports and cached data.

## Usage

### Python API

```python
from app.plugins.graph_analysis_plugin import GraphAnalysisPlugin

# Initialize plugin
plugin = GraphAnalysisPlugin(data_dir="data")
plugin.initialize(context={})

# Get preset view
constitutional_graph = plugin.get_graph(preset="constitutional")
print(f"Nodes: {constitutional_graph['stats']['node_count']}")

# Custom filter
custom_graph = plugin.get_graph(custom_filter={
    "node_types": ["agent", "ai_system"],
    "tags": ["validation", "learning"]
})

# Export to file
plugin.export("data/graph_analysis/my_view.json", preset="security")

# Get statistics
stats = plugin.get_statistics()
print(f"Total nodes: {stats['total_nodes']}")
```

### Integration with Plugin Manager

```python
from app.core.ai_systems import PluginManager
from app.plugins.graph_analysis_plugin import GraphAnalysisPlugin

manager = PluginManager(plugins_dir="plugins")
plugin = GraphAnalysisPlugin()
manager.load_plugin(plugin)
```

### Dashboard Integration

```python
# Add to leather_book_dashboard.py
from app.plugins.graph_analysis_plugin import GraphAnalysisPlugin

class GraphPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.plugin = GraphAnalysisPlugin()
        self.plugin.initialize()
        self.load_view("constitutional")
    
    def load_view(self, preset_name):
        graph_data = self.plugin.get_graph(preset=preset_name)
        # Render with visualization library (Cytoscape.js, Sigma.js, etc.)
```

## Graph Structure

### Node Types (7)

1. **constitutional** - Ethics and validation framework (Four Laws, validators)
2. **security** - Security enforcement (Cerberus, User Manager, honeypots)
3. **agent** - AI agents (oversight, planner, validator, explainability)
4. **ai_system** - Core AI capabilities (persona, memory, learning)
5. **knowledge** - Knowledge bases and documentation
6. **module** - Functional code modules (image generator, data analysis)
7. **data** - Persistence and storage (JSON files)

### Link Types (8)

1. **validates** - Constitutional or safety validation
2. **enforces** - Security policy enforcement
3. **uses** - Component usage dependency
4. **depends_on** - Hard dependency relationship
5. **extends** - Inheritance or extension
6. **references** - Documentation cross-references
7. **stores** - Data persistence
8. **triggers** - Event triggering

### Preset Statistics

| Preset | Nodes | Links | Primary Types |
|--------|-------|-------|---------------|
| constitutional | 15-20 | 25-30 | constitutional, agent, ai_system |
| security | 12-15 | 20-25 | security, constitutional |
| agents | 10-12 | 15-20 | agent, ai_system |
| ai_core | 8-10 | 12-15 | ai_system, knowledge |
| data_flow | 12-15 | 10-12 | data, ai_system, module |
| full | 30-35 | 40-50 | All types |

## Examples

### Example 1: Explore Constitutional AI Architecture

```python
plugin = GraphAnalysisPlugin()
plugin.initialize()

# Get constitutional view
graph = plugin.get_graph(preset="constitutional")

# Print nodes
for node in graph["nodes"]:
    print(f"{node['name']} ({node['type']})")

# Print validation chains
for link in graph["links"]:
    if link["type"] == "validates":
        print(f"{link['source']} -> {link['target']}")
```

### Example 2: Analyze Security Architecture

```python
# Get security view
security_graph = plugin.get_graph(preset="security")

# Find all enforcement relationships
enforcement_links = [
    link for link in security_graph["links"]
    if link["type"] == "enforces"
]

for link in enforcement_links:
    print(f"{link['source']} enforces {link['target']}")
```

### Example 3: Custom Filter for Learning Systems

```python
# Custom filter for learning-related components
learning_graph = plugin.get_graph(custom_filter={
    "tags": ["learning", "black_vault", "approval"],
    "node_types": ["ai_system", "data"],
    "link_types": ["stores", "depends_on"]
})

print(f"Learning components: {learning_graph['stats']['node_count']}")
```

## Performance

### Current Performance

- **Full system view:** <2s for 34 nodes, 48 links
- **Preset views:** <1s for 8-20 nodes
- **Memory usage:** ~5MB for full graph in memory
- **Export:** <1s for JSON serialization

### Scaling Recommendations

**For 100-500 nodes:**
- Add viewport culling (only render visible nodes)
- Implement lazy rendering with intersection observers
- Use WebGL-based rendering (Sigma.js, Cytoscape.js)

**For 500-1000 nodes:**
- Migrate to graph database (Neo4j, Amazon Neptune)
- Implement GraphQL API with field-level filtering
- Add Redis caching for preset queries

**For 1000+ nodes:**
- Full GraphQL + WebGL stack
- Server-side graph algorithms
- Progressive loading and pagination

## File Structure

```
src/app/plugins/
├── graph_analysis_plugin.py      # Main plugin implementation (800+ lines)
├── graph_analysis_config.json    # Plugin configuration
└── README.md                      # This file

tests/
└── test_graph_analysis_plugin.py # Comprehensive tests (400+ lines)

data/graph_analysis/
├── constitutional_view.json      # Example constitutional view export
├── security_view.json            # Example security view export
├── agents_view.json              # Example agents view export
└── [custom exports]              # User-generated exports

GRAPH_VIEW_GUIDE.md              # Comprehensive usage guide (500+ words)
```

## Testing

### Run Tests

```bash
# All tests
pytest tests/test_graph_analysis_plugin.py -v

# Specific test class
pytest tests/test_graph_analysis_plugin.py::TestGraphAnalysisEngine -v

# Performance benchmarks
pytest tests/test_graph_analysis_plugin.py::TestPerformance -v
```

### Test Coverage

- ✅ Node and link creation
- ✅ Filter operations (tag, folder, link type)
- ✅ All six presets
- ✅ Export functionality
- ✅ Statistics generation
- ✅ Four Laws validation
- ✅ Performance benchmarks

## Visualization Integration

The plugin outputs JSON-compatible data that can be visualized with:

**Recommended Libraries:**

1. **Cytoscape.js** (Web-based, highly customizable)
   ```javascript
   fetch('data/graph_analysis/constitutional_view.json')
     .then(res => res.json())
     .then(data => {
       cytoscape({
         container: document.getElementById('cy'),
         elements: {
           nodes: data.nodes,
           edges: data.links
         }
       });
     });
   ```

2. **Sigma.js** (WebGL-based, high performance)
   ```javascript
   const graph = new Graph();
   data.nodes.forEach(n => graph.addNode(n.id, n));
   data.links.forEach(l => graph.addEdge(l.source, l.target, l));
   ```

3. **D3.js** (Force-directed layouts)
   ```javascript
   d3.forceSimulation(data.nodes)
     .force("link", d3.forceLink(data.links))
     .force("charge", d3.forceManyBody())
     .force("center", d3.forceCenter());
   ```

## Troubleshooting

**Issue:** Plugin initialization fails  
**Solution:** Verify `data_dir` exists and is writable, check Four Laws validation context

**Issue:** Missing nodes in filtered view  
**Solution:** Check filter criteria - may be too restrictive, try broader filters first

**Issue:** Export fails  
**Solution:** Ensure output directory exists, verify write permissions

**Issue:** Performance degradation with large graphs  
**Solution:** Use preset views instead of full system, implement viewport culling

## Future Enhancements

- [ ] Dynamic node discovery (auto-scan codebase)
- [ ] Interactive web-based UI with zoom/pan
- [ ] Temporal analysis (architecture evolution over time)
- [ ] Shortest path algorithms between nodes
- [ ] Impact analysis (downstream effects of changes)
- [ ] Graph metrics (centrality, clustering, betweenness)
- [ ] 3D visualization support
- [ ] Real-time filesystem watching for auto-updates

## License

See Project-AI LICENSE file.

## Support

- Documentation: `GRAPH_VIEW_GUIDE.md`
- Tests: `tests/test_graph_analysis_plugin.py`
- Issues: Project-AI GitHub repository

---

**Maintainer:** Project-AI Core Team  
**Last Updated:** 2024
