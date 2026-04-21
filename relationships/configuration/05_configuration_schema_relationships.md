# Configuration Schema System Relationships

**System:** Configuration Schema  
**Core Files:**
- `config/schemas/defense_engine.schema.json` - JSON Schema for Defense Engine
- `src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]] - Dataclass-based schema (Python type hints)
- `src/app/temporal/config.py` [[src/app/temporal/config.py]] - Pydantic schema with Field constraints
- `config/inspection_config.yaml` - YAML schema via comments

**Last Updated:** 2025-04-20  
**Mission:** AGENT-065 Configuration Systems Relationship Mapping

---


## Navigation

**Location**: `relationships\configuration\05_configuration_schema_relationships.md`

**Parent**: [[relationships\configuration\README.md]]


## Schema Definition Approaches

Project-AI uses **three distinct schema definition methods**:

### 1. JSON Schema (Declarative, External)

**File:** `config/schemas/defense_engine.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Defense Engine Configuration Schema",
  "type": "object",
  "required": ["version", "bootstrap", "subsystems"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "operational_mode": {
      "type": "string",
      "enum": ["normal", "degraded", "air_gapped", "adversarial", "recovery", "maintenance", "emergency"]
    },
    "bootstrap": {
      "type": "object",
      "required": ["auto_discover", "failure_mode"],
      "properties": {
        "health_check_interval": {
          "type": "number",
          "minimum": 1,
          "maximum": 300
        }
      }
    }
  }
}
```

**Advantages:**
- Language-agnostic
- Rich validation (patterns, enums, ranges)
- Tooling support (validators, generators)

**Disadvantages:**
- Not enforced in codebase (no validation code found)
- Separate from implementation (drift risk)

---

### 2. Dataclass Schema (Python Type Hints)

**File:** `src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]]

```python
from dataclasses import dataclass, field

@dataclass
class VoiceModelConfig:
    """Voice model configuration schema."""
    enabled: bool = True
    models: list[str] = field(default_factory=lambda: ["basic_tts", "emotional_tts"])
    default_model: str = "conversational"
    bonding_enabled: bool = True
    experimentation_rounds: int = 5
    auto_select: bool = True

@dataclass
class CameraConfig:
    """Camera configuration schema."""
    enabled: bool = True
    auto_discover: bool = True
    preferred_device: str | None = None
    resolution: list[int] = field(default_factory=lambda: [1280, 720])
    fps: int = 30

@dataclass
class GodTierConfig:
    """Master configuration schema."""
    version: str = "1.0.0"
    deployment_mode: str = "production"  # production|development|testing
    
    voice_model: VoiceModelConfig = field(default_factory=VoiceModelConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    # ... 8 total nested configs
```

**Schema Features:**
- Type hints enforce structure
- Default values via `field(default_factory=...)`
- Nested composition via dataclasses
- IDE autocomplete support

**Validation:**
```python
# Manual validation in validate_config()
if camera.enabled:
    if len(camera.resolution) != 2:
        errors.append("Camera resolution must be [width, height]")
    if camera.fps <= 0:
        errors.append("Camera FPS must be positive")
```

---

### 3. Pydantic Schema (Python + Validation)

**File:** `src/app/temporal/config.py` [[src/app/temporal/config.py]]

```python
from pydantic import Field
from pydantic_settings import BaseSettings

class TemporalConfig(BaseSettings):
    """Temporal configuration schema with automatic validation."""
    
    # String field with default
    host: str = Field(
        default="localhost:7233",
        description="Temporal server address"
    )
    
    # Integer field (implicit ≥ 0)
    max_concurrent_activities: int = Field(
        default=50,
        description="Maximum concurrent activity executions"
    )
    
    # Integer with timeout (implicit validation)
    workflow_execution_timeout: int = Field(
        default=3600,
        description="Maximum time for entire workflow execution"
    )
    
    # Optional string
    cloud_namespace: str | None = Field(
        default=None,
        description="Temporal Cloud namespace"
    )
    
    class Config:
        env_prefix = "TEMPORAL_"          # Auto-load from env
        env_file = ".env.temporal"        # Additional env file
        case_sensitive = False
```

**Schema Features:**
- Automatic type validation
- Environment variable integration
- Optional fields via `str | None`
- Descriptions for documentation
- Constraint validation (min/max via ge/le)

---

## Schema Composition Patterns

### Nested Dataclass Schema (God Tier)

```
GodTierConfig (Root)
├── voice_model: VoiceModelConfig
│   ├── enabled: bool
│   ├── models: list[str]
│   └── default_model: str
├── visual_model: VisualModelConfig
│   ├── enabled: bool
│   └── models: list[str]
├── camera: CameraConfig
│   ├── enabled: bool
│   ├── resolution: list[int]
│   └── fps: int
├── conversation: ConversationConfig
│   ├── enabled: bool
│   └── context_window: int
├── policy: PolicyConfig
│   ├── enabled: bool
│   ├── default_empathy: float (0.0-1.0)
│   └── default_humor: float (0.0-1.0)
├── fusion: FusionConfig
│   ├── enabled: bool
│   ├── strategy: str (enum)
│   └── confidence_threshold: float
├── logging: LoggingConfig
│   ├── enabled: bool
│   ├── level: str
│   └── file_path: str
└── storage: DataStorageConfig
    ├── base_dir: str
    ├── auto_save: bool
    └── backup_enabled: bool
```

**8 nested schemas**, each defining a subsystem.

---

### Flat Schema with Sections (CLI Config)

```python
# src/app/core/config.py
DEFAULTS = {
    "general": {
        "log_level": "INFO",
        "data_dir": "data",
        "verbose": False
    },
    "ai": {
        "model": "gpt-3.5-turbo",
        "provider": "openai",
        "temperature": 0.7,
        "max_tokens": 256
    },
    "security": {
        "enable_four_laws": True,
        "enable_black_vault": True,
        "enable_audit_log": True
    }
}
```

**No explicit schema** - just dictionary structure with defaults.

---

## Schema Evolution & Versioning

### God Tier Config Versioning

```python
@dataclass
class GodTierConfig:
    version: str = "1.0.0"  # Schema version
    
    # Migration pattern (not implemented):
    # if loaded_version < current_version:
    #     migrate_config(config_dict)
```

### Defense Engine Schema Versioning

```json
{
  "version": {
    "type": "string",
    "pattern": "^\\d+\\.\\d+\\.\\d+$",
    "description": "Configuration schema version"
  },
  "schema_version": "1.0"
}
```

### Temporal Config (No Versioning)

```python
# No version field - Pydantic handles schema evolution via:
# - Optional fields (backward compatible)
# - Default values (forward compatible)
```

---

## Schema Validation Integration

### Defense Engine (JSON Schema)

```python
# Expected usage (NOT IMPLEMENTED):
import jsonschema

with open("config/schemas/defense_engine.schema.json") as f:
    schema = json.load(f)

with open("config/defense_engine.toml") as f:
    config = toml.load(f)

jsonschema.validate(instance=config, schema=schema)
```

**Status:** ❌ Schema exists but no validation code in codebase.

### God Tier (Manual Validation)

```python
def validate_config(self) -> tuple[bool, list[str]]:
    """Validate against dataclass schema + business rules."""
    errors = []
    
    # Type validation (implicit via dataclass)
    # Range validation (manual)
    if self.config.camera.fps <= 0:
        errors.append("FPS must be positive")
    
    # Enum validation (manual)
    if self.config.fusion.strategy not in ["early_fusion", "late_fusion", "hybrid_fusion"]:
        errors.append(f"Invalid strategy: {self.config.fusion.strategy}")
    
    return len(errors) == 0, errors
```

**Status:** ✅ Partial validation (manual checks required).

### Temporal (Automatic via Pydantic)

```python
# Validation happens on instantiation
config = TemporalConfig()  # ← Pydantic validates types automatically

# Invalid type raises error
config = TemporalConfig(max_concurrent_activities="invalid")
# → pydantic.ValidationError
```

**Status:** ✅ Full automatic validation.

---

## Schema Documentation

### JSON Schema (Self-Documenting)

```json
{
  "properties": {
    "health_check_interval": {
      "type": "number",
      "minimum": 1,
      "maximum": 300,
      "description": "Health check interval in seconds"
    }
  }
}
```

**Generates documentation** from schema definitions.

### Dataclass (Docstring + Type Hints)

```python
@dataclass
class VoiceModelConfig:
    """Voice model configuration.
    
    Attributes:
        enabled: Enable/disable voice model system
        models: List of available voice models
        default_model: Model to use by default
    """
    enabled: bool = True
    models: list[str] = field(default_factory=lambda: ["basic_tts"])
    default_model: str = "conversational"
```

### Pydantic (Field Descriptions)

```python
host: str = Field(
    default="localhost:7233",
    description="Temporal server address"  # ← Extracted for docs
)
```

---

## Schema Enforcement Levels

| Config System | Schema Type | Enforcement | Validation Trigger |
|--------------|-------------|-------------|-------------------|
| **CLI Config** | Dict structure | None | N/A |
| **API Config** | Class attributes | Type casting only | On `os.getenv()` call |
| **Temporal Config** | Pydantic | Automatic | On object creation |
| **God Tier Config** | Dataclass | Manual | On `validate_config()` call |
| **Defense Engine** | JSON Schema | None (unimplemented) | N/A |
| **Settings Manager** | Dict structure | Security checks only | On `validate_settings()` call |

---

## Schema Serialization

### Dataclass → YAML (God Tier)

```python
from dataclasses import asdict
import yaml

config_dict = asdict(self.config)  # Dataclass → dict
with open(self.config_file, "w") as f:
    yaml.dump(config_dict, f, default_flow_style=False)
```

### YAML → Dataclass (God Tier)

```python
with open(self.config_file) as f:
    config_dict = yaml.safe_load(f)  # YAML → dict

# Manual dict → dataclass conversion
config = GodTierConfig()
for key, value in config_dict.items():
    if hasattr(config, key) and isinstance(value, dict):
        nested_config = getattr(config, key)
        for nested_key, nested_value in value.items():
            setattr(nested_config, nested_key, nested_value)
```

### Pydantic → Dict

```python
config = TemporalConfig()
config_dict = config.model_dump()  # Pydantic v2
# or config.dict() in Pydantic v1
```

---

## Schema vs. Settings Manager

### Settings Manager (No Schema)

```python
# Arbitrary structure - no schema enforcement
settings = {
    "privacy": {
        "god_tier_encryption": True,
        "new_field_added_at_runtime": "value"  # ← No validation
    }
}
```

**Risk:** Runtime additions can break assumptions.

### God Tier (Schema-Enforced)

```python
@dataclass
class GodTierConfig:
    voice_model: VoiceModelConfig  # ← Only defined fields allowed
    
# Typo causes AttributeError (good!)
config.voice_modell.enabled = True  # ← Error: no attribute 'voice_modell'
```

---

## Relationship Matrix

| Schema System | Loader System | Validator System | Serialization Format |
|--------------|--------------|------------------|---------------------|
| **JSON Schema** | Defense Engine (N/A) | None (unimplemented) | JSON/TOML |
| **Dataclass** | God Tier Config | Manual `validate_config()` | YAML |
| **Pydantic** | Temporal Config | Automatic | Environment/dict |
| **Dict Structure** | CLI Config | None | TOML |
| **Dict Structure** | Settings Manager | Security validation | In-memory |

---

## Gaps & Recommendations

### ❌ Current Gaps

1. **No enforcement** for CLI Config schema
2. **JSON Schema unused** despite existence
3. **Manual validation** required for God Tier
4. **No migration system** for schema versioning
5. **Settings Manager has no schema** (arbitrary dict)

### ✅ Recommended Improvements

```python
# 1. Add Pydantic schema for CLI Config
class CLIConfigSchema(BaseSettings):
    class GeneralSection(BaseModel):
        log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        data_dir: Path
        verbose: bool
    
    general: GeneralSection
    ai: AISection
    security: SecuritySection

# 2. Implement JSON Schema validation for Defense Engine
def load_defense_config(config_file: str) -> dict:
    with open(config_file) as f:
        config = toml.load(f)
    
    with open("config/schemas/defense_engine.schema.json") as f:
        schema = json.load(f)
    
    jsonschema.validate(instance=config, schema=schema)  # ← Enforce
    return config

# 3. Automatic validation for God Tier
@dataclass
class GodTierConfig:
    def __post_init__(self):
        """Auto-validate on creation."""
        is_valid, errors = self.validate()
        if not is_valid:
            raise ValueError(f"Invalid config: {errors}")
```

---

## Related Systems

### Configuration Systems
- [Settings Validator](./03_settings_validator_relationships.md)
- [Config Loader](./01_config_loader_relationships.md)
- [Default Values](./10_default_values_relationships.md)
- [Config Inheritance](./08_config_inheritance_relationships.md)

### Cross-System Dependencies
- [[../security/01_security_system_overview.md|Security System Overview]] - Schema-enforced security policies
- [[../data/01-PERSISTENCE-PATTERNS.md|Persistence Patterns]] - Schema serialization patterns
- [[../data/00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure]] - Schema-based data validation
- [[../monitoring/01-logging-system.md|Logging System]] - Schema validation logging
