"""
Tests for Build Cognition and State Integration.

Tests cognitive deliberation, build optimization, and integration
with Project-AI's deliberation engine and boundary system.
"""

from unittest.mock import patch

from gradle_evolution.cognition.build_cognition import BuildCognitionEngine
from gradle_evolution.cognition.state_integration import BuildStateIntegration


class TestBuildCognitionEngine:
    """Test BuildCognitionEngine component."""

    def test_initialization(self, mock_deliberation_engine):
        """Test engine initializes with deliberation engine."""
        engine = BuildCognitionEngine(mock_deliberation_engine)

        assert engine.deliberation == mock_deliberation_engine
        assert engine.build_patterns == {}
        assert engine.optimization_history == []

    def test_deliberate_build_plan_success(self, mock_deliberation_engine):
        """Test successful build plan deliberation."""
        engine = BuildCognitionEngine(mock_deliberation_engine)

        tasks = ["clean", "compile", "test"]
        context = {"cache_enabled": True}

        with patch(
            "gradle_evolution.cognition.build_cognition.check_boundary",
            return_value=True,
        ):
            optimized, reasoning = engine.deliberate_build_plan(tasks, context)

        assert len(optimized) == 3
        assert "reasoning" in reasoning or "optimized_order" in str(reasoning)
        mock_deliberation_engine.deliberate.assert_called_once()

    def test_deliberate_with_boundary_exceeded(self, mock_deliberation_engine):
        """Test deliberation when cognitive boundary exceeded."""
        engine = BuildCognitionEngine(mock_deliberation_engine)

        tasks = ["task"] * 1000  # Many tasks
        context = {}

        with patch(
            "gradle_evolution.cognition.build_cognition.check_boundary",
            return_value=False,
        ):
            optimized, reasoning = engine.deliberate_build_plan(tasks, context)

        # Should return original order with warning
        assert optimized == tasks
        assert "warning" in reasoning or "Boundary" in reasoning.get("warning", "")

    def test_pattern_analysis(self, mock_deliberation_engine, sample_build_context):
        """Test build pattern analysis."""
        engine = BuildCognitionEngine(mock_deliberation_engine)

        # Simulate multiple builds to establish patterns
        for _i in range(3):
            tasks = sample_build_context["tasks"]
            with patch(
                "gradle_evolution.cognition.build_cognition.check_boundary",
                return_value=True,
            ):
                engine.deliberate_build_plan(tasks, sample_build_context)

        # Should have pattern data
        assert len(engine.optimization_history) == 3

    def test_learn_from_build(self, mock_deliberation_engine):
        """Test learning from build execution."""
        engine = BuildCognitionEngine(mock_deliberation_engine)

        build_id = "test-build-001"
        tasks = ["clean", "compile"]
        performance = {"duration_seconds": 45.2, "success": True}

        engine.learn_from_build(build_id, tasks, performance)

        # Should update patterns
        assert build_id in engine.build_patterns or len(engine.optimization_history) > 0

    def test_get_optimization_stats(
        self, mock_deliberation_engine, sample_build_context
    ):
        """Test retrieving optimization statistics."""
        engine = BuildCognitionEngine(mock_deliberation_engine)

        # Perform some optimizations
        with patch(
            "gradle_evolution.cognition.build_cognition.check_boundary",
            return_value=True,
        ):
            engine.deliberate_build_plan(["a", "b", "c"], sample_build_context)
            engine.deliberate_build_plan(["x", "y", "z"], sample_build_context)

        stats = engine.get_optimization_stats()

        assert "total_optimizations" in stats
        assert stats["total_optimizations"] == 2

    def test_invariant_validation(self, mock_deliberation_engine):
        """Test that invariant checker is invoked."""
        engine = BuildCognitionEngine(mock_deliberation_engine)

        tasks = ["compile", "test"]
        context = {"dependencies": {"compile": ["test"]}}

        with (
            patch(
                "gradle_evolution.cognition.build_cognition.check_boundary",
                return_value=True,
            ),
            patch.object(
                engine, "_validate_task_order", return_value=False
            ) as mock_validate,
        ):
            optimized, reasoning = engine.deliberate_build_plan(tasks, context)

            # Should call validation
            mock_validate.assert_called_once()
            # Should revert to original due to invariant violation
            assert optimized == tasks

    def test_error_handling(self, mock_deliberation_engine):
        """Test error handling in deliberation."""
        engine = BuildCognitionEngine(mock_deliberation_engine)

        # Make deliberation raise error
        mock_deliberation_engine.deliberate.side_effect = Exception(
            "Deliberation error"
        )

        tasks = ["clean", "compile"]
        context = {}

        with patch(
            "gradle_evolution.cognition.build_cognition.check_boundary",
            return_value=True,
        ):
            optimized, reasoning = engine.deliberate_build_plan(tasks, context)

        # Should gracefully fallback to original order
        assert optimized == tasks
        assert "error" in reasoning or "Error" in reasoning.get("error", "")


class TestBuildStateIntegration:
    """Test BuildStateIntegration component."""

    def test_initialization(self, temp_dir):
        """Test state integration initializes."""
        storage = temp_dir / "build_state.json"
        integration = BuildStateIntegration(storage_path=storage)

        assert integration.storage_path == storage
        assert integration.build_states == {}

    def test_record_build_state(self, temp_dir):
        """Test recording build state."""
        storage = temp_dir / "build_state.json"
        integration = BuildStateIntegration(storage_path=storage)

        build_id = "build-001"
        state = {
            "tasks": ["clean", "compile"],
            "status": "in_progress",
            "start_time": "2024-01-01T00:00:00Z",
        }

        integration.record_build_state(build_id, state)

        assert build_id in integration.build_states
        assert integration.build_states[build_id]["status"] == "in_progress"

    def test_update_build_state(self, temp_dir):
        """Test updating existing build state."""
        storage = temp_dir / "build_state.json"
        integration = BuildStateIntegration(storage_path=storage)

        build_id = "build-001"
        initial = {"status": "in_progress"}
        integration.record_build_state(build_id, initial)

        # Update state
        updates = {"status": "completed", "duration": 45.2}
        integration.update_build_state(build_id, updates)

        assert integration.build_states[build_id]["status"] == "completed"
        assert integration.build_states[build_id]["duration"] == 45.2

    def test_get_build_state(self, temp_dir):
        """Test retrieving build state."""
        storage = temp_dir / "build_state.json"
        integration = BuildStateIntegration(storage_path=storage)

        build_id = "build-001"
        state = {"status": "completed"}
        integration.record_build_state(build_id, state)

        retrieved = integration.get_build_state(build_id)

        assert retrieved is not None
        assert retrieved["status"] == "completed"

    def test_get_nonexistent_state(self, temp_dir):
        """Test retrieving nonexistent build state returns None."""
        storage = temp_dir / "build_state.json"
        integration = BuildStateIntegration(storage_path=storage)

        retrieved = integration.get_build_state("nonexistent")

        assert retrieved is None

    def test_persistence(self, temp_dir):
        """Test state persistence to disk."""
        storage = temp_dir / "build_state.json"
        integration = BuildStateIntegration(storage_path=storage)

        build_id = "build-001"
        state = {"status": "completed", "tasks": ["test"]}
        integration.record_build_state(build_id, state)
        integration.save()

        # Load in new instance
        new_integration = BuildStateIntegration(storage_path=storage)
        new_integration.load()

        assert build_id in new_integration.build_states
        assert new_integration.build_states[build_id]["status"] == "completed"

    def test_query_builds_by_status(self, temp_dir):
        """Test querying builds by status."""
        storage = temp_dir / "build_state.json"
        integration = BuildStateIntegration(storage_path=storage)

        # Create multiple builds with different statuses
        integration.record_build_state("build-1", {"status": "completed"})
        integration.record_build_state("build-2", {"status": "failed"})
        integration.record_build_state("build-3", {"status": "completed"})

        completed = integration.query_builds_by_status("completed")

        assert len(completed) == 2
        assert all(b["status"] == "completed" for b in completed)

    def test_cleanup_old_states(self, temp_dir):
        """Test cleaning up old build states."""
        storage = temp_dir / "build_state.json"
        integration = BuildStateIntegration(storage_path=storage)

        # Create multiple builds
        for i in range(10):
            integration.record_build_state(f"build-{i}", {"status": "completed"})

        # Cleanup keeping only 5 most recent
        integration.cleanup_old_states(keep_count=5)

        assert len(integration.build_states) == 5

    def test_get_build_metrics(self, temp_dir):
        """Test retrieving build metrics."""
        storage = temp_dir / "build_state.json"
        integration = BuildStateIntegration(storage_path=storage)

        # Create builds with metrics
        integration.record_build_state(
            "build-1",
            {
                "status": "completed",
                "duration": 30.5,
            },
        )
        integration.record_build_state(
            "build-2",
            {
                "status": "failed",
                "duration": 20.0,
            },
        )

        metrics = integration.get_build_metrics()

        assert metrics["total_builds"] == 2
        assert metrics["completed_builds"] == 1
        assert metrics["failed_builds"] == 1
        assert "average_duration" in metrics
