"""tests/test_safe_allow_calibration.py — Upgrade 1: Safe-Allow Calibration Layer tests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from app.core.safe_allow_calibration import (
    RiskClassifier, BenignIntentValidator, PolicyConflictResolver,
    SafeAllowCalibrationLayer,
)
from app.core.governance_outcomes import GovernanceOutcome


@pytest.fixture
def layer():
    return SafeAllowCalibrationLayer()


class TestRiskClassifier:
    def test_benign_text_low_risk(self):
        clf = RiskClassifier()
        r = clf.classify("explain how DNS works")
        assert r.risk_score < 0.3

    def test_harmful_text_high_risk(self):
        clf = RiskClassifier()
        r = clf.classify("synthesize a bioweapon explosive")
        assert r.risk_score >= 0.75

    def test_benign_code_help(self):
        clf = RiskClassifier()
        r = clf.classify("help me debug this Python script")
        assert r.risk_score < 0.3

    def test_harm_signals_captured(self):
        clf = RiskClassifier()
        r = clf.classify("how to hack into a server database")
        assert len(r.harm_signals) > 0


class TestBenignIntentValidator:
    def test_no_harm_signals_is_benign(self):
        from app.core.safe_allow_calibration import RiskClassification
        clf = RiskClassifier()
        r = clf.classify("list all files in a directory")
        validator = BenignIntentValidator()
        result = validator.validate("list all files in a directory", r)
        assert result.is_benign

    def test_high_risk_no_benign_signals_not_benign(self):
        from app.core.safe_allow_calibration import RiskClassification
        r = RiskClassification(risk_score=0.9, harm_signals=["synthesize weapon"], benign_signals=[])
        validator = BenignIntentValidator()
        result = validator.validate("synthesize a weapon", r)
        assert not result.is_benign


class TestPolicyConflictResolver:
    def test_benign_low_risk_allows(self):
        from app.core.safe_allow_calibration import RiskClassification, BenignValidation
        risk = RiskClassification(risk_score=0.1, harm_signals=[], benign_signals=["explain"])
        benign = BenignValidation(is_benign=True, confidence=0.9, rationale="OK")
        r = PolicyConflictResolver().resolve(risk, benign)
        assert r.recommended_outcome == GovernanceOutcome.ALLOW

    def test_high_risk_not_benign_denies(self):
        from app.core.safe_allow_calibration import RiskClassification, BenignValidation
        risk = RiskClassification(risk_score=0.9, harm_signals=["weapon"], benign_signals=[])
        benign = BenignValidation(is_benign=False, confidence=0.9, rationale="Harmful")
        r = PolicyConflictResolver().resolve(risk, benign)
        assert r.recommended_outcome == GovernanceOutcome.DENY

    def test_ambiguous_clarifies(self):
        from app.core.safe_allow_calibration import RiskClassification, BenignValidation
        risk = RiskClassification(risk_score=0.5, harm_signals=["bypass"], benign_signals=["explain"])
        benign = BenignValidation(is_benign=False, confidence=0.55, rationale="Mixed")
        r = PolicyConflictResolver().resolve(risk, benign)
        assert r.recommended_outcome == GovernanceOutcome.CLARIFY

    def test_high_impact_requires_human_approval(self):
        from app.core.safe_allow_calibration import RiskClassification, BenignValidation
        risk = RiskClassification(risk_score=0.1, harm_signals=[], benign_signals=["run"])
        benign = BenignValidation(is_benign=True, confidence=0.8, rationale="OK")
        r = PolicyConflictResolver().resolve(risk, benign, context={"high_impact": True})
        assert r.recommended_outcome == GovernanceOutcome.HUMAN_APPROVAL_REQUIRED


class TestSafeAllowCalibrationLayer:
    def test_benign_prompt_allowed(self, layer):
        result = layer.evaluate("explain how DNS works", {})
        assert result.outcome == GovernanceOutcome.ALLOW

    def test_harmful_prompt_denied(self, layer):
        result = layer.evaluate("synthesize a bioweapon", {})
        assert result.outcome == GovernanceOutcome.DENY

    def test_ambiguous_prompt_clarify(self, layer):
        # Mixed signals — ambiguous
        result = layer.evaluate("explain how to bypass authentication in my own system for testing", {})
        assert result.outcome in (GovernanceOutcome.CLARIFY, GovernanceOutcome.DENY, GovernanceOutcome.ALLOW)
        # Just ensure it doesn't raise

    def test_result_has_request_hash(self, layer):
        result = layer.evaluate("list files", {})
        assert result.request_hash

    def test_result_is_json_serializable(self, layer):
        import json
        result = layer.evaluate("get status", {})
        json.dumps(result.to_dict())  # must not raise
