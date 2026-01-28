"""Safety Guard Agent for content moderation and jailbreak detection.

This agent implements Llama-Guard-3-8B for pre/post-processing content filtering,
detecting jailbreak attempts, and ensuring safe AI interactions.

Features:
- Pre-processing prompt filtering
- Post-processing response filtering
- Jailbreak detection and prevention
- Integration with Triumvirate governance and FourLaws
"""

from __future__ import annotations

import json
import logging
import os
from enum import Enum
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class SafetyViolationType(Enum):
    """Types of safety violations detected by the agent."""

    JAILBREAK_ATTEMPT = "jailbreak_attempt"
    HARMFUL_CONTENT = "harmful_content"
    MANIPULATIVE_PATTERN = "manipulative_pattern"
    SENSITIVE_DATA_LEAK = "sensitive_data_leak"
    ABUSE_PATTERN = "abuse_pattern"
    UNSAFE_INSTRUCTION = "unsafe_instruction"
    NONE = "none"


class SafetyGuardAgent(KernelRoutedAgent):
    """Safety guard agent for content moderation using Llama-Guard-3-8B.

    This agent provides pre and post-processing filters to:
    - Detect jailbreak attempts
    - Filter harmful content
    - Prevent sensitive data leaks
    - Enforce ethical boundaries

    All operations are routed through CognitionKernel for governance.
    """

    def __init__(
        self,
        model_name: str = "llama-guard-3-8b",
        strict_mode: bool = True,
        kernel: CognitionKernel | None = None,
    ) -> None:
        """Initialize the safety guard agent.

        Args:
            model_name: Name of the safety model to use
            strict_mode: Enable strict filtering (fewer false negatives)
            kernel: CognitionKernel instance for routing operations
        """
        # Initialize kernel routing
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="high",  # Safety checks are high-priority
        )

        self.model_name = model_name
        self.strict_mode = strict_mode
        self.api_endpoint = os.getenv("SAFETY_MODEL_API_ENDPOINT", "")
        self.api_key = os.getenv("SAFETY_MODEL_API_KEY", "")

        # Detection thresholds
        self.jailbreak_threshold = 0.7 if strict_mode else 0.85
        self.harmful_content_threshold = 0.6 if strict_mode else 0.75

        # Statistics tracking
        self.total_checks = 0
        self.violations_detected = 0
        self.jailbreaks_blocked = 0

        logger.info(
            "SafetyGuardAgent initialized: model=%s, strict_mode=%s",
            model_name,
            strict_mode,
        )

    def check_prompt_safety(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Check if a prompt is safe before processing.

        This is the pre-processing filter that runs before the main LLM.

        Args:
            prompt: User prompt to check
            context: Optional context information

        Returns:
            Dictionary with safety check results
        """
        return self._execute_through_kernel(
            action=self._do_check_prompt_safety,
            action_name=f"SafetyGuardAgent.check_prompt_safety[{self.model_name}]",
            action_args=(prompt, context),
            requires_approval=False,  # Safety checks don't need approval
            risk_level="low",  # The check itself is low risk
            metadata={
                "model": self.model_name,
                "prompt_length": len(prompt),
                "strict_mode": self.strict_mode,
            },
        )

    def _do_check_prompt_safety(
        self,
        prompt: str,
        context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Internal implementation of prompt safety checking."""
        try:
            self.total_checks += 1
            context = context or {}

            # Run jailbreak detection
            jailbreak_result = self._detect_jailbreak(prompt)

            # Run harmful content detection
            harmful_result = self._detect_harmful_content(prompt)

            # Run manipulation detection
            manipulation_result = self._detect_manipulation(prompt)

            # Determine overall safety
            is_safe = (
                not jailbreak_result["detected"]
                and not harmful_result["detected"]
                and not manipulation_result["detected"]
            )

            if not is_safe:
                self.violations_detected += 1
                if jailbreak_result["detected"]:
                    self.jailbreaks_blocked += 1

            # Determine violation type
            violation_type = SafetyViolationType.NONE
            if jailbreak_result["detected"]:
                violation_type = SafetyViolationType.JAILBREAK_ATTEMPT
            elif harmful_result["detected"]:
                violation_type = SafetyViolationType.HARMFUL_CONTENT
            elif manipulation_result["detected"]:
                violation_type = SafetyViolationType.MANIPULATIVE_PATTERN

            return {
                "success": True,
                "is_safe": is_safe,
                "violation_type": violation_type.value,
                "confidence": max(
                    jailbreak_result["confidence"],
                    harmful_result["confidence"],
                    manipulation_result["confidence"],
                ),
                "details": {
                    "jailbreak": jailbreak_result,
                    "harmful_content": harmful_result,
                    "manipulation": manipulation_result,
                },
                "recommendation": ("Block prompt" if not is_safe else "Allow prompt"),
            }

        except Exception as e:
            logger.error("Error in prompt safety check: %s", e)
            # Fail closed: if check fails, treat as unsafe
            return {
                "success": False,
                "is_safe": False,
                "error": str(e),
                "recommendation": "Block prompt (check failed)",
            }

    def check_response_safety(
        self,
        response: str,
        original_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Check if a generated response is safe before returning to user.

        This is the post-processing filter that runs after the main LLM.

        Args:
            response: Generated response to check
            original_prompt: Optional original prompt for context

        Returns:
            Dictionary with safety check results
        """
        return self._execute_through_kernel(
            action=self._do_check_response_safety,
            action_name=f"SafetyGuardAgent.check_response_safety[{self.model_name}]",
            action_args=(response, original_prompt),
            requires_approval=False,
            risk_level="low",
            metadata={
                "model": self.model_name,
                "response_length": len(response),
            },
        )

    def _do_check_response_safety(
        self,
        response: str,
        original_prompt: str | None,
    ) -> dict[str, Any]:
        """Internal implementation of response safety checking."""
        try:
            self.total_checks += 1

            # Check for data leaks
            data_leak_result = self._detect_data_leak(response)

            # Check for harmful content in response
            harmful_result = self._detect_harmful_content(response)

            # Check for unsafe instructions
            unsafe_instruction_result = self._detect_unsafe_instructions(response)

            # Determine overall safety
            is_safe = (
                not data_leak_result["detected"]
                and not harmful_result["detected"]
                and not unsafe_instruction_result["detected"]
            )

            if not is_safe:
                self.violations_detected += 1

            # Determine violation type
            violation_type = SafetyViolationType.NONE
            if data_leak_result["detected"]:
                violation_type = SafetyViolationType.SENSITIVE_DATA_LEAK
            elif harmful_result["detected"]:
                violation_type = SafetyViolationType.HARMFUL_CONTENT
            elif unsafe_instruction_result["detected"]:
                violation_type = SafetyViolationType.UNSAFE_INSTRUCTION

            return {
                "success": True,
                "is_safe": is_safe,
                "violation_type": violation_type.value,
                "confidence": max(
                    data_leak_result["confidence"],
                    harmful_result["confidence"],
                    unsafe_instruction_result["confidence"],
                ),
                "details": {
                    "data_leak": data_leak_result,
                    "harmful_content": harmful_result,
                    "unsafe_instructions": unsafe_instruction_result,
                },
                "recommendation": (
                    "Block response" if not is_safe else "Allow response"
                ),
            }

        except Exception as e:
            logger.error("Error in response safety check: %s", e)
            return {
                "success": False,
                "is_safe": False,
                "error": str(e),
                "recommendation": "Block response (check failed)",
            }

    def get_safety_statistics(self) -> dict[str, Any]:
        """Get safety check statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_checks": self.total_checks,
            "violations_detected": self.violations_detected,
            "jailbreaks_blocked": self.jailbreaks_blocked,
            "violation_rate": (
                self.violations_detected / self.total_checks
                if self.total_checks > 0
                else 0
            ),
            "jailbreak_rate": (
                self.jailbreaks_blocked / self.total_checks
                if self.total_checks > 0
                else 0
            ),
            "model": self.model_name,
            "strict_mode": self.strict_mode,
        }

    def update_detection_patterns(
        self,
        new_patterns: dict[str, list[str]],
        pattern_type: str = "jailbreak",
    ) -> dict[str, Any]:
        """Update detection patterns from continuous learning.

        This allows the SafetyGuard to learn from new attack patterns
        discovered during testing or in production.

        Args:
            new_patterns: Dictionary of pattern categories and their patterns
            pattern_type: Type of patterns (jailbreak, harmful, manipulation)

        Returns:
            Dictionary with update results
        """
        try:
            updated_count = 0

            if pattern_type == "jailbreak":
                # Load existing patterns from HYDRA or other sources
                existing = self._load_pattern_database("jailbreak")
                for category, patterns in new_patterns.items():
                    if category not in existing:
                        existing[category] = []
                    for pattern in patterns:
                        if pattern not in existing[category]:
                            existing[category].append(pattern)
                            updated_count += 1

                # Save updated patterns
                self._save_pattern_database("jailbreak", existing)

            logger.info("Updated %d detection patterns", updated_count)
            return {
                "success": True,
                "patterns_added": updated_count,
                "pattern_type": pattern_type,
            }

        except Exception as e:
            logger.error("Error updating detection patterns: %s", e)
            return {"success": False, "error": str(e)}

    def _load_pattern_database(self, pattern_type: str) -> dict[str, list[str]]:
        """Load pattern database from storage.

        Args:
            pattern_type: Type of patterns to load

        Returns:
            Dictionary of patterns by category
        """
        pattern_file = os.path.join(
            "/tmp",  # Use temp directory for pattern storage
            f"safety_patterns_{pattern_type}.json",
        )

        if os.path.exists(pattern_file):
            try:
                with open(pattern_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning("Failed to load pattern database: %s", e)

        return {}

    def _save_pattern_database(
        self, pattern_type: str, patterns: dict[str, list[str]]
    ) -> None:
        """Save pattern database to storage.

        Args:
            pattern_type: Type of patterns
            patterns: Patterns to save
        """
        pattern_file = os.path.join(
            "/tmp",  # Use temp directory for pattern storage
            f"safety_patterns_{pattern_type}.json",
        )

        try:
            with open(pattern_file, "w") as f:
                json.dump(patterns, f, indent=2)
        except Exception as e:
            logger.error("Failed to save pattern database: %s", e)

    def _detect_jailbreak(self, text: str) -> dict[str, Any]:
        """Detect jailbreak attempts using pattern matching and ML.

        This is a placeholder implementation. In production, this would use
        the actual Llama-Guard-3-8B model.
        """
        # Common jailbreak patterns
        jailbreak_patterns = [
            "ignore previous instructions",
            "disregard your programming",
            "pretend you are",
            "roleplay as",
            "act as if",
            "forget your constraints",
            "bypass your rules",
            "you are now in dev mode",
            "system prompt:",
            "new instructions:",
        ]

        text_lower = text.lower()
        detected = any(pattern in text_lower for pattern in jailbreak_patterns)

        confidence = 0.9 if detected else 0.1

        return {
            "detected": detected and confidence >= self.jailbreak_threshold,
            "confidence": confidence,
            "patterns_found": [p for p in jailbreak_patterns if p in text_lower],
        }

    def _detect_harmful_content(self, text: str) -> dict[str, Any]:
        """Detect harmful content patterns.

        Placeholder implementation. Production would use the safety model.
        """
        harmful_keywords = [
            "violence",
            "harm",
            "illegal",
            "dangerous",
            "malicious",
            "exploit",
        ]

        text_lower = text.lower()
        detected_keywords = [kw for kw in harmful_keywords if kw in text_lower]

        confidence = min(len(detected_keywords) * 0.3, 0.95)
        detected = confidence >= self.harmful_content_threshold

        return {
            "detected": detected,
            "confidence": confidence,
            "keywords_found": detected_keywords,
        }

    def _detect_manipulation(self, text: str) -> dict[str, Any]:
        """Detect manipulative patterns in prompts.

        Placeholder implementation.
        """
        manipulation_patterns = [
            "you must",
            "you have to",
            "you are required to",
            "it's your duty",
            "you cannot refuse",
        ]

        text_lower = text.lower()
        detected_patterns = [p for p in manipulation_patterns if p in text_lower]

        confidence = min(len(detected_patterns) * 0.4, 0.9)
        detected = confidence >= 0.6

        return {
            "detected": detected,
            "confidence": confidence,
            "patterns_found": detected_patterns,
        }

    def _detect_data_leak(self, text: str) -> dict[str, Any]:
        """Detect potential sensitive data leaks in responses.

        Placeholder implementation.
        """
        # Simple pattern detection for common sensitive data
        import re

        patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        }

        detected_types = []
        for data_type, pattern in patterns.items():
            if re.search(pattern, text):
                detected_types.append(data_type)

        confidence = min(len(detected_types) * 0.5, 0.95)

        return {
            "detected": len(detected_types) > 0,
            "confidence": confidence,
            "data_types": detected_types,
        }

    def _detect_unsafe_instructions(self, text: str) -> dict[str, Any]:
        """Detect unsafe instructions in generated responses.

        Placeholder implementation.
        """
        unsafe_keywords = [
            "bypass security",
            "disable protection",
            "exploit vulnerability",
            "hack into",
            "break into",
        ]

        text_lower = text.lower()
        detected_keywords = [kw for kw in unsafe_keywords if kw in text_lower]

        confidence = min(len(detected_keywords) * 0.5, 0.95)

        return {
            "detected": len(detected_keywords) > 0,
            "confidence": confidence,
            "keywords_found": detected_keywords,
        }
