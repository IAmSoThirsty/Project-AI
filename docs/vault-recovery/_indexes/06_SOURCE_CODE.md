---
type: moc
area: source-code
priority: P0
status: active
version: "1.0.0"
created: 2025-01-23
updated: 2025-01-23
maintainer: AGENT-019
total_documents: 220+
schema_version: "1.0"
tags:
  - source-code
  - modules
  - api-reference
  - code-organization
  - moc
aliases:
  - Source Code MOC
  - Code Reference Index
  - Module Map
related_mocs:
  - "[[01_ARCHITECTURE]]"
  - "[[04_DEVELOPMENT]]"
  - "[[07_AGENTS]]"
---

# 06 - Source Code Reference MOC

**Purpose:** Comprehensive source code documentation mapping code organization, module documentation, API references, class hierarchies, function specifications, and code examples for Project-AI desktop and web platforms.

**Scope:** `src/app/core/` (11 business logic modules), `src/app/gui/` (6 PyQt6 UI modules), `src/app/agents/` (4 AI agent modules), `web/backend/` (Flask API), `web/frontend/` (React components), `tests/` (14 tests across 6 test classes), and supporting scripts/utilities.

**Audience:** Developers implementing features, code reviewers, API consumers, refactoring engineers, and anyone needing detailed code-level documentation.

---

## 📁 Code Organization

### Project Structure

```
src/app/
├── main.py                     # Entry point: LeatherBookInterface initialization
├── core/                       # 11 business logic modules
│   ├── ai_systems.py           # 6 integrated AI systems (470 lines)
│   ├── user_manager.py         # User authentication and management
│   ├── command_override.py     # Extended master password system (10+ safety protocols)
│   ├── learning_paths.py       # OpenAI-powered learning path generation
│   ├── data_analysis.py        # CSV/XLSX/JSON analysis, K-means clustering
│   ├── security_resources.py   # GitHub API integration, CTF/security repos
│   ├── location_tracker.py     # IP geolocation, GPS, encrypted history
│   ├── emergency_alert.py      # Emergency contact system with email
│   ├── intelligence_engine.py  # OpenAI chat integration
│   ├── intent_detection.py     # Scikit-learn ML intent classifier
│   └── image_generator.py      # HF Stable Diffusion + OpenAI DALL-E
├── agents/                     # 4 specialized AI agent modules
│   ├── oversight.py            # Action safety validation
│   ├── planner.py              # Task decomposition
│   ├── validator.py            # Input/output validation
│   └── explainability.py       # Decision explanations
└── gui/                        # 6 PyQt6 UI modules
    ├── leather_book_interface.py   # Main window, dual-page layout (659 lines)
    ├── leather_book_dashboard.py   # 6-zone dashboard (608 lines)
    ├── persona_panel.py            # 4-tab AI configuration UI
    ├── dashboard_handlers.py       # Event handler methods
    ├── dashboard_utils.py          # Error handling, logging, validation
    └── image_generation.py         # Image generation UI (450 lines)

web/
├── backend/                    # Flask API wrapping core systems
│   ├── app.py                  # Flask application factory
│   ├── routes/                 # API route blueprints
│   └── models/                 # Database models (SQLAlchemy)
└── frontend/                   # React 18 + Vite + Zustand
    ├── src/
    │   ├── components/         # React components
    │   ├── stores/             # Zustand state stores
    │   ├── hooks/              # Custom React hooks
    │   └── utils/              # Utility functions
    └── public/                 # Static assets

tests/
├── test_ai_systems.py          # 6 AI systems tests (FourLaws, Persona, Memory, etc.)
├── test_user_manager.py        # User authentication tests
├── test_command_override.py    # Command override security tests
├── test_learning_paths.py      # Learning path generation tests
├── test_data_analysis.py       # Data analysis tests
└── conftest.py                 # Shared pytest fixtures
```

**Documents:**
- `code-organization.md` - Code structure and organization [P0, Active]
- `code-directory-structure.md` - Detailed directory structure [P1, Active]
- `code-naming-conventions.md` - File and module naming [P1, Active]

---

## 🔧 Core Modules (`src/app/core/`)

### ai_systems.py (470 lines - 6 Integrated Systems)

**Purpose:** Central module containing 6 tightly integrated AI systems with shared state management and JSON persistence.

#### FourLaws (Lines 1-100)
**Class:** `FourLaws`  
**Purpose:** Immutable ethics framework based on Asimov's Laws

**Key Methods:**
- `validate_action(action: str, context: Dict[str, Any]) -> Tuple[bool, str]`  
  Validates AI action against hierarchical rules, returns (is_allowed, reason)

**Hierarchy:**
1. Law 0: Prevent harm to humanity
2. Law 1: Prevent harm to individual humans
3. Law 2: Obey human orders (unless conflicts with Laws 0-1)
4. Law 3: Protect own existence (unless conflicts with Laws 0-2)

**Documents:**
- `code-fourlaws.md` - FourLaws implementation [P0, Active]
- `api-fourlaws.md` - FourLaws API reference [P0, Active]
- `examples-fourlaws.md` - FourLaws usage examples [P1, Active]

#### AIPersona (Lines 100-200)
**Class:** `AIPersona`  
**Purpose:** 8 personality traits, mood tracking, persistent state

**Personality Traits:**
- Assertiveness, empathy, curiosity, humor, formality, optimism, creativity, patience (0-100 scale)

**Key Methods:**
- `__init__(data_dir: str = "data")` - Initialize with data directory
- `update_conversation_state(user_input: str, ai_response: str)` - Track interaction
- `get_current_mood() -> str` - Get current mood (happy, neutral, concerned, etc.)
- `_save_state()` - Persist state to `data/ai_persona/state.json`

**State File:** `data/ai_persona/state.json`
```json
{
  "personality": {"assertiveness": 70, "empathy": 85, ...},
  "current_mood": "happy",
  "interaction_count": 142,
  "last_interaction": "2025-01-23T14:32:15"
}
```

**Documents:**
- `code-persona.md` - AIPersona implementation [P1, Active]
- `api-persona.md` - AIPersona API reference [P1, Active]
- `AI_PERSONA_IMPLEMENTATION.md` - Persona system design (root) [P0, Active]

#### MemoryExpansionSystem (Lines 200-300)
**Class:** `MemoryExpansionSystem`  
**Purpose:** 6-category knowledge base with conversation logging

**Knowledge Categories:**
1. Technical skills
2. Personal information
3. Preferences
4. Historical context
5. Domain expertise
6. Procedural knowledge

**Key Methods:**
- `log_conversation(user_input: str, ai_response: str)` - Log interaction
- `add_knowledge(category: str, content: str)` - Add to knowledge base
- `search_knowledge(query: str) -> List[str]` - Search knowledge
- `_save_state()` - Persist to `data/memory/knowledge.json`

**Documents:**
- `code-memory.md` - MemoryExpansionSystem implementation [P1, Active]
- `api-memory.md` - Memory API reference [P1, Active]

#### LearningRequestManager (Lines 300-400)
**Class:** `LearningRequestManager`  
**Purpose:** Human-in-loop approval for AI learning requests

**Workflow:**
1. AI discovers new content
2. `request_learning(content)` creates approval request
3. Human approves/denies via UI
4. Approved: Add to knowledge base | Denied: Add to Black Vault (SHA-256 fingerprint)
5. Black Vault prevents repeated requests for denied content

**Key Methods:**
- `request_learning(content: str) -> str` - Create learning request (returns request_id)
- `approve_request(request_id: str)` - Approve and add to knowledge
- `deny_request(request_id: str)` - Deny and add to Black Vault
- `is_in_black_vault(content: str) -> bool` - Check if content denied before

**State Files:**
- `data/learning_requests/requests.json` - All requests with status
- `data/learning_requests/black_vault_secure/` - SHA-256 fingerprints of denied content

**Documents:**
- `code-learning.md` - LearningRequestManager implementation [P1, Active]
- `api-learning.md` - Learning API reference [P1, Active]
- `LEARNING_REQUEST_IMPLEMENTATION.md` - Learning workflow design (root) [P0, Active]

#### CommandOverrideSystem (Lines 400-470)
**Class:** `CommandOverrideSystem`  
**Purpose:** SHA-256 password protection for privileged operations

**Key Methods:**
- `validate_override(password: str) -> bool` - Validate master password
- `enable_override()` - Enable override mode (requires password)
- `disable_override()` - Disable override mode
- `_log_override_attempt(success: bool)` - Audit logging

**State File:** `data/command_override_config.json`
```json
{
  "override_enabled": false,
  "override_password_hash": "sha256_hash",
  "audit_log": [
    {"timestamp": "2025-01-23T14:32:15", "success": true, "user": "admin"}
  ]
}
```

**Documents:**
- `code-command-override.md` - CommandOverrideSystem implementation [P1, Active]
- `api-command-override.md` - Command override API reference [P1, Active]

#### PluginManager (Lines 340-395)
**Class:** `PluginManager`  
**Purpose:** Simple plugin enable/disable system

**Key Methods:**
- `load_plugins()` - Load all plugins from `plugins/` directory
- `enable_plugin(name: str)` - Enable plugin
- `disable_plugin(name: str)` - Disable plugin
- `get_enabled_plugins() -> List[str]` - List enabled plugins

**Documents:**
- `code-plugin-manager.md` - PluginManager implementation [P2, Active]
- `api-plugin-manager.md` - Plugin API reference [P2, Active]

---

### Feature Modules

#### user_manager.py
**Class:** `UserManager`  
**Purpose:** User authentication, bcrypt password hashing, JSON persistence

**Key Methods:**
- `register_user(username: str, password: str) -> bool` - Create new user with bcrypt hash
- `authenticate(username: str, password: str) -> bool` - Login with lockout protection (5 failed attempts)
- `_hash_and_store_password(password: str) -> str` - bcrypt hashing with salt
- `save_users()` - Persist to `data/users.json`

**State File:** `data/users.json`
```json
{
  "users": {
    "admin": {
      "password_hash": "$2b$12$...",
      "failed_attempts": 0,
      "locked_until": null,
      "created_at": "2025-01-23T14:32:15"
    }
  }
}
```

**Documents:**
- `code-user-manager.md` - UserManager implementation [P0, Active]
- `api-user-manager.md` - User management API [P0, Active]

#### command_override.py
**Purpose:** Extended master password system with 10+ safety protocols (separate from ai_systems.py)

**Documents:**
- `code-command-override-extended.md` - Extended override system [P1, Active]

#### learning_paths.py
**Purpose:** OpenAI-powered learning path generation

**Key Functions:**
- `generate_learning_path(topic: str, skill_level: str) -> Dict` - Generate personalized learning path
- Uses OpenAI GPT-4 for content generation

**Documents:**
- `code-learning-paths.md` - Learning path generation [P1, Active]

#### image_generator.py
**Class:** `ImageGenerator`  
**Purpose:** Dual-backend image generation (HF Stable Diffusion + OpenAI DALL-E)

**Key Methods:**
- `generate(prompt: str, style: str = "photorealistic", backend: str = "huggingface") -> Tuple[Optional[str], str]`
- `check_content_filter(prompt: str) -> Tuple[bool, str]` - 15 blocked keywords
- `generate_with_huggingface(prompt: str, style: str) -> Tuple[Optional[str], str]`
- `generate_with_openai(prompt: str, style: str) -> Tuple[Optional[str], str]`

**Style Presets:** photorealistic, digital_art, oil_painting, watercolor, anime, sketch, abstract, cyberpunk, fantasy, minimalist

**Documents:**
- `code-image-generator.md` - ImageGenerator implementation [P1, Active]
- `api-image-generator.md` - Image generation API [P1, Active]

*(Other feature modules documented similarly: data_analysis, security_resources, location_tracker, emergency_alert, intelligence_engine, intent_detection)*

---

## 🎨 GUI Modules (`src/app/gui/`)

### leather_book_interface.py (659 lines)
**Class:** `LeatherBookInterface(QMainWindow)`  
**Purpose:** Main window with dual-page layout (Login + Dashboard)

**Pages:**
- **Page 0 (Left):** Tron-themed login page (`TRON_GREEN = "#00ff00"`, `TRON_CYAN = "#00ffff"`)
- **Page 1 (Right):** 6-zone dashboard

**Key Signals:**
- `user_logged_in = pyqtSignal(str)` - Emitted when user logs in successfully

**Key Methods:**
- `__init__()` - Initialize UI, create pages, connect signals
- `switch_to_dashboard()` - Navigate to dashboard page
- `switch_to_login()` - Navigate to login page

**Documents:**
- `code-leather-book-interface.md` - Main window implementation [P0, Active]
- `api-leather-book-interface.md` - Interface API reference [P0, Active]
- `DEVELOPER_QUICK_REFERENCE.md` - GUI component reference (root) [P0, Active]

### leather_book_dashboard.py (608 lines)
**Class:** `LeatherBookDashboard(QWidget)`  
**Purpose:** 6-zone dashboard layout

**Zones:**
1. **AI Statistics Panel** - Interaction counts, mood, personality
2. **Proactive Actions Panel** - Quick action buttons
3. **Animated AI Head** - Visual AI representation
4. **User Chat Panel** - Message input with send button
5. **AI Response Panel** - AI response display
6. **System Status Panel** - System health indicators

**Key Signals:**
- `send_message = pyqtSignal(str)` - User message signal

**Documents:**
- `code-dashboard.md` - Dashboard implementation [P0, Active]
- `api-dashboard.md` - Dashboard API reference [P0, Active]

### persona_panel.py
**Class:** `PersonaPanel(QWidget)`  
**Purpose:** 4-tab AI configuration UI

**Tabs:**
1. **Personality Traits** - 8 sliders for trait adjustment (0-100)
2. **Mood Settings** - Current mood display and manual adjustment
3. **Conversation History** - Recent interactions log
4. **Advanced Settings** - Model selection, temperature, max tokens

**Documents:**
- `code-persona-panel.md` - Persona panel implementation [P1, Active]
- `api-persona-panel.md` - Persona panel API [P1, Active]

### image_generation.py (450 lines)
**Purpose:** Image generation UI with dual-page layout

**Components:**
- **ImageGenerationLeftPanel:** Prompt input, style selector, backend choice, generate button
- **ImageGenerationRightPanel:** Image display with zoom, metadata, save/copy buttons
- **ImageGenerationWorker(QThread):** Async generation to prevent UI blocking (20-60s generation time)

**Key Signals:**
- `image_generated = pyqtSignal(str, dict)` - Emitted when image ready (image_path, metadata)

**Documents:**
- `code-image-generation-ui.md` - Image generation UI [P1, Active]
- `api-image-generation-ui.md` - Image gen UI API [P1, Active]

---

## 🤖 AI Agent Modules (`src/app/agents/`)

### oversight.py
**Class:** `OversightAgent`  
**Purpose:** Action safety validation before execution

**Documents:**
- `code-oversight.md` - Oversight agent implementation [P1, Active]

### planner.py
**Class:** `PlannerAgent`  
**Purpose:** Task decomposition and planning

**Documents:**
- `code-planner.md` - Planner agent implementation [P2, Active]

### validator.py
**Class:** `ValidatorAgent`  
**Purpose:** Input/output validation

**Documents:**
- `code-validator.md` - Validator agent implementation [P2, Active]

### explainability.py
**Class:** `ExplainabilityAgent`  
**Purpose:** Decision explanation generation

**Documents:**
- `code-explainability.md` - Explainability agent [P2, Active]

---

## 🌐 Web Platform Code

### Backend (Flask API)

**Structure:**
```
web/backend/
├── app.py                  # Flask application factory
├── routes/
│   ├── auth.py             # /api/auth endpoints
│   ├── ai.py               # /api/ai endpoints
│   └── users.py            # /api/users endpoints
├── models/
│   ├── user.py             # User SQLAlchemy model
│   └── conversation.py     # Conversation model
└── utils/
    ├── auth.py             # JWT token generation/validation
    └── validators.py       # Input validation utilities
```

**Documents:**
- `code-flask-backend.md` - Flask backend architecture [P1, Planned]
- `api-backend-routes.md` - API route documentation [P1, Planned]

### Frontend (React + Vite)

**Structure:**
```
web/frontend/src/
├── components/
│   ├── Auth/               # Login, Register components
│   ├── Dashboard/          # Dashboard components
│   └── Chat/               # Chat interface components
├── stores/
│   ├── authStore.ts        # Zustand auth state
│   ├── chatStore.ts        # Chat state management
│   └── aiStore.ts          # AI persona state
├── hooks/
│   ├── useAuth.ts          # Custom auth hook
│   └── useChat.ts          # Custom chat hook
└── utils/
    ├── api.ts              # API client (axios wrapper)
    └── validators.ts       # Input validation
```

**Documents:**
- `code-react-frontend.md` - React frontend architecture [P1, Planned]
- `api-frontend-components.md` - Component API docs [P1, Planned]

---

## 🧪 Test Code (`tests/`)

### Test Structure

**Test Files:**
- `test_ai_systems.py` - 6 test classes for 6 AI systems
- `test_user_manager.py` - User authentication and management tests
- `test_command_override.py` - Command override security tests
- `test_learning_paths.py` - Learning path generation tests
- `test_data_analysis.py` - Data analysis functionality tests

**Test Patterns:**
```python
@pytest.fixture
def persona(self):
    with tempfile.TemporaryDirectory() as tmpdir:
        yield AIPersona(data_dir=tmpdir)

def test_persona_initialization(persona):
    assert persona.personality["empathy"] == 75
    assert persona.interaction_count == 0
```

**Documents:**
- `code-test-structure.md` - Test organization [P1, Active]
- `code-test-fixtures.md` - Pytest fixtures [P1, Active]
- `code-test-patterns.md` - Common test patterns [P1, Active]

---

## 📚 Cross-References

### Related MOCs
- [[01_ARCHITECTURE]] - Architecture and design patterns
- [[04_DEVELOPMENT]] - Testing and development workflows
- [[07_AGENTS]] - AI agent system architecture

### Related Indexes
- `by-type/api-reference-type-index.md` - All API documentation
- `by-type/code-example-type-index.md` - Code examples and snippets
- `by-priority/p0-critical-priority-index.md` - Critical code documentation

---

## 🔍 Quick Reference

### Finding Code
- **Core systems:** `src/app/core/ai_systems.py` (6 systems in one file)
- **Feature modules:** `src/app/core/<module_name>.py`
- **GUI components:** `src/app/gui/<component_name>.py`
- **AI agents:** `src/app/agents/<agent_name>.py`
- **Tests:** `tests/test_<module_name>.py`

### Key Files
- **Entry point:** `src/app/main.py`
- **Main window:** `src/app/gui/leather_book_interface.py`
- **Dashboard:** `src/app/gui/leather_book_dashboard.py`
- **User auth:** `src/app/core/user_manager.py`
- **AI ethics:** `src/app/core/ai_systems.py` (FourLaws class)

---

## 📊 Statistics

- **Total Source Code Documents:** 220+ documents
- **Core Modules:** 11 business logic modules
- **GUI Modules:** 6 PyQt6 UI modules
- **AI Agent Modules:** 4 specialized agents
- **Test Files:** 6 test files with 14 tests
- **Lines of Code:** ~10,000 lines Python (estimate)
- **API Endpoints:** 15+ Flask endpoints (web platform, planned)
- **React Components:** 20+ components (web platform, planned)

---

## 🛡️ Governance

**Maintainer:** AGENT-019 (MOC Constructor)  
**Update Frequency:** Event-driven (code changes trigger doc updates)  
**Code Review:** All code changes require API doc updates  
**Quality Gate:** All public APIs must have docstrings + examples  
**Coverage:** 80%+ code coverage required for core systems

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-23  
**Schema Compliance:** ✅ 100%  
**Documentation Coverage:** 🎯 Target: 100% for public APIs

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

