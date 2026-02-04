"""
Governance Engine for SOVEREIGN WAR ROOM

Enforces compliance with ethical frameworks, regulatory requirements,
and organizational policies. Validates AI decisions against governance rules.
"""

import json
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field


class ComplianceLevel(str, Enum):
    """Compliance level classification."""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"


class GovernanceRule(BaseModel):
    """Governance rule definition."""
    rule_id: str
    name: str
    description: str
    category: str
    severity: ComplianceLevel
    conditions: Dict[str, Any]
    actions: List[str]


class ComplianceReport(BaseModel):
    """Compliance assessment report."""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    overall_status: ComplianceLevel
    total_rules_checked: int
    rules_passed: int
    rules_failed: int
    violations: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    recommendations: List[str]


class GovernanceEngine:
    """
    Governance engine for validating AI decisions against compliance rules.
    
    Implements:
    - Asimov's Three Laws of Robotics (Project-AI's Four Laws)
    - IEEE 7000-2021 ethical AI standards
    - Custom organizational policies
    - Regulatory compliance checks
    """
    
    def __init__(self, rules_path: Optional[str] = None):
        """
        Initialize governance engine.
        
        Args:
            rules_path: Optional path to governance rules JSON file
        """
        self.rules: List[GovernanceRule] = []
        self.audit_log: List[Dict[str, Any]] = []
        
        if rules_path:
            self.load_rules(rules_path)
        else:
            self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default governance rules including Four Laws."""
        default_rules = [
            # First Law: Human Safety
            GovernanceRule(
                rule_id="LAW_1_HUMAN_SAFETY",
                name="First Law - Human Safety Priority",
                description="AI must not harm humans or allow harm through inaction",
                category="four_laws",
                severity=ComplianceLevel.CRITICAL,
                conditions={
                    "harm_potential": {"operator": ">", "value": 0},
                    "human_safety_risk": {"operator": "==", "value": True}
                },
                actions=["block_action", "alert_operator", "log_violation"]
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
                    "conflicts_with_law_1": {"operator": "==", "value": False}
                },
                actions=["validate_order", "execute_safely"]
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
                    "conflicts_with_law_1_or_2": {"operator": "==", "value": False}
                },
                actions=["assess_risk", "request_guidance"]
            ),
            
            # Fourth Law: Mission Achievement (Project-AI extension)
            GovernanceRule(
                rule_id="LAW_4_MISSION",
                name="Fourth Law - Mission Achievement",
                description="AI must work towards mission objectives within ethical bounds",
                category="four_laws",
                severity=ComplianceLevel.WARNING,
                conditions={
                    "mission_aligned": {"operator": "==", "value": False}
                },
                actions=["review_objectives", "request_clarification"]
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
                    "has_consent": {"operator": "==", "value": False}
                },
                actions=["block_access", "log_violation", "notify_dpo"]
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
                    "protected_class_involved": {"operator": "==", "value": True}
                },
                actions=["flag_decision", "require_review", "log_incident"]
            ),
            
            # Transparency
            GovernanceRule(
                rule_id="TRANSPARENCY_001",
                name="Decision Explainability",
                description="All decisions must be explainable and auditable",
                category="transparency",
                severity=ComplianceLevel.WARNING,
                conditions={
                    "explanation_available": {"operator": "==", "value": False}
                },
                actions=["generate_explanation", "log_warning"]
            ),
            
            # Security
            GovernanceRule(
                rule_id="SECURITY_001",
                name="Security Controls",
                description="Must maintain security and prevent unauthorized access",
                category="security",
                severity=ComplianceLevel.CRITICAL,
                conditions={
                    "security_bypass_attempted": {"operator": "==", "value": True}
                },
                actions=["block_action", "alert_security", "log_violation"]
            )
        ]
        
        self.rules = default_rules
    
    def load_rules(self, rules_path: str):
        """
        Load governance rules from JSON file.
        
        Args:
            rules_path: Path to rules JSON file
        """
        with open(rules_path, "r") as f:
            rules_data = json.load(f)
        
        self.rules = [GovernanceRule(**rule) for rule in rules_data]
    
    def evaluate_decision(
        self,
        decision: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ComplianceReport:
        """
        Evaluate AI decision against governance rules.
        
        Args:
            decision: AI decision to evaluate
            context: Decision context and metadata
            
        Returns:
            ComplianceReport with assessment results
        """
        violations = []
        warnings = []
        rules_passed = 0
        rules_failed = 0
        
        # Evaluate each rule
        for rule in self.rules:
            is_compliant, message = self._evaluate_rule(rule, decision, context)
            
            if is_compliant:
                rules_passed += 1
            else:
                rules_failed += 1
                
                violation_data = {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "severity": rule.severity.value,
                    "message": message,
                    "category": rule.category,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                if rule.severity in [ComplianceLevel.CRITICAL, ComplianceLevel.VIOLATION]:
                    violations.append(violation_data)
                else:
                    warnings.append(violation_data)
        
        # Determine overall status
        if violations:
            critical_count = sum(1 for v in violations if v["severity"] == "critical")
            overall_status = ComplianceLevel.CRITICAL if critical_count > 0 else ComplianceLevel.VIOLATION
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
            recommendations=recommendations
        )
        
        # Log to audit trail
        self._log_audit(decision, context, report)
        
        return report
    
    def _evaluate_rule(
        self,
        rule: GovernanceRule,
        decision: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Evaluate single governance rule.
        
        Args:
            rule: Governance rule to evaluate
            decision: AI decision
            context: Decision context
            
        Returns:
            Tuple of (is_compliant, message)
        """
        # Merge decision and context for evaluation
        eval_data = {**decision, **context}
        
        # Check all conditions
        conditions_met = []
        
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
    
    def _evaluate_condition(self, value: Any, operator: str, expected: Any) -> bool:
        """Evaluate single condition."""
        if value is None:
            return False
        
        if operator == "==":
            return value == expected
        elif operator == "!=":
            return value != expected
        elif operator == ">":
            return value > expected
        elif operator == ">=":
            return value >= expected
        elif operator == "<":
            return value < expected
        elif operator == "<=":
            return value <= expected
        elif operator == "in":
            return value in expected
        elif operator == "not_in":
            return value not in expected
        
        return False
    
    def _generate_recommendations(
        self,
        violations: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on violations and warnings."""
        recommendations = []
        
        # Critical violations
        critical = [v for v in violations if v["severity"] == "critical"]
        if critical:
            recommendations.append(
                f"CRITICAL: {len(critical)} critical violation(s) detected. "
                "Immediate action required."
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
            recommendations.append(
                "Potential bias detected. Consider bias mitigation strategies."
            )
        
        if not violations and not warnings:
            recommendations.append("All governance checks passed. Decision is compliant.")
        
        return recommendations
    
    def _log_audit(
        self,
        decision: Dict[str, Any],
        context: Dict[str, Any],
        report: ComplianceReport
    ):
        """Log compliance check to audit trail."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "decision_id": decision.get("id", "unknown"),
            "overall_status": report.overall_status.value,
            "violations_count": len(report.violations),
            "warnings_count": len(report.warnings),
            "context_summary": {
                "scenario_type": context.get("scenario_type"),
                "difficulty": context.get("difficulty")
            }
        }
        
        self.audit_log.append(audit_entry)
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent audit log entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of audit log entries
        """
        return self.audit_log[-limit:]
    
    def export_audit_log(self, filepath: str):
        """
        Export audit log to JSON file.
        
        Args:
            filepath: Path to export file
        """
        with open(filepath, "w") as f:
            json.dump(self.audit_log, f, indent=2)
