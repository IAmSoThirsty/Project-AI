"""Test configuration and fixtures"""

import asyncio
from typing import AsyncGenerator

import pytest
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
    return {"X-API-Key": "test-api-key"}
