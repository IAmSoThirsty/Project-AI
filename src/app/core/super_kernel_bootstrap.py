"""
SuperKernel Bootstrap - Setup and Configuration.

This module provides convenience functions for setting up and configuring
the SuperKernel with all subordinate kernels.
"""

import logging
from typing import Any

from .kernel_adapters import (
    MemoryEngineAdapter,
    PerspectiveEngineAdapter,
    ReflectionCycleAdapter,
)
from .kernel_types import KernelType
from .super_kernel import SuperKernel

logger = logging.getLogger(__name__)


def bootstrap_super_kernel(
    cognition_kernel: Any | None = None,
    reflection_cycle: Any | None = None,
    memory_engine: Any | None = None,
    perspective_engine: Any | None = None,
    identity_system: Any | None = None,
    triumvirate: Any | None = None,
    governance: Any | None = None,
    rbac_system: Any | None = None,
) -> SuperKernel:
    """
    Bootstrap SuperKernel with all available kernels.
    
    This function creates a SuperKernel instance and registers all provided
    subordinate kernels. Kernels that don't match the KernelInterface are
    automatically wrapped with appropriate adapters.
    
    Args:
        cognition_kernel: CognitionKernel instance (already has process/route)
        reflection_cycle: ReflectionCycle instance (will be wrapped)
        memory_engine: MemoryEngine instance (will be wrapped)
        perspective_engine: PerspectiveEngine instance (will be wrapped)
        identity_system: Identity system instance (will be wrapped)
        triumvirate: Triumvirate instance for governance
        governance: Legacy governance system (optional)
        rbac_system: RBAC system for access control (optional)
        
    Returns:
        Configured SuperKernel instance
        
    Example:
        >>> from app.core.cognition_kernel import CognitionKernel
        >>> from app.core.reflection_cycle import ReflectionCycle
        >>> from app.core.memory_engine import MemoryEngine
        >>> 
        >>> cognition = CognitionKernel(...)
        >>> reflection = ReflectionCycle(data_dir="data/reflection")
        >>> memory = MemoryEngine(data_dir="data/memory")
        >>> 
        >>> super_kernel = bootstrap_super_kernel(
        ...     cognition_kernel=cognition,
        ...     reflection_cycle=reflection,
        ...     memory_engine=memory,
        ...     triumvirate=triumvirate,
        ... )
        >>> 
        >>> # Use SuperKernel for all operations
        >>> result = super_kernel.process(
        ...     {"action": "solve_task"},
        ...     kernel_type=KernelType.COGNITION,
        ... )
    """
    logger.info("Bootstrapping SuperKernel...")
    
    # Create SuperKernel with governance
    super_kernel = SuperKernel(
        triumvirate=triumvirate,
        governance=governance,
        rbac_system=rbac_system,
    )
    
    # Register CognitionKernel (no adapter needed - has process/route)
    if cognition_kernel:
        super_kernel.register_kernel(
            KernelType.COGNITION,
            cognition_kernel,
            metadata={"type": "CognitionKernel", "adapter": False},
        )
        logger.info("  Registered: CognitionKernel (native)")
    
    # Register ReflectionCycle (with adapter)
    if reflection_cycle:
        adapter = ReflectionCycleAdapter(reflection_cycle)
        super_kernel.register_kernel(
            KernelType.REFLECTION,
            adapter,
            metadata={"type": "ReflectionCycle", "adapter": True},
        )
        logger.info("  Registered: ReflectionCycle (with adapter)")
    
    # Register MemoryEngine (with adapter)
    if memory_engine:
        adapter = MemoryEngineAdapter(memory_engine)
        super_kernel.register_kernel(
            KernelType.MEMORY,
            adapter,
            metadata={"type": "MemoryEngine", "adapter": True},
        )
        logger.info("  Registered: MemoryEngine (with adapter)")
    
    # Register PerspectiveEngine (with adapter)
    if perspective_engine:
        adapter = PerspectiveEngineAdapter(perspective_engine)
        super_kernel.register_kernel(
            KernelType.PERSPECTIVE,
            adapter,
            metadata={"type": "PerspectiveEngine", "adapter": True},
        )
        logger.info("  Registered: PerspectiveEngine (with adapter)")
    
    # Note: Identity system could be registered as IDENTITY kernel type
    # if needed, but typically it's managed by CognitionKernel
    
    logger.info("SuperKernel bootstrapped successfully")
    logger.info("  Registered kernels: %s", super_kernel.get_registered_kernels())
    
    return super_kernel


def create_minimal_super_kernel(
    data_dir: str = "data",
) -> SuperKernel:
    """
    Create a minimal SuperKernel for testing or simple use cases.
    
    This function creates a basic SuperKernel with minimal configuration.
    Useful for testing or when you don't need all subsystems.
    
    Args:
        data_dir: Base data directory for all kernels
        
    Returns:
        Minimal SuperKernel instance
    """
    logger.info("Creating minimal SuperKernel...")
    
    # Create SuperKernel without governance
    super_kernel = SuperKernel()
    
    logger.info("Minimal SuperKernel created")
    logger.warning("No governance configured - all operations auto-approved")
    
    return super_kernel


__all__ = [
    "bootstrap_super_kernel",
    "create_minimal_super_kernel",
]
