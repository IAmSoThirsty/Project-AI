# GUI Components Architecture

```mermaid
graph TB
    subgraph "Main Window (LeatherBookInterface)"
        MAIN[QMainWindow<br/>Main Entry Point]
        
        subgraph "Page Management"
            STACK[QStackedWidget<br/>Page Switcher]
            PAGE0[Page 0<br/>Login (Tron UI)]
            PAGE1[Page 1<br/>Dashboard (6 Zones)]
            PAGE2[Page 2<br/>Extended Panels]
        end
        
        SIGNALS[PyQt6 Signals<br/>Event Bus]
    end

    subgraph "Login Page (Tron-Themed)"
        LOGIN_PANEL[Login Panel<br/>QWidget]
        USERNAME[Username Field<br/>QLineEdit]
        PASSWORD[Password Field<br/>QLineEdit]
        LOGIN_BTN[Login Button<br/>QPushButton]
        CREATE_USER[Create User<br/>QPushButton]
        STYLE_TRON[Tron Styling<br/>Green/Cyan Theme]
    end

    subgraph "Dashboard (6-Zone Layout)"
        DASHBOARD[LeatherBookDashboard<br/>QWidget]
        
        subgraph "Zone 1: Stats (Top Left)"
            STATS[Stats Panel<br/>QLabel Grid]
            AI_STATUS[AI Status<br/>Online/Offline]
            MOOD[Current Mood<br/>Dynamic]
            UPTIME[System Uptime<br/>Timer]
        end
        
        subgraph "Zone 2: Actions (Top Right)"
            ACTIONS[Proactive Actions<br/>QPushButton Grid]
            LEARN_BTN[Request Learning]
            DATA_BTN[Analyze Data]
            IMAGE_BTN[Generate Image]
            LOCATION_BTN[Track Location]
            EMERGENCY_BTN[Send Alert]
        end
        
        subgraph "Zone 3: AI Head (Center)"
            AI_HEAD[AI Visualization<br/>QLabel/QGraphicsView]
            ANIMATION[Mood Animation<br/>Dynamic States]
        end
        
        subgraph "Zone 4: Chat Input (Bottom Left)"
            CHAT_INPUT[User Chat Panel<br/>QTextEdit]
            SEND_BTN[Send Button<br/>QPushButton]
            CLEAR_BTN[Clear Button]
        end
        
        subgraph "Zone 5: Response (Bottom Right)"
            RESPONSE[AI Response Panel<br/>QTextBrowser]
            HISTORY[Conversation History<br/>Scrollable]
        end
        
        subgraph "Zone 6: Menu Bar (Top)"
            MENU[Menu Bar<br/>QMenuBar]
            FILE_MENU[File Menu]
            SETTINGS_MENU[Settings Menu]
            PERSONA_MENU[Persona Config]
            HELP_MENU[Help Menu]
        end
    end

    subgraph "Persona Panel (4 Tabs)"
        PERSONA_PANEL[PersonaPanel<br/>QTabWidget]
        
        TAB1[Tab 1: Traits<br/>8 Sliders]
        CREATIVITY[Creativity Slider]
        FORMALITY[Formality Slider]
        HUMOR[Humor Slider]
        EMPATHY[Empathy Slider]
        CURIOSITY[Curiosity Slider]
        CAUTION[Caution Slider]
        VERBOSITY[Verbosity Slider]
        PROACTIVITY[Proactivity Slider]
        
        TAB2[Tab 2: Mood<br/>Current State]
        MOOD_DISPLAY[Mood Display<br/>QLabel]
        MOOD_HISTORY[Mood History<br/>QListWidget]
        
        TAB3[Tab 3: Memory<br/>Knowledge Base]
        MEMORY_VIEW[Memory Viewer<br/>QTreeWidget]
        CATEGORIES[6 Categories<br/>Technical/Creative/etc]
        
        TAB4[Tab 4: Settings<br/>Configuration]
        SAVE_BTN[Save Config]
        RESET_BTN[Reset to Default]
        IMPORT_BTN[Import Config]
        EXPORT_BTN[Export Config]
    end

    subgraph "Extended Panels (Page 2)"
        IMAGE_GEN[Image Generation<br/>Dual-Page Layout]
        IMG_LEFT[Left: Prompt Input<br/>Style Selector]
        IMG_RIGHT[Right: Display<br/>Zoom Controls]
        
        GOD_TIER[God Tier Panel<br/>Advanced Controls]
        HYDRA[Hydra 50 Panel<br/>Multi-Agent Orchestration]
        CERBERUS[Cerberus Panel<br/>Security Dashboard]
        WATCH_TOWER[Watch Tower Panel<br/>Global Monitoring]
    end

    subgraph "Utility Modules"
        HANDLERS[DashboardHandlers<br/>Event Logic]
        UTILS[DashboardUtils<br/>Error Handling]
        STYLES[QSS Stylesheets<br/>3 Themes]
        DARK_STYLE[styles_dark.qss]
        MODERN_STYLE[styles_modern.qss]
        CLASSIC_STYLE[styles.qss]
    end

    subgraph "Backend Integration"
        CORE_SYSTEMS[Core AI Systems<br/>ai_systems.py]
        USER_MGR[UserManager<br/>user_manager.py]
        INTEL_ENGINE[Intelligence Engine<br/>intelligence_engine.py]
        IMG_GENERATOR[Image Generator<br/>image_generator.py]
    end

    %% Main Window Structure
    MAIN --> STACK
    STACK --> PAGE0
    STACK --> PAGE1
    STACK --> PAGE2
    MAIN --> SIGNALS

    %% Login Page
    PAGE0 --> LOGIN_PANEL
    LOGIN_PANEL --> USERNAME
    LOGIN_PANEL --> PASSWORD
    LOGIN_PANEL --> LOGIN_BTN
    LOGIN_PANEL --> CREATE_USER
    LOGIN_PANEL --> STYLE_TRON

    %% Dashboard Layout
    PAGE1 --> DASHBOARD
    DASHBOARD --> STATS
    DASHBOARD --> ACTIONS
    DASHBOARD --> AI_HEAD
    DASHBOARD --> CHAT_INPUT
    DASHBOARD --> RESPONSE
    DASHBOARD --> MENU

    %% Stats Zone
    STATS --> AI_STATUS
    STATS --> MOOD
    STATS --> UPTIME

    %% Actions Zone
    ACTIONS --> LEARN_BTN
    ACTIONS --> DATA_BTN
    ACTIONS --> IMAGE_BTN
    ACTIONS --> LOCATION_BTN
    ACTIONS --> EMERGENCY_BTN

    %% AI Head
    AI_HEAD --> ANIMATION

    %% Chat Zone
    CHAT_INPUT --> SEND_BTN
    CHAT_INPUT --> CLEAR_BTN

    %% Response Zone
    RESPONSE --> HISTORY

    %% Menu Bar
    MENU --> FILE_MENU
    MENU --> SETTINGS_MENU
    MENU --> PERSONA_MENU
    MENU --> HELP_MENU

    %% Persona Panel
    PAGE2 --> PERSONA_PANEL
    PERSONA_PANEL --> TAB1
    TAB1 --> CREATIVITY
    TAB1 --> FORMALITY
    TAB1 --> HUMOR
    TAB1 --> EMPATHY
    TAB1 --> CURIOSITY
    TAB1 --> CAUTION
    TAB1 --> VERBOSITY
    TAB1 --> PROACTIVITY
    
    PERSONA_PANEL --> TAB2
    TAB2 --> MOOD_DISPLAY
    TAB2 --> MOOD_HISTORY
    
    PERSONA_PANEL --> TAB3
    TAB3 --> MEMORY_VIEW
    TAB3 --> CATEGORIES
    
    PERSONA_PANEL --> TAB4
    TAB4 --> SAVE_BTN
    TAB4 --> RESET_BTN
    TAB4 --> IMPORT_BTN
    TAB4 --> EXPORT_BTN

    %% Extended Panels
    PAGE2 --> IMAGE_GEN
    IMAGE_GEN --> IMG_LEFT
    IMAGE_GEN --> IMG_RIGHT
    
    PAGE2 --> GOD_TIER
    PAGE2 --> HYDRA
    PAGE2 --> CERBERUS
    PAGE2 --> WATCH_TOWER

    %% Signal Connections
    SIGNALS -.user_logged_in.-> DASHBOARD
    SIGNALS -.switch_to_dashboard.-> STACK
    SIGNALS -.image_gen_requested.-> IMAGE_GEN
    SEND_BTN -.send_message.-> INTEL_ENGINE
    LEARN_BTN -.learning_requested.-> CORE_SYSTEMS
    IMAGE_BTN -.image_gen_requested.-> IMG_GENERATOR

    %% Utility Integration
    DASHBOARD --> HANDLERS
    DASHBOARD --> UTILS
    MAIN --> STYLES
    STYLES --> DARK_STYLE
    STYLES --> MODERN_STYLE
    STYLES --> CLASSIC_STYLE

    %% Backend Integration
    LOGIN_BTN --> USER_MGR
    CHAT_INPUT --> INTEL_ENGINE
    ACTIONS --> CORE_SYSTEMS
    IMAGE_GEN --> IMG_GENERATOR
    PERSONA_PANEL --> CORE_SYSTEMS

    %% Styling
    classDef mainClass fill:#1e3a8a,stroke:#3b82f6,stroke-width:3px,color:#fff
    classDef pageClass fill:#7c2d12,stroke:#f97316,stroke-width:2px,color:#fff
    classDef zoneClass fill:#065f46,stroke:#10b981,stroke-width:2px,color:#fff
    classDef personaClass fill:#4c1d95,stroke:#a78bfa,stroke-width:2px,color:#fff
    classDef extendedClass fill:#581c87,stroke:#c084fc,stroke-width:2px,color:#fff
    classDef utilClass fill:#0c4a6e,stroke:#0ea5e9,stroke-width:2px,color:#fff
    classDef backendClass fill:#991b1b,stroke:#f87171,stroke-width:2px,color:#fff
    classDef tronClass fill:#00ff00,stroke:#00ffff,stroke-width:3px,color:#000

    class MAIN,STACK,SIGNALS mainClass
    class PAGE0,PAGE1,PAGE2 pageClass
    class STATS,ACTIONS,AI_HEAD,CHAT_INPUT,RESPONSE,MENU zoneClass
    class PERSONA_PANEL,TAB1,TAB2,TAB3,TAB4 personaClass
    class IMAGE_GEN,GOD_TIER,HYDRA,CERBERUS,WATCH_TOWER extendedClass
    class HANDLERS,UTILS,STYLES,DARK_STYLE,MODERN_STYLE,CLASSIC_STYLE utilClass
    class CORE_SYSTEMS,USER_MGR,INTEL_ENGINE,IMG_GENERATOR backendClass
    class LOGIN_PANEL,STYLE_TRON tronClass
```

## GUI Architecture

### Main Window Structure

**LeatherBookInterface (QMainWindow)**

Entry point: `src/app/gui/leather_book_interface.py` (659 lines)

```python
class LeatherBookInterface(QMainWindow):
    # Signals
    user_logged_in = pyqtSignal(str)
    switch_to_dashboard = pyqtSignal()
    image_gen_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project-AI - Leather Book Interface")
        self.setGeometry(100, 100, 1400, 900)
        
        # Page management
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        
        # Left page (Tron login)
        self.left_page = self.create_login_page()
        
        # Right page (Dashboard placeholder)
        self.right_page = QWidget()
        
        self.layout.addWidget(self.left_page)
        self.layout.addWidget(self.right_page)
```

**Page Switching Pattern**

```python
def switch_to_dashboard(self, username: str):
    """Replace left page with dashboard"""
    # Remove login page
    self.layout.removeWidget(self.left_page)
    self.left_page.deleteLater()
    
    # Create dashboard
    self.dashboard = LeatherBookDashboard(username, self)
    self.layout.insertWidget(0, self.dashboard)
    
    # Emit signal
    self.user_logged_in.emit(username)
```

### Login Page (Tron Theme)

**Styling: Green on Black**

```python
# Tron color scheme
TRON_GREEN = "#00ff00"
TRON_CYAN = "#00ffff"
TRON_BLACK = "#000000"

TRON_STYLE = f"""
    QWidget {{
        background-color: {TRON_BLACK};
        color: {TRON_GREEN};
        font-family: 'Courier New', monospace;
    }}
    QPushButton {{
        background-color: {TRON_BLACK};
        border: 2px solid {TRON_CYAN};
        color: {TRON_CYAN};
        padding: 10px;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background-color: {TRON_CYAN};
        color: {TRON_BLACK};
    }}
    QLineEdit {{
        background-color: {TRON_BLACK};
        border: 1px solid {TRON_GREEN};
        color: {TRON_GREEN};
        padding: 8px;
    }}
"""
```

### Dashboard (6-Zone Layout)

**LeatherBookDashboard (QWidget)**

Source: `src/app/gui/leather_book_dashboard.py` (608 lines)

```python
class LeatherBookDashboard(QWidget):
    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        
        # Core systems integration
        self.persona = AIPersona()
        self.memory = MemoryExpansionSystem()
        self.four_laws = FourLaws()
        self.user_manager = UserManager()
        
        # Layout
        main_layout = QVBoxLayout(self)
        
        # Zone 6: Menu Bar (top)
        menu_bar = self.create_menu_bar()
        main_layout.addWidget(menu_bar)
        
        # Top row: Zones 1 & 2
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.create_stats_panel())  # Zone 1
        top_layout.addWidget(self.create_actions_panel())  # Zone 2
        main_layout.addLayout(top_layout)
        
        # Middle row: Zone 3 (AI Head)
        main_layout.addWidget(self.create_ai_head_panel())
        
        # Bottom row: Zones 4 & 5
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.create_chat_panel())  # Zone 4
        bottom_layout.addWidget(self.create_response_panel())  # Zone 5
        main_layout.addLayout(bottom_layout)
```

**Zone 1: Stats Panel (Top Left)**

```python
def create_stats_panel(self) -> QWidget:
    panel = QWidget()
    layout = QVBoxLayout(panel)
    
    # AI Status
    self.status_label = QLabel("🟢 AI Online")
    layout.addWidget(self.status_label)
    
    # Current Mood
    mood = self.persona.get_current_mood()
    self.mood_label = QLabel(f"Mood: {mood}")
    layout.addWidget(self.mood_label)
    
    # Uptime
    self.uptime_label = QLabel("Uptime: 0:00:00")
    layout.addWidget(self.uptime_label)
    
    # Update timer
    self.uptime_timer = QTimer()
    self.uptime_timer.timeout.connect(self.update_uptime)
    self.uptime_timer.start(1000)  # Update every second
    
    return panel
```

**Zone 2: Proactive Actions (Top Right)**

```python
def create_actions_panel(self) -> QWidget:
    panel = QWidget()
    layout = QGridLayout(panel)
    
    # 5 action buttons
    learn_btn = QPushButton("📚 REQUEST LEARNING")
    learn_btn.clicked.connect(self.request_learning)
    layout.addWidget(learn_btn, 0, 0)
    
    data_btn = QPushButton("📊 ANALYZE DATA")
    data_btn.clicked.connect(self.analyze_data)
    layout.addWidget(data_btn, 0, 1)
    
    image_btn = QPushButton("🎨 GENERATE IMAGE")
    image_btn.clicked.connect(self.generate_image)
    layout.addWidget(image_btn, 1, 0)
    
    location_btn = QPushButton("📍 TRACK LOCATION")
    location_btn.clicked.connect(self.track_location)
    layout.addWidget(location_btn, 1, 1)
    
    emergency_btn = QPushButton("🚨 SEND ALERT")
    emergency_btn.clicked.connect(self.send_emergency_alert)
    layout.addWidget(emergency_btn, 2, 0, 1, 2)
    
    return panel
```

**Zone 3: AI Head Visualization**

```python
def create_ai_head_panel(self) -> QWidget:
    panel = QWidget()
    layout = QVBoxLayout(panel)
    
    # AI head image
    self.ai_head = QLabel()
    pixmap = QPixmap("assets/ai_head_neutral.png")
    self.ai_head.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
    self.ai_head.setAlignment(Qt.AlignCenter)
    layout.addWidget(self.ai_head)
    
    # Mood-based animation
    self.animation_timer = QTimer()
    self.animation_timer.timeout.connect(self.animate_ai_head)
    self.animation_timer.start(100)  # 10 FPS
    
    return panel
```

**Zone 4: User Chat Input (Bottom Left)**

```python
def create_chat_panel(self) -> QWidget:
    panel = QWidget()
    layout = QVBoxLayout(panel)
    
    # Chat history (read-only)
    self.chat_history = QTextBrowser()
    layout.addWidget(self.chat_history)
    
    # Input area
    input_layout = QHBoxLayout()
    self.chat_input = QTextEdit()
    self.chat_input.setMaximumHeight(100)
    input_layout.addWidget(self.chat_input)
    
    # Send button
    send_btn = QPushButton("SEND")
    send_btn.clicked.connect(self.send_message)
    input_layout.addWidget(send_btn)
    
    # Clear button
    clear_btn = QPushButton("CLEAR")
    clear_btn.clicked.connect(self.chat_input.clear)
    input_layout.addWidget(clear_btn)
    
    layout.addLayout(input_layout)
    return panel
```

**Zone 5: AI Response Panel (Bottom Right)**

```python
def create_response_panel(self) -> QWidget:
    panel = QWidget()
    layout = QVBoxLayout(panel)
    
    # Response display
    self.response_browser = QTextBrowser()
    self.response_browser.setOpenExternalLinks(True)
    layout.addWidget(self.response_browser)
    
    return panel
```

### Signal-Based Communication

**PyQt6 Signal Pattern**

```python
# In LeatherBookInterface
class LeatherBookInterface(QMainWindow):
    user_logged_in = pyqtSignal(str)
    image_gen_requested = pyqtSignal()

# In Dashboard
def send_message(self):
    message = self.chat_input.toPlainText()
    
    # Emit to parent
    self.parent().send_message.emit(message)
    
    # Or handle directly
    response = self.intelligence_engine.chat(message)
    self.display_response(response)
```

### Persona Panel (4 Tabs)

**PersonaPanel (QTabWidget)**

Source: `src/app/gui/persona_panel.py`

```python
class PersonaPanel(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.persona = AIPersona()
        
        # Tab 1: Traits (8 sliders)
        self.addTab(self.create_traits_tab(), "Personality Traits")
        
        # Tab 2: Mood display
        self.addTab(self.create_mood_tab(), "Current Mood")
        
        # Tab 3: Memory viewer
        self.addTab(self.create_memory_tab(), "Memory & Knowledge")
        
        # Tab 4: Settings
        self.addTab(self.create_settings_tab(), "Configuration")
```

**Tab 1: Personality Traits (8 Sliders)**

```python
def create_traits_tab(self) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    traits = [
        ("Creativity", "creativity"),
        ("Formality", "formality"),
        ("Humor", "humor"),
        ("Empathy", "empathy"),
        ("Curiosity", "curiosity"),
        ("Caution", "caution"),
        ("Verbosity", "verbosity"),
        ("Proactivity", "proactivity")
    ]
    
    self.trait_sliders = {}
    for display_name, trait_key in traits:
        slider_layout = QHBoxLayout()
        
        label = QLabel(f"{display_name}:")
        slider_layout.addWidget(label)
        
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(self.persona.traits[trait_key])
        slider.valueChanged.connect(lambda v, k=trait_key: self.update_trait(k, v))
        slider_layout.addWidget(slider)
        
        value_label = QLabel(f"{slider.value()}")
        slider.valueChanged.connect(lambda v, l=value_label: l.setText(str(v)))
        slider_layout.addWidget(value_label)
        
        layout.addLayout(slider_layout)
        self.trait_sliders[trait_key] = slider
    
    return widget
```

### Threading Pattern (CRITICAL)

**NEVER use `threading.Thread` in GUI code**

```python
# ❌ WRONG - Blocks UI
def send_message_blocking(self):
    response = openai.ChatCompletion.create(...)  # 5-10 second block
    self.display_response(response)

# ✅ CORRECT - QTimer for delays
def send_message_async(self):
    self.show_loading_spinner()
    QTimer.singleShot(100, self._send_message_worker)

def _send_message_worker(self):
    response = openai.ChatCompletion.create(...)
    self.display_response(response)
    self.hide_loading_spinner()

# ✅ CORRECT - QThread for long tasks
class ImageGenerationWorker(QThread):
    image_generated = pyqtSignal(str, dict)  # path, metadata
    
    def __init__(self, prompt: str, style: str):
        super().__init__()
        self.prompt = prompt
        self.style = style
    
    def run(self):
        generator = ImageGenerator()
        image_path, metadata = generator.generate(self.prompt, self.style)
        self.image_generated.emit(image_path, metadata)

# Usage
worker = ImageGenerationWorker(prompt, style)
worker.image_generated.connect(self.display_image)
worker.start()  # Non-blocking
```

### Stylesheet System

**Three Themes Available**

```python
# Load stylesheet
def load_stylesheet(theme: str) -> str:
    stylesheet_map = {
        "classic": "src/app/gui/styles.qss",
        "dark": "src/app/gui/styles_dark.qss",
        "modern": "src/app/gui/styles_modern.qss"
    }
    
    path = stylesheet_map.get(theme, stylesheet_map["classic"])
    with open(path) as f:
        return f.read()

# Apply to application
app = QApplication(sys.argv)
app.setStyleSheet(load_stylesheet("dark"))
```

### Error Handling Pattern

**DashboardUtils (Error Wrapper)**

Source: `src/app/gui/dashboard_utils.py`

```python
def safe_execute(func):
    """Decorator for safe GUI operations"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            show_error_dialog(f"Operation failed: {e}")
    return wrapper

# Usage
@safe_execute
def send_message(self):
    message = self.chat_input.toPlainText()
    response = self.intelligence_engine.chat(message)
    self.display_response(response)
```

## Integration Points

### Core Systems Integration

```python
# In LeatherBookDashboard.__init__()
self.persona = AIPersona(data_dir="data/ai_persona")
self.memory = MemoryExpansionSystem(data_dir="data/memory")
self.four_laws = FourLaws()
self.user_manager = UserManager(data_dir="data")
self.intelligence_engine = IntelligenceEngine()
```

### Image Generation Integration

```python
# Button click handler
def generate_image(self):
    # Switch to image generation page
    self.parent().switch_to_image_generation()

# In LeatherBookInterface
def switch_to_image_generation(self):
    # Add ImageGenerationLeftPanel to page 2
    if not hasattr(self, 'image_gen_panel'):
        from app.gui.image_generation import ImageGenerationLeftPanel, ImageGenerationRightPanel
        
        self.image_gen_left = ImageGenerationLeftPanel(self)
        self.image_gen_right = ImageGenerationRightPanel(self)
        
        # Insert into layout
        self.layout.addWidget(self.image_gen_left)
        self.layout.addWidget(self.image_gen_right)
```

## Best Practices

### 1. Always Use Signals for Cross-Component Communication

```python
# ✅ CORRECT
class ParentWidget(QWidget):
    data_updated = pyqtSignal(dict)

class ChildWidget(QWidget):
    def update_data(self, data: dict):
        self.parent().data_updated.emit(data)

# ❌ WRONG - Direct method call breaks encapsulation
def update_data(self, data: dict):
    self.parent().parent().dashboard.update_display(data)
```

### 2. Separate UI Logic from Business Logic

```python
# ✅ CORRECT - Business logic in core, UI calls it
def send_message(self):
    message = self.chat_input.toPlainText()
    response = self.intelligence_engine.chat(message)  # Core module
    self.display_response(response)

# ❌ WRONG - Business logic in GUI
def send_message(self):
    message = self.chat_input.toPlainText()
    # OpenAI API call directly in GUI module
    response = openai.ChatCompletion.create(...)
    self.display_response(response)
```

### 3. Use QTimer for Periodic Updates

```python
# Update stats every second
self.stats_timer = QTimer()
self.stats_timer.timeout.connect(self.update_stats)
self.stats_timer.start(1000)
```

### 4. Clean Up Resources

```python
def closeEvent(self, event):
    """Called when window is closing"""
    # Stop timers
    self.uptime_timer.stop()
    self.animation_timer.stop()
    
    # Save state
    self.persona._save_state()
    self.memory._save_state()
    
    event.accept()
```
