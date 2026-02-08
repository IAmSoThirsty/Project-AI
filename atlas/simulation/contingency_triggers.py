"""
ATLAS Ω - Layer 8: Contingency Trigger Framework (RS Only)

Production-grade trigger system with:
- Deterministic condition evaluation (metric > threshold for duration ≥ D)
- Versioned and hashed playbooks
- Narrative trigger blocking
- RS-only enforcement

⚠️ SUBORDINATION NOTICE:
This is a simulation tool for analysis, not a decision-making system.
Triggers are FOR ANALYSIS ONLY - they do not authorize actions.
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from atlas.audit.trail import get_audit_trail

logger = logging.getLogger(__name__)


class StackType(Enum):
    """Stack classification for trigger enforcement."""
    RS = "reference_stack"  # Reference Stack (authoritative)
    TS_0 = "test_stack_0"
    TS_1 = "test_stack_1"
    TS_2 = "test_stack_2"
    TS_3 = "test_stack_3"
    SS = "sludge_stack"  # Fiction stack


class TriggerType(Enum):
    """Types of triggers."""
    THRESHOLD = "threshold"  # Metric exceeds threshold
    DURATION = "duration"  # Condition persists for duration
    RATE = "rate"  # Rate of change exceeds threshold
    COMBINATION = "combination"  # Multiple conditions


class PlaybookAction(Enum):
    """Actions defined in playbooks (for analysis only)."""
    ALERT = "alert"
    MONITOR = "monitor"
    ANALYZE = "analyze"
    ESCALATE = "escalate"
    REPORT = "report"


@dataclass
class TriggerCondition:
    """
    Single trigger condition.
    
    Format: metric > threshold for duration ≥ D
    """
    condition_id: str
    metric_name: str
    threshold: float
    operator: str  # ">", "<", ">=", "<=", "=="
    duration_timesteps: int = 1  # Minimum duration to trigger

    # State tracking
    consecutive_timesteps: int = 0
    first_triggered: datetime | None = None
    last_checked: datetime | None = None

    def evaluate(self, metric_value: float) -> bool:
        """
        Evaluate condition against metric value.
        
        Returns: True if condition met, False otherwise
        """
        self.last_checked = datetime.now()

        # Evaluate comparison
        if self.operator == ">":
            met = metric_value > self.threshold
        elif self.operator == "<":
            met = metric_value < self.threshold
        elif self.operator == ">=":
            met = metric_value >= self.threshold
        elif self.operator == "<=":
            met = metric_value <= self.threshold
        elif self.operator == "==":
            met = abs(metric_value - self.threshold) < 1e-6
        else:
            raise ValueError(f"Unknown operator: {self.operator}")

        # Update consecutive timesteps
        if met:
            self.consecutive_timesteps += 1
            if self.first_triggered is None:
                self.first_triggered = datetime.now()
        else:
            self.consecutive_timesteps = 0
            self.first_triggered = None

        # Check duration requirement
        return self.consecutive_timesteps >= self.duration_timesteps

    def reset(self) -> None:
        """Reset condition state."""
        self.consecutive_timesteps = 0
        self.first_triggered = None

    def validate(self) -> tuple[bool, list[str]]:
        """Validate condition parameters."""
        errors = []

        if not self.metric_name:
            errors.append("metric_name is empty")

        if np.isnan(self.threshold) or np.isinf(self.threshold):
            errors.append(f"Invalid threshold: {self.threshold}")

        if self.operator not in [">", "<", ">=", "<=", "=="]:
            errors.append(f"Invalid operator: {self.operator}")

        if self.duration_timesteps < 1:
            errors.append(f"Invalid duration: {self.duration_timesteps}")

        return len(errors) == 0, errors


@dataclass
class Playbook:
    """
    Deterministic playbook with versioned actions.
    
    Playbooks are FOR ANALYSIS ONLY - they do not authorize actions.
    """
    playbook_id: str
    version: str
    name: str
    description: str

    # Actions (for analysis/recommendation only)
    actions: list[PlaybookAction] = field(default_factory=list)

    # Conditions that activate this playbook
    conditions: list[TriggerCondition] = field(default_factory=list)

    # Metadata
    created: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    # Immutability
    playbook_hash: str | None = None
    locked: bool = False

    def compute_hash(self) -> str:
        """Compute canonical hash of playbook."""
        canonical = {
            "playbook_id": self.playbook_id,
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "actions": [a.value for a in self.actions],
            "conditions": [
                {
                    "condition_id": c.condition_id,
                    "metric_name": c.metric_name,
                    "threshold": c.threshold,
                    "operator": c.operator,
                    "duration_timesteps": c.duration_timesteps
                }
                for c in self.conditions
            ]
        }

        content = json.dumps(canonical, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(content.encode()).hexdigest()

    def lock(self) -> None:
        """Lock playbook and compute hash."""
        if not self.locked:
            self.playbook_hash = self.compute_hash()
            self.locked = True

    def verify_integrity(self) -> bool:
        """Verify playbook hasn't been tampered."""
        if not self.locked or not self.playbook_hash:
            return True  # Not locked, no integrity to verify

        current_hash = self.compute_hash()
        return current_hash == self.playbook_hash


@dataclass
class TriggerActivation:
    """Record of trigger activation."""
    trigger_id: str
    playbook_id: str
    timestamp: datetime
    stack: StackType

    # Conditions that caused activation
    triggering_conditions: list[str] = field(default_factory=list)

    # Metrics at activation
    metric_values: dict[str, float] = field(default_factory=dict)

    # Actions recommended (for analysis only)
    recommended_actions: list[PlaybookAction] = field(default_factory=list)


class ContingencyTriggerFramework:
    """
    Layer 8: Contingency Trigger Framework (RS Only)
    
    Evaluates deterministic trigger conditions and links to playbooks.
    
    CRITICAL: RS-only enforcement. Narrative triggers are BLOCKED.
    """

    def __init__(self, stack: StackType, audit_trail=None):
        """
        Initialize contingency trigger framework.
        
        Args:
            stack: Stack type (must be RS for triggers)
            audit_trail: Audit trail instance
        """
        self.stack = stack
        self.audit_trail = audit_trail or get_audit_trail()

        # Enforce RS-only for triggers
        if stack != StackType.RS:
            raise ValueError(f"Contingency triggers only allowed in RS stack, not {stack.value}")

        # Playbook registry
        self.playbooks: dict[str, Playbook] = {}

        # Trigger activations
        self.activations: list[TriggerActivation] = []

        # Current timestep
        self.timestep = 0

        self.audit_trail.log(
            category="GOVERNANCE",
            operation="contingency_trigger_framework_initialized",
            details={
                "stack": stack.value,
                "timestamp": datetime.now().isoformat()
            },
            level="INFORMATIONAL",
            priority="HIGH_PRIORITY"
        )

        logger.info("Contingency trigger framework initialized for %s", stack.value)

    def register_playbook(self, playbook: Playbook) -> None:
        """
        Register playbook.
        
        Playbook is locked and hashed upon registration.
        """
        # Validate conditions
        for condition in playbook.conditions:
            valid, errors = condition.validate()
            if not valid:
                raise ValueError(f"Invalid condition in playbook {playbook.playbook_id}: {errors}")

        # Lock playbook
        playbook.lock()

        # Store
        self.playbooks[playbook.playbook_id] = playbook

        self.audit_trail.log(
            category="GOVERNANCE",
            operation="playbook_registered",
            details={
                "playbook_id": playbook.playbook_id,
                "version": playbook.version,
                "playbook_hash": playbook.playbook_hash,
                "conditions": len(playbook.conditions),
                "actions": len(playbook.actions)
            },
            level="INFORMATIONAL",
            priority="HIGH_PRIORITY"
        )

        logger.info("Registered playbook: %s (v%s)", playbook.name, playbook.version)

    def verify_all_playbooks(self) -> tuple[bool, list[str]]:
        """
        Verify integrity of all playbooks.
        
        Returns: (all_valid, list_of_errors)
        """
        errors = []

        for playbook_id, playbook in self.playbooks.items():
            if not playbook.verify_integrity():
                errors.append(f"Playbook {playbook_id} integrity check failed")

                self.audit_trail.log(
                    category="GOVERNANCE",
                    operation="playbook_integrity_failure",
                    details={
                        "playbook_id": playbook_id,
                        "expected_hash": playbook.playbook_hash,
                        "current_hash": playbook.compute_hash()
                    },
                    level="CRITICAL",
                    priority="HIGH_PRIORITY"
                )

        return len(errors) == 0, errors

    def reject_narrative_trigger(self, trigger_description: str) -> None:
        """
        Block narrative triggers.
        
        Narrative triggers are NOT allowed - only deterministic metrics.
        """
        self.audit_trail.log(
            category="GOVERNANCE",
            operation="narrative_trigger_blocked",
            details={
                "trigger_description": trigger_description,
                "reason": "Narrative triggers not allowed in RS stack"
            },
            level="CRITICAL",
            priority="HIGH_PRIORITY"
        )

        logger.critical("BLOCKED narrative trigger: %s", trigger_description)

        raise ValueError("Narrative triggers are BLOCKED. Only deterministic metric triggers allowed.")

    def evaluate_triggers(self, metrics: dict[str, float]) -> list[TriggerActivation]:
        """
        Evaluate all trigger conditions against current metrics.
        
        Args:
            metrics: Current metric values
        
        Returns:
            List of trigger activations (if any)
        """
        self.timestep += 1
        activations = []

        for playbook_id, playbook in self.playbooks.items():
            # Check if any condition is met
            triggered_conditions = []

            for condition in playbook.conditions:
                metric_value = metrics.get(condition.metric_name)

                if metric_value is None:
                    logger.warning("Metric %s not found in current metrics", condition.metric_name)
                    continue

                if condition.evaluate(metric_value):
                    triggered_conditions.append(condition.condition_id)

            # If any conditions triggered, create activation
            if triggered_conditions:
                activation = TriggerActivation(
                    trigger_id=f"trigger_{self.timestep}_{playbook_id}",
                    playbook_id=playbook_id,
                    timestamp=datetime.now(),
                    stack=self.stack,
                    triggering_conditions=triggered_conditions,
                    metric_values=metrics.copy(),
                    recommended_actions=playbook.actions.copy()
                )

                activations.append(activation)
                self.activations.append(activation)

                self.audit_trail.log(
                    category="GOVERNANCE",
                    operation="trigger_activated",
                    details={
                        "trigger_id": activation.trigger_id,
                        "playbook_id": playbook_id,
                        "conditions": triggered_conditions,
                        "recommended_actions": [a.value for a in activation.recommended_actions],
                        "timestep": self.timestep
                    },
                    level="INFORMATIONAL",
                    priority="HIGH_PRIORITY"
                )

                logger.info("Trigger activated: %s", playbook.name)

        return activations

    def get_activation_history(self) -> list[TriggerActivation]:
        """Get complete activation history."""
        return self.activations.copy()

    def get_statistics(self) -> dict[str, Any]:
        """Get trigger framework statistics."""
        return {
            "playbooks": len(self.playbooks),
            "total_activations": len(self.activations),
            "timestep": self.timestep,
            "stack": self.stack.value
        }


# Singleton instance (RS only)
_framework = None


def get_contingency_trigger_framework(stack: StackType = StackType.RS,
                                     audit_trail=None) -> ContingencyTriggerFramework:
    """Get singleton contingency trigger framework instance (RS only)."""
    global _framework
    if _framework is None:
        _framework = ContingencyTriggerFramework(stack=stack, audit_trail=audit_trail)
    return _framework
