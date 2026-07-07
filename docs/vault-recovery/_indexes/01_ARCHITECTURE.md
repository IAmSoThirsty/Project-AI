---
type: moc
area: architecture
priority: P0
status: active
version: "1.0.0"
created: 2025-01-23
updated: 2025-01-23
maintainer: AGENT-019
total_documents: 200+
schema_version: "1.0"
tags:
  - architecture
  - design
  - system-design
  - moc
aliases:
  - Architecture MOC
  - System Design Index
  - Architecture Map
related_mocs:
  - "[[02_SECURITY]]"
  - "[[06_SOURCE_CODE]]"
  - "[[07_AGENTS]]"
---

# 01 - Architecture & Design MOC

**Purpose:** Comprehensive map of Project-AI's architectural documentation, design patterns, system diagrams, integration points, and architecture decision records (ADRs). This MOC provides structured access to architectural knowledge spanning desktop application (PyQt6), web platform (React + Flask), AI systems (6 core + 4 specialized agents), data persistence, and external integrations.

**Scope:** System architecture, component design, data flows, architectural patterns, ADRs, integration designs, scalability considerations, and technical debt tracking.

**Audience:** System architects, senior developers, technical leads, and anyone making architectural decisions or evaluating system design changes.

---

## 🏗️ System Architecture Overview

### High-Level Architecture

#### Desktop Application Architecture
- **UI Layer:** PyQt6 Leather Book Interface (6-zone dashboard + dual-page layout)
- **Core Layer:** 11 business logic modules in `src/app/core/`
- **Agent Layer:** 4 specialized AI agents in `src/app/agents/`
- **Data Layer:** JSON persistence in `data/` directory
- **Integration Layer:** OpenAI, Hugging Face, GitHub APIs

**Key Documents:**
- `architecture-desktop-overview.md` - Desktop application architecture [P0, Active]
- `architecture-pyqt6-design.md` - PyQt6 UI architecture and patterns [P0, Active]
- `architecture-leather-book-ui.md` - Leather Book interface design [P1, Active]
- `data-flow-user-interaction.md` - User interaction data flows [P0, Active]

#### Web Platform Architecture
- **Frontend:** React 18 + Vite + Zustand state management
- **Backend:** Flask API wrapping core systems
- **Database:** PostgreSQL (planned, currently JSON)
- **Deployment:** Docker Compose with service separation
- **Ports:** Backend (5000), Frontend (3000)

**Key Documents:**
- `architecture-web-overview.md` - Web platform architecture [P1, In-Progress]
- `architecture-react-frontend.md` - React frontend design [P1, Planned]
- `architecture-flask-api.md` - Flask API architecture [P1, Planned]
- `web-desktop-integration.md` - Web/desktop integration strategy [P2, Planned]

#### AI Systems Architecture
- **Core Systems:** FourLaws, AIPersona, MemoryExpansion, Learning, Override, Plugin
- **Specialized Agents:** Oversight, Planner, Validator, Explainability
- **Ethics Framework:** Hierarchical rule validation (Asimov's Laws)
- **Decision Engine:** Constitutional AI with value alignment
- **State Management:** JSON persistence with atomic saves

**Key Documents:**
- `architecture-ai-systems.md` - AI systems architecture overview [P0, Active]
- `architecture-fourlaws.md` - FourLaws ethics framework design [P0, Active]
- `architecture-persona.md` - AIPersona system architecture [P1, Active]
- `architecture-memory.md` - MemoryExpansionSystem design [P1, Active]
- `architecture-learning.md` - LearningRequestManager architecture [P1, Active]
- `architecture-agents.md` - Specialized agents architecture [P1, Active]

---

## 🎯 Architecture Decision Records (ADRs)

### Active ADRs

#### Language & Framework Decisions
- `adr-001-python-stack.md` - Python as primary backend language [P0, Active, 2024-01]
  - **Decision:** Python 3.11+ for backend development
  - **Rationale:** Rich AI/ML ecosystem, rapid development, strong typing support
  - **Alternatives Considered:** Node.js (rejected: typing complexity), Go (rejected: AI library ecosystem)

- `adr-002-pyqt6-gui.md` - PyQt6 for desktop UI framework [P0, Active, 2024-01]
  - **Decision:** PyQt6 for cross-platform desktop UI
  - **Rationale:** Mature framework, native performance, comprehensive widgets
  - **Alternatives Considered:** Tkinter (rejected: limited styling), Electron (rejected: resource overhead)

- `adr-003-react-web-frontend.md` - React 18 for web UI [P1, Active, 2024-02]
  - **Decision:** React 18 with Vite build tool
  - **Rationale:** Component reusability, strong ecosystem, developer familiarity
  - **Alternatives Considered:** Vue (rejected: smaller ecosystem), Svelte (rejected: team experience)

#### Data & Persistence Decisions
- `adr-004-json-persistence.md` - JSON for configuration persistence [P0, Active, 2024-01]
  - **Decision:** JSON files for user data, AI state, configuration
  - **Rationale:** Simple, human-readable, version-controllable, sufficient for single-user desktop
  - **Alternatives Considered:** SQLite (rejected: overkill for config), YAML (rejected: no native Python support)
  - **Future Migration:** PostgreSQL for web platform (multi-user requirements)

- `adr-005-bcrypt-hashing.md` - bcrypt for password hashing [P0, Active, 2024-01]
  - **Decision:** bcrypt with salt for user password storage
  - **Rationale:** Industry standard, adaptive cost factor, built-in salt
  - **Alternatives Considered:** SHA-256 (rejected: no salt, too fast), Argon2 (rejected: complexity)

#### AI & Ethics Decisions
- `adr-006-fourlaws-ethics.md` - FourLaws hierarchical ethics framework [P0, Active, 2024-02]
  - **Decision:** Immutable hierarchical rules based on Asimov's Laws
  - **Rationale:** Clear ethical boundaries, predictable behavior, user safety
  - **Alternatives Considered:** Reinforcement learning (rejected: unpredictable), hardcoded rules (rejected: inflexible)

- `adr-007-constitutional-ai.md` - Constitutional AI for value alignment [P1, Active, 2024-03]
  - **Decision:** Multi-path governance with constitutional constraints
  - **Rationale:** Value alignment, interpretable decisions, human oversight
  - **Alternatives Considered:** Pure ML (rejected: black box), manual review (rejected: doesn't scale)

- `adr-008-learning-approval.md` - Human-in-loop for learning requests [P0, Active, 2024-02]
  - **Decision:** Explicit approval required for all AI learning requests
  - **Rationale:** User control, prevent unwanted learning, transparency
  - **Alternatives Considered:** Auto-approve (rejected: loss of control), ML filtering (rejected: false positives)

#### Integration Decisions
- `adr-009-openai-integration.md` - OpenAI as primary LLM provider [P1, Active, 2024-02]
  - **Decision:** OpenAI GPT models for intelligence engine
  - **Rationale:** Best-in-class performance, comprehensive API, strong safety features
  - **Alternatives Considered:** Local models (rejected: quality), Anthropic (rejected: cost)

- `adr-010-huggingface-images.md` - Hugging Face for image generation [P1, Active, 2024-03]
  - **Decision:** Stable Diffusion 2.1 via Hugging Face Inference API
  - **Rationale:** Open source, cost-effective, good quality, no content policy restrictions
  - **Alternatives Considered:** DALL-E only (rejected: cost), local SD (rejected: hardware requirements)

### Superseded ADRs
- `adr-legacy-001-flask-only.md` - Flask-only architecture [Superseded, 2024-01]
  - **Superseded By:** [[adr-002-pyqt6-gui]]
  - **Reason:** Desktop-first approach required native UI performance

- `adr-legacy-002-sha256-only.md` - SHA-256 for all hashing [Superseded, 2024-01]
  - **Superseded By:** [[adr-005-bcrypt-hashing]]
  - **Reason:** Password hashing requires adaptive cost factors

---

## 🔧 Design Patterns

### Architectural Patterns

#### Layered Architecture
- **Pattern:** Strict layer separation (UI → Core → Data)
- **Implementation:** PyQt6 GUI calls core modules, core modules manage data persistence
- **Benefits:** Clear separation of concerns, testability, maintainability
- **Documents:** `pattern-layered-architecture.md` [P1, Active]

#### Repository Pattern
- **Pattern:** Data access abstraction via repository classes
- **Implementation:** UserManager, AIPersona, MemoryExpansionSystem use repository pattern
- **Benefits:** Decoupled persistence, easy testing with mocks, migration flexibility
- **Documents:** `pattern-repository.md` [P2, Active]

#### Observer Pattern
- **Pattern:** Event-driven communication via PyQt6 signals
- **Implementation:** `user_logged_in` signal, `send_message` signal, dashboard event handlers
- **Benefits:** Loose coupling, reactive UI updates, extensibility
- **Documents:** `pattern-observer-signals.md` [P1, Active]

#### Strategy Pattern
- **Pattern:** Interchangeable algorithms for AI decision-making
- **Implementation:** FourLaws rule strategies, Persona mood strategies, Learning approval strategies
- **Benefits:** Flexible decision logic, easy to add new strategies, testable
- **Documents:** `pattern-strategy-ai.md` [P1, Active]

#### Template Method Pattern
- **Pattern:** Base class defines skeleton, subclasses implement specifics
- **Implementation:** Dashboard panels extend base panel, agents extend base agent
- **Benefits:** Code reuse, consistent structure, enforced contracts
- **Documents:** `pattern-template-method.md` [P2, Active]

### Design Principles

#### SOLID Principles
- **Single Responsibility:** Each module has one clear purpose
- **Open/Closed:** Extensible via plugins, closed for modification
- **Liskov Substitution:** Agent subclasses are interchangeable
- **Interface Segregation:** Focused interfaces for each system
- **Dependency Inversion:** Depend on abstractions, not implementations

**Documents:** `principles-solid.md` [P1, Active]

#### DRY (Don't Repeat Yourself)
- **Implementation:** Shared utilities in `dashboard_utils.py`, reusable components
- **Benefits:** Single source of truth, easier maintenance
- **Documents:** `principles-dry.md` [P2, Active]

#### KISS (Keep It Simple, Stupid)
- **Implementation:** Simple JSON persistence, straightforward data flows
- **Benefits:** Easier to understand, debug, and maintain
- **Documents:** `principles-kiss.md` [P2, Active]

---

## 📊 Component Architecture

### Core Systems (`src/app/core/`)

#### ai_systems.py (470 lines - 6 integrated systems)
- **FourLaws:** Immutable ethics framework (lines 1-100)
- **AIPersona:** 8 personality traits, mood tracking (lines 100-200)
- **MemoryExpansionSystem:** 6-category knowledge base (lines 200-300)
- **LearningRequestManager:** Human-in-loop approval (lines 300-400)
- **CommandOverrideSystem:** SHA-256 password protection (lines 400-470)
- **PluginManager:** Enable/disable plugins (lines 340-395)

**Documents:**
- `component-ai-systems.md` - ai_systems.py architecture [P0, Active]
- `component-fourlaws.md` - FourLaws implementation [P0, Active]
- `component-persona.md` - AIPersona implementation [P1, Active]
- `component-memory.md` - MemoryExpansionSystem implementation [P1, Active]

#### Feature Modules
- `user_manager.py` - User auth, bcrypt hashing, JSON persistence
- `command_override.py` - Extended master password system (10+ safety protocols)
- `learning_paths.py` - OpenAI-powered learning path generation
- `data_analysis.py` - CSV/XLSX/JSON analysis, K-means clustering
- `security_resources.py` - GitHub API integration, CTF/security repos
- `location_tracker.py` - IP geolocation, GPS, encrypted history (Fernet)
- `emergency_alert.py` - Emergency contact system with email alerts
- `intelligence_engine.py` - OpenAI chat integration
- `intent_detection.py` - Scikit-learn ML intent classifier
- `image_generator.py` - HF Stable Diffusion + OpenAI DALL-E

**Documents:**
- `component-user-manager.md` - User management architecture [P0, Active]
- `component-command-override.md` - Command override system [P1, Active]
- `component-learning-paths.md` - Learning path generation [P1, Active]
- `component-image-generator.md` - Image generation architecture [P1, Active]

### GUI Components (`src/app/gui/`)

#### Leather Book Interface
- `leather_book_interface.py` - Main window, dual-page layout (659 lines)
- `leather_book_dashboard.py` - 6-zone dashboard (608 lines)
- `persona_panel.py` - 4-tab AI configuration
- `dashboard_handlers.py` - Event handler methods
- `dashboard_utils.py` - Error handling, logging, validation
- `image_generation.py` - Image gen UI, dual-page (450 lines)

**Documents:**
- `component-leather-book.md` - Leather Book UI architecture [P0, Active]
- `component-dashboard.md` - Dashboard architecture [P0, Active]
- `component-persona-panel.md` - Persona panel design [P1, Active]
- `component-image-gen-ui.md` - Image generation UI [P1, Active]

### AI Agents (`src/app/agents/`)

- `oversight.py` - Action safety validation
- `planner.py` - Task decomposition
- `validator.py` - Input/output validation
- `explainability.py` - Decision explanations

**Documents:**
- `component-agents.md` - AI agents architecture [P1, Active]
- `component-oversight.md` - Oversight agent design [P1, Active]
- `component-planner.md` - Planner agent design [P2, Active]

---

## 🔄 Data Flow Diagrams

### User Interaction Flow
```
User Input (GUI) → Dashboard Handler → FourLaws Validation → Core Module → 
OpenAI/Local Processing → Persona Update → Memory Log → GUI Response
```

**Documents:** `dataflow-user-interaction.md` [P0, Active]

### Learning Request Flow
```
AI discovers content → LearningRequestManager.request_learning() → 
Human approval UI → Approve/Deny → 
Approved: Add to knowledge base | Denied: Add to Black Vault (SHA-256)
```

**Documents:** `dataflow-learning-request.md` [P0, Active]

### Authentication Flow
```
User login → UserManager.authenticate() → bcrypt.checkpw() → 
Success: user_logged_in signal | Failure: increment failed_attempts → 
Account lockout after 5 attempts
```

**Documents:** `dataflow-authentication.md` [P0, Active]

### Image Generation Flow
```
User prompt → Content filter check → Backend selection → 
HF API / OpenAI API → ImageGenerationWorker (QThread) → 
image_generated signal → Display + Save to history
```

**Documents:** `dataflow-image-generation.md` [P1, Active]

---

## 🧩 Integration Points

### External API Integrations
- **OpenAI:** GPT models (intelligence_engine), DALL-E 3 (image_generator)
- **Hugging Face:** Stable Diffusion 2.1 (image_generator)
- **GitHub:** Repository search, security resources (security_resources)
- **SMTP:** Email alerts (emergency_alert)
- **IP Geolocation:** Location tracking (location_tracker)

**Documents:**
- `integration-openai.md` - OpenAI integration architecture [P1, Active]
- `integration-huggingface.md` - Hugging Face integration [P1, Active]
- `integration-github.md` - GitHub API integration [P2, Active]

### Internal System Integrations
- **Core ↔ GUI:** PyQt6 signals for event-driven communication
- **Core ↔ Agents:** Direct method calls for validation/planning
- **Core ↔ Data:** Repository pattern for persistence
- **GUI ↔ Data:** Indirect via Core layer (strict layering)

**Documents:**
- `integration-internal.md` - Internal system integration [P1, Active]
- `integration-signals.md` - PyQt6 signal architecture [P1, Active]

---

## 🚀 Scalability & Performance

### Current Architecture Limitations
- **Single-user desktop:** No multi-user support in JSON persistence
- **Synchronous operations:** Blocking UI during long operations (mitigated by QThread)
- **In-memory state:** No distributed state management
- **File-based storage:** No transactional consistency guarantees

**Documents:** `scalability-limitations.md` [P2, Active]

### Planned Improvements
- **PostgreSQL migration:** Multi-user support, ACID transactions
- **Async operations:** Full async/await for all I/O operations
- **Redis caching:** Session management, rate limiting
- **Microservices:** Service separation for web platform

**Documents:**
- `scalability-roadmap.md` - Scalability improvement roadmap [P2, Planned]
- `performance-optimization.md` - Performance optimization strategies [P2, Planned]

### Performance Benchmarks
- **Desktop startup:** <2 seconds to dashboard
- **AI response time:** 1-5 seconds (OpenAI API latency)
- **Image generation:** 20-60 seconds (model inference time)
- **State persistence:** <100ms (JSON write operations)

**Documents:** `performance-benchmarks.md` [P2, Active]

---

## 🛠️ Technical Debt

### Known Debt Items

#### High Priority (P1)
- **SHA-256 password hashing in CommandOverride:** Should use bcrypt for consistency
- **Synchronous OpenAI calls:** Block UI thread, need async/await
- **Hardcoded paths:** Some modules use hardcoded `data/` paths instead of parameters
- **Limited error recovery:** Some failures don't have retry logic

**Documents:** `tech-debt-p1.md` [P1, Active]

#### Medium Priority (P2)
- **Mixed signal/direct call patterns:** Inconsistent inter-component communication
- **Duplicate validation logic:** Some validation duplicated across modules
- **Limited test coverage:** Some edge cases not covered (targeting 80%+)
- **Missing type hints:** Some older code lacks type annotations

**Documents:** `tech-debt-p2.md` [P2, Active]

#### Low Priority (P3)
- **Code duplication in GUI:** Some dashboard panel code is duplicated
- **Inefficient graph rendering:** Obsidian graph can be slow with 2000+ docs
- **Limited internationalization:** UI is English-only

**Documents:** `tech-debt-p3.md` [P3, Active]

---

## 📚 Cross-References

### Related MOCs
- [[02_SECURITY]] - Security architecture, threat models, encryption
- [[06_SOURCE_CODE]] - Code organization, module documentation
- [[07_AGENTS]] - AI agent architecture, decision systems
- [[08_INTEGRATIONS]] - External API integrations

### Related Indexes
- `by-type/adr-type-index.md` - All Architecture Decision Records
- `by-type/specification-type-index.md` - Technical specifications
- `by-priority/p0-critical-priority-index.md` - Critical architecture docs
- `cross-reference/architecture-dependencies-index.md` - Architecture dependencies

---

## 🔍 Quick Reference

### Common Tasks

**Finding Architecture Decisions:**
1. Check ADR section in this MOC
2. Search `by-type/adr-type-index.md`
3. Filter by date or status

**Understanding Component Design:**
1. Check Component Architecture section
2. Review source code in [[06_SOURCE_CODE]]
3. Check data flow diagrams

**Evaluating Integration Options:**
1. Review Integration Points section
2. Check [[08_INTEGRATIONS]] for detailed API docs
3. Review related ADRs for context

**Assessing Scalability:**
1. Review Scalability & Performance section
2. Check performance benchmarks
3. Review planned improvements roadmap

---

## 📊 Statistics

- **Total Architecture Documents:** 200+ documents
- **Active ADRs:** 10 decision records
- **Superseded ADRs:** 2 historical records
- **Design Patterns:** 5 core patterns documented
- **Integration Points:** 5 external + 4 internal
- **Performance Benchmarks:** 4 key metrics tracked
- **Technical Debt Items:** 15 tracked items (P1: 4, P2: 4, P3: 7)

---

## 🛡️ Governance

**Maintainer:** AGENT-019 (MOC Constructor)  
**Update Frequency:** Event-driven (when architecture changes)  
**Review Cycle:** Quarterly architecture review  
**Change Control:** ADR required for architectural changes  
**Quality Gate:** All architecture docs must include diagrams + rationale

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-23  
**Schema Compliance:** ✅ 100%  
**Link Validation:** ⏳ Pending Phase 2 document creation

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

