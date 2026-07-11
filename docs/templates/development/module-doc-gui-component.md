---
# ═══════════════════════════════════════════════════════════════════════════
# GUI COMPONENT MODULE DOCUMENTATION TEMPLATE
# Document Type: Module Documentation (PyQt6 UI Components)
# Target: src/app/gui/ components
# Schema Version: 2.0.0
# ═══════════════════════════════════════════════════════════════════════════

# Universal Fields (Required)
title: "<%tp.file.title%>"
id: "<%tp.file.title.toLowerCase().replace(/\s+/g, '-')%>"
type: "api_reference"
version: "1.0.0"
created_date: "<%tp.date.now("YYYY-MM-DD")%>"
updated_date: "<%tp.date.now("YYYY-MM-DD")%>"
status: "draft"
author:
  name: "<%tp.user.name || 'Documentation Team'%>"
  email: ""
  github: ""

# Domain-Specific Fields
category: "frontend"
tags:
  - "module"
  - "gui"
  - "pyqt6"
  - "ui-component"
  - "architecture/desktop"
technologies:
  - "Python"
  - "PyQt6"
  - "Qt Signals"
classification: "internal"
audience:
  - "developer"
  - "architect"

# Component-Specific Fields
component_name: ""
component_type: "QWidget"
parent_class: "QWidget/QMainWindow/QDialog"
signals: []
slots: []

# Quality Metadata
review_status:
  reviewed: false
  reviewers: []
  review_date: null
  approved: false
test_coverage:
  has_tests: false
  coverage_percent: 0
  test_files: []

# Discovery & SEO
keywords:
  - "pyqt6 component"
  - "gui widget"
  - "user interface"
summary: "Documentation for <% await tp.system.prompt('Component name (e.g., LeatherBookDashboard):') %> PyQt6 UI component including widget hierarchy, signals/slots, and styling."

# Relationships
related_docs: []
supersedes: null
---

# <%tp.file.title%>

> **Component Type:** PyQt6 Widget
> **Location:** `src/app/gui/`
> **Parent Class:** <%`${await tp.system.prompt('Parent class (QWidget/QMainWindow/QDialog):') || 'QWidget'}`%>
> **Last Updated:** <%tp.date.now("YYYY-MM-DD")%>

---

## Table of Contents

1. [Component Overview](#component-overview)
2. [Widget Hierarchy](#widget-hierarchy)
3. [API Reference](#api-reference)
4. [Signals and Slots](#signals-and-slots)
5. [Layout and Styling](#layout-and-styling)
6. [Event Handling](#event-handling)
7. [Usage Examples](#usage-examples)
8. [Integration Patterns](#integration-patterns)
9. [Testing GUI Components](#testing-gui-components)
10. [Accessibility](#accessibility)
11. [Related Components](#related-components)

---

## Component Overview

### Purpose

**What:** [One-sentence description of the UI component]

**Why:** [User experience justification - what UX need does this fulfill?]

**When:** [When in the user workflow does this component appear?]

**Where:** [Where in the application window hierarchy?]

**Who:** [Which user roles interact with this component?]

### Visual Preview

```
┌──────────────────────────────────────────────────┐
│  Component Name                          [X] [ ] │
├──────────────────────────────────────────────────┤
│                                                  │
│  [Sketch of component layout]                   │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Button 1 │  │ Button 2 │  │ Button 3 │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│                                                  │
│  Text Area:                                     │
│  ┌────────────────────────────────────────┐    │
│  │                                        │    │
│  │                                        │    │
│  └────────────────────────────────────────┘    │
│                                                  │
└──────────────────────────────────────────────────┘
```

### Key Features

- [ ] **Feature 1:** [Description]
- [ ] **Feature 2:** [Description]
- [ ] **Feature 3:** [Description]

### UI Context

| Context | Value |
|---------|-------|
| **Window Type** | Main Window / Dialog / Panel |
| **Modal** | Yes / No |
| **Resizable** | Yes / No |
| **Minimum Size** | [Width x Height] |
| **Theme** | Leather Book / Tron / Custom |

---

## Widget Hierarchy

### Component Tree

```
ComponentName (QWidget)
├── QVBoxLayout (main_layout)
│   ├── QLabel (title_label)
│   ├── QHBoxLayout (button_row)
│   │   ├── QPushButton (btn_action1)
│   │   ├── QPushButton (btn_action2)
│   │   └── QPushButton (btn_action3)
│   ├── QTextEdit (text_area)
│   └── QHBoxLayout (status_row)
│       ├── QLabel (status_icon)
│       └── QLabel (status_text)
```

### Widget Registry

| Widget | Type | Name | Purpose |
|--------|------|------|---------|
| Main Container | `QWidget` | `self` | Root component |
| Layout | `QVBoxLayout` | `main_layout` | Primary layout manager |
| Label | `QLabel` | `title_label` | Component title |
| Button | `QPushButton` | `btn_action1` | [Action description] |

---

## API Reference

### Class Definition

#### Class: `ComponentName(QWidget)`

**Inheritance:** `QWidget` → `ComponentName`

**Description:** [Detailed component description]

**Constructor:**

```python
def __init__(
    self,
    parent: QWidget = None,
    title: str = "Default Title",
    **kwargs
):
    """
    Initialize the component.

    Args:
        parent (QWidget, optional): Parent widget for Qt hierarchy
        title (str): Display title for the component
        **kwargs: Additional configuration options

    Raises:
        TypeError: If parent is not QWidget or None
    """
    super().__init__(parent)
    self.title = title
    self._init_ui()
    self._connect_signals()
```

**Example:**
```python
from PyQt6.QtWidgets import QApplication, QWidget
from app.gui.component_name import ComponentName

app = QApplication([])
window = QWidget()

component = ComponentName(
    parent=window,
    title="My Component"
)

window.show()
app.exec()
```

---

### Public Methods

#### `set_title(self, title: str) -> None`

**Purpose:** Update the component title dynamically

**Parameters:**
- `title` (`str`): New title text

**Returns:** `None`

**Side Effects:** Updates `title_label` text and emits `title_changed` signal

**Example:**
```python
component.set_title("Updated Title")
```

---

#### `clear(self) -> None`

**Purpose:** Reset component to initial state

**Parameters:** None

**Returns:** `None`

**Side Effects:**
- Clears all text fields
- Resets buttons to default state
- Emits `cleared` signal

**Example:**
```python
component.clear()
```

---

### Protected Methods

#### `_init_ui(self) -> None`

**Purpose:** Initialize all UI widgets and layouts (called by constructor)

**Pattern:**
```python
def _init_ui(self):
    # 1. Create main layout
    self.main_layout = QVBoxLayout(self)

    # 2. Create widgets
    self.title_label = QLabel(self.title)

    # 3. Apply styling
    self._apply_styles()

    # 4. Add to layout
    self.main_layout.addWidget(self.title_label)

    # 5. Set layout
    self.setLayout(self.main_layout)
```

---

#### `_connect_signals(self) -> None`

**Purpose:** Connect all signal/slot relationships

**Pattern:**
```python
def _connect_signals(self):
    # Internal connections
    self.btn_action1.clicked.connect(self._on_action1_clicked)

    # Component signals to internal handlers
    self.some_signal.connect(self._handle_signal)
```

---

#### `_apply_styles(self) -> None`

**Purpose:** Apply Qt stylesheet to all widgets

**Pattern:**
```python
def _apply_styles(self):
    self.setStyleSheet("""
        QWidget {
            background-color: #1a1a1a;
            color: #ffffff;
            font-family: 'Courier New';
        }
        QPushButton {
            background-color: #00ff00;
            border: 2px solid #00aa00;
            padding: 10px;
        }
    """)
```

---

## Signals and Slots

### Signals Emitted

| Signal | Parameters | When Emitted | Purpose |
|--------|------------|--------------|---------|
| `action_triggered` | `str: action_name` | When action button clicked | Notify parent of user action |
| `data_changed` | `dict: new_data` | When component data modified | Propagate state changes |
| `error_occurred` | `str: error_message` | On validation failure | Report errors to parent |

**Signal Definitions:**
```python
from PyQt6.QtCore import pyqtSignal

class ComponentName(QWidget):
    # Define signals as class-level attributes
    action_triggered = pyqtSignal(str)
    data_changed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
```

**Signal Usage:**
```python
# Emitting a signal
self.action_triggered.emit("save_action")

# With data
self.data_changed.emit({"key": "value", "count": 42})
```

---

### Slots (Public Methods)

| Slot | Parameters | Purpose | Connected By |
|------|------------|---------|--------------|
| `on_data_received(data: dict)` | `dict` | Process incoming data | Parent component |
| `enable_actions(enabled: bool)` | `bool` | Enable/disable buttons | State manager |

**Slot Implementation:**
```python
def on_data_received(self, data: dict):
    """
    Slot to handle data from parent component.

    Args:
        data (dict): Data to process and display
    """
    # Validate
    if not isinstance(data, dict):
        self.error_occurred.emit("Invalid data type")
        return

    # Process
    self._update_display(data)

    # Acknowledge
    self.data_changed.emit(data)
```

---

### Signal Connection Patterns

**Parent-to-Child:**
```python
# In parent component
parent.data_ready.connect(child_component.on_data_received)
```

**Child-to-Parent:**
```python
# In parent component
child_component.action_triggered.connect(parent._handle_child_action)
```

**Sibling Components:**
```python
# In common parent
component_a.data_changed.connect(component_b.on_data_received)
component_b.response_ready.connect(component_a.on_response)
```

---

## Layout and Styling

### Layout Strategy

**Primary Layout:** <%`${await tp.system.prompt('Primary layout type (QVBoxLayout/QHBoxLayout/QGridLayout):') || 'QVBoxLayout'}`%>

**Layout Hierarchy:**
```python
main_layout = QVBoxLayout()
├── top_section = QHBoxLayout()
├── middle_section = QGridLayout()
└── bottom_section = QHBoxLayout()
```

**Spacing and Margins:**
```python
self.main_layout.setContentsMargins(20, 20, 20, 20)  # left, top, right, bottom
self.main_layout.setSpacing(10)  # pixels between widgets
```

---

### Stylesheet

**Theme:** <%`${await tp.system.prompt('Theme (Leather Book/Tron/Custom):') || 'Leather Book'}`%>

**Colors:**
```python
# Color Palette
BACKGROUND = "#1a1a1a"
FOREGROUND = "#ffffff"
PRIMARY = "#00ff00"  # Tron green
SECONDARY = "#00ffff"  # Tron cyan
ACCENT = "#ffd700"   # Gold
ERROR = "#ff0000"
```

**Component Stylesheet:**
```python
COMPONENT_STYLE = """
QWidget#ComponentName {
    background-color: #1a1a1a;
    border: 2px solid #00ff00;
    border-radius: 10px;
}

QLabel#title_label {
    color: #00ffff;
    font-size: 18pt;
    font-weight: bold;
    font-family: 'Courier New';
}

QPushButton {
    background-color: transparent;
    border: 2px solid #00ff00;
    color: #00ff00;
    padding: 10px 20px;
    font-size: 12pt;
    border-radius: 5px;
}

QPushButton:hover {
    background-color: #00ff00;
    color: #000000;
}

QPushButton:pressed {
    background-color: #00aa00;
}

QPushButton:disabled {
    border-color: #555555;
    color: #555555;
}
"""
```

---

## Event Handling

### Mouse Events

```python
def mousePressEvent(self, event: QMouseEvent):
    """Handle mouse press events."""
    if event.button() == Qt.MouseButton.LeftButton:
        # Handle left click
        pass
    super().mousePressEvent(event)

def mouseDoubleClickEvent(self, event: QMouseEvent):
    """Handle double-click events."""
    # Custom double-click logic
    pass
```

### Keyboard Events

```python
def keyPressEvent(self, event: QKeyEvent):
    """Handle keyboard input."""
    if event.key() == Qt.Key.Key_Return:
        # Handle Enter key
        self._on_submit()
    elif event.key() == Qt.Key.Key_Escape:
        # Handle Escape key
        self.clear()
    else:
        super().keyPressEvent(event)
```

### Custom Events

```python
def event(self, e: QEvent) -> bool:
    """Override to handle custom events."""
    if e.type() == QEvent.Type.User:
        # Handle custom event
        return True
    return super().event(e)
```

---

## Usage Examples

### Example 1: Basic Instantiation

```python
from PyQt6.QtWidgets import QApplication
from app.gui.component_name import ComponentName

app = QApplication([])

# Create component
component = ComponentName(title="Example Component")

# Connect signals
component.action_triggered.connect(
    lambda action: print(f"Action triggered: {action}")
)

# Show component
component.show()

# Run event loop
app.exec()
```

---

### Example 2: Integration with Main Window

```python
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from app.gui.component_name import ComponentName

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create central widget
        central = QWidget()
        layout = QVBoxLayout(central)

        # Add component
        self.component = ComponentName(parent=central)
        layout.addWidget(self.component)

        # Connect signals
        self.component.action_triggered.connect(self._handle_action)

        self.setCentralWidget(central)

    def _handle_action(self, action: str):
        print(f"Main window received action: {action}")
```

---

### Example 3: Programmatic Updates

```python
# Update component state
component.set_title("New Title")

# Send data to component
component.on_data_received({
    "status": "success",
    "message": "Operation completed"
})

# Enable/disable actions
component.enable_actions(False)  # Disable all buttons
```

---

## Integration Patterns

### Pattern 1: Event-Driven Updates

```python
# Component receives data via signal
parent.data_updated.connect(component.on_data_received)

# Component processes and emits result
def on_data_received(self, data):
    result = self._process(data)
    self.processing_complete.emit(result)
```

### Pattern 2: Timer-Based Polling

```python
from PyQt6.QtCore import QTimer

class ComponentName(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup polling timer
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._poll_data)
        self.poll_timer.start(1000)  # Poll every 1 second

    def _poll_data(self):
        # Fetch and update data
        pass
```

### Pattern 3: Dialog Interaction

```python
def show_configuration_dialog(self):
    """Show modal dialog for component configuration."""
    dialog = ConfigurationDialog(self)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        config = dialog.get_config()
        self.apply_config(config)
```

---

## Testing GUI Components

### Test File Location

`tests/gui/test_[component_name].py`

### Testing Strategy

**Use pytest-qt plugin:**
```bash
pip install pytest-qt
```

**Example Test:**
```python
import pytest
from PyQt6.QtCore import Qt
from app.gui.component_name import ComponentName

@pytest.fixture
def component(qtbot):
    """Fixture to create component instance."""
    widget = ComponentName()
    qtbot.addWidget(widget)
    return widget

def test_component_initialization(component):
    """Verify component initializes correctly."""
    assert component.title == "Default Title"
    assert component.isVisible() is False

def test_signal_emission(component, qtbot):
    """Verify signals are emitted on user action."""
    with qtbot.waitSignal(component.action_triggered, timeout=1000) as blocker:
        component.btn_action1.click()

    assert blocker.args[0] == "action1"

def test_slot_response(component):
    """Verify slot handles data correctly."""
    test_data = {"key": "value"}
    component.on_data_received(test_data)

    # Verify component updated
    assert component.current_data == test_data
```

### Visual Regression Testing

```python
def test_component_appearance(component, qtbot):
    """Take screenshot for visual regression testing."""
    component.show()
    qtbot.waitExposed(component)

    # Capture screenshot
    pixmap = component.grab()
    # Compare against baseline (manual process)
```

---

## Accessibility

### Keyboard Navigation

- **Tab Order:** Properly set with `setTabOrder(widget1, widget2)`
- **Shortcuts:** Alt+[Key] for button access
- **Focus Indicators:** Visible focus rectangles

```python
# Set tab order
self.setTabOrder(self.btn_action1, self.btn_action2)
self.setTabOrder(self.btn_action2, self.text_area)

# Set shortcuts
self.btn_action1.setShortcut("Alt+S")  # Alt+S for Save
```

### Screen Reader Support

```python
# Set accessible names and descriptions
self.btn_action1.setAccessibleName("Save Button")
self.btn_action1.setAccessibleDescription("Save current changes to file")

# Set tooltips
self.btn_action1.setToolTip("Save changes (Alt+S)")
```

---

## Related Components

### Parent Components

- [[gui-main-window]]: Container for this component
- [[gui-dashboard]]: Dashboard integration

### Child Components

- [[gui-subcomponent-1]]: Embedded widget
- [[gui-dialog-config]]: Configuration dialog

### Sibling Components

- [[gui-peer-component]]: Related UI component
- [[gui-status-panel]]: Status display integration

### Related Documentation

- [[architecture-doc-pyqt6-patterns]]: GUI design patterns
- [[guide-developer-reference]]: GUI API reference

---

## Changelog

### Version 1.0.0 (<%tp.date.now("YYYY-MM-DD")%>)

- Initial documentation creation
- Complete API reference
- Signal/slot documentation
- Testing guidance established

---

**Document Status:** <%`${await tp.system.prompt('Document status (draft/review/active):') || 'draft'}`%>
**Next Review Date:** [YYYY-MM-DD]
**Maintainer:** <%tp.user.name || 'Documentation Team'%>

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
