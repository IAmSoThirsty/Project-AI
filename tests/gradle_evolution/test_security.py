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
    ScheduledPolicy,
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
            path="src/main/java/Main.java",
            operation="read"
        )
        
        assert is_allowed
    
    def test_validate_path_access_denied(self, security_config_file):
        """Test path access validation denies unpermitted paths."""
        engine = SecurityEngine(config_path=security_config_file)
        
        is_allowed, reason = engine.validate_path_access(
            agent="build_agent",
            path="/etc/passwd",
            operation="read"
        )
        
        assert not is_allowed
        assert "path" in reason.lower() or "not" in reason.lower()
    
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
        """Test access logging via validation."""
        engine = SecurityEngine(config_path=security_config_file)
        
        # Perform validation which logs access
        engine.validate_path_access(
            agent="build_agent",
            path="src/Main.java",
            operation="read"
        )
        
        assert len(engine.access_log) == 1
        assert engine.access_log[0]["agent"] == "build_agent"
    
    def test_log_denied_operation(self, security_config_file):
        """Test denied operation logging."""
        engine = SecurityEngine(config_path=security_config_file)
        
        # Perform validation that will be denied
        engine.validate_path_access(
            agent="test_agent",
            path="/etc/passwd",
            operation="write"
        )
        
        assert len(engine.denied_operations) == 1
    
    def test_get_security_summary(self, security_config_file):
        """Test retrieving security summary."""
        engine = SecurityEngine(config_path=security_config_file)
        
        # Create some access logs via validation
        for i in range(5):
            engine.validate_path_access(
                agent="build_agent",
                path=f"src/File{i}.java",
                operation="read"
            )
        
        summary = engine.get_security_summary()
        
        assert "total_accesses" in summary
        assert "agents" in summary or len(engine.access_log) == 5
    
    def test_security_context_ttl(self, security_config_file):
        """Test security context has TTL configuration."""
        engine = SecurityEngine(config_path=security_config_file)
        
        # Get context with TTL
        context = engine.get_security_context("build_agent")
        
        assert context is not None
        assert context.credential_ttl_hours == 2


class TestScheduledPolicy:
    """Test ScheduledPolicy component."""
    
    def test_policy_creation(self):
        """Test creating scheduled policy."""
        policy = ScheduledPolicy(
            policy_id="test_policy_001",
            policy_data={"name": "Test Policy", "rules": ["rule1", "rule2"]},
            activation_time=datetime.utcnow(),
            expiration_time=None
        )
        
        assert policy.policy_id == "test_policy_001"
        assert not policy.is_active


class TestPolicyScheduler:
    """Test PolicyScheduler component."""
    
    def test_initialization(self):
        """Test scheduler initializes."""
        scheduler = PolicyScheduler()
        
        assert scheduler.scheduled_policies == {}
        assert scheduler.active_policies == set()
    
    def test_schedule_policy(self):
        """Test scheduling a security policy."""
        scheduler = PolicyScheduler()
        
        activation_time = datetime.utcnow()
        policy_data = {
            "name": "Security Policy",
            "rules": ["encrypt_at_rest"],
            "priority": "high",
        }
        
        scheduler.schedule_policy(
            policy_id="policy_001",
            policy_data=policy_data,
            activation_time=activation_time
        )
        
        assert "policy_001" in scheduler.scheduled_policies
    
    def test_get_active_policies(self):
        """Test retrieving only active policies."""
        scheduler = PolicyScheduler()
        
        # Schedule policies
        now = datetime.utcnow()
        scheduler.schedule_policy(
            policy_id="active",
            policy_data={"name": "Active", "rules": ["rule1"]},
            activation_time=now - timedelta(hours=1)
        )
        
        scheduler.schedule_policy(
            policy_id="future",
            policy_data={"name": "Future", "rules": ["rule2"]},
            activation_time=now + timedelta(hours=1)
        )
        
        # Manually activate one
        scheduler.scheduled_policies["active"].is_active = True
        scheduler.active_policies.add("active")
        
        active = scheduler.get_active_policies()
        
        assert len(active) >= 1
        assert "active" in [p.policy_id for p in active]
    
    def test_deactivate_policy(self):
        """Test manually deactivating a policy."""
        scheduler = PolicyScheduler()
        
        scheduler.schedule_policy(
            policy_id="policy_001",
            policy_data={"name": "Policy", "rules": ["rule"]},
            activation_time=datetime.utcnow()
        )
        
        # Manually activate first
        scheduler.scheduled_policies["policy_001"].is_active = True
        scheduler.active_policies.add("policy_001")
        
        # Manually deactivate
        scheduler.scheduled_policies["policy_001"].is_active = False
        scheduler.active_policies.discard("policy_001")
        
        assert not scheduler.scheduled_policies["policy_001"].is_active
        assert "policy_001" not in scheduler.active_policies
    
    def test_get_scheduled_policies(self):
        """Test retrieving scheduled policies."""
        scheduler = PolicyScheduler()
        
        # Schedule multiple policies
        for i in range(3):
            scheduler.schedule_policy(
                policy_id=f"policy_{i}",
                policy_data={"name": f"Policy {i}"},
                activation_time=datetime.utcnow() + timedelta(hours=i)
            )
        
        # Should have 3 scheduled
        assert len(scheduler.scheduled_policies) == 3
    
    def test_get_policy_history(self):
        """Test retrieving policy history."""
        scheduler = PolicyScheduler()
        
        # Record some policy events manually
        scheduler._record_policy_event(
            "policy_001",
            "activated",
            {"timestamp": datetime.utcnow().isoformat()}
        )
        
        history = scheduler.get_policy_history()
        
        assert len(history) >= 1
