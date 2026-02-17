# 3D Visualization Integration

This document describes the 3D visualization prototype for Project-AI's GUI.

## Overview

The `visualization_3d.py` module provides 3D rendering capabilities for visualizing:

- AI system component relationships
- Persona state in 3D space
- Agent network topology
- Memory expansion graphs

## Components

### Visualization3DWidget

Base class providing 3D projection and rendering using PyQt6's QPainter with perspective transformations.

**Features:**

- Rotation animation (20 FPS)
- Perspective projection
- Zoom and elevation controls
- Node and connection rendering with glow effects

### AISystemVisualization3D

Specialized visualization showing Project-AI's core systems:

- AI Core (center, magenta)
- Four Laws System (green)
- Persona System (cyan)
- Memory System (yellow)
- Learning System (red)
- Agent System (blue)

## Usage

```python
from app.gui.visualization_3d import AISystemVisualization3D

# Create widget

viz = AISystemVisualization3D(parent)

# Customize

viz.set_zoom(1.5)
viz.set_elevation(45)

# Add custom nodes

viz.add_node(x, y, z, "Custom Node", QColor(255, 0, 0))
viz.add_connection(0, 1)
```

## Integration Points

### Dashboard Integration

To integrate into the leather book dashboard:

1. Import the visualization:

```python
from app.gui.visualization_3d import AISystemVisualization3D
```

1. Add to layout:

```python
self.viz_3d = AISystemVisualization3D(self)
layout.addWidget(self.viz_3d)
```

1. Control visibility:

```python

# Toggle between 2D and 3D views

self.viz_3d.setVisible(show_3d)
```

### Future Enhancements

- [ ] Mouse interaction (rotate, zoom with mouse)
- [ ] VR headset support via PyOpenGL
- [ ] WebGL export for web frontend
- [ ] Real-time data binding to AI system state
- [ ] Particle effects for data flow visualization
- [ ] Stereoscopic 3D mode

## Performance

The visualization uses CPU-based rendering via QPainter. For production:

- Consider PyOpenGL for GPU acceleration
- Add LOD (Level of Detail) for complex scenes
- Implement culling for off-screen nodes

## Testing

Basic visualization test:
```bash
python -c "
from PyQt6.QtWidgets import QApplication
from app.gui.visualization_3d import AISystemVisualization3D
import sys

app = QApplication(sys.argv)
viz = AISystemVisualization3D()
viz.show()
sys.exit(app.exec())
"
```
