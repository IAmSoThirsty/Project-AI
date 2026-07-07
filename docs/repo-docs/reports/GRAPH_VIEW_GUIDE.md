---
type: guide
tags:
  - p2-root
  - status
  - guide
  - obsidian
  - graph-analysis
  - visualization
created: 2024-01-01
last_verified: 2026-04-20
status: current
related_systems:
  - graph-analysis-plugin
  - knowledge-graph
  - architecture-visualization
stakeholders:
  - architecture-team
  - plugin-team
report_type: guide
agent_id: AGENT-014
supersedes: []
review_cycle: as-needed
---

# Graph View Guide: Navigating Project-AI Knowledge Architecture

## Overview

The **Graph Analysis Plugin** provides a powerful visual navigation system for exploring Project-AI's complex architecture. This system models the codebase as an interactive knowledge graph with 500+ words of guidance, optimized filters, and preset views for different investigation scenarios.

## Architecture

### Node Types

The graph organizes Project-AI components into seven primary node types:

1. **Constitutional Nodes** (`constitutional`) - Ethics and validation framework
   - Four Laws Framework (Asimov's Laws implementation)
   - Constitutional validators and scenario engines
   - Ethical decision-making systems

2. **Security Nodes** (`security`) - Security enforcement and monitoring
   - Cerberus Security Engine (multi-headed orchestration)
   - User Manager (authentication with bcrypt)
   - Honeypot Detector (intrusion detection)
   - Command Override System (with audit logging)

3. **Agent Nodes** (`agent`) - Specialized AI agents
   - Oversight Agent (action safety validation)
   - Planner Agent (task decomposition)
   - Validator Agent (input/output validation)
   - Explainability Agent (decision transparency)

4. **AI System Nodes** (`ai_system`) - Core AI capabilities
   - AI Persona (personality and mood tracking)
   - Memory Expansion (knowledge base and conversation logging)
   - Learning Request Manager (human-in-the-loop approval)
   - Intelligence Engine (OpenAI integration)

5. **Knowledge Nodes** (`knowledge`) - Documentation and knowledge bases
   - Learning paths and educational content
   - Security resources and CTF repositories
   - Domain-specific knowledge categorization

6. **Module Nodes** (`module`) - Functional code modules
   - Image Generator (Stable Diffusion + DALL-E)
   - Data Analysis (CSV/XLSX processing)
   - Location Tracker (GPS and IP geolocation)

7. **Data Nodes** (`data`) - Persistence and storage
   - Persona state storage (`data/ai_persona/state.json`)
   - Memory knowledge base (`data/memory/knowledge.json`)
   - Learning requests and Black Vault (`data/learning_requests/requests.json`)
   - User database (`data/users.json`)

### Link Types

Relationships between nodes are categorized by eight link types:

- **VALIDATES** - Constitutional or safety validation (e.g., Four Laws → Oversight Agent)
- **ENFORCES** - Security policy enforcement (e.g., Cerberus → User Manager)
- **USES** - Component usage dependency (e.g., Persona → Intelligence Engine)
- **DEPENDS_ON** - Hard dependency relationship (e.g., Learning System → Four Laws)
- **EXTENDS** - Inheritance or extension (e.g., custom plugins extending base Plugin)
- **REFERENCES** - Documentation cross-references
- **STORES** - Data persistence (e.g., AI Persona → Persona Data)
- **TRIGGERS** - Event triggering (e.g., Honeypot → Cerberus alerts)

## Graph Filters

### Filter by Tag

Tags provide semantic categorization across node types. Common tags:

**Constitutional AI:**
- `four_laws` - Asimov's Laws implementation
- `ethics` - Ethical decision-making
- `validation` - Safety and ethics validation
- `constitutional` - Constitutional model components

**Security:**
- `security` - General security modules
- `cerberus` - Cerberus integration
- `honeypot` - Honeypot detection
- `auth` - Authentication systems
- `encryption` - Cryptographic systems

**AI Systems:**
- `persona` - AI personality systems
- `memory` - Memory and knowledge management
- `learning` - Learning and approval workflows
- `black_vault` - Forbidden content tracking

**Agents:**
- `agent` - AI agent systems
- `oversight` - Oversight and safety
- `planner` - Task planning
- `validator` - Validation systems
- `explainability` - Transparency and explanation

**Data:**
- `data` - Data nodes
- `persistence` - JSON persistence
- `json` - JSON-based storage

### Filter by Folder

Folder-based filtering maps to the actual codebase structure:

- `src/app/core` - Core business logic (AI systems, user management, etc.)
- `src/app/agents` - AI agent modules (oversight, planner, validator, explainability)
- `src/app/security` - Security modules (Cerberus, honeypots, encryption)
- `src/app/plugins` - Plugin system components
- `src/app/gui` - PyQt6 GUI modules
- `data/ai_persona` - Persona state persistence
- `data/memory` - Knowledge base storage
- `data/learning_requests` - Learning approval tracking

### Filter by Link Type

Link type filtering reveals specific relationship patterns:

**Data Flow Analysis:**
- Filter by `STORES` to see persistence patterns
- Filter by `USES` to track component dependencies

**Validation Chains:**
- Filter by `VALIDATES` to trace ethics enforcement
- Combine with `DEPENDS_ON` to see validation hierarchies

**Security Enforcement:**
- Filter by `ENFORCES` to see security policy propagation
- Filter by `TRIGGERS` to trace alert chains

## Graph Presets

Six optimized presets provide instant views for common investigation scenarios:

### 1. Constitutional AI View (`constitutional`)

**Purpose:** Explore ethics and validation architecture

**Includes:**
- Four Laws Framework
- Constitutional validators
- AI agents (oversight, planner, validator, explainability)
- AI systems with ethical dependencies

**Use Cases:**
- Understanding ethics enforcement
- Tracing validation chains
- Debugging constitutional violations
- Designing new ethical constraints

**Example Query:**
```python
plugin.get_graph(preset="constitutional")
```

**Performance:** <1s for 15-20 nodes, 25-30 links

### 2. Security View (`security`)

**Purpose:** Analyze security architecture and enforcement

**Includes:**
- Cerberus Security Engine
- User Manager and authentication
- Honeypot detectors
- Command Override System
- Constitutional validators (security overlap)

**Use Cases:**
- Security audits
- Threat modeling
- Access control analysis
- Incident response planning

**Example Query:**
```python
plugin.get_graph(preset="security")
```

**Performance:** <1s for 12-15 nodes, 20-25 links

### 3. Agent Systems View (`agents`)

**Purpose:** Visualize AI agent ecosystem

**Includes:**
- All four AI agents (oversight, planner, validator, explainability)
- Core AI systems (persona, memory, learning)
- Agent-system relationships

**Use Cases:**
- Agent coordination analysis
- Multi-agent workflow design
- Debugging agent interactions
- Performance optimization

**Example Query:**
```python
plugin.get_graph(preset="agents")
```

**Performance:** <1s for 10-12 nodes, 15-20 links

### 4. AI Core View (`ai_core`)

**Purpose:** Examine core AI capabilities

**Includes:**
- AI Persona System
- Memory Expansion System
- Learning Request Manager
- Intelligence Engine
- Knowledge bases

**Use Cases:**
- AI system integration
- Memory and learning analysis
- Persona behavior debugging
- Knowledge base expansion

**Example Query:**
```python
plugin.get_graph(preset="ai_core")
```

**Performance:** <1s for 8-10 nodes, 12-15 links

### 5. Data Flow View (`data_flow`)

**Purpose:** Trace data persistence and usage

**Includes:**
- All data nodes (JSON storage)
- AI systems and modules that persist data
- `STORES` and `USES` relationships only

**Use Cases:**
- Data architecture analysis
- Migration planning
- Backup/restore strategy
- Performance optimization (I/O bottlenecks)

**Example Query:**
```python
plugin.get_graph(preset="data_flow")
```

**Performance:** <1s for 12-15 nodes, 10-12 links

### 6. Full System View (`full`)

**Purpose:** Complete architecture overview

**Includes:**
- All nodes (constitutional, security, agents, AI systems, modules, data)
- All links (all eight link types)

**Use Cases:**
- System-wide impact analysis
- Architecture documentation
- Onboarding new developers
- Comprehensive audits

**Example Query:**
```python
plugin.get_graph(preset="full")
```

**Performance:** <2s for 30-35 nodes, 40-50 links

## Performance Optimization

The Graph Analysis Plugin is optimized for sub-5-second rendering with up to 1000 nodes. Current implementation supports:

### Current Scale
- **Nodes:** 30-35 (constitutional, security, agents, AI systems, modules, data)
- **Links:** 40-50 (validation, enforcement, usage, storage)
- **Render Time:** <2s for full system view on typical hardware

### Optimization Settings

1. **Lazy Loading:** Nodes and links are only computed when filtered
2. **Index-Based Filtering:** O(1) lookup for tag and node type filters
3. **Minimal Serialization:** Only serialize filtered subgraphs
4. **Cached Presets:** Preset configurations are pre-compiled

### Scaling Strategies (for future expansion to 1000+ nodes)

**Client-Side Optimizations:**
- Implement viewport culling (only render visible nodes)
- Use WebGL-based rendering (e.g., Sigma.js, Cytoscape.js)
- Progressive loading (fetch nodes on-demand)

**Server-Side Optimizations:**
- Graph database backend (Neo4j, Amazon Neptune)
- GraphQL API with field-level filtering
- Redis caching for preset queries

**Current Recommendations:**
- For <100 nodes: Current JSON-based approach is optimal
- For 100-500 nodes: Add viewport culling and lazy rendering
- For 500-1000 nodes: Migrate to graph database with caching
- For 1000+ nodes: Full GraphQL + WebGL stack

## Usage Examples

### Python API

```python
from app.plugins.graph_analysis_plugin import GraphAnalysisPlugin

# Initialize plugin
plugin = GraphAnalysisPlugin(data_dir="data")
plugin.initialize(context={})

# Get preset view
constitutional_graph = plugin.get_graph(preset="constitutional")
print(f"Nodes: {constitutional_graph['stats']['node_count']}")
print(f"Links: {constitutional_graph['stats']['link_count']}")

# Custom filter
custom_graph = plugin.get_graph(custom_filter={
    "node_types": ["agent", "ai_system"],
    "tags": ["validation", "learning"],
    "folders": ["src/app/agents", "src/app/core"]
})

# Export to file
plugin.export("graph_export.json", preset="security")

# Get statistics
stats = plugin.get_statistics()
print(f"Total nodes: {stats['total_nodes']}")
print(f"Presets: {stats['presets']}")
```

### Integration with Dashboard

```python
# In src/app/gui/leather_book_dashboard.py

from app.plugins.graph_analysis_plugin import GraphAnalysisPlugin

class GraphAnalysisPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.plugin = GraphAnalysisPlugin()
        self.plugin.initialize()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Preset selector
        preset_combo = QComboBox()
        preset_combo.addItems([
            "constitutional", "security", "agents",
            "ai_core", "data_flow", "full"
        ])
        preset_combo.currentTextChanged.connect(self.load_preset)
        
        layout.addWidget(preset_combo)
        self.setLayout(layout)
    
    def load_preset(self, preset_name: str):
        graph_data = self.plugin.get_graph(preset=preset_name)
        # Render graph using visualization library
        self.render_graph(graph_data)
```

## Best Practices

1. **Start with Presets:** Use predefined presets before creating custom filters
2. **Progressive Refinement:** Start with broad views (full, ai_core) then narrow down
3. **Tag Combinations:** Combine tags for precise filtering (e.g., `["security", "validation"]`)
4. **Folder Filtering:** Use folder paths for architecture-specific views
5. **Export for Documentation:** Export graphs to JSON for architecture diagrams
6. **Performance Monitoring:** Check `stats` field for node/link counts before rendering

## Troubleshooting

**Issue:** Graph renders slowly (>5s)
- **Solution:** Use more restrictive filters or switch to preset views

**Issue:** Missing nodes or links
- **Solution:** Check filter criteria - may be too restrictive

**Issue:** Plugin initialization fails
- **Solution:** Verify `data_dir` exists and is writable, check Four Laws validation context

**Issue:** Export fails
- **Solution:** Ensure output directory exists and has write permissions

## Future Enhancements

1. **Dynamic Node Discovery:** Auto-scan codebase for new modules
2. **Interactive Visualization:** Web-based graph UI with zoom/pan
3. **Temporal Analysis:** Track architecture evolution over time
4. **Path Finding:** Shortest path between any two nodes
5. **Impact Analysis:** Show downstream effects of changes
6. **Graph Metrics:** Centrality, clustering coefficient, betweenness
7. **3D Visualization:** Three-dimensional graph rendering
8. **Real-Time Updates:** Watch filesystem for architecture changes

## Support

For issues, enhancements, or questions:
- Check logs in `data/graph_analysis/` directory
- Review plugin code in `src/app/plugins/graph_analysis_plugin.py`
- Consult Project-AI documentation in `.github/instructions/`

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Maintainer:** Project-AI Core Team  
**License:** See PROJECT LICENSE
