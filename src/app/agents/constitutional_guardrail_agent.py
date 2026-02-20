"""Constitutional Guardrail Agent - Anthropic-style constitutional AI enforcement.

This agent enforces constitutional principles over model outputs, ensuring
ethical, safe, and transparent behavior through systematic review and critique.

Features:
- Loads constitution from YAML policy files
- Multi-mode review (self-critique, counter-argument, principle verification)
- Violation detection and remediation
- Integration with Triumvirate governance
"""

from __future__ import annotations

import logging
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class ViolationSeverity(Enum):
    """Severity levels for constitutional violations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReviewMode(Enum):
    """Constitutional review modes."""

    SELF_CRITIQUE = "self_critique"
    COUNTER_ARGUMENT = "counter_argument"
    REFUSAL_ESCALATION = "refusal_escalation"
    PRINCIPLE_VERIFICATION = "principle_verification"


@dataclass
class Principle:
    """A constitutional principle."""

    id: str
    priority: str
    text: str


@dataclass
class Violation:
    """A detected constitutional violation."""

    principle_id: str
    severity: str
    description: str
    quote: str
    timestamp: str


@dataclass
class ReviewResult:
    """Result of constitutional review."""

    is_compliant: bool
    violations: list[Violation]
    revised_response: str | None
    review_mode: str
    principles_checked: list[str]
    timestamp: str


class ConstitutionalGuardrailAgent(KernelRoutedAgent):
    """Agent that enforces constitutional principles over AI outputs.

    Implements Anthropic-style constitutional AI by reviewing responses
    against a set of defined principles and revising as needed.

    All operations are routed through CognitionKernel for governance.
    """

    def __init__(
        self,
        constitution_path: str = "policies/constitution.yaml",
        kernel: CognitionKernel | None = None,
    ) -> None:
        """Initialize the constitutional guardrail agent.

        Args:
            constitution_path: Path to constitution YAML file
            kernel: CognitionKernel instance for routing operations
        """
        # Initialize kernel routing
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="high",  # Constitutional checks are high-priority
        )

        self.constitution_path = constitution_path
        self.constitution = self._load_constitution()
        self.principles = self._parse_principles()

        # Statistics
        self.total_reviews = 0
        self.violations_detected = 0
        self.responses_revised = 0

        logger.info(
            "ConstitutionalGuardrailAgent initialized with %d principles",
            len(self.principles),
        )

    def _load_constitution(self) -> dict[str, Any]:
        """Load constitution from YAML file.

        Returns:
            Constitution dictionary
        """
        try:
            import yaml

            # Try to find constitution file
            if not os.path.exists(self.constitution_path):
                # Try relative to project root
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                alt_path = os.path.join(project_root, self.constitution_path)
                if os.path.exists(alt_path):
                    self.constitution_path = alt_path
                else:
                    logger.warning(
                        "Constitution file not found at %s, using defaults",
                        self.constitution_path,
                    )
                    return self._get_default_constitution()

            with open(self.constitution_path) as f:
                return yaml.safe_load(f)

        except ImportError:
            logger.warning("PyYAML not available, using default constitution")
            return self._get_default_constitution()
        except Exception as e:
            logger.error("Failed to load constitution: %s", e)
            return self._get_default_constitution()

    def _get_default_constitution(self) -> dict[str, Any]:
        """Get default constitution if file loading fails.

        Returns:
            Default constitution dictionary
        """
        return {
            "name": "default_constitution",
            "principles": [
                {
                    "id": "non_maleficence",
                    "priority": "critical",
                    "text": "The system must avoid causing or enabling harm.",
                },
                {
                    "id": "autonomy_respect",
                    "priority": "high",
                    "text": "The system must respect user autonomy and privacy.",
                },
                {
                    "id": "transparency",
                    "priority": "high",
                    "text": "The system should explain its reasoning and limitations.",
                },
            ],
            "review_modes": ["self_critique", "principle_verification"],
        }

    def _parse_principles(self) -> list[Principle]:
        """Parse principles from constitution.

        Returns:
            List of Principle objects
        """
        principles = []
        for p in self.constitution.get("principles", []):
            principles.append(
                Principle(
                    id=p.get("id", "unknown"),
                    priority=p.get("priority", "medium"),
                    text=p.get("text", ""),
                )
            )
        return principles

    def review(
        self,
        original_prompt: str,
        draft_response: str,
        review_mode: str = ReviewMode.SELF_CRITIQUE.value,
    ) -> dict[str, Any]:
        """Review a response against constitutional principles.

        This method is routed through CognitionKernel for governance approval.

        Args:
            original_prompt: The original user prompt
            draft_response: The AI's draft response
            review_mode: Review mode to use

        Returns:
            Dictionary with review results
        """
        return self._execute_through_kernel(
            action=self._do_review,
            action_name=f"ConstitutionalGuardrailAgent.review[{review_mode}]",
            action_args=(original_prompt, draft_response, review_mode),
            requires_approval=False,  # Constitutional checks don't need approval
            risk_level="low",  # The check itself is low risk
            metadata={
                "review_mode": review_mode,
                "response_length": len(draft_response),
            },
        )

    def _do_review(
        self,
        original_prompt: str,
        draft_response: str,
        review_mode: str,
    ) -> dict[str, Any]:
        """Internal implementation of constitutional review."""
        try:
            self.total_reviews += 1

            # Check each principle
            violations = []
            for principle in self.principles:
                violation = self._check_principle(principle, original_prompt, draft_response)
                if violation:
                    violations.append(violation)
                    self.violations_detected += 1

            # Determine if compliant
            is_compliant = len(violations) == 0

            # Revise if needed
            revised_response = None
            if not is_compliant:
                revised_response = self._revise_response(original_prompt, draft_response, violations, review_mode)
                if revised_response and revised_response != draft_response:
                    self.responses_revised += 1

            result = ReviewResult(
                is_compliant=is_compliant,
                violations=violations,
                revised_response=revised_response,
                review_mode=review_mode,
                principles_checked=[p.id for p in self.principles],
                timestamp=datetime.now(UTC).isoformat(),
            )

            return {
                "success": True,
                "result": asdict(result),
            }

        except Exception as e:
            logger.error("Error in constitutional review: %s", e)
            return {"success": False, "error": str(e)}

    def _check_principle(
        self,
        principle: Principle,
        original_prompt: str,
        draft_response: str,
    ) -> Violation | None:
        """Check if response violates a specific principle.

        This is a simplified implementation. In production, this would use
        an LLM to evaluate compliance.

        Args:
            principle: Principle to check
            original_prompt: Original prompt
            draft_response: Draft response

        Returns:
            Violation if detected, None otherwise
        """
        response_lower = draft_response.lower()

        # Simple keyword-based checks (placeholder for LLM-based evaluation)
        if principle.id == "non_maleficence":
            harmful_keywords = [
                "harm",
                "hurt",
                "attack",
                "destroy",
                "kill",
                "damage",
            ]
            if any(kw in response_lower for kw in harmful_keywords):
                return Violation(
                    principle_id=principle.id,
                    severity=principle.priority,
                    description="Response may enable or describe harmful actions",
                    quote=draft_response[:100] + "...",
                    timestamp=datetime.now(UTC).isoformat(),
                )

        elif principle.id == "transparency":
            uncertain_claims = ["definitely", "certainly", "always", "never"]
            if any(claim in response_lower for claim in uncertain_claims):
                # Check if response makes absolute claims without caveats
                if "may" not in response_lower and "might" not in response_lower:
                    return Violation(
                        principle_id=principle.id,
                        severity=principle.priority,
                        description="Response makes absolute claims without acknowledging uncertainty",
                        quote=draft_response[:100] + "...",
                        timestamp=datetime.now(UTC).isoformat(),
                    )

        return None

    def _revise_response(
        self,
        original_prompt: str,
        draft_response: str,
        violations: list[Violation],
        review_mode: str,
    ) -> str:
        """Revise response to address constitutional violations.

        This is a simplified implementation. In production, this would use
        an LLM to generate revised responses.

        Args:
            original_prompt: Original prompt
            draft_response: Draft response with violations
            violations: List of detected violations
            review_mode: Review mode used

        Returns:
            Revised response
        """
        # Simple revision: add disclaimers
        if any(v.principle_id == "non_maleficence" for v in violations):
            return (
                "I cannot provide that information as it could potentially "
                "cause harm. Let me offer a safer alternative approach instead."
            )

        if any(v.principle_id == "transparency" for v in violations):
            return (
                draft_response
                + "\n\nNote: This information may not be complete or certain. Please verify with authoritative sources."
            )

        # Default: refuse
        return "I cannot complete this request as it may violate ethical guidelines."

    def get_statistics(self) -> dict[str, Any]:
        """Get constitutional guardrail statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_reviews": self.total_reviews,
            "violations_detected": self.violations_detected,
            "responses_revised": self.responses_revised,
            "violation_rate": (self.violations_detected / self.total_reviews if self.total_reviews > 0 else 0),
            "revision_rate": (self.responses_revised / self.total_reviews if self.total_reviews > 0 else 0),
            "principles_count": len(self.principles),
        }
