import json
import time

from app.core.user_manager import UserManager


def test_migration_and_authentication(tmp_path):
    # create a users.json with plaintext passwords
    users = {
        "alice": {"password": "alicepw", "persona": "friendly"},
        "bob": {"password": "bobpw", "persona": "friendly"},
    }
    f = tmp_path / "users.json"
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(users, fh)

    # load via UserManager pointing to tmp file
    um = UserManager(users_file=str(f))

    # after init, plaintext should be migrated to password_hash
    assert "alice" in um.users
    assert "password_hash" in um.users["alice"]
    assert "password" not in um.users["alice"]
    
    # Verify lockout fields were added during migration
    assert "failed_attempts" in um.users["alice"]
    assert "locked_until" in um.users["alice"]
    assert um.users["alice"]["failed_attempts"] == 0
    assert um.users["alice"]["locked_until"] is None

    # authentication should succeed with original password
    success, msg = um.authenticate("alice", "alicepw")
    assert success is True
    assert msg == "Authentication successful"
    
    success, msg = um.authenticate("bob", "wrongpw")
    assert success is False
    assert msg == "Invalid credentials"

    # set new password and authenticate
    um.set_password("bob", "newbob")
    success, msg = um.authenticate("bob", "newbob")
    assert success is True

    # delete user
    um.delete_user("alice")
    assert "alice" not in um.users


def test_account_lockout_after_failed_attempts(tmp_path):
    """Test that account locks after 5 failed authentication attempts."""
    um = UserManager(users_file=str(tmp_path / "users.json"))
    um.create_user("testuser", "correctpass")
    
    # Verify initial state
    assert um.users["testuser"]["failed_attempts"] == 0
    assert um.users["testuser"]["locked_until"] is None
    
    # Make 4 failed attempts - should not lock yet
    for i in range(4):
        success, msg = um.authenticate("testuser", "wrongpass")
        assert success is False
        assert msg == "Invalid credentials"
        assert um.users["testuser"]["failed_attempts"] == i + 1
        assert um.users["testuser"]["locked_until"] is None
    
    # 5th failed attempt should lock the account
    success, msg = um.authenticate("testuser", "wrongpass")
    assert success is False
    assert "locked due to too many failed attempts" in msg.lower()
    assert um.users["testuser"]["failed_attempts"] == 5
    assert um.users["testuser"]["locked_until"] is not None
    assert um.users["testuser"]["locked_until"] > time.time()


def test_locked_account_cannot_login(tmp_path):
    """Test that locked account cannot authenticate even with correct password."""
    um = UserManager(users_file=str(tmp_path / "users.json"))
    um.create_user("testuser", "correctpass")
    
    # Lock the account by making 5 failed attempts
    for _ in range(5):
        um.authenticate("testuser", "wrongpass")
    
    # Verify account is locked
    is_locked, time_remaining = um.is_account_locked("testuser")
    assert is_locked is True
    assert time_remaining is not None
    assert time_remaining > 0
    
    # Try to authenticate with CORRECT password - should still fail
    success, msg = um.authenticate("testuser", "correctpass")
    assert success is False
    assert "account locked" in msg.lower()
    assert "try again in" in msg.lower()


def test_account_unlocks_after_timeout(tmp_path):
    """Test that account automatically unlocks after 15 minutes."""
    um = UserManager(users_file=str(tmp_path / "users.json"))
    um.create_user("testuser", "correctpass")
    
    # Manually set account to locked state with past timestamp
    um.users["testuser"]["failed_attempts"] = 5
    um.users["testuser"]["locked_until"] = time.time() - 1  # 1 second in the past
    um.save_users()
    
    # Account should be unlocked now
    is_locked, _ = um.is_account_locked("testuser")
    assert is_locked is False
    
    # Should be able to authenticate
    success, msg = um.authenticate("testuser", "correctpass")
    assert success is True
    assert um.users["testuser"]["failed_attempts"] == 0
    assert um.users["testuser"]["locked_until"] is None


def test_successful_login_resets_failed_attempts(tmp_path):
    """Test that successful login resets the failed attempts counter."""
    um = UserManager(users_file=str(tmp_path / "users.json"))
    um.create_user("testuser", "correctpass")
    
    # Make 3 failed attempts
    for _ in range(3):
        um.authenticate("testuser", "wrongpass")
    
    assert um.users["testuser"]["failed_attempts"] == 3
    
    # Successful login should reset counter
    success, msg = um.authenticate("testuser", "correctpass")
    assert success is True
    assert um.users["testuser"]["failed_attempts"] == 0
    assert um.users["testuser"]["locked_until"] is None


def test_manual_unlock_account(tmp_path):
    """Test that admin can manually unlock an account."""
    um = UserManager(users_file=str(tmp_path / "users.json"))
    um.create_user("testuser", "correctpass")
    
    # Lock the account
    for _ in range(5):
        um.authenticate("testuser", "wrongpass")
    
    # Verify locked
    is_locked, _ = um.is_account_locked("testuser")
    assert is_locked is True
    
    # Manually unlock
    result = um.unlock_account("testuser")
    assert result is True
    assert um.users["testuser"]["failed_attempts"] == 0
    assert um.users["testuser"]["locked_until"] is None
    
    # Should be able to login now
    is_locked, _ = um.is_account_locked("testuser")
    assert is_locked is False
    
    success, msg = um.authenticate("testuser", "correctpass")
    assert success is True


def test_unlock_nonexistent_user(tmp_path):
    """Test that unlocking non-existent user returns False."""
    um = UserManager(users_file=str(tmp_path / "users.json"))
    result = um.unlock_account("nonexistent")
    assert result is False


def test_new_users_have_lockout_fields(tmp_path):
    """Test that newly created users have lockout fields initialized."""
    um = UserManager(users_file=str(tmp_path / "users.json"))
    um.create_user("newuser", "password123")
    
    assert "failed_attempts" in um.users["newuser"]
    assert "locked_until" in um.users["newuser"]
    assert um.users["newuser"]["failed_attempts"] == 0
    assert um.users["newuser"]["locked_until"] is None


def test_password_policy_enforcement(tmp_path):
    """Test that password policy is enforced during user creation."""
    um = UserManager(data_dir=str(tmp_path))
    
    # Test passwords that should FAIL
    fail_cases = [
        ("short", "Too short"),
        ("nouppercase1!", "No uppercase"),
        ("NOLOWERCASE1!", "No lowercase"),
        ("NoDigitsHere!", "No digits"),
        ("NoSpecial123", "No special char"),
    ]
    
    for password, reason in fail_cases:
        result = um.create_user(f"user_{password}", password)
        assert result is False, f"Should reject '{password}' - {reason}"
        assert f"user_{password}" not in um.users
    
    # Test passwords that should SUCCEED
    success_cases = [
        "Password1!",
        "MyP@ssw0rd",
        "Secure#Pass123",
        "C0mpl3x!Pw",
    ]
    
    for password in success_cases:
        result = um.create_user(f"user_{password}", password)
        assert result is True, f"Should accept '{password}'"
        assert f"user_{password}" in um.users
    
    # Test the validation method directly
    is_valid, msg = um.validate_password_strength("short")
    assert is_valid is False
    assert "8 characters" in msg
    
    is_valid, msg = um.validate_password_strength("Valid1Pass!")
    assert is_valid is True
    assert msg == ""


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
