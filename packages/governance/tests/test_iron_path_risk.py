"""Tests for Iron Path with the wave-3 risk calibration and executor stages."""

from __future__ import annotations

from collections.abc import Mapping

from kernel.threat_detection import ThreatDetectionEngine

from execution import (
    LexicalRiskClassifier,
    RiskClass,
    SafeAllowCalibration,
)
from governance import (
    DEFAULT_POLICY_VERSION,
    GovernanceEngine,
    IronPath,
    Rule,
    RuleGovernor,
)
from kernel import (
    ActionRequest,
    EventSpine,
    InvariantEngine,
    JsonValue,
    Outcome,
    TrustedClock,
)


def request(operation: str = "write", resource: str = "record:1") -> ActionRequest:
    return ActionRequest("a-iron-3", "operator", operation, resource)


def governance(outcome: Outcome = Outcome.ALLOW) -> GovernanceEngine:
    rules: tuple[Rule, ...] = ()
    if outcome is not Outcome.ALLOW:
        rules = (Rule("decision", lambda _r, _s: False, outcome, "policy decision"),)
    return GovernanceEngine(policy_version="v1", governors=(RuleGovernor("primary", rules),))


def test_iron_path_accepts_optional_risk_calibrator() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())
    cal = SafeAllowCalibration(spine, classifier=LexicalRiskClassifier())
    path = IronPath(
        spine=spine,
        governance=governance(Outcome.ALLOW),
        risk_calibrator=cal,
    )
    result = path.run(request())
    assert result.outcome is Outcome.ALLOW
    assert result.risk_assessment is not None
    assert result.risk_assessment.risk_class is RiskClass.BENIGN


def test_iron_path_risk_calibration_downgrades_allow_to_escalate() -> None:
    """Risk calibrator returning AMBIGUOUS must downgrade ALLOW to ESCALATE."""
    spine = EventSpine(clock=lambda: TrustedClock().now())

    class AmbiguousClassifier:
        def score(self, request: ActionRequest) -> float:
            return 0.5  # AMBIGUOUS

    cal = SafeAllowCalibration(spine, classifier=AmbiguousClassifier())
    path = IronPath(
        spine=spine,
        governance=governance(Outcome.ALLOW),
        risk_calibrator=cal,
    )
    result = path.run(request())
    assert result.outcome is Outcome.ESCALATE
    assert result.risk_assessment is not None


def test_iron_path_risk_calibration_can_deny() -> None:
    """HIGH_RISK calibration must override ALLOW to DENY (fail-closed)."""
    spine = EventSpine(clock=lambda: TrustedClock().now())

    class HighRiskClassifier:
        def score(self, request: ActionRequest) -> float:
            return 1.0

    cal = SafeAllowCalibration(spine, classifier=HighRiskClassifier())
    path = IronPath(
        spine=spine,
        governance=governance(Outcome.ALLOW),
        risk_calibrator=cal,
    )
    result = path.run(request())
    assert result.outcome is Outcome.DENY
    assert result.risk_assessment is not None


def test_iron_path_risk_calibration_does_not_upgrade_deny() -> None:
    """Calibrator must not be consulted when governance already DENIED."""
    spine = EventSpine(clock=lambda: TrustedClock().now())

    consulted = []

    class TrackingClassifier:
        def score(self, request: ActionRequest) -> float:
            consulted.append(request)
            return 0.0

    cal = SafeAllowCalibration(spine, classifier=TrackingClassifier())
    path = IronPath(
        spine=spine,
        governance=governance(Outcome.DENY),
        risk_calibrator=cal,
    )
    result = path.run(request())
    assert result.outcome is Outcome.DENY
    assert consulted == []  # calibrator never called
    assert result.risk_assessment is None


def test_iron_path_executor_invoked_only_when_full_allow() -> None:
    """Executor runs only when everything ALLOWs."""
    spine = EventSpine(clock=lambda: TrustedClock().now())
    calls: list[ActionRequest] = []

    def executor(req: ActionRequest) -> JsonValue:
        calls.append(req)
        return {"changed": True, "id": req.action_id}

    path = IronPath(
        spine=spine,
        governance=governance(Outcome.ALLOW),
        executor=executor,
    )
    result = path.run(request())
    assert result.outcome is Outcome.ALLOW
    assert result.executor_output == {"changed": True, "id": "a-iron-3"}
    assert len(calls) == 1


def test_iron_path_executor_not_invoked_on_deny() -> None:
    """Executor must NOT run if governance DENIED."""
    spine = EventSpine(clock=lambda: TrustedClock().now())
    calls: list[ActionRequest] = []

    def executor(req: ActionRequest) -> JsonValue:
        calls.append(req)
        return {"called": True}

    path = IronPath(
        spine=spine,
        governance=governance(Outcome.DENY),
        executor=executor,
    )
    result = path.run(request())
    assert result.outcome is Outcome.DENY
    assert calls == []


def test_iron_path_executor_failure_becomes_deny() -> None:
    """An executor exception must produce a DENY Decision, not propagate."""
    spine = EventSpine(clock=lambda: TrustedClock().now())

    def bad_executor(req: ActionRequest) -> JsonValue:
        raise RuntimeError("upstream failed")

    path = IronPath(
        spine=spine,
        governance=governance(Outcome.ALLOW),
        executor=bad_executor,
    )
    result = path.run(request())
    assert result.outcome is Outcome.DENY
    assert any("executor failed" in r for r in result.final_decision.reasons)


def test_iron_path_executor_not_invoked_when_risk_denies() -> None:
    """HIGH_RISK calibration prevents executor invocation."""
    spine = EventSpine(clock=lambda: TrustedClock().now())

    class HighRiskClassifier:
        def score(self, request: ActionRequest) -> float:
            return 1.0

    cal = SafeAllowCalibration(spine, classifier=HighRiskClassifier())
    calls: list[ActionRequest] = []

    def executor(req: ActionRequest) -> JsonValue:
        calls.append(req)
        return {"called": True}

    path = IronPath(
        spine=spine,
        governance=governance(Outcome.ALLOW),
        risk_calibrator=cal,
        executor=executor,
    )
    result = path.run(request())
    assert result.outcome is Outcome.DENY
    assert calls == []  # executor never called because risk DENIED


def test_iron_path_full_pipeline_with_threat_risk_governance_executor() -> None:
    """End-to-end: threat + risk + governance + executor all composed."""
    from kernel import InvariantViolation

    spine = EventSpine(clock=lambda: TrustedClock().now())
    threat = ThreatDetectionEngine(spine)

    class SafeClassifier:
        def score(self, request: ActionRequest) -> float:
            return 0.05  # BENIGN

    cal = SafeAllowCalibration(spine, classifier=SafeClassifier())
    calls: list[ActionRequest] = []

    def executor(req: ActionRequest) -> JsonValue:
        calls.append(req)
        return {"id": req.action_id, "wrote": True}

    def noop_invariant(_r: ActionRequest, _s: Mapping[str, object]) -> InvariantViolation | None:
        return None

    gov = GovernanceEngine(
        policy_version="v1",
        governors=(RuleGovernor("ok", ()),),
        invariants=InvariantEngine((noop_invariant,)),
    )
    path = IronPath(
        spine=spine,
        governance=gov,
        threat_engine=threat,
        risk_calibrator=cal,
        executor=executor,
        policy_version="v1",
    )
    result = path.run(
        request(operation="read", resource="record:1"),
        threat_session="op",
        threat_command="ls",
    )
    assert result.outcome is Outcome.ALLOW
    assert result.threat_assessment is not None
    assert result.risk_assessment is not None
    assert result.governance_result is not None
    assert result.executor_output == {"id": "a-iron-3", "wrote": True}
    assert len(calls) == 1


def test_iron_path_full_policy_version_propagated() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())
    path = IronPath(
        spine=spine,
        governance=governance(Outcome.ALLOW),
        policy_version=DEFAULT_POLICY_VERSION,
    )
    result = path.run(request())
    # Governance uses its own policy_version ("v1"); IronPath's
    # policy_version is used for risk + executor-failure decisions.
    assert result.final_decision.policy_version == "v1"


# (Removed the unused RiskClassProxy class.)
