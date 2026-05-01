"""Execution gate (Cerberus layer) — governance-verified entry point for all actions."""

from __future__ import annotations

from typing import Any, Callable, Dict, Tuple

from app.core.governance_kernel import get_kernel
from app.core.mutation_binding import MutationGovernanceBinding


class ExecutionGate:

    def __init__(self) -> None:
        self.kernel = get_kernel()

    def execute(
        self,
        domain: str,
        action: str,
        context: Dict[str, Any],
        executor_fn: Callable[[Dict[str, Any]], Any],
    ) -> Tuple[bool, Any]:
        approved, decision = self.kernel.evaluate_action(domain, action, context)

        if not approved:
            return False, decision.reason

        binding = MutationGovernanceBinding.create(decision)

        if not binding.verify():
            return False, "Binding verification failed"

        result = executor_fn(context)
        return True, result


_gate_instance: ExecutionGate | None = None


def get_execution_gate() -> ExecutionGate:
    global _gate_instance
    if _gate_instance is None:
        _gate_instance = ExecutionGate()
    return _gate_instance


__all__ = ["ExecutionGate", "get_execution_gate"]
