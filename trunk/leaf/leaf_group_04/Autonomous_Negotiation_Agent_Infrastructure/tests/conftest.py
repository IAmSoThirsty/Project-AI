# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / conftest.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / conftest.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""Test configuration and fixtures"""
import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient

from app.main import app
from app.repository import database


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db():
    """Database fixture with cleanup"""
    await database.connect()
    yield database
    # Cleanup
database.data.clear()
await database.disconnect()


@pytest.fixture
def client() -> TestClient:
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict:
    """Authentication headers for testing"""
    return {
"X-API-Key": "test-api-key"
}
