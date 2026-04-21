---
type: deployment-guide
tags: [deployment, desktop, gui, pyqt6, installation, shortcuts, windows, quickstart]
created: 2025-11-01
last_verified: 2026-04-20
status: current
related_systems: [desktop-app, leather-book-ui, command-override, memory-expansion]
stakeholders: [developers, new-users, operators, deployment-team]
audience: beginner
prerequisites: [windows-7+, python-3.11+, 4gb-ram, git]
estimated_time: 10 minutes
review_cycle: monthly
deployment_target: desktop
deployment_complexity: simple
production_ready: true
platform_support: [windows]
automation: [batch-scripts, powershell-scripts]
related_to:
  - "[[README]]"
  - "[[DEVELOPER_QUICK_REFERENCE]]"
  - "[[ARCHITECTURE_QUICK_REF]]"
  - "[[PROGRAM_SUMMARY]]"
  - "[[AGENT-084-LEARNING-PATHS]]"
---

# 🚀 Project-AI Desktop Application - Quick Start Guide

Get the desktop application running in 10 minutes. For comprehensive architecture details, see [[PROGRAM_SUMMARY]].

---

## Installation Steps

### Step 1: One-Click Setup

**Double-click `setup-desktop.bat`**

This will:
✓ Check for Python 3.11+  
✓ Create virtual environment  
✓ Install all dependencies  
✓ Launch the application  

**Learn More**:
- Environment setup: [[DEVELOPER_QUICK_REFERENCE]] → Environment Setup
- Deployment workflows: [[PROGRAM_SUMMARY]] → Deployment Workflows
- Production deployment: [[INFRASTRUCTURE_PRODUCTION_GUIDE]]

---

### Step 2: (Optional) Create Desktop Shortcuts

After first successful launch, run:

```powershell
python install-shortcuts.py
```

This creates:

- Desktop shortcut for quick access
- Start Menu entry

---

## Quick Launch Methods

| Method | Steps | Learn More |
|--------|-------|------------|
| **Batch Script** | Double-click `launch-desktop.bat` | [[DEVELOPER_QUICK_REFERENCE]] |
| **PowerShell** | Right-click `launch-desktop.ps1` → Run with PowerShell | [[DEVELOPER_QUICK_REFERENCE]] |
| **Desktop Shortcut** | Double-click shortcut (after running install-shortcuts.py) | - |
| **Start Menu** | Search "Project-AI" (after running install-shortcuts.py) | - |
| **Manual** | `python -m src.app.main` | [[COPILOT_MANDATORY_GUIDE]] → Module Imports |

---

## System Requirements

✓ Windows 7+  
✓ Python 3.11+  
✓ 4GB RAM (8GB recommended)  
✓ 500MB disk space  

**Learn More**: [[PROGRAM_SUMMARY]] → System Requirements

---

## Features at a Glance

### 🔐 Command Override

- Master password protection
- Control 10 safety protocols
- Audit logging
- Emergency lockdown

**API Reference**: [[API_QUICK_REFERENCE#core/command_override.py|CommandOverrideSystem]] - Master password and safety protocol management

**Learn More**:
- Implementation details: [[PROGRAM_SUMMARY]] → CommandOverrideSystem
- Security architecture: [[ARCHITECTURE_QUICK_REF]] → Security Layers
- Password security: [[COPILOT_MANDATORY_GUIDE]] → Password Security

---

### 🧠 Memory Expansion

- Persistent AI memory
- Autonomous learning
- Knowledge base building
- Semantic search

**API Reference**: [[API_QUICK_REFERENCE#core/ai_systems.py|MemoryExpansionSystem]] - Conversation logging and knowledge base management

**Learn More**:
- Complete implementation: [[PROGRAM_SUMMARY]] → MemoryExpansionSystem
- Data persistence: [[ARCHITECTURE_QUICK_REF]] → State Persistence
- Knowledge base structure: [[PROGRAM_SUMMARY]] → Data Persistence

---

### 🎓 Learning Request System

- Human-in-the-loop approval
- Black Vault for denied content
- SHA-256 fingerprinting
- Subliminal filtering

**API Reference**: [[API_QUICK_REFERENCE#core/ai_systems.py|LearningRequestManager]] - Learning request workflow and Black Vault management

**Learn More**:
- Complete guide: [[LEARNING_REQUEST_IMPLEMENTATION]]
- Black Vault details: [[LEARNING_REQUEST_IMPLEMENTATION]] → Black Vault section
- Workflow diagram: [[ARCHITECTURE_QUICK_REF]] → Learning Request Workflow

---

### 🤖 AI Persona & Ethics

- 8 personality traits
- Four Laws ethical framework
- Mood tracking
- Proactive conversation

**API Reference**: 
- [[API_QUICK_REFERENCE#core/ai_systems.py|AIPersona]] - Personality trait management and mood tracking
- [[API_QUICK_REFERENCE#core/ai_systems.py|FourLaws]] - Ethical validation framework

**Learn More**:
- Complete guide: [[AI_PERSONA_IMPLEMENTATION]]
- Four Laws validation: [[AI_PERSONA_IMPLEMENTATION]] → Four Laws section
- Ethics framework: [[ARCHITECTURE_QUICK_REF]] → Security Layers

---

### 📊 Additional Features

- **Data Analysis**: CSV/XLSX/JSON analysis, K-means clustering ([[API_QUICK_REFERENCE#core/data_analysis.py|DataAnalyzer]])
- **Security Resources**: GitHub API integration, CTF repos ([[API_QUICK_REFERENCE#core/security_resources.py|SecurityResourceFetcher]])
- **Location Tracking**: IP geolocation, encrypted history ([[API_QUICK_REFERENCE#core/location_tracker.py|LocationTracker]])
- **Emergency Alerts**: Contact system with email alerts ([[API_QUICK_REFERENCE#core/emergency_alert.py|EmergencyAlert]])
- **Image Generation**: HuggingFace Stable Diffusion, OpenAI DALL-E ([[API_QUICK_REFERENCE#core/image_generator.py|ImageGenerator]])

**Learn More**:
- Data analysis: [[PROGRAM_SUMMARY]] → Data Analysis Module
- Security resources: [[PROGRAM_SUMMARY]] → Security Resources Module
- Image generation: [[PROGRAM_SUMMARY]] → Image Generation System
- All features: [[PROGRAM_SUMMARY]]

---

## Troubleshooting

| Problem | Solution | Learn More |
|---------|----------|------------|
| "Python not found" | Install Python from python.org | [[DEVELOPER_QUICK_REFERENCE]] → Environment Setup |
| App won't start | Run setup-desktop.bat again | [[DEVELOPER_QUICK_REFERENCE]] → Troubleshooting |
| Shortcuts won't create | Run as Administrator | - |
| Import errors | Use `python -m src.app.main` not `python src/app/main.py` | [[COPILOT_MANDATORY_GUIDE]] → Module Imports |
| Persistence fails | Ensure `data/` directory exists | [[COPILOT_MANDATORY_GUIDE]] → Critical Gotchas |
| GUI freezes | Check for threading issues | [[COPILOT_MANDATORY_GUIDE]] → PyQt6 threading |

---

## Important Files

| File | Purpose | Learn More |
|------|---------|------------|
| `launch-desktop.bat` | Quick application launch | [[DEVELOPER_QUICK_REFERENCE]] |
| `setup-desktop.bat` | Full environment setup | [[DEVELOPER_QUICK_REFERENCE]] → Environment Setup |
| `install-shortcuts.py` | Create desktop shortcuts | - |
| `app-config.json` | Configuration settings | [[PROGRAM_SUMMARY]] → Configuration Management |
| `.env` | Environment variables (API keys) | [[DEVELOPER_QUICK_REFERENCE]] → Environment Setup |

---

## Next Steps

### For End Users

1. ✅ **You're done!** - Application is running
1. 📖 Explore features through the GUI
1. 🎨 Try image generation: Click "🎨 GENERATE IMAGES"
1. 🤖 Configure AI personality: Open "AI Persona" panel
1. 📚 Review learning requests: Check "Learning Requests" tab

**Learn More**: [[PROGRAM_SUMMARY]] → GUI Architecture

---

### For Developers

1. ✅ Application running
1. 📖 Read architecture: [[ARCHITECTURE_QUICK_REF]] (30 min)
1. 💻 Review commands: [[DEVELOPER_QUICK_REFERENCE]] (15 min)
1. 🔍 Deep-dive: [[COPILOT_MANDATORY_GUIDE]] (60 min)
1. 🏗️ Complete details: [[PROGRAM_SUMMARY]] (2+ hours)

**Navigation**: See [[AGENT-084-LEARNING-PATHS]] for complete learning paths

---

## Need Help?

📖 **Quick Reference**: [[DEVELOPER_QUICK_REFERENCE]]  
🏗️ **Architecture**: [[ARCHITECTURE_QUICK_REF]]  
📚 **Complete Docs**: [[PROGRAM_SUMMARY]]  
🎓 **Learning Paths**: [[AGENT-084-LEARNING-PATHS]]  
🐛 **Issues**: GitHub Issues page  
🔒 **Security**: [[SECURITY]]  
💬 **Contributing**: [[CONTRIBUTING]]  

---

**Version**: 1.0.1  
**Status**: Production Ready ✓  
**Last Updated**: 2026-04-20

---

## API Reference

This section provides direct links to the API documentation for modules used in the desktop application.

### Core AI Systems

Located in `src/app/core/ai_systems.py` - Six AI systems framework:

- **[[API_QUICK_REFERENCE#core/ai_systems.py|FourLaws]]** - Ethical validation framework
  - `validate_action(action, context)` - Check if action aligns with Four Laws
  - `get_hierarchy()` - Get law priority hierarchy
  - Validates all AI actions before execution

- **[[API_QUICK_REFERENCE#core/ai_systems.py|AIPersona]]** - Personality management system
  - `update_trait(trait, value)` - Modify personality trait (0.0-1.0)
  - `get_mood()` - Get current emotional state
  - `_save_state()` - Persist personality to `data/ai_persona/state.json`
  - Manages 8 personality traits: curiosity, empathy, humor, formality, patience, creativity, assertiveness, optimism

- **[[API_QUICK_REFERENCE#core/ai_systems.py|MemoryExpansionSystem]]** - Conversation and knowledge management
  - `add_memory(content, category)` - Store knowledge (6 categories)
  - `search_memory(query)` - Semantic search knowledge base
  - `log_conversation(user, ai)` - Log conversation turns
  - Persists to `data/memory/knowledge.json`

- **[[API_QUICK_REFERENCE#core/ai_systems.py|LearningRequestManager]]** - Human-in-the-loop learning approval
  - `request_learning(content, source)` - Submit learning request
  - `approve_request(request_id)` - Approve learning
  - `deny_request(request_id)` - Deny and add to Black Vault
  - Black Vault uses SHA-256 fingerprinting
  - Persists to `data/learning_requests/requests.json`

- **[[API_QUICK_REFERENCE#core/ai_systems.py|CommandOverride]]** - Basic override system (see also `command_override.py`)
  - `check_override(password)` - Validate override password (SHA-256)
  - `enable_override()` / `disable_override()` - Toggle override state
  - `audit_log(action)` - Log override actions

- **[[API_QUICK_REFERENCE#core/ai_systems.py|PluginManager]]** - Plugin system
  - `load_plugin(name)` - Load plugin module
  - `enable_plugin(name)` / `disable_plugin(name)` - Toggle plugin state
  - `get_enabled_plugins()` - List active plugins

### User Management

- **[[API_QUICK_REFERENCE#core/user_manager.py|UserManager]]** - User authentication and profiles
  - `create_user(username, password)` - Create new user with bcrypt hashing
  - `authenticate_user(username, password)` - Verify credentials
  - `lock_account(username)` - Lock account after failed attempts
  - `save_users()` - Persist to `data/users.json`

### Extended Command Override

- **[[API_QUICK_REFERENCE#core/command_override.py|CommandOverrideSystem]]** - Extended master password system
  - `validate_override(password)` - SHA-256 password validation
  - `toggle_protocol(protocol_name, state)` - Control 10+ safety protocols
  - `audit_override(action, user)` - Comprehensive audit logging
  - Persists to `data/command_override_config.json`

### AI Intelligence

- **[[API_QUICK_REFERENCE#core/intelligence_engine.py|IntelligenceEngine]]** - OpenAI chat integration
  - `generate_response(prompt, context)` - Generate AI response via GPT-4
  - `stream_completion(prompt)` - Stream response tokens
  - Requires `OPENAI_API_KEY` in `.env`

### GUI Components

Located in `src/app/gui/`:

- **[[API_QUICK_REFERENCE#gui/leather_book_interface.py|LeatherBookInterface]]** - Main application window
  - `QMainWindow` subclass with dual-page layout (Tron login + Dashboard)
  - `switch_to_dashboard()` - Navigate to dashboard page
  - `user_logged_in` signal - Emitted on successful authentication
  - Entry point: `python -m src.app.main`

- **[[API_QUICK_REFERENCE#gui/leather_book_dashboard.py|LeatherBookDashboard]]** - 6-zone dashboard
  - `QWidget` with AI stats, proactive actions, AI head, chat, response zones
  - `send_message.emit(str)` - Signal for user messages
  - Integrates all AI systems (persona, memory, learning, override)

- **[[API_QUICK_REFERENCE#gui/persona_panel.py|PersonaPanel]]** - AI configuration UI
  - 4-tab interface: Personality, Four Laws, Conversation, Memory
  - Personality trait sliders (0.0-1.0)
  - Real-time mood display
  - Save/reset functionality

- **[[API_QUICK_REFERENCE#gui/image_generation.py|ImageGenerationUI]]** - Image generation interface
  - Dual-page layout: Prompt input (left) + Image display (right)
  - Style presets, size selection, backend choice
  - Async generation using `QThread` worker
  - Zoom controls, save, copy to clipboard

### Additional Core Modules

- **[[API_QUICK_REFERENCE#core/image_generator.py|ImageGenerator]]** - Image generation backends
  - `generate(prompt, style, size, backend)` - Generate image
  - `check_content_filter(prompt)` - Block 15 forbidden keywords
  - Supports Hugging Face Stable Diffusion 2.1 and OpenAI DALL-E 3
  - Requires `HUGGINGFACE_API_KEY` and/or `OPENAI_API_KEY`

- **[[API_QUICK_REFERENCE#core/data_analysis.py|DataAnalyzer]]** - Data analysis module
  - `analyze_file(path)` - Analyze CSV/XLSX/JSON files
  - `cluster_data(data, n_clusters)` - K-means clustering
  - Returns pandas DataFrames

- **[[API_QUICK_REFERENCE#core/security_resources.py|SecurityResourceFetcher]]** - Security resources
  - `fetch_ctf_repos()` - Fetch CTF repositories from GitHub
  - `search_security_tools(query)` - Search security tools
  - GitHub API integration

- **[[API_QUICK_REFERENCE#core/location_tracker.py|LocationTracker]]** - Location tracking
  - `track_location(ip)` - IP geolocation
  - `get_gps_location()` - GPS coordinates
  - `encrypt_history()` - Encrypt location history (Fernet)

- **[[API_QUICK_REFERENCE#core/emergency_alert.py|EmergencyAlert]]** - Emergency contact system
  - `send_alert(message, contacts)` - Send email alerts
  - Requires `SMTP_USERNAME` and `SMTP_PASSWORD` in `.env`

### Agent Modules

Located in `src/app/agents/`:

- **[[API_QUICK_REFERENCE#agents/oversight.py|Oversight]]** - Action oversight and safety validation
- **[[API_QUICK_REFERENCE#agents/planner.py|Planner]]** - Task planning and decomposition
- **[[API_QUICK_REFERENCE#agents/validator.py|Validator]]** - Input/output validation
- **[[API_QUICK_REFERENCE#agents/explainability.py|Explainability]]** - Decision explanation generation

### Configuration Files

- **`app-config.json`** - Application configuration settings
- **`.env`** - Environment variables (API keys, credentials)
  - `OPENAI_API_KEY` - Required for AI responses and DALL-E 3
  - `HUGGINGFACE_API_KEY` - Required for Stable Diffusion
  - `FERNET_KEY` - Required for encryption
  - `SMTP_USERNAME`, `SMTP_PASSWORD` - Optional for email alerts

### Data Persistence Pattern

All systems use JSON persistence in `data/` directory:

```python
# Example: AIPersona state persistence
data_dir = "data/ai_persona/"
os.makedirs(data_dir, exist_ok=True)  # CRITICAL: Always create dir
state = {"traits": {...}, "mood": "neutral"}
with open(f"{data_dir}/state.json", "w") as f:
    json.dump(state, f, indent=2)
```

**Critical Pattern**: ALWAYS call `os.makedirs(data_dir, exist_ok=True)` before writing to JSON.

### Threading Pattern (PyQt6)

**NEVER** use `threading.Thread` in GUI code. Use PyQt6 patterns:

```python
# Correct: Use QTimer for delays
QTimer.singleShot(1000, callback)

# Correct: Use pyqtSignal for cross-thread communication
self.user_logged_in.emit(username)

# Correct: Use QThread for background work
worker = ImageGenerationWorker(prompt, style, size)
worker.image_generated.connect(self.display_image)
worker.start()
```

### Error Handling Pattern

All core systems use Python logging:

```python
import logging
logger = logging.getLogger(__name__)

try:
    # operation
except Exception as e:
    logger.error(f"Error in operation: {e}")
```

### Related Documentation

- **Complete API Reference**: [[API_QUICK_REFERENCE]] (339 modules)
- **Architecture Guide**: [[ARCHITECTURE_QUICK_REF]] (visual diagrams)
- **Developer Reference**: [[DEVELOPER_QUICK_REFERENCE]] (commands, workflows)
- **Complete Program Summary**: [[PROGRAM_SUMMARY]] (600+ lines, comprehensive)
- **AI Persona Guide**: [[AI_PERSONA_IMPLEMENTATION]] (persona system deep-dive)
- **Learning System Guide**: [[LEARNING_REQUEST_IMPLEMENTATION]] (learning workflow)
- **Image Generation Restoration**: [[IMAGE_GENERATION_RESTORATION]] (image gen troubleshooting)

### Source Code Locations

```
src/app/
├── main.py                         # Entry point: LeatherBookInterface
├── core/                           # 11 business logic modules
│   ├── ai_systems.py              # 6 AI systems (1,500 LOC)
│   ├── user_manager.py            # User auth (400 LOC)
│   ├── command_override.py        # Extended override (600 LOC)
│   ├── intelligence_engine.py     # OpenAI integration (350 LOC)
│   ├── image_generator.py         # Image generation (220 LOC)
│   ├── data_analysis.py           # CSV/XLSX/JSON analysis (180 LOC)
│   ├── security_resources.py      # GitHub API (200 LOC)
│   ├── location_tracker.py        # Location tracking (250 LOC)
│   ├── emergency_alert.py         # Emergency alerts (180 LOC)
│   ├── learning_paths.py          # Learning path gen (250 LOC)
│   └── intent_detection.py        # Intent classifier (200 LOC)
├── agents/                         # 4 AI agent modules
│   ├── oversight.py               # Action oversight
│   ├── planner.py                 # Task planning
│   ├── validator.py               # Validation
│   └── explainability.py          # Explanations
└── gui/                            # 6 PyQt6 UI modules
    ├── leather_book_interface.py  # Main window (659 LOC)
    ├── leather_book_dashboard.py  # Dashboard (608 LOC)
    ├── persona_panel.py           # Persona UI (4 tabs)
    ├── dashboard_handlers.py      # Event handlers
    ├── dashboard_utils.py         # Utils, logging
    └── image_generation.py        # Image gen UI (450 LOC)
```

---

**Quick Navigation**:
- [[#Installation Steps|↑ Installation]]
- [[#Features at a Glance|↑ Features]]
- [[#Troubleshooting|↑ Troubleshooting]]
- [[API_QUICK_REFERENCE|→ Full API Reference]]
- [[PROGRAM_SUMMARY|→ Complete Documentation]]
