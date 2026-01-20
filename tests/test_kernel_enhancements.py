"""
Tests for kernel enhancement tools: fuzz harness, replay, and drift monitor.
"""

import tempfile
from datetime import UTC, datetime, timedelta

import pytest

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.deterministic_replay import DeterministicReplayTool
from app.core.governance_drift_monitor import GovernanceDriftMonitor
from app.core.kernel_fuzz_harness import KernelFuzzHarness


class TestKernelFuzzHarness:
    """Test the kernel fuzz harness."""

    @pytest.fixture
    def kernel(self):
        """Create a mock kernel for testing."""
        return CognitionKernel()

    def test_fuzz_harness_initialization(self, kernel):
        """Test fuzz harness can be initialized."""
        harness = KernelFuzzHarness(kernel)
        assert harness.kernel == kernel
        assert harness.results == []

    def test_fuzz_malformed_actions(self, kernel):
        """Test fuzzing with malformed actions."""
        harness = KernelFuzzHarness(kernel)
        harness.fuzz_malformed_actions(iterations=5)

        assert len(harness.results) == 5
        # Should handle gracefully - no crashes
        assert all(not r.crash for r in harness.results)

    def test_fuzz_boundary_conditions(self, kernel):
        """Test fuzzing with boundary conditions."""
        harness = KernelFuzzHarness(kernel)
        harness.fuzz_boundary_conditions(iterations=5)

        assert len(harness.results) == 5
        # Should handle gracefully
        assert all(not r.crash for r in harness.results)

    def test_run_all_tests(self, kernel):
        """Test running all fuzz tests."""
        harness = KernelFuzzHarness(kernel)
        results = harness.run_all_tests(iterations=10)

        # Should have run 5 test types x 10 iterations = 50 tests
        assert results["total_tests"] == 50
        assert results["crashes"] == 0  # No crashes allowed
        assert results["verdict"] == "PASS"


class TestDeterministicReplayTool:
    """Test the deterministic replay tool."""

    @pytest.fixture
    def replay_tool(self):
        """Create replay tool with temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield DeterministicReplayTool(data_dir=tmpdir)

    def test_replay_tool_initialization(self, replay_tool):
        """Test replay tool can be initialized."""
        assert replay_tool.replay_dir.exists()

    def test_save_and_load_execution(self, replay_tool):
        """Test saving and loading an execution."""
        # Create mock execution context
        from app.core.cognition_kernel import (
            Action,
            Decision,
            ExecutionContext,
            ExecutionStatus,
        )

        action = Action(
            action_id="test_action_1",
            action_name="test_action",
            action_type=ExecutionType.AGENT_ACTION,
            callable=lambda: "test",
            args=(),
            kwargs={},
            source="test",
        )

        decision = Decision(
            decision_id="test_decision_1",
            action_id="test_action_1",
            approved=True,
            reason="Test approved",
        )

        context = ExecutionContext(
            trace_id="test_trace_123",
            timestamp=datetime.now(UTC),
            perception={"test": "data"},
            interpretation={"test": "interpretation"},
            proposed_action=action,
            governance_decision=decision,
            status=ExecutionStatus.COMPLETED,
            source="test",
        )

        # Save
        filepath = replay_tool.save_execution(context)
        assert filepath

        # Load
        loaded = replay_tool.load_execution("test_trace_123")
        assert loaded["trace_id"] == "test_trace_123"
        assert loaded["status"] == "completed"

    def test_replay_execution(self, replay_tool):
        """Test replaying an execution."""
        # Save a test execution first
        from app.core.cognition_kernel import (
            Action,
            Decision,
            ExecutionContext,
            ExecutionStatus,
        )

        action = Action(
            action_id="test_action_2",
            action_name="test_replay",
            action_type=ExecutionType.AGENT_ACTION,
            callable=lambda: "test",
            args=(),
            kwargs={},
            source="test",
        )

        decision = Decision(
            decision_id="test_decision_2",
            action_id="test_action_2",
            approved=True,
            reason="Test approved",
        )

        context = ExecutionContext(
            trace_id="test_trace_456",
            timestamp=datetime.now(UTC),
            perception={"test": "data"},
            interpretation={"test": "interpretation"},
            proposed_action=action,
            governance_decision=decision,
            status=ExecutionStatus.COMPLETED,
            source="test",
        )
        context.channels["attempt"] = {"action_name": "test_replay"}
        context.channels["decision"] = {
            "decision_id": "test_decision_2",
            "approved": True,
            "reason": "Test approved"
        }
        context.channels["result"] = "test_result"

        replay_tool.save_execution(context)

        # Replay
        replay = replay_tool.replay_execution("test_trace_456")

        assert replay["trace_id"] == "test_trace_456"
        assert len(replay["timeline"]) >= 1
        assert replay["analysis"]["status"] == "completed"


class TestGovernanceDriftMonitor:
    """Test the governance drift monitor."""

    @pytest.fixture
    def drift_monitor(self):
        """Create drift monitor with temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield GovernanceDriftMonitor(data_dir=tmpdir, alert_threshold=0.1)

    def test_drift_monitor_initialization(self, drift_monitor):
        """Test drift monitor can be initialized."""
        assert drift_monitor.alerts_dir.exists()
        assert drift_monitor.window_days == 30
        assert drift_monitor.alert_threshold == 0.1

    def test_analyze_drift_no_data(self, drift_monitor):
        """Test drift analysis with no data."""
        result = drift_monitor.analyze_drift()

        assert result["status"] == "no_data"

    def test_detect_approval_rate_drift(self, drift_monitor):
        """Test detecting approval rate drift."""
        # Create historical executions (low approval)
        historical = [
            {
                "timestamp": (
                    datetime.now(UTC) - timedelta(days=60)
                ).isoformat(),
                "governance_decision": {"approved": False},
                "proposed_action": {"risk_level": "medium", "mutation_targets": []},
            }
            for _ in range(10)
        ]

        # Create recent executions (high approval)
        recent = [
            {
                "timestamp": (
                    datetime.now(UTC) - timedelta(days=5)
                ).isoformat(),
                "governance_decision": {"approved": True},
                "proposed_action": {"risk_level": "medium", "mutation_targets": []},
            }
            for _ in range(10)
        ]

        # Test drift detection
        alert = drift_monitor._detect_approval_rate_drift(historical, recent)

        assert alert is not None
        assert alert.severity in ["high", "critical"]
        assert "increased" in alert.message.lower()
