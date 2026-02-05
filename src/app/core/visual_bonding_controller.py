"""
Visual Bonding Protocol and Visual Controller
Handles visual model experimentation, scoring, and event integration.
Production-grade, fully integrated.
"""

import json
import logging
import os
import threading
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np

from app.core.visual_cue_models import (
    CameraManager,
    VisualCueData,
    VisualCueModel,
    VisualCueModelRegistry,
)

logger = logging.getLogger(__name__)


class VisualBondingPhase(Enum):
    """Phases of visual bonding"""

    DISCOVERY = "discovery"
    CALIBRATION = "calibration"
    EXPERIMENTATION = "experimentation"
    EVALUATION = "evaluation"
    BONDED = "bonded"


@dataclass
class VisualBondingScore:
    """Score for visual model during bonding"""

    model_id: str
    total_detections: int = 0
    successful_detections: int = 0
    failed_detections: int = 0
    avg_confidence: float = 0.0
    avg_latency_ms: float = 0.0
    emotion_accuracy: float = 0.0
    focus_accuracy: float = 0.0
    overall_score: float = 0.0
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def calculate_overall_score(self) -> float:
        """Calculate weighted overall score"""
        if self.total_detections == 0:
            return 0.0

        # Success rate (30%)
        success_rate = self.successful_detections / self.total_detections
        success_component = success_rate * 0.3

        # Confidence (25%)
        confidence_component = self.avg_confidence * 0.25

        # Performance (20%)
        perf_score = max(0, 1.0 - (self.avg_latency_ms / 500.0))
        performance_component = perf_score * 0.2

        # Accuracy (25%)
        accuracy_component = (self.emotion_accuracy + self.focus_accuracy) / 2 * 0.25

        self.overall_score = max(
            0.0,
            min(
                1.0,
                success_component
                + confidence_component
                + performance_component
                + accuracy_component,
            ),
        )
        return self.overall_score


class VisualBondingProtocol:
    """
    Visual model bonding protocol with experimentation and scoring.
    Selects optimal visual model based on detection performance.
    """

    def __init__(
        self,
        registry: VisualCueModelRegistry,
        camera_manager: CameraManager,
        data_dir: str = "data/visual_bonding",
    ):
        self.registry = registry
        self.camera_manager = camera_manager
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self._bonding_states: dict[str, VisualBondingPhase] = {}
        self._scores: dict[str, dict[str, VisualBondingScore]] = {}
        self._selected_models: dict[str, str] = {}
        self._ground_truth: dict[str, Any] = {}
        self._lock = threading.RLock()

        logger.info("VisualBondingProtocol initialized")

    def start_bonding(self, user_id: str) -> bool:
        """Start bonding process for a user"""
        try:
            with self._lock:
                if user_id in self._bonding_states:
                    logger.warning(f"Visual bonding already in progress for {user_id}")
                    return False

                self._bonding_states[user_id] = VisualBondingPhase.DISCOVERY
                self._scores[user_id] = {}

                # Initialize scores for all models
                for model_id in self.registry.list_models():
                    self._scores[user_id][model_id] = VisualBondingScore(
                        model_id=model_id
                    )

                logger.info(f"Started visual bonding for user {user_id}")
                return True

        except Exception as e:
            logger.error(f"Failed to start visual bonding: {e}")
            return False

    def experiment_with_model(
        self,
        user_id: str,
        model_id: str,
        frame_data: np.ndarray,
        ground_truth: dict[str, Any] | None = None,
    ) -> VisualCueData | None:
        """
        Experiment with a model during bonding.
        Returns detection results and updates bonding score.
        """
        try:
            model = self.registry.get_model(model_id)
            if not model or not model.is_ready():
                logger.error(f"Visual model not ready: {model_id}")
                return None

            # Perform detection
            start_time = time.time()
            cue_data = model.detect(frame_data)
            latency_ms = (time.time() - start_time) * 1000

            # Update bonding score
            if user_id in self._scores and model_id in self._scores[user_id]:
                score = self._scores[user_id][model_id]
                score.total_detections += 1

                if cue_data.is_present:
                    score.successful_detections += 1
                else:
                    score.failed_detections += 1

                # Update average confidence
                score.avg_confidence = (
                    score.avg_confidence * (score.total_detections - 1)
                    + cue_data.emotion_confidence
                ) / score.total_detections

                # Update average latency
                score.avg_latency_ms = (
                    score.avg_latency_ms * (score.total_detections - 1) + latency_ms
                ) / score.total_detections

                # Compare with ground truth if available
                if ground_truth:
                    if "emotion" in ground_truth:
                        if ground_truth["emotion"] == cue_data.emotion.value:
                            score.emotion_accuracy = min(
                                1.0, score.emotion_accuracy + 0.05
                            )

                    if "focus_level" in ground_truth:
                        if ground_truth["focus_level"] == cue_data.focus_level.value:
                            score.focus_accuracy = min(1.0, score.focus_accuracy + 0.05)

                score.calculate_overall_score()
                score.last_updated = datetime.utcnow().isoformat()

            return cue_data

        except Exception as e:
            logger.error(f"Visual experimentation error: {e}")
            return None

    def set_ground_truth(self, user_id: str, truth_data: dict[str, Any]) -> None:
        """Set ground truth for calibration"""
        with self._lock:
            self._ground_truth[user_id] = truth_data

    def calibrate(
        self,
        user_id: str,
        calibration_frames: list[np.ndarray],
        ground_truth_sequence: list[dict[str, Any]],
    ) -> dict[str, float]:
        """
        Calibrate models with known ground truth.
        Returns calibration accuracy for each model.
        """
        if len(calibration_frames) != len(ground_truth_sequence):
            logger.error("Calibration frame count mismatch")
            return {}

        try:
            with self._lock:
                if user_id not in self._bonding_states:
                    return {}

                self._bonding_states[user_id] = VisualBondingPhase.CALIBRATION

                calibration_results = {}

                for model_id in self.registry.list_models():
                    model = self.registry.get_model(model_id)
                    if not model or not model.is_ready():
                        continue

                    correct_count = 0

                    for frame, truth in zip(calibration_frames, ground_truth_sequence):
                        cue_data = self.experiment_with_model(
                            user_id, model_id, frame, truth
                        )

                        if cue_data and "emotion" in truth:
                            if cue_data.emotion.value == truth["emotion"]:
                                correct_count += 1

                    accuracy = correct_count / len(calibration_frames)
                    calibration_results[model_id] = accuracy

                self._bonding_states[user_id] = VisualBondingPhase.EXPERIMENTATION
                self._save_bonding_state(user_id)

                logger.info(f"Calibration complete for user {user_id}")
                return calibration_results

        except Exception as e:
            logger.error(f"Calibration error: {e}")
            return {}

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
                self._bonding_states[user_id] = VisualBondingPhase.BONDED

                self._save_bonding_state(user_id)

                logger.info(
                    f"Selected visual model {best_model_id} for user {user_id} "
                    f"with score {scores[best_model_id].overall_score:.2f}"
                )

                return best_model_id

        except Exception as e:
            logger.error(f"Failed to evaluate and select: {e}")
            return None

    def get_selected_model(self, user_id: str) -> VisualCueModel | None:
        """Get the selected visual model for a user"""
        with self._lock:
            model_id = self._selected_models.get(user_id)
            if model_id:
                return self.registry.get_model(model_id)
            return None

    def get_bonding_status(self, user_id: str) -> dict[str, Any]:
        """Get current bonding status"""
        with self._lock:
            if user_id not in self._bonding_states:
                return {"status": "not_started"}

            return {
                "status": self._bonding_states[user_id].value,
                "selected_model": self._selected_models.get(user_id),
                "experimented_models": len(self._scores.get(user_id, {})),
                "scores": {
                    model_id: score.overall_score
                    for model_id, score in self._scores.get(user_id, {}).items()
                },
            }

    def _save_bonding_state(self, user_id: str) -> None:
        """Save bonding state to disk"""
        try:
            state_file = os.path.join(self.data_dir, f"{user_id}_visual_bonding.json")

            state_data = {
                "phase": self._bonding_states.get(
                    user_id, VisualBondingPhase.DISCOVERY
                ).value,
                "selected_model": self._selected_models.get(user_id),
                "scores": {
                    model_id: asdict(score)
                    for model_id, score in self._scores.get(user_id, {}).items()
                },
                "updated_at": datetime.utcnow().isoformat(),
            }

            with open(state_file, "w") as f:
                json.dump(state_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save visual bonding state: {e}")


class VisualEvent(Enum):
    """Types of visual events"""

    EMOTION_DETECTED = "emotion_detected"
    EMOTION_CHANGED = "emotion_changed"
    FOCUS_CHANGED = "focus_changed"
    USER_PRESENT = "user_present"
    USER_ABSENT = "user_absent"
    GAZE_DIRECTED = "gaze_directed"
    GAZE_DIVERTED = "gaze_diverted"
    EXPRESSION_DETECTED = "expression_detected"


@dataclass
class VisualEventData:
    """Data for visual events"""

    event_type: VisualEvent
    user_id: str
    cue_data: VisualCueData
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


class VisualController:
    """
    Visual controller with seamless event integration.
    Manages visual detection pipeline and event dispatch.
    """

    def __init__(
        self,
        registry: VisualCueModelRegistry,
        camera_manager: CameraManager,
        bonding_protocol: VisualBondingProtocol,
        data_dir: str = "data/visual_controller",
    ):
        self.registry = registry
        self.camera_manager = camera_manager
        self.bonding_protocol = bonding_protocol
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self._event_handlers: dict[VisualEvent, list[Callable]] = defaultdict(list)
        self._active_users: dict[str, bool] = {}
        self._last_cue_data: dict[str, VisualCueData] = {}
        self._is_running = False
        self._lock = threading.RLock()

        logger.info("VisualController initialized")

    def register_event_handler(
        self, event_type: VisualEvent, handler: Callable[[VisualEventData], None]
    ) -> None:
        """Register an event handler"""
        with self._lock:
            self._event_handlers[event_type].append(handler)
            logger.info(f"Registered handler for {event_type.value}")

    def unregister_event_handler(
        self, event_type: VisualEvent, handler: Callable[[VisualEventData], None]
    ) -> None:
        """Unregister an event handler"""
        with self._lock:
            if handler in self._event_handlers[event_type]:
                self._event_handlers[event_type].remove(handler)

    def start_monitoring(self, user_id: str) -> bool:
        """Start visual monitoring for a user"""
        try:
            with self._lock:
                if user_id in self._active_users and self._active_users[user_id]:
                    logger.warning(f"Monitoring already active for {user_id}")
                    return False

                self._active_users[user_id] = True

                # Start camera capture if not already running
                if not self._is_running:
                    success = self.camera_manager.start_capture(
                        lambda frame: self._on_frame_captured(frame, user_id)
                    )
                    if success:
                        self._is_running = True
                    else:
                        return False

                logger.info(f"Started visual monitoring for {user_id}")
                return True

        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return False

    def stop_monitoring(self, user_id: str) -> None:
        """Stop visual monitoring for a user"""
        try:
            with self._lock:
                if user_id in self._active_users:
                    self._active_users[user_id] = False

                # Stop camera if no active users
                if not any(self._active_users.values()):
                    self.camera_manager.stop_capture()
                    self._is_running = False

                logger.info(f"Stopped visual monitoring for {user_id}")

        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")

    def _on_frame_captured(self, frame: np.ndarray, user_id: str) -> None:
        """Handle captured frame"""
        try:
            if not self._active_users.get(user_id, False):
                return

            # Get selected model for user
            model = self.bonding_protocol.get_selected_model(user_id)
            if not model or not model.is_ready():
                # Use default model if no bonded model
                models = self.registry.list_models()
                if models:
                    model = self.registry.get_model(models[0])
                else:
                    return

            # Detect visual cues
            cue_data = model.detect(frame)

            # Generate and dispatch events
            self._process_cue_data(user_id, cue_data)

            # Store last cue data
            self._last_cue_data[user_id] = cue_data

        except Exception as e:
            logger.error(f"Frame processing error: {e}")

    def _process_cue_data(self, user_id: str, cue_data: VisualCueData) -> None:
        """Process cue data and generate events"""
        try:
            # User presence
            if cue_data.is_present:
                last_cue = self._last_cue_data.get(user_id)
                if not last_cue or not last_cue.is_present:
                    self._dispatch_event(VisualEvent.USER_PRESENT, user_id, cue_data)
            else:
                last_cue = self._last_cue_data.get(user_id)
                if last_cue and last_cue.is_present:
                    self._dispatch_event(VisualEvent.USER_ABSENT, user_id, cue_data)
                return

            last_cue = self._last_cue_data.get(user_id)

            # Emotion detection
            self._dispatch_event(VisualEvent.EMOTION_DETECTED, user_id, cue_data)

            # Emotion change
            if last_cue and last_cue.emotion != cue_data.emotion:
                self._dispatch_event(
                    VisualEvent.EMOTION_CHANGED,
                    user_id,
                    cue_data,
                    {"previous_emotion": last_cue.emotion.value},
                )

            # Focus change
            if last_cue and last_cue.focus_level != cue_data.focus_level:
                self._dispatch_event(
                    VisualEvent.FOCUS_CHANGED,
                    user_id,
                    cue_data,
                    {"previous_focus": last_cue.focus_level.value},
                )

            # Gaze direction
            gaze_x, gaze_y = cue_data.gaze_direction
            if abs(gaze_x) < 0.3 and abs(gaze_y) < 0.3:
                self._dispatch_event(VisualEvent.GAZE_DIRECTED, user_id, cue_data)
            else:
                if last_cue:
                    last_gaze_x, last_gaze_y = last_cue.gaze_direction
                    if abs(last_gaze_x) < 0.3 and abs(last_gaze_y) < 0.3:
                        self._dispatch_event(
                            VisualEvent.GAZE_DIVERTED, user_id, cue_data
                        )

            # Expression detection
            self._dispatch_event(VisualEvent.EXPRESSION_DETECTED, user_id, cue_data)

        except Exception as e:
            logger.error(f"Error processing cue data: {e}")

    def _dispatch_event(
        self,
        event_type: VisualEvent,
        user_id: str,
        cue_data: VisualCueData,
        extra_metadata: dict | None = None,
    ) -> None:
        """Dispatch event to registered handlers"""
        try:
            metadata = extra_metadata or {}

            event_data = VisualEventData(
                event_type=event_type,
                user_id=user_id,
                cue_data=cue_data,
                metadata=metadata,
            )

            handlers = self._event_handlers.get(event_type, [])
            for handler in handlers:
                try:
                    handler(event_data)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")

        except Exception as e:
            logger.error(f"Event dispatch error: {e}")

    def get_last_cue_data(self, user_id: str) -> VisualCueData | None:
        """Get last detected cue data for user"""
        with self._lock:
            return self._last_cue_data.get(user_id)

    def shutdown(self) -> None:
        """Shutdown visual controller"""
        try:
            with self._lock:
                # Stop all monitoring
                for user_id in list(self._active_users.keys()):
                    self.stop_monitoring(user_id)

                self._event_handlers.clear()
                self._last_cue_data.clear()

                logger.info("VisualController shutdown complete")

        except Exception as e:
            logger.error(f"Shutdown error: {e}")


# Global instances
_default_visual_bonding: VisualBondingProtocol | None = None
_default_visual_controller: VisualController | None = None


def get_default_visual_bonding(
    registry: VisualCueModelRegistry | None = None,
    camera_manager: CameraManager | None = None,
) -> VisualBondingProtocol:
    """Get or create default visual bonding protocol"""
    global _default_visual_bonding
    if _default_visual_bonding is None:
        from app.core.visual_cue_models import (
            get_default_camera_manager,
            get_default_visual_registry,
        )

        reg = registry or get_default_visual_registry()
        cam = camera_manager or get_default_camera_manager()
        _default_visual_bonding = VisualBondingProtocol(reg, cam)
    return _default_visual_bonding


def get_default_visual_controller(
    registry: VisualCueModelRegistry | None = None,
    camera_manager: CameraManager | None = None,
    bonding: VisualBondingProtocol | None = None,
) -> VisualController:
    """Get or create default visual controller"""
    global _default_visual_controller
    if _default_visual_controller is None:
        from app.core.visual_cue_models import (
            get_default_camera_manager,
            get_default_visual_registry,
        )

        reg = registry or get_default_visual_registry()
        cam = camera_manager or get_default_camera_manager()
        bond = bonding or get_default_visual_bonding(reg, cam)
        _default_visual_controller = VisualController(reg, cam, bond)
    return _default_visual_controller
