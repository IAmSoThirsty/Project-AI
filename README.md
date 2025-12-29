# Project AI

The Synthesis Manifesto: On the Emergent Symbiosis of Project AI, Cerberus, and Codex Deus Maximus

Author's Note

This manifesto serves to outline the philosophical and technical architecture of The Triumvirate—the integrated system of Project AI, Cerberus, and Codex Deus Maximus. It is a declaration of our intentions and a call to participatory evolution.

—Jeremy Karrick, Founder and Head Developer

-1.0 Preamble: A New Paradigm for a Post-Digital Epoch
In the contemporary epoch of post-digital transformation, the velocity of technological evolution consistently outpaces the linear paradigms of traditional organizational adaptation. This growing chasm threatens to destabilize core societal institutions.

The foundational philosophy of the Triumvirate eschews reductionist, compartmentalized systems in favor of an organically intertwined operational theorem. Within this architecture, cognition (Project AI), integrity (Cerberus), and institutional memory (Codex Deus Maximus) are unified into a living, evolving enterprise.

This document will deconstruct this architecture, first by examining the specialized role of each constituent and then by analyzing the operational choreography that binds them into a cohesive, self-improving system.

*(Manifesto follows...)*  
<!-- Manifesto content lines 11–109 left completely unchanged -->

---

## About Project AI

**Project AI** is a next-generation, locally runnable desktop AI assistant for power users, developers, and researchers. It combines advanced machine learning with ethical safety controls, deep extensibility, and an easy-to-use PyQt6 GUI.

The app is feature-complete (as of late 2025) and places privacy, security, customization, and transparency at its core. All data is processed locally; optional cloud sync is encrypted end-to-end.

### Core Features

- **AI Persona Engine** — Adaptive personal AI with adjustable traits, emotional awareness, and immutable Four Laws ethical core.
- **Plugin System** — Dynamic extension via hooks (8 built-in), supporting third-party plugins.
- **Local/Cloud Data** — Persistent memory, encrypted cloud sync, and cross-device history.
- **Learning Request Log** — Human-in-the-loop management for all new knowledge.
- **ML Threat Detection** — Real-time safety net for ethical, legal, and privacy compliance.
- **Advanced Analytics** — Powerful data analysis (CSV/XLSX/JSON), model training, visualizations.
- **Security & Emergency** — Role-based controls, location tracking, emergency email alerts.
- **Modern UI** — Customizable PyQt6 “leather book” GUI with dashboard, Four Laws tab, and personality management.

## Bots, Agents & Automation in Project-AI

Project-AI is built as a “council” of intelligent agents and bots—each providing specialized automation, self-improvement, security, or orchestration. Here is a full, up-to-date list of all autonomous agents, bots, and automated functional systems employed in the repository:

### 🧠 Principal Bots & Agents (Active in the Core System)

- **AIPersona:**  
  The core self-aware AI. Possesses adjustable personality, emotional state, and enforces the Four Laws in all actions/interactions. Handles conversation, ethics, learning and guidance.

- **MemoryExpansionSystem:**  
  Logs, organizes, and persists all conversations and learned knowledge. Provides context-aware retrieval and tracks knowledge metrics.

- **ContinuousLearningEngine:**  
  Background learning/refinement of knowledge base—both supervised (human-in-loop) and unsupervised.

- **Cerberus:**  
  Dynamic security bot: Launches “guardians” to monitor and defend the system, escalates defenses, triggers lockdown/shutdown if breaches occur.

- **ThreatDetector:**  
  ML-based agent: Detects violations of the Four Laws, possible harm/threats, and provides extra safety net. Runs on-PyTorch for best results, otherwise falls back to heuristics.

- **LearningRequestManager:**  
  Human-in-the-loop approval manager: All candidate learning content must pass through this system (“Black Vault” for denied/restricted info).

- **CommandOverride (OverrideManager):**  
  Allows master password overrides of AI “hard rules” (emergency only); all actions are strictly audited.

- **KnowledgeCurator:**  
  Cleans, deduplicates, and organizes new information/insight integrated by the AI.

- **TestQAGenerator:**  
  Generates and validates questions/answers for test coverage and AI regression checks.

- **DependencyAuditor:**  
  Automatically audits software dependencies for security and stability.

- **DocGenerator:**  
  Auto-generates and updates README and documentation from codebase and AI summaries.

- **RefactorAgent:**  
  Scans for possible code improvement/refactoring, assists CI pipeline, and can auto-suggest changes.

- **SandboxRunner:**  
  Runs code and experiments in an isolated environment, protecting main app from faulty or malicious code.

- **RetrievalAgent:**  
  Searches and fetches context/resources across knowledge bases, memory, and web (local or remote).

- **RollbackAgent:**  
  Can detect and revert problematic changes, provides automated rollback/integration flows.

- **PlannerAgent:**  
  Background planner for scheduling, task delegation, and auto-prioritizing work.

- **PluginManager:**  
  Auto-discovers, validates, loads, and manages plugins/extensions. Supports 8+ hooks for full automation extension.

### 🔧 Additional Automated & Integration Functions

- **CloudSync Bot:**  
  Handles secure, encrypted cross-device synchronization and conflict resolution for user data/profiles.

- **UserManager:**  
  Manages authentication, secure password storage (hashed), access controls, and auditing.

- **Learning Paths Engine:**  
  AI/ML-based system for generating personalized stepwise “learning roadmaps”.

- **DataAnalysis Pipeline:**  
  Automates ingestion, clustering, prediction, and visualization of user and external data.

- **LocationTracker & EmergencyAlerts:**  
  Background monitoring (user-authorized), automated geo-tracking, and rapid emergency alert dispatch.

- **Automated GUI Dashboard Utilities:**  
  Async management, input validation, user feedback, and centralized error reporting.

- **Comprehensive TestQAGenerator:**  
  (see above) plus automated test runs before code acceptance.

---

### 🆕 What’s Newly Clarified/Added in this Update

- This list was **created and added for public documentation transparency as of Dec 29, 2025**.
- Each bot/agent and function listed above is actively referenced in the latest code (`src/app/core/council_hub.py`, `ai_systems.py`, README.md, docs).
- The public README now includes direct descriptions of each bot/agent and their safety, orchestration, and learning role.
- The summary also highlights new developer-facing docs, audit systems, and plugin extensibility.

> **For full technical details, developer tips, and agent customization,**  
> see: [`docs/overview/PROGRAM_SUMMARY.md`](docs/overview/PROGRAM_SUMMARY.md) and [`docs/developer/COMMAND_MEMORY_FEATURES.md`](docs/developer/COMMAND_MEMORY_FEATURES.md).

---

**Last updated:** 2025-12-29

## Quick Start

### Requirements

- Python 3.10+
- Node.js (for web components/optional frontend)
- (Windows recommended for full Designer/UI setup; Linux/Mac supported)
- See [requirements.txt](./requirements.txt) for Python dependencies
- Docs and setup instructions in [`docs/`](./docs/)

### First-Time Setup

#### 1. Clone the repository

```powershell
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI
```

#### 2. (Recommended) Create and activate a new virtualenv

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
```

#### 3. Install dependencies

```powershell
pip install -r requirements.txt
npm install
```

#### 4. (Optional) Set up environment variables

Copy `.env.example` to `.env` and configure keys (OpenAI, email for alerts, etc).  
**Never commit secrets!**

#### 5. Run tests and linters

```powershell
python -m pytest -q
npm run lint:markdown
```

#### 6. Launch the GUI application

```powershell
$env:PYTHONPATH='src'; python src/app/main.py
```

- On first use: create an Admin account and personalize your AI.

## Documentation & Resources

- **Quick Start**: [docs/overview/DESKTOP_APP_QUICKSTART.md](docs/overview/DESKTOP_APP_QUICKSTART.md)
- **AI Persona & Ethics**: [docs/overview/AI_PERSONA_FOUR_LAWS.md](docs/overview/AI_PERSONA_FOUR_LAWS.md)
- **Memory & Override**: [docs/overview/COMMAND_MEMORY_FEATURES.md](docs/overview/COMMAND_MEMORY_FEATURES.md)
- **API/Integration**: [docs/overview/INTEGRATION_SUMMARY.md](docs/overview/INTEGRATION_SUMMARY.md)
- **Web/Android Stubs**: See [android/README.md](android/README.md) for mobile integration roadmaps.

All advanced configuration, developer notes, and policy documents live under [`docs/`](./docs/). Check out [docs/README.md](docs/README.md) for a full map.

## Contribution & Community

- Contributing: [docs/policy/CONTRIBUTING.md](docs/policy/CONTRIBUTING.md)
- Code of Conduct: [docs/policy/CODE_OF_CONDUCT.md](docs/policy/CODE_OF_CONDUCT.md)
- Security: [docs/policy/SECURITY.md](docs/policy/SECURITY.md)

## Current Status

- ✔️ All core systems stable (AI Persona, plugins, ML detectors, override manager, memory/logging)
- 🧑‍💻 13/13 core API tests passing
- 🛠️ Next: Full end-to-end (E2E) system tests, performance analysis, audit

Officially maintained and supported for Windows, with cross-platform compatibility where possible.

---

**Repository note:** Last updated: 2025-12-29 (automated rebuild for public release)

<!-- last-updated-marker -->
