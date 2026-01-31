# Project AI - End-to-End Test Suite

## Overview

This directory contains **comprehensive, production-grade end-to-end (E2E) test coverage** for the entire Project AI monolith, including all fully integrated subsystems and the Trading Hub integration.

## Test Coverage

### 1. Full-Stack Scenario Tests
- **UI Layer**: Leather Book Dashboard, PyQt6 GUI interactions
- **Service Layer**: Flask/FastAPI REST APIs, service orchestration
- **Data Persistence**: JSON storage, state management, data integrity
- **AI/ML Components**: OpenAI integration, HuggingFace models, ML pipelines
- **Third-Party Integrations**: External APIs, service dependencies

### 2. Subsystem Integration Tests
- **Council Hub**: Agent coordination and message routing
- **Triumvirate**: Galahad (ethics), Cerberus (security), CodexDeus (orchestration)
- **Global Watch Tower**: Event monitoring and audit trail propagation
- **TARL Runtime**: Policy evaluation and enforcement
- **Cognition Kernel**: Secure agent operation routing

### 3. Comprehensive Scenario Coverage
- **Happy Path**: Normal user workflows and AI agent operations
- **Failure Scenarios**: Error handling, degradation, recovery
- **Security Boundaries**: Permission checks, authentication, authorization
- **Policy Enforcement**: Four Laws validation, command overrides, Black Vault
- **Event Propagation**: Audit logging, Global Watch Tower triggers

### 4. Validation Targets
- **State Transitions**: Correct state changes across components
- **Event Log Integrity**: Complete audit trail with no gaps
- **Business Invariants**: System constraints and rules enforcement
- **Observable Behavior**: User-visible and system-level outcomes

## Directory Structure

```
e2e/
├── config/                      # Test configuration and environment setup
│   ├── e2e_config.py           # Main E2E test configuration
│   └── test_environments.yaml   # Environment-specific settings
│
├── fixtures/                    # Test data and reusable fixtures
│   ├── test_users.py           # User account fixtures
│   ├── test_data.py            # Sample data for tests
│   └── mocks.py                # Mock objects and services
│
├── orchestration/               # Service lifecycle management
│   ├── service_manager.py      # Start/stop critical services
│   ├── setup_teardown.py       # Test environment setup/cleanup
│   └── health_checks.py        # Service health verification
│
├── scenarios/                   # E2E test scenarios by subsystem
│   ├── test_gui_workflows.py           # GUI E2E tests
│   ├── test_api_integration.py         # API E2E tests
│   ├── test_council_hub_e2e.py         # Council Hub integration
│   ├── test_triumvirate_e2e.py         # Triumvirate workflows
│   ├── test_watch_tower_e2e.py         # Global Watch Tower
│   ├── test_tarl_enforcement_e2e.py    # TARL policy tests
│   ├── test_security_boundaries_e2e.py # Security & permissions
│   ├── test_ai_ml_pipeline_e2e.py      # AI/ML integrations
│   ├── test_data_persistence_e2e.py    # Data layer tests
│   └── test_failure_scenarios_e2e.py   # Failure & recovery
│
├── utils/                       # Helper functions and utilities
│   ├── assertions.py           # Custom E2E assertions
│   ├── test_helpers.py         # Common test utilities
│   └── reporting.py            # Test result reporting
│
└── reports/                     # Test execution reports
    ├── coverage/               # Coverage reports
    └── results/                # Test result artifacts
```

## Running E2E Tests

### Quick Start

```bash
# Run all E2E tests
pytest e2e/ -v --tb=short

# Run specific subsystem tests
pytest e2e/scenarios/test_council_hub_e2e.py -v

# Run with coverage
pytest e2e/ -v --cov=. --cov-report=html --cov-report=term
```

### Test Markers

E2E tests are organized with pytest markers:

```bash
# Run only E2E tests
pytest -m e2e

# Run GUI E2E tests
pytest -m "e2e and gui"

# Run API E2E tests  
pytest -m "e2e and api"

# Run security E2E tests
pytest -m "e2e and security"

# Skip slow E2E tests
pytest -m "e2e and not slow"
```

### CI/CD Integration

E2E tests are integrated into the CI pipeline via `.github/workflows/ci.yml`:

```yaml
- name: Run E2E Tests
  run: |
    pytest e2e/ -v --cov=. --cov-report=xml --cov-report=html
```

## Test Requirements

### Dependencies

All dependencies are specified in `requirements.txt`:

```
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
pytest-timeout>=2.0.0
pytest-qt>=4.2.0  # For GUI testing
```

### Environment Setup

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Configure test environment**:
   ```bash
   # Set required API keys
   export OPENAI_API_KEY=sk-...
   export HUGGINGFACE_API_KEY=hf_...
   ```

3. **Initialize test database**:
   ```bash
   python e2e/orchestration/setup_teardown.py --init
   ```

## Writing E2E Tests

### Test Pattern

```python
import pytest
from e2e.fixtures.test_users import admin_user
from e2e.orchestration.service_manager import ServiceManager
from e2e.utils.assertions import assert_state_transition


@pytest.mark.e2e
@pytest.mark.council_hub
def test_council_hub_agent_coordination(service_manager):
    """E2E test for Council Hub agent coordination and message routing."""
    # Arrange: Set up test environment
    service_manager.start_all()
    agent_a = service_manager.register_agent("agent_a")
    agent_b = service_manager.register_agent("agent_b")
    
    # Act: Execute scenario
    result = agent_a.send_message(agent_b, "test_message")
    
    # Assert: Validate outcomes
    assert result.status == "success"
    assert_state_transition(agent_b, "idle", "processing")
    
    # Cleanup
    service_manager.stop_all()
```

### Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Setup/Teardown**: Use fixtures for consistent test environment setup
3. **Explicit Assertions**: Validate all expected outcomes explicitly
4. **Timeout Protection**: Use `@pytest.mark.timeout()` for long-running tests
5. **Error Messages**: Provide clear failure messages for debugging
6. **Documentation**: Document the scenario and expected behavior

## Troubleshooting

### Common Issues

1. **Service startup failures**: Check logs in `e2e/reports/logs/`
2. **Port conflicts**: Ensure test ports are available (5000, 5001, etc.)
3. **Missing dependencies**: Run `pip install -r requirements.txt`
4. **Environment variables**: Verify `.env` file is configured

### Debug Mode

```bash
# Run with verbose output
pytest e2e/ -vv --tb=long

# Run with debug logging
pytest e2e/ -v --log-cli-level=DEBUG

# Run single test with debugging
pytest e2e/scenarios/test_council_hub_e2e.py::test_specific_scenario -vv --pdb
```

## Coverage Requirements

E2E tests must maintain:
- **Overall Coverage**: ≥80% of critical paths
- **Integration Points**: 100% of subsystem boundaries
- **Security Checks**: 100% of permission boundaries
- **Audit Events**: 100% of Global Watch Tower triggers

Coverage is enforced in CI and must pass for merges.

## Contributing

When adding new E2E tests:

1. Follow the established directory structure
2. Use appropriate pytest markers
3. Add fixtures to `fixtures/` for reusability
4. Update this README with new test categories
5. Ensure tests pass locally before pushing
6. Include test documentation in docstrings

## Contact

For questions or issues with E2E tests, please:
- Open an issue on GitHub
- Tag with `e2e-tests` label
- Provide test output and logs
