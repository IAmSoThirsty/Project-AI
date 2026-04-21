# Configuration Management System

## Overview

The Configuration Management module (`src/app/core/config.py`) provides flexible configuration loading with support for TOML files, environment variable overrides, and hierarchical configuration merging from multiple sources.

**Location**: `src/app/core/config.py`  
**Lines of Code**: ~250  
**Key Features**: TOML parsing, environment overrides, default values, hierarchical config  
**Dependencies**: tomllib/tomli, pathlib, os

---

## Configuration Priority

Configuration is loaded in order of increasing priority:

1. **Default Values** (lowest priority - hardcoded in code)
2. **User Config** (`~/.projectai.toml` - user-wide settings)
3. **Project Config** (`.projectai.toml` - project-specific)
4. **Explicit Config** (passed to constructor)
5. **Environment Variables** (highest priority - runtime overrides)

---

## Configuration Structure

### Default Configuration

```python
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

---

## Core API

### 1. Initialization

```python
class Config:
    """Configuration manager for Project-AI."""
    
    def __init__(self, config_path: Path | None = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Optional path to config file. If not provided,
                        will search in standard locations.
        """
```

**Example**:
```python
# Load from standard locations
config = Config()

# Load from specific file
config = Config(Path("/etc/projectai.toml"))

# Access configuration
log_level = config.get("general", "log_level")
ai_model = config.get("ai", "model")
```

---

### 2. Getting Values

#### get()
```python
def get(self, section: str, key: str, default: Any = None) -> Any:
    """
    Get configuration value.
    
    Args:
        section: Configuration section (e.g., "general", "ai")
        key: Configuration key within section
        default: Default value if not found
    
    Returns:
        Configuration value or default
    """
```

**Example**:
```python
config = Config()

# Get with default section value
log_level = config.get("general", "log_level")  # "INFO"

# Get with custom default
timeout = config.get("api", "timeout", default=60)

# Get from non-existent section
custom = config.get("custom", "setting", default="fallback")
```

---

#### get_section()
```python
def get_section(self, section: str) -> dict[str, Any]:
    """
    Get entire configuration section.
    
    Args:
        section: Section name
    
    Returns:
        Dictionary of all values in section
    """
```

**Example**:
```python
# Get all AI settings
ai_config = config.get_section("ai")
print(f"Model: {ai_config['model']}")
print(f"Provider: {ai_config['provider']}")
print(f"Temperature: {ai_config['temperature']}")

# Get all security settings
security = config.get_section("security")
if security["enable_four_laws"]:
    initialize_four_laws()
```

---

### 3. Setting Values

#### set()
```python
def set(self, section: str, key: str, value: Any) -> None:
    """
    Set configuration value at runtime.
    
    Args:
        section: Configuration section
        key: Configuration key
        value: Value to set
    """
```

**Example**:
```python
config = Config()

# Change log level at runtime
config.set("general", "log_level", "DEBUG")

# Update AI model
config.set("ai", "model", "gpt-4")
config.set("ai", "temperature", 0.9)
```

**Note**: Runtime changes are not persisted to file. To save, use `save_config()`.

---

#### update_section()
```python
def update_section(self, section: str, updates: dict[str, Any]) -> None:
    """
    Update multiple values in a section.
    
    Args:
        section: Section to update
        updates: Dictionary of key-value pairs to update
    """
```

**Example**:
```python
# Update multiple AI settings
config.update_section("ai", {
    "model": "gpt-4",
    "temperature": 0.8,
    "max_tokens": 512
})

# Update security settings
config.update_section("security", {
    "enable_four_laws": True,
    "enable_black_vault": True
})
```

---

### 4. Environment Variable Overrides

Environment variables in format `PROJECTAI_SECTION_KEY` override configuration:

```bash
# Override log level
export PROJECTAI_GENERAL_LOG_LEVEL=DEBUG

# Override AI model
export PROJECTAI_AI_MODEL=gpt-4

# Override boolean
export PROJECTAI_SECURITY_ENABLE_FOUR_LAWS=true

# Override number
export PROJECTAI_API_TIMEOUT=60
```

**Type Preservation**:
```python
# Config has: "timeout": 30 (int)
# Env var: PROJECTAI_API_TIMEOUT=60
# Result: config.get("api", "timeout") -> 60 (int, not "60" string)

# Config has: "verbose": False (bool)
# Env var: PROJECTAI_GENERAL_VERBOSE=true
# Result: config.get("general", "verbose") -> True (bool)
```

---

## Configuration Files

### TOML Format

```toml
# ~/.projectai.toml or .projectai.toml

[general]
log_level = "DEBUG"
data_dir = "/var/lib/projectai"
verbose = true

[ai]
model = "gpt-4"
provider = "openai"
temperature = 0.8
max_tokens = 512

[ai.fallback]
model = "gpt-3.5-turbo"
enabled = true

[security]
enable_four_laws = true
enable_black_vault = true
enable_audit_log = true

[security.encryption]
algorithm = "AES-256-GCM"
key_rotation_days = 90

[api]
timeout = 60
retry_attempts = 5
base_url = "https://api.example.com"

[api.rate_limit]
max_requests = 100
window_seconds = 60

[health]
collect_system_metrics = true
snapshot_dir = "data/health_snapshots"
report_dir = "docs/assets"
```

---

### Nested Configuration

```python
config = Config()

# Access nested values
fallback_model = config.get("ai.fallback", "model")
encryption_algo = config.get("security.encryption", "algorithm")
rate_limit = config.get("api.rate_limit", "max_requests")
```

---

## Usage Patterns

### Pattern 1: Application Initialization

```python
class Application:
    def __init__(self, config_path: Path | None = None):
        self.config = Config(config_path)
        self._setup_logging()
        self._setup_ai()
        self._setup_security()
    
    def _setup_logging(self):
        """Configure logging from config."""
        level = self.config.get("general", "log_level")
        verbose = self.config.get("general", "verbose")
        
        logging.basicConfig(
            level=getattr(logging, level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
    
    def _setup_ai(self):
        """Initialize AI with config."""
        ai_config = self.config.get_section("ai")
        
        self.ai_engine = IntelligenceEngine(
            model=ai_config["model"],
            provider=ai_config["provider"],
            temperature=ai_config["temperature"],
            max_tokens=ai_config["max_tokens"]
        )
    
    def _setup_security(self):
        """Initialize security systems."""
        security = self.config.get_section("security")
        
        if security["enable_four_laws"]:
            self.four_laws = FourLaws()
        
        if security["enable_black_vault"]:
            self.black_vault = BlackVault()
```

---

### Pattern 2: Feature Flags

```python
class FeatureFlags:
    """Feature flag management via configuration."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def is_enabled(self, feature: str) -> bool:
        """Check if feature is enabled."""
        return self.config.get("features", feature, default=False)
    
    def enable(self, feature: str):
        """Enable a feature at runtime."""
        self.config.set("features", feature, True)
    
    def disable(self, feature: str):
        """Disable a feature at runtime."""
        self.config.set("features", feature, False)

# Usage
flags = FeatureFlags(config)

if flags.is_enabled("experimental_ai"):
    use_experimental_model()
else:
    use_stable_model()
```

**TOML Configuration**:
```toml
[features]
experimental_ai = false
advanced_monitoring = true
beta_ui = false
```

---

### Pattern 3: Environment-Specific Config

```python
class EnvironmentConfig:
    """Environment-specific configuration."""
    
    def __init__(self):
        env = os.getenv("PROJECTAI_ENV", "development")
        config_file = Path(f".projectai.{env}.toml")
        
        self.config = Config(config_file)
        self.environment = env
    
    def is_production(self) -> bool:
        return self.environment == "production"
    
    def is_development(self) -> bool:
        return self.environment == "development"

# Create environment-specific configs:
# .projectai.development.toml
# .projectai.staging.toml
# .projectai.production.toml

env_config = EnvironmentConfig()

if env_config.is_production():
    # Strict settings
    config.set("general", "log_level", "WARNING")
    config.set("security", "enable_audit_log", True)
else:
    # Relaxed settings for development
    config.set("general", "log_level", "DEBUG")
    config.set("general", "verbose", True)
```

---

### Pattern 4: Configuration Validation

```python
class ConfigValidator:
    """Validate configuration values."""
    
    def __init__(self, config: Config):
        self.config = config
        self.errors = []
    
    def validate(self) -> bool:
        """Validate all configuration."""
        self._validate_log_level()
        self._validate_ai_config()
        self._validate_paths()
        
        if self.errors:
            for error in self.errors:
                logger.error(f"Config error: {error}")
            return False
        
        return True
    
    def _validate_log_level(self):
        """Validate log level value."""
        level = self.config.get("general", "log_level")
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        if level not in valid_levels:
            self.errors.append(
                f"Invalid log_level '{level}'. Must be one of: {valid_levels}"
            )
    
    def _validate_ai_config(self):
        """Validate AI configuration."""
        temperature = self.config.get("ai", "temperature")
        if not 0.0 <= temperature <= 2.0:
            self.errors.append(
                f"Invalid temperature {temperature}. Must be between 0.0 and 2.0"
            )
        
        max_tokens = self.config.get("ai", "max_tokens")
        if max_tokens <= 0:
            self.errors.append(
                f"Invalid max_tokens {max_tokens}. Must be positive"
            )
    
    def _validate_paths(self):
        """Validate directory paths."""
        data_dir = self.config.get("general", "data_dir")
        if not Path(data_dir).exists():
            logger.warning(f"Data directory does not exist: {data_dir}")

# Usage
config = Config()
validator = ConfigValidator(config)

if not validator.validate():
    print("Configuration validation failed!")
    sys.exit(1)
```

---

### Pattern 5: Hot Reload

```python
class HotReloadConfig:
    """Configuration with hot reload support."""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = Config(config_path)
        self.last_modified = self._get_mtime()
        
        # Start watcher thread
        self.watcher_thread = threading.Thread(
            target=self._watch_config,
            daemon=True
        )
        self.watcher_thread.start()
    
    def _get_mtime(self) -> float:
        """Get file modification time."""
        return self.config_path.stat().st_mtime if self.config_path.exists() else 0
    
    def _watch_config(self):
        """Watch config file for changes."""
        while True:
            time.sleep(5)  # Check every 5 seconds
            
            current_mtime = self._get_mtime()
            if current_mtime > self.last_modified:
                logger.info("Config file changed, reloading...")
                self.config = Config(self.config_path)
                self.last_modified = current_mtime
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get value from potentially reloaded config."""
        return self.config.get(section, key, default)

# Usage
hot_config = HotReloadConfig(Path(".projectai.toml"))

# Config reloads automatically when file changes
while True:
    log_level = hot_config.get("general", "log_level")
    # Use log_level...
    time.sleep(1)
```

---

## Advanced Features

### 1. Configuration Schema

```python
class ConfigSchema:
    """Define configuration schema with types and validation."""
    
    SCHEMA = {
        "general": {
            "log_level": {
                "type": str,
                "allowed": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                "default": "INFO"
            },
            "data_dir": {
                "type": str,
                "default": "data"
            },
            "verbose": {
                "type": bool,
                "default": False
            }
        },
        "ai": {
            "model": {
                "type": str,
                "default": "gpt-3.5-turbo"
            },
            "temperature": {
                "type": float,
                "min": 0.0,
                "max": 2.0,
                "default": 0.7
            },
            "max_tokens": {
                "type": int,
                "min": 1,
                "max": 4096,
                "default": 256
            }
        }
    }
    
    @classmethod
    def validate_value(cls, section: str, key: str, value: Any) -> bool:
        """Validate a configuration value against schema."""
        if section not in cls.SCHEMA or key not in cls.SCHEMA[section]:
            return True  # No schema defined, allow
        
        schema = cls.SCHEMA[section][key]
        
        # Type check
        if not isinstance(value, schema["type"]):
            return False
        
        # Allowed values check
        if "allowed" in schema and value not in schema["allowed"]:
            return False
        
        # Range check for numbers
        if "min" in schema and value < schema["min"]:
            return False
        if "max" in schema and value > schema["max"]:
            return False
        
        return True
```

---

### 2. Configuration Export

```python
def export_config(config: Config, output_path: Path):
    """Export current configuration to TOML file."""
    import toml  # Requires toml package for writing
    
    with open(output_path, "w") as f:
        toml.dump(config.config, f)
    
    logger.info(f"Configuration exported to {output_path}")

# Usage
config = Config()
config.set("ai", "model", "gpt-4")
export_config(config, Path("custom_config.toml"))
```

---

### 3. Configuration Diff

```python
def diff_configs(config1: Config, config2: Config) -> dict:
    """Find differences between two configurations."""
    diffs = {}
    
    all_sections = set(config1.config.keys()) | set(config2.config.keys())
    
    for section in all_sections:
        section_diffs = {}
        
        sect1 = config1.get_section(section)
        sect2 = config2.get_section(section)
        
        all_keys = set(sect1.keys()) | set(sect2.keys())
        
        for key in all_keys:
            val1 = sect1.get(key)
            val2 = sect2.get(key)
            
            if val1 != val2:
                section_diffs[key] = {"old": val1, "new": val2}
        
        if section_diffs:
            diffs[section] = section_diffs
    
    return diffs

# Usage
prod_config = Config(Path(".projectai.production.toml"))
dev_config = Config(Path(".projectai.development.toml"))

diffs = diff_configs(prod_config, dev_config)
print("Configuration differences:")
for section, changes in diffs.items():
    print(f"\n[{section}]")
    for key, values in changes.items():
        print(f"  {key}: {values['old']} -> {values['new']}")
```

---

## Testing

```python
import unittest
import tempfile

class TestConfig(unittest.TestCase):
    def test_default_config(self):
        config = Config()
        self.assertEqual(config.get("general", "log_level"), "INFO")
        self.assertEqual(config.get("ai", "model"), "gpt-3.5-turbo")
    
    def test_env_override(self):
        os.environ["PROJECTAI_GENERAL_LOG_LEVEL"] = "DEBUG"
        config = Config()
        self.assertEqual(config.get("general", "log_level"), "DEBUG")
    
    def test_file_override(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write('[general]\nlog_level = "WARNING"\n')
            config_path = f.name
        
        try:
            config = Config(Path(config_path))
            self.assertEqual(config.get("general", "log_level"), "WARNING")
        finally:
            Path(config_path).unlink()
```

---

## Related Documentation

- **Environment Setup**: `docs/setup/environment.md`
- **Deployment Guide**: `docs/deployment/README.md`
- **Security Configuration**: `docs/security/configuration.md`

---

**Last Updated**: 2025-01-24  
**Status**: Stable - Production Ready  
**Maintainer**: Core Infrastructure Team
