"""Extended tests for CommandOverrideSystem and the adapter (20+ cases)."""

from __future__ import annotations

import tempfile

import pytest

from app.core.ai_systems import CommandOverride, OverrideType
from app.core.command_override import CommandOverrideSystem


@pytest.fixture
def tmpdir():
    with tempfile.TemporaryDirectory() as td:
        yield td


def test_adapter_password_lifecycle(tmpdir):
    adapter = CommandOverride(data_dir=tmpdir)
    assert adapter.set_password("SecretPass123!") is True
    assert adapter.verify_password("SecretPass123!") is True
    assert adapter.verify_password("wrong") is False


def test_adapter_request_override_and_status(tmpdir):
    adapter = CommandOverride(data_dir=tmpdir)
    adapter.set_password("SecretPass123!")
    ok, msg = adapter.request_override(
        "SecretPass123!", OverrideType.CONTENT_FILTER, reason="testing"
    )
    assert ok is True
    assert "Override" in msg
    assert adapter.is_override_active(OverrideType.CONTENT_FILTER) is True


def test_adapter_unknown_protocol_is_graceful(tmpdir):
    adapter = CommandOverride(data_dir=tmpdir)
    adapter.set_password("SecretPass123!")

    class FakeOverride:
        value = "nonexistent_protocol"
        name = "FAKE"

    ok, msg = adapter.request_override("SecretPass123!", FakeOverride)  # type: ignore[arg-type]
    assert ok is True
    assert "Override" in msg


def test_adapter_statistics(tmpdir):
    adapter = CommandOverride(data_dir=tmpdir)
    adapter.set_password("SecretPass123!")
    adapter.request_override("SecretPass123!", OverrideType.RATE_LIMITING)
    stats = adapter.get_statistics()
    assert stats["password_set"] is True
    assert stats["active_overrides"] >= 1
    assert isinstance(stats["audit_entries"], int)


def test_system_master_override_flow(tmpdir):
    sys = CommandOverrideSystem(data_dir=tmpdir)
    assert sys.set_master_password("StrongPass123!") is True
    assert sys.authenticate("StrongPass123!") is True
    assert sys.enable_master_override() is True
    assert all(v is False for v in sys.get_all_protocols().values())
    assert sys.disable_master_override() is True
    assert all(v is True for v in sys.get_all_protocols().values())


def test_system_override_protocol_requires_auth(tmpdir):
    sys = CommandOverrideSystem(data_dir=tmpdir)
    ok = sys.override_protocol("content_filter", enabled=False)
    assert ok is False
    sys.set_master_password("StrongPass123!")
    sys.authenticate("StrongPass123!")
    assert sys.override_protocol("content_filter", enabled=False) is True
    assert sys.is_protocol_enabled("content_filter") is False


def test_system_unknown_protocol(tmpdir):
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("StrongPass123!")
    sys.authenticate("StrongPass123!")
    ok = sys.override_protocol("totally_unknown", enabled=False)
    assert ok is False


def test_system_emergency_lockdown(tmpdir):
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("StrongPass123!")
    sys.authenticate("StrongPass123!")
    sys.enable_master_override()
    sys.emergency_lockdown()
    assert all(sys.is_protocol_enabled(k) is True for k in sys.get_all_protocols())
    assert sys.get_status()["authenticated"] is False


def test_system_audit_log_written(tmpdir):
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("StrongPass123!")
    sys.authenticate("StrongPass123!")
    sys.override_protocol("prompt_safety", enabled=False)
    lines = sys.get_audit_log(lines=10)
    assert any("OVERRIDE_PROTOCOL" in (line or "") for line in lines)


def test_adapter_audit_log_access(tmpdir):
    adapter = CommandOverride(data_dir=tmpdir)
    adapter.set_password("SecretPass123!")
    adapter.request_override("SecretPass123!", OverrideType.CONTENT_FILTER)
    assert len(adapter.audit_log) > 0


def test_account_lockout_after_five_failed_attempts(tmpdir):
    """Test that account locks after 5 failed authentication attempts."""
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("CorrectPass123!")

    # First 4 failed attempts should not lock
    for i in range(4):
        assert sys.authenticate("wrong_password") is False
        assert sys.failed_auth_attempts == i + 1
        assert sys.auth_locked_until is None

    # 5th failed attempt should trigger lockout
    assert sys.authenticate("wrong_password") is False
    assert sys.failed_auth_attempts == 5
    assert sys.auth_locked_until is not None

    # Verify locked for 900 seconds (15 minutes)
    import time
    lockout_duration = sys.auth_locked_until - time.time()
    assert 895 < lockout_duration <= 900  # Allow small timing variance


def test_cannot_authenticate_during_lockout(tmpdir):
    """Test that authentication fails during lockout period even with correct password."""
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("CorrectPass123!")

    # Trigger lockout with 5 failed attempts
    for _ in range(5):
        sys.authenticate("wrong_password")

    assert sys.auth_locked_until is not None

    # Even correct password should fail during lockout
    assert sys.authenticate("CorrectPass123!") is False
    assert sys.authenticated is False


def test_lockout_expires_after_duration(tmpdir):
    """Test that lockout expires and allows authentication after 15 minutes."""
    import time
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("CorrectPass123!")

    # Trigger lockout
    for _ in range(5):
        sys.authenticate("wrong_password")

    # Manually set lockout to expire (simulate time passing)
    sys.auth_locked_until = time.time() - 1  # 1 second in the past
    sys._save_config()

    # Should be able to authenticate now
    assert sys.authenticate("CorrectPass123!") is True
    assert sys.authenticated is True
    assert sys.failed_auth_attempts == 0
    assert sys.auth_locked_until is None


def test_successful_auth_resets_failed_attempts(tmpdir):
    """Test that successful authentication resets failed attempt counter."""
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("CorrectPass123!")

    # Make 3 failed attempts
    for _ in range(3):
        sys.authenticate("wrong_password")
    
    assert sys.failed_auth_attempts == 3

    # Successful authentication should reset counter
    assert sys.authenticate("CorrectPass123!") is True
    assert sys.failed_auth_attempts == 0
    assert sys.auth_locked_until is None


def test_emergency_unlock_clears_lockout(tmpdir):
    """Test that emergency_unlock() clears account lockout."""
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("CorrectPass123!")

    # Trigger lockout
    for _ in range(5):
        sys.authenticate("wrong_password")
    
    assert sys.auth_locked_until is not None
    assert sys.failed_auth_attempts == 5

    # Emergency unlock should clear lockout
    result = sys.emergency_unlock()
    assert result is True
    assert sys.auth_locked_until is None
    assert sys.failed_auth_attempts == 0

    # Should be able to authenticate now
    assert sys.authenticate("CorrectPass123!") is True


def test_emergency_unlock_when_not_locked(tmpdir):
    """Test emergency_unlock() when account is not locked."""
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("correct_password")

    # No lockout active
    result = sys.emergency_unlock()
    assert result is False  # Returns False when no lockout to clear


def test_lockout_persists_across_instances(tmpdir):
    """Test that lockout state persists when system is reloaded."""
    # Create first instance and trigger lockout
    sys1 = CommandOverrideSystem(data_dir=tmpdir)
    sys1.set_master_password("CorrectPass123!")
    for _ in range(5):
        sys1.authenticate("wrong_password")
    
    assert sys1.auth_locked_until is not None
    locked_until = sys1.auth_locked_until

    # Create new instance (simulates restart)
    sys2 = CommandOverrideSystem(data_dir=tmpdir)
    
    # Lockout should persist
    assert sys2.auth_locked_until == locked_until
    assert sys2.failed_auth_attempts == 5
    assert sys2.authenticate("CorrectPass123!") is False


def test_emergency_lockdown_still_works_during_lockout(tmpdir):
    """Test that emergency_lockdown() works even during account lockout."""
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("CorrectPass123!")

    # Trigger lockout
    for _ in range(5):
        sys.authenticate("wrong_password")
    
    assert sys.auth_locked_until is not None

    # emergency_lockdown() should still work (doesn't require auth)
    sys.emergency_lockdown()
    
    assert sys.authenticated is False
    assert all(sys.is_protocol_enabled(k) is True for k in sys.get_all_protocols())
    # Note: lockout state remains (this is intentional - emergency_lockdown focuses on protocols)


def test_get_status_includes_lockout_info(tmpdir):
    """Test that get_status() includes lockout information."""
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("CorrectPass123!")

    # No lockout initially
    status = sys.get_status()
    assert "failed_auth_attempts" in status
    assert status["failed_auth_attempts"] == 0
    assert "lockout_status" in status
    assert status["lockout_status"] is None

    # Trigger lockout
    for _ in range(5):
        sys.authenticate("wrong_password")
    
    status = sys.get_status()
    assert status["failed_auth_attempts"] == 5
    assert status["lockout_status"] is not None
    assert status["lockout_status"]["locked"] is True
    assert "remaining_seconds" in status["lockout_status"]
    assert 0 < status["lockout_status"]["remaining_seconds"] <= 900


def test_lockout_audit_log_entries(tmpdir):
    """Test that lockout events are logged in audit log."""
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("CorrectPass123!")

    # Trigger lockout
    for i in range(5):
        sys.authenticate("wrong_password")
    
    # Check audit log
    log_entries = sys.get_audit_log(lines=20)
    log_text = "".join(log_entries)
    
    # Should have failed attempt messages
    assert "Invalid password" in log_text or "FAILED" in log_text
    # Should have lockout message
    assert "locked" in log_text.lower() or "Account locked" in log_text
    
    # Emergency unlock
    sys.emergency_unlock()
    log_entries = sys.get_audit_log(lines=5)
    log_text = "".join(log_entries)
    assert "EMERGENCY_UNLOCK" in log_text


def test_password_policy_weak_passwords_rejected(tmpdir):
    """Test that weak passwords are rejected by the password policy."""
    sys = CommandOverrideSystem(data_dir=tmpdir)
    
    weak_passwords = [
        "weak",         # too short
        "password",     # no uppercase, no digit, no special char
        "Password1",    # no special character
        "password!",    # no uppercase, no digit
        "PASSWORD1!",   # no lowercase
        "Password!",    # no digit
        "Pass1!",       # too short (only 6 chars)
    ]
    
    for password in weak_passwords:
        result = sys.set_master_password(password)
        assert result is False, f"Password '{password}' should have been rejected"
        assert sys.master_password_hash is None or sys.master_password_hash == ""


def test_password_policy_strong_passwords_accepted(tmpdir):
    """Test that strong passwords are accepted by the password policy."""
    sys = CommandOverrideSystem(data_dir=tmpdir)
    
    strong_passwords = [
        "MasterP@ss123",
        "Override!2024",
        "Secure#Pass1",
        "MyP@ssw0rd!",
        "C0mpl3x!Pass",
        "Adm1n#2024!",
    ]
    
    for password in strong_passwords:
        # Create new instance for each test to ensure clean state
        sys = CommandOverrideSystem(data_dir=tmpdir)
        result = sys.set_master_password(password)
        assert result is True, f"Password '{password}' should have been accepted"
        assert sys.master_password_hash is not None
        
        # Verify we can authenticate with the accepted password
        assert sys.authenticate(password) is True


def test_password_policy_audit_log(tmpdir):
    """Test that password policy rejections are logged in audit log."""
    sys = CommandOverrideSystem(data_dir=tmpdir)
    
    # Try weak password
    sys.set_master_password("weak")
    
    # Check audit log
    log_entries = sys.get_audit_log(lines=5)
    log_text = "".join(log_entries)
    
    assert "Rejected:" in log_text or "FAILED" in log_text
    assert "password" in log_text.lower()


def test_password_policy_validation_method(tmpdir):
    """Test the _validate_master_password_strength() method directly."""
    sys = CommandOverrideSystem(data_dir=tmpdir)
    
    # Test weak passwords
    is_valid, msg = sys._validate_master_password_strength("weak")
    assert is_valid is False
    assert "8 characters" in msg
    
    is_valid, msg = sys._validate_master_password_strength("password")
    assert is_valid is False
    
    is_valid, msg = sys._validate_master_password_strength("Password1")
    assert is_valid is False
    assert "special character" in msg
    
    is_valid, msg = sys._validate_master_password_strength("password!")
    assert is_valid is False
    
    is_valid, msg = sys._validate_master_password_strength("PASSWORD1!")
    assert is_valid is False
    assert "lowercase" in msg
    
    is_valid, msg = sys._validate_master_password_strength("Password!")
    assert is_valid is False
    assert "digit" in msg
    
    # Test strong password
    is_valid, msg = sys._validate_master_password_strength("MasterP@ss123")
    assert is_valid is True
    assert msg == ""


