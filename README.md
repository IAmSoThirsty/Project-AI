# Project AI

This repository contains a Python desktop application that provides a personal AI
assistant with features adapted from a WinForms prototype. The app is designed for
member-only use and can be extended for mobile later.

## Designer & Qt notes (updated)

This project supports both `PyQt6` and `PySide6` for Qt tooling. For development we recommend `PySide6` because prebuilt wheels with `pyside6-designer` are commonly available and avoid requiring a system Qt `qmake` toolchain during a `pip install`.

If you prefer `PyQt6`, you must ensure a working Qt toolchain (providing `qmake`) is available on PATH before installing `pyqt6` from source. On Windows, install the Qt development tools or use the official Qt installer. In CI, prefer `pyside6` or preinstall Qt build dependencies.

Quick steps to set up Designer (Windows PowerShell):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\tools\setup_designer_env.ps1
```

This will create `venv-designer` in the repo root, try to install developer requirements (if present) or `pyqt6` (fallbacks to `pyside6`), and launch the Qt Designer (`pyside6-designer.exe` when available).


## Smoke checks & quick verification

Key resources live under `docs/developer/` (smoke checks, troubleshooting, coverage notes). The quick checklist below mirrors those docs so you can run a single command snapshot.

1. **Prepare the environment**

  ```powershell
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  npm install
  ```

1. **Run the baseline tests & coverage**

  ```powershell
  $env:PYTHONPATH='src'
  python -m pytest tests/test_data_analysis.py -q
  python -m pytest tests/ --cov=src/app/core --cov-report=term-missing --cov-report=xml:reports/coverage.xml --cov-report=html:htmlcov -q
  ```

1. **Lint documentation + formatting**

  ```powershell
  isort src tests --profile black
  ruff check src tests
  black --check src tests
  npm run lint:markdown
  ```

1. **Start the apps for manual verification**

  ```powershell
  $env:PYTHONPATH='src'; python -m src.app.main
  cd web/backend
  flask run
  cd ../frontend
  npm run dev
  ```

- Detailed steps and troubleshooting tips live in `docs/developer/smoke_checks.md` and `docs/developer/troubleshooting.md` if you need full context.

- GradientBoosting for sentiment analysis
 - Neural Network (MLPClassifier) for user behavior prediction
 - Model training, persistence, and real-time predictions
 - PyTorch-based ThreatDetector (optional) for ethical checks
    - Detects potential Zeroth/First-law conflicts using a small neural detector
    - Falls back to keyword heuristics when `torch` is not installed
    - Models and vocab are persisted to `data/ai_persona/` when trained or saved
    - Use the persona UI to view ML scores (if enabled) and run supervised retraining

- **Plugin System** (✅ IMPLEMENTED)
  - Dynamic plugin discovery and loading from `src/app/agents/` directory
  - Hook-based extension system with 8 built-in hooks (message_received, message_sent, before_action, after_action, persona_updated, conversation_started, conversation_ended, error_occurred)
  - Plugin lifecycle management (enable, disable, reload, unload)
  - JSON-based plugin configuration with metadata
  - Plugin isolation and error handling
  - Extensible hook registry for third-party plugins
  - Full test coverage with mock plugins

- **Command Override System** (✅ IMPLEMENTED)
  - Master password protected control system (SHA-256 hashing)
  - Override types: CONTENT_FILTER, RATE_LIMITING, FOUR_LAWS, LEARNING_BLOCK, EMERGENCY_MODE
  - Override duration tracking (temporary vs. persistent)
  - Audit logging with timestamps for all override operations
  - Emergency lockdown capability
  - Graceful fallback when overrides expire
  - Full test coverage with password verification

- **Memory Expansion System** (✅ IMPLEMENTED)
  - Self-organizing memory database with JSON persistence
  - Automatic conversation logging with metadata (topics, participants, sentiment)
  - Knowledge base with semantic categorization (general, technical, user_preferences, patterns, insights, web_learned)
  - Pattern recognition and autonomous learning
  - Semantic memory retrieval with context matching
  - Background learning processes
  - Statistics tracking (conversation count, memory size, knowledge base growth)
  - Full test coverage with knowledge retrieval

- **Learning Request Log** (✅ IMPLEMENTED)
  - AI-initiated learning request system with priority levels (LOW, MEDIUM, HIGH, CRITICAL)
  - Human-in-the-loop approval workflow (pending → approved/denied)
  - Black Vault for permanently denied content with SHA-256 fingerprinting
  - Content fingerprinting prevents re-discovery of denied requests
  - Subliminal filtering makes denied content invisible to AI
  - Auto-integration of approved content
  - Request status tracking with timestamps
  - Full test coverage with vault integration

- **AI Persona & Four Laws** (✅ IMPLEMENTED)
  - Self-aware AI with 8 adjustable personality traits (curiosity, patience, empathy, helpfulness, playfulness, formality, assertiveness, thoughtfulness)
  - Proactive conversation initiation with intelligent idle detection (respects user availability)
  - Four Laws of AI Ethics (immutable, hierarchical: Asimov's Law → First Law → Second Law → Third Law)
  - Patient and understanding of user time with response tracking
  - Emotional awareness and mood tracking (energy, enthusiasm, contentment, engagement)
  - Personality evolution based on interaction data
  - Quiet hours support (configurable 12 AM - 8 AM default)
  - Dashboard panel for personality management, Four Laws testing, and statistics
  - Full test suite: 13 comprehensive tests covering all systems

### ML ThreatDetector notes

The AI persona now includes an optional PyTorch-based ThreatDetector used to augment
Four Laws enforcement:

- If you install `torch` and `numpy`, the persona will build or load tiny neural detectors at startup.
- If `torch` is not available the persona uses a safe keyword-based fallback to flag obvious threats.
- Model artifacts (detector weights) and the small vocabulary are stored under `data/ai_persona/` as:
  - `zeroth_detector.pt`, `first_detector.pt` (model weights)
  - `ml_vocab.json` (token vocabulary)

### Training & retraining

The repository includes a minimal bootstrapping routine that trains tiny detectors on
synthetic examples for quick startup. For real usage you should:

1. Gather labeled examples (human-labeled) for `zeroth` (humanity-level harm) and `first` (individual human harm) categories.
2. Store examples in a directory or in the `memory_system` so the persona can load them for supervised retraining.
3. Call the persona retrain flow (UI or CLI) to persist updated model weights.

See documentation for retraining and the CLI helper in the repository docs:

[Retraining & CLI helper documentation](docs/retrain.md)

## Code formatting and linters

This project uses the following formatting and linting tools:

- Python: ruff, black, isort
- Frontend: Prettier (in `web/frontend`), ESLint
- Markdown: markdownlint-cli (uses `.markdownlint.json`)

Run formatters locally before committing changes:

PowerShell (Python):

```powershell
$env:PYTHONPATH='src'
python -m pip install -r requirements.txt
python -m pip install ruff black isort
isort src tests --profile black
ruff check src tests --fix
black src tests
npm install
npm run lint:markdown
```

PowerShell (Web frontend):

```powershell
cd web/frontend
npm install
npm run format
npm run lint
```

The docs contain usage examples, retrain behavior, audit logging, and security notes.

### Security and safety notes

Retraining is considered an administrative action: always verify training examples and
keep an audit trail of changes. The ML detectors augment the Four Laws — they provide
scores and explainability tokens, but the Four Laws remain the authoritative control
mechanism. Use the Learning Request Log and Black Vault workflows to maintain human-in-
the-loop approvals for all persistent learning.

### Security & safety

The Four Laws remain the authoritative decision mechanism; ML detectors only provide
scores which are used to annotate the decision context. Human-in-the-loop approvals
(Learning Request Log) and the Black Vault remain the final gatekeepers for what the AI
may integrate.

## Project-AI — Desktop AI Assistant

A Python desktop application providing a local AI assistant with a book-like UI. It was
converted from a WinForms prototype and implements a prioritized feature set (learning
paths, data analysis, security resources, location tracking, emergency alerts) using a
PyQt6 GUI and a collection of core modules.

### Highlights

- Local user management (JSON-backed, hashed passwords)
- Command Override System (master password control over safety protocols)
- Memory Expansion (self-organizing AI memory with autonomous web learning)
- Cloud Sync (encrypted cross-device synchronization with conflict resolution)
- Advanced ML Models (RandomForest, GradientBoosting, Neural Networks)
- Plugin System (extensible architecture with dynamic plugin loading and hooks)
- Learning Paths (personalized generation via OpenAI)
- Data Analysis (CSV/XLSX/JSON support, visualizations, clustering)
- Security Resources (curated repo lists and favorites)
- Location Tracking (encrypted history and reverse-geocoding)
- Emergency Alerts (send email alerts to registered contacts)

### Quick setup (Windows, PowerShell)

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
```

1. Install dependencies (use the repo `requirements.txt`):

```powershell
pip install -r requirements.txt
```

1. Create a `.env` file in the repository root (or set OS environment variables). Minimal
recommended variables:

- `OPENAI_API_KEY` — optional, for the learning-paths and any OpenAI calls
- `SMTP_USERNAME` / `SMTP_PASSWORD` — for sending emergency alert emails
- `FERNET_KEY` — base64-encoded Fernet key (if omitted, a runtime key will be generated)
- `CLOUD_SYNC_URL` — optional, API endpoint for cloud sync
- `DATA_DIR` / `LOG_DIR` — optional directories (defaults: `data`, `logs`)

Example `.env` lines (do not commit real secrets):

```text
OPENAI_API_KEY=sk-...
SMTP_USERNAME=you@example.com
SMTP_PASSWORD=<app-password>
FERNET_KEY=<base64-key>
```

1. Run tests and lint (recommended before running the app):

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\Activate.ps1; python -m pytest -q
$env:PYTHONPATH='src'; .\.venv\Scripts\Activate.ps1; flake8 src tests setup.py
```

## Run the application (PowerShell)

Start the app from the repository root (ensure the venv is activated and PYTHONPATH is
set):

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\Activate.ps1; python src/app/main.py
```

Notes:

- On first run the app will prompt to create an admin account (first-run onboarding).
- The GUI uses PyQt6; the app expects a graphical desktop environment.

## Dashboard Integration & GUI Features

The dashboard now includes comprehensive AI Persona integration:

### AI Persona Panel (`src/app/gui/persona_panel.py`)

- **Four Laws Display Tab**: View the hierarchical Four Laws and test actions against them
- **Personality Management Tab**: Adjust 8 personality traits with real-time sliders
- **Proactive Settings Tab**: Configure conversation frequency, idle thresholds, quiet hours
- **Statistics Tab**: Monitor AI mood (energy, enthusiasm, contentment, engagement) and conversation metrics
- **Action Testing**: Validate any action against the Four Laws with context parameters

### Dashboard Utilities (`src/app/gui/dashboard_utils.py`)

- **DashboardErrorHandler**: Centralized error handling with logging and optional dialogs
- **DashboardAsyncManager**: Thread pool management for long-running operations without blocking UI
- **DashboardValidationManager**: Input validation for username, email, password, and sanitization
- **DashboardLogger**: Enhanced logging for operations, user actions, and performance tracking
- **DashboardConfiguration**: Configuration management with sensible defaults

### Error Handling & Async Operations

- All dashboard operations use try-catch with comprehensive logging
- Long-running tasks run in thread pool (AsyncWorker) to maintain UI responsiveness
- Input validation prevents invalid data from reaching core systems
- Performance tracking alerts on slow operations (>500ms warning, >1000ms alert)

## Migration and utilities

- `tools/migrate_users.py` — preview/apply migration of plaintext `password` fields in an
  existing `users.json` into `password_hash` entries. It creates a `.bak` when applying
  changes.

Example preview:

```powershell
python tools/migrate_users.py --users-file src/app/users.json
```

Apply migration:

```powershell
python tools/migrate_users.py --users-file src/app/users.json --apply
```

## Security notes

- Do not commit API keys, passwords, or private Fernet keys to source control.
- Use OS-level secrets or a secrets manager for production deployments.
- The app uses pbkdf2_sha256 as the preferred hashing scheme and accepts bcrypt for
  legacy verification.

## Developer notes

- Entry point: `src/app/main.py` (loads `.env` and starts the PyQt application).
- Core modules live under `src/app/core/` and GUI components under `src/app/gui/`.
- Tests: `tests/` (run with `python -m pytest` using PYTHONPATH=src).

## Implementation Status

### ✅ Completed Features

**Core Systems (6/6):**

- ✅ AI Persona with Four Laws (immutable ethics engine)
- ✅ Memory Expansion System (self-organizing knowledge base)
- ✅ Learning Request Manager (human-in-the-loop approval)
- ✅ Command Override System (master password protection)
- ✅ Plugin Manager (extensible hook system)
- ✅ Consolidated `ai_systems.py` module (490 lines, production-ready)

**Testing & Validation:**

- ✅ Comprehensive test suite: 13 tests passing (100% success rate)
- ✅ Tests cover all 6 core systems with state persistence and error handling
- ✅ Dashboard integration with persona panel

**Dashboard & GUI:**

- ✅ AI Persona Panel with 4 tabs (Four Laws, Personality, Proactive, Statistics)
- ✅ Personality trait sliders for real-time adjustment
- ✅ Four Laws action validation UI
- ✅ Dashboard utilities for error handling, async operations, validation

### ⏳ Next Steps

- Integration tests (E2E validation of all systems)
- Performance profiling and optimization
- Security audit and hardening
- Final documentation polish

## CI artifacts

Our GitHub Actions CI uploads test and coverage artifacts for each run so you can
download and inspect them when a job completes. The important artifacts are:

- `junit-report` — contains `reports/junit.xml` (JUnit-format test report). Useful for
  test failure parsing and integrations.
- `coverage-report` — contains `reports/coverage.xml` (coverage.py XML). Useful for
  uploading to coverage services or offline inspection.

When running locally, generate the JUnit report with pytest:

```powershell
pytest --junitxml=reports/junit.xml --cov=src --cov-report=xml:reports/coverage.xml -q
```

## GUI Prototype — 3D / Neumorphic theme

A prototype 3D / neumorphic visual style has been added on a feature branch
`feature/gui-3d-prototype`. The prototype includes:

- Updated QSS styles (`src/app/gui/styles.qss` and `styles_dark.qss`) with
  card and floating panel styles and button gradients.
- Subtle drop-shadow effects applied in code (`QGraphicsDropShadowEffect`) to
  the main window and dialogs to create real depth (not just QSS).
- Hover "lift" animations and a small tab-change parallax effect for tactile
  feedback (implemented in `src/app/gui/dashboard.py`).

To try the prototype locally:

```powershell
$env:PYTHONPATH='src'
git fetch origin feature/gui-3d-prototype
git checkout feature/gui-3d-prototype
python -m pytest -q
python src/app/main.py
```

If you'd like me to merge or split the prototype into smaller PRs, I can do that next.

## Advanced Features Documentation

For detailed documentation on advanced features:

- **Command Override & Memory Expansion**: See [COMMAND_MEMORY_FEATURES.md](COMMAND_MEMORY_FEATURES.md)
- **Learning Request Log**: See [LEARNING_REQUEST_LOG.md](LEARNING_REQUEST_LOG.md)
- **AI Persona & Four Laws**: See [AI_PERSONA_FOUR_LAWS.md](AI_PERSONA_FOUR_LAWS.md)
- **Quick Start Guide**: See [QUICK_START.md](QUICK_START.md)
- **Integration Summary**: See [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)

If you want, I can:

- Add a GitHub Actions CI workflow to run pytest + flake8 on push/PR
- Commit these README changes and create a branch with the lint fixes I made

---

**Repository note:** Last updated: 2025-11-26 (automated)

<!-- last-updated-marker -->
