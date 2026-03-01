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
    assert data["service"] == "Autonomous Negotiation Agent Infrastructure"
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
    assert "service_autonomous_negotiation_agent_infrastructure" in response.text
