# Excalidraw Plugin Guide

## Overview

The Excalidraw plugin integrates powerful visual diagramming capabilities into Project-AI, enabling users to create hand-drawn style diagrams, architecture maps, flowcharts, and relationship visualizations. Excalidraw provides an intuitive sketching experience with professional export options.

## What is Excalidraw?

Excalidraw is a virtual whiteboard application for sketching diagrams that have a hand-drawn feel. It's perfect for:

- **Architecture diagrams**: System architecture, component relationships, data flows
- **Flowcharts**: Process flows, decision trees, workflows
- **Mind maps**: Brainstorming, concept mapping, knowledge organization
- **UML diagrams**: Class diagrams, sequence diagrams, state machines
- **Network diagrams**: Infrastructure layouts, topology maps
- **Wireframes**: UI/UX mockups and prototypes

## Installation & Setup

### Desktop Application (PyQt6)

The Excalidraw plugin is already included in Project-AI. To enable it:

1. **Initialize the plugin**:
   ```python
   from app.plugins.excalidraw_plugin import ExcalidrawPlugin
   
   # Create plugin instance
   excalidraw = ExcalidrawPlugin(data_dir="data")
   
   # Initialize with safety validation
   success = excalidraw.initialize()
   
   if success:
       print("Excalidraw plugin enabled!")
   ```

2. **Directory structure created**:
   ```
   data/
   └── excalidraw_diagrams/
       ├── config.json          # Plugin configuration
       ├── metadata.json        # Diagram tracking
       └── *.excalidraw         # Saved diagrams
   ```

### Web Application (Next.js)

The web component is available at `web/components/ExcalidrawComponent.tsx`.

1. **Import the component**:
   ```tsx
   import ExcalidrawComponent from '@/components/ExcalidrawComponent';
   ```

2. **Use in your page**:
   ```tsx
   export default function DiagramPage() {
     return (
       <div style={{ height: '100vh' }}>
         <ExcalidrawComponent
           height="100%"
           darkMode={false}
           onSave={(diagram, content) => {
             console.log('Diagram saved:', diagram.name);
           }}
         />
       </div>
     );
   }
   ```

## Features

### 1. Diagram Creation & Management

**Desktop API**:
```python
# Create a new diagram
diagram = excalidraw.create_diagram(
    name="System Architecture",
    description="High-level overview of Project-AI components"
)

# List all diagrams
diagrams = excalidraw.list_diagrams()
for d in diagrams:
    print(f"{d['name']} - Created: {d['created_at']}")

# Load existing diagram
content = excalidraw.load_diagram(diagram['id'])

# Save diagram content
excalidraw.save_diagram(diagram['id'], content)
```

**Web Interface**:
- Click "**+ New Diagram**" to create
- Use dropdown to select existing diagrams
- Auto-saves to browser localStorage
- Real-time editing with instant feedback

### 2. Drawing Tools

Excalidraw provides comprehensive drawing capabilities:

- **Shapes**: Rectangles, circles, diamonds, ellipses
- **Lines**: Straight lines, arrows (single/double-headed)
- **Text**: Multi-line text with formatting
- **Hand-drawn**: Free-hand drawing tool
- **Selection**: Move, resize, rotate, group elements
- **Layers**: Bring to front/back, arrange layers
- **Colors**: Stroke and fill colors, opacity control
- **Styles**: Stroke width, dash patterns, edge styles

**Drawing Workflow**:
1. Select a tool from the toolbar (rectangle, arrow, text, etc.)
2. Click and drag on canvas to create elements
3. Use selection tool to modify existing elements
4. Group related elements (Ctrl+G / Cmd+G)
5. Arrange layers with right-click menu
6. Add text labels for clarity

### 3. Collaboration Features

While the plugin provides local storage, Excalidraw diagrams use a **collaborative-ready format**:

- JSON-based format enables version control
- Shareable `.excalidraw` files
- Compatible with Excalidraw's official app
- Can be committed to Git repositories
- Supports collaborative editing when hosted

**Sharing Diagrams**:
```python
# Export diagram for sharing
diagram_content = excalidraw.load_diagram(diagram_id)

# Save to file for version control
with open('docs/architecture.excalidraw', 'w') as f:
    f.write(diagram_content)

# Commit to Git
# git add docs/architecture.excalidraw
# git commit -m "Add system architecture diagram"
```

### 4. Export Formats

Excalidraw supports multiple export formats for different use cases:

#### PNG Export (Raster Image)
- **Use for**: Documentation, presentations, web display
- **Pros**: Universal compatibility, embedded in markdown
- **Cons**: Not scalable, larger file size
- **Desktop**:
  ```python
  export_info = excalidraw.export_diagram(diagram_id, "png")
  print(f"Export saved to: {export_info['file_path']}")
  ```
- **Web**: Click "Export PNG" button in toolbar

#### SVG Export (Vector Graphics)
- **Use for**: Print materials, scalable graphics
- **Pros**: Infinite scaling, smaller file size, editable
- **Cons**: May have compatibility issues in some viewers
- **Desktop**:
  ```python
  export_info = excalidraw.export_diagram(diagram_id, "svg")
  ```
- **Web**: Click "Export SVG" button

#### JSON Export (Native Format)
- **Use for**: Backup, version control, re-editing
- **Pros**: Preserves all elements, fully editable
- **Cons**: Requires Excalidraw to view
- **Desktop**:
  ```python
  # Native format is already JSON
  content = excalidraw.load_diagram(diagram_id)
  ```
- **Web**: Click "Export JSON" button

### 5. Configuration

Customize plugin behavior via configuration:

```python
# Access configuration
config = excalidraw.config

# Available settings
config['auto_save'] = True              # Auto-save on changes
config['default_export_format'] = 'png' # Default export format
config['grid_enabled'] = True           # Show grid
config['theme'] = 'light'               # 'light' or 'dark'

# Save configuration
excalidraw._save_config()
```

**Web Component Props**:
```tsx
<ExcalidrawComponent
  height="800px"              // Editor height
  darkMode={true}             // Enable dark theme
  initialDiagram={diagram}    // Load specific diagram
  onSave={(diagram, content) => {
    // Handle save event
  }}
  onExport={(format, data) => {
    // Handle export event
  }}
/>
```

### 6. Advanced Usage

#### Programmatic Diagram Creation

While manual drawing is primary, you can generate diagrams programmatically:

```python
import json

# Create diagram structure
diagram_data = {
    "type": "excalidraw",
    "version": 2,
    "source": "https://excalidraw.com",
    "elements": [
        {
            "type": "rectangle",
            "x": 100,
            "y": 100,
            "width": 200,
            "height": 100,
            "strokeColor": "#000000",
            "backgroundColor": "#4CAF50",
            "fillStyle": "hachure",
            "strokeWidth": 2,
            "roughness": 1,
        },
        {
            "type": "text",
            "x": 150,
            "y": 130,
            "text": "AI Systems",
            "fontSize": 20,
            "fontFamily": 1,
        },
    ],
    "appState": {
        "gridSize": null,
        "viewBackgroundColor": "#ffffff"
    }
}

# Save programmatically created diagram
diagram = excalidraw.create_diagram("Generated Diagram")
excalidraw.save_diagram(diagram['id'], json.dumps(diagram_data))
```

#### Integration with AI Systems

Leverage Excalidraw for AI-generated diagrams:

```python
from app.core.intelligence_engine import IntelligenceEngine

# Request AI to describe architecture
ai = IntelligenceEngine()
response = ai.chat("Describe the Project-AI architecture in bullet points")

# User creates diagram based on AI description
excalidraw.open_excalidraw()  # Opens browser
print("AI Suggestions:")
print(response)
print("\nCreate diagram in opened browser window")
```

#### Diagram Templates

Create reusable templates for common diagrams:

```python
# Save template
template_diagram = excalidraw.create_diagram(
    name="TEMPLATE: System Architecture",
    description="Reusable template for system diagrams"
)

# Load template when creating new diagram
template_content = excalidraw.load_diagram(template_diagram['id'])
new_diagram = excalidraw.create_diagram("Project X Architecture")
excalidraw.save_diagram(new_diagram['id'], template_content)
```

## Best Practices

### 1. Naming Conventions
- Use descriptive names: "User Authentication Flow" not "Diagram 1"
- Include version in name: "Architecture v2.0"
- Add dates for iterations: "API Design 2024-01-15"

### 2. Organization
- Group related elements together
- Use consistent colors for element types (e.g., databases = blue, services = green)
- Add text labels to all components
- Use arrows to show relationships and data flow

### 3. Export & Documentation
- Export PNG for embedding in markdown docs
- Keep `.excalidraw` files in version control
- Update exports when diagrams change
- Include diagram descriptions in metadata

### 4. Performance
- Keep diagrams focused (20-30 elements max)
- Split complex systems into multiple diagrams
- Use references between diagrams (e.g., "See Data Flow Diagram")

### 5. Collaboration
- Commit `.excalidraw` files to Git
- Use clear commit messages: "Update: Add auth module to architecture"
- Review diagram changes in pull requests
- Maintain a diagrams index in README

## Example: Creating an Architecture Diagram

### Step 1: Initialize
```python
from app.plugins.excalidraw_plugin import ExcalidrawPlugin

excalidraw = ExcalidrawPlugin()
excalidraw.initialize()
```

### Step 2: Create Diagram
```python
diagram = excalidraw.create_diagram(
    name="Project-AI Core Architecture",
    description="Shows the 6 core AI systems and their relationships"
)
```

### Step 3: Open Editor
```python
excalidraw.open_excalidraw()
# Browser opens to https://excalidraw.com
```

### Step 4: Draw Components
In the browser:
1. Draw rectangles for each system (FourLaws, AIPersona, Memory, Learning, Plugin, Override)
2. Add arrows showing dependencies
3. Add text labels for each component
4. Color-code by function (ethics=red, personality=blue, data=green)
5. Add title and legend

### Step 5: Save & Export
From Excalidraw menu → "Save to disk" → download `.excalidraw` file

Then in Python:
```python
# Load downloaded file
with open('downloads/diagram.excalidraw') as f:
    content = f.read()

# Save to plugin storage
excalidraw.save_diagram(diagram['id'], content)

# Record export
excalidraw.export_diagram(diagram['id'], 'png')
```

## Sample Diagrams

See `data/excalidraw_diagrams/samples/` for example diagrams:
- `architecture_example.excalidraw` - System architecture
- `data_flow_example.excalidraw` - Data flow diagram
- `user_journey_example.excalidraw` - User interaction flow

## Troubleshooting

### Browser doesn't open
```python
# Check if plugin is enabled
stats = excalidraw.get_statistics()
print(f"Enabled: {stats['enabled']}")

# Manually open URL
import webbrowser
webbrowser.open("https://excalidraw.com")
```

### Diagrams not saving
```python
# Check permissions
import os
print(f"Directory exists: {os.path.exists(excalidraw.diagrams_dir)}")
print(f"Writable: {os.access(excalidraw.diagrams_dir, os.W_OK)}")

# Verify metadata
print(f"Total diagrams: {len(excalidraw.metadata['diagrams'])}")
```

### Web component not loading
- Check browser console for errors
- Verify localStorage is enabled
- Clear browser cache
- Check iframe permissions for clipboard access

## API Reference

### Desktop Plugin

**ExcalidrawPlugin**
- `__init__(data_dir: str)` - Initialize plugin
- `initialize(context: dict)` → bool - Enable with validation
- `create_diagram(name: str, description: str)` → dict - Create new diagram
- `save_diagram(diagram_id: str, content: str)` → bool - Save content
- `load_diagram(diagram_id: str)` → str - Load content
- `list_diagrams()` → list - Get all diagrams
- `open_excalidraw()` → bool - Open web interface
- `export_diagram(diagram_id: str, format: str)` → dict - Record export
- `get_statistics()` → dict - Get plugin stats
- `disable()` → bool - Disable plugin

### Web Component

**ExcalidrawComponent Props**
- `initialDiagram?: ExcalidrawDiagram` - Diagram to load
- `onSave?: (diagram, content) => void` - Save callback
- `onExport?: (format, data) => void` - Export callback
- `height?: string` - Editor height (default: "600px")
- `darkMode?: boolean` - Dark theme (default: false)

## Resources

- **Excalidraw Official**: https://excalidraw.com
- **Documentation**: https://docs.excalidraw.com
- **GitHub**: https://github.com/excalidraw/excalidraw
- **Examples**: https://excalidraw.com/#room=examples
- **Libraries**: Built-in shape libraries for common diagrams

## Integration with Project-AI

### GUI Integration (Future Enhancement)

The plugin can be integrated into the Leather Book UI:

```python
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView

class DiagramPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.excalidraw = ExcalidrawPlugin()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Embedded browser
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://excalidraw.com"))
        
        # Controls
        btn_save = QPushButton("Save Diagram")
        btn_save.clicked.connect(self.save_diagram)
        
        layout.addWidget(self.browser)
        layout.addWidget(btn_save)
        self.setLayout(layout)
```

### CLI Integration

Use from command line:

```bash
# List diagrams
python -c "from app.plugins.excalidraw_plugin import ExcalidrawPlugin; \
           e = ExcalidrawPlugin(); e.initialize(); \
           print(e.list_diagrams())"

# Open Excalidraw
python -c "from app.plugins.excalidraw_plugin import ExcalidrawPlugin; \
           e = ExcalidrawPlugin(); e.initialize(); e.open_excalidraw()"
```

## Conclusion

The Excalidraw plugin brings professional diagramming capabilities to Project-AI with minimal overhead. Its hand-drawn aesthetic makes technical diagrams more approachable while maintaining precision and clarity. The plugin's integration with Project-AI's safety systems ensures all diagram operations comply with ethical guidelines, making it a perfect fit for the system's architecture.

Start creating diagrams today to visualize your AI's architecture, document workflows, and communicate complex relationships effectively!
