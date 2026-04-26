---
type: guide
guide_type: integration
area: plugin-system
audience: [developer, integrator]
prerequisites:
  - 01-plugin-architecture-overview.md
  - 05-plugin-development-guide.md
tags:
  - plugin/integration
  - core-integration
  - gui-integration
  - deployment
related_docs:
  - 01-plugin-architecture-overview.md
  - 07-plugin-extensibility-patterns.md
  - ../architecture/ARCHITECTURE_OVERVIEW.md
last_updated: 2026-04-20
version: 1.0.0
---

# Plugin Integration Guide

**Complete guide to integrating plugins with Project-AI core systems**  
**Version:** 1.0.0  
**Last Updated:** 2026-04-20

---

## Table of Contents

1. [Integration Overview](#integration-overview)
2. [Core System Integration](#core-system-integration)
3. [GUI Integration](#gui-integration)
4. [Intelligence Engine Integration](#intelligence-engine-integration)
5. [Learning System Integration](#learning-system-integration)
6. [Memory System Integration](#memory-system-integration)
7. [Dashboard Integration](#dashboard-integration)
8. [Deployment and Distribution](#deployment-and-distribution)

---

## Integration Overview

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Project-AI Core Systems                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Intelligence │  │   Learning   │  │   Memory         │  │
│  │   Engine     │  │   System     │  │   System         │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────────┘  │
│         │                  │                  │               │
│         └──────────────────┼──────────────────┘               │
│                            ▼                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            Plugin Manager / Registry                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │  Plugin A    │  │  Plugin B    │  │  Plugin C  │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                            ▲                                  │
│  ┌─────────────────────────┴─────────────────────────────┐  │
│  │              GUI Integration Layer                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │  Dashboard   │  │  Actions     │  │  Settings  │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Integration Layers

| Layer | Responsibility | Files |
|-------|---------------|-------|
| **Core Integration** | Plugin manager, lifecycle, validation | `src/app/core/ai_systems.py` |
| **GUI Integration** | Dashboard actions, UI controls | `src/app/gui/leather_book_dashboard.py` |
| **Intelligence Integration** | AI response processing | `src/app/core/intelligence_engine.py` |
| **Learning Integration** | Learning path enrichment | `src/app/core/learning_paths.py` |
| **Memory Integration** | Knowledge base expansion | `src/app/core/ai_systems.py` (MemoryExpansionSystem) |

---

## Core System Integration

### Integrating with PluginManager

**Location:** `src/app/core/ai_systems.py:1015-1038`

#### Step 1: Initialize PluginManager

```python
from app.core.ai_systems import PluginManager

# Create plugin manager (typically in main.py)
plugin_manager = PluginManager(plugins_dir="data/plugins")

# Store as global or in application context
app_context["plugin_manager"] = plugin_manager
```

#### Step 2: Load Plugins at Startup

```python
from app.plugins.excalidraw_plugin import ExcalidrawPlugin
from app.plugins.sample_plugin import MarketplaceSamplePlugin

def load_plugins(plugin_manager: PluginManager):
    """Load all plugins at application startup."""
    
    # Plugin 1: Excalidraw
    excalidraw = ExcalidrawPlugin(data_dir="data")
    success = excalidraw.initialize({
        "is_user_order": True,
        "harms_human": False
    })
    if success:
        plugin_manager.load_plugin(excalidraw)
        logger.info("Loaded Excalidraw plugin")
    
    # Plugin 2: Sample plugin
    sample = MarketplaceSamplePlugin()
    success = sample.initialize({
        "is_user_order": True,
        "harms_human": False
    })
    if success:
        plugin_manager.load_plugin(sample)
        logger.info("Loaded sample plugin")
    
    # Get statistics
    stats = plugin_manager.get_statistics()
    logger.info("Plugin stats: %s", stats)

# Call during application initialization
load_plugins(app_context["plugin_manager"])
```

#### Step 3: Access Plugins from Core

```python
def use_plugin_in_core(plugin_manager: PluginManager):
    """Use plugins from core systems."""
    
    # Get specific plugin
    excalidraw = plugin_manager.plugins.get("excalidraw")
    
    if excalidraw and excalidraw.enabled:
        # Use plugin functionality
        diagram = excalidraw.create_diagram(
            name="System Architecture",
            description="Core system diagram"
        )
        logger.info("Created diagram: %s", diagram["id"])
```

### Integrating with PluginRegistry

**Location:** `src/app/core/interfaces.py:297-389`

#### Step 1: Initialize Registry

```python
from app.core.interfaces import PluginRegistry

# Create registry (typically in main.py)
plugin_registry = PluginRegistry()

# Store in application context
app_context["plugin_registry"] = plugin_registry
```

#### Step 2: Register Plugins

```python
from app.plugins.data_processor_plugin import DataProcessorPlugin

def register_plugins(registry: PluginRegistry):
    """Register PluginInterface implementations."""
    
    # Register data processor
    data_plugin = DataProcessorPlugin()
    registry.register(data_plugin)
    logger.info("Registered data processor plugin")
    
    # Register additional plugins...
    
    # List all registered plugins
    plugins = registry.list_plugins()
    logger.info("Total plugins: %d", len(plugins))

# Call during initialization
register_plugins(app_context["plugin_registry"])
```

#### Step 3: Execute Plugins

```python
def execute_plugin_from_core(registry: PluginRegistry):
    """Execute plugin from core system."""
    
    try:
        result = registry.execute_plugin(
            "data_processor",
            context={
                "operation": "sum",
                "data": [1, 2, 3, 4, 5]
            }
        )
        
        if result["status"] == "success":
            logger.info("Plugin result: %s", result["result"])
        else:
            logger.error("Plugin error: %s", result.get("error"))
    
    except KeyError as e:
        logger.error("Plugin not found: %s", e)
    except ValueError as e:
        logger.error("Invalid context: %s", e)
```

---

## GUI Integration

### Dashboard Integration

**Location:** `src/app/gui/leather_book_dashboard.py`

#### Pattern 1: Add Plugin Action Buttons

```python
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal

class ProactiveActionsPanel(QWidget):
    """Dashboard actions panel with plugin integration."""
    
    # Define signal for plugin action
    plugin_action_requested = pyqtSignal(str)  # plugin_name
    
    def __init__(self, plugin_manager: PluginManager):
        super().__init__()
        self.plugin_manager = plugin_manager
        self._setup_plugin_actions()
    
    def _setup_plugin_actions(self):
        """Create action buttons for enabled plugins."""
        layout = QVBoxLayout(self)
        
        # Iterate through enabled plugins
        for plugin_name, plugin in self.plugin_manager.plugins.items():
            if plugin.enabled:
                # Check if plugin has GUI actions
                if hasattr(plugin, "get_gui_actions"):
                    actions = plugin.get_gui_actions()
                    
                    for action in actions:
                        button = QPushButton(action["label"])
                        button.clicked.connect(
                            lambda checked, p=plugin_name: self.plugin_action_requested.emit(p)
                        )
                        layout.addWidget(button)
```

#### Pattern 2: Handle Plugin Actions

```python
class LeatherBookDashboard(QWidget):
    """Main dashboard with plugin integration."""
    
    def __init__(self, plugin_manager: PluginManager):
        super().__init__()
        self.plugin_manager = plugin_manager
        
        # Setup UI
        self.actions_panel = ProactiveActionsPanel(plugin_manager)
        
        # Connect signals
        self.actions_panel.plugin_action_requested.connect(self.handle_plugin_action)
    
    def handle_plugin_action(self, plugin_name: str):
        """Handle plugin action request from UI."""
        plugin = self.plugin_manager.plugins.get(plugin_name)
        
        if not plugin or not plugin.enabled:
            QMessageBox.warning(self, "Error", f"Plugin {plugin_name} not available")
            return
        
        # Execute plugin-specific action
        if plugin_name == "excalidraw":
            self.open_excalidraw(plugin)
        elif plugin_name == "graph_analysis":
            self.run_graph_analysis(plugin)
    
    def open_excalidraw(self, plugin: ExcalidrawPlugin):
        """Open Excalidraw plugin."""
        success = plugin.open_excalidraw()
        
        if success:
            QMessageBox.information(
                self,
                "Excalidraw",
                "Opened Excalidraw in browser"
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "Failed to open Excalidraw"
            )
```

#### Example: Excalidraw Integration

```python
# In leather_book_dashboard.py

class ProactiveActionsPanel(QWidget):
    image_gen_requested = pyqtSignal()
    excalidraw_requested = pyqtSignal()  # Add new signal
    
    def __init__(self, plugin_manager: PluginManager):
        super().__init__()
        self.plugin_manager = plugin_manager
        self._create_actions()
    
    def _create_actions(self):
        layout = QVBoxLayout(self)
        
        # Existing action: Image generation
        image_gen_button = QPushButton("🎨 GENERATE IMAGES")
        image_gen_button.clicked.connect(self.image_gen_requested.emit)
        layout.addWidget(image_gen_button)
        
        # New action: Excalidraw (if plugin enabled)
        excalidraw = self.plugin_manager.plugins.get("excalidraw")
        if excalidraw and excalidraw.enabled:
            excalidraw_button = QPushButton("📊 CREATE DIAGRAM")
            excalidraw_button.clicked.connect(self.excalidraw_requested.emit)
            layout.addWidget(excalidraw_button)

# In main dashboard class
class LeatherBookDashboard(QWidget):
    def __init__(self):
        # ... existing init ...
        self.actions_panel.excalidraw_requested.connect(self.open_excalidraw_plugin)
    
    def open_excalidraw_plugin(self):
        """Handle Excalidraw button click."""
        plugin = self.plugin_manager.plugins.get("excalidraw")
        if plugin:
            plugin.open_excalidraw()
```

### Settings Integration

#### Pattern: Plugin Settings Panel

```python
from PyQt6.QtWidgets import QGroupBox, QCheckBox, QLabel

class PluginSettingsPanel(QGroupBox):
    """Settings panel for managing plugins."""
    
    def __init__(self, plugin_manager: PluginManager):
        super().__init__("Plugin Settings")
        self.plugin_manager = plugin_manager
        self._setup_ui()
    
    def _setup_ui(self):
        """Create plugin enable/disable controls."""
        layout = QVBoxLayout(self)
        
        # Create checkbox for each plugin
        for plugin_name, plugin in self.plugin_manager.plugins.items():
            checkbox = QCheckBox(f"Enable {plugin_name}")
            checkbox.setChecked(plugin.enabled)
            checkbox.stateChanged.connect(
                lambda state, p=plugin: self.toggle_plugin(p, state)
            )
            
            # Add plugin info label
            info = QLabel(f"Version: {plugin.version}")
            info.setStyleSheet("color: gray; font-size: 10px;")
            
            layout.addWidget(checkbox)
            layout.addWidget(info)
    
    def toggle_plugin(self, plugin: Plugin, state: int):
        """Enable or disable plugin."""
        if state == 2:  # Qt.Checked
            plugin.enable()
            logger.info("Enabled plugin: %s", plugin.name)
        else:
            plugin.disable()
            logger.info("Disabled plugin: %s", plugin.name)
```

---

## Intelligence Engine Integration

**Location:** `src/app/core/intelligence_engine.py`

### Pattern: Plugin Response Processing

```python
class IntelligenceEngine:
    """AI intelligence engine with plugin integration."""
    
    def __init__(self, plugin_registry: PluginRegistry):
        self.plugin_registry = plugin_registry
        self.openai_client = OpenAI()
    
    def generate_response(self, prompt: str) -> str:
        """Generate AI response with plugin processing."""
        
        # Step 1: Get base response from OpenAI
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        text = response.choices[0].message.content
        
        # Step 2: Process through plugins
        processed_text = self.process_with_plugins(text, prompt)
        
        return processed_text
    
    def process_with_plugins(self, text: str, original_prompt: str) -> str:
        """Process AI response through registered plugins."""
        
        # Find plugins with "response_processing" capability
        for plugin_meta in self.plugin_registry.list_plugins():
            capabilities = plugin_meta.get("capabilities", [])
            
            if "response_processing" in capabilities:
                try:
                    result = self.plugin_registry.execute_plugin(
                        plugin_meta["name"],
                        context={
                            "action": "process_response",
                            "text": text,
                            "prompt": original_prompt
                        }
                    )
                    
                    if result.get("status") == "success":
                        text = result.get("processed_text", text)
                
                except Exception as e:
                    logger.error("Plugin processing failed: %s", e)
        
        return text
```

### Example: Markdown Formatting Plugin

```python
from app.core.interfaces import PluginInterface

class MarkdownFormatterPlugin(PluginInterface):
    """Plugin to format AI responses with markdown."""
    
    def get_name(self) -> str:
        return "markdown_formatter"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_metadata(self) -> dict:
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "capabilities": ["response_processing"]
        }
    
    def execute(self, context: dict) -> dict:
        """Format text with markdown."""
        text = context["text"]
        
        # Add markdown formatting
        formatted = self._add_code_blocks(text)
        formatted = self._add_headers(formatted)
        
        return {
            "status": "success",
            "processed_text": formatted
        }
    
    def validate_context(self, context: dict) -> bool:
        return "text" in context and "action" in context
    
    def _add_code_blocks(self, text: str) -> str:
        """Wrap code snippets in markdown code blocks."""
        # Implementation...
        return text
    
    def _add_headers(self, text: str) -> str:
        """Convert section titles to markdown headers."""
        # Implementation...
        return text
```

---

## Learning System Integration

**Location:** `src/app/core/learning_paths.py`

### Pattern: Plugin Learning Resources

```python
class LearningRequestManager:
    """Learning system with plugin integration."""
    
    def __init__(self, plugin_registry: PluginRegistry):
        self.plugin_registry = plugin_registry
    
    def get_learning_resources(self, topic: str) -> list[dict]:
        """Get learning resources including plugin-provided ones."""
        
        resources = []
        
        # Step 1: Get base resources from OpenAI
        base_resources = self._generate_learning_path(topic)
        resources.extend(base_resources)
        
        # Step 2: Get plugin-provided resources
        plugin_resources = self._get_plugin_learning_resources(topic)
        resources.extend(plugin_resources)
        
        return resources
    
    def _get_plugin_learning_resources(self, topic: str) -> list[dict]:
        """Get learning resources from plugins."""
        resources = []
        
        # Find plugins with "learning_resources" capability
        for plugin_meta in self.plugin_registry.list_plugins():
            capabilities = plugin_meta.get("capabilities", [])
            
            if "learning_resources" in capabilities:
                try:
                    result = self.plugin_registry.execute_plugin(
                        plugin_meta["name"],
                        context={
                            "action": "get_learning_resources",
                            "topic": topic
                        }
                    )
                    
                    if result.get("status") == "success":
                        resources.extend(result.get("resources", []))
                
                except Exception as e:
                    logger.error("Plugin failed to provide resources: %s", e)
        
        return resources
```

### Example: Security Learning Plugin

```python
from app.core.interfaces import PluginInterface

class SecurityLearningPlugin(PluginInterface):
    """Plugin providing security-focused learning resources."""
    
    def get_name(self) -> str:
        return "security_learning"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_metadata(self) -> dict:
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "capabilities": ["learning_resources"]
        }
    
    def execute(self, context: dict) -> dict:
        """Provide security learning resources."""
        topic = context["topic"]
        
        # Map topics to security resources
        resources = self._find_security_resources(topic)
        
        return {
            "status": "success",
            "resources": resources
        }
    
    def validate_context(self, context: dict) -> bool:
        return "action" in context and "topic" in context
    
    def _find_security_resources(self, topic: str) -> list[dict]:
        """Find relevant security resources."""
        security_resources = [
            {
                "title": "OWASP Top 10",
                "url": "https://owasp.org/www-project-top-ten/",
                "type": "documentation",
                "topics": ["web_security", "vulnerabilities"]
            },
            {
                "title": "CWE Top 25",
                "url": "https://cwe.mitre.org/top25/",
                "type": "reference",
                "topics": ["security", "vulnerabilities"]
            }
        ]
        
        # Filter by topic
        return [
            r for r in security_resources
            if topic.lower() in r["topics"]
        ]
```

---

## Memory System Integration

**Location:** `src/app/core/ai_systems.py` (MemoryExpansionSystem)

### Pattern: Plugin Memory Storage

```python
class MemoryExpansionSystem:
    """Memory system with plugin integration."""
    
    def __init__(self, plugin_registry: PluginRegistry):
        self.plugin_registry = plugin_registry
        self.knowledge_base = []
    
    def add_memory(self, content: str, category: str, metadata: dict = None):
        """Add memory with plugin enrichment."""
        
        # Step 1: Create base memory entry
        memory = {
            "content": content,
            "category": category,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        
        # Step 2: Enrich with plugins
        enriched_memory = self._enrich_with_plugins(memory)
        
        # Step 3: Store
        self.knowledge_base.append(enriched_memory)
    
    def _enrich_with_plugins(self, memory: dict) -> dict:
        """Enrich memory with plugin-provided data."""
        
        # Find plugins with "memory_enrichment" capability
        for plugin_meta in self.plugin_registry.list_plugins():
            capabilities = plugin_meta.get("capabilities", [])
            
            if "memory_enrichment" in capabilities:
                try:
                    result = self.plugin_registry.execute_plugin(
                        plugin_meta["name"],
                        context={
                            "action": "enrich_memory",
                            "memory": memory
                        }
                    )
                    
                    if result.get("status") == "success":
                        # Merge enriched data
                        enriched_data = result.get("enriched_data", {})
                        memory["metadata"].update(enriched_data)
                
                except Exception as e:
                    logger.error("Memory enrichment failed: %s", e)
        
        return memory
```

---

## Dashboard Integration

### Complete Integration Example

```python
# src/app/main.py

from PyQt6.QtWidgets import QApplication
from app.gui.leather_book_interface import LeatherBookInterface
from app.core.ai_systems import PluginManager
from app.core.interfaces import PluginRegistry
from app.plugins.excalidraw_plugin import ExcalidrawPlugin

def main():
    """Application entry point with plugin integration."""
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Initialize plugin systems
    plugin_manager = PluginManager(plugins_dir="data/plugins")
    plugin_registry = PluginRegistry()
    
    # Load plugins
    load_plugins(plugin_manager, plugin_registry)
    
    # Create main window with plugin integration
    window = LeatherBookInterface(
        plugin_manager=plugin_manager,
        plugin_registry=plugin_registry
    )
    
    window.show()
    sys.exit(app.exec())

def load_plugins(manager: PluginManager, registry: PluginRegistry):
    """Load all plugins at startup."""
    
    # System A plugins (PluginManager)
    excalidraw = ExcalidrawPlugin(data_dir="data")
    if excalidraw.initialize({"is_user_order": True, "harms_human": False}):
        manager.load_plugin(excalidraw)
        logger.info("Loaded Excalidraw plugin")
    
    # System B plugins (PluginRegistry)
    data_plugin = DataProcessorPlugin()
    registry.register(data_plugin)
    logger.info("Registered data processor plugin")

if __name__ == "__main__":
    main()
```

---

## Deployment and Distribution

### Packaging Plugins

#### Plugin Package Structure

```
my_plugin/
├── setup.py              # Plugin distribution
├── requirements.txt      # Plugin dependencies
├── plugin.json           # Plugin manifest
├── README.md             # Plugin documentation
├── my_plugin/
│   ├── __init__.py
│   ├── plugin.py         # Plugin implementation
│   └── utils.py          # Plugin utilities
└── tests/
    └── test_plugin.py    # Plugin tests
```

#### setup.py Example

```python
from setuptools import setup, find_packages

setup(
    name="project-ai-my-plugin",
    version="1.0.0",
    author="Your Name",
    description="My custom Project-AI plugin",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        # ... plugin dependencies ...
    ],
    entry_points={
        "project_ai.plugins": [
            "my_plugin = my_plugin.plugin:MyPlugin"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
)
```

### Installing Plugins

```bash
# Install from local directory
pip install -e path/to/my_plugin

# Install from repository
pip install git+https://github.com/username/project-ai-my-plugin.git

# Install from PyPI (if published)
pip install project-ai-my-plugin
```

### Plugin Discovery

```python
import pkg_resources

def discover_installed_plugins() -> list[PluginInterface]:
    """Discover plugins via entry points."""
    plugins = []
    
    for entry_point in pkg_resources.iter_entry_points("project_ai.plugins"):
        try:
            plugin_class = entry_point.load()
            plugin = plugin_class()
            plugins.append(plugin)
            logger.info("Discovered plugin: %s", entry_point.name)
        except Exception as e:
            logger.error("Failed to load plugin %s: %s", entry_point.name, e)
    
    return plugins

# Auto-load discovered plugins
discovered_plugins = discover_installed_plugins()
for plugin in discovered_plugins:
    registry.register(plugin)
```

---

## References

- [Plugin Architecture Overview](./01-plugin-architecture-overview.md)
- [Plugin Development Guide](./05-plugin-development-guide.md)
- [Plugin Extensibility Patterns](./07-plugin-extensibility-patterns.md)
- [Architecture Overview](../architecture/ARCHITECTURE_OVERVIEW.md)

---

**Author:** AGENT-046 (Plugin System Documentation Specialist)  
**Review Status:** 📝 Draft  
**Next Review:** After integration testing
