"""
Tests for Security Engine and Policy Scheduler.

Tests security policy enforcement, least privilege controls,
and runtime security validation integrated with security_hardening.yaml.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from gradle_evolution.security.security_engine import (
    SecurityEngine,
    SecurityContext,
)
from gradle_evolution.security.policy_scheduler import (
    PolicyScheduler,
    SecurityPolicy,
)


class TestSecurityContext:
    """Test SecurityContext component."""
    
    def test_context_creation(self):
        """Test creating security context."""
        context = SecurityContext(
            agent="build_agent",
            allowed_paths=["src/**", "build/**"],
            allowed_operations=["read", "write"],
            credential_ttl_hours=2
        )
        
        assert context.agent == "build_agent"
        assert len(context.allowed_paths) == 2
        assert "read" in context.allowed_operations


class TestSecurityEngine:
    """Test SecurityEngine component."""
    
    def test_initialization_with_config(self, security_config_file):
        """Test engine initializes with config file."""
        engine = SecurityEngine(config_path=security_config_file)
        
        assert engine.config is not None
        assert "least_privilege" in engine.config
    
    def test_initialization_without_config(self, temp_dir):
        """Test engine uses defaults when config missing."""
        nonexistent = temp_dir / "missing.yaml"
        engine = SecurityEngine(config_path=nonexistent)
        
        assert engine.config is not None
        assert "least_privilege" in engine.config
    
    def test_get_security_context(self, security_config_file):
        """Test retrieving security context for agent."""
        engine = SecurityEngine(config_path=security_config_file)
        
        context = engine.get_security_context("build_agent")
        
        assert context is not None
        assert context.agent == "build_agent"
        assert "src/**" in context.allowed_paths
    
    def test_get_context_for_unknown_agent(self, security_config_file):
        """Test getting context for unknown agent returns None."""
        engine = SecurityEngine(config_path=security_config_file)
        
        context = engine.get_security_context("unknown_agent")
        
        assert context is None
    
    def test_validate_path_access_allowed(self, security_config_file):
        """Test path access validation allows permitted paths."""
        engine = SecurityEngine(config_path=security_config_file)
        
        is_allowed, reason = engine.validate_path_access(
            agent="build_agent",
            path="src/main/java/Main.java"
        )
        
        assert is_allowed
    
    def test_validate_path_access_denied(self, security_config_file):
        """Test path access validation denies unpermitted paths."""
        engine = SecurityEngine(config_path=security_config_file)
        
        is_allowed, reason = engine.validate_path_access(
            agent="build_agent",
            path="/etc/passwd"
        )
        
        assert not is_allowed
        assert "denied" in reason.lower() or "not allowed" in reason.lower()
    
    def test_validate_operation_allowed(self, security_config_file):
        """Test operation validation allows permitted operations."""
        engine = SecurityEngine(config_path=security_config_file)
        
        is_allowed, reason = engine.validate_operation(
            agent="build_agent",
            operation="read"
        )
        
        assert is_allowed
    
    def test_validate_operation_denied(self, security_config_file):
        """Test operation validation denies unpermitted operations."""
        engine = SecurityEngine(config_path=security_config_file)
        
        is_allowed, reason = engine.validate_operation(
            agent="test_agent",
            operation="write"  # test_agent can only read/execute
        )
        
        assert not is_allowed
    
    def test_log_access(self, security_config_file):
        """Test access logging."""
        engine = SecurityEngine(config_path=security_config_file)
        
        engine.log_access(
            agent="build_agent",
            path="src/Main.java",
            operation="read",
            allowed=True
        )
        
        assert len(engine.access_log) == 1
        assert engine.access_log[0]["agent"] == "build_agent"
        assert engine.access_log[0]["allowed"]
    
    def test_log_denied_operation(self, security_config_file):
        """Test denied operation logging."""
        engine = SecurityEngine(config_path=security_config_file)
        
        engine.log_access(
            agent="test_agent",
            path="/etc/passwd",
            operation="write",
            allowed=False
        )
        
        assert len(engine.denied_operations) == 1
        assert not engine.denied_operations[0]["allowed"]
    
    def test_get_access_summary(self, security_config_file):
        """Test retrieving access summary."""
        engine = SecurityEngine(config_path=security_config_file)
        
        # Create some access logs
        for i in range(5):
            engine.log_access(
                agent="build_agent",
                path=f"src/File{i}.java",
                operation="read",
                allowed=True
            )
        
        summary = engine.get_access_summary()
        
        assert summary["total_accesses"] == 5
        assert summary["allowed_accesses"] == 5
        assert summary["denied_accesses"] == 0
    
    def test_check_credential_ttl(self, security_config_file):
        """Test credential TTL checking."""
        engine = SecurityEngine(config_path=security_config_file)
        
        # Create context with 2 hour TTL
        context = engine.get_security_context("build_agent")
        
        # Check within TTL
        issue_time = datetime.utcnow()
        is_valid = engine.check_credential_ttl(context, issue_time)
        
        assert is_valid
    
    def test_credential_expired(self, security_config_file):
        """Test expired credential detection."""
        engine = SecurityEngine(config_path=security_config_file)
        
        context = engine.get_security_context("build_agent")
        
        # Check beyond TTL (3 hours ago for 2 hour TTL)
        issue_time = datetime.utcnow() - timedelta(hours=3)
        is_valid = engine.check_credential_ttl(context, issue_time)
        
        assert not is_valid


class TestSecurityPolicy:
    """Test SecurityPolicy component."""
    
    def test_policy_creation(self):
        """Test creating security policy."""
        policy = SecurityPolicy(
            policy_id="test_policy_001",
            name="Test Policy",
            rules=["rule1", "rule2"],
            priority="high",
            active=True
        )
        
        assert policy.policy_id == "test_policy_001"
        assert policy.priority == "high"
        assert policy.active
    
    def test_policy_to_dict(self):
        """Test converting policy to dictionary."""
        policy = SecurityPolicy(
            policy_id="test_policy_001",
            name="Test Policy",
            rules=["rule1"],
            priority="medium",
            active=True
        )
        
        policy_dict = policy.to_dict()
        
        assert policy_dict["policy_id"] == "test_policy_001"
        assert "rules" in policy_dict


class TestPolicyScheduler:
    """Test PolicyScheduler component."""
    
    def test_initialization(self, temp_dir):
        """Test scheduler initializes."""
        storage = temp_dir / "policies.json"
        scheduler = PolicyScheduler(storage_path=storage)
        
        assert scheduler.storage_path == storage
        assert scheduler.policies == {}
    
    def test_add_policy(self, temp_dir):
        """Test adding a security policy."""
        storage = temp_dir / "policies.json"
        scheduler = PolicyScheduler(storage_path=storage)
        
        policy = SecurityPolicy(
            policy_id="policy_001",
            name="Security Policy",
            rules=["encrypt_at_rest"],
            priority="high",
            active=True
        )
        
        scheduler.add_policy(policy)
        
        assert policy.policy_id in scheduler.policies
    
    def test_get_active_policies(self, temp_dir):
        """Test retrieving only active policies."""
        storage = temp_dir / "policies.json"
        scheduler = PolicyScheduler(storage_path=storage)
        
        active_policy = SecurityPolicy(
            policy_id="active",
            name="Active",
            rules=["rule1"],
            priority="high",
            active=True
        )
        
        inactive_policy = SecurityPolicy(
            policy_id="inactive",
            name="Inactive",
            rules=["rule2"],
            priority="low",
            active=False
        )
        
        scheduler.add_policy(active_policy)
        scheduler.add_policy(inactive_policy)
        
        active = scheduler.get_active_policies()
        
        assert len(active) == 1
        assert active[0].policy_id == "active"
    
    def test_deactivate_policy(self, temp_dir):
        """Test deactivating a policy."""
        storage = temp_dir / "policies.json"
        scheduler = PolicyScheduler(storage_path=storage)
        
        policy = SecurityPolicy(
            policy_id="policy_001",
            name="Policy",
            rules=["rule"],
            priority="medium",
            active=True
        )
        
        scheduler.add_policy(policy)
        scheduler.deactivate_policy("policy_001")
        
        assert not scheduler.policies["policy_001"].active
    
    def test_get_policies_by_priority(self, temp_dir):
        """Test filtering policies by priority."""
        storage = temp_dir / "policies.json"
        scheduler = PolicyScheduler(storage_path=storage)
        
        high_policy = SecurityPolicy(
            policy_id="high",
            name="High",
            rules=["rule1"],
            priority="high",
            active=True
        )
        
        low_policy = SecurityPolicy(
            policy_id="low",
            name="Low",
            rules=["rule2"],
            priority="low",
            active=True
        )
        
        scheduler.add_policy(high_policy)
        scheduler.add_policy(low_policy)
        
        high_policies = scheduler.get_policies_by_priority("high")
        
        assert len(high_policies) == 1
        assert high_policies[0].priority == "high"
    
    def test_persistence(self, temp_dir):
        """Test policy persistence to disk."""
        storage = temp_dir / "policies.json"
        scheduler = PolicyScheduler(storage_path=storage)
        
        policy = SecurityPolicy(
            policy_id="policy_001",
            name="Policy",
            rules=["rule"],
            priority="medium",
            active=True
        )
        
        scheduler.add_policy(policy)
        scheduler.save()
        
        # Load in new scheduler
        new_scheduler = PolicyScheduler(storage_path=storage)
        new_scheduler.load()
        
        assert "policy_001" in new_scheduler.policies
    
    def test_evaluate_policies(self, temp_dir):
        """Test evaluating policies against context."""
        storage = temp_dir / "policies.json"
        scheduler = PolicyScheduler(storage_path=storage)
        
        policy = SecurityPolicy(
            policy_id="encryption",
            name="Encryption Required",
            rules=["encrypt_at_rest", "encrypt_in_transit"],
            priority="critical",
            active=True
        )
        
        scheduler.add_policy(policy)
        
        context = {"encryption": "none"}
        violations = scheduler.evaluate_policies(context)
        
        # Should detect encryption policy violation
        assert len(violations) > 0 or "violations" in str(violations)
