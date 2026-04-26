# Pytest Configuration

**Module:** `tests/conftest.py`  
**Purpose:** Global pytest configuration and path setup  
**Scope:** All test modules inherit this configuration  

---

## Overview

The root `conftest.py` provides minimal but critical configuration:

1. **Path Setup** - Ensures importability of all project modules
2. **Import Resolution** - Handles both `src/` and non-src packages (like `web/`)
3. **Cross-Platform Compatibility** - Works on Windows, Linux, macOS

---

## Source Code

```python
"""Pytest configuration: ensure repository root (for non-src packages like `web`) is importable.

This adds the project root to sys.path so tests can import the top-level `web` package.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

for path in (ROOT, SRC):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
```

---

## Path Resolution Strategy

### 1. **ROOT Directory**
```python
ROOT = Path(__file__).resolve().parent.parent
```

- `__file__` → `T:/Project-AI-main/tests/conftest.py`
- `.parent` → `T:/Project-AI-main/tests/`
- `.parent.parent` → `T:/Project-AI-main/` (project root)

Enables imports like:
```python
from web.backend.app import create_app
```

### 2. **SRC Directory**
```python
SRC = ROOT / "src"
```

- Points to `T:/Project-AI-main/src/`
- Critical for `app.core` imports

Enables imports like:
```python
from app.core.ai_systems import FourLaws
from app.gui.leather_book_interface import LeatherBookInterface
```

### 3. **sys.path Insertion**
```python
for path in (ROOT, SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, path_str)
```

- Uses `insert(0, ...)` to prioritize local modules over installed packages
- Checks for duplicates to avoid multiple insertions
- Converts `Path` objects to strings for `sys.path` compatibility

---

## Import Patterns Enabled

### Core Application Imports
```python
# AI Systems
from app.core.ai_systems import (
    FourLaws,
    AIPersona,
    MemoryExpansionSystem,
    LearningRequestManager,
    CommandOverride,
)

# User Management
from app.core.user_manager import UserManager

# Agents
from app.agents.oversight import OversightAgent
from app.agents.planner import PlannerAgent
```

### Web Application Imports
```python
# Backend
from web.backend.app import create_app
from web.backend.routes import api_bp

# Frontend (if running Python tests for frontend config)
# Generally not used, frontend is React/JS
```

### GUI Imports
```python
from app.gui.leather_book_interface import LeatherBookInterface
from app.gui.leather_book_dashboard import LeatherBookDashboard
from app.gui.persona_panel import PersonaPanel
```

---

## Why Minimal Configuration?

Project-AI uses a **minimal conftest.py** strategy:

### ✅ Advantages
1. **Explicit Fixtures** - Each test suite defines its own fixtures (clear dependencies)
2. **No Hidden Magic** - Configuration is obvious and traceable
3. **Easy Debugging** - Fewer layers between test and system under test
4. **Flexible Isolation** - Tests control their own environment setup

### 🚫 Avoided Patterns
- **Auto-fixtures** - No implicit fixtures injected into all tests
- **Global Mocks** - Mocking is done per-test or per-module
- **Database Fixtures** - No shared database state (uses JSON persistence)
- **Subprocess Management** - No pytest-xdist configuration (tests run serially by default)

---

## Gradle Evolution Configuration

The `tests/gradle_evolution/` subdirectory has its **own conftest.py** with specialized fixtures.

### Location
```
tests/gradle_evolution/conftest.py
```

### Fixtures Provided
```python
# Mock fixtures
@pytest.fixture
def mocker():
    """Fallback mocker fixture when pytest-mock unavailable."""

# File system fixtures
@pytest.fixture
def temp_dir():
    """Temporary directory for test isolation."""

@pytest.fixture
def constitution_file(temp_dir):
    """YAML constitution for testing."""

@pytest.fixture
def security_config_file(temp_dir):
    """Security hardening configuration."""

@pytest.fixture
def capsule_storage(temp_dir):
    """Capsule storage directory."""

@pytest.fixture
def audit_log_path(temp_dir):
    """Audit log file path."""

# Data fixtures
@pytest.fixture
def sample_build_context():
    """Sample Gradle build context."""

@pytest.fixture
def sample_build_capsule_data():
    """Sample build capsule metadata."""

@pytest.fixture
def sample_security_violation():
    """Sample security violation data."""

@pytest.fixture
def sample_temporal_law():
    """Sample temporal law configuration."""

# Mock system fixtures
@pytest.fixture
def mock_deliberation_engine(mocker):
    """Mock DeliberationEngine."""

@pytest.fixture
def mock_four_laws(mocker):
    """Mock FourLaws validator."""

@pytest.fixture
def mock_identity_manager(mocker):
    """Mock IdentityManager."""

@pytest.fixture
def mock_audit_function(mocker):
    """Mock audit function from cognition.audit."""
```

See `06_GRADLE_EVOLUTION_FIXTURES.md` for detailed documentation.

---

## Running Tests

### Default Pytest Discovery
```bash
# From project root
pytest

# Verbose mode
pytest -v

# Show print statements
pytest -s

# Specific file
pytest tests/test_ai_systems.py

# Specific test function
pytest tests/test_ai_systems.py::TestFourLaws::test_law_validation_blocked
```

### With Coverage
```bash
# Generate coverage report
pytest --cov=app --cov=web

# HTML coverage report
pytest --cov=app --cov-report=html

# Coverage for specific module
pytest --cov=app.core.ai_systems tests/test_ai_systems.py
```

### Marker-Based Execution
```bash
# Run only unit tests (if markers defined)
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run integration tests
pytest -m integration
```

---

## Custom Test Runners

Project-AI includes specialized test runners:

### 1. **Exhaustive Test Runner**
```bash
python tests/run_exhaustive_tests.py
```

- Executes all 2315+ stress tests
- Generates individual Markdown reports per test
- Produces JSON summary with execution times
- Output: `test_execution_reports/`

### 2. **Security Verification**
```bash
python tests/verify_security_agents.py
```

- Validates security agent implementations
- Checks Four Laws enforcement
- Verifies audit logging

### 3. **Test Uniqueness Checker**
```bash
python tests/verify_test_uniqueness.py
```

- Ensures all stress test IDs are unique
- Validates scenario uniqueness (MD5 hash of steps)
- Reports duplicate test names

### 4. **Test Sample Viewer**
```bash
python tests/show_test_sample.py
```

- Displays sample test structure
- Verifies required fields present
- Shows test format examples

---

## Environment Variables

### Test Artifacts Location
```bash
export PROJECT_AI_TEST_ARTIFACTS="test-artifacts"
```

- Default: `test-artifacts/` (gitignored)
- Used by `ScenarioRecorder` for JSONL output
- Used by exhaustive test runner for reports

### API Keys (Mocked in Tests)
```bash
# Should NOT be set during testing
# Tests mock OpenAI/Hugging Face calls
unset OPENAI_API_KEY
unset HUGGINGFACE_API_KEY
```

### Database Paths (Temporary)
```bash
# Tests use tempfile.TemporaryDirectory()
# No environment variables needed
```

---

## Pytest Plugins

### Installed
- **pytest** - Core framework
- **pytest-cov** - Coverage reporting

### NOT Used (Intentionally)
- **pytest-mock** - Has fallback implementation in `gradle_evolution/conftest.py`
- **pytest-xdist** - Tests run serially (simpler debugging)
- **pytest-asyncio** - No async tests currently
- **pytest-django** - Not a Django project
- **pytest-flask** - Flask tests use direct client

---

## Test Isolation Strategy

### Per-Test Isolation
Tests are fully isolated using:

1. **Temporary Directories**
   ```python
   with tempfile.TemporaryDirectory() as tmpdir:
       manager = LearningRequestManager(data_dir=tmpdir)
   ```

2. **Data Directory Parameters**
   ```python
   persona = AIPersona(data_dir="/path/to/temp/dir")
   ```

3. **Mock External Services**
   ```python
   @patch('app.core.intelligence_engine.openai.ChatCompletion.create')
   def test_chat(mock_openai):
       mock_openai.return_value = {...}
   ```

4. **No Shared State**
   - Each test creates fresh instances
   - No module-level singletons in test code
   - Systems clean up after themselves

---

## Common Issues and Solutions

### Issue: ImportError for `app.core`
**Solution:** Ensure running tests from project root:
```bash
cd T:/Project-AI-main
pytest tests/
```

### Issue: Tests create files in `data/`
**Solution:** Always pass `data_dir` parameter:
```python
# ❌ BAD
persona = AIPersona()  # Uses production data/ directory

# ✅ GOOD
with tempfile.TemporaryDirectory() as tmpdir:
    persona = AIPersona(data_dir=tmpdir)
```

### Issue: QApplication errors in GUI tests
**Solution:** Create QApplication in fixture:
```python
@pytest.fixture
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
    app.quit()
```

### Issue: Test pollution (tests pass individually, fail together)
**Solution:** Check for shared state:
- Module-level variables modified by tests
- Singleton patterns without reset
- File system state not cleaned up

---

## Configuration Best Practices

### ✅ DO
- Run tests from project root
- Use `tempfile.TemporaryDirectory()` for file I/O
- Pass `data_dir` to all systems under test
- Mock external API calls
- Use `-v` flag for debugging
- Check coverage with `pytest --cov`

### ❌ DON'T
- Modify conftest.py without understanding import impact
- Add global fixtures that hide test dependencies
- Use production data directories in tests
- Rely on test execution order
- Skip cleanup in fixtures

---

## Next Steps

1. Read `03_TEST_UTILITIES.md` for helper functions
2. See `04_FIXTURE_REFERENCE.md` for available fixtures
3. Check `05_CORE_SYSTEM_TESTS.md` for testing patterns

---

**See Also:**
- `tests/gradle_evolution/conftest.py` - Specialized fixtures
- `pytest.ini` (if exists) - Additional pytest configuration
- `.github/workflows/ci.yml` - CI test execution
