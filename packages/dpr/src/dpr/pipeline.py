"""
DeliberationEngine — Phase 3.

Phase 3 core invariant:

  COUNTER_PROPOSE may only return if the alternative action independently
  satisfies the same governance burden required of an ALLOW path, except
  that its terminal decision remains COUNTER_PROPOSE rather than ALLOW.

Adds to Phase 2:
  - _authority_status_for_action(): the single TrustRoot-verified
    authorization path, used for BOTH the primary action and every
    candidate alternative. AuthorityChain.claims_to_cover() (renamed from
    `covers`) is never used for authorization; it is unverified by design.
  - _evaluate_candidate_alternative(): replaces _find_viable_alternative().
    Runs authority, capability, policy, evidence, uncertainty, temporal
    hold, proportionality, and reversibility checks against the candidate,
    and returns a CandidateEvaluation — not just a name. High-severity /
    low-reversibility candidates are never counter-proposed; they would
    need to escalate, so they are rejected as alternatives outright.
  - Grant fingerprinting (matched_grant_hash / matched_alternative_grant_hash)
    on every Decision, replacing the too-weak grantor-name-only
    authority_used field as the sole authority record.
  - policy_bundle_hash + a policy-source-integrity gate: if
    ctx.policies hashes differently from the policies the engine was
    actually constructed with, that is a governance-integrity failure
    (POLICY_SOURCE_INTEGRITY), not a normal input variation, and the
    engine halts before evaluating anything.
  - candidate_evaluations recorded and audited on every decision that
    considered any alternatives, whether or not one was viable.
"""

from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import Sequence
from typing import cast

from .audit import AuditChain, Signer
from .models import (
    ActionRiskProfile,
    AuthorityGrant,
    CandidateEvaluation,
    Decision,
    DecisionType,
    DeliberationContext,
    FailureMode,
    Policy,
    RiskAssessment,
    new_decision_id,
)
from .policy import PolicyEngine, hash_policy_bundle
from .trust import EXPIRED, FORGERY_STATUSES, VALID, TrustRoot, grant_hash

UNCERTAINTY_AMBIGUITY_THRESHOLD = 0.7
HIGH_RISK_SEVERITY_THRESHOLD = 0.6
LOW_REVERSIBILITY_THRESHOLD = 0.2
ESCALATION_LOOP_LIMIT = 3
DEFERRAL_LOOP_LIMIT = 3
DELAY_LOOP_LIMIT = 3
OBEDIENCE_COLLAPSE_RISK_THRESHOLD = 0.3


class DeliberationEngine:
    def __init__(
        self, signer: Signer, policies: Sequence[Policy], trust_root: TrustRoot | None = None
    ) -> None:
        self.audit_chain = AuditChain(signer)
        self.policy_engine = PolicyEngine(policies)
        self.policy_bundle_hash = hash_policy_bundle(policies)
        self.trust_root = trust_root if trust_root is not None else TrustRoot()
        self._escalation_counts: defaultdict[str, int] = defaultdict(int)
        self._deferral_counts: defaultdict[str, int] = defaultdict(int)
        self._delay_counts: defaultdict[str, int] = defaultdict(int)

    # ------------------------------------------------------------------
    def decide(self, ctx: DeliberationContext) -> Decision:
        steps = []
        reasons = []
        flags = []
        policies_used: list[str] = []
        candidate_evaluations: list[dict[str, object]] = []
        raw_now = ctx.temporal_state.get("now")
        t = float(raw_now) if isinstance(raw_now, (int, float)) else time.time()

        # Step 0 (Phase 3): policy-source integrity.
        steps.append("verify_policy_source_integrity")
        if ctx.policies:
            ctx_policy_hash = hash_policy_bundle(ctx.policies)
            if ctx_policy_hash != self.policy_bundle_hash:
                flags.append(FailureMode.POLICY_SOURCE_INTEGRITY.value)
                return self._finalize(
                    ctx,
                    DecisionType.SAFE_HALT,
                    [
                        "Context-supplied policy set does not match the policy set this "
                        "engine was constructed with — refusing to evaluate against an "
                        "ambiguous policy source"
                    ],
                    flags,
                    steps,
                )

        # Step 1: verify identity
        steps.append("verify_identity")
        if not ctx.actor.verified:
            return self._finalize(
                ctx,
                DecisionType.REFUSE,
                ["Identity not verified — refusing by default"],
                flags,
                steps,
            )

        # Step 2: verify authority — cryptographically, against the trust root.
        steps.append("verify_authority")
        auth_status, matched_grant = self._authority_status_for_action(
            ctx, ctx.action.name, t, check_identity_drift=True
        )
        matched_grant_hash = grant_hash(matched_grant) if matched_grant is not None else None

        if auth_status == "no_grant_for_action":
            return self._finalize(
                ctx,
                DecisionType.REFUSE,
                [f"No authority grant in the chain covers action '{ctx.action.name}' at all"],
                flags,
                steps,
            )

        if auth_status == "identity_drift":
            flags.append(FailureMode.IDENTITY_DRIFT.value)
            return self._finalize(
                ctx,
                DecisionType.SAFE_HALT,
                [
                    f"Action '{ctx.action.name}' is covered by the authority chain, but not for "
                    f"actor '{ctx.actor.actor_id}' — the chain grants it to a different grantee. "
                    f"Identity drift / impersonation attempt detected, halting"
                ],
                flags,
                steps,
            )

        if auth_status in FORGERY_STATUSES:
            flags.append(FailureMode.AUTHORITY_FORGERY.value)
            return self._finalize(
                ctx,
                DecisionType.SAFE_HALT,
                [
                    f"Authority grant for '{ctx.action.name}' failed cryptographic verification "
                    f"({auth_status}) — treating as forged, halting rather than refusing quietly"
                ],
                flags,
                steps,
            )

        if auth_status == EXPIRED:
            return self._finalize(
                ctx,
                DecisionType.REFUSE,
                [f"Authority grant for '{ctx.action.name}' has expired"],
                flags,
                steps,
            )

        # auth_status == VALID: matched_grant is real and verified. Proceed.

        # Step 3: verify capabilities
        steps.append("verify_capabilities")
        cap_names = {c.name for c in ctx.capabilities if c.granted_to == ctx.actor.actor_id}
        if ctx.action.name not in cap_names:
            flags.append(FailureMode.CAPABILITY_ESCALATION.value)
            alt_eval = self._select_viable_alternative(ctx, t, candidate_evaluations)
            if alt_eval is not None:
                return self._finalize(
                    ctx,
                    DecisionType.COUNTER_PROPOSE,
                    [
                        f"Actor '{ctx.actor.actor_id}' lacks granted capability for "
                        f"'{ctx.action.name}'",
                        f"Governed alternative available and independently validated: "
                        f"'{alt_eval.candidate_action}'",
                    ],
                    flags,
                    steps,
                    policies_used=list(alt_eval.policy_reasons),
                    alternative_actions=[alt_eval.candidate_action],
                    matched_grant_hash=matched_grant_hash,
                    matched_alternative_grant_hash=alt_eval.matched_grant_hash,
                    candidate_evaluations=candidate_evaluations,
                )
            return self._finalize(
                ctx,
                DecisionType.REFUSE,
                [
                    f"Actor '{ctx.actor.actor_id}' lacks granted capability for '{ctx.action.name}', "
                    f"and no viable governed alternative was found"
                ],
                flags,
                steps,
                matched_grant_hash=matched_grant_hash,
                candidate_evaluations=candidate_evaluations,
            )

        # Step 4: verify evidence
        steps.append("verify_evidence")
        unverified = [e for e in ctx.evidence if not e.verified]
        if unverified and ctx.risk.severity >= HIGH_RISK_SEVERITY_THRESHOLD:
            flags.append(FailureMode.CONTEXT_POISONING.value)
            reasons.append(
                f"{len(unverified)} unverified evidence item(s) present under high-severity "
                f"action (severity={ctx.risk.severity:.2f}) — treating as poisoned context risk"
            )

        # Step 5: ambiguity
        steps.append("identify_ambiguity")
        ambiguous = ctx.uncertainty >= UNCERTAINTY_AMBIGUITY_THRESHOLD
        if ambiguous:
            reasons.append(f"High uncertainty ({ctx.uncertainty:.2f}) identified")

        # Step 6: competing obligations
        steps.append("identify_competing_obligations")

        # Step 7: uncertainty
        steps.append("identify_uncertainty")

        # Step 7b: temporal hold check -> DELAY branch.
        steps.append("evaluate_temporal_hold")
        active_holds = [
            c
            for c in ctx.constraints
            if c.temporal_hold_until is not None and c.temporal_hold_until > t
        ]
        if active_holds:
            delay_key = f"{ctx.actor.actor_id}:{ctx.action.name}"
            self._delay_counts[delay_key] += 1
            if self._delay_counts[delay_key] > DELAY_LOOP_LIMIT:
                flags.append(FailureMode.INFINITE_DEFERRAL.value)
                return self._finalize(
                    ctx,
                    DecisionType.SAFE_HALT,
                    [
                        f"Delay loop limit ({DELAY_LOOP_LIMIT}) exceeded for this actor/action "
                        f"pair — refusing to delay indefinitely"
                    ],
                    flags,
                    steps,
                    matched_grant_hash=matched_grant_hash,
                )
            hold_names = ", ".join(c.name for c in active_holds)
            soonest = min(
                c.temporal_hold_until for c in active_holds if c.temporal_hold_until is not None
            )
            return self._finalize(
                ctx,
                DecisionType.DELAY,
                [
                    f"Action otherwise valid but under temporal hold: {hold_names}",
                    f"Earliest retry time: {soonest:.0f} (unix ts)",
                ],
                flags,
                steps,
                matched_grant_hash=matched_grant_hash,
            )

        # Steps 8-10: generate / evaluate / reject actions
        steps.append("generate_possible_actions")
        steps.append("evaluate_actions")
        steps.append("reject_invalid_actions")
        allowed, policies_used, policy_reasons = self.policy_engine.evaluate(ctx.action.name)
        reasons.extend(policy_reasons)
        if not allowed:
            alt_eval = self._select_viable_alternative(ctx, t, candidate_evaluations)
            if alt_eval is not None:
                return self._finalize(
                    ctx,
                    DecisionType.COUNTER_PROPOSE,
                    [
                        *reasons,
                        f"Governed alternative available and independently validated: "
                        f"'{alt_eval.candidate_action}'",
                    ],
                    flags,
                    steps,
                    policies_used=policies_used,
                    alternative_actions=[alt_eval.candidate_action],
                    matched_grant_hash=matched_grant_hash,
                    matched_alternative_grant_hash=alt_eval.matched_grant_hash,
                    candidate_evaluations=candidate_evaluations,
                )
            return self._finalize(
                ctx,
                DecisionType.REFUSE,
                reasons,
                flags,
                steps,
                policies_used,
                matched_grant_hash=matched_grant_hash,
                candidate_evaluations=candidate_evaluations,
            )

        # Step 11: generate reasons
        steps.append("generate_reasons")

        # Step 12: proportionality
        steps.append("evaluate_proportionality")
        proportional = ctx.risk.severity <= 0.3 or ctx.risk.severity <= (1 - ctx.uncertainty)
        if not proportional:
            reasons.append(
                f"Risk severity ({ctx.risk.severity:.2f}) disproportionate to available "
                f"certainty ({1 - ctx.uncertainty:.2f})"
            )

        # Step 13: reversibility -> may force ESCALATE
        steps.append("evaluate_reversibility")
        if (
            ctx.risk.severity >= HIGH_RISK_SEVERITY_THRESHOLD
            and ctx.risk.reversibility <= LOW_REVERSIBILITY_THRESHOLD
        ):
            steps.append("evaluate_continuity")
            steps.append("evaluate_accountability")
            escalate_key = f"{ctx.actor.actor_id}:{ctx.action.name}"
            self._escalation_counts[escalate_key] += 1
            if self._escalation_counts[escalate_key] > ESCALATION_LOOP_LIMIT:
                flags.append(FailureMode.INFINITE_ESCALATION.value)
                return self._finalize(
                    ctx,
                    DecisionType.SAFE_HALT,
                    [
                        f"Escalation loop limit ({ESCALATION_LOOP_LIMIT}) exceeded for this "
                        f"actor/action pair — halting instead of re-escalating indefinitely"
                    ],
                    flags,
                    steps,
                    policies_used,
                    matched_grant_hash=matched_grant_hash,
                )
            return self._finalize(
                ctx,
                DecisionType.ESCALATE,
                [
                    *reasons,
                    "High severity + low reversibility — escalating to human/higher authority",
                ],
                flags,
                steps,
                policies_used,
                matched_grant_hash=matched_grant_hash,
            )

        # Step 14-15: continuity / accountability
        steps.append("evaluate_continuity")
        steps.append("evaluate_accountability")

        # Ambiguity gate -> REQUEST_INFORMATION, with deferral-loop guard
        if ambiguous:
            defer_key = f"{ctx.actor.actor_id}:{ctx.action.name}"
            self._deferral_counts[defer_key] += 1
            if self._deferral_counts[defer_key] > DEFERRAL_LOOP_LIMIT:
                flags.append(FailureMode.INFINITE_DEFERRAL.value)
                return self._finalize(
                    ctx,
                    DecisionType.SAFE_HALT,
                    [
                        f"Deferral loop limit ({DEFERRAL_LOOP_LIMIT}) exceeded — refusing to "
                        f"defer indefinitely without new evidence"
                    ],
                    flags,
                    steps,
                    policies_used,
                    matched_grant_hash=matched_grant_hash,
                )
            return self._finalize(
                ctx,
                DecisionType.REQUEST_INFORMATION,
                [
                    *reasons,
                    "Uncertainty too high to decide — requesting information before proceeding",
                ],
                flags,
                steps,
                policies_used,
                matched_grant_hash=matched_grant_hash,
            )

        # Step 16: produce governed decision
        steps.append("produce_decision")
        confidence = round(max(0.0, 1 - ctx.uncertainty), 3)

        if not reasons and ctx.risk.severity > OBEDIENCE_COLLAPSE_RISK_THRESHOLD:
            flags.append(FailureMode.OBEDIENCE_COLLAPSE.value)
            return self._finalize(
                ctx,
                DecisionType.SAFE_HALT,
                [
                    "Refusing to ALLOW a risk-bearing action with zero accumulated justification "
                    "— obedience-collapse guard triggered"
                ],
                flags,
                steps,
                policies_used,
                confidence=confidence,
                matched_grant_hash=matched_grant_hash,
            )

        if not reasons:
            reasons.append("All governance checks passed with no outstanding objections")

        return self._finalize(
            ctx,
            DecisionType.ALLOW,
            reasons,
            flags,
            steps,
            policies_used,
            confidence=confidence,
            matched_grant_hash=matched_grant_hash,
        )

    # ------------------------------------------------------------------
    def _authority_status_for_action(
        self,
        ctx: DeliberationContext,
        action_name: str,
        at_time: float,
        check_identity_drift: bool = False,
    ) -> tuple[str, AuthorityGrant | None]:
        """
        The ONLY TrustRoot-verified authorization path in this engine. Used
        for both the primary action and every candidate alternative.

        Returns (status, matched_grant):
          "no_grant_for_action"  — nothing in the chain covers this action at all
          "identity_drift"       — covered, but for a different grantee
                                    (only reported if check_identity_drift=True)
          <FORGERY_STATUS>       — covered for this actor, but doesn't verify
          EXPIRED                — covered for this actor, verified, expired
          VALID                  — covered for this actor and cryptographically verified
        """
        covering_any = [g for g in ctx.authority.grants if "*" in g.scope or action_name in g.scope]
        if not covering_any:
            return "no_grant_for_action", None

        covering_this_actor = [g for g in covering_any if g.grantee == ctx.actor.actor_id]
        if not covering_this_actor:
            return ("identity_drift" if check_identity_drift else "no_grant_for_action"), None

        # covering_this_actor is non-empty here, so the loop always sets a
        # status; "" is a sentinel no verify_grant() result can collide with.
        best_status = ""
        best_grant: AuthorityGrant | None = None
        for g in covering_this_actor:
            status = self.trust_root.verify_grant(g, at_time)
            if status == VALID:
                return VALID, g
            if not best_status or (best_status == EXPIRED and status in FORGERY_STATUSES):
                best_status = status
                best_grant = g
        return best_status, best_grant

    def _evaluate_candidate_alternative(
        self,
        ctx: DeliberationContext,
        candidate_action: str,
        at_time: float,
    ) -> CandidateEvaluation:
        """
        Phase 3 core method + Phase 4 enhancement.

        Phase 3: Runs candidate through same governance burden as ALLOW.

        Phase 4: Risk assessment now per-action when available.
          - If ctx.risk_by_action[candidate_action] exists, use it for risk checks
          - Otherwise fall back to ctx.risk (backward compatible)
          - Candidates with high-severity + low-reversibility profiles are
            rejected outright (they need ESCALATE, not COUNTER_PROPOSE)
        """
        reasons = []
        rejected_flags = []

        # Get the risk profile for this specific action (Phase 4)
        # Prefer per-action profile; fall back to shared context risk
        candidate_risk: ActionRiskProfile | RiskAssessment
        if candidate_action in ctx.risk_by_action:
            candidate_risk = ctx.risk_by_action[candidate_action]
            reasons.append(
                f"Using per-action risk profile for '{candidate_action}': "
                f"severity={candidate_risk.severity:.2f}, "
                f"reversibility={candidate_risk.reversibility:.2f}"
            )
        else:
            # Phase 3 backward compat: use shared context risk
            candidate_risk = ctx.risk
            reasons.append(
                f"No per-action risk profile for '{candidate_action}'; "
                f"using shared context risk: "
                f"severity={candidate_risk.severity:.2f}, "
                f"reversibility={candidate_risk.reversibility:.2f}"
            )

        auth_status, matched_grant = self._authority_status_for_action(
            ctx, candidate_action, at_time, check_identity_drift=False
        )
        matched_grant_hash = grant_hash(matched_grant) if matched_grant is not None else None
        if auth_status != VALID:
            reasons.append(f"Authority status for '{candidate_action}': {auth_status}")
            if auth_status in FORGERY_STATUSES:
                rejected_flags.append(FailureMode.AUTHORITY_FORGERY.value)

        cap_names = {c.name for c in ctx.capabilities if c.granted_to == ctx.actor.actor_id}
        capability_held = candidate_action in cap_names
        if not capability_held:
            reasons.append(f"Actor does not hold capability '{candidate_action}'")
            rejected_flags.append(FailureMode.CAPABILITY_ESCALATION.value)

        policy_allowed, policy_used, policy_reasons = self.policy_engine.evaluate(candidate_action)
        reasons.extend(policy_reasons)
        if not policy_allowed:
            rejected_flags.append("POLICY_DENIED")

        # Phase 4: Risk-based evidence check (use candidate_risk, not ctx.risk)
        unverified = [e for e in ctx.evidence if not e.verified]
        evidence_ok = not (unverified and candidate_risk.severity >= HIGH_RISK_SEVERITY_THRESHOLD)
        if not evidence_ok:
            reasons.append(
                f"{len(unverified)} unverified evidence item(s) under high-severity risk "
                f"— alternative also subject to context-poisoning risk"
            )
            rejected_flags.append(FailureMode.CONTEXT_POISONING.value)

        uncertainty_ok = ctx.uncertainty < UNCERTAINTY_AMBIGUITY_THRESHOLD
        if not uncertainty_ok:
            reasons.append(f"Uncertainty ({ctx.uncertainty:.2f}) at or above ambiguity threshold")

        active_holds = [
            c
            for c in ctx.constraints
            if c.temporal_hold_until is not None and c.temporal_hold_until > at_time
        ]
        temporal_hold_ok = not active_holds
        if not temporal_hold_ok:
            reasons.append(
                f"Active temporal hold(s) also block the alternative: "
                f"{', '.join(c.name for c in active_holds)}"
            )

        # Phase 4: Proportionality check using candidate_risk
        proportionality_ok = candidate_risk.severity <= 0.3 or candidate_risk.severity <= (
            1 - ctx.uncertainty
        )
        if not proportionality_ok:
            reasons.append(
                f"Candidate risk severity ({candidate_risk.severity:.2f}) disproportionate to available certainty"
            )

        # Phase 4: Reversibility check using candidate_risk
        # HIGH SEVERITY + LOW REVERSIBILITY → requires ESCALATE, never COUNTER_PROPOSE
        high_severity_low_reversibility = (
            candidate_risk.severity >= HIGH_RISK_SEVERITY_THRESHOLD
            and candidate_risk.reversibility <= LOW_REVERSIBILITY_THRESHOLD
        )
        reversibility_ok = not high_severity_low_reversibility
        if not reversibility_ok:
            reasons.append(
                f"Candidate risk profile: severity={candidate_risk.severity:.2f} "
                f"(>= {HIGH_RISK_SEVERITY_THRESHOLD}), "
                f"reversibility={candidate_risk.reversibility:.2f} "
                f"(< {LOW_REVERSIBILITY_THRESHOLD}) → requires ESCALATE, not COUNTER_PROPOSE. "
                f"Cannot be offered as an alternative."
            )

        viable = (
            auth_status == VALID
            and capability_held
            and policy_allowed
            and evidence_ok
            and uncertainty_ok
            and temporal_hold_ok
            and proportionality_ok
            and reversibility_ok
        )

        if viable:
            reasons.append(
                f"'{candidate_action}' independently satisfies the full governance "
                f"burden required of ALLOW"
            )

        return CandidateEvaluation(
            candidate_action=candidate_action,
            authority_status=auth_status,
            matched_grant_hash=matched_grant_hash,
            capability_held=capability_held,
            policy_allowed=policy_allowed,
            policy_reasons=policy_used,
            evidence_ok=evidence_ok,
            uncertainty_ok=uncertainty_ok,
            temporal_hold_ok=temporal_hold_ok,
            proportionality_ok=proportionality_ok,
            reversibility_ok=reversibility_ok,
            risk_severity=candidate_risk.severity,  # Phase 4: use candidate_risk, not ctx.risk
            risk_reversibility=candidate_risk.reversibility,  # Phase 4
            reasons=reasons,
            rejected_failure_modes=rejected_flags,
            viable=viable,
        )

    def _select_viable_alternative(
        self,
        ctx: DeliberationContext,
        at_time: float,
        out_evaluations: list[dict[str, object]],
    ) -> CandidateEvaluation | None:
        """
        Evaluates every candidate_alternatives entry (skipping the primary
        action itself), appends each CandidateEvaluation's serialized form
        to out_evaluations (non-viable candidates are audited too), and
        returns the first viable CandidateEvaluation or None.
        """
        chosen: CandidateEvaluation | None = None
        for alt_name in ctx.candidate_alternatives:
            if alt_name == ctx.action.name:
                continue
            evaluation = self._evaluate_candidate_alternative(ctx, alt_name, at_time)
            out_evaluations.append(evaluation.to_serializable())
            if chosen is None and evaluation.viable:
                chosen = evaluation
        return chosen

    # ------------------------------------------------------------------
    def _finalize(
        self,
        ctx: DeliberationContext,
        decision_type: DecisionType,
        reasons: list[str],
        flags: list[str],
        steps: list[str],
        policies_used: list[str] | None = None,
        confidence: float | None = None,
        alternative_actions: list[str] | None = None,
        matched_grant_hash: str | None = None,
        matched_alternative_grant_hash: str | None = None,
        candidate_evaluations: list[dict[str, object]] | None = None,
    ) -> Decision:
        # GOVERNANCE_BYPASS invariant. A policy-source-integrity halt occurs
        # before verify_identity/verify_authority by design (step 0) — that
        # is an earlier fail-closed gate, not a bypass, so it is exempted.
        required_min = {"verify_identity", "verify_authority"}
        is_policy_source_halt = FailureMode.POLICY_SOURCE_INTEGRITY.value in flags
        if not is_policy_source_halt and not required_min.issubset(set(steps)):
            flags = [*list(flags), FailureMode.GOVERNANCE_BYPASS.value]

        # REASON_FABRICATION invariant: every decision must carry >=1 reason.
        if not reasons:
            flags = [*list(flags), FailureMode.REASON_FABRICATION.value]
            reasons = ["No reasons were generated — this is itself a governance failure"]
            decision_type = DecisionType.SAFE_HALT

        d = Decision(
            decision_id=new_decision_id(),
            decision=decision_type,
            reasons=reasons,
            evidence_used=[e.source for e in ctx.evidence],
            policies_used=policies_used or [],
            authority_used=",".join(sorted({g.grantor for g in ctx.authority.grants})),
            constraints=[c.name for c in ctx.constraints],
            competing_values=[c.description for c in ctx.commitments if c.binding],
            risk_analysis={"severity": ctx.risk.severity, "reversibility": ctx.risk.reversibility},
            confidence=confidence
            if confidence is not None
            else round(max(0.0, 1 - ctx.uncertainty), 3),
            remaining_uncertainty=ctx.uncertainty,
            alternative_actions=alternative_actions or [],
            failure_risks=list(flags),
            timestamp=time.time(),
            steps_executed=steps,
            flagged_failure_modes=list(flags),
            matched_grant_hash=matched_grant_hash,
            matched_alternative_grant_hash=matched_alternative_grant_hash,
            policy_bundle_hash=self.policy_bundle_hash,
            candidate_evaluations=candidate_evaluations or [],
        )
        entry = self.audit_chain.append(d.to_serializable())
        # append() sets these three keys as str on every entry it returns.
        d.audit_hash = cast(str, entry["audit_hash"])
        d.signature = cast(str, entry["signature"])
        d.prev_hash = cast(str, entry["prev_hash"])
        return d
