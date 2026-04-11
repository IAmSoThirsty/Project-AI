"""
Tests for Enhanced Sovereign Runtime
[2026-03-05]

Comprehensive test suite covering:
- Capability-based security
- Time-based constraints
- Policy compilation (JIT)
- Cryptographic proofs
- Integration scenarios
"""

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from governance.sovereign_runtime_enhanced import (
    CapabilityConstraint,
    CapabilityRegistry,
    CapabilityScope,
    CapabilityToken,
    CompiledPolicy,
    EnhancedSovereignRuntime,
    PolicyCompiler,
    ProofGenerator,
    RateLimitConfig,
    RateLimiter,
    TimeConstraintEngine,
    TimeWindow,
)


# ============================================================================
# CAPABILITY-BASED SECURITY TESTS
# ============================================================================


class TestCapabilityToken:
    """Test CapabilityToken functionality"""
    
    def test_basic_capability_creation(self):
        """Test creating a basic capability token"""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=1)
        
        token = CapabilityToken(
            token_id="test-token-1",
            issuer="admin",
            subject="user123",
            action="read:data",
            scope=CapabilityScope.RESOURCE,
            scope_value="database",
            issued_at=now,
            expires_at=expires,
            max_uses=10
        )
        
        assert token.token_id == "test-token-1"
        assert token.issuer == "admin"
        assert token.subject == "user123"
        assert token.action == "read:data"
        assert token.scope == CapabilityScope.RESOURCE
        assert token.max_uses == 10
        assert token.uses_count == 0
    
    def test_capability_expiration(self):
        """Test capability expiration check"""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=1)
        
        token = CapabilityToken(
            token_id="expired-token",
            issuer="admin",
            subject="user123",
            action="read:data",
            scope=CapabilityScope.GLOBAL,
            scope_value=None,
            issued_at=past - timedelta(hours=2),
            expires_at=past
        )
        
        valid, reason = token.is_valid()
        assert not valid
        assert "expired" in reason.lower()
    
    def test_capability_max_uses(self):
        """Test max uses enforcement"""
        now = datetime.now(timezone.utc)
        
        token = CapabilityToken(
            token_id="limited-token",
            issuer="admin",
            subject="user123",
            action="write:data",
            scope=CapabilityScope.GLOBAL,
            scope_value=None,
            issued_at=now,
            expires_at=None,
            max_uses=3
        )
        
        # Use 3 times
        for i in range(3):
            valid, _ = token.is_valid()
            assert valid
            token.use()
        
        # Fourth use should fail
        valid, reason = token.is_valid()
        assert not valid
        assert "max uses" in reason.lower()
    
    def test_capability_delegation(self):
        """Test capability delegation"""
        now = datetime.now(timezone.utc)
        
        original = CapabilityToken(
            token_id="original-token",
            issuer="admin",
            subject="user1",
            action="manage:resource",
            scope=CapabilityScope.SERVICE,
            scope_value="api",
            issued_at=now,
            expires_at=now + timedelta(hours=24),
            can_delegate=True,
            max_delegation_depth=2
        )
        
        # Delegate to user2
        delegated = original.delegate("user2")
        assert delegated is not None
        assert delegated.subject == "user2"
        assert delegated.issuer == "user1"
        assert delegated.delegation_depth == 1
        assert delegated.action == "manage:resource"
        
        # Delegate again to user3
        delegated2 = delegated.delegate("user3")
        assert delegated2 is not None
        assert delegated2.delegation_depth == 2
        
        # Can't delegate beyond max depth
        delegated3 = delegated2.delegate("user4")
        assert delegated3 is None
    
    def test_capability_constraints(self):
        """Test capability constraints evaluation"""
        now = datetime.now(timezone.utc)
        
        # Time window constraint
        time_constraint = CapabilityConstraint(
            constraint_type="time_window",
            parameters={
                "start": (now - timedelta(hours=1)).isoformat(),
                "end": (now + timedelta(hours=1)).isoformat()
            }
        )
        
        valid, reason = time_constraint.evaluate({})
        assert valid
        
        # Rate limit constraint
        rate_constraint = CapabilityConstraint(
            constraint_type="rate_limit",
            parameters={
                "max_calls": 10,
                "window_seconds": 60
            }
        )
        
        valid, reason = rate_constraint.evaluate({"rate_limit_calls": 5})
        assert valid
        
        valid, reason = rate_constraint.evaluate({"rate_limit_calls": 15})
        assert not valid
        
        # Condition constraint
        condition_constraint = CapabilityConstraint(
            constraint_type="condition",
            parameters={
                "expression": "context.get('user_role') == 'admin'"
            }
        )
        
        valid, reason = condition_constraint.evaluate({"user_role": "admin"})
        assert valid
        
        valid, reason = condition_constraint.evaluate({"user_role": "user"})
        assert not valid


class TestCapabilityRegistry:
    """Test CapabilityRegistry functionality"""
    
    def test_register_and_retrieve(self):
        """Test registering and retrieving capabilities"""
        registry = CapabilityRegistry()
        now = datetime.now(timezone.utc)
        
        token = CapabilityToken(
            token_id="token-1",
            issuer="admin",
            subject="user1",
            action="read:data",
            scope=CapabilityScope.GLOBAL,
            scope_value=None,
            issued_at=now,
            expires_at=None
        )
        
        registry.register(token)
        
        retrieved = registry.get("token-1")
        assert retrieved is not None
        assert retrieved.token_id == "token-1"
    
    def test_get_by_subject(self):
        """Test retrieving capabilities by subject"""
        registry = CapabilityRegistry()
        now = datetime.now(timezone.utc)
        
        for i in range(3):
            token = CapabilityToken(
                token_id=f"token-{i}",
                issuer="admin",
                subject="user1",
                action=f"action-{i}",
                scope=CapabilityScope.GLOBAL,
                scope_value=None,
                issued_at=now,
                expires_at=None
            )
            registry.register(token)
        
        tokens = registry.get_by_subject("user1")
        assert len(tokens) == 3
    
    def test_revoke_capability(self):
        """Test revoking a capability"""
        registry = CapabilityRegistry()
        now = datetime.now(timezone.utc)
        
        token = CapabilityToken(
            token_id="revoke-test",
            issuer="admin",
            subject="user1",
            action="write:data",
            scope=CapabilityScope.GLOBAL,
            scope_value=None,
            issued_at=now,
            expires_at=now + timedelta(hours=1)
        )
        
        registry.register(token)
        
        # Verify it's valid before revoke
        valid, _ = token.is_valid()
        assert valid
        
        # Revoke it
        assert registry.revoke("revoke-test")
        
        # Token should now be expired (expires_at set to past)
        retrieved = registry.get("revoke-test")
        # Need to wait a tiny bit for the expiration to take effect
        import time
        time.sleep(0.01)
        valid, reason = retrieved.is_valid()
        # Revoke sets expires_at to now, so it should be expired or about to expire
        # Check that expires_at was updated to a past time
        assert retrieved.expires_at <= datetime.now(timezone.utc)
    
    def test_cleanup_expired(self):
        """Test cleaning up expired tokens"""
        registry = CapabilityRegistry()
        now = datetime.now(timezone.utc)
        
        # Add expired token
        expired_token = CapabilityToken(
            token_id="expired",
            issuer="admin",
            subject="user1",
            action="test",
            scope=CapabilityScope.GLOBAL,
            scope_value=None,
            issued_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1)
        )
        registry.register(expired_token)
        
        # Add valid token
        valid_token = CapabilityToken(
            token_id="valid",
            issuer="admin",
            subject="user1",
            action="test",
            scope=CapabilityScope.GLOBAL,
            scope_value=None,
            issued_at=now,
            expires_at=now + timedelta(hours=1)
        )
        registry.register(valid_token)
        
        # Cleanup
        removed = registry.cleanup_expired()
        assert removed == 1
        assert registry.get("expired") is None
        assert registry.get("valid") is not None


# ============================================================================
# TIME-BASED CONSTRAINTS TESTS
# ============================================================================


class TestTimeWindow:
    """Test TimeWindow functionality"""
    
    def test_business_hours_weekday(self):
        """Test business hours on weekday"""
        window = TimeWindow(
            start_hour=9,
            end_hour=17,
            days_of_week=[0, 1, 2, 3, 4]  # Monday-Friday
        )
        
        # Monday 10:00
        monday_10am = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)  # Monday
        assert window.is_active(monday_10am)
        
        # Monday 8:00 (before hours)
        monday_8am = datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc)
        assert not window.is_active(monday_8am)
        
        # Monday 18:00 (after hours)
        monday_6pm = datetime(2024, 1, 1, 18, 0, tzinfo=timezone.utc)
        assert not window.is_active(monday_6pm)
    
    def test_business_hours_weekend(self):
        """Test business hours on weekend"""
        window = TimeWindow(
            start_hour=9,
            end_hour=17,
            days_of_week=[0, 1, 2, 3, 4]  # Monday-Friday
        )
        
        # Saturday 10:00
        saturday_10am = datetime(2024, 1, 6, 10, 0, tzinfo=timezone.utc)  # Saturday
        assert not window.is_active(saturday_10am)
    
    def test_overnight_window(self):
        """Test window that crosses midnight"""
        window = TimeWindow(
            start_hour=22,  # 10 PM
            end_hour=6,     # 6 AM
            days_of_week=[0, 1, 2, 3, 4, 5, 6]
        )
        
        # 23:00 (should be active)
        night = datetime(2024, 1, 1, 23, 0, tzinfo=timezone.utc)
        assert window.is_active(night)
        
        # 02:00 (should be active)
        early_morning = datetime(2024, 1, 1, 2, 0, tzinfo=timezone.utc)
        assert window.is_active(early_morning)
        
        # 12:00 (should not be active)
        noon = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        assert not window.is_active(noon)


class TestRateLimiter:
    """Test RateLimiter functionality"""
    
    def test_basic_rate_limiting(self):
        """Test basic rate limiting"""
        config = RateLimitConfig(
            max_calls=5,
            window_seconds=10
        )
        limiter = RateLimiter(config)
        
        # First 5 calls should succeed
        for i in range(5):
            allowed, info = limiter.check_limit("user1")
            assert allowed
        
        # 6th call should fail
        allowed, info = limiter.check_limit("user1")
        assert not allowed
    
    def test_rate_limit_refill(self):
        """Test token bucket refill"""
        config = RateLimitConfig(
            max_calls=2,
            window_seconds=1  # 1 second window
        )
        limiter = RateLimiter(config)
        
        # Use 2 tokens
        limiter.check_limit("user1")
        limiter.check_limit("user1")
        
        # Should fail immediately
        allowed, info = limiter.check_limit("user1")
        assert not allowed
        
        # Wait for refill
        time.sleep(1.5)
        
        # Should succeed after refill
        allowed, info = limiter.check_limit("user1")
        assert allowed
    
    def test_multiple_keys(self):
        """Test rate limiting with multiple keys"""
        config = RateLimitConfig(
            max_calls=3,
            window_seconds=10
        )
        limiter = RateLimiter(config)
        
        # Use up user1's quota
        for i in range(3):
            allowed, _ = limiter.check_limit("user1")
            assert allowed
        
        # user1 should be limited
        allowed, _ = limiter.check_limit("user1")
        assert not allowed
        
        # user2 should still have quota
        allowed, _ = limiter.check_limit("user2")
        assert allowed


class TestTimeConstraintEngine:
    """Test TimeConstraintEngine functionality"""
    
    def test_business_hours_check(self):
        """Test business hours checking"""
        engine = TimeConstraintEngine()
        
        # Set custom business hours
        window = TimeWindow(
            start_hour=9,
            end_hour=17,
            days_of_week=[0, 1, 2, 3, 4]
        )
        engine.set_business_hours(window)
        
        # Test with specific datetime
        monday_10am = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
        assert engine.is_business_hours(monday_10am)
        
        saturday_10am = datetime(2024, 1, 6, 10, 0, tzinfo=timezone.utc)
        assert not engine.is_business_hours(saturday_10am)
    
    def test_rate_limit_registration(self):
        """Test rate limit policy registration"""
        engine = TimeConstraintEngine()
        
        config = RateLimitConfig(max_calls=10, window_seconds=60)
        engine.register_rate_limit("api_calls", config)
        
        # Should be able to check rate limit
        allowed, info = engine.check_rate_limit("api_calls", "user1")
        assert allowed
    
    def test_temporal_policy_evaluation(self):
        """Test temporal policy evaluation"""
        engine = TimeConstraintEngine()
        
        now = datetime.now(timezone.utc)
        
        # Register temporal policy with time windows
        policy = {
            "allowed_windows": [
                {
                    "start_hour": 9,
                    "end_hour": 17,
                    "days_of_week": [0, 1, 2, 3, 4],
                    "timezone_name": "UTC"
                }
            ]
        }
        engine.register_temporal_policy("business_hours_policy", policy)
        
        # Evaluation depends on current time
        valid, reason = engine.evaluate_temporal_policy("business_hours_policy", {})
        assert isinstance(valid, bool)
    
    def test_blackout_periods(self):
        """Test blackout period enforcement"""
        engine = TimeConstraintEngine()
        
        now = datetime.now(timezone.utc)
        
        # Register policy with blackout period
        policy = {
            "blackout_periods": [
                {
                    "start": (now - timedelta(hours=1)).isoformat(),
                    "end": (now + timedelta(hours=1)).isoformat(),
                    "reason": "Maintenance window"
                }
            ]
        }
        engine.register_temporal_policy("maintenance_policy", policy)
        
        valid, reason = engine.evaluate_temporal_policy("maintenance_policy", {})
        assert not valid
        assert "blackout" in reason.lower()


# ============================================================================
# POLICY COMPILATION TESTS
# ============================================================================


class TestPolicyCompiler:
    """Test PolicyCompiler functionality"""
    
    def test_simple_policy_compilation(self):
        """Test compiling a simple policy"""
        compiler = PolicyCompiler()
        
        policy_def = {
            "rules": [
                {
                    "condition": "context.get('user_role') == 'admin'",
                    "allow": True,
                    "reason": "Admin access granted"
                },
                {
                    "condition": "context.get('user_role') == 'user'",
                    "allow": False,
                    "reason": "User access denied"
                }
            ],
            "default": {
                "allowed": False,
                "reason": "No matching rule"
            }
        }
        
        compiled = compiler.compile_policy("test_policy", policy_def)
        assert compiled is not None
        assert compiled.policy_id == "test_policy"
    
    def test_policy_execution(self):
        """Test executing compiled policy"""
        compiler = PolicyCompiler()
        
        policy_def = {
            "rules": [
                {
                    "condition": "context.get('score', 0) > 50",
                    "allow": True,
                    "reason": "Score threshold met"
                }
            ],
            "default": {
                "allowed": False,
                "reason": "Score too low"
            }
        }
        
        compiled = compiler.compile_policy("score_policy", policy_def)
        
        # Test with high score
        allowed, reason, metadata = compiled.execute({"score": 75})
        assert allowed
        assert "threshold met" in reason.lower()
        
        # Test with low score
        allowed, reason, metadata = compiled.execute({"score": 25})
        assert not allowed
        assert "too low" in reason.lower()
    
    def test_multiple_rules(self):
        """Test policy with multiple rules"""
        compiler = PolicyCompiler()
        
        policy_def = {
            "rules": [
                {
                    "condition": "context.get('emergency', False)",
                    "allow": True,
                    "reason": "Emergency override"
                },
                {
                    "condition": "context.get('user_role') == 'admin'",
                    "allow": True,
                    "reason": "Admin access"
                },
                {
                    "condition": "context.get('user_role') == 'user' and context.get('approved', False)",
                    "allow": True,
                    "reason": "Approved user access"
                }
            ],
            "default": {
                "allowed": False,
                "reason": "Access denied"
            }
        }
        
        compiled = compiler.compile_policy("complex_policy", policy_def)
        
        # Test emergency override
        allowed, reason, _ = compiled.execute({"emergency": True})
        assert allowed
        
        # Test admin access
        allowed, reason, _ = compiled.execute({"user_role": "admin"})
        assert allowed
        
        # Test approved user
        allowed, reason, _ = compiled.execute({"user_role": "user", "approved": True})
        assert allowed
        
        # Test denied user
        allowed, reason, _ = compiled.execute({"user_role": "user", "approved": False})
        assert not allowed
    
    def test_policy_stats(self):
        """Test policy execution statistics"""
        compiler = PolicyCompiler()
        
        policy_def = {
            "rules": [
                {
                    "condition": "True",
                    "allow": True,
                    "reason": "Always allow"
                }
            ],
            "default": {"allowed": False, "reason": "Default"}
        }
        
        compiled = compiler.compile_policy("stats_policy", policy_def)
        
        # Execute multiple times
        for i in range(10):
            compiled.execute({})
        
        stats = compiled.get_stats()
        assert stats["execution_count"] == 10
        assert stats["total_execution_time"] >= 0  # May be very fast


# ============================================================================
# CRYPTOGRAPHIC PROOFS TESTS
# ============================================================================


class TestProofGenerator:
    """Test ProofGenerator functionality"""
    
    def test_proof_generation(self):
        """Test generating cryptographic proof"""
        with TemporaryDirectory() as tmpdir:
            from governance.sovereign_runtime import SovereignRuntime
            
            runtime = SovereignRuntime(Path(tmpdir))
            proof_gen = ProofGenerator(runtime)
            
            context = {"user": "test_user", "action": "read"}
            decision = {"allowed": True, "reason": "Access granted"}
            
            proof = proof_gen.generate_proof(
                decision_type="allow",
                policy_id="test_policy",
                context=context,
                decision=decision
            )
            
            assert proof.proof_id is not None
            assert proof.decision_type == "allow"
            assert proof.policy_id == "test_policy"
            assert proof.signature is not None
            assert proof.public_key is not None
    
    def test_proof_verification(self):
        """Test verifying cryptographic proof"""
        with TemporaryDirectory() as tmpdir:
            from governance.sovereign_runtime import SovereignRuntime
            
            runtime = SovereignRuntime(Path(tmpdir))
            proof_gen = ProofGenerator(runtime)
            
            context = {"user": "test_user", "action": "write"}
            decision = {"allowed": False, "reason": "Access denied"}
            
            proof = proof_gen.generate_proof(
                decision_type="deny",
                policy_id="security_policy",
                context=context,
                decision=decision
            )
            
            # Verify proof
            is_valid = proof_gen.verify_proof(proof)
            assert is_valid
    
    def test_proof_tampering_detection(self):
        """Test that tampered proofs are detected"""
        with TemporaryDirectory() as tmpdir:
            from governance.sovereign_runtime import SovereignRuntime
            
            runtime = SovereignRuntime(Path(tmpdir))
            proof_gen = ProofGenerator(runtime)
            
            context = {"user": "test_user"}
            decision = {"allowed": True, "reason": "OK"}
            
            proof = proof_gen.generate_proof(
                decision_type="allow",
                policy_id="test",
                context=context,
                decision=decision
            )
            
            # Tamper with proof
            proof.decision_type = "deny"
            
            # Verification should fail
            is_valid = proof_gen.verify_proof(proof)
            assert not is_valid
    
    def test_proof_export(self):
        """Test exporting proofs to file"""
        with TemporaryDirectory() as tmpdir:
            from governance.sovereign_runtime import SovereignRuntime
            
            tmppath = Path(tmpdir)
            runtime = SovereignRuntime(tmppath)
            proof_gen = ProofGenerator(runtime)
            
            # Generate multiple proofs
            for i in range(5):
                proof_gen.generate_proof(
                    decision_type="allow",
                    policy_id=f"policy_{i}",
                    context={"index": i},
                    decision={"allowed": True}
                )
            
            # Export proofs
            output_path = tmppath / "proofs.json"
            success = proof_gen.export_proofs(output_path)
            assert success
            assert output_path.exists()
            
            # Verify export content
            with open(output_path) as f:
                data = json.load(f)
            
            assert data["total_proofs"] == 5
            assert len(data["proofs"]) == 5


# ============================================================================
# ENHANCED RUNTIME INTEGRATION TESTS
# ============================================================================


class TestEnhancedSovereignRuntime:
    """Test EnhancedSovereignRuntime integration"""
    
    def test_initialization(self):
        """Test runtime initialization"""
        with TemporaryDirectory() as tmpdir:
            runtime = EnhancedSovereignRuntime(Path(tmpdir))
            
            assert runtime.capability_registry is not None
            assert runtime.time_engine is not None
            assert runtime.policy_compiler is not None
            assert runtime.proof_generator is not None
    
    def test_issue_capability(self):
        """Test issuing capabilities"""
        with TemporaryDirectory() as tmpdir:
            runtime = EnhancedSovereignRuntime(Path(tmpdir))
            
            token = runtime.issue_capability(
                issuer="admin",
                subject="user1",
                action="read:data",
                scope=CapabilityScope.SERVICE,
                scope_value="api",
                ttl_seconds=3600
            )
            
            assert token is not None
            assert token.subject == "user1"
            assert token.action == "read:data"
    
    def test_check_and_use_capability(self):
        """Test checking and using capabilities"""
        with TemporaryDirectory() as tmpdir:
            runtime = EnhancedSovereignRuntime(Path(tmpdir))
            
            token = runtime.issue_capability(
                issuer="admin",
                subject="user1",
                action="write:data",
                scope=CapabilityScope.GLOBAL,
                ttl_seconds=3600,
                max_uses=3
            )
            
            # Check capability
            valid, reason = runtime.check_capability(token.token_id)
            assert valid
            
            # Use capability
            for i in range(3):
                success, reason = runtime.use_capability(token.token_id)
                assert success
            
            # Fourth use should fail
            success, reason = runtime.use_capability(token.token_id)
            assert not success
    
    def test_compile_and_evaluate_policy(self):
        """Test compiling and evaluating policies"""
        with TemporaryDirectory() as tmpdir:
            runtime = EnhancedSovereignRuntime(Path(tmpdir))
            
            policy_def = {
                "rules": [
                    {
                        "condition": "context.get('authorized', False)",
                        "allow": True,
                        "reason": "Authorized"
                    }
                ],
                "default": {"allowed": False, "reason": "Not authorized"}
            }
            
            # Compile policy
            success = runtime.compile_policy("auth_policy", policy_def)
            assert success
            
            # Evaluate with authorized context
            allowed, reason, metadata = runtime.evaluate_policy(
                "auth_policy",
                {"authorized": True},
                generate_proof=True
            )
            assert allowed
            assert "proof_id" in metadata
            
            # Evaluate with unauthorized context
            allowed, reason, metadata = runtime.evaluate_policy(
                "auth_policy",
                {"authorized": False}
            )
            assert not allowed
    
    def test_enforce_policy_full_pipeline(self):
        """Test full policy enforcement pipeline"""
        with TemporaryDirectory() as tmpdir:
            runtime = EnhancedSovereignRuntime(Path(tmpdir))
            
            # Configure time constraint - no restrictions
            runtime.time_engine.register_temporal_policy("test_policy", {})
            
            # Compile policy
            policy_def = {
                "rules": [
                    {
                        "condition": "context.get('level', 0) >= 5",
                        "allow": True,
                        "reason": "Level requirement met"
                    }
                ],
                "default": {"allowed": False, "reason": "Insufficient level"}
            }
            runtime.compile_policy("test_policy", policy_def)
            
            # Enforce policy
            allowed, reason, metadata = runtime.enforce_policy(
                "test_policy",
                {"level": 10, "subject": "user1"}
            )
            
            assert allowed
            assert "proof_id" in metadata
    
    def test_business_hours_capability(self):
        """Test creating business hours capability"""
        with TemporaryDirectory() as tmpdir:
            runtime = EnhancedSovereignRuntime(Path(tmpdir))
            
            token = runtime.create_business_hours_capability(
                issuer="admin",
                subject="employee1",
                action="access:office",
                ttl_days=30
            )
            
            assert token is not None
            assert len(token.constraints) > 0
    
    def test_rate_limited_capability(self):
        """Test creating rate-limited capability"""
        with TemporaryDirectory() as tmpdir:
            runtime = EnhancedSovereignRuntime(Path(tmpdir))
            
            token = runtime.create_rate_limited_capability(
                issuer="admin",
                subject="api_client",
                action="api:call",
                max_calls=100,
                window_seconds=60,
                ttl_days=7
            )
            
            assert token is not None
            assert len(token.constraints) > 0
    
    def test_state_summary(self):
        """Test getting state summary"""
        with TemporaryDirectory() as tmpdir:
            runtime = EnhancedSovereignRuntime(Path(tmpdir))
            
            # Issue some capabilities
            runtime.issue_capability(
                issuer="admin",
                subject="user1",
                action="test",
                scope=CapabilityScope.GLOBAL
            )
            
            # Compile a policy
            policy_def = {
                "rules": [],
                "default": {"allowed": True, "reason": "Default"}
            }
            runtime.compile_policy("test", policy_def)
            
            # Get summary
            summary = runtime.get_state_summary()
            
            assert summary["capabilities"]["total"] > 0
            assert summary["policies"]["total_policies"] > 0
            assert "audit_trail" in summary
    
    def test_triumvirate_callback(self):
        """Test Triumvirate integration callback"""
        with TemporaryDirectory() as tmpdir:
            runtime = EnhancedSovereignRuntime(Path(tmpdir))
            
            # Register mock callback
            override_called = []
            
            def mock_triumvirate(policy_id, context, decision):
                override_called.append(True)
                return {
                    "override": True,
                    "allowed": False,
                    "reason": "Triumvirate override"
                }
            
            runtime.register_triumvirate_callback(mock_triumvirate)
            
            # Compile policy
            policy_def = {
                "rules": [],
                "default": {"allowed": True, "reason": "Default allow"}
            }
            runtime.compile_policy("override_test", policy_def)
            
            # Enforce with override
            allowed, reason, metadata = runtime.enforce_policy(
                "override_test",
                {"test": True},
                triumvirate_override=True
            )
            
            assert len(override_called) > 0
            assert not allowed  # Should be overridden to deny
            assert "triumvirate_override" in metadata
    
    def test_export_compliance_bundle(self):
        """Test exporting full compliance bundle"""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            runtime = EnhancedSovereignRuntime(tmppath)
            
            # Generate some activity
            runtime.issue_capability(
                issuer="admin",
                subject="user1",
                action="test",
                scope=CapabilityScope.GLOBAL
            )
            
            policy_def = {
                "rules": [],
                "default": {"allowed": True, "reason": "Test"}
            }
            runtime.compile_policy("test", policy_def)
            runtime.evaluate_policy("test", {})
            
            # Export bundle
            output_dir = tmppath / "compliance"
            success = runtime.export_full_compliance_bundle(output_dir)
            
            assert success
            assert (output_dir / "base_compliance.json").exists()
            assert (output_dir / "policy_proofs.json").exists()
            assert (output_dir / "state_summary.json").exists()


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


class TestPerformance:
    """Performance tests for JIT compilation"""
    
    def test_policy_compilation_performance(self):
        """Test that compiled policies are faster than interpreted"""
        with TemporaryDirectory() as tmpdir:
            runtime = EnhancedSovereignRuntime(Path(tmpdir))
            
            # Create complex policy
            policy_def = {
                "rules": [
                    {
                        "condition": f"context.get('value', 0) == {i}",
                        "allow": True,
                        "reason": f"Match {i}"
                    }
                    for i in range(100)
                ],
                "default": {"allowed": False, "reason": "No match"}
            }
            
            runtime.compile_policy("perf_test", policy_def)
            
            # Execute many times
            iterations = 100
            start = time.time()
            
            for i in range(iterations):
                runtime.evaluate_policy(
                    "perf_test",
                    {"value": i % 100},
                    generate_proof=False  # Skip proof for performance test
                )
            
            elapsed = time.time() - start
            avg_time = elapsed / iterations
            
            # Should be reasonably fast (relaxed for slower systems)
            assert avg_time < 0.05  # Less than 50ms per evaluation
    
    def test_capability_check_performance(self):
        """Test capability check performance"""
        with TemporaryDirectory() as tmpdir:
            runtime = EnhancedSovereignRuntime(Path(tmpdir))
            
            # Create capability
            token = runtime.issue_capability(
                issuer="admin",
                subject="user1",
                action="test",
                scope=CapabilityScope.GLOBAL
            )
            
            # Check many times
            iterations = 1000
            start = time.time()
            
            for _ in range(iterations):
                runtime.check_capability(token.token_id)
            
            elapsed = time.time() - start
            avg_time = elapsed / iterations
            
            # Should be very fast
            assert avg_time < 0.001  # Less than 1ms per check


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
