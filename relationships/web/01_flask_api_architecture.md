# Flask API Architecture Relationships

**System:** Flask Backend API  
**Location:** `web/backend/app.py`  
**Type:** HTTP REST API  

## Overview

The Flask API serves as a **thin adapter layer** that routes all HTTP requests through the governance pipeline. It does NOT contain business logic - all functionality flows through the centralized runtime router.

## Core Architecture Pattern

```
HTTP Request → Flask Endpoint → Runtime Router → Governance Pipeline → AI Orchestrator → Core Systems → State
```

### Architectural Principle

**Old behavior:** Flask → Direct business logic  
**New behavior:** Flask → Router → Governance → AI Orchestrator → Systems

This ensures consistent governance across ALL execution paths (web, desktop, CLI, agents).

## Primary Relationships

### 1. **Flask App → Runtime Router**

**Relationship:** Every endpoint delegates to router  
**Direction:** Flask → `app.core.runtime.router.route_request()`  
**Purpose:** Unified governance entry point

```python
# Pattern used by ALL endpoints
response = route_request(
    source="web",
    payload={
        "action": "user.login",  # Whitelisted action
        "username": payload.get("username"),
        "password": payload.get("password"),
    },
)
```

**Key Insight:** Flask has ZERO business logic. It only:
- Validates JSON presence
- Extracts Authorization headers
- Calls `route_request()`
- Transforms response to HTTP format

### 2. **Flask App → Security Middleware**

**Relationship:** Initialization-time configuration  
**Direction:** Flask → `app.core.security.middleware`  
**Components:**
- `configure_cors(app)` - CORS with strict origin control
- `configure_rate_limiting(app)` - Request rate limits

**CORS Configuration:**
```python
allowed_origins = [
    "http://localhost:3000",  # Next.js dev
    "http://localhost:5173",  # Vite dev
]
```

**Rate Limits:**
- Authentication: 5/minute
- API calls: 100/minute
- Image generation: 10/hour

### 3. **Flask Endpoints → Governance Pipeline**

**Relationship:** Indirect via router  
**Direction:** Flask → Router → `app.core.governance.pipeline.enforce_pipeline()`  
**Purpose:** Six-phase governance enforcement

**Governance Phases:**
1. **Validation** - Input sanitization, type checking
2. **Simulation** - Shadow execution for impact analysis
3. **Gate** - Authorization checks (Four Laws, user permissions)
4. **Execution** - Actual operation via AI orchestrator
5. **Commit** - State persistence with rollback capability
6. **Logging** - Complete audit trail

### 4. **Flask Endpoints → AI Orchestrator**

**Relationship:** Indirect via governance pipeline  
**Direction:** Flask → Router → Governance → `app.core.ai.orchestrator.run_ai()`  
**Purpose:** AI provider fallback coordination

**Provider Fallback Chain:**
1. OpenAI (default, most reliable)
2. HuggingFace (fallback)
3. Perplexity (web-enhanced fallback)
4. Local models (offline fallback)

## Endpoint Inventory

### Authentication Endpoints

#### `/api/auth/login` (POST)
- **Action:** `user.login`
- **Governance:** Routes through auth validation
- **Returns:** JWT token + user profile
- **Security:** Argon2 password hashing, JWT generation
- **Rate Limit:** 5/minute

**Request Flow:**
```
POST /api/auth/login
  → route_request(source="web", action="user.login")
    → enforce_pipeline(context)
      → UserManager.authenticate()
        → Argon2 verification
        → JWT generation
  ← {token, user: {username, role}}
```

### AI Endpoints

#### `/api/ai/chat` (POST)
- **Action:** `ai.chat`
- **Task Type:** Chat completion
- **Requires:** Bearer token authentication
- **Governance:** Four Laws ethics validation
- **Provider:** OpenAI → HuggingFace fallback

**Request Flow:**
```
POST /api/ai/chat + Bearer token
  → route_request(source="web", action="ai.chat")
    → enforce_pipeline(context)
      → AI Orchestrator
        → OpenAI GPT-4 (primary)
        → HuggingFace (fallback)
  ← {result: "AI response", metadata: {provider, model, timestamp}}
```

#### `/api/ai/image` (POST)
- **Action:** `ai.image`
- **Task Type:** Image generation
- **Requires:** Bearer token authentication
- **Backends:** HF Stable Diffusion 2.1, OpenAI DALL-E 3
- **Security:** 15+ blocked keywords, safety negative prompts

**Request Flow:**
```
POST /api/ai/image + Bearer token
  → route_request(source="web", action="ai.image")
    → enforce_pipeline(context)
      → Content filtering (15 blocked keywords)
      → AI Orchestrator
        → Stable Diffusion 2.1 (default)
        → DALL-E 3 (fallback)
  ← {result: {image_url, style, size}, metadata: {provider, generation_time}}
```

#### `/api/persona/update` (POST)
- **Action:** `persona.update`
- **Modifies:** AI personality traits (8 configurable)
- **State:** Persisted to `data/ai_persona/state.json`
- **Requires:** Bearer token authentication

**Request Flow:**
```
POST /api/persona/update + Bearer token
  → route_request(source="web", action="persona.update")
    → enforce_pipeline(context)
      → AIPersona.update_trait(trait, value)
        → Validate trait range (0.0-1.0)
        → Update state
        → _save_state()
  ← {success: true, result: {trait, new_value}}
```

### System Endpoints

#### `/api/status` (GET)
- **Action:** Health check
- **Authentication:** None required
- **Purpose:** Service discovery, uptime monitoring

**Response:**
```json
{
  "status": "ok",
  "component": "web-backend"
}
```

## Security Architecture

### Request Validation Layer

**Three-Stage Validation:**

1. **Flask Layer (Outer):**
   - JSON body presence check
   - Content-Type validation
   - Authorization header extraction

2. **Router Layer (Middle):**
   - Source identification (`source="web"`)
   - Action whitelisting (VALID_ACTIONS registry)
   - Context enrichment (timestamp, metadata)

3. **Governance Layer (Inner):**
   - Input sanitization (dangerous characters)
   - Type validation (schemas)
   - Authorization checks (JWT validation)
   - Four Laws ethics validation

### CORS Policy

**Strict Origin Control:**
- Whitelisted origins only (localhost:3000, localhost:5173)
- Credentials support enabled
- Methods: GET, POST, PUT, DELETE, OPTIONS
- Headers: Content-Type, Authorization

### Rate Limiting

**Endpoint-Specific Limits:**
```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"],
    storage_uri="memory://",
)
```

**Critical Endpoints:**
- `/api/auth/login`: 5/minute (brute-force prevention)
- `/api/ai/image`: 10/hour (resource-intensive)
- General API: 100/minute (DDoS prevention)

## Error Handling

### Standard Error Response Format

```json
{
  "status": "error",
  "success": false,
  "error": "error-code",
  "message": "Human-readable error message"
}
```

### HTTP Status Codes

- **200 OK:** Successful operation
- **400 Bad Request:** Missing/invalid JSON
- **401 Unauthorized:** Invalid credentials or token
- **500 Internal Server Error:** AI request failed or system error

### Error Propagation

```
Exception in Core System
  → Caught by Governance Pipeline
    → Logged with full context
      → Converted to error response
        → Returned to Flask
          → HTTP 500 + error details
```

## Dependencies

### Required Packages

```python
# Core
from flask import Flask, jsonify, request

# Security
from app.core.security.middleware import configure_cors, configure_rate_limiting

# Routing
from app.core.runtime.router import route_request
```

### Optional Packages (Middleware)

- `flask-cors` - CORS support
- `flask-limiter` - Rate limiting
- Both checked at runtime with graceful degradation

## Configuration

### Environment Variables

**Required:**
- `OPENAI_API_KEY` - OpenAI API authentication
- `HUGGINGFACE_API_KEY` - HuggingFace API authentication

**Optional:**
- `FLASK_ENV=development` - Development mode
- `FLASK_DEBUG=1` - Debug logging

### Server Configuration

```python
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",  # All interfaces
        port=5000,       # Standard Flask port
        debug=True       # Development only
    )
```

**Production:** Use gunicorn or uwsgi (not Flask dev server)

## Testing Hooks

### Manual Testing

```bash
# Health check
curl http://localhost:5000/api/status

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"open-sesame"}'

# AI Chat (with token)
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"prompt":"Hello, AI!","model":"gpt-4"}'
```

### Integration Testing

All endpoints flow through governance pipeline, so testing should verify:
1. Valid requests succeed
2. Invalid JSON rejected (400)
3. Missing auth rejected (401)
4. Rate limits enforced (429)
5. CORS headers present
6. Audit logs created

## Key Design Decisions

### Why Thin Adapter?

**Problem:** Old code had business logic scattered across Flask routes  
**Solution:** Flask only handles HTTP concerns, all logic in core systems  
**Benefit:** Consistent governance across web/desktop/CLI

### Why Router Pattern?

**Problem:** Each interface (web/desktop/CLI) had different validation  
**Solution:** All interfaces route through same governance pipeline  
**Benefit:** Single source of truth for authorization/ethics

### Why Action Whitelist?

**Problem:** Arbitrary action strings could bypass validation  
**Solution:** VALID_ACTIONS registry in governance pipeline  
**Benefit:** Prevents unknown/malicious actions

## Performance Considerations

### Request Path Length

**Typical request traverses:**
1. Flask endpoint (< 1ms)
2. Router (< 1ms)
3. Governance pipeline (5-10ms)
   - Validation (1ms)
   - Simulation (2ms)
   - Gate (2ms)
   - Execution (varies)
   - Commit (2ms)
   - Logging (1ms)
4. AI orchestrator (varies by provider)
   - OpenAI: 200-2000ms
   - HuggingFace: 5000-20000ms
   - Local: 100-500ms

**Total overhead:** ~15ms (excluding AI provider latency)

### Caching Strategy

**NOT implemented at Flask layer** - caching handled by:
- AI orchestrator (provider-level caching)
- Core systems (state caching)
- External reverse proxy (if deployed)

### Async Considerations

**Current:** Synchronous Flask (blocking requests)  
**Future:** Consider Flask-Async for concurrent request handling  
**Impact:** AI requests can block other requests during generation

## Deployment Patterns

### Development

```bash
python web/backend/app.py
# Runs on http://0.0.0.0:5000
```

### Docker

```dockerfile
FROM python:3.11-slim
COPY web/backend /app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

### Production

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 web.backend.app:app
```

**Workers:** 4-8 workers for CPU-bound workload  
**Timeout:** 300s for image generation  
**Keep-alive:** 5s for persistent connections

## Monitoring Integration

### Logging

All requests logged by governance pipeline:
```python
logger.info(f"Routing request from web: {payload.get('action')}")
```

### Audit Trail

Every request creates audit log entry:
- Source: "web"
- Action: whitelisted action string
- User: JWT username (if authenticated)
- Timestamp: ISO 8601 UTC
- Result: success/error/blocked
- Duration: milliseconds

### Health Checks

```bash
# Kubernetes liveness probe
curl -f http://localhost:5000/api/status || exit 1

# Readiness probe (check AI orchestrator)
curl -f http://localhost:5000/api/ai/chat \
  -H "Authorization: Bearer <token>" \
  -d '{"prompt":"health check"}' || exit 1
```

## Related Systems

- **Runtime Router:** `src/app/core/runtime/router.py`
- **Governance Pipeline:** `src/app/core/governance/pipeline.py`
- **AI Orchestrator:** `src/app/core/ai/orchestrator.py`
- **Security Middleware:** `src/app/core/security/middleware.py`
- **User Manager:** `src/app/core/user_manager.py`
- **AI Persona:** `src/app/core/ai_systems.py` (AIPersona class)

## Migration Notes

### Pre-Governance Architecture

**Before:**
```python
@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    # Direct OpenAI call
    response = openai.ChatCompletion.create(...)
    return jsonify(response)
```

**After:**
```python
@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    # Route through governance pipeline
    response = route_request(
        source="web",
        payload={"action": "ai.chat", "prompt": payload.get("prompt")},
    )
    return jsonify(result=response["result"])
```

### Backward Compatibility

**Maintained:** All endpoints preserve same URLs and request/response formats  
**Changed:** Internal routing (transparent to clients)  
**Breaking:** None - clients unaware of governance pipeline

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-XX  
**Maintainer:** Project-AI Team  
