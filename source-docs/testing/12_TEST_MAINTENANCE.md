# Test Maintenance

**Purpose:** Strategies for maintaining and evolving the test suite  
**Coverage:** Test organization, refactoring, performance, CI/CD integration  

---

## Overview

Test maintenance ensures:

1. **Test Quality** - Tests remain reliable and meaningful
2. **Performance** - Tests run quickly and efficiently
3. **Maintainability** - Tests are easy to understand and modify
4. **Coverage** - Tests adequately cover system functionality
5. **CI/CD Integration** - Tests integrate smoothly with automation

---

## Test Organization

### Directory Structure

```
tests/
├── conftest.py                 # Global configuration
├── utils/                      # Test utilities
│   └── scenario_recorder.py
├── test_*.py                   # Unit tests (120+ files)
├── e2e/                        # End-to-end tests
│   ├── conftest.py
│   └── test_*.py
├── gui_e2e/                    # GUI tests
│   └── test_*.py
├── integration/                # Integration tests
├── plugins/                    # Plugin tests
├── temporal/                   # Temporal workflow tests
├── gradle_evolution/           # Gradle evolution suite
│   ├── conftest.py
│   └── test_*.py
├── agents/                     # Agent-specific tests
├── monitoring/                 # Monitoring tests
└── inspection/                 # Repository inspection tests
```

### Naming Conventions

#### Test Files
```python
# Pattern: test_<module_name>.py
test_ai_systems.py              # ✅ Clear
test_user_manager.py            # ✅ Specific
test_four_laws_stress.py        # ✅ Descriptive

# Avoid
test_1.py                       # ❌ Not descriptive
test_stuff.py                   # ❌ Too vague
ai_tests.py                     # ❌ Missing test_ prefix
```

#### Test Functions
```python
# Pattern: test_<what>_<condition>_<expected>
def test_login_with_valid_credentials_succeeds():     # ✅
def test_four_laws_blocks_harmful_actions():          # ✅
def test_account_lockout_after_failed_attempts():     # ✅

# Avoid
def test_login():                                      # ❌ Not specific
def test_case_1():                                     # ❌ Not descriptive
def check_auth():                                      # ❌ Missing test_ prefix
```

#### Test Classes
```python
# Pattern: Test<SystemName>
class TestFourLaws:                # ✅
class TestAIPersona:               # ✅
class TestMemorySystem:            # ✅

# Avoid
class FourLawsTests:               # ❌ Wrong suffix
class TestSuite1:                  # ❌ Not descriptive
```

---

## Test Quality

### Characteristics of Good Tests

#### 1. Independent
```python
# ✅ GOOD: Test creates its own data
def test_user_creation(tmp_path):
    um = UserManager(users_file=str(tmp_path / "users.json"))
    um.create_user("testuser", "password123")
    assert "testuser" in um.users

# ❌ BAD: Test depends on previous test
def test_user_login():  # Assumes test_user_creation ran first
    um = UserManager()
    success, _ = um.authenticate("testuser", "password123")
    assert success
```

#### 2. Repeatable
```python
# ✅ GOOD: Uses temporary directory
def test_persona_state(tmp_path):
    persona = AIPersona(data_dir=str(tmp_path))
    persona.adjust_trait("curiosity", 0.1)
    # Clean state every run

# ❌ BAD: Uses production directory
def test_persona_state():
    persona = AIPersona()  # Uses data/ directory
    persona.adjust_trait("curiosity", 0.1)
    # State persists between runs
```

#### 3. Fast
```python
# ✅ GOOD: Mocks slow operations
@patch('requests.get')
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {"data": "test"}
    result = fetch_data()
    assert result["data"] == "test"

# ❌ BAD: Makes real API calls
def test_api_call():
    result = fetch_data()  # Real network call
    assert result["data"] is not None
```

#### 4. Clear
```python
# ✅ GOOD: Clear intent and assertions
def test_lockout_prevents_login_with_correct_password():
    """Account lockout blocks login even with correct password."""
    um = UserManager(users_file=str(tmp_path / "users.json"))
    um.create_user("user", "correct_password")
    
    # Lock account with failed attempts
    for _ in range(5):
        um.authenticate("user", "wrong_password")
    
    # Correct password still rejected
    success, msg = um.authenticate("user", "correct_password")
    assert not success
    assert "locked" in msg.lower()

# ❌ BAD: Unclear purpose
def test_lockout():
    um = UserManager(users_file=str(tmp_path / "users.json"))
    um.create_user("user", "pass")
    for _ in range(5):
        um.authenticate("user", "x")
    r, m = um.authenticate("user", "pass")
    assert not r  # Why is this expected?
```

---

## Test Refactoring

### Extract Common Setup to Fixtures

```python
# Before: Duplicated setup
def test_persona_trait_adjustment():
    with tempfile.TemporaryDirectory() as tmpdir:
        persona = AIPersona(data_dir=tmpdir)
        persona.adjust_trait("curiosity", 0.1)
        assert persona.personality["curiosity"] > 0.5

def test_persona_mood():
    with tempfile.TemporaryDirectory() as tmpdir:
        persona = AIPersona(data_dir=tmpdir)
        persona.set_mood("happy", 0.8)
        assert persona.current_mood == "happy"

# After: Fixture for common setup
@pytest.fixture
def persona(tmp_path):
    return AIPersona(data_dir=str(tmp_path))

def test_persona_trait_adjustment(persona):
    persona.adjust_trait("curiosity", 0.1)
    assert persona.personality["curiosity"] > 0.5

def test_persona_mood(persona):
    persona.set_mood("happy", 0.8)
    assert persona.current_mood == "happy"
```

### Parameterize Repetitive Tests

```python
# Before: Multiple similar tests
def test_xss_script_tag():
    assert not validate_input("<script>alert('XSS')</script>")

def test_xss_img_onerror():
    assert not validate_input("<img src=x onerror=alert('XSS')>")

def test_xss_svg_onload():
    assert not validate_input("<svg onload=alert('XSS')>")

# After: Parameterized test
@pytest.mark.parametrize("payload", [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert('XSS')>",
    "javascript:alert('XSS')",
    "<iframe src=javascript:alert('XSS')>",
])
def test_xss_prevention(payload):
    assert not validate_input(payload)
```

### Extract Helper Functions

```python
# Before: Repeated logic
def test_user_flow_1():
    um = UserManager(users_file=str(tmp_path / "users.json"))
    um.create_user("user1", "pass1")
    success, msg = um.authenticate("user1", "pass1")
    assert success
    # ... test logic

def test_user_flow_2():
    um = UserManager(users_file=str(tmp_path / "users.json"))
    um.create_user("user2", "pass2")
    success, msg = um.authenticate("user2", "pass2")
    assert success
    # ... test logic

# After: Helper function
def create_and_authenticate(um, username, password):
    """Helper to create user and authenticate."""
    um.create_user(username, password)
    success, msg = um.authenticate(username, password)
    assert success
    return success

def test_user_flow_1(tmp_path):
    um = UserManager(users_file=str(tmp_path / "users.json"))
    create_and_authenticate(um, "user1", "pass1")
    # ... test logic
```

---

## Performance Optimization

### Profile Test Execution

```bash
# Measure test duration
pytest --durations=10

# Output:
# slowest 10 durations
# 5.23s call     tests/test_four_laws_1000_deterministic.py::test_all_scenarios
# 3.45s call     tests/test_image_generator.py::test_generate_with_api
# 2.87s call     tests/test_web_backend_complete_e2e.py::test_complete_flow
```

### Parallel Test Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4

# Auto-detect CPU count
pytest -n auto
```

### Skip Slow Tests by Default

```python
# Mark slow tests
@pytest.mark.slow
def test_exhaustive_stress_scenarios():
    """Run 2000+ stress test scenarios."""
    # ... long-running test

# pytest.ini configuration
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')

# Run fast tests only
pytest -m "not slow"

# Run all tests including slow
pytest
```

### Mock Expensive Operations

```python
# Before: Slow (real API call)
def test_openai_integration():
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
    assert "content" in response["choices"][0]["message"]

# After: Fast (mocked)
@patch('openai.ChatCompletion.create')
def test_openai_integration(mock_create):
    mock_create.return_value = {
        "choices": [{"message": {"content": "Hello!"}}]
    }
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
    assert response["choices"][0]["message"]["content"] == "Hello!"
```

---

## Coverage Management

### Measure Coverage

```bash
# Run with coverage
pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html
```

### Target Critical Paths

```python
# Prioritize coverage for:
# 1. Security-critical code (authentication, authorization)
# 2. Core business logic (Four Laws, AI systems)
# 3. Error handling paths
# 4. Integration points

# Example: Security-critical coverage
def test_authentication_all_paths(tmp_path):
    um = UserManager(users_file=str(tmp_path / "users.json"))
    um.create_user("user", "pass")
    
    # Success path
    success, msg = um.authenticate("user", "pass")
    assert success
    
    # Wrong password path
    success, msg = um.authenticate("user", "wrong")
    assert not success
    
    # Nonexistent user path
    success, msg = um.authenticate("nonexistent", "pass")
    assert not success
    
    # Locked account path
    for _ in range(5):
        um.authenticate("user", "wrong")
    success, msg = um.authenticate("user", "pass")
    assert not success and "locked" in msg.lower()
```

### Coverage-Driven Test Creation

```bash
# Run coverage and identify gaps
pytest --cov=app --cov-report=term-missing

# Output shows uncovered lines:
# app/core/ai_systems.py    265-266    # Line 265-266 not covered

# Create targeted test:
def test_issue_1_ai_systems_265_266():
    """Test coverage for ai_systems.py lines 265-266."""
    # ... test for uncovered code path
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### Pre-commit Hooks

```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: ["-x", "--tb=short"]

# Install hooks
pre-commit install
```

### Test Failure Notifications

```yaml
# Notify on test failures
- name: Notify Slack on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Test suite failed!'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Test Documentation

### Test Docstrings

```python
def test_account_lockout_after_failed_attempts(tmp_path):
    """Test that account locks after 5 failed authentication attempts.
    
    Security requirement: Prevent brute force attacks by locking
    accounts after repeated failed login attempts.
    
    Expected behavior:
        1. First 4 failures increment counter
        2. 5th failure triggers lockout
        3. Lockout duration is 15 minutes
        4. Correct password rejected during lockout
    
    Related:
        - User Story: US-123 (Account Security)
        - Security Policy: SEC-456 (Brute Force Prevention)
    """
```

### Test Coverage Matrix

Create documentation mapping features to tests:

```markdown
# Test Coverage Matrix

| Feature | Unit Tests | Integration Tests | E2E Tests |
|---------|-----------|-------------------|-----------|
| User Authentication | ✅ test_user_manager.py | ✅ test_complete_system.py | ✅ test_web_backend_endpoints.py |
| Four Laws | ✅ test_ai_systems.py | ✅ test_agents_pipeline.py | ✅ test_governance_api_e2e.py |
| Memory System | ✅ test_memory_extended.py | ✅ test_integration_user_learning.py | ✅ test_web_backend_complete_e2e.py |
```

---

## Test Maintenance Checklist

### Weekly
- [ ] Review failing tests
- [ ] Check test execution time
- [ ] Update flaky test list
- [ ] Review coverage reports

### Monthly
- [ ] Refactor duplicated test code
- [ ] Update test documentation
- [ ] Review and update fixtures
- [ ] Identify obsolete tests

### Quarterly
- [ ] Audit test suite organization
- [ ] Performance optimization pass
- [ ] Update testing standards
- [ ] Review CI/CD integration

---

## Common Maintenance Issues

### Flaky Tests

**Symptom:** Tests pass sometimes, fail sometimes

**Solutions:**
```python
# Issue: Race condition
# Fix: Use proper waits
qtbot.waitSignal(signal, timeout=5000)
time.sleep(0.5)  # Allow async operation to complete

# Issue: Shared state
# Fix: Use isolated fixtures
@pytest.fixture
def isolated_system(tmp_path):
    return System(data_dir=str(tmp_path))

# Issue: Non-deterministic data
# Fix: Seed random generators
import random
random.seed(42)
```

### Brittle Tests

**Symptom:** Tests break on minor implementation changes

**Solutions:**
```python
# Issue: Testing implementation details
# Fix: Test behavior, not implementation
# ❌ BAD
def test_internal_method():
    result = obj._internal_calculate()
    assert result == 42

# ✅ GOOD
def test_public_behavior():
    obj.set_value(10)
    assert obj.get_result() == 42
```

### Slow Tests

**Symptom:** Test suite takes too long

**Solutions:**
- Mock external services
- Use in-memory databases
- Parallelize test execution
- Mark slow tests with `@pytest.mark.slow`

---

## Best Practices Summary

### ✅ DO
- Write independent, repeatable tests
- Use descriptive names
- Extract common setup to fixtures
- Mock external dependencies
- Maintain high coverage for critical code
- Document test purpose and expectations
- Run tests in CI/CD
- Review and refactor regularly

### ❌ DON'T
- Write dependent tests
- Use production data/directories
- Make real API calls
- Ignore flaky tests
- Skip test documentation
- Let test suite slow down
- Ignore coverage gaps

---

## Resources

### Tools
- **pytest** - Test framework
- **pytest-cov** - Coverage reporting
- **pytest-xdist** - Parallel execution
- **pytest-mock** - Mocking utilities
- **hypothesis** - Property-based testing

### Documentation
- pytest: https://docs.pytest.org/
- pytest-qt: https://pytest-qt.readthedocs.io/
- coverage.py: https://coverage.readthedocs.io/

---

**See Also:**
- `01_TEST_FRAMEWORK_OVERVIEW.md` - Testing architecture
- `.github/workflows/ci.yml` - CI configuration
- `pyproject.toml` - Test configuration
- All other testing documentation files in `source-docs/testing/`
