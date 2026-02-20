"""
Multi-Modal Fusion Layer
Integrates voice, vision, and conversation context for comprehensive user understanding.
Production-grade, fully integrated.
"""

import logging
import os
import threading
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np

from app.core.conversation_context_engine import (
    ConversationContextEngine,
    Intent,
    PolicyManager,
)
from app.core.visual_bonding_controller import (
    VisualController,
    VisualEvent,
    VisualEventData,
)
from app.core.visual_cue_models import EmotionType as VisualEmotionType
from app.core.visual_cue_models import FocusLevel
from app.core.voice_bonding_protocol import EngagementProfiler
from app.core.voice_models import VoiceEmotionType

logger = logging.getLogger(__name__)


class ModalityType(Enum):
    """Types of input modalities"""

    VOICE = "voice"
    VISUAL = "visual"
    TEXT = "text"
    GESTURE = "gesture"


class FusionStrategy(Enum):
    """Fusion strategies for multi-modal data"""

    EARLY_FUSION = "early_fusion"  # Combine raw features
    LATE_FUSION = "late_fusion"  # Combine decisions
    HYBRID_FUSION = "hybrid_fusion"  # Combination of both


@dataclass
class MultiModalInput:
    """Multi-modal input data"""

    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    text_input: str | None = None
    audio_data: bytes | None = None
    visual_frame: np.ndarray | None = None
    gesture_data: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FusedContext:
    """Fused multi-modal context"""

    user_id: str
    session_id: str
    timestamp: str

    # Voice modality
    voice_emotion: VoiceEmotionType = VoiceEmotionType.NEUTRAL
    speech_detected: bool = False

    # Visual modality
    visual_emotion: VisualEmotionType = VisualEmotionType.NEUTRAL
    focus_level: FocusLevel = FocusLevel.MEDIUM_FOCUS
    user_present: bool = False
    gaze_engaged: bool = False

    # Conversation modality
    detected_intent: Intent = Intent.UNKNOWN
    active_topics: list[str] = field(default_factory=list)
    context_references: list[str] = field(default_factory=list)

    # Fused understanding
    overall_emotional_state: str = "neutral"
    engagement_level: float = 0.5
    confidence_score: float = 0.5
    attention_score: float = 0.5

    # Adaptive parameters
    recommended_response_style: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)


class MultiModalFusionEngine:
    """
    Multi-modal fusion engine integrating voice, vision, and conversation.
    Provides comprehensive understanding of user state and intent.
    """

    def __init__(
        self,
        voice_profiler: EngagementProfiler,
        visual_controller: VisualController,
        context_engine: ConversationContextEngine,
        policy_manager: PolicyManager,
        fusion_strategy: FusionStrategy = FusionStrategy.HYBRID_FUSION,
        data_dir: str = "data/multimodal_fusion",
    ):

        self.voice_profiler = voice_profiler
        self.visual_controller = visual_controller
        self.context_engine = context_engine
        self.policy_manager = policy_manager
        self.fusion_strategy = fusion_strategy
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self._active_fusions: dict[str, FusedContext] = {}
        self._fusion_history: dict[str, list[FusedContext]] = {}
        self._event_handlers: dict[str, list[Callable]] = {}
        self._lock = threading.RLock()

        # Register for visual events
        self._register_visual_events()

        logger.info("MultiModalFusionEngine initialized with %s", fusion_strategy.value)

    def _register_visual_events(self) -> None:
        """Register handlers for visual events"""
        self.visual_controller.register_event_handler(VisualEvent.EMOTION_CHANGED, self._on_visual_emotion_changed)
        self.visual_controller.register_event_handler(VisualEvent.FOCUS_CHANGED, self._on_focus_changed)
        self.visual_controller.register_event_handler(VisualEvent.USER_PRESENT, self._on_user_presence_changed)
        self.visual_controller.register_event_handler(VisualEvent.GAZE_DIRECTED, self._on_gaze_changed)

    def process_multimodal_input(self, user_id: str, session_id: str, input_data: MultiModalInput) -> FusedContext:
        """
        Process multi-modal input and return fused context.
        Main entry point for multi-modal fusion.
        """
        try:
            with self._lock:
                # Initialize fused context
                fused = FusedContext(
                    user_id=user_id,
                    session_id=session_id,
                    timestamp=input_data.timestamp,
                )

                # Process each modality
                if input_data.text_input:
                    self._process_text_modality(user_id, session_id, input_data.text_input, fused)

                if input_data.visual_frame is not None:
                    self._process_visual_modality(user_id, input_data.visual_frame, fused)

                # Apply fusion strategy
                if self.fusion_strategy == FusionStrategy.EARLY_FUSION:
                    self._apply_early_fusion(fused)
                elif self.fusion_strategy == FusionStrategy.LATE_FUSION:
                    self._apply_late_fusion(fused)
                else:  # HYBRID_FUSION
                    self._apply_hybrid_fusion(fused)

                # Get adaptive policies
                policies = self.policy_manager.get_adaptive_policy(user_id, session_id, asdict(fused))
                fused.recommended_response_style = policies

                # Store fusion result
                self._active_fusions[user_id] = fused

                if user_id not in self._fusion_history:
                    self._fusion_history[user_id] = []
                self._fusion_history[user_id].append(fused)

                # Trigger fusion events
                self._trigger_fusion_event(user_id, fused)

                return fused

        except Exception as e:
            logger.error("Multi-modal fusion error: %s", e)
            return FusedContext(user_id=user_id, session_id=session_id, timestamp=input_data.timestamp)

    def _process_text_modality(self, user_id: str, session_id: str, text: str, fused: FusedContext) -> None:
        """Process text/conversation modality"""
        try:
            # Analyze with engagement profiler
            voice_analysis = self.voice_profiler.analyze_user_input(user_id, text)

            # Update fused context
            fused.speech_detected = True
            fused.voice_emotion = voice_analysis.get("recommended_emotion", VoiceEmotionType.NEUTRAL)

            # Get conversation context
            conv_context = self.context_engine.get_context(session_id)

            if conv_context:
                recent_turns = conv_context.get("recent_turns", [])
                if recent_turns and len(recent_turns) > 0:
                    last_turn = recent_turns[-1]
                    fused.detected_intent = Intent(last_turn.get("detected_intent", "unknown"))

                fused.active_topics = conv_context.get("active_topics", [])
                fused.context_references = recent_turns[-1].get("context_references", []) if recent_turns else []

        except Exception as e:
            logger.error("Text modality processing error: %s", e)

    def _process_visual_modality(self, user_id: str, frame: np.ndarray, fused: FusedContext) -> None:
        """Process visual modality"""
        try:
            # Get last visual cue data
            cue_data = self.visual_controller.get_last_cue_data(user_id)

            if cue_data and cue_data.is_present:
                fused.visual_emotion = cue_data.emotion
                fused.focus_level = cue_data.focus_level
                fused.user_present = True

                # Check gaze engagement
                gaze_x, gaze_y = cue_data.gaze_direction
                fused.gaze_engaged = abs(gaze_x) < 0.3 and abs(gaze_y) < 0.3

        except Exception as e:
            logger.error("Visual modality processing error: %s", e)

    def _apply_early_fusion(self, fused: FusedContext) -> None:
        """Apply early fusion strategy"""
        # Combine features at low level
        # Simplified for production

        # Emotion fusion (weighted average)
        emotions_detected = []
        if fused.speech_detected:
            emotions_detected.append(self._emotion_to_value(fused.voice_emotion.value))
        if fused.user_present:
            emotions_detected.append(self._emotion_to_value(fused.visual_emotion.value))

        if emotions_detected:
            avg_emotion = sum(emotions_detected) / len(emotions_detected)
            fused.overall_emotional_state = self._value_to_emotion(avg_emotion)

        # Engagement level from focus and presence
        engagement = 0.5
        if fused.user_present:
            engagement += 0.2
        if fused.gaze_engaged:
            engagement += 0.2
        if fused.focus_level in [FocusLevel.HIGH_FOCUS, FocusLevel.INTENSE_FOCUS]:
            engagement += 0.1

        fused.engagement_level = min(1.0, engagement)
        fused.confidence_score = 0.8

    def _apply_late_fusion(self, fused: FusedContext) -> None:
        """Apply late fusion strategy"""
        # Combine decisions from individual modalities

        # Take visual emotion if present, otherwise voice
        if fused.user_present:
            fused.overall_emotional_state = fused.visual_emotion.value
        else:
            fused.overall_emotional_state = fused.voice_emotion.value

        # Engagement from multiple signals
        engagement_scores = []
        if fused.user_present:
            engagement_scores.append(0.7)
        if fused.gaze_engaged:
            engagement_scores.append(0.9)
        if fused.focus_level == FocusLevel.HIGH_FOCUS:
            engagement_scores.append(0.8)
        elif fused.focus_level == FocusLevel.INTENSE_FOCUS:
            engagement_scores.append(1.0)

        if engagement_scores:
            fused.engagement_level = sum(engagement_scores) / len(engagement_scores)

        fused.confidence_score = 0.75

    def _apply_hybrid_fusion(self, fused: FusedContext) -> None:
        """Apply hybrid fusion strategy (combination of early and late)"""
        # Best of both worlds

        # Early fusion for emotion
        voice_emotion_val = self._emotion_to_value(fused.voice_emotion.value)
        visual_emotion_val = self._emotion_to_value(fused.visual_emotion.value)

        # Weight visual more if user is present and focused
        visual_weight = 0.6 if fused.user_present else 0.3
        voice_weight = 1.0 - visual_weight

        combined_emotion = voice_emotion_val * voice_weight + visual_emotion_val * visual_weight
        fused.overall_emotional_state = self._value_to_emotion(combined_emotion)

        # Late fusion for engagement
        engagement = 0.3  # Base

        if fused.user_present:
            engagement += 0.2
        if fused.gaze_engaged:
            engagement += 0.25

        focus_bonus = {
            FocusLevel.UNFOCUSED: 0.0,
            FocusLevel.LOW_FOCUS: 0.05,
            FocusLevel.MEDIUM_FOCUS: 0.1,
            FocusLevel.HIGH_FOCUS: 0.15,
            FocusLevel.INTENSE_FOCUS: 0.2,
        }.get(fused.focus_level, 0.1)

        engagement += focus_bonus

        fused.engagement_level = min(1.0, engagement)

        # Attention score
        attention = 0.5
        if fused.gaze_engaged:
            attention += 0.3
        if fused.focus_level in [FocusLevel.HIGH_FOCUS, FocusLevel.INTENSE_FOCUS]:
            attention += 0.2

        fused.attention_score = min(1.0, attention)

        # Confidence based on available modalities
        modalities_active = sum(
            [
                fused.speech_detected,
                fused.user_present,
                fused.focus_level != FocusLevel.UNFOCUSED,
            ]
        )
        fused.confidence_score = min(1.0, 0.5 + (modalities_active * 0.15))

    def _emotion_to_value(self, emotion: str) -> float:
        """Convert emotion string to numeric value"""
        emotion_map = {
            "neutral": 0.5,
            "happy": 0.8,
            "sad": 0.2,
            "angry": 0.1,
            "excited": 0.9,
            "calm": 0.6,
            "empathetic": 0.65,
            "surprised": 0.75,
            "fearful": 0.25,
            "disgusted": 0.15,
            "confused": 0.4,
        }
        return emotion_map.get(emotion.lower(), 0.5)

    def _value_to_emotion(self, value: float) -> str:
        """Convert numeric value to emotion string"""
        if value >= 0.85:
            return "excited"
        elif value >= 0.7:
            return "happy"
        elif value >= 0.55:
            return "calm"
        elif value >= 0.45:
            return "neutral"
        elif value >= 0.3:
            return "confused"
        elif value >= 0.15:
            return "sad"
        else:
            return "angry"

    def _on_visual_emotion_changed(self, event_data: VisualEventData) -> None:
        """Handle visual emotion change event"""
        try:
            user_id = event_data.user_id
            if user_id in self._active_fusions:
                fused = self._active_fusions[user_id]
                fused.visual_emotion = event_data.cue_data.emotion
                # Trigger re-fusion
                self._apply_hybrid_fusion(fused)
        except Exception as e:
            logger.error("Error handling emotion change: %s", e)

    def _on_focus_changed(self, event_data: VisualEventData) -> None:
        """Handle focus change event"""
        try:
            user_id = event_data.user_id
            if user_id in self._active_fusions:
                fused = self._active_fusions[user_id]
                fused.focus_level = event_data.cue_data.focus_level
                self._apply_hybrid_fusion(fused)
        except Exception as e:
            logger.error("Error handling focus change: %s", e)

    def _on_user_presence_changed(self, event_data: VisualEventData) -> None:
        """Handle user presence change"""
        try:
            user_id = event_data.user_id
            if user_id in self._active_fusions:
                fused = self._active_fusions[user_id]
                fused.user_present = event_data.cue_data.is_present
                self._apply_hybrid_fusion(fused)
        except Exception as e:
            logger.error("Error handling presence change: %s", e)

    def _on_gaze_changed(self, event_data: VisualEventData) -> None:
        """Handle gaze change"""
        try:
            user_id = event_data.user_id
            if user_id in self._active_fusions:
                fused = self._active_fusions[user_id]
                gaze_x, gaze_y = event_data.cue_data.gaze_direction
                fused.gaze_engaged = abs(gaze_x) < 0.3 and abs(gaze_y) < 0.3
                self._apply_hybrid_fusion(fused)
        except Exception as e:
            logger.error("Error handling gaze change: %s", e)

    def register_fusion_event_handler(self, handler: Callable[[str, FusedContext], None]) -> None:
        """Register handler for fusion events"""
        with self._lock:
            if "fusion_complete" not in self._event_handlers:
                self._event_handlers["fusion_complete"] = []
            self._event_handlers["fusion_complete"].append(handler)

    def _trigger_fusion_event(self, user_id: str, fused: FusedContext) -> None:
        """Trigger fusion complete event"""
        handlers = self._event_handlers.get("fusion_complete", [])
        for handler in handlers:
            try:
                handler(user_id, fused)
            except Exception as e:
                logger.error("Fusion event handler error: %s", e)

    def get_current_fusion(self, user_id: str) -> FusedContext | None:
        """Get current fused context for user"""
        with self._lock:
            return self._active_fusions.get(user_id)

    def get_fusion_history(self, user_id: str, limit: int = 50) -> list[FusedContext]:
        """Get fusion history for user"""
        with self._lock:
            history = self._fusion_history.get(user_id, [])
            return history[-limit:] if len(history) > limit else history

    def shutdown(self) -> None:
        """Shutdown fusion engine"""
        with self._lock:
            self._active_fusions.clear()
            self._event_handlers.clear()
            logger.info("MultiModalFusionEngine shutdown complete")


# Global instance
_default_fusion_engine: MultiModalFusionEngine | None = None


def get_default_fusion_engine() -> MultiModalFusionEngine:
    """Get or create default fusion engine"""
    global _default_fusion_engine
    if _default_fusion_engine is None:
        from app.core.conversation_context_engine import (
            get_default_context_engine,
            get_default_policy_manager,
        )
        from app.core.visual_bonding_controller import get_default_visual_controller
        from app.core.voice_bonding_protocol import get_default_profiler

        profiler = get_default_profiler()
        visual_ctrl = get_default_visual_controller()
        context_engine = get_default_context_engine()
        policy_mgr = get_default_policy_manager(context_engine)

        _default_fusion_engine = MultiModalFusionEngine(profiler, visual_ctrl, context_engine, policy_mgr)

    return _default_fusion_engine
