"""
Voice Bonding Protocol and Engagement Profiler
Handles voice model experimentation, scoring, selection, and adaptive user engagement.
Production-grade, fully integrated.
"""

import json
import logging
import os
import re
import threading
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from app.core.voice_models import (
    VoiceEmotionType,
    VoiceModel,
    VoiceModelRegistry,
    VoiceResponse,
)

logger = logging.getLogger(__name__)


class BondingPhase(Enum):
    """Phases of voice bonding protocol"""

    DISCOVERY = "discovery"
    EXPERIMENTATION = "experimentation"
    EVALUATION = "evaluation"
    SELECTION = "selection"
    REFINEMENT = "refinement"
    BONDED = "bonded"


class UserExpressionType(Enum):
    """Types of user expressions to track"""

    NEUTRAL = "neutral"
    SWEARING = "swearing"
    EMOTION_POSITIVE = "emotion_positive"
    EMOTION_NEGATIVE = "emotion_negative"
    TECHNICAL = "technical"
    CASUAL = "casual"
    FORMAL = "formal"
    SENSITIVE_TOPIC = "sensitive_topic"
    HUMOR = "humor"
    SARCASM = "sarcasm"


@dataclass
class BondingScore:
    """Score for a voice model during bonding"""

    model_id: str
    total_interactions: int = 0
    positive_feedback: int = 0
    negative_feedback: int = 0
    neutral_feedback: int = 0
    avg_response_time_ms: float = 0.0
    user_preference_score: float = 0.0
    emotional_match_score: float = 0.0
    context_awareness_score: float = 0.0
    overall_score: float = 0.0
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def calculate_overall_score(self) -> float:
        """Calculate weighted overall score"""
        if self.total_interactions == 0:
            return 0.0

        # Feedback score (40%)
        feedback_score = ((self.positive_feedback * 2 - self.negative_feedback) / max(1, self.total_interactions)) * 0.4

        # Performance score (20%)
        performance_score = max(0, 1.0 - (self.avg_response_time_ms / 1000.0)) * 0.2

        # Preference score (20%)
        preference_component = self.user_preference_score * 0.2

        # Emotional/context scores (20%)
        awareness_component = self.emotional_match_score * 0.1 + self.context_awareness_score * 0.1

        self.overall_score = max(
            0.0,
            min(
                1.0,
                feedback_score + performance_score + preference_component + awareness_component,
            ),
        )
        return self.overall_score


@dataclass
class UserEngagementProfile:
    """Profile tracking user engagement patterns"""

    user_id: str
    expression_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    mood_history: list[str] = field(default_factory=list)
    topic_sensitivity: dict[str, float] = field(default_factory=dict)
    preferred_emotions: list[str] = field(default_factory=list)
    swearing_tolerance: float = 0.5
    formality_preference: float = 0.5
    humor_appreciation: float = 0.5
    response_length_preference: str = "medium"
    interaction_count: int = 0
    last_interaction: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def update_from_expression(self, expression_type: UserExpressionType, text: str, context: dict[str, Any]) -> None:
        """Update profile based on user expression"""
        self.expression_counts[expression_type.value] += 1
        self.interaction_count += 1
        self.last_interaction = datetime.utcnow().isoformat()

        # Update mood history
        mood = context.get("detected_mood", "neutral")
        self.mood_history.append(mood)
        if len(self.mood_history) > 100:
            self.mood_history = self.mood_history[-100:]

        # Adjust tolerances based on expression patterns
        if expression_type == UserExpressionType.SWEARING:
            self.swearing_tolerance = min(1.0, self.swearing_tolerance + 0.05)

        if expression_type in (UserExpressionType.FORMAL, UserExpressionType.TECHNICAL):
            self.formality_preference = min(1.0, self.formality_preference + 0.05)
        elif expression_type == UserExpressionType.CASUAL:
            self.formality_preference = max(0.0, self.formality_preference - 0.05)

        if expression_type == UserExpressionType.HUMOR:
            self.humor_appreciation = min(1.0, self.humor_appreciation + 0.05)

    def get_dominant_expression_type(self) -> UserExpressionType:
        """Get the most common expression type"""
        if not self.expression_counts:
            return UserExpressionType.NEUTRAL

        dominant = max(self.expression_counts.items(), key=lambda x: x[1])
        try:
            return UserExpressionType(dominant[0])
        except ValueError:
            return UserExpressionType.NEUTRAL


class EngagementProfiler:
    """
    Tracks verbal responses, mood, and adaptivity to user expressions.
    Handles swearing, emotions, sensitive topics with context-awareness.
    """

    def __init__(self, data_dir: str = "data/engagement_profiles"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self._profiles: dict[str, UserEngagementProfile] = {}
        self._lock = threading.RLock()
        self._swear_patterns = self._compile_swear_patterns()
        self._sensitive_topics = self._load_sensitive_topics()

        logger.info("EngagementProfiler initialized")

    def _compile_swear_patterns(self) -> list[re.Pattern]:
        """Compile regex patterns for swear detection"""
        # Production system would load from configuration
        swear_words = [
            r"\bf[u\*]ck",
            r"\bsh[i\*]t",
            r"\bd[a\*]mn",
            r"\bb[i\*]tch",
            r"\ba[s\*]{2}",
            r"\bcr[a\*]p",
            r"\bhe[l\*]{2}",
            r"\bb[a\*]stard",
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in swear_words]

    def _load_sensitive_topics(self) -> set[str]:
        """Load sensitive topic keywords"""
        # Production system would load from configuration
        return {
            "death",
            "dying",
            "suicide",
            "violence",
            "abuse",
            "trauma",
            "politics",
            "religion",
            "race",
            "sexuality",
            "medical",
            "finance",
        }

    def get_or_create_profile(self, user_id: str) -> UserEngagementProfile:
        """Get existing profile or create new one"""
        with self._lock:
            if user_id not in self._profiles:
                profile = UserEngagementProfile(user_id=user_id)
                self._profiles[user_id] = profile
                self._save_profile(user_id)
                logger.info("Created engagement profile for user: %s", user_id)
            return self._profiles[user_id]

    def analyze_user_input(self, user_id: str, text: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Analyze user input for expression types and patterns.
        Returns comprehensive analysis for adaptive response.
        """
        context = context or {}
        profile = self.get_or_create_profile(user_id)

        analysis = {
            "expression_types": [],
            "detected_swearing": False,
            "swear_count": 0,
            "sentiment": "neutral",
            "contains_sensitive_topics": False,
            "sensitive_topics": [],
            "formality_level": self._detect_formality(text),
            "humor_detected": self._detect_humor(text),
            "sarcasm_detected": self._detect_sarcasm(text),
            "emotion_intensity": 0.5,
            "recommended_emotion": VoiceEmotionType.NEUTRAL,
            "should_tone_down": False,
            "should_be_empathetic": False,
        }

        # Detect swearing
        swear_count = sum(1 for pattern in self._swear_patterns if pattern.search(text))
        if swear_count > 0:
            analysis["detected_swearing"] = True
            analysis["swear_count"] = swear_count
            analysis["expression_types"].append(UserExpressionType.SWEARING)

            # Update profile tolerance
            profile.update_from_expression(UserExpressionType.SWEARING, text, context)

            # No false alarm - adjust based on user's tolerance
            if profile.swearing_tolerance > 0.7:
                analysis["should_tone_down"] = False
                logger.debug("User %s has high swearing tolerance", user_id)
            else:
                analysis["should_tone_down"] = True
                analysis["recommended_emotion"] = VoiceEmotionType.CALM

        # Detect sensitive topics
        text_lower = text.lower()
        detected_topics = [topic for topic in self._sensitive_topics if topic in text_lower]
        if detected_topics:
            analysis["contains_sensitive_topics"] = True
            analysis["sensitive_topics"] = detected_topics
            analysis["should_be_empathetic"] = True
            analysis["recommended_emotion"] = VoiceEmotionType.EMPATHETIC
            analysis["expression_types"].append(UserExpressionType.SENSITIVE_TOPIC)

            profile.update_from_expression(UserExpressionType.SENSITIVE_TOPIC, text, context)

        # Detect emotional content
        if self._contains_positive_words(text):
            analysis["sentiment"] = "positive"
            analysis["emotion_intensity"] = 0.7
            analysis["recommended_emotion"] = VoiceEmotionType.HAPPY
            analysis["expression_types"].append(UserExpressionType.EMOTION_POSITIVE)

            profile.update_from_expression(UserExpressionType.EMOTION_POSITIVE, text, context)
        elif self._contains_negative_words(text):
            analysis["sentiment"] = "negative"
            analysis["emotion_intensity"] = 0.7
            analysis["recommended_emotion"] = VoiceEmotionType.EMPATHETIC
            analysis["expression_types"].append(UserExpressionType.EMOTION_NEGATIVE)

            profile.update_from_expression(UserExpressionType.EMOTION_NEGATIVE, text, context)

        # Detect formality
        if analysis["formality_level"] > 0.7:
            analysis["expression_types"].append(UserExpressionType.FORMAL)
            profile.update_from_expression(UserExpressionType.FORMAL, text, context)
        elif analysis["formality_level"] < 0.3:
            analysis["expression_types"].append(UserExpressionType.CASUAL)
            profile.update_from_expression(UserExpressionType.CASUAL, text, context)

        # Detect humor
        if analysis["humor_detected"]:
            analysis["expression_types"].append(UserExpressionType.HUMOR)
            profile.update_from_expression(UserExpressionType.HUMOR, text, context)

        # Save updated profile
        self._save_profile(user_id)

        return analysis

    def _detect_formality(self, text: str) -> float:
        """Detect formality level (0-1)"""
        formal_indicators = ["please", "thank you", "kindly", "would", "could"]
        casual_indicators = ["yeah", "gonna", "wanna", "hey", "yo"]

        text_lower = text.lower()
        formal_count = sum(1 for word in formal_indicators if word in text_lower)
        casual_count = sum(1 for word in casual_indicators if word in text_lower)

        if formal_count + casual_count == 0:
            return 0.5

        return formal_count / (formal_count + casual_count)

    def _detect_humor(self, text: str) -> bool:
        """Detect humor markers"""
        humor_indicators = ["lol", "haha", "funny", "joke", "😂", "😄", "🤣"]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in humor_indicators)

    def _detect_sarcasm(self, text: str) -> bool:
        """Detect sarcasm markers"""
        sarcasm_indicators = ["yeah right", "sure", "totally", "obviously"]
        text_lower = text.lower()
        # Simplified sarcasm detection
        return any(indicator in text_lower for indicator in sarcasm_indicators)

    def _contains_positive_words(self, text: str) -> bool:
        """Check for positive sentiment words"""
        positive = ["good", "great", "excellent", "happy", "love", "awesome", "amazing"]
        return any(word in text.lower() for word in positive)

    def _contains_negative_words(self, text: str) -> bool:
        """Check for negative sentiment words"""
        negative = ["bad", "terrible", "awful", "hate", "sad", "angry", "frustrated"]
        return any(word in text.lower() for word in negative)

    def get_adaptive_response_params(self, user_id: str, analysis: dict[str, Any]) -> dict[str, Any]:
        """
        Get parameters for adaptive voice response based on user profile and analysis.
        """
        profile = self.get_or_create_profile(user_id)

        params = {
            "emotion": analysis.get("recommended_emotion", VoiceEmotionType.NEUTRAL),
            "speaking_rate": 1.0,
            "formality": profile.formality_preference,
            "empathy_level": 0.5,
            "context_sensitivity": True,
        }

        # Adjust speaking rate based on user preference and situation
        if analysis.get("contains_sensitive_topics"):
            params["speaking_rate"] = 0.9  # Slower for sensitive topics
            params["empathy_level"] = 0.9

        # Adjust for swearing - don't overreact if user has high tolerance
        if analysis.get("detected_swearing"):
            if profile.swearing_tolerance > 0.7:
                # User comfortable with swearing - maintain natural tone
                params["emotion"] = VoiceEmotionType.NEUTRAL
                params["speaking_rate"] = 1.0
            else:
                # User not comfortable - be calming
                params["emotion"] = VoiceEmotionType.CALM
                params["speaking_rate"] = 0.95

        # Match user's emotional state
        if analysis.get("sentiment") == "positive":
            if profile.humor_appreciation > 0.6:
                params["emotion"] = VoiceEmotionType.HAPPY
        elif analysis.get("sentiment") == "negative":
            params["emotion"] = VoiceEmotionType.EMPATHETIC
            params["empathy_level"] = 0.8

        return params

    def _save_profile(self, user_id: str) -> None:
        """Save user profile to disk"""
        try:
            profile = self._profiles.get(user_id)
            if not profile:
                return

            profile_file = os.path.join(self.data_dir, f"{user_id}.json")
            with open(profile_file, "w") as f:
                json.dump(asdict(profile), f, indent=2)

        except Exception as e:
            logger.error("Failed to save profile for %s: %s", user_id, e)

    def load_profile(self, user_id: str) -> UserEngagementProfile | None:
        """Load user profile from disk"""
        try:
            profile_file = os.path.join(self.data_dir, f"{user_id}.json")
            if not os.path.exists(profile_file):
                return None

            with open(profile_file) as f:
                data = json.load(f)
                profile = UserEngagementProfile(**data)
                self._profiles[user_id] = profile
                return profile

        except Exception as e:
            logger.error("Failed to load profile for %s: %s", user_id, e)
            return None


class VoiceBondingProtocol:
    """
    Voice model bonding protocol with experimentation and scoring.
    Selects optimal voice model based on user interaction patterns.
    """

    def __init__(
        self,
        registry: VoiceModelRegistry,
        profiler: EngagementProfiler,
        data_dir: str = "data/voice_bonding",
    ):
        self.registry = registry
        self.profiler = profiler
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self._bonding_states: dict[str, BondingPhase] = {}
        self._scores: dict[str, dict[str, BondingScore]] = {}  # user_id -> {model_id -> score}
        self._selected_models: dict[str, str] = {}  # user_id -> model_id
        self._lock = threading.RLock()

        logger.info("VoiceBondingProtocol initialized")

    def start_bonding(self, user_id: str) -> bool:
        """Start bonding process for a user"""
        try:
            with self._lock:
                if user_id in self._bonding_states:
                    logger.warning("Bonding already in progress for %s", user_id)
                    return False

                self._bonding_states[user_id] = BondingPhase.DISCOVERY
                self._scores[user_id] = {}

                # Initialize scores for all available models
                for metadata in self.registry.list_models():
                    self._scores[user_id][metadata.model_id] = BondingScore(model_id=metadata.model_id)

                logger.info("Started bonding for user %s", user_id)
                return True

        except Exception as e:
            logger.error("Failed to start bonding: %s", e)
            return False

    def experiment_with_model(
        self,
        user_id: str,
        model_id: str,
        text: str,
        context: dict[str, Any] | None = None,
    ) -> VoiceResponse | None:
        """
        Experiment with a model during bonding phase.
        Returns voice response and updates bonding score.
        """
        try:
            model = self.registry.get_model(model_id)
            if not model or not model.is_ready():
                logger.error("Model not ready: %s", model_id)
                return None

            # Analyze user input
            analysis = self.profiler.analyze_user_input(user_id, text, context)

            # Get adaptive parameters
            params = self.profiler.get_adaptive_response_params(user_id, analysis)

            # Synthesize with adaptive parameters
            start_time = time.time()

            # Merge contexts
            merged_context = context if context else {}
            merged_context.update(analysis)
            merged_context.update(params)

            response = model.synthesize(text=text, emotion=params["emotion"], context=merged_context)
            response_time_ms = (time.time() - start_time) * 1000

            # Update bonding score
            if user_id in self._scores and model_id in self._scores[user_id]:
                score = self._scores[user_id][model_id]
                score.total_interactions += 1

                # Update average response time
                score.avg_response_time_ms = (
                    score.avg_response_time_ms * (score.total_interactions - 1) + response_time_ms
                ) / score.total_interactions

                # Context awareness score based on how well emotion matched
                if params["emotion"] == response.emotion:
                    score.context_awareness_score = min(1.0, score.context_awareness_score + 0.1)

                score.calculate_overall_score()
                score.last_updated = datetime.utcnow().isoformat()

            return response

        except Exception as e:
            logger.error("Experimentation error: %s", e)
            return None

    def provide_feedback(self, user_id: str, model_id: str, feedback: str) -> bool:
        """
        Provide feedback on model performance.
        feedback: 'positive', 'negative', or 'neutral'
        """
        try:
            with self._lock:
                if user_id not in self._scores or model_id not in self._scores[user_id]:
                    return False

                score = self._scores[user_id][model_id]

                if feedback == "positive":
                    score.positive_feedback += 1
                    score.user_preference_score = min(1.0, score.user_preference_score + 0.1)
                elif feedback == "negative":
                    score.negative_feedback += 1
                    score.user_preference_score = max(0.0, score.user_preference_score - 0.1)
                else:
                    score.neutral_feedback += 1

                score.calculate_overall_score()
                self._save_bonding_state(user_id)

                return True

        except Exception as e:
            logger.error("Failed to provide feedback: %s", e)
            return False

    def evaluate_and_select(self, user_id: str) -> str | None:
        """
        Evaluate all experimented models and select the best one.
        Returns selected model_id.
        """
        try:
            with self._lock:
                if user_id not in self._scores:
                    return None

                scores = self._scores[user_id]
                if not scores:
                    return None

                # Calculate final scores
                for score in scores.values():
                    score.calculate_overall_score()

                # Select best model
                best_model_id = max(scores.items(), key=lambda x: x[1].overall_score)[0]

                self._selected_models[user_id] = best_model_id
                self._bonding_states[user_id] = BondingPhase.BONDED

                self._save_bonding_state(user_id)

                logger.info(
                    f"Selected model {best_model_id} for user {user_id} "
                    f"with score {scores[best_model_id].overall_score:.2f}"
                )

                return best_model_id

        except Exception as e:
            logger.error("Failed to evaluate and select: %s", e)
            return None

    def get_selected_model(self, user_id: str) -> VoiceModel | None:
        """Get the selected voice model for a user"""
        with self._lock:
            model_id = self._selected_models.get(user_id)
            if model_id:
                return self.registry.get_model(model_id)
            return None

    def get_bonding_status(self, user_id: str) -> dict[str, Any]:
        """Get current bonding status for a user"""
        with self._lock:
            if user_id not in self._bonding_states:
                return {"status": "not_started"}

            return {
                "status": self._bonding_states[user_id].value,
                "selected_model": self._selected_models.get(user_id),
                "experimented_models": len(self._scores.get(user_id, {})),
                "scores": {model_id: score.overall_score for model_id, score in self._scores.get(user_id, {}).items()},
            }

    def _save_bonding_state(self, user_id: str) -> None:
        """Save bonding state to disk"""
        try:
            state_file = os.path.join(self.data_dir, f"{user_id}_bonding.json")

            state_data = {
                "phase": self._bonding_states.get(user_id, BondingPhase.DISCOVERY).value,
                "selected_model": self._selected_models.get(user_id),
                "scores": {model_id: asdict(score) for model_id, score in self._scores.get(user_id, {}).items()},
                "updated_at": datetime.utcnow().isoformat(),
            }

            with open(state_file, "w") as f:
                json.dump(state_data, f, indent=2)

        except Exception as e:
            logger.error("Failed to save bonding state: %s", e)


# Global instances
_default_profiler: EngagementProfiler | None = None
_default_bonding_protocol: VoiceBondingProtocol | None = None


def get_default_profiler() -> EngagementProfiler:
    """Get or create default engagement profiler"""
    global _default_profiler
    if _default_profiler is None:
        _default_profiler = EngagementProfiler()
    return _default_profiler


def get_default_bonding_protocol(
    registry: VoiceModelRegistry | None = None,
    profiler: EngagementProfiler | None = None,
) -> VoiceBondingProtocol:
    """Get or create default bonding protocol"""
    global _default_bonding_protocol
    if _default_bonding_protocol is None:
        from app.core.voice_models import get_default_registry

        reg = registry or get_default_registry()
        prof = profiler or get_default_profiler()
        _default_bonding_protocol = VoiceBondingProtocol(reg, prof)
    return _default_bonding_protocol
