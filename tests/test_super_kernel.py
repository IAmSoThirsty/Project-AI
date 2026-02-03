"""
Tests for SuperKernel system.

This test suite validates:
- KernelType enum
- KernelInterface base class
- Kernel adapters (ReflectionCycleAdapter, MemoryEngineAdapter, PerspectiveEngineAdapter)
- SuperKernel orchestration
- Bootstrap functions
"""

from unittest.mock import Mock

import pytest

from app.core.kernel_adapters import (
    MemoryEngineAdapter,
    PerspectiveEngineAdapter,
    ReflectionCycleAdapter,
)
from app.core.kernel_types import KernelInterface, KernelType
from app.core.super_kernel import SuperKernel
from app.core.super_kernel_bootstrap import (
    bootstrap_super_kernel,
    create_minimal_super_kernel,
)


class TestKernelType:
    """Test KernelType enum."""

    def test_kernel_types_defined(self):
        """Test that all expected kernel types are defined."""
        assert KernelType.COGNITION
        assert KernelType.REFLECTION
        assert KernelType.MEMORY
        assert KernelType.PERSPECTIVE
        assert KernelType.IDENTITY

    def test_kernel_types_unique(self):
        """Test that kernel types have unique values."""
        types = list(KernelType)
        values = [t.value for t in types]
        assert len(values) == len(set(values))


class TestKernelInterface:
    """Test KernelInterface base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that KernelInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            KernelInterface()

    def test_concrete_implementation(self):
        """Test that concrete implementations work."""

        class TestKernel(KernelInterface):
            def process(self, input_data, **kwargs):
                return {"result": "test"}

        kernel = TestKernel()
        result = kernel.process("test")
        assert result == {"result": "test"}

    def test_default_route_delegates_to_process(self):
        """Test that default route() delegates to process()."""

        class TestKernel(KernelInterface):
            def process(self, input_data, **kwargs):
                return {"input": input_data, "kwargs": kwargs}

        kernel = TestKernel()
        result = kernel.route("task", source="agent")
        assert result["input"] == "task"
        assert result["kwargs"]["source"] == "agent"


class TestReflectionCycleAdapter:
    """Test ReflectionCycleAdapter."""

    @pytest.fixture
    def mock_reflection_cycle(self):
        """Create mock ReflectionCycle."""
        reflection = Mock()
        reflection.perform_daily_reflection = Mock(
            return_value={"type": "daily", "insights": []}
        )
        reflection.perform_weekly_reflection = Mock(
            return_value={"type": "weekly", "insights": []}
        )
        reflection.perform_triggered_reflection = Mock(
            return_value={"type": "triggered", "insights": []}
        )
        reflection.get_statistics = Mock(return_value={"total_reflections": 5})
        return reflection

    @pytest.fixture
    def adapter(self, mock_reflection_cycle):
        """Create ReflectionCycleAdapter."""
        return ReflectionCycleAdapter(mock_reflection_cycle)

    def test_adapter_initialization(self, adapter, mock_reflection_cycle):
        """Test adapter initializes correctly."""
        assert adapter.reflection_cycle == mock_reflection_cycle

    def test_daily_reflection(self, adapter, mock_reflection_cycle):
        """Test daily reflection routing."""
        memory = Mock()
        perspective = Mock()

        result = adapter.process(
            "daily", memory_engine=memory, perspective_engine=perspective
        )

        assert result["type"] == "daily"
        mock_reflection_cycle.perform_daily_reflection.assert_called_once()

    def test_weekly_reflection(self, adapter, mock_reflection_cycle):
        """Test weekly reflection routing."""
        memory = Mock()

        result = adapter.process("weekly", memory_engine=memory)

        assert result["type"] == "weekly"
        mock_reflection_cycle.perform_weekly_reflection.assert_called_once()

    def test_triggered_reflection(self, adapter, mock_reflection_cycle):
        """Test triggered reflection routing."""
        memory = Mock()

        result = adapter.process(
            "triggered", memory_engine=memory, trigger_reason="Test trigger"
        )

        assert result["type"] == "triggered"
        mock_reflection_cycle.perform_triggered_reflection.assert_called_once()

    def test_missing_memory_engine(self, adapter):
        """Test error when memory_engine is missing."""
        with pytest.raises(ValueError, match="memory_engine is required"):
            adapter.process("daily")

    def test_invalid_reflection_type(self, adapter):
        """Test error for invalid reflection type."""
        memory = Mock()

        with pytest.raises(ValueError, match="Unknown reflection type"):
            adapter.process("invalid", memory_engine=memory)

    def test_get_statistics(self, adapter, mock_reflection_cycle):
        """Test statistics retrieval."""
        stats = adapter.get_statistics()
        assert stats["total_reflections"] == 5


class TestMemoryEngineAdapter:
    """Test MemoryEngineAdapter."""

    @pytest.fixture
    def mock_memory_engine(self):
        """Create mock MemoryEngine."""
        memory = Mock()
        memory.episodic_memories = {"mem1": {}, "mem2": {}}
        memory.semantic_concepts = {"concept1": {}}
        memory.procedural_skills = {"skill1": {}, "skill2": {}, "skill3": {}}
        memory.search_episodic_memories = Mock(return_value=[{"id": "mem1"}])
        memory.retrieve_episodic_memory = Mock(return_value={"id": "mem1"})
        memory.get_recent_memories = Mock(return_value=[{"id": "mem1"}, {"id": "mem2"}])
        return memory

    @pytest.fixture
    def adapter(self, mock_memory_engine):
        """Create MemoryEngineAdapter."""
        return MemoryEngineAdapter(mock_memory_engine)

    def test_adapter_initialization(self, adapter, mock_memory_engine):
        """Test adapter initializes correctly."""
        assert adapter.memory_engine == mock_memory_engine

    def test_statistics_operation(self, adapter):
        """Test statistics operation (None input)."""
        result = adapter.process(None)

        assert result["episodic_count"] == 2
        assert result["semantic_count"] == 1
        assert result["procedural_count"] == 3

    def test_search_operation(self, adapter, mock_memory_engine):
        """Test search operation."""
        result = adapter.process("search", query="test", limit=5)

        assert len(result) == 1
        mock_memory_engine.search_episodic_memories.assert_called_once()

    def test_retrieve_operation(self, adapter, mock_memory_engine):
        """Test retrieve operation."""
        result = adapter.process("retrieve", memory_id="mem1")

        assert result["id"] == "mem1"
        mock_memory_engine.retrieve_episodic_memory.assert_called_once_with("mem1")

    def test_recent_operation(self, adapter, mock_memory_engine):
        """Test recent memories operation."""
        result = adapter.process("recent", limit=10)

        assert len(result) == 2
        mock_memory_engine.get_recent_memories.assert_called_once()

    def test_retrieve_without_memory_id(self, adapter):
        """Test error when memory_id is missing."""
        with pytest.raises(ValueError, match="memory_id required"):
            adapter.process("retrieve")


class TestPerspectiveEngineAdapter:
    """Test PerspectiveEngineAdapter."""

    @pytest.fixture
    def mock_perspective_engine(self):
        """Create mock PerspectiveEngine."""
        perspective = Mock()
        perspective.update_from_interaction = Mock(return_value={"updated": True})
        perspective.get_perspective_summary = Mock(
            return_value={"traits": {"openness": 0.7}}
        )
        perspective.activate_work_profile = Mock(return_value=True)
        perspective.deactivate_work_profile = Mock()
        return perspective

    @pytest.fixture
    def adapter(self, mock_perspective_engine):
        """Create PerspectiveEngineAdapter."""
        return PerspectiveEngineAdapter(mock_perspective_engine)

    def test_adapter_initialization(self, adapter, mock_perspective_engine):
        """Test adapter initializes correctly."""
        assert adapter.perspective_engine == mock_perspective_engine

    def test_summary_operation(self, adapter, mock_perspective_engine):
        """Test summary operation."""
        result = adapter.process("summary")

        assert "traits" in result
        mock_perspective_engine.get_perspective_summary.assert_called_once()

    def test_update_operation(self, adapter, mock_perspective_engine):
        """Test update operation."""
        result = adapter.process(
            "update",
            interaction_type="conversation",
            sentiment=0.5,
            outcome="success",
        )

        assert result["updated"] is True
        mock_perspective_engine.update_from_interaction.assert_called_once()

    def test_profile_activate_operation(self, adapter, mock_perspective_engine):
        """Test profile activation."""
        result = adapter.process("profile_activate", profile_name="work")

        assert result is True
        mock_perspective_engine.activate_work_profile.assert_called_once_with("work")

    def test_profile_deactivate_operation(self, adapter, mock_perspective_engine):
        """Test profile deactivation."""
        result = adapter.process("profile_deactivate")

        assert result["status"] == "profile deactivated"
        mock_perspective_engine.deactivate_work_profile.assert_called_once()


class TestSuperKernel:
    """Test SuperKernel orchestration."""

    @pytest.fixture
    def mock_kernel(self):
        """Create mock kernel implementing KernelInterface."""

        class MockKernel(KernelInterface):
            def __init__(self):
                self.process_called = False
                self.process_input = None

            def process(self, input_data, **kwargs):
                self.process_called = True
                self.process_input = input_data
                return {"result": "success", "input": input_data}

            def get_statistics(self):
                return {"calls": 1}

        return MockKernel()

    @pytest.fixture
    def super_kernel(self):
        """Create SuperKernel instance."""
        return SuperKernel()

    def test_initialization(self, super_kernel):
        """Test SuperKernel initialization."""
        assert len(super_kernel.kernels) == 0
        assert super_kernel.execution_count == 0
        assert super_kernel.blocked_count == 0

    def test_register_kernel(self, super_kernel, mock_kernel):
        """Test kernel registration."""
        super_kernel.register_kernel(KernelType.COGNITION, mock_kernel)

        assert KernelType.COGNITION in super_kernel.kernels
        assert super_kernel.kernels[KernelType.COGNITION].instance == mock_kernel

    def test_register_duplicate_kernel(self, super_kernel, mock_kernel):
        """Test that duplicate registration raises error."""
        super_kernel.register_kernel(KernelType.COGNITION, mock_kernel)

        with pytest.raises(ValueError, match="already registered"):
            super_kernel.register_kernel(KernelType.COGNITION, mock_kernel)

    def test_register_invalid_kernel(self, super_kernel):
        """Test that invalid kernel raises error."""
        with pytest.raises(TypeError, match="must implement KernelInterface"):
            super_kernel.register_kernel(KernelType.COGNITION, "not a kernel")

    def test_unregister_kernel(self, super_kernel, mock_kernel):
        """Test kernel unregistration."""
        super_kernel.register_kernel(KernelType.COGNITION, mock_kernel)
        super_kernel.unregister_kernel(KernelType.COGNITION)

        assert KernelType.COGNITION not in super_kernel.kernels

    def test_get_registered_kernels(self, super_kernel, mock_kernel):
        """Test getting list of registered kernels."""
        super_kernel.register_kernel(KernelType.COGNITION, mock_kernel)
        super_kernel.register_kernel(KernelType.REFLECTION, mock_kernel)

        kernels = super_kernel.get_registered_kernels()
        assert len(kernels) == 2
        assert KernelType.COGNITION in kernels
        assert KernelType.REFLECTION in kernels

    def test_process_success(self, super_kernel, mock_kernel):
        """Test successful processing through SuperKernel."""
        super_kernel.register_kernel(KernelType.COGNITION, mock_kernel)

        result = super_kernel.process(
            "test_input", kernel_type=KernelType.COGNITION, source="test"
        )

        assert result["result"] == "success"
        assert result["input"] == "test_input"
        assert mock_kernel.process_called
        assert super_kernel.execution_count == 1

    def test_process_unregistered_kernel(self, super_kernel):
        """Test error when routing to unregistered kernel."""
        with pytest.raises(RuntimeError, match="No kernel registered"):
            super_kernel.process("test", kernel_type=KernelType.COGNITION)

    def test_route_method(self, super_kernel, mock_kernel):
        """Test route() method."""
        super_kernel.register_kernel(KernelType.COGNITION, mock_kernel)

        result = super_kernel.route("task", kernel_type=KernelType.COGNITION)

        assert result["result"] == "success"

    def test_execution_history(self, super_kernel, mock_kernel):
        """Test execution history tracking."""
        super_kernel.register_kernel(KernelType.COGNITION, mock_kernel)

        super_kernel.process("input1", kernel_type=KernelType.COGNITION)
        super_kernel.process("input2", kernel_type=KernelType.COGNITION)

        history = super_kernel.get_execution_history(limit=10)
        assert len(history) == 2

    def test_get_statistics(self, super_kernel, mock_kernel):
        """Test statistics retrieval."""
        super_kernel.register_kernel(KernelType.COGNITION, mock_kernel)
        super_kernel.process("test", kernel_type=KernelType.COGNITION)

        stats = super_kernel.get_statistics()
        assert stats["total_executions"] == 1
        assert stats["blocked_executions"] == 0
        assert KernelType.COGNITION.name in stats["registered_kernels"]

    def test_get_kernel_statistics(self, super_kernel, mock_kernel):
        """Test getting statistics for specific kernel."""
        super_kernel.register_kernel(KernelType.COGNITION, mock_kernel)

        stats = super_kernel.get_kernel_statistics(KernelType.COGNITION)
        assert stats["calls"] == 1


class TestSuperKernelBootstrap:
    """Test SuperKernel bootstrap functions."""

    def test_create_minimal_super_kernel(self):
        """Test creating minimal SuperKernel."""
        super_kernel = create_minimal_super_kernel()

        assert isinstance(super_kernel, SuperKernel)
        assert len(super_kernel.get_registered_kernels()) == 0

    def test_bootstrap_with_cognition_kernel(self):
        """Test bootstrapping with CognitionKernel."""
        mock_cognition = Mock(spec=KernelInterface)

        super_kernel = bootstrap_super_kernel(cognition_kernel=mock_cognition)

        assert KernelType.COGNITION in super_kernel.get_registered_kernels()

    def test_bootstrap_with_reflection_cycle(self):
        """Test bootstrapping with ReflectionCycle."""
        mock_reflection = Mock()
        mock_reflection.perform_daily_reflection = Mock()
        mock_reflection.get_statistics = Mock(return_value={})

        super_kernel = bootstrap_super_kernel(reflection_cycle=mock_reflection)

        assert KernelType.REFLECTION in super_kernel.get_registered_kernels()

    def test_bootstrap_with_multiple_kernels(self):
        """Test bootstrapping with multiple kernels."""
        mock_cognition = Mock(spec=KernelInterface)
        mock_reflection = Mock()
        mock_reflection.get_statistics = Mock(return_value={})
        mock_memory = Mock()
        mock_memory.episodic_memories = {}
        mock_memory.semantic_concepts = {}
        mock_memory.procedural_skills = {}

        super_kernel = bootstrap_super_kernel(
            cognition_kernel=mock_cognition,
            reflection_cycle=mock_reflection,
            memory_engine=mock_memory,
        )

        registered = super_kernel.get_registered_kernels()
        assert len(registered) == 3
        assert KernelType.COGNITION in registered
        assert KernelType.REFLECTION in registered
        assert KernelType.MEMORY in registered
