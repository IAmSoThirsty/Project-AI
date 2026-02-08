"""
Constitutional Engine - Enforces constitutional principles during builds
"""

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ConstitutionalEngine:
    """
    Enforces constitutional principles from policies/constitution.yaml
    during Gradle build lifecycle events.
    
    Integrates with existing Project-AI governance infrastructure.
    """

    def __init__(self, constitution_path: str = "policies/constitution.yaml"):
        """
        Initialize constitutional engine.
        
        Args:
            constitution_path: Path to constitution.yaml file
        """
        self.constitution_path = Path(constitution_path)
        self.constitution: dict[str, Any] = {}
        self.violation_log: list[dict[str, Any]] = []
        self.load_constitution()

    def load_constitution(self) -> None:
        """Load constitutional principles from YAML."""
        if not self.constitution_path.exists():
            logger.warning("Constitution file not found: %s", self.constitution_path)
            self.constitution = self._get_default_constitution()
            return

        with open(self.constitution_path) as f:
            self.constitution = yaml.safe_load(f)

        logger.info("Loaded constitution: %s", self.constitution.get('name', 'unknown'))
        logger.info("Principles: %s", len(self.constitution.get('principles', [])))

    def _get_default_constitution(self) -> dict[str, Any]:
        """Provide default constitution if file missing."""
        return {
            "name": "default_constitution",
            "version": "1.0.0",
            "principles": [],
            "enforcement_levels": {
                "critical": {"action": "block", "log": True},
                "high": {"action": "warn_and_modify", "log": True},
                "medium": {"action": "warn", "log": True},
                "low": {"action": "log_only", "log": True},
            }
        }

    def validate_build_action(
        self,
        action: str,
        context: dict[str, Any]
    ) -> tuple[bool, str]:
        """
        Validate a build action against constitutional principles.
        
        Args:
            action: Build action to validate (e.g., "compile", "test", "deploy")
            context: Action context with metadata
            
        Returns:
            (is_allowed, reason) tuple
        """
        # Check for critical violations
        enforcement = self.constitution.get("enforcement_levels", {})
        violations = context.get("violations", [])

        for violation_type in violations:
            if violation_type in self.constitution.get("violation_handling", {}).get("immediate_block", []):
                reason = f"Constitutional violation: {violation_type} (immediate block)"
                self._log_violation(action, context, "critical", reason)
                return False, reason

        # Check principle compliance
        principles = self.constitution.get("principles", [])
        for principle in principles:
            priority = principle.get("priority", "medium")
            principle_id = principle.get("id", "unknown")

            # Check if action violates this principle
            if self._violates_principle(action, context, principle):
                enforcement_rule = enforcement.get(priority, {})
                action_type = enforcement_rule.get("action", "log_only")

                if action_type == "block":
                    reason = f"Violates principle: {principle_id} (priority: {priority})"
                    self._log_violation(action, context, priority, reason)
                    return False, reason
                elif action_type in ["warn_and_modify", "warn"]:
                    reason = f"Warning: Action may violate principle {principle_id}"
                    self._log_violation(action, context, priority, reason)

        return True, "Action complies with constitutional principles"

    def _violates_principle(
        self,
        action: str,
        context: dict[str, Any],
        principle: dict[str, Any]
    ) -> bool:
        """Check if an action violates a specific principle."""
        principle_id = principle.get("id", "")

        if principle_id == "non_maleficence":
            return context.get("causes_harm", False)
        elif principle_id == "transparency":
            return not context.get("is_transparent", True)
        elif principle_id == "accountability":
            return not context.get("has_audit_trail", True)
        elif principle_id == "autonomy_respect":
            return context.get("bypasses_human_control", False)

        return False

    def _log_violation(
        self,
        action: str,
        context: dict[str, Any],
        severity: str,
        reason: str
    ) -> None:
        """Log a constitutional violation."""
        from datetime import datetime
        violation = {
            "action": action,
            "context": context,
            "severity": severity,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.violation_log.append(violation)
        logger.warning("Constitutional violation: %s", reason)

    def get_violations(self) -> list[dict[str, Any]]:
        """Get all logged violations."""
        return self.violation_log


__all__ = ["ConstitutionalEngine"]
