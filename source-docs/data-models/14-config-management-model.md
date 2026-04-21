# Configuration Management Data Model

**Module**: `src/app/core/config.py` [[src/app/core/config.py]]  
**Storage**: `data/settings.json`, `config.yaml` (environment-specific)  
**Persistence**: JSON and YAML with environment variable overrides  
**Schema Version**: 1.0

---

## Overview

Configuration management system with multi-source hierarchy (environment variables > config files > defaults), schema validation, and hot-reload support.

### Key Features

- **Multi-Source Configuration**: Env vars, YAML, JSON, defaults
- **Environment-Specific Configs**: dev, test, staging, prod
- **Schema Validation**: Pydantic-based validation
- **Hot Reload**: Watch for config file changes
- **Secret Management**: Secure handling of sensitive values

---

## Configuration Hierarchy

**Priority (highest to lowest)**:
1. **Environment Variables**: `PROJECT_AI_*` prefix
2. **Config File**: `config.yaml` or `data/settings.json`
3. **Defaults**: Hardcoded defaults in code

---

## Schema Structure

### Application Settings

**File**: `data/settings.json`

```json
{
  "app": {
    "name": "Project-AI",
    "version": "2.0.0",
    "debug": false,
    "log_level": "INFO"
  },
  "database": {
    "engine": "sqlite",
    "path": "data/cognition.db",
    "backup_enabled": true,
    "backup_retention_days": 30
  },
  "ai": {
    "default_model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2048,
    "timeout_seconds": 30
  },
  "security": {
    "password_min_length": 8,
    "session_timeout_minutes": 30,
    "max_login_attempts": 5,
    "lockout_duration_minutes": 15
  },
  "telemetry": {
    "enabled": false,
    "max_events": 1000,
    "rotate_days": 7
  },
  "ui": {
    "theme": "dark",
    "language": "en",
    "auto_save": true
  }
}
```

---

## Field Specifications

### App Config

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `app.name` | string | "Project-AI" | Application name |
| `app.version` | string | "2.0.0" | Semantic version |
| `app.debug` | boolean | false | Debug mode (verbose logging) |
| `app.log_level` | string | "INFO" | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Database Config

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `database.engine` | string | "sqlite" | Database type ("sqlite", "postgresql") |
| `database.path` | string | "data/cognition.db" | SQLite database file path |
| `database.backup_enabled` | boolean | true | Enable automatic backups |
| `database.backup_retention_days` | integer | 30 | Days to retain backups |

### AI Config

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `ai.default_model` | string | "gpt-4" | Default AI model |
| `ai.temperature` | float | 0.7 | Sampling temperature (0.0-1.0) |
| `ai.max_tokens` | integer | 2048 | Maximum tokens per response |
| `ai.timeout_seconds` | integer | 30 | API request timeout |

### Security Config

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `security.password_min_length` | integer | 8 | Minimum password length |
| `security.session_timeout_minutes` | integer | 30 | Session expiration time |
| `security.max_login_attempts` | integer | 5 | Max failed login attempts before lockout |
| `security.lockout_duration_minutes` | integer | 15 | Account lockout duration |

---

## Environment Variable Overrides

### Naming Convention

**Format**: `PROJECT_AI_<SECTION>_<KEY>`

**Examples**:
```bash
PROJECT_AI_APP_DEBUG=true
PROJECT_AI_DATABASE_PATH=/var/lib/project-ai/db.sqlite
PROJECT_AI_AI_DEFAULT_MODEL=gpt-4-turbo
PROJECT_AI_SECURITY_PASSWORD_MIN_LENGTH=12
```

### Loading Priority

```python
import os
from pathlib import Path

def load_config() -> dict:
    """Load configuration from multiple sources."""
    # 1. Load defaults
    config = get_default_config()
    
    # 2. Load from file (if exists)
    config_file = Path("data/settings.json")
    if config_file.exists():
        with open(config_file) as f:
            file_config = json.load(f)
            merge_config(config, file_config)
    
    # 3. Override with environment variables
    for key, value in os.environ.items():
        if key.startswith("PROJECT_AI_"):
            path = key[11:].lower().split("_")  # Remove prefix
            set_nested_value(config, path, value)
    
    return config
```

---

## Schema Validation

### Pydantic Models

```python
from pydantic import BaseModel, Field, validator

class AppConfig(BaseModel):
    name: str = "Project-AI"
    version: str = "2.0.0"
    debug: bool = False
    log_level: str = Field("INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

class DatabaseConfig(BaseModel):
    engine: str = Field("sqlite", pattern="^(sqlite|postgresql)$")
    path: str = "data/cognition.db"
    backup_enabled: bool = True
    backup_retention_days: int = Field(30, ge=1, le=365)

class AIConfig(BaseModel):
    default_model: str = "gpt-4"
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(2048, ge=1, le=32000)
    timeout_seconds: int = Field(30, ge=1, le=300)

class SecurityConfig(BaseModel):
    password_min_length: int = Field(8, ge=6, le=128)
    session_timeout_minutes: int = Field(30, ge=5, le=1440)
    max_login_attempts: int = Field(5, ge=1, le=100)
    lockout_duration_minutes: int = Field(15, ge=1, le=1440)

class Settings(BaseModel):
    app: AppConfig = AppConfig()
    database: DatabaseConfig = DatabaseConfig()
    ai: AIConfig = AIConfig()
    security: SecurityConfig = SecurityConfig()
    
    @validator("*", pre=True)
    def validate_all(cls, v):
        """Custom validation for all fields."""
        return v
```

### Validation Usage

```python
from pydantic import ValidationError

try:
    settings = Settings(**config_data)
except ValidationError as e:
    logger.error("Configuration validation failed: %s", e)
    raise
```

---

## Hot Reload

### File Watcher

```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigFileHandler(FileSystemEventHandler):
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.last_reload = time.time()
    
    def on_modified(self, event):
        if event.src_path.endswith("settings.json"):
            # Debounce: only reload if >1 second since last reload
            if time.time() - self.last_reload > 1.0:
                logger.info("Config file changed, reloading...")
                self.config_manager.reload()
                self.last_reload = time.time()

def start_config_watcher(config_manager):
    """Start watching config file for changes."""
    event_handler = ConfigFileHandler(config_manager)
    observer = Observer()
    observer.schedule(event_handler, "data/", recursive=False)
    observer.start()
    return observer
```

---

## Secret Management

### Sensitive Values

**Never commit to version control**:
- API keys (OpenAI, Hugging Face, etc.)
- Database passwords
- Encryption keys (FERNET_KEY)
- SMTP credentials

### Environment Variable Pattern

```bash
# .env (gitignored)
OPENAI_API_KEY=sk-...
HUGGINGFACE_API_KEY=hf_...
FERNET_KEY=<base64-key>
SMTP_PASSWORD=<password>
```

### Loading Secrets

```python
from dotenv import load_dotenv

load_dotenv()  # Load .env file

openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("OPENAI_API_KEY not set")
```

---

## Usage Examples

### Load Configuration

```python
from app.core.config import ConfigManager

config = ConfigManager()
settings = config.get_settings()

print(f"App Name: {settings.app.name}")
print(f"Database: {settings.database.path}")
print(f"AI Model: {settings.ai.default_model}")
```

### Update Configuration

```python
# Update in-memory
config.set("ai.temperature", 0.8)

# Save to file
config.save()
```

### Access Nested Values

```python
# Get value
temperature = config.get("ai.temperature")

# Get with default
max_retries = config.get("ai.max_retries", default=3)
```

### Environment-Specific Configs

```python
# config/dev.yaml
app:
  debug: true
  log_level: DEBUG

# config/prod.yaml
app:
  debug: false
  log_level: WARNING

# Load based on environment
env = os.getenv("PROJECT_AI_ENV", "dev")
config = ConfigManager(config_file=f"config/{env}.yaml")
```

---

## Testing Strategy

### Unit Tests

```python
def test_default_config():
    config = ConfigManager()
    settings = config.get_settings()
    
    assert settings.app.name == "Project-AI"
    assert settings.database.engine == "sqlite"
    assert settings.ai.temperature == 0.7

def test_env_var_override():
    os.environ["PROJECT_AI_APP_DEBUG"] = "true"
    
    config = ConfigManager()
    settings = config.get_settings()
    
    assert settings.app.debug == True
```

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `storage.py` | Uses database config |
| `intelligence_engine.py` | Uses AI config |
| `user_manager.py` | Uses security config |
| `telemetry.py` | Uses telemetry config |

---

## Future Enhancements

1. **HashiCorp Vault Integration**: Secret management
2. **AWS Secrets Manager**: Cloud-native secrets
3. **Config Encryption**: Encrypt entire config file at rest
4. **Remote Config**: Load from remote server
5. **A/B Testing**: Feature flags and experimentation

---

**Last Updated**: 2024-01-20  
**Schema Version**: 1.0  
**Maintainer**: Project-AI Core Team


---

## Related Documentation

- **Relationship Map**: [[relationships\data\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/config.py]]
