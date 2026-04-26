"""
Kernel Adapters for SuperKernel System.

This module provides adapter classes that wrap kernels with non-standard
interfaces to make them compatible with the KernelInterface.
"""

import logging
from typing import Any

from .kernel_types import KernelInterface

logger = logging.getLogger(__name__)


class ReflectionCycleAdapter(KernelInterface):
    """
    Adapter for ReflectionCycle to match KernelInterface.

    ReflectionCycle has three different methods for different reflection types:
    - perform_daily_reflection()
    - perform_weekly_reflection()
    - perform_triggered_reflection()

    This adapter exposes a unified process() interface that routes to the
    appropriate method based on input parameters.
    """

    def __init__(self, reflection_cycle):
        """
        Initialize adapter with ReflectionCycle instance.

        Args:
            reflection_cycle: ReflectionCycle instance to wrap
        """
        self.reflection_cycle = reflection_cycle
        logger.info("ReflectionCycleAdapter initialized")

    def process(self, input_data: Any, **kwargs) -> Any:
        """
        Process reflection request.

        Args:
            input_data: Reflection type ("daily", "weekly", "triggered") or None
            **kwargs: Additional arguments for reflection:
                - memory_engine: MemoryEngine instance (required)
                - perspective_engine: PerspectiveEngine instance (optional)
                - trigger_reason: Reason for triggered reflection (for triggered type)

        Returns:
            ReflectionReport object

        Raises:
            ValueError: If reflection type is invalid or required args missing
        """
        # Determine reflection type
        reflection_type = input_data if isinstance(input_data, str) else "daily"

        # Extract required arguments
        memory_engine = kwargs.get("memory_engine")
        perspective_engine = kwargs.get("perspective_engine")

        if not memory_engine:
            raise ValueError("memory_engine is required for reflection")

        # Route to appropriate method
        if reflection_type == "daily":
            return self.reflection_cycle.perform_daily_reflection(
                memory_engine=memory_engine,
                perspective_engine=perspective_engine,
            )
        elif reflection_type == "weekly":
            return self.reflection_cycle.perform_weekly_reflection(
                memory_engine=memory_engine,
                perspective_engine=perspective_engine,
            )
        elif reflection_type == "triggered":
            trigger_reason = kwargs.get("trigger_reason", "Unknown trigger")
            return self.reflection_cycle.perform_triggered_reflection(
                trigger_reason=trigger_reason,
                memory_engine=memory_engine,
                perspective_engine=perspective_engine,
            )
        else:
            raise ValueError(f"Unknown reflection type: {reflection_type}")

    def get_statistics(self) -> dict[str, Any]:
        """Get reflection cycle statistics."""
        return self.reflection_cycle.get_statistics()


class MemoryEngineAdapter(KernelInterface):
    """
    Adapter for MemoryEngine to match KernelInterface.

    MemoryEngine has multiple specific methods for different memory operations:
    - store_episodic_memory()
    - retrieve_episodic_memory()
    - search_episodic_memories()
    - store_semantic_concept()
    - store_procedural_skill()
    - etc.

    This adapter exposes a unified process() interface that routes to the
    appropriate method based on input parameters.
    """

    def __init__(self, memory_engine):
        """
        Initialize adapter with MemoryEngine instance.

        Args:
            memory_engine: MemoryEngine instance to wrap
        """
        self.memory_engine = memory_engine
        logger.info("MemoryEngineAdapter initialized")

    def process(self, input_data: Any, **kwargs) -> Any:
        """
        Process memory operation.

        Args:
            input_data: Operation type or data structure:
                - "search": Search episodic memories
                - "retrieve": Retrieve specific memory
                - "consolidate": Consolidate memories
                - dict with 'operation' key: Specific operation
                - None: Return memory statistics
            **kwargs: Operation-specific arguments

        Returns:
            Operation result (type depends on operation)

        Raises:
            ValueError: If operation is invalid
        """
        # Handle different input formats
        if input_data is None:
            # Return statistics
            return {
                "episodic_count": len(self.memory_engine.episodic_memories),
                "semantic_count": len(self.memory_engine.semantic_concepts),
                "procedural_count": len(self.memory_engine.procedural_skills),
            }

        if isinstance(input_data, str):
            operation = input_data
        elif isinstance(input_data, dict):
            operation = input_data.get("operation", "search")
        else:
            operation = "search"

        # Route to appropriate method
        if operation == "search":
            query = kwargs.get("query", "")
            limit = kwargs.get("limit", 10)
            return self.memory_engine.search_episodic_memories(query=query, limit=limit)
        elif operation == "retrieve":
            memory_id = kwargs.get("memory_id")
            if not memory_id:
                raise ValueError("memory_id required for retrieve operation")
            return self.memory_engine.retrieve_episodic_memory(memory_id)
        elif operation == "recent":
            limit = kwargs.get("limit", 10)
            return self.memory_engine.get_recent_memories(limit=limit)
        elif operation == "consolidate":
            # Memory consolidation is typically done during weekly reflection
            # This is a placeholder for potential future direct consolidation
            return {"status": "consolidation scheduled"}
        else:
            raise ValueError(f"Unknown memory operation: {operation}")

    def get_statistics(self) -> dict[str, Any]:
        """Get memory engine statistics."""
        return {
            "episodic_count": len(self.memory_engine.episodic_memories),
            "semantic_count": len(self.memory_engine.semantic_concepts),
            "procedural_count": len(self.memory_engine.procedural_skills),
        }


class PerspectiveEngineAdapter(KernelInterface):
    """
    Adapter for PerspectiveEngine to match KernelInterface.

    PerspectiveEngine has various methods for managing perspective:
    - update_from_interaction()
    - get_perspective_summary()
    - create_work_profile()
    - activate_work_profile()
    - etc.

    This adapter exposes a unified process() interface that routes to the
    appropriate method based on input parameters.
    """

    def __init__(self, perspective_engine):
        """
        Initialize adapter with PerspectiveEngine instance.

        Args:
            perspective_engine: PerspectiveEngine instance to wrap
        """
        self.perspective_engine = perspective_engine
        logger.info("PerspectiveEngineAdapter initialized")

    def process(self, input_data: Any, **kwargs) -> Any:
        """
        Process perspective operation.

        Args:
            input_data: Operation type or data:
                - "update": Update from interaction
                - "summary": Get perspective summary
                - "profile_activate": Activate work profile
                - "profile_deactivate": Deactivate work profile
                - None: Return perspective summary
            **kwargs: Operation-specific arguments

        Returns:
            Operation result (type depends on operation)

        Raises:
            ValueError: If operation is invalid
        """
        # Handle different input formats
        if input_data is None:
            return self.perspective_engine.get_perspective_summary()

        if isinstance(input_data, str):
            operation = input_data
        elif isinstance(input_data, dict):
            operation = input_data.get("operation", "summary")
        else:
            operation = "summary"

        # Route to appropriate method
        if operation == "update":
            interaction_type = kwargs.get("interaction_type", "general")
            sentiment = kwargs.get("sentiment", 0.0)
            outcome = kwargs.get("outcome", "neutral")
            traits_observed = kwargs.get("traits_observed", {})

            return self.perspective_engine.update_from_interaction(
                interaction_type=interaction_type,
                sentiment=sentiment,
                outcome=outcome,
                traits_observed=traits_observed,
            )
        elif operation == "summary":
            return self.perspective_engine.get_perspective_summary()
        elif operation == "profile_activate":
            profile_name = kwargs.get("profile_name")
            if not profile_name:
                raise ValueError("profile_name required for profile_activate")
            return self.perspective_engine.activate_work_profile(profile_name)
        elif operation == "profile_deactivate":
            self.perspective_engine.deactivate_work_profile()
            return {"status": "profile deactivated"}
        else:
            raise ValueError(f"Unknown perspective operation: {operation}")

    def get_statistics(self) -> dict[str, Any]:
        """Get perspective engine statistics."""
        return self.perspective_engine.get_perspective_summary()


__all__ = [
    "ReflectionCycleAdapter",
    "MemoryEngineAdapter",
    "PerspectiveEngineAdapter",
]
