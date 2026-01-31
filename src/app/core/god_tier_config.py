"""
God Tier Configuration System
Comprehensive YAML-based configuration for all components.
Production-grade, fully integrated.
"""

import logging
import os
from dataclasses import asdict, dataclass, field
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class VoiceModelConfig:
    """Voice model configuration"""

    enabled: bool = True
    models: list[str] = field(
        default_factory=lambda: ["basic_tts", "emotional_tts", "conversational"]
    )
    default_model: str = "conversational"
    bonding_enabled: bool = True
    experimentation_rounds: int = 5
    auto_select: bool = True


@dataclass
class VisualModelConfig:
    """Visual model configuration"""

    enabled: bool = True
    models: list[str] = field(
        default_factory=lambda: ["facial_emotion", "focus_attention"]
    )
    default_model: str = "facial_emotion"
    bonding_enabled: bool = True
    calibration_frames: int = 30
    detection_fps: int = 10


@dataclass
class CameraConfig:
    """Camera configuration"""

    enabled: bool = True
    auto_discover: bool = True
    preferred_device: str | None = None
    resolution: list[int] = field(default_factory=lambda: [1280, 720])
    fps: int = 30


@dataclass
class ConversationConfig:
    """Conversation engine configuration"""

    enabled: bool = True
    context_window: int = 10
    max_history_turns: int = 1000
    intent_detection: bool = True
    entity_extraction: bool = True
    topic_tracking: bool = True
    session_timeout_minutes: int = 30


@dataclass
class PolicyConfig:
    """Policy manager configuration"""

    enabled: bool = True
    auto_adjust: bool = True
    adjustment_rate: float = 0.05

    # Default policy values (0-1 scale)
    default_response_length: float = 0.5
    default_formality: float = 0.5
    default_empathy: float = 0.7
    default_sensitivity: float = 0.8
    default_humor: float = 0.3

    # Context-aware adjustments
    no_false_alarms: bool = (
        True  # Critical: no overreaction to swearing/sensitive topics
    )
    user_adaptation: bool = True


@dataclass
class FusionConfig:
    """Multi-modal fusion configuration"""

    enabled: bool = True
    strategy: str = "hybrid_fusion"  # early_fusion, late_fusion, hybrid_fusion

    # Modality weights
    voice_weight: float = 0.4
    visual_weight: float = 0.4
    text_weight: float = 0.2

    # Fusion parameters
    confidence_threshold: float = 0.6
    min_modalities: int = 1
    event_driven: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration"""

    enabled: bool = True
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Log destinations
    console: bool = True
    file: bool = True
    file_path: str = "data/logs/god_tier.log"

    # Rotation
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5

    # Component-specific logging
    voice_debug: bool = False
    visual_debug: bool = False
    fusion_debug: bool = False


@dataclass
class DataStorageConfig:
    """Data storage configuration"""

    base_dir: str = "data"

    # Subdirectories
    voice_models_dir: str = "voice_models"
    visual_models_dir: str = "visual_models"
    camera_dir: str = "camera"
    engagement_profiles_dir: str = "engagement_profiles"
    conversation_context_dir: str = "conversation_context"
    policy_manager_dir: str = "policy_manager"
    fusion_dir: str = "multimodal_fusion"
    bonding_dir: str = "bonding"

    # Persistence
    auto_save: bool = True
    save_interval_seconds: int = 30
    backup_enabled: bool = True
    backup_interval_hours: int = 24


@dataclass
class GodTierConfig:
    """Master configuration for God Tier system"""

    version: str = "1.0.0"
    deployment_mode: str = "production"  # production, development, testing

    # Component configurations
    voice_model: VoiceModelConfig = field(default_factory=VoiceModelConfig)
    visual_model: VisualModelConfig = field(default_factory=VisualModelConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    conversation: ConversationConfig = field(default_factory=ConversationConfig)
    policy: PolicyConfig = field(default_factory=PolicyConfig)
    fusion: FusionConfig = field(default_factory=FusionConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    storage: DataStorageConfig = field(default_factory=DataStorageConfig)

    # System-wide settings
    system_name: str = "God Tier Project-AI"
    enable_all_features: bool = True
    fail_safe_mode: bool = True
    auto_recovery: bool = True


class ConfigurationManager:
    """
    Configuration manager with YAML persistence.
    Handles loading, saving, and validation of configurations.
    """

    def __init__(self, config_file: str = "config/god_tier_config.yaml"):
        self.config_file = config_file
        self.config: GodTierConfig = GodTierConfig()
        self._ensure_config_dir()
        logger.info(f"ConfigurationManager initialized with {config_file}")

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists"""
        config_dir = os.path.dirname(self.config_file)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)

    def load_config(self) -> GodTierConfig:
        """Load configuration from YAML file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file) as f:
                    config_dict = yaml.safe_load(f)

                if config_dict:
                    self.config = self._dict_to_config(config_dict)
                    logger.info(f"Configuration loaded from {self.config_file}")
                else:
                    logger.warning("Empty config file, using defaults")
            else:
                logger.info("Config file not found, using defaults")
                self.save_config()  # Save defaults

            return self.config

        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self.config

    def save_config(self) -> bool:
        """Save configuration to YAML file"""
        try:
            config_dict = asdict(self.config)

            with open(self.config_file, "w") as f:
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Configuration saved to {self.config_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    def _dict_to_config(self, config_dict: dict[str, Any]) -> GodTierConfig:
        """Convert dictionary to GodTierConfig"""
        # Simplified conversion - in production, use proper deserialization
        config = GodTierConfig()

        # Update from dict
        for key, value in config_dict.items():
            if hasattr(config, key) and isinstance(value, dict):
                # Handle nested configs
                nested_config = getattr(config, key)
                for nested_key, nested_value in value.items():
                    if hasattr(nested_config, nested_key):
                        setattr(nested_config, nested_key, nested_value)
            elif hasattr(config, key):
                setattr(config, key, value)

        return config

    def get_voice_config(self) -> VoiceModelConfig:
        """Get voice model configuration"""
        return self.config.voice_model

    def get_visual_config(self) -> VisualModelConfig:
        """Get visual model configuration"""
        return self.config.visual_model

    def get_camera_config(self) -> CameraConfig:
        """Get camera configuration"""
        return self.config.camera

    def get_conversation_config(self) -> ConversationConfig:
        """Get conversation configuration"""
        return self.config.conversation

    def get_policy_config(self) -> PolicyConfig:
        """Get policy configuration"""
        return self.config.policy

    def get_fusion_config(self) -> FusionConfig:
        """Get fusion configuration"""
        return self.config.fusion

    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration"""
        return self.config.logging

    def get_storage_config(self) -> DataStorageConfig:
        """Get storage configuration"""
        return self.config.storage

    def update_config(self, updates: dict[str, Any]) -> bool:
        """Update configuration with new values"""
        try:
            for key, value in updates.items():
                if hasattr(self.config, key):
                    if isinstance(value, dict):
                        # Handle nested updates
                        nested_config = getattr(self.config, key)
                        for nested_key, nested_value in value.items():
                            if hasattr(nested_config, nested_key):
                                setattr(nested_config, nested_key, nested_value)
                    else:
                        setattr(self.config, key, value)

            self.save_config()
            logger.info("Configuration updated successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to update config: {e}")
            return False

    def validate_config(self) -> tuple[bool, list[str]]:
        """Validate configuration"""
        errors = []

        # Validate voice config
        voice = self.config.voice_model
        if voice.enabled and not voice.models:
            errors.append("Voice models list is empty but voice is enabled")

        # Validate visual config
        visual = self.config.visual_model
        if visual.enabled and not visual.models:
            errors.append("Visual models list is empty but visual is enabled")

        # Validate camera config
        camera = self.config.camera
        if camera.enabled:
            if len(camera.resolution) != 2:
                errors.append("Camera resolution must be [width, height]")
            if camera.fps <= 0:
                errors.append("Camera FPS must be positive")

        # Validate conversation config
        conv = self.config.conversation
        if conv.context_window <= 0:
            errors.append("Context window must be positive")

        # Validate policy config
        policy = self.config.policy
        for attr in [
            "default_response_length",
            "default_formality",
            "default_empathy",
            "default_sensitivity",
            "default_humor",
        ]:
            value = getattr(policy, attr)
            if not 0.0 <= value <= 1.0:
                errors.append(f"Policy {attr} must be between 0 and 1")

        # Validate fusion config
        fusion = self.config.fusion
        if fusion.strategy not in ["early_fusion", "late_fusion", "hybrid_fusion"]:
            errors.append(f"Invalid fusion strategy: {fusion.strategy}")

        is_valid = len(errors) == 0

        if is_valid:
            logger.info("Configuration validation passed")
        else:
            logger.error(f"Configuration validation failed: {errors}")

        return is_valid, errors

    def export_config_template(self, output_file: str) -> bool:
        """Export configuration template"""
        try:
            template = GodTierConfig()  # Default config
            template_dict = asdict(template)

            with open(output_file, "w") as f:
                yaml.dump(template_dict, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Configuration template exported to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to export template: {e}")
            return False


# Global configuration manager
_default_config_manager: ConfigurationManager | None = None


def get_default_config_manager() -> ConfigurationManager:
    """Get or create default configuration manager"""
    global _default_config_manager
    if _default_config_manager is None:
        _default_config_manager = ConfigurationManager()
        _default_config_manager.load_config()
    return _default_config_manager


def load_god_tier_config() -> GodTierConfig:
    """Load God Tier configuration"""
    manager = get_default_config_manager()
    return manager.load_config()


def save_god_tier_config(config: GodTierConfig) -> bool:
    """Save God Tier configuration"""
    manager = get_default_config_manager()
    manager.config = config
    return manager.save_config()
