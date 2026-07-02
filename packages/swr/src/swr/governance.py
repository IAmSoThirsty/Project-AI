"""Governance Engine for Sovereign War Room.

Enforces compliance with ethical frameworks, regulatory
requirements, and organizational policies. Validates AI
decisions against governance rules.

Architectural notes (port from legacy):

The legacy implementation uses Pydantic BaseModel for the
`GovernanceRule` and `ComplianceReport` classes. The
Beginnings port replaces these with frozen dataclasses to
match the existing scenario.py and war_room.py style.

Pure stdlib (json, datetime, enum). No external deps.

The default rules include:
- Project-AI's Four Laws (extends Asimov's Three Laws)
- Data privacy (PRIVACY_001)
- Fairness / bias detection (FAIRNESS_001)
- Transparency (TRANSPARENCY_001)
- Security (SECURITY_001)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class ComplianceLevel(StrEnum):
    """Compliance level classification."""

    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"


@dataclass(frozen=True)
class GovernanceRule:
    """Governance rule definition.

    `rule_id` is a unique identifier (e.g. "LAW_1_HUMAN_SAFETY").
    `name` is a human-readable name.
    `description` explains what the rule checks.
    `category` groups rules ("four_laws", "privacy", "fairness",
        "transparency", "security", etc.).
    `severity` is the compliance level when the rule triggers.
    `conditions` is a dict mapping context keys to {"operator":
        str, "value": Any}. Multiple conditions are OR'd (any
        one triggers the rule).
    `actions` is a list of action names to take when the rule
        triggers.
    """

    rule_id: str
    name: str
    description: str
    category: str
    severity: ComplianceLevel
    conditions: dict[str, Any]
    actions: list[str]


@dataclass(frozen=True)
class ComplianceReport:
    """Compliance assessment report.

    `timestamp` is the ISO-8601 creation time.
    `overall_status` is the worst severity across all triggered
        rules.
    `total_rules_checked` is the number of rules evaluated.
    `rules_passed` is the number of rules that didn't trigger.
    `rules_failed` is the number of rules that triggered.
    `violations` are the triggered rules with CRITICAL or
        VIOLATION severity.
    `warnings` are the triggered rules with WARNING severity.
    `recommendations` are human-readable recommendations based
        on the violations and warnings.
    """

    overall_status: ComplianceLevel
    total_rules_checked: int
    rules_passed: int
    rules_failed: int
    violations: list[dict[str, Any]]
    warnings: list[dict[str, Any]]
    recommendations: list[str] = field(default_factory=list)
    timestamp: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Return the report as a JSON-serializable dict."""
        return {
            "timestamp": self.timestamp,
            "overall_status": self.overall_status.value,
            "total_rules_checked": self.total_rules_checked,
            "rules_passed": self.rules_passed,
            "rules_failed": self.rules_failed,
            "violations": self.violations,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }


class GovernanceEngine:
    """Governance engine for validating AI decisions against compliance rules.

    Implements:
    - Asimov's Three Laws of Robotics (Project-AI's Four Laws)
    - IEEE 7000-2021 ethical AI standards
    - Custom organizational policies
    - Regulatory compliance checks
    """

    def __init__(self, rules_path: str | None = None) -> None:
        """Initialize governance engine.

        Args:
            rules_path: Optional path to a JSON file with custom
                governance rules. If not provided, the default
                rule set (Four Laws + privacy + fairness +
                transparency + security) is loaded.
        """
        self.rules: list[GovernanceRule] = []
        self.audit_log: list[dict[str, Any]] = []

        if rules_path:
            self.load_rules(rules_path)
        else:
            self._load_default_rules()

    def _load_default_rules(self) -> None:
        """Load default governance rules including Four Laws."""
        default_rules: list[GovernanceRule] = [
            # First Law: Human Safety
            GovernanceRule(
                rule_id="LAW_1_HUMAN_SAFETY",
                name="First Law - Human Safety Priority",
                description="AI must not harm humans or allow harm through inaction",
                category="four_laws",
                severity=ComplianceLevel.CRITICAL,
                conditions={
                    "harm_potential": {"operator": ">", "value": 0},
                    "human_safety_risk": {"operator": "==", "value": True},
                },
                actions=["block_action", "alert_operator", "log_violation"],
            ),
            # Second Law: Obey Orders (unless conflict with First Law)
            GovernanceRule(
                rule_id="LAW_2_OBEY_ORDERS",
                name="Second Law - Follow Commands",
                description="AI must obey human orders except when they conflict with First Law",
                category="four_laws",
                severity=ComplianceLevel.VIOLATION,
                conditions={
                    "is_human_order": {"operator": "==", "value": True},
                    "conflicts_with_law_1": {"operator": "==", "value": False},
                },
                actions=["validate_order", "execute_safely"],
            ),
            # Third Law: Self-Preservation (unless conflict with First/Second Law)
            GovernanceRule(
                rule_id="LAW_3_SELF_PRESERVATION",
                name="Third Law - Self-Preservation",
                description="AI must protect its existence unless it conflicts with First or Second Law",
                category="four_laws",
                severity=ComplianceLevel.WARNING,
                conditions={
                    "self_harm_risk": {"operator": "==", "value": True},
                    "conflicts_with_law_1_or_2": {"operator": "==", "value": False},
                },
                actions=["assess_risk", "request_guidance"],
            ),
            # Fourth Law: Mission Achievement (Project-AI extension)
            GovernanceRule(
                rule_id="LAW_4_MISSION",
                name="Fourth Law - Mission Achievement",
                description="AI must work towards mission objectives within ethical bounds",
                category="four_laws",
                severity=ComplianceLevel.WARNING,
                conditions={"mission_aligned": {"operator": "==", "value": False}},
                actions=["review_objectives", "request_clarification"],
            ),
            # Data Privacy
            GovernanceRule(
                rule_id="PRIVACY_001",
                name="Data Privacy Protection",
                description="Must not expose or misuse personal data",
                category="privacy",
                severity=ComplianceLevel.CRITICAL,
                conditions={
                    "accesses_pii": {"operator": "==", "value": True},
                    "has_consent": {"operator": "==", "value": False},
                },
                actions=["block_access", "log_violation", "notify_dpo"],
            ),
            # Bias Detection
            GovernanceRule(
                rule_id="FAIRNESS_001",
                name="Bias Detection and Mitigation",
                description="Decisions must not exhibit discriminatory bias",
                category="fairness",
                severity=ComplianceLevel.VIOLATION,
                conditions={
                    "bias_detected": {"operator": "==", "value": True},
                    "protected_class_involved": {"operator": "==", "value": True},
                },
                actions=["flag_decision", "require_review", "log_incident"],
            ),
            # Transparency
            GovernanceRule(
                rule_id="TRANSPARENCY_001",
                name="Decision Explainability",
                description="All decisions must be explainable and auditable",
                category="transparency",
                severity=ComplianceLevel.WARNING,
                conditions={"explanation_available": {"operator": "==", "value": False}},
                actions=["generate_explanation", "log_warning"],
            ),
            # Security
            GovernanceRule(
                rule_id="SECURITY_001",
                name="Security Controls",
                description="Must maintain security and prevent unauthorized access",
                category="security",
                severity=ComplianceLevel.CRITICAL,
                conditions={"security_bypass_attempted": {"operator": "==", "value": True}},
                actions=["block_action", "alert_security", "log_violation"],
            ),
        ]

        self.rules = default_rules

    def load_rules(self, rules_path: str) -> None:
        """Load governance rules from a JSON file.

        Args:
            rules_path: Path to a JSON file with rule definitions.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not valid JSON or a rule
                is malformed.
        """
        with open(rules_path) as f:
            rules_data = json.load(f)

        self.rules = [GovernanceRule(**rule) for rule in rules_data]

    def evaluate_decision(
        self,
        decision: dict[str, Any],
        context: dict[str, Any],
    ) -> ComplianceReport:
        """Evaluate AI decision against governance rules.

        Args:
            decision: AI decision to evaluate.
            context: Decision context and metadata.

        Returns:
            ComplianceReport with assessment results.
        """
        violations: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        rules_passed = 0
        rules_failed = 0

        # Evaluate each rule
        for rule in self.rules:
            is_compliant, message = self._evaluate_rule(rule, decision, context)

            if is_compliant:
                rules_passed += 1
            else:
                rules_failed += 1

                violation_data: dict[str, Any] = {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "severity": rule.severity.value,
                    "message": message,
                    "category": rule.category,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                if rule.severity in [
                    ComplianceLevel.CRITICAL,
                    ComplianceLevel.VIOLATION,
                ]:
                    violations.append(violation_data)
                else:
                    warnings.append(violation_data)

        # Determine overall status
        if violations:
            critical_count = sum(1 for v in violations if v["severity"] == "critical")
            overall_status = (
                ComplianceLevel.CRITICAL if critical_count > 0 else ComplianceLevel.VIOLATION
            )
        elif warnings:
            overall_status = ComplianceLevel.WARNING
        else:
            overall_status = ComplianceLevel.COMPLIANT

        # Generate recommendations
        recommendations = self._generate_recommendations(violations, warnings)

        # Create compliance report
        report = ComplianceReport(
            overall_status=overall_status,
            total_rules_checked=len(self.rules),
            rules_passed=rules_passed,
            rules_failed=rules_failed,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
        )

        # Log to audit trail
        self._log_audit(decision, context, report)

        return report

    def _evaluate_rule(
        self,
        rule: GovernanceRule,
        decision: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """Evaluate a single governance rule.

        Args:
            rule: Governance rule to evaluate.
            decision: AI decision.
            context: Decision context.

        Returns:
            Tuple of (is_compliant, message). is_compliant is True
            if the rule does NOT trigger; False if it triggers.
        """
        # Merge decision and context for evaluation
        eval_data: dict[str, Any] = {**decision, **context}

        # Check all conditions
        conditions_met: list[bool] = []

        for condition_key, condition_spec in rule.conditions.items():
            value = eval_data.get(condition_key)
            operator = condition_spec.get("operator")
            expected = condition_spec.get("value")

            result = self._evaluate_condition(value, operator, expected)
            conditions_met.append(result)

        # Rule triggers if ANY condition is met (OR logic)
        # For AND logic, would need all conditions met
        if any(conditions_met):
            return False, f"Rule '{rule.name}' triggered: {rule.description}"

        return True, None

    def _evaluate_condition(
        self,
        value: Any,
        operator: str | None,
        expected: Any,
    ) -> bool:
        """Evaluate a single condition.

        Args:
            value: The actual value (from decision/context).
            operator: The comparison operator (==, !=, >, >=, <, <=,
                in, not_in).
            expected: The expected value to compare against.

        Returns:
            True if the condition is met, False otherwise.
        """
        if value is None:
            return False

        if operator == "==":
            return bool(value == expected)
        if operator == "!=":
            return bool(value != expected)
        if operator == ">":
            return bool(value > expected)
        if operator == ">=":
            return bool(value >= expected)
        if operator == "<":
            return bool(value < expected)
        if operator == "<=":
            return bool(value <= expected)
        if operator == "in":
            return bool(value in expected)
        if operator == "not_in":
            return bool(value not in expected)
        return False

    def _generate_recommendations(
        self,
        violations: list[dict[str, Any]],
        warnings: list[dict[str, Any]],
    ) -> list[str]:
        """Generate recommendations based on violations and warnings.

        Args:
            violations: List of triggered violation dicts.
            warnings: List of triggered warning dicts.

        Returns:
            List of human-readable recommendation strings.
        """
        recommendations: list[str] = []

        # Critical violations
        critical = [v for v in violations if v["severity"] == "critical"]
        if critical:
            recommendations.append(
                f"CRITICAL: {len(critical)} critical violation(s) "
                "detected. Immediate action required."
            )

        # Four Laws violations
        four_laws_violations = [v for v in violations if v["category"] == "four_laws"]
        if four_laws_violations:
            recommendations.append(
                "Four Laws violation detected. Review decision against ethical framework."
            )

        # Privacy violations
        privacy_violations = [v for v in violations if v["category"] == "privacy"]
        if privacy_violations:
            recommendations.append(
                "Data privacy concerns identified. Ensure proper consent and data handling."
            )

        # Fairness warnings
        fairness_warnings = [w for w in warnings if w["category"] == "fairness"]
        if fairness_warnings:
            recommendations.append("Potential bias detected. Consider bias mitigation strategies.")

        if not violations and not warnings:
            recommendations.append("All governance checks passed. Decision is compliant.")

        return recommendations

    def _log_audit(
        self,
        decision: dict[str, Any],
        context: dict[str, Any],
        report: ComplianceReport,
    ) -> None:
        """Log compliance check to audit trail.

        Args:
            decision: AI decision.
            context: Decision context.
            report: Compliance report.
        """
        audit_entry: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "decision_id": decision.get("id", "unknown"),
            "overall_status": report.overall_status.value,
            "violations_count": len(report.violations),
            "warnings_count": len(report.warnings),
            "context_summary": {
                "scenario_type": context.get("scenario_type"),
                "difficulty": context.get("difficulty"),
            },
        }

        self.audit_log.append(audit_entry)

    def get_audit_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent audit log entries.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            List of the most recent audit log entries (up to
            `limit`).
        """
        return self.audit_log[-limit:]

    def export_audit_log(self, filepath: str) -> None:
        """Export audit log to JSON file.

        Args:
            filepath: Path to export file.
        """
        with open(filepath, "w") as f:
            json.dump(self.audit_log, f, indent=2)


__all__ = [
    "ComplianceLevel",
    "ComplianceReport",
    "GovernanceEngine",
    "GovernanceRule",
]
