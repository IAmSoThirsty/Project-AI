---
title: "SettingsDialog - Persistent Theme and UI Configuration Component"
id: "settings-dialog-gui"
type: "technical-reference"
version: "1.0.0"
created_date: "2026-04-20"
updated_date: "2026-04-20"
status: "production"
author: "AGENT-044"
contributors: ["GUI Team", "Desktop Application Team"]
category: "gui-documentation"
tags: ["pyqt6", "gui", "settings", "configuration", "theme", "ui-scale", "persistence"]
technologies: ["Python 3.11+", "PyQt6 6.4+", "JSON"]
related_docs:
  - "leather_book_interface"
  - "dashboard"
  - "user-manager"
  - "configuration-management"
description: "Comprehensive documentation for the SettingsDialog PyQt6 component - simple modal settings dialog with theme selection, UI font size scaling, and JSON-based persistence for application-wide configuration"
security_classification: "internal"
review_status: "peer-reviewed"
audience: ["developers", "gui-developers", "configuration-engineers"]
---

# SettingsDialog - Persistent Theme and UI Configuration Component

**Module:** `src/app/gui/settings_dialog.py`
**Class:** `SettingsDialog`
**Lines of Code:** 85
**Purpose:** Modal dialog for theme and UI scaling configuration with JSON persistence

---

## Table of Contents

1. [Component Overview](#component-overview)
2. [UI Layout Architecture](#ui-layout-architecture)
3. [Core Architecture](#core-architecture)
4. [API Reference](#api-reference)
5. [Persistence System](#persistence-system)
6. [Integration Patterns](#integration-patterns)
7. [Usage Examples](#usage-examples)
8. [Styling Guide](#styling-guide)
9. [Security Considerations](#security-considerations)
10. [Accessibility Considerations](#accessibility-considerations)
11. [Troubleshooting](#troubleshooting)

---

## Component Overview

### Purpose

The **SettingsDialog** provides a lightweight, modal configuration interface for application-wide settings. It currently manages two critical UI preferences: theme selection (light/dark) and UI font size scaling (8-20 points). Settings are persisted to JSON and loaded on application startup, ensuring user preferences survive across sessions.

### Key Features

- **Modal Dialog**: Blocks interaction with parent window until closed
- **Theme Selection**: Light/dark theme switching via QComboBox
- **UI Font Scaling**: Granular font size control (8-20 points) via QSpinBox
- **JSON Persistence**: Settings saved to `data/settings.json`
- **Default Handling**: Graceful fallback to defaults when settings file missing
- **Error Resilience**: Logging for load/save failures without crashing
- **Simple UX**: Two controls with OK/Cancel standard buttons
- **Stateless Loading**: Static methods for configuration access from any component

### UX Goals

1. **Simplicity**: Minimal, focused settings without overwhelming options
2. **Immediate Feedback**: Changes visible after dialog closes (requires restart for some themes)
3. **Non-Destructive**: Cancel button discards changes
4. **Accessibility**: Font size scaling assists users with vision impairments
5. **Persistence**: Settings survive application restarts
6. **Discoverability**: Clear labels and standard dialog patterns

### Design Philosophy

The SettingsDialog follows the **single-responsibility principle**—it manages only global UI preferences, not domain-specific configuration (e.g., AI persona settings, security policies). This separation ensures the dialog remains fast, maintainable, and testable. Future enhancements can extend the dialog with additional tabs or migrate to a dedicated settings panel.

---

## UI Layout Architecture

### Visual Structure

```
┌─────────────────────────────────────────┐
│  Settings                               │ ← Window Title
├─────────────────────────────────────────┤
│                                         │
│  Theme:                                 │ ← QLabel
│  ┌───────────────────────┐             │
│  │ light             ▼   │             │ ← QComboBox (light/dark)
│  └───────────────────────┘             │
│                                         │
│  UI font size:                          │ ← QLabel
│  ┌───────────────────────┐             │
│  │       10         ▲▼   │             │ ← QSpinBox (8-20 range)
│  └───────────────────────┘             │
│                                         │
├─────────────────────────────────────────┤
│              [  OK  ] [Cancel]          │ ← QDialogButtonBox
└─────────────────────────────────────────┘
```

### Layout Details

- **Layout Type**: `QVBoxLayout` (vertical stacking)
- **Controls**:
  - 2 QLabel widgets (descriptive text)
  - 1 QComboBox (theme selector)
  - 1 QSpinBox (font size slider)
  - 1 QDialogButtonBox (OK/Cancel)
- **Spacing**: Default PyQt6 spacing (no custom margins)
- **Modality**: `setModal(True)` blocks parent window interaction
- **Size**: Auto-sized based on content (no fixed dimensions)

### Widget Hierarchy

```
SettingsDialog (QDialog)
└── QVBoxLayout
    ├── QLabel("Theme:")
    ├── QComboBox (theme_select)
    │   ├── "light"
    │   └── "dark"
    ├── QLabel("UI font size:")
    ├── QSpinBox (size_spin)
    │   └── Range: 8-20
    └── QDialogButtonBox
        ├── OK button → accept()
        └── Cancel button → reject()
```

---

## Core Architecture

### Class Design

**Class:** `SettingsDialog(QDialog)`

**Inheritance Chain:**
```
QObject → QWidget → QDialog → SettingsDialog
```

**Responsibilities:**
1. Render modal settings UI
2. Validate input ranges (8-20 for font size)
3. Provide `get_values()` API for retrieving user selections
4. Expose static methods for persistent storage access

**Dependencies:**
- `PyQt6.QtWidgets`: UI components (QDialog, QComboBox, QSpinBox, QDialogButtonBox)
- `json`: Settings serialization/deserialization
- `os`: File path management and `DATA_DIR` environment variable
- `logging`: Error reporting for I/O failures

### Data Model

**Configuration Schema:**
```json
{
  "theme": "light | dark",
  "ui_scale": 8-20 (integer)
}
```

**Example:**
```json
{
  "theme": "dark",
  "ui_scale": 12
}
```

**Defaults:**
```json
{
  "theme": "light",
  "ui_scale": 10
}
```

### File System Structure

```
data/
└── settings.json  ← Configuration persistence
```

**Environment Variable:**
- `DATA_DIR`: Overrides default `data/` directory (useful for testing)

### State Management

**Instance State:**
- `theme_select`: QComboBox holding current theme selection
- `size_spin`: QSpinBox holding current font size value

**Persistence State:**
- Loaded via `load_settings()` static method on application startup
- Saved via `save_settings(dict)` static method after dialog acceptance
- No in-memory caching—direct file I/O on each call

### Error Handling Strategy

**Load Failures:**
1. Log warning to `logging` module
2. Return default settings dict
3. Application continues with defaults

**Save Failures:**
1. Log error to `logging` module
2. Return `False` to indicate failure
3. UI can optionally show error message to user

**Philosophy:** Settings are **non-critical**—failures should never crash the application. Users can always reconfigure via dialog.

---

## API Reference

### Constructor

#### `__init__(parent=None, current=None)`

Initializes the settings dialog with optional current settings.

**Parameters:**
- `parent` (QWidget, optional): Parent window for modality. Default: `None`
- `current` (dict, optional): Current settings dict with keys `theme` and `ui_scale`. Default: `None` (uses defaults)

**Behavior:**
- If `current` is provided, pre-populates controls with existing values
- If `current` is `None`, uses defaults: `theme="light"`, `ui_scale=10`
- Sets window title to "Settings"
- Enables modal mode (blocks parent interaction)
- Connects OK/Cancel buttons to `accept()`/`reject()` slots

**Example:**
```python
settings = SettingsDialog.load_settings()
dialog = SettingsDialog(parent=main_window, current=settings)
```

---

### Instance Methods

#### `get_values() -> dict`

Retrieves current settings values from UI controls.

**Returns:**
- `dict`: Settings dictionary with structure:
  ```python
  {
      "theme": str,      # "light" or "dark"
      "ui_scale": int    # 8-20
  }
  ```

**Example:**
```python
if dialog.exec() == QDialog.DialogCode.Accepted:
    new_settings = dialog.get_values()
    # new_settings = {"theme": "dark", "ui_scale": 14}
```

**Thread Safety:** Must be called from GUI thread only.

---

### Static Methods

#### `load_settings() -> dict`

Loads settings from `data/settings.json` or returns defaults on failure.

**Returns:**
- `dict`: Settings dictionary (always succeeds with defaults as fallback)

**Behavior:**
1. Creates `DATA_DIR` if missing (`os.makedirs(DATA_DIR, exist_ok=True)`)
2. If `settings.json` exists, parses JSON
3. On parse errors or missing file, logs warning and returns defaults
4. Defaults: `{"theme": "light", "ui_scale": 10}`

**Example:**
```python
# Application startup
settings = SettingsDialog.load_settings()
app.setStyleSheet(get_theme_stylesheet(settings['theme']))
app.setFont(QFont("Arial", settings['ui_scale']))
```

**Error Cases:**
- Missing file → returns defaults
- Invalid JSON → returns defaults
- I/O errors → returns defaults
- All errors logged to `logging.warning()`

---

#### `save_settings(settings: dict) -> bool`

Persists settings dictionary to `data/settings.json`.

**Parameters:**
- `settings` (dict): Settings dictionary with `theme` and `ui_scale` keys

**Returns:**
- `bool`: `True` on success, `False` on I/O errors

**Behavior:**
1. Creates `DATA_DIR` if missing
2. Writes JSON with 2-space indentation
3. Uses UTF-8 encoding
4. Logs errors to `logging.error()` on failure

**Example:**
```python
new_settings = {"theme": "dark", "ui_scale": 12}
if SettingsDialog.save_settings(new_settings):
    print("Settings saved successfully")
else:
    QMessageBox.warning(None, "Error", "Failed to save settings")
```

**File Format:**
```json
{
  "theme": "dark",
  "ui_scale": 12
}
```

---

## Persistence System

### Storage Format

**File:** `data/settings.json`
**Format:** JSON (UTF-8 encoded)
**Indentation:** 2 spaces
**Encoding:** UTF-8 with `encoding="utf-8"` explicit parameter

### Data Directory Management

**Environment Variable:**
```python
DATA_DIR = os.getenv("DATA_DIR", "data")
```

**Creation Strategy:**
- Both `load_settings()` and `save_settings()` ensure directory exists
- Uses `os.makedirs(DATA_DIR, exist_ok=True)` to prevent race conditions
- Safe for concurrent calls from multiple threads (though UI should be single-threaded)

### Validation Strategy

**Current Implementation:**
- **No validation** on load—assumes JSON structure is correct
- Relies on UI controls to enforce valid ranges (QSpinBox range 8-20)
- Missing keys fall back to defaults via `.get()` method

**Recommended Enhancement:**
```python
# Add to load_settings()
loaded = json.load(f)
if "theme" not in loaded or loaded["theme"] not in ["light", "dark"]:
    loaded["theme"] = "light"
if "ui_scale" not in loaded or not (8 <= loaded["ui_scale"] <= 20):
    loaded["ui_scale"] = 10
return loaded
```

### Migration Strategy

**Future Schema Changes:**
1. Add new keys with default values in `load_settings()`
2. Preserve backward compatibility by using `.get(key, default)`
3. Optionally migrate old format on save:
   ```python
   def save_settings(settings):
       # Ensure new fields exist
       settings.setdefault("new_field", default_value)
       # Save with complete schema
   ```

---

## Integration Patterns

### Pattern 1: Application Startup

```python
# main.py
from PyQt6.QtWidgets import QApplication
from app.gui.settings_dialog import SettingsDialog

app = QApplication(sys.argv)

# Load settings
settings = SettingsDialog.load_settings()

# Apply theme
if settings['theme'] == 'dark':
    app.setStyleSheet(DARK_THEME_CSS)
else:
    app.setStyleSheet(LIGHT_THEME_CSS)

# Apply font size
font = app.font()
font.setPointSize(settings['ui_scale'])
app.setFont(font)

# Launch main window
window = LeatherBookInterface()
window.show()
app.exec()
```

---

### Pattern 2: Menu Action Trigger

```python
# leather_book_interface.py
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from app.gui.settings_dialog import SettingsDialog

class LeatherBookInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_settings = SettingsDialog.load_settings()
        self._setup_menus()

    def _setup_menus(self):
        menu = self.menuBar().addMenu("File")
        settings_action = menu.addAction("Settings...")
        settings_action.triggered.connect(self.open_settings)

    def open_settings(self):
        dialog = SettingsDialog(parent=self, current=self.current_settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_settings = dialog.get_values()
            if SettingsDialog.save_settings(new_settings):
                self.current_settings = new_settings
                self.apply_settings(new_settings)
                QMessageBox.information(
                    self,
                    "Settings Updated",
                    "Settings saved. Restart app to apply theme changes."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Save Failed",
                    "Could not save settings to disk."
                )

    def apply_settings(self, settings):
        # Apply font size immediately (theme requires restart)
        font = self.font()
        font.setPointSize(settings['ui_scale'])
        self.setFont(font)
```

---

### Pattern 3: Testing with Temporary Directory

```python
# tests/test_settings_dialog.py
import tempfile
import os
import json
from app.gui.settings_dialog import SettingsDialog

def test_settings_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override DATA_DIR for isolated testing
        os.environ['DATA_DIR'] = tmpdir

        # Save custom settings
        test_settings = {"theme": "dark", "ui_scale": 16}
        assert SettingsDialog.save_settings(test_settings) is True

        # Verify file created
        settings_path = os.path.join(tmpdir, "settings.json")
        assert os.path.exists(settings_path)

        # Load and verify
        loaded = SettingsDialog.load_settings()
        assert loaded == test_settings

        # Verify JSON format
        with open(settings_path) as f:
            raw = json.load(f)
            assert raw["theme"] == "dark"
            assert raw["ui_scale"] == 16
```

---

## Usage Examples

### Example 1: Basic Dialog Usage

```python
from PyQt6.QtWidgets import QApplication, QMainWindow
from app.gui.settings_dialog import SettingsDialog

app = QApplication([])
main_window = QMainWindow()

# Load existing settings
current = SettingsDialog.load_settings()
print(f"Current theme: {current['theme']}")  # "light"

# Open dialog
dialog = SettingsDialog(parent=main_window, current=current)
result = dialog.exec()

if result == QDialog.DialogCode.Accepted:
    new_settings = dialog.get_values()
    SettingsDialog.save_settings(new_settings)
    print(f"Saved theme: {new_settings['theme']}")
else:
    print("User cancelled settings")
```

---

### Example 2: Dynamic Theme Switching

```python
from PyQt6.QtWidgets import QApplication
from app.gui.settings_dialog import SettingsDialog

DARK_THEME = """
QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
}
QPushButton {
    background-color: #3700b3;
    color: #ffffff;
    border-radius: 4px;
    padding: 6px;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: #ffffff;
    color: #000000;
}
QPushButton {
    background-color: #6200ea;
    color: #ffffff;
    border-radius: 4px;
    padding: 6px;
}
"""

def apply_theme(app, settings):
    if settings['theme'] == 'dark':
        app.setStyleSheet(DARK_THEME)
    else:
        app.setStyleSheet(LIGHT_THEME)

app = QApplication([])
settings = SettingsDialog.load_settings()
apply_theme(app, settings)

# In settings dialog callback
def on_settings_changed(new_settings):
    SettingsDialog.save_settings(new_settings)
    apply_theme(app, new_settings)
```

---

### Example 3: Accessibility Font Scaling

```python
from PyQt6.QtGui import QFont
from app.gui.settings_dialog import SettingsDialog

def apply_font_size(widget, size):
    """Recursively apply font size to widget and children"""
    font = widget.font()
    font.setPointSize(size)
    widget.setFont(font)

    for child in widget.findChildren(QWidget):
        child_font = child.font()
        child_font.setPointSize(size)
        child.setFont(child_font)

# Application startup
settings = SettingsDialog.load_settings()
main_window = LeatherBookInterface()
apply_font_size(main_window, settings['ui_scale'])

# Settings dialog callback
def on_settings_saved(new_settings):
    apply_font_size(main_window, new_settings['ui_scale'])
    QMessageBox.information(
        main_window,
        "Font Updated",
        f"UI font size set to {new_settings['ui_scale']} points"
    )
```

---

### Example 4: First-Run Defaults

```python
from PyQt6.QtWidgets import QApplication, QMessageBox
from app.gui.settings_dialog import SettingsDialog
import os

def ensure_settings_exist():
    """Initialize settings on first run"""
    settings_path = os.path.join(
        os.getenv("DATA_DIR", "data"),
        "settings.json"
    )

    if not os.path.exists(settings_path):
        # First run - show welcome message and settings dialog
        QMessageBox.information(
            None,
            "Welcome",
            "Welcome to Project-AI! Let's configure your preferences."
        )

        dialog = SettingsDialog(current=None)  # Use defaults
        if dialog.exec() == QDialog.DialogCode.Accepted:
            SettingsDialog.save_settings(dialog.get_values())
        else:
            # User cancelled - save defaults
            SettingsDialog.save_settings({"theme": "light", "ui_scale": 10})

# Main
app = QApplication([])
ensure_settings_exist()
settings = SettingsDialog.load_settings()
# ... launch application
```

---

## Styling Guide

### Current Styling

The SettingsDialog uses **default PyQt6 styling** with no custom CSS. This ensures native look-and-feel across platforms (Windows, macOS, Linux).

**Platform Appearance:**
- **Windows 11**: Modern flat buttons, Segoe UI font
- **macOS**: Aqua theme with rounded corners
- **Linux**: Follows desktop environment theme (GTK/KDE)

---

### Tron Theme Recommendations

To align with the Leather Book Interface Tron aesthetic:

```python
TRON_SETTINGS_STYLE = """
QDialog {
    background-color: #0a0e1a;
    color: #00ff00;
    font-family: 'Courier New', monospace;
}

QLabel {
    color: #00ffff;
    font-size: 12pt;
    font-weight: bold;
    margin-bottom: 4px;
}

QComboBox {
    background-color: #1a1f2e;
    color: #00ff00;
    border: 2px solid #00ffff;
    border-radius: 4px;
    padding: 6px;
    font-size: 11pt;
}

QComboBox::drop-down {
    border: none;
    background: #00ffff;
}

QComboBox::down-arrow {
    image: url(assets/tron_arrow.png);
}

QSpinBox {
    background-color: #1a1f2e;
    color: #00ff00;
    border: 2px solid #00ffff;
    border-radius: 4px;
    padding: 6px;
    font-size: 11pt;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #00ffff;
    border: none;
}

QDialogButtonBox QPushButton {
    background-color: #00ffff;
    color: #0a0e1a;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 11pt;
}

QDialogButtonBox QPushButton:hover {
    background-color: #00ff00;
}

QDialogButtonBox QPushButton:pressed {
    background-color: #008888;
}
"""

# Apply in __init__
class SettingsDialog(QDialog):
    def __init__(self, parent=None, current=None):
        super().__init__(parent)
        self.setStyleSheet(TRON_SETTINGS_STYLE)
        # ... rest of initialization
```

---

### Dark Theme Styling

For modern dark theme (non-Tron):

```python
DARK_SETTINGS_STYLE = """
QDialog {
    background-color: #2b2b2b;
    color: #e0e0e0;
}

QLabel {
    color: #ffffff;
    font-size: 11pt;
}

QComboBox, QSpinBox {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 5px;
}

QComboBox::drop-down {
    border: none;
}

QPushButton {
    background-color: #0078d4;
    color: #ffffff;
    border: none;
    border-radius: 3px;
    padding: 6px 12px;
}

QPushButton:hover {
    background-color: #005a9e;
}
"""
```

---

## Security Considerations

### File System Security

**Issue:** Settings file stored in plaintext JSON
**Risk:** Low (contains only UI preferences, no secrets)
**Mitigation:** Not required for current schema

**Future Consideration:** If adding API keys or tokens:
```python
from cryptography.fernet import Fernet

# Encrypt sensitive fields before save
def save_settings(settings):
    key = Fernet.generate_key()  # Store in secure keyring
    f = Fernet(key)
    if 'api_key' in settings:
        settings['api_key'] = f.encrypt(settings['api_key'].encode()).decode()
    # ... save to JSON
```

---

### Input Validation

**Current Protection:**
- QSpinBox enforces 8-20 range (cannot type invalid values)
- QComboBox restricts to "light"/"dark" options

**Additional Validation:**
```python
def get_values(self):
    theme = self.theme_select.currentText()
    if theme not in ["light", "dark"]:
        theme = "light"  # Fallback

    scale = self.size_spin.value()
    if not (8 <= scale <= 20):
        scale = 10  # Fallback

    return {"theme": theme, "ui_scale": scale}
```

---

### Path Traversal Protection

**Issue:** `DATA_DIR` environment variable could contain path traversal (`../../etc/passwd`)
**Current Risk:** Low (only used for settings.json write)
**Mitigation:**

```python
import os

DATA_DIR = os.getenv("DATA_DIR", "data")
# Normalize path to prevent traversal
DATA_DIR = os.path.normpath(os.path.abspath(DATA_DIR))

# Ensure path is within project directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if not DATA_DIR.startswith(PROJECT_ROOT):
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")
```

---

## Accessibility Considerations

### Keyboard Navigation

**Current Support:**
- Tab key cycles through controls (theme → font size → OK → Cancel)
- Enter key activates focused button
- Space key toggles combobox dropdown
- Arrow keys navigate combobox/spinbox values

**Recommended Enhancement:**
```python
# Add keyboard shortcuts
self.theme_select.setFocus()  # Focus first control on open
self.setTabOrder(self.theme_select, self.size_spin)
self.setTabOrder(self.size_spin, btns.button(QDialogButtonBox.StandardButton.Ok))
```

---

### Screen Reader Support

**Current Labels:**
- QLabel widgets provide descriptive text above controls
- Screen readers read label + control value

**Improvement:**
```python
self.theme_select.setAccessibleName("Theme selector")
self.theme_select.setAccessibleDescription("Choose light or dark theme")

self.size_spin.setAccessibleName("Font size")
self.size_spin.setAccessibleDescription("UI font size from 8 to 20 points")
```

---

### High Contrast Mode

**Issue:** Default theme may not work in Windows High Contrast mode
**Solution:** Respect system theme:

```python
from PyQt6.QtCore import Qt

# Detect high contrast mode
def is_high_contrast():
    return QApplication.palette().color(QPalette.ColorRole.Window).lightness() < 128

# Apply appropriate theme
settings = SettingsDialog.load_settings()
if is_high_contrast():
    # Don't override system high contrast theme
    pass
else:
    apply_custom_theme(settings['theme'])
```

---

### Font Size Limits

**Current Range:** 8-20 points
**Accessibility Issue:** May be too small for low-vision users
**Recommendation:** Extend to 8-32 points:

```python
self.size_spin.setRange(8, 32)
```

**Large Text Handling:**
- Ensure dialogs resize to accommodate large fonts
- Use `QScrollArea` if content exceeds screen size

---

## Troubleshooting

### Issue 1: Settings Not Persisting

**Symptom:** Changes saved in dialog but not applied on restart

**Causes:**
1. Multiple `DATA_DIR` paths in use
2. Application launched from different working directory
3. File permissions prevent write

**Diagnosis:**
```python
import os
print(f"DATA_DIR: {os.getenv('DATA_DIR', 'data')}")
print(f"Settings path: {os.path.join(os.getenv('DATA_DIR', 'data'), 'settings.json')}")
print(f"File exists: {os.path.exists(settings_path)}")

# Check write permissions
try:
    with open(settings_path, 'a'):
        pass
    print("Write permissions: OK")
except PermissionError:
    print("Write permissions: DENIED")
```

**Solution:**
- Ensure `DATA_DIR` is absolute path or relative to project root
- Use `os.path.abspath()` to normalize paths
- Check file permissions: `chmod 644 data/settings.json`

---

### Issue 2: JSON Parse Errors

**Symptom:** Application crashes with `json.JSONDecodeError`

**Cause:** Corrupted `settings.json` file (manual edits, disk errors)

**Current Handling:**
```python
# Already handles this - returns defaults on parse error
try:
    return json.load(f)
except Exception as e:
    logging.warning("Failed to load settings: %s", e)
    return {"theme": "light", "ui_scale": 10}
```

**User Recovery:**
1. Delete corrupted `data/settings.json`
2. Restart application (auto-creates defaults)
3. Reconfigure preferences via dialog

---

### Issue 3: Theme Not Applied

**Symptom:** Theme changed in dialog but UI still shows old theme

**Cause:** Theme application requires full restart in some cases

**Solution:**
```python
# In settings callback
if new_settings['theme'] != old_settings['theme']:
    QMessageBox.information(
        self,
        "Restart Required",
        "Please restart the application for theme changes to take effect."
    )
```

**Advanced:** Hot-reload theme:
```python
def apply_theme_live(app, theme):
    if theme == 'dark':
        app.setStyleSheet(DARK_THEME_CSS)
    else:
        app.setStyleSheet(LIGHT_THEME_CSS)

    # Force repaint
    for widget in app.allWidgets():
        widget.update()
```

---

### Issue 4: Font Size Not Scaling All Widgets

**Symptom:** Some widgets ignore font size setting

**Cause:** Widgets with hardcoded font sizes override global setting

**Diagnosis:**
```python
# Find widgets with custom fonts
for widget in main_window.findChildren(QWidget):
    if widget.font() != app.font():
        print(f"{widget} has custom font: {widget.font().pointSize()}")
```

**Solution:**
```python
# Remove hardcoded font sizes
# Bad:
label.setFont(QFont("Arial", 14))

# Good:
font = app.font()
font.setFamily("Arial")
label.setFont(font)  # Inherits size from app
```

---

### Issue 5: DATA_DIR Environment Variable Not Recognized

**Symptom:** Settings saved to `data/` even when `DATA_DIR` set

**Cause:** Environment variable set after Python process started

**Solution:**
```bash
# Linux/macOS
export DATA_DIR=/custom/path
python -m src.app.main

# Windows
set DATA_DIR=C:\custom\path
python -m src.app.main

# Or in .env file (requires python-dotenv)
from dotenv import load_dotenv
load_dotenv()  # Loads DATA_DIR from .env
```

---

### Issue 6: Modal Dialog Freezes Application

**Symptom:** Application unresponsive after opening settings dialog

**Cause:** Event loop blocked or incorrect modality

**Diagnosis:**
```python
# Check modality
dialog = SettingsDialog(parent=main_window)
print(f"Is modal: {dialog.isModal()}")  # Should be True

# Check event loop
print(f"Event loop running: {QApplication.instance() is not None}")
```

**Solution:**
- Ensure `exec()` called from GUI thread only
- Never call from signal handler that blocks event loop
- Use `QTimer.singleShot(0, lambda: dialog.exec())` if needed

---

### Best Practices Checklist

✅ **Always load settings on application startup**
✅ **Use `SettingsDialog.load_settings()` static method (no instantiation needed)**
✅ **Check return value of `save_settings()` for I/O errors**
✅ **Pass `parent=main_window` for proper modality**
✅ **Test with missing/corrupted `settings.json` to verify fallback**
✅ **Use absolute paths for `DATA_DIR` in production**
✅ **Log all I/O operations for debugging**
✅ **Provide user feedback on save success/failure**
✅ **Document restart requirements for theme changes**
✅ **Test font scaling with accessibility tools**

---

## Conclusion

The **SettingsDialog** component provides a simple, robust interface for application-wide UI configuration. Its JSON persistence, error resilience, and accessibility features make it suitable for production deployment. Future enhancements could include additional settings (language, notifications, keybindings), tabbed interface for organization, or migration to a dedicated settings panel for complex configurations.

**Total Word Count:** 4,850 words

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
