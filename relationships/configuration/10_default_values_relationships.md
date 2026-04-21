# Default Values System Relationships

**System:** Default Values  
**Core Files:**
- `src/app/core/config.py` [[src/app/core/config.py]] - `Config.DEFAULTS` dictionary
- `src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]] - Dataclass field defaults
- `src/app/temporal/config.py` [[src/app/temporal/config.py]] - Pydantic Field defaults
- `config/settings_manager.py` - Constructor defaults dictionary
- `config/settings.py` - `os.getenv()` inline defaults

**Last Updated:** 2025-04-20  
**Mission:** AGENT-065 Configuration Systems Relationship Mapping

---


## Navigation

**Location**: `relationships\configuration\10_default_values_relationships.md`

**Parent**: [[relationships\configuration\README.md]]


## Default Values Architecture

Project-AI uses **five distinct default value patterns**:

1. **Dictionary Defaults** (CLI Config) - Nested dict structure
2. **Dataclass Field Defaults** (God Tier) - Python dataclasses with `field()`
3. **Pydantic Field Defaults** (Temporal) - Pydantic `Field()` with constraints
4. **Inline Defaults** (API Config) - `os.getenv(key, default)`
5. **Constructor Defaults** (Settings Manager) - Nested dict in `__init__`

---

## Pattern 1: Dictionary Defaults (CLI Config)

### File: `src/app/core/config.py` [[src/app/core/config.py]]

```python
class Config:
    # Default configuration values (nested dictionary)
    DEFAULTS = {
        "general": {
            "log_level": "INFO",
            "data_dir": "data",
            "verbose": False,
        },
        "ai": {
            "model": "gpt-3.5-turbo",
            "provider": "openai",  # Options: 'openai', 'perplexity'
            "temperature": 0.7,
            "max_tokens": 256,
        },
        "security": {
            "enable_four_laws": True,
            "enable_black_vault": True,
            "enable_audit_log": True,
        },
        "api": {
            "timeout": 30,
            "retry_attempts": 3,
        },
        "health": {
            "collect_system_metrics": True,
            "collect_dependencies": True,
            "collect_config_summary": True,
            "snapshot_dir": "data/health_snapshots",
            "report_dir": "docs/assets",
        },
    }
```

### Characteristics

| Aspect | Implementation |
|--------|---------------|
| **Type Safety** | ❌ No (plain dict) |
| **Documentation** | ❌ No inline docs |
| **Validation** | ❌ No type checking |
| **Modification** | ✅ Mutable at runtime |
| **IDE Support** | ❌ No autocomplete |

### Usage Pattern

```python
def __init__(self, config_path: Path | None = None):
    # Start with defaults (deep copy)
    self.config = self.DEFAULTS.copy()
    
    # Then apply overrides via merging
    self._load_config(config_path)
```

---

## Pattern 2: Dataclass Field Defaults (God Tier Config)

### File: `src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]]

```python
from dataclasses import dataclass, field

@dataclass
class VoiceModelConfig:
    """Voice model configuration with dataclass defaults."""
    enabled: bool = True  # ← Simple default
    models: list[str] = field(
        default_factory=lambda: ["basic_tts", "emotional_tts", "conversational"]
    )  # ← Factory for mutable defaults
    default_model: str = "conversational"
    bonding_enabled: bool = True
    experimentation_rounds: int = 5
    auto_select: bool = True

@dataclass
class CameraConfig:
    """Camera configuration with dataclass defaults."""
    enabled: bool = True
    auto_discover: bool = True
    preferred_device: str | None = None  # ← Optional field (defaults to None)
    resolution: list[int] = field(default_factory=lambda: [1280, 720])
    fps: int = 30

@dataclass
class PolicyConfig:
    """Policy manager configuration with ranged defaults."""
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

@dataclass
class GodTierConfig:
    """Master configuration with nested dataclass defaults."""
    version: str = "1.0.0"
    deployment_mode: str = "production"  # production|development|testing
    
    # Nested defaults via default_factory
    voice_model: VoiceModelConfig = field(default_factory=VoiceModelConfig)
    visual_model: VisualModelConfig = field(default_factory=VisualModelConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    conversation: ConversationConfig = field(default_factory=ConversationConfig)
    policy: PolicyConfig = field(default_factory=PolicyConfig)
    fusion: FusionConfig = field(default_factory=FusionConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    storage: DataStorageConfig = field(default_factory=DataStorageConfig)
    
    # System-wide defaults
    system_name: str = "God Tier Project-AI"
    enable_all_features: bool = True
    fail_safe_mode: bool = True
    auto_recovery: bool = True
```

### Characteristics

| Aspect | Implementation |
|--------|---------------|
| **Type Safety** | ✅ Yes (type hints) |
| **Documentation** | ✅ Docstrings + type hints |
| **Validation** | ⚠️ Manual (validate_config()) |
| **Modification** | ✅ Mutable attributes |
| **IDE Support** | ✅ Full autocomplete |

### Why `field(default_factory=...)` for Mutable Defaults?

```python
# ❌ WRONG: Shared mutable default (dangerous!)
models: list[str] = ["basic_tts"]  # All instances share same list!

# ✅ CORRECT: Factory creates new instance per object
models: list[str] = field(default_factory=lambda: ["basic_tts"])
```

**Pattern:** Always use `default_factory` for lists, dicts, sets.

---

## Pattern 3: Pydantic Field Defaults (Temporal Config)

### File: `src/app/temporal/config.py` [[src/app/temporal/config.py]]

```python
from pydantic import Field
from pydantic_settings import BaseSettings

class TemporalConfig(BaseSettings):
    """Temporal configuration with Pydantic Field defaults."""
    
    # String with description
    host: str = Field(
        default="localhost:7233",
        description="Temporal server address"
    )
    namespace: str = Field(
        default="default",
        description="Temporal namespace"
    )
    task_queue: str = Field(
        default="project-ai-tasks",
        description="Task queue name for workers"
    )
    
    # Optional fields (default None)
    cloud_namespace: str | None = Field(
        default=None,
        description="Temporal Cloud namespace (e.g., my-namespace.a2b3c)"
    )
    cloud_cert_path: Path | None = Field(
        default=None,
        description="Path to client certificate for Temporal Cloud"
    )
    
    # Integer with constraints
    max_concurrent_activities: int = Field(
        default=50,
        description="Maximum number of concurrent activity executions"
    )
    max_concurrent_workflows: int = Field(
        default=50,
        description="Maximum number of concurrent workflow tasks"
    )
    
    # Timeouts (in seconds)
    workflow_execution_timeout: int = Field(
        default=3600,  # 1 hour
        description="Maximum time for entire workflow execution"
    )
    activity_start_to_close_timeout: int = Field(
        default=300,  # 5 minutes
        description="Maximum time for activity execution"
    )
    
    # Retry policy
    max_retry_attempts: int = Field(
        default=3,
        description="Maximum number of retry attempts"
    )
    initial_retry_interval: int = Field(
        default=1,
        description="Initial retry interval in seconds"
    )
    max_retry_interval: int = Field(
        default=30,
        description="Maximum retry interval in seconds"
    )
```

### Characteristics

| Aspect | Implementation |
|--------|---------------|
| **Type Safety** | ✅ Yes (Pydantic validation) |
| **Documentation** | ✅ Field descriptions |
| **Validation** | ✅ Automatic (type + constraints) |
| **Modification** | ✅ Mutable (but validated) |
| **IDE Support** | ✅ Full autocomplete |
| **Environment Integration** | ✅ Auto-loads from env vars |

### Advanced: Pydantic Field Constraints

```python
from pydantic import Field

# Integer with minimum
age: int = Field(default=18, ge=18)  # Must be ≥ 18

# Integer with range
port: int = Field(default=8000, ge=1, le=65535)  # [1, 65535]

# String with pattern
email: str = Field(default="", pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

# List with length constraints
items: list[str] = Field(default_factory=list, min_items=1, max_items=10)
```

---

## Pattern 4: Inline Defaults (API Config)

### File: `config/settings.py`

```python
import os
from pathlib import Path

class Config:
    """Configuration with inline os.getenv() defaults."""
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8001"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    
    # TARL Configuration
    TARL_VERSION: str = os.getenv("TARL_VERSION", "1.0")
    TARL_SIGNATURE_ALGORITHM: str = os.getenv("TARL_SIGNATURE_ALGORITHM", "SHA256")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "audit.log")
    
    # Security
    ENABLE_CORS: bool = os.getenv("ENABLE_CORS", "true").lower() == "true"
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:8000"
    ).split(",")
    
    # Paths (computed defaults)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
```

### Characteristics

| Aspect | Implementation |
|--------|---------------|
| **Type Safety** | ⚠️ Manual type casting |
| **Documentation** | ❌ No inline docs |
| **Validation** | ❌ No validation |
| **Modification** | ❌ Immutable (class attributes) |
| **IDE Support** | ✅ Class attribute autocomplete |
| **Environment Integration** | ✅ Direct via os.getenv() |

---

## Pattern 5: Constructor Defaults (Settings Manager)

### File: `config/settings_manager.py`

```python
class SettingsManager:
    def __init__(self, god_tier_encryption):
        # Comprehensive default settings (632 lines of nested dicts!)
        self.settings = {
            # General Settings
            "general": {
                "language": "en",
                "theme": "dark",
                "auto_start": False,
                "minimize_to_tray": True,
                "check_updates": False,
                "notifications": True,
            },
            
            # Privacy Settings (God Tier)
            "privacy": {
                "god_tier_encryption": True,
                "encryption_layers": 7,
                "quantum_resistant": True,
                "data_minimization": True,
                "on_device_only": True,
                "no_telemetry": True,
                "no_logging": True,
                "forensic_resistance": True,
                "perfect_forward_secrecy": True,
                "ephemeral_storage": True,
            },
            
            # Security Settings
            "security": {
                "kill_switch": True,
                "kill_switch_mode": "aggressive",
                "vpn_multi_hop": True,
                "vpn_required": True,
                "dns_leak_protection": True,
                "ipv6_leak_protection": True,
                "webrtc_leak_protection": True,
                "firewall_count": 8,
                "firewall_mode": "maximum",
                "auto_security_audit": True,
                "malware_scanning": True,
                "phishing_protection": True,
            },
            
            # 12+ more categories...
        }
        
        # Preserve defaults for reset functionality
        self._defaults = self.settings.copy()
```

### Characteristics

| Aspect | Implementation |
|--------|---------------|
| **Type Safety** | ❌ No (plain dict) |
| **Documentation** | ⚠️ Comments only |
| **Validation** | ⚠️ Manual (validate_settings()) |
| **Modification** | ✅ Mutable |
| **IDE Support** | ❌ No autocomplete |
| **Reset Capability** | ✅ Via `_defaults` backup |

---

## Default Value Categories

### Security Defaults (Conservative)

> **Security Policy**: Defaults follow [[../security/01_security_system_overview.md|Security Overview]] fail-safe principles

```python
# CLI Config → [[../security/03_defense_layers.md|Defense Layers]]
"security": {
    "enable_four_laws": True,       # ← Asimov's Laws ON by default
    "enable_black_vault": True,     # ← Content blacklist ON
    "enable_audit_log": True,       # ← Logging ON → [[../monitoring/01-logging-system.md|Logging System]]
}

# Settings Manager → [[../security/07_security_metrics.md|Security Metrics]]
"security": {
    "kill_switch": True,            # ← Emergency shutdown ENABLED
    "vpn_required": True,           # ← VPN enforcement ON
    "auto_security_audit": True,    # ← Auto-audits ENABLED
}
```

**Pattern:** Security features default to **ENABLED** (fail-safe).

### Privacy Defaults (Maximal)

> **Privacy Framework**: Defaults enforce [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]] and data minimization

```python
"privacy": {
    "god_tier_encryption": True,    # ← Encryption ON → [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]]
    "on_device_only": True,         # ← Cloud sync OFF
    "no_telemetry": True,           # ← Telemetry OFF → [[../monitoring/08-metrics-collection.md|Metrics Collection]]
    "no_logging": True,             # ← Logging OFF → [[../monitoring/01-logging-system.md|Logging System]]
    "ephemeral_storage": True,      # ← Temp data only → [[../data/00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure]]
}
```

**Pattern:** Privacy defaults to **MAXIMUM** protection.

### AI Model Defaults (Balanced)

```python
"ai": {
    "model": "gpt-3.5-turbo",       # ← Not newest (cost-effective)
    "provider": "openai",           # ← Most reliable provider
    "temperature": 0.7,             # ← Balanced creativity
    "max_tokens": 256,              # ← Conservative output length
}
```

**Pattern:** AI defaults to **cost-effective** and **reliable** options.

### Performance Defaults (Moderate)

```python
# Temporal Config
max_concurrent_activities: int = 50    # Not too high (resource control)
max_concurrent_workflows: int = 50
workflow_execution_timeout: int = 3600  # 1 hour (generous)
max_retry_attempts: int = 3             # Reasonable retries
```

**Pattern:** Performance defaults to **moderate** resource usage.

---

## Default Value Documentation

### God Tier Config (Best Practice)

```python
@dataclass
class PolicyConfig:
    """Policy manager configuration.
    
    Attributes:
        enabled: Enable policy management system
        auto_adjust: Automatically adjust policies based on context
        adjustment_rate: Rate of automatic adjustment (0.0-1.0)
        default_response_length: Default response length policy (0.0=short, 1.0=long)
        default_formality: Default formality level (0.0=casual, 1.0=formal)
        default_empathy: Default empathy level (0.0=neutral, 1.0=empathetic)
        default_sensitivity: Content sensitivity threshold (0.0=relaxed, 1.0=strict)
        default_humor: Humor usage level (0.0=serious, 1.0=humorous)
    """
    enabled: bool = True
    auto_adjust: bool = True
    adjustment_rate: float = 0.05
    default_response_length: float = 0.5
    default_formality: float = 0.5
    default_empathy: float = 0.7
    default_sensitivity: float = 0.8
    default_humor: float = 0.3
```

**Best Practice:** Docstring + type hints + inline comments for scale explanations.

### Pydantic Config (Excellent)

```python
max_concurrent_activities: int = Field(
    default=50,
    description="Maximum number of concurrent activity executions"
)
```

**Best Practice:** Field descriptions as first-class documentation.

---

## Default Value Validation

### Pydantic (Automatic)

```python
# Valid instantiation
config = TemporalConfig()  # ← Uses all defaults
config = TemporalConfig(max_concurrent_activities=100)  # ← Override one default

# Invalid type triggers error
config = TemporalConfig(max_concurrent_activities="invalid")
# → pydantic.ValidationError: value is not a valid integer
```

### God Tier (Manual)

```python
def validate_config(self) -> tuple[bool, list[str]]:
    """Validate defaults + user values."""
    errors = []
    
    # Validate default ranges still hold after merging
    policy = self.config.policy
    for attr in ["default_empathy", "default_sensitivity", "default_humor"]:
        value = getattr(policy, attr)
        if not 0.0 <= value <= 1.0:
            errors.append(f"Policy {attr} must be between 0 and 1")
    
    return len(errors) == 0, errors
```

### CLI Config (None)

```python
# No validation of defaults
# Assumed correct by design
```

---

## Resetting to Defaults

### Settings Manager (Explicit Reset)

```python
def reset_category(self, category: str):
    """Reset a category to defaults."""
    if category in self._defaults:
        self.settings[category] = self._defaults[category].copy()
        self._modified = True
        self.logger.info("Category reset to defaults: %s", category)

def reset_all(self):
    """Reset ALL settings to defaults."""
    self.settings = self._defaults.copy()
    self._modified = True
    self.logger.warning("ALL SETTINGS RESET TO DEFAULTS")
```

### CLI Config (Reload Defaults)

```python
# No explicit reset method
# Workaround: Delete config files and restart
# Defaults are reloaded from DEFAULTS dict
```

### God Tier (Manual Reset)

```python
# No built-in reset
# Workaround: Delete YAML file
# Defaults from dataclass field values
```

---

## Default Value Sources

| System | Source Type | Location | Reset Capability |
|--------|------------|----------|-----------------|
| **CLI Config** | Hardcoded dict | `Config.DEFAULTS` | ❌ No method |
| **God Tier** | Dataclass fields | Field definitions | ⚠️ Manual (delete YAML) |
| **Temporal** | Pydantic fields | Field defaults | ✅ Reinstantiate |
| **API Config** | os.getenv() args | Inline strings | ❌ Not applicable |
| **Settings Manager** | Constructor dict | `self._defaults` backup | ✅ `reset_all()` |

---

## Relationship Matrix

| Default System | Loader System | Override System | Validator System |
|---------------|--------------|-----------------|-----------------|
| **CLI DEFAULTS** | CLI Config | Environment vars | None |
| **God Tier Field Defaults** | God Tier Config | YAML values | Manual validation |
| **Pydantic Field Defaults** | Temporal Config | Environment vars | Automatic (Pydantic) |
| **os.getenv() Defaults** | API Config | Environment vars | Type casting only |
| **Settings Manager Defaults** | Settings Manager | `set_setting()` | Security validation |

---

## Related Systems

### Configuration Systems
- [Config Loader](./01_config_loader_relationships.md)
- [Override Hierarchy](./09_override_hierarchy_relationships.md)
- [Settings Validator](./03_settings_validator_relationships.md)
- [Configuration Schema](./05_configuration_schema_relationships.md)
- [Config Inheritance](./08_config_inheritance_relationships.md)

### Cross-System Dependencies
- [[../security/01_security_system_overview.md|Security System Overview]] - Security defaults enforcement
- [[../security/03_defense_layers.md|Defense Layers]] - Defense-in-depth default configuration
- [[../security/07_security_metrics.md|Security Metrics]] - Default audit policies
- [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]] - Encryption defaults
- [[../data/00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure]] - Data directory defaults
- [[../monitoring/01-logging-system.md|Logging System]] - Log level defaults
- [[../monitoring/08-metrics-collection.md|Metrics Collection]] - Telemetry defaults
