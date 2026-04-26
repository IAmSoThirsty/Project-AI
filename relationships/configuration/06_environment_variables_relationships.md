# Environment Variables System Relationships

**System:** Environment Variables  
**Core Files:**
- `.env` [[.env]] - Production environment variables
- `.env.example` - Template and documentation
- `dotenv` library - Environment loader
- 27+ files consuming environment variables

**Last Updated:** 2025-04-20  
**Mission:** AGENT-065 Configuration Systems Relationship Mapping

---


## Navigation

**Location**: `relationships\configuration\06_environment_variables_relationships.md`

**Parent**: [[relationships\configuration\README.md]]


## Complete Environment Variable Catalog

### API Keys & Authentication

```bash
# OpenAI Services
OPENAI_API_KEY=sk-...              # GPT models, DALL-E, embeddings
OPENAI_ORG_ID=org-...              # Optional organization context

# DeepSeek AI
DEEPSEEK_API_KEY=sk-...            # DeepSeek V3.2 inference

# Hugging Face
HUGGINGFACE_API_KEY=hf_...         # Stable Diffusion, model hub access

# MCP Integration
WIKI_TASKS_BEARER_TOKEN=<token>   # Bearer token for wiki-tasks MCP server
```

### Server Configuration

```bash
# API Server
API_HOST=0.0.0.0                   # Bind address
API_PORT=8001                      # Port (default: 8001)
API_WORKERS=4                      # Number of worker processes
API_DEBUG=false                    # Debug mode (true|false)

# Environment Mode
ENVIRONMENT=development            # development|production|testing
```

### Service Endpoints

```bash
# Temporal Workflow Engine
TEMPORAL_HOST=localhost:7233       # Server address
TEMPORAL_NAMESPACE=default         # Workflow namespace

# Database
DATABASE_URL=<connection-string>   # Optional database connection

# MCP Server
WIKI_TASKS_MCP_PORT=7777          # Local MCP endpoint port
```

### Security & Cryptography

> **Encryption Integration**: See [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]] for key management details

```bash
# Application Secrets
SECRET_KEY=<urlsafe-32>            # Generated via secrets.token_urlsafe(32) → [[../security/02_threat_models.md|Threat Models]]
FERNET_KEY=<base64-key>            # Generated via Fernet.generate_key() → [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]]

# CORS → [[../security/01_security_system_overview.md|Security Overview]]
CORS_ORIGINS=http://localhost:8000,http://localhost:3000
```

### Audit & Logging

> **Logging Configuration**: See [[../monitoring/01-logging-system.md|Logging System]] for detailed logging architecture

```bash
# Logging Configuration
AUDIT_LOG_PATH=audit.log           # Audit log file location → [[../security/07_security_metrics.md|Security Metrics]]
LOG_LEVEL=INFO                     # DEBUG|INFO|WARNING|ERROR|CRITICAL → [[../monitoring/01-logging-system.md|Logging System]]
```

### TARL Configuration

```bash
# Tamper-proof Archive Layer
TARL_VERSION=1.0                   # TARL protocol version
```

### CLI Configuration Overrides (Prefixed)

```bash
# Format: PROJECTAI_SECTION_KEY=value
PROJECTAI_GENERAL_LOG_LEVEL=DEBUG
PROJECTAI_GENERAL_DATA_DIR=/custom/path
PROJECTAI_GENERAL_VERBOSE=true

PROJECTAI_AI_MODEL=gpt-4
PROJECTAI_AI_PROVIDER=openai
PROJECTAI_AI_TEMPERATURE=0.8
PROJECTAI_AI_MAX_TOKENS=512

PROJECTAI_SECURITY_ENABLE_FOUR_LAWS=true
PROJECTAI_SECURITY_ENABLE_BLACK_VAULT=true
PROJECTAI_SECURITY_ENABLE_AUDIT_LOG=true

PROJECTAI_HEALTH_COLLECT_SYSTEM_METRICS=false
PROJECTAI_HEALTH_SNAPSHOT_DIR=/custom/snapshots
```

---

## Environment Variable Consumers

### High-Security Components (API Keys)

| Component | File | Variable | Fallback Behavior |
|-----------|------|----------|------------------|
| **Intelligence Engine** | `src/app/core/intelligence_engine.py` [[src/app/core/intelligence_engine.py]] | `OPENAI_API_KEY` | Raises error |
| **Image Generator** | `src/app/core/image_generator.py` [[src/app/core/image_generator.py]] | `OPENAI_API_KEY`, `HUGGINGFACE_API_KEY` | Returns error message |
| **DeepSeek Inference** | `src/app/core/deepseek_v32_inference.py` [[src/app/core/deepseek_v32_inference.py]] | `DEEPSEEK_API_KEY` | Feature disabled |
| **Model Providers** | `src/app/core/model_providers.py` [[src/app/core/model_providers.py]] | `OPENAI_API_KEY` | Falls back to other providers |
| **User Manager** | `src/app/core/user_manager.py` [[src/app/core/user_manager.py]] | `FERNET_KEY` | Generates runtime key |

### Configuration Components

| Component | File | Variables | Purpose |
|-----------|------|-----------|---------|
| **API Settings** | `config/settings.py` | `API_HOST`, `API_PORT`, `API_DEBUG` | Server binding |
| **Temporal Config** | `src/app/temporal/config.py` [[src/app/temporal/config.py]] | `TEMPORAL_*` (prefixed) | Workflow engine connection |
| **CLI Config** | `src/app/core/config.py` [[src/app/core/config.py]] | `PROJECTAI_*` (prefixed) | Runtime overrides |
| **Security Auth** | `src/app/core/security/auth.py` [[src/app/core/security/auth.py]] | `SECRET_KEY` | Session signing |

---

## Environment Variable Loading Flow

```
Application Startup
    ↓
┌─────────────────────────────────────────┐
│  1. Python dotenv Loader                │
│     from dotenv import load_dotenv      │
│     load_dotenv()                       │
│                                         │
│  Searches for .env in:                  │
│  - Current directory                    │
│  - Parent directories (recursive)       │
│  - Does NOT override existing env vars  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  2. Environment Variables in os.environ │
│     All .env variables now accessible   │
│     via os.getenv("VAR_NAME")           │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  3. Component Initialization            │
│     - User Manager loads FERNET_KEY     │
│     - Config loads API_*, TARL_*        │
│     - CLI Config reads PROJECTAI_*      │
│     - Temporal reads TEMPORAL_*         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  4. Pydantic BaseSettings (Temporal)    │
│     Reads TEMPORAL_* with validation    │
│     Also reads .env.temporal if exists  │
└─────────────────────────────────────────┘
```

---

## Environment Variable Precedence

```
System Environment Variables (Highest Priority)
    ↓ (if not set)
.env File (Current Directory)
    ↓ (if not set)
.env File (Parent Directories)
    ↓ (if not set)
.env.temporal (Pydantic Config.env_file)
    ↓ (if not set)
Default Value in os.getenv("VAR", "default")
    ↓ (if not set)
None (Variable missing)
```

**Critical**: System environment variables **always win** over .env file.

---

## Type Conversion Patterns

### Pattern 1: String (Direct)

```python
api_key = os.getenv("OPENAI_API_KEY")
# No conversion - raw string
```

### Pattern 2: Integer (Manual Cast)

```python
API_PORT: int = int(os.getenv("API_PORT", "8001"))
# Manual int() conversion with string default
```

### Pattern 3: Boolean (String Comparison)

```python
API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
# Converts "true"/"false" string to boolean
```

### Pattern 4: List (String Split)

```python
ALLOWED_ORIGINS: list = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",")
# Splits comma-separated string into list
```

### Pattern 5: Pydantic (Automatic)

```python
class TemporalConfig(BaseSettings):
    max_concurrent_activities: int = Field(default=50)
    # Pydantic automatically converts "50" → 50
```

---

## Environment Variable Validation

### No Validation (Most Components)

```python
# Typical pattern - no validation
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("Missing OPENAI_API_KEY")
    # But no exception raised - silent failure
```

### Pydantic Validation (Temporal Only)

```python
class TemporalConfig(BaseSettings):
    max_concurrent_activities: int = Field(default=50, ge=1)
    # ge=1 ensures value ≥ 1
    # Raises ValidationError if "0" or negative
```

### Manual Validation (User Manager)

```python
env_key = os.getenv("FERNET_KEY")
if env_key:
    try:
        key = env_key.encode()
        self.cipher_suite = Fernet(key)  # ← Validates key format
    except Exception:
        # Invalid key - fall back to runtime key
        self.cipher_suite = Fernet(Fernet.generate_key())
```

---

## Environment Variable Security

### ✅ Good Practices

1. **Gitignore Protection**: `.env` [[.env]] in `.gitignore`
2. **Example Template**: `.env.example` documents all variables
3. **Secrets in .env Only**: No hardcoded API keys
4. **Fernet Key Generation**: Runtime fallback if missing

### ⚠️ Security Gaps

1. **No Permission Checks**: .env file permissions not validated
2. **No Encryption**: .env stored in plaintext
3. **No Secrets Manager**: No integration with HashiCorp Vault, AWS Secrets Manager
4. **No Rotation**: No automated key rotation
5. **Logging Risk**: API keys might appear in debug logs

### 🛡️ Recommended Hardening

```python
# 1. Validate .env permissions (Unix)
import os
import stat

env_path = ".env"
if os.path.exists(env_path):
    st = os.stat(env_path)
    mode = st.st_mode & 0o777
    if mode != 0o600:  # Should be -rw-------
        logger.warning(f".env has insecure permissions: {oct(mode)}")

# 2. Mask secrets in logs
import logging

class SecretFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'msg'):
            # Redact API keys
            record.msg = record.msg.replace(os.getenv("OPENAI_API_KEY", ""), "***")
        return True
```

---

## Multi-Environment Support

### Current Structure

```
Project-AI/
├── .env                    # Development environment
├── .env.example            # Template (committed)
├── web/.env.example        # Web-specific template
├── desktop/.env.example    # Desktop-specific template
└── config/examples/
    ├── .env.example
    └── .env.temporal.example
```

### Recommended: Environment-Specific Files

```
Project-AI/
├── .env                    # Default (gitignored)
├── .env.development        # Development config
├── .env.staging            # Staging config
├── .env.production         # Production config (gitignored)
└── .env.test               # Test config
```

**Load pattern:**

```python
import os
from dotenv import load_dotenv

env = os.getenv("ENVIRONMENT", "development")
load_dotenv(f".env.{env}")  # Load environment-specific file
load_dotenv(".env")         # Load base file (doesn't override)
```

---

## Environment Variable Debugging

### Pattern: Log Loaded Values (Masked)

```python
import logging
import os

logger = logging.getLogger(__name__)

def log_environment():
    """Log loaded environment variables (mask secrets)."""
    env_vars = {
        "API_HOST": os.getenv("API_HOST"),
        "API_PORT": os.getenv("API_PORT"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT"),
        "OPENAI_API_KEY": "***" if os.getenv("OPENAI_API_KEY") else "NOT SET",
        "FERNET_KEY": "***" if os.getenv("FERNET_KEY") else "NOT SET",
    }
    logger.info(f"Environment variables: {env_vars}")
```

### Pattern: Verify Required Variables

```python
def verify_required_env_vars():
    """Verify required environment variables are set."""
    required = [
        "API_HOST",
        "API_PORT",
        "OPENAI_API_KEY",  # Required for core functionality
    ]
    
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        raise EnvironmentError(f"Missing required env vars: {missing}")
```

---

## Relationships to Other Systems

### Environment Variables → Config Loader

```python
# CLI Config: PROJECTAI_* → config sections
PROJECTAI_GENERAL_LOG_LEVEL=DEBUG
# → config["general"]["log_level"] = "DEBUG"

# API Config: Direct mapping
API_PORT=8001
# → Config.API_PORT = 8001
```

### Environment Variables → Feature Flags

```python
# Presence of key enables features
if os.getenv("OPENAI_API_KEY"):
    enable_openai_features()

if os.getenv("DEEPSEEK_API_KEY"):
    enable_deepseek_features()
```

### Environment Variables → Secrets Management

```python
# FERNET_KEY used for encryption
FERNET_KEY=<base64-key>
# → UserManager._setup_cipher() → Fernet(key)

# SECRET_KEY used for session signing
SECRET_KEY=<urlsafe-token>
# → Auth.sign_session(secret_key)
```

---

## Testing with Environment Variables

### Pattern: Temporary Override (pytest)

```python
import pytest
import os

@pytest.fixture
def mock_openai_key(monkeypatch):
    """Mock OpenAI API key for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    yield
    # Auto-cleanup after test

def test_intelligence_engine(mock_openai_key):
    """Test with mocked API key."""
    engine = IntelligenceEngine()
    # Uses sk-test-key instead of real key
```

### Pattern: Test-Specific .env.test

```python
# tests/conftest.py
from dotenv import load_dotenv

def pytest_configure(config):
    """Load test environment before tests run."""
    load_dotenv(".env.test")
```

---

## Related Systems

### Configuration Systems
- [Environment Manager](./02_environment_manager_relationships.md)
- [Config Loader](./01_config_loader_relationships.md)
- [Secrets Management](./07_secrets_management_relationships.md)
- [Feature Flags](./04_feature_flags_relationships.md)
- [Override Hierarchy](./09_override_hierarchy_relationships.md)

### Cross-System Dependencies
- [[../security/01_security_system_overview.md|Security System Overview]] - API key and secret management
- [[../security/02_threat_models.md|Threat Models]] - Environment variable security threats
- [[../security/03_defense_layers.md|Defense Layers]] - Environment-based security controls
- [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]] - FERNET_KEY encryption integration
- [[../data/00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure]] - Data directory configuration
- [[../monitoring/01-logging-system.md|Logging System]] - LOG_LEVEL configuration
- [[../monitoring/08-metrics-collection.md|Metrics Collection]] - Telemetry environment settings
