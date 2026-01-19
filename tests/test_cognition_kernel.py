"""
Tests for CognitionKernel - Central processing hub for all executions.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from app.core.cognition_kernel import (
    CognitionKernel,
    ExecutionType,
    ExecutionStatus,
    ExecutionResult,
)


class TestCognitionKernel:
    """Test suite for CognitionKernel."""
    
    @pytest.fixture
    def mock_subsystems(self):
        """Create mock subsystems for testing."""
        identity = Mock()
        memory = Mock()
        memory.add_memory = Mock(return_value="mem_123")
        governance = Mock()
        governance.validate_action = Mock(return_value={"allowed": True, "reason": "Test approved"})
        reflection = Mock()
        triumvirate = Mock()
        triumvirate.process = Mock(return_value={"success": True, "output": "approved"})
        
        return {
            "identity": identity,
            "memory": memory,
            "governance": governance,
            "reflection": reflection,
            "triumvirate": triumvirate,
        }
    
    @pytest.fixture
    def kernel(self, mock_subsystems):
        """Create a CognitionKernel with mock subsystems."""
        return CognitionKernel(
            identity_system=mock_subsystems["identity"],
            memory_engine=mock_subsystems["memory"],
            governance_system=mock_subsystems["governance"],
            reflection_engine=mock_subsystems["reflection"],
            triumvirate=mock_subsystems["triumvirate"],
            data_dir="data/test",
        )
    
    def test_kernel_initialization(self, kernel):
        """Test that kernel initializes with all subsystems."""
        assert kernel.identity_system is not None
        assert kernel.memory_engine is not None
        assert kernel.governance_system is not None
        assert kernel.reflection_engine is not None
        assert kernel.triumvirate is not None
        assert kernel.execution_count == 0
        assert len(kernel.execution_history) == 0
    
    def test_simple_execution(self, kernel):
        """Test a simple execution through the kernel."""
        # Define a test action
        def test_action(x, y):
            return x + y
        
        # Process through kernel
        result = kernel.process(
            action=test_action,
            action_name="test_addition",
            execution_type=ExecutionType.AGENT_ACTION,
            action_args=(2, 3),
            user_id="test_user",
        )
        
        # Verify result
        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert result.result == 5
        assert result.governance_approved is True
        assert result.error is None
        
        # Verify kernel state
        assert kernel.execution_count == 1
        assert len(kernel.execution_history) == 1
    
    def test_execution_with_kwargs(self, kernel):
        """Test execution with keyword arguments."""
        def test_action(name, greeting="Hello"):
            return f"{greeting}, {name}"
        
        result = kernel.process(
            action=test_action,
            action_name="test_greeting",
            execution_type=ExecutionType.TOOL_INVOCATION,
            action_kwargs={"name": "Alice", "greeting": "Hi"},
        )
        
        assert result.success is True
        assert result.result == "Hi, Alice"
    
    def test_execution_blocked_by_governance(self, kernel, mock_subsystems):
        """Test that governance can block executions."""
        # Configure governance to block
        mock_subsystems["governance"].validate_action = Mock(
            return_value={"allowed": False, "reason": "Test blocked"}
        )
        
        def test_action():
            return "Should not execute"
        
        result = kernel.process(
            action=test_action,
            action_name="blocked_action",
            execution_type=ExecutionType.AGENT_ACTION,
            requires_approval=True,
        )
        
        # Verify execution was blocked
        assert result.success is False
        assert result.governance_approved is False
        assert result.blocked_reason is not None
        assert "blocked" in result.blocked_reason.lower()
    
    def test_execution_with_triumvirate_approval(self, kernel, mock_subsystems):
        """Test execution with Triumvirate approval (when governance system is not configured)."""
        # Remove governance system so Triumvirate is used
        kernel.governance_system = None
        
        def test_action():
            return "approved"
        
        result = kernel.process(
            action=test_action,
            action_name="triumvirate_test",
            execution_type=ExecutionType.AGENT_ACTION,
            requires_approval=True,
            risk_level="high",
        )
        
        # Verify Triumvirate was called
        mock_subsystems["triumvirate"].process.assert_called_once()
        
        # Verify execution succeeded
        assert result.success is True
        assert result.governance_approved is True
    
    def test_execution_failure_handling(self, kernel):
        """Test that execution failures are properly handled."""
        def failing_action():
            raise ValueError("Test error")
        
        result = kernel.process(
            action=failing_action,
            action_name="failing_action",
            execution_type=ExecutionType.AGENT_ACTION,
        )
        
        # Verify failure is captured
        assert result.success is False
        assert result.error is not None
        assert "Test error" in result.error
        
        # Verify execution is still recorded
        assert kernel.execution_count == 1
    
    def test_memory_recording(self, kernel, mock_subsystems):
        """Test that executions are recorded in memory."""
        def test_action():
            return "test result"
        
        result = kernel.process(
            action=test_action,
            action_name="memory_test",
            execution_type=ExecutionType.SYSTEM_OPERATION,
        )
        
        # Verify memory was called
        mock_subsystems["memory"].add_memory.assert_called_once()
        call_args = mock_subsystems["memory"].add_memory.call_args
        
        # Verify memory content
        assert "Executed: memory_test" in call_args[1]["content"]
        assert call_args[1]["category"] == "execution"
    
    def test_pre_execution_hooks(self, kernel):
        """Test pre-execution hooks are called."""
        hook_called = []
        
        def pre_hook(context):
            hook_called.append(context.action_name)
        
        kernel.add_pre_hook(pre_hook)
        
        def test_action():
            return "test"
        
        kernel.process(
            action=test_action,
            action_name="hook_test",
            execution_type=ExecutionType.AGENT_ACTION,
        )
        
        # Verify hook was called
        assert "hook_test" in hook_called
    
    def test_post_execution_hooks(self, kernel):
        """Test post-execution hooks are called."""
        hook_called = []
        
        def post_hook(context):
            hook_called.append(context.action_name)
        
        kernel.add_post_hook(post_hook)
        
        def test_action():
            return "test"
        
        kernel.process(
            action=test_action,
            action_name="post_hook_test",
            execution_type=ExecutionType.AGENT_ACTION,
        )
        
        # Verify hook was called
        assert "post_hook_test" in hook_called
    
    def test_error_hooks(self, kernel):
        """Test error hooks are called on failures."""
        hook_called = []
        
        def error_hook(context, error):
            hook_called.append((context.action_name, str(error)))
        
        kernel.add_error_hook(error_hook)
        
        def failing_action():
            raise RuntimeError("Test failure")
        
        kernel.process(
            action=failing_action,
            action_name="error_hook_test",
            execution_type=ExecutionType.AGENT_ACTION,
        )
        
        # Verify hook was called with error
        assert len(hook_called) == 1
        assert hook_called[0][0] == "error_hook_test"
        assert "Test failure" in hook_called[0][1]
    
    def test_execution_history(self, kernel):
        """Test execution history tracking."""
        def test_action(value):
            return value * 2
        
        # Execute multiple actions
        for i in range(5):
            kernel.process(
                action=test_action,
                action_name=f"action_{i}",
                execution_type=ExecutionType.AGENT_ACTION,
                action_args=(i,),
            )
        
        # Get history
        history = kernel.get_execution_history(limit=10)
        
        assert len(history) == 5
        assert all("execution_id" in entry for entry in history)
        assert all("action_name" in entry for entry in history)
    
    def test_statistics(self, kernel):
        """Test kernel statistics."""
        def success_action():
            return "success"
        
        def fail_action():
            raise ValueError("fail")
        
        # Execute some actions
        kernel.process(
            action=success_action,
            action_name="success_1",
            execution_type=ExecutionType.AGENT_ACTION,
        )
        kernel.process(
            action=success_action,
            action_name="success_2",
            execution_type=ExecutionType.AGENT_ACTION,
        )
        kernel.process(
            action=fail_action,
            action_name="fail_1",
            execution_type=ExecutionType.AGENT_ACTION,
        )
        
        # Get statistics
        stats = kernel.get_statistics()
        
        assert stats["total_executions"] == 3
        assert stats["completed"] == 2
        assert stats["failed"] == 1
        assert stats["success_rate"] == pytest.approx(2/3)
        assert stats["subsystems"]["identity"] is True
        assert stats["subsystems"]["memory"] is True
    
    def test_low_risk_auto_approval(self, kernel):
        """Test that low-risk actions are auto-approved."""
        def test_action():
            return "auto_approved"
        
        result = kernel.process(
            action=test_action,
            action_name="low_risk_test",
            execution_type=ExecutionType.TOOL_INVOCATION,
            requires_approval=False,
            risk_level="low",
        )
        
        assert result.success is True
        assert result.governance_approved is True
        assert "auto-approved" in result.governance_reason.lower()
    
    def test_metadata_preservation(self, kernel):
        """Test that metadata is preserved through execution."""
        def test_action():
            return "test"
        
        metadata = {"custom_key": "custom_value", "tags": ["test", "metadata"]}
        
        result = kernel.process(
            action=test_action,
            action_name="metadata_test",
            execution_type=ExecutionType.AGENT_ACTION,
            metadata=metadata,
        )
        
        assert result.success is True
        assert result.metadata["custom_key"] == "custom_value"
        assert "test" in result.metadata["tags"]


class TestCognitionKernelWithoutSubsystems:
    """Test kernel behavior when subsystems are not available."""
    
    def test_kernel_without_subsystems(self):
        """Test kernel can operate without subsystems (degraded mode)."""
        kernel = CognitionKernel(
            identity_system=None,
            memory_engine=None,
            governance_system=None,
            reflection_engine=None,
            triumvirate=None,
        )
        
        def test_action():
            return "works"
        
        result = kernel.process(
            action=test_action,
            action_name="no_subsystems_test",
            execution_type=ExecutionType.AGENT_ACTION,
        )
        
        # Should still execute successfully
        assert result.success is True
        assert result.result == "works"
    
    def test_memory_recording_without_memory_engine(self):
        """Test that execution succeeds even if memory recording fails."""
        kernel = CognitionKernel(memory_engine=None)
        
        def test_action():
            return "success"
        
        result = kernel.process(
            action=test_action,
            action_name="no_memory_test",
            execution_type=ExecutionType.AGENT_ACTION,
        )
        
        assert result.success is True
        assert result.result == "success"


class TestExecutionTypes:
    """Test different execution types."""
    
    @pytest.fixture
    def kernel(self):
        return CognitionKernel()
    
    def test_agent_action_type(self, kernel):
        """Test AGENT_ACTION execution type."""
        result = kernel.process(
            action=lambda: "agent",
            action_name="agent_test",
            execution_type=ExecutionType.AGENT_ACTION,
        )
        assert result.success is True
    
    def test_tool_invocation_type(self, kernel):
        """Test TOOL_INVOCATION execution type."""
        result = kernel.process(
            action=lambda: "tool",
            action_name="tool_test",
            execution_type=ExecutionType.TOOL_INVOCATION,
        )
        assert result.success is True
    
    def test_system_operation_type(self, kernel):
        """Test SYSTEM_OPERATION execution type."""
        result = kernel.process(
            action=lambda: "system",
            action_name="system_test",
            execution_type=ExecutionType.SYSTEM_OPERATION,
        )
        assert result.success is True
    
    def test_plugin_execution_type(self, kernel):
        """Test PLUGIN_EXECUTION execution type."""
        result = kernel.process(
            action=lambda: "plugin",
            action_name="plugin_test",
            execution_type=ExecutionType.PLUGIN_EXECUTION,
        )
        assert result.success is True
    
    def test_council_decision_type(self, kernel):
        """Test COUNCIL_DECISION execution type."""
        result = kernel.process(
            action=lambda: "council",
            action_name="council_test",
            execution_type=ExecutionType.COUNCIL_DECISION,
        )
        assert result.success is True
    
    def test_learning_request_type(self, kernel):
        """Test LEARNING_REQUEST execution type."""
        result = kernel.process(
            action=lambda: "learning",
            action_name="learning_test",
            execution_type=ExecutionType.LEARNING_REQUEST,
        )
        assert result.success is True
    
    def test_reflection_type(self, kernel):
        """Test REFLECTION execution type."""
        result = kernel.process(
            action=lambda: "reflection",
            action_name="reflection_test",
            execution_type=ExecutionType.REFLECTION,
        )
        assert result.success is True
