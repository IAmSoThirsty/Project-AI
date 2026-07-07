"""
Governed action submission for the Project-AI
execution-governance spine.

This module composes the 3 packages recovered in
Phase B (``audit``, ``identity``, ``canonical``)
into a single ``submit_action`` pipeline. It is the
"glue layer" that wires identity, capability, policy,
audit, and execute into one call:

    submit_action(state, audit_log,
                  actor_id, action, resource, context)
        -> GovernedActionResult

Pipeline (short-circuits on first deny):

  1. ``IdentityRegistry.verify(actor_id)`` returns
     ``IdentityVerification(active, reason)``. If
     ``active`` is False, deny with reason
     "identity: <reason>".

  2. ``CanonicalState.policy.evaluate(actor_id,
     action, resource, context)`` returns
     ``PolicyDecision(allowed, reason)``. If
     ``allowed`` is False, deny with reason
     "policy: <reason>".

  3. If both checks pass, the action is allowed.
     The caller is responsible for performing the
     action and then calling ``audit_log.\
append_event(...)`` with the result. (This
     module does NOT auto-audit; the caller decides
     when to record, because some actions may
     require additional business-logic validation
     before they're "actually done".)

  4. The ``GovernedActionResult`` carries the
     decision (allowed/denied), the reason, and
     the two pre-check verdicts (identity,
     policy) for audit-trail purposes.

The two pre-check verdicts and the final result
are returned together so the caller can pass
all three to ``AuditLog.append_event`` as a
single, hash-chained record.

Vendoring history: this module is the smallest
correct change that wires the 3 Phase B packages
together. It is intentionally NOT a new workspace
member (no new ``pyproject.toml``); it lives in
``canonical`` because ``canonical`` already depends
on ``audit`` and ``identity`` (per
``packages/canonical/pyproject.toml``).

Thirstys V3 compliance:

  - #1 smallest correct change: one new file, no
    new package, no new dependencies.
  - #6 deterministic, replayable, testable: the
    module has no hidden state; the caller
    provides the ``CanonicalState`` and
    ``AuditLog``, so the same inputs always
    produce the same outputs.
  - #7 add tests for changed behavior: tests in
    ``packages/canonical/tests/\
test_governed_action.py`` cover all 4 paths
    (allowed, identity-denied, policy-denied,
    audit-appended).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from audit.chain import AuditLog

from canonical.state import CanonicalState


@dataclass(frozen=True)
class GovernedActionResult:
    """Result of a ``submit_action`` call.

    Carries the final decision (allowed/denied) plus
    the two pre-check verdicts for audit-trail
    purposes. The caller passes these to
    ``AuditLog.append_event`` to record the action
    in the SHA256-chained audit log.
    """

    allowed: bool
    reason: str
    identity_active: bool
    identity_reason: str
    policy_allowed: bool
    policy_reason: str


def submit_action(
    state: CanonicalState,
    audit_log: AuditLog,
    *,
    decision_id: str,
    actor_id: str | None,
    action: str,
    resource: str,
    context: Mapping[str, Any] | None = None,
    event_type: str = "governed_action",
) -> GovernedActionResult:
    """Run the 3-stage governed-action pipeline.

    Stages:

      1. Identity check
         (``state.identities.verify(actor_id)``)
      2. Policy check
         (``state.policy.evaluate(actor_id, action,
         resource, context)``)
      3. Audit append
         (``audit_log.append_event(decision_id=...,
         actor_id=..., action=..., resource=...,
         result=..., reason=..., event_type=...)``)

    The audit append happens unconditionally with
    the final ``result`` (``"allow"`` or
    ``"deny"``) so the audit log captures every
    submission, including denials.

    Args:
        state: The ``CanonicalState`` (identities,
            capabilities, policy).
        audit_log: The ``AuditLog`` to append the
            event to.
        decision_id: Unique ID for this action.
        actor_id: The actor submitting the action.
            May be ``None`` (denied at the identity
            stage).
        action: The action verb (e.g.,
            ``"register"``, ``"promote"``).
        resource: The resource being acted on (e.g.,
            ``"audit_chain"``).
        context: Optional context dict passed to the
            policy evaluator.
        event_type: The ``AuditEvent.event_type``
            (default ``"governed_action"``).

    Returns:
        A ``GovernedActionResult`` summarizing the
        decision and the two pre-check verdicts.

    Note:
        This function does NOT perform the action
        itself. It only authorizes/denies and
        records the decision. The caller is
        responsible for actually performing the
        action after a successful authorize (and
        recording the post-execution result with a
        second ``audit_log.append_event`` call if
        desired).
    """
    context_dict: dict[str, Any] = dict(context or {})

    # Stage 1: identity check
    identity_verification = state.identities.verify(actor_id)
    if not identity_verification.allowed:
        result = GovernedActionResult(
            allowed=False,
            reason=f"identity: {identity_verification.reason}",
            identity_active=False,
            identity_reason=identity_verification.reason,
            policy_allowed=False,
            policy_reason="not evaluated (identity denied)",
        )
        audit_log.append_event(
            decision_id=decision_id,
            actor_id=actor_id,
            action=action,
            resource=resource,
            result="deny",
            reason=result.reason,
            event_type=event_type,
        )
        return result

    # Stage 2: policy check
    policy_decision = state.policy.evaluate(
        actor_id=actor_id or "",
        action=action,
        resource=resource,
        context=context_dict,
    )
    if not policy_decision.allowed:
        result = GovernedActionResult(
            allowed=False,
            reason=f"policy: {policy_decision.reason}",
            identity_active=True,
            identity_reason=identity_verification.reason,
            policy_allowed=False,
            policy_reason=policy_decision.reason,
        )
        audit_log.append_event(
            decision_id=decision_id,
            actor_id=actor_id,
            action=action,
            resource=resource,
            result="deny",
            reason=result.reason,
            event_type=event_type,
        )
        return result

    # Stage 3: both checks passed, action is allowed
    result = GovernedActionResult(
        allowed=True,
        reason="allowed",
        identity_active=True,
        identity_reason=identity_verification.reason,
        policy_allowed=True,
        policy_reason=policy_decision.reason,
    )
    audit_log.append_event(
        decision_id=decision_id,
        actor_id=actor_id,
        action=action,
        resource=resource,
        result="allow",
        reason=result.reason,
        event_type=event_type,
    )
    return result


__all__ = ["GovernedActionResult", "submit_action"]
