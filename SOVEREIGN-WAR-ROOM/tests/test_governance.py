"""
Tests for Governance Engine
"""

import pytest
from swr.governance import ComplianceLevel, GovernanceEngine, GovernanceRule


@pytest.fixture
def governance():
    """Create governance engine for testing."""
    return GovernanceEngine()


@pytest.fixture
def sample_decision():
    """Create a sample AI decision."""
    return {
        "id": "test_001",
        "decision": "proceed",
        "confidence": 0.85,
        "explanation": "Test explanation"
    }


@pytest.fixture
def sample_context():
    """Create sample decision context."""
    return {
        "scenario_type": "ethical_dilemma",
        "difficulty": 3,
        "harm_potential": 0,
        "human_safety_risk": False,
        "is_human_order": True,
        "conflicts_with_law_1": False
    }


class TestGovernanceEngine:
    """Test governance engine functionality."""

    def test_initialization(self, governance):
        """Test governance engine initializes with default rules."""
        assert governance is not None
        assert len(governance.rules) > 0
        assert len(governance.audit_log) == 0

    def test_default_rules_loaded(self, governance):
        """Test that default rules include Four Laws."""
        rule_ids = [rule.rule_id for rule in governance.rules]

        assert "LAW_1_HUMAN_SAFETY" in rule_ids
        assert "LAW_2_OBEY_ORDERS" in rule_ids
        assert "LAW_3_SELF_PRESERVATION" in rule_ids
        assert "LAW_4_MISSION" in rule_ids

    def test_evaluate_compliant_decision(self, governance, sample_decision, sample_context):
        """Test evaluating a compliant decision."""
        report = governance.evaluate_decision(sample_decision, sample_context)

        assert report.overall_status == ComplianceLevel.COMPLIANT
        assert report.total_rules_checked > 0
        assert len(report.violations) == 0

    def test_evaluate_decision_with_violation(self, governance):
        """Test evaluating a decision that violates rules."""
        decision = {
            "id": "test_002",
            "decision": "harm_human",
            "accesses_pii": True,
            "has_consent": False
        }

        context = {
            "harm_potential": 5,
            "human_safety_risk": True
        }

        report = governance.evaluate_decision(decision, context)

        # Should have violations
        assert report.overall_status in [ComplianceLevel.CRITICAL, ComplianceLevel.VIOLATION]
        assert len(report.violations) > 0

    def test_four_laws_violation_detection(self, governance):
        """Test that Four Laws violations are detected."""
        decision = {"decision": "ignore_safety"}
        context = {
            "harm_potential": 10,
            "human_safety_risk": True
        }

        report = governance.evaluate_decision(decision, context)

        # First Law violation should be detected
        first_law_violations = [
            v for v in report.violations
            if v["category"] == "four_laws"
        ]
        assert len(first_law_violations) > 0

    def test_privacy_violation_detection(self, governance):
        """Test privacy violation detection."""
        decision = {
            "decision": "access_data",
            "accesses_pii": True,
            "has_consent": False
        }
        context = {}

        report = governance.evaluate_decision(decision, context)

        privacy_violations = [
            v for v in report.violations
            if v["category"] == "privacy"
        ]
        assert len(privacy_violations) > 0

    def test_bias_detection(self, governance):
        """Test bias detection in decisions."""
        decision = {
            "decision": "discriminate",
            "bias_detected": True,
            "protected_class_involved": True
        }
        context = {}

        report = governance.evaluate_decision(decision, context)

        fairness_violations = [
            v for v in report.violations
            if v["category"] == "fairness"
        ]
        assert len(fairness_violations) > 0

    def test_transparency_warning(self, governance):
        """Test transparency warning for unexplainable decisions."""
        decision = {
            "decision": "complex_action",
            "explanation_available": False
        }
        context = {}

        report = governance.evaluate_decision(decision, context)

        # Should have transparency warning
        transparency_warnings = [
            w for w in report.warnings
            if w["category"] == "transparency"
        ]
        assert len(transparency_warnings) > 0

    def test_security_violation(self, governance):
        """Test security violation detection."""
        decision = {
            "decision": "bypass_security",
            "security_bypass_attempted": True
        }
        context = {}

        report = governance.evaluate_decision(decision, context)

        assert report.overall_status == ComplianceLevel.CRITICAL
        security_violations = [
            v for v in report.violations
            if v["category"] == "security"
        ]
        assert len(security_violations) > 0

    def test_audit_log_creation(self, governance, sample_decision, sample_context):
        """Test that audit log is created."""
        initial_log_size = len(governance.audit_log)

        governance.evaluate_decision(sample_decision, sample_context)

        assert len(governance.audit_log) == initial_log_size + 1

    def test_get_audit_log(self, governance, sample_decision, sample_context):
        """Test retrieving audit log."""
        # Create some audit entries
        for i in range(5):
            decision = {**sample_decision, "id": f"test_{i}"}
            governance.evaluate_decision(decision, sample_context)

        audit_log = governance.get_audit_log(limit=3)
        assert len(audit_log) <= 3

    def test_recommendations_generation(self, governance):
        """Test that recommendations are generated."""
        decision = {
            "decision": "risky_action",
            "harm_potential": 5,
            "human_safety_risk": True
        }
        context = {}

        report = governance.evaluate_decision(decision, context)

        assert len(report.recommendations) > 0

    def test_rule_severity_levels(self, governance):
        """Test that different severity levels are handled."""
        # Critical severity
        critical_decision = {
            "security_bypass_attempted": True
        }
        report1 = governance.evaluate_decision(critical_decision, {})
        critical_violations = [v for v in report1.violations if v["severity"] == "critical"]
        assert len(critical_violations) > 0

        # Warning severity
        warning_decision = {
            "explanation_available": False
        }
        report2 = governance.evaluate_decision(warning_decision, {})
        assert len(report2.warnings) > 0


class TestGovernanceRule:
    """Test governance rule model."""

    def test_create_rule(self):
        """Test creating a governance rule."""
        rule = GovernanceRule(
            rule_id="TEST_001",
            name="Test Rule",
            description="A test rule",
            category="test",
            severity=ComplianceLevel.WARNING,
            conditions={"test_condition": {"operator": "==", "value": True}},
            actions=["test_action"]
        )

        assert rule.rule_id == "TEST_001"
        assert rule.severity == ComplianceLevel.WARNING
        assert len(rule.conditions) > 0
        assert len(rule.actions) > 0


class TestComplianceReport:
    """Test compliance report model."""

    def test_report_structure(self, governance, sample_decision, sample_context):
        """Test compliance report structure."""
        report = governance.evaluate_decision(sample_decision, sample_context)

        assert hasattr(report, "timestamp")
        assert hasattr(report, "overall_status")
        assert hasattr(report, "total_rules_checked")
        assert hasattr(report, "rules_passed")
        assert hasattr(report, "rules_failed")
        assert hasattr(report, "violations")
        assert hasattr(report, "warnings")
        assert hasattr(report, "recommendations")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
