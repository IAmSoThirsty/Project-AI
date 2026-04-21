# Configuration Management and Environment Setup

## Overview

Project-AI requires comprehensive configuration management across multiple deployment environments (development, staging, production) and platforms (desktop, web, mobile, containers). This document covers environment variables, configuration files, secrets management, and environment-specific settings.

## Configuration Architecture

### Multi-Layer Configuration Hierarchy

```
Configuration Layers (precedence: bottom → top)/
├── 1. Default Values (hardcoded in code)
│   └── src/app/core/config.py: DEFAULT_CONFIG
├── 2. Configuration Files (committed to Git)
│   ├── config/default.json
│   ├── config/development.json
│   ├── config/production.json
│   └── pyproject.toml
├── 3. Environment Files (.env, NOT committed)
│   ├── .env (root)
│   ├── .env.development
│   ├── .env.production
│   └── .env.local (overrides all)
├── 4. Environment Variables (OS-level)
│   └── export OPENAI_API_KEY=sk-...
└── 5. CLI Arguments/Flags (highest priority)
    └── --config-file custom.json
```

**Priority**: CLI args > Env vars > .env files > config files > defaults

## Environment Variable Management

### Root .env File

**Location**: `.env` [[.env]] (root directory)

**Template** (`.env.example`):
```bash
# ===== OpenAI Integration =====
OPENAI_API_KEY=sk-your-key-here
OPENAI_ORG_ID=org-your-org-here
OPENAI_MODEL=gpt-4

# ===== HuggingFace Integration =====
HUGGINGFACE_API_KEY=hf_your-key-here

# ===== Encryption =====
FERNET_KEY=your-fernet-key-base64

# ===== Database (Web) =====
DATABASE_URL=postgresql://user:pass@localhost:5432/legion_web
# Development: sqlite:///legion_web_dev.db
# Production: postgresql://...

# ===== Redis (Caching) =====
REDIS_URL=redis://localhost:6379/0

# ===== Email Alerts (Optional) =====
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@projectai.com

# ===== Flask (Web Backend) =====
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_APP=app.py

# ===== React (Web Frontend) =====
VITE_API_URL=http://localhost:5000/api

# ===== Security =====
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
JWT_SECRET_KEY=your-jwt-secret-here
JWT_EXPIRATION_HOURS=24

# ===== Feature Flags =====
ENABLE_IMAGE_GENERATION=true
ENABLE_LEARNING_REQUESTS=true
ENABLE_LOCATION_TRACKING=false
ENABLE_EMERGENCY_ALERTS=false

# ===== Logging =====
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
ENABLE_FILE_LOGGING=true
ENABLE_CONSOLE_LOGGING=true

# ===== Rate Limiting =====
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# ===== Application Settings =====
APP_NAME=Project AI
APP_VERSION=1.0.0
APP_ENV=development
DATA_DIR=data
```

### Loading Environment Variables

**Python** (`src/app/core/config.py` [[src/app/core/config.py]]):

```python
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file
env_path = Path(__file__).resolve().parents[3] / '.env'
load_dotenv(dotenv_path=env_path)

# Also load environment-specific .env
env = os.getenv('APP_ENV', 'development')
env_specific_path = Path(__file__).resolve().parents[3] / f'.env.{env}'
if env_specific_path.exists():
    load_dotenv(dotenv_path=env_specific_path, override=True)

# Load .env.local (overrides everything, never commit)
local_path = Path(__file__).resolve().parents[3] / '.env.local'
if local_path.exists():
    load_dotenv(dotenv_path=local_path, override=True)

class Config:
    """Application configuration."""
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ORG_ID = os.getenv('OPENAI_ORG_ID')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # HuggingFace
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    
    # Encryption
    FERNET_KEY = os.getenv('FERNET_KEY')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///legion_web_dev.db')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Email
    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_FROM = os.getenv('SMTP_FROM', 'noreply@projectai.com')
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Feature Flags
    ENABLE_IMAGE_GENERATION = os.getenv('ENABLE_IMAGE_GENERATION', 'true').lower() == 'true'
    ENABLE_LEARNING_REQUESTS = os.getenv('ENABLE_LEARNING_REQUESTS', 'true').lower() == 'true'
    ENABLE_LOCATION_TRACKING = os.getenv('ENABLE_LOCATION_TRACKING', 'false').lower() == 'true'
    ENABLE_EMERGENCY_ALERTS = os.getenv('ENABLE_EMERGENCY_ALERTS', 'false').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    ENABLE_FILE_LOGGING = os.getenv('ENABLE_FILE_LOGGING', 'true').lower() == 'true'
    ENABLE_CONSOLE_LOGGING = os.getenv('ENABLE_CONSOLE_LOGGING', 'true').lower() == 'true'
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '1000'))
    
    # Application
    APP_NAME = os.getenv('APP_NAME', 'Project AI')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    APP_ENV = os.getenv('APP_ENV', 'development')
    DATA_DIR = os.getenv('DATA_DIR', 'data')
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        errors = []
        
        # Check required API keys (production only)
        if cls.APP_ENV == 'production':
            if not cls.OPENAI_API_KEY:
                errors.append("OPENAI_API_KEY not set")
            if not cls.FERNET_KEY:
                errors.append("FERNET_KEY not set")
            if cls.SECRET_KEY == 'dev-secret-key':
                errors.append("SECRET_KEY must be set in production")
        
        # Check database URL format
        if cls.DATABASE_URL and not (
            cls.DATABASE_URL.startswith('sqlite://') or
            cls.DATABASE_URL.startswith('postgresql://') or
            cls.DATABASE_URL.startswith('mysql://')
        ):
            errors.append("DATABASE_URL has invalid format")
        
        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    
    @classmethod
    def to_dict(cls):
        """Export config as dictionary (for logging, exclude secrets)."""
        safe_config = {}
        for key, value in cls.__dict__.items():
            if not key.startswith('_') and key.isupper():
                # Mask sensitive values
                if 'KEY' in key or 'PASSWORD' in key or 'SECRET' in key:
                    safe_config[key] = '***REDACTED***' if value else None
                else:
                    safe_config[key] = value
        return safe_config

# Validate on import (fail fast)
Config.validate()
```

**Usage**:
```python
from app.core.config import Config

# Access configuration
api_key = Config.OPENAI_API_KEY
log_level = Config.LOG_LEVEL

# Feature flag check
if Config.ENABLE_IMAGE_GENERATION:
    # Enable image generation feature
    pass
```

### TypeScript/React (.env)

**Location**: `web/frontend/.env`

```bash
# Vite environment variables (prefix with VITE_)
VITE_API_URL=http://localhost:5000/api
VITE_WS_URL=ws://localhost:5000/ws
VITE_APP_NAME=Project AI
VITE_APP_VERSION=1.0.0
VITE_ENABLE_ANALYTICS=false
```

**Loading** (`web/frontend/src/config.ts`):
```typescript
export const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:5000/ws',
  appName: import.meta.env.VITE_APP_NAME || 'Project AI',
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
  enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true'
}
```

### Android (gradle.properties)

**Location**: `android/gradle.properties`

```properties
# SDK paths
android.useAndroidX=true
android.enableJetifier=true

# Build optimizations
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
org.gradle.parallel=true
org.gradle.caching=true

# API endpoints
API_BASE_URL=http://10.0.2.2:8001
# Note: 10.0.2.2 is Android emulator's host machine
```

**Load in build.gradle**:
```gradle
android {
    defaultConfig {
        buildConfigField "String", "API_BASE_URL", "\"${project.findProperty('API_BASE_URL') ?: 'http://localhost:8001'}\""
    }
}
```

**Access in code**:
```java
String apiUrl = BuildConfig.API_BASE_URL;
```

## Environment-Specific Configuration

### Development Environment

**File**: `.env.development`

```bash
APP_ENV=development
LOG_LEVEL=DEBUG
ENABLE_FILE_LOGGING=true
ENABLE_CONSOLE_LOGGING=true

# Use local SQLite
DATABASE_URL=sqlite:///legion_web_dev.db

# No Redis (use in-memory cache)
REDIS_URL=

# Relaxed CORS
CORS_ORIGINS=*

# Disable SSL verification (local testing)
PYTHONHTTPSVERIFY=0

# Enable all features for testing
ENABLE_IMAGE_GENERATION=true
ENABLE_LEARNING_REQUESTS=true
ENABLE_LOCATION_TRACKING=true
ENABLE_EMERGENCY_ALERTS=true
```

### Staging Environment

**File**: `.env.staging`

```bash
APP_ENV=staging
LOG_LEVEL=INFO

# PostgreSQL (staging)
DATABASE_URL=postgresql://stageuser:stagepass@staging-db:5432/legion_web_staging

# Redis (staging)
REDIS_URL=redis://staging-redis:6379/0

# Staging API keys (limited quota)
OPENAI_API_KEY=sk-staging-...
HUGGINGFACE_API_KEY=hf_staging-...

# Restricted CORS
CORS_ORIGINS=https://staging.projectai.com

# Enable most features
ENABLE_IMAGE_GENERATION=true
ENABLE_LEARNING_REQUESTS=true
ENABLE_LOCATION_TRACKING=false  # Privacy concern
ENABLE_EMERGENCY_ALERTS=false   # Not tested yet
```

### Production Environment

**File**: `.env.production` (NOT committed, deployed via secrets)

```bash
APP_ENV=production
LOG_LEVEL=WARNING

# PostgreSQL (production)
DATABASE_URL=postgresql://produser:$STRONG_PASSWORD@prod-db:5432/legion_web

# Redis (production cluster)
REDIS_URL=redis://prod-redis:6379/0

# Production API keys
OPENAI_API_KEY=$OPENAI_PROD_KEY
HUGGINGFACE_API_KEY=$HF_PROD_KEY

# Strong secrets
SECRET_KEY=$SECRET_KEY_256BIT
JWT_SECRET_KEY=$JWT_SECRET_256BIT
FERNET_KEY=$FERNET_KEY_BASE64

# Production domains
CORS_ORIGINS=https://projectai.com,https://www.projectai.com

# Strict rate limiting
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=500

# Enable only tested features
ENABLE_IMAGE_GENERATION=true
ENABLE_LEARNING_REQUESTS=true
ENABLE_LOCATION_TRACKING=false
ENABLE_EMERGENCY_ALERTS=false
```

## Configuration File Management

### Structured Configuration (JSON)

**Location**: `config/default.json`

```json
{
  "app": {
    "name": "Project AI",
    "version": "1.0.0",
    "description": "Personal AI Assistant"
  },
  "ai_systems": {
    "persona": {
      "default_traits": {
        "curiosity": 7,
        "helpfulness": 9,
        "humor": 5,
        "formality": 4,
        "verbosity": 6,
        "creativity": 8,
        "caution": 7,
        "empathy": 8
      },
      "mood_decay_rate": 0.1,
      "interaction_boost": 0.05
    },
    "four_laws": {
      "enabled": true,
      "strict_mode": false,
      "log_violations": true
    },
    "memory": {
      "max_conversations": 1000,
      "max_knowledge_entries": 5000,
      "auto_cleanup_days": 30
    },
    "learning": {
      "auto_approve": false,
      "black_vault_enabled": true,
      "fingerprint_algorithm": "sha256"
    }
  },
  "image_generation": {
    "default_backend": "huggingface",
    "default_style": "photorealistic",
    "default_size": "512x512",
    "content_filter_enabled": true,
    "max_history": 100
  },
  "location_tracking": {
    "enabled": false,
    "encryption_enabled": true,
    "max_history": 1000,
    "cleanup_after_days": 90
  },
  "security": {
    "password_min_length": 8,
    "password_require_uppercase": true,
    "password_require_lowercase": true,
    "password_require_digit": true,
    "password_require_special": true,
    "max_login_attempts": 5,
    "lockout_duration_minutes": 15,
    "bcrypt_rounds": 12
  },
  "data_persistence": {
    "auto_save_interval_seconds": 60,
    "backup_enabled": true,
    "backup_interval_hours": 24,
    "max_backups": 7
  }
}
```

**Loading** (`src/app/core/config.py` [[src/app/core/config.py]]):

```python
import json
from pathlib import Path

def load_config_file(env='default'):
    """Load JSON configuration file."""
    config_path = Path(__file__).resolve().parents[3] / 'config' / f'{env}.json'
    
    if not config_path.exists():
        config_path = Path(__file__).resolve().parents[3] / 'config' / 'default.json'
    
    with open(config_path, 'r') as f:
        return json.load(f)

# Merge with environment-specific overrides
base_config = load_config_file('default')
env = os.getenv('APP_ENV', 'development')
env_config = load_config_file(env)

# Deep merge
import copy
config_data = copy.deepcopy(base_config)

def deep_merge(base, override):
    """Recursively merge override into base."""
    for key, value in override.items():
        if isinstance(value, dict) and key in base:
            deep_merge(base[key], value)
        else:
            base[key] = value

deep_merge(config_data, env_config)
```

## Secrets Management

### Encryption Key Generation

**Fernet Key**:
```python
from cryptography.fernet import Fernet

# Generate new key
key = Fernet.generate_key()
print(key.decode())  # Copy to .env
```

**Secret Key (Flask)**:
```python
import secrets

# Generate 32-byte (256-bit) secret key
secret_key = secrets.token_urlsafe(32)
print(secret_key)  # Copy to .env
```

**JWT Secret**:
```python
import secrets
import base64

# Generate strong JWT secret
jwt_secret = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
print(jwt_secret)  # Copy to .env
```

### Secrets Rotation

**Script** (`scripts/rotate_secrets.py`):

```python
import os
import secrets
from cryptography.fernet import Fernet
from dotenv import load_dotenv, set_key

def rotate_secrets(env_file='.env'):
    """Rotate all secrets in .env file."""
    load_dotenv(env_file)
    
    # Generate new secrets
    new_fernet_key = Fernet.generate_key().decode()
    new_secret_key = secrets.token_urlsafe(32)
    new_jwt_secret = secrets.token_urlsafe(32)
    
    # Update .env file
    set_key(env_file, 'FERNET_KEY', new_fernet_key)
    set_key(env_file, 'SECRET_KEY', new_secret_key)
    set_key(env_file, 'JWT_SECRET_KEY', new_jwt_secret)
    
    print("Secrets rotated successfully!")
    print(f"FERNET_KEY: {new_fernet_key}")
    print(f"SECRET_KEY: {new_secret_key}")
    print(f"JWT_SECRET_KEY: {new_jwt_secret}")
    print("\n⚠️  WARNING: You must:")
    print("  1. Re-encrypt all existing data with new FERNET_KEY")
    print("  2. Invalidate all existing JWT tokens")
    print("  3. Users will need to re-login")

if __name__ == '__main__':
    rotate_secrets()
```

**Usage**:
```bash
python scripts/rotate_secrets.py
```

### Secrets Validation

**Script** (`scripts/validate_secrets.py`):

```python
import os
import re
from dotenv import load_dotenv

def validate_secrets(env_file='.env'):
    """Validate .env file for security issues."""
    load_dotenv(env_file)
    
    issues = []
    
    # Check for weak secrets
    secret_key = os.getenv('SECRET_KEY', '')
    if len(secret_key) < 32:
        issues.append("SECRET_KEY too short (min 32 characters)")
    if secret_key == 'dev-secret-key':
        issues.append("SECRET_KEY is default value (change for production)")
    
    # Check for weak Fernet key
    fernet_key = os.getenv('FERNET_KEY', '')
    if fernet_key and len(fernet_key) != 44:
        issues.append("FERNET_KEY invalid length (should be 44 characters)")
    
    # Check for placeholder API keys
    openai_key = os.getenv('OPENAI_API_KEY', '')
    if openai_key and not openai_key.startswith('sk-'):
        issues.append("OPENAI_API_KEY invalid format")
    
    hf_key = os.getenv('HUGGINGFACE_API_KEY', '')
    if hf_key and not hf_key.startswith('hf_'):
        issues.append("HUGGINGFACE_API_KEY invalid format")
    
    # Check for sensitive data in plain text
    db_url = os.getenv('DATABASE_URL', '')
    if 'password' in db_url.lower() and ':password@' in db_url.lower():
        issues.append("DATABASE_URL contains literal 'password' (use real password)")
    
    # Report results
    if issues:
        print("❌ Validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All secrets valid!")
        return True

if __name__ == '__main__':
    validate_secrets()
```

## Docker Configuration

### Environment Variables in Docker

**docker-compose.yml**:
```yaml
services:
  backend:
    image: projectai/backend:latest
    env_file:
      - .env
      - .env.production
    environment:
      - APP_ENV=production
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - DATABASE_URL=${DATABASE_URL}
    secrets:
      - openai_api_key
      - fernet_key

secrets:
  openai_api_key:
    external: true
  fernet_key:
    external: true
```

**Create Secrets**:
```bash
# Docker Swarm
echo "sk-..." | docker secret create openai_api_key -
echo "fernet-key-here" | docker secret create fernet_key -

# Kubernetes
kubectl create secret generic project-ai-secrets \
  --from-literal=openai-api-key=sk-... \
  --from-literal=fernet-key=...
```

**Read Secrets in Application**:
```python
import os

# Docker Swarm mounts secrets to /run/secrets/
def load_docker_secrets():
    secrets_dir = '/run/secrets'
    if os.path.exists(secrets_dir):
        for secret_name in os.listdir(secrets_dir):
            secret_path = os.path.join(secrets_dir, secret_name)
            with open(secret_path, 'r') as f:
                secret_value = f.read().strip()
                # Set as environment variable
                env_var_name = secret_name.upper().replace('-', '_')
                os.environ[env_var_name] = secret_value

load_docker_secrets()
```

## Kubernetes Configuration

### ConfigMap

**config-map.yaml**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: project-ai-config
data:
  APP_NAME: "Project AI"
  APP_VERSION: "1.0.0"
  LOG_LEVEL: "INFO"
  RATE_LIMIT_PER_MINUTE: "30"
  ENABLE_IMAGE_GENERATION: "true"
  ENABLE_LEARNING_REQUESTS: "true"
  
  # Structured config (JSON)
  config.json: |
    {
      "ai_systems": {
        "persona": {
          "default_traits": {
            "curiosity": 7,
            "helpfulness": 9
          }
        }
      }
    }
```

**Mount in Pod**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: project-ai
spec:
  containers:
  - name: app
    image: projectai/desktop:latest
    envFrom:
    - configMapRef:
        name: project-ai-config
    volumeMounts:
    - name: config
      mountPath: /app/config
  volumes:
  - name: config
    configMap:
      name: project-ai-config
      items:
      - key: config.json
        path: config.json
```

### Secrets

**secrets.yaml**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: project-ai-secrets
type: Opaque
stringData:
  OPENAI_API_KEY: sk-...
  FERNET_KEY: ...
  SECRET_KEY: ...
  DATABASE_URL: postgresql://user:pass@db:5432/legion_web
```

**Mount in Pod**:
```yaml
envFrom:
- secretRef:
    name: project-ai-secrets
```

## Configuration Best Practices

1. **Never commit secrets**: Add `.env*` to `.gitignore` (except `.env.example`)
2. **Use strong secrets**: 32+ bytes for keys, 256-bit for tokens
3. **Rotate regularly**: Every 90 days for production secrets
4. **Validate on startup**: Fail fast if required config missing
5. **Use environment-specific files**: `.env.development`, `.env.production`
6. **Encrypt sensitive config**: Use Fernet for API keys in config files
7. **Audit config changes**: Git log for config files, change tracking for secrets
8. **Document all variables**: `.env.example` with descriptions

## Related Documentation

- `07_container_security.md` - Secrets in containers
- `05_web_deployment.md` - Flask/React configuration
- `02_desktop_distribution.md` - Desktop environment setup

## References

- **12-Factor App**: https://12factor.net/config
- **python-dotenv**: https://saurabh-kumar.com/python-dotenv/
- **Kubernetes Secrets**: https://kubernetes.io/docs/concepts/configuration/secret/
- **HashiCorp Vault**: https://www.vaultproject.io/docs
