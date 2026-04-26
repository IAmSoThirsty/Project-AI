# GUI Testing

**Purpose:** Testing PyQt6 desktop GUI components  
**Directory:** `tests/gui_e2e/`  
**Coverage:** Leather Book interface, dashboard, persona panel, image generation  

---

## Overview

GUI testing in Project-AI validates:

1. **Launch & Login Flow** - Application startup and authentication
2. **Leather Book Interface** - Main window and navigation
3. **Dashboard Components** - Six-zone dashboard functionality
4. **Persona Panel** - AI configuration interface
5. **Image Generation UI** - Dual-page image generation interface

---

## GUI Test Structure

```
tests/gui_e2e/
├── test_launch_and_login.py    # Launch and login flow
└── (other GUI test modules)

Related test files:
tests/test_leather_book_smoke.py  # Smoke tests for Leather Book UI
```

---

## Launch and Login Testing

### test_launch_and_login.py

**Purpose:** Test application launch and user authentication flow

#### QApplication Setup
```python
import pytest
from PyQt6.QtWidgets import QApplication
from app.gui.leather_book_interface import LeatherBookInterface

@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def main_window(qapp, tmp_path):
    """Create main window with isolated data directory."""
    window = LeatherBookInterface(data_dir=str(tmp_path))
    window.show()
    yield window
    window.close()
```

#### Application Launch
```python
def test_application_launches(main_window):
    """Test that application window opens."""
    assert main_window.isVisible()
    assert main_window.windowTitle() == "Project-AI - Leather Book"
    assert main_window.width() >= 1200
    assert main_window.height() >= 800
```

#### Login Flow
```python
def test_login_flow(main_window, qtbot):
    """Test complete login flow."""
    # Verify starting on login page
    assert main_window.stacked_widget.currentIndex() == 0
    
    # Fill in credentials
    username_field = main_window.login_page.username_input
    password_field = main_window.login_page.password_input
    login_button = main_window.login_page.login_button
    
    qtbot.keyClicks(username_field, "testuser")
    qtbot.keyClicks(password_field, "testpass123")
    
    # Click login
    qtbot.mouseClick(login_button, Qt.MouseButton.LeftButton)
    
    # Wait for page transition
    qtbot.wait(500)
    
    # Verify switched to dashboard
    assert main_window.stacked_widget.currentIndex() == 1
```

#### Login Validation
```python
def test_login_validation(main_window, qtbot):
    """Test login validation."""
    login_page = main_window.login_page
    
    # Test empty credentials
    qtbot.mouseClick(login_page.login_button, Qt.MouseButton.LeftButton)
    qtbot.wait(100)
    
    # Verify error message displayed
    assert login_page.error_label.isVisible()
    assert "required" in login_page.error_label.text().lower()
    
    # Test invalid credentials
    qtbot.keyClicks(login_page.username_input, "invalid")
    qtbot.keyClicks(login_page.password_input, "wrong")
    qtbot.mouseClick(login_page.login_button, Qt.MouseButton.LeftButton)
    qtbot.wait(100)
    
    # Verify error message
    assert "invalid" in login_page.error_label.text().lower()
```

---

## Dashboard Testing

### test_leather_book_smoke.py

**Purpose:** Smoke tests for Leather Book dashboard

#### Dashboard Components
```python
def test_dashboard_components_exist(main_window, qtbot):
    """Test that all dashboard components exist."""
    # Login first
    login_to_dashboard(main_window, qtbot)
    
    dashboard = main_window.dashboard
    
    # Verify six zones exist
    assert dashboard.stats_panel is not None
    assert dashboard.actions_panel is not None
    assert dashboard.ai_head_panel is not None
    assert dashboard.user_chat_panel is not None
    assert dashboard.response_panel is not None
    assert dashboard.footer_panel is not None
```

#### Stats Panel
```python
def test_stats_panel_displays_data(main_window, qtbot):
    """Test stats panel displays system statistics."""
    login_to_dashboard(main_window, qtbot)
    
    stats_panel = main_window.dashboard.stats_panel
    
    # Verify stat labels exist
    assert stats_panel.interaction_count_label is not None
    assert stats_panel.uptime_label is not None
    assert stats_panel.mood_label is not None
    
    # Verify stats have values
    interaction_text = stats_panel.interaction_count_label.text()
    assert interaction_text.startswith("Interactions:")
    
    mood_text = stats_panel.mood_label.text()
    assert "Mood:" in mood_text
```

#### Actions Panel
```python
def test_actions_panel_buttons(main_window, qtbot):
    """Test actions panel buttons are functional."""
    login_to_dashboard(main_window, qtbot)
    
    actions_panel = main_window.dashboard.actions_panel
    
    # Verify buttons exist
    assert actions_panel.learning_button is not None
    assert actions_panel.memory_button is not None
    assert actions_panel.settings_button is not None
    assert actions_panel.image_gen_button is not None
    
    # Test image generation button
    with qtbot.waitSignal(actions_panel.image_gen_requested, timeout=1000):
        qtbot.mouseClick(actions_panel.image_gen_button, 
                        Qt.MouseButton.LeftButton)
```

#### Chat Interaction
```python
def test_chat_interaction(main_window, qtbot):
    """Test user chat and AI response."""
    login_to_dashboard(main_window, qtbot)
    
    chat_panel = main_window.dashboard.user_chat_panel
    response_panel = main_window.dashboard.response_panel
    
    # Type message
    message = "Hello AI!"
    qtbot.keyClicks(chat_panel.input_field, message)
    
    # Send message
    with qtbot.waitSignal(chat_panel.send_message, timeout=1000):
        qtbot.mouseClick(chat_panel.send_button, Qt.MouseButton.LeftButton)
    
    # Wait for response
    qtbot.wait(2000)  # Allow time for AI processing
    
    # Verify response displayed
    response_text = response_panel.response_display.toPlainText()
    assert len(response_text) > 0
```

---

## Persona Panel Testing

### Persona Configuration
```python
def test_persona_panel_navigation(main_window, qtbot):
    """Test persona panel tab navigation."""
    login_to_dashboard(main_window, qtbot)
    
    # Open persona panel
    main_window.show_persona_panel()
    qtbot.wait(500)
    
    persona_panel = main_window.persona_panel
    
    # Verify tabs exist
    assert persona_panel.tab_widget.count() == 4
    assert persona_panel.tab_widget.tabText(0) == "Personality"
    assert persona_panel.tab_widget.tabText(1) == "Mood"
    assert persona_panel.tab_widget.tabText(2) == "Statistics"
    assert persona_panel.tab_widget.tabText(3) == "Settings"
```

### Personality Trait Adjustment
```python
def test_personality_trait_adjustment(main_window, qtbot):
    """Test adjusting personality traits."""
    login_to_dashboard(main_window, qtbot)
    main_window.show_persona_panel()
    
    persona_panel = main_window.persona_panel
    persona_panel.tab_widget.setCurrentIndex(0)  # Personality tab
    
    # Get curiosity slider
    curiosity_slider = persona_panel.trait_sliders["curiosity"]
    original_value = curiosity_slider.value()
    
    # Adjust slider
    new_value = original_value + 10
    curiosity_slider.setValue(new_value)
    qtbot.wait(100)
    
    # Verify trait updated
    trait_label = persona_panel.trait_labels["curiosity"]
    assert str(new_value) in trait_label.text()
```

---

## Image Generation UI Testing

### Dual-Page Navigation
```python
def test_image_generation_navigation(main_window, qtbot):
    """Test navigation to image generation interface."""
    login_to_dashboard(main_window, qtbot)
    
    actions_panel = main_window.dashboard.actions_panel
    
    # Click image generation button
    qtbot.mouseClick(actions_panel.image_gen_button, 
                    Qt.MouseButton.LeftButton)
    qtbot.wait(500)
    
    # Verify page switched
    assert main_window.stacked_widget.currentIndex() == 2
    
    # Verify image generation interface loaded
    assert main_window.image_gen_interface is not None
```

### Prompt Input and Generation
```python
def test_image_generation_flow(main_window, qtbot, mocker):
    """Test complete image generation flow."""
    login_to_dashboard(main_window, qtbot)
    
    # Navigate to image generation
    main_window.switch_to_image_generation()
    qtbot.wait(500)
    
    image_gen = main_window.image_gen_interface
    left_panel = image_gen.left_panel
    
    # Mock image generator to avoid API calls
    mock_generator = mocker.patch.object(
        image_gen,
        'generator',
        return_value=("test_image.png", {"style": "photorealistic"})
    )
    
    # Enter prompt
    prompt = "A beautiful sunset over mountains"
    qtbot.keyClicks(left_panel.prompt_input, prompt)
    
    # Select style
    left_panel.style_combo.setCurrentText("photorealistic")
    
    # Click generate
    with qtbot.waitSignal(image_gen.image_generated, timeout=5000):
        qtbot.mouseClick(left_panel.generate_button, 
                        Qt.MouseButton.LeftButton)
    
    # Verify generation called
    mock_generator.assert_called_once()
```

---

## GUI Test Utilities

### Helper Functions

```python
def login_to_dashboard(main_window, qtbot):
    """Helper to login and reach dashboard."""
    login_page = main_window.login_page
    
    # Fill credentials
    qtbot.keyClicks(login_page.username_input, "testuser")
    qtbot.keyClicks(login_page.password_input, "testpass123")
    
    # Click login
    qtbot.mouseClick(login_page.login_button, Qt.MouseButton.LeftButton)
    
    # Wait for transition
    qtbot.wait(500)

def wait_for_signal(signal, timeout=1000):
    """Wait for signal with timeout."""
    from PyQt6.QtCore import QTimer, QEventLoop
    
    loop = QEventLoop()
    timer = QTimer()
    timer.setSingleShot(True)
    
    signal.connect(loop.quit)
    timer.timeout.connect(loop.quit)
    
    timer.start(timeout)
    loop.exec()
    
    return timer.isActive()
```

---

## qtbot Usage Patterns

### Mouse Interactions
```python
# Click button
qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

# Double click
qtbot.mouseDClick(widget, Qt.MouseButton.LeftButton)

# Mouse move
qtbot.mouseMove(widget, pos=QPoint(100, 100))

# Mouse press and release
qtbot.mousePress(widget, Qt.MouseButton.LeftButton)
qtbot.mouseRelease(widget, Qt.MouseButton.LeftButton)
```

### Keyboard Interactions
```python
# Type text
qtbot.keyClicks(line_edit, "Hello World")

# Single key press
qtbot.keyPress(widget, Qt.Key.Key_Return)

# Key sequence
qtbot.keyPress(widget, Qt.Key.Key_Control)
qtbot.keyPress(widget, Qt.Key.Key_S)
qtbot.keyRelease(widget, Qt.Key.Key_S)
qtbot.keyRelease(widget, Qt.Key.Key_Control)
```

### Waiting
```python
# Wait milliseconds
qtbot.wait(500)

# Wait for signal
qtbot.waitSignal(signal, timeout=1000)

# Wait until condition
qtbot.waitUntil(lambda: widget.isVisible(), timeout=1000)
```

---

## Mocking in GUI Tests

### Mock External Services
```python
def test_with_mocked_api(main_window, qtbot, mocker):
    """Test GUI with mocked external API."""
    # Mock OpenAI API
    mock_openai = mocker.patch('openai.ChatCompletion.create')
    mock_openai.return_value = {
        'choices': [{'message': {'content': 'Test response'}}]
    }
    
    # Interact with GUI
    login_to_dashboard(main_window, qtbot)
    chat_panel = main_window.dashboard.user_chat_panel
    
    qtbot.keyClicks(chat_panel.input_field, "Hello")
    qtbot.mouseClick(chat_panel.send_button, Qt.MouseButton.LeftButton)
    
    qtbot.wait(1000)
    
    # Verify mock called
    mock_openai.assert_called_once()
```

### Mock File Dialogs
```python
def test_file_dialog(main_window, qtbot, mocker):
    """Test with mocked file dialog."""
    # Mock QFileDialog
    mock_dialog = mocker.patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName')
    mock_dialog.return_value = ('/path/to/file.txt', 'Text Files (*.txt)')
    
    # Click button that opens dialog
    qtbot.mouseClick(main_window.open_button, Qt.MouseButton.LeftButton)
    
    # Verify dialog was shown
    mock_dialog.assert_called_once()
```

---

## GUI Testing Best Practices

### ✅ DO
- Use `qtbot` for all GUI interactions
- Mock external API calls
- Use `waitSignal` for asynchronous operations
- Test error handling (dialog messages, error labels)
- Use fixtures for QApplication and main window
- Test keyboard shortcuts
- Verify UI state changes

### ❌ DON'T
- Call GUI methods directly without `qtbot`
- Skip waiting for signals/delays
- Test with real API keys (mock instead)
- Ignore QApplication context
- Run GUI tests in parallel (use `-n 0` with pytest-xdist)
- Skip cleanup (close windows in fixtures)

---

## Running GUI Tests

### Run GUI Tests
```bash
# All GUI tests
pytest tests/gui_e2e/ -v

# Specific GUI test
pytest tests/gui_e2e/test_launch_and_login.py -v

# GUI smoke tests
pytest tests/test_leather_book_smoke.py -v
```

### GUI Test Requirements
```bash
# Install PyQt6 and pytest-qt
pip install PyQt6 pytest-qt

# Set display (Linux headless)
export QT_QPA_PLATFORM=offscreen
```

### CI/CD GUI Testing
```yaml
# .github/workflows/ci.yml
- name: Run GUI Tests
  run: |
    export QT_QPA_PLATFORM=offscreen
    pytest tests/gui_e2e/ -v
```

---

## Common GUI Test Issues

### Issue: QApplication Not Created
**Solution:** Use `qapp` fixture
```python
@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
    app.quit()
```

### Issue: Tests Hang
**Solution:** Use proper timeouts
```python
qtbot.waitSignal(signal, timeout=5000)  # 5 second timeout
```

### Issue: Flaky Tests
**Solution:** Add appropriate waits
```python
qtbot.wait(500)  # Wait for UI update
qtbot.waitUntil(lambda: widget.isVisible())
```

### Issue: CI Fails (No Display)
**Solution:** Use offscreen platform
```bash
export QT_QPA_PLATFORM=offscreen
```

---

## Next Steps

1. Read `12_TEST_MAINTENANCE.md` for maintaining GUI tests
2. See `DEVELOPER_QUICK_REFERENCE.md` for GUI component API
3. Check PyQt6 documentation: https://www.riverbankcomputing.com/static/Docs/PyQt6/

---

**See Also:**
- `tests/gui_e2e/test_launch_and_login.py` - GUI test examples
- `tests/test_leather_book_smoke.py` - Smoke tests
- `app/gui/leather_book_interface.py` - Main window implementation
- `pytest-qt` documentation: https://pytest-qt.readthedocs.io/
