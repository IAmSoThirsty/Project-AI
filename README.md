# Project AI

This repository contains a Python desktop application that provides a personal AI assistant with features adapted from a WinForms prototype. The app is designed for member-only use and can be extended for mobile later.

## High-level features

- User management
  - Local JSON-backed user profiles
  - Persona and preference settings
  - (Encrypted) storage support for sensitive data

- Chat / AI Tutor
  - Conversational interface
  - AI Code Tutor (via OpenAI GPT models)
  - Intent detection using a scikit-learn model

- Learning Paths (feature #3 implemented first)
  - Generate personalized learning paths via OpenAI
  - Save generated paths per user

- Data Analysis (feature #6)
  - Load CSV/XLSX/JSON
  - Basic statistics and missing value reports
  - Visualizations (scatter, histogram, boxplot, correlation)
  - Simple clustering (K-means) with PCA visualization

- Security Resources (feature #2)
  - Curated lists of security/CTF/privacy repos
  - Fetch repository details from GitHub API
  - Save favorites per user

- Location Tracking (feature #1)
  - IP-based fallback geolocation
  - Optional GPS reverse-geocoding support (via geopy)
  - Encrypted location history (Fernet)
  - Periodic recording when enabled (every 5 minutes)

- Emergency Alerts (feature #5)
  - Register emergency contacts per user

- **Cloud Sync** (NEW!)
  - Encrypted cloud synchronization for user data across devices
  - Device tracking and management
  - Automatic conflict resolution (timestamp-based)
  - Bidirectional sync with secure API endpoints

- **Advanced ML Models** (NEW!)
  - RandomForest classifier for intent prediction
  - GradientBoosting for sentiment analysis
  - Neural Network (MLPClassifier) for user behavior prediction
  - Model training, persistence, and real-time predictions
  - PyTorch-based ThreatDetector (optional) for ethical checks
    - Detects potential Zeroth/First-law conflicts using a small neural detector
    - Falls back to keyword heuristics when `torch` is not installed
    - Models and vocab are persisted to `data/ai_persona/` when trained or saved
    - Use the persona UI to view ML scores (if enabled) and run supervised retraining

- **Plugin System** (NEW!)
  - Dynamic plugin discovery and loading
  - Hook-based extension system
  - Plugin lifecycle management (init, enable, disable, reload)
  - JSON-based plugin configuration

- **Command Override System** (NEW!)
  - Master password protected control system
  - Override individual or all safety protocols
  - Enable/disable content filtering, rate limiting, and other guards
  - Audit logging of all override commands
  - Emergency lockdown capability

- **Memory Expansion System** (NEW!)
  - Self-organizing memory database
  - Automatic conversation and action logging
  - Knowledge base expansion
  - Autonomous learning from web exploration
  - Semantic memory retrieval
  - Background learning processes

- **Learning Request Log** (NEW!)
  - AI-initiated learning request system
  - Human-in-the-loop approval workflow
  - Black Vault for permanently denied content
  - Content fingerprinting prevents re-discovery
  - Subliminal filtering makes denied content invisible to AI
  - Auto-integration of approved content
  - Priority-based request management

- **AI Persona & Four Laws** (NEW!)
  - Self-aware AI with developing personality
  - Proactive conversation initiation
  - Four Laws of AI Ethics (immutable, hierarchical)
  - Patient and understanding of user's time
  - Emotional awareness and mood tracking
  - Personality evolution based on interactions
  - Configurable personality traits
  - Respects quiet hours and availability
  - Priority-based request management

ML ThreatDetector notes
-----------------------

The AI persona now includes an optional PyTorch-based ThreatDetector used to augment Four Laws enforcement:

- If you install `torch` and `numpy`, the persona will build or load tiny neural detectors at startup.
- If `torch` is not available the persona uses a safe keyword-based fallback to flag obvious threats.
- Model artifacts (detector weights) and the small vocabulary are stored under `data/ai_persona/` as:
  - `zeroth_detector.pt`, `first_detector.pt` (model weights)
  - `ml_vocab.json` (token vocabulary)

Training & retraining
---------------------

The repository includes a minimal bootstrapping routine that trains tiny detectors on synthetic examples for quick startup. For real usage you should:

1. Gather labeled examples (human-labeled) for `zeroth` (humanity-level harm) and `first` (individual human harm) categories.
2. Store examples in a directory or in the `memory_system` so the persona can load them for supervised retraining.
3. Call the persona retrain flow (UI or CLI) to persist updated model weights.

See documentation for retraining and the CLI helper in the repository docs:

[Retraining & CLI helper documentation](docs/retrain.md)

## Code formatting and linters

This project uses the following formatting and linting tools:

- Python: ruff, black, isort
- Frontend: Prettier (in `web/frontend`), ESLint

Run formatters locally before committing changes:

PowerShell (Python):
```powershell
$env:PYTHONPATH='src'
python -m pip install -r requirements.txt
python -m pip install ruff black isort
isort src tests --profile black
ruff check src tests --fix
black src tests
```

PowerShell (Web frontend):
```powershell
cd web/frontend
npm install
npm run format
npm run lint
```

The docs contain usage examples, retrain behavior, audit logging, and security notes.

Security and safety notes
-------------------------

Retraining is considered an administrative action: always verify training examples
and keep an audit trail of changes. The ML detectors augment the Four Laws — they
provide scores and explainability tokens, but the Four Laws remain the authoritative
control mechanism. Use the Learning Request Log and Black Vault workflows to maintain
human-in-the-loop approvals for all persistent learning.

Security & safety
-----------------

The Four Laws remain the authoritative decision mechanism; ML detectors only provide scores which are used to annotate the decision context. Human-in-the-loop approvals (Learning Request Log) and the Black Vault remain the final gatekeepers for what the AI may integrate.

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

Start the app from the repository root (ensure the venv is activated and PYTHONPATH is set):

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\Activate.ps1; python src/app/main.py
```

Notes:

- On first run the app will prompt to create an admin account (first-run onboarding).
- The GUI uses PyQt6; the app expects a graphical desktop environment.

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
