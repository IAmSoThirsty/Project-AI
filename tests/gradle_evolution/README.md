# Gradle Evolution Test Suite

Comprehensive pytest test suite for the Gradle Evolution substrate, validating constitutional enforcement, cognitive deliberation, build capsules, security policies, audit integration, and API functionality.

## Test Structure

```
tests/gradle_evolution/
├── conftest.py                 # Shared fixtures and configuration
├── test_constitutional.py      # Constitutional engine, enforcer, temporal law
├── test_cognition.py          # Build cognition and state integration
├── test_capsules.py           # Capsule engine and replay engine
├── test_security.py           # Security engine and policy scheduler
├── test_audit.py              # Audit integration and accountability
├── test_api.py                # Verifiability API and documentation
└── test_integration.py        # End-to-end integration tests
```

## Test Coverage

### Constitutional Tests (277 lines)
- Constitutional engine initialization and configuration
- Principle validation and enforcement
- Violation logging and history tracking
- Temporal law activation and lifecycle
- Law registry persistence

**Test Classes:**
- `TestConstitutionalEngine` - 6 tests
- `TestConstitutionalEnforcer` - 5 tests
- `TestTemporalLaw` - 5 tests
- `TestTemporalLawRegistry` - 6 tests

### Cognition Tests (261 lines)
- Build plan deliberation and optimization
- Cognitive boundary validation
- Pattern analysis and learning
- Build state recording and persistence
- Metrics and statistics

**Test Classes:**
- `TestBuildCognitionEngine` - 8 tests
- `TestBuildStateIntegration` - 10 tests

### Capsule Tests (303 lines)
- Build capsule creation and immutability
- Merkle tree computation and verification
- Capsule persistence and retrieval
- Replay engine functionality
- Forensic analysis and comparison

**Test Classes:**
- `TestBuildCapsule` - 7 tests
- `TestCapsuleEngine` - 9 tests
- `TestReplayEngine` - 7 tests

### Security Tests (299 lines)
- Security context management
- Path and operation validation
- Access logging and denied operations
- Credential TTL checking
- Policy scheduling and evaluation

**Test Classes:**
- `TestSecurityContext` - 1 test
- `TestSecurityEngine` - 12 tests
- `TestSecurityPolicy` - 2 tests
- `TestPolicyScheduler` - 8 tests

### Audit Tests (351 lines)
- Build event auditing
- Audit buffer management
- Accountability tracking
- Action recording and retrieval
- Compliance reporting

**Test Classes:**
- `TestBuildAuditIntegration` - 9 tests
- `TestActionRecord` - 2 tests
- `TestAccountabilityTracker` - 8 tests

### API Tests (362 lines)
- REST API endpoints (health, capsules, audit)
- Verifiability and proof generation
- CORS and error handling
- OpenAPI specification generation
- Documentation export (Markdown, Postman)

**Test Classes:**
- `TestVerifiabilityAPI` - 11 tests
- `TestAPIDocumentation` - 2 tests
- `TestDocumentationGenerator` - 8 tests

### Integration Tests (337 lines)
- Complete build lifecycle workflow
- Security violation handling
- Capsule replay workflow
- Multi-build pattern learning
- Error recovery and resilience
- Performance and scalability

**Test Classes:**
- `TestFullBuildWorkflow` - 4 tests
- `TestAPIIntegration` - 1 test
- `TestErrorRecovery` - 4 tests
- `TestPerformanceAndScalability` - 2 tests

## Running Tests

### Run All Gradle Evolution Tests
```bash
pytest tests/gradle_evolution/ -v
```

### Run Specific Test File
```bash
pytest tests/gradle_evolution/test_constitutional.py -v
pytest tests/gradle_evolution/test_integration.py -v
```

### Run Specific Test Class
```bash
pytest tests/gradle_evolution/test_capsules.py::TestBuildCapsule -v
```

### Run Specific Test
```bash
pytest tests/gradle_evolution/test_security.py::TestSecurityEngine::test_validate_path_access_allowed -v
```

### Run With Coverage
```bash
pytest tests/gradle_evolution/ --cov=gradle_evolution --cov-report=html
```

### Run With Verbose Output
```bash
pytest tests/gradle_evolution/ -vv -s
```

## Fixtures

The `conftest.py` provides shared fixtures for all tests:

### File System Fixtures
- `temp_dir` - Temporary directory for test isolation
- `constitution_file` - Test constitution.yaml
- `security_config_file` - Test security_hardening.yaml
- `capsule_storage` - Capsule storage directory
- `audit_log_path` - Audit log file path

### Mock Fixtures
- `mock_deliberation_engine` - Mock DeliberationEngine
- `mock_four_laws` - Mock FourLaws validator
- `mock_audit_function` - Mock audit function

### Data Fixtures
- `sample_build_context` - Build context dictionary
- `sample_build_capsule_data` - Capsule data dictionary
- `sample_security_violation` - Security violation data
- `sample_temporal_law` - Temporal law configuration

## Test Patterns

### Pattern 1: Initialization Tests
```python
def test_initialization(self, fixture):
    """Test component initializes correctly."""
    component = Component(config=fixture)
    assert component.config is not None
```

### Pattern 2: Validation Tests
```python
def test_validate_allowed_action(self, fixture):
    """Test validation allows compliant actions."""
    is_allowed, reason = component.validate(action, context)
    assert is_allowed
```

### Pattern 3: Persistence Tests
```python
def test_persistence(self, temp_dir):
    """Test data persistence to disk."""
    storage = temp_dir / "data.json"
    component = Component(storage_path=storage)
    component.save()
    
    new_component = Component(storage_path=storage)
    new_component.load()
    assert new_component.data == component.data
```

### Pattern 4: Mock Integration Tests
```python
@patch("module.function")
def test_integration(self, mock_function, fixture):
    """Test integration with mocked dependencies."""
    component = Component(fixture)
    component.execute()
    mock_function.assert_called_once()
```

## Dependencies

Tests require the following packages:
- `pytest>=7.4.4` - Test framework
- `pytest-mock>=3.12.0` - Mocking utilities
- `pyyaml>=6.0` - YAML parsing (for config fixtures)
- `flask>=3.0.0` - For API tests

All test dependencies should be in `requirements-dev.txt`.

## Test Data Isolation

All tests use:
- `tempfile.TemporaryDirectory()` for file operations
- Separate fixtures per test via `@pytest.fixture`
- No shared state between test classes
- Cleanup handled automatically by pytest

## Integration with Project-AI

Tests validate integration with existing Project-AI components:

### Constitutional Integration
- Uses `policies/constitution.yaml` structure
- Validates against existing governance principles
- Integrates with FourLaws validation

### Cognition Integration
- Uses `project_ai.engine.cognition.deliberation_engine`
- Validates boundary checks via `cognition.boundary`
- Uses invariant checker from `cognition.invariants`

### Audit Integration
- Uses `cognition.audit.audit` function
- Follows existing audit event patterns
- Compatible with audit log format

### Security Integration
- Uses `config/security_hardening.yaml`
- Follows least privilege patterns
- Integrates with existing security agents

## Continuous Integration

Tests are designed to run in CI/CD pipelines:
- No external dependencies required
- All data mocked or fixture-based
- Fast execution (< 5 seconds for full suite)
- Clear failure messages

## Adding New Tests

When adding new tests:

1. **Follow existing patterns** - Use similar structure to existing tests
2. **Use fixtures** - Add to `conftest.py` for shared setup
3. **Test isolation** - Use `temp_dir` fixture for file operations
4. **Mock external deps** - Patch external calls with `@patch` or `mocker`
5. **Document tests** - Add docstrings explaining what's tested
6. **Test both paths** - Include positive and negative test cases

Example:
```python
class TestNewComponent:
    """Test NewComponent functionality."""
    
    def test_initialization(self, fixture):
        """Test component initializes."""
        component = NewComponent(fixture)
        assert component is not None
    
    def test_success_case(self, fixture):
        """Test successful operation."""
        result = component.operate()
        assert result.success
    
    def test_failure_case(self, fixture):
        """Test handles errors gracefully."""
        with pytest.raises(ValueError):
            component.operate(invalid_input)
```

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'gradle_evolution'`:
- Ensure gradle-evolution module is in PYTHONPATH
- Run tests from project root: `cd /path/to/Project-AI && pytest tests/gradle_evolution/`

### Fixture Errors
If fixtures are not found:
- Check `conftest.py` is in the same directory
- Verify fixture names match usage

### Mock Errors
If mocks aren't working:
- Install pytest-mock: `pip install pytest-mock`
- Use correct patch path (where it's imported, not defined)

## Test Statistics

- **Total Tests**: ~90+ tests across 7 files
- **Total Lines**: 2,489 lines of test code
- **Coverage Target**: 80%+ for all gradle-evolution modules
- **Execution Time**: < 10 seconds for full suite
- **Test Ratio**: ~3-4 tests per module function

## Future Enhancements

Planned test improvements:
- [ ] Property-based testing with Hypothesis
- [ ] Performance benchmarks with pytest-benchmark
- [ ] Mutation testing with mutmut
- [ ] Contract testing for API endpoints
- [ ] Load testing for scalability validation
