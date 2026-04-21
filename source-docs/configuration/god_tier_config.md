# God-Tier Configuration System

**Module**: `src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]]  
**Purpose**: YAML-based configuration for multi-modal AI system (voice, visual, camera, conversation)  
**Classification**: Advanced AI Configuration  
**Priority**: P0 - Core System

---

## Overview

The God-Tier Configuration System provides comprehensive YAML-based configuration for the multi-modal AI system including voice models, visual models, camera settings, conversation engine, policy management, fusion strategies, logging, and data storage. It supports runtime configuration updates, validation, and template export.

### Key Characteristics

- **Format**: YAML configuration files
- **Components**: 8 major configuration dataclasses
- **Validation**: Built-in configuration validation
- **Persistence**: YAML file-based with auto-save
- **Deployment Modes**: production, development, testing
- **Fail-Safe**: Auto-recovery and fail-safe modes

---

## Architecture

### Configuration Hierarchy

```
GodTierConfig (Master)
├── VoiceModelConfig
├── VisualModelConfig
├── CameraConfig
├── ConversationConfig
├── PolicyConfig
├── FusionConfig
├── LoggingConfig
└── DataStorageConfig
```

### Class Structure

```python
@dataclass
class GodTierConfig:
    """Master configuration for God Tier system"""
    version: str = "1.0.0"
    deployment_mode: str = "production"
    
    voice_model: VoiceModelConfig
    visual_model: VisualModelConfig
    camera: CameraConfig
    conversation: ConversationConfig
    policy: PolicyConfig
    fusion: FusionConfig
    logging: LoggingConfig
    storage: DataStorageConfig
    
    system_name: str = "God Tier Project-AI"
    enable_all_features: bool = True
    fail_safe_mode: bool = True
    auto_recovery: bool = True
```

---

## Configuration Components

### 1. Voice Model Configuration

```python
@dataclass
class VoiceModelConfig:
    """Voice model configuration"""
    enabled: bool = True
    models: list[str] = ["basic_tts", "emotional_tts", "conversational"]
    default_model: str = "conversational"
    bonding_enabled: bool = True
    experimentation_rounds: int = 5
    auto_select: bool = True
```

**Purpose**: Configure text-to-speech and voice synthesis

**Key Settings**:
- `models`: Available voice models
- `default_model`: Model used by default
- `bonding_enabled`: Enable voice bonding experiments
- `experimentation_rounds`: Number of rounds for model selection
- `auto_select`: Automatically select best model

### 2. Visual Model Configuration

```python
@dataclass
class VisualModelConfig:
    """Visual model configuration"""
    enabled: bool = True
    models: list[str] = ["facial_emotion", "focus_attention"]
    default_model: str = "facial_emotion"
    bonding_enabled: bool = True
    calibration_frames: int = 30
    detection_fps: int = 10
```

**Purpose**: Configure computer vision and facial recognition

**Key Settings**:
- `models`: Available visual models
- `calibration_frames`: Frames for calibration
- `detection_fps`: Detection frame rate
- `bonding_enabled`: Enable visual bonding

### 3. Camera Configuration

```python
@dataclass
class CameraConfig:
    """Camera configuration"""
    enabled: bool = True
    auto_discover: bool = True
    preferred_device: str | None = None
    resolution: list[int] = [1280, 720]
    fps: int = 30
```

**Purpose**: Configure camera hardware settings

**Key Settings**:
- `auto_discover`: Auto-detect cameras
- `preferred_device`: Specific camera device
- `resolution`: [width, height] in pixels
- `fps`: Frame rate

### 4. Conversation Configuration

```python
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
```

**Purpose**: Configure conversation context and NLP

**Key Settings**:
- `context_window`: Recent turns to consider
- `max_history_turns`: Maximum conversation history
- `intent_detection`: Enable intent classification
- `entity_extraction`: Extract entities from text
- `topic_tracking`: Track conversation topics
- `session_timeout_minutes`: Session timeout

### 5. Policy Configuration

```python
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
    no_false_alarms: bool = True
    user_adaptation: bool = True
```

**Purpose**: Configure AI response policy and personality

**Key Settings**:
- `auto_adjust`: Automatically adjust policies
- `adjustment_rate`: How quickly policies adapt (0-1)
- `default_*`: Default policy values on 0-1 scale
- `no_false_alarms`: Critical safety setting
- `user_adaptation`: Adapt to user preferences

**Policy Values**:
- 0.0 = Minimal
- 0.5 = Moderate
- 1.0 = Maximum

### 6. Fusion Configuration

```python
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
```

**Purpose**: Configure multi-modal data fusion

**Fusion Strategies**:
- `early_fusion`: Combine features before processing
- `late_fusion`: Process independently, combine results
- `hybrid_fusion`: Adaptive combination of both

**Key Settings**:
- `*_weight`: Relative importance of each modality (sum to 1.0)
- `confidence_threshold`: Minimum confidence for fusion
- `min_modalities`: Minimum modalities required
- `event_driven`: React to events vs polling

### 7. Logging Configuration

```python
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
```

**Purpose**: Configure logging behavior

**Key Settings**:
- `level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `console`: Log to console
- `file`: Log to file
- `max_bytes`: Max log file size before rotation
- `backup_count`: Number of backup log files
- `*_debug`: Enable debug logging for specific components

### 8. Data Storage Configuration

```python
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
```

**Purpose**: Configure data persistence and storage

**Key Settings**:
- `base_dir`: Base directory for all data
- `*_dir`: Subdirectories for each component
- `auto_save`: Enable automatic saving
- `save_interval_seconds`: Save frequency
- `backup_enabled`: Enable backups
- `backup_interval_hours`: Backup frequency

---

## Configuration Manager

### Class Structure

```python
class ConfigurationManager:
    """Configuration manager with YAML persistence."""
    
    def __init__(self, config_file: str = "config/god_tier_config.yaml"):
        self.config_file = config_file
        self.config: GodTierConfig = GodTierConfig()
```

### Core API

#### Loading Configuration

```python
def load_config(self) -> GodTierConfig:
    """Load configuration from YAML file.
    
    Returns:
        GodTierConfig instance
    
    Behavior:
        - Creates config directory if needed
        - Returns defaults if file doesn't exist
        - Saves defaults to file on first run
        - Logs errors and returns defaults on failure
    """
```

#### Saving Configuration

```python
def save_config(self) -> bool:
    """Save configuration to YAML file.
    
    Returns:
        True if successful, False otherwise
    
    Side Effects:
        - Creates config directory if needed
        - Overwrites existing file
        - Logs save operation
    """
```

#### Component Access

```python
def get_voice_config(self) -> VoiceModelConfig:
    """Get voice model configuration."""

def get_visual_config(self) -> VisualModelConfig:
    """Get visual model configuration."""

def get_camera_config(self) -> CameraConfig:
    """Get camera configuration."""

def get_conversation_config(self) -> ConversationConfig:
    """Get conversation configuration."""

def get_policy_config(self) -> PolicyConfig:
    """Get policy configuration."""

def get_fusion_config(self) -> FusionConfig:
    """Get fusion configuration."""

def get_logging_config(self) -> LoggingConfig:
    """Get logging configuration."""

def get_storage_config(self) -> DataStorageConfig:
    """Get storage configuration."""
```

#### Updating Configuration

```python
def update_config(self, updates: dict[str, Any]) -> bool:
    """Update configuration with new values.
    
    Args:
        updates: Dictionary of updates (nested supported)
    
    Returns:
        True if successful, False otherwise
    
    Example:
        >>> manager.update_config({
        ...     "voice_model": {"enabled": False},
        ...     "deployment_mode": "development"
        ... })
    """
```

#### Validation

```python
def validate_config(self) -> tuple[bool, list[str]]:
    """Validate configuration.
    
    Returns:
        (is_valid, list_of_errors)
    
    Validation Checks:
        - Voice models not empty if enabled
        - Visual models not empty if enabled
        - Camera resolution is [width, height]
        - Camera FPS is positive
        - Context window is positive
        - Policy values are in range [0.0, 1.0]
        - Fusion strategy is valid
    """
```

#### Template Export

```python
def export_config_template(self, output_file: str) -> bool:
    """Export configuration template.
    
    Args:
        output_file: Path to save template
    
    Returns:
        True if successful, False otherwise
    
    Use Case: Generate template for new deployments
    """
```

---

## Usage Patterns

### Pattern 1: Basic Initialization

```python
from src.app.core.god_tier_config import (
    ConfigurationManager,
    load_god_tier_config,
    save_god_tier_config
)

# Method 1: Using ConfigurationManager
manager = ConfigurationManager("config/god_tier_config.yaml")
config = manager.load_config()

# Method 2: Using convenience functions
config = load_god_tier_config()
```

### Pattern 2: Component Configuration

```python
# Get specific component config
voice_config = manager.get_voice_config()
camera_config = manager.get_camera_config()
policy_config = manager.get_policy_config()

# Use in component initialization
voice_model = VoiceModel(
    models=voice_config.models,
    default_model=voice_config.default_model
)
```

### Pattern 3: Runtime Updates

```python
# Update configuration at runtime
manager.update_config({
    "voice_model": {"enabled": True},
    "policy": {"default_empathy": 0.9}
})

# Validate after updates
is_valid, errors = manager.validate_config()
if not is_valid:
    logger.error("Invalid config: %s", errors)
```

### Pattern 4: Development vs Production

```python
# Development mode
config = GodTierConfig(deployment_mode="development")
config.logging.level = "DEBUG"
config.logging.voice_debug = True
config.logging.visual_debug = True

# Production mode
config = GodTierConfig(deployment_mode="production")
config.logging.level = "INFO"
config.fail_safe_mode = True
config.auto_recovery = True
```

### Pattern 5: Template Generation

```python
# Generate template for new deployment
manager = ConfigurationManager()
manager.export_config_template("config_template.yaml")

# Customize and use
# Edit config_template.yaml with your settings
new_manager = ConfigurationManager("config_template.yaml")
config = new_manager.load_config()
```

---

## Configuration File Example

### Complete YAML Configuration

```yaml
version: "1.0.0"
deployment_mode: production
system_name: God Tier Project-AI
enable_all_features: true
fail_safe_mode: true
auto_recovery: true

voice_model:
  enabled: true
  models:
    - basic_tts
    - emotional_tts
    - conversational
  default_model: conversational
  bonding_enabled: true
  experimentation_rounds: 5
  auto_select: true

visual_model:
  enabled: true
  models:
    - facial_emotion
    - focus_attention
  default_model: facial_emotion
  bonding_enabled: true
  calibration_frames: 30
  detection_fps: 10

camera:
  enabled: true
  auto_discover: true
  preferred_device: null
  resolution:
    - 1280
    - 720
  fps: 30

conversation:
  enabled: true
  context_window: 10
  max_history_turns: 1000
  intent_detection: true
  entity_extraction: true
  topic_tracking: true
  session_timeout_minutes: 30

policy:
  enabled: true
  auto_adjust: true
  adjustment_rate: 0.05
  default_response_length: 0.5
  default_formality: 0.5
  default_empathy: 0.7
  default_sensitivity: 0.8
  default_humor: 0.3
  no_false_alarms: true
  user_adaptation: true

fusion:
  enabled: true
  strategy: hybrid_fusion
  voice_weight: 0.4
  visual_weight: 0.4
  text_weight: 0.2
  confidence_threshold: 0.6
  min_modalities: 1
  event_driven: true

logging:
  enabled: true
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  console: true
  file: true
  file_path: data/logs/god_tier.log
  max_bytes: 10485760
  backup_count: 5
  voice_debug: false
  visual_debug: false
  fusion_debug: false

storage:
  base_dir: data
  voice_models_dir: voice_models
  visual_models_dir: visual_models
  camera_dir: camera
  engagement_profiles_dir: engagement_profiles
  conversation_context_dir: conversation_context
  policy_manager_dir: policy_manager
  fusion_dir: multimodal_fusion
  bonding_dir: bonding
  auto_save: true
  save_interval_seconds: 30
  backup_enabled: true
  backup_interval_hours: 24
```

---

## Validation Rules

### Voice Model Validation

- `enabled=True` requires non-empty `models` list
- `default_model` must be in `models` list

### Visual Model Validation

- `enabled=True` requires non-empty `models` list
- `default_model` must be in `models` list

### Camera Validation

- `resolution` must be [width, height] (length 2)
- `fps` must be positive integer

### Conversation Validation

- `context_window` must be positive
- `max_history_turns` must be positive

### Policy Validation

All policy values must be in range [0.0, 1.0]:
- `default_response_length`
- `default_formality`
- `default_empathy`
- `default_sensitivity`
- `default_humor`

### Fusion Validation

- `strategy` must be one of: `early_fusion`, `late_fusion`, `hybrid_fusion`
- `confidence_threshold` in range [0.0, 1.0]
- Weights should sum to 1.0 (not enforced, but recommended)

---

## Testing

### Unit Testing

```python
import pytest
from src.app.core.god_tier_config import (
    ConfigurationManager,
    GodTierConfig,
    VoiceModelConfig
)

def test_default_config():
    config = GodTierConfig()
    assert config.version == "1.0.0"
    assert config.deployment_mode == "production"
    assert config.fail_safe_mode is True

def test_voice_config():
    config = GodTierConfig()
    assert config.voice_model.enabled is True
    assert "conversational" in config.voice_model.models

def test_validate_valid_config():
    manager = ConfigurationManager()
    is_valid, errors = manager.validate_config()
    assert is_valid is True
    assert len(errors) == 0

def test_validate_invalid_policy():
    config = GodTierConfig()
    config.policy.default_empathy = 1.5  # Invalid: > 1.0
    
    manager = ConfigurationManager()
    manager.config = config
    is_valid, errors = manager.validate_config()
    
    assert is_valid is False
    assert any("empathy" in err for err in errors)
```

---

## Best Practices

1. **Validate After Load**: Always validate config after loading
2. **Use Defaults**: Start with default config and customize
3. **Component Access**: Use get_*_config() methods for type safety
4. **Save After Updates**: Call save_config() after runtime updates
5. **Template for Deployment**: Use export_config_template() for new environments
6. **Development Mode**: Use debug logging in development
7. **Fail-Safe Production**: Enable fail_safe_mode and auto_recovery in production
8. **Backup Config**: Enable backups for configuration persistence
9. **Policy Tuning**: Keep policy values in [0.0, 1.0] range
10. **Modality Weights**: Ensure fusion weights are balanced

---

## Related Modules

- **Settings Manager**: `config/settings_manager.py` - Comprehensive app settings
- **Core Config**: `src/app/core/config.py` [[src/app/core/config.py]] - CLI configuration
- **Optimization Config**: `src/app/core/memory_optimization/optimization_config.py` [[src/app/core/memory_optimization/optimization_config.py]] - Memory settings
- **Temporal Config**: `src/app/temporal/config.py` [[src/app/temporal/config.py]] - Workflow configuration

---

## Future Enhancements

1. **Schema Validation**: JSON schema for YAML validation
2. **Config Profiles**: Named profiles (dev, staging, prod)
3. **Hot Reload**: Reload config without restart
4. **Config Diff**: Compare configurations
5. **Config Inheritance**: Base configs with overrides
6. **Environment Overrides**: Environment variable support
7. **Config Versioning**: Migration between config versions
8. **Config Encryption**: Encrypt sensitive config sections
9. **Remote Config**: Load config from remote source
10. **Config Monitoring**: Monitor config changes in production


---

## Related Documentation

- **Relationship Map**: [[relationships\configuration\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/god_tier_config.py]]
