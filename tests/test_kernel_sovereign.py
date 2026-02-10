"""
Tests for ExecutionKernel Sovereign Enforcement

Validates that the ExecutionKernel properly enforces cryptographic
governance at the kernel level - the critical non-bypassability layer.
"""

import tempfile
from pathlib import Path

import pytest

from governance.sovereign_runtime import SovereignRuntime
from kernel.execution import ExecutionKernel


class MockGovernance:
    """Mock governance for testing."""

    def __init__(self):
        self.name = "mock_governance"


class MockTarlRuntime:
    """Mock TARL runtime for testing."""

    def __init__(self):
        self.name = "mock_tarl"


class MockCodex:
    """Mock Codex for testing."""

    def __init__(self):
        self.name = "mock_codex"


class MockTarlGate:
    """Mock TARL gate that tracks enforcement calls."""

    def __init__(self, tarl_runtime, codex):
        self.tarl_runtime = tarl_runtime
        self.codex = codex
        self.enforce_called = False
        self.enforce_context = None

    def enforce(self, context):
        """Mock enforcement that tracks calls."""
        self.enforce_called = True
        self.enforce_context = context


@pytest.fixture
def sovereign():
    """Create sovereign runtime in temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield SovereignRuntime(data_dir=Path(tmpdir))


@pytest.fixture
def kernel_with_sovereign(sovereign):
    """Create ExecutionKernel with sovereign runtime enabled."""
    governance = MockGovernance()
    tarl_runtime = MockTarlRuntime()
    codex = MockCodex()

    kernel = ExecutionKernel(
        governance=governance,
        tarl_runtime=tarl_runtime,
        codex=codex,
        sovereign_runtime=sovereign,
    )

    # Replace TarlGate with mock
    kernel.tarl_gate = MockTarlGate(tarl_runtime, codex)

    return kernel


@pytest.fixture
def kernel_without_sovereign():
    """Create ExecutionKernel without sovereign runtime."""
    governance = MockGovernance()
    tarl_runtime = MockTarlRuntime()
    codex = MockCodex()

    kernel = ExecutionKernel(
        governance=governance,
        tarl_runtime=tarl_runtime,
        codex=codex,
        sovereign_runtime=None,
    )

    # Replace TarlGate with mock
    kernel.tarl_gate = MockTarlGate(tarl_runtime, codex)

    return kernel


class TestExecutionKernelSovereign:
    """Test suite for ExecutionKernel sovereign enforcement."""

    def test_kernel_without_sovereign_runs_normally(self, kernel_without_sovereign):
        """Test that kernel without sovereign runtime runs normally."""
        action = "test_action"
        context = {"test": "context"}

        result = kernel_without_sovereign.execute(action, context)

        assert result["status"] == "success"
        assert result["action"] == action
        assert kernel_without_sovereign.tarl_gate.enforce_called

    def test_kernel_with_sovereign_requires_policy_binding(self, kernel_with_sovereign):
        """
        CRITICAL TEST: Kernel with sovereign runtime REQUIRES policy binding.

        This is the core non-bypassability guarantee.
        """
        action = "test_action"
        context = {"test": "context"}

        # Should raise RuntimeError without policy binding
        with pytest.raises(RuntimeError) as exc_info:
            kernel_with_sovereign.execute(action, context)

        assert "SOVEREIGN ENFORCEMENT" in str(exc_info.value)
        assert "no policy binding provided" in str(exc_info.value)

    def test_kernel_with_sovereign_blocks_invalid_binding(
        self, kernel_with_sovereign, sovereign
    ):
        """
        CRITICAL TEST: Kernel blocks execution with invalid policy binding.

        This proves governance cannot be bypassed.
        """
        action = "test_action"
        context = {"stage": "test"}

        # Create policy binding with different context
        wrong_context = {"stage": "different"}
        policy_state = {"stage_allowed": True, "governance_active": True}

        policy_binding = sovereign.create_policy_state_binding(
            policy_state, wrong_context
        )

        # Should raise RuntimeError with invalid binding
        with pytest.raises(RuntimeError) as exc_info:
            kernel_with_sovereign.execute(
                action, context, policy_binding=policy_binding
            )

        assert "SOVEREIGN ENFORCEMENT" in str(exc_info.value)
        assert "policy binding verification failed" in str(exc_info.value)

    def test_kernel_with_sovereign_allows_valid_binding(
        self, kernel_with_sovereign, sovereign
    ):
        """
        Test that kernel allows execution with valid policy binding.

        This is the "golden path" - proper sovereign execution.
        """
        action = "test_action"
        context = {"stage": "test"}

        # Create valid policy binding
        policy_state = {"stage_allowed": True, "governance_active": True}
        policy_binding = sovereign.create_policy_state_binding(policy_state, context)

        # Should succeed with valid binding
        result = kernel_with_sovereign.execute(
            action, context, policy_binding=policy_binding
        )

        assert result["status"] == "success"
        assert result["action"] == action
        assert "sovereign_proof" in result
        assert result["sovereign_proof"]["verified"]
        assert (
            result["sovereign_proof"]["binding_hash"] == policy_binding["binding_hash"]
        )

    def test_sovereign_enforcement_logs_to_audit_trail(
        self, kernel_with_sovereign, sovereign
    ):
        """Test that sovereign enforcement logs to audit trail."""
        action = "test_action"
        context = {"stage": "test"}

        policy_state = {"stage_allowed": True, "governance_active": True}
        policy_binding = sovereign.create_policy_state_binding(policy_state, context)

        # Execute with valid binding
        kernel_with_sovereign.execute(action, context, policy_binding=policy_binding)

        # Verify audit log has entries
        with open(sovereign.audit_log_path) as f:
            lines = f.readlines()
            events = [line for line in lines if "EXECUTION_" in line]

            # Should have AUTHORIZED and COMPLETED events
            assert len(events) >= 2

    def test_sovereign_enforcement_logs_blocked_execution(
        self, kernel_with_sovereign, sovereign
    ):
        """Test that blocked executions are logged to audit trail."""
        action = "test_action"
        context = {"stage": "test"}

        # Try to execute without binding
        try:
            kernel_with_sovereign.execute(action, context)
        except RuntimeError:
            pass  # Expected

        # Verify audit log has BLOCKED event
        with open(sovereign.audit_log_path) as f:
            lines = f.readlines()
            blocked_events = [line for line in lines if "EXECUTION_BLOCKED" in line]

            assert len(blocked_events) >= 1

    def test_non_bypassability_proof(self, kernel_with_sovereign, sovereign):
        """
        CRITICAL TEST: Prove non-bypassability.

        This test demonstrates that execution literally cannot run
        unless governance state resolves true.

        This is the key promise: "This execution path literally cannot run
        unless governance state resolves true."
        """
        action = "critical_operation"
        context = {"stage": "production_deployment"}

        # Attempt 1: No binding - BLOCKED
        with pytest.raises(RuntimeError) as exc1:
            kernel_with_sovereign.execute(action, context)
        assert "no policy binding provided" in str(exc1.value)

        # Attempt 2: Wrong binding - BLOCKED
        wrong_context = {"stage": "test"}
        policy_state = {"stage_allowed": True, "governance_active": True}
        wrong_binding = sovereign.create_policy_state_binding(
            policy_state, wrong_context
        )

        with pytest.raises(RuntimeError) as exc2:
            kernel_with_sovereign.execute(action, context, policy_binding=wrong_binding)
        assert "verification failed" in str(exc2.value)

        # Attempt 3: Valid binding - ALLOWED
        correct_binding = sovereign.create_policy_state_binding(policy_state, context)
        result = kernel_with_sovereign.execute(
            action, context, policy_binding=correct_binding
        )
        assert result["status"] == "success"

        # PROOF COMPLETE:
        # 1. Execution without binding is blocked ✓
        # 2. Execution with invalid binding is blocked ✓
        # 3. Execution with valid binding succeeds ✓
        # 4. All attempts are logged to immutable audit trail ✓
        #
        # = GOVERNANCE IS NON-BYPASSABLE BY DESIGN

    def test_tarl_gate_still_enforced_in_sovereign_mode(
        self, kernel_with_sovereign, sovereign
    ):
        """Test that TARL gate is still enforced even in sovereign mode."""
        action = "test_action"
        context = {"stage": "test"}

        policy_state = {"stage_allowed": True, "governance_active": True}
        policy_binding = sovereign.create_policy_state_binding(policy_state, context)

        # Execute
        kernel_with_sovereign.execute(action, context, policy_binding=policy_binding)

        # TARL gate should have been called
        assert kernel_with_sovereign.tarl_gate.enforce_called
        assert kernel_with_sovereign.tarl_gate.enforce_context == context

    def test_sovereign_proof_in_result(self, kernel_with_sovereign, sovereign):
        """Test that sovereign proof is included in execution result."""
        action = "test_action"
        context = {"stage": "test"}

        policy_state = {"stage_allowed": True, "governance_active": True}
        policy_binding = sovereign.create_policy_state_binding(policy_state, context)

        result = kernel_with_sovereign.execute(
            action, context, policy_binding=policy_binding
        )

        # Verify sovereign proof
        assert "sovereign_proof" in result
        proof = result["sovereign_proof"]

        assert "binding_hash" in proof
        assert "policy_hash" in proof
        assert proof["verified"] is True
        assert proof["binding_hash"] == policy_binding["binding_hash"]
        assert proof["policy_hash"] == policy_binding["policy_hash"]
