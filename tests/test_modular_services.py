"""
Tests for modular services extracted from CognitionKernel.

This test suite validates the GovernanceService, ExecutionService, and
MemoryLoggingService that were extracted to improve maintainability.
"""

from unittest.mock import Mock

import pytest

from app.core.services import (
    ExecutionService,
    GovernanceService,
    MemoryLoggingService,
)
from app.core.services.execution_service import ExecutionStatus
from app.core.services.governance_service import Decision


class TestGovernanceService:
    """Test suite for GovernanceService."""

    @pytest.fixture
    def mock_triumvirate(self):
        """Create mock Triumvirate."""
        triumvirate = Mock()
        triumvirate.process = Mock(
            return_value={
                "success": True,
                "output": "Triumvirate consensus: Approved",
                "votes": {
                    "galahad": "approve",
                    "cerberus": "approve",
                    "codex_deus_maximus": "approve",
                },
            }
        )
        return triumvirate

    @pytest.fixture
    def mock_governance_system(self):
        """Create mock legacy governance system."""
        governance = Mock()
        governance.validate_action = Mock(
            return_value={
                "allowed": True,
                "reason": "Action approved by governance system",
            }
        )
        return governance

    @pytest.fixture
    def mock_identity_system(self):
        """Create mock identity system."""
        identity = Mock()
        identity.snapshot = Mock(
            return_value={"personality": "test", "identity_version": "1.0"}
        )
        return identity

    @pytest.fixture
    def governance_service(self, mock_triumvirate, mock_identity_system):
        """Create GovernanceService with Triumvirate."""
        return GovernanceService(
            triumvirate=mock_triumvirate,
            identity_system=mock_identity_system,
        )

    def test_service_initialization(self, governance_service):
        """Test that governance service initializes correctly."""
        assert governance_service.triumvirate is not None
        assert governance_service.identity_system is not None
        assert governance_service.approval_count == 0
        assert governance_service.block_count == 0
        assert len(governance_service.decision_log) == 0

    def test_approve_with_triumvirate(self, governance_service, mock_triumvirate):
        """Test action approval through Triumvirate."""
        # Create mock action and context
        action = Mock()
        action.action_id = "act_123"
        action.action_name = "test_action"
        action.action_type = Mock(value="agent_action")
        action.risk_level = "low"
        action.metadata = {}

        context = Mock()
        context.trace_id = "trace_123"

        # Evaluate action
        decision = governance_service.evaluate_action(action, context)

        # Verify decision
        assert isinstance(decision, Decision)
        assert decision.approved is True
        assert "Triumvirate" in decision.reason
        assert decision.council_votes is not None

        # Verify Triumvirate was called
        mock_triumvirate.process.assert_called_once()

        # Verify statistics
        assert governance_service.approval_count == 1
        assert governance_service.block_count == 0

    def test_block_with_triumvirate(self, governance_service, mock_triumvirate):
        """Test action blocking through Triumvirate."""
        # Configure Triumvirate to block
        mock_triumvirate.process.return_value = {
            "success": False,
            "output": "Triumvirate consensus: Blocked by Cerberus (safety concern)",
            "votes": {
                "galahad": "approve",
                "cerberus": "block",
                "codex_deus_maximus": "approve",
            },
        }

        action = Mock()
        action.action_id = "act_456"
        action.action_name = "dangerous_action"
        action.action_type = Mock(value="system_operation")
        action.risk_level = "high"
        action.metadata = {}

        context = Mock()
        context.trace_id = "trace_456"

        # Evaluate action
        decision = governance_service.evaluate_action(action, context)

        # Verify decision
        assert decision.approved is False
        assert "Blocked" in decision.reason or "Cerberus" in decision.reason

        # Verify statistics
        assert governance_service.block_count == 1

    def test_use_governance_system_fallback(
        self, mock_governance_system, mock_identity_system
    ):
        """Test fallback to legacy governance system."""
        service = GovernanceService(
            governance_system=mock_governance_system,
            identity_system=mock_identity_system,
        )

        action = Mock()
        action.action_id = "act_789"
        action.action_name = "legacy_action"
        action.action_type = Mock(value="tool_invocation")
        action.risk_level = "medium"
        action.metadata = {}

        context = Mock()
        context.trace_id = "trace_789"

        # Evaluate action
        decision = service.evaluate_action(action, context)

        # Verify governance system was used
        mock_governance_system.validate_action.assert_called_once()
        assert decision.approved is True

    def test_auto_approve_low_risk(self):
        """Test auto-approval for low-risk actions when no governance."""
        service = GovernanceService()  # No governance configured

        action = Mock()
        action.action_id = "act_auto"
        action.action_name = "low_risk_action"
        action.action_type = Mock(value="agent_action")
        action.risk_level = "low"
        action.metadata = {}

        context = Mock()
        context.trace_id = "trace_auto"

        # Evaluate action
        decision = service.evaluate_action(action, context)

        # Verify auto-approval
        assert decision.approved is True
        assert "Auto-approved" in decision.reason

    def test_block_high_risk_without_governance(self):
        """Test blocking high-risk actions when no governance."""
        service = GovernanceService()  # No governance configured

        action = Mock()
        action.action_id = "act_risk"
        action.action_name = "high_risk_action"
        action.action_type = Mock(value="system_operation")
        action.risk_level = "high"
        action.metadata = {}

        context = Mock()
        context.trace_id = "trace_risk"

        # Evaluate action
        decision = service.evaluate_action(action, context)

        # Verify blocking
        assert decision.approved is False
        assert "High-risk" in decision.reason

    def test_get_statistics(self, governance_service):
        """Test governance statistics retrieval."""
        # Perform some evaluations
        for i in range(3):
            action = Mock()
            action.action_id = f"act_{i}"
            action.action_name = f"action_{i}"
            action.action_type = Mock(value="agent_action")
            action.risk_level = "low"
            action.metadata = {}

            context = Mock()
            context.trace_id = f"trace_{i}"

            governance_service.evaluate_action(action, context)

        stats = governance_service.get_statistics()

        assert stats["total_decisions"] == 3
        assert stats["approvals"] == 3
        assert stats["blocks"] == 0
        assert stats["approval_rate"] == 1.0
        assert stats["triumvirate_active"] is True

    def test_get_recent_decisions(self, governance_service):
        """Test recent decisions retrieval."""
        # Perform some evaluations
        for i in range(5):
            action = Mock()
            action.action_id = f"act_{i}"
            action.action_name = f"action_{i}"
            action.action_type = Mock(value="agent_action")
            action.risk_level = "low"
            action.metadata = {}

            context = Mock()
            context.trace_id = f"trace_{i}"

            governance_service.evaluate_action(action, context)

        recent = governance_service.get_recent_decisions(limit=3)

        assert len(recent) == 3
        assert all(isinstance(d, Decision) for d in recent)


class TestExecutionService:
    """Test suite for ExecutionService."""

    @pytest.fixture
    def execution_service(self):
        """Create ExecutionService."""
        return ExecutionService()

    def test_service_initialization(self, execution_service):
        """Test that execution service initializes correctly."""
        assert execution_service.execution_count == 0
        assert execution_service.success_count == 0
        assert execution_service.failure_count == 0

    def test_successful_execution(self, execution_service):
        """Test successful action execution."""
        # Create mock action
        def test_callable(x, y):
            return x + y

        action = Mock()
        action.action_name = "test_addition"
        action.callable = test_callable
        action.args = (2, 3)
        action.kwargs = {}

        context = Mock()
        context.trace_id = "trace_exec_123"
        context.timestamp = Mock()
        context.timestamp.isoformat = Mock(return_value="2026-01-01T00:00:00Z")

        # Execute action
        result, status, error = execution_service.execute_action(action, context)

        # Verify result
        assert result == 5
        assert status == ExecutionStatus.COMPLETED
        assert error is None
        assert execution_service.success_count == 1

    def test_failed_execution(self, execution_service):
        """Test failed action execution."""

        def failing_callable():
            raise ValueError("Test error")

        action = Mock()
        action.action_name = "failing_action"
        action.callable = failing_callable
        action.args = ()
        action.kwargs = {}

        context = Mock()
        context.trace_id = "trace_fail_456"
        context.timestamp = Mock()
        context.timestamp.isoformat = Mock(return_value="2026-01-01T00:00:00Z")

        # Execute action
        result, status, error = execution_service.execute_action(action, context)

        # Verify failure
        assert result is None
        assert status == ExecutionStatus.FAILED
        assert error is not None
        assert "Test error" in error
        assert execution_service.failure_count == 1

    def test_execution_with_kwargs(self, execution_service):
        """Test execution with keyword arguments."""

        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}"

        action = Mock()
        action.action_name = "greet_action"
        action.callable = greet
        action.args = ()
        action.kwargs = {"name": "Alice", "greeting": "Hi"}

        context = Mock()
        context.trace_id = "trace_kwargs_789"
        context.timestamp = Mock()
        context.timestamp.isoformat = Mock(return_value="2026-01-01T00:00:00Z")

        # Execute action
        result, status, error = execution_service.execute_action(action, context)

        # Verify result
        assert result == "Hi, Alice"
        assert status == ExecutionStatus.COMPLETED

    def test_get_statistics(self, execution_service):
        """Test execution statistics retrieval."""
        # Perform some executions
        for i in range(5):
            action = Mock()
            action.action_name = f"action_{i}"
            action.callable = lambda: "success"
            action.args = ()
            action.kwargs = {}

            context = Mock()
            context.trace_id = f"trace_{i}"
            context.timestamp = Mock()
            context.timestamp.isoformat = Mock(return_value="2026-01-01T00:00:00Z")

            execution_service.execute_action(action, context)

        stats = execution_service.get_statistics()

        assert stats["total_executions"] == 5
        assert stats["successful"] == 5
        assert stats["failed"] == 0
        assert stats["success_rate"] == 1.0

    def test_execution_timing(self, execution_service):
        """Test that execution timing is tracked."""
        import time

        def slow_action():
            time.sleep(0.01)  # 10ms delay
            return "done"

        action = Mock()
        action.action_name = "slow_action"
        action.callable = slow_action
        action.args = ()
        action.kwargs = {}

        context = Mock()
        context.trace_id = "trace_timing"
        context.timestamp = Mock()
        context.timestamp.isoformat = Mock(return_value="2026-01-01T00:00:00Z")

        # Execute action
        result, status, error = execution_service.execute_action(action, context)

        # Verify timing was tracked
        assert context.duration_ms > 0
        assert result == "done"


class TestMemoryLoggingService:
    """Test suite for MemoryLoggingService."""

    @pytest.fixture
    def mock_memory_engine(self):
        """Create mock memory engine."""
        memory = Mock()
        memory.record_execution = Mock()
        return memory

    @pytest.fixture
    def memory_service(self, mock_memory_engine):
        """Create MemoryLoggingService."""
        return MemoryLoggingService(memory_engine=mock_memory_engine)

    def test_service_initialization(self, memory_service):
        """Test that memory logging service initializes correctly."""
        assert memory_service.memory_engine is not None
        assert len(memory_service.execution_history) == 0
        assert memory_service.total_recordings == 0

    def test_record_successful_execution(self, memory_service, mock_memory_engine):
        """Test recording a successful execution."""
        # Create mock context
        context = Mock()
        context.trace_id = "trace_mem_123"
        context.timestamp = Mock()
        context.timestamp.isoformat = Mock(return_value="2026-01-01T00:00:00Z")
        context.proposed_action = Mock()
        context.proposed_action.action_name = "test_action"
        context.proposed_action.action_type = Mock(value="agent_action")
        context.source = "test"
        context.user_id = "user123"
        context.status = Mock(value="completed")
        context.governance_decision = Mock()
        context.governance_decision.decision_id = "dec_123"
        context.governance_decision.approved = True
        context.governance_decision.reason = "Approved"
        context.governance_decision.council_votes = {}
        context.result = "success"
        context.error = None
        context.duration_ms = 10.5
        context.channels = {}

        # Record execution
        success, error = memory_service.record_execution(context)

        # Verify recording
        assert success is True
        assert error is None
        assert len(memory_service.execution_history) == 1
        assert memory_service.total_recordings == 1

        # Verify memory engine was called
        mock_memory_engine.record_execution.assert_called_once()

    def test_record_failed_execution(self, memory_service):
        """Test recording a failed execution."""
        context = Mock()
        context.trace_id = "trace_fail_456"
        context.timestamp = Mock()
        context.timestamp.isoformat = Mock(return_value="2026-01-01T00:00:00Z")
        context.proposed_action = Mock()
        context.proposed_action.action_name = "failing_action"
        context.proposed_action.action_type = Mock(value="agent_action")
        context.source = "test"
        context.user_id = "user123"
        context.status = Mock(value="failed")
        context.governance_decision = None
        context.result = None
        context.error = "Test error"
        context.duration_ms = 5.0
        context.channels = {}

        # Record execution
        success, error = memory_service.record_execution(context)

        # Verify recording
        assert success is True
        assert len(memory_service.execution_history) == 1

        # Verify error channel was populated
        assert context.channels["error"] is not None

    def test_get_execution_history(self, memory_service):
        """Test execution history retrieval."""
        # Record multiple executions
        for i in range(5):
            context = Mock()
            context.trace_id = f"trace_{i}"
            context.timestamp = Mock()
            context.timestamp.isoformat = Mock(return_value=f"2026-01-01T00:00:0{i}Z")
            context.proposed_action = Mock()
            context.proposed_action.action_name = f"action_{i}"
            context.proposed_action.action_type = Mock(value="agent_action")
            context.source = "test"
            context.user_id = "user123"
            context.status = Mock(value="completed")
            context.governance_decision = None
            context.result = "success"
            context.error = None
            context.duration_ms = 10.0
            context.channels = {}

            memory_service.record_execution(context)

        # Get history
        history = memory_service.get_execution_history(limit=3)

        assert len(history) == 3
        assert all("trace_id" in entry for entry in history)
        assert all("action_name" in entry for entry in history)

    def test_get_statistics(self, memory_service):
        """Test memory logging statistics retrieval."""
        # Record some executions
        for i in range(3):
            context = Mock()
            context.trace_id = f"trace_{i}"
            context.timestamp = Mock()
            context.timestamp.isoformat = Mock(return_value="2026-01-01T00:00:00Z")
            context.proposed_action = Mock()
            context.proposed_action.action_name = f"action_{i}"
            context.proposed_action.action_type = Mock(value="agent_action")
            context.source = "test"
            context.user_id = "user123"
            context.status = Mock(value="completed")
            context.governance_decision = None
            context.result = "success"
            context.error = None
            context.duration_ms = 10.0
            context.channels = {}

            memory_service.record_execution(context)

        stats = memory_service.get_statistics()

        assert stats["total_recordings"] == 3
        assert stats["successful_recordings"] == 3
        assert stats["failed_recordings"] == 0
        assert stats["history_size"] == 3
        assert stats["memory_engine_active"] is True

    def test_channel_population(self, memory_service):
        """Test that all five channels are populated."""
        context = Mock()
        context.trace_id = "trace_channels"
        context.timestamp = Mock()
        context.timestamp.isoformat = Mock(return_value="2026-01-01T00:00:00Z")
        context.proposed_action = Mock()
        context.proposed_action.action_name = "channel_test"
        context.proposed_action.action_type = Mock(value="agent_action")
        context.source = "test"
        context.user_id = "user123"
        context.status = Mock(value="completed")
        context.governance_decision = Mock()
        context.governance_decision.decision_id = "dec_channel"
        context.governance_decision.approved = True
        context.governance_decision.reason = "Test"
        context.governance_decision.council_votes = {}
        context.result = "test_result"
        context.error = None
        context.duration_ms = 10.0
        context.channels = {}

        # Record execution
        memory_service.record_execution(context)

        # Verify channels
        assert context.channels["attempt"] is not None
        assert context.channels["decision"] is not None
        assert context.channels["result"] == "test_result"
