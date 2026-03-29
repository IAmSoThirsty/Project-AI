# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / tarl_gate.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / tarl_gate.py

#
# COMPLIANCE: Sovereign Substrate / tarl_gate.py


from kernel.tarl_codex_bridge import TarlCodexBridge
from src.cognition.codex.escalation import CodexDeus
from tarl import TarlRuntime
from tarl.spec import TarlVerdict


class TarlEnforcementError(Exception):
    """Raised when TARL policy enforcement blocks an action."""

    pass


class TarlGate:
    def __init__(self, runtime: TarlRuntime, codex: CodexDeus):
        self.runtime = runtime
        self.codex_bridge = TarlCodexBridge(codex)

    def enforce(self, execution_context):
        """
        Enforce TARL policies on the execution context.

        Args:
            execution_context: Dictionary containing execution metadata

        Raises:
            TarlEnforcementError: If policy denies or escalates the action
        """
        decision = self.runtime.evaluate(execution_context)

        if decision.verdict == TarlVerdict.DENY:
            raise TarlEnforcementError(f"Denied: {decision.reason}")

        if decision.verdict == TarlVerdict.ESCALATE:
            self.codex_bridge.handle(decision, execution_context)
            raise TarlEnforcementError(f"Escalated: {decision.reason}")

        return decision
