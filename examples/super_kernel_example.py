"""
SuperKernel Example - Demonstrates SuperKernel usage.

This example shows how to use the SuperKernel system to orchestrate
multiple subordinate kernels with centralized governance and logging.
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def example_1_minimal_setup():
    """Example 1: Minimal SuperKernel setup for testing."""
    from app.core.kernel_types import KernelInterface, KernelType
    from app.core.super_kernel_bootstrap import create_minimal_super_kernel

    logger.info("=== Example 1: Minimal Setup ===")

    # Create minimal SuperKernel
    super_kernel = create_minimal_super_kernel()

    # Create a simple test kernel
    class TestKernel(KernelInterface):
        def process(self, input_data, **kwargs):
            return {"result": f"Processed: {input_data}"}

    # Register kernel
    super_kernel.register_kernel(KernelType.COGNITION, TestKernel())

    # Use it
    result = super_kernel.process(
        "Hello World",
        kernel_type=KernelType.COGNITION,
        source="test",
    )

    logger.info("Result: %s", result)
    logger.info("Statistics: %s", super_kernel.get_statistics())


def example_2_with_adapters():
    """Example 2: Using adapters for non-standard kernels."""
    from unittest.mock import Mock

    from app.core.kernel_adapters import (
        MemoryEngineAdapter,
        ReflectionCycleAdapter,
    )
    from app.core.kernel_types import KernelType
    from app.core.super_kernel import SuperKernel

    logger.info("\n=== Example 2: With Adapters ===")

    # Create SuperKernel
    super_kernel = SuperKernel()

    # Create mock ReflectionCycle
    mock_reflection = Mock()
    mock_reflection.perform_daily_reflection = Mock(
        return_value=Mock(
            type="daily",
            insights=[{"text": "Test insight"}],
            memories_processed=5,
        )
    )
    mock_reflection.get_statistics = Mock(return_value={"reflections": 1})

    # Create mock MemoryEngine
    mock_memory = Mock()
    mock_memory.episodic_memories = {"mem1": {}, "mem2": {}}
    mock_memory.semantic_concepts = {}
    mock_memory.procedural_skills = {}
    mock_memory.search_episodic_memories = Mock(
        return_value=[{"id": "mem1", "description": "Test memory"}]
    )

    # Wrap with adapters
    reflection_adapter = ReflectionCycleAdapter(mock_reflection)
    memory_adapter = MemoryEngineAdapter(mock_memory)

    # Register kernels
    super_kernel.register_kernel(KernelType.REFLECTION, reflection_adapter)
    super_kernel.register_kernel(KernelType.MEMORY, memory_adapter)

    # Use ReflectionCycle
    logger.info("Running daily reflection...")
    report = super_kernel.process(
        "daily",
        kernel_type=KernelType.REFLECTION,
        memory_engine=mock_memory,
    )
    logger.info("Reflection result: %s", report)

    # Use MemoryEngine
    logger.info("Searching memories...")
    results = super_kernel.process(
        "search",
        kernel_type=KernelType.MEMORY,
        query="test",
    )
    logger.info("Memory results: %s", results)

    # Get statistics
    logger.info("SuperKernel stats: %s", super_kernel.get_statistics())
    logger.info(
        "Reflection stats: %s",
        super_kernel.get_kernel_statistics(KernelType.REFLECTION),
    )
    logger.info(
        "Memory stats: %s", super_kernel.get_kernel_statistics(KernelType.MEMORY)
    )


def example_3_execution_history():
    """Example 3: Execution history and five-channel logging."""
    from app.core.kernel_types import KernelInterface, KernelType
    from app.core.super_kernel_bootstrap import create_minimal_super_kernel

    logger.info("\n=== Example 3: Execution History ===")

    # Create SuperKernel
    super_kernel = create_minimal_super_kernel()

    # Create test kernel
    class CounterKernel(KernelInterface):
        def __init__(self):
            self.count = 0

        def process(self, input_data, **kwargs):
            self.count += 1
            return {"count": self.count, "input": input_data}

    counter = CounterKernel()
    super_kernel.register_kernel(KernelType.COGNITION, counter)

    # Execute multiple operations
    for i in range(5):
        result = super_kernel.process(
            f"Operation {i+1}",
            kernel_type=KernelType.COGNITION,
            source="test",
        )
        logger.info("Operation %s result: %s", i + 1, result)

    # Get execution history
    logger.info("\nExecution History:")
    history = super_kernel.get_execution_history(limit=10)
    for record in history:
        logger.info("  Execution %s:", record["execution_id"])
        logger.info("    Attempt: %s", record["attempt"])
        logger.info("    Decision: %s", record["decision"])
        logger.info("    Result: %s", record["result"])
        logger.info("    Duration: %sms", record["duration_ms"])


def example_4_error_handling():
    """Example 4: Error handling and blocked executions."""
    from unittest.mock import Mock

    from app.core.kernel_types import KernelInterface, KernelType
    from app.core.super_kernel import SuperKernel

    logger.info("\n=== Example 4: Error Handling ===")

    # Create SuperKernel with mock governance
    mock_governance = Mock()
    super_kernel = SuperKernel(governance=mock_governance)

    # Create failing kernel
    class FailingKernel(KernelInterface):
        def process(self, input_data, **kwargs):
            if input_data == "fail":
                raise ValueError("Intentional failure")
            return {"result": "success"}

    super_kernel.register_kernel(KernelType.COGNITION, FailingKernel())

    # Test success case
    logger.info("Testing success case...")
    mock_governance.validate_action = Mock(
        return_value={"allowed": True, "reason": "Approved"}
    )
    result = super_kernel.process(
        "success",
        kernel_type=KernelType.COGNITION,
    )
    logger.info("Success result: %s", result)

    # Test failure case
    logger.info("\nTesting failure case...")
    try:
        result = super_kernel.process(
            "fail",
            kernel_type=KernelType.COGNITION,
        )
    except ValueError as e:
        logger.info("Caught expected error: %s", e)

    # Test blocked case
    logger.info("\nTesting blocked case...")
    mock_governance.validate_action = Mock(
        return_value={"allowed": False, "reason": "Blocked for safety"}
    )
    try:
        result = super_kernel.process(
            "blocked",
            kernel_type=KernelType.COGNITION,
        )
    except PermissionError as e:
        logger.info("Caught expected permission error: %s", e)

    # Check statistics
    stats = super_kernel.get_statistics()
    logger.info("\nFinal statistics: %s", stats)
    logger.info("Blocked count: %s", super_kernel.blocked_count)


def main():
    """Run all examples."""
    try:
        example_1_minimal_setup()
        example_2_with_adapters()
        example_3_execution_history()
        example_4_error_handling()

        logger.info("\n=== All Examples Completed Successfully ===")
    except Exception as e:
        logger.error("Example failed: %s", e, exc_info=True)


if __name__ == "__main__":
    main()
