# Settings Dialog Module

**Module**: `src/app/gui/settings_dialog.py` [[src/app/gui/settings_dialog.py]]  
**Purpose**: Simple GUI settings dialog with theme and UI scale configuration  
**Classification**: GUI Configuration  
**Priority**: P2 - User Interface

---

## Overview

The Settings Dialog provides a PyQt6-based settings interface for basic application configuration including theme selection and UI font size. It features JSON persistence to `data/settings.json` with automatic directory creation.

### Key Characteristics

- **Framework**: PyQt6 QDialog
- **Settings**: Theme (light/dark), UI font size (8-20pt)
- **Persistence**: JSON file storage
- **Location**: `data/settings.json`
- **Modal**: Blocks parent window until closed

---

## Architecture

### Class Structure

```python
class SettingsDialog(QDialog):
    """Settings dialog for theme and UI configuration."""
    
    def __init__(self, parent=None, current=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        
        # UI components
        self.theme_select: QComboBox
        self.size_spin: QSpinBox
```

### Constants

```python
DATA_DIR = os.getenv("DATA_DIR", "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
```

---

## Settings Structure

### Configuration Format

```python
{
    "theme": "light",      # or "dark"
    "ui_scale": 10         # Font size in points (8-20)
}
```

**Defaults**:
- `theme`: "light"
- `ui_scale`: 10

---

## Core API

### Dialog Initialization

```python
def __init__(self, parent=None, current=None):
    """Initialize settings dialog.
    
    Args:
        parent: Parent widget (optional)
        current: Current settings dictionary (optional)
    
    UI Components:
        - Theme combo box (light, dark)
        - Font size spin box (8-20)
        - OK/Cancel buttons
    """
```

### Getting Values

```python
def get_values(self) -> dict:
    """Get current dialog values.
    
    Returns:
        {
            "theme": str,
            "ui_scale": int
        }
    
    Example:
        >>> dialog = SettingsDialog()
        >>> if dialog.exec() == QDialog.Accepted:
        ...     settings = dialog.get_values()
        ...     print(settings)
        {'theme': 'dark', 'ui_scale': 12}
    """
```

### Loading Settings

```python
@staticmethod
def load_settings() -> dict:
    """Load settings from file.
    
    Returns:
        Settings dictionary or defaults if error
    
    Behavior:
        - Creates data directory if needed
        - Returns defaults if file doesn't exist
        - Returns defaults if JSON parse error
        - Logs warnings on error
    
    Example:
        >>> settings = SettingsDialog.load_settings()
        >>> print(settings["theme"])
        'light'
    """
```

### Saving Settings

```python
@staticmethod
def save_settings(settings: dict) -> bool:
    """Save settings to file.
    
    Args:
        settings: Settings dictionary to save
    
    Returns:
        True if successful, False otherwise
    
    Behavior:
        - Creates data directory if needed
        - Overwrites existing file
        - Logs errors on failure
    
    Example:
        >>> settings = {"theme": "dark", "ui_scale": 12}
        >>> success = SettingsDialog.save_settings(settings)
        >>> assert success is True
    """
```

---

## Usage Patterns

### Pattern 1: Basic Usage

```python
from src.app.gui.settings_dialog import SettingsDialog

# Load current settings
current_settings = SettingsDialog.load_settings()

# Show dialog
dialog = SettingsDialog(parent=main_window, current=current_settings)

if dialog.exec() == QDialog.Accepted:
    # User clicked OK
    new_settings = dialog.get_values()
    
    # Save settings
    SettingsDialog.save_settings(new_settings)
    
    # Apply settings
    apply_theme(new_settings["theme"])
    apply_ui_scale(new_settings["ui_scale"])
```

### Pattern 2: Settings Menu Action

```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_menus()
    
    def setup_menus(self):
        settings_menu = self.menuBar().addMenu("Settings")
        
        preferences_action = settings_menu.addAction("Preferences...")
        preferences_action.triggered.connect(self.show_settings)
    
    def show_settings(self):
        current = SettingsDialog.load_settings()
        dialog = SettingsDialog(parent=self, current=current)
        
        if dialog.exec() == QDialog.Accepted:
            settings = dialog.get_values()
            SettingsDialog.save_settings(settings)
            
            # Reload UI with new settings
            self.apply_settings(settings)
```

### Pattern 3: First-Run Setup

```python
def first_run_setup():
    # Check if settings file exists
    try:
        settings = SettingsDialog.load_settings()
        if not os.path.exists(SETTINGS_FILE):
            # First run - show settings dialog
            dialog = SettingsDialog()
            dialog.exec()
            
            settings = dialog.get_values()
            SettingsDialog.save_settings(settings)
    except Exception as e:
        logger.error(f"First run setup failed: {e}")
```

### Pattern 4: Apply Settings on Load

```python
def initialize_app():
    # Load settings
    settings = SettingsDialog.load_settings()
    
    # Apply theme
    if settings["theme"] == "dark":
        app.setStyleSheet(DARK_THEME_CSS)
    else:
        app.setStyleSheet(LIGHT_THEME_CSS)
    
    # Apply UI scale
    font = app.font()
    font.setPointSize(settings["ui_scale"])
    app.setFont(font)
```

### Pattern 5: Settings Validation

```python
def validate_and_save_settings(settings):
    # Validate theme
    if settings["theme"] not in ["light", "dark"]:
        logger.warning(f"Invalid theme: {settings['theme']}, using default")
        settings["theme"] = "light"
    
    # Validate UI scale
    if not (8 <= settings["ui_scale"] <= 20):
        logger.warning(f"Invalid UI scale: {settings['ui_scale']}, using default")
        settings["ui_scale"] = 10
    
    # Save validated settings
    return SettingsDialog.save_settings(settings)
```

---

## Integration Examples

### Example 1: Theme Application

```python
# Dark theme stylesheet
DARK_THEME_CSS = """
QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
}
QLineEdit, QTextEdit {
    background-color: #383838;
    border: 1px solid #555555;
}
"""

# Light theme stylesheet
LIGHT_THEME_CSS = """
QWidget {
    background-color: #ffffff;
    color: #000000;
}
QLineEdit, QTextEdit {
    background-color: #f0f0f0;
    border: 1px solid #cccccc;
}
"""

def apply_theme(theme):
    if theme == "dark":
        app.setStyleSheet(DARK_THEME_CSS)
    else:
        app.setStyleSheet(LIGHT_THEME_CSS)
```

### Example 2: Dynamic Font Scaling

```python
def apply_ui_scale(scale):
    font = QFont()
    font.setPointSize(scale)
    app.setFont(font)
    
    # Update specific widgets
    for widget in app.allWidgets():
        widget.updateGeometry()
```

### Example 3: Settings Manager Integration

```python
class ApplicationSettings:
    def __init__(self):
        self.settings = SettingsDialog.load_settings()
    
    def get_theme(self):
        return self.settings["theme"]
    
    def set_theme(self, theme):
        self.settings["theme"] = theme
        self.save()
    
    def get_ui_scale(self):
        return self.settings["ui_scale"]
    
    def set_ui_scale(self, scale):
        self.settings["ui_scale"] = scale
        self.save()
    
    def save(self):
        SettingsDialog.save_settings(self.settings)
    
    def show_dialog(self, parent=None):
        dialog = SettingsDialog(parent, self.settings)
        if dialog.exec() == QDialog.Accepted:
            self.settings = dialog.get_values()
            self.save()
            return True
        return False
```

---

## Testing

### Unit Testing

```python
import pytest
from src.app.gui.settings_dialog import SettingsDialog
import os
import json
import tempfile

@pytest.fixture
def temp_data_dir(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("DATA_DIR", tmpdir)
        yield tmpdir

def test_default_settings():
    settings = SettingsDialog.load_settings()
    assert settings["theme"] == "light"
    assert settings["ui_scale"] == 10

def test_save_and_load(temp_data_dir):
    test_settings = {"theme": "dark", "ui_scale": 14}
    
    # Save settings
    success = SettingsDialog.save_settings(test_settings)
    assert success is True
    
    # Load settings
    loaded = SettingsDialog.load_settings()
    assert loaded["theme"] == "dark"
    assert loaded["ui_scale"] == 14

def test_get_values():
    dialog = SettingsDialog()
    dialog.theme_select.setCurrentText("dark")
    dialog.size_spin.setValue(12)
    
    values = dialog.get_values()
    assert values["theme"] == "dark"
    assert values["ui_scale"] == 12

def test_settings_file_creation(temp_data_dir):
    settings_file = os.path.join(temp_data_dir, "settings.json")
    
    # File shouldn't exist initially
    assert not os.path.exists(settings_file)
    
    # Save settings
    SettingsDialog.save_settings({"theme": "dark", "ui_scale": 10})
    
    # File should now exist
    assert os.path.exists(settings_file)
```

---

## Best Practices

1. **Load on Startup**: Load settings early in application lifecycle
2. **Apply Immediately**: Apply theme and UI scale after loading
3. **Save on Accept**: Only save when user clicks OK
4. **Validate Inputs**: Validate theme and UI scale values
5. **Default Handling**: Provide sensible defaults for missing settings
6. **Error Logging**: Log errors but don't crash on settings failure
7. **Directory Creation**: Ensure data directory exists before saving
8. **Modal Dialog**: Keep dialog modal to prevent state issues
9. **Current Values**: Pass current settings to dialog for initialization
10. **Backup Settings**: Consider backing up settings.json periodically

---

## Comparison with Settings Manager

| Feature | SettingsDialog | SettingsManager |
|---------|---------------|-----------------|
| **Complexity** | Simple | Comprehensive |
| **Encryption** | None | God-tier |
| **Settings** | 2 (theme, scale) | 100+ settings |
| **GUI** | Built-in dialog | External dialog required |
| **Persistence** | JSON file | Encrypted export |
| **Use Case** | Basic UI settings | Full app configuration |

**When to Use**:
- `SettingsDialog`: Simple UI preferences
- `SettingsManager`: Production deployment with security

---

## Migration to Settings Manager

### Migration Example

```python
# Before: SettingsDialog
settings = SettingsDialog.load_settings()
theme = settings["theme"]
ui_scale = settings["ui_scale"]

# After: SettingsManager
from config.settings_manager import SettingsManager
manager = SettingsManager(god_tier_encryption)
theme = manager.get_setting("general", "theme")
ui_scale = manager.get_setting("general", "ui_scale")
```

---

## Related Modules

- **Settings Manager**: `config/settings_manager.py` - Comprehensive settings
- **Leather Book Interface**: `src/app/gui/leather_book_interface.py` [[src/app/gui/leather_book_interface.py]] - Main GUI
- **Core Config**: `src/app/core/config.py` [[src/app/core/config.py]] - Application configuration

---

## Future Enhancements

1. **More Settings**: Add more UI customization options
2. **Validation**: Input validation before saving
3. **Reset Button**: Add reset to defaults button
4. **Preview**: Live preview of theme changes
5. **Custom Themes**: Support custom theme files
6. **Font Family**: Add font family selection
7. **Language**: Add language selection
8. **Export/Import**: Export/import settings
9. **Profiles**: Support multiple settings profiles
10. **Cloud Sync**: Sync settings across devices
11. **Encryption**: Optional settings encryption
12. **Backup**: Automatic settings backup


---

## Related Documentation

- **Relationship Map**: [[relationships\configuration\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/gui/settings_dialog.py]]
