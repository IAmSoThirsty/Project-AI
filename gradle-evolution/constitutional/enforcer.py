"""
Constitutional Enforcer
========================

Integrates Project-AI's PolicyEngine with Gradle build enforcement.
Validates build actions against constitutional policies and identity-aware constraints.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from project_ai.engine.policy.policy_engine import PolicyEngine
from project_ai.engine.identity.identity_manager import IdentityManager

logger = logging.getLogger(__name__)


class BuildActionViolation(Exception):
    """Raised when a build action violates constitutional policy."""
    pass


class ConstitutionalEnforcer:
    """
    Enforces constitutional constraints on Gradle build actions.
    Integrates PolicyEngine for identity-aware policy enforcement.
    """

    def __init__(
        self,
        identity_manager: IdentityManager,
        config_path: Optional[Path] = None
    ):
        """
        Initialize constitutional enforcer.

        Args:
            identity_manager: Project-AI identity manager
            config_path: Optional path to additional policy configuration
        """
        self.policy_engine = PolicyEngine(identity_manager)
        self.identity_manager = identity_manager
        self.config_path = config_path
        self.violation_history: List[Dict[str, Any]] = []
        
        # Build-specific policy extensions
        self.build_policies = {
            "bootstrap": {
                "allow_network_access": False,
                "allow_file_write": False,
                "allow_plugin_execution": False,
                "max_build_tasks": 10,
            },
            "bonded": {
                "allow_network_access": True,
                "allow_file_write": True,
                "allow_plugin_execution": True,
                "max_build_tasks": -1,  # unlimited
            },
        }
        
        logger.info("Constitutional enforcer initialized")

    def validate_build_action(
        self,
        action: str,
        metadata: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a build action against constitutional policies.

        Args:
            action: Action identifier (e.g., "task:compile", "plugin:apply")
            metadata: Action metadata including risk_level, requires_external, etc.

        Returns:
            Tuple of (is_valid, reason). reason is None if valid.
        """
        try:
            # Refresh policy from identity phase
            self.policy_engine.refresh_from_identity()
            policy_context = self.policy_engine.get_policy_context()
            
            # Check capability-level policy
            if not self.policy_engine.is_capability_allowed(metadata):
                reason = (
                    f"Action '{action}' denied by policy engine. "
                    f"Phase: {policy_context['phase']}, "
                    f"Risk: {metadata.get('risk_level', 'unknown')}"
                )
                self._record_violation(action, metadata, reason)
                return False, reason
            
            # Check build-specific policies
            mode = self.policy_engine.policy_mode
            build_rules = self.build_policies[mode]
            
            if metadata.get("requires_network") and not build_rules["allow_network_access"]:
                reason = f"Network access denied in {mode} mode"
                self._record_violation(action, metadata, reason)
                return False, reason
            
            if metadata.get("requires_file_write") and not build_rules["allow_file_write"]:
                reason = f"File write access denied in {mode} mode"
                self._record_violation(action, metadata, reason)
                return False, reason
            
            if metadata.get("is_plugin") and not build_rules["allow_plugin_execution"]:
                reason = f"Plugin execution denied in {mode} mode"
                self._record_violation(action, metadata, reason)
                return False, reason
            
            logger.debug(f"Build action '{action}' validated successfully")
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating build action '{action}': {e}", exc_info=True)
            return False, f"Validation error: {str(e)}"

    def enforce_task_limit(self, task_count: int) -> Tuple[bool, Optional[str]]:
        """
        Enforce maximum task count based on current policy mode.

        Args:
            task_count: Number of tasks to execute

        Returns:
            Tuple of (is_allowed, reason)
        """
        try:
            mode = self.policy_engine.policy_mode
            max_tasks = self.build_policies[mode]["max_build_tasks"]
            
            if max_tasks == -1:
                return True, None
            
            if task_count > max_tasks:
                reason = f"Task count {task_count} exceeds limit {max_tasks} in {mode} mode"
                logger.warning(reason)
                return False, reason
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error enforcing task limit: {e}", exc_info=True)
            return False, f"Task limit enforcement error: {str(e)}"

    def validate_batch_actions(
        self,
        actions: List[Tuple[str, Dict[str, Any]]]
    ) -> Dict[str, Tuple[bool, Optional[str]]]:
        """
        Validate multiple build actions in batch.

        Args:
            actions: List of (action, metadata) tuples

        Returns:
            Dictionary mapping action to (is_valid, reason) result
        """
        results = {}
        for action, metadata in actions:
            results[action] = self.validate_build_action(action, metadata)
        return results

    def get_policy_summary(self) -> Dict[str, Any]:
        """
        Get current policy configuration summary.

        Returns:
            Dictionary with policy context and build rules
        """
        try:
            self.policy_engine.refresh_from_identity()
            policy_context = self.policy_engine.get_policy_context()
            mode = self.policy_engine.policy_mode
            
            return {
                "identity_phase": policy_context["phase"],
                "policy_mode": mode,
                "core_rules": policy_context["rules"],
                "build_rules": self.build_policies[mode],
                "violation_count": len(self.violation_history),
            }
        except Exception as e:
            logger.error(f"Error getting policy summary: {e}", exc_info=True)
            return {"error": str(e)}

    def _record_violation(
        self,
        action: str,
        metadata: Dict[str, Any],
        reason: str
    ) -> None:
        """
        Record a policy violation for audit purposes.

        Args:
            action: Action that was denied
            metadata: Action metadata
            reason: Reason for denial
        """
        from datetime import datetime
        
        violation = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "metadata": metadata,
            "reason": reason,
            "identity_phase": self.identity_manager.get_identity_phase(),
        }
        self.violation_history.append(violation)
        logger.warning(f"Policy violation recorded: {reason}")

    def get_violations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent policy violations.

        Args:
            limit: Maximum number of violations to return

        Returns:
            List of recent violations
        """
        return self.violation_history[-limit:]

    def clear_violations(self) -> int:
        """
        Clear violation history.

        Returns:
            Number of violations cleared
        """
        count = len(self.violation_history)
        self.violation_history.clear()
        logger.info(f"Cleared {count} violations")
        return count


__all__ = ["ConstitutionalEnforcer", "BuildActionViolation"]
