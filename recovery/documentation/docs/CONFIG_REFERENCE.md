# Configuration Reference

**Sovereign Governance Substrate**  
Complete configuration options and environment variables

---

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Configuration Files](#configuration-files)
3. [Docker Configuration](#docker-configuration)
4. [Kubernetes Configuration](#kubernetes-configuration)
5. [Microservices Configuration](#microservices-configuration)
6. [Core Application Settings](#core-application-settings)
7. [Monitoring & Observability](#monitoring--observability)
8. [Security Settings](#security-settings)
9. [Quick Start Guide](#quick-start-guide)

---

## Environment Variables

### Required Variables (Production)

#### `OPENAI_API_KEY`

**Type**: String  
**Required**: Yes (if using OpenAI)  
**Default**: None  
**Description**: OpenAI API authentication key  
**Example**: `sk-proj-...`  
**Get Key**: https://platform.openai.com/api-keys

```bash
OPENAI_API_KEY=sk-proj-abc123xyz456...
```

#### `SECRET_KEY`

**Type**: String  
**Required**: Yes (production)  
**Default**: None  
**Description**: Application secret key for session encryption  
**Security**: Must be cryptographically random, minimum 32 bytes  
**Generate**: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

```bash
SECRET_KEY=abc123_random_secret_xyz789
```

#### `JWT_SECRET`

**Type**: String  
**Required**: Yes (if using JWT auth)  
**Default**: None  
**Description**: JWT token signing secret  
**Security**: Must be strong random string  
**Generate**: `python -c "import secrets; print(secrets.token_urlsafe(64))"`

```bash
JWT_SECRET=your_jwt_secret_key_here
```

#### `API_KEYS`

**Type**: Comma-separated strings  
**Required**: Yes (microservices)  
**Default**: None  
**Description**: API keys for service authentication  
**Example**: `key1,key2,key3`

```bash
API_KEYS=service_key_1,service_key_2,admin_key
```

---

### Optional Variables

#### `DEEPSEEK_API_KEY`

**Type**: String  
**Required**: No  
**Default**: None  
**Description**: DeepSeek API authentication key  
**Get Key**: https://platform.deepseek.com

```bash
DEEPSEEK_API_KEY=your_deepseek_key
```

#### `ENVIRONMENT`

**Type**: String  
**Required**: No  
**Default**: `development`  
**Options**: `development`, `staging`, `production`  
**Description**: Deployment environment identifier  
**Impact**: Affects logging, debug mode, validation strictness

```bash
ENVIRONMENT=production
```

#### `API_HOST`

**Type**: String (IP/hostname)  
**Required**: No  
**Default**: `0.0.0.0`  
**Description**: API server bind address  
**Note**: Use `0.0.0.0` to bind to all interfaces

```bash
API_HOST=0.0.0.0
```

#### `API_PORT`

**Type**: Integer  
**Required**: No  
**Default**: `8001`  
**Range**: 1024-65535  
**Description**: API server port

```bash
API_PORT=8001
```

#### `API_WORKERS`

**Type**: Integer  
**Required**: No  
**Default**: `4`  
**Range**: 1-32  
**Description**: Number of API worker processes  
**Recommendation**: Set to number of CPU cores

```bash
API_WORKERS=4
```

#### `LOG_LEVEL`

**Type**: String  
**Required**: No  
**Default**: `INFO`  
**Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`  
**Description**: Logging verbosity level

```bash
LOG_LEVEL=INFO
```

#### `AUDIT_LOG_PATH`

**Type**: String (file path)  
**Required**: No  
**Default**: `audit.log`  
**Description**: Path to audit log file

```bash
AUDIT_LOG_PATH=logs/audit.log
```

#### `DATABASE_URL`

**Type**: String (connection URL)  
**Required**: No (if using database)  
**Default**: None  
**Format**: `postgresql://user:[REDACTED]@host:port/db`  
**Description**: Database connection string

```bash
DATABASE_URL=postgresql://user:[REDACTED]@localhost:5432/dbname
```

#### `TEMPORAL_HOST`

**Type**: String (host:port)  
**Required**: No  
**Default**: `localhost:7233`  
**Description**: Temporal workflow server address

```bash
TEMPORAL_HOST=temporal-server:7233
```

#### `TEMPORAL_NAMESPACE`

**Type**: String  
**Required**: No  
**Default**: `default`  
**Description**: Temporal workflow namespace

```bash
TEMPORAL_NAMESPACE=project-ai
```

#### `CORS_ORIGINS`

**Type**: Comma-separated URLs  
**Required**: No  
**Default**: `http://localhost:3000,http://localhost:8000`  
**Description**: Allowed CORS origins  
**Security**: Restrict in production to specific domains

```bash

# Development

CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Production

CORS_ORIGINS=https://app.example.com,https://api.example.com
```

---

### Monitoring & Metrics

#### `ENABLE_METRICS`

**Type**: Boolean  
**Required**: No  
**Default**: `true`  
**Description**: Enable Prometheus metrics export

```bash
ENABLE_METRICS=true
```

#### `METRICS_PORT`

**Type**: Integer  
**Required**: No  
**Default**: `9090`  
**Description**: Prometheus metrics port

```bash
METRICS_PORT=9090
```

#### `ENABLE_TRACING`

**Type**: Boolean  
**Required**: No  
**Default**: `true`  
**Description**: Enable distributed tracing

```bash
ENABLE_TRACING=true
```

---

## Configuration Files

### Root Level

#### `pyproject.toml`

**Format**: TOML  
**Purpose**: Python project metadata and build configuration  
**Location**: Repository root

**Key Sections**:
```toml
[project]
name = "project-ai"
version = "1.0.1"
requires-python = ">=3.11"

[project.dependencies]

# Core dependencies listed here

[tool.ruff]

# Linter configuration

[tool.pytest.ini_options]

# Test configuration

```

#### `setup.cfg`

**Format**: INI  
**Purpose**: Tool configurations (flake8, isort, mypy, coverage)  
**Location**: Repository root

**Key Sections**:
```ini
[flake8]
max-line-length = 100

[isort]
profile = black

[mypy]
python_version = 3.11

[coverage:run]
source = .
```

#### `docker-compose.yml`

**Format**: YAML  
**Purpose**: Docker orchestration for local development  
**Location**: Repository root

**Services**:

- `project-ai` - Main application
- `prometheus` - Metrics collection
- `grafana` - Metrics visualization
- `temporal` - Workflow orchestration
- `temporal-postgresql` - Temporal database
- 7 emergent microservices

#### `.env` and `.env.example`

**Format**: ENV (key=value)  
**Purpose**: Environment variables  
**Location**: Repository root

**`.env`**: Local environment (git-ignored)  
**`.env.example`**: Template with documentation (committed)

---

### Config Directory (`config/`)

#### `config/settings.py`

**Format**: Python module  
**Purpose**: Centralized application settings  
**Pattern**: Class-based configuration with environment variable loading

**Key Classes**:
```python
class Config:
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8001"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Paths

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    
    @classmethod
    def get(cls, key: str, default=None):
        return getattr(cls, key, default)
```

**Usage**:
```python
from config.settings import Config

host = Config.API_HOST
port = Config.get("API_PORT", 8000)
```

#### `config/settings_manager.py`

**Format**: Python module  
**Purpose**: Comprehensive settings with God-tier encryption  
**Features**: Category-based settings, import/export, validation

**Settings Categories**:

- `general` - Language, theme, startup
- `privacy` - Encryption, data minimization
- `security` - Kill switch, VPN, firewalls
- `browser` - History, cache, cookies
- `ad_blocker` - Ad blocking configuration
- `consigliere` - AI assistant settings
- `media_downloader` - Media download settings
- `remote_access` - Remote access configuration
- `network` - VPN and network settings
- `firewalls` - 8-layer firewall config
- `support` - Support system settings
- `advanced` - Advanced tuning options

**Usage**:
```python
from config.settings_manager import SettingsManager

settings = SettingsManager(god_tier_encryption)
settings.set_setting("security", "kill_switch", True)
status = settings.get_status()
```

#### `config/god_tier_config.yaml`

**Format**: YAML  
**Purpose**: Multi-modal AI system configuration  
**Components**: Voice, visual, camera, conversation, policy, fusion

**Example**:
```yaml
deployment_mode: production
system_name: "God Tier Project-AI"

voice_model:
  enabled: true
  default_model: conversational
  bonding_enabled: true

camera:
  enabled: true
  resolution: [1280, 720]
  fps: 30

conversation:
  context_window: 10
  max_history_turns: 1000
  intent_detection: true
```

#### `config/defense_engine.toml`

**Format**: TOML  
**Purpose**: Zombie apocalypse defense engine configuration  
**Subsystems**: 10 functional domain subsystems

**Example**:
```toml
version = "1.0.0"

[security]
encryption_enabled = true
encryption_algorithm = "AES-256-GCM"
operational_mode = "normal"

[subsystems.situational_awareness]
priority = "CRITICAL"
enabled = true
auto_init = true
```

#### `config/mcp.json`

**Format**: JSON  
**Purpose**: MCP (Model Context Protocol) server configuration  
**Usage**: Claude Desktop integration

---

## Docker Configuration

### Environment Variables in Docker Compose

**Set via**:

1. `.env` file in repository root
2. `environment:` section in service
3. `env_file:` directive

**Example**:
```yaml
services:
  project-ai:
    environment:

      - PYTHONUNBUFFERED=1
      - PYTHONPATH=/app/src
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=development
    env_file:
      - .env

```

### Volume Mounts

**Configuration volumes**:
```yaml
volumes:

  - ./config:/app/config
  - ./data:/app/data
  - ./logs:/app/logs

```

### Port Mappings

| Service | Internal | External | Purpose |
|---------|----------|----------|---------|
| project-ai | 5000 | 5000 | Main app |
| project-ai | 8000 | 8000 | Metrics |
| prometheus | 9090 | 9090 | Prometheus UI |
| grafana | 3000 | 3000 | Grafana UI |
| temporal | 7233 | 7233 | Temporal gRPC |
| temporal | 8233 | 8233 | Temporal UI |

---

## Kubernetes Configuration

### ConfigMaps

#### Base ConfigMap (`k8s/base/configmap.yaml`)

**Non-sensitive configuration**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: project-ai-config
data:
  APP_ENV: "production"
  LOG_LEVEL: "INFO"
  API_HOST: "0.0.0.0"
  API_PORT: "5000"
  ENABLE_METRICS: "true"
```

#### Environment-Specific Patches

**Development** (`k8s/overlays/dev/configmap-patch.yaml`):
```yaml

- op: replace
  path: /data/APP_ENV
  value: "development"
- op: replace
  path: /data/LOG_LEVEL
  value: "DEBUG"

```

**Production** (`k8s/overlays/production/configmap-patch.yaml`):
```yaml

- op: replace
  path: /data/APP_ENV
  value: "production"
- op: replace
  path: /data/LOG_LEVEL
  value: "WARNING"

```

### Secrets

**Create from .env**:
```bash
kubectl create secret generic project-ai-secrets \
  --from-env-file=.env \
  --namespace=project-ai
```

**Reference in Pod**:
```yaml
envFrom:

  - secretRef:
      name: project-ai-secrets
  - configMapRef:
      name: project-ai-config

```

---

## Microservices Configuration

### Common Pattern (Pydantic Settings)

All emergent microservices use **Pydantic Settings** for type-safe configuration:

**File**: `app/config.py`

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    # Service Metadata

    SERVICE_NAME: str = "My Service"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")
    
    # Server

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security

    API_KEYS: List[str] = Field(default_factory=list)
    JWT_SECRET: str = Field(...)  # Required
    
    # Observability

    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

settings = Settings()
```

### Service-Specific Variables

#### Trust Graph Engine

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICE_NAME` | "Trust Graph Engine" | Service identifier |
| `PORT` | 8000 | Service port |
| `API_KEYS` | [] | API authentication keys |
| `RATE_LIMIT_PER_MINUTE` | 250 | Request rate limit |

#### AI Mutation Governance Firewall

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICE_NAME` | "AI Mutation Governance Firewall" | Service identifier |
| `PORT` | 8000 | Service port |
| `MUTATION_THRESHOLD` | 0.7 | Mutation detection threshold |

#### Sovereign Data Vault

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICE_NAME` | "Sovereign Data Vault" | Service identifier |
| `PORT` | 8000 | Service port |
| `ENCRYPTION_ALGORITHM` | "AES-256-GCM" | Vault encryption algorithm |

---

## Core Application Settings

### `src/app/core/config.py`

**Configuration Class**:
```python
class Config:

    # API Configuration

    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8001"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    
    # TARL Configuration

    TARL_VERSION: str = os.getenv("TARL_VERSION", "1.0")
    TARL_SIGNATURE_ALGORITHM: str = "SHA256"
    
    # Logging

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "audit.log")
    
    # Security

    ENABLE_CORS: bool = True
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Paths

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
```

### `kernel/config.py`

**Features**:

- Hierarchical configuration (YAML/TOML/JSON)
- Hot-reload without restart
- Schema validation
- Environment variable override
- Change audit trail

**Usage**:
```python
from kernel.config import ConfigurationManager

config_mgr = ConfigurationManager(config_dir="./config")
config_mgr.load_file("defense_engine.toml")

value = config_mgr.get("subsystems.situational_awareness.enabled")
config_mgr.set("security.encryption_enabled", True)
```

---

## Monitoring & Observability

### Prometheus Configuration

**File**: `config/prometheus/prometheus.yml`

**Scrape Configs**:
```yaml
scrape_configs:

  - job_name: 'project-ai'
    static_configs:
      - targets: ['project-ai:8000']
  
  - job_name: 'microservices'
    static_configs:
      - targets:
        - 'mutation-firewall:8000'
        - 'trust-graph:8000'
        - 'data-vault:8000'

```

### Grafana Configuration

**File**: `config/grafana/provisioning/datasources/prometheus.yml`

**Datasource**:
```yaml
datasources:

  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy

```

### Alertmanager Configuration

**File**: `config/alertmanager/alertmanager.yml`

**Alert Routes**:
```yaml
route:
  receiver: 'default'
  routes:

    - match:
        severity: critical
      receiver: 'critical-alerts'

```

---

## Security Settings

### Encryption Configuration

**God-Tier Encryption** (from `settings_manager.py`):
```python
"privacy": {
    "god_tier_encryption": True,
    "encryption_layers": 7,
    "quantum_resistant": True,
    "perfect_forward_secrecy": True,
}
```

### Firewall Configuration

**8-Layer Firewall System**:
```python
"firewalls": {
    "packet_filtering": {"enabled": True, "mode": "strict"},
    "circuit_level": {"enabled": True},
    "stateful_inspection": {"enabled": True},
    "proxy": {"enabled": True},
    "next_generation": {"enabled": True, "ai_powered": True},
    "software": {"enabled": True},
    "hardware": {"enabled": True},
    "cloud": {"enabled": True},
}
```

### VPN Configuration

**Multi-Hop VPN**:
```python
"network": {
    "vpn_enabled": True,
    "vpn_hops": 3,
    "max_hops": 5,
    "stealth_mode": True,
    "dns_over_https": True,
}
```

---

## Quick Start Guide

### 1. Initial Setup

```bash

# Clone repository

git clone <repo-url>
cd Sovereign-Governance-Substrate

# Copy environment template

cp .env.example .env

# Edit .env with your values

nano .env
```

### 2. Required Environment Variables

**Minimum .env for development**:
```bash

# AI APIs

OPENAI_API_KEY=sk-proj-your-key-here

# Security

SECRET_KEY=your-secret-key-generate-with-python
JWT_SECRET=your-jwt-secret-generate-with-python

# Application

ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 3. Generate Secrets

```bash

# Generate SECRET_KEY

python -c "import secrets; print('SECRET_KEY='[REDACTED]"

# Generate JWT_SECRET

python -c "import secrets; print('JWT_SECRET='[REDACTED]"
```

### 4. Start with Docker Compose

```bash

# Start all services

docker-compose up -d

# View logs

docker-compose logs -f project-ai

# Stop services

docker-compose down
```

### 5. Validate Configuration

```bash

# Run configuration validator

python config_validator.py

# Check for issues

python config_validator.py --fail-on-error
```

### 6. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Main App | http://localhost:5000 | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Temporal UI | http://localhost:8233 | - |

---

## Configuration Validation

### Run Validator

```bash

# Basic validation

python config_validator.py

# Fail on errors (CI/CD)

python config_validator.py --fail-on-error

# Save report

python config_validator.py --output validation_report.txt
```

### Common Issues

#### Missing Environment Variables

**Error**: "Required environment variable not set"  
**Fix**: Add to `.env` file

#### Hardcoded Secrets

**Error**: "Potential hardcoded SECRET detected"  
**Fix**: Move to environment variable

#### Invalid Syntax

**Error**: "Failed to parse YAML file"  
**Fix**: Check YAML syntax with linter

#### Production Defaults

**Error**: "JWT_SECRET uses default value in production"  
**Fix**: Set environment variable from secrets manager

---

## Environment-Specific Configuration

### Development

**Characteristics**:

- Debug logging enabled
- Relaxed CORS
- Local services
- Test data allowed

**Setup**:
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=*
```

### Staging

**Characteristics**:

- Production-like environment
- Limited debug logging
- Restricted CORS
- Test data allowed

**Setup**:
```bash
ENVIRONMENT=staging
LOG_LEVEL=INFO
CORS_ORIGINS=https://staging.example.com
```

### Production

**Characteristics**:

- Minimal logging
- Strict security
- No debug mode
- Performance optimized

**Setup**:
```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
CORS_ORIGINS=https://app.example.com,https://api.example.com
DEBUG=false
```

**Validation**: Production configs must pass:

- No debug mode enabled
- No default secrets
- Restricted CORS
- Strong encryption
- Rate limiting enabled

---

## Troubleshooting

### Configuration Not Loading

**Check**:

1. File exists and has correct permissions
2. Syntax is valid (YAML/JSON/TOML)
3. Environment variables are set
4. File is in correct location

### Environment Variables Not Applied

**Check**:

1. `.env` file exists
2. Variables are exported (if not using docker-compose)
3. No typos in variable names
4. Service has been restarted

### Docker Compose Issues

**Check**:

1. `.env` file in same directory as `docker-compose.yml`
2. Environment variable syntax: `${VAR_NAME}`
3. Restart containers after .env changes: `docker-compose down && docker-compose up -d`

### Kubernetes ConfigMap Not Applied

**Check**:

1. ConfigMap exists: `kubectl get configmap -n project-ai`
2. Pod references correct ConfigMap
3. Restart pods: `kubectl rollout restart deployment/project-ai -n project-ai`

---

## Best Practices

### ✅ DO

- Use environment variables for all secrets
- Keep `.env` in `.gitignore`
- Document all config options
- Validate configs before deployment
- Use type-safe configs (Pydantic)
- Implement config hot-reload where possible
- Version control `.env.example`
- Use different secrets per environment

### ❌ DON'T

- Commit `.env` to git
- Hardcode secrets in config files
- Use same secrets in dev/prod
- Ignore config validation errors
- Use `CORS_ORIGINS=*` in production
- Enable debug mode in production
- Store passwords in plain text

---

## Additional Resources

- **Architecture Report**: See `CONFIGURATION_ARCHITECTURE_REPORT.md`
- **Validator Script**: Run `config_validator.py`
- **Docker Docs**: https://docs.docker.com/compose/
- **Kubernetes ConfigMaps**: https://kubernetes.io/docs/concepts/configuration/configmap/
- **Pydantic Settings**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

---

**Document Version**: 1.0  
**Last Updated**: 2026-04-10  
**Maintained By**: Configuration Architect
