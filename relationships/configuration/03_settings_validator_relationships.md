# Settings Validator System Relationships

**System:** Settings Validator  
**Core Files:**
- `src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]] - `ConfigurationManager.validate_config()`
- `src/app/temporal/config.py` [[src/app/temporal/config.py]] - Pydantic Field validators
- `config/settings_manager.py` - `SettingsManager.validate_settings()`
- `config/schemas/defense_engine.schema.json` - JSON Schema validation

**Last Updated:** 2025-04-20  
**Mission:** AGENT-065 Configuration Systems Relationship Mapping

---


## Navigation

**Location**: `relationships\configuration\03_settings_validator_relationships.md`

**Parent**: [[relationships\configuration\README.md]]


## Architecture Overview

Project-AI uses **four distinct validation approaches**:

1. **Pydantic Validators** (Temporal config) - Type and constraint validation
2. **Manual Validation** (God Tier config) - Custom business logic
3. **Security Validation** (Settings Manager) - Security policy enforcement
4. **JSON Schema** (Defense Engine) - Declarative schema validation

---

## Validation System 1: Pydantic Field Validators

### File: `src/app/temporal/config.py` [[src/app/temporal/config.py]]

#### Validation Approach

```python
from pydantic import Field
from pydantic_settings import BaseSettings

class TemporalConfig(BaseSettings):
    """Pydantic-based config with automatic validation."""
    
    # Type validation (implicit)
    host: str = Field(default="localhost:7233")
    
    # Integer with constraints
    max_concurrent_activities: int = Field(
        default=50,
        description="Maximum number of concurrent activity executions"
    )
    
    # Integer with min/max constraints
    workflow_execution_timeout: int = Field(
        default=3600,
        description="Maximum time for entire workflow execution"
    )
    
    # Custom validation via property
    @property
    def is_cloud(self) -> bool:
        """Derived validation: check if using Temporal Cloud."""
        return bool(self.cloud_namespace)
```

#### Validation Triggers

```
┌──────────────────────────────────┐
│  Config Instantiation            │
│  config = TemporalConfig()       │
└──────────────────────────────────┘
         ↓
┌──────────────────────────────────┐
│  Pydantic Validation (Auto)      │
│  1. Type checking                │
│  2. Field constraints            │
│  3. Default value assignment     │
└──────────────────────────────────┘
         ↓
┌──────────────────────────────────┐
│  Environment Variable Parsing    │
│  - TEMPORAL_HOST → str           │
│  - TEMPORAL_MAX_CONCURRENT → int │
└──────────────────────────────────┘
         ↓
    Validated Config Instance
```

#### Validation Rules

| Field | Type | Constraints | Error on Violation |
|-------|------|-------------|-------------------|
| `host` | `str` | None | TypeError if not string |
| `max_concurrent_activities` | `int` | None (implicit ≥ 0) | ValueError if not int |
| `max_retry_attempts` | `int` | Default: 3 | ValueError if not int |
| `cloud_namespace` | `str \| None` | None | TypeError if wrong type |

---

## Validation System 2: God Tier Config Manual Validation

### File: `src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]]

#### Method: `ConfigurationManager.validate_config()`

```python
def validate_config(self) -> tuple[bool, list[str]]:
    """Validate configuration with custom business logic."""
    errors = []
    
    # 1. Voice model validation
    voice = self.config.voice_model
    if voice.enabled and not voice.models:
        errors.append("Voice models list is empty but voice is enabled")
    
    # 2. Visual model validation
    visual = self.config.visual_model
    if visual.enabled and not visual.models:
        errors.append("Visual models list is empty but visual is enabled")
    
    # 3. Camera configuration validation
    camera = self.config.camera
    if camera.enabled:
        if len(camera.resolution) != 2:
            errors.append("Camera resolution must be [width, height]")
        if camera.fps <= 0:
            errors.append("Camera FPS must be positive")
    
    # 4. Conversation config validation
    conv = self.config.conversation
    if conv.context_window <= 0:
        errors.append("Context window must be positive")
    
    # 5. Policy range validation (0.0-1.0)
    policy = self.config.policy
    for attr in ["default_response_length", "default_formality", 
                 "default_empathy", "default_sensitivity", "default_humor"]:
        value = getattr(policy, attr)
        if not 0.0 <= value <= 1.0:
            errors.append(f"Policy {attr} must be between 0 and 1")
    
    # 6. Fusion strategy enum validation
    fusion = self.config.fusion
    if fusion.strategy not in ["early_fusion", "late_fusion", "hybrid_fusion"]:
        errors.append(f"Invalid fusion strategy: {fusion.strategy}")
    
    is_valid = len(errors) == 0
    return is_valid, errors
```

#### Validation Categories

```
┌─────────────────────────────────────────┐
│  Component Existence Checks             │
│  - Voice models present if enabled      │
│  - Visual models present if enabled     │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  Structural Validation                  │
│  - Camera resolution is [width, height] │
│  - Lists have correct length            │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  Range Validation                       │
│  - FPS > 0                              │
│  - Context window > 0                   │
│  - Policy values in [0.0, 1.0]          │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  Enum Validation                        │
│  - Fusion strategy in allowed values    │
│  - Deployment mode in allowed values    │
└─────────────────────────────────────────┘
```

#### When Validation Runs

```python
# Manual invocation (not automatic)
manager = ConfigurationManager()
manager.load_config()
is_valid, errors = manager.validate_config()  # ← Explicit call required

if not is_valid:
    logger.error(f"Config validation failed: {errors}")
```

**Critical**: Validation is **NOT automatic** - must be called explicitly.

---

## Validation System 3: Settings Manager Security Validation

### File: `config/settings_manager.py`

#### Method: `SettingsManager.validate_settings()`

```python
def validate_settings(self) -> dict[str, Any]:
    """Validate settings for SECURITY and CONSISTENCY."""
    issues = []
    
    # 1. Critical security: God tier encryption
    if not self.settings["privacy"]["god_tier_encryption"]:
        issues.append("God tier encryption is disabled!")
    
    # 2. Critical security: Kill switch
    if not self.settings["security"]["kill_switch"]:
        issues.append("Kill switch is disabled!")
    
    # 3. Critical security: Ad blocker HOLY WAR mode
    if not self.settings["ad_blocker"]["holy_war_mode"]:
        issues.append("Ad blocker HOLY WAR mode is disabled!")
    
    # 4. Remote access authentication
    if (self.settings["remote_access"]["browser_enabled"] or 
        self.settings["remote_access"]["desktop_enabled"]):
        if not self.settings["remote_access"]["require_authentication"]:
            issues.append("Remote access enabled without authentication!")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": len(issues)
    }
```

#### Security Policy Enforcement

| Policy Check | Category | Impact if Failed |
|--------------|----------|-----------------|
| God tier encryption enabled | Privacy | Data exposure risk |
| Kill switch enabled | Security | No emergency shutdown |
| HOLY WAR mode enabled | Privacy | Ad/tracker exposure |
| Remote auth required | Security | Unauthorized access risk |

#### Validation Trigger Points

```python
# 1. On-demand status check
status = settings_manager.get_status()
# status["validation"] contains validation results

# 2. Before exporting settings
encrypted = settings_manager.export_settings()
# Should validate before export (not implemented)

# 3. After importing settings
settings_manager.import_settings(encrypted_data)
# Should validate after import (not implemented)
```

---

## Validation System 4: JSON Schema (Defense Engine)

### File: `config/schemas/defense_engine.schema.json`

#### Schema Structure

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
        "auto_discover": {"type": "boolean"},
        "failure_mode": {
          "type": "string",
          "enum": ["continue", "stop", "rollback"]
        },
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

#### Validation Capabilities

```
┌─────────────────────────────────────────┐
│  Type Validation                        │
│  - string, number, boolean, object      │
│  - array with item constraints          │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  Pattern Matching                       │
│  - Regex for version numbers            │
│  - Regex for subsystem IDs              │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  Enum Constraints                       │
│  - operational_mode values              │
│  - failure_mode values                  │
│  - encryption_algorithm values          │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  Numeric Constraints                    │
│  - minimum/maximum values               │
│  - health_check_interval: [1, 300]      │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  Required Fields                        │
│  - version, bootstrap, subsystems       │
│  - Per-object required fields           │
└─────────────────────────────────────────┘
```

#### Usage Pattern (Not Currently Implemented)

```python
# Expected usage (not in codebase)
import json
import jsonschema

# Load schema
with open("config/schemas/defense_engine.schema.json") as f:
    schema = json.load(f)

# Load config
with open("config/defense_engine.toml") as f:
    config = toml.load(f)

# Validate
try:
    jsonschema.validate(instance=config, schema=schema)
    print("Config is valid!")
except jsonschema.ValidationError as e:
    print(f"Validation error: {e.message}")
```

**Status**: Schema exists but **no validation code found** in codebase.

---

## Relationships Between Validation Systems

### System Interaction Matrix

| Source System | Target System | Relationship | Integration Point |
|--------------|---------------|--------------|-------------------|
| **Pydantic Validators** | Temporal Config | Direct | Type validation on instantiation |
| **God Tier Validator** | God Tier Config | Manual | `validate_config()` method |
| **Settings Validator** | Settings Manager | Manual | `validate_settings()` method |
| **JSON Schema** | Defense Engine | None | Schema exists, no validation code |

### Validation Coverage by Config Type

```
┌──────────────────────────────────────────────────────┐
│  CLI Config (.projectai.toml)                        │
│  Validation: NONE                                    │
│  Risk: Type errors, invalid values                   │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  API Config (settings.py)                            │
│  Validation: Type casting in os.getenv()             │
│  Risk: Runtime errors if env var malformed           │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  Temporal Config (temporal/config.py)                │
│  Validation: Pydantic (automatic)                    │
│  Risk: LOW - types enforced                          │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  God Tier Config (god_tier_config.py)                │
│  Validation: Manual validate_config()                │
│  Risk: MEDIUM - validation not automatic             │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  Settings Manager (settings_manager.py)              │
│  Validation: Security policy checks                  │
│  Risk: MEDIUM - validation not enforced on set       │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  Defense Engine (defense_engine.toml)                │
│  Validation: JSON Schema (not implemented)           │
│  Risk: HIGH - no validation code                     │
└──────────────────────────────────────────────────────┘
```

---

## Validation Flow Patterns

### Pattern 1: Automatic Validation (Pydantic)

```python
# Validation happens on object creation
config = TemporalConfig()  # ← Pydantic validates here

# Invalid value triggers immediate error
config = TemporalConfig(max_concurrent_activities="invalid")
# → pydantic.ValidationError: value is not a valid integer
```

### Pattern 2: Manual Validation (God Tier)

```python
# Load config (no validation)
manager = ConfigurationManager()
config = manager.load_config()  # ← NO validation

# Explicit validation call required
is_valid, errors = manager.validate_config()  # ← Validation here
if not is_valid:
    # Handle errors
```

### Pattern 3: On-Demand Validation (Settings Manager)

```python
# Settings can be set without validation
settings.set_setting("security", "kill_switch", False)  # ← No check

# Validation only when requested
validation = settings.validate_settings()  # ← Validation here
if not validation["valid"]:
    # Warning logged, but setting already changed
```

### Pattern 4: Schema Validation (Not Active)

```python
# Schema exists but no validation implementation
# Expected pattern:
jsonschema.validate(instance=config_dict, schema=schema)
```

---

## Validation Error Handling

### Pydantic Errors (Temporal Config)

```python
try:
    config = TemporalConfig(max_concurrent_activities="invalid")
except pydantic.ValidationError as e:
    # Structured error with field details
    print(e.json())
    # {
    #   "loc": ["max_concurrent_activities"],
    #   "msg": "value is not a valid integer",
    #   "type": "type_error.integer"
    # }
```

### Manual Validation Errors (God Tier)

```python
is_valid, errors = manager.validate_config()
# errors = [
#   "Camera FPS must be positive",
#   "Policy default_empathy must be between 0 and 1"
# ]

if not is_valid:
    for error in errors:
        logger.error(f"Config validation: {error}")
```

### Security Validation Warnings (Settings Manager)

```python
validation = settings.validate_settings()
# {
#   "valid": False,
#   "issues": ["Kill switch is disabled!"],
#   "warnings": 1
# }

if not validation["valid"]:
    logger.warning(f"Security issues: {validation['issues']}")
```

---

## Validation Gaps & Recommendations

### Current Gaps

1. **CLI Config**: No validation (TOML parsing only)
2. **API Config**: Only type casting, no constraint checks
3. **God Tier**: Manual validation not enforced
4. **Settings Manager**: Validation after modification, not before
5. **Defense Engine**: Schema exists but unused

### Recommended Improvements

```python
# 1. CLI Config: Add Pydantic validator
class CLIConfig(BaseSettings):
    class GeneralConfig(BaseModel):
        log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]
        data_dir: Path
    
    general: GeneralConfig

# 2. Settings Manager: Validate before set
def set_setting(self, category: str, key: str, value: Any):
    # Validate value before setting
    if category == "security" and key == "kill_switch":
        if not isinstance(value, bool):
            raise ValueError("kill_switch must be boolean")
    self.settings[category][key] = value

# 3. Defense Engine: Implement JSON Schema validation
def load_defense_config(config_file: str) -> dict:
    with open(config_file) as f:
        config = toml.load(f)
    
    with open("config/schemas/defense_engine.schema.json") as f:
        schema = json.load(f)
    
    jsonschema.validate(instance=config, schema=schema)
    return config
```

---

## Related Systems

### Configuration Systems
- [Config Loader](./01_config_loader_relationships.md)
- [Configuration Schema](./05_configuration_schema_relationships.md)
- [Environment Manager](./02_environment_manager_relationships.md)
- [Default Values](./10_default_values_relationships.md)

### Cross-System Dependencies
- [[../security/01_security_system_overview.md|Security System Overview]] - Security validation policies
- [[../security/07_security_metrics.md|Security Metrics]] - Validation audit logging
- [[../data/01-PERSISTENCE-PATTERNS.md|Persistence Patterns]] - Config validation on load/save
- [[../monitoring/01-logging-system.md|Logging System]] - Validation error logging
- [[../monitoring/08-metrics-collection.md|Metrics Collection]] - Validation metrics tracking
