"""
Policy Engine - Pre-persistence and Output Enforcement

Implements policy abstraction for validating and enforcing
constraints on AI outputs before persistence or delivery.
Default: allow-all for production (can be customized).
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class PolicyDecision(Enum):
    """Policy decision outcomes."""

    ALLOW = "allow"
    DENY = "deny"
    MODIFY = "modify"
    WARN = "warn"


@dataclass
class PolicyResult:
    """Result of policy evaluation."""

    decision: PolicyDecision
    reason: str
    modified_output: Any | None = None
    warnings: list[str] | None = None


class Policy(ABC):
    """Abstract base class for policies."""

    @abstractmethod
    def evaluate(self, output: Any, context: dict | None = None) -> PolicyResult:
        """
        Evaluate output against policy.

        Args:
            output: Output to evaluate
            context: Optional context information

        Returns:
            PolicyResult with decision and details
        """
        pass


class AllowAllPolicy(Policy):
    """Production default: allows all outputs."""

    def evaluate(self, output: Any, context: dict | None = None) -> PolicyResult:
        """Allow all outputs."""
        return PolicyResult(decision=PolicyDecision.ALLOW, reason="Allow-all policy")


class ContentFilterPolicy(Policy):
    """Filter outputs based on content rules."""

    def __init__(self, blocked_patterns: list[str] | None = None):
        """
        Initialize content filter.

        Args:
            blocked_patterns: List of regex patterns to block
        """
        self.blocked_patterns = blocked_patterns or []

    def evaluate(self, output: Any, context: dict | None = None) -> PolicyResult:
        """Check output against blocked patterns."""
        import re

        output_str = str(output)

        for pattern in self.blocked_patterns:
            if re.search(pattern, output_str, re.IGNORECASE):
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason=f"Blocked by pattern: {pattern}",
                )

        return PolicyResult(decision=PolicyDecision.ALLOW, reason="No violations found")


class LengthLimitPolicy(Policy):
    """Enforce output length limits."""

    def __init__(self, max_length: int = 10000):
        """
        Initialize length limit policy.

        Args:
            max_length: Maximum allowed output length
        """
        self.max_length = max_length

    def evaluate(self, output: Any, context: dict | None = None) -> PolicyResult:
        """Check output length."""
        output_str = str(output)

        if len(output_str) > self.max_length:
            truncated = output_str[: self.max_length] + "... [truncated]"
            return PolicyResult(
                decision=PolicyDecision.MODIFY,
                reason=f"Output exceeds {self.max_length} characters",
                modified_output=truncated,
            )

        return PolicyResult(decision=PolicyDecision.ALLOW, reason="Length OK")


class SensitivityPolicy(Policy):
    """Detect and handle sensitive information."""

    def __init__(self):
        """Initialize sensitivity policy."""
        self.sensitive_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        ]

    def evaluate(self, output: Any, context: dict | None = None) -> PolicyResult:
        """Check for sensitive information."""
        import re

        output_str = str(output)
        warnings = []

        for pattern in self.sensitive_patterns:
            if re.search(pattern, output_str):
                warnings.append(f"Potential sensitive data detected: {pattern}")

        if warnings:
            return PolicyResult(
                decision=PolicyDecision.WARN,
                reason="Sensitive data detected",
                warnings=warnings,
            )

        return PolicyResult(decision=PolicyDecision.ALLOW, reason="No sensitive data")


class PolicyEngine:
    """
    Central policy enforcement engine.

    Evaluates outputs against multiple policies and
    aggregates decisions.
    """

    def __init__(self, policies: list[Policy] | None = None, mode: str = "production"):
        """
        Initialize policy engine.

        Args:
            policies: List of policies to enforce
            mode: Engine mode ('production', 'strict', 'custom')
        """
        self.mode = mode

        if policies is None:
            # Default to allow-all in production
            if mode == "production":
                policies = [AllowAllPolicy()]
            elif mode == "strict":
                policies = [
                    ContentFilterPolicy(),
                    LengthLimitPolicy(),
                    SensitivityPolicy(),
                ]
            else:
                policies = []

        self.policies = policies
        logger.info(
            f"PolicyEngine initialized with {len(policies)} policies (mode: {mode})"
        )

    def add_policy(self, policy: Policy):
        """Add a policy to the engine."""
        self.policies.append(policy)
        logger.info(f"Added policy: {policy.__class__.__name__}")

    def remove_policy(self, policy_class: type):
        """Remove policies of a specific type."""
        self.policies = [p for p in self.policies if not isinstance(p, policy_class)]

    def enforce(self, output: Any, context: dict | None = None) -> PolicyResult:
        """
        Enforce all policies on output.

        Args:
            output: Output to evaluate
            context: Optional context information

        Returns:
            Aggregated PolicyResult
        """
        if not self.policies:
            return PolicyResult(
                decision=PolicyDecision.ALLOW, reason="No policies defined"
            )

        # Evaluate all policies
        results = []
        current_output = output
        all_warnings = []

        for policy in self.policies:
            try:
                result = policy.evaluate(current_output, context)
                results.append(result)

                # Accumulate warnings
                if result.warnings:
                    all_warnings.extend(result.warnings)

                # Handle DENY decision (stop immediately)
                if result.decision == PolicyDecision.DENY:
                    logger.warning(f"Policy denied output: {result.reason}")
                    return PolicyResult(
                        decision=PolicyDecision.DENY,
                        reason=result.reason,
                        warnings=all_warnings,
                    )

                # Handle MODIFY decision (apply modification)
                if (
                    result.decision == PolicyDecision.MODIFY
                    and result.modified_output is not None
                ):
                    current_output = result.modified_output

            except Exception as e:
                logger.error(f"Policy evaluation error: {e}")
                # Continue with other policies

        # Aggregate results
        has_modifications = any(r.decision == PolicyDecision.MODIFY for r in results)
        has_warnings = len(all_warnings) > 0

        if has_modifications:
            return PolicyResult(
                decision=PolicyDecision.MODIFY,
                reason="Output modified by policies",
                modified_output=current_output,
                warnings=all_warnings if has_warnings else None,
            )

        if has_warnings:
            return PolicyResult(
                decision=PolicyDecision.WARN,
                reason="Warnings generated",
                warnings=all_warnings,
            )

        return PolicyResult(
            decision=PolicyDecision.ALLOW, reason="All policies passed", warnings=None
        )

    def get_policy_info(self) -> dict:
        """Get information about active policies."""
        return {
            "mode": self.mode,
            "policy_count": len(self.policies),
            "policies": [p.__class__.__name__ for p in self.policies],
        }
