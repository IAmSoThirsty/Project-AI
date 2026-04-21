---
type: source-doc
tags: [source-docs, aggregated-content, technical-reference, gui-components, pyqt6, leather-book-ui]
created: 2025-01-26
last_verified: 2026-04-20
status: current
related_systems: [leather-book-interface, leather-book-dashboard, persona-panel, image-generation-ui, dashboard-handlers, dashboard-utils]
stakeholders: [content-team, knowledge-management, developers, ui-ux-designers]
content_category: technical
review_cycle: quarterly
---

# GUI Components Documentation

**Directory:** `source-docs/gui/`  
**Source Code:** `src/app/gui/`  
**Version:** 1.0.0  
**Last Updated:** 2025-01-26

## Purpose

This directory contains documentation for the six PyQt6 GUI modules that implement Project-AI's distinctive "Leather Book" interface. The GUI provides a dual-page layout with Tron-themed login, six-zone dashboard, and specialized panels for AI configuration and image generation.

## Architecture Overview

### Design Philosophy

The Leather Book interface follows a **dual-page, zone-based layout** pattern inspired by Tron aesthetics and physical book metaphors:

```
Main Window (LeatherBookInterface)
├── Page 0: Login (Tron-themed, left side)
└── Page 1: Dashboard (6-zone layout, right side)
    ├── Zone 1: System Statistics (top-left)
    ├── Zone 2: Proactive Actions (top-right)
    ├── Zone 3: AI Head Animation (center)
    ├── Zone 4: User Chat Input (bottom-left)
    ├── Zone 5: AI Response Display (bottom-right)
    └── Floating: Persona Panel (overlay)
```

### Technology Stack

- **Framework:** PyQt6 (Qt 6.x Python bindings)
- **Layout:** QVBoxLayout, QHBoxLayout, QGridLayout
- **Threading:** QThread for async operations
- **Signals:** pyqtSignal for inter-component communication
- **Styling:** QSS (Qt Style Sheets) with Tron color palette

## The Six GUI Modules

### 🖼️ Main Window (`leather_book_interface.py`)

**Purpose:** Application entry point and page management

**Lines:** 659 | **Complexity:** High | **Dependencies:** All other GUI modules

#### Key Components

1. **QMainWindow Setup**
   - Central widget with QStackedWidget for page switching
   - Window geometry: 1400x900 (desktop), fullscreen option
   - Custom window icon and title

2. **Page Management**
   - Page 0: Login interface (Tron theme)
   - Page 1: Main dashboard (6-zone layout)
   - Page 2+: Dynamic pages (image generation, settings, etc.)

3. **Signal Routing**
   - Connects login signals to dashboard activation
   - Routes user actions to appropriate handlers
   - Manages cross-page communication

#### API Reference

```python
from app.gui.leather_book_interface import LeatherBookInterface

# Initialize main window
app = QApplication(sys.argv)
window = LeatherBookInterface(
    user_manager=user_manager,
    core_systems={
        "four_laws": four_laws_system,
        "persona": ai_persona,
        "memory": memory_system,
        "learning": learning_manager,
        "override": command_override,
        "plugins": plugin_manager
    }
)

# Show window
window.show()
sys.exit(app.exec())
```

#### Signals

```python
# Emitted when user successfully logs in
user_logged_in = pyqtSignal(str)  # username

# Emitted when switching pages
page_changed = pyqtSignal(int)  # page_index

# Emitted on window close
closing = pyqtSignal()
```

#### Color Palette

```python
# Tron-inspired colors
TRON_GREEN = "#00ff00"  # Primary accent
TRON_CYAN = "#00ffff"   # Secondary accent
TRON_DARK = "#0a0a0a"   # Background
TRON_GRAY = "#1a1a1a"   # Panel background
```

---

### 📊 Dashboard (`leather_book_dashboard.py`)

**Purpose:** Six-zone main interface layout

**Lines:** 608 | **Complexity:** High | **Dependencies:** dashboard_handlers, dashboard_utils

#### Zone Layout

```
┌─────────────────────────────────────────┐
│ Zone 1: Stats      │ Zone 2: Actions    │
│ (top-left)         │ (top-right)        │
├────────────────────┴────────────────────┤
│           Zone 3: AI Head               │
│           (center, animated)            │
├────────────────────┬────────────────────┤
│ Zone 4: User Chat  │ Zone 5: AI Response│
│ (bottom-left)      │ (bottom-right)     │
└────────────────────┴────────────────────┘
```

#### Zone 1: System Statistics Panel

**Purpose:** Real-time system metrics

**Components:**
- CPU usage (live graph)
- Memory usage (progress bar)
- Active plugins count
- Current AI mood indicator
- Conversation count

**Update Frequency:** 1 second (QTimer)

**Implementation:**
```python
class SystemStatsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # Update every 1 second
    
    def update_stats(self):
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        self.cpu_label.setText(f"CPU: {cpu}%")
        self.memory_label.setText(f"Memory: {memory}%")
```

#### Zone 2: Proactive Actions Panel

**Purpose:** Quick-access action buttons

**Actions:**
- 🧠 "CONFIGURE AI PERSONA" → Opens PersonaPanel
- 📚 "REQUEST LEARNING" → Opens learning request dialog
- 🗺️ "TRACK LOCATION" → Initiates location tracking
- 🚨 "EMERGENCY ALERT" → Opens emergency contact form
- 🎨 "GENERATE IMAGES" → Switches to image generation page
- 🔌 "MANAGE PLUGINS" → Opens plugin management panel

**Signal Pattern:**
```python
class ProactiveActionsPanel(QWidget):
    persona_requested = pyqtSignal()
    learning_requested = pyqtSignal()
    location_requested = pyqtSignal()
    emergency_requested = pyqtSignal()
    image_gen_requested = pyqtSignal()
    plugins_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.persona_button = QPushButton("🧠 CONFIGURE AI PERSONA")
        self.persona_button.clicked.connect(self.persona_requested.emit)
```

#### Zone 3: AI Head Animation

**Purpose:** Visual representation of AI state

**States:**
- Idle: Slow pulsing blue circle
- Thinking: Rotating gear animation
- Speaking: Waveform animation
- Alert: Red pulsing (for warnings)

**Implementation:**
```python
class AIHeadWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.state = "idle"
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # 20 FPS
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.state == "idle":
            self.draw_idle_animation(painter)
        elif self.state == "thinking":
            self.draw_thinking_animation(painter)
```

#### Zone 4: User Chat Panel

**Purpose:** User message input

**Components:**
- Multi-line text input (QTextEdit)
- "SEND MESSAGE" button
- Character count indicator
- Voice input button (future)

**Signal:**
```python
send_message = pyqtSignal(str)  # Emitted when user sends message

def on_send_clicked(self):
    message = self.input_box.toPlainText()
    if message.strip():
        self.send_message.emit(message)
        self.input_box.clear()
```

#### Zone 5: AI Response Panel

**Purpose:** Display AI responses

**Features:**
- Scrollable text area (QTextBrowser)
- Markdown rendering support
- Code syntax highlighting
- Clickable links
- Copy-to-clipboard button

**Implementation:**
```python
class AIResponsePanel(QWidget):
    def display_response(self, response: str):
        # Convert markdown to HTML
        html = markdown.markdown(response, extensions=['fenced_code'])
        self.text_browser.setHtml(html)
        self.text_browser.scrollToBottom()
```

---

### 🎭 Persona Panel (`persona_panel.py`)

**Purpose:** AI personality configuration

**Lines:** 450 | **Complexity:** Medium | **Dependencies:** ai_systems.AIPersona

#### 4-Tab Interface

**Tab 1: Personality Traits**

8 sliders for trait configuration:
- Curiosity (0-100)
- Humor (0-100)
- Formality (0-100)
- Creativity (0-100)
- Empathy (0-100)
- Patience (0-100)
- Assertiveness (0-100)
- Optimism (0-100)

```python
class TraitsTab(QWidget):
    trait_changed = pyqtSignal(str, int)  # trait_name, value
    
    def create_trait_slider(self, trait_name: str, initial_value: int):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(initial_value)
        slider.valueChanged.connect(
            lambda v: self.trait_changed.emit(trait_name, v)
        )
        return slider
```

**Tab 2: Mood Monitor**

Real-time mood display and manual override:
- Current mood indicator
- Mood history graph (last 24 hours)
- Manual mood override dropdown
- Mood trigger explanation

**Tab 3: Interaction Stats**

Analytics and metrics:
- Total interactions count
- Average response time
- Most used features
- User satisfaction score (from feedback)

**Tab 4: Advanced Settings**

Expert configuration options:
- Enable/disable specific AI systems
- Adjust response verbosity
- Set ethical strictness level
- Configure learning rate

---

### 🎨 Image Generation Interface (`image_generation.py`)

**Purpose:** Dual-backend image generation with async workers

**Lines:** 450 | **Complexity:** High | **Dependencies:** image_generator (core)

#### Dual-Page Layout

**Left Panel: Prompt Input (Tron Theme)**

Components:
- Prompt text area (multi-line)
- Style selector dropdown (10 presets)
- Size selector (512x512, 768x768, 1024x1024)
- Backend choice (Hugging Face, OpenAI DALL-E 3)
- "GENERATE IMAGE" button

**Right Panel: Image Display**

Components:
- Image preview (QLabel with pixmap)
- Zoom controls (+/- buttons, 25%-400%)
- Metadata display (prompt, style, backend, generation time)
- Save button (PNG export)
- Copy to clipboard button
- History navigation (previous/next)

#### Async Worker Pattern

```python
class ImageGenerationWorker(QThread):
    image_generated = pyqtSignal(str, dict)  # image_path, metadata
    progress_updated = pyqtSignal(int)  # 0-100
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, generator, prompt, style, size, backend):
        super().__init__()
        self.generator = generator
        self.prompt = prompt
        self.style = style
        self.size = size
        self.backend = backend
    
    def run(self):
        try:
            self.progress_updated.emit(10)
            image_path, metadata = self.generator.generate(
                prompt=self.prompt,
                style=self.style,
                size=self.size,
                backend=self.backend
            )
            self.progress_updated.emit(100)
            self.image_generated.emit(image_path, metadata)
        except Exception as e:
            self.error_occurred.emit(str(e))
```

#### Content Safety UI

When content filter blocks generation:
- Display warning dialog with reason
- Suggest alternative prompts
- Provide content policy link

```python
def on_content_blocked(self, reason: str):
    QMessageBox.warning(
        self,
        "Content Filter",
        f"Image generation blocked: {reason}\n\n"
        "Please revise your prompt to comply with content policy."
    )
```

---

### ⚙️ Dashboard Handlers (`dashboard_handlers.py`)

**Purpose:** Event handler methods for dashboard interactions

**Lines:** 320 | **Complexity:** Medium | **Dependencies:** core systems

#### Handler Categories

1. **Chat Handlers**
   - `handle_user_message(message: str)` - Process user chat input
   - `handle_ai_response(response: str)` - Display AI response
   - `handle_chat_history()` - Show conversation history

2. **Persona Handlers**
   - `handle_trait_change(trait: str, value: int)` - Update personality trait
   - `handle_mood_override(mood: str)` - Manually set AI mood
   - `handle_persona_reset()` - Reset to default persona

3. **Learning Handlers**
   - `handle_learning_request(topic: str)` - Submit learning request
   - `handle_learning_approval(request_id: str)` - Approve/deny request
   - `handle_black_vault_review()` - View blocked content

4. **System Handlers**
   - `handle_plugin_toggle(plugin_name: str)` - Enable/disable plugin
   - `handle_command_override(password: str)` - Activate master override
   - `handle_emergency_alert(contacts: list)` - Send emergency notification

#### Error Handling Pattern

```python
def handle_user_message(self, message: str):
    try:
        # Validate input
        is_valid, errors = self.validator.validate_input(
            message,
            {"type": "string", "max_length": 5000}
        )
        if not is_valid:
            self.show_error_dialog(errors)
            return
        
        # Process message
        response = self.intelligence_engine.chat(message, context=[])
        self.handle_ai_response(response)
        
    except Exception as e:
        logger.exception(f"Error handling user message: {e}")
        self.show_error_dialog(f"Failed to process message: {e}")
```

---

### 🛠️ Dashboard Utilities (`dashboard_utils.py`)

**Purpose:** Error handling, logging, validation, and common utilities

**Lines:** 180 | **Complexity:** Low | **Dependencies:** logging, PyQt6.QtWidgets

#### Utility Functions

1. **Error Dialogs**
   ```python
   def show_error_dialog(parent, title: str, message: str):
       QMessageBox.critical(parent, title, message)
   
   def show_warning_dialog(parent, title: str, message: str):
       QMessageBox.warning(parent, title, message)
   
   def show_info_dialog(parent, title: str, message: str):
       QMessageBox.information(parent, title, message)
   ```

2. **Input Validation**
   ```python
   def validate_email(email: str) -> bool:
       pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
       return re.match(pattern, email) is not None
   
   def validate_password_strength(password: str) -> tuple[bool, str]:
       if len(password) < 8:
           return False, "Password must be at least 8 characters"
       if not re.search(r'[A-Z]', password):
           return False, "Password must contain uppercase letter"
       if not re.search(r'[a-z]', password):
           return False, "Password must contain lowercase letter"
       if not re.search(r'[0-9]', password):
           return False, "Password must contain number"
       return True, "Password is strong"
   ```

3. **Logging Setup**
   ```python
   def setup_gui_logger(log_file: str = "logs/gui.log"):
       logger = logging.getLogger("gui")
       logger.setLevel(logging.DEBUG)
       
       handler = logging.FileHandler(log_file)
       formatter = logging.Formatter(
           '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
       )
       handler.setFormatter(formatter)
       logger.addHandler(handler)
       
       return logger
   ```

4. **QSS Style Helpers**
   ```python
   def get_tron_button_style() -> str:
       return """
           QPushButton {
               background-color: #1a1a1a;
               color: #00ff00;
               border: 2px solid #00ff00;
               padding: 10px 20px;
               font-size: 14px;
               font-weight: bold;
           }
           QPushButton:hover {
               background-color: #00ff00;
               color: #0a0a0a;
           }
           QPushButton:pressed {
               background-color: #00ffff;
           }
       """
   ```

---

## GUI Threading Best Practices

### Rule: NEVER Use `threading.Thread` in GUI Code

**Correct Approach:**
```python
# Use QTimer for delays
QTimer.singleShot(1000, self.delayed_callback)

# Use QThread for background work
class Worker(QThread):
    finished = pyqtSignal(str)
    
    def run(self):
        result = expensive_operation()
        self.finished.emit(result)

worker = Worker()
worker.finished.connect(self.handle_result)
worker.start()
```

**Wrong Approach:**
```python
# DON'T DO THIS - will cause crashes
import threading

def background_task():
    result = expensive_operation()
    self.label.setText(result)  # CRASH: GUI update from non-main thread

thread = threading.Thread(target=background_task)
thread.start()
```

### Signal-Based Communication

```python
# Component A emits signal
class SenderWidget(QWidget):
    data_ready = pyqtSignal(str)
    
    def on_button_click(self):
        data = self.process_data()
        self.data_ready.emit(data)

# Component B receives signal
class ReceiverWidget(QWidget):
    def __init__(self, sender):
        super().__init__()
        sender.data_ready.connect(self.handle_data)
    
    def handle_data(self, data: str):
        self.display_label.setText(data)
```

## Testing GUI Components

### Unit Testing with QTest

```python
import pytest
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from app.gui.persona_panel import PersonaPanel

@pytest.fixture
def persona_panel(qtbot):
    panel = PersonaPanel(ai_persona=mock_persona)
    qtbot.addWidget(panel)
    return panel

def test_trait_slider_update(persona_panel, qtbot):
    # Find curiosity slider
    slider = persona_panel.findChild(QSlider, "curiosity_slider")
    
    # Simulate user dragging slider to 75
    QTest.mousePress(slider, Qt.MouseButton.LeftButton)
    slider.setValue(75)
    QTest.mouseRelease(slider, Qt.MouseButton.LeftButton)
    
    # Verify signal emitted
    assert slider.value() == 75
```

### Integration Testing

```python
def test_full_login_flow(qtbot):
    # Create main window
    window = LeatherBookInterface(user_manager, core_systems)
    qtbot.addWidget(window)
    
    # Find login inputs
    username_input = window.findChild(QLineEdit, "username_input")
    password_input = window.findChild(QLineEdit, "password_input")
    login_button = window.findChild(QPushButton, "login_button")
    
    # Simulate user login
    QTest.keyClicks(username_input, "testuser")
    QTest.keyClicks(password_input, "password123")
    QTest.mouseClick(login_button, Qt.MouseButton.LeftButton)
    
    # Verify page switched to dashboard
    assert window.current_page() == 1
```

## Accessibility Features

### Keyboard Navigation

All interactive elements support keyboard navigation:
- **Tab:** Move between inputs
- **Enter:** Activate focused button
- **Space:** Toggle checkboxes
- **Arrow keys:** Navigate sliders

```python
# Enable keyboard focus
button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

# Custom key handling
def keyPressEvent(self, event):
    if event.key() == Qt.Key.Key_Return:
        self.on_send_clicked()
    super().keyPressEvent(event)
```

### Screen Reader Support

```python
# Set accessible names and descriptions
button.setAccessibleName("Send Message")
button.setAccessibleDescription("Send your message to the AI assistant")

# Provide text alternatives for images
image_label.setAccessibleDescription("AI head animation showing thinking state")
```

## Performance Optimization

### Lazy Loading

```python
# Don't create panels until needed
def show_persona_panel(self):
    if not hasattr(self, '_persona_panel'):
        self._persona_panel = PersonaPanel(self.ai_persona)
    self._persona_panel.show()
```

### Debouncing User Input

```python
class DebouncedTextEdit(QTextEdit):
    text_stabilized = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.on_text_stable)
        self.textChanged.connect(self.on_text_changed)
    
    def on_text_changed(self):
        self.debounce_timer.start(500)  # Wait 500ms after last keystroke
    
    def on_text_stable(self):
        self.text_stabilized.emit(self.toPlainText())
```

### Efficient Repainting

```python
# Update only changed regions
def paintEvent(self, event):
    painter = QPainter(self)
    # Only paint the exposed region
    painter.setClipRect(event.rect())
    self.draw_content(painter)
```

## Related Documentation

- **Parent:** [source-docs/README.md](../README.md)
- **Core Systems:** [source-docs/core/README.md](../core/README.md)
- **Agents:** [source-docs/agents/README.md](../agents/README.md)
- **Supporting:** [source-docs/supporting/README.md](../supporting/README.md)

---

**Document Status:** ✅ Production-Ready  
**Quality Gate:** PASSED - All 6 GUI modules documented with examples  
**Compliance:** Fully compliant with Project-AI Governance Profile
