# GUI Relationships - Master Index

## Overview
This directory contains comprehensive relationship documentation for Project-AI's 6 GUI systems. Each map details signal chains, event flows, component hierarchies, and user interactions.

---

## 📁 Relationship Maps

### 01_DASHBOARD_RELATIONSHIPS.md
**Component:** LeatherBookDashboard [[src/app/gui/leather_book_dashboard.py]]  
**Lines:** 608  
**Coverage:**
- 6-zone dashboard layout (stats, actions, AI head, chat, response)
- 9 unique signals across 5 panel types
- Animation system (20 FPS + 1 Hz stats updates)
- Message routing: User → Dashboard → Interface → Intelligence System
- Navigation hub for 5 feature panels

**Key Relationships:**
- Parent: LeatherBookInterface [[src/app/gui/leather_book_interface.py]]
- Children: StatsPanel [[src/app/gui/leather_book_dashboard.py]], ProactiveActionsPanel [[src/app/gui/leather_book_dashboard.py]], UserChatPanel [[src/app/gui/leather_book_dashboard.py]], AIResponsePanel [[src/app/gui/leather_book_dashboard.py]], AINeuralHead [[src/app/gui/leather_book_dashboard.py]]
- Siblings: ImageGeneration, NewsIntelligence, IntelligenceLibrary, WatchTower, GodTierCommand

---

### 02_PANEL_RELATIONSHIPS.md
**Components:** 5 Dashboard Panels + AINeuralHead  
**Coverage:**
- StatsPanel: System status display (username, time, location, interactions, memory)
- ProactiveActionsPanel: 5 navigation buttons + AI activity label
- UserChatPanel: Message input with validation (sanitize_input [[src/app/security/data_validation.py]], validate_length [[src/app/security/data_validation.py]])
- AIResponsePanel: HTML-formatted conversation history (user: cyan, AI: green)
- AINeuralHead: Animated AI visualization (thinking state, eyes, circuits)

**Key Relationships:**
- All panels isolated, communicate via parent Dashboard
- Shared styling: PANEL_STYLESHEET, TRON colors, TITLE_FONT
- Signal flow: Panel → Dashboard → Interface (upward only)

---

### 03_HANDLER_RELATIONSHIPS.md
**Component:** DashboardHandlers [[src/app/gui/dashboard_handlers.py]]  
**Lines:** 400+  
**Coverage:**
- 10+ event handlers routed through governance pipeline
- Learning path generation (OpenAI-powered)
- Data file loading (CSV/XLSX/JSON)
- Data analysis (clustering, stats)
- Security resources (GitHub API)
- Location tracking toggle
- Emergency alert system

**Key Relationships:**
- Pattern: Handler → Desktop Adapter → Router → Governance → Core Systems
- Fallback: Direct core system calls if governance unavailable
- Validation: sanitize_input, validate_email [[src/app/security/data_validation.py]], validate_length
- Logging: 4 error handling layers

---

### 04_UTILS_RELATIONSHIPS.md
**Components:** 3 Utility Classes  
**Coverage:**
- DashboardErrorHandler [[src/app/gui/dashboard_utils.py]]: Static error handling (handle_exception, handle_warning, validate_input)
- AsyncWorker [[src/app/gui/dashboard_utils.py]]: QThread-based background tasks (finished, error, result signals)
- DashboardAsyncManager [[src/app/gui/dashboard_utils.py]]: Managed thread pool, task tracking, cancellation

**Key Relationships:**
- Used by: All handlers and panels
- Thread safety: Signals for cross-thread communication
- Performance: QThreadPool with configurable max threads
- Cleanup: cancel_all_tasks() on dashboard close

---

### 05_PERSONA_PANEL_RELATIONSHIPS.md
**Component:** PersonaPanel [[src/app/gui/persona_panel.py]]  
**Lines:** 400+  
**Coverage:**
- 4 tabs: Four Laws, Personality, Proactive, Statistics
- Four Laws: Asimov's Laws display + action validator
- Personality: 8 trait sliders (curiosity, patience, empathy, etc.)
- Proactive: Conversation settings (quiet hours, idle time, probability)
- Statistics: Mood, interaction count, trait summary

**Key Relationships:**
- Core System: AIPersona [[src/app/core/ai_systems.py]] (via governance-routed execute_persona_update)
- FourLaws [[src/app/core/ai_systems.py]]: Read-only validation (immutable ethics)
- Signals: personality_changed, proactive_settings_changed
- Governance: All trait updates routed through Desktop Adapter

---

### 06_IMAGE_GENERATION_RELATIONSHIPS.md
**Components:** 3 Classes (Worker + 2 Panels)  
**Lines:** 450+  
**Coverage:**
- ImageGenerationWorker [[src/app/gui/image_generation.py]]: QThread for 20-60s async generation
- ImageGenerationLeftPanel [[src/app/gui/image_generation.py]]: Tron-themed prompt input (10 styles, 3 sizes, 2 backends)
- ImageGenerationRightPanel [[src/app/gui/image_generation.py]]: Image display with zoom, save, copy
- Content filtering: 15 blocked keywords, safety negative prompts
- Dual backend: Hugging Face Stable Diffusion 2.1 + OpenAI DALL-E 3

**Key Relationships:**
- Core System: ImageGenerator [[src/app/core/image_generator.py]] (src/app/core/image_generator.py)
- File System: generated_images/ directory + history.json
- Security: Input sanitization, content filtering
- Performance: Thread-safe, non-blocking UI during generation

---

## 🔗 Cross-Cutting Relationships

### Signal Architecture Summary
```
Total Signals Across 6 Systems: 20+

Dashboard Signals (3):
- send_message (str)
- page_changed (int)
- user_logged_in (str)

Panel Signals (8):
- message_sent (str) - UserChatPanel
- image_gen_requested () - ProactiveActionsPanel
- news_intelligence_requested ()
- intelligence_library_requested ()
- watch_tower_requested ()
- command_center_requested ()

Persona Panel Signals (2):
- personality_changed (dict)
- proactive_settings_changed (dict)

Image Generation Signals (2):
- generate_requested (str, str)
- finished (dict)
- progress (str)

Utils Signals (3):
- AsyncWorker.finished ()
- AsyncWorker.error (Exception)
- AsyncWorker.result (object)
```

### Common Patterns

#### Pattern 1: Upward Signal Propagation
```
Panel emits signal → Dashboard receives → Dashboard re-emits → Interface receives → Executes action
```

#### Pattern 2: Governance-Routed Updates
```
UI change → Handler validates → Desktop Adapter → Router → Governance → Core System → Persistence
```

#### Pattern 3: Async Operation
```
UI trigger → Create AsyncWorker → Connect signals → Start thread → Wait → Receive result/error → Update UI
```

#### Pattern 4: Input Validation
```
User input → sanitize_input(text, max_length) → validate_length(text, min, max) → Process or reject
```

---

## 📊 Component Hierarchy

```
LeatherBookInterface (Main Window)
├── Page 0: IntroInfoPage (Login)
├── Page 1: LeatherBookDashboard (Main UI)
│   ├── StatsPanel
│   ├── ProactiveActionsPanel
│   ├── UserChatPanel
│   ├── AIResponsePanel
│   └── AINeuralHead
│
└── Page 2: Feature Panels (Dynamically Added)
    ├── ImageGenerationInterface
    │   ├── ImageGenerationLeftPanel
    │   └── ImageGenerationRightPanel
    ├── NewsIntelligencePanel
    ├── IntelligenceLibraryPanel
    ├── WatchTowerPanel
    └── GodTierCommandPanel
```

---

## 🔐 Security Integration Points

### Input Validation (Used by 5/6 systems)
```python
from app.security.data_validation import (
    sanitize_input,      # XSS protection, HTML escaping
    validate_length,     # Min/max length constraints
    validate_email,      # Email format validation
)

# Pattern:
text = sanitize_input(user_input, max_length=2000)
if not validate_length(text, min_len=1, max_len=2000):
    show_error()
    return
```

### Content Filtering (Image Generation)
- 15 blocked keywords: nude, naked, violence, blood, gore, weapons, etc.
- Safety negative prompts automatically added
- Filter applied before API call

---

## 🎨 Styling System

### Tron Color Scheme (Consistent Across All Systems)
```python
TRON_GREEN = "#00ff00"   # Primary UI color
TRON_CYAN = "#00ffff"    # Accent/highlight color
TRON_BLACK = "#0a0a0a"   # Background
TRON_DARK = "#1a1a1a"    # Panel backgrounds
```

### Shared Stylesheets
- PANEL_STYLESHEET: Border-radius panels with green borders
- ACTION_BUTTON_STYLESHEET: Green buttons with cyan hover
- TITLE_FONT: Courier New, 12pt Bold

---

## 🧪 Testing Surface

### Unit Test Targets (Per System)
1. **Dashboard**: Signal emission, animation updates, message routing
2. **Panels**: Widget state changes, signal connections, input validation
3. **Handlers**: Governance routing, fallback behavior, error handling
4. **Utils**: Error handler methods, AsyncWorker success/error paths, thread safety
5. **Persona Panel**: Trait slider updates, Four Laws validation, proactive settings
6. **Image Generation**: Worker completion, panel communication, content filtering

### Integration Test Targets
- End-to-end message sending: Type → send → display
- Navigation flow: Dashboard → Feature panel → Back → Dashboard
- Personality update: Slider → governance → persistence
- Image generation: Prompt → worker → display

---

## 📈 Performance Metrics

### Timer Frequencies
- Dashboard animations: 50ms (20 FPS)
- Stats updates: 1000ms (1 Hz)
- Auto-refresh (various panels): 5000-30000ms

### Thread Pool Configuration
- Default: CPU core count
- Configurable via DashboardAsyncManager
- Cleanup: waitForDone(5000ms) on close

### Memory Management
- Panels created once, reused for session
- Feature panels created on-demand, destroyed on navigation
- Images: Original pixmap cached, single scaled version in memory

---

## 🔍 Debugging Checklist

### Signal Not Working?
1. Check connection: `signal.connect(slot)` called?
2. Verify slot signature matches signal signature
3. Check if signal emitter still exists (not destroyed)
4. Add debug print in slot to confirm call

### UI Not Updating?
1. Update called from main thread? (Use signals from worker threads)
2. Widget visible? (`isVisible()`, `show()`)
3. Parent layout properly configured? (`addWidget()`, `addLayout()`)
4. Stylesheet conflicting? (Check CSS specificity)

### Governance Routing Failed?
1. Check if Desktop Adapter available: `get_desktop_adapter [[src/app/interfaces/desktop/integration.py]]()`
2. Verify route exists in Router mapping
3. Check CognitionKernel running and initialized
4. Review logs for error messages
5. Use fallback to direct core system call

### Async Operation Stuck?
1. Check worker.start() called
2. Verify signals connected before start
3. Check for exceptions in worker.run() (logged)
4. Ensure QThreadPool has available threads
5. Test with smaller timeout to confirm blocking

---

## 📚 Cross-References

### Related Systems Documentation

#### Core AI Systems ([[../core-ai/00-INDEX|Core AI Index]])
- [[../core-ai/01-FourLaws-Relationship-Map|FourLaws System]] - Ethics validation for all GUI actions
- [[../core-ai/02-AIPersona-Relationship-Map|AIPersona System]] - Personality management via PersonaPanel
- [[../core-ai/03-MemoryExpansionSystem [[src/app/core/ai_systems.py]]-Relationship-Map|MemoryExpansionSystem]] - Conversation history in Dashboard
- [[../core-ai/04-LearningRequestManager [[src/app/core/ai_systems.py]]-Relationship-Map|LearningRequestManager]] - Learning approval workflow
- [[../core-ai/05-PluginManager [[src/app/core/ai_systems.py]]-Relationship-Map|PluginManager]] - Plugin management UI integration
- [[../core-ai/06-CommandOverride-Relationship-Map|CommandOverride System]] - Master password system

#### Agent Systems ([[../agents/README|Agents Overview]])
- [[../agents/AGENT_ORCHESTRATION|Agent Orchestration]] - CognitionKernel integration for handlers
- [[../agents/VALIDATION_CHAINS|Validation Chains]] - 4-layer validation (GUI → ValidatorAgent → Kernel)
- [[../agents/PLANNING_HIERARCHIES|Planning Hierarchies]] - Task decomposition for complex workflows

### Related Documentation

### Cross-References

- [[relationships/gui/01_DASHBOARD_RELATIONSHIPS.md|01 Dashboard Relationships]]
- [[relationships/gui/02_PANEL_RELATIONSHIPS.md|02 Panel Relationships]]
- [[relationships/gui/03_HANDLER_RELATIONSHIPS.md|03 Handler Relationships]]
- [[relationships/gui/04_UTILS_RELATIONSHIPS.md|04 Utils Relationships]]
- [[relationships/gui/05_PERSONA_PANEL_RELATIONSHIPS.md|05 Persona Panel Relationships]]
- [[relationships/gui/06_IMAGE_GENERATION_RELATIONSHIPS.md|06 Image Generation Relationships]]
- [[source-docs/gui/README.md|Readme]]
- **Architecture**: `.github/instructions/ARCHITECTURE_QUICK_REF.md`
- **Developer Guide**: `DEVELOPER_QUICK_REFERENCE.md`
- **Program Summary**: `PROGRAM_SUMMARY.md`
- **Desktop Quickstart**: `DESKTOP_APP_QUICKSTART.md`

### Core System Integration
- **AI Systems**: `src/app/core/ai_systems.py` ([[../core-ai/02-AIPersona-Relationship-Map|AIPersona]], [[../core-ai/01-FourLaws-Relationship-Map|FourLaws]])
- **Image Generator**: `src/app/core/image_generator.py` (ImageGenerator, ImageStyle)
- **User Manager**: `src/app/core/user_manager.py` (Authentication)
- **Data Validation**: `src/app/security/data_validation.py` (Sanitization → [[../agents/VALIDATION_CHAINS#layer-1-validatoragent-data-validation|ValidatorAgent]])

### Governance Integration
- **Desktop Adapter**: `src/app/interfaces/desktop/integration.py` ([[../agents/AGENT_ORCHESTRATION#councilhub-coordination|CouncilHub Integration]])
- **Router**: `src/app/governance/router.py` ([[../agents/AGENT_ORCHESTRATION#governance-integration|Governance Flow]])
- **Cognition Kernel**: `src/app/core/cognition_kernel.py` ([[../agents/AGENT_ORCHESTRATION#centralized-kernel-architecture|Kernel Architecture]])

---

## 🎯 Quick Lookup

### Find Signal Definitions
```bash
grep -r "pyqtSignal" src/app/gui/*.py
```

### Find Signal Connections
```bash
grep -r "\.connect\(" src/app/gui/*.py
```

### Find Handler Methods
```bash
grep -r "def.*_handler\|def.*_on_" src/app/gui/*.py
```

### Find Validation Calls
```bash
grep -r "sanitize_input\|validate_length" src/app/gui/*.py
```

---

## 📝 Maintenance Notes

### When Adding New Panels
1. Create panel class inheriting QWidget or QFrame
2. Define signals for outward communication
3. Connect signals in parent (Dashboard or Interface)
4. Add navigation button in ProactiveActionsPanel
5. Implement switch_to_*() method in Interface
6. Add back_requested signal and connection
7. Update this index with new panel documentation

### When Modifying Signals
1. Update signal definition in class
2. Update all .connect() calls
3. Update signal chain documentation in relevant map
4. Update unit tests for signal emission
5. Update integration tests for signal propagation

### When Changing Governance Routes
1. Update handler method to use new route
2. Update adapter.execute() call
3. Update Router mapping in governance layer
4. Update handler documentation map
5. Test fallback behavior

---

## 📌 Key Insights

### Design Principles Across All Systems
1. **Isolation**: Components don't directly reference siblings
2. **Signal-Based**: All communication via signals/slots
3. **Governance-Routed**: Core system updates via adapter
4. **Security-First**: All input validated and sanitized
5. **Async-Ready**: Long operations use QThread/AsyncWorker
6. **Consistent Styling**: Tron theme across all panels
7. **Error Handling**: 4-layer approach (validation → governance → fallback → feedback)

### Most Complex Relationships
1. **Dashboard ↔ Interface**: 5 navigation signals + message routing
2. **Persona Panel ↔ AIPersona**: 8 trait updates via governance
3. **Image Generation**: 3-class async coordination (Worker + 2 Panels)
4. **Handlers**: Dual-path execution (governance + fallback)

### Most Critical Paths
1. **User message sending** (Dashboard → Interface → Intelligence)
2. **Navigation to feature panels** (ProactiveActions → Interface)
3. **Personality trait updates** (PersonaPanel → Governance → AIPersona)
4. **Image generation** (LeftPanel → Worker → RightPanel)

---

## 🔗 Related Systems Integration Map

### GUI → Core AI System Connections

| GUI Component | Core AI System | Integration Point | Documentation |
|--------------|----------------|-------------------|---------------|
| **PersonaPanel** [[src/app/gui/persona_panel.py]] | [[../core-ai/02-AIPersona-Relationship-Map\|AIPersona]] | Personality trait sliders → persona state | Section 5 of PersonaPanel doc |
| **PersonaPanel** | [[../core-ai/01-FourLaws-Relationship-Map\|FourLaws]] | Read-only Four Laws display | Section 2 of PersonaPanel doc |
| **Dashboard** | [[../core-ai/03-MemoryExpansionSystem-Relationship-Map\|Memory]] | Conversation logging & knowledge | Section 3 of Dashboard doc |
| **ImageGeneration** | [[../core-ai/06-CommandOverride-Relationship-Map\|Override]] | Content filter bypass (admin only) | Section 4 of ImageGen doc |
| **DashboardHandlers** [[src/app/gui/dashboard_handlers.py]] | [[../core-ai/04-LearningRequestManager-Relationship-Map\|Learning]] | Learning path generation | Section 3 of Handlers doc |
| **All Panels** | [[../core-ai/05-PluginManager-Relationship-Map\|Plugins]] | Plugin UI integration (future) | N/A (planned) |

### GUI → Agent System Connections

| GUI Component | Agent System | Integration Point | Documentation |
|--------------|--------------|-------------------|---------------|
| **DashboardHandlers** | [[../agents/AGENT_ORCHESTRATION\|CognitionKernel]] | All handlers route via kernel | Section 3 of Handlers doc |
| **All Input Fields** | [[../agents/VALIDATION_CHAINS\|ValidatorAgent]] | Input sanitization & validation | Section 4 of Utils doc |
| **PersonaPanel** | [[../agents/VALIDATION_CHAINS#layer-3-cognitionkernel-four-laws-validation\|Four Laws Validation]] | Trait update validation | Section 5 of PersonaPanel doc |
| **DashboardHandlers** | [[../agents/PLANNING_HIERARCHIES\|PlannerAgent]] | Complex task decomposition (future) | N/A (planned) |

### Cross-Cutting Concerns

**Governance Pipeline Flow:**
```
GUI Action → Desktop Adapter → [[../agents/AGENT_ORCHESTRATION#governance-integration|Router]] → 
[[../agents/VALIDATION_CHAINS|Validation Chain]] → [[../core-ai/01-FourLaws-Relationship-Map|Four Laws]] → 
Core System → Response → GUI Update
```

**Validation Chain:**
```
User Input → [[../agents/VALIDATION_CHAINS#layer-1-validatoragent-data-validation|ValidatorAgent]] (Data) → 
[[../agents/VALIDATION_CHAINS#layer-2-oversightagent-compliance-validation|OversightAgent]] (Compliance) → 
[[../agents/VALIDATION_CHAINS#layer-3-cognitionkernel-four-laws-validation|CognitionKernel]] (Ethics) → 
[[../agents/VALIDATION_CHAINS#layer-4-cognitionkernel-triumvirate-validation|Triumvirate]] (Consensus) → Execute
```

---

## ✅ Completion Checklist

- [x] 01_DASHBOARD_RELATIONSHIPS.md (17KB, 500+ lines)
- [x] 02_PANEL_RELATIONSHIPS.md (21KB, 600+ lines)
- [x] 03_HANDLER_RELATIONSHIPS.md (20KB, 550+ lines)
- [x] 04_UTILS_RELATIONSHIPS.md (22KB, 600+ lines)
- [x] 05_PERSONA_PANEL_RELATIONSHIPS.md (22KB, 650+ lines)
- [x] 06_IMAGE_GENERATION_RELATIONSHIPS.md (26KB, 700+ lines)
- [x] 00_MASTER_INDEX.md (This file)

**Total Documentation:** ~130KB, 3600+ lines covering 6 GUI systems

---

**Generated by:** AGENT-056: GUI Relationship Mapping Specialist  
**Date:** 2026-04-20  
**Working Directory:** T:\Project-AI-main  
**Status:** ✅ MISSION COMPLETE
