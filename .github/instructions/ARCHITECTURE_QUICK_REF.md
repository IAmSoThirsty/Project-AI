---
title: "Project-AI Architecture Quick Reference"
id: architecture-quick-ref
type: reference
version: 1.2.0
created_date: 2025-11-20
updated_date: 2026-04-20
status: active
author: "Architecture Team <projectaidevs@gmail.com>"
tags:
  - architecture
  - architecture/desktop
  - architecture/backend
  - architecture/data
  - development
  - development/python
  - reference
  - guide
  - quickstart
area:
  - architecture
  - development
component:
  - gui
  - constitutional-ai
  - persona-system
  - memory-system
  - learning-system
  - user-manager
  - command-override
  - intelligence-engine
  - agents
audience:
  - developer
  - architect
  - contributor
priority: p0
related_to:
  - "[[README]]"
  - "[[COPILOT_MANDATORY_GUIDE]]"
  - "[[DEVELOPER_QUICK_REFERENCE]]"
  - "[[PROGRAM_SUMMARY]]"
  - "[[AI_PERSONA_IMPLEMENTATION]]"
depends_on:
  - "[[README]]"
what: "Visual architecture diagram and reference guide showing system structure, core components (6 AI systems, GUI modules, agents), data flows, and persistence patterns for Project-AI desktop application"
who: "Developers and architects needing rapid orientation to codebase structure, module interactions, and data persistence patterns"
when: "After reading README - use when understanding component relationships, debugging integration issues, or planning new features"
where: ".github/instructions/ as canonical architectural reference - complements COPILOT_MANDATORY_GUIDE with visual representations"
why: "Provides instant architectural comprehension through ASCII diagrams, eliminates need to reverse-engineer structure from code, documents 6-system integration pattern in ai_systems.py"
---

# Project-AI Architecture Quick Reference

## 🏗️ System Overview

**Implementation:** See [[AGENT-080-CONCEPT-CODE-MAP|Complete Concept-to-Code Traceability Matrix]]

**Core Implementations:**
- [[src/app/core/cognition_kernel.py|CognitionKernel]] - Central processing hub (1200+ lines)
- [[src/app/core/super_kernel.py|SuperKernel]] - Two-tier orchestration
- [[src/app/core/ai_systems.py|AI Systems]] - 6 integrated systems (470+ lines)
- [[src/app/gui/leather_book_interface.py|LeatherBookInterface]] - Main GUI (659 lines)

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

**Learn More**:
- Complete architecture: [[PROGRAM_SUMMARY]]
- GUI implementation: [[INTEGRATION_GUIDE]]
- Core systems detail: [[PROGRAM_SUMMARY]] → Six Core AI Systems
- Agents deep-dive: [[SECURITY_AGENTS_GUIDE]]
- Data persistence patterns: [[PROGRAM_SUMMARY]] → Data Persistence

## 🔄 Data Flow Patterns

**Implementation Reference:**
- [[AGENT-080-CONCEPT-CODE-MAP#core-kernel-architecture|Kernel Architecture Implementation]]
- [[AGENT-080-CONCEPT-CODE-MAP#governance-systems|Governance Systems Implementation]]
- [[AGENT-080-CONCEPT-CODE-MAP#data-persistence|Data Persistence Implementation]]

### User Action → AI Response

**Implementation Files:**
- [[src/app/gui/dashboard_handlers.py|Dashboard Handlers]] - User input processing
- [[src/app/core/ai_systems.py|FourLaws]] - Lines 220-280: Ethics validation
- [[src/app/core/memory_engine.py|MemoryEngine]] - Conversation logging
- [[tests/test_cognition_kernel.py|Kernel Tests]] - 88% coverage

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

**Learn More**:
- FourLaws ethics: [[AI_PERSONA_IMPLEMENTATION]] → Four Laws Validation
- Dashboard handlers: [[INTEGRATION_GUIDE]] → Signal Callbacks
- OpenAI integration: [[PROGRAM_SUMMARY]] → OpenAI Integration
- Memory persistence: [[PROGRAM_SUMMARY]] → MemoryExpansionSystem

---

### Learning Request Workflow

**Implementation:** [[AGENT-080-CONCEPT-CODE-MAP#learningrequestmanager-human-in-the-loop-learning|Learning Request System in Traceability Matrix]]

**Core Files:**
- [[src/app/core/ai_systems.py|LearningRequestManager]] - Lines 530-625
- [[src/app/gui/persona_panel.py|PersonaPanel]] - Learning UI (4 tabs)
- [[docs/LEARNING_REQUEST_IMPLEMENTATION|Learning Request Documentation]]

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

**Learn More**:
- Complete workflow: [[LEARNING_REQUEST_IMPLEMENTATION]]
- Black Vault details: [[LEARNING_REQUEST_IMPLEMENTATION]] → Black Vault section
- Memory integration: [[PROGRAM_SUMMARY]] → LearningRequestManager
- Security implications: [[SECURITY_AGENTS_GUIDE]]

---

### State Persistence Pattern

**Implementation:** All 6 AI systems use this pattern - [[AGENT-080-CONCEPT-CODE-MAP#json-persistence-pattern|See Traceability Matrix]]

**Example Implementations:**
- [[src/app/core/ai_systems.py|AIPersona._save_state()]] - Lines 405-420
- [[src/app/core/user_manager.py|UserManager.save_users()]] - Bcrypt persistence
- [[tests/test_ai_systems.py|Persistence Tests]] - Isolated test pattern

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

**Learn More**:
- Data persistence patterns: [[PROGRAM_SUMMARY]] → Data Persistence Pattern
- Testing with isolated state: [[PROGRAM_SUMMARY]] → Testing Strategy
- Critical gotchas: [[COPILOT_MANDATORY_GUIDE]] → Critical Gotchas → Data directory creation

## 🎯 Testing Strategy

### Isolated Test Pattern

```python
@pytest.fixture
def system_under_test(self):
    with tempfile.TemporaryDirectory() as tmpdir:
        yield AISystem(data_dir=tmpdir)  # Isolated state
        # Cleanup automatic via context manager
```

**Learn More**:
- Complete testing strategy: [[PROGRAM_SUMMARY]] → Testing Strategy
- Test coverage details: [[PROGRAM_SUMMARY]] → Test Coverage Matrix
- CI/CD pipeline: [[DEVELOPER_QUICK_REFERENCE]] → CI/CD

---

### Test Coverage Matrix

| System               | Init | State | Persist | Total |
|---------------------|------|-------|---------|-------|
| FourLaws            | ✓    | ✓     | N/A     | 2     |
| AIPersona           | ✓    | ✓     | ✓       | 3     |
| MemorySystem        | ✓    | ✓     | ✓       | 3     |
| LearningRequests    | ✓    | ✓     | ✓       | 4     |
| CommandOverride     | ✓    | ✓     | ✓       | 3     |
| **Total**           |      |       |         | **14**|

**Learn More**:
- Detailed test descriptions: [[PROGRAM_SUMMARY]] → Testing section
- Running tests: [[DEVELOPER_QUICK_REFERENCE]] → Tests
- Test patterns: [[COPILOT_MANDATORY_GUIDE]] → Testing Patterns

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

**Learn More**:
- API key setup: [[DEVELOPER_QUICK_REFERENCE]] → Environment Setup
- OpenAI integration: [[PROGRAM_SUMMARY]] → OpenAI Integration
- Environment configuration: [[COPILOT_MANDATORY_GUIDE]] → Environment Setup

---

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

**Learn More**:
- Signal/slot patterns: [[INTEGRATION_GUIDE]]
- Dashboard integration: [[INTEGRATION_GUIDE]] → Handle Signal Callbacks
- GUI architecture: [[PROGRAM_SUMMARY]] → GUI Architecture
- Threading gotchas: [[COPILOT_MANDATORY_GUIDE]] → PyQt6 threading

---

### Agent vs Plugin

- **Agents**: Specialized AI subsystems in `src/app/agents/` (oversight, planner, validator, explainability)
- **Plugins**: Simple enable/disable extensions via PluginManager (lines 340-395 in ai_systems.py)
- **Key Difference**: Agents are core functionality; Plugins are optional extensions

**Learn More**:
- AI Agent System: [[PROGRAM_SUMMARY]] → AI Agent System
- Security agents: [[SECURITY_AGENTS_GUIDE]]
- Plugin system: [[PROGRAM_SUMMARY]] → PluginManager

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

**Learn More**:
- Complete command reference: [[DEVELOPER_QUICK_REFERENCE]]
- Development workflows: [[COPILOT_MANDATORY_GUIDE]] → Development Workflows
- Production deployment: [[INFRASTRUCTURE_PRODUCTION_GUIDE]]

## ⚠️ Critical Patterns

### Module Imports

```python
# ✅ CORRECT (from project root)
python -m src.app.main

# ❌ WRONG (breaks imports)
python src/app/main.py
```

**Learn More**: [[COPILOT_MANDATORY_GUIDE]] → Module Imports

---

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

**Learn More**:
- Persistence patterns: [[PROGRAM_SUMMARY]] → Data Persistence Pattern
- Critical gotchas: [[COPILOT_MANDATORY_GUIDE]] → Critical Gotchas → State persistence

---

### Threading in PyQt6

```python
# ✅ CORRECT
QTimer.singleShot(1000, self.delayed_action)

# ❌ WRONG (thread safety issues)
threading.Thread(target=self.delayed_action).start()
```

**Learn More**:
- PyQt6 threading: [[COPILOT_MANDATORY_GUIDE]] → PyQt6 threading
- Integration guide: [[INTEGRATION_GUIDE]]

## 🔐 Security Layers

**Implementation:** [[AGENT-080-CONCEPT-CODE-MAP#security-frameworks|Complete Security Implementation in Traceability Matrix]]

**Core Security Files:**
- [[src/app/core/asymmetric_security_engine.py|AsymmetricSecurityEngine]] - RSA-4096, ECDSA (1200+ lines)
- [[src/app/core/user_manager.py|UserManager]] - Bcrypt password hashing (400+ lines)
- [[src/app/core/location_tracker.py|LocationTracker]] - Fernet encryption (Lines 200-350)
- [[src/app/core/ai_systems.py|FourLaws & Black Vault]] - Ethics + content filtering
- [[tests/test_asymmetric_security.py|Security Tests]] - 88% coverage

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

**Learn More**:
- Four Laws implementation: [[AI_PERSONA_IMPLEMENTATION]] → Four Laws Validation
- Black Vault details: [[LEARNING_REQUEST_IMPLEMENTATION]] → Black Vault section
- Command Override: [[PROGRAM_SUMMARY]] → CommandOverrideSystem
- Password security: [[COPILOT_MANDATORY_GUIDE]] → Password Security
- Security agents: [[SECURITY_AGENTS_GUIDE]]
- Security overview: [[SECURITY]]

## 📚 Documentation Hierarchy

**Complete Traceability:** [[AGENT-080-CONCEPT-CODE-MAP|Architecture Concept-to-Code Map]] - 421 bidirectional concept→code links

1. **Quick Start**: [[DESKTOP_APP_QUICKSTART]] - Installation & launch (10 min)
1. **Quick Reference**: [[DEVELOPER_QUICK_REFERENCE]] - Essential commands (5 min)
1. **Architecture**: [[PROGRAM_SUMMARY]] - Complete system overview (600+ lines, 2+ hours)
1. **Features**:
   - [[AI_PERSONA_IMPLEMENTATION]] - Personality system (90 min) → [[src/app/core/ai_systems.py#aipersona|Implementation]]
   - [[LEARNING_REQUEST_IMPLEMENTATION]] - Learning workflow (60 min) → [[src/app/core/ai_systems.py#learningrequestmanager|Implementation]]
   - [[INTEGRATION_GUIDE]] - Dashboard integration (35 min)
1. **This File**: Architecture patterns and data flows (30 min)
1. **AI Agent Guide**: [[COPILOT_MANDATORY_GUIDE]] - Development patterns (60 min)
1. **Security**: [[SECURITY_AGENTS_GUIDE]] - Security testing agents (180 min)
1. **Infrastructure**: [[INFRASTRUCTURE_PRODUCTION_GUIDE]] - Production deployment (120 min)
1. **Traceability**: [[AGENT-080-CONCEPT-CODE-MAP]] - Concept→code bidirectional links

---

## 🎓 Learn More

**New developer?** Start with [[DEVELOPER_QUICK_REFERENCE]] → this document → [[COPILOT_MANDATORY_GUIDE]] → [[PROGRAM_SUMMARY]]

**Need comprehensive details?** See [[PROGRAM_SUMMARY]] for exhaustive component inventory and implementation details.

**Planning integrations?** Review [[INTEGRATION_GUIDE]] for dashboard integration patterns and signal callbacks.

**Deploying to production?** Follow [[INFRASTRUCTURE_PRODUCTION_GUIDE]] for Kubernetes deployment and monitoring.

**Security audit?** Read [[SECURITY_AGENTS_GUIDE]] → [[AI_PERSONA_IMPLEMENTATION]] (Four Laws) → [[LEARNING_REQUEST_IMPLEMENTATION]] (Black Vault)

**Complete navigation?** See [[AGENT-084-LEARNING-PATHS]] for all learning paths, documentation tiers, and 350+ cross-referenced wiki links.

**Concept-to-Code Traceability?** See [[AGENT-080-CONCEPT-CODE-MAP]] for 421 bidirectional links from architecture concepts to implementing code.

---

**Last Updated**: April 20, 2026  
**Target Audience**: AI coding agents and new developers  
**Traceability Matrix**: [[AGENT-080-CONCEPT-CODE-MAP|Complete Concept-to-Code Map]]

**Last Updated**: 2026-04-20  
**Target Audience**: AI coding agents and new developers  
**Version**: 1.2.1
