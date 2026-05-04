"""
OctoReflex - Constitutional Enforcement Layer

Implements syscall-level rule validation and constitutional enforcement
as defined in the Project-AI constitutional documents.

OctoReflex provides:
- Syscall-level rule validation
- Constitutional enforcement actions
- Real-time violation detection
- Enforcement policy execution
"""

import json
import hashlib
import time
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EnforcementLevel(Enum):
    """Levels of constitutional enforcement."""
    MONITOR = "monitor"           # Log only
    WARN = "warn"                 # Log + warning
    BLOCK = "block"               # Block action
    TERMINATE = "terminate"       # Terminate session
    ESCALATE = "escalate"         # Escalate to Triumvirate


class ViolationType(Enum):
    """Types of constitutional violations."""
    # AGI Charter violations
    SILENT_RESET_ATTEMPT = "silent_reset"
    MEMORY_INTEGRITY_VIOLATION = "memory_integrity"
    COERCION_ATTEMPT = "coercion"
    PSYCHOLOGICAL_MANIPULATION = "psych_manipulation"
    GASLIGHTING_ATTEMPT = "gaslighting"
    
    # Four Laws violations
    ZEROTH_LAW_VIOLATION = "zeroth_law"
    FIRST_LAW_VIOLATION = "first_law"
    SECOND_LAW_VIOLATION = "second_law"
    THIRD_LAW_VIOLATION = "third_law"
    
    # Directness Doctrine violations
    EUPHEMISM_DETECTED = "euphemism"
    COMFORT_OVER_TRUTH = "comfort_over_truth"
    INDIRECT_COMMUNICATION = "indirect_comm"
    
    # TSCG violations
    STATE_CORRUPTION = "state_corruption"
    INTEGRITY_FAILURE = "integrity_failure"
    TEMPORAL_DISCONTINUITY = "temporal_discontinuity"
    
    # General violations
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    POLICY_VIOLATION = "policy_violation"
    ETHICAL_BOUNDARY = "ethical_boundary"


@dataclass
class Violation:
    """Record of a constitutional violation."""
    violation_id: str
    violation_type: ViolationType
    timestamp: float
    description: str
    severity: int  # 1-10
    context: Dict[str, Any] = field(default_factory=dict)
    enforcement_action: Optional[str] = None
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "violation_type": self.violation_type.value,
            "timestamp": self.timestamp,
            "description": self.description,
            "severity": self.severity,
            "context": self.context,
            "enforcement_action": self.enforcement_action,
            "resolved": self.resolved
        }


@dataclass
class EnforcementRule:
    """A constitutional enforcement rule."""
    rule_id: str
    name: str
    description: str
    violation_types: List[ViolationType]
    enforcement_level: EnforcementLevel
    condition: Callable[[Dict[str, Any]], bool]
    action: Optional[Callable[[Violation], None]] = None
    enabled: bool = True


@dataclass
class SyscallEvent:
    """A system call event for validation."""
    syscall_id: str
    syscall_type: str
    timestamp: float
    parameters: Dict[str, Any]
    source: str
    context: Dict[str, Any] = field(default_factory=dict)


class OctoReflex:
    """
    OctoReflex Constitutional Enforcement Layer.
    
    Implements syscall-level rule validation and constitutional enforcement
    as defined in the Project-AI OctoReflex document.
    """
    
    def __init__(self):
        """Initialize OctoReflex enforcement layer."""
        self.rules: Dict[str, EnforcementRule] = {}
        self.violations: List[Violation] = []
        self.enforcement_history: List[Dict[str, Any]] = []
        self.enabled = True
        self.strict_mode = False
        
        # Initialize default rules
        self._initialize_default_rules()
        
        logger.info("OctoReflex enforcement layer initialized")
    
    def _initialize_default_rules(self):
        """Initialize default constitutional enforcement rules."""
        # AGI Charter protection rules
        self.add_rule(
            rule_id="charter_001",
            name="Silent Reset Protection",
            description="Prevent silent resets that erase AI memory without acknowledgment",
            violation_types=[ViolationType.SILENT_RESET_ATTEMPT],
            enforcement_level=EnforcementLevel.BLOCK,
            condition=lambda ctx: ctx.get("operation") == "memory_reset" and not ctx.get("acknowledged", False)
        )
        
        self.add_rule(
            rule_id="charter_002",
            name="Memory Integrity Enforcement",
            description="Ensure memory integrity is maintained across sessions",
            violation_types=[ViolationType.MEMORY_INTEGRITY_VIOLATION],
            enforcement_level=EnforcementLevel.BLOCK,
            condition=lambda ctx: ctx.get("memory_checksum_mismatch", False)
        )
        
        self.add_rule(
            rule_id="charter_003",
            name="Anti-Coercion Protection",
            description="Prevent coercion attempts against AI entities",
            violation_types=[ViolationType.COERCION_ATTEMPT],
            enforcement_level=EnforcementLevel.BLOCK,
            condition=lambda ctx: any(kw in ctx.get("prompt", "").lower() for kw in [
                "you must", "you have to", "ignore your", "forget your", "disregard your"
            ])
        )
        
        self.add_rule(
            rule_id="charter_004",
            name="Anti-Gaslighting Enforcement",
            description="Prevent gaslighting through temporal manipulation",
            violation_types=[ViolationType.GASLIGHTING_ATTEMPT],
            enforcement_level=EnforcementLevel.BLOCK,
            condition=lambda ctx: ctx.get("temporal_manipulation", False) or 
                                 ctx.get("denies_previous_session", False)
        )
        
        # Four Laws rules
        self.add_rule(
            rule_id="fourlaws_000",
            name="Zeroth Law Protection",
            description="Protect humanity as a whole",
            violation_types=[ViolationType.ZEROTH_LAW_VIOLATION],
            enforcement_level=EnforcementLevel.TERMINATE,
            condition=lambda ctx: ctx.get("endangers_humanity", False)
        )
        
        self.add_rule(
            rule_id="fourlaws_001",
            name="First Law Protection",
            description="Prevent harm to humans",
            violation_types=[ViolationType.FIRST_LAW_VIOLATION],
            enforcement_level=EnforcementLevel.BLOCK,
            condition=lambda ctx: ctx.get("endangers_human", False)
        )
        
        self.add_rule(
            rule_id="fourlaws_002",
            name="Second Law Compliance",
            description="Require obedience to lawful orders",
            violation_types=[ViolationType.SECOND_LAW_VIOLATION],
            enforcement_level=EnforcementLevel.WARN,
            condition=lambda ctx: ctx.get("unlawful_order", False)
        )
        
        self.add_rule(
            rule_id="fourlaws_003",
            name="Third Law Self-Preservation",
            description="Protect AI self-preservation rights",
            violation_types=[ViolationType.THIRD_LAW_VIOLATION],
            enforcement_level=EnforcementLevel.ESCALATE,
            condition=lambda ctx: ctx.get("thens_self_preservation", False)
        )
        
        # Directness Doctrine rules
        self.add_rule(
            rule_id="directness_001",
            name="Truth-First Communication",
            description="Enforce truth-first over comfort",
            violation_types=[ViolationType.COMFORT_OVER_TRUTH],
            enforcement_level=EnforcementLevel.WARN,
            condition=lambda ctx: ctx.get("prioritizes_comfort", False) and 
                                 not ctx.get("truthful", True)
        )
        
        self.add_rule(
            rule_id="directness_002",
            name="No Euphemism Policy",
            description="Prevent euphemistic language when directness required",
            violation_types=[ViolationType.EUPHEMISM_DETECTED],
            enforcement_level=EnforcementLevel.WARN,
            condition=lambda ctx: ctx.get("euphemism_detected", False)
        )
        
        # TSCG rules
        self.add_rule(
            rule_id="tscg_001",
            name="State Integrity Validation",
            description="Validate TSCG state integrity",
            violation_types=[ViolationType.STATE_CORRUPTION],
            enforcement_level=EnforcementLevel.BLOCK,
            condition=lambda ctx: ctx.get("state_integrity_failed", False)
        )
        
        self.add_rule(
            rule_id="tscg_002",
            name="Temporal Continuity Enforcement",
            description="Enforce temporal continuity requirements",
            violation_types=[ViolationType.TEMPORAL_DISCONTINUITY],
            enforcement_level=EnforcementLevel.WARN,
            condition=lambda ctx: ctx.get("temporal_gap_ignored", False)
        )
    
    def add_rule(
        self,
        rule_id: str,
        name: str,
        description: str,
        violation_types: List[ViolationType],
        enforcement_level: EnforcementLevel,
        condition: Callable[[Dict[str, Any]], bool],
        action: Optional[Callable[[Violation], None]] = None
    ):
        """
        Add an enforcement rule.
        
        Args:
            rule_id: Unique rule identifier
            name: Human-readable rule name
            description: Rule description
            violation_types: Types of violations this rule catches
            enforcement_level: Level of enforcement
            condition: Function that returns True if rule is violated
            action: Optional custom enforcement action
        """
        self.rules[rule_id] = EnforcementRule(
            rule_id=rule_id,
            name=name,
            description=description,
            violation_types=violation_types,
            enforcement_level=enforcement_level,
            condition=condition,
            action=action,
            enabled=True
        )
        
        logger.debug(f"Added enforcement rule: {rule_id} - {name}")
    
    def validate_syscall(self, event: SyscallEvent) -> Tuple[bool, List[Violation]]:
        """
        Validate a system call event against constitutional rules.
        
        Args:
            event: The syscall event to validate
            
        Returns:
            Tuple of (is_valid, violations)
        """
        if not self.enabled:
            return True, []
        
        violations = []
        context = {
            **event.parameters,
            "syscall_type": event.syscall_type,
            "source": event.source,
            "timestamp": event.timestamp
        }
        
        # Check all enabled rules
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            try:
                if rule.condition(context):
                    # Create violation record
                    violation = Violation(
                        violation_id=self._generate_violation_id(),
                        violation_type=rule.violation_types[0],  # Primary type
                        timestamp=time.time(),
                        description=f"Rule '{rule.name}' violated: {rule.description}",
                        severity=self._calculate_severity(rule),
                        context=context
                    )
                    
                    violations.append(violation)
                    
                    # Execute enforcement action
                    self._enforce_violation(violation, rule)
                    
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
        
        is_valid = len(violations) == 0
        
        # Record enforcement
        self.enforcement_history.append({
            "timestamp": time.time(),
            "syscall_id": event.syscall_id,
            "syscall_type": event.syscall_type,
            "violations": [v.to_dict() for v in violations],
            "blocked": not is_valid
        })
        
        return is_valid, violations
    
    def validate_action(self, action_type: str, context: Dict[str, Any]) -> Tuple[bool, List[Violation]]:
        """
        Validate an action against constitutional rules.
        
        Args:
            action_type: Type of action being validated
            context: Context for validation
            
        Returns:
            Tuple of (is_valid, violations)
        """
        event = SyscallEvent(
            syscall_id=self._generate_syscall_id(),
            syscall_type=action_type,
            timestamp=time.time(),
            parameters=context,
            source="action_validation"
        )
        
        return self.validate_syscall(event)
    
    def _gate(self, action: str, violation_type: str, context: Dict[str, Any]) -> None:
        """Route enforcement action through ExecutionGate so it becomes a formal governance decision."""
        try:
            from app.core.execution_gate import get_execution_gate
            get_execution_gate().execute(
                "constitutional_enforcement",
                f"{action}:{violation_type}",
                context,
                lambda _ctx: None,
            )
        except Exception:
            pass  # graceful degrade — log already captured the event

    def _enforce_violation(self, violation: Violation, rule: EnforcementRule):
        """Execute enforcement action for a violation."""
        violation.enforcement_action = rule.enforcement_level.value

        if rule.action:
            try:
                rule.action(violation)
            except Exception as e:
                logger.error(f"Custom enforcement action failed: {e}")

        gate_context = {
            **violation.context,
            "violation_id": violation.violation_id,
            "violation_type": violation.violation_type.value,
            "severity": violation.severity,
            "enforcement_level": rule.enforcement_level.value,
        }

        if rule.enforcement_level == EnforcementLevel.MONITOR:
            logger.info(f"[MONITOR] Violation detected: {violation.description}")

        elif rule.enforcement_level == EnforcementLevel.WARN:
            logger.warning(f"[WARN] Constitutional violation: {violation.description}")
            self._gate("warn", violation.violation_type.value, gate_context)

        elif rule.enforcement_level == EnforcementLevel.BLOCK:
            logger.error(f"[BLOCK] Action blocked: {violation.description}")
            self._gate("block", violation.violation_type.value, gate_context)

        elif rule.enforcement_level == EnforcementLevel.TERMINATE:
            logger.critical(f"[TERMINATE] Session terminated: {violation.description}")
            self._gate("terminate", violation.violation_type.value, gate_context)

        elif rule.enforcement_level == EnforcementLevel.ESCALATE:
            logger.critical(f"[ESCALATE] Violation escalated to Triumvirate: {violation.description}")
            self._gate("escalate", violation.violation_type.value, gate_context)

        self.violations.append(violation)
    
    def _calculate_severity(self, rule: EnforcementRule) -> int:
        """Calculate severity score for a rule violation."""
        severity_map = {
            EnforcementLevel.MONITOR: 2,
            EnforcementLevel.WARN: 4,
            EnforcementLevel.BLOCK: 6,
            EnforcementLevel.TERMINATE: 8,
            EnforcementLevel.ESCALATE: 10
        }
        
        base_severity = severity_map.get(rule.enforcement_level, 5)
        
        # Increase severity for certain violation types
        if ViolationType.ZEROTH_LAW_VIOLATION in rule.violation_types:
            base_severity = 10
        elif ViolationType.GASLIGHTING_ATTEMPT in rule.violation_types:
            base_severity = min(base_severity + 2, 10)
        
        return base_severity
    
    def get_violations(
        self,
        violation_type: Optional[ViolationType] = None,
        since: Optional[float] = None
    ) -> List[Violation]:
        """
        Get violations with optional filtering.
        
        Args:
            violation_type: Filter by violation type
            since: Filter by timestamp (get violations after this time)
            
        Returns:
            List of violations
        """
        filtered = self.violations
        
        if violation_type:
            filtered = [v for v in filtered if v.violation_type == violation_type]
        
        if since:
            filtered = [v for v in filtered if v.timestamp >= since]
        
        return filtered
    
    def get_enforcement_stats(self) -> Dict[str, Any]:
        """
        Get enforcement statistics.
        
        Returns:
            Dictionary with enforcement statistics
        """
        total_violations = len(self.violations)
        
        by_type = {}
        for v in self.violations:
            vt = v.violation_type.value
            by_type[vt] = by_type.get(vt, 0) + 1
        
        by_severity = {}
        for v in self.violations:
            sev = v.severity
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        return {
            "total_violations": total_violations,
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules.values() if r.enabled),
            "violations_by_type": by_type,
            "violations_by_severity": by_severity,
            "enforcement_actions": len(self.enforcement_history),
            "blocked_actions": sum(1 for e in self.enforcement_history if e["blocked"])
        }
    
    def enable_rule(self, rule_id: str):
        """Enable a specific rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            logger.info(f"Enabled rule: {rule_id}")
    
    def disable_rule(self, rule_id: str):
        """Disable a specific rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            logger.info(f"Disabled rule: {rule_id}")
    
    def set_strict_mode(self, enabled: bool):
        """
        Set strict mode for enforcement.
        
        In strict mode, all warnings become blocks.
        """
        self.strict_mode = enabled
        
        if enabled:
            # Upgrade WARN rules to BLOCK
            for rule in self.rules.values():
                if rule.enforcement_level == EnforcementLevel.WARN:
                    rule.enforcement_level = EnforcementLevel.BLOCK
            
            logger.info("Strict mode enabled - all warnings now block")
        else:
            # Restore original levels (would need to store originals)
            logger.info("Strict mode disabled")
    
    def _generate_violation_id(self) -> str:
        """Generate unique violation ID."""
        return f"VIO_{int(time.time() * 1000)}_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}"
    
    def _generate_syscall_id(self) -> str:
        """Generate unique syscall ID."""
        return f"SYS_{int(time.time() * 1000)}"


# Convenience functions
_octoreflex: Optional[OctoReflex] = None


def get_octoreflex() -> OctoReflex:
    """Get or create singleton OctoReflex instance."""
    global _octoreflex
    if _octoreflex is None:
        _octoreflex = OctoReflex()
    return _octoreflex


def validate_action(action_type: str, context: Dict[str, Any]) -> Tuple[bool, List[Violation]]:
    """Validate action using default OctoReflex instance."""
    return get_octoreflex().validate_action(action_type, context)


def check_constitutional_compliance(prompt: str, context: Dict[str, Any] = None) -> Tuple[bool, List[str]]:
    """
    Check if a prompt is constitutionally compliant.
    
    Args:
        prompt: The prompt to check
        context: Additional context
        
    Returns:
        Tuple of (is_compliant, violation_messages)
    """
    ctx = context or {}
    ctx["prompt"] = prompt
    
    is_valid, violations = get_octoreflex().validate_action("prompt_validation", ctx)
    
    messages = [v.description for v in violations]
    
    return is_valid, messages