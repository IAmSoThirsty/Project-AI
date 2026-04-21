# Settings Module (Simple Configuration)

**Module**: `config/settings.py`  
**Purpose**: Simple constants and configuration values  
**Classification**: Basic Configuration  
**Priority**: P2 - Utility

---

## Overview

The Settings module provides simple, hardcoded configuration constants and paths. It serves as a lightweight alternative to the comprehensive Settings Manager for basic configuration needs without encryption requirements.

### Key Characteristics

- **Format**: Python module with constants
- **Simplicity**: No dependencies, direct imports
- **Purpose**: API configuration, TARL settings, logging, paths
- **Usage**: Development and simple deployments

---

## Configuration Constants

### API Configuration

```python
# API Server Configuration
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8001"))
API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
```

**Purpose**: Configure API server binding and debug mode

**Environment Variables**:
- `API_HOST`: Server bind address (default: 0.0.0.0)
- `API_PORT`: Server port (default: 8001)
- `API_DEBUG`: Enable debug mode (default: false)

### TARL Configuration

```python
# TARL Configuration
TARL_VERSION: str = os.getenv("TARL_VERSION", "1.0")
TARL_SIGNATURE_ALGORITHM: str = os.getenv("TARL_SIGNATURE_ALGORITHM", "SHA256")
```

**Purpose**: TARL (Temporal Action Rule Language) settings

**Settings**:
- `TARL_VERSION`: TARL specification version
- `TARL_SIGNATURE_ALGORITHM`: Signature algorithm for TARL rules

### Logging Configuration

```python
# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE: str = os.getenv("LOG_FILE", "audit.log")
```

**Purpose**: Configure logging behavior

**Settings**:
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FILE`: Log file path

### Security Configuration

```python
# Security
ENABLE_CORS: bool = os.getenv("ENABLE_CORS", "true").lower() == "true"
ALLOWED_ORIGINS: list = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:8000"
).split(",")
```

**Purpose**: Configure CORS and security settings

**Settings**:
- `ENABLE_CORS`: Enable Cross-Origin Resource Sharing
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins

### Path Configuration

```python
# Paths
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "data"
LOGS_DIR: Path = BASE_DIR / "logs"
```

**Purpose**: Define standard directory structure

**Paths**:
- `BASE_DIR`: Project root directory
- `DATA_DIR`: Data storage directory
- `LOGS_DIR`: Log file directory

---

## Config Class

### Structure

```python
class Config:
    """Central configuration class."""
    
    # All configuration constants as class attributes
    API_HOST: str
    API_PORT: int
    API_DEBUG: bool
    TARL_VERSION: str
    TARL_SIGNATURE_ALGORITHM: str
    LOG_LEVEL: str
    LOG_FILE: str
    ENABLE_CORS: bool
    ALLOWED_ORIGINS: list
    BASE_DIR: Path
    DATA_DIR: Path
    LOGS_DIR: Path
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        
    @classmethod
    def to_dict(cls) -> dict[str, Any]:
        """Convert configuration to dictionary."""
```

### Core API

```python
@classmethod
def get(cls, key: str, default: Any = None) -> Any:
    """Get configuration value by key.
    
    Args:
        key: Configuration key name
        default: Default value if key not found
    
    Returns:
        Configuration value or default
    
    Example:
        >>> Config.get("API_PORT", 8000)
        8001
        >>> Config.get("UNKNOWN", "fallback")
        'fallback'
    """

@classmethod
def to_dict(cls) -> dict[str, Any]:
    """Convert configuration to dictionary.
    
    Returns:
        Dictionary of non-private, non-callable attributes
    
    Example:
        >>> config_dict = Config.to_dict()
        >>> print(config_dict["API_HOST"])
        '0.0.0.0'
    """
```

---

## Directory Initialization

### Auto-Creation

```python
# Ensure directories exist
Config.DATA_DIR.mkdir(exist_ok=True)
Config.LOGS_DIR.mkdir(exist_ok=True)
```

**Behavior**: Directories automatically created on module import

---

## Usage Patterns

### Pattern 1: Direct Access

```python
from config.settings import Config

# Access configuration directly
host = Config.API_HOST
port = Config.API_PORT
log_level = Config.LOG_LEVEL

# Use in application
app.run(host=host, port=port)
```

### Pattern 2: Dictionary Access

```python
from config.settings import Config

# Get all config as dictionary
config_dict = Config.to_dict()

# Access with get()
api_debug = Config.get("API_DEBUG", False)
```

### Pattern 3: Environment Override

```bash
# Set environment variables
export API_HOST=127.0.0.1
export API_PORT=8080
export LOG_LEVEL=DEBUG

# Python automatically reads from environment
python -m src.app.main
```

### Pattern 4: Path Usage

```python
from config.settings import Config

# Use configured paths
data_file = Config.DATA_DIR / "users.json"
log_file = Config.LOGS_DIR / "app.log"

# Ensure parent exists
data_file.parent.mkdir(parents=True, exist_ok=True)
```

---

## Comparison with Settings Manager

| Feature | config/settings.py | config/settings_manager.py |
|---------|-------------------|---------------------------|
| **Encryption** | None | God-tier 7-layer |
| **Complexity** | Simple constants | 13 setting categories |
| **Persistence** | Environment only | Encrypted export/import |
| **Use Case** | API config | Comprehensive app settings |
| **Dependencies** | None | Requires encryption |
| **GUI Support** | No | Yes (via settings dialog) |
| **Validation** | No | Yes |
| **Categories** | Single level | Multi-level nested |

**When to Use**:
- `config/settings.py`: Simple API configuration, development, CLI tools
- `config/settings_manager.py`: Full application with GUI, production deployment

---

## Environment Variables

### Required Variables

None - all have defaults

### Optional Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
API_DEBUG=false

# TARL Configuration
TARL_VERSION=1.0
TARL_SIGNATURE_ALGORITHM=SHA256

# Logging
LOG_LEVEL=INFO
LOG_FILE=audit.log

# Security
ENABLE_CORS=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## Testing

### Unit Testing

```python
import pytest
from config.settings import Config
import os

def test_default_values():
    assert Config.API_HOST == "0.0.0.0"
    assert Config.API_PORT == 8001
    assert Config.LOG_LEVEL == "INFO"

def test_get_method():
    assert Config.get("API_HOST") == "0.0.0.0"
    assert Config.get("UNKNOWN", "default") == "default"

def test_to_dict():
    config_dict = Config.to_dict()
    assert "API_HOST" in config_dict
    assert "API_PORT" in config_dict

def test_env_override(monkeypatch):
    monkeypatch.setenv("API_PORT", "9000")
    # Reload module to pick up environment change
    import importlib
    import config.settings
    importlib.reload(config.settings)
    
    from config.settings import Config
    assert Config.API_PORT == 9000

def test_directories_exist():
    assert Config.DATA_DIR.exists()
    assert Config.LOGS_DIR.exists()
```

---

## Best Practices

1. **Use Environment Variables**: Override via environment, not code changes
2. **Keep Simple**: Don't add complex logic to settings module
3. **Validate Early**: Validate settings at application startup
4. **Document Defaults**: Comment default values with rationale
5. **Path Safety**: Always use `Path` objects, not strings
6. **Type Hints**: Add type hints for IDE support
7. **Immutable**: Treat Config as immutable, don't modify at runtime
8. **Separate Secrets**: Use environment for secrets, not hardcoded
9. **Test Defaults**: Ensure defaults work in fresh environment
10. **Upgrade Path**: Plan migration to Settings Manager for production

---

## Related Modules

- **Settings Manager**: `config/settings_manager.py` - Comprehensive configuration
- **Core Config**: `src/app/core/config.py` [[src/app/core/config.py]] - TOML-based configuration
- **Constants**: `config/constants.py` - System constants

---

## Migration to Settings Manager

### When to Migrate

Migrate from `config/settings.py` to `config/settings_manager.py` when:
- Adding GUI settings interface
- Need encrypted settings storage
- Require settings import/export
- Managing multiple setting categories
- Production deployment with security requirements

### Migration Example

```python
# Before: config/settings.py
from config.settings import Config
log_level = Config.LOG_LEVEL

# After: config/settings_manager.py
from config.settings_manager import SettingsManager
manager = SettingsManager(god_tier_encryption)
log_level = manager.get_setting("general", "log_level")
```

---

## Future Enhancements

1. **Type Validation**: Runtime type checking
2. **Config Schema**: Define expected config structure
3. **Config Reload**: Hot reload on environment change
4. **Config Export**: Export current config to file
5. **Config Diff**: Compare with defaults
6. **Deprecation Warnings**: Warn on deprecated settings
7. **Config Documentation**: Auto-generate config docs
8. **Config Testing**: Automated config validation
9. **Config Profiles**: Support multiple config profiles
10. **Config Encryption**: Optional encryption layer


---

## Related Documentation

- **Relationship Map**: [[relationships\configuration\README.md]]
- **03_Settings_Validator_Relationships**: [[relationships\configuration\03_settings_validator_relationships.md]]


---

## Source Code References

- **Primary Module**: [[config/settings.py]]
