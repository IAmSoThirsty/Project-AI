# Excalidraw Drawing Workflow Documentation

## Quick Start (30 seconds)

```python
from app.plugins.excalidraw_plugin import ExcalidrawPlugin

# 1. Initialize
excalidraw = ExcalidrawPlugin()
excalidraw.initialize()

# 2. Create diagram
diagram = excalidraw.create_diagram("My First Diagram")

# 3. Open drawing interface
excalidraw.open_excalidraw()

# 4. Draw in browser, then save from Excalidraw menu
# 5. Load downloaded file and save to plugin storage
```

## Complete Workflow

### 1. Desktop Application Workflow

#### Step 1: Plugin Setup
```python
from app.plugins.excalidraw_plugin import ExcalidrawPlugin

# Create plugin with custom data directory
excalidraw = ExcalidrawPlugin(data_dir="data")

# Initialize with safety validation
success = excalidraw.initialize(context={"is_user_order": True})

if not success:
    print("Plugin initialization failed")
else:
    print("Excalidraw ready!")
```

#### Step 2: Create New Diagram
```python
# Create diagram entry
diagram = excalidraw.create_diagram(
    name="System Architecture v2.0",
    description="Updated architecture showing microservices"
)

print(f"Diagram ID: {diagram['id']}")
print(f"Created at: {diagram['created_at']}")
print(f"File path: {diagram['file_path']}")
```

#### Step 3: Open Drawing Interface
```python
# Opens https://excalidraw.com in default browser
excalidraw.open_excalidraw()

# Alternative: Open with specific URL parameters
import webbrowser
webbrowser.open("https://excalidraw.com?theme=dark&gridMode=1")
```

#### Step 4: Create Your Diagram

**In the Excalidraw web interface:**

1. **Choose tools from toolbar:**
   - Rectangle: For boxes/components
   - Ellipse: For processes/states
   - Diamond: For decision points
   - Arrow: For relationships/flows
   - Line: For connections
   - Text: For labels

2. **Draw your diagram:**
   - Click tool, then click-drag on canvas
   - Use selection tool (V or mouse) to move elements
   - Ctrl+Click to multi-select
   - Ctrl+G to group elements
   - Right-click for more options

3. **Style your elements:**
   - Stroke color: Outline color
   - Background: Fill color
   - Stroke width: Line thickness
   - Stroke style: Solid, dashed, dotted
   - Fill style: Solid, hachure, cross-hatch
   - Roughness: Hand-drawn effect intensity

4. **Organize:**
   - Arrange layers: Bring to front/back
   - Align elements: Left, center, right, top, middle, bottom
   - Distribute: Space evenly
   - Group: Ctrl+G (move together)

#### Step 5: Save Your Work

**From Excalidraw interface:**
1. Click hamburger menu (☰)
2. Select "Save to disk"
3. Downloads `.excalidraw` file

**Then in Python:**
```python
# Read downloaded file
import os
downloads_path = os.path.expanduser("~/Downloads")
excalidraw_file = os.path.join(downloads_path, "diagram.excalidraw")

with open(excalidraw_file, 'r') as f:
    content = f.read()

# Save to plugin storage
excalidraw.save_diagram(diagram['id'], content)
print("Diagram saved to plugin storage!")
```

#### Step 6: Export Diagram

**From Excalidraw interface:**
1. Click hamburger menu (☰)
2. Select "Export image"
3. Choose format:
   - PNG: For documentation (supports transparency)
   - SVG: For scaling (vector graphics)
   - Clipboard: Quick paste into docs

4. Configure export:
   - Background: Include or transparent
   - Dark mode: Match theme
   - Embed scene: Include editable data
   - Scale: 1x, 2x, 3x (for high DPI)
   - Only selected: Export selection only

5. Download export

**Record export in plugin:**
```python
# Track export metadata
export_info = excalidraw.export_diagram(diagram['id'], format='png')
print(f"Export recorded: {export_info['file_path']}")

# You can track multiple exports
excalidraw.export_diagram(diagram['id'], 'svg')
excalidraw.export_diagram(diagram['id'], 'json')
```

#### Step 7: Load Existing Diagram

```python
# List all diagrams
diagrams = excalidraw.list_diagrams()
for d in diagrams:
    print(f"- {d['name']} (ID: {d['id']})")

# Load specific diagram
diagram_id = diagrams[0]['id']
content = excalidraw.load_diagram(diagram_id)

# Save to file for editing
with open('diagram_to_edit.excalidraw', 'w') as f:
    f.write(content)

# Open file in Excalidraw:
# 1. Go to https://excalidraw.com
# 2. Click hamburger menu (☰) → Open
# 3. Select diagram_to_edit.excalidraw
# 4. Edit and re-save
```

### 2. Web Application Workflow

#### Step 1: Add Component to Page

```tsx
// app/diagrams/page.tsx
import ExcalidrawComponent from '@/components/ExcalidrawComponent';

export default function DiagramsPage() {
  const handleSave = (diagram, content) => {
    console.log('Saved:', diagram.name);
    // Optionally: Send to backend API
  };

  const handleExport = (format, data) => {
    // Handle export (download file, send to server, etc.)
    const blob = new Blob([data], { type: `image/${format}` });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `diagram.${format}`;
    a.click();
  };

  return (
    <div style={{ height: '100vh' }}>
      <h1>Visual Diagrams</h1>
      <ExcalidrawComponent
        height="calc(100vh - 100px)"
        darkMode={false}
        onSave={handleSave}
        onExport={handleExport}
      />
    </div>
  );
}
```

#### Step 2: Create and Edit Diagrams

**In the web interface:**

1. **Click "+ New Diagram"**
   - Enter name: "User Authentication Flow"
   - Enter description (optional)
   - Click "Create"

2. **Draw in embedded Excalidraw**
   - All drawing tools available
   - Real-time editing
   - Auto-saves to browser localStorage

3. **Save Diagram**
   - Click "💾 Save" button
   - Triggers `onSave` callback
   - Saves to localStorage
   - Optionally syncs to server

4. **Export Diagram**
   - Click "Export PNG", "Export SVG", or "Export JSON"
   - Downloads file
   - Triggers `onExport` callback

5. **Switch Diagrams**
   - Use dropdown to select different diagram
   - Loads from localStorage
   - Continue editing

#### Step 3: Advanced Web Integration

**Persist to Backend:**
```tsx
const handleSave = async (diagram, content) => {
  try {
    const response = await fetch('/api/diagrams', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: diagram.id,
        name: diagram.name,
        content: content,
      }),
    });
    
    if (response.ok) {
      console.log('Saved to server');
    }
  } catch (error) {
    console.error('Save failed:', error);
  }
};
```

**Load from Backend:**
```tsx
const [initialDiagram, setInitialDiagram] = useState(null);

useEffect(() => {
  fetch('/api/diagrams/123')
    .then(res => res.json())
    .then(diagram => setInitialDiagram(diagram));
}, []);

return (
  <ExcalidrawComponent
    initialDiagram={initialDiagram}
    onSave={handleSave}
  />
);
```

## Common Workflows

### Workflow 1: Architecture Documentation

**Goal:** Create system architecture diagram for documentation

```python
# Setup
excalidraw = ExcalidrawPlugin()
excalidraw.initialize()

# Create
arch_diagram = excalidraw.create_diagram(
    name="Project-AI Architecture v3.0",
    description="System components and their relationships"
)

# Draw
excalidraw.open_excalidraw()
# 1. Add rectangles for each component
# 2. Add arrows showing data flow
# 3. Color-code by layer (red=security, blue=UI, green=data)
# 4. Add text labels
# 5. Add legend

# Save downloaded file
with open('downloads/architecture.excalidraw') as f:
    excalidraw.save_diagram(arch_diagram['id'], f.read())

# Export PNG for README
excalidraw.export_diagram(arch_diagram['id'], 'png')
# Copy downloaded PNG to docs/images/architecture.png
```

### Workflow 2: User Flow Diagram

**Goal:** Document user interaction flow

```python
# Create
flow_diagram = excalidraw.create_diagram(
    name="User Authentication Flow",
    description="Step-by-step user login process"
)

# Draw
excalidraw.open_excalidraw()
# 1. Use diamonds for decision points
# 2. Use rectangles for actions
# 3. Use arrows for flow direction
# 4. Add yes/no labels on decision branches
# 5. Use colors for success (green) vs error (red) paths

# Save and export
with open('downloads/user-flow.excalidraw') as f:
    excalidraw.save_diagram(flow_diagram['id'], f.read())

excalidraw.export_diagram(flow_diagram['id'], 'png')
```

### Workflow 3: Data Model Diagram

**Goal:** Visualize database schema

```python
# Create
data_diagram = excalidraw.create_diagram(
    name="Database Schema",
    description="Entity relationships and data model"
)

# Draw
excalidraw.open_excalidraw()
# 1. Rectangle for each table
# 2. List fields inside rectangle
# 3. Lines for relationships
# 4. Add cardinality labels (1:1, 1:N, N:M)
# 5. Group related tables

# Save
with open('downloads/schema.excalidraw') as f:
    excalidraw.save_diagram(data_diagram['id'], f.read())
```

### Workflow 4: Iterative Updates

**Goal:** Update existing diagram with new information

```python
# Load existing
diagrams = excalidraw.list_diagrams()
arch_diagram = next(d for d in diagrams if d['name'] == 'System Architecture')

# Export to file for editing
content = excalidraw.load_diagram(arch_diagram['id'])
with open('temp_edit.excalidraw', 'w') as f:
    f.write(content)

# Open and edit
excalidraw.open_excalidraw()
# Load temp_edit.excalidraw from Excalidraw menu
# Make updates
# Save back to disk

# Re-import updated version
with open('downloads/temp_edit.excalidraw') as f:
    updated_content = f.read()

excalidraw.save_diagram(arch_diagram['id'], updated_content)
print("Diagram updated!")
```

## Tips & Tricks

### Drawing Efficiency
- **Keyboard shortcuts:**
  - V: Selection tool
  - R: Rectangle
  - D: Diamond
  - E: Ellipse
  - A: Arrow
  - L: Line
  - T: Text
  - Ctrl+D: Duplicate
  - Ctrl+G: Group
  - Ctrl+Z: Undo
  - Ctrl+Y: Redo

- **Quick styling:**
  - Click element → Stroke color picker (top toolbar)
  - Double-click → Edit text
  - Shift+drag → Maintain aspect ratio
  - Alt+drag → Duplicate while moving

### Organization
- **Layer groups:**
  - Group related elements (Ctrl+G)
  - Name groups for clarity
  - Lock groups to prevent accidental changes

- **Color coding:**
  - Consistent colors for element types
  - Example: Blue=UI, Green=Backend, Red=Security
  - Add legend for clarity

- **Alignment:**
  - Use grid (View → Show grid)
  - Enable snap to grid
  - Use alignment tools (top toolbar)

### Collaboration
- **Version control:**
  - Commit `.excalidraw` files to Git
  - Meaningful commit messages
  - Include exports (PNG) for easy review

- **Sharing:**
  - Export PNG for presentations
  - Export SVG for print materials
  - Share `.excalidraw` for editing

## Troubleshooting

### Issue: Browser doesn't open
```python
# Manual open
import webbrowser
webbrowser.open("https://excalidraw.com")
```

### Issue: Can't save diagram
```python
# Check write permissions
import os
print(f"Can write: {os.access(excalidraw.diagrams_dir, os.W_OK)}")

# Check directory exists
print(f"Exists: {excalidraw.diagrams_dir.exists()}")

# Manually create if needed
excalidraw.diagrams_dir.mkdir(parents=True, exist_ok=True)
```

### Issue: Diagram not loading in Excalidraw
- Verify file is valid JSON
- Check Excalidraw version compatibility
- Try opening in text editor to check for corruption

### Issue: Export button not working (web)
- Check browser console for errors
- Verify iframe has clipboard permissions
- Try different browser

## Best Practices

1. **Naming:** Use descriptive names with versions
2. **Descriptions:** Add purpose and context
3. **Regular saves:** Save frequently during drawing
4. **Exports:** Keep PNG exports for easy viewing
5. **Version control:** Commit source `.excalidraw` files
6. **Documentation:** Update diagrams when code changes
7. **Templates:** Create reusable templates for common diagrams
8. **Backups:** Regularly backup diagram directory

## Next Steps

- Explore sample diagrams in `data/excalidraw_diagrams/samples/`
- Read full guide in `EXCALIDRAW_GUIDE.md`
- Create your first diagram following Quick Start
- Integrate into your documentation workflow
