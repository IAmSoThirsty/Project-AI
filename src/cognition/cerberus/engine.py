"""
Cerberus Engine - Policy Enforcement and Output Validation

Provides policy abstraction for:
- Pre-persistence validation
- Output enforcement
- Security checks
- Production-ready allow-all default
"""

import logging
from dataclasses import dataclass
from typing import Any

from src.cognition.adapters.policy_engine import PolicyDecision, PolicyEngine

logger = logging.getLogger(__name__)


@dataclass
class CerberusConfig:
    """Configuration for Cerberus engine."""

    mode: str = "production"  # 'production', 'strict', 'custom'
    enforce_on_input: bool = False
    enforce_on_output: bool = True
    block_on_deny: bool = True


class CerberusEngine:
    """
    Policy enforcement and validation engine.

    Features:
    - Configurable policy enforcement
    - Pre-persistence validation
    - Output sanitization
    - Production allow-all default
    """

    def __init__(self, config: CerberusConfig | None = None):
        """
        Initialize Cerberus engine.

        Args:
            config: Engine configuration
        """
        self.config = config or CerberusConfig()

        # Initialize policy engine
        self.policy_engine = PolicyEngine(mode=self.config.mode)

        self.enforcement_count = 0
        self.denied_count = 0
        self.modified_count = 0

        logger.info("Cerberus engine initialized")
        logger.info(f"Config: {self.config}")
        logger.info(f"Policy mode: {self.config.mode}")

    def validate_input(self, input_data: Any, context: dict | None = None) -> dict:
        """
        Validate input data before processing.

        Args:
            input_data: Input to validate
            context: Optional context dictionary

        Returns:
            Validation result
        """
        if not self.config.enforce_on_input:
            return {
                "valid": True,
                "input": input_data,
                "reason": "Input validation disabled",
            }

        logger.info("Validating input")
        self.enforcement_count += 1

        try:
            result = self.policy_engine.enforce(input_data, context)

            if result.decision == PolicyDecision.DENY:
                self.denied_count += 1
                if self.config.block_on_deny:
                    return {
                        "valid": False,
                        "input": None,
                        "reason": result.reason,
                        "warnings": result.warnings,
                    }

            if result.decision == PolicyDecision.MODIFY:
                self.modified_count += 1
                return {
                    "valid": True,
                    "input": result.modified_output,
                    "reason": result.reason,
                    "modified": True,
                    "warnings": result.warnings,
                }

            return {
                "valid": True,
                "input": input_data,
                "reason": result.reason,
                "warnings": result.warnings,
            }

        except Exception as e:
            logger.error(f"Input validation error: {e}")
            return {"valid": False, "input": None, "reason": f"Validation error: {e}"}

    def enforce_output(self, output_data: Any, context: dict | None = None) -> dict:
        """
        Enforce policies on output before delivery/persistence.

        Args:
            output_data: Output to enforce policies on
            context: Optional context dictionary

        Returns:
            Enforcement result
        """
        if not self.config.enforce_on_output:
            return {
                "allowed": True,
                "output": output_data,
                "reason": "Output enforcement disabled",
            }

        logger.info("Enforcing output policies")
        self.enforcement_count += 1

        try:
            result = self.policy_engine.enforce(output_data, context)

            if result.decision == PolicyDecision.DENY:
                self.denied_count += 1
                if self.config.block_on_deny:
                    return {
                        "allowed": False,
                        "output": None,
                        "reason": result.reason,
                        "warnings": result.warnings,
                    }

            if result.decision == PolicyDecision.MODIFY:
                self.modified_count += 1
                return {
                    "allowed": True,
                    "output": result.modified_output,
                    "reason": result.reason,
                    "modified": True,
                    "warnings": result.warnings,
                }

            return {
                "allowed": True,
                "output": output_data,
                "reason": result.reason,
                "warnings": result.warnings,
            }

        except Exception as e:
            logger.error(f"Output enforcement error: {e}")
            return {"allowed": False, "output": None, "reason": f"Enforcement error: {e}"}

    def check_pre_persistence(self, data: Any, context: dict | None = None) -> dict:
        """
        Check data before persistence (database, file, etc.).

        Args:
            data: Data to check before persistence
            context: Optional context dictionary

        Returns:
            Pre-persistence check result
        """
        logger.info("Pre-persistence check")

        # Run output enforcement
        result = self.enforce_output(data, context)

        # Add persistence-specific metadata
        result["persistence_approved"] = result.get("allowed", False)

        return result

    def get_statistics(self) -> dict:
        """Get enforcement statistics."""
        return {
            "total_enforcements": self.enforcement_count,
            "denied_count": self.denied_count,
            "modified_count": self.modified_count,
            "policy_mode": self.config.mode,
            "policy_info": self.policy_engine.get_policy_info(),
        }

    def add_custom_policy(self, policy):
        """
        Add a custom policy to the engine.

        Args:
            policy: Policy instance implementing Policy interface
        """
        self.policy_engine.add_policy(policy)
        logger.info(f"Added custom policy: {policy.__class__.__name__}")

    def reset_statistics(self):
        """Reset enforcement statistics."""
        self.enforcement_count = 0
        self.denied_count = 0
        self.modified_count = 0
        logger.info("Statistics reset")
