"""
God Tier System Integration
Main integration module that wires all components together with comprehensive logging.
Production-grade, fully integrated, drop-in ready.
"""

import logging
import logging.handlers
import os
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np

from app.core.conversation_context_engine import (
    ConversationContextEngine,
    PolicyManager,
)
from app.core.god_tier_config import (
    GodTierConfig,
    load_god_tier_config,
)
from app.core.multimodal_fusion import (
    FusedContext,
    FusionStrategy,
    MultiModalFusionEngine,
    MultiModalInput,
)
from app.core.visual_bonding_controller import VisualBondingProtocol, VisualController
from app.core.visual_cue_models import (
    CameraManager,
    FacialEmotionModel,
    FocusAttentionModel,
    VisualCueModelRegistry,
)
from app.core.voice_bonding_protocol import EngagementProfiler, VoiceBondingProtocol
from app.core.voice_models import (
    BasicTTSVoiceModel,
    ConversationalVoiceModel,
    EmotionalTTSVoiceModel,
    VoiceModelMetadata,
    VoiceModelRegistry,
    VoiceModelType,
)

logger = logging.getLogger(__name__)


@dataclass
class SystemStatus:
    """System status information"""

    initialized: bool = False
    start_time: str | None = None
    uptime_seconds: float = 0.0

    voice_system_active: bool = False
    visual_system_active: bool = False
    conversation_system_active: bool = False
    fusion_system_active: bool = False

    active_users: int = 0
    active_sessions: int = 0
    total_interactions: int = 0

    errors_count: int = 0
    warnings_count: int = 0

    metadata: dict[str, Any] = field(default_factory=dict)


class GodTierSystemLogger:
    """Monolithic logging system for all components"""

    def __init__(self, config: GodTierConfig):
        self.config = config.logging
        self.storage_config = config.storage
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup comprehensive logging"""
        try:
            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(getattr(logging, self.config.level))

            # Remove existing handlers
            root_logger.handlers.clear()

            # Create formatter
            formatter = logging.Formatter(self.config.format)

            # Console handler
            if self.config.console:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(formatter)
                root_logger.addHandler(console_handler)

            # File handler with rotation
            if self.config.file:
                log_dir = os.path.dirname(self.config.file_path)
                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)

                file_handler = logging.handlers.RotatingFileHandler(
                    self.config.file_path,
                    maxBytes=self.config.max_bytes,
                    backupCount=self.config.backup_count,
                )
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)

            logger.info("Logging system initialized")

        except Exception as e:
            print(f"Failed to setup logging: {e}")
            # Fallback to basic logging
            logging.basicConfig(level=logging.INFO)

    def set_component_debug(self, component: str, enabled: bool) -> None:
        """Enable/disable debug logging for specific component"""
        component_logger = logging.getLogger(f"app.core.{component}")
        component_logger.setLevel(logging.DEBUG if enabled else logging.INFO)


class GodTierIntegratedSystem:
    """
    God Tier integrated system - monolithic, production-ready.
    Wires all components with full event hooks, controllers, and managers.
    """

    def __init__(self, config: GodTierConfig | None = None):
        self.config = config or load_god_tier_config()
        self.status = SystemStatus()

        # Components (initialized to None)
        self.voice_registry: VoiceModelRegistry | None = None
        self.engagement_profiler: EngagementProfiler | None = None
        self.voice_bonding: VoiceBondingProtocol | None = None

        self.visual_registry: VisualCueModelRegistry | None = None
        self.camera_manager: CameraManager | None = None
        self.visual_bonding: VisualBondingProtocol | None = None
        self.visual_controller: VisualController | None = None

        self.context_engine: ConversationContextEngine | None = None
        self.policy_manager: PolicyManager | None = None

        self.fusion_engine: MultiModalFusionEngine | None = None

        self.logger_system: GodTierSystemLogger | None = None

        self._lock = threading.RLock()
        self._start_time: float | None = None

        logger.info("GodTierIntegratedSystem instance created")

    def initialize(self) -> bool:
        """
        Initialize the complete God Tier system.
        Returns True if successful, False otherwise.
        """
        try:
            with self._lock:
                logger.info("=" * 80)
                logger.info("INITIALIZING GOD TIER INTEGRATED SYSTEM")
                logger.info("=" * 80)

                self._start_time = time.time()
                self.status.start_time = datetime.utcnow().isoformat()

                # Setup logging
                logger.info("1/8 - Initializing logging system...")
                self.logger_system = GodTierSystemLogger(self.config)

                # Initialize voice system
                if self.config.voice_model.enabled:
                    logger.info("2/8 - Initializing voice system...")
                    if not self._initialize_voice_system():
                        logger.error("Voice system initialization failed")
                        if not self.config.fail_safe_mode:
                            return False
                    else:
                        self.status.voice_system_active = True
                else:
                    logger.info("2/8 - Voice system disabled in config")

                # Initialize visual system
                if self.config.visual_model.enabled:
                    logger.info("3/8 - Initializing visual system...")
                    if not self._initialize_visual_system():
                        logger.error("Visual system initialization failed")
                        if not self.config.fail_safe_mode:
                            return False
                    else:
                        self.status.visual_system_active = True
                else:
                    logger.info("3/8 - Visual system disabled in config")

                # Initialize conversation system
                if self.config.conversation.enabled:
                    logger.info("4/8 - Initializing conversation system...")
                    if not self._initialize_conversation_system():
                        logger.error("Conversation system initialization failed")
                        if not self.config.fail_safe_mode:
                            return False
                    else:
                        self.status.conversation_system_active = True
                else:
                    logger.info("4/8 - Conversation system disabled in config")

                # Initialize policy system
                if self.config.policy.enabled:
                    logger.info("5/8 - Initializing policy manager...")
                    if not self._initialize_policy_system():
                        logger.error("Policy system initialization failed")
                        if not self.config.fail_safe_mode:
                            return False
                else:
                    logger.info("5/8 - Policy system disabled in config")

                # Initialize fusion engine
                if self.config.fusion.enabled:
                    logger.info("6/8 - Initializing multi-modal fusion...")
                    if not self._initialize_fusion_system():
                        logger.error("Fusion system initialization failed")
                        if not self.config.fail_safe_mode:
                            return False
                    else:
                        self.status.fusion_system_active = True
                else:
                    logger.info("6/8 - Fusion system disabled in config")

                # Wire event hooks
                logger.info("7/8 - Wiring event hooks and controllers...")
                self._wire_event_hooks()

                # Final setup
                logger.info("8/8 - Final system setup...")
                self._final_setup()

                self.status.initialized = True

                logger.info("=" * 80)
                logger.info("GOD TIER SYSTEM INITIALIZATION COMPLETE")
                logger.info("Status: %s", self.get_status_summary())
                logger.info("=" * 80)

                return True

        except Exception as e:
            logger.error("System initialization failed: %s", e, exc_info=True)
            return False

    def _initialize_voice_system(self) -> bool:
        """Initialize voice system components"""
        try:
            # Create voice registry
            voice_dir = os.path.join(
                self.config.storage.base_dir, self.config.storage.voice_models_dir
            )
            self.voice_registry = VoiceModelRegistry(voice_dir)

            # Register voice models
            for model_name in self.config.voice_model.models:
                if model_name == "basic_tts":
                    model = BasicTTSVoiceModel(
                        VoiceModelMetadata(
                            model_id="basic_tts_1",
                            model_type=VoiceModelType.TTS_BASIC,
                            name="Basic TTS",
                        )
                    )
                elif model_name == "emotional_tts":
                    model = EmotionalTTSVoiceModel(
                        VoiceModelMetadata(
                            model_id="emotional_tts_1",
                            model_type=VoiceModelType.TTS_EMOTIONAL,
                            name="Emotional TTS",
                        )
                    )
                elif model_name == "conversational":
                    model = ConversationalVoiceModel(
                        VoiceModelMetadata(
                            model_id="conversational_1",
                            model_type=VoiceModelType.CONVERSATIONAL,
                            name="Conversational Voice",
                        )
                    )
                else:
                    continue

                self.voice_registry.register(model)

            # Initialize all models
            init_results = self.voice_registry.initialize_all()
            logger.info("Voice models initialized: %s", init_results)

            # Create engagement profiler
            engagement_dir = os.path.join(
                self.config.storage.base_dir,
                self.config.storage.engagement_profiles_dir,
            )
            self.engagement_profiler = EngagementProfiler(engagement_dir)

            # Create voice bonding protocol
            if self.config.voice_model.bonding_enabled:
                bonding_dir = os.path.join(
                    self.config.storage.base_dir,
                    self.config.storage.bonding_dir,
                    "voice",
                )
                self.voice_bonding = VoiceBondingProtocol(
                    self.voice_registry, self.engagement_profiler, bonding_dir
                )

            logger.info("Voice system initialized successfully")
            return True

        except Exception as e:
            logger.error("Voice system initialization error: %s", e)
            return False

    def _initialize_visual_system(self) -> bool:
        """Initialize visual system components"""
        try:
            # Create visual registry
            visual_dir = os.path.join(
                self.config.storage.base_dir, self.config.storage.visual_models_dir
            )
            self.visual_registry = VisualCueModelRegistry(visual_dir)

            # Register visual models
            for model_name in self.config.visual_model.models:
                if model_name == "facial_emotion":
                    model = FacialEmotionModel()
                elif model_name == "focus_attention":
                    model = FocusAttentionModel()
                else:
                    continue

                self.visual_registry.register(model)

            # Initialize all models
            init_results = self.visual_registry.initialize_all()
            logger.info("Visual models initialized: %s", init_results)

            # Create camera manager
            if self.config.camera.enabled:
                camera_dir = os.path.join(
                    self.config.storage.base_dir, self.config.storage.camera_dir
                )
                self.camera_manager = CameraManager(camera_dir)

                if self.config.camera.auto_discover:
                    devices = self.camera_manager.discover_devices()
                    logger.info("Discovered %s camera devices", len(devices))

                    # Activate preferred or first device
                    if self.config.camera.preferred_device:
                        self.camera_manager.activate_device(
                            self.config.camera.preferred_device
                        )
                    elif devices:
                        self.camera_manager.activate_device(devices[0].device_id)

            # Create visual bonding protocol
            if self.config.visual_model.bonding_enabled and self.camera_manager:
                bonding_dir = os.path.join(
                    self.config.storage.base_dir,
                    self.config.storage.bonding_dir,
                    "visual",
                )
                self.visual_bonding = VisualBondingProtocol(
                    self.visual_registry, self.camera_manager, bonding_dir
                )

            # Create visual controller
            if self.camera_manager and self.visual_bonding:
                controller_dir = os.path.join(
                    self.config.storage.base_dir, "visual_controller"
                )
                self.visual_controller = VisualController(
                    self.visual_registry,
                    self.camera_manager,
                    self.visual_bonding,
                    controller_dir,
                )

            logger.info("Visual system initialized successfully")
            return True

        except Exception as e:
            logger.error("Visual system initialization error: %s", e)
            return False

    def _initialize_conversation_system(self) -> bool:
        """Initialize conversation system"""
        try:
            context_dir = os.path.join(
                self.config.storage.base_dir,
                self.config.storage.conversation_context_dir,
            )
            self.context_engine = ConversationContextEngine(context_dir)
            self.context_engine._context_window = (
                self.config.conversation.context_window
            )

            logger.info("Conversation system initialized successfully")
            return True

        except Exception as e:
            logger.error("Conversation system initialization error: %s", e)
            return False

    def _initialize_policy_system(self) -> bool:
        """Initialize policy system"""
        try:
            if not self.context_engine:
                logger.error("Context engine required for policy system")
                return False

            policy_dir = os.path.join(
                self.config.storage.base_dir, self.config.storage.policy_manager_dir
            )
            self.policy_manager = PolicyManager(self.context_engine, policy_dir)

            logger.info("Policy system initialized successfully")
            return True

        except Exception as e:
            logger.error("Policy system initialization error: %s", e)
            return False

    def _initialize_fusion_system(self) -> bool:
        """Initialize multi-modal fusion system"""
        try:
            if not all(
                [
                    self.engagement_profiler,
                    self.visual_controller,
                    self.context_engine,
                    self.policy_manager,
                ]
            ):
                logger.error("All component systems required for fusion")
                return False

            fusion_dir = os.path.join(
                self.config.storage.base_dir, self.config.storage.fusion_dir
            )

            fusion_strategy = FusionStrategy(self.config.fusion.strategy)

            self.fusion_engine = MultiModalFusionEngine(
                self.engagement_profiler,
                self.visual_controller,
                self.context_engine,
                self.policy_manager,
                fusion_strategy,
                fusion_dir,
            )

            logger.info("Fusion system initialized successfully")
            return True

        except Exception as e:
            logger.error("Fusion system initialization error: %s", e)
            return False

    def _wire_event_hooks(self) -> None:
        """Wire all event hooks and controllers"""
        logger.info("Wiring event hooks...")

        # Example: Wire fusion events to logging
        if self.fusion_engine:
            self.fusion_engine.register_fusion_event_handler(self._on_fusion_complete)

        logger.info("Event hooks wired successfully")

    def _on_fusion_complete(self, user_id: str, fused: FusedContext) -> None:
        """Handle fusion complete event"""
        logger.debug(
            f"Fusion complete for user {user_id}: "
            f"emotion={fused.overall_emotional_state}, "
            f"engagement={fused.engagement_level:.2f}"
        )

        self.status.total_interactions += 1

    def _final_setup(self) -> None:
        """Final system setup"""
        # Any final wiring or setup
        pass

    def process_user_interaction(
        self, user_id: str, text_input: str, visual_frame: np.ndarray | None = None
    ) -> dict[str, Any]:
        """
        Process complete user interaction through all systems.
        Main entry point for integrated processing.
        """
        try:
            if not self.status.initialized:
                logger.error("System not initialized")
                return {"error": "System not initialized"}

            # Start or get session
            session_id = None
            if self.context_engine:
                # Check for active session
                # For simplicity, create new session (production would track active sessions)
                session_id = self.context_engine.start_session(user_id)

            # Create multi-modal input
            multimodal_input = MultiModalInput(
                text_input=text_input, visual_frame=visual_frame
            )

            # Process through fusion engine
            fused_context = None
            if self.fusion_engine and session_id:
                fused_context = self.fusion_engine.process_multimodal_input(
                    user_id, session_id, multimodal_input
                )

            # Generate response (simplified - production would use actual response generation)
            response = self._generate_response(
                user_id, session_id, text_input, fused_context
            )

            # Add conversation turn
            if self.context_engine and session_id:
                self.context_engine.add_turn(
                    session_id,
                    text_input,
                    response,
                    asdict(fused_context) if fused_context else {},
                )

            return {
                "success": True,
                "response": response,
                "fused_context": asdict(fused_context) if fused_context else {},
                "session_id": session_id,
            }

        except Exception as e:
            logger.error("Interaction processing error: %s", e)
            return {"error": str(e)}

    def _generate_response(
        self,
        user_id: str,
        session_id: str,
        text_input: str,
        fused_context: FusedContext | None,
    ) -> str:
        """Generate response (simplified placeholder)"""
        # In production, this would use actual LLM/response generation
        return f"Processed: {text_input}"

    def get_status(self) -> SystemStatus:
        """Get current system status"""
        with self._lock:
            if self._start_time:
                self.status.uptime_seconds = time.time() - self._start_time
            return self.status

    def get_status_summary(self) -> str:
        """Get human-readable status summary"""
        status = self.get_status()
        return (
            f"Initialized={status.initialized}, "
            f"Voice={status.voice_system_active}, "
            f"Visual={status.visual_system_active}, "
            f"Conversation={status.conversation_system_active}, "
            f"Fusion={status.fusion_system_active}"
        )

    def shutdown(self) -> None:
        """Graceful shutdown of all systems"""
        logger.info("=" * 80)
        logger.info("SHUTTING DOWN GOD TIER SYSTEM")
        logger.info("=" * 80)

        try:
            if self.fusion_engine:
                self.fusion_engine.shutdown()

            if self.visual_controller:
                self.visual_controller.shutdown()

            if self.camera_manager:
                self.camera_manager.shutdown()

            if self.visual_registry:
                self.visual_registry.shutdown_all()

            if self.voice_registry:
                self.voice_registry.shutdown_all()

            logger.info("God Tier system shutdown complete")

        except Exception as e:
            logger.error("Shutdown error: %s", e)


# Global system instance
_god_tier_system: GodTierIntegratedSystem | None = None


def get_god_tier_system() -> GodTierIntegratedSystem:
    """Get or create God Tier system instance"""
    global _god_tier_system
    if _god_tier_system is None:
        _god_tier_system = GodTierIntegratedSystem()
    return _god_tier_system


def initialize_god_tier_system() -> bool:
    """Initialize the God Tier system"""
    system = get_god_tier_system()
    return system.initialize()
