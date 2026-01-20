"""Explainability agent for decision transparency.

Provides explanations for AI decisions, generates reasoning traces,
and supports interpretability for user trust and debugging.

All explanation operations route through CognitionKernel.
"""


from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent


class ExplainabilityAgent(KernelRoutedAgent):
    """Explains AI decisions and provides reasoning transparency.

    All explanation generation routes through CognitionKernel.
    """

    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        """Initialize the explainability agent with explanation models.

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
            default_risk_level="low"  # Explanation generation is low risk
        )

        # State initialization: The explainability agent state is initialized
        # with disabled mode (enabled = False) and empty explanation storage.
        # This is a placeholder design that allows future implementation of
        # explanation generation and reasoning trace features without breaking
        # existing code that may reference this agent.
        self.enabled: bool = False
        self.explanations: dict = {}
