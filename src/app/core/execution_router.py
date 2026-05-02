"""Unified execution router — the ONLY legal execution path in the system."""

from __future__ import annotations

from typing import Any, Callable, Dict, Tuple

from app.core.execution_gate import get_execution_gate
from app.core.invariant_engine import get_invariant_engine
from app.core.waterfall_filter import get_waterfall_filter


def execute(
    domain: str,
    action: str,
    context: Dict[str, Any],
    executor_fn: Callable[[Dict[str, Any]], Any],
) -> Tuple[bool, Any]:
    """The only legal way to execute anything in the system. No exceptions."""
    # 1. Waterfall inbound filter (outermost gate).
    wf = get_waterfall_filter()
    wf_result = wf.filter(context)
    if not wf_result.allowed:
        return False, f"Waterfall rejected: {wf_result.reason}"
    context = wf_result.context  # may have been enriched

    # 2. Invariant pre-checks.
    invariant_engine = get_invariant_engine()
    try:
        invariant_engine.validate(context)
    except Exception as exc:
        return False, str(exc)

    # 3. Governance gate (authority chain + Triumvirate + Fates + ledger).
    gate = get_execution_gate()
    return gate.execute(domain, action, context, executor_fn)


__all__ = ["execute"]
