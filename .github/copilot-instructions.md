# Project-AI Copilot Instructions

## Project Overview

Project-AI is a sophisticated Python desktop application providing a self-aware AI assistant with ethical decision-making (Asimov's Laws), autonomous learning, and a PyQt6 "Leather Book" UI. Features include plugin system, command overrides, memory expansion, and a web version (React + Flask).

## Architecture

### Core Structure

```
src/app/
├── main.py                    # Entry point: LeatherBookInterface
├── core/                      # 11 business logic modules
│   ├── ai_systems.py         # 6 AI systems (470 lines: FourLaws, Persona, Memory, Learning, Plugin, Override)
│   ├── user_manager.py       # User auth, bcrypt hashing, JSON persistence
│   ├── command_override.py   # Extended master password system with 10+ safety protocols
│   ├── learning_paths.py     # OpenAI-powered learning path generation
│   ├── data_analysis.py      # CSV/XLSX/JSON analysis, K-means clustering
│   ├── security_resources.py # GitHub API integration, CTF/security repos
│   ├── location_tracker.py   # IP geolocation, GPS, encrypted history (Fernet)
│   ├── emergency_alert.py    # Emergency contact system with email alerts
│   ├── intelligence_engine.py # OpenAI chat integration
│   ├── intent_detection.py   # Scikit-learn ML intent classifier
│   └── image_generator.py    # Image generation (HF Stable Diffusion, OpenAI DALL-E)
├── agents/                    # 4 AI agent modules (NOT plugins)
│   ├── oversight.py          # Action safety validation
│   ├── planner.py            # Task decomposition
│   ├── validator.py          # Input/output validation
│   └── explainability.py     # Decision explanations
└── gui/                       # 6 PyQt6 UI modules
    ├── leather_book_interface.py   # Main window (659 lines)
    ├── leather_book_dashboard.py   # 6-zone dashboard (608 lines)
    ├── persona_panel.py            # 4-tab AI configuration
    ├── dashboard_handlers.py       # Event handler methods
    ├── dashboard_utils.py          # Error handling, logging, validation
    └── image_generation.py         # Image gen UI (dual-page layout, 450 lines)
```

### Six Core AI Systems (`src/app/core/ai_systems.py`)

All six systems are implemented in a single file for cohesion:

1. **FourLaws**: Immutable ethics framework validating actions against hierarchical rules
1. **AIPersona**: 8 personality traits, mood tracking, persistent state in `data/ai_persona/state.json`
1. **MemoryExpansionSystem**: Conversation logging, knowledge base (6 categories), JSON persistence
1. **LearningRequestManager**: Human-in-the-loop approval workflow, Black Vault for denied content
1. **CommandOverride**: SHA-256 password protection, audit logging (lines 400-470)
1. **PluginManager**: Simple plugin system with enable/disable (lines 340-395)

Note: `command_override.py` contains extended override system with 10+ safety protocols.

### Data Persistence Pattern

All systems use JSON for persistence in `data/` directory:

- `users.json` - User profiles with bcrypt password hashes
- `data/ai_persona/state.json` - Personality, mood, interaction counts
- `data/memory/knowledge.json` - Categorized knowledge base
- `data/learning_requests/requests.json` - Learning requests with status tracking
- `data/command_override_config.json` - Override states and audit logs

**Critical**: Always call `_save_state()` or `save_users()` after modifying state to ensure persistence.

## Development Workflows

### Running the Application

```powershell
# Desktop (PyQt6)
python -m src.app.main

# Tests (14 tests in tests/)
pytest -v
npm run test:python

# Linting (ruff configured in pyproject.toml)
ruff check .
ruff check . --fix

# Docker (see docker-compose.yml)
docker-compose up
```

### Testing Strategy

All core systems accept `data_dir` parameter for isolated testing:

```python
@pytest.fixture
def persona(self):
    with tempfile.TemporaryDirectory() as tmpdir:
        yield AIPersona(data_dir=tmpdir)
```

Pattern: Use context managers with `tempfile.TemporaryDirectory()` to avoid test data leakage.
Tests: 14 tests across 6 test classes in `tests/test_ai_systems.py`, `tests/test_user_manager.py`
Coverage: Each system has 2-4 tests validating core functionality (initialization, state changes, persistence)

### GUI Development

**Leather Book UI** uses dual-page layout:

- **Left (Tron)**: Login page with `TRON_GREEN = "#00ff00"`, `TRON_CYAN = "#00ffff"`
- **Right**: Dashboard with 6 zones (stats, actions, AI head, chat, response)

Key classes:

- `LeatherBookInterface(QMainWindow)` - Main window with page switching
- `LeatherBookDashboard(QWidget)` - 6-zone dashboard
- `PersonaPanel(QWidget)` - 4-tab AI configuration UI

**Signal pattern**: Use PyQt6 signals for inter-component communication:
```python
user_logged_in = pyqtSignal(str)  # In LeatherBookInterface
send_message = pyqtSignal(str)     # In UserChatPanel
```

## Project-Specific Conventions

### Error Handling Pattern

All core systems use Python logging:
```python
import logging
logger = logging.getLogger(__name__)
try:
    # operation
except Exception as e:
    logger.error(f"Error description: {e}")
```

### State Validation Pattern

AI systems validate actions through `FourLaws.validate_action(action, context)` before execution:
```python
is_allowed, reason = FourLaws.validate_action(
    "Delete cache",
    context={"is_user_order": True, "endangers_humanity": False}
)
```

### Password Security

- Use `bcrypt` for password hashing (see `UserManager._hash_and_store_password`)
- `CommandOverrideSystem` uses SHA-256 for master password (legacy, consider bcrypt)
- Fernet encryption for sensitive data (location history, cloud sync)

### Import Organization

Follow ruff-enforced order (pyproject.toml configures isort):

1. Standard library
1. Third-party (PyQt6, scikit-learn, openai, etc.)
1. Local modules (`from app.core import ...`)

## Integration Points

### OpenAI Integration

API key via environment variable:
```python
from dotenv import load_dotenv
load_dotenv()  # Loads OPENAI_API_KEY from .env
```
Used in: `learning_paths.py`, `intelligence_engine.py`, `image_generator.py`

### Image Generation System

Dual backend support with content filtering and style presets:

**Core Module** (`src/app/core/image_generator.py`):

- `ImageGenerator` class with async generation
- Backends: Hugging Face Stable Diffusion 2.1 (`stabilityai/stable-diffusion-2-1`), OpenAI DALL-E 3
- Content filtering: 15 blocked keywords, automatic safety negative prompts
- Style presets: 10 options (photorealistic, digital_art, oil_painting, watercolor, anime, sketch, abstract, cyberpunk, fantasy, minimalist)
- Generation history tracking with JSON persistence
- Methods: `generate()`, `check_content_filter()`, `generate_with_huggingface()`, `generate_with_openai()`

**GUI Module** (`src/app/gui/image_generation.py`):

- Dual-page layout: Left (Tron-themed prompt input) + Right (image display)
- `ImageGenerationWorker`: QThread for async generation (prevents UI blocking during 20-60s generation)
- `ImageGenerationLeftPanel`: Prompt input, style selector, size selector, backend choice, generate button
- `ImageGenerationRightPanel`: Image display with zoom controls, metadata, save/copy buttons
- Signal-based communication: `image_generated.emit(image_path, metadata)`

**Dashboard Integration**:

- "🎨 GENERATE IMAGES" button in `ProactiveActionsPanel`
- Signal: `actions_panel.image_gen_requested.connect(switch_to_image_generation)`
- Navigation: `switch_to_image_generation()` adds interface to page 2, `switch_to_dashboard()` returns to page 1

**Environment Setup**:
```bash
# Required in .env
HUGGINGFACE_API_KEY=hf_...  # From https://huggingface.co/settings/tokens
OPENAI_API_KEY=sk-...        # For DALL-E 3 backend
```

**Content Safety Pattern**:
```python
is_safe, reason = generator.check_content_filter(prompt)
if not is_safe:
    return None, f"Content filter: {reason}"
```

### Web Version Architecture

**Note**: Web version is in development - desktop is production-ready.

- **Backend**: Flask API wrapping core (`web/backend/`)
- **Frontend**: React 18 + Vite, Zustand state management (`web/frontend/`)
- **Port Separation**: Backend (5000), Frontend (3000)
- **Deployment**: Docker Compose with PostgreSQL (see `web/DEPLOYMENT.md`)

Switching contexts:

- Desktop: `python -m src.app.main` (PyQt6)
- Web backend: `cd web/backend && flask run`
- Web frontend: `cd web/frontend && npm run dev`

### AI Agent System

Four specialized agents in `src/app/agents/`:

- `oversight.py` - Action oversight and safety validation
- `planner.py` - Task decomposition and planning
- `validator.py` - Input/output validation
- `explainability.py` - Decision explanation generation

Agents are NOT the same as plugins. Plugin system is simpler (enable/disable only).

## Critical Gotchas

1. **Module imports**: ALWAYS use `python -m src.app.main` NOT `python src/app/main.py`
   - Reason: PYTHONPATH must include `src/` for imports like `from app.core import ...`
   - Tests also require: `pytest` (auto-discovers from project root)

1. **Data directory creation**: Every system constructor must call:

   ```python
   os.makedirs(data_dir, exist_ok=True)
   ```
   Without this, JSON persistence will fail silently in new installations.

1. **PyQt6 threading**: NEVER use `threading.Thread` in GUI code
   - Correct: `QTimer.singleShot(1000, callback)` for delays
   - Correct: `pyqtSignal` for cross-thread communication
   - GUI updates MUST occur on main thread

1. **State persistence**: Call `_save_state()` or `save_users()` after EVERY state modification
   - Systems persist to JSON - forgetting this loses user data
   - Pattern in `ai_systems.py`: all mutating methods call `_save_state()` before returning

1. **Black Vault fingerprinting**: SHA-256 hash content before checking vault

   ```python
   content_hash = hashlib.sha256(content.encode()).hexdigest()
   if content_hash in manager.black_vault:
       return  # Content is forbidden
   ```

1. **Password security**: Different systems use different hashing
   - `UserManager`: bcrypt (secure, salted)
   - `CommandOverride`: SHA-256 (legacy, consider upgrading)

1. **Codacy integration**: After file edits, MUST run `codacy_cli_analyze`
   - See `.github/instructions/codacy.instructions.md` for workflow

## Deployment Workflows

### Development (Desktop)

```powershell
# Quick launch (Windows)
.\launch-desktop.bat
# or
.\launch-desktop.ps1

# Manual launch
python -m src.app.main
```

### Production (Docker)

```bash
# Desktop in container
docker-compose up

# Multi-stage build (optimized)
docker build -t project-ai:latest .
```

Dockerfile uses:

- Multi-stage build (builder + runtime)
- Python 3.11-slim base
- Health checks every 30s
- Volume mounts for `data/` and `logs/`

### Web Deployment

```bash
# Local development
cd web/backend && flask run
cd web/frontend && npm run dev

# Production (Docker Compose)
docker-compose -f web/docker-compose.yml up -d
```

Cloud options: Vercel (frontend), Railway/Heroku (backend) - see `web/DEPLOYMENT.md`

## Key Documentation Files

- `PROGRAM_SUMMARY.md` - Complete architecture (600+ lines)
- `DEVELOPER_QUICK_REFERENCE.md` - GUI component API reference
- `AI_PERSONA_IMPLEMENTATION.md` - Persona system details
- `LEARNING_REQUEST_IMPLEMENTATION.md` - Learning workflow and Black Vault
- `DESKTOP_APP_QUICKSTART.md` - Installation and launch methods
- `.github/instructions/ARCHITECTURE_QUICK_REF.md` - Visual diagrams and data flows
- `.github/instructions/README.md` - Instructions index and navigation guide

## Environment Setup

Required in `.env` (root directory):
```bash
OPENAI_API_KEY=sk-...           # For GPT models and DALL-E 3
HUGGINGFACE_API_KEY=hf_...      # For Stable Diffusion 2.1 (get from https://huggingface.co/settings/tokens)
FERNET_KEY=<generated_key>      # For encryption
SMTP_USERNAME=<optional>        # For email alerts
SMTP_PASSWORD=<optional>        # For email alerts
```

Generate Fernet key:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

API Key Setup:

- **OpenAI**: Sign up at <https://platform.openai.com/api-keys>
- **Hugging Face**: Create account and get token at <a href="https://huggingface.co/settings/tokens">https://huggingface.co/settings/tokens</a>

Dependencies:

- Python: See `pyproject.toml` (PyQt6, scikit-learn, openai, cryptography, requests, etc.)
- Node.js: See `package.json` (test runners only, not required for desktop)

## Automated Workflows

### Pull Request Automation

The repository has automated workflows to handle pull requests and safety alerts:

**Auto PR Handler** (`.github/workflows/auto-pr-handler.yml`):

- Automatically reviews PRs from Dependabot
- Runs linting and tests on all PRs
- Auto-approves PRs that pass all checks
- Auto-merges Dependabot patch and minor version updates
- Comments on PRs with review results
- Flags major version updates for manual review

**Auto-merge criteria**:

- PR is from Dependabot or has `auto-merge` label
- All linting checks pass (ruff)
- All tests pass (pytest)
- For Dependabot: Only patch/minor updates are auto-merged

### Security Alert Automation

Multiple workflows monitor and respond to security issues:

**Auto Security Fixes** (`.github/workflows/auto-security-fixes.yml`):

- Runs daily at 2 AM UTC
- Scans dependencies using `pip-audit` and `safety`
- Automatically creates issues for security vulnerabilities
- Attempts to auto-fix security issues via PRs
- Monitors CodeQL alerts and creates tracking issues
- Uploads detailed security reports as workflow artifacts

**Auto Bandit Fixes** (`.github/workflows/auto-bandit-fixes.yml`):

- Runs weekly on Mondays at 3 AM UTC
- Scans Python code for security issues using Bandit
- Categorizes findings by severity (High/Medium/Low)
- Creates issues for security findings with detailed reports
- Uploads SARIF results to GitHub Security tab
- Provides actionable recommendations for fixes

**Dependabot Configuration** (`.github/dependabot.yml`):

- Daily updates for Python dependencies
- Weekly updates for npm, GitHub Actions, and Docker
- Groups security updates for batch processing
- Auto-labels PRs by dependency type
- Limits open PRs to prevent noise (10 for Python, 5 for npm/Actions, 3 for Docker)
- Configures reviewers and commit message prefixes

### Existing Security Workflows

**CodeQL** (`.github/workflows/codeql.yml`):

- Runs on push/PR to main and cerberus-integration branches
- Analyzes Python code for security vulnerabilities
- Uploads results to GitHub Security tab

**Bandit** (`.github/workflows/bandit.yml`):

- Runs on push to main, PRs, and weekly schedule
- Scans for common Python security issues
- Fails workflow if security issues found

**CI Pipeline** (`.github/workflows/ci.yml`):

- Comprehensive test suite with Python 3.11 and 3.12
- Linting (ruff), type checking (mypy), security audit (pip-audit)
- Test coverage reporting
- Docker build and smoke tests

### Manual Triggering

All automated workflows support manual dispatch:
```bash
# Trigger security scan manually
gh workflow run auto-security-fixes.yml

# Trigger Bandit scan manually
gh workflow run auto-bandit-fixes.yml
```

### Monitoring and Alerts

Security issues are tracked through:

1. **GitHub Issues**: Auto-created with `security` and `automated` labels
1. **Workflow Artifacts**: Detailed JSON/SARIF reports for each scan
1. **Security Tab**: CodeQL and Bandit SARIF results
1. **PR Comments**: Automated review comments on pull requests

### Best Practices for Working with Automation

1. **Check for auto-created issues** before starting security work
1. **Review Dependabot PRs** even when auto-approved (especially major updates)
1. **Don't disable security workflows** without team discussion
1. **Use workflow artifacts** for detailed security scan results
1. **Label PRs with `auto-merge`** to trigger automated approval (only for safe changes)
1. **Monitor GitHub Actions usage** as security scans count toward monthly limits
