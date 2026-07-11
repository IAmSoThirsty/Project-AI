---
type: moc
area: development
priority: P0
status: active
version: "1.0.0"
created: 2025-01-23
updated: 2025-01-23
maintainer: AGENT-019
total_documents: 180+
schema_version: "1.0"
tags:
  - development
  - testing
  - debugging
  - workflows
  - moc
aliases:
  - Development MOC
  - Developer Index
  - Dev Workflows Map
related_mocs:
  - "[[01_ARCHITECTURE]]"
  - "[[03_GOVERNANCE]]"
  - "[[06_SOURCE_CODE]]"
---

# 04 - Development Workflows MOC

**Purpose:** Comprehensive developer documentation mapping environment setup, testing strategies, debugging guides, contribution workflows, local development procedures, IDE configuration, and development best practices for Project-AI desktop and web platforms.

**Scope:** Development environment setup (.env configuration, API keys, dependencies), desktop development (PyQt6 + Python 3.11+), web development (React 18 + Flask + Vite), testing workflows (pytest, npm test runners), linting & code quality (ruff, mypy, Codacy), CI/CD pipelines (GitHub Actions), and debugging procedures.

**Audience:** Developers (new and experienced), contributors, code reviewers, DevOps engineers, and anyone setting up local development environments or implementing new features.

---

## 🚀 Getting Started

### Quick Start Guides

#### Desktop Application Development
**Prerequisites:**
- Python 3.11+ (3.12 recommended)
- Git for version control
- Virtual environment tool (venv, virtualenv)
- Optional: Docker for containerized development

**Setup Steps:**
1. Clone repository: `git clone https://github.com/username/Project-AI.git`
2. Create virtual environment: `python -m venv .venv`
3. Activate virtual environment: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/Mac)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure API keys
6. Run application: `python -m src.app.main`

**Documents:**
- `guide-desktop-quickstart.md` - Desktop quick start [P0, Active]
- `guide-environment-setup.md` - Development environment setup [P0, Active]
- `DESKTOP_APP_QUICKSTART.md` - Desktop application quick start (root) [P0, Active]
- `DEVELOPER_QUICK_REFERENCE.md` - GUI component API reference (root) [P0, Active]

#### Web Platform Development
**Prerequisites:**
- Python 3.11+ for backend
- Node.js 18+ and npm/yarn for frontend
- Docker and Docker Compose (optional)

**Setup Steps:**
1. **Backend:**
   ```bash
   cd web/backend
   pip install -r requirements.txt
   flask run  # Runs on port 5000
   ```
2. **Frontend:**
   ```bash
   cd web/frontend
   npm install
   npm run dev  # Runs on port 3000
   ```
3. **Docker (full stack):**
   ```bash
   docker-compose -f web/docker-compose.yml up
   ```

**Documents:**
- `guide-web-quickstart.md` - Web platform quick start [P1, In-Progress]
- `guide-frontend-setup.md` - React frontend setup [P1, Planned]
- `guide-backend-setup.md` - Flask backend setup [P1, Planned]
- `web/DEPLOYMENT.md` - Web deployment guide [P1, Active]

### Environment Configuration

#### .env File Setup
**Required Variables:**
```bash
# OpenAI Integration (required for GPT models, DALL-E 3)
OPENAI_API_KEY=sk-...  # Get from https://platform.openai.com/api-keys

# Hugging Face Integration (required for Stable Diffusion 2.1)
HUGGINGFACE_API_KEY=hf_...  # Get from https://huggingface.co/settings/tokens

# Encryption (required for sensitive data)
FERNET_KEY=<generated_key>  # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Email Integration (optional, for emergency alerts)
SMTP_USERNAME=<your_email>
SMTP_PASSWORD=<app_password>
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**API Key Setup:**
- **OpenAI:** Sign up at <https://platform.openai.com/>, create API key
- **Hugging Face:** Create account, generate token at <https://huggingface.co/settings/tokens>
- **SMTP:** Use app-specific password for Gmail (enable 2FA first)

**Documents:**
- `guide-env-configuration.md` - Environment variable configuration [P0, Active]
- `guide-api-keys.md` - API key setup and management [P0, Active]
- `guide-secrets-management.md` - Secrets management best practices [P1, Active]

#### Dependencies Management

**Python Dependencies:**
- **File:** `requirements.txt` (pinned versions), `requirements.in` (unpinned), `requirements.lock` (lock file)
- **Install:** `pip install -r requirements.txt`
- **Update:** `pip install -U -r requirements.in && pip freeze > requirements.txt`
- **Dev Dependencies:** `requirements-dev.txt` (testing, linting tools)

**Node.js Dependencies:**
- **File:** `package.json` (web frontend dependencies)
- **Install:** `npm install` or `yarn install`
- **Update:** `npm update` or `yarn upgrade`
- **Lock File:** `package-lock.json` (commit to version control)

**Documents:**
- `guide-dependencies.md` - Dependency management [P1, Active]
- `guide-dependency-updates.md` - Updating dependencies safely [P1, Active]
- `DEPENDENCY_AUDIT_REPORT.md` - Dependency security audit [P0, Active]

---

## 🧪 Testing

### Testing Strategy

#### Test Pyramid
```
        /\
       /E2E\       End-to-End (10%) - Full user workflows
      /____\
     /Integr\      Integration (30%) - Component interactions
    /________\
   /   Unit   \    Unit (60%) - Individual functions/classes
  /____________\
```

**Coverage Target:** 80%+ overall, 100% for critical paths (auth, security, AI ethics)

**Documents:**
- `testing-strategy.md` - Overall testing strategy [P0, Active]
- `testing-pyramid.md` - Test pyramid implementation [P1, Active]
- `testing-coverage.md` - Coverage requirements and tracking [P1, Active]

### Unit Testing

#### Python Unit Tests (pytest)
**Test Framework:** pytest with pytest-cov for coverage

**Test Structure:**
```
tests/
├── test_ai_systems.py        # 6 AI systems tests
├── test_user_manager.py       # User auth tests
├── test_command_override.py   # Command override tests
├── test_learning_paths.py     # Learning path generation tests
└── conftest.py                # Shared fixtures
```

**Running Tests:**
```bash
# All tests
pytest

# Specific test file
pytest tests/test_ai_systems.py

# With coverage report
pytest --cov=src --cov-report=html

# Verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_fourlaws"
```

**Test Patterns:**
- Use `tempfile.TemporaryDirectory()` for isolated file system tests
- Mock external APIs (OpenAI, Hugging Face) to avoid rate limits
- Test both success and failure paths
- Parametrize tests for multiple scenarios

**Documents:**
- `testing-unit-tests.md` - Unit testing guide [P0, Active]
- `testing-pytest.md` - pytest configuration and usage [P0, Active]
- `testing-fixtures.md` - Test fixtures and mocking [P1, Active]
- `testing-parametrization.md` - Parametrized testing [P2, Active]

#### JavaScript Unit Tests (Jest/Vitest)
**Test Framework:** Vitest (planned for React frontend)

**Running Tests:**
```bash
# npm test
npm run test

# With coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

**Documents:**
- `testing-frontend-unit.md` - Frontend unit testing [P1, Planned]
- `testing-vitest.md` - Vitest configuration [P2, Planned]

### Integration Testing

#### Component Integration Tests
Test interactions between core systems (e.g., FourLaws + LearningRequestManager).

**Example Tests:**
- User login → Dashboard state update → Persona interaction count
- Learning request → Black Vault rejection → Audit log
- Image generation → Content filter → Backend API call

**Documents:**
- `testing-integration.md` - Integration testing strategy [P1, Active]
- `testing-component-integration.md` - Component integration tests [P1, Active]

#### API Integration Tests
Test Flask API endpoints with real database (PostgreSQL in test mode).

**Documents:**
- `testing-api-integration.md` - API integration testing [P1, Planned]

### End-to-End Testing

#### Desktop E2E Tests
**Framework:** PyQt6 Test framework (QTest)

**Test Scenarios:**
- Complete user workflow: Login → Send message → Receive AI response
- Image generation workflow: Prompt → Filter → Generate → Display
- Learning request workflow: Request → Approval dialog → Accept/Deny

**Documents:**
- `testing-e2e-desktop.md` - Desktop E2E testing [P2, Planned]

#### Web E2E Tests
**Framework:** Playwright or Cypress (planned)

**Test Scenarios:**
- User registration and login flow
- API request/response cycles
- UI state management

**Documents:**
- `testing-e2e-web.md` - Web E2E testing [P2, Planned]

### Test Automation

#### CI/CD Test Pipeline
**File:** `.github/workflows/ci.yml`

**Test Stages:**
1. **Lint:** ruff check (fast Python linting)
2. **Type Check:** mypy (static type analysis)
3. **Security Scan:** bandit (security issues), pip-audit (vulnerability scan)
4. **Unit Tests:** pytest with coverage report
5. **Integration Tests:** Component integration tests (planned)
6. **Build Test:** Docker build smoke test

**Quality Gates:**
- All tests pass (exit code 0)
- Coverage ≥ 80%
- No critical/high security issues
- Type checking passes

**Documents:**
- `testing-ci-pipeline.md` - CI/CD test automation [P0, Active]
- `testing-quality-gates.md` - Test quality gates [P0, Active]

---

## 🐛 Debugging

### Debugging Tools

#### Python Debugging
**Tools:**
- **pdb:** Built-in Python debugger (command-line)
- **ipdb:** Enhanced pdb with IPython features
- **VS Code Debugger:** Visual debugger with breakpoints
- **PyCharm Debugger:** Full-featured IDE debugger

**Usage:**
```python
# Insert breakpoint in code
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()
```

**VS Code Launch Configuration:**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Desktop App",
      "type": "python",
      "request": "launch",
      "module": "src.app.main",
      "console": "integratedTerminal"
    }
  ]
}
```

**Documents:**
- `debugging-python.md` - Python debugging guide [P1, Active]
- `debugging-vscode.md` - VS Code debugging setup [P1, Active]
- `debugging-pycharm.md` - PyCharm debugging setup [P2, Active]

#### JavaScript Debugging
**Tools:**
- **Browser DevTools:** Chrome/Firefox developer tools
- **VS Code Debugger:** Debug React app in VS Code
- **React DevTools:** Component hierarchy and state inspection

**Documents:**
- `debugging-javascript.md` - JavaScript debugging [P1, Planned]
- `debugging-react.md` - React debugging techniques [P1, Planned]

### Logging & Tracing

#### Python Logging
**Framework:** Built-in `logging` module

**Configuration:**
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
```

**Log Levels:**
- **DEBUG:** Detailed diagnostic information (development only)
- **INFO:** General informational messages
- **WARNING:** Warning messages (potential issues)
- **ERROR:** Error messages (handled exceptions)
- **CRITICAL:** Critical errors (unrecoverable failures)

**Documents:**
- `debugging-logging.md` - Logging best practices [P1, Active]
- `debugging-log-levels.md` - Log level guidelines [P2, Active]

#### Error Tracking
**Pattern:** All core modules use try-except with logging

```python
try:
    # operation
except Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)
    # Handle error gracefully
```

**Documents:**
- `debugging-error-handling.md` - Error handling patterns [P1, Active]
- `debugging-exception-tracking.md` - Exception tracking [P2, Active]

### Common Issues & Solutions

#### "ModuleNotFoundError: No module named 'app'"
**Cause:** Incorrect module import path or missing `src/` in PYTHONPATH
**Solution:** Always run with `python -m src.app.main`, not `python src/app/main.py`

#### "OpenAI API Key Not Found"
**Cause:** Missing or incorrect `OPENAI_API_KEY` in `.env`
**Solution:** Copy `.env.example` to `.env`, add valid API key, restart app

#### "Port 5000 Already in Use"
**Cause:** Flask backend already running or port conflict
**Solution:** Kill existing process or change port in configuration

#### "PyQt6 Not Found"
**Cause:** PyQt6 not installed in virtual environment
**Solution:** Activate venv, run `pip install -r requirements.txt`

**Documents:**
- `troubleshooting-common-issues.md` - Common issues and solutions [P0, Active]
- `troubleshooting-environment.md` - Environment setup issues [P1, Active]
- `troubleshooting-dependencies.md` - Dependency issues [P1, Active]

---

## 🔧 Development Workflows

### Local Development

#### Development Mode
**Desktop:**
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Run in development mode
python -m src.app.main

# With debug logging
python -m src.app.main --debug
```

**Web:**
```bash
# Backend (Flask development server)
cd web/backend
FLASK_ENV=development flask run --reload

# Frontend (Vite dev server with hot reload)
cd web/frontend
npm run dev
```

**Documents:**
- `workflow-local-development.md` - Local development workflow [P1, Active]
- `workflow-hot-reload.md` - Hot reload setup (web) [P2, Planned]

#### Feature Development
1. **Create Branch:** `git checkout -b feature/my-feature`
2. **Develop:** Implement feature with tests
3. **Test Locally:** Run `pytest` and manual testing
4. **Lint:** `ruff check .` and `mypy src/`
5. **Commit:** Descriptive commit messages
6. **Push:** `git push origin feature/my-feature`
7. **Create PR:** GitHub pull request with description
8. **Code Review:** Address review feedback
9. **Merge:** After approval and CI passes

**Documents:**
- `workflow-feature-development.md` - Feature development workflow [P1, Active]
- `workflow-branching-strategy.md` - Git branching strategy [P1, Active]

### Code Quality

#### Linting
**Tool:** ruff (fast Python linter)

**Configuration:** `pyproject.toml`
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # Line too long (handled by formatter)
```

**Running:**
```bash
# Check all files
ruff check .

# Auto-fix issues
ruff check . --fix

# Specific directory
ruff check src/app/core/
```

**Documents:**
- `workflow-linting.md` - Linting workflow [P1, Active]
- `workflow-ruff-config.md` - ruff configuration [P1, Active]

#### Type Checking
**Tool:** mypy (static type checker)

**Configuration:** `pyproject.toml`
```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

**Running:**
```bash
# Type check all files
mypy src/

# Specific module
mypy src/app/core/ai_systems.py

# With verbose output
mypy src/ --verbose
```

**Documents:**
- `workflow-type-checking.md` - Type checking workflow [P1, Active]
- `workflow-mypy-config.md` - mypy configuration [P1, Active]

#### Code Coverage
**Tool:** pytest-cov (coverage.py wrapper for pytest)

**Running:**
```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term

# View HTML report
# Open htmlcov/index.html in browser

# Check coverage threshold (80%+)
pytest --cov=src --cov-fail-under=80
```

**Documents:**
- `workflow-code-coverage.md` - Code coverage workflow [P1, Active]
- `workflow-coverage-reports.md` - Coverage reporting [P1, Active]

---

## 🛠️ IDE Setup

### Visual Studio Code

#### Recommended Extensions
- **Python:** Python language support, IntelliSense, debugging
- **Pylance:** Fast Python language server
- **Ruff:** ruff linting integration
- **GitLens:** Enhanced Git integration
- **Docker:** Docker container management
- **ESLint:** JavaScript/TypeScript linting

**Extensions File:** `.vscode/extensions.json`

**Documents:**
- `ide-vscode-setup.md` - VS Code setup guide [P1, Active]
- `ide-vscode-extensions.md` - Recommended extensions [P1, Active]

#### Workspace Settings
**File:** `.vscode/settings.json`
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "editor.rulers": [100],
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true
  }
}
```

**Documents:**
- `ide-vscode-settings.md` - VS Code workspace settings [P1, Active]

### PyCharm

#### Configuration
- **Python Interpreter:** Select `.venv` virtual environment
- **Run Configuration:** Module: `src.app.main`
- **Pytest Integration:** Enable pytest as test runner
- **Code Style:** Configure to match ruff rules (100 char line length)

**Documents:**
- `ide-pycharm-setup.md` - PyCharm setup guide [P2, Active]
- `ide-pycharm-run-config.md` - Run configurations [P2, Active]

---

## 📚 Cross-References

### Related MOCs
- [[01_ARCHITECTURE]] - System architecture, component design
- [[03_GOVERNANCE]] - Coding standards, review processes
- [[06_SOURCE_CODE]] - Source code organization, module docs

### Related Indexes
- `by-type/guide-type-index.md` - All development guides
- `by-priority/p0-critical-priority-index.md` - Critical development docs
- `cross-reference/development-dependencies-index.md` - Development dependencies

---

## 🔍 Quick Reference

### First-Time Setup Checklist
1. [ ] Clone repository
2. [ ] Install Python 3.11+ and Node.js 18+
3. [ ] Create virtual environment (`.venv`)
4. [ ] Install dependencies (`pip install -r requirements.txt`)
5. [ ] Copy `.env.example` to `.env`
6. [ ] Configure API keys (OpenAI, Hugging Face)
7. [ ] Generate Fernet key for encryption
8. [ ] Run tests to verify setup (`pytest`)
9. [ ] Run application (`python -m src.app.main`)
10. [ ] Configure IDE (VS Code or PyCharm)

### Daily Development Workflow
1. [ ] Pull latest changes (`git pull origin main`)
2. [ ] Activate virtual environment
3. [ ] Create feature branch
4. [ ] Implement feature with tests
5. [ ] Run tests (`pytest`)
6. [ ] Lint code (`ruff check .`)
7. [ ] Type check (`mypy src/`)
8. [ ] Commit with descriptive message
9. [ ] Push branch and create PR
10. [ ] Address code review feedback

### Pre-Commit Checklist
1. [ ] All tests pass (`pytest`)
2. [ ] Linting clean (`ruff check .`)
3. [ ] Type checking passes (`mypy src/`)
4. [ ] Coverage ≥ 80% (`pytest --cov`)
5. [ ] No hardcoded secrets
6. [ ] Documentation updated
7. [ ] Commit message descriptive
8. [ ] Branch up-to-date with main

---

## 📊 Statistics

- **Total Development Documents:** 180+ documents
- **Quick Start Guides:** 4 guides (desktop, web, environment, API keys)
- **Testing Frameworks:** pytest (Python), Vitest (JS/planned)
- **Current Test Count:** 14 tests across 6 test classes
- **Target Test Coverage:** 80%+ overall, 100% for critical paths
- **Linting Tools:** ruff (Python), ESLint (JavaScript)
- **IDE Support:** VS Code (primary), PyCharm (secondary)
- **CI/CD Pipelines:** 1 comprehensive pipeline (`.github/workflows/ci.yml`)

---

## 🛡️ Governance

**Maintainer:** AGENT-019 (MOC Constructor)
**Update Frequency:** Event-driven (when development workflows change)
**Review Cycle:** Quarterly review of development practices
**Quality Gate:** All development docs must include working examples
**Onboarding:** New contributors must complete First-Time Setup Checklist

---

**Version:** 1.0.0
**Last Updated:** 2025-01-23
**Schema Compliance:** ✅ 100%
**Developer Satisfaction:** 🎯 Target: Onboarding < 30 minutes

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
