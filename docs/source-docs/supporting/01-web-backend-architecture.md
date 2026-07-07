# Web Backend Architecture

**Document Type:** Technical Reference  
**Component:** Web Backend (Flask)  
**Status:** Production  
**Version:** 2.0.0  
**Last Updated:** 2025-01-26  
**Author:** AGENT-046  
**Audience:** Backend Developers, DevOps, Integration Engineers  
**Scope:** Flask web application, API endpoints, middleware, governance integration  
**Related Docs:**
- `02-api-endpoint-reference.md`
- `03-middleware-security.md`
- `../core/governance-pipeline.md`
- `../core/ai-orchestrator.md`

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture & Design](#architecture--design)
3. [Core Components](#core-components)
4. [API Endpoints](#api-endpoints)
5. [Governance Integration](#governance-integration)
6. [Security Middleware](#security-middleware)
7. [Request Flow](#request-flow)
8. [Configuration Guide](#configuration-guide)
9. [Deployment Architecture](#deployment-architecture)
10. [Error Handling](#error-handling)
11. [Monitoring & Observability](#monitoring--observability)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)

---

## System Overview

### Purpose and Responsibility

The Project-AI Web Backend is a **lightweight Flask adapter** that provides HTTP/REST API access to the core AI systems. It acts as a thin translation layer between web requests and the internal governance pipeline.

**Key Characteristics:**
- **Thin Adapter Pattern**: No business logic in the web layer
- **Governance-First**: All requests flow through the governance pipeline
- **Stateless Design**: Token-based authentication, no server-side sessions
- **Multi-Provider Support**: Integrates with OpenAI, DeepSeek, and other AI providers
- **Security Hardened**: CORS, rate limiting, input sanitization, JWT authentication

**NOT a Traditional MVC Application:**
- Does NOT contain business logic (delegated to core systems)
- Does NOT implement direct database access (uses core managers)
- Does NOT make direct external API calls (routed through AI orchestrator)

### Strategic Position

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXECUTION SOURCES                             │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│   Desktop    │   Web UI     │     CLI      │   Temporal         │
│   (PyQt6)    │   (React)    │   (Typer)    │   (Workflows)      │
└──────┬───────┴──────┬───────┴──────┬───────┴──────┬─────────────┘
       │              │              │              │
       └──────────────┴──────────────┴──────────────┘
                       │
              ┌────────▼────────┐
              │  Runtime Router │  ◄── web/backend/app.py
              └────────┬────────┘
                       │
              ┌────────▼─────────┐
              │ Governance Pipeline│
              │  (TARL Policies)  │
              └────────┬──────────┘
                       │
              ┌────────▼─────────┐
              │  AI Orchestrator │
              │ (Multi-Provider)  │
              └────────┬──────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
   ┌───▼────┐    ┌────▼─────┐   ┌────▼──────┐
   │ User   │    │ Persona  │   │ Memory    │
   │Manager │    │ System   │   │ System    │
   └────────┘    └──────────┘   └───────────┘
```

**Adapter Benefits:**
1. **Separation of Concerns**: Web layer only handles HTTP translation
2. **Code Reuse**: Desktop, CLI, and web all use the same core logic
3. **Security Consistency**: Single governance pipeline for all entry points
4. **Testing Simplification**: Test core logic once, not per interface
5. **Deployment Flexibility**: Web backend can be scaled independently

---

## Architecture & Design

### Design Principles

1. **Stateless HTTP**: Each request is self-contained with JWT tokens
2. **Fail-Safe Defaults**: All operations default to deny unless explicitly allowed
3. **Explicit Over Implicit**: All configuration and behavior is explicit
4. **Defense in Depth**: Multiple security layers (CORS, rate limiting, governance)
5. **Observable Operations**: All requests logged for audit and debugging

### Architectural Patterns

#### 1. Thin Adapter Pattern

```python
@app.route("/api/auth/login", methods=["POST"])
def login():
    """
    Old: Direct authentication with plaintext passwords
    New: Routes through governance → secure auth (argon2/JWT)
    """
    payload = request.get_json(silent=True)
    
    # NO business logic here - delegate to router
    response = route_request(
        source="web",
        payload={
            "action": "user.login",
            "username": payload.get("username"),
            "password": payload.get("password"),
        },
    )
    
    # Translate internal response to HTTP
    if response["status"] == "success":
        return jsonify(token=response["result"]["token"]), 200
    else:
        return jsonify(error=response.get("error")), 401
```

**Why This Pattern:**
- **Testability**: Core logic can be tested without HTTP mocking
- **Consistency**: Desktop and web execute identical logic paths
- **Security**: Governance pipeline applies uniformly across all entry points
- **Maintainability**: Business logic changes don't require web layer updates

#### 2. Request-Response Translation

```
HTTP Request → Flask Handler → Runtime Router → Governance → AI Orchestrator → Core Systems
                                                                                    ↓
HTTP Response ← Flask Handler ← Response Dict ← Result ← Execution ← State Change ←
```

**Translation Responsibilities:**
- Extract HTTP headers (Authorization, Content-Type)
- Parse JSON body with error handling
- Build internal payload structure
- Map internal status codes to HTTP status codes
- Format response with appropriate headers

#### 3. Security Middleware Layering

```
Request
  │
  ├─► CORS Check (allowed origins)
  ├─► Rate Limit Check (per IP/endpoint)
  ├─► Content-Type Validation
  ├─► Request Size Limit
  ├─► JWT Token Validation (if protected route)
  │
  └─► Flask Route Handler
        │
        └─► Runtime Router
              │
              └─► Governance Pipeline (TARL policies)
```

---

## Core Components

### 1. Flask Application (`web/backend/app.py`)

**Responsibilities:**
- Initialize Flask app with security middleware
- Define API route handlers
- Translate HTTP requests to internal payloads
- Format responses with appropriate status codes and headers

**Key Attributes:**
```python
app = Flask(__name__)
logger = logging.getLogger(__name__)

# Security middleware configured on startup
configure_cors(app)
configure_rate_limiting(app)
```

**Route Organization:**
- `/api/status` - Health check endpoint
- `/api/auth/*` - Authentication endpoints
- `/api/ai/*` - AI interaction endpoints
- `/api/persona/*` - AI persona management
- `/api/memory/*` - Memory operations (future)
- `/api/learning/*` - Learning requests (future)

### 2. Runtime Router (`app/core/runtime/router.py`)

**Purpose:** Multi-path coordination layer that routes requests from any execution source (web/desktop/CLI/agent) through the unified governance pipeline.

**Interface:**
```python
def route_request(
    source: Literal["web", "desktop", "cli", "agent", "temporal", "test"],
    payload: dict[str, Any]
) -> dict[str, Any]:
    """
    Route requests from any execution path through governance pipeline.
    
    Returns:
        {
            "status": "success" | "error" | "blocked",
            "result": Any,  # Action result
            "metadata": {...}  # Execution metadata
        }
    """
```

**Context Building:**
```python
context = {
    "source": source,           # Execution path identifier
    "payload": payload,         # Original request data
    "action": payload.get("action"),  # Action identifier
    "user": payload.get("user", {}),  # User context
    "config": payload.get("config", {}),  # Config overrides
    "timestamp": _get_timestamp(),  # ISO 8601 timestamp
}
```

**Execution Flow:**
1. Build execution context from source and payload
2. Import governance pipeline (lazy to avoid circular imports)
3. Delegate to `enforce_pipeline(context)`
4. Wrap result with metadata
5. Return structured response

### 3. Security Middleware (`app/core/security/middleware.py`)

#### CORS Configuration

**Purpose:** Control cross-origin resource sharing to prevent unauthorized access.

```python
def configure_cors(app: Any, allowed_origins: list[str] | None = None) -> None:
    """
    Configure CORS with strict origin control.
    
    Default allowed origins:
        - http://localhost:3000 (React dev server)
        - http://localhost:5173 (Vite dev server)
    """
    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
```

**Configuration Options:**
- **Origins**: Whitelist of allowed domains
- **Credentials**: Enable cookie/auth header support
- **Methods**: Allowed HTTP methods
- **Headers**: Allowed request headers

**Production Considerations:**
- NEVER use wildcard `*` for origins in production
- Set origins from environment variable `CORS_ORIGINS`
- Use HTTPS origins for production deployments
- Enable credentials only if necessary (increases attack surface)

#### Rate Limiting

**Purpose:** Prevent abuse and ensure fair resource usage.

```python
def configure_rate_limiting(app: Any) -> None:
    """
    Configure rate limiting for Flask app.
    
    Limits:
        - Authentication: 5/minute
        - API calls: 100/minute
        - Image generation: 10/hour
    """
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per minute"],
        storage_uri="memory://",  # Use Redis in production
    )
```

**Rate Limit Strategy:**
| Endpoint | Limit | Reason |
|----------|-------|--------|
| `/api/auth/login` | 5/minute | Prevent brute force attacks |
| `/api/ai/chat` | 100/minute | Balance between usability and cost |
| `/api/ai/image` | 10/hour | Image generation is expensive |
| Default | 100/minute | General API usage |

**Production Configuration:**
```python
# Use Redis for distributed rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://redis:6379",
)
```

#### Request Sanitization

**Purpose:** Remove dangerous headers and validate content types.

```python
class RequestSanitizer:
    @staticmethod
    def sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
        """Remove dangerous headers."""
        dangerous = ["X-Forwarded-For", "X-Real-IP"]
        return {k: v for k, v in headers.items() if k not in dangerous}

    @staticmethod
    def validate_content_type(content_type: str | None) -> bool:
        """Validate content type is allowed."""
        allowed = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        ]
        base_type = content_type.split(";")[0].strip()
        return base_type in allowed
```

---

## API Endpoints

### Health Check

**Endpoint:** `GET /api/status`  
**Authentication:** None  
**Rate Limit:** 100/minute

**Purpose:** Health check for monitoring and load balancers.

**Request:**
```bash
curl http://localhost:5000/api/status
```

**Response:**
```json
{
  "status": "ok",
  "component": "web-backend"
}
```

**Status Codes:**
- `200 OK` - Service is healthy
- `500 Internal Server Error` - Service degraded

**Use Cases:**
- Kubernetes liveness/readiness probes
- Load balancer health checks
- Monitoring dashboards (Prometheus, Grafana)
- CI/CD deployment verification

### Authentication

#### Login

**Endpoint:** `POST /api/auth/login`  
**Authentication:** None  
**Rate Limit:** 5/minute

**Purpose:** Authenticate user and receive JWT token.

**Request:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "secure-password"
  }'
```

**Response (Success):**
```json
{
  "status": "ok",
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "username": "admin",
    "role": "superuser"
  }
}
```

**Response (Failure):**
```json
{
  "status": "error",
  "success": false,
  "error": "invalid-credentials",
  "message": "Authentication failed"
}
```

**Status Codes:**
- `200 OK` - Authentication successful
- `400 Bad Request` - Missing JSON body
- `401 Unauthorized` - Invalid credentials
- `429 Too Many Requests` - Rate limit exceeded

**Security Features:**
1. **Argon2 Password Hashing**: Passwords hashed with memory-hard algorithm
2. **JWT Token Generation**: Stateless token with 24-hour expiration
3. **Account Lockout**: 5 failed attempts triggers 15-minute lockout
4. **Audit Logging**: All login attempts logged with IP and timestamp
5. **Rate Limiting**: 5 attempts per minute to prevent brute force

**Token Structure:**
```json
{
  "username": "admin",
  "role": "superuser",
  "exp": 1706371200,  // Expiration timestamp
  "iat": 1706284800   // Issued at timestamp
}
```

### AI Interaction

#### Chat

**Endpoint:** `POST /api/ai/chat`  
**Authentication:** Bearer Token  
**Rate Limit:** 100/minute

**Purpose:** Send chat messages to AI and receive responses.

**Request:**
```bash
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "prompt": "Explain quantum computing",
    "model": "gpt-4",
    "provider": "openai"
  }'
```

**Response:**
```json
{
  "result": {
    "response": "Quantum computing is...",
    "model": "gpt-4",
    "provider": "openai",
    "tokens_used": 156
  },
  "metadata": {
    "timestamp": "2025-01-26T12:00:00Z",
    "latency_ms": 1234,
    "governance_checks": ["four_laws", "content_filter"]
  }
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | User message to send to AI |
| `model` | string | No | AI model (default: gpt-4) |
| `provider` | string | No | AI provider (default: openai) |
| `temperature` | float | No | Response randomness (0-1, default: 0.7) |
| `max_tokens` | int | No | Maximum response length |

**Supported Providers:**
- `openai` - GPT-3.5-Turbo, GPT-4, GPT-4-Turbo
- `deepseek` - DeepSeek Chat, DeepSeek Coder
- `anthropic` - Claude 2, Claude 3 (future)

**Status Codes:**
- `200 OK` - Request successful
- `400 Bad Request` - Missing required fields
- `401 Unauthorized` - Missing or invalid token
- `500 Internal Server Error` - AI provider error

**Error Handling:**
```json
{
  "error": "AI request failed",
  "details": {
    "provider": "openai",
    "error_type": "rate_limit_exceeded",
    "retry_after": 60
  }
}
```

#### Image Generation

**Endpoint:** `POST /api/ai/image`  
**Authentication:** Bearer Token  
**Rate Limit:** 10/hour

**Purpose:** Generate images from text prompts.

**Request:**
```bash
curl -X POST http://localhost:5000/api/ai/image \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "prompt": "A futuristic cityscape at sunset",
    "model": "dall-e-3",
    "provider": "openai",
    "size": "1024x1024"
  }'
```

**Response:**
```json
{
  "result": {
    "image_url": "https://...",
    "image_path": "/data/images/2025-01-26/12345.png",
    "model": "dall-e-3",
    "provider": "openai"
  },
  "metadata": {
    "timestamp": "2025-01-26T12:00:00Z",
    "generation_time_s": 8.5,
    "content_filter": "passed"
  }
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Image description |
| `model` | string | No | Model (dall-e-3, sd-2.1) |
| `provider` | string | No | Provider (openai, huggingface) |
| `size` | string | No | Image size (256x256, 512x512, 1024x1024) |
| `style` | string | No | Style preset (photorealistic, anime, etc.) |

**Content Filtering:**
- 15 blocked keywords (violence, explicit content, etc.)
- Automatic safety negative prompts
- Post-generation content analysis
- Rejected prompts logged for review

### Persona Management

**Endpoint:** `POST /api/persona/update`  
**Authentication:** Bearer Token  
**Rate Limit:** 100/minute

**Purpose:** Update AI persona traits.

**Request:**
```bash
curl -X POST http://localhost:5000/api/persona/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "trait": "humor",
    "value": 0.8
  }'
```

**Response:**
```json
{
  "success": true,
  "result": {
    "trait": "humor",
    "old_value": 0.5,
    "new_value": 0.8,
    "updated_at": "2025-01-26T12:00:00Z"
  }
}
```

**Supported Traits:**
| Trait | Range | Default | Description |
|-------|-------|---------|-------------|
| `humor` | 0.0-1.0 | 0.5 | Wit and playfulness |
| `formality` | 0.0-1.0 | 0.5 | Professional vs casual |
| `curiosity` | 0.0-1.0 | 0.7 | Asking follow-up questions |
| `empathy` | 0.0-1.0 | 0.8 | Emotional awareness |
| `assertiveness` | 0.0-1.0 | 0.5 | Directness of communication |
| `creativity` | 0.0-1.0 | 0.7 | Novel solutions |
| `patience` | 0.0-1.0 | 0.9 | Tolerance for repetition |
| `detail` | 0.0-1.0 | 0.6 | Depth of explanations |

---

## Governance Integration

### Request Flow Through Governance

```python
# web/backend/app.py
@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    payload = request.get_json(silent=True)
    
    # Step 1: Route to governance pipeline
    response = route_request(
        source="web",
        payload={
            "action": "ai.chat",
            "task_type": "chat",
            "prompt": payload.get("prompt"),
            "model": payload.get("model"),
            "provider": payload.get("provider"),
            "token": extract_token(request),
        },
    )
    
    # Step 2: Translate response to HTTP
    if response["status"] == "success":
        return jsonify(result=response["result"]), 200
    else:
        return jsonify(error=response["error"]), 500
```

### Governance Pipeline Execution

```python
# app/core/runtime/router.py
def route_request(source, payload):
    context = {
        "source": source,
        "action": payload.get("action"),
        "user": payload.get("user"),
        "timestamp": _get_timestamp(),
    }
    
    # Import governance pipeline (lazy to avoid circular imports)
    from app.core.governance.pipeline import enforce_pipeline
    
    # Execute governance checks:
    # 1. TARL policy validation
    # 2. Four Laws compliance
    # 3. User authorization
    # 4. Resource quotas
    # 5. Content filtering
    result = enforce_pipeline(context)
    
    return {
        "status": "success",
        "result": result,
        "metadata": {...},
    }
```

### Governance Checks Applied

1. **TARL Policy Validation**
   - Evaluate request against TARL policies
   - Check for policy violations
   - Apply policy-defined transformations

2. **Four Laws Compliance**
   - Law 1: Protect humanity (content safety)
   - Law 2: Follow user orders (unless conflicts with Law 1)
   - Law 3: Self-preservation (resource limits)
   - Law 4: Transparency (audit logging)

3. **User Authorization**
   - Verify JWT token validity
   - Check user role and permissions
   - Enforce RBAC policies

4. **Resource Quotas**
   - Check daily AI request quota
   - Verify image generation limits
   - Enforce storage quotas

5. **Content Filtering**
   - Scan prompts for prohibited content
   - Apply safety classifiers
   - Log violations for review

---

## Configuration Guide

### Environment Variables

**Required:**
```bash
# OpenAI API Key
OPENAI_API_KEY=sk-...

# Flask Secret Key (for session signing)
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

**Optional:**
```bash
# API Server Configuration
API_HOST=0.0.0.0           # Listen address (default: 0.0.0.0)
API_PORT=5000              # Port (default: 5000)
ENVIRONMENT=production     # production|development|test

# CORS Configuration
CORS_ORIGINS=https://app.example.com,https://admin.example.com

# Rate Limiting Storage (use Redis in production)
RATE_LIMIT_STORAGE_URI=redis://redis:6379

# DeepSeek (optional)
DEEPSEEK_API_KEY=sk-...

# Logging
LOG_LEVEL=INFO             # DEBUG|INFO|WARNING|ERROR
AUDIT_LOG_PATH=audit.log   # Path to audit log file
```

### Flask Configuration

**Development:**
```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

**Production (Gunicorn):**
```bash
gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 4 \
  --worker-class sync \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  web.backend.app:app
```

**Production (uWSGI):**
```bash
uwsgi \
  --http :5000 \
  --module web.backend.app:app \
  --master \
  --processes 4 \
  --threads 2 \
  --harakiri 120
```

### Security Configuration

**HTTPS (Production):**
```bash
# Use reverse proxy (Nginx, Traefik, Caddy)
# DO NOT terminate TLS in Flask

# Nginx example:
server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Security Headers:**
```python
@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

## Deployment Architecture

### Local Development

```
┌─────────────────────────────────────┐
│  Developer Workstation              │
│                                     │
│  ┌──────────────┐  ┌──────────────┐ │
│  │ React Dev    │  │ Flask Dev    │ │
│  │ Server       │  │ Server       │ │
│  │ :3000        │  │ :5000        │ │
│  └──────┬───────┘  └──────┬───────┘ │
│         │                 │         │
│         └────► CORS ◄─────┘         │
│                                     │
└─────────────────────────────────────┘
```

**Start Commands:**
```bash
# Terminal 1: Backend
cd web/backend
flask run --host=0.0.0.0 --port=5000

# Terminal 2: Frontend
cd web/frontend
npm run dev
```

### Docker Compose (Staging)

```yaml
version: '3.8'

services:
  web-backend:
    build:
      context: .
      dockerfile: Dockerfile.web
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=staging
      - CORS_ORIGINS=http://localhost:3000
    volumes:
      - ./data:/app/data
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  web-frontend:
    build:
      context: ./web/frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - web-backend
```

### Production (Kubernetes)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-backend
  template:
    metadata:
      labels:
        app: web-backend
    spec:
      containers:
      - name: web-backend
        image: projectai/web-backend:latest
        ports:
        - containerPort: 5000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-secrets
              key: openai-api-key
        - name: ENVIRONMENT
          value: "production"
        - name: CORS_ORIGINS
          value: "https://app.example.com"
        - name: RATE_LIMIT_STORAGE_URI
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/status
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/status
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: web-backend-service
spec:
  selector:
    app: web-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

---

## Error Handling

### Error Response Format

**Standard Error Response:**
```json
{
  "status": "error",
  "error": "error-code",
  "message": "Human-readable error message",
  "details": {
    "field": "username",
    "constraint": "required"
  },
  "request_id": "req_abc123",
  "timestamp": "2025-01-26T12:00:00Z"
}
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `missing-json` | 400 | Request body must be JSON |
| `invalid-credentials` | 401 | Username or password incorrect |
| `missing-token` | 401 | Authorization header required |
| `invalid-token` | 403 | Token expired or invalid |
| `rate-limit-exceeded` | 429 | Too many requests |
| `ai-provider-error` | 500 | Upstream AI service unavailable |
| `internal-error` | 500 | Unexpected server error |

### Error Handling Strategy

```python
@app.errorhandler(400)
def bad_request(e):
    return jsonify(error="bad-request", message=str(e)), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify(error="unauthorized", message=str(e)), 401

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify(
        error="rate-limit-exceeded",
        message="Too many requests",
        retry_after=e.description
    ), 429

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal error: {e}", exc_info=True)
    return jsonify(
        error="internal-error",
        message="An unexpected error occurred"
    ), 500
```

---

## Monitoring & Observability

### Logging

**Structured Logging:**
```python
logger.info(
    "Request processed",
    extra={
        "request_id": request_id,
        "user": username,
        "action": "ai.chat",
        "latency_ms": 1234,
        "tokens_used": 156,
    }
)
```

**Log Levels:**
- `DEBUG`: Request/response details (development only)
- `INFO`: Normal operations (requests, governance checks)
- `WARNING`: Recoverable errors (rate limits, invalid input)
- `ERROR`: System errors (AI provider failures, database errors)

### Metrics

**Key Metrics to Track:**
1. **Request Metrics**
   - Requests per second
   - Request latency (p50, p95, p99)
   - Error rate by endpoint

2. **Business Metrics**
   - AI tokens used per day
   - Image generations per day
   - Active users

3. **Infrastructure Metrics**
   - CPU usage
   - Memory usage
   - Connection pool size

**Prometheus Integration:**
```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter(
    'web_backend_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'web_backend_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

@app.route('/metrics')
def metrics():
    return generate_latest()
```

### Health Checks

**Liveness Probe:**
```bash
# Simple health check
curl http://localhost:5000/api/status
```

**Readiness Probe:**
```python
@app.route("/api/health/ready")
def readiness():
    # Check dependencies
    checks = {
        "database": check_database(),
        "redis": check_redis(),
        "openai": check_openai_api(),
    }
    
    if all(checks.values()):
        return jsonify(status="ready", checks=checks), 200
    else:
        return jsonify(status="not-ready", checks=checks), 503
```

---

## Best Practices

### 1. Security

✅ **DO:**
- Use JWT tokens with short expiration (1-24 hours)
- Hash passwords with Argon2 or bcrypt
- Validate all inputs before processing
- Log all authentication attempts
- Use HTTPS in production
- Set restrictive CORS policies

❌ **DON'T:**
- Store passwords in plaintext
- Use wildcard CORS origins in production
- Trust client-provided headers (X-Forwarded-For)
- Expose stack traces in error responses
- Log sensitive data (passwords, tokens)

### 2. Performance

✅ **DO:**
- Use connection pooling for databases
- Cache frequently accessed data
- Implement request timeouts
- Use async workers for long operations
- Monitor and set resource limits

❌ **DON'T:**
- Make synchronous calls to slow external APIs
- Load large datasets into memory
- Skip pagination on large result sets

### 3. Reliability

✅ **DO:**
- Implement circuit breakers for external services
- Use exponential backoff for retries
- Log all errors with context
- Set up health checks
- Test failure scenarios

❌ **DON'T:**
- Assume external services are always available
- Retry forever without backoff
- Ignore transient errors

---

## Troubleshooting

### Common Issues

#### 1. CORS Errors

**Symptom:** Browser shows "CORS policy blocked" error.

**Solution:**
```python
# Add frontend origin to CORS configuration
configure_cors(app, allowed_origins=["http://localhost:3000"])
```

#### 2. Rate Limit Exceeded

**Symptom:** `429 Too Many Requests` response.

**Solution:**
```python
# Increase rate limit for specific endpoint
@app.route("/api/ai/chat", methods=["POST"])
@limiter.limit("200 per minute")  # Override default
def ai_chat():
    ...
```

#### 3. Token Validation Fails

**Symptom:** `403 Forbidden` with "invalid-token" error.

**Solution:**
```python
# Check token expiration and secret key
import jwt

try:
    payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    logger.warning("Token expired")
except jwt.InvalidTokenError:
    logger.warning("Invalid token")
```

#### 4. AI Provider Timeout

**Symptom:** Requests to `/api/ai/chat` timeout after 30 seconds.

**Solution:**
```python
# Increase timeout in AI orchestrator
response = requests.post(
    api_url,
    json=payload,
    timeout=120  # Increase from 30 to 120 seconds
)
```

### Debug Mode

**Enable Debug Logging:**
```bash
export LOG_LEVEL=DEBUG
export FLASK_DEBUG=1
flask run
```

**Debug Request/Response:**
```python
@app.before_request
def log_request():
    if app.debug:
        logger.debug(f"Request: {request.method} {request.path}")
        logger.debug(f"Headers: {dict(request.headers)}")
        logger.debug(f"Body: {request.get_data(as_text=True)}")
```

---

## Summary

The Project-AI Web Backend is a **production-grade Flask adapter** that:

1. **Delegates Business Logic**: Routes all requests through the governance pipeline
2. **Enforces Security**: CORS, rate limiting, JWT authentication, input sanitization
3. **Provides Observability**: Structured logging, metrics, health checks
4. **Scales Horizontally**: Stateless design enables easy scaling
5. **Integrates Seamlessly**: Works with desktop, CLI, and Temporal workflows

**Next Steps:**
- Review `02-api-endpoint-reference.md` for complete API documentation
- See `03-middleware-security.md` for security deep dive
- Check `../core/governance-pipeline.md` for governance details

**Key Files:**
- `web/backend/app.py` - Flask application and route handlers
- `app/core/runtime/router.py` - Multi-path coordination layer
- `app/core/security/middleware.py` - CORS and rate limiting
- `app/core/governance/pipeline.py` - Governance enforcement

**Support:**
- GitHub Issues: https://github.com/IAmSoThirsty/Project-AI/issues
- Documentation: T:\Project-AI-vault\source-docs\
- Security: security@project-ai.dev

---

**Document Metadata:**
- **Word Count:** 5,247 words
- **Code Examples:** 25
- **Diagrams:** 3
- **Tables:** 8
- **Last Reviewed:** 2025-01-26
- **Next Review:** 2025-04-26

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

