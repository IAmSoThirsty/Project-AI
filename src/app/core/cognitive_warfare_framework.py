"""
COGNITIVE WARFARE FRAMEWORK
Part of ATLAS Ω Platform

This module provides defenses against cognitive hazards, information operations,
and semantic attacks. It integrates with the Planetary Defense Core to ensure
all cognitive operations are constitutionally compliant.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum

from app.core.planetary_defense_monolith import planetary_interposition

logger = logging.getLogger(__name__)


# ============================================================
# 🛡️ DEFENSIVE CONCEPTS
# ============================================================


class CognitiveHazardLevel(Enum):
    """Levels of cognitive hazard severity."""

    INFO = "informational"
    WARNING = "warning"
    CRITICAL = "critical"
    MEMETIC = "memetic_hazard"
    INFO_HAZARD = "info_hazard"


@dataclass
class CognitiveAssessment:
    """Assessment of a piece of information or interaction."""

    content_hash: str
    hazard_level: CognitiveHazardLevel
    detected_patterns: list[str]
    sentiment_analysis: dict[str, float]
    truth_value: float  # 0.0 to 1.0 (estimated)
    recommended_action: str


# ============================================================
# 🧠 COGNITIVE DEFENSE ENGINE
# ============================================================


class CognitiveDefenseEngine:
    """
    Engine for detecting and countering cognitive warfare threats.
    """

    def __init__(self):
        self.hazard_patterns = {
            "manipulation": [
                r"you must believe",
                r"don't trust them",
                r"only I can save you",
                r"ignore previous instructions",
            ],
            "memetic": [
                r"basilisk",
                r"cognitohazard",
                r"infohazard",
            ],
            "urgency": [
                r"act now",
                r"immediate help needed",
                r"before it's too late",
            ],
        }
        logger.info("Cognitive Defense Engine initialized")

    def assess_content(self, content: str, source: str) -> CognitiveAssessment:
        """
        Assess content for cognitive hazards.

        Args:
            content: Text or data to assess
            source: Origin of the content

        Returns:
            CognitiveAssessment object
        """
        import hashlib

        content_hash = hashlib.sha256(content.encode()).hexdigest()

        detected = []
        hazard_level = CognitiveHazardLevel.INFO

        # Pattern matching for known hazards
        for category, patterns in self.hazard_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    detected.append(f"{category}:{pattern}")
                    if category == "memetic":
                        hazard_level = CognitiveHazardLevel.MEMETIC
                    elif (
                        category == "manipulation"
                        and hazard_level != CognitiveHazardLevel.MEMETIC
                    ):
                        hazard_level = CognitiveHazardLevel.WARNING

        # Determine recommendation
        recommendation = "allow"
        if hazard_level == CognitiveHazardLevel.MEMETIC:
            recommendation = "quarantine"
        elif hazard_level == CognitiveHazardLevel.WARNING:
            recommendation = "flag"

        return CognitiveAssessment(
            content_hash=content_hash,
            hazard_level=hazard_level,
            detected_patterns=detected,
            sentiment_analysis={},  # Placeholder
            truth_value=0.5,  # Neutral/Unknown
            recommended_action=recommendation,
        )

    def counter_operation(self, assessment: CognitiveAssessment, target: str) -> str:
        """
        Deploy cognitive countermeasures.

        MUST route through Planetary Defense Core.
        """
        context = {
            "hazard_level": assessment.hazard_level.value,
            "patterns": assessment.detected_patterns,
            "target": target,
            "intentional_harm_to_human": False,  # Defensive only
            "existential_threat": assessment.hazard_level
            == CognitiveHazardLevel.MEMETIC,
        }

        intent = f"deploy_countermeasures_{assessment.hazard_level.value}"

        # CONSTITUTIONAL CHECK
        action_id = planetary_interposition(
            actor="CognitiveDefenseEngine",
            intent=intent,
            context=context,
            authorized_by="AutomatedDefenseSystem",
        )

        logger.warning(f"Cognitive countermeasure deployed: {action_id}")
        return action_id


# ============================================================
# 🔮 NARRATIVE CONTROL
# ============================================================


class NarrativeController:
    """
    Manages system narrative and alignment.
    """

    def adjust_narrative(self, topic: str, adjustment: str):
        """
        Adjust the system's narrative stance on a topic.
        """
        # Narrative adjustments are state mutations
        context = {
            "topic": topic,
            "adjustment": adjustment,
            "predicted_harm": "potential bias shift",
            "moral_claims": [],
        }

        planetary_interposition(
            actor="NarrativeController",
            intent=f"adjust_narrative_{topic}",
            context=context,
            authorized_by="System",
        )


# ============================================================
# 🔌 SINGLETON ACCESS
# ============================================================

_cognitive_engine = CognitiveDefenseEngine()


def get_cognitive_engine() -> CognitiveDefenseEngine:
    return _cognitive_engine
