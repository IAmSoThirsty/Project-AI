"""Chaos Engineering Tests for Project-AI"""

import httpx
import pytest


@pytest.mark.chaos
class TestChaosEngineering:
    @pytest.mark.asyncio
    async def test_system_resilience(self):
        """Test system handles failures gracefully"""
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:5000/health/live", timeout=10.0)
            assert response.status_code == 200
