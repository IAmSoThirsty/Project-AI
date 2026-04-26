# Dashboard Relationships Map

## Component: LeatherBookDashboard [[src/app/gui/leather_book_dashboard.py]]
**File:** `src/app/gui/leather_book_dashboard.py`  
**Lines:** 608  
**Role:** Main post-login interface with 6-zone layout

---

## 1. COMPONENT HIERARCHY

```
LeatherBookDashboard (QWidget)
├── StatsPanel (QFrame)
│   ├── username_label
│   ├── time_label
│   ├── location_label
│   ├── interaction_label
│   ├── memory_label
│   └── stats_timer (QTimer)
│
├── ProactiveActionsPanel (QFrame)
│   ├── image_gen_btn (QPushButton)
│   ├── news_btn (QPushButton)
│   ├── library_btn (QPushButton)
│   ├── tower_btn (QPushButton)
│   ├── command_btn (QPushButton)
│   └── proactive_label (QLabel)
│
├── AINeuralHead (QWidget)
│   ├── eyes (list of circles)
│   ├── circuit_lines (list of animated lines)
│   └── thinking_state (bool)
│
├── UserChatPanel (QFrame)
│   ├── chat_input (QTextEdit)
│   └── send_btn (QPushButton)
│
└── AIResponsePanel (QFrame)
    ├── response_text (QTextEdit)
    └── clear_btn (QPushButton)
```

---

## 2. SIGNAL CHAINS

### 2.1 User Message Flow
```
User types → UserChatPanel.chat_input (QTextEdit)
          ↓
User clicks send_btn OR presses Enter
          ↓
UserChatPanel._send_message() validates input
          ↓
UserChatPanel.message_sent.emit(message: str)
          ↓
LeatherBookDashboard._on_user_message(message: str)
          ↓
Dashboard performs 3 actions:
  1. emit send_message signal (propagates to parent)
  2. ai_head.start_thinking() (visual feedback)
  3. ai_response.add_user_message(message) (display)
          ↓
LeatherBookInterface (parent) receives send_message
          ↓
Intelligence system processes message
          ↓
Response returns via add_ai_response(response: str)
          ↓
ai_response.add_ai_response(response)
ai_head.stop_thinking()
```

**Signal Definition:**
```python
# UserChatPanel (line 359)
message_sent = pyqtSignal(str)

# LeatherBookDashboard (line 78)
send_message = pyqtSignal(str)
```

**Connection:**
```python
# Line 117 in _build_middle_section()
self.chat_input.message_sent.connect(self._on_user_message)
```

---

### 2.2 Navigation Signal Chain

```
User clicks action button in ProactiveActionsPanel
          ↓
Button emits corresponding signal:
  - image_gen_requested
  - news_intelligence_requested
  - intelligence_library_requested
  - watch_tower_requested
  - command_center_requested
          ↓
LeatherBookInterface receives signal
          ↓
Interface calls switch method:
  - switch_to_image_generation()
  - switch_to_news_intelligence()
  - switch_to_intelligence_library()
  - switch_to_watch_tower()
  - switch_to_command_center()
          ↓
Creates panel instance + connects back_requested signal
          ↓
Adds to QStackedWidget page 2
          ↓
User clicks back → back_requested.emit()
          ↓
Interface.switch_to_dashboard() → setCurrentIndex(1)
```

**Signal Definitions:**
```python
# ProactiveActionsPanel (lines 267-271)
image_gen_requested = pyqtSignal()
intelligence_library_requested = pyqtSignal()
watch_tower_requested = pyqtSignal()
command_center_requested = pyqtSignal()
news_intelligence_requested = pyqtSignal()
```

**Connections:**
```python
# ProactiveActionsPanel button connections (lines 287-310)
image_gen_btn.clicked.connect(self.image_gen_requested.emit)
news_btn.clicked.connect(self.news_intelligence_requested.emit)
library_btn.clicked.connect(self.intelligence_library_requested.emit)
tower_btn.clicked.connect(self.watch_tower_requested.emit)
command_btn.clicked.connect(self.command_center_requested.emit)

# LeatherBookInterface connections (lines 163-178)
dashboard.actions_panel.image_gen_requested.connect(
    self.switch_to_image_generation
)
dashboard.actions_panel.news_intelligence_requested.connect(
    self.switch_to_news_intelligence
)
# ... (similar pattern for all navigation signals)
```

---

## 3. EVENT FLOWS

### 3.1 Dashboard Initialization Flow
```
1. LeatherBookInterface.switch_to_main_dashboard(username)
   ↓
2. Create LeatherBookDashboard(username)
   ↓
3. _build_main_layout() → QVBoxLayout created
   ↓
4. _build_top_section()
   ├── StatsPanel(username) → stores username, starts stats_timer
   └── ProactiveActionsPanel() → creates action buttons
   ↓
5. _build_middle_section()
   ├── UserChatPanel() → creates input + send button
   ├── AINeuralHead() → initializes eyes + circuit graphics
   └── AIResponsePanel() → creates scrollable response area
   ↓
6. _setup_animation_timer()
   ├── QTimer created (50ms interval)
   └── timeout.connect(_update_animations)
   ↓
7. Connect all signals (line 163-178 in interface)
   ↓
8. Dashboard displayed on page 1 of QStackedWidget
```

---

### 3.2 Stats Update Flow
```
StatsPanel initialization
          ↓
_configure_stats_timer() creates QTimer (1000ms)
          ↓
stats_timer.timeout → _update_stats()
          ↓
Fetches current data:
  - username (from self.username)
  - current_time (QDateTime.currentDateTime())
  - location (placeholder "Earth")
  - interactions (placeholder count)
  - memory (placeholder percentage)
          ↓
Updates QLabel text with styled HTML
          ↓
Repeats every 1 second
```

**Timer Setup:**
```python
# Line 256 in StatsPanel._configure_stats_timer()
self.stats_timer = QTimer()
self.stats_timer.timeout.connect(self._update_stats)
self.stats_timer.start(1000)
```

---

### 3.3 Animation Update Flow
```
animation_timer fires every 50ms
          ↓
_update_animations() called
          ↓
Calls two update methods:
  1. ai_head.update() → animates eyes, circuits
  2. stats_panel.update() → can trigger redraws
          ↓
AINeuralHead.update() logic:
  - If thinking_state == True:
      * animate circuit lines
      * pulse eyes
  - Always:
      * update eye positions
      * redraw with updated geometry
          ↓
paintEvent() triggered automatically
          ↓
Visual updates rendered to screen
```

---

## 4. USER INTERACTION FLOWS

### 4.1 Send Message Interaction
```
USER ACTION: Types in chat_input, clicks send OR presses Enter

VALIDATION:
├── sanitize_input(text, max_length=2000)
├── validate_length(text, min_len=1, max_len=2000)
└── If invalid → warning dialog

SUCCESS PATH:
1. UserChatPanel._send_message()
2. message_sent.emit(sanitized_message)
3. LeatherBookDashboard._on_user_message(message)
4. Dashboard actions:
   - emit send_message (to parent Interface)
   - ai_head.start_thinking() (visual cue)
   - ai_response.add_user_message(message)
5. chat_input.clear()

AI RESPONSE PATH:
1. Intelligence system processes (external)
2. Interface calls dashboard.add_ai_response(response)
3. ai_response.add_ai_response(response)
4. ai_head.stop_thinking()

VISUAL FEEDBACK:
- Chat input cleared
- User message appears in response panel (blue)
- AI head eyes animate (thinking state)
- AI response appears in response panel (green)
```

---

### 4.2 Navigation Button Interaction
```
USER ACTION: Clicks "🎨 GENERATE IMAGES" button

IMMEDIATE FEEDBACK:
- Button hover effect (border cyan, text cyan)

SIGNAL EMISSION:
1. image_gen_btn.clicked
2. image_gen_requested.emit()

INTERFACE HANDLING:
1. LeatherBookInterface.switch_to_image_generation()
2. Import ImageGenerationInterface
3. Create instance: image_gen = ImageGenerationInterface()
4. _set_stack_page(image_gen, 2)
   - Adds to page_container if new
   - Sets current index to 2
   - Updates self.current_page = 2

RESULT:
- Dashboard (page 1) hidden
- Image Generation UI (page 2) shown
- Back button on new panel connects to switch_to_dashboard()
```

---

### 4.3 Proactive AI Notification Flow
```
TIMER-DRIVEN:
ProactiveActionsPanel displays rotating messages
          ↓
proactive_label updates every animation cycle
          ↓
Messages from PROACTIVE_ACTIONS tuple:
  - "Analyzing user patterns"
  - "Optimizing memory cache"
  - "Updating knowledge base"
  - "Processing data streams"
  - "Monitoring global intelligence"
  - "Watch Tower security scan"
  - "News intelligence updates"
          ↓
Text color: TRON_CYAN (#00ffff)
Text glow: 0px 0px 10px #00ffff

USER INTERACTION:
- Read-only display
- No direct interaction
- Provides ambient awareness of AI activity
```

---

## 5. DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                    LeatherBookInterface                      │
│                     (Main Container)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├── username (str)
                         ├── backend_token (str | None)
                         ├── user_logged_in signal
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   LeatherBookDashboard                       │
│                      (Page 1 Widget)                         │
└─┬──────────────┬──────────────┬────────────────┬───────────┘
  │              │              │                │
  ▼              ▼              ▼                ▼
┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐
│ Stats  │ │ Actions  │ │ AI Head  │ │ Chat/Response    │
│ Panel  │ │ Panel    │ │          │ │ Panels           │
└────────┘ └──────────┘ └──────────┘ └──────────────────┘
    │          │              │               │
    │          │              │               │
    ▼          ▼              ▼               ▼
┌────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                            │
├────────────────────────────────────────────────────────────┤
│ • username (passed from parent)                            │
│ • QDateTime.currentDateTime() (time)                       │
│ • Location placeholder (future: location_tracker.py)       │
│ • Interaction count (future: memory_expansion_system)      │
│ • Memory usage (future: ai_systems.py)                     │
│ • AI thinking state (boolean flag)                         │
│ • User messages (sanitized input strings)                  │
│ • AI responses (processed by intelligence_engine)          │
└────────────────────────────────────────────────────────────┘
```

---

## 6. DEPENDENCIES

### Parent Dependencies
```
LeatherBookDashboard → LeatherBookInterface
  - Created by Interface.switch_to_main_dashboard()
  - Receives username from Interface
  - Signals propagate to Interface for routing
```

### Sibling Dependencies (Navigation Targets)
```
ProactiveActionsPanel signals → LeatherBookInterface → creates:
  - ImageGenerationInterface
  - NewsIntelligencePanel
  - IntelligenceLibraryPanel
  - WatchTowerPanel
  - GodTierCommandPanel

All sibling panels:
  - back_requested signal → Interface.switch_to_dashboard()
  - Displayed on page 2 of QStackedWidget
  - Replaced when new panel requested
```

### Core System Dependencies
```
UserChatPanel → app.security.data_validation
  - sanitize_input()
  - validate_length()

Dashboard (future integration):
  - app.core.location_tracker (for location data)
  - app.core.ai_systems.MemoryExpansionSystem (for interaction count)
  - app.core.intelligence_engine (for AI responses)
```

---

## 7. STATE MANAGEMENT

### Dashboard State
```python
# LeatherBookDashboard instance variables
self.username: str  # Immutable after creation
self._main_layout: QVBoxLayout  # Container layout
self.stats_panel: StatsPanel
self.actions_panel: ProactiveActionsPanel
self.chat_input: UserChatPanel
self.ai_head: AINeuralHead
self.ai_response: AIResponsePanel
self.animation_timer: QTimer  # 50ms, drives all animations
```

### Panel States
```python
# StatsPanel state
self.username: str
self.stats_timer: QTimer  # 1000ms, updates stats labels

# AINeuralHead state
self.thinking_state: bool  # True = animating, False = idle
self.eyes: list  # Circle positions and colors
self.circuit_lines: list  # Animated line geometries

# UserChatPanel state
self.chat_input: QTextEdit  # User's current typed message

# AIResponsePanel state
self.response_text: QTextEdit  # Full conversation history
```

---

## 8. STYLING SYSTEM

### Color Constants
```python
TRON_GREEN = "#00ff00"  # Primary UI color
TRON_CYAN = "#00ffff"   # Accent/highlight color
TRON_BLACK = "#0a0a0a"  # Background
TRON_DARK = "#1a1a1a"   # Panel backgrounds
```

### Shared Stylesheets
```python
PANEL_STYLESHEET = """
    QFrame {
        background-color: #0f0f0f;
        border: 2px solid #00ff00;
        border-radius: 5px;
    }
"""

TITLE_FONT = QFont("Courier New", 12, QFont.Weight.Bold)
STYLE_CYAN_GLOW = "color: #00ffff; text-shadow: 0px 0px 10px #00ffff;"
STYLE_GREEN_TEXT = "color: #00ff00;"

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

**Applied To:**
- StatsPanel → PANEL_STYLESHEET
- ProactiveActionsPanel → PANEL_STYLESHEET
- UserChatPanel → PANEL_STYLESHEET
- AIResponsePanel → PANEL_STYLESHEET
- All action buttons → ACTION_BUTTON_STYLESHEET

---

## 9. PERFORMANCE CONSIDERATIONS

### Timer Strategy
```
animation_timer: 50ms (20 FPS)
  - Drives visual updates only
  - No heavy computation
  - Calls update() methods for repaints

stats_timer: 1000ms (1 Hz)
  - Updates stat labels
  - Minimal text formatting
  - No external API calls (currently placeholders)
```

### Signal Efficiency
- Signals use direct connections (same thread)
- No queued connections needed
- Message validation before emission prevents unnecessary processing

### Memory Management
- Panels created once, reused for session
- Navigation panels created on-demand
- Old panels removed from stack when replaced (garbage collected)

---

## 10. TESTING SURFACE

### Unit Test Targets
1. **Signal Emission:**
   - UserChatPanel.message_sent emits on valid input
   - ProactiveActionsPanel emits correct navigation signals

2. **Input Validation:**
   - UserChatPanel rejects empty messages
   - UserChatPanel sanitizes input (XSS protection)
   - UserChatPanel enforces 2000 char limit

3. **State Transitions:**
   - AINeuralHead.start_thinking() → thinking_state = True
   - AINeuralHead.stop_thinking() → thinking_state = False

### Integration Test Targets
1. **End-to-End Message Flow:**
   - Type message → send → signal received by dashboard
   - Dashboard propagates to interface
   - Response displayed in correct panel

2. **Navigation Flow:**
   - Click action button → correct panel shown
   - Back button → dashboard restored

3. **Timer Behavior:**
   - Stats update every 1 second
   - Animations run at 20 FPS
   - No timer conflicts or deadlocks

---

## 11. FUTURE INTEGRATION POINTS

### Planned Connections
```python
# StatsPanel will connect to:
from app.core.location_tracker import LocationTracker
from app.core.ai_systems import MemoryExpansionSystem

# Update _update_stats() to use real data:
self.location_label.setText(
    f"📍 Location: {location_tracker.get_current_location()}"
)
self.interaction_label.setText(
    f"💬 Interactions: {memory_system.get_interaction_count()}"
)
```

### Signal Extensions
```python
# Future signals for Dashboard:
persona_changed = pyqtSignal(dict)  # AI personality updates
learning_requested = pyqtSignal(str)  # Learning path generation
data_analysis_requested = pyqtSignal(str)  # Data file analysis
```

---

## 12. CRITICAL PATHS

### High-Priority Flows (Must Always Work)
1. **User Message Sending** (Core functionality)
2. **Navigation to Feature Panels** (Primary use case)
3. **Dashboard Display** (Entry point after login)

### Error Handling Requirements
```python
# UserChatPanel validation
try:
    sanitized = sanitize_input(text, max_length=2000)
    if not validate_length(sanitized, min_len=1, max_len=2000):
        QMessageBox.warning(self, "Input Error", "Message too long/short")
        return
except Exception as e:
    logger.error("Message validation failed: %s", e)
    QMessageBox.critical(self, "Error", f"Validation error: {e}")
```

**Logging Points:**
- Line 166: User message received
- Line 179-182: Animation update cycle
- Any validation failures

---

## SUMMARY

**LeatherBookDashboard** [[src/app/gui/leather_book_dashboard.py]] is the central hub of Project-AI's UI, orchestrating 6 specialized panels through a clean signal architecture. It serves as:
- **Message Router**: User input → Intelligence system
- **Navigation Hub**: 5 feature panels accessible via action buttons
- **Visual Feedback System**: Animated AI head, live stats, conversation display
- **State Container**: Maintains session data, timers, panel references

**Key Relationship Patterns:**
1. **Upward Signals**: Panels → Dashboard → Interface (for global actions)
2. **Downward Method Calls**: Interface → Dashboard → Panels (for state updates)
3. **Peer Relationships**: Dashboard ↔ Sibling Panels via Interface routing

**Total Signal Count:** 9 unique signals across 5 panel types
**Total Connections:** 15+ signal/slot connections
**Performance:** 20 FPS animations + 1 Hz stats updates


---


---

## 📚 Related Documentation

### Cross-References

- [[source-docs/gui/leather_book_dashboard.md|Leather Book Dashboard]]
- [[source-docs/gui/leather_book_interface.md|Leather Book Interface]]
- [[relationships/gui/02_PANEL_RELATIONSHIPS.md|02 Panel Relationships]]

## 🔗 Source Code References

This documentation references the following GUI source files:

- [[src/app/gui/leather_book_dashboard.py]] - Implementation file
- [[src/app/gui/leather_book_interface.py]] - Implementation file


---

## 11. RELATED SYSTEMS

### Core AI Integration ([[../core-ai/00-INDEX|Core AI Index]])

| System | Integration Point | Data Flow | Reference |
|--------|-------------------|-----------|-----------|
| [[../core-ai/02-AIPersona-Relationship-Map\|AIPersona]] | User interactions count | Dashboard stats → AIPersona.interaction_count | Planned integration |
| [[../core-ai/03-MemoryExpansionSystem-Relationship-Map\|Memory]] | Conversation history | UserChat → Memory.log_conversation() → AIResponse display | Section 2.1 signal chain |
| [[../core-ai/01-FourLaws-Relationship-Map\|FourLaws]] | Action validation | Dashboard actions → validate_action() before execution | Via governance pipeline |
| [[../core-ai/04-LearningRequestManager-Relationship-Map\|Learning]] | Learning path requests | ProactiveActions button → LearningPathGenerator | Via DashboardHandlers |

### Agent System Integration ([[../agents/README|Agents Overview]])

| System | Integration Point | Purpose | Reference |
|--------|-------------------|---------|-----------|
| [[../agents/AGENT_ORCHESTRATION#centralized-kernel-architecture\|CognitionKernel]] | Desktop Adapter | Routes all dashboard handler calls | Section 3 (Handlers) |
| [[../agents/VALIDATION_CHAINS#layer-1-validatoragent-data-validation\|ValidatorAgent]] | Input sanitization | UserChatPanel.chat_input validation | Section 2.1 (message flow) |
| [[../agents/VALIDATION_CHAINS#layer-3-cognitionkernel-four-laws-validation\|Four Laws Layer]] | Message safety | Validates user messages don't violate ethics | Via kernel routing |
| [[../agents/PLANNING_HIERARCHIES\|PlannerAgent]] | Task decomposition | Complex multi-step workflows (future) | Planned feature |

### Signal Routing Pattern

```
Dashboard Signal → Interface Handler → Desktop Adapter → 
[[../agents/AGENT_ORCHESTRATION#governance-integration|Router]] → 
[[../agents/VALIDATION_CHAINS|Validation Chain]] → 
[[../core-ai/02-AIPersona-Relationship-Map|AIPersona]]/[[../core-ai/03-MemoryExpansionSystem-Relationship-Map|Memory]]/etc. → 
Response → Dashboard Update
```

### Governance Pipeline

All dashboard actions follow this pattern:
1. **GUI Event** (button click, message send)
2. **Validation** ([[../agents/VALIDATION_CHAINS#layer-1-validatoragent-data-validation|ValidatorAgent]] sanitizes input)
3. **Ethics Check** ([[../agents/VALIDATION_CHAINS#layer-3-cognitionkernel-four-laws-validation|Four Laws validation]])
4. **Execution** (Core system processes request)
5. **Response** (Update UI with result)

See [[03_HANDLER_RELATIONSHIPS#governance-routing-pattern|Handler Governance Routing]] for implementation details.

---

**Generated by:** AGENT-056: GUI Relationship Mapping Specialist  
**Enhanced by:** AGENT-078: GUI & Agent Cross-Links Specialist  
**Status:** ✅ Cross-linked with Core AI and Agent systems