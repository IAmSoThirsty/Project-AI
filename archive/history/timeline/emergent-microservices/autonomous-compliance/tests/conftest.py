# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-10 | TIME: 21:02               #
# COMPLIANCE: Regulator-Ready / UTF-8                                          #
# ============================================================================ #

# Date: 2026-03-10 | Time: 20:37 | Status: Active | Tier: Master
#                                           [2026-03-10 18:58]
#                                          Productivity: Active
# ============================================================================ #
#                                                            DATE: 2026-03-10 #
#                                                          TIME: 15:01:56 PST #
#                                                        PRODUCTIVITY: Active #
# ============================================================================ #

#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""Test configuration and fixtures"""

import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient

from api.main import app
from archive.history.timeline.emergent-microservices.ai-mutation-governance-firewall.app.repository import database


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
    return {"X-API-Key": "test-api-key"}
