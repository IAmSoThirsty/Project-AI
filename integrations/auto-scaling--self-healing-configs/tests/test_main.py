import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: auto-scaling--self-healing-configs / test_main.py
# ============================================================================ #
"""Test main application"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_root_endpoint():
    """Test root endpoint"""
    client = TestClient(app)
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Auto-scaling & self-healing configs"
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
    assert "service_auto_scaling_&_self_healing_configs" in response.text
