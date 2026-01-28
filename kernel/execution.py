from kernel.tarl_gate import TarlGate
from src.cognition.codex.escalation import CodexDeus


class ExecutionKernel:
    def __init__(self, governance, tarl_runtime, codex: CodexDeus):
        self.governance = governance
        self.codex = codex
        self.tarl_gate = TarlGate(tarl_runtime, codex)

    def execute(self, action, context=None):
        """
        Execute an action through the kernel with TARL enforcement.

        Args:
            action: The action to execute
            context: Execution context for TARL evaluation

        Returns:
            Result of the action execution
        """
        if context is None:
            context = {}

        # Enforce TARL policies
        self.tarl_gate.enforce(context)

        # Execute the action (placeholder for actual execution logic)
        return {
            "status": "success",
            "action": action,
            "governance": self.governance,
        }
