"""
Pytest Configuration for E2E Tests

Provides fixtures and configuration for E2E test execution.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from e2e.config.e2e_config import get_config
from e2e.fixtures.mocks import (
    mock_email,
    mock_geolocation,
    mock_huggingface,
    mock_openai,
    reset_all_mocks,
)
from e2e.fixtures.test_data import (
    TEST_AUDIT_LOGS,
    TEST_KNOWLEDGE_BASE,
    TEST_PERSONA_STATES,
)
from e2e.fixtures.test_users import get_admin_user, get_regular_user
from e2e.orchestration.health_checks import HealthChecker
from e2e.orchestration.service_manager import ServiceManager
from e2e.orchestration.setup_teardown import E2ETestEnvironment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# ==================== Configuration Fixtures ====================


@pytest.fixture(scope="session")
def e2e_config():
    """Get E2E configuration for tests."""
    return get_config()


# ==================== Environment Fixtures ====================


@pytest.fixture(scope="session")
def e2e_environment():
    """Set up E2E test environment for entire session."""
    env = E2ETestEnvironment()
    env.setup()
    yield env
    env.teardown()


@pytest.fixture(scope="function")
def test_temp_dir(e2e_environment):
    """Get temporary directory for test."""
    return e2e_environment.get_temp_dir()


# ==================== Service Fixtures ====================


@pytest.fixture(scope="session")
def service_manager(e2e_config):
    """Service manager fixture for entire test session."""
    manager = ServiceManager(e2e_config)
    # Note: Don't start services by default in session scope
    # Individual tests should start services as needed
    yield manager
    manager.stop_all()


@pytest.fixture(scope="function")
def running_services(service_manager):
    """Start all services for a test function."""
    service_manager.start_all(wait_for_health=True)
    yield service_manager
    service_manager.stop_all()


@pytest.fixture(scope="function")
def health_checker():
    """Health checker fixture."""
    return HealthChecker()


# ==================== User Fixtures ====================


@pytest.fixture
def admin_user():
    """Admin user fixture."""
    return get_admin_user()


@pytest.fixture
def regular_user():
    """Regular user fixture."""
    return get_regular_user()


# ==================== Test Data Fixtures ====================


@pytest.fixture
def test_persona_state():
    """Test AI persona state."""
    return TEST_PERSONA_STATES["neutral"].copy()


@pytest.fixture
def test_knowledge_base():
    """Test knowledge base data."""
    return TEST_KNOWLEDGE_BASE.copy()


@pytest.fixture
def test_audit_logs():
    """Test audit log data."""
    return TEST_AUDIT_LOGS.copy()


# ==================== Mock Service Fixtures ====================


@pytest.fixture(scope="function", autouse=True)
def reset_mocks():
    """Reset all mock services before each test."""
    reset_all_mocks()
    yield
    reset_all_mocks()


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client fixture."""
    return mock_openai


@pytest.fixture
def mock_huggingface_client():
    """Mock HuggingFace client fixture."""
    return mock_huggingface


@pytest.fixture
def mock_email_service():
    """Mock email service fixture."""
    return mock_email


@pytest.fixture
def mock_geolocation_service():
    """Mock geolocation service fixture."""
    return mock_geolocation


# ==================== Pytest Configuration ====================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "e2e: Mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "gui: Mark test as GUI test"
    )
    config.addinivalue_line(
        "markers", "api: Mark test as API test"
    )
    config.addinivalue_line(
        "markers", "council_hub: Mark test as Council Hub test"
    )
    config.addinivalue_line(
        "markers", "triumvirate: Mark test as Triumvirate test"
    )
    config.addinivalue_line(
        "markers", "watch_tower: Mark test as Watch Tower test"
    )
    config.addinivalue_line(
        "markers", "tarl: Mark test as TARL enforcement test"
    )
    config.addinivalue_line(
        "markers", "security: Mark test as security test"
    )
    config.addinivalue_line(
        "markers", "slow: Mark test as slow-running"
    )
    config.addinivalue_line(
        "markers", "integration: Mark test as integration test"
    )
    # Additional E2E markers
    config.addinivalue_line(
        "markers", "batch: Mark test as batch processing test"
    )
    config.addinivalue_line(
        "markers", "temporal: Mark test as Temporal workflow test"
    )
    config.addinivalue_line(
        "markers", "memory: Mark test as memory system test"
    )
    config.addinivalue_line(
        "markers", "knowledge: Mark test as knowledge base test"
    )
    config.addinivalue_line(
        "markers", "rag: Mark test as RAG pipeline test"
    )
    config.addinivalue_line(
        "markers", "agents: Mark test as multi-agent test"
    )
    config.addinivalue_line(
        "markers", "failover: Mark test as failover test"
    )
    config.addinivalue_line(
        "markers", "recovery: Mark test as recovery test"
    )
    config.addinivalue_line(
        "markers", "circuit_breaker: Mark test as circuit breaker test"
    )
    config.addinivalue_line(
        "markers", "adversarial: Mark test as adversarial/security test"
    )
    config.addinivalue_line(
        "markers", "batch: Mark test as batch processing test"
    )
    config.addinivalue_line(
        "markers", "memory: Mark test as memory system test"
    )
    config.addinivalue_line(
        "markers", "knowledge: Mark test as knowledge base test"
    )
    config.addinivalue_line(
        "markers", "rag: Mark test as RAG pipeline test"
    )
    config.addinivalue_line(
        "markers", "agents: Mark test as multi-agent test"
    )
    config.addinivalue_line(
        "markers", "failover: Mark test as failover test"
    )
    config.addinivalue_line(
        "markers", "recovery: Mark test as recovery test"
    )
    config.addinivalue_line(
        "markers", "circuit_breaker: Mark test as circuit breaker test"
    )
    config.addinivalue_line(
        "markers", "adversarial: Mark test as adversarial security test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test items during collection."""
    # Auto-mark all tests in e2e/ directory as e2e tests
    for item in items:
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
