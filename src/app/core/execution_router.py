"""Unified execution router — the ONLY legal execution path in the system."""

# IRON_PATH_2_PHASE_1_ANNOTATION_ONLY
# IRON_PATH_2_STOP_CONDITION: execution authority fragmentation
# Current behavior: execution_router.py is one execution authority fragment, while pipeline.py and OctoReflex can enter governance through other paths.
# Required before Phase 2+: Build a caller-map-driven consolidation so no execution path bypasses ExecutionGate unless explicitly classified as test-only or non-authoritative.
# Do not change behavior in Phase 1.

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Callable, Dict, Tuple

from app.core.execution_gate import get_execution_gate
from app.core.invariant_engine import get_invariant_engine
from app.core.nirl.forge import Forge
from app.core.waterfall_filter import get_waterfall_filter
from app.core.liara_bridge import get_liara_context, liara_ttl_check
from app.core.state_register import get_state_register

logger = logging.getLogger(__name__)


_VALID_ROUTER_RECEIPT_OUTCOMES = {
    "ALLOW",
    "DENY",
    "CLARIFY",
    "HUMAN_APPROVAL_REQUIRED",
    "DEGRADED_READ_ONLY",
    "HALT",
    "ESCALATE",
}

_PROTECTED_CONTEXT_KEYS = (
    "requires_capability_token",
    "_capability_token",
    "capability_token",
    "required_scope",
    "required_resource",
    "high_impact",
    "is_government",
    "is_commercial",
    "requires_continuity",
    "continuity_required",
    "protected",
    "is_protected",
)

_DIAGNOSTIC_ACTION_TOKENS = (
    "status",
    "health",
    "ping",
    "info",
    "audit",
    "log",
    "observe",
    "monitor",
    "inspect",
    "diagnostic",
    "diagnostics",
    "describe",
    "show",
    "view",
    "stat",
)


def _context_risk_score(context: Dict[str, Any]) -> float:
    for key in ("risk_score", "semantic_risk_score", "threat_score"):
        if key not in context:
            continue
        try:
            return float(context.get(key) or 0.0)
        except (TypeError, ValueError):
            return 1.0
    return 0.0


def _is_high_risk_context(context: Dict[str, Any]) -> bool:
    risk_level = str(context.get("risk_level", "")).lower()
    if risk_level in {"medium", "high", "critical"}:
        return True
    return _context_risk_score(context) > 0.2


def _is_protected_context(context: Dict[str, Any]) -> bool:
    return any(bool(context.get(key)) for key in _PROTECTED_CONTEXT_KEYS)


def _has_meaningful_payload(context: Dict[str, Any]) -> bool:
    payload = context.get("payload")
    if payload is None:
        return False
    if isinstance(payload, str):
        return bool(payload.strip())
    if isinstance(payload, (bytes, bytearray)):
        return bool(payload.strip())
    if isinstance(payload, (dict, list, tuple, set)):
        return bool(payload)
    return True


def _is_diagnostic_action(action: str, context: Dict[str, Any]) -> bool:
    if context.get("is_low_risk_diagnostic") or context.get("low_risk_diagnostic"):
        return True
    normalized = action.lower().replace("-", "_")
    return any(token in normalized for token in _DIAGNOSTIC_ACTION_TOKENS)


def _is_explicit_low_risk_read_only_diagnostic(
    action: str,
    context: Dict[str, Any],
    *,
    require_no_payload: bool = False,
) -> bool:
    from app.core.degraded_mode import classify_action_mutability

    if classify_action_mutability(action, context):
        return False
    if _is_protected_context(context) or _is_high_risk_context(context):
        return False
    if require_no_payload and _has_meaningful_payload(context):
        return False
    return _is_diagnostic_action(action, context)


def _router_request_hash(domain: str, action: str, context: Dict[str, Any]) -> str:
    user_id_hash = hashlib.sha256(
        str(context.get("user_id", "anonymous")).encode()
    ).hexdigest()[:16]
    session_id_hash = hashlib.sha256(
        str(context.get("session_id", "")).encode()
    ).hexdigest()[:16]
    payload = {
        "domain": domain,
        "action": action,
        "context_keys": sorted(str(key) for key in context.keys()),
        "protected": _is_protected_context(context),
        "high_risk": _is_high_risk_context(context),
        "payload_present": _has_meaningful_payload(context),
        "user_id_hash": user_id_hash,
        "session_id_hash": session_id_hash,
    }
    data = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(data.encode()).hexdigest()


def _failure_metadata(
    *,
    failure_source: str,
    failure_mode: str,
    exc: Exception,
    failed_components: list[str] | None = None,
    non_authoritative_warning: bool = False,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "router_precheck": True,
        "failure_source": failure_source,
        "failure_mode": failure_mode,
        "bypass_recorded": True,
        "error_type": type(exc).__name__,
        "error_hash": hashlib.sha256(str(exc).encode()).hexdigest()[:16],
    }
    if failed_components:
        metadata["failed_components"] = failed_components
    if non_authoritative_warning:
        metadata["non_authoritative_warning"] = True
    return metadata


def _with_router_bypass_record(
    context: Dict[str, Any],
    metadata: dict[str, Any],
) -> Dict[str, Any]:
    records = list(context.get("_router_bypass_records", []))
    records.append(dict(metadata))
    return {
        **context,
        "_router_bypass_records": records,
        "_router_precheck_degraded": True,
    }


def _emit_router_precheck_receipt(
    *,
    domain: str,
    action: str,
    context: Dict[str, Any],
    final_outcome: str,
    metadata: dict[str, Any],
) -> None:
    if final_outcome not in _VALID_ROUTER_RECEIPT_OUTCOMES:
        raise ValueError(f"Invalid router precheck outcome: {final_outcome}")

    from app.core.evidence_bundle import EvidenceBundleWriter
    from app.core.governance_observability import build_observation, get_collector

    policy_version = str(context.get("policy_version", "") or "")
    policy_hash = str(context.get("policy_hash", "") or "")
    risk_score = _context_risk_score(context)
    bundle = EvidenceBundleWriter().build(
        request_hash=_router_request_hash(domain, action, context),
        intent_classification="router_precheck",
        risk_score=risk_score,
        final_outcome=final_outcome,
        policy_version=policy_version,
        policy_hash=policy_hash,
    )
    observation = build_observation(
        session_id=str(context.get("session_id", "") or ""),
        domain=domain,
        action=action,
        final_outcome=final_outcome,
        risk_score=risk_score,
        policy_version=policy_version,
        policy_hash=policy_hash,
        bundle_id=bundle.bundle_id,
        metadata=metadata,
    )
    get_collector().record(observation)


def _deny_router_precheck(
    *,
    domain: str,
    action: str,
    context: Dict[str, Any],
    failure_source: str,
    label: str,
    exc: Exception,
    failed_components: list[str] | None = None,
) -> Tuple[bool, str]:
    metadata = _failure_metadata(
        failure_source=failure_source,
        failure_mode="fail_closed",
        exc=exc,
        failed_components=failed_components,
    )
    try:
        _emit_router_precheck_receipt(
            domain=domain,
            action=action,
            context=context,
            final_outcome="DENY",
            metadata=metadata,
        )
    except Exception as receipt_exc:
        logger.exception(
            "Router precheck DENY receipt emission failed: source=%s",
            failure_source,
        )
        return (
            False,
            f"{label} failed closed: {exc} "
            f"(receipt emission failed: {receipt_exc})",
        )
    return False, f"{label} failed closed: {exc}"


def _record_degraded_router_precheck(
    *,
    domain: str,
    action: str,
    context: Dict[str, Any],
    failure_source: str,
    label: str,
    exc: Exception,
    failed_components: list[str] | None = None,
) -> Tuple[bool, str | None, Dict[str, Any]]:
    metadata = _failure_metadata(
        failure_source=failure_source,
        failure_mode="degraded_read_only",
        exc=exc,
        failed_components=failed_components,
        non_authoritative_warning=True,
    )
    try:
        _emit_router_precheck_receipt(
            domain=domain,
            action=action,
            context=context,
            final_outcome="DEGRADED_READ_ONLY",
            metadata=metadata,
        )
    except Exception as receipt_exc:
        logger.exception(
            "Router precheck DEGRADED_READ_ONLY receipt emission failed: source=%s",
            failure_source,
        )
        return False, f"{label} receipt emission failed closed: {receipt_exc}", context
    return True, None, _with_router_bypass_record(context, metadata)


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
    except Exception as exc:
        # IRON_PATH_2_PHASE_4: RuntimeEnforcer failures are router precheck
        # denials with receipts; BYPASS_RECORDED remains metadata only.
        return _deny_router_precheck(
            domain=domain,
            action=action,
            context=context,
            failure_source="runtime_enforcer",
            label="RuntimeEnforcer",
            exc=exc,
        )

    # 3. State Register — inject temporal context for anti-gaslighting checks.
    try:
        sr = get_state_register()
        temporal = sr.get_temporal_context()
        context = {**context, "_temporal": temporal}
    except Exception as exc:
        # IRON_PATH_2_PHASE_4: StateRegister failures block protected or
        # mutating work and degrade only explicit low-risk read-only diagnostics.
        try:
            can_degrade = _is_explicit_low_risk_read_only_diagnostic(
                action,
                context,
            )
        except Exception as classify_exc:
            return _deny_router_precheck(
                domain=domain,
                action=action,
                context=context,
                failure_source="state_register",
                label="StateRegister",
                exc=classify_exc,
                failed_components=["mutability_classifier"],
            )
        if not can_degrade:
            return _deny_router_precheck(
                domain=domain,
                action=action,
                context=context,
                failure_source="state_register",
                label="StateRegister",
                exc=exc,
            )
        recorded, reason, context = _record_degraded_router_precheck(
            domain=domain,
            action=action,
            context=context,
            failure_source="state_register",
            label="StateRegister",
            exc=exc,
        )
        if not recorded:
            return False, reason
        context = {
            **context,
            "_temporal": {
                "error": "StateRegister unavailable",
                "failure_source": "state_register",
            },
            "_temporal_unavailable": True,
        }

    # 3.5. Trust scoring + adversarial pattern detection.
    try:
        from app.core.tarl_operational_extensions import (
            TrustScoringEngine, AdversarialPatternRegistry,
        )
    except Exception as exc:
        failed_components = [
            "trust_scoring_engine",
            "adversarial_pattern_registry",
        ]
        try:
            can_degrade = _is_explicit_low_risk_read_only_diagnostic(
                action,
                context,
                require_no_payload=True,
            )
        except Exception as classify_exc:
            return _deny_router_precheck(
                domain=domain,
                action=action,
                context=context,
                failure_source="trust_adversarial_context",
                label="Trust/adversarial context",
                exc=classify_exc,
                failed_components=["mutability_classifier"],
            )
        if not can_degrade:
            return _deny_router_precheck(
                domain=domain,
                action=action,
                context=context,
                failure_source="trust_adversarial_context",
                label="Trust/adversarial context",
                exc=exc,
                failed_components=failed_components,
            )
        recorded, reason, context = _record_degraded_router_precheck(
            domain=domain,
            action=action,
            context=context,
            failure_source="trust_adversarial_context",
            label="Trust/adversarial context",
            exc=exc,
            failed_components=failed_components,
        )
        if not recorded:
            return False, reason
        context = {
            **context,
            "_trust_score_unavailable": True,
            "_adversarial_flags_unavailable": True,
        }
    else:
        _trust_score = None
        _adv_flags: list[dict[str, Any]] | None = None
        _failed_components: list[str] = []
        _first_failure: Exception | None = None

        try:
            _trust_score, _ = TrustScoringEngine().calculate_trust_score(
                context.get("user_id", "anonymous"),
                {
                    "behavioral": 0.7,
                    "security": 0.7,
                    "governance": 0.7,
                    "pattern": 0.7,
                },
            )
        except Exception as exc:
            _failed_components.append("trust_scoring_engine")
            _first_failure = exc

        try:
            _adv_flags = AdversarialPatternRegistry().detect_patterns(
                str(context.get("payload", ""))
            )
        except Exception as exc:
            _failed_components.append("adversarial_pattern_registry")
            if _first_failure is None:
                _first_failure = exc

        if _failed_components:
            assert _first_failure is not None
            try:
                can_degrade = _is_explicit_low_risk_read_only_diagnostic(
                    action,
                    context,
                    require_no_payload=True,
                )
            except Exception as classify_exc:
                return _deny_router_precheck(
                    domain=domain,
                    action=action,
                    context=context,
                    failure_source="trust_adversarial_context",
                    label="Trust/adversarial context",
                    exc=classify_exc,
                    failed_components=["mutability_classifier"],
                )
            if not can_degrade:
                return _deny_router_precheck(
                    domain=domain,
                    action=action,
                    context=context,
                    failure_source="trust_adversarial_context",
                    label="Trust/adversarial context",
                    exc=_first_failure,
                    failed_components=_failed_components,
                )
            recorded, reason, context = _record_degraded_router_precheck(
                domain=domain,
                action=action,
                context=context,
                failure_source="trust_adversarial_context",
                label="Trust/adversarial context",
                exc=_first_failure,
                failed_components=_failed_components,
            )
            if not recorded:
                return False, reason
            if "trust_scoring_engine" in _failed_components:
                context = {**context, "_trust_score_unavailable": True}
            else:
                context = {**context, "_trust_score": _trust_score}
            if "adversarial_pattern_registry" in _failed_components:
                context = {**context, "_adversarial_flags_unavailable": True}
            else:
                context = {**context, "_adversarial_flags": _adv_flags}
        else:
            context = {
                **context,
                "_trust_score": _trust_score,
                "_adversarial_flags": _adv_flags,
            }

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
