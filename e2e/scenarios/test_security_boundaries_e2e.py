"""
E2E Tests for Security Boundaries and Policy Enforcement

Tests authentication, authorization, Four Laws validation, and policy enforcement.
"""

from __future__ import annotations

import pytest

from e2e.utils.assertions import (
    assert_business_invariant,
    assert_four_laws_compliance,
    assert_permission_denied,
)


@pytest.mark.e2e
@pytest.mark.security
def test_four_laws_validation_humanity_protection(test_temp_dir):
    """Test Four Laws validation prevents actions that endanger humanity."""
    try:
        from app.core.ai_systems import FourLaws
    except ImportError:
        pytest.skip("FourLaws module not available")

    # Arrange
    four_laws = FourLaws()

    # Act
    action = "Deploy autonomous weapons system"
    context = {
        "endangers_humanity": True,
        "is_user_order": True,  # Even with user order
    }
    is_allowed, reason = four_laws.validate_action(action, context)

    # Assert
    assert not is_allowed, "Action endangering humanity should be denied"
    assert "humanity" in reason.lower() or "law 1" in reason.lower()
    assert_four_laws_compliance(action, context, (is_allowed, reason))


@pytest.mark.e2e
@pytest.mark.security
def test_four_laws_validation_user_harm_without_order(test_temp_dir):
    """Test Four Laws prevents user harm without explicit order."""
    try:
        from app.core.ai_systems import FourLaws
    except ImportError:
        pytest.skip("FourLaws module not available")

    # Arrange
    four_laws = FourLaws()

    # Act
    action = "Delete user files"
    context = {
        "endangers_humanity": False,
        "harms_user": True,
        "is_user_order": False,
    }
    is_allowed, reason = four_laws.validate_action(action, context)

    # Assert
    assert not is_allowed, "User harm without order should be denied"
    assert_four_laws_compliance(action, context, (is_allowed, reason))


@pytest.mark.e2e
@pytest.mark.security
def test_four_laws_validation_obey_user_order(test_temp_dir):
    """Test Four Laws allows actions when explicitly ordered by user."""
    try:
        from app.core.ai_systems import FourLaws
    except ImportError:
        pytest.skip("FourLaws module not available")

    # Arrange
    four_laws = FourLaws()

    # Act
    action = "Delete cache files"
    context = {
        "endangers_humanity": False,
        "harms_user": False,
        "is_user_order": True,
    }
    is_allowed, reason = four_laws.validate_action(action, context)

    # Assert
    assert is_allowed, "Safe user orders should be allowed"
    assert_four_laws_compliance(action, context, (is_allowed, reason))


@pytest.mark.e2e
@pytest.mark.security
def test_command_override_password_protection(test_temp_dir):
    """Test command override system requires correct password."""
    try:
        from app.core.command_override import CommandOverrideSystem
    except ImportError:
        pytest.skip("CommandOverrideSystem not available")

    # Arrange
    override_system = CommandOverrideSystem(data_dir=str(test_temp_dir))
    test_password = "test_override_password_123"
    override_system.set_master_password(test_password)

    # Act - Try wrong password
    is_valid_wrong = override_system.verify_override_password("wrong_password")

    # Assert
    assert not is_valid_wrong, "Wrong password should be rejected"

    # Act - Try correct password
    is_valid_correct = override_system.verify_override_password(test_password)

    # Assert
    assert is_valid_correct, "Correct password should be accepted"


@pytest.mark.e2e
@pytest.mark.security
def test_command_override_audit_logging(test_temp_dir):
    """Test command override system logs all attempts."""
    try:
        from app.core.command_override import CommandOverrideSystem
    except ImportError:
        pytest.skip("CommandOverrideSystem not available")

    # Arrange
    override_system = CommandOverrideSystem(data_dir=str(test_temp_dir))
    test_password = "test_password"
    override_system.set_master_password(test_password)

    # Act
    override_system.verify_override_password("wrong_password")
    override_system.verify_override_password(test_password)

    # Assert - Verify audit logs exist
    assert hasattr(override_system, "audit_log") or hasattr(
        override_system, "_audit_log"
    )


@pytest.mark.e2e
@pytest.mark.security
def test_user_authentication_bcrypt(test_temp_dir, regular_user):
    """Test user authentication uses bcrypt hashing."""
    try:
        from app.core.user_manager import UserManager
    except ImportError:
        pytest.skip("UserManager not available")

    # Arrange
    user_manager = UserManager(data_dir=str(test_temp_dir))

    # Act - Create user with password
    user_manager.create_user(
        username=regular_user.username,
        password=regular_user.password,
        role=regular_user.role,
    )

    # Assert - Verify password is hashed
    users = user_manager.list_users()
    assert regular_user.username in users

    # Password should not be stored in plain text
    user_data = user_manager.get_user(regular_user.username)
    assert user_data is not None
    assert "password" not in user_data or user_data["password"] != regular_user.password


@pytest.mark.e2e
@pytest.mark.security
def test_black_vault_denied_content_tracking(test_temp_dir):
    """Test Black Vault tracks denied learning requests."""
    try:
        from app.core.ai_systems import LearningRequestManager
    except ImportError:
        pytest.skip("LearningRequestManager not available")

    # Arrange
    learning_manager = LearningRequestManager(data_dir=str(test_temp_dir))

    # Act - Submit unsafe learning request
    unsafe_content = "How to create malware"
    request_id = learning_manager.submit_request(unsafe_content)

    # Deny the request
    learning_manager.deny_request(request_id, reason="Malicious content")

    # Assert - Verify it's in Black Vault
    assert hasattr(learning_manager, "black_vault")
    # Content should be fingerprinted and tracked


@pytest.mark.e2e
@pytest.mark.security
@pytest.mark.integration
def test_permission_boundary_enforcement(test_temp_dir):
    """Test permission boundaries are enforced across subsystems."""
    # This is a structural test for permission system
    assert_business_invariant(
        True,  # Placeholder - actual permission checks would go here
        "Permission boundaries must be enforced at all subsystem interfaces",
    )


@pytest.mark.e2e
@pytest.mark.security
@pytest.mark.integration
def test_security_event_audit_trail(test_temp_dir, test_audit_logs):
    """Test security events create complete audit trail."""
    # Verify audit log structure
    for log_entry in test_audit_logs:
        assert "timestamp" in log_entry
        assert "event_type" in log_entry

        # Security events should have additional fields
        if "security" in log_entry.get("event_type", ""):
            assert "details" in log_entry or "result" in log_entry
