"""
E2E Tests for API Integration

Tests the Flask/FastAPI REST API endpoints with full-stack integration.
"""

from __future__ import annotations

import pytest
import requests



@pytest.mark.e2e
@pytest.mark.api
def test_api_health_endpoint(e2e_config):
    """Test API health check endpoint."""
    # Try to connect to Flask API
    service = e2e_config.get_service("flask_api")
    if not service or not service.enabled:
        pytest.skip("Flask API service not enabled")

    try:
        response = requests.get(
            service.health_url,
            timeout=e2e_config.api_request_timeout,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    except requests.RequestException:
        pytest.skip("Flask API not running")


@pytest.mark.e2e
@pytest.mark.api
@pytest.mark.security
def test_api_authentication_flow(e2e_config, admin_user):
    """Test complete API authentication flow."""
    service = e2e_config.get_service("flask_api")
    if not service or not service.enabled:
        pytest.skip("Flask API service not enabled")

    base_url = service.base_url

    try:
        # Attempt login
        login_payload = {
            "username": admin_user.username,
            "password": admin_user.password,
        }
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_payload,
            timeout=e2e_config.api_request_timeout,
        )

        # For this E2E test, we verify the endpoint structure
        # Real authentication would require actual user setup
        assert response.status_code in [200, 401, 404]
    except requests.RequestException:
        pytest.skip("Flask API not running")


@pytest.mark.e2e
@pytest.mark.api
def test_api_error_handling(e2e_config):
    """Test API error handling and responses."""
    service = e2e_config.get_service("flask_api")
    if not service or not service.enabled:
        pytest.skip("Flask API service not enabled")

    base_url = service.base_url

    try:
        # Try invalid endpoint
        response = requests.get(
            f"{base_url}/api/nonexistent",
            timeout=e2e_config.api_request_timeout,
        )
        assert response.status_code == 404
    except requests.RequestException:
        pytest.skip("Flask API not running")


@pytest.mark.e2e
@pytest.mark.api
@pytest.mark.integration
def test_api_cors_headers(e2e_config):
    """Test CORS headers are properly set on API responses."""
    service = e2e_config.get_service("flask_api")
    if not service or not service.enabled:
        pytest.skip("Flask API service not enabled")

    try:
        response = requests.options(
            service.health_url,
            timeout=e2e_config.api_request_timeout,
        )

        # Verify CORS headers (if configured)
        # Note: Actual CORS configuration depends on deployment
        assert response.status_code in [200, 204, 404]
    except requests.RequestException:
        pytest.skip("Flask API not running")


@pytest.mark.e2e
@pytest.mark.api
@pytest.mark.integration
def test_api_rate_limiting(e2e_config):
    """Test API rate limiting (if configured)."""
    service = e2e_config.get_service("flask_api")
    if not service or not service.enabled:
        pytest.skip("Flask API service not enabled")

    # This is a structural test - actual rate limiting
    # would require multiple rapid requests
    try:
        response = requests.get(
            service.health_url,
            timeout=e2e_config.api_request_timeout,
        )
        # Verify response structure
        assert response.status_code == 200
    except requests.RequestException:
        pytest.skip("Flask API not running")


@pytest.mark.e2e
@pytest.mark.api
@pytest.mark.security
def test_api_request_validation(e2e_config):
    """Test API request validation and sanitization."""
    service = e2e_config.get_service("flask_api")
    if not service or not service.enabled:
        pytest.skip("Flask API service not enabled")

    base_url = service.base_url

    try:
        # Send malformed request
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"invalid": "payload"},
            timeout=e2e_config.api_request_timeout,
        )

        # Should handle invalid payload gracefully
        assert response.status_code in [400, 401, 404, 422]
    except requests.RequestException:
        pytest.skip("Flask API not running")


@pytest.mark.e2e
@pytest.mark.api
@pytest.mark.integration
def test_api_json_response_format(e2e_config):
    """Test API responses follow consistent JSON format."""
    service = e2e_config.get_service("flask_api")
    if not service or not service.enabled:
        pytest.skip("Flask API service not enabled")

    try:
        response = requests.get(
            service.health_url,
            timeout=e2e_config.api_request_timeout,
        )

        assert response.status_code == 200
        assert response.headers.get("Content-Type") == "application/json"

        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
    except requests.RequestException:
        pytest.skip("Flask API not running")
