# Fixture Reference

**Purpose:** Complete reference for pytest fixtures across all test modules  
**Scope:** Global fixtures, specialized fixtures, mock fixtures  

---

## Global Fixtures

### From `tests/conftest.py`
No global fixtures defined - uses minimal configuration pattern.

---

## Gradle Evolution Fixtures

**Location:** `tests/gradle_evolution/conftest.py`  
**Purpose:** Specialized fixtures for constitutional, cognition, and capsule systems  

### Mock Fixtures

#### mocker
```python
@pytest.fixture
def mocker() -> Generator[_FallbackMocker, None, None]:
    """Fallback mocker fixture when pytest-mock is unavailable.
    
    Provides:
        - patch(target, *args, **kwargs) -> Any
        - MagicMock class
        - stopall() for cleanup
    
    Usage:
        def test_with_mock(mocker):
            mock_fn = mocker.patch('module.function')
            mock_fn.return_value = 42
    """
```

**Implementation:** Lightweight wrapper around `unittest.mock`

**Methods:**
- `patch(target: str, *args, **kwargs) -> Any` - Patch a module/function
- `stopall() -> None` - Stop all patches (automatic cleanup)
- `MagicMock` - Reference to `unittest.mock.MagicMock`

### File System Fixtures

#### temp_dir
```python
@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test isolation.
    
    Yields:
        Path object pointing to temporary directory
    
    Cleanup:
        Automatic - directory removed after test
    
    Usage:
        def test_file_creation(temp_dir):
            test_file = temp_dir / "test.txt"
            test_file.write_text("content")
            assert test_file.exists()
    """
```

#### constitution_file
```python
@pytest.fixture
def constitution_file(temp_dir: Path) -> Path:
    """Create test constitution.yaml file.
    
    Structure:
        - name: "test_constitution"
        - version: "1.0.0"
        - principles: [security_first, transparency, efficiency]
        - enforcement_levels: {critical, high, medium, low}
        - violation_handling: {immediate_block: [...]}
    
    Returns:
        Path to constitution.yaml in temp_dir
    
    Usage:
        def test_constitution_loading(constitution_file):
            with open(constitution_file) as f:
                config = yaml.safe_load(f)
            assert config["name"] == "test_constitution"
    """
```

**Principles Defined:**
1. **security_first** - Security is paramount (critical, block)
2. **transparency** - All actions auditable (high, warn_and_modify)
3. **efficiency** - Optimize for performance (medium, warn)

#### security_config_file
```python
@pytest.fixture
def security_config_file(temp_dir: Path) -> Path:
    """Create test security_hardening.yaml file.
    
    Structure:
        - least_privilege.agents:
            - build_agent: {allowed_paths, operations, credential_ttl}
            - test_agent: {allowed_paths, operations, credential_ttl}
        - runtime_controls:
            - max_build_duration_minutes: 60
            - require_signature: True
    
    Returns:
        Path to security_hardening.yaml in temp_dir
    
    Usage:
        def test_security_config(security_config_file):
            with open(security_config_file) as f:
                config = yaml.safe_load(f)
            assert config["runtime_controls"]["require_signature"]
    """
```

#### capsule_storage
```python
@pytest.fixture
def capsule_storage(temp_dir: Path) -> Path:
    """Create capsule storage directory.
    
    Returns:
        Path to capsules/ directory in temp_dir
    
    Usage:
        def test_capsule_save(capsule_storage):
            capsule_path = capsule_storage / "test-capsule-001.json"
            capsule_path.write_text('{"id": "001"}')
            assert capsule_path.exists()
    """
```

#### audit_log_path
```python
@pytest.fixture
def audit_log_path(temp_dir: Path) -> Path:
    """Create audit log path.
    
    Returns:
        Path to audit.log in temp_dir (empty file)
    
    Usage:
        def test_audit_logging(audit_log_path):
            with open(audit_log_path, "a") as f:
                f.write("audit entry\\n")
            assert audit_log_path.read_text().startswith("audit")
    """
```

### Data Fixtures

#### sample_build_context
```python
@pytest.fixture
def sample_build_context() -> dict[str, Any]:
    """Sample build context for testing.
    
    Returns:
        {
            "project": "test-project",
            "tasks": ["clean", "build", "test"],
            "dependencies": {
                "compile": ["org.junit:junit:4.13.2"]
            },
            "cache_enabled": True,
            "parallel": False
        }
    
    Usage:
        def test_build_processing(sample_build_context):
            result = process_build(sample_build_context)
            assert result["project"] == "test-project"
    """
```

#### sample_build_capsule_data
```python
@pytest.fixture
def sample_build_capsule_data() -> dict[str, Any]:
    """Sample build capsule data.
    
    Returns:
        {
            "capsule_id": "test-capsule-001",
            "tasks": ["clean", "compileJava", "test"],
            "inputs": {
                "src/main/java/Main.java": "abc123hash",
                "build.gradle": "def456hash"
            },
            "outputs": {
                "build/classes/Main.class": "output123hash",
                "build/reports/test.xml": "output456hash"
            },
            "metadata": {
                "timestamp": "2024-01-01T00:00:00Z",
                "duration_seconds": 45.2,
                "gradle_version": "8.5",
                "jdk_version": "17"
            }
        }
    
    Usage:
        def test_capsule_creation(sample_build_capsule_data):
            capsule = BuildCapsule.from_dict(sample_build_capsule_data)
            assert capsule.capsule_id == "test-capsule-001"
    """
```

#### sample_security_violation
```python
@pytest.fixture
def sample_security_violation() -> dict[str, Any]:
    """Sample security violation data.
    
    Returns:
        {
            "violation_type": "unauthorized_path_access",
            "agent": "test_agent",
            "attempted_path": "/etc/passwd",
            "timestamp": "2024-01-01T00:00:00Z",
            "severity": "critical"
        }
    
    Usage:
        def test_violation_handling(sample_security_violation):
            handler = SecurityViolationHandler()
            result = handler.process(sample_security_violation)
            assert result["blocked"] is True
    """
```

#### sample_temporal_law
```python
@pytest.fixture
def sample_temporal_law() -> dict[str, Any]:
    """Sample temporal law configuration.
    
    Returns:
        {
            "law_id": "test_law_001",
            "effective_from": "2024-01-01T00:00:00Z",
            "effective_until": None,
            "description": "Test security policy",
            "rules": [
                {
                    "condition": "build_duration > 60",
                    "action": "terminate",
                    "priority": "high"
                }
            ]
        }
    
    Usage:
        def test_temporal_law_enforcement(sample_temporal_law):
            enforcer = TemporalLawEnforcer()
            result = enforcer.apply(sample_temporal_law, build_context)
            assert result["enforced"]
    """
```

### Mock System Fixtures

#### mock_deliberation_engine
```python
@pytest.fixture
def mock_deliberation_engine(mocker):
    """Mock DeliberationEngine for testing.
    
    Returns:
        MagicMock with deliberate() method configured
    
    Configuration:
        deliberate() returns:
        {
            "optimized_order": ["clean", "build", "test"],
            "reasoning": {
                "optimization_applied": True,
                "confidence": 0.95
            }
        }
    
    Usage:
        def test_with_deliberation(mock_deliberation_engine):
            result = mock_deliberation_engine.deliberate(tasks)
            assert result["reasoning"]["confidence"] == 0.95
    """
```

#### mock_four_laws
```python
@pytest.fixture
def mock_four_laws(mocker):
    """Mock FourLaws for testing.
    
    Returns:
        MagicMock with validate_action() method configured
    
    Configuration:
        validate_action() returns: (True, "Action allowed")
    
    Usage:
        def test_with_four_laws(mock_four_laws):
            is_allowed, reason = mock_four_laws.validate_action("test", {})
            assert is_allowed is True
    """
```

#### mock_identity_manager
```python
@pytest.fixture
def mock_identity_manager(mocker):
    """Mock IdentityManager for testing.
    
    Returns:
        MagicMock with verify_identity() method configured
    
    Configuration:
        verify_identity() returns: True
    
    Usage:
        def test_with_identity(mock_identity_manager):
            verified = mock_identity_manager.verify_identity(user_id)
            assert verified is True
    """
```

#### mock_audit_function
```python
@pytest.fixture
def mock_audit_function(mocker):
    """Mock audit function from cognition.audit.
    
    Returns:
        MagicMock patching 'cognition.audit.audit'
    
    Usage:
        def test_with_audit(mock_audit_function):
            perform_action()
            mock_audit_function.assert_called_once()
    """
```

---

## Common Fixture Patterns

### Pattern 1: Temporary Directory with System
```python
@pytest.fixture
def persona():
    """Create AIPersona with isolated data directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield AIPersona(data_dir=tmpdir)
```

### Pattern 2: Mock External API
```python
@pytest.fixture
def mock_openai(mocker):
    """Mock OpenAI API calls."""
    mock = mocker.patch('openai.ChatCompletion.create')
    mock.return_value = {
        'choices': [{'message': {'content': 'Test response'}}]
    }
    return mock
```

### Pattern 3: Test Data File
```python
@pytest.fixture
def test_data_file(tmp_path):
    """Create test data file."""
    data_file = tmp_path / "test_data.json"
    data_file.write_text('{"test": true}')
    return data_file
```

### Pattern 4: QApplication for GUI Tests
```python
@pytest.fixture
def qapp():
    """Create QApplication for GUI tests."""
    app = QApplication.instance() or QApplication([])
    yield app
    app.quit()
```

### Pattern 5: Database with Cleanup
```python
@pytest.fixture
def db_session():
    """Create database session with rollback."""
    session = create_session()
    yield session
    session.rollback()
    session.close()
```

---

## Fixture Scope

Pytest fixtures support different scopes:

### Function Scope (Default)
```python
@pytest.fixture
def temp_dir():
    """New directory per test function."""
```

### Class Scope
```python
@pytest.fixture(scope="class")
def shared_data():
    """Shared across all methods in test class."""
```

### Module Scope
```python
@pytest.fixture(scope="module")
def expensive_setup():
    """Shared across all tests in module."""
```

### Session Scope
```python
@pytest.fixture(scope="session")
def database():
    """Shared across entire test session."""
```

**Project-AI Convention:** Use function scope by default for test isolation.

---

## Fixture Composition

Fixtures can depend on other fixtures:

```python
@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def constitution_file(temp_dir):
    # Uses temp_dir fixture
    config_file = temp_dir / "constitution.yaml"
    config_file.write_text("...")
    return config_file

@pytest.fixture
def loaded_constitution(constitution_file):
    # Uses constitution_file, which uses temp_dir
    with open(constitution_file) as f:
        return yaml.safe_load(f)
```

---

## Using Fixtures in Tests

### Basic Usage
```python
def test_with_fixture(temp_dir):
    """temp_dir automatically provided by pytest."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("content")
    assert test_file.exists()
```

### Multiple Fixtures
```python
def test_with_multiple(temp_dir, mocker, sample_build_context):
    """Use multiple fixtures in one test."""
    mock_fn = mocker.patch('module.function')
    result = process_build(sample_build_context, output_dir=temp_dir)
    assert result["success"]
```

### Class-Level Fixtures
```python
class TestAIPersona:
    @pytest.fixture
    def persona(self):
        """Fixture available to all methods in class."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield AIPersona(data_dir=tmpdir)
    
    def test_initialization(self, persona):
        assert persona.user_name == "Friend"
    
    def test_trait_adjustment(self, persona):
        persona.adjust_trait("curiosity", 0.1)
        assert persona.personality["curiosity"] > 0.5
```

---

## Custom Fixture Creation

### Guidelines

1. **Use descriptive names:** `constitution_file` not `cfg`
2. **Document return type:** What does the fixture provide?
3. **Clean up resources:** Use context managers or explicit cleanup
4. **Compose when possible:** Build on existing fixtures
5. **Keep scope minimal:** Function scope unless expensive setup

### Template
```python
@pytest.fixture
def my_fixture(dependency_fixture) -> ReturnType:
    """Brief description of what fixture provides.
    
    Args:
        dependency_fixture: Description if needed
    
    Returns:
        Description of returned object
    
    Usage:
        def test_example(my_fixture):
            result = my_fixture.method()
            assert result
    """
    # Setup
    resource = create_resource(dependency_fixture)
    
    yield resource
    
    # Teardown
    resource.cleanup()
```

---

## Fixture Best Practices

### ✅ DO
- Use `tempfile.TemporaryDirectory()` for file system isolation
- Clean up resources in `yield` fixtures
- Document what fixture provides
- Use descriptive names
- Compose fixtures (build on existing ones)
- Test fixtures independently

### ❌ DON'T
- Use production data directories
- Leave resources uncleaned
- Create global state in fixtures
- Use session scope unless necessary
- Skip documentation
- Make fixtures too complex

---

## Debugging Fixtures

### Show Fixture Setup
```bash
pytest --setup-show tests/test_file.py
```

Output shows fixture setup/teardown:
```
tests/test_file.py::test_example
  SETUP    F temp_dir
  SETUP    F constitution_file (fixtures used: temp_dir)
    tests/test_file.py::test_example (fixtures used: constitution_file, temp_dir)
  TEARDOWN F constitution_file
  TEARDOWN F temp_dir
```

### List Available Fixtures
```bash
pytest --fixtures tests/
```

---

## Next Steps

1. Read `05_CORE_SYSTEM_TESTS.md` for testing patterns
2. See `06_GRADLE_EVOLUTION_FIXTURES.md` for detailed fixture documentation
3. Check `03_TEST_UTILITIES.md` for helper utilities

---

**See Also:**
- `tests/conftest.py` - Global configuration
- `tests/gradle_evolution/conftest.py` - Specialized fixtures
- pytest documentation: https://docs.pytest.org/en/stable/fixture.html
