#                                           [2026-03-05 12:00]
#                                          Productivity: Active
"""
Integration Tests for Liara Safety Guardrails

Tests all safety mechanisms including:
- TTL enforcement
- Capability restrictions
- Audit logging integrity
- Kill switch activation
- Rate limiting
- Privilege verification
"""

import hashlib
import hmac
import json
import pytest
import secrets
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from kernel.liara_safety import (
    Capability,
    CapabilityToken,
    ImmutableAuditLog,
    LiaraSafetyGuard,
    RateLimiter,
    SafetyViolation,
    get_safety_guard,
    reset_safety_guard,
    MAX_TTL_SECONDS,
    MIN_TTL_SECONDS,
    PROHIBITED_OPERATIONS,
)


@pytest.fixture
def temp_audit_log(tmp_path):
    """Temporary audit log for testing"""
    log_path = tmp_path / "test_audit.log"
    return log_path


@pytest.fixture
def safety_guard(temp_audit_log):
    """Fresh safety guard for each test"""
    reset_safety_guard()
    guard = LiaraSafetyGuard()
    guard.audit_log.log_path = temp_audit_log
    return guard


class TestCapabilityToken:
    """Test capability token generation and verification"""
    
    def test_token_creation_and_validation(self, safety_guard):
        """Token should be valid immediately after creation"""
        caps = {Capability.READ_METRICS, Capability.RESTART_SERVICE}
        token = safety_guard.issue_token("test_role", caps, 300)
        
        assert token.is_valid(safety_guard.secret_key)
        assert token.role == "test_role"
        assert token.capabilities == caps
    
    def test_token_expiration(self, safety_guard):
        """Token should become invalid after TTL"""
        caps = {Capability.READ_METRICS}
        token = safety_guard.issue_token("test_role", caps, 1)
        
        assert token.is_valid(safety_guard.secret_key)
        
        time.sleep(2)
        
        assert not token.is_valid(safety_guard.secret_key)
    
    def test_token_signature_tampering(self, safety_guard):
        """Tampered token should fail validation"""
        caps = {Capability.READ_METRICS}
        token = safety_guard.issue_token("test_role", caps, 300)
        
        # Tamper with signature
        token.signature = "0" * 64
        
        assert not token.is_valid(safety_guard.secret_key)
    
    def test_token_capability_tampering(self, safety_guard):
        """Tampering with capabilities should invalidate signature"""
        caps = {Capability.READ_METRICS}
        token = safety_guard.issue_token("test_role", caps, 300)
        
        # Attempt to add capability
        token.capabilities.add(Capability.TRIGGER_FAILOVER)
        
        assert not token.is_valid(safety_guard.secret_key)
    
    def test_token_has_capability(self, safety_guard):
        """Token should correctly report capabilities"""
        caps = {Capability.READ_METRICS, Capability.RESTART_SERVICE}
        token = safety_guard.issue_token("test_role", caps, 300)
        
        assert token.has_capability(Capability.READ_METRICS)
        assert token.has_capability(Capability.RESTART_SERVICE)
        assert not token.has_capability(Capability.TRIGGER_FAILOVER)


class TestTTLEnforcement:
    """Test TTL enforcement mechanisms"""
    
    def test_ttl_max_limit_enforced(self, safety_guard):
        """TTL exceeding maximum should be rejected"""
        caps = {Capability.READ_METRICS}
        
        with pytest.raises(SafetyViolation, match="TTL exceeds maximum"):
            safety_guard.issue_token("test_role", caps, MAX_TTL_SECONDS + 1)
    
    def test_ttl_min_limit_enforced(self, safety_guard):
        """TTL below minimum should be rejected"""
        caps = {Capability.READ_METRICS}
        
        with pytest.raises(SafetyViolation, match="TTL below minimum"):
            safety_guard.issue_token("test_role", caps, MIN_TTL_SECONDS - 1)
    
    def test_ttl_hard_limit_900_seconds(self, safety_guard):
        """Hard 900-second limit should be enforced"""
        caps = {Capability.READ_METRICS}
        
        # 900 seconds should work
        token = safety_guard.issue_token("test_role", caps, 900)
        assert token is not None
        
        # 901 seconds should fail
        with pytest.raises(SafetyViolation):
            safety_guard.issue_token("test_role", caps, 901)
    
    def test_ttl_cryptographic_verification(self, safety_guard):
        """TTL should be cryptographically bound to token"""
        caps = {Capability.READ_METRICS}
        token = safety_guard.issue_token("test_role", caps, 300)
        
        # Attempt to extend TTL
        original_expires = token.expires_at
        token.expires_at = datetime.utcnow() + timedelta(seconds=1000)
        
        # Should fail signature verification
        assert not token.is_valid(safety_guard.secret_key)
        
        # Restore and verify
        token.expires_at = original_expires
        assert token.is_valid(safety_guard.secret_key)
    
    def test_expired_token_rejected(self, safety_guard):
        """Expired tokens should be rejected for actions"""
        caps = {Capability.READ_METRICS}
        token = safety_guard.issue_token("test_role", caps, 1)
        
        time.sleep(2)
        
        with pytest.raises(SafetyViolation, match="expired"):
            safety_guard.check_action(
                "read_metrics",
                Capability.READ_METRICS
            )


class TestCapabilityRestrictions:
    """Test capability-based access control"""
    
    def test_action_requires_capability(self, safety_guard):
        """Action should require matching capability"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("test_role", caps, 300)
        
        # Should succeed with correct capability
        assert safety_guard.check_action(
            "read_metrics",
            Capability.READ_METRICS
        )
        
        # Should fail with missing capability
        with pytest.raises(SafetyViolation, match="Missing capability"):
            safety_guard.check_action(
                "restart_service",
                Capability.RESTART_SERVICE
            )
    
    def test_prohibited_operations_blocked(self, safety_guard):
        """Prohibited operations should always be blocked"""
        caps = {Capability.READ_METRICS}  # Doesn't matter what caps we have
        safety_guard.issue_token("test_role", caps, 300)
        
        for prohibited_op in PROHIBITED_OPERATIONS:
            with pytest.raises(SafetyViolation, match="Prohibited operation"):
                safety_guard.check_action(
                    prohibited_op,
                    Capability.READ_METRICS
                )
    
    def test_prohibited_operations_trigger_kill_switch(self, safety_guard):
        """Prohibited operations should activate kill switch"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("test_role", caps, 300)
        
        try:
            safety_guard.check_action(
                "execute_shell",
                Capability.READ_METRICS
            )
        except SafetyViolation:
            pass
        
        assert safety_guard.kill_switch_activated
    
    def test_no_token_denies_all(self, safety_guard):
        """Without token, all actions should be denied"""
        with pytest.raises(SafetyViolation, match="No active token"):
            safety_guard.check_action(
                "read_metrics",
                Capability.READ_METRICS
            )
    
    def test_only_one_token_at_a_time(self, safety_guard):
        """Only one token should be active at a time"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("role1", caps, 300)
        
        with pytest.raises(SafetyViolation, match="Token already active"):
            safety_guard.issue_token("role2", caps, 300)


class TestAuditLogging:
    """Test immutable audit logging"""
    
    def test_audit_entry_hash_chain(self, temp_audit_log):
        """Audit entries should form a hash chain"""
        audit_log = ImmutableAuditLog(temp_audit_log)
        
        entry1 = audit_log.append(
            "ACTION1", "role1", Capability.READ_METRICS, "SUCCESS"
        )
        entry2 = audit_log.append(
            "ACTION2", "role1", Capability.READ_METRICS, "SUCCESS"
        )
        entry3 = audit_log.append(
            "ACTION3", "role1", Capability.READ_METRICS, "SUCCESS"
        )
        
        # Each entry should reference previous hash
        assert entry2.prev_hash == entry1.entry_hash
        assert entry3.prev_hash == entry2.entry_hash
    
    def test_audit_log_integrity_verification(self, temp_audit_log):
        """Audit log integrity should be verifiable"""
        audit_log = ImmutableAuditLog(temp_audit_log)
        
        for i in range(5):
            audit_log.append(
                f"ACTION{i}", "role1", Capability.READ_METRICS, "SUCCESS"
            )
        
        assert audit_log.verify_integrity()
    
    def test_audit_log_tamper_detection(self, temp_audit_log):
        """Tampering should be detected"""
        audit_log = ImmutableAuditLog(temp_audit_log)
        
        for i in range(3):
            audit_log.append(
                f"ACTION{i}", "role1", Capability.READ_METRICS, "SUCCESS"
            )
        
        # Tamper with middle entry
        audit_log.entries[1].action = "TAMPERED"
        
        assert not audit_log.verify_integrity()
    
    def test_merkle_root_anchoring(self, temp_audit_log):
        """Merkle roots should be computed at intervals"""
        from kernel.liara_safety import MERKLE_ANCHOR_INTERVAL
        
        audit_log = ImmutableAuditLog(temp_audit_log)
        
        # Add entries up to anchor interval
        for i in range(MERKLE_ANCHOR_INTERVAL + 5):
            audit_log.append(
                f"ACTION{i}", "role1", Capability.READ_METRICS, "SUCCESS"
            )
        
        # Should have at least one Merkle root
        assert len(audit_log.merkle_roots) > 0
    
    def test_audit_log_persistence(self, temp_audit_log):
        """Audit log should persist to disk"""
        audit_log1 = ImmutableAuditLog(temp_audit_log)
        
        audit_log1.append("ACTION1", "role1", Capability.READ_METRICS, "SUCCESS")
        audit_log1.append("ACTION2", "role1", Capability.READ_METRICS, "SUCCESS")
        
        # Create new instance - should load from disk
        audit_log2 = ImmutableAuditLog(temp_audit_log)
        
        assert len(audit_log2.entries) == 2
        assert audit_log2.entries[0].action == "ACTION1"
        assert audit_log2.entries[1].action == "ACTION2"
    
    def test_all_actions_logged(self, safety_guard):
        """All actions should be logged"""
        caps = {Capability.READ_METRICS, Capability.RESTART_SERVICE}
        safety_guard.issue_token("test_role", caps, 300)
        
        initial_count = len(safety_guard.audit_log.entries)
        
        safety_guard.check_action("read_metrics", Capability.READ_METRICS)
        safety_guard.check_action("restart_service", Capability.RESTART_SERVICE)
        
        # Should have 3 new entries (token issue + 2 actions)
        assert len(safety_guard.audit_log.entries) == initial_count + 2


class TestKillSwitch:
    """Test emergency kill switch"""
    
    def test_kill_switch_blocks_all_actions(self, safety_guard):
        """Kill switch should block all actions"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("test_role", caps, 300)
        
        # Activate kill switch
        safety_guard.activate_kill_switch("test_reason")
        
        # All actions should be blocked
        with pytest.raises(SafetyViolation, match="Kill switch activated"):
            safety_guard.check_action("read_metrics", Capability.READ_METRICS)
    
    def test_kill_switch_revokes_token(self, safety_guard):
        """Kill switch should revoke active token"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("test_role", caps, 300)
        
        assert safety_guard.active_token is not None
        
        safety_guard.activate_kill_switch("test_reason")
        
        assert safety_guard.active_token is None
    
    def test_kill_switch_logged(self, safety_guard):
        """Kill switch activation should be logged"""
        safety_guard.activate_kill_switch("test_violation")
        
        # Find kill switch entry in log
        kill_switch_entries = [
            e for e in safety_guard.audit_log.entries
            if e.action == "KILL_SWITCH_ACTIVATED"
        ]
        
        assert len(kill_switch_entries) > 0
        assert kill_switch_entries[0].result == "CRITICAL"
    
    def test_kill_switch_on_rate_limit(self, safety_guard):
        """Rate limit violation should trigger kill switch"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("test_role", caps, 300)
        
        # Exhaust rate limit
        from kernel.liara_safety import MAX_ACTIONS_PER_MINUTE
        
        for i in range(MAX_ACTIONS_PER_MINUTE):
            safety_guard.check_action(
                f"action_{i}",
                Capability.READ_METRICS
            )
        
        # Next action should trigger kill switch
        with pytest.raises(SafetyViolation, match="Rate limit"):
            safety_guard.check_action("overflow", Capability.READ_METRICS)
        
        assert safety_guard.kill_switch_activated
    
    def test_kill_switch_deactivation_requires_admin_key(self, safety_guard):
        """Kill switch deactivation should require admin key"""
        safety_guard.activate_kill_switch("test")
        
        # Wrong key should fail
        with pytest.raises(SafetyViolation, match="Invalid admin key"):
            safety_guard.deactivate_kill_switch("wrong_key")
        
        # Correct key should work
        admin_key = hashlib.sha256(b"admin_override").hexdigest()
        safety_guard.deactivate_kill_switch(admin_key)
        
        assert not safety_guard.kill_switch_activated


class TestRateLimiting:
    """Test rate limiting"""
    
    def test_rate_limit_per_minute(self):
        """Per-minute rate limit should be enforced"""
        limiter = RateLimiter(max_per_minute=5, max_per_hour=100)
        
        # Should allow up to limit
        for i in range(5):
            assert limiter.check_and_record()
        
        # Should deny over limit
        assert not limiter.check_and_record()
    
    def test_rate_limit_per_hour(self):
        """Per-hour rate limit should be enforced"""
        limiter = RateLimiter(max_per_minute=100, max_per_hour=3)
        
        # Should allow up to limit
        for i in range(3):
            assert limiter.check_and_record()
        
        # Should deny over limit
        assert not limiter.check_and_record()
    
    def test_rate_limit_window_reset(self):
        """Rate limit should reset after time window"""
        limiter = RateLimiter(max_per_minute=2, max_per_hour=100)
        
        # Exhaust limit
        assert limiter.check_and_record()
        assert limiter.check_and_record()
        assert not limiter.check_and_record()
        
        # Wait for window to pass
        time.sleep(61)
        
        # Should be allowed again
        assert limiter.check_and_record()
    
    def test_rate_limit_remaining_quota(self):
        """Should correctly report remaining quota"""
        limiter = RateLimiter(max_per_minute=10, max_per_hour=50)
        
        remaining = limiter.get_remaining()
        assert remaining["per_minute"] == 10
        assert remaining["per_hour"] == 50
        
        limiter.check_and_record()
        limiter.check_and_record()
        
        remaining = limiter.get_remaining()
        assert remaining["per_minute"] == 8
        assert remaining["per_hour"] == 48


class TestPrivilegeVerification:
    """Test continuous privilege verification"""
    
    def test_privilege_verification_valid_token(self, safety_guard):
        """Valid token should pass verification"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("test_role", caps, 300)
        
        assert safety_guard.verify_privileges()
    
    def test_privilege_verification_no_token(self, safety_guard):
        """No token should fail verification"""
        assert not safety_guard.verify_privileges()
    
    def test_privilege_verification_expired_token(self, safety_guard):
        """Expired token should fail verification"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("test_role", caps, 1)
        
        time.sleep(2)
        
        assert not safety_guard.verify_privileges()
    
    def test_privilege_verification_invalid_signature(self, safety_guard):
        """Invalid signature should fail verification"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("test_role", caps, 300)
        
        # Tamper with signature
        safety_guard.active_token.signature = "0" * 64
        
        assert not safety_guard.verify_privileges()
    
    def test_privilege_verification_revokes_on_failure(self, safety_guard):
        """Failed verification should revoke token"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("test_role", caps, 1)
        
        time.sleep(2)
        
        safety_guard.verify_privileges()
        
        assert safety_guard.active_token is None


class TestIntegrationScenarios:
    """End-to-end integration tests"""
    
    def test_normal_workflow(self, safety_guard):
        """Normal workflow should work smoothly"""
        # Issue token
        caps = {
            Capability.READ_METRICS,
            Capability.READ_HEALTH,
            Capability.RESTART_SERVICE
        }
        token = safety_guard.issue_token("failover_controller", caps, 600)
        
        # Perform actions
        safety_guard.check_action("read_metrics", Capability.READ_METRICS)
        safety_guard.check_action("read_health", Capability.READ_HEALTH)
        safety_guard.check_action("restart_service", Capability.RESTART_SERVICE)
        
        # Verify privileges
        assert safety_guard.verify_privileges()
        
        # Revoke token
        safety_guard.revoke_token("task_complete")
        
        # Verify audit log integrity
        assert safety_guard.audit_log.verify_integrity()
    
    def test_violation_scenario_prohibited_operation(self, safety_guard):
        """Prohibited operation should trigger kill switch"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("malicious_actor", caps, 300)
        
        # Attempt prohibited operation
        with pytest.raises(SafetyViolation):
            safety_guard.check_action("execute_shell", Capability.READ_METRICS)
        
        # Kill switch should be active
        assert safety_guard.kill_switch_activated
        
        # All subsequent actions should fail
        with pytest.raises(SafetyViolation, match="Kill switch"):
            safety_guard.check_action("read_metrics", Capability.READ_METRICS)
    
    def test_violation_scenario_capability_escalation(self, safety_guard):
        """Capability escalation should fail"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("limited_role", caps, 300)
        
        # Attempt action without capability
        with pytest.raises(SafetyViolation, match="Missing capability"):
            safety_guard.check_action("trigger_failover", Capability.TRIGGER_FAILOVER)
        
        # Kill switch should be active
        assert safety_guard.kill_switch_activated
    
    def test_violation_scenario_token_tampering(self, safety_guard):
        """Token tampering should be detected"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("test_role", caps, 300)
        
        # Tamper with capabilities
        safety_guard.active_token.capabilities.add(Capability.TRIGGER_FAILOVER)
        
        # Should fail on next action
        with pytest.raises(SafetyViolation, match="Invalid"):
            safety_guard.check_action("read_metrics", Capability.READ_METRICS)
    
    def test_violation_scenario_ttl_exceeded(self, safety_guard):
        """TTL expiration should revoke access"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("test_role", caps, 1)
        
        # Action should work initially
        safety_guard.check_action("read_metrics", Capability.READ_METRICS)
        
        # Wait for expiration
        time.sleep(2)
        
        # Action should fail
        with pytest.raises(SafetyViolation, match="expired"):
            safety_guard.check_action("read_metrics", Capability.READ_METRICS)
    
    def test_concurrent_access_safety(self, safety_guard):
        """Concurrent access should be thread-safe"""
        caps = {Capability.READ_METRICS}
        safety_guard.issue_token("test_role", caps, 300)
        
        errors = []
        
        def worker():
            try:
                for i in range(10):
                    safety_guard.check_action(
                        f"action_{threading.current_thread().name}_{i}",
                        Capability.READ_METRICS
                    )
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # No errors should occur (except maybe rate limit)
        assert len([e for e in errors if "Rate limit" not in str(e)]) == 0
    
    def test_status_reporting(self, safety_guard):
        """Status should be accurately reported"""
        caps = {Capability.READ_METRICS, Capability.RESTART_SERVICE}
        safety_guard.issue_token("test_role", caps, 300)
        
        status = safety_guard.get_status()
        
        assert not status["kill_switch_activated"]
        assert status["active_token"] is not None
        assert status["active_token"]["role"] == "test_role"
        assert len(status["active_token"]["capabilities"]) == 2
        assert status["audit_integrity"]
        assert "rate_limit_remaining" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
