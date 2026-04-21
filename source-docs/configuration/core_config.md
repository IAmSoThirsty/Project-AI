# Core Configuration Module

**Module**: `src/app/core/config.py` [[src/app/core/config.py]]  
**Purpose**: CLI configuration management with TOML support and environment overrides  
**Classification**: Core Configuration System  
**Priority**: P1 - Developer Tools

---

## Overview

The Core Configuration Module provides hierarchical configuration loading from multiple sources with environment variable overrides. It supports user-specific config (`~/.projectai.toml`), project-specific config (`.projectai.toml`), and environment-based overrides using the `PROJECTAI_` prefix.

### Key Characteristics

- **Format**: TOML-based configuration files
- **Hierarchy**: Environment > Project > User > Defaults
- **Sections**: general, ai, security, api, health
- **Type Preservation**: Automatic type casting for env overrides
- **Singleton**: Global config instance pattern

---

## Architecture

### Class Structure

```python
class Config:
    """Configuration manager for Project-AI."""
    
    DEFAULTS: dict[str, dict[str, Any]]  # Default configuration values
    
    def __init__(self, config_path: Path | None = None):
        self.config: dict[str, Any] = {}
        self._load_config(config_path)
```

### Configuration Hierarchy

Priority order (highest to lowest):
1. **Environment Variables** (`PROJECTAI_*`)
2. **Project Config** (`.projectai.toml` in current directory)
3. **User Config** (`~/.projectai.toml` in home directory)
4. **Defaults** (hardcoded in `DEFAULTS` dict)

---

## Default Configuration

### General Settings

```python
"general": {
    "log_level": "INFO",
    "data_dir": "data",
    "verbose": False
}
```

### AI Settings

```python
"ai": {
    "model": "gpt-3.5-turbo",
    "provider": "openai",  # Options: 'openai', 'perplexity'
    "temperature": 0.7,
    "max_tokens": 256
}
```

### Security Settings

```python
"security": {
    "enable_four_laws": True,
    "enable_black_vault": True,
    "enable_audit_log": True
}
```

### API Settings

```python
"api": {
    "timeout": 30,
    "retry_attempts": 3
}
```

### Health Settings

```python
"health": {
    "collect_system_metrics": True,
    "collect_dependencies": True,
    "collect_config_summary": True,
    "snapshot_dir": "data/health_snapshots",
    "report_dir": "docs/assets"
}
```

---

## Core API

### Initialization

```python
def __init__(self, config_path: Path | None = None):
    """Initialize configuration.
    
    Args:
        config_path: Optional path to config file. If not provided,
                    will search in standard locations.
    
    Loading Order:
        1. Load defaults
        2. Load user config (~/.projectai.toml)
        3. Load project config (.projectai.toml)
        4. Load specified config (if provided)
        5. Apply environment overrides
    """
```

### Accessing Configuration

```python
def get(self, section: str, key: str, default: Any = None) -> Any:
    """Get a configuration value.
    
    Args:
        section: Configuration section name
        key: Configuration key name
        default: Default value if key not found
    
    Returns:
        Configuration value or default
    
    Example:
        >>> config.get("ai", "model", "gpt-3.5-turbo")
        'gpt-4'
    """

def get_section(self, section: str) -> dict[str, Any]:
    """Get entire configuration section.
    
    Args:
        section: Configuration section name
    
    Returns:
        Configuration section dictionary
    
    Example:
        >>> config.get_section("ai")
        {'model': 'gpt-4', 'temperature': 0.7, ...}
    """
```

### Global Instance

```python
def get_config(reload: bool = False) -> Config:
    """Get global configuration instance.
    
    Args:
        reload: If True, reload configuration from files
    
    Returns:
        Global Config instance
    
    Pattern: Singleton with reload capability
    """
```

---

## Configuration File Format

### TOML Structure

```toml
# ~/.projectai.toml or .projectai.toml

[general]
log_level = "DEBUG"
data_dir = "custom_data"
verbose = true

[ai]
model = "gpt-4"
provider = "openai"
temperature = 0.8
max_tokens = 512

[security]
enable_four_laws = true
enable_black_vault = true
enable_audit_log = true

[api]
timeout = 60
retry_attempts = 5

[health]
collect_system_metrics = true
snapshot_dir = "data/health_snapshots"
report_dir = "docs/assets"
```

---

## Environment Variable Overrides

### Naming Convention

```
PROJECTAI_<SECTION>_<KEY>=<value>
```

### Examples

```bash
# Override log level
export PROJECTAI_GENERAL_LOG_LEVEL=DEBUG

# Override AI model
export PROJECTAI_AI_MODEL=gpt-4

# Override security setting
export PROJECTAI_SECURITY_ENABLE_FOUR_LAWS=false

# Override API timeout
export PROJECTAI_API_TIMEOUT=60
```

### Type Preservation

Environment variables are automatically cast to match original types:

```python
# Boolean conversion
PROJECTAI_GENERAL_VERBOSE=true  → True
PROJECTAI_GENERAL_VERBOSE=false → False
PROJECTAI_GENERAL_VERBOSE=1     → True
PROJECTAI_GENERAL_VERBOSE=0     → False

# Integer conversion
PROJECTAI_API_TIMEOUT=60        → 60

# Float conversion
PROJECTAI_AI_TEMPERATURE=0.8    → 0.8

# String (default)
PROJECTAI_AI_MODEL=gpt-4        → "gpt-4"
```

---

## Configuration Patterns

### Pattern 1: Simple Configuration Access

```python
from src.app.core.config import get_config

config = get_config()

# Get values with defaults
log_level = config.get("general", "log_level", "INFO")
ai_model = config.get("ai", "model", "gpt-3.5-turbo")
timeout = config.get("api", "timeout", 30)
```

### Pattern 2: Section-Based Access

```python
# Get entire section
ai_config = config.get_section("ai")
model = ai_config["model"]
temperature = ai_config["temperature"]

# Use in function
def create_ai_client(config: Config):
    ai_settings = config.get_section("ai")
    return AIClient(
        model=ai_settings["model"],
        temperature=ai_settings["temperature"]
    )
```

### Pattern 3: Environment Override

```python
# Development: Use environment for quick testing
export PROJECTAI_AI_MODEL=gpt-4
export PROJECTAI_GENERAL_LOG_LEVEL=DEBUG
python -m src.app.main

# Production: Use config file
# .projectai.toml in deployment directory
python -m src.app.main
```

### Pattern 4: User vs Project Config

```python
# User config: ~/.projectai.toml
# Personal preferences, applies to all projects
[general]
verbose = true
log_level = "DEBUG"

# Project config: .projectai.toml
# Project-specific overrides
[ai]
model = "gpt-4"
[security]
enable_audit_log = true
```

### Pattern 5: Reload on Change

```python
# Initial load
config = get_config()

# Modify config file externally
# ...

# Reload configuration
config = get_config(reload=True)
```

---

## Integration Patterns

### Pattern 1: Application Startup

```python
from src.app.core.config import get_config
import logging

def main():
    # Load configuration
    config = get_config()
    
    # Configure logging
    log_level = config.get("general", "log_level", "INFO")
    logging.basicConfig(level=log_level)
    
    # Initialize components with config
    ai_settings = config.get_section("ai")
    initialize_ai(ai_settings)
```

### Pattern 2: Component Configuration

```python
class AIEngine:
    def __init__(self, config: Config):
        self.model = config.get("ai", "model")
        self.temperature = config.get("ai", "temperature")
        self.max_tokens = config.get("ai", "max_tokens")
        self.provider = config.get("ai", "provider")
```

### Pattern 3: Health Reporting

```python
from src.app.core.config import get_config

def generate_health_report():
    config = get_config()
    health_config = config.get_section("health")
    
    if health_config["collect_system_metrics"]:
        collect_metrics()
    
    if health_config["collect_dependencies"]:
        check_dependencies()
    
    save_report(health_config["report_dir"])
```

---

## Testing

### Unit Testing

```python
import pytest
from pathlib import Path
from src.app.core.config import Config

def test_default_config():
    config = Config()
    assert config.get("general", "log_level") == "INFO"
    assert config.get("ai", "model") == "gpt-3.5-turbo"

def test_config_from_file(tmp_path):
    # Create test config file
    config_file = tmp_path / ".projectai.toml"
    config_file.write_text("""
[general]
log_level = "DEBUG"

[ai]
model = "gpt-4"
    """)
    
    # Load config
    config = Config(config_file)
    assert config.get("general", "log_level") == "DEBUG"
    assert config.get("ai", "model") == "gpt-4"

def test_env_override(monkeypatch):
    monkeypatch.setenv("PROJECTAI_GENERAL_LOG_LEVEL", "ERROR")
    config = Config()
    assert config.get("general", "log_level") == "ERROR"

def test_get_section():
    config = Config()
    ai_section = config.get_section("ai")
    assert "model" in ai_section
    assert "temperature" in ai_section
```

---

## Security Considerations

### 1. Config File Permissions

```bash
# User config should be readable only by owner
chmod 600 ~/.projectai.toml

# Project config can be more permissive (checked into version control)
chmod 644 .projectai.toml
```

### 2. Sensitive Data

**DO NOT** store secrets in config files:
```toml
# ❌ Bad: API keys in config
[api]
api_key = "sk-xxxxx"

# ✅ Good: Use environment variables
export OPENAI_API_KEY=sk-xxxxx
```

### 3. Environment Variable Security

```python
# Sanitize before logging
def log_config(config: Config):
    safe_config = {
        section: {
            key: "***" if "key" in key.lower() or "secret" in key.lower() else value
            for key, value in values.items()
        }
        for section, values in config.config.items()
    }
    logger.info("Config: %s", safe_config)
```

---

## Troubleshooting

### Issue: Config File Not Found

**Symptom**: Using defaults despite having config file

**Solutions**:
1. Check file location:
   ```bash
   # User config
   ls -la ~/.projectai.toml
   
   # Project config
   ls -la .projectai.toml
   ```

2. Verify TOML syntax:
   ```python
   import tomllib
   with open(".projectai.toml", "rb") as f:
       tomllib.load(f)  # Will raise error if invalid
   ```

### Issue: Environment Override Not Working

**Symptom**: Environment variable ignored

**Solutions**:
1. Check variable name format:
   ```bash
   # Must be uppercase with PROJECTAI_ prefix
   export PROJECTAI_GENERAL_LOG_LEVEL=DEBUG  # ✅
   export projectai_general_log_level=DEBUG  # ❌
   ```

2. Verify variable is exported:
   ```bash
   env | grep PROJECTAI
   ```

3. Check type mismatch:
   ```bash
   # For boolean, use lowercase
   export PROJECTAI_GENERAL_VERBOSE=true  # ✅
   export PROJECTAI_GENERAL_VERBOSE=True  # ❌
   ```

### Issue: Type Conversion Error

**Symptom**: ValueError when loading config

**Solution**: Ensure environment variable can be converted:
```bash
# Integer
export PROJECTAI_API_TIMEOUT=60  # ✅
export PROJECTAI_API_TIMEOUT=sixty  # ❌

# Boolean
export PROJECTAI_GENERAL_VERBOSE=true  # ✅
export PROJECTAI_GENERAL_VERBOSE=yes   # ✅
export PROJECTAI_GENERAL_VERBOSE=maybe # ❌
```

---

## Related Modules

- **Settings Manager**: `config/settings_manager.py` - Comprehensive GUI settings
- **API Config**: `config/settings.py` - Simple API configuration
- **Temporal Config**: `src/app/temporal/config.py` [[src/app/temporal/config.py]] - Temporal workflow settings
- **God-Tier Config**: `src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]] - Multi-modal system config

---

## Best Practices

1. **Use Hierarchy**: Place user preferences in `~/.projectai.toml`, project settings in `.projectai.toml`
2. **Environment for Secrets**: Never commit secrets to config files
3. **Type Safety**: Validate config values after loading
4. **Defaults First**: Provide sensible defaults for all settings
5. **Document Overrides**: Document available environment variables
6. **Reload Sparingly**: Only reload when config changes are expected
7. **Validate Early**: Check required config values at startup
8. **Log Configuration**: Log loaded config (sanitized) for debugging
9. **Version Control**: Commit project config, ignore user config
10. **TOML Validation**: Validate TOML syntax before deployment

---

## Migration Guide

### From JSON Config

```python
# Old: JSON config
import json
with open("config.json") as f:
    old_config = json.load(f)

# New: TOML config
import tomllib
with open("config.toml", "wb") as f:
    # Convert to TOML (manual or using toml library)
    pass
```

### Adding New Config Section

```python
# 1. Add to DEFAULTS in Config class
DEFAULTS = {
    # ... existing sections ...
    "new_section": {
        "setting1": default_value1,
        "setting2": default_value2
    }
}

# 2. Update documentation
# 3. Add to .projectai.toml template
```

---

## Future Enhancements

1. **Schema Validation**: Validate config against schema
2. **Config Encryption**: Encrypt sensitive config sections
3. **Remote Config**: Load config from remote source
4. **Hot Reload**: Automatic reload on file change
5. **Config Diff**: Show differences between config sources
6. **Config Merge Strategies**: Customize how configs merge
7. **Config Profiles**: Named configuration profiles (dev, prod, test)
8. **Config Export**: Export effective config to file
9. **Config Validation**: Pre-flight validation before app start
10. **Config Documentation**: Auto-generate config documentation from defaults


---

## Related Documentation

- **Relationship Map**: [[relationships\configuration\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/config.py]]
