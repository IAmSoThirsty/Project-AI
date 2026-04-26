# GUI Systems - Component Hierarchy & Architecture

**Document Type:** Visual Architecture Reference  
**Created:** 2025-01-20 by AGENT-032  
**Purpose:** Complete UI component hierarchy, signal flows, and architectural diagrams

---

## 1. Complete GUI Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        QApplication (main.py)                            │
│                                 ▲                                        │
│                                 │                                        │
│                       Creates and manages                                │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   LeatherBookInterface (QMainWindow)                     │
│  Main window container - 659 lines                                      │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ Central Widget: QWidget                                            │ │
│  │  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │  │ Main Layout: QHBoxLayout (Horizontal: Left + Right)          │  │ │
│  │  │                                                               │  │ │
│  │  │  ┌──────────────────┬────────────────────────────────────┐  │  │ │
│  │  │  │ LEFT (40%)       │ RIGHT (60%)                        │  │  │ │
│  │  │  │ TronFacePage     │ QStackedWidget (Dynamic Pages)     │  │  │ │
│  │  │  │ (Fixed)          │                                    │  │  │ │
│  │  │  │                  │  Page 0: IntroInfoPage (Login)     │  │  │ │
│  │  │  │                  │  Page 1: LeatherBookDashboard ─────┼──┼──┼─┐
│  │  │  │                  │  Page 2: ImageGenerationInterface ─┼──┼──┼─┼─┐
│  │  │  │                  │  Page 3: NewsIntelligencePanel     │  │  │ │ │
│  │  │  │                  │  Page 4: IntelligenceLibraryPanel  │  │  │ │ │
│  │  │  │                  │  Page 5: WatchTowerPanel           │  │  │ │ │
│  │  │  │                  │  Page 6: GodTierCommandPanel       │  │  │ │ │
│  │  │  └──────────────────┴────────────────────────────────────┘  │  │ │
│  │  └─────────────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
             │                                       │
             │                                       │
┌────────────▼──────────────────┐    ┌──────────────▼─────────────────────┐
│ TronFacePage (Fixed Left)     │    │ LeatherBookDashboard (Page 1)      │
│ - Digital face animation      │    │ 6-zone layout - 608 lines          │
│ - Tron grid background        │    │                                    │
│ - No user interaction         │    │ ┌──────────────────────────────┐  │
└───────────────────────────────┘    │ │ QVBoxLayout (Vertical)       │  │
                                     │ │                              │  │
                                     │ │  ┌────────────────────────┐  │  │
                                     │ │  │ Top: QHBoxLayout       │  │  │
                                     │ │  │  ┌──────┬──────────┐   │  │  │
                                     │ │  │  │Stats │ Proactive│   │  │  │
                                     │ │  │  │Panel │  Actions │   │  │  │
                                     │ │  │  └──┬───┴────┬─────┘   │  │  │
                                     │ │  └─────┼────────┼─────────┘  │  │
                                     │ │        │        │            │  │
                                     │ │  ┌─────▼────────▼─────────┐  │  │
                                     │ │  │ Middle: QHBoxLayout     │  │  │
                                     │ │  │  ┌──────┬──────┬──────┐│  │  │
                                     │ │  │  │User  │  AI  │ AI   ││  │  │
                                     │ │  │  │Chat  │ Head │Resp. ││  │  │
                                     │ │  │  └──┬───┴──┬───┴──┬───┘│  │  │
                                     │ │  └─────┼──────┼──────┼────┘  │  │
                                     │ └────────┼──────┼──────┼───────┘  │
                                     └──────────┼──────┼──────┼──────────┘
                                                │      │      │
              ┌─────────────────────────────────┼──────┼──────┼───────────┐
              │                                 │      │      │           │
         ┌────▼────────┐   ┌───────────────────▼──┐  ┌▼──────▼────┐   ┌─▼───────────┐
         │ StatsPanel  │   │ ProactiveActionsPanel│  │AINeuralHead│   │AIResponsePnl│
         │ (QFrame)    │   │ (QFrame)             │  │(QFrame)    │   │(QFrame)     │
         │             │   │                      │  │            │   │             │
         │ - User      │   │ - Action list scroll │  │- AIFaceCanv│   │- Convo log  │
         │ - Uptime    │   │ - 8 action buttons   │  │- Status    │   │- User msgs  │
         │ - Memory    │   │ - 5 feature signals  │  │- Thinking  │   │- AI resps   │
         │ - CPU       │   │                      │  │  animation │   │             │
         │ - Session   │   └──────────────────────┘  └────────────┘   └─────────────┘
         │             │
         │ QTimer(1s)  │
         └─────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ ImageGenerationInterface (Page 2) - 450 lines                           │
│ ┌───────────────────────────────────────────────────────────────────┐  │
│ │ QHBoxLayout (Horizontal: Left Control + Right Display)            │  │
│ │  ┌──────────────────────────┬────────────────────────────────┐   │  │
│ │  │ ImageGenerationLeftPanel │ ImageGenerationRightPanel      │   │  │
│ │  │ (QFrame) Tron Theme      │ (QFrame) Display               │   │  │
│ │  │                          │                                │   │  │
│ │  │ - Title                  │ - Title                        │   │  │
│ │  │ - Prompt input (QTextEdit)│ - QScrollArea                 │   │  │
│ │  │ - Style selector (QComboBox)│  └─> Image QLabel          │   │  │
│ │  │ - Backend selector (QComboBox)│ - Metadata label         │   │  │
│ │  │ - Generate button        │ - Action buttons (Save/Copy)   │   │  │
│ │  │ - Status label           │                                │   │  │
│ │  │ - History button         │ States:                        │   │  │
│ │  │ - Content warning        │  • Idle (placeholder)          │   │  │
│ │  │                          │  • Generating (progress)       │   │  │
│ │  │ Signal:                  │  • Success (image displayed)   │   │  │
│ │  │  generate_requested      │  • Error (error message)       │   │  │
│ │  └──────────────────────────┴────────────────────────────────┘   │  │
│ └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│ Background Worker:                                                      │
│ ┌────────────────────────────────────────────────────────────────┐    │
│ │ ImageGenerationWorker (QThread)                                 │    │
│ │ - generator: ImageGenerator                                     │    │
│ │ - prompt: str                                                   │    │
│ │ - style: ImageStyle                                             │    │
│ │                                                                 │    │
│ │ Signals:                                                        │    │
│ │  • finished(dict) - Result with filepath or error               │    │
│ │  • progress(str) - Status updates                               │    │
│ └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ PersonaPanel (Embedded in Dashboard) - 433 lines                        │
│ ┌───────────────────────────────────────────────────────────────────┐  │
│ │ QTabWidget (4 tabs)                                               │  │
│ │  ┌──────┬──────────┬───────────┬────────────┐                    │  │
│ │  │ Tab 0│  Tab 1   │   Tab 2   │   Tab 3    │                    │  │
│ │  │ Four │Personal- │ Proactive │ Statistics │                    │  │
│ │  │ Laws │   ity    │           │            │                    │  │
│ │  └──┬───┴────┬─────┴─────┬─────┴──────┬─────┘                    │  │
│ │     │        │           │            │                          │  │
│ │  ┌──▼──────┐ ┌──▼────────┐ ┌─▼────────┐ ┌─▼──────────┐          │  │
│ │  │Four Laws│ │Personality│ │Proactive │ │Statistics  │          │  │
│ │  │Tab      │ │Tab        │ │Tab       │ │Tab         │          │  │
│ │  │         │ │           │ │          │ │            │          │  │
│ │  │- Laws   │ │- 8 sliders│ │- Enable  │ │- Traits    │          │  │
│ │  │  display│ │  QSlider  │ │  checkbox│ │  display   │          │  │
│ │  │- Action │ │  (0-100)  │ │- Quiet   │ │- Mood      │          │  │
│ │  │  input  │ │           │ │  hours   │ │  status    │          │  │
│ │  │- Context│ │- Reset btn│ │- Min idle│ │- Convo     │          │  │
│ │  │  checks │ │           │ │  spin    │ │  stats     │          │  │
│ │  │- Validate││Signal:    │ │- Prob    │ │- Refresh   │          │  │
│ │  │  button │ │ personality│ │  spin    │ │  button    │          │  │
│ │  │- Result │ │  _changed │ │          │ │            │          │  │
│ │  │  display│ │           │ │Signal:   │ │            │          │  │
│ │  └─────────┘ └───────────┘ │ proactive│ └────────────┘          │  │
│ │                            │  _settings│                         │  │
│ │                            │   _changed│                         │  │
│ │                            └───────────┘                         │  │
│ └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Signal/Slot Connection Map

### Global Signal Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Signal Flow Hierarchy                               │
│  (Arrows show signal direction: source → destination)                   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ LEVEL 1: Main Window Signals (LeatherBookInterface)                     │
└─────────────────────────────────────────────────────────────────────────┘

LeatherBookInterface
    ├─> page_changed(int) ─────────────────────> [External page listeners]
    └─> user_logged_in(str) ───────────────────> [External auth systems]

IntroInfoPage
    └─> login_success(str) ────────────────────> LeatherBookInterface.switch_to_main_dashboard()

┌─────────────────────────────────────────────────────────────────────────┐
│ LEVEL 2: Dashboard Signals (LeatherBookDashboard)                       │
└─────────────────────────────────────────────────────────────────────────┘

LeatherBookDashboard
    └─> send_message(str) ─────────────────────> [External AI systems]

ProactiveActionsPanel (5 feature navigation signals)
    ├─> image_gen_requested() ─────────────────> LeatherBookInterface.switch_to_image_generation()
    ├─> news_intelligence_requested() ─────────> LeatherBookInterface.switch_to_news_intelligence()
    ├─> intelligence_library_requested() ──────> LeatherBookInterface.switch_to_intelligence_library()
    ├─> watch_tower_requested() ───────────────> LeatherBookInterface.switch_to_watch_tower()
    └─> command_center_requested() ────────────> LeatherBookInterface.switch_to_command_center()

UserChatPanel
    └─> message_sent(str) ─────────────────────> LeatherBookDashboard._on_user_message()
            │
            ├─> ai_head.start_thinking() ──────> [Animation state change]
            ├─> ai_response.add_user_message()  > [Update conversation log]
            └─> send_message.emit() ───────────> [Re-emit to external]

┌─────────────────────────────────────────────────────────────────────────┐
│ LEVEL 3: Feature Panel Signals                                          │
└─────────────────────────────────────────────────────────────────────────┘

ImageGenerationLeftPanel
    └─> generate_requested(str, str) ──────────> ImageGenerationInterface._start_generation()

ImageGenerationWorker (QThread)
    ├─> progress(str) ─────────────────────────> ImageGenerationLeftPanel.set_status()
    └─> finished(dict) ────────────────────────> ImageGenerationInterface._on_generation_complete()
            │
            ├─> left_panel.set_generating(False)
            ├─> right_panel.display_image() ───> [Success: show image]
            └─> right_panel.show_error() ──────> [Failure: show error]

PersonaPanel
    ├─> personality_changed(dict) ─────────────> [External persona systems]
    └─> proactive_settings_changed(dict) ──────> [External conversation manager]

┌─────────────────────────────────────────────────────────────────────────┐
│ LEVEL 4: Utility Signals (AsyncWorker)                                  │
└─────────────────────────────────────────────────────────────────────────┘

AsyncWorker.Signals (QObject)
    ├─> result(object) ────────────────────────> [User-defined on_result callback]
    ├─> error(Exception) ──────────────────────> [User-defined on_error callback]
    └─> finished() ────────────────────────────> [Cleanup: remove from active_tasks]
```

### Signal Connection Table

| Source Component | Signal | Parameters | Destination | Handler Method |
|------------------|--------|------------|-------------|----------------|
| **LeatherBookInterface** | | | | |
| IntroInfoPage | `login_success` | `str` (username) | LeatherBookInterface | `switch_to_main_dashboard()` |
| LeatherBookInterface | `user_logged_in` | `str` (username) | External | N/A |
| LeatherBookInterface | `page_changed` | `int` (page_index) | External | N/A |
| **LeatherBookDashboard** | | | | |
| UserChatPanel | `message_sent` | `str` (message) | LeatherBookDashboard | `_on_user_message()` |
| LeatherBookDashboard | `send_message` | `str` (message) | External AI System | N/A |
| ProactiveActionsPanel | `image_gen_requested` | None | LeatherBookInterface | `switch_to_image_generation()` |
| ProactiveActionsPanel | `news_intelligence_requested` | None | LeatherBookInterface | `switch_to_news_intelligence()` |
| ProactiveActionsPanel | `intelligence_library_requested` | None | LeatherBookInterface | `switch_to_intelligence_library()` |
| ProactiveActionsPanel | `watch_tower_requested` | None | LeatherBookInterface | `switch_to_watch_tower()` |
| ProactiveActionsPanel | `command_center_requested` | None | LeatherBookInterface | `switch_to_command_center()` |
| **ImageGenerationInterface** | | | | |
| ImageGenerationLeftPanel | `generate_requested` | `str, str` (prompt, style) | ImageGenerationInterface | `_start_generation()` |
| ImageGenerationWorker | `progress` | `str` (status) | ImageGenerationLeftPanel | `set_status()` |
| ImageGenerationWorker | `finished` | `dict` (result) | ImageGenerationInterface | `_on_generation_complete()` |
| **PersonaPanel** | | | | |
| PersonaPanel | `personality_changed` | `dict` | External | N/A |
| PersonaPanel | `proactive_settings_changed` | `dict` | External | N/A |
| Trait Slider | `valueChanged` | `int` | PersonaPanel | `update_value()` (closure) |
| **Utility Signals** | | | | |
| AsyncWorker | `result` | `object` | User callback | User-defined |
| AsyncWorker | `error` | `Exception` | User callback | User-defined |
| AsyncWorker | `finished` | None | DashboardAsyncManager | `on_finished()` (cleanup) |

---

## 3. Event Handling Flow Diagrams

### User Login Flow

```
┌───────────┐
│User enters│
│credentials│
│in IntroInfo│
│Page       │
└─────┬─────┘
      │
      ▼
┌─────────────────────┐
│Login button clicked │
│Validate credentials │
└─────────┬───────────┘
          │
          ▼
     ┌─────────┐
     │ Valid?  │
     └────┬────┘
      Yes │  No
      ┌───▼──┐ │
      │Emit  │ │
      │login_│ │
      │success│ │
      │signal│ │
      └───┬──┘ │
          │    │
          ▼    ▼
     ┌────────────────┐
     │LeatherBook     │
     │Interface.switch│
     │_to_main_       │
     │dashboard()     │
     └────┬───────────┘
          │
          ├─> Set username
          ├─> Emit user_logged_in
          ├─> Create dashboard
          ├─> Connect signals
          └─> _set_stack_page(1)
```

### Image Generation Flow

```
┌───────────┐
│User enters│
│prompt in  │
│left panel │
└─────┬─────┘
      │
      ▼
┌─────────────────────┐
│Generate btn clicked │
│Sanitize & validate  │
└─────────┬───────────┘
          │
          ▼
     ┌─────────┐
     │ Valid?  │
     └────┬────┘
      Yes │  No
      ┌───▼──┐ │
      │Emit  │ │
      │generate│ │
      │_requested│ │
      │signal│ │
      └───┬──┘ │
          │    │
          ▼    ▼
     ┌────────────────┐
     │ImageGeneration │
     │Interface._start│
     │_generation()   │
     └────┬───────────┘
          │
          ├─> Disable inputs
          ├─> Show "Generating..."
          ├─> Create worker thread
          └─> Start worker
                │
                ▼
          ┌─────────────────┐
          │Worker.run()     │
          │(Background)     │
          │                 │
          │1. Check filter  │
          │2. Call generator│
          │3. Save image    │
          │4. Emit finished │
          └────┬────────────┘
               │
               ▼
          ┌─────────────────┐
          │_on_generation_  │
          │complete()       │
          │                 │
          │Success?         │
          └────┬────────────┘
           Yes │  No
          ┌────▼───┐ ┌──────▼─────┐
          │Display │ │Show error  │
          │image   │ │message     │
          └────────┘ └────────────┘
```

### Dashboard Message Flow

```
┌───────────┐
│User types │
│message in │
│chat input │
└─────┬─────┘
      │
      ▼
┌─────────────────────┐
│Send button clicked  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│UserChatPanel        │
│._send_message()     │
│                     │
│1. Get text          │
│2. Emit message_sent │
│3. Clear input       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│Dashboard._on_user_  │
│message()            │
│                     │
│1. Re-emit send_msg  │
│2. ai_head.start_    │
│   thinking()        │
│3. ai_response.add_  │
│   user_message()    │
└─────────┬───────────┘
          │
          ├────────────────┐
          │                │
          ▼                ▼
┌──────────────────┐ ┌───────────────────┐
│AINeuralHead      │ │External AI system │
│Animation state:  │ │processes message  │
│is_thinking=True  │ │                   │
│Status: THINKING..│ │Returns response   │
└──────────────────┘ └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │Dashboard.add_ai_  │
                     │response()         │
                     │                   │
                     │1. ai_response.add_│
                     │   ai_response()   │
                     │2. ai_head.stop_   │
                     │   thinking()      │
                     └───────────────────┘
```

---

## 4. Tier Integration Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PLATFORM TIER ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 3: USER INTERFACE (Sandboxed, Replaceable)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  LeatherBookInterface ────┐                                             │
│  LeatherBookDashboard     ├──> Registered as Tier-3 components          │
│  PersonaPanel             │                                              │
│  ImageGenerationInterface │    Authority: SANDBOXED                      │
│                           └──> Can be paused/replaced by Tier-1          │
│                                                                          │
│  All GUI operations routed through:                                     │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │ DesktopAdapter.execute(action, params)                         │     │
│  └────────────────────────────┬──────────────────────────────────┘     │
│                               │                                         │
└───────────────────────────────┼─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ INTERFACE LAYER: Desktop Adapter                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  DesktopAdapter                                                          │
│    ├─> Translates GUI actions to governance requests                    │
│    └─> Returns standardized responses                                   │
│                                                                          │
│  Example:                                                               │
│    adapter.execute("learning.generate_path", {...})                     │
│         │                                                               │
│         └─> Returns: {"status": "success", "result": {...}}             │
│                                                                          │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 1: GOVERNANCE (Root Authority)                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CognitionKernel ────────┐                                              │
│  CouncilHub              ├──> Permission checks                          │
│  Router                  │    Audit logging                             │
│                          │    Rate limiting                             │
│                          └──> Context injection                          │
│                                                                          │
│  Validates all Tier-3 requests before forwarding to Tier-2               │
│                                                                          │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 2: BUSINESS LOGIC                                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  AIPersona                   ┐                                          │
│  LearningRequestManager      │                                          │
│  DataAnalyzer                ├──> Core systems                           │
│  SecurityResources           │    Execute business logic                │
│  ImageGenerator              │                                          │
│  LocationTracker             │                                          │
│  EmergencyAlert              ┘                                          │
│                                                                          │
│  Returns results to Tier-1 → Adapter → GUI                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Cross-Reference Index

| Document | Key Content |
|----------|-------------|
| `leather_book_interface.md` | Main window, page navigation, QStackedWidget |
| `leather_book_dashboard.md` | 6-zone layout, stats, AI head, chat panels |
| `persona_panel.md` | 4-tab configuration, personality sliders, Four Laws |
| `dashboard_handlers.md` | Governance-routed event handlers, fallback patterns |
| `dashboard_utils.md` | Error handling, async workers, validation utilities |
| `image_generation.md` | Dual-panel image gen, worker threads, content filtering |

---

**Document Status:** ✅ Complete  
**Purpose:** Visual reference for GUI architecture  
**Last Updated:** 2025-01-20 by AGENT-032
