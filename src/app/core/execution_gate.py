"""execution_gate.py — Governance-verified entry point for all actions.

Upgraded with Upgrades 1, 4, 5, 7, 9, 10, 15, 17 wired into the pipeline.

Old bool-returning callers still work via compatibility shim:
    approved, result = gate.execute(domain, action, context, fn)

New pipeline:
    Request → SafeAllowCalibration → PolicyDecision → ContextBinding
            → ExecutionAuthorization → CapabilityToken → InvariantCheck
            → SemanticCollision → EvidenceBundle → Execute / Deny / ...
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from collections.abc import Callable
from typing import Any

from app.core.governance_kernel import get_kernel
from app.core.mutation_binding import MutationGovernanceBinding

logger = logging.getLogger(__name__)


class ExecutionGate:
    def __init__(self) -> None:
        self.kernel = get_kernel()

    def execute(
        self,
        domain: str,
        action: str,
        context: dict[str, Any],
        executor_fn: Callable[[dict[str, Any]], Any],
    ) -> tuple[bool, Any]:
        """Execute a governed action.

        Returns (True, result) on success, (False, reason_string) on denial.
        This signature is backward-compatible with all existing callers.
        """
        start_time = time.time()
        session_id = context.get("session_id", "")
        conversation_id = context.get("conversation_id", "")
        request_text = context.get("request_text", f"{domain}.{action}")

        request_hash = hashlib.sha256(request_text.encode()).hexdigest()[:32]
        context_hash = self._hash_context(context)
        degraded_read_only_allowed = self._degraded_read_only_allowed(action, domain, context)

        # --- Stage 0: Legacy kernel eval (preserves existing governance) ---
        approved, decision = self.kernel.evaluate_action(domain, action, context)
        policy_version = getattr(decision, "policy_version", "") or ""
        policy_hash_val = getattr(decision, "policy_hash", "") or ""

        if not approved:
            self._report_denial(context, domain, action, getattr(decision, "reason", str(decision)))
            outcome = self._determine_outcome_from_denial(context)
            self._emit_evidence_bundle(
                request_hash=request_hash, domain=domain, action=action,
                final_outcome=outcome, start_time=start_time,
                policy_version=policy_version, policy_hash=policy_hash_val,
            )
            return False, getattr(decision, "reason", decision)

        # --- Stage 1: Safe-Allow Calibration ---
        try:
            from app.core.safe_allow_calibration import SafeAllowCalibrationLayer
            cal = SafeAllowCalibrationLayer()
            cal_result = cal.evaluate(request_text, context, domain, action)
            risk_score = cal_result.risk_score
            if not cal_result.outcome.is_executable():
                self._emit_evidence_bundle(
                    request_hash=request_hash, domain=domain, action=action,
                    final_outcome=cal_result.outcome.value, start_time=start_time,
                    risk_score=risk_score,
                )
                return False, cal_result.reason
        except Exception as exc:
            if not degraded_read_only_allowed:
                self._emit_evidence_bundle(
                    request_hash=request_hash, domain=domain, action=action,
                    final_outcome="DENY", start_time=start_time,
                    policy_version=policy_version, policy_hash=policy_hash_val,
                )
                return False, f"SafeAllowCalibration failed closed: {exc}"
            logger.warning("SafeAllowCalibration degraded read-only continuation: %s", exc)
            risk_score = 0.0

        # --- Stage 2: PolicyDecision ---
        policy_decision = None
        try:
            from app.core.policy_decision import PolicyDecisionEvaluator
            pd_eval = PolicyDecisionEvaluator()
            policy_decision = pd_eval.evaluate(domain, action, context)
            policy_version = policy_decision.policy_version
            policy_hash_val = policy_decision.policy_hash
            if not policy_decision.permitted:
                self._emit_evidence_bundle(
                    request_hash=request_hash, domain=domain, action=action,
                    final_outcome=policy_decision.outcome.value, start_time=start_time,
                    policy_version=policy_version, policy_hash=policy_hash_val,
                )
                return False, policy_decision.reason
        except Exception as exc:
            if not degraded_read_only_allowed:
                self._emit_evidence_bundle(
                    request_hash=request_hash, domain=domain, action=action,
                    final_outcome="DENY", start_time=start_time,
                    risk_score=risk_score,
                    policy_version=policy_version, policy_hash=policy_hash_val,
                )
                return False, f"PolicyDecision failed closed: {exc}"
            logger.warning("PolicyDecision degraded read-only continuation: %s", exc)

        # --- Stage 3: ExecutionAuthorization ---
        exec_auth = None
        if policy_decision is not None:
            try:
                from app.core.execution_authorization import (
                    ExecutionAuthorizationEvaluator,
                )
                ea_eval = ExecutionAuthorizationEvaluator()
                exec_auth = ea_eval.evaluate(policy_decision, context, session_id)
                if not exec_auth.authorized:
                    self._emit_evidence_bundle(
                        request_hash=request_hash, domain=domain, action=action,
                        final_outcome=exec_auth.outcome.value, start_time=start_time,
                    )
                    return False, exec_auth.reason
            except Exception as exc:
                if not degraded_read_only_allowed:
                    self._emit_evidence_bundle(
                        request_hash=request_hash, domain=domain, action=action,
                        final_outcome="DENY", start_time=start_time,
                        risk_score=risk_score,
                        policy_version=policy_version, policy_hash=policy_hash_val,
                        policy_decision=policy_decision,
                    )
                    return False, f"ExecutionAuthorization failed closed: {exc}"
                logger.warning("ExecutionAuthorization degraded read-only continuation: %s", exc)

        if policy_decision is None and not degraded_read_only_allowed:
            self._emit_evidence_bundle(
                request_hash=request_hash, domain=domain, action=action,
                final_outcome="DENY", start_time=start_time,
                risk_score=risk_score,
                policy_version=policy_version, policy_hash=policy_hash_val,
            )
            return False, "PolicyDecision required for protected execution"

        # --- Stage 4: Binding verification (existing) ---
        binding = MutationGovernanceBinding.create(decision)
        if not binding.verify():
            return False, "Binding verification failed"

        # --- Stage 5: Sovereign policy-state binding (existing) ---
        try:
            import sys as _sys
            from pathlib import Path as _Path
            _repo_root = str(_Path(__file__).resolve().parents[4])
            if _repo_root not in _sys.path:
                _sys.path.insert(0, _repo_root)
            from governance.sovereign_runtime import SovereignRuntime
            _sr = SovereignRuntime()
            _policy_state = {"domain": domain, "action": action, "decision_id": getattr(decision, "decision_id", "")}
            _sov_binding = _sr.create_policy_state_binding(_policy_state, context)
            if not _sr.verify_policy_state_binding(_policy_state, context, _sov_binding):
                return False, "Sovereign policy binding verification failed"
            _sr.audit_log("execution_authorized", {"domain": domain, "action": action}, severity="INFO")
        except Exception as exc:
            if not degraded_read_only_allowed:
                return False, f"Sovereign policy binding failed closed: {exc}"
            logger.warning("Sovereign policy binding degraded read-only continuation: %s", exc)

        # --- Stage 6: Capability Token verification ---
        cap_token = context.get("_capability_token")
        token_required = self._requires_capability_token(action, context, degraded_read_only_allowed)
        if cap_token is None and token_required:
            self._emit_evidence_bundle(
                request_hash=request_hash, domain=domain, action=action,
                final_outcome="DENY", start_time=start_time,
                risk_score=risk_score,
                policy_version=policy_version, policy_hash=policy_hash_val,
                policy_decision=policy_decision, exec_auth=exec_auth,
            )
            return False, "CapabilityToken required for protected execution"
        if cap_token is not None:
            try:
                from app.core.capability_token import CapabilityTokenService
                cts = CapabilityTokenService()
                ok, reason = cts.verify(
                    cap_token, action,
                    required_scope=context.get("required_scope", []),
                    current_context_hash=context_hash,
                    current_policy_hash=policy_hash_val,
                )
                if not ok:
                    self._emit_evidence_bundle(
                        request_hash=request_hash, domain=domain, action=action,
                        final_outcome="DENY", start_time=start_time,
                    )
                    return False, f"CapabilityToken rejected: {reason}"
            except Exception as exc:
                self._emit_evidence_bundle(
                    request_hash=request_hash, domain=domain, action=action,
                    final_outcome="DENY", start_time=start_time,
                    risk_score=risk_score,
                    policy_version=policy_version, policy_hash=policy_hash_val,
                    policy_decision=policy_decision, exec_auth=exec_auth,
                )
                return False, f"CapabilityToken verification failed closed: {exc}"

        # --- Stage 7: Semantic collision check ---
        try:
            from app.core.semantic_collision import detect_semantic_collision
            shadow_text = context.get("shadow_text", request_text)
            execution_text = context.get("execution_text", request_text)
            col = detect_semantic_collision(request_text, shadow_text, execution_text)
            if col.collision_detected:
                self._emit_evidence_bundle(
                    request_hash=request_hash, domain=domain, action=action,
                    final_outcome="DENY", start_time=start_time,
                )
                return False, f"Semantic collision detected: {col.mismatch_plane}"
        except Exception as exc:
            if not degraded_read_only_allowed:
                return False, f"SemanticCollision check failed closed: {exc}"
            logger.warning("SemanticCollision degraded read-only continuation: %s", exc)

        # --- Stage 8: InvariantSeverity check ---
        inv_results: list[Any] = []
        try:
            from app.core.invariant_severity import get_severity_engine
            sev_engine = get_severity_engine()
            inv_results = sev_engine.evaluate_all(context)
            if sev_engine.should_block_execution(inv_results):
                max_sev = sev_engine.max_severity(inv_results)
                outcome_map = {
                    "HALT": "HALT",
                    "ESCALATE": "ESCALATE",
                    "BLOCK": "DENY",
                }
                outcome_str = outcome_map.get(max_sev.value, "DENY")
                self._emit_evidence_bundle(
                    request_hash=request_hash, domain=domain, action=action,
                    final_outcome=outcome_str, start_time=start_time,
                    invariant_results=inv_results,
                )
                return False, f"Invariant {max_sev.value}: execution blocked"
        except Exception as exc:
            if not degraded_read_only_allowed:
                return False, f"SeverityAwareInvariant check failed closed: {exc}"
            logger.warning("SeverityAwareInvariant degraded read-only continuation: %s", exc)

        # --- Execute ---
        result = executor_fn(context)

        # --- Stage 9: EvidenceBundle + Observability ---
        self._emit_evidence_bundle(
            request_hash=request_hash, domain=domain, action=action,
            final_outcome="ALLOW", start_time=start_time,
            risk_score=risk_score,
            policy_version=policy_version, policy_hash=policy_hash_val,
            policy_decision=policy_decision, exec_auth=exec_auth,
            invariant_results=inv_results, executor_result=result,
        )
        return True, result

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _hash_context(self, context: dict[str, Any]) -> str:
        try:
            return hashlib.sha256(
                json.dumps(context, sort_keys=True, default=str).encode()
            ).hexdigest()[:32]
        except Exception:
            return "unhashable"

    def _report_denial(self, context: dict[str, Any], domain: str, action: str, reason: str) -> None:
        try:
            from app.security.chimera_bridge import get_bridge
            get_bridge().report_governance_denial(
                ip=context.get("ip") or context.get("client_ip"),
                domain=domain, action=action, reason=reason,
            )
        except Exception:
            pass

    def _determine_outcome_from_denial(self, context: dict[str, Any]) -> str:
        if context.get("governance_degraded"):
            return "DEGRADED_READ_ONLY"
        if context.get("high_impact"):
            return "HUMAN_APPROVAL_REQUIRED"
        return "DENY"

    def _degraded_read_only_allowed(self, action: str, domain: str, context: dict[str, Any]) -> bool:
        if not context.get("governance_degraded"):
            return False
        try:
            from app.core.degraded_mode import get_degraded_mode_checker
            result = get_degraded_mode_checker().evaluate(action, domain=domain, context=context)
            return bool(result.allowed and result.is_read_only)
        except Exception as exc:
            logger.warning("DegradedModeChecker failed closed: %s", exc)
            return False

    def _requires_capability_token(
        self,
        action: str,
        context: dict[str, Any],
        degraded_read_only_allowed: bool,
    ) -> bool:
        if degraded_read_only_allowed:
            return False
        if "requires_capability_token" in context:
            return bool(context["requires_capability_token"])
        try:
            from app.core.degraded_mode import classify_action_mutability
            return classify_action_mutability(action, context)
        except Exception as exc:
            logger.warning("CapabilityToken mutability classification failed closed: %s", exc)
            return True

    def _emit_evidence_bundle(
        self,
        *,
        request_hash: str = "",
        domain: str = "",
        action: str = "",
        final_outcome: str = "DENY",
        start_time: float = 0.0,
        risk_score: float = 0.0,
        policy_version: str = "",
        policy_hash: str = "",
        policy_decision: Any = None,
        exec_auth: Any = None,
        invariant_results: list[Any] | None = None,
        executor_result: Any = None,
    ) -> None:
        try:
            from app.core.evidence_bundle import EvidenceBundleWriter
            from app.core.governance_observability import (
                build_observation,
                get_collector,
            )
            writer = EvidenceBundleWriter()
            bundle = writer.build(
                request_hash=request_hash,
                risk_score=risk_score,
                policy_decision=policy_decision,
                execution_authorization=exec_auth,
                invariant_results=invariant_results or [],
                executor_result=executor_result,
                final_outcome=final_outcome,
                policy_version=policy_version,
                policy_hash=policy_hash,
            )
            obs = build_observation(
                domain=domain, action=action,
                final_outcome=final_outcome,
                risk_score=risk_score,
                policy_version=policy_version,
                policy_hash=policy_hash,
                bundle_id=bundle.bundle_id,
                start_time=start_time,
                invariant_results=invariant_results or [],
            )
            get_collector().record(obs)
        except Exception as exc:
            logger.debug("EvidenceBundle/Observability emit failed: %s", exc)


_gate_instance: ExecutionGate | None = None


def get_execution_gate() -> ExecutionGate:
    global _gate_instance
    if _gate_instance is None:
        _gate_instance = ExecutionGate()
    return _gate_instance


__all__ = ["ExecutionGate", "get_execution_gate"]
