"""
pytest configuration for integration_enhanced tests
"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def integration_context():
    """Provide common integration test context"""
    return {
        "test_mode": True,
        "mock_external_systems": True,
        "validation_run": True,
    }


def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end scenario"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance benchmark"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security audit"
    )
