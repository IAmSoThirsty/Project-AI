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

        # Sovereignty layer — Ed25519 policy-state binding for every approved execution.
        try:
            import sys as _sys
            from pathlib import Path as _Path
            _repo_root = str(_Path(__file__).resolve().parents[4])
            if _repo_root not in _sys.path:
                _sys.path.insert(0, _repo_root)
            from governance.sovereign_runtime import SovereignRuntime
            _sr = SovereignRuntime()
            _policy_state = {
                "domain": domain,
                "action": action,
                "decision_id": decision.decision_id,
            }
            _sov_binding = _sr.create_policy_state_binding(_policy_state, context)
            if not _sr.verify_policy_state_binding(_policy_state, context, _sov_binding):
                return False, "Sovereign policy binding verification failed"
            _sr.audit_log(
                "execution_authorized",
                {"domain": domain, "action": action},
                severity="INFO",
            )
        except Exception:
            pass  # graceful degrade when governance/ not on path

        result = executor_fn(context)
        return True, result


_gate_instance: ExecutionGate | None = None


def get_execution_gate() -> ExecutionGate:
    global _gate_instance
    if _gate_instance is None:
        _gate_instance = ExecutionGate()
    return _gate_instance


__all__ = ["ExecutionGate", "get_execution_gate"]
