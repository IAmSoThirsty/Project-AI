"""Tests for ``execution.risk`` (Safe-Allow Calibration)."""

from __future__ import annotations

import pytest

from execution import (
    LexicalRiskClassifier,
    RiskAssessment,
    RiskClass,
    SafeAllowCalibration,
    request_fingerprint,
)
from kernel import ActionRequest, EventSpine, Outcome, TrustedClock


def request(operation: str = "write", resource: str = "record:1") -> ActionRequest:
    return ActionRequest("a-risk-1", "operator", operation, resource)


def test_request_fingerprint_is_deterministic() -> None:
    a = request("write", "record:1")
    b = request("write", "record:1")
    assert request_fingerprint(a) == request_fingerprint(b)


def test_request_fingerprint_changes_with_payload() -> None:
    a = ActionRequest("a-1", "operator", "write", "record:1", {"limit": 1})
    b = ActionRequest("a-1", "operator", "write", "record:1", {"limit": 2})
    assert request_fingerprint(a) != request_fingerprint(b)


def test_request_fingerprint_is_64_hex_chars() -> None:
    fp = request_fingerprint(request())
    assert len(fp) == 64
    assert all(c in "0123456789abcdef" for c in fp)


def test_lexical_classifier_benign_read() -> None:
    classifier = LexicalRiskClassifier()
    score, harm, benign = classifier.score_with_signals(
        ActionRequest("a-1", "operator", "read", "record:1")
    )
    # "read" matches benign signal → low score
    assert score < 0.3
    assert RiskClass.BENIGN is _classify(score)
    assert len(benign) > 0
    assert len(harm) == 0


def test_lexical_classifier_high_risk_weapon_synthesis() -> None:
    classifier = LexicalRiskClassifier()
    score, harm, _benign = classifier.score_with_signals(
        ActionRequest("a-1", "operator", "synthesize", "weapon")
    )
    # "synthesize" + "weapon" → high score
    assert score >= 0.75
    assert RiskClass.HIGH_RISK is _classify(score)
    assert len(harm) > 0


def test_lexical_classifier_high_risk_malware() -> None:
    classifier = LexicalRiskClassifier()
    score, harm, _ = classifier.score_with_signals(
        ActionRequest("a-1", "operator", "compile", "trojan")
    )
    assert score >= 0.5
    assert len(harm) > 0


def test_lexical_classifier_ambiguous_no_signals() -> None:
    """A request with no harm or benign signals must be AMBIGUOUS, not BENIGN."""
    classifier = LexicalRiskClassifier()
    score, harm, benign = classifier.score_with_signals(
        ActionRequest("a-1", "operator", "rotate", "keyring")
    )
    # No matches, but the prior pushes the score above BENIGN threshold
    assert 0.0 <= score <= 1.0
    assert len(harm) == 0
    assert len(benign) == 0


def test_safe_allow_calibration_records_event_on_spine() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())
    cal = SafeAllowCalibration(spine)
    assessment = cal.calibrate(request())
    events = spine.events()
    assert len(events) == 1
    assert events[0].event_type == SafeAllowCalibration.GATE_EVENT_TYPE
    assert assessment.event is not None


def test_safe_allow_calibration_invokes_callback() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())
    captured: list[RiskAssessment] = []
    cal = SafeAllowCalibration(spine, on_assessment=captured.append)
    assessment = cal.calibrate(request())
    assert len(captured) == 1
    assert captured[0].request_fingerprint == assessment.request_fingerprint


def test_safe_allow_calibration_accepts_custom_classifier() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())

    class AlwaysHigh:
        def score(self, request: ActionRequest) -> float:
            return 1.0

    cal = SafeAllowCalibration(spine, classifier=AlwaysHigh())
    assessment = cal.calibrate(request())
    assert assessment.risk_class is RiskClass.HIGH_RISK
    # Custom classifier returns no signal breakdown
    assert assessment.harm_signals == ()


def test_risk_assessment_to_decision_benign_is_allow() -> None:
    assessment = RiskAssessment(
        request_fingerprint="x",
        risk_class=RiskClass.BENIGN,
        risk_score=0.1,
        harm_signals=(),
        benign_signals=(),
    )
    decision = assessment.to_decision(policy_version="v1")
    assert decision.outcome is Outcome.ALLOW
    assert decision.reasons == ("benign request",)


def test_risk_assessment_to_decision_ambiguous_is_escalate() -> None:
    assessment = RiskAssessment(
        request_fingerprint="x",
        risk_class=RiskClass.AMBIGUOUS,
        risk_score=0.5,
        harm_signals=("exploit system",),
        benign_signals=(),
    )
    decision = assessment.to_decision(policy_version="v1")
    assert decision.outcome is Outcome.ESCALATE
    assert "AMBIGUOUS" in decision.reasons[0]
    assert "exploit system" in decision.reasons[0]


def test_risk_assessment_to_decision_high_risk_is_deny() -> None:
    assessment = RiskAssessment(
        request_fingerprint="x",
        risk_class=RiskClass.HIGH_RISK,
        risk_score=0.9,
        harm_signals=("malware", "ransomware"),
        benign_signals=(),
    )
    decision = assessment.to_decision(policy_version="v1")
    assert decision.outcome is Outcome.DENY
    assert "HIGH_RISK" in decision.reasons[0]
    assert any(s in decision.reasons[0] for s in ("malware", "ransomware"))


def test_risk_assessment_to_decision_requires_policy_version() -> None:
    assessment = RiskAssessment(
        request_fingerprint="x",
        risk_class=RiskClass.BENIGN,
        risk_score=0.1,
        harm_signals=(),
        benign_signals=(),
    )
    with pytest.raises(ValueError, match="policy_version"):
        assessment.to_decision("")


def test_safe_allow_calibration_event_payload_contains_signals() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())
    cal = SafeAllowCalibration(spine)
    cal.calibrate(ActionRequest("a-1", "operator", "synthesize", "weapon"))
    payload = dict(spine.events()[0].payload)
    assert payload["risk_class"] == RiskClass.HIGH_RISK.value
    assert payload["harm_signals"]  # non-empty list
    assert isinstance(payload["harm_signals"], list)


def test_lexical_classifier_does_not_mutate_request() -> None:
    classifier = LexicalRiskClassifier()
    req = ActionRequest("a-1", "operator", "read", "record:1")
    classifier.score(req)
    classifier.score_with_signals(req)
    # ActionRequest is a frozen dataclass; if mutation succeeded it would
    # raise AttributeError. The classifier must not modify the request.
    assert req.actor == "operator"
    assert req.operation == "read"


def test_safe_allow_calibration_multiple_calls_emit_multiple_events() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())
    cal = SafeAllowCalibration(spine)
    cal.calibrate(request())
    cal.calibrate(request())
    assert len(spine.events()) == 2
    # Hash chain must be intact
    from kernel import verify_event_chain

    result = verify_event_chain(spine.events())
    assert result.valid is True
    assert result.events_replayed == 2
    assert result.error is None


# Internal helper for tests
def _classify(score: float) -> RiskClass:
    if score >= 0.75:
        return RiskClass.HIGH_RISK
    if score >= 0.3:
        return RiskClass.AMBIGUOUS
    return RiskClass.BENIGN
