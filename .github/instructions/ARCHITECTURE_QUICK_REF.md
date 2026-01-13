# Project-AI Architecture Quick Reference

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    LEATHER BOOK UI (PyQt6)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │  Login Page  │──│  Dashboard   │──│  Persona Panel     │   │
│  │  (Tron UI)   │  │  (6 Zones)   │  │  (4 Tabs)          │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CORE SYSTEMS (10 Modules)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ai_systems.py (470 lines - 6 integrated systems)         │  │
│  │  • FourLaws          • AIPersona       • MemorySystem    │  │
│  │  • LearningRequests  • CommandOverride • PluginManager   │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Feature Modules                                          │  │
│  │  • user_manager      • learning_paths  • data_analysis   │  │
│  │  • security_resources • location_tracker • emergency     │  │
│  │  • intelligence_engine • intent_detection                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI AGENTS (4 Specialized)                    │
│  ┌───────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────┐ │
│  │ Oversight │  │ Planner  │  │ Validator │  │ Explainability│ │
│  └───────────┘  └──────────┘  └───────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DATA PERSISTENCE (JSON Files)                  │
│  data/                                                          │
│  ├── users.json                    # User profiles (bcrypt)     │
│  ├── ai_persona/                                                │
│  │   └── state.json                # Personality, mood          │
│  ├── memory/                                                    │
│  │   └── knowledge.json            # 6-category knowledge base  │
│  ├── learning_requests/                                         │
│  │   ├── requests.json             # Learning workflow          │
│  │   └── black_vault_secure/      # Denied content (SHA-256)   │
│  ├── command_override_config.json  # Override states            │
│  └── settings.json                 # App configuration          │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Patterns

### User Action → AI Response
```
User Input (GUI)
    ↓
Dashboard Handler
    ↓
FourLaws.validate_action()  ← Ethics check
    ↓
Core Module (e.g., learning_paths)
    ↓
OpenAI API / Local Processing
    ↓
AIPersona.update_conversation_state()  ← Track interaction
    ↓
MemorySystem.log_conversation()  ← Persist
    ↓
GUI Response Display
```

### Learning Request Workflow
```
AI discovers new content
    ↓
LearningRequestManager.create_request()
    ↓
Save to data/learning_requests/requests.json
    ↓
User reviews in PersonaPanel
    ↓
┌─────────────────┬──────────────────┐
│   APPROVE       │      DENY        │
└─────────────────┴──────────────────┘
         │                  │
         ▼                  ▼
MemorySystem.add_knowledge()  BlackVault
                              (SHA-256 fingerprint)
```

### State Persistence Pattern
```python
class AISystem:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)  # CRITICAL
        self._load_state()  # Load from JSON
    
    def mutating_operation(self):
        # ... modify state ...
        self._save_state()  # ALWAYS call after changes
```

## 🎯 Testing Strategy

### Isolated Test Pattern
```python
@pytest.fixture
def system_under_test(self):
    with tempfile.TemporaryDirectory() as tmpdir:
        yield AISystem(data_dir=tmpdir)  # Isolated state
        # Cleanup automatic via context manager
```

### Test Coverage Matrix
| System               | Init | State | Persist | Total |
|---------------------|------|-------|---------|-------|
| FourLaws            | ✓    | ✓     | N/A     | 2     |
| AIPersona           | ✓    | ✓     | ✓       | 3     |
| MemorySystem        | ✓    | ✓     | ✓       | 3     |
| LearningRequests    | ✓    | ✓     | ✓       | 4     |
| CommandOverride     | ✓    | ✓     | ✓       | 3     |
| **Total**           |      |       |         | **14**|

## 🔌 Integration Points

### OpenAI API
```python
# Environment setup
from dotenv import load_dotenv
load_dotenv()  # Loads OPENAI_API_KEY

# Used in:
# - learning_paths.py (path generation)
# - intelligence_engine.py (chat completion)
```

### PyQt6 Signal Pattern
```python
# Define signals in class
class Dashboard(QWidget):
    send_message = pyqtSignal(str)  # Custom signal
    
    def on_button_click(self):
        self.send_message.emit("Hello")  # Emit

# Connect in parent
dashboard = Dashboard()
dashboard.send_message.connect(self.handle_message)  # Connect
```

### Agent vs Plugin
- **Agents**: Specialized AI subsystems in `src/app/agents/` (oversight, planner, validator, explainability)
- **Plugins**: Simple enable/disable extensions via PluginManager (lines 340-395 in ai_systems.py)
- **Key Difference**: Agents are core functionality; Plugins are optional extensions

## 📝 Common Commands

```powershell
# Development
python -m src.app.main           # Launch desktop app
pytest -v                        # Run tests
ruff check .                     # Lint
ruff check . --fix              # Auto-fix

# Docker
docker-compose up                # Dev environment
docker build -t project-ai .     # Production build

# Web (separate context)
cd web/backend && flask run      # Backend API
cd web/frontend && npm run dev   # Frontend dev server
```

## ⚠️ Critical Patterns

### Module Imports
```python
# ✅ CORRECT (from project root)
python -m src.app.main

# ❌ WRONG (breaks imports)
python src/app/main.py
```

### State Persistence
```python
# ✅ CORRECT
def adjust_trait(self, trait, delta):
    self.personality[trait] += delta
    self._save_state()  # Don't forget!

# ❌ WRONG (data lost on restart)
def adjust_trait(self, trait, delta):
    self.personality[trait] += delta
    # Missing save - state not persisted
```

### Threading in PyQt6
```python
# ✅ CORRECT
QTimer.singleShot(1000, self.delayed_action)

# ❌ WRONG (thread safety issues)
threading.Thread(target=self.delayed_action).start()
```

## 🔐 Security Layers

```
┌──────────────────────────────────────────┐
│ FourLaws (Asimov's Laws hierarchy)       │ ← Ethics
├──────────────────────────────────────────┤
│ CommandOverride (master password)        │ ← Authentication
├──────────────────────────────────────────┤
│ Black Vault (SHA-256 fingerprinting)     │ ← Content filtering
├──────────────────────────────────────────┤
│ Bcrypt password hashing (users)          │ ← User security
├──────────────────────────────────────────┤
│ Fernet encryption (location, cloud)      │ ← Data encryption
└──────────────────────────────────────────┘
```

## 📚 Documentation Hierarchy

1. **Quick Start**: `DESKTOP_APP_QUICKSTART.md` - Installation & launch
2. **Architecture**: `PROGRAM_SUMMARY.md` - Complete system overview (600+ lines)
3. **Components**: `DEVELOPER_QUICK_REFERENCE.md` - GUI API reference
4. **Features**:
   - `AI_PERSONA_IMPLEMENTATION.md` - Personality system
   - `LEARNING_REQUEST_IMPLEMENTATION.md` - Learning workflow
   - `COMMAND_MEMORY_FEATURES.md` - Memory system specs
5. **This File**: Architecture patterns and data flows

---

**Last Updated**: November 29, 2025  
**Target Audience**: AI coding agents and new developers
