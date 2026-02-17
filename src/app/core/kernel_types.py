"""
Kernel Types and Base Interface for SuperKernel System.

This module defines the types of kernels in the system and provides
a base interface that all kernels must implement (directly or via adapter).
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any


class KernelType(Enum):
    """
    Types of kernels in the system.

    Each kernel type represents a specific domain of cognitive processing:
    - COGNITION: General cognitive processing (actions, tools, agents)
    - REFLECTION: Self-reflection and insight generation
    - MEMORY: Memory storage and retrieval
    - PERSPECTIVE: Personality and worldview management
    - IDENTITY: Identity and self-concept management
    """

    COGNITION = auto()
    REFLECTION = auto()
    MEMORY = auto()
    PERSPECTIVE = auto()
    IDENTITY = auto()


class KernelInterface(ABC):
    """
    Base interface that all kernels must implement.

    This ensures consistent interaction patterns across all subordinate
    kernels in the SuperKernel system. Kernels that don't naturally fit
    this interface should be wrapped with an adapter.

    The process() method is the primary entrypoint for all kernel operations.
    The optional route() method provides an alternative entrypoint for
    agent-initiated tasks (similar to CognitionKernel.route()).
    """

    @abstractmethod
    def process(self, input_data: Any, **kwargs) -> Any:
        """
        Process input data and return result.

        This is the primary entrypoint for kernel operations. The specific
        interpretation of input_data and kwargs depends on the kernel type.

        Args:
            input_data: Input data to process (type depends on kernel)
            **kwargs: Additional keyword arguments for processing

        Returns:
            Processing result (type depends on kernel)

        Raises:
            RuntimeError: If processing fails
        """

    def route(self, task: Any, *, source: str = "agent", **kwargs) -> Any:
        """
        Optional routing method for agent-initiated tasks.

        This method provides an alternative entrypoint similar to
        CognitionKernel.route(). Not all kernels need to implement this.

        Default implementation delegates to process().

        Args:
            task: Task to route
            source: Source of the task (default: "agent")
            **kwargs: Additional keyword arguments

        Returns:
            Task result
        """
        return self.process(task, source=source, **kwargs)

    def get_statistics(self) -> dict[str, Any]:
        """
        Get kernel statistics (optional).

        Returns:
            Dictionary with kernel statistics
        """
        return {}


__all__ = [
    "KernelType",
    "KernelInterface",
]
