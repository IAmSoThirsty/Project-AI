"""System oversight agent for monitoring and compliance.

Monitors system health, tracks activities, and ensures compliance with
policy constraints and security requirements.

All operations route through CognitionKernel for governance tracking.
"""

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent


class OversightAgent(KernelRoutedAgent):
    """Monitors system state and enforces compliance rules.

    All monitoring and compliance operations route through CognitionKernel.
    """

    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        """Initialize the oversight agent with system monitors.

        Args:
            kernel: CognitionKernel instance for routing operations

        This method initializes the agent state. Full feature implementation
        is deferred to future development phases. The agent currently operates
        in disabled mode and maintains empty data structures for future use.
        """
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",
        )

        # State initialization: The oversight agent state is initialized
        # with disabled mode (enabled = False) and empty monitor storage.
        # This is a placeholder design that allows future implementation of
        # system monitoring and compliance checking features without breaking
        # existing code that may reference this agent.
        self.enabled: bool = False
        self.monitors: dict = {}
