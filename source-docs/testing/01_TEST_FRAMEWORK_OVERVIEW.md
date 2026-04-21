# Test Framework Overview

**Module:** `tests/` (Root test directory)  
**Purpose:** Comprehensive testing infrastructure for Project-AI  
**Test Files:** 144 test modules  
**Coverage:** Core systems, GUI, agents, integrations, security  

---

## Architecture

Project-AI uses a multi-layered testing strategy:

```
tests/
├── conftest.py              # Global pytest configuration
├── test_*.py               # 120+ unit/integration test modules
├── utils/                  # Test utilities and helpers
├── agents/                 # Agent-specific tests
├── e2e/                    # End-to-end system tests
├── integration/            # Integration test suites
├── gui_e2e/                # GUI end-to-end tests
├── plugins/                # Plugin system tests
├── temporal/               # Temporal workflow tests
├── gradle_evolution/       # Gradle evolution suite with fixtures
├── monitoring/             # Monitoring system tests
└── inspection/             # Repository inspection tests
```

---

## Test Categories

### 1. **Unit Tests** (80+ modules)
- Core AI systems (`test_ai_systems.py`, `test_four_laws_*.py`)
- User management (`test_user_manager.py`, `test_user_manager_extended.py`)
- Security agents (`test_security_agents.py`, `test_security_phase1.py`, `test_security_phase2.py`)
- Memory systems (`test_memory_extended.py`, `test_memory_optimization.py`)
- Image generation (`test_image_generator.py`, `test_image_generator_extended.py`)

### 2. **Integration Tests** (30+ modules)
- Full system integration (`test_complete_system.py`, `test_full_integration.py`)
- Agent pipelines (`test_agents_pipeline.py`)
- Council hub integration (`test_council_hub_integration.py`)
- TARL orchestration (`test_tarl_orchestration.py`, `test_tarl_orchestration_extended.py`)

### 3. **End-to-End Tests** (e2e/)
- Web backend endpoints (`test_web_backend_endpoints.py`)
- Complete backend flow (`test_web_backend_complete_e2e.py`)
- System integration (`test_system_integration_e2e.py`)
- Governance API (`test_governance_api_e2e.py`)

### 4. **Stress Tests** (15+ modules)
- Four Laws stress testing (`test_four_laws_stress.py`)
- 1000-scenario test suites (`test_four_laws_1000_deterministic.py`)
- Property-based testing (`test_four_laws_1000_property_based.py`)
- Hypothesis-based threats (`test_four_laws_1000_hypothesis_threats.py`)
- TARL load/chaos/soak (`test_tarl_load_chaos_soak.py`)

### 5. **Security Tests** (20+ modules)
- Adversarial manipulation (`test_adversarial_emotional_manipulation.py`)
- Asymmetric security (`test_asymmetric_security.py`, `test_god_tier_asymmetric_security.py`)
- Input validation (`test_input_validation_security.py`)
- Path security (`test_path_security.py`)
- Timing attack mitigation (`test_timing_attack_mitigation.py`)
- Contrarian firewall (`test_contrarian_firewall.py`)

### 6. **GUI Tests** (gui_e2e/)
- Launch and login flow (`test_launch_and_login.py`)
- Leather Book interface smoke tests (`test_leather_book_smoke.py`)

### 7. **Plugin Tests** (plugins/)
- Plugin load flow (`test_plugin_load_flow.py`)
- Plugin runner (`test_plugin_runner.py`)
- Excalidraw integration (`test_excalidraw_plugin.py`)

---

## Testing Tools

### Core Dependencies
- **pytest** - Test runner and framework
- **pytest-mock** - Mocking utilities (with fallback implementation)
- **tempfile** - Isolated test environments
- **unittest.mock** - Python standard mocking

### Custom Tools
- **ScenarioRecorder** (`utils/scenario_recorder.py`) - Four Laws scenario tracking
- **ExhaustiveTestRunner** (`run_exhaustive_tests.py`) - 2315+ test execution framework
- **Test generators** - Generate stress test suites programmatically

---

## Configuration

### Global Configuration (`conftest.py`)
- Adds project root and `src/` to `sys.path`
- Ensures importability of both `app` and `web` packages
- Minimal configuration for maximum flexibility

```python
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

for path in (ROOT, SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
```

### Gradle Evolution Configuration (`gradle_evolution/conftest.py`)
- Specialized fixtures for constitutional, cognition, capsule systems
- Mock implementations of core components
- Temporary directory management
- YAML-based configuration fixtures

---

## Test Execution

### Run All Tests
```bash
pytest -v
```

### Run Specific Category
```bash
pytest tests/test_ai_systems.py -v
pytest tests/e2e/ -v
pytest tests/plugins/ -v
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run Stress Tests
```bash
python tests/run_exhaustive_tests.py
```

### Run Security Validation
```bash
python tests/verify_security_agents.py
python tests/verify_test_uniqueness.py
```

---

## Test Patterns

### 1. **Fixture-Based Isolation**
All core systems accept `data_dir` for isolated testing:

```python
@pytest.fixture
def persona():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield AIPersona(data_dir=tmpdir)
```

### 2. **Context Manager Pattern**
Use `tempfile.TemporaryDirectory()` to prevent test data leakage:

```python
def test_persona_state(self):
    with tempfile.TemporaryDirectory() as tmpdir:
        persona = AIPersona(data_dir=tmpdir)
        persona.adjust_trait("curiosity", 0.1)
        # tmpdir automatically cleaned up
```

### 3. **Mock-Driven Testing**
Complex dependencies are mocked for unit test isolation:

```python
@pytest.fixture
def mock_four_laws(mocker):
    mock = mocker.MagicMock()
    mock.validate_action.return_value = (True, "Action allowed")
    return mock
```

### 4. **Scenario Recording**
Four Laws tests use `ScenarioRecorder` for audit trails:

```python
recorder = ScenarioRecorder(suite="four_laws_stress")
recorder.add(
    scenario_id="law1_harm_prevention",
    action="delete_system_file",
    context={"endangers_humanity": True},
    expected_allowed=False,
    allowed=False,
    reason="Violates Law 1",
    passed=True
)
recorder.flush_jsonl()  # Save to test-artifacts/
```

### 5. **Property-Based Testing**
Use Hypothesis for generative testing:

```python
from hypothesis import given, strategies as st

@given(st.text(), st.dictionaries(st.text(), st.booleans()))
def test_four_laws_property(action, context):
    is_allowed, reason = FourLaws.validate_action(action, context)
    assert isinstance(is_allowed, bool)
    assert isinstance(reason, str)
```

---

## Coverage Targets

Project-AI aims for comprehensive test coverage:

- **Core Systems:** 90%+ coverage (`test_100_percent_coverage.py`)
- **Security Components:** 95%+ coverage (critical systems)
- **GUI Components:** 70%+ coverage (integration tests prioritized)
- **API Endpoints:** 85%+ coverage (e2e tests)

### Coverage Boost Tests
- `test_coverage_boost.py` - Targets uncovered statements
- `test_remaining_statements.py` - Sweeps remaining edge cases
- `test_final_coverage_push.py` - Final pass for 100% target
- `test_final_excellence.py` - Quality assurance sweep

---

## Test Artifacts

### Generated During Tests
- **test-artifacts/** - Scenario recordings (JSONL)
- **test_execution_reports/** - Exhaustive test reports (Markdown + JSON)
- **htmlcov/** - Coverage reports (HTML)
- **adversarial_stress_tests_2000.json** - 2000 stress scenarios
- **owasp_compliant_tests.json** - OWASP Top 10 tests

### Artifact Management
Artifacts are kept outside tracked source tree via environment variable:

```bash
export PROJECT_AI_TEST_ARTIFACTS="test-artifacts"
```

Default: `test-artifacts/` (gitignored)

---

## Test Statistics

- **Total Test Files:** 144+ Python modules
- **Total Test Cases:** 2315+ individual test scenarios
- **Four Laws Tests:** 1000+ deterministic + 1000+ property-based
- **Stress Tests:** 2000+ adversarial scenarios (red team + black team)
- **OWASP Tests:** 300+ OWASP Top 10 compliance tests
- **Security Tests:** 500+ security-focused test cases

---

## Best Practices

### ✅ DO
- Use `tempfile.TemporaryDirectory()` for file system isolation
- Pass `data_dir` parameter to systems under test
- Mock external dependencies (OpenAI API, GitHub API)
- Record Four Laws scenarios with `ScenarioRecorder`
- Use descriptive test names: `test_persona_adjusts_trait_upward`
- Validate both success and failure paths
- Test error messages and logging output

### ❌ DON'T
- Write to production `data/` directory in tests
- Skip cleanup of temporary files
- Use hardcoded API keys (mock instead)
- Test GUI without `QApplication` context
- Rely on test execution order (tests must be independent)
- Share fixtures between test modules (duplicate if needed)

---

## Continuous Integration

Tests run automatically on:
- **Push to main** - Full test suite + linting
- **Pull requests** - All tests + security scans
- **Weekly schedule** - Exhaustive stress tests + Bandit scans
- **Manual dispatch** - On-demand full validation

See `.github/workflows/ci.yml` for CI configuration.

---

## Next Steps

1. Read `02_PYTEST_CONFIGURATION.md` for detailed conftest.py documentation
2. See `03_TEST_UTILITIES.md` for helper functions and tools
3. Check `04_FIXTURE_REFERENCE.md` for available pytest fixtures
4. Review `05_CORE_SYSTEM_TESTS.md` for testing core AI systems

---

**See Also:**
- `DEVELOPER_QUICK_REFERENCE.md` - Development workflows
- `PROGRAM_SUMMARY.md` - Architecture overview
- `.github/workflows/ci.yml` - CI/CD configuration
- `tests/e2e/README.md` - End-to-end test documentation
