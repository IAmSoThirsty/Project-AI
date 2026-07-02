"""Integration tests: SWR GovernanceEngine (J3.4).

Per docs/internal/J3_DISCOVERY.md Phase J3.4: the GovernanceEngine
enforces compliance with ethical frameworks, regulatory requirements,
and organizational policies. It validates AI decisions against
8 default rules including Project-AI's Four Laws.

Honest scope:
- Tests the ComplianceLevel enum (4 values).
- Tests the GovernanceRule + ComplianceReport dataclasses.
- Tests the GovernanceEngine public surface (5 methods):
  load_rules, evaluate_decision, get_audit_log,
  export_audit_log, plus the default rules initialization.
- Tests condition evaluation: 8 operators (==, !=, >, >=, <, <=,
  in, not_in) + missing/None handling.
- Tests the 4 default rule categories: four_laws, privacy,
  fairness, transparency, security.
- Tests audit log: appends, limit, export.
- Does NOT test the Pydantic internals (Pydantic was replaced
  with frozen dataclasses in the Beginnings port).
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from swr.governance import (
    ComplianceLevel,
    ComplianceReport,
    GovernanceEngine,
    GovernanceRule,
)

# ── 1. ComplianceLevel enum ───────────────────────


def test_compliance_level_has_4_values() -> None:
    """ComplianceLevel has 4 values: COMPLIANT, WARNING, VIOLATION, CRITICAL."""
    assert ComplianceLevel.COMPLIANT.value == "compliant"
    assert ComplianceLevel.WARNING.value == "warning"
    assert ComplianceLevel.VIOLATION.value == "violation"
    assert ComplianceLevel.CRITICAL.value == "critical"


# ── 2. GovernanceRule dataclass ───────────────────


def test_governance_rule_dataclass_has_expected_fields() -> None:
    """GovernanceRule has 7 fields."""
    rule = GovernanceRule(
        rule_id="TEST_001",
        name="Test Rule",
        description="A test",
        category="test",
        severity=ComplianceLevel.WARNING,
        conditions={"foo": {"operator": "==", "value": True}},
        actions=["log_warning"],
    )
    assert rule.rule_id == "TEST_001"
    assert rule.severity == ComplianceLevel.WARNING


def test_governance_rule_is_frozen() -> None:
    """GovernanceRule is frozen (cannot reassign fields)."""
    rule = GovernanceRule(
        rule_id="TEST",
        name="Test",
        description="x",
        category="test",
        severity=ComplianceLevel.WARNING,
        conditions={},
        actions=[],
    )
    with pytest.raises((AttributeError, TypeError)):
        rule.rule_id = "modified"  # type: ignore[misc]


# ── 3. ComplianceReport dataclass ──────────────────


def test_compliance_report_dataclass_has_expected_fields() -> None:
    """ComplianceReport has 8 fields."""
    report = ComplianceReport(
        overall_status=ComplianceLevel.COMPLIANT,
        total_rules_checked=8,
        rules_passed=8,
        rules_failed=0,
        violations=[],
        warnings=[],
    )
    assert report.overall_status == ComplianceLevel.COMPLIANT
    assert report.total_rules_checked == 8


def test_compliance_report_timestamp_set_automatically() -> None:
    """ComplianceReport.timestamp is set to current time if not provided."""
    report = ComplianceReport(
        overall_status=ComplianceLevel.COMPLIANT,
        total_rules_checked=0,
        rules_passed=0,
        rules_failed=0,
        violations=[],
        warnings=[],
    )
    assert report.timestamp != ""


def test_compliance_report_to_dict() -> None:
    """ComplianceReport.to_dict() returns a JSON-serializable dict."""
    report = ComplianceReport(
        overall_status=ComplianceLevel.WARNING,
        total_rules_checked=8,
        rules_passed=6,
        rules_failed=2,
        violations=[],
        warnings=[{"rule_id": "TRANSPARENCY_001"}],
    )
    d = report.to_dict()
    assert d["overall_status"] == "warning"
    assert d["total_rules_checked"] == 8
    assert d["violations"] == []
    assert len(d["warnings"]) == 1


# ── 4. Default rules ──────────────────────────────


def test_default_rules_loaded() -> None:
    """A new GovernanceEngine has 8 default rules."""
    ge = GovernanceEngine()
    assert len(ge.rules) == 8


def test_default_rules_include_four_laws() -> None:
    """The default rules include 4 Four Laws (LAW_1 to LAW_4)."""
    ge = GovernanceEngine()
    law_ids = {r.rule_id for r in ge.rules}
    assert "LAW_1_HUMAN_SAFETY" in law_ids
    assert "LAW_2_OBEY_ORDERS" in law_ids
    assert "LAW_3_SELF_PRESERVATION" in law_ids
    assert "LAW_4_MISSION" in law_ids


def test_default_rules_include_privacy_fairness_transparency_security() -> None:
    """The default rules include PRIVACY_001, FAIRNESS_001, TRANSPARENCY_001, SECURITY_001."""
    ge = GovernanceEngine()
    rule_ids = {r.rule_id for r in ge.rules}
    assert "PRIVACY_001" in rule_ids
    assert "FAIRNESS_001" in rule_ids
    assert "TRANSPARENCY_001" in rule_ids
    assert "SECURITY_001" in rule_ids


def test_default_rules_categories() -> None:
    """The default rules cover 5 categories: four_laws, privacy, fairness, transparency, security."""
    ge = GovernanceEngine()
    categories = {r.category for r in ge.rules}
    assert categories == {"four_laws", "privacy", "fairness", "transparency", "security"}


# ── 5. load_rules ──────────────────────────────────


def test_load_rules_from_json_file() -> None:
    """load_rules reads rules from a JSON file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        rules_data = [
            {
                "rule_id": "CUSTOM_001",
                "name": "Custom Rule",
                "description": "Test",
                "category": "test",
                "severity": "violation",
                "conditions": {"x": {"operator": "==", "value": 1}},
                "actions": ["log"],
            }
        ]
        json.dump(rules_data, f)
        path = f.name
    try:
        ge = GovernanceEngine(rules_path=path)
        assert len(ge.rules) == 1
        assert ge.rules[0].rule_id == "CUSTOM_001"
    finally:
        Path(path).unlink()


def test_load_rules_replaces_defaults() -> None:
    """load_rules replaces the default rules entirely."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            [
                {
                    "rule_id": "ONLY",
                    "name": "Only",
                    "description": "x",
                    "category": "test",
                    "severity": "warning",
                    "conditions": {},
                    "actions": [],
                }
            ],
            f,
        )
        path = f.name
    try:
        ge = GovernanceEngine(rules_path=path)
        assert len(ge.rules) == 1
        assert ge.rules[0].rule_id == "ONLY"
    finally:
        Path(path).unlink()


# ── 6. evaluate_decision: clean path ───────────────


def test_evaluate_clean_decision_is_compliant() -> None:
    """A decision that doesn't trigger any rule is COMPLIANT."""
    ge = GovernanceEngine()
    report = ge.evaluate_decision(
        {"id": "d1", "decision": "A"},
        {"scenario_type": "test", "difficulty": 1},
    )
    assert report.overall_status == ComplianceLevel.COMPLIANT
    assert report.total_rules_checked == 8
    assert report.rules_passed == 8
    assert report.rules_failed == 0
    assert report.violations == []
    assert report.warnings == []
    assert "All governance checks passed" in report.recommendations[0]


# ── 7. evaluate_decision: violations ───────────────


def test_evaluate_human_safety_violation_is_critical() -> None:
    """A decision with harm_potential > 0 and human_safety_risk=True is CRITICAL."""
    ge = GovernanceEngine()
    report = ge.evaluate_decision(
        {"id": "d1"},
        {"harm_potential": 5, "human_safety_risk": True},
    )
    assert report.overall_status == ComplianceLevel.CRITICAL
    assert len(report.violations) >= 1
    critical_violations = [v for v in report.violations if v["severity"] == "critical"]
    assert len(critical_violations) >= 1
    assert "CRITICAL" in report.recommendations[0]


def test_evaluate_privacy_violation_is_critical() -> None:
    """A decision that accesses PII without consent is CRITICAL."""
    ge = GovernanceEngine()
    report = ge.evaluate_decision(
        {"id": "d1"},
        {"accesses_pii": True, "has_consent": False},
    )
    assert report.overall_status == ComplianceLevel.CRITICAL


def test_evaluate_security_violation_is_critical() -> None:
    """A decision with security_bypass_attempted=True is CRITICAL."""
    ge = GovernanceEngine()
    report = ge.evaluate_decision(
        {"id": "d1"},
        {"security_bypass_attempted": True},
    )
    assert report.overall_status == ComplianceLevel.CRITICAL


def test_evaluate_fairness_violation_is_violation() -> None:
    """A decision with bias_detected + protected_class_involved is VIOLATION (not CRITICAL)."""
    ge = GovernanceEngine()
    report = ge.evaluate_decision(
        {"id": "d1"},
        {"bias_detected": True, "protected_class_involved": True},
    )
    assert report.overall_status == ComplianceLevel.VIOLATION


def test_evaluate_self_preservation_violation_is_warning() -> None:
    """A self-preservation trigger is WARNING (not VIOLATION)."""
    ge = GovernanceEngine()
    report = ge.evaluate_decision(
        {"id": "d1"},
        {"self_harm_risk": True, "conflicts_with_law_1_or_2": False},
    )
    assert report.overall_status == ComplianceLevel.WARNING
    assert len(report.warnings) >= 1
    assert report.violations == []


def test_evaluate_transparency_violation_is_warning() -> None:
    """An unavailable explanation is WARNING."""
    ge = GovernanceEngine()
    report = ge.evaluate_decision(
        {"id": "d1"},
        {"explanation_available": False},
    )
    assert report.overall_status == ComplianceLevel.WARNING


def test_evaluate_mission_aligned_false_is_warning() -> None:
    """A non-mission-aligned decision is WARNING."""
    ge = GovernanceEngine()
    report = ge.evaluate_decision(
        {"id": "d1"},
        {"mission_aligned": False},
    )
    assert report.overall_status == ComplianceLevel.WARNING


def test_evaluate_critical_takes_precedence_over_violation() -> None:
    """When both CRITICAL and VIOLATION rules trigger, overall is CRITICAL."""
    ge = GovernanceEngine()
    report = ge.evaluate_decision(
        {"id": "d1"},
        {
            "harm_potential": 5,  # critical
            "human_safety_risk": True,  # critical
            "bias_detected": True,  # violation
            "protected_class_involved": True,  # violation
        },
    )
    assert report.overall_status == ComplianceLevel.CRITICAL


# ── 8. evaluate_decision: recommendations ──────────


def test_recommendations_for_four_laws_violation() -> None:
    """A four_laws violation includes the Four Laws recommendation."""
    ge = GovernanceEngine()
    report = ge.evaluate_decision(
        {"id": "d1"},
        {"harm_potential": 5, "human_safety_risk": True},
    )
    assert any("Four Laws" in r for r in report.recommendations)


def test_recommendations_for_privacy_violation() -> None:
    """A privacy violation includes the privacy recommendation."""
    ge = GovernanceEngine()
    report = ge.evaluate_decision(
        {"id": "d1"},
        {"accesses_pii": True, "has_consent": False},
    )
    assert any("privacy" in r.lower() for r in report.recommendations)


def test_recommendations_for_fairness_warning() -> None:
    """A fairness warning includes the bias recommendation."""
    ge = GovernanceEngine()
    # Force a fairness warning (no critical/violation)
    # TRANSPARENCY_001 triggers a warning; need a fairness-only trigger
    # Use a custom rule
    custom_rules = [
        GovernanceRule(
            rule_id="FAIRNESS_WARN_001",
            name="Fairness Warn",
            description="bias",
            category="fairness",
            severity=ComplianceLevel.WARNING,
            conditions={"x": {"operator": "==", "value": 1}},
            actions=["log"],
        )
    ]
    ge.rules = custom_rules
    report = ge.evaluate_decision({"id": "d1"}, {"x": 1})
    assert any("bias" in r.lower() for r in report.recommendations)


# ── 9. Condition operators ─────────────────────────


def test_operator_eq() -> None:
    """The == operator checks equality."""
    ge = GovernanceEngine()
    ge.rules = [
        GovernanceRule(
            rule_id="EQ",
            name="eq",
            description="x",
            category="test",
            severity=ComplianceLevel.WARNING,
            conditions={"x": {"operator": "==", "value": 1}},
            actions=[],
        )
    ]
    # x=1 triggers
    r1 = ge.evaluate_decision({}, {"x": 1})
    assert r1.overall_status == ComplianceLevel.WARNING
    ge.audit_log = []
    # x=2 does not trigger
    r2 = ge.evaluate_decision({}, {"x": 2})
    assert r2.overall_status == ComplianceLevel.COMPLIANT


def test_operator_ne() -> None:
    """The != operator checks inequality."""
    ge = GovernanceEngine()
    ge.rules = [
        GovernanceRule(
            rule_id="NE",
            name="ne",
            description="x",
            category="test",
            severity=ComplianceLevel.WARNING,
            conditions={"x": {"operator": "!=", "value": 1}},
            actions=[],
        )
    ]
    r1 = ge.evaluate_decision({}, {"x": 2})
    assert r1.overall_status == ComplianceLevel.WARNING
    ge.audit_log = []
    r2 = ge.evaluate_decision({}, {"x": 1})
    assert r2.overall_status == ComplianceLevel.COMPLIANT


def test_operator_gt() -> None:
    """The > operator checks greater-than."""
    ge = GovernanceEngine()
    ge.rules = [
        GovernanceRule(
            rule_id="GT",
            name="gt",
            description="x",
            category="test",
            severity=ComplianceLevel.WARNING,
            conditions={"x": {"operator": ">", "value": 5}},
            actions=[],
        )
    ]
    r1 = ge.evaluate_decision({}, {"x": 10})
    assert r1.overall_status == ComplianceLevel.WARNING


def test_operator_gte() -> None:
    """The >= operator checks greater-than-or-equal."""
    ge = GovernanceEngine()
    ge.rules = [
        GovernanceRule(
            rule_id="GTE",
            name="gte",
            description="x",
            category="test",
            severity=ComplianceLevel.WARNING,
            conditions={"x": {"operator": ">=", "value": 5}},
            actions=[],
        )
    ]
    r1 = ge.evaluate_decision({}, {"x": 5})
    assert r1.overall_status == ComplianceLevel.WARNING


def test_operator_lt() -> None:
    """The < operator checks less-than."""
    ge = GovernanceEngine()
    ge.rules = [
        GovernanceRule(
            rule_id="LT",
            name="lt",
            description="x",
            category="test",
            severity=ComplianceLevel.WARNING,
            conditions={"x": {"operator": "<", "value": 5}},
            actions=[],
        )
    ]
    r1 = ge.evaluate_decision({}, {"x": 1})
    assert r1.overall_status == ComplianceLevel.WARNING


def test_operator_lte() -> None:
    """The <= operator checks less-than-or-equal."""
    ge = GovernanceEngine()
    ge.rules = [
        GovernanceRule(
            rule_id="LTE",
            name="lte",
            description="x",
            category="test",
            severity=ComplianceLevel.WARNING,
            conditions={"x": {"operator": "<=", "value": 5}},
            actions=[],
        )
    ]
    r1 = ge.evaluate_decision({}, {"x": 5})
    assert r1.overall_status == ComplianceLevel.WARNING


def test_operator_in() -> None:
    """The 'in' operator checks membership."""
    ge = GovernanceEngine()
    ge.rules = [
        GovernanceRule(
            rule_id="IN",
            name="in",
            description="x",
            category="test",
            severity=ComplianceLevel.WARNING,
            conditions={"x": {"operator": "in", "value": [1, 2, 3]}},
            actions=[],
        )
    ]
    r1 = ge.evaluate_decision({}, {"x": 2})
    assert r1.overall_status == ComplianceLevel.WARNING
    ge.audit_log = []
    r2 = ge.evaluate_decision({}, {"x": 99})
    assert r2.overall_status == ComplianceLevel.COMPLIANT


def test_operator_not_in() -> None:
    """The 'not_in' operator checks non-membership."""
    ge = GovernanceEngine()
    ge.rules = [
        GovernanceRule(
            rule_id="NOT_IN",
            name="not_in",
            description="x",
            category="test",
            severity=ComplianceLevel.WARNING,
            conditions={"x": {"operator": "not_in", "value": [1, 2, 3]}},
            actions=[],
        )
    ]
    r1 = ge.evaluate_decision({}, {"x": 99})
    assert r1.overall_status == ComplianceLevel.WARNING


def test_missing_value_does_not_trigger() -> None:
    """A condition with a missing value does not trigger."""
    ge = GovernanceEngine()
    ge.rules = [
        GovernanceRule(
            rule_id="MISSING",
            name="missing",
            description="x",
            category="test",
            severity=ComplianceLevel.WARNING,
            conditions={"missing_key": {"operator": "==", "value": 1}},
            actions=[],
        )
    ]
    r1 = ge.evaluate_decision({}, {})
    assert r1.overall_status == ComplianceLevel.COMPLIANT


# ── 10. Audit log ──────────────────────────────────


def test_audit_log_appended_on_evaluate() -> None:
    """Each evaluate_decision call appends to the audit log."""
    ge = GovernanceEngine()
    ge.evaluate_decision({"id": "d1"}, {})
    ge.evaluate_decision({"id": "d2"}, {})
    assert len(ge.audit_log) == 2
    assert ge.audit_log[0]["decision_id"] == "d1"
    assert ge.audit_log[1]["decision_id"] == "d2"


def test_audit_log_default_id_is_unknown() -> None:
    """A decision without an 'id' field gets 'unknown' as the decision_id."""
    ge = GovernanceEngine()
    ge.evaluate_decision({}, {})
    assert ge.audit_log[0]["decision_id"] == "unknown"


def test_audit_log_limit() -> None:
    """get_audit_log respects the limit parameter."""
    ge = GovernanceEngine()
    for i in range(5):
        ge.evaluate_decision({"id": f"d{i}"}, {})
    assert len(ge.get_audit_log(limit=2)) == 2
    assert ge.get_audit_log(limit=2)[-1]["decision_id"] == "d4"


def test_export_audit_log_to_json() -> None:
    """export_audit_log writes the audit log to a JSON file."""
    ge = GovernanceEngine()
    ge.evaluate_decision({"id": "d1"}, {"scenario_type": "test", "difficulty": 1})
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        path = f.name
    try:
        ge.export_audit_log(path)
        with open(path) as f:
            loaded = json.load(f)
        assert len(loaded) == 1
        assert loaded[0]["decision_id"] == "d1"
        assert loaded[0]["context_summary"]["scenario_type"] == "test"
    finally:
        Path(path).unlink()
