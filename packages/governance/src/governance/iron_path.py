"""The Iron Path: canonical execution pipeline for every governed action.

This module ties together the wave-1 kernel primitives
(:class:`kernel.threat_detection.ThreatDetectionEngine`,
:class:`kernel.tarl_bridge.TarlGate`) with the existing
:class:`governance.engine.GovernanceEngine` and the wave-3 risk
calibration (:class:`execution.risk.SafeAllowCalibration`) into a
single end-to-end pipeline. Every :class:`kernel.ActionRequest`
flowing through the system should pass through :class:`IronPath` so
that:

1. invariants are checked (BLOCKING short-circuits, existing
   :class:`GovernanceEngine` behaviour);
2. threat signals are recorded to the audit spine and converted to a
   :class:`kernel.Decision` if any non-trivial signal is present;
3. the action request is then submitted to :class:`GovernanceEngine`
   for the full governor vote;
4. (optional) risk calibration runs on the resulting ALLOW and can
   downgrade to ESCALATE or DENY;
5. (optional) if everything ALLOWs, the supplied executor is invoked
   and its output is captured on the result.

The pipeline is the "Iron Path" — there is exactly one way to evaluate
an action. Code that bypasses :class:`IronPath` (calling governors
directly, or producing a :class:`Decision` ad hoc) violates the
principal architecture and is rejected by the project's reviewer
checklist.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final, Protocol, cast, runtime_checkable

from kernel.tarl_bridge import TarlGate, TarlVerdictView
from kernel.threat_detection import ThreatAssessment, ThreatDetectionEngine

from governance.engine import GovernanceEngine
from governance.types import GovernanceResult
from kernel import (
    ActionRequest,
    Decision,
    EventSpine,
    InvariantSeverity,
    JsonValue,
    Outcome,
)

DEFAULT_POLICY_VERSION: Final[str] = "iron-path-v1"


# Reuse the existing ``Executor`` contract from execution.gate.
# The :class:`execution.gate.ExecutionGate` exposes this Protocol.
type Executor = Callable[[ActionRequest], JsonValue]


@runtime_checkable
class _RiskAssessmentLike(Protocol):
    """Minimal protocol for risk calibration results.

    The full :class:`execution.risk.RiskAssessment` satisfies this
    protocol structurally. By depending on a Protocol rather than the
    concrete class, the ``governance`` package preserves its
    downward-only dependency graph (no import from ``execution``).
    """

    risk_class: object
    risk_score: float
    harm_signals: Sequence[object]
    benign_signals: Sequence[object]


class RiskCalibrator(Protocol):
    """Pluggable risk-calibration stage for the Iron Path.

    Concrete implementation lives in ``execution.risk.SafeAllowCalibration``.
    Any object with a ``calibrate(request) -> _RiskAssessmentLike`` method
    satisfies this Protocol.
    """

    def calibrate(self, request: ActionRequest) -> _RiskAssessmentLike: ...


# Import-safe Decision construction: risk assessment classes may differ
# across packages, so we derive ``Decision`` from the protocol fields.
_RISK_TO_OUTCOME: Final[dict[str, Outcome]] = {
    "high_risk": Outcome.DENY,
    "ambiguous": Outcome.ESCALATE,
    "benign": Outcome.ALLOW,
}


def _risk_decision(assessment: _RiskAssessmentLike, policy_version: str) -> Decision | None:
    """Map a risk assessment to a governance Decision.

    Returns ``None`` when the assessment indicates ALLOW (no override).
    """
    risk_class_name = getattr(assessment.risk_class, "value", str(assessment.risk_class))
    outcome = _RISK_TO_OUTCOME.get(risk_class_name, Outcome.ALLOW)
    if outcome is Outcome.ALLOW:
        return None
    signals = assessment.harm_signals or assessment.benign_signals or ("risk assessment",)
    reason = f"{risk_class_name.upper()}: {','.join(str(s) for s in signals)}"
    return Decision(outcome=outcome, reasons=(reason,), policy_version=policy_version)


def threat_decision_from_assessment(
    assessment: ThreatAssessment,
    *,
    policy_version: str,
) -> Decision | None:
    """Convert a threat assessment to a governance :class:`Decision`.

    Returns ``None`` when the assessment is at ``INFO`` severity — i.e.
    no governance action is required. Returns a ``Decision`` for any
    ``WARNING`` / ``BLOCKING`` / ``CRITICAL`` assessment so the caller
    can short-circuit :class:`GovernanceEngine` for known-bad actions.
    """
    if assessment.severity is InvariantSeverity.INFO:
        return None
    return assessment.to_decision(policy_version=policy_version)


@dataclass(frozen=True)
class IronPathResult:
    """Outcome of running an :class:`ActionRequest` through the Iron Path."""

    request: ActionRequest
    threat_assessment: ThreatAssessment | None
    tarl_verdict: TarlVerdictView | None
    governance_result: GovernanceResult | None
    risk_assessment: _RiskAssessmentLike | None
    final_decision: Decision
    executor_output: JsonValue = None

    @property
    def outcome(self) -> Outcome:
        return self.final_decision.outcome

    @property
    def allowed(self) -> bool:
        return self.final_decision.outcome is Outcome.ALLOW


class IronPath:
    """The canonical action pipeline.

    Construct with an :class:`EventSpine`, a :class:`GovernanceEngine`,
    and (optionally) a :class:`ThreatDetectionEngine`,
    :class:`TarlGate`, :class:`RiskCalibrator`, and / or
    :class:`Executor`. Omitting the optional components degrades
    gracefully — the pipeline still runs invariants and governors, just
    without threat, TARL, risk, or execution augmentation.
    """

    def __init__(
        self,
        *,
        spine: EventSpine,
        governance: GovernanceEngine,
        threat_engine: ThreatDetectionEngine | None = None,
        tarl_gate: TarlGate | None = None,
        risk_calibrator: Any | None = None,
        executor: Executor | None = None,
        policy_version: str = DEFAULT_POLICY_VERSION,
    ) -> None:
        if not policy_version.strip():
            raise ValueError("policy_version must not be empty")
        self._spine = spine
        self._governance = governance
        self._threat = threat_engine
        self._tarl = tarl_gate
        self._risk = risk_calibrator
        self._executor = executor
        self._policy_version = policy_version

    @property
    def spine(self) -> EventSpine:
        return self._spine

    @property
    def governance(self) -> GovernanceEngine:
        return self._governance

    def run(
        self,
        request: ActionRequest,
        *,
        threat_session: str | None = None,
        threat_command: str | None = None,
        observed_behavior: Mapping[str, object] | None = None,
        state: Mapping[str, object] | None = None,
    ) -> IronPathResult:
        """Evaluate ``request`` through the Iron Path.

        ``threat_session`` / ``threat_command`` / ``observed_behavior``
        are only used when a threat engine is configured. Pass
        ``threat_command=None`` to skip threat analysis even if an
        engine is configured.
        """
        threat_assessment: ThreatAssessment | None = None
        if self._threat is not None and threat_session is not None and threat_command is not None:
            behavior: Mapping[str, object] = observed_behavior or {}
            threat_assessment = self._threat.analyze(
                session_id=threat_session,
                command=threat_command,
                observed_behavior=cast_observed_to_jsonvalue(behavior),
            )

        tarl_verdict: TarlVerdictView | None = None
        if self._tarl is not None:
            tarl_payload = _build_tarl_payload(request, threat_assessment)
            try:
                self._tarl.enforce(
                    execution_context=cast_context_to_jsonvalue(request),
                    verdict=tarl_payload,
                )
            except Exception as error:
                tarl_verdict = TarlVerdictView(
                    verdict="DENY",
                    reason=f"tarl enforcement: {type(error).__name__}",
                )
                decision = Decision(
                    outcome=Outcome.DENY,
                    reasons=(f"tarl: {error}",),
                    policy_version=self._policy_version,
                )
                return IronPathResult(
                    request=request,
                    threat_assessment=threat_assessment,
                    tarl_verdict=tarl_verdict,
                    governance_result=None,
                    risk_assessment=None,
                    final_decision=decision,
                )

            tarl_verdict = TarlVerdictView.from_payload(tarl_payload)

        threat_decision = (
            threat_decision_from_assessment(threat_assessment, policy_version=self._policy_version)
            if threat_assessment is not None
            else None
        )

        if threat_decision is not None and threat_decision.outcome is Outcome.DENY:
            governance_result: GovernanceResult | None = None
            return IronPathResult(
                request=request,
                threat_assessment=threat_assessment,
                tarl_verdict=tarl_verdict,
                governance_result=governance_result,
                risk_assessment=None,
                final_decision=threat_decision,
            )

        governance_result = self._governance.decide(request, state=state)
        base_decision = governance_result.decision

        # Risk calibration runs after governance. It can downgrade an
        # ALLOW to ESCALATE or DENY; it cannot upgrade DENY/ESCALATE to
        # ALLOW (fail-closed). If governance did not ALLOW, the
        # calibrator is not consulted.
        risk_assessment: _RiskAssessmentLike | None = None
        final_decision: Decision = base_decision
        executor_output: JsonValue = None

        if self._risk is not None and base_decision.outcome is Outcome.ALLOW:
            raw_assessment = self._risk.calibrate(request)
            calibrated: _RiskAssessmentLike | None = cast(
                "_RiskAssessmentLike | None", raw_assessment
            )
            if calibrated is not None:
                risk_assessment = calibrated
                risk_decision = _risk_decision(calibrated, self._policy_version)
                if risk_decision is not None:
                    final_decision = Decision(
                        outcome=risk_decision.outcome,
                        reasons=base_decision.reasons + risk_decision.reasons,
                        policy_version=self._policy_version,
                    )

        # Execution only happens when EVERYTHING ALLOWs.
        if final_decision.outcome is Outcome.ALLOW and self._executor is not None:
            try:
                executor_output = self._executor(request)
            except Exception as error:
                final_decision = Decision(
                    outcome=Outcome.DENY,
                    reasons=(*base_decision.reasons, f"executor failed: {type(error).__name__}"),
                    policy_version=self._policy_version,
                )

        return IronPathResult(
            request=request,
            threat_assessment=threat_assessment,
            tarl_verdict=tarl_verdict,
            governance_result=governance_result,
            risk_assessment=risk_assessment,
            final_decision=final_decision,
            executor_output=executor_output,
        )


def _build_tarl_payload(
    request: ActionRequest,
    threat_assessment: ThreatAssessment | None,
) -> dict[str, object]:
    """Build a TARL verdict-shaped payload for the optional TARL gate.

    The pipeline does not depend on a full TARL runtime; it derives a
    verdict from the request + threat signals so the gate can be exercised
    in tests and dry-runs. Real TARL integration (Stage pending — see
    LEGACY_GAP_INVENTORY §6) replaces this with a runtime query.
    """
    if threat_assessment is not None and threat_assessment.severity >= InvariantSeverity.BLOCKING:
        return {
            "verdict": "DENY",
            "reason": f"threat:{threat_assessment.severity.name}",
        }
    return {"verdict": "ALLOW", "reason": f"action:{request.operation}"}


def cast_context_to_jsonvalue(
    request: ActionRequest,
) -> dict[str, JsonValue]:
    """Return the action's context as a JSON-safe mapping for TARL payloads."""
    return cast(
        "dict[str, JsonValue]",
        {
            "action_id": request.action_id,
            "actor": request.actor,
            "operation": request.operation,
            "resource": request.resource,
        },
    )


def cast_observed_to_jsonvalue(
    behavior: Mapping[str, object],
) -> dict[str, JsonValue]:
    """Pass-through helper: the Iron Path threat engine accepts any JSON value.

    Kept as a named function so future tightening of the
    ``ThreatDetectionEngine.analyze`` signature is centralized. The cast
    acknowledges that callers may pass non-JSON-typed values; the engine
    must validate them at runtime.
    """
    return cast("dict[str, JsonValue]", dict(behavior))


__all__ = [
    "DEFAULT_POLICY_VERSION",
    "Executor",
    "IronPath",
    "IronPathResult",
    "RiskCalibrator",
    "threat_decision_from_assessment",
]
