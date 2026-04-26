# Environment Manager System Relationships

**System:** Environment Manager  
**Core Files:**
- `.env` [[.env]] - Production secrets and API keys
- `.env.example` - Template with documentation
- `src/app/core/user_manager.py` [[src/app/core/user_manager.py]] - Fernet key loading
- `src/app/security/environment_hardening.py` [[src/app/security/environment_hardening.py]] - Environment validation
- Environment variable consumers (27+ files)

**Last Updated:** 2025-04-20  
**Mission:** AGENT-065 Configuration Systems Relationship Mapping

---


## Navigation

**Location**: `relationships\configuration\02_environment_manager_relationships.md`

**Parent**: [[relationships\configuration\README.md]]


## Architecture Overview

Project-AI uses **environment variables** for:
1. **Secrets Management**: API keys, encryption keys, bearer tokens
2. **Runtime Configuration**: Server ports, hostnames, debug flags
3. **Service Endpoints**: Temporal, database, external APIs
4. **Feature Flags**: Implicit (via API key presence)

---

## Environment Variable Categories

### 1. API Keys & Secrets

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...           # Required for GPT models, DALL-E
OPENAI_ORG_ID=org-...           # Optional organization ID

# DeepSeek Configuration
DEEPSEEK_API_KEY=sk-...         # Required for DeepSeek models

# Security Keys
SECRET_KEY=<urlsafe-token>      # Generated via secrets.token_urlsafe(32)
FERNET_KEY=<base64-key>         # Generated via Fernet.generate_key()

# MCP Integration
WIKI_TASKS_BEARER_TOKEN=<token> # Bearer token for wiki-tasks MCP server
```

### 2. Service Configuration

```bash
# API Server
API_HOST=0.0.0.0                # Bind address (default: 0.0.0.0)
API_PORT=8001                   # Port number (default: 8001)
API_WORKERS=4                   # Worker processes
ENVIRONMENT=development         # development | production

# Temporal Workflow
TEMPORAL_HOST=localhost:7233    # Temporal server address
TEMPORAL_NAMESPACE=default      # Temporal namespace

# Database
DATABASE_URL=<connection-string> # Optional database connection

# MCP Server
WIKI_TASKS_MCP_PORT=7777        # Local MCP endpoint port
```

### 3. Audit & Logging

```bash
AUDIT_LOG_PATH=audit.log        # Audit log file path
LOG_LEVEL=INFO                  # DEBUG|INFO|WARNING|ERROR|CRITICAL
```

### 4. Security Settings

```bash
# CORS Configuration
CORS_ORIGINS=http://localhost:8000,http://localhost:3000

# TARL Signature
TARL_VERSION=1.0
```

### 5. CLI Config Overrides (PROJECTAI_* prefix)

```bash
# Override any CLI config value
PROJECTAI_GENERAL_LOG_LEVEL=DEBUG
PROJECTAI_AI_MODEL=gpt-4
PROJECTAI_SECURITY_ENABLE_FOUR_LAWS=true
```

---

## Environment Loading Flow

```
Application Startup
    ↓
┌─────────────────────────────────────────┐
│  dotenv.load_dotenv()                   │
│  - Searches for .env in current dir     │
│  - Loads variables into os.environ      │
│  - Does NOT override existing env vars  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Component Initialization               │
│  - UserManager: loads FERNET_KEY        │
│  - Config: loads API_*, TARL_*, etc.    │
│  - CLI Config: reads PROJECTAI_*        │
│  - Intelligence Engine: loads OPENAI_*  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Environment Hardening (optional)       │
│  - Validates virtualenv                 │
│  - Checks sys.path security             │
│  - Verifies ASLR/SSP                    │
└─────────────────────────────────────────┘
```

---

## Key Environment Variable Consumers

### File: `src/app/core/user_manager.py` [[src/app/core/user_manager.py]]

```python
def _setup_cipher(self):
    """Setup Fernet cipher from environment or generate new key."""
    load_dotenv()  # Ensures .env is loaded
    env_key = os.getenv("FERNET_KEY")
    if env_key:
        try:
            key = env_key.encode()
            self.cipher_suite = Fernet(key)
        except Exception:
            # Fallback to runtime key
            self.cipher_suite = Fernet(Fernet.generate_key())
    else:
        # No env key, generate runtime-only key
        self.cipher_suite = Fernet(Fernet.generate_key())
```

**Pattern**: Graceful degradation - uses env key if present, generates runtime key otherwise.

### File: `config/settings.py`

```python
class Config:
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8001"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    
    # String parsing
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:8000"
    ).split(",")
```

**Pattern**: Direct `os.getenv()` with inline defaults and type conversion.

### File: `src/app/core/config.py` [[src/app/core/config.py]]

```python
def _apply_env_overrides(self) -> None:
    """Apply environment variable overrides with PROJECTAI_ prefix."""
    prefix = "PROJECTAI_"
    for key, value in os.environ.items():
        if key.startswith(prefix):
            parts = key[len(prefix):].lower().split("_", 1)
            if len(parts) == 2:
                section, config_key = parts
                # Type preservation
                if isinstance(original_value, bool):
                    value = value.lower() in ("true", "1", "yes")
                elif isinstance(original_value, int):
                    value = int(value)
                self.config[section][config_key] = value
```

**Pattern**: Prefixed namespace with automatic type conversion.

### File: `src/app/temporal/config.py` [[src/app/temporal/config.py]]

```python
class TemporalConfig(BaseSettings):
    """Pydantic-based config with environment loading."""
    
    host: str = Field(default="localhost:7233", description="Temporal server address")
    namespace: str = Field(default="default", description="Temporal namespace")
    
    class Config:
        env_prefix = "TEMPORAL_"      # Reads TEMPORAL_HOST, TEMPORAL_NAMESPACE
        env_file = ".env.temporal"    # Additional env file
        env_file_encoding = "utf-8"
        case_sensitive = False
```

**Pattern**: Pydantic BaseSettings with automatic env parsing and validation.

---

## Environment Hardening

### File: `src/app/security/environment_hardening.py` [[src/app/security/environment_hardening.py]]

```python
class EnvironmentHardening:
    """Security validation for deployment environment."""
    
    def validate_environment(self) -> tuple[bool, list[str]]:
        """Run comprehensive environment validation."""
        issues = []
        
        # 1. Virtualenv check
        if not self._check_virtualenv():
            issues.append("Not running in virtualenv - security risk")
        
        # 2. sys.path validation
        path_issues = self._validate_sys_path()
        issues.extend(path_issues)
        
        # 3. ASLR/SSP verification
        if not self._check_aslr_ssp():
            issues.append("ASLR/SSP not fully enabled")
        
        # 4. Directory permissions
        perm_issues = self._validate_directory_permissions()
        issues.extend(perm_issues)
        
        return len(issues) == 0, issues
```

#### Checks Performed

| Check | Purpose | Security Impact |
|-------|---------|----------------|
| **Virtualenv Detection** | Ensures isolated Python environment | Prevents system-wide dependency conflicts |
| **sys.path Validation** | Checks for suspicious path entries | Mitigates Python import hijacking |
| **ASLR/SSP Verification** | Validates memory protection | Hardens against buffer overflow attacks |
| **Directory Permissions** | Ensures secure file access (0600/0700) | Prevents unauthorized data access |

---

## Relationships to Other Systems

### 1. Config Loader ← Environment Manager

```python
# src/app/core/config.py
def _apply_env_overrides(self) -> None:
    """Environment variables OVERRIDE all config file settings."""
    # Priority: ENV > Project Config > User Config > Defaults
```

**Direction**: Environment provides highest-priority overrides.

### 2. Secrets Management ← Environment Manager

> **Security Integration**: Environment secrets follow [[../security/01_security_system_overview.md|Security System Overview]] and [[../security/02_threat_models.md|Threat Models]]

```python
# src/app/core/user_manager.py
env_key = os.getenv("FERNET_KEY")  # Encryption key from environment → [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]]

# src/app/core/image_generator.py
openai_key = os.getenv("OPENAI_API_KEY")  # API key from environment → [[../security/03_defense_layers.md|Defense Layers]]
```

**Direction**: Environment is the **source of truth** for secrets.

### 3. Feature Flags ← Environment Manager (Implicit)

```python
# Presence of API key enables features
if os.getenv("OPENAI_API_KEY"):
    # OpenAI features enabled
    
if os.getenv("DEEPSEEK_API_KEY"):
    # DeepSeek features enabled
```

**Direction**: Environment **implicitly controls** feature availability.

### 4. Environment Manager → Settings Validator

```python
# Temporal config validates env values via Pydantic
class TemporalConfig(BaseSettings):
    max_concurrent_activities: int = Field(default=50, ge=1)
    # Pydantic validates type and constraints
```

**Direction**: Environment values **pass through** validation layer.

---

## Environment Variable Precedence

```
┌─────────────────────────────────────────┐
│  1. System Environment Variables        │  ← HIGHEST
│     (set via OS, docker, shell)         │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  2. .env File (dotenv)                  │  ← Loaded if not already set
│     (via load_dotenv())                 │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  3. .env.temporal (Pydantic)            │  ← Component-specific env files
│     (via BaseSettings.Config.env_file)  │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  4. Config File Defaults                │  ← Only if env var missing
│     (TOML/YAML defaults)                │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  5. Hardcoded Defaults                  │  ← LOWEST
│     (Config.DEFAULTS, field defaults)   │
└─────────────────────────────────────────┘
```

---

## Security Best Practices

> **Environment Hardening**: See [[../security/03_defense_layers.md|Defense Layers]] for comprehensive environment security

### ✅ What Project-AI Does Well

1. **Separates Secrets from Code**: API keys in `.env` [[.env]], not hardcoded → [[../security/02_threat_models.md|Threat Models]]
2. **Provides Example File**: `.env.example` documents all variables
3. **Graceful Degradation**: Components work without optional env vars (e.g., FERNET_KEY) → [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]]
4. **Environment Validation**: `EnvironmentHardening` checks security posture → [[../security/01_security_system_overview.md|Security Overview]]
5. **Gitignore Protection**: `.env` [[.env]] is gitignored

### ⚠️ Security Gaps

1. **No Permission Checks on .env**: File permissions not validated → [[../security/03_defense_layers.md|Defense Layers]]
2. **No Secrets Rotation**: No automated key rotation mechanism → [[../security/07_security_metrics.md|Security Metrics]]
3. **No Environment Encryption**: .env stored in plaintext → [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]]
4. **No Mixed Secret Storage**: Some secrets in env, some in config files
5. **Logging Risk**: API keys might appear in debug logs → [[../monitoring/01-logging-system.md|Logging System]]

---

## Environment Files Structure

```
Project-AI/
├── .env                          # Production secrets (NEVER commit)
├── .env.example                  # Template with all variables
├── web/.env.example              # Web-specific template
├── desktop/.env.example          # Desktop-specific template
├── config/examples/
│   ├── .env.example              # General example
│   └── .env.temporal.example     # Temporal-specific example
└── src/app/temporal/
    └── config.py                 # Reads .env.temporal
```

---

## Environment Variable Validation Matrix

| Variable | Required | Type | Validated By | Default |
|----------|----------|------|--------------|---------|
| `OPENAI_API_KEY` | Optional | String | None | None |
| `FERNET_KEY` | Optional | Base64 | Fernet constructor | Generated |
| `API_PORT` | Optional | Integer | `int()` cast | 8001 |
| `TEMPORAL_HOST` | Optional | String | Pydantic | localhost:7233 |
| `TEMPORAL_MAX_CONCURRENT_ACTIVITIES` | Optional | Integer (≥1) | Pydantic Field | 50 |
| `PROJECTAI_GENERAL_LOG_LEVEL` | Optional | String | None | INFO |

---

## Integration Patterns

### Pattern 1: Direct Access (Simple)
```python
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY")
```

### Pattern 2: Class Attribute (API Config)
```python
class Config:
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
```

### Pattern 3: Pydantic BaseSettings (Temporal)
```python
class TemporalConfig(BaseSettings):
    host: str = Field(default="localhost:7233")
    class Config:
        env_prefix = "TEMPORAL_"
```

### Pattern 4: Prefixed Override (CLI Config)
```python
# PROJECTAI_SECTION_KEY → config["section"]["key"]
for key, value in os.environ.items():
    if key.startswith("PROJECTAI_"):
        # Parse and apply
```

---

## Data Flow: Environment Variable → Runtime Value

```
.env File
    ↓
[load_dotenv()] ────> os.environ
    ↓                     ↓
Component Reads:     Validation:
- os.getenv()        - Type casting
- Config class       - Pydantic
- BaseSettings       - Custom checks
    ↓
Runtime Configuration Value
```

---

## Related Systems

### Configuration Systems
- [Config Loader](./01_config_loader_relationships.md)
- [Secrets Management](./07_secrets_management_relationships.md)
- [Settings Validator](./03_settings_validator_relationships.md)
- [Feature Flags](./04_feature_flags_relationships.md)
- [Override Hierarchy](./09_override_hierarchy_relationships.md)

### Cross-System Dependencies
- [[../security/01_security_system_overview.md|Security System Overview]] - Environment hardening and validation
- [[../security/02_threat_models.md|Threat Models]] - API key security and threat modeling
- [[../security/03_defense_layers.md|Defense Layers]] - Environment-based defense mechanisms
- [[../security/07_security_metrics.md|Security Metrics]] - Environment security audit logging
- [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]] - FERNET_KEY encryption integration
- [[../data/04-BACKUP-RECOVERY.md|Backup & Recovery]] - Environment backup strategies
- [[../monitoring/01-logging-system.md|Logging System]] - LOG_LEVEL and audit configuration
