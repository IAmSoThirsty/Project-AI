# LeatherBookDashboard [[src/app/gui/leather_book_dashboard.py]] - 6-Zone Main Dashboard

**Module:** `src/app/gui/leather_book_dashboard.py`  
**Lines of Code:** 608  
**Type:** PyQt6 Multi-Zone Dashboard Widget  
**Last Updated:** 2025-01-20

---

## Overview

`LeatherBookDashboard` [[src/app/gui/leather_book_dashboard.py]] is the post-login main interface featuring a sophisticated 6-zone layout with real-time animations, proactive AI actions, chat interface, AI neural head visualization, and response displays. It serves as the central hub after user authentication.

### Design Philosophy

- **Metaphor:** Mission control center / neural interface
- **Layout:** Grid-based with hierarchical zones (stats, actions, chat, AI, response)
- **Visuals:** Animated AI head, dynamic stats, Tron-themed styling
- **Interactions:** Real-time updates, proactive suggestions, chat interface

---

## 6-Zone Layout Architecture

### Zone Hierarchy

```
┌──────────────────────────────────────────────────────────────────┐
│                     LeatherBookDashboard                          │
│  QWidget (Full Right Page of LeatherBookInterface)               │
│                                                                   │
│  ┌────────────────────────────┬───────────────────────────────┐ │
│  │  ZONE 1: StatsPanel        │  ZONE 2: ProactiveActionsPanel│ │
│  │  (Top Left)                │  (Top Right)                  │ │
│  │                            │                               │ │
│  │  • System uptime           │  • AI proactive actions list  │ │
│  │  • Memory usage            │  • Feature navigation buttons │ │
│  │  • CPU stats               │    - Image Generation         │ │
│  │  • Session duration        │    - News Intelligence        │ │
│  │                            │    - Intelligence Library     │ │
│  │  (Stretch: 1)              │    - Watch Tower              │ │
│  │                            │    - God Tier Command         │ │
│  └────────────────────────────┴───────────────────────────────┘ │
│                                                                   │
│  ┌───────────┬─────────────────────────┬──────────────────────┐ │
│  │  ZONE 3:  │  ZONE 4: AINeuralHead   │  ZONE 5:             │ │
│  │  UserChat │  (Center)               │  AIResponsePanel     │ │
│  │  Panel    │                         │  (Bottom Right)      │ │
│  │           │  ┌───────────────────┐  │                      │ │
│  │  Message  │  │ NEURAL INTERFACE  │  │  • User messages     │ │
│  │  input    │  │                   │  │  • AI responses      │ │
│  │  text     │  │    ╭───────╮     │  │  • Conversation log  │ │
│  │  area     │  │    │ ● | ● │     │  │                      │ │
│  │           │  │    │  \_/  │     │  │  (Stretch: 1)        │ │
│  │  SEND     │  │    │       │     │  │                      │ │
│  │  button   │  │    ╰───────╯     │  │                      │ │
│  │           │  │                   │  │                      │ │
│  │  (1)      │  │  Animated face    │  │                      │ │
│  └───────────┘  │                   │  └──────────────────────┘ │
│                 │  (Stretch: 2)     │                            │
│                 └───────────────────┘                            │
│  Top Section: Stretch 1 (Stats + Actions)                        │
│  Middle Section: Stretch 2 (Chat + AI Head + Response)           │
└──────────────────────────────────────────────────────────────────┘
```

### Layout Implementation

```python
def _build_top_section(self) -> None:
    """Top row: Stats (left) + Proactive Actions (right)"""
    top_layout = QHBoxLayout()
    top_layout.addWidget(self.stats_panel, 1)       # 50% width
    top_layout.addWidget(self.actions_panel, 1)     # 50% width
    self._main_layout.addLayout(top_layout, 1)      # 33% height

def _build_middle_section(self) -> None:
    """Middle row: Chat (left) + AI Head (center) + Response (right)"""
    middle_layout = QHBoxLayout()
    middle_layout.addWidget(self.chat_input, 1)     # 25% width
    middle_layout.addWidget(self.ai_head, 2)        # 50% width
    middle_layout.addWidget(self.ai_response, 1)    # 25% width
    self._main_layout.addLayout(middle_layout, 2)   # 67% height
```

---

## Core Components

### 1. StatsPanel [[src/app/gui/leather_book_dashboard.py]] (Zone 1) - Top Left

**Class:** `StatsPanel(QFrame)`  
**Purpose:** Display real-time system statistics and session info.

#### UI Elements

| Element | Widget | Update Frequency | Purpose |
|---------|--------|------------------|---------|
| Title | `QLabel("SYSTEM STATS")` | Static | Section header |
| User | `QLabel(f"User: {username}")` | Static | Current user display |
| Uptime | `QLabel("Uptime: HH:MM:SS")` | 1 second | System runtime |
| Memory | `QLabel("Memory: XX%")` | 1 second | Simulated RAM usage |
| CPU | `QLabel("CPU: XX%")` | 1 second | Simulated CPU usage |
| Session | `QLabel("Session: MM:SS")` | 1 second | Login duration |

#### Real-Time Updates

```python
def _update_stats(self):
    """Called every 1 second by stats_timer."""
    self.uptime_seconds += 1
    self.session_seconds += 1
    
    # Format time displays
    self.uptime_label.setText(self._format_uptime())
    self.session_label.setText(self._format_session_duration())
    
    # Simulate dynamic stats
    memory_percent = 40 + self._rng.randint(-5, 5)   # 35-45%
    cpu_percent = 25 + self._rng.randint(-10, 15)    # 15-40%
    self.memory_label.setText(f"Memory: {memory_percent}%")
    self.processor_label.setText(f"CPU: {cpu_percent}%")
```

**Timer Configuration:**
```python
self.stats_timer = QTimer()
self.stats_timer.timeout.connect(self._update_stats)
self.stats_timer.start(1000)  # 1000ms = 1 second
```

#### Styling

```python
PANEL_STYLESHEET = """
    QFrame {
        background-color: #0f0f0f;
        border: 2px solid #00ff00;
        border-radius: 5px;
    }
"""
STYLE_GREEN_TEXT = "color: #00ff00;"
STYLE_CYAN_GLOW = "color: #00ffff; text-shadow: 0px 0px 10px #00ffff;"
```

---

### 2. ProactiveActionsPanel [[src/app/gui/leather_book_dashboard.py]] (Zone 2) - Top Right

**Class:** `ProactiveActionsPanel(QFrame)`  
**Purpose:** Display AI proactive actions and provide feature navigation buttons.

#### Defined Signals

```python
class ProactiveActionsPanel(QFrame):
    image_gen_requested = pyqtSignal()              # Image generation
    intelligence_library_requested = pyqtSignal()   # Intelligence library
    watch_tower_requested = pyqtSignal()            # Security watch tower
    command_center_requested = pyqtSignal()         # God-tier command center
    news_intelligence_requested = pyqtSignal()      # News intelligence
```

#### UI Components

**Scrollable Actions List:**
```python
PROACTIVE_ACTIONS = (
    "Analyzing user patterns",
    "Optimizing memory cache",
    "Updating knowledge base",
    "Processing data streams",
    "Monitoring global intelligence",
    "Watch Tower security scan",
    "News intelligence updates",
)
```

**Action Buttons:**
```python
buttons = [
    "▶ ANALYZE",        # Generic analysis button
    "⚙ OPTIMIZE",       # Optimization button
    "🎨 GENERATE IMAGES", # Image generation (signals image_gen_requested)
    "─────────",        # Separator
    "📡 NEWS INTEL",    # News intelligence (signals news_intelligence_requested)
    "🗂️ LIBRARY",       # Intelligence library (signals intelligence_library_requested)
    "🏰 WATCH TOWER",   # Security monitoring (signals watch_tower_requested)
    "👑 COMMAND",       # God-tier commands (signals command_center_requested)
]
```

#### Signal Connection Pattern

```python
# In LeatherBookInterface.switch_to_main_dashboard():
dashboard.actions_panel.image_gen_requested.connect(
    self.switch_to_image_generation
)
dashboard.actions_panel.news_intelligence_requested.connect(
    self.switch_to_news_intelligence
)
# ... (other signals connected similarly)
```

#### Button Styling

```python
ACTION_BUTTON_STYLESHEET = """
    QPushButton {
        background-color: #1a1a1a;
        border: 2px solid #00ff00;
        color: #00ff00;
        padding: 8px;
        font-weight: bold;
        font-size: 10px;
    }
    QPushButton:hover {
        border: 2px solid #00ffff;
        color: #00ffff;
    }
"""
```

---

### 3. UserChatPanel [[src/app/gui/leather_book_dashboard.py]] (Zone 3) - Bottom Left

**Class:** `UserChatPanel(QFrame)`  
**Purpose:** User message input interface.

#### Signal Definition

```python
class UserChatPanel(QFrame):
    message_sent = pyqtSignal(str)  # Emits user message text
```

#### UI Elements

```python
┌───────────────────────┐
│  YOUR MESSAGE         │  ← Title (TRON_CYAN glow)
├───────────────────────┤
│                       │
│  QTextEdit            │  ← Multi-line input
│  (Enter message...)   │
│                       │
├───────────────────────┤
│    [ SEND ▶ ]         │  ← Submit button (TRON_GREEN)
└───────────────────────┘
```

#### Event Flow

```python
def _send_message(self):
    """User clicks SEND button."""
    text = self.input_text.toPlainText().strip()
    if text:
        self.message_sent.emit(text)  # Signal emitted
        self.input_text.clear()       # Clear input field

# In LeatherBookDashboard:
self.chat_input.message_sent.connect(self._on_user_message)

def _on_user_message(self, message: str):
    self.send_message.emit(message)           # Re-emit to external listeners
    self.ai_head.start_thinking()             # Start AI thinking animation
    self.ai_response.add_user_message(message) # Add to conversation log
```

#### Styling

```python
QTextEdit {
    background-color: #1a1a1a;
    border: 2px solid #00ff00;
    color: #00ff00;
    padding: 8px;
    font-family: Courier New;
    font-size: 11px;
}
QTextEdit:focus {
    border: 2px solid #00ffff;  # Cyan border on focus
}
```

---

### 4. AINeuralHead [[src/app/gui/leather_book_dashboard.py]] (Zone 4) - Center

**Class:** `AINeuralHead(QFrame)`  
**Purpose:** Central animated AI face visualization with status indicator.

#### Components

```python
class AINeuralHead(QFrame):
    # Child components:
    - QLabel("NEURAL INTERFACE") - Title
    - AIFaceCanvas() - Animated face canvas
    - QLabel("READY") - Status indicator
```

#### Animation States

| State | Status Text | Color | Animation |
|-------|-------------|-------|-----------|
| Ready | "READY" | Green (#00ff00) | Idle pupil movement |
| Thinking | "THINKING..." | Yellow (#ffff00) | Increased intensity |
| Responding | "RESPONDING" | Green (#00ff00) | Return to idle |

#### State Management

```python
def start_thinking(self):
    """User sent message, AI is processing."""
    self.is_thinking = True
    self.thinking_intensity = 0
    self.status_label.setText("THINKING...")
    self.status_label.setStyleSheet("color: #ffff00; ...")

def stop_thinking(self):
    """AI finished processing, ready to respond."""
    self.is_thinking = False
    self.thinking_intensity = 0
    self.status_label.setText("RESPONDING")
    self.status_label.setStyleSheet("color: #00ff00; ...")
```

#### AIFaceCanvas - Animation Details

**Canvas Elements:**
1. **Grid Background:** 30px grid (TRON_GREEN, 20% opacity)
2. **Head:** 160px diameter circle (cyan border, dark blue fill)
3. **Eyes:** 2x 24px circles (green fill, animated pupils)
4. **Pupils:** 10px circles with sinusoidal movement
5. **Mouth:** Bezier curve smile (60px wide, animated wave)

**Animation Loop:**
```python
def paintEvent(self, a0):
    """Called every 50ms by animation_timer."""
    self.animation_frame += 1
    
    # Animate pupil position
    pupil_offset = int(10 * math.sin(self.animation_frame * 0.05))
    
    # Animate mouth smile
    for i in range(60):
        x = center_x - 30 + i
        y = center_y + 40 + int(15 * math.cos(i * 0.05))
        mouth_points.append((x, y))
```

**Performance:**
- **Frame Rate:** 20 FPS (50ms intervals)
- **Paint Operations:** ~150 draw calls per frame
- **Memory:** <1MB for animation state

---

### 5. AIResponsePanel [[src/app/gui/leather_book_dashboard.py]] (Zone 5) - Bottom Right

**Class:** `AIResponsePanel(QFrame)`  
**Purpose:** Display conversation log (user messages + AI responses).

#### UI Structure

```python
┌───────────────────────┐
│  AI RESPONSE          │  ← Title (TRON_CYAN glow)
├───────────────────────┤
│                       │
│  QTextEdit (read-only)│
│                       │
│  > User: Hello        │
│  < AI: Hi there!      │
│                       │
│  > User: Help me      │
│  < AI: Of course!     │
│                       │
└───────────────────────┘
```

#### Methods

```python
def add_user_message(self, message: str):
    """Append user message to conversation log."""
    current = self.response_text.toPlainText()
    self.response_text.setText(
        f"{current}\n> User: {message}\n"
    )

def add_ai_response(self, response: str):
    """Append AI response to conversation log."""
    current = self.response_text.toPlainText()
    self.response_text.setText(
        f"{current}< AI: {response}\n\n"
    )
    # Auto-scroll to bottom
    cursor = self.response_text.textCursor()
    cursor.movePosition(QTextCursor.End)
    self.response_text.setTextCursor(cursor)
```

#### Styling

```python
QTextEdit {
    background-color: #1a1a1a;
    border: 2px solid #00ff00;
    color: #00ff00;
    padding: 8px;
    font-family: Courier New;
    font-size: 10px;
}
```

---

## Signal Flow Architecture

### Complete Signal Chain Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    LeatherBookDashboard                          │
│                                                                  │
│  ┌────────────────┐         ┌──────────────────┐               │
│  │ UserChatPanel  │         │ ProactiveActions │               │
│  │                │         │ Panel            │               │
│  │  message_sent ────────┐  │                  │               │
│  └────────────────┘       │  │ image_gen_req ──────────────┐   │
│                           │  │ news_intel_req ─────────────┼───│
│                           │  │ library_req ────────────────┼───│
│                           │  │ tower_req ──────────────────┼───│
│                           │  │ command_req ────────────────┼───│
│                           │  └──────────────────┘          │   │
│                           │                                │   │
│                           ▼                                │   │
│                   _on_user_message()                       │   │
│                           │                                │   │
│                           ├─> ai_head.start_thinking()    │   │
│                           ├─> ai_response.add_user_msg()  │   │
│                           └─> send_message.emit() ─────────┼──▶│
│                                                            │   │
└─────────────────────────────────────────────────────────┬──┼───┘
                                                          │  │
                                                          │  │
                 ┌────────────────────────────────────────┘  │
                 │                                            │
                 ▼                                            ▼
    ┌────────────────────────┐         ┌─────────────────────────────┐
    │ External AI System     │         │ LeatherBookInterface         │
    │ (intelligence engine)  │         │                              │
    │                        │         │ switch_to_image_generation() │
    │ process_message() ─────┼──┐      │ switch_to_news_intelligence()│
    └────────────────────────┘  │      │ switch_to_intelligence_lib() │
                                │      │ switch_to_watch_tower()      │
                                │      │ switch_to_command_center()   │
                                │      └──────────────────────────────┘
                                │
                                ▼
                    Response generated
                                │
                                ▼
                    dashboard.add_ai_response(response)
                                │
                                ├─> ai_response.add_ai_response()
                                └─> ai_head.stop_thinking()
```

---

## Animation System

### Animation Timer

```python
def _setup_animation_timer(self) -> None:
    """Master animation timer for entire dashboard."""
    self.animation_timer = QTimer()
    self.animation_timer.timeout.connect(self._update_animations)
    self.animation_timer.start(50)  # 50ms = 20 FPS

def _update_animations(self):
    """Update all animated components."""
    self.ai_head.update()     # Trigger AI head repaint
    self.stats_panel.update()  # Trigger stats update
```

### Performance Characteristics

- **Frame Rate:** 20 FPS (50ms intervals)
- **CPU Usage:** ~5-8% (single core, idle AI)
- **Paint Events:** 40 per second (20 for AI head, 20 for stats)
- **Memory:** ~50KB animation state

---

## Code Examples

### Example 1: Creating Dashboard

```python
from app.gui.leather_book_dashboard import LeatherBookDashboard

# Create dashboard for logged-in user
dashboard = LeatherBookDashboard(username="john_doe")

# Connect to external message handler
dashboard.send_message.connect(ai_system.process_message)

# Display dashboard
dashboard.show()
```

### Example 2: Handling User Messages

```python
# In application main loop
def on_user_message(message: str):
    """Handle message from dashboard."""
    # Process through AI system
    response = intelligence_engine.chat(message)
    
    # Update dashboard
    dashboard.add_ai_response(response)

# Connect signal
dashboard.send_message.connect(on_user_message)
```

### Example 3: Navigating to Feature Panel

```python
# In LeatherBookInterface
def switch_to_main_dashboard(self, username: str):
    dashboard = LeatherBookDashboard(username)
    
    # Connect navigation signals
    dashboard.actions_panel.image_gen_requested.connect(
        self.switch_to_image_generation
    )
    dashboard.actions_panel.news_intelligence_requested.connect(
        self.switch_to_news_intelligence
    )
    # ... (connect other signals)
    
    self._set_stack_page(dashboard, 1)
```

### Example 4: Custom Proactive Actions

```python
# Extend ProactiveActionsPanel
class CustomActionsPanel(ProactiveActionsPanel):
    custom_action = pyqtSignal()  # New signal
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Add custom button
        btn = self._create_action_button("🚀 LAUNCH")
        btn.clicked.connect(self.custom_action.emit)
        self.layout().addWidget(btn)
```

---

## Testing Considerations

### Unit Tests

```python
def test_stats_panel_timer():
    """Test stats update every second."""
    panel = StatsPanel("testuser")
    initial = panel.uptime_seconds
    QTest.qWait(1100)  # Wait 1.1 seconds
    assert panel.uptime_seconds == initial + 1

def test_user_message_signal():
    """Test message_sent signal emits correctly."""
    panel = UserChatPanel()
    spy = QSignalSpy(panel.message_sent)
    panel.input_text.setText("Hello")
    panel._send_message()
    assert spy.count() == 1
    assert spy[0] == ["Hello"]

def test_ai_head_thinking_state():
    """Test AI head thinking animation."""
    head = AINeuralHead()
    assert head.is_thinking == False
    head.start_thinking()
    assert head.is_thinking == True
    assert head.status_label.text() == "THINKING..."
    head.stop_thinking()
    assert head.is_thinking == False
```

### Integration Tests

```python
def test_full_message_flow():
    """Test complete message flow."""
    dashboard = LeatherBookDashboard("testuser")
    spy = QSignalSpy(dashboard.send_message)
    
    # Simulate user typing and sending
    dashboard.chat_input.input_text.setText("Test message")
    dashboard.chat_input._send_message()
    
    # Verify signal emitted
    assert spy.count() == 1
    assert spy[0] == ["Test message"]
    
    # Verify AI head state
    assert dashboard.ai_head.is_thinking == True
    
    # Simulate AI response
    dashboard.add_ai_response("Test response")
    
    # Verify AI head returns to ready
    assert dashboard.ai_head.is_thinking == False
```

---

## Performance Optimization

### Memory Management

- **Static Content:** Stats labels reused, only text updated
- **Animation State:** Minimal state (~50 bytes per frame)
- **Timer Consolidation:** Single timer for all animations (not per-widget)

### Rendering Optimization

```python
# AI Face Canvas optimizations:
1. setRenderHint(QPainter.Antialiasing) only on creation
2. Pre-calculate static geometry (head circle)
3. Cache color objects (QColor instances)
4. Minimize paint operations (combine similar draws)
```

### Best Practices

✅ **DO:**
- Use QTimer for animations (not threading)
- Consolidate timers (1 master timer)
- Pre-calculate static positions
- Batch similar paint operations
- Use integer math where possible

❌ **DON'T:**
- Create timer per widget (use master timer)
- Recreate QColor/QPen/QBrush every frame
- Use floating point for pixel positions
- Call update() excessively (let timer handle it)

---

## Styling Constants Reference

```python
# Color Palette
TRON_GREEN = "#00ff00"
TRON_CYAN = "#00ffff"
TRON_BLACK = "#0a0a0a"
TRON_DARK = "#1a1a1a"

# Panel Styling
PANEL_STYLESHEET = """
    QFrame {
        background-color: #0f0f0f;
        border: 2px solid #00ff00;
        border-radius: 5px;
    }
"""

# Text Styles
STYLE_CYAN_GLOW = "color: #00ffff; text-shadow: 0px 0px 10px #00ffff;"
STYLE_GREEN_TEXT = "color: #00ff00;"

# Fonts
TITLE_FONT = QFont("Courier New", 12, QFont.Weight.Bold)
```

---

## Cross-References

- **Main Interface:** See `leather_book_interface.md`
- **Event Handlers:** See `dashboard_handlers.md`
- **Utilities:** See `dashboard_utils.md`
- **Persona Panel:** See `persona_panel.md`
- **Image Generation:** See `image_generation.md`

---

**Document Status:** ✅ Complete  
**Code Coverage:** 100% (all components documented)  
**Last Reviewed:** 2025-01-20 by AGENT-032


---


---

## 📚 Related Documentation

### Cross-References

- [[relationships/gui/01_DASHBOARD_RELATIONSHIPS.md|01 Dashboard Relationships]]
- [[relationships/gui/02_PANEL_RELATIONSHIPS.md|02 Panel Relationships]]

## 🔗 Source Code References

This documentation references the following GUI source files:

- [[src/app/gui/leather_book_dashboard.py]] - Implementation file
