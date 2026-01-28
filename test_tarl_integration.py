#!/usr/bin/env python3
"""
Test TARL Integration - Comprehensive Tests

This test suite verifies the complete TARL integration including:
- TARL policy evaluation
- Kernel execution with TARL enforcement
- CodexDeus escalation handling
- Governance integration
"""

import pytest
from tarl.runtime import TarlRuntime
from tarl.policies.default import DEFAULT_POLICIES
from tarl.spec import TarlVerdict, TarlDecision
from kernel.execution import ExecutionKernel
from kernel.tarl_gate import TarlGate, TarlEnforcementError
from governance.core import GovernanceCore
from src.cognition.codex.escalation import CodexDeus, EscalationLevel


def test_tarl_allow_policy():
    """Test that TARL allows valid contexts."""
    runtime = TarlRuntime(DEFAULT_POLICIES)
    context = {
        "agent": "test_agent",
        "mutation": False,
        "mutation_allowed": False,
    }
    decision = runtime.evaluate(context)
    assert decision.verdict == TarlVerdict.ALLOW


def test_tarl_deny_unauthorized_mutation():
    """Test that TARL denies unauthorized mutations."""
    runtime = TarlRuntime(DEFAULT_POLICIES)
    context = {
        "agent": "test_agent",
        "mutation": True,
        "mutation_allowed": False,
    }
    decision = runtime.evaluate(context)
    assert decision.verdict == TarlVerdict.DENY
    assert "Mutation not permitted" in decision.reason


def test_tarl_escalate_unknown_agent():
    """Test that TARL escalates on unknown agents."""
    runtime = TarlRuntime(DEFAULT_POLICIES)
    context = {
        "agent": None,
        "mutation": False,
        "mutation_allowed": False,
    }
    decision = runtime.evaluate(context)
    assert decision.verdict == TarlVerdict.ESCALATE
    assert "Unknown agent" in decision.reason


def test_tarl_gate_enforce_allow():
    """Test TARL gate allows valid contexts."""
    runtime = TarlRuntime(DEFAULT_POLICIES)
    codex = CodexDeus()
    gate = TarlGate(runtime, codex)
    
    context = {
        "agent": "test_agent",
        "mutation": False,
        "mutation_allowed": False,
    }
    
    decision = gate.enforce(context)
    assert decision.verdict == TarlVerdict.ALLOW


def test_tarl_gate_enforce_deny():
    """Test TARL gate raises error on deny."""
    runtime = TarlRuntime(DEFAULT_POLICIES)
    codex = CodexDeus()
    gate = TarlGate(runtime, codex)
    
    context = {
        "agent": "test_agent",
        "mutation": True,
        "mutation_allowed": False,
    }
    
    with pytest.raises(TarlEnforcementError) as exc_info:
        gate.enforce(context)
    assert "Denied" in str(exc_info.value)


def test_tarl_gate_enforce_escalate():
    """Test TARL gate raises error on escalation."""
    runtime = TarlRuntime(DEFAULT_POLICIES)
    codex = CodexDeus()
    gate = TarlGate(runtime, codex)
    
    context = {
        "agent": None,
        "mutation": False,
        "mutation_allowed": False,
    }
    
    # This should raise SystemExit due to HIGH escalation level
    with pytest.raises(SystemExit) as exc_info:
        gate.enforce(context)
    assert "CRITICAL ESCALATION" in str(exc_info.value)


def test_execution_kernel_integration():
    """Test full execution kernel integration."""
    runtime = TarlRuntime(DEFAULT_POLICIES)
    codex = CodexDeus()
    governance = GovernanceCore()
    kernel = ExecutionKernel(governance, runtime, codex)
    
    # Valid context should succeed
    context = {
        "agent": "test_agent",
        "mutation": False,
        "mutation_allowed": False,
    }
    
    result = kernel.execute("test_action", context)
    assert result["status"] == "success"


def test_execution_kernel_deny():
    """Test execution kernel denies unauthorized mutations."""
    runtime = TarlRuntime(DEFAULT_POLICIES)
    codex = CodexDeus()
    governance = GovernanceCore()
    kernel = ExecutionKernel(governance, runtime, codex)
    
    # Invalid context should raise error
    context = {
        "agent": "test_agent",
        "mutation": True,
        "mutation_allowed": False,
    }
    
    with pytest.raises(TarlEnforcementError):
        kernel.execute("test_action", context)


def test_governance_core():
    """Test governance core functionality."""
    governance = GovernanceCore()
    
    # Test policy management
    governance.add_policy("test_policy")
    assert len(governance.policies) == 1
    
    # Test audit logging
    governance.audit({"event": "test_event"})
    audit_log = governance.get_audit_log()
    assert len(audit_log) == 1
    assert audit_log[0]["event"] == "test_event"


if __name__ == "__main__":
    # Run tests manually without pytest
    print("Running TARL integration tests...")
    
    tests = [
        test_tarl_allow_policy,
        test_tarl_deny_unauthorized_mutation,
        test_tarl_escalate_unknown_agent,
        test_tarl_gate_enforce_allow,
        test_tarl_gate_enforce_deny,
        test_execution_kernel_integration,
        test_execution_kernel_deny,
        test_governance_core,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All tests passed!")
    else:
        print(f"✗ {failed} test(s) failed")
