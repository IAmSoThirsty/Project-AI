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
"""Test main application"""

import pytest
from fastapi.testclient import TestClient

from api.main import app


def test_root_endpoint():
    """Test root endpoint"""
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Autonomous Incident Reflex System"
    assert data["version"] == "1.0.0"
    assert data["status"] == "operational"


def test_health_check():
    """Test health check endpoint"""
    client = TestClient(app)
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_metrics_endpoint():
    """Test Prometheus metrics endpoint"""
    client = TestClient(app)
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "service_autonomous_incident_reflex_system" in response.text
