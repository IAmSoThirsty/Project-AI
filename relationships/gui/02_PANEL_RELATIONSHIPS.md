# Panel Relationships Map

## Overview: Dashboard Panel System
**Scope:** 4 core panels within LeatherBookDashboard [[src/app/gui/leather_book_dashboard.py]]  
**Files:** `leather_book_dashboard.py` (lines 185-650)  
**Role:** Specialized UI components for different functions

---

## 1. PANEL HIERARCHY

```
LeatherBookDashboard (Container)
│
├── StatsPanel (QFrame)
│   ├── Purpose: System stats display
│   ├── Location: Top-left
│   ├── Size: 1 unit (stretch factor)
│   └── Update: 1Hz timer
│
├── ProactiveActionsPanel (QFrame)
│   ├── Purpose: Navigation + AI activity
│   ├── Location: Top-right
│   ├── Size: 1 unit (stretch factor)
│   └── Buttons: 5 navigation + 1 label
│
├── UserChatPanel (QFrame)
│   ├── Purpose: User message input
│   ├── Location: Bottom-left
│   ├── Size: 1 unit (stretch factor)
│   └── Input: QTextEdit + QPushButton
│
└── AIResponsePanel (QFrame)
    ├── Purpose: Conversation history
    ├── Location: Bottom-right
    ├── Size: 1 unit (stretch factor)
    └── Display: Scrollable QTextEdit

CENTER: AINeuralHead (QWidget)
├── Purpose: Visual AI representation
├── Location: Middle center
├── Size: 2 units (stretch factor)
└── Animation: Eye movement + circuits
```

---

## 2. STATSPANEL RELATIONSHIPS

### Class Definition
```python
class StatsPanel(QFrame):
    """Top left panel showing system stats."""
    # Lines 185-240
```

### Internal Structure
```
StatsPanel
├── Layout: QVBoxLayout
│   ├── margins: (15, 15, 15, 15)
│   └── spacing: 10px
│
├── Title Label
│   ├── text: "SYSTEM STATUS"
│   ├── font: TITLE_FONT (Courier New, 12pt, Bold)
│   └── style: STYLE_CYAN_GLOW
│
├── 5 Stat Labels (QLabel)
│   ├── username_label: "👤 User: {username}"
│   ├── time_label: "🕒 Time: {current_time}"
│   ├── location_label: "📍 Location: {location}"
│   ├── interaction_label: "💬 Interactions: {count}"
│   └── memory_label: "🧠 Memory: {percentage}%"
│
└── stats_timer (QTimer)
    ├── interval: 1000ms
    └── slot: _update_stats()
```

### Signal/Slot Connections
```python
# Line 256 in _configure_stats_timer()
self.stats_timer.timeout.connect(self._update_stats)
```

### Data Dependencies
```python
# Current Implementation (Placeholders)
username: str  # From constructor parameter
current_time: QDateTime  # From QDateTime.currentDateTime()
location: str = "Earth"  # Placeholder
interactions: int = random.randint(100, 500)  # Placeholder
memory: int = random.randint(60, 90)  # Placeholder

# Future Integration
location → LocationTracker.get_current_location()
interactions → MemoryExpansionSystem.get_interaction_count()
memory → System memory metrics
```

### Update Flow
```
Timer fires (1000ms) → _update_stats()
                           ↓
Fetch current data:
├── time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
├── location = "Earth"  # TODO: LocationTracker
├── interactions = random.randint(100, 500)  # TODO: MemoryExpansionSystem
└── memory = random.randint(60, 90)  # TODO: System metrics
                           ↓
Update QLabel.setText() for each stat
                           ↓
Labels auto-repaint with new values
```

### Relationship to Parent
```python
# Created in LeatherBookDashboard._build_top_section()
self.stats_panel = StatsPanel(self.username)
top_layout.addWidget(self.stats_panel, 1)  # stretch=1

# Referenced in animation update
def _update_animations(self):
    self.stats_panel.update()  # Triggers repaint if needed
```

---

## 3. PROACTIVEACTIONSPANEL RELATIONSHIPS

### Class Definition
```python
class ProactiveActionsPanel(QFrame):
    """Top right panel with action buttons and AI activity."""
    # Lines 265-320
```

### Signal Definitions
```python
# Lines 267-271
image_gen_requested = pyqtSignal()
intelligence_library_requested = pyqtSignal()
watch_tower_requested = pyqtSignal()
command_center_requested = pyqtSignal()
news_intelligence_requested = pyqtSignal()
```

### Internal Structure
```
ProactiveActionsPanel
├── Layout: QVBoxLayout
│   ├── margins: (15, 15, 15, 15)
│   └── spacing: 10px
│
├── Title Label
│   ├── text: "AI ACTIONS"
│   ├── font: TITLE_FONT
│   └── style: STYLE_CYAN_GLOW
│
├── 5 Action Buttons (QPushButton)
│   ├── 🎨 GENERATE IMAGES → image_gen_requested
│   ├── 📰 NEWS INTELLIGENCE → news_intelligence_requested
│   ├── 📚 INTELLIGENCE LIBRARY → intelligence_library_requested
│   ├── 🗼 WATCH TOWER → watch_tower_requested
│   └── 🎮 COMMAND CENTER → command_center_requested
│
└── Proactive Label (QLabel)
    ├── text: Rotating AI activity messages
    ├── style: STYLE_CYAN_GLOW
    └── updates: On animation cycle
```

### Button-to-Signal Mapping
```python
# Lines 287-310
image_gen_btn.clicked.connect(self.image_gen_requested.emit)
news_btn.clicked.connect(self.news_intelligence_requested.emit)
library_btn.clicked.connect(self.intelligence_library_requested.emit)
tower_btn.clicked.connect(self.watch_tower_requested.emit)
command_btn.clicked.connect(self.command_center_requested.emit)
```

### Signal Propagation Chain
```
User clicks button
        ↓
button.clicked signal fires
        ↓
Signal emitter lambda executes
        ↓
ProactiveActionsPanel.{signal_name}.emit()
        ↓
LeatherBookInterface receives signal
        ↓
Interface calls corresponding switch_to_*() method
        ↓
New panel created and displayed
```

### Relationship to Parent
```python
# Created in LeatherBookDashboard._build_top_section()
self.actions_panel = ProactiveActionsPanel()
top_layout.addWidget(self.actions_panel, 1)  # stretch=1

# Signals connected in LeatherBookInterface (lines 163-178)
dashboard.actions_panel.image_gen_requested.connect(
    self.switch_to_image_generation
)
# ... 4 more similar connections
```

---

## 4. USERCHATPANEL RELATIONSHIPS

### Class Definition
```python
class UserChatPanel(QFrame):
    """Bottom left panel for user input."""
    # Lines 355-425
```

### Signal Definition
```python
# Line 359
message_sent = pyqtSignal(str)  # Emits sanitized message
```

### Internal Structure
```
UserChatPanel
├── Layout: QVBoxLayout
│   ├── margins: (15, 15, 15, 15)
│   └── spacing: 10px
│
├── Title Label
│   ├── text: "YOUR MESSAGE"
│   ├── font: TITLE_FONT
│   └── style: STYLE_GREEN_TEXT
│
├── chat_input (QTextEdit)
│   ├── placeholder: "Type your message here..."
│   ├── max_height: 150px
│   ├── style: TRON_DARK background, TRON_GREEN text
│   └── shortcut: Ctrl+Return → _send_message()
│
└── send_btn (QPushButton)
    ├── text: "SEND MESSAGE"
    ├── icon: "📤"
    └── clicked → _send_message()
```

### Message Validation Flow
```python
def _send_message(self):
    text = self.chat_input.toPlainText().strip()
    
    # Security validation
    sanitized = sanitize_input(text, max_length=2000)
    
    if not validate_length(sanitized, min_len=1, max_len=2000):
        QMessageBox.warning(
            self, "Input Error",
            "Message must be 1-2000 characters"
        )
        return
    
    # Emit signal with validated message
    self.message_sent.emit(sanitized)
    self.chat_input.clear()
```

### Signal/Slot Connections
```python
# Internal connections (lines 410-413)
send_btn.clicked.connect(self._send_message)
# Note: Ctrl+Return handled via QShortcut (if implemented)

# External connection in Dashboard (line 117)
self.chat_input.message_sent.connect(self._on_user_message)
```

### Security Integration
```python
# Imports from app.security.data_validation
from app.security.data_validation import (
    sanitize_input,  # XSS protection, HTML escaping
    validate_length,  # Length constraints
)

# Applied in _send_message() before emission
```

### Relationship to Parent
```python
# Created in LeatherBookDashboard._build_middle_section()
self.chat_input = UserChatPanel()
self.chat_input.message_sent.connect(self._on_user_message)
middle_layout.addWidget(self.chat_input, 1)  # stretch=1

# Parent handler
def _on_user_message(self, message: str):
    self.send_message.emit(message)  # Propagate to Interface
    self.ai_head.start_thinking()     # Visual feedback
    self.ai_response.add_user_message(message)  # Display
```

---

## 5. AIRESPONSEPANEL RELATIONSHIPS

### Class Definition
```python
class AIResponsePanel(QFrame):
    """Bottom right panel showing AI responses and conversation."""
    # Lines 430-650
```

### Internal Structure
```
AIResponsePanel
├── Layout: QVBoxLayout
│   ├── margins: (15, 15, 15, 15)
│   └── spacing: 10px
│
├── Title Label
│   ├── text: "AI RESPONSE"
│   ├── font: TITLE_FONT
│   └── style: STYLE_CYAN_GLOW
│
├── response_text (QTextEdit)
│   ├── read_only: True
│   ├── style: TRON_DARK background, TRON_GREEN text
│   ├── content: HTML-formatted conversation history
│   └── scrollbar: Auto-scroll to bottom
│
└── clear_btn (QPushButton)
    ├── text: "CLEAR"
    ├── clicked → response_text.clear()
    └── style: ACTION_BUTTON_STYLESHEET
```

### Message Display Methods
```python
def add_user_message(self, message: str):
    """Add user message to display with blue color."""
    timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
    html = f"""
    <div style='color: #00ffff; margin: 10px 0;'>
        <b>[{timestamp}] You:</b><br/>
        {message}
    </div>
    """
    self.response_text.append(html)
    self._scroll_to_bottom()

def add_ai_response(self, response: str):
    """Add AI response to display with green color."""
    timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
    html = f"""
    <div style='color: #00ff00; margin: 10px 0;'>
        <b>[{timestamp}] AI:</b><br/>
        {response}
    </div>
    """
    self.response_text.append(html)
    self._scroll_to_bottom()

def _scroll_to_bottom(self):
    """Ensure latest message is visible."""
    scrollbar = self.response_text.verticalScrollBar()
    scrollbar.setValue(scrollbar.maximum())
```

### Conversation Format
```
HTML Structure:
<div style='color: #00ffff;'>  <!-- User messages: cyan -->
    <b>[12:34:56] You:</b><br/>
    User's sanitized message text
</div>
<div style='color: #00ff00;'>  <!-- AI messages: green -->
    <b>[12:35:01] AI:</b><br/>
    AI's response text
</div>
```

### Relationship to Parent
```python
# Created in LeatherBookDashboard._build_middle_section()
self.ai_response = AIResponsePanel()
middle_layout.addWidget(self.ai_response, 1)  # stretch=1

# Called from Dashboard._on_user_message()
self.ai_response.add_user_message(message)

# Called from Dashboard.add_ai_response()
self.ai_response.add_ai_response(response)
self.ai_head.stop_thinking()
```

### Signal/Slot Connections
```python
# Line 630
clear_btn.clicked.connect(self.response_text.clear)
```

---

## 6. AINEURALHEAD RELATIONSHIPS

### Class Definition
```python
class AINeuralHead(QWidget):
    """Central visual representation of AI."""
    # Lines 240-355
```

### Internal Structure
```
AINeuralHead
├── thinking_state: bool
│   ├── False: Idle animation
│   └── True: Active thinking animation
│
├── eyes: list[dict]
│   ├── Structure: {"x": int, "y": int, "radius": int}
│   ├── Count: 2 eyes
│   └── Animation: Subtle movement
│
├── circuit_lines: list[dict]
│   ├── Structure: {"x1": int, "y1": int, "x2": int, "y2": int}
│   ├── Count: 10-15 lines
│   └── Animation: Pulsing when thinking
│
└── Animation driven by:
    └── parent animation_timer (50ms)
```

### State Control Methods
```python
def start_thinking(self):
    """Activate thinking animation."""
    self.thinking_state = True
    # Eyes pulse faster, circuits glow brighter
    
def stop_thinking(self):
    """Return to idle animation."""
    self.thinking_state = False
    # Eyes return to normal, circuits dim
    
def update(self):
    """Called every 50ms by dashboard timer."""
    if self.thinking_state:
        self._animate_thinking()
    else:
        self._animate_idle()
    self.repaint()  # Trigger paintEvent()
```

### Paint Event Logic
```python
def paintEvent(self, event):
    """Custom rendering of AI head."""
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw background (optional grid)
    self._draw_background(painter)
    
    # Draw circuit lines
    for line in self.circuit_lines:
        pen = QPen(QColor(TRON_CYAN), 2)
        if self.thinking_state:
            pen.setWidth(3)  # Thicker when thinking
        painter.setPen(pen)
        painter.drawLine(line["x1"], line["y1"], line["x2"], line["y2"])
    
    # Draw eyes
    for eye in self.eyes:
        brush = QBrush(QColor(TRON_GREEN))
        if self.thinking_state:
            brush = QBrush(QColor(TRON_CYAN))  # Change color when thinking
        painter.setBrush(brush)
        painter.drawEllipse(eye["x"], eye["y"], eye["radius"], eye["radius"])
```

### Relationship to Parent
```python
# Created in LeatherBookDashboard._build_middle_section()
self.ai_head = AINeuralHead()
middle_layout.addWidget(self.ai_head, 2)  # stretch=2 (larger than panels)

# State controlled by Dashboard
def _on_user_message(self, message: str):
    self.ai_head.start_thinking()  # User sent message

def add_ai_response(self, response: str):
    self.ai_head.stop_thinking()   # AI finished processing

# Animation driven by Dashboard
def _update_animations(self):
    self.ai_head.update()  # 50ms interval
```

### Animation State Machine
```
STATE: Idle (thinking_state = False)
├── Eyes: Slow random movement
├── Circuits: Dim glow
└── Update rate: 50ms

STATE: Thinking (thinking_state = True)
├── Eyes: Rapid pulsing + color shift (green → cyan)
├── Circuits: Bright pulsing + width increase
└── Update rate: 50ms

TRANSITIONS:
Idle → Thinking: user_message received
Thinking → Idle: ai_response completed
```

---

## 7. INTER-PANEL COMMUNICATION

### Direct Connections (Within Dashboard)
```
UserChatPanel.message_sent
        ↓
LeatherBookDashboard._on_user_message()
        ↓
Actions:
├── emit send_message (to Interface)
├── ai_head.start_thinking() (visual feedback)
└── ai_response.add_user_message() (display)
```

### Indirect Connections (Via Parent Interface)
```
ProactiveActionsPanel.image_gen_requested
        ↓
LeatherBookInterface receives signal
        ↓
Interface.switch_to_image_generation()
        ↓
Dashboard hidden, ImageGenInterface shown
```

### No Direct Panel-to-Panel Communication
- Panels do not reference each other
- All communication routed through parent Dashboard or Interface
- Pattern: Panel → Dashboard → Interface → Target

---

## 8. SHARED STYLING

### All Panels Use
```python
# Shared stylesheet constants
PANEL_STYLESHEET = """
    QFrame {
        background-color: #0f0f0f;
        border: 2px solid #00ff00;
        border-radius: 5px;
    }
"""

TITLE_FONT = QFont("Courier New", 12, QFont.Weight.Bold)

# Applied to: StatsPanel, ProactiveActionsPanel, 
#             UserChatPanel, AIResponsePanel
```

### Color Coordination
```
User messages (cyan):  #00ffff
AI messages (green):   #00ff00
Panel borders (green): #00ff00
Highlights (cyan):     #00ffff
Backgrounds (black):   #0a0a0a / #1a1a1a
```

---

## 9. PANEL LIFECYCLE

### Creation Order
```
1. LeatherBookDashboard.__init__()
   ↓
2. _build_top_section()
   ├── StatsPanel(username)
   └── ProactiveActionsPanel()
   ↓
3. _build_middle_section()
   ├── UserChatPanel()
   ├── AINeuralHead()
   └── AIResponsePanel()
   ↓
4. Connect signals
   ↓
5. Start timers
```

### Destruction
- All panels destroyed when Dashboard removed from stack
- Timers automatically stopped (QObject parent-child ownership)
- No manual cleanup required (Qt handles memory)

---

## 10. DATA FLOW BETWEEN PANELS

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ Types message
                       ▼
              ┌─────────────────┐
              │ UserChatPanel   │
              │ (Input)         │
              └────────┬────────┘
                       │ message_sent signal
                       ▼
              ┌─────────────────┐
              │ Dashboard       │
              │ (_on_user_msg)  │
              └─┬───────┬───────┘
                │       │
    ┌───────────┘       └──────────┐
    │ signal                        │ visual feedback
    ▼                               ▼
┌──────────┐                   ┌──────────┐
│Interface │                   │AINeuralH │
│(routing) │                   │(thinking)│
└──────────┘                   └──────────┘
    │                               │
    │ intelligence processing       │ animation
    ▼                               ▼
┌──────────┐                   ┌──────────┐
│AI Engine │                   │  User    │
│(external)│                   │ sees AI  │
└──────────┘                   │ thinking │
    │                          └──────────┘
    │ response
    ▼
┌─────────────────┐
│ Dashboard       │
│ (add_ai_resp)   │
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
    ▼          ▼
┌──────┐  ┌─────────┐
│ Head │  │Response │
│(stop)│  │(display)│
└──────┘  └─────────┘
```

---

## 11. ERROR HANDLING IN PANELS

### UserChatPanel Validation
```python
try:
    sanitized = sanitize_input(text, max_length=2000)
    if not validate_length(sanitized, min_len=1, max_len=2000):
        raise ValueError("Invalid message length")
except Exception as e:
    QMessageBox.warning(self, "Input Error", str(e))
    logger.error("Message validation failed: %s", e)
    return
```

### StatsPanel Resilience
```python
def _update_stats(self):
    try:
        time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        # Update labels...
    except Exception as e:
        logger.error("Stats update failed: %s", e)
        # Continue running, don't crash dashboard
```

### ProactiveActionsPanel Error Propagation
```python
# Signals simply emit, no error handling needed
# Error handling done in Interface.switch_to_*() methods
try:
    new_panel = ImageGenerationInterface()
    self._set_stack_page(new_panel, 2)
except Exception as e:
    logger.error("Panel creation failed: %s", e)
    QMessageBox.critical(self, "Error", f"Failed to load panel: {e}")
```

---

## 12. TESTING STRATEGIES

### Unit Tests per Panel
```python
# test_stats_panel.py
def test_stats_timer_starts():
    panel = StatsPanel("testuser")
    assert panel.stats_timer.isActive()
    assert panel.stats_timer.interval() == 1000

def test_stats_update_without_crash():
    panel = StatsPanel("testuser")
    panel._update_stats()  # Should not raise

# test_chat_panel.py
def test_message_validation():
    panel = UserChatPanel()
    panel.chat_input.setText("")
    # Should not emit signal
    with pytest.raises(ValueError):
        panel._send_message()

def test_signal_emission():
    panel = UserChatPanel()
    received = []
    panel.message_sent.connect(received.append)
    panel.chat_input.setText("Test message")
    panel._send_message()
    assert received == ["Test message"]

# test_actions_panel.py
def test_navigation_signals():
    panel = ProactiveActionsPanel()
    signals_fired = []
    panel.image_gen_requested.connect(lambda: signals_fired.append("image_gen"))
    # Simulate button click
    panel.findChild(QPushButton, name="image_gen_btn").click()
    assert "image_gen" in signals_fired
```

---

## SUMMARY

**Panel System Design Principles:**
1. **Isolation**: Panels are self-contained, no cross-panel dependencies
2. **Communication**: All inter-panel communication via parent Dashboard/Interface
3. **Signals**: Emit signals upward, receive method calls downward
4. **Styling**: Shared constants for consistent Tron aesthetic
5. **Performance**: Efficient timers (1Hz for stats, 20Hz for animations)

**Key Relationships:**
- **StatsPanel** [[src/app/gui/leather_book_dashboard.py]]: Displays system status, future integration with core systems
- **ProactiveActionsPanel** [[src/app/gui/leather_book_dashboard.py]]: Navigation hub, 5 feature panel gateways
- **UserChatPanel** [[src/app/gui/leather_book_dashboard.py]]: Input validation → signal emission → dashboard routing
- **AIResponsePanel** [[src/app/gui/leather_book_dashboard.py]]: Conversation display, HTML-formatted history
- **AINeuralHead** [[src/app/gui/leather_book_dashboard.py]]: Visual feedback, state-driven animation

**Total Components:** 5 panels + 1 central head = 6 visual elements
**Total Signals:** 6 unique signals (1 from UserChatPanel, 5 from ProactiveActionsPanel)
**Total Timers:** 2 (stats 1Hz, animations 20Hz)


---


---

## 📚 Related Documentation

### Cross-References

- [[source-docs/gui/leather_book_dashboard.md|Leather Book Dashboard]]
- [[relationships/gui/01_DASHBOARD_RELATIONSHIPS.md|01 Dashboard Relationships]]

## 🔗 Source Code References

This documentation references the following GUI source files:

- [[src/app/gui/leather_book_dashboard.py]] - Implementation file


---

## RELATED SYSTEMS

### Core AI Integration

| Panel | Core AI System | Integration | Reference |
|-------|----------------|-------------|-----------|
| **StatsPanel** | [[../core-ai/02-AIPersona-Relationship-Map\|AIPersona]] | Displays interaction count | Section 2 (StatsPanel structure) |
| **StatsPanel** | [[../core-ai/03-MemoryExpansionSystem-Relationship-Map\|Memory]] | Shows memory usage % | Section 2 (data dependencies) |
| **UserChatPanel** | [[../core-ai/03-MemoryExpansionSystem-Relationship-Map\|Memory]] | Logs conversations | Section 4 (UserChatPanel) |
| **AIResponsePanel** | [[../core-ai/02-AIPersona-Relationship-Map\|AIPersona]] | Displays AI personality-driven responses | Section 5 (AIResponsePanel) |
| **ProactiveActionsPanel** | [[../core-ai/04-LearningRequestManager-Relationship-Map\|Learning]] | Triggers learning workflows | Section 3 (navigation) |

### Agent System Integration

| Panel | Agent System | Purpose | Reference |
|-------|--------------|---------|-----------|
| **UserChatPanel** | [[../agents/VALIDATION_CHAINS#layer-1-validatoragent-data-validation\|ValidatorAgent]] | Input sanitization (XSS protection) | Section 4 (validation flow) |
| **All Panels** | [[../agents/AGENT_ORCHESTRATION#centralized-kernel-architecture\|CognitionKernel]] | Routed via Desktop Adapter | Via parent Dashboard |
| **UserChatPanel** | [[../agents/VALIDATION_CHAINS#layer-3-cognitionkernel-four-laws-validation\|Four Laws]] | Message content validation | Via governance pipeline |

### Validation Flow

```
User Input (UserChatPanel) → 
sanitize_input() → 
validate_length() → 
[[../agents/VALIDATION_CHAINS#layer-1-validatoragent-data-validation|ValidatorAgent]] → 
[[../agents/VALIDATION_CHAINS#layer-3-cognitionkernel-four-laws-validation|Four Laws Check]] → 
[[../core-ai/03-MemoryExpansionSystem-Relationship-Map|Memory.log_conversation()]] → 
Intelligence Processing
```

---

**Enhanced by:** AGENT-078: GUI & Agent Cross-Links Specialist  
**Status:** ✅ Cross-linked with Core AI and Agent systems