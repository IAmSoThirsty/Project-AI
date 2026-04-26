# Configuration Loader System Relationships

**System:** Config Loader  
**Core Files:** 
- `src/app/core/config.py` [[src/app/core/config.py]] - CLI TOML-based config loader
- `config/settings.py` - Basic API config with environment variables
- `src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]] - YAML-based comprehensive config system

**Last Updated:** 2025-04-20  
**Mission:** AGENT-065 Configuration Systems Relationship Mapping

---


## Navigation

**Location**: `relationships\configuration\01_config_loader_relationships.md`

**Parent**: [[relationships\configuration\README.md]]


## Architecture Overview

The Project-AI system has **three distinct configuration loading systems** operating in parallel:

1. **CLI Config System** (`src/app/core/config.py` [[src/app/core/config.py]]) - TOML-based for CLI operations
2. **API Config System** (`config/settings.py`) - Simple environment-based for API server
3. **God Tier Config System** (`src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]]) - YAML-based for advanced features

---

## System 1: CLI Configuration Loader

### File: `src/app/core/config.py` [[src/app/core/config.py]]

#### Load Chain & Priority (Highest to Lowest)

```
┌─────────────────────────────────────────────┐
│  1. ENVIRONMENT VARIABLES (PROJECTAI_*)     │  ← HIGHEST PRIORITY
│     Format: PROJECTAI_SECTION_KEY=value     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  2. PROJECT CONFIG (.projectai.toml)        │  ← Project-specific
│     Location: Current working directory     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  3. USER CONFIG (~/.projectai.toml)         │  ← User-specific
│     Location: User's home directory         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  4. DEFAULT VALUES (Config.DEFAULTS)        │  ← Hardcoded fallbacks
│     Location: Embedded in config.py         │
└─────────────────────────────────────────────┘
```

#### Configuration Sections

```python
DEFAULTS = {
    "general": {
        "log_level": "INFO",
        "data_dir": "data",
        "verbose": False
    },
    "ai": {
        "model": "gpt-3.5-turbo",
        "provider": "openai",      # openai | perplexity
        "temperature": 0.7,
        "max_tokens": 256
    },
    "security": {
        "enable_four_laws": True,
        "enable_black_vault": True,
        "enable_audit_log": True
    },
    "api": {
        "timeout": 30,
        "retry_attempts": 3
    },
    "health": {
        "collect_system_metrics": True,
        "collect_dependencies": True,
        "collect_config_summary": True,
        "snapshot_dir": "data/health_snapshots",
        "report_dir": "docs/assets"
    }
}
```

#### Relationships to Other Systems

| System | Relationship | Integration Point |
|--------|-------------|-------------------|
| **Environment Manager** | Consumes | `_apply_env_overrides()` reads `PROJECTAI_*` variables |
| **Settings Validator** | None | No explicit validation (relies on type preservation) |
| **Default Values** | Provides | `DEFAULTS` dict serves as fallback |
| **Override Hierarchy** | Implements | 4-tier precedence system |
| **Config Inheritance** | Implements | `_merge_config()` for cascading configs |

#### Key Methods

```python
def _load_config(config_path: Path | None = None) -> None:
    """Load configuration from file(s) with cascading priority"""
    # 1. Start with defaults
    self.config = self.DEFAULTS.copy()
    
    # 2. Load user config
    user_config_path = Path.home() / ".projectai.toml"
    if user_config_path.exists():
        self._merge_config(self._read_toml(user_config_path))
    
    # 3. Load project config
    project_config_path = Path.cwd() / ".projectai.toml"
    if project_config_path.exists():
        self._merge_config(self._read_toml(project_config_path))
    
    # 4. Apply environment overrides
    self._apply_env_overrides()
```

---

## System 2: API Configuration Loader

### File: `config/settings.py`

#### Direct Environment Variables

```python
class Config:
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8001"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    
    # TARL Configuration
    TARL_VERSION: str = os.getenv("TARL_VERSION", "1.0")
    TARL_SIGNATURE_ALGORITHM: str = os.getenv("TARL_SIGNATURE_ALGORITHM", "SHA256")
    
    # Security
    ENABLE_CORS: bool = os.getenv("ENABLE_CORS", "true").lower() == "true"
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:8000"
    ).split(",")
    
    # Paths (auto-generated)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
```

#### Relationships to Other Systems

| System | Relationship | Integration Point |
|--------|-------------|-------------------|
| **Environment Variables** | Direct consumer | Every attribute reads from `os.getenv()` |
| **Default Values** | Provides inline | Default values in `os.getenv()` second parameter |
| **Override Hierarchy** | Simple (env-only) | No file-based overrides, only environment |

---

## System 3: God Tier Configuration Loader

### File: `src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]]

#### YAML-based Dataclass System

```python
@dataclass
class GodTierConfig:
    """Master configuration with nested dataclass components"""
    version: str = "1.0.0"
    deployment_mode: str = "production"  # production|development|testing
    
    # Component configurations
    voice_model: VoiceModelConfig = field(default_factory=VoiceModelConfig)
    visual_model: VisualModelConfig = field(default_factory=VisualModelConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    conversation: ConversationConfig = field(default_factory=ConversationConfig)
    policy: PolicyConfig = field(default_factory=PolicyConfig)
    fusion: FusionConfig = field(default_factory=FusionConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    storage: DataStorageConfig = field(default_factory=DataStorageConfig)
```

#### Load/Save Flow

```
┌─────────────────────────────────┐
│  ConfigurationManager.__init__  │
└─────────────────────────────────┘
                ↓
┌─────────────────────────────────┐
│  load_config()                  │ ← Loads from god_tier_config.yaml
│  - Check file exists            │
│  - Parse YAML                   │
│  - Convert dict → dataclasses   │
└─────────────────────────────────┘
                ↓
┌─────────────────────────────────┐
│  save_config()                  │ ← Persists to YAML
│  - Convert dataclasses → dict   │
│  - Write YAML (sorted keys)     │
└─────────────────────────────────┘
```

#### Relationships to Other Systems

| System | Relationship | Integration Point |
|--------|-------------|-------------------|
| **Configuration Schema** | Enforced by dataclasses | Type hints validate structure |
| **Settings Validator** | Built-in | `validate_config()` method |
| **Default Values** | Dataclass defaults | `field(default_factory=...)` |
| **Config Inheritance** | None | Flat YAML structure |

---

## Cross-System Integration Points

### 1. CLI Config ↔ Environment Variables

```python
# config.py reads environment with prefix
def _apply_env_overrides(self) -> None:
    prefix = "PROJECTAI_"
    for key, value in os.environ.items():
        if key.startswith(prefix):
            # Parse: PROJECTAI_GENERAL_LOG_LEVEL → section="general", key="log_level"
            parts = key[len(prefix):].lower().split("_", 1)
```

### 2. API Config ↔ .env Files

```python
# settings.py directly reads os.getenv()
# Assumes .env loaded by application startup (dotenv)
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
```

### 3. God Tier Config ↔ YAML Persistence

```python
# god_tier_config.py manages entire lifecycle
manager = ConfigurationManager("config/god_tier_config.yaml")
config = manager.load_config()  # YAML → dataclasses
manager.save_config()           # dataclasses → YAML
```

---

## Data Flow: User Request → Configuration

```
User Request
    ↓
┌───────────────────────────────────────┐
│  Application Initialization           │
├───────────────────────────────────────┤
│  1. Load .env (dotenv)                │
│  2. Init Config (CLI/API/God Tier)    │
│  3. Apply environment overrides       │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│  Config Access Pattern                │
├───────────────────────────────────────┤
│  CLI:      config.get("ai", "model")  │
│  API:      Config.API_HOST            │
│  God Tier: config.voice_model.enabled │
└───────────────────────────────────────┘
    ↓
Runtime Configuration Values
```

---

## Persistence Patterns

> **Cross-System Integration**: Configuration persistence follows [[../data/01-PERSISTENCE-PATTERNS.md|Persistence Patterns]] and uses [[../data/00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure]]

### CLI Config (TOML)
```toml
# ~/.projectai.toml or ./.projectai.toml
[general]
log_level = "DEBUG"
data_dir = "custom_data"

[ai]
model = "gpt-4"
provider = "openai"
```

### API Config (Environment)
```bash
# .env
API_HOST=0.0.0.0
API_PORT=8001
TARL_VERSION=1.0
```

### God Tier Config (YAML)
```yaml
# config/god_tier_config.yaml
version: "1.0.0"
deployment_mode: "production"
voice_model:
  enabled: true
  models:
    - "basic_tts"
    - "emotional_tts"
```

---

## Security Considerations

1. **File Permissions**: No explicit checks on config file permissions → See [[../security/03_defense_layers.md|Defense Layers]]
2. **Sensitive Data**: API keys stored in environment variables (good practice) → See [[../security/02_threat_models.md|Threat Models]]
3. **Config Injection**: Environment variables can override any CLI config setting → See [[../security/01_security_system_overview.md|Security Overview]]
4. **Validation**: Only God Tier has comprehensive validation via `validate_config()` → See [[../security/07_security_metrics.md|Security Metrics]]
5. **Audit Logging**: Security config changes tracked → See [[../monitoring/01-logging-system.md|Logging System]]

---

## Related Systems

### Configuration Systems
- [Environment Manager](./02_environment_manager_relationships.md)
- [Settings Validator](./03_settings_validator_relationships.md)
- [Override Hierarchy](./09_override_hierarchy_relationships.md)
- [Default Values](./10_default_values_relationships.md)

### Cross-System Dependencies
- [[../security/01_security_system_overview.md|Security System Overview]] - Security configuration enforcement
- [[../security/07_security_metrics.md|Security Metrics]] - Audit logging for config changes
- [[../data/01-PERSISTENCE-PATTERNS.md|Persistence Patterns]] - TOML/YAML config storage
- [[../data/00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure]] - data_dir configuration
- [[../monitoring/01-logging-system.md|Logging System]] - log_level configuration
