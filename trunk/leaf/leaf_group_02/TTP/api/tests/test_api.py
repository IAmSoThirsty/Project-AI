# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_api.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_api.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Basic test suite for TTP API.

Run with: pytest
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.models.models import User
from app.services.auth import get_password_hash
from main import app

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create database tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create a test user."""
    db = TestingSessionLocal()
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        display_name="Test User",
        role="creator",
        status="active",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()


@pytest.fixture
def auth_token(test_user):
    """Get authentication token for test user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpassword123"}
    )
    return response.json()["access_token"]


# Test Health Endpoints
def test_health_check():
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_check():
    """Test readiness check endpoint."""
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


# Test Authentication
def test_register_user():
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123",
            "display_name": "New User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["role"] == "viewer"


def test_register_duplicate_username():
    """Test registration with duplicate username."""
    # First registration
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicate",
            "email": "user1@example.com",
            "password": "password123"
        }
    )

    # Second registration with same username
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicate",
            "email": "user2@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 409


def test_login_success(test_user):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(test_user):
    """Test login with wrong password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401


# Test User Endpoints
def test_get_current_user(auth_token):
    """Test getting current user profile."""
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


def test_get_current_user_unauthorized():
    """Test getting current user without authentication."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 403  # No credentials provided


def test_update_current_user(auth_token):
    """Test updating current user profile."""
    response = client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"display_name": "Updated Name"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["display_name"] == "Updated Name"


# Test Pack Endpoints
def test_list_packs_empty():
    """Test listing packs when none exist."""
    response = client.get("/api/v1/packs")
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["pagination"]["total_items"] == 0


def test_create_pack_unauthorized():
    """Test creating pack without authentication."""
    response = client.post(
        "/api/v1/packs",
        json={
            "name": "Test Pack",
            "version": "1.0.0",
            "description": "A test texture pack for testing purposes",
            "category": "test",
            "quality_tier": "standard",
            "license": "MIT",
            "tags": ["test"]
        }
    )
    assert response.status_code == 403


def test_create_pack_success(auth_token):
    """Test creating a pack."""
    response = client.post(
        "/api/v1/packs",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Test Pack",
            "version": "1.0.0",
            "description": "A test texture pack for testing purposes",
            "category": "test",
            "quality_tier": "standard",
            "license": "MIT",
            "tags": ["test", "demo"],
            "metadata": {"engine": "unity"}
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Pack"
    assert data["slug"] == "test-pack"
    assert data["status"] == "draft"


def test_get_pack_not_found():
    """Test getting non-existent pack."""
    from uuid import uuid4
    fake_id = str(uuid4())
    response = client.get(f"/api/v1/packs/{fake_id}")
    assert response.status_code == 404


# Test Metrics Endpoint
def test_metrics_endpoint():
    """Test Prometheus metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    # Metrics should be in Prometheus text format
    assert "python_info" in response.text or "process_" in response.text
