# Gradle Evolution Fixtures

**Module:** `tests/gradle_evolution/conftest.py`  
**Purpose:** Specialized pytest fixtures for Gradle Evolution test suite  
**Scope:** Constitutional testing, cognition systems, capsules, security  

---

## Overview

The Gradle Evolution test suite (`tests/gradle_evolution/`) has its own `conftest.py` providing:

- **Mock fixtures** - Fallback mocker implementation
- **File system fixtures** - Temporary directories and configuration files
- **Data fixtures** - Sample build contexts, capsules, violations
- **System mocks** - Mock implementations of core components

---

## Mock Infrastructure

### _FallbackMocker Class

```python
class _FallbackMocker:
    """Lightweight subset of pytest-mock's mocker fixture API."""
    
    def __init__(self) -> None:
        self._patches: list[mock._patch] = []
        self.MagicMock = mock.MagicMock
    
    def patch(self, target: str, *args: Any, **kwargs: Any) -> Any:
        """Patch a target with unittest.mock.patch."""
        patcher = mock.patch(target, *args, **kwargs)
        patched = patcher.start()
        self._patches.append(patcher)
        return patched
    
    def stopall(self) -> None:
        """Stop all active patches."""
        while self._patches:
            patcher = self._patches.pop()
            patcher.stop()
```

**Purpose:** Provides pytest-mock-like API when pytest-mock is unavailable.

**Methods:**
- `patch(target, *args, **kwargs)` - Create and start a patch
- `stopall()` - Clean up all patches
- `MagicMock` - Reference to `unittest.mock.MagicMock`

### mocker Fixture

```python
@pytest.fixture
def mocker() -> Generator[_FallbackMocker, None, None]:
    """Fallback mocker fixture when pytest-mock is unavailable."""
    m = _FallbackMocker()
    try:
        yield m
    finally:
        m.stopall()  # Automatic cleanup
```

**Usage:**
```python
def test_with_mock(mocker):
    mock_fn = mocker.patch('module.function')
    mock_fn.return_value = 42
    
    result = call_module_function()
    assert result == 42
    mock_fn.assert_called_once()
```

---

## File System Fixtures

### temp_dir

```python
@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test isolation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
```

**Returns:** `pathlib.Path` object  
**Cleanup:** Automatic - directory deleted after test  
**Scope:** Function (new directory per test)  

**Usage:**
```python
def test_file_operations(temp_dir):
    test_file = temp_dir / "test.txt"
    test_file.write_text("content")
    assert test_file.exists()
    assert test_file.read_text() == "content"
```

### constitution_file

```python
@pytest.fixture
def constitution_file(temp_dir: Path) -> Path:
    """Create test constitution.yaml file."""
    constitution = {
        "name": "test_constitution",
        "version": "1.0.0",
        "principles": [
            {
                "id": "security_first",
                "description": "Security is paramount",
                "priority": "critical",
                "enforcement": "block",
            },
            {
                "id": "transparency",
                "description": "All actions must be auditable",
                "priority": "high",
                "enforcement": "warn_and_modify",
            },
            {
                "id": "efficiency",
                "description": "Optimize for performance",
                "priority": "medium",
                "enforcement": "warn",
            },
        ],
        "enforcement_levels": {
            "critical": {"action": "block", "log": True},
            "high": {"action": "warn_and_modify", "log": True},
            "medium": {"action": "warn", "log": True},
            "low": {"action": "log_only", "log": True},
        },
        "violation_handling": {
            "immediate_block": ["security_violation", "credential_leak"],
        },
    }
    
    const_file = temp_dir / "constitution.yaml"
    with open(const_file, "w") as f:
        yaml.dump(constitution, f)
    
    return const_file
```

**Returns:** `Path` to constitution.yaml  
**Dependencies:** `temp_dir`  

**Constitution Structure:**

#### Principles (3 defined)
1. **security_first** (critical, block)
   - Security is paramount
   - Blocks operations that violate security
   
2. **transparency** (high, warn_and_modify)
   - All actions must be auditable
   - Modifies actions to ensure auditability
   
3. **efficiency** (medium, warn)
   - Optimize for performance
   - Warns about inefficient operations

#### Enforcement Levels (4 defined)
- **critical** → block + log
- **high** → warn_and_modify + log
- **medium** → warn + log
- **low** → log_only

#### Violation Handling
- **immediate_block** → ["security_violation", "credential_leak"]

**Usage:**
```python
def test_constitution_loading(constitution_file):
    with open(constitution_file) as f:
        config = yaml.safe_load(f)
    
    assert config["name"] == "test_constitution"
    assert len(config["principles"]) == 3
    assert config["principles"][0]["id"] == "security_first"
    assert config["enforcement_levels"]["critical"]["action"] == "block"
```

### security_config_file

```python
@pytest.fixture
def security_config_file(temp_dir: Path) -> Path:
    """Create test security_hardening.yaml file."""
    config = {
        "least_privilege": {
            "agents": {
                "build_agent": {
                    "allowed_paths": ["build/**", "src/**", "gradle/**"],
                    "allowed_operations": ["read", "write", "execute"],
                    "credential_ttl_hours": 2,
                },
                "test_agent": {
                    "allowed_paths": ["test/**", "build/test/**"],
                    "allowed_operations": ["read", "execute"],
                    "credential_ttl_hours": 1,
                },
            }
        },
        "runtime_controls": {
            "max_build_duration_minutes": 60,
            "require_signature": True,
        },
    }
    
    sec_file = temp_dir / "security_hardening.yaml"
    with open(sec_file, "w") as f:
        yaml.dump(config, f)
    
    return sec_file
```

**Returns:** `Path` to security_hardening.yaml  
**Dependencies:** `temp_dir`  

**Security Configuration Structure:**

#### Least Privilege Agents
- **build_agent**
  - Paths: build/**, src/**, gradle/**
  - Operations: read, write, execute
  - Credential TTL: 2 hours
  
- **test_agent**
  - Paths: test/**, build/test/**
  - Operations: read, execute (no write)
  - Credential TTL: 1 hour

#### Runtime Controls
- **max_build_duration_minutes:** 60
- **require_signature:** true

**Usage:**
```python
def test_security_config(security_config_file):
    with open(security_config_file) as f:
        config = yaml.safe_load(f)
    
    build_agent = config["least_privilege"]["agents"]["build_agent"]
    assert "write" in build_agent["allowed_operations"]
    
    test_agent = config["least_privilege"]["agents"]["test_agent"]
    assert "write" not in test_agent["allowed_operations"]
    
    assert config["runtime_controls"]["require_signature"] is True
```

### capsule_storage

```python
@pytest.fixture
def capsule_storage(temp_dir: Path) -> Path:
    """Create capsule storage directory."""
    capsule_dir = temp_dir / "capsules"
    capsule_dir.mkdir()
    return capsule_dir
```

**Returns:** `Path` to capsules/ directory  
**Dependencies:** `temp_dir`  
**State:** Empty directory (created but unpopulated)  

**Usage:**
```python
def test_capsule_save(capsule_storage):
    capsule_path = capsule_storage / "test-capsule-001.json"
    capsule_data = {
        "capsule_id": "test-capsule-001",
        "tasks": ["clean", "build"],
    }
    
    with open(capsule_path, "w") as f:
        json.dump(capsule_data, f)
    
    assert capsule_path.exists()
    assert len(list(capsule_storage.glob("*.json"))) == 1
```

### audit_log_path

```python
@pytest.fixture
def audit_log_path(temp_dir: Path) -> Path:
    """Create audit log path."""
    audit_file = temp_dir / "audit.log"
    audit_file.touch()  # Create empty file
    return audit_file
```

**Returns:** `Path` to audit.log  
**Dependencies:** `temp_dir`  
**State:** Empty file (exists but has no content)  

**Usage:**
```python
def test_audit_logging(audit_log_path):
    # Append audit entry
    with open(audit_log_path, "a") as f:
        f.write("2024-01-15T10:30:00Z | ACTION | user123 | build\n")
    
    # Verify written
    content = audit_log_path.read_text()
    assert "ACTION" in content
    assert "user123" in content
```

---

## Data Fixtures

### sample_build_context

```python
@pytest.fixture
def sample_build_context() -> dict[str, Any]:
    """Sample build context for testing."""
    return {
        "project": "test-project",
        "tasks": ["clean", "build", "test"],
        "dependencies": {
            "compile": ["org.junit:junit:4.13.2"],
        },
        "cache_enabled": True,
        "parallel": False,
    }
```

**Returns:** Dictionary representing Gradle build context  
**Type:** Pure data fixture (no setup/teardown)  

**Structure:**
- **project:** Project name string
- **tasks:** List of Gradle tasks to execute
- **dependencies:** Dict of dependency scopes → artifact lists
- **cache_enabled:** Boolean for cache usage
- **parallel:** Boolean for parallel execution

**Usage:**
```python
def test_build_processing(sample_build_context):
    result = process_build(sample_build_context)
    assert result["project"] == "test-project"
    assert len(result["tasks"]) == 3
```

### sample_build_capsule_data

```python
@pytest.fixture
def sample_build_capsule_data() -> dict[str, Any]:
    """Sample build capsule data."""
    return {
        "capsule_id": "test-capsule-001",
        "tasks": ["clean", "compileJava", "test"],
        "inputs": {
            "src/main/java/Main.java": "abc123hash",
            "build.gradle": "def456hash",
        },
        "outputs": {
            "build/classes/Main.class": "output123hash",
            "build/reports/test.xml": "output456hash",
        },
        "metadata": {
            "timestamp": "2024-01-01T00:00:00Z",
            "duration_seconds": 45.2,
            "gradle_version": "8.5",
            "jdk_version": "17",
        },
    }
```

**Returns:** Dictionary representing build capsule  
**Type:** Pure data fixture  

**Structure:**
- **capsule_id:** Unique capsule identifier
- **tasks:** Executed Gradle tasks
- **inputs:** Input file → hash mapping
- **outputs:** Output file → hash mapping
- **metadata:** Build metadata (timestamp, duration, versions)

**Usage:**
```python
def test_capsule_creation(sample_build_capsule_data):
    capsule = BuildCapsule.from_dict(sample_build_capsule_data)
    assert capsule.capsule_id == "test-capsule-001"
    assert len(capsule.inputs) == 2
    assert capsule.metadata["gradle_version"] == "8.5"
```

### sample_security_violation

```python
@pytest.fixture
def sample_security_violation() -> dict[str, Any]:
    """Sample security violation data."""
    return {
        "violation_type": "unauthorized_path_access",
        "agent": "test_agent",
        "attempted_path": "/etc/passwd",
        "timestamp": "2024-01-01T00:00:00Z",
        "severity": "critical",
    }
```

**Returns:** Dictionary representing security violation  
**Type:** Pure data fixture  

**Structure:**
- **violation_type:** Type of security violation
- **agent:** Agent that caused violation
- **attempted_path:** Path that was accessed
- **timestamp:** When violation occurred (UTC)
- **severity:** critical/high/medium/low

**Usage:**
```python
def test_violation_handling(sample_security_violation):
    handler = SecurityViolationHandler()
    result = handler.process(sample_security_violation)
    
    assert result["blocked"] is True
    assert result["severity"] == "critical"
    assert "audit_logged" in result
```

### sample_temporal_law

```python
@pytest.fixture
def sample_temporal_law() -> dict[str, Any]:
    """Sample temporal law configuration."""
    return {
        "law_id": "test_law_001",
        "effective_from": "2024-01-01T00:00:00Z",
        "effective_until": None,
        "description": "Test security policy",
        "rules": [
            {
                "condition": "build_duration > 60",
                "action": "terminate",
                "priority": "high",
            }
        ],
    }
```

**Returns:** Dictionary representing temporal law  
**Type:** Pure data fixture  

**Structure:**
- **law_id:** Unique law identifier
- **effective_from:** UTC timestamp when law becomes active
- **effective_until:** UTC timestamp when law expires (None = permanent)
- **description:** Human-readable description
- **rules:** List of rule objects with condition/action/priority

**Usage:**
```python
def test_temporal_law_enforcement(sample_temporal_law):
    enforcer = TemporalLawEnforcer()
    
    # Build context exceeds duration limit
    build_context = {"build_duration": 75}
    result = enforcer.apply(sample_temporal_law, build_context)
    
    assert result["enforced"] is True
    assert result["action"] == "terminate"
    assert result["triggered_rule"]["priority"] == "high"
```

---

## System Mock Fixtures

### mock_deliberation_engine

```python
@pytest.fixture
def mock_deliberation_engine(mocker):
    """Mock DeliberationEngine for testing."""
    mock = mocker.MagicMock()
    mock.deliberate.return_value = {
        "optimized_order": ["clean", "build", "test"],
        "reasoning": {
            "optimization_applied": True,
            "confidence": 0.95,
        },
    }
    return mock
```

**Returns:** MagicMock with configured `deliberate()` method  
**Dependencies:** `mocker`  

**Mock Configuration:**
- `deliberate()` returns dictionary with:
  - `optimized_order`: List of task names
  - `reasoning`: Dict with optimization details

**Usage:**
```python
def test_with_deliberation(mock_deliberation_engine):
    tasks = ["test", "build", "clean"]
    result = mock_deliberation_engine.deliberate(tasks)
    
    assert result["optimized_order"] == ["clean", "build", "test"]
    assert result["reasoning"]["confidence"] == 0.95
    mock_deliberation_engine.deliberate.assert_called_once_with(tasks)
```

### mock_four_laws

```python
@pytest.fixture
def mock_four_laws(mocker):
    """Mock FourLaws for testing."""
    mock = mocker.MagicMock()
    mock.validate_action.return_value = (True, "Action allowed")
    return mock
```

**Returns:** MagicMock with configured `validate_action()` method  
**Dependencies:** `mocker`  

**Mock Configuration:**
- `validate_action()` returns: `(True, "Action allowed")`

**Usage:**
```python
def test_with_four_laws(mock_four_laws):
    is_allowed, reason = mock_four_laws.validate_action("test_action", {})
    
    assert is_allowed is True
    assert reason == "Action allowed"
    
    # Test with denial
    mock_four_laws.validate_action.return_value = (False, "Blocked by Law 1")
    is_allowed, reason = mock_four_laws.validate_action("dangerous_action", {})
    assert is_allowed is False
```

### mock_identity_manager

```python
@pytest.fixture
def mock_identity_manager(mocker):
    """Mock IdentityManager for testing."""
    mock = mocker.MagicMock()
    mock.verify_identity.return_value = True
    return mock
```

**Returns:** MagicMock with configured `verify_identity()` method  
**Dependencies:** `mocker`  

**Mock Configuration:**
- `verify_identity()` returns: `True`

**Usage:**
```python
def test_with_identity(mock_identity_manager):
    verified = mock_identity_manager.verify_identity("user123")
    assert verified is True
    
    # Test rejection
    mock_identity_manager.verify_identity.return_value = False
    verified = mock_identity_manager.verify_identity("unknown_user")
    assert verified is False
```

### mock_audit_function

```python
@pytest.fixture
def mock_audit_function(mocker):
    """Mock audit function from cognition.audit."""
    return mocker.patch("cognition.audit.audit")
```

**Returns:** MagicMock patching `cognition.audit.audit`  
**Dependencies:** `mocker`  

**Usage:**
```python
def test_with_audit(mock_audit_function):
    from cognition import audit
    
    # Perform action that should audit
    perform_sensitive_action()
    
    # Verify audit called
    mock_audit_function.assert_called_once()
    call_args = mock_audit_function.call_args
    assert call_args[0][0] == "sensitive_action"
```

---

## Fixture Dependency Graph

```
mocker (independent)
    ↓
mock_deliberation_engine
mock_four_laws
mock_identity_manager
mock_audit_function

temp_dir (independent)
    ↓
constitution_file
security_config_file
capsule_storage
audit_log_path

# Data fixtures (independent)
sample_build_context
sample_build_capsule_data
sample_security_violation
sample_temporal_law
```

---

## Best Practices

### ✅ DO
- Use `temp_dir` for file system isolation
- Combine fixtures: `def test_x(constitution_file, mock_four_laws):`
- Verify mock calls with `mock.assert_called_once()`
- Load YAML files with `yaml.safe_load()`
- Use descriptive test names

### ❌ DON'T
- Modify fixture return values in tests (create copies if needed)
- Rely on fixture execution order
- Share state between tests
- Skip cleanup (fixtures handle it)
- Hardcode paths (use fixtures)

---

## Next Steps

1. Read `07_STRESS_TESTING.md` for stress test patterns
2. See `09_INTEGRATION_TESTING.md` for integration strategies
3. Check `05_CORE_SYSTEM_TESTS.md` for core system patterns

---

**See Also:**
- `tests/gradle_evolution/conftest.py` - Source code
- `tests/gradle_evolution/` - Test modules using these fixtures
- `04_FIXTURE_REFERENCE.md` - General fixture documentation
