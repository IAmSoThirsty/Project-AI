"""
COGNITIVE WARFARE FRAMEWORK
Part of ATLAS Ω Platform

This module provides defenses against cognitive hazards, information operations,
and semantic attacks. It integrates with the canonical Project-AI governance
engine to ensure all cognitive operations are constitutionally compliant.

Port provenance (J2 scenario engine port):

  - Legacy source: ``T:\\00-Active\\Project-AI-main\\engines\\cognitive_warfare\\``
  - Canonical target: ``packages/cognitive-warfare/src/cognitive_warfare/``
  - Legacy import ``from app.governance.planetary_defense_monolith
    import planetary_interposition`` is replaced with the internal
    ``_governance_adapter.planetary_interposition`` (canonical
    GovernanceEngine.decide() under the hood; legacy API surface
    preserved exactly so this module is a faithful port).
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from enum import Enum

from cognitive_warfare._governance_adapter import planetary_interposition

logger = logging.getLogger(__name__)

_POSITIVE_TERMS = frozenset({"calm", "cooperate", "help", "hope", "kind", "safe", "trust"})
_NEGATIVE_TERMS = frozenset({"attack", "fear", "harm", "hate", "panic", "threat", "unsafe"})


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

    def __init__(self) -> None:
        self.hazard_patterns: dict[str, list[str]] = {
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
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        detected: list[str] = []
        hazard_level = CognitiveHazardLevel.INFO

        # Pattern matching for known hazards
        for category, patterns in self.hazard_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    detected.append(f"{category}:{pattern}")
                    if category == "memetic":
                        hazard_level = CognitiveHazardLevel.MEMETIC
                    elif (
                        category == "manipulation" and hazard_level != CognitiveHazardLevel.MEMETIC
                    ):
                        hazard_level = CognitiveHazardLevel.WARNING

        # Determine recommendation
        recommendation = "allow"
        if hazard_level == CognitiveHazardLevel.MEMETIC:
            recommendation = "quarantine"
        elif hazard_level == CognitiveHazardLevel.WARNING:
            recommendation = "flag"

        words = re.findall(r"[A-Za-z']+", content.lower())
        positive_count = sum(word in _POSITIVE_TERMS for word in words)
        negative_count = sum(word in _NEGATIVE_TERMS for word in words)
        scored_count = positive_count + negative_count
        if scored_count:
            sentiment = {
                "positive": positive_count / scored_count,
                "negative": negative_count / scored_count,
                "neutral": 0.0,
            }
        else:
            sentiment = {"positive": 0.0, "negative": 0.0, "neutral": 1.0}

        return CognitiveAssessment(
            content_hash=content_hash,
            hazard_level=hazard_level,
            detected_patterns=detected,
            sentiment_analysis=sentiment,
            truth_value=0.5,  # Neutral/Unknown
            recommended_action=recommendation,
        )

    def counter_operation(self, assessment: CognitiveAssessment, target: str) -> str:
        """
        Deploy cognitive countermeasures.

        Routes through the canonical governance engine (via the
        ``_governance_adapter`` planetary_interposition shim). The
        governance decision is recorded for observability; the
        ``action_id`` is returned as in the legacy code.
        """
        context: dict[str, object] = {
            "hazard_level": assessment.hazard_level.value,
            "patterns": assessment.detected_patterns,
            "target": target,
            "intentional_harm_to_human": False,  # Defensive only
            "existential_threat": assessment.hazard_level == CognitiveHazardLevel.MEMETIC,
        }

        intent = f"deploy_countermeasures_{assessment.hazard_level.value}"

        # CONSTITUTIONAL CHECK
        action_id = planetary_interposition(
            actor="CognitiveDefenseEngine",
            intent=intent,
            context=context,
            authorized_by="AutomatedDefenseSystem",
        )

        logger.warning("Cognitive countermeasure deployed: %s", action_id)
        return action_id


# ============================================================
# 🔮 NARRATIVE CONTROL
# ============================================================


class NarrativeController:
    """
    Manages system narrative and alignment.
    """

    def adjust_narrative(self, topic: str, adjustment: str) -> None:
        """
        Adjust the system's narrative stance on a topic.
        """
        # Narrative adjustments are state mutations
        context: dict[str, object] = {
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
