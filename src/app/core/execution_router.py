"""Unified execution router — the ONLY legal execution path in the system."""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Callable, Dict, Tuple

from app.core.execution_gate import get_execution_gate
from app.core.invariant_engine import get_invariant_engine
from app.core.nirl.forge import Forge
from app.core.waterfall_filter import get_waterfall_filter
from app.core.liara_bridge import get_liara_context, liara_ttl_check
from app.core.state_register import get_state_register

logger = logging.getLogger(__name__)


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

    # 2. Liara TTL check — auto-revoke expired crisis roles, inject state.
    liara_ttl_check(context)
    context = {**context, **get_liara_context()}

    # 2.5. Runtime enforcement — consent / PAGL prohibitions / tier / sovereign.
    try:
        from app.governance.runtime_enforcer import get_runtime_enforcer, EnforcementContext
        _enforce_ctx = EnforcementContext(
            user_id=context.get("user_id", "anonymous"),
            action=action,
            is_commercial=context.get("is_commercial", False),
            is_government=context.get("is_government", False),
            metadata=context,
        )
        _enforce_result = get_runtime_enforcer().enforce(_enforce_ctx)
        if _enforce_result.verdict == "deny":
            return False, f"RuntimeEnforcer denied: {_enforce_result.reason}"
    except Exception:
        pass

    # 3. State Register — inject temporal context for anti-gaslighting checks.
    try:
        sr = get_state_register()
        temporal = sr.get_temporal_context()
        context = {**context, "_temporal": temporal}
    except Exception:
        pass

    # 3.5. Trust scoring + adversarial pattern detection.
    try:
        from app.core.tarl_operational_extensions import (
            TrustScoringEngine, AdversarialPatternRegistry,
        )
        _trust_score, _ = TrustScoringEngine().calculate_trust_score(
            context.get("user_id", "anonymous"),
            {"behavioral": 0.7, "security": 0.7, "governance": 0.7, "pattern": 0.7},
        )
        _adv_flags = AdversarialPatternRegistry().detect_patterns(
            str(context.get("payload", ""))
        )
        context = {**context, "_trust_score": _trust_score, "_adversarial_flags": _adv_flags}
    except Exception:
        pass

    # 4. Invariant pre-checks.
    invariant_engine = get_invariant_engine()
    try:
        invariant_engine.validate(context)
    except Exception as exc:
        return False, str(exc)

    # 5. Governance gate (authority chain + Triumvirate + Fates + ledger).
    gate = get_execution_gate()
    gate_ok, gate_result = gate.execute(domain, action, context, executor_fn)

    # 6. NIRL Forge — verify governance context integrity after gate approval.
    #    Forge failure is non-fatal (logged) so legitimate executions are not blocked.
    if gate_ok:
        try:
            ctx_str = f"{domain}:{action}:{sorted(context.items())}"
            forge = Forge()
            forge_payload = {
                "data": ctx_str,
                "checksum": hashlib.sha256(ctx_str.encode()).hexdigest(),
                "section_id": domain,
                "probe_id": action,
            }
            forge_result = forge.process(forge_payload)
            if not forge_result.get("success"):
                logger.warning(
                    "NIRL Forge integrity warning: domain=%s action=%s reason=%s",
                    domain, action, forge_result.get("reason"),
                )
        except Exception:
            logger.exception("NIRL Forge processing failed (non-fatal)")

    return gate_ok, gate_result


__all__ = ["execute"]
