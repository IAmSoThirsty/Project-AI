"""
Test User Fixtures for E2E Tests

Provides user account fixtures for testing authentication and authorization.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TestUser:
    """Test user account."""

    username: str
    password: str
    role: str
    email: str | None = None
    full_name: str | None = None


# Admin user with full permissions
ADMIN_USER = TestUser(
    username="admin",
    password="admin_test_password_123",
    role="admin",
    email="admin@test.projectai.local",
    full_name="Test Administrator",
)

# Regular user with standard permissions
REGULAR_USER = TestUser(
    username="testuser",
    password="test_password_456",
    role="user",
    email="user@test.projectai.local",
    full_name="Test User",
)

# Guest user with minimal permissions
GUEST_USER = TestUser(
    username="guest",
    password="guest_password_789",
    role="guest",
    email="guest@test.projectai.local",
    full_name="Guest User",
)

# User with special override permissions
OVERRIDE_USER = TestUser(
    username="override_admin",
    password="override_password_abc",
    role="override_admin",
    email="override@test.projectai.local",
    full_name="Override Administrator",
)

# All test users
ALL_TEST_USERS = [
    ADMIN_USER,
    REGULAR_USER,
    GUEST_USER,
    OVERRIDE_USER,
]


def get_test_user(username: str) -> TestUser | None:
    """Get a test user by username.

    Args:
        username: Username to look up

    Returns:
        TestUser instance or None if not found
    """
    for user in ALL_TEST_USERS:
        if user.username == username:
            return user
    return None


def get_admin_user() -> TestUser:
    """Get the admin test user."""
    return ADMIN_USER


def get_regular_user() -> TestUser:
    """Get the regular test user."""
    return REGULAR_USER
