# Environment Variables Reference

**Complete Registry of All Environment Variables**  
**Generated**: 2026-04-09  
**Status**: ✅ Canonical Reference  

---

## Table of Contents

1. [Critical Security Variables](#1-critical-security-variables)
2. [API Keys & External Services](#2-api-keys--external-services)
3. [Application Configuration](#3-application-configuration)
4. [Database Configuration](#4-database-configuration)
5. [Observability & Monitoring](#5-observability--monitoring)
6. [Temporal Workflow](#6-temporal-workflow)
7. [Web Frontend (Next.js)](#7-web-frontend-nextjs)
8. [Microservices Configuration](#8-microservices-configuration)
9. [Feature Flags](#9-feature-flags)
10. [Storage & File Paths](#10-storage--file-paths)

---

## 1. Critical Security Variables

### FERNET_KEY

**Purpose**: Symmetric encryption key for encrypting sensitive data (location history, secrets storage)  
**Type**: String (Base64-encoded Fernet key)  
**Required**: **YES** (if using encrypted features)  
**Default**: None  
**Environment**: All  
**Example**: `gAAAAABh...` (44 characters)  
**Generation**:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
**Used in**:

- `src/app/core/secrets_manager.py` - Encrypted secret storage
- Location history encryption
- Sensitive data at rest

**Security Notes**:

- ⚠️ **NEVER commit this to git**
- Rotate every 90 days
- Store in secure secret management system (production)
- Different key per environment

---

### SECRET_KEY

**Purpose**: Master secret for session signing, CSRF protection, general cryptographic operations  
**Type**: String (minimum 32 characters)  
**Required**: **YES** (production), Optional (development)  
**Default**: None (must be set in production)  
**Environment**: All  
**Example**: `your-super-secret-key-change-in-production-min-32-chars`  
**Generation**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
**Used in**:

- API session management
- CSRF token generation
- General cryptographic signing

**Security Notes**:

- Minimum 32 characters (64+ recommended)
- Random alphanumeric + special characters
- Unique per environment
- Rotate on suspected compromise

---

### JWT_SECRET

**Purpose**: JSON Web Token signing key for stateless authentication  
**Type**: String (minimum 32 characters)  
**Required**: Production only  
**Default**: `changeme-secret-key` (development)  
**Environment**: All  
**Example**: `jwt-signing-secret-production-key-2026`  
**Generation**: Same as SECRET_KEY  
**Used in**:

- Microservices authentication
- API token generation
- Service-to-service auth

**Validation**:
```python
if settings.is_production() and settings.JWT_SECRET == "changeme-secret-key":
    raise ValueError("JWT_SECRET must be changed in production")
```

**Security Notes**:

- Must differ from SECRET_KEY
- HS256 algorithm (configurable via JWT_ALGORITHM)
- Token expiry controlled by JWT_EXPIRY_HOURS

---

### API_KEYS

**Purpose**: Comma-separated list of valid API keys for service authentication  
**Type**: String (comma-separated)  
**Required**: Production only  
**Default**: `changeme` (development)  
**Environment**: Production, Staging  
**Example**: `key1-prod-abc123,key2-prod-def456,key3-prod-ghi789`  
**Format**: Comma-separated, no spaces  
**Used in**:

- Microservice API authentication
- Service mesh security
- External API access control

**Validation**:
```python
if settings.is_production() and "changeme" in settings.API_KEYS:
    raise ValueError("API_KEYS must be changed in production")
```

**Security Notes**:

- Minimum 3 keys recommended
- Rotate individual keys without downtime
- Header: `X-API-Key` (configurable via API_KEY_HEADER)

---

## 2. API Keys & External Services

### OPENAI_API_KEY

**Purpose**: OpenAI API access for GPT models, embeddings, and DALL-E  
**Type**: String (OpenAI API key format)  
**Required**: Optional (required if using OpenAI features)  
**Default**: None (empty string)  
**Environment**: All  
**Example**: `sk-proj-...` (starts with `sk-`)  
**Obtain from**: https://platform.openai.com/api-keys  
**Used in**:

- `src/app/core/model_providers.py` - OpenAIProvider
- `src/app/core/image_generator.py` - DALL-E integration
- Chat completion endpoints
- Learning path generation

**Associated Variables**:

- `OPENAI_ORG_ID` - Organization ID (optional)

**Fallback**: Service degrades gracefully if not set (warnings logged)

---

### DEEPSEEK_API_KEY

**Purpose**: DeepSeek API access for DeepSeek-V3 long-context models  
**Type**: String  
**Required**: Optional  
**Default**: None  
**Environment**: All  
**Example**: `ds-...`  
**Obtain from**: https://platform.deepseek.com  
**Used in**:

- `src/app/core/deepseek_v32_inference.py` - DeepSeek integration
- Long-context reasoning tasks

**Rate Limits**: Check DeepSeek documentation  
**Fallback**: Falls back to OpenAI or local models

---

### HUGGINGFACE_API_KEY

**Purpose**: Hugging Face Hub API access for model downloads and inference  
**Type**: String (HF token)  
**Required**: Optional  
**Default**: None  
**Environment**: All  
**Example**: `hf_...`  
**Obtain from**: https://huggingface.co/settings/tokens  
**Used in**:

- Stable Diffusion image generation
- Model downloads from HF Hub
- Inference API calls

**Permissions**: Read access sufficient (write if pushing models)

---

### SMTP_USERNAME

**Purpose**: SMTP server username for emergency email alerts  
**Type**: String (email address or username)  
**Required**: Optional (required if using emergency alerts)  
**Default**: None  
**Environment**: Production, Staging  
**Example**: `alerts@yourcompany.com`  
**Used in**:

- `src/app/core/emergency_alert.py` - Email notification system
- Critical system alerts
- Guardian approval notifications

**Associated Variables**:

- `SMTP_PASSWORD` - SMTP authentication password
- `SMTP_HOST` - SMTP server address (implicit, may need to add)
- `SMTP_PORT` - SMTP server port (implicit, may need to add)

---

### SMTP_PASSWORD

**Purpose**: SMTP server password for email authentication  
**Type**: String (password)  
**Required**: Optional (with SMTP_USERNAME)  
**Default**: None  
**Environment**: Production, Staging  
**Example**: `your-email-password`  
**Security**: Use app-specific passwords (Gmail, etc.)  
**Encryption**: Transmitted over TLS

---

### LONG_CONTEXT_API_ENDPOINT

**Purpose**: API endpoint for long-context model (Nous-Capybara-34B-200k)  
**Type**: String (URL)  
**Required**: Optional  
**Default**: None  
**Environment**: All  
**Example**: `https://api.example.com/v1/chat/completions`  
**Used in**: Long-context reasoning tasks  

**Associated Variables**:

- `LONG_CONTEXT_API_KEY` - Authentication for endpoint

---

### SAFETY_MODEL_API_ENDPOINT

**Purpose**: API endpoint for safety model (Llama-Guard-3-8B)  
**Type**: String (URL)  
**Required**: Optional  
**Default**: None  
**Environment**: Production (recommended)  
**Example**: `https://api.example.com/v1/safety/check`  
**Used in**: Content moderation, safety checks  

**Associated Variables**:

- `SAFETY_MODEL_API_KEY` - Authentication for endpoint

---

## 3. Application Configuration

### ENVIRONMENT

**Purpose**: Deployment environment identifier  
**Type**: Enum string  
**Required**: **YES**  
**Default**: `development`  
**Valid Values**: `development`, `staging`, `production`  
**Environment**: All  
**Example**: `production`  
**Validation**: Pydantic pattern `^(development|staging|production)$`  
**Used in**:

- Conditional feature enablement
- Logging level determination
- Security validation strictness
- API documentation visibility

**Behavior by Environment**:
| Environment | API Docs | Default Secrets | CORS | Log Level |
|-------------|----------|----------------|------|-----------|
| development | Enabled  | Allowed        | *    | DEBUG     |
| staging     | Enabled  | Warning        | Limited | INFO   |
| production  | Disabled | **ERROR**      | Strict | WARN    |

---

### API_HOST

**Purpose**: API server bind address  
**Type**: String (IP address)  
**Required**: No  
**Default**: `0.0.0.0` (all interfaces)  
**Environment**: All  
**Example**: `0.0.0.0` or `127.0.0.1`  
**Used in**: Uvicorn/FastAPI server startup  
**Docker**: Always `0.0.0.0` in containers

---

### API_PORT

**Purpose**: API server port  
**Type**: Integer  
**Required**: No  
**Default**: `8001`  
**Environment**: All  
**Valid Range**: 1024-65535  
**Example**: `8001`  
**Used in**: API server binding  

**Port Allocation**:
| Service | Port | Purpose |
|---------|------|---------|
| Main API | 8001 | Primary API |
| Metrics | 8000 | Prometheus metrics |
| Firewall | 8011 | Mutation firewall |
| Incident Reflex | 8012 | Incident response |
| Trust Graph | 8013 | Trust engine |
| Data Vault | 8014 | Sovereign vault |
| Negotiation | 8015 | Negotiation agent |
| Compliance | 8016 | Compliance engine |
| Verifiable Reality | 8017 | Reality verification |

---

### API_WORKERS

**Purpose**: Number of Uvicorn worker processes  
**Type**: Integer  
**Required**: No  
**Default**: `4`  
**Environment**: Production  
**Recommended**: 2-4 per CPU core  
**Example**: `4`  
**Used in**: Production deployments  
**Note**: Single worker in development

---

### API_PREFIX

**Purpose**: API route prefix for versioning  
**Type**: String  
**Required**: No  
**Default**: `/api/v1`  
**Environment**: All  
**Example**: `/api/v1`  
**Used in**: FastAPI router configuration  

---

### APP_VERSION

**Purpose**: Application version for tracking and telemetry  
**Type**: String (semver)  
**Required**: No  
**Default**: `1.0.0`  
**Environment**: All  
**Example**: `1.2.3`  
**Used in**:

- API metadata
- Health checks
- OpenTelemetry service version

---

### LOG_LEVEL

**Purpose**: Application logging verbosity  
**Type**: Enum string  
**Required**: No  
**Default**: `INFO`  
**Valid Values**: `DEBUG`, `INFO`, `WARN`, `ERROR`, `CRITICAL`  
**Environment**: All  
**Example**: `INFO`  
**Used in**: Python logging configuration  

**Recommended by Environment**:

- Development: `DEBUG`
- Staging: `INFO`
- Production: `WARN` or `INFO`

---

### CORS_ORIGINS

**Purpose**: Comma-separated list of allowed CORS origins  
**Type**: String (comma-separated URLs)  
**Required**: No  
**Default**: `*` (development), specific origins (production)  
**Environment**: All  
**Example**: `http://localhost:3000,https://app.example.com`  
**Format**: `origin1,origin2,origin3` (no spaces)  
**Used in**: FastAPI CORSMiddleware  

**Security**:

- Development: `*` acceptable
- Production: **NEVER** use `*`, specify exact origins

---

## 4. Database Configuration

### DATABASE_URL

**Purpose**: Primary database connection string  
**Type**: String (database URL)  
**Required**: Optional (depends on features used)  
**Default**: None  
**Environment**: All  
**Format**: `postgresql://user:password@host:port/dbname`  
**Example**: `postgresql://sovereign:secret@localhost:5432/project_ai`  
**Used in**:

- SQLAlchemy connections
- Async database pools
- Data persistence layers

**Security**:

- Never log this value
- Use connection pooling
- Enable SSL in production

---

### DB_POOL_SIZE

**Purpose**: Database connection pool size  
**Type**: Integer  
**Required**: No  
**Default**: `20`  
**Environment**: All  
**Recommended**: 10-50 depending on load  
**Example**: `20`  
**Used in**: SQLAlchemy pool configuration  

---

### DB_TIMEOUT

**Purpose**: Database query timeout in seconds  
**Type**: Integer  
**Required**: No  
**Default**: `30`  
**Environment**: All  
**Example**: `30`  
**Used in**: Database query execution  

---

### POSTGRES_USER

**Purpose**: PostgreSQL username (Temporal database)  
**Type**: String  
**Required**: Docker Compose only  
**Default**: `temporal`  
**Environment**: Development (Docker)  
**Example**: `temporal`  
**Used in**: Temporal PostgreSQL container  

---

### POSTGRES_PASSWORD

**Purpose**: PostgreSQL password (Temporal database)  
**Type**: String  
**Required**: Docker Compose only  
**Default**: `temporal`  
**Environment**: Development (Docker)  
**Example**: `temporal`  
**Security**: Change in production, use secrets

---

### POSTGRES_DB

**Purpose**: PostgreSQL database name (Temporal)  
**Type**: String  
**Required**: Docker Compose only  
**Default**: `temporal`  
**Environment**: Development (Docker)  
**Example**: `temporal`  

---

## 5. Observability & Monitoring

### ENABLE_METRICS

**Purpose**: Enable Prometheus metrics collection  
**Type**: Boolean  
**Required**: No  
**Default**: `true`  
**Valid Values**: `true`, `false`  
**Environment**: All  
**Example**: `true`  
**Used in**: Metrics middleware, Prometheus exporters  
**Endpoint**: `/metrics` (typically on METRICS_PORT)

---

### ENABLE_TRACING

**Purpose**: Enable distributed tracing (OpenTelemetry)  
**Type**: Boolean  
**Required**: No  
**Default**: `true`  
**Valid Values**: `true`, `false`  
**Environment**: Production, Staging  
**Example**: `true`  
**Used in**: OpenTelemetry instrumentation  

---

### ENABLE_OTLP

**Purpose**: Enable OpenTelemetry Protocol export  
**Type**: Boolean  
**Required**: No  
**Default**: `true`  
**Valid Values**: `true`, `false`  
**Environment**: Production  
**Example**: `true`  
**Used in**: OTLP exporter configuration  

---

### METRICS_PORT

**Purpose**: Port for Prometheus metrics endpoint  
**Type**: Integer  
**Required**: No  
**Default**: `8000` (main service), `9090` (microservices)  
**Environment**: All  
**Example**: `9090`  
**Used in**: Metrics HTTP server  
**Note**: Should differ from main API_PORT

---

### OTLP_ENDPOINT

**Purpose**: OpenTelemetry Collector endpoint  
**Type**: String (host:port)  
**Required**: If ENABLE_OTLP=true  
**Default**: `localhost:4317`  
**Environment**: Production, Staging  
**Example**: `otel-collector:4317`  
**Protocol**: gRPC (4317) or HTTP (4318)  
**Used in**: OpenTelemetry exporter  

---

### SERVICE_NAME

**Purpose**: Service identifier for telemetry  
**Type**: String  
**Required**: No  
**Default**: `project-ai` (varies by service)  
**Environment**: All  
**Example**: `ai-mutation-firewall`  
**Used in**:

- OpenTelemetry service name
- Prometheus labels
- Log aggregation

---

### SERVICE_VERSION

**Purpose**: Service version for telemetry  
**Type**: String (semver)  
**Required**: No  
**Default**: `1.0.0`  
**Environment**: All  
**Example**: `1.2.3`  
**Used in**: Telemetry metadata  

---

### APP_ENV

**Purpose**: Application environment (alias for ENVIRONMENT)  
**Type**: String  
**Required**: No  
**Default**: `production`  
**Environment**: All  
**Example**: `production`  
**Used in**: OpenTelemetry environment tag  

---

## 6. Temporal Workflow

### TEMPORAL_HOST

**Purpose**: Temporal server address  
**Type**: String (host:port)  
**Required**: If using Temporal workflows  
**Default**: `localhost:7233`  
**Environment**: All  
**Example**: `temporal:7233` (Docker), `temporal.example.com:7233` (production)  
**Used in**:

- Temporal client connection
- Workflow execution
- Activity scheduling

---

### TEMPORAL_NAMESPACE

**Purpose**: Temporal namespace for workflow isolation  
**Type**: String  
**Required**: No  
**Default**: `default`  
**Environment**: All  
**Example**: `project-ai-prod`  
**Used in**: Temporal client configuration  
**Recommended**: Unique per environment

---

## 7. Web Frontend (Next.js)

All frontend variables are prefixed with `NEXT_PUBLIC_` for client-side access.

### NEXT_PUBLIC_API_URL

**Purpose**: Backend API base URL  
**Type**: String (URL)  
**Required**: **YES**  
**Default**: `http://localhost:5000`  
**Environment**: All  
**Example**: `https://api.example.com`  
**Used in**: API client configuration  

---

### NEXT_PUBLIC_API_TIMEOUT

**Purpose**: API request timeout in milliseconds  
**Type**: Integer  
**Required**: No  
**Default**: `30000` (30 seconds)  
**Environment**: All  
**Example**: `30000`  

---

### NEXT_PUBLIC_APP_NAME

**Purpose**: Application display name  
**Type**: String  
**Required**: No  
**Default**: `Project-AI`  
**Environment**: All  
**Example**: `Project-AI`  
**Used in**: UI header, page titles  

---

### NEXT_PUBLIC_APP_VERSION

**Purpose**: Frontend version display  
**Type**: String (semver)  
**Required**: No  
**Default**: `1.0.0`  
**Environment**: All  
**Example**: `1.0.0`  

---

### NEXT_PUBLIC_ENV

**Purpose**: Frontend environment indicator  
**Type**: String  
**Required**: No  
**Default**: `production`  
**Environment**: All  
**Example**: `production`  
**Used in**: Environment-specific UI behavior  

---

### NEXT_PUBLIC_SESSION_TIMEOUT

**Purpose**: User session timeout in milliseconds  
**Type**: Integer  
**Required**: No  
**Default**: `3600000` (1 hour)  
**Environment**: All  
**Example**: `3600000`  

---

### NEXT_PUBLIC_MAX_FILE_SIZE

**Purpose**: Maximum file upload size in bytes  
**Type**: Integer  
**Required**: No  
**Default**: `10485760` (10 MB)  
**Environment**: All  
**Example**: `10485760`  

---

### NEXT_PUBLIC_ANALYTICS_ID

**Purpose**: Analytics service ID (Google Analytics, etc.)  
**Type**: String  
**Required**: Optional  
**Default**: None  
**Environment**: Production  
**Example**: `G-XXXXXXXXXX`  

---

### NEXT_PUBLIC_SENTRY_DSN

**Purpose**: Sentry error tracking DSN  
**Type**: String (URL)  
**Required**: Optional  
**Default**: None  
**Environment**: Production, Staging  
**Example**: `https://xxx@sentry.io/xxx`  

---

## 8. Microservices Configuration

### RATE_LIMIT_PER_MINUTE

**Purpose**: API rate limit requests per minute  
**Type**: Integer  
**Required**: No  
**Default**: `250` (microservices), `60` (main API)  
**Environment**: All  
**Example**: `250`  
**Used in**: Rate limiting middleware  

---

### RATE_LIMIT_BURST

**Purpose**: Rate limit burst capacity  
**Type**: Integer  
**Required**: No  
**Default**: `500`  
**Environment**: All  
**Example**: `500`  
**Used in**: Token bucket algorithm  

---

### ENABLE_RATE_LIMITING

**Purpose**: Enable/disable rate limiting  
**Type**: Boolean  
**Required**: No  
**Default**: `true`  
**Environment**: All  
**Example**: `true`  

---

### JWT_ALGORITHM

**Purpose**: JWT signing algorithm  
**Type**: String  
**Required**: No  
**Default**: `HS256`  
**Valid Values**: `HS256`, `HS384`, `HS512`, `RS256`  
**Environment**: All  
**Example**: `HS256`  

---

### JWT_EXPIRY_HOURS

**Purpose**: JWT token expiration time in hours  
**Type**: Integer  
**Required**: No  
**Default**: `24`  
**Environment**: All  
**Example**: `24`  
**Recommended**: 1-24 hours depending on security requirements  

---

### API_KEY_HEADER

**Purpose**: HTTP header name for API key authentication  
**Type**: String  
**Required**: No  
**Default**: `X-API-Key`  
**Environment**: All  
**Example**: `X-API-Key`  

---

## 9. Feature Flags

### ENABLE_API_DOCS

**Purpose**: Enable interactive API documentation (Swagger/ReDoc)  
**Type**: Boolean  
**Required**: No  
**Default**: `true` (development), `false` (production)  
**Environment**: All  
**Example**: `true`  
**Endpoints**: `/docs`, `/redoc`  

---

### NEXT_PUBLIC_ENABLE_IMAGE_GENERATION

**Purpose**: Enable image generation features in UI  
**Type**: Boolean  
**Required**: No  
**Default**: `true`  
**Environment**: All  
**Example**: `true`  

---

### NEXT_PUBLIC_ENABLE_DATA_ANALYSIS

**Purpose**: Enable data analysis features in UI  
**Type**: Boolean  
**Required**: No  
**Default**: `true`  
**Environment**: All  
**Example**: `true`  

---

### NEXT_PUBLIC_ENABLE_LEARNING_PATHS

**Purpose**: Enable learning paths feature in UI  
**Type**: Boolean  
**Required**: No  
**Default**: `true`  
**Environment**: All  
**Example**: `true`  

---

### NEXT_PUBLIC_ENABLE_SECURITY_RESOURCES

**Purpose**: Enable security resources in UI  
**Type**: Boolean  
**Required**: No  
**Default**: `true`  
**Environment**: All  
**Example**: `true`  

---

### NEXT_PUBLIC_ENABLE_EMERGENCY_ALERTS

**Purpose**: Enable emergency alert system in UI  
**Type**: Boolean  
**Required**: No  
**Default**: `true`  
**Environment**: All  
**Example**: `true`  

---

## 10. Storage & File Paths

### DATA_DIR

**Purpose**: Data storage directory path  
**Type**: String (path)  
**Required**: No  
**Default**: `data` (relative), `/app/data` (Docker)  
**Environment**: All  
**Example**: `data` or `/app/data`  
**Used in**: File storage, data persistence  

---

### LOG_DIR

**Purpose**: Log file storage directory  
**Type**: String (path)  
**Required**: No  
**Default**: `logs` (relative), `/app/logs` (Docker)  
**Environment**: All  
**Example**: `logs` or `/app/logs`  
**Used in**: Log file writers  

---

### AUDIT_LOG_PATH

**Purpose**: Audit log file path  
**Type**: String (path)  
**Required**: No  
**Default**: `audit.log`  
**Environment**: All  
**Example**: `audit.log`  
**Used in**: Governance audit logging  

---

### CLOUD_SYNC_URL

**Purpose**: Cloud synchronization endpoint URL  
**Type**: String (URL)  
**Required**: Optional  
**Default**: None  
**Environment**: All  
**Example**: `https://sync.example.com/api`  
**Used in**: Cross-device synchronization  
**Note**: Cloud sync disabled if not set

---

## Environment Variable Summary

**Total Variables Documented**: 80+  
**Required (Production)**: 4 (FERNET_KEY, SECRET_KEY, JWT_SECRET, API_KEYS)  
**Optional**: 76+  
**Security-Critical**: 8  
**Feature Flags**: 6  

---

## Validation Checklist

Use this checklist when deploying to production:

### Critical

- [ ] FERNET_KEY is set and unique
- [ ] SECRET_KEY is set and non-default (32+ chars)
- [ ] JWT_SECRET is set and non-default
- [ ] API_KEYS are set and non-default
- [ ] ENVIRONMENT=production
- [ ] CORS_ORIGINS is restrictive (no `*`)

### Recommended

- [ ] OPENAI_API_KEY set (if using AI features)
- [ ] DATABASE_URL set (if using database)
- [ ] TEMPORAL_HOST set (if using workflows)
- [ ] SMTP credentials set (if using alerts)
- [ ] ENABLE_METRICS=true
- [ ] ENABLE_TRACING=true
- [ ] OTLP_ENDPOINT configured
- [ ] LOG_LEVEL=WARN or INFO

### Optional

- [ ] DEEPSEEK_API_KEY (for long-context)
- [ ] HUGGINGFACE_API_KEY (for HF models)
- [ ] SENTRY_DSN (for error tracking)
- [ ] ANALYTICS_ID (for analytics)

---

## Quick Reference Commands

### Generate Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Validate Environment

```bash
python env_validator.py
```

### Check Current Environment

```bash
echo $ENVIRONMENT

# or

python -c "import os; print(os.getenv('ENVIRONMENT', 'NOT SET'))"
```

---

**This is the canonical reference for all environment variables.**  
**Last Updated**: 2026-04-09  
**Maintainer**: Environment Architecture Team
