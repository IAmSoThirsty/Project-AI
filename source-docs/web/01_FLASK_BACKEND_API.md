---
type: api-reference
module: web.backend
tags: [flask, rest-api, backend, governance-pipeline, authentication]
created: 2026-04-20
status: production
related_systems: [runtime-router, ai-orchestrator, security-middleware]
stakeholders: [backend-team, integration-team, security-team]
platform: web
dependencies: [flask, werkzeug, app.core.runtime.router]
---

# Flask Backend API Reference

**Module:** `web/backend/app.py`  
**Purpose:** Web interface adapter routing Flask requests through governance pipeline  
**Architecture:** Thin adapter preserving web functionality with governance compliance

---

## Architecture Overview

### Design Philosophy

The Flask backend is a **thin adapter** that routes all requests through the runtime governance pipeline:

```
Old: Flask → Direct business logic
New: Flask → Router → Governance → AI Orchestrator → Systems
```

**Key Principles:**
- Zero business logic in routes (all logic in core systems)
- Every request flows through governance validation
- Secure by default (CORS, rate limiting, JWT)
- Backend-agnostic (can swap Flask for FastAPI without changing core)

### Request Flow

```
1. Client HTTP Request
   ↓
2. Flask Route Handler (@app.route)
   ↓
3. Security Middleware (CORS, rate limiting)
   ↓
4. route_request(source="web", payload={...})
   ↓
5. Runtime Router → Governance → AI Orchestrator
   ↓
6. Core System Execution (ai_systems.py, user_manager.py, etc.)
   ↓
7. JSON Response to Client
```

---

## API Endpoints

### 1. Health Check

**Endpoint:** `GET /api/status`  
**Authentication:** None  
**Purpose:** Backend health verification

**Response:**
```json
{
  "status": "ok",
  "component": "web-backend"
}
```

**Status Codes:**
- `200 OK` - Backend is operational

**Usage:**
```typescript
// Frontend health check
const response = await fetch('/api/status');
const { status } = await response.json();
```

---

### 2. User Authentication

**Endpoint:** `POST /api/auth/login`  
**Authentication:** None (this IS the auth endpoint)  
**Purpose:** Authenticate user and receive JWT token

**Request Body:**
```json
{
  "username": "admin",
  "password": "open-sesame"
}
```

**Success Response (200):**
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

**Error Response (401):**
```json
{
  "status": "error",
  "success": false,
  "error": "invalid-credentials",
  "message": "Authentication failed"
}
```

**Error Response (400):**
```json
{
  "error": "missing-json",
  "message": "Request must include JSON body."
}
```

**Governance Pipeline:**
```python
route_request(
    source="web",
    payload={
        "action": "user.login",
        "username": payload.get("username"),
        "password": payload.get("password"),
    },
)
```

**Security Features:**
- Argon2 password hashing (via governance pipeline)
- JWT token generation with expiration
- Rate limiting (10 attempts per minute via middleware)
- Audit logging of all login attempts

**Demo Credentials:**
```
admin / open-sesame (superuser role)
guest / letmein (user role)
```

---

### 3. AI Chat

**Endpoint:** `POST /api/ai/chat`  
**Authentication:** Required (Bearer token)  
**Purpose:** Send chat messages to AI and receive responses

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Request Body:**
```json
{
  "prompt": "What is the Four Laws ethics framework?",
  "model": "gpt-4",
  "provider": "openai"
}
```

**Success Response (200):**
```json
{
  "result": {
    "response": "The Four Laws is an immutable ethics framework...",
    "model": "gpt-4",
    "tokens_used": 342
  },
  "metadata": {
    "execution_time_ms": 1250,
    "provider": "openai",
    "governance_checks": ["four_laws", "content_filter"]
  }
}
```

**Error Response (500):**
```json
{
  "error": "AI request failed"
}
```

**Error Response (400):**
```json
{
  "error": "missing-json"
}
```

**Governance Pipeline:**
```python
route_request(
    source="web",
    payload={
        "action": "ai.chat",
        "task_type": "chat",
        "prompt": payload.get("prompt", ""),
        "model": payload.get("model"),
        "provider": payload.get("provider"),
        "token": token,
    },
)
```

**Features:**
- Multi-provider support (OpenAI, Anthropic, fallback)
- Automatic token extraction from Authorization header
- Four Laws ethics validation on all prompts
- Response streaming support (future)

---

### 4. AI Image Generation

**Endpoint:** `POST /api/ai/image`  
**Authentication:** Required (Bearer token)  
**Purpose:** Generate images using AI models (DALL-E 3, Stable Diffusion)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Request Body:**
```json
{
  "prompt": "A futuristic cityscape at sunset",
  "model": "dall-e-3",
  "provider": "openai",
  "size": "1024x1024"
}
```

**Success Response (200):**
```json
{
  "result": {
    "image_url": "https://example.com/generated-image.png",
    "prompt": "A futuristic cityscape at sunset",
    "model": "dall-e-3",
    "size": "1024x1024",
    "revised_prompt": "A futuristic cityscape at sunset with neon lights"
  },
  "metadata": {
    "execution_time_ms": 8500,
    "provider": "openai",
    "content_filter_passed": true
  }
}
```

**Error Response (500):**
```json
{
  "error": "Image generation failed"
}
```

**Governance Pipeline:**
```python
route_request(
    source="web",
    payload={
        "action": "ai.image",
        "task_type": "image",
        "prompt": payload.get("prompt", ""),
        "model": payload.get("model"),
        "provider": payload.get("provider"),
        "size": payload.get("size", "1024x1024"),
        "token": token,
    },
)
```

**Supported Sizes:**
- `1024x1024` (default)
- `1024x1792` (portrait)
- `1792x1024` (landscape)

**Content Filtering:**
- 15 blocked keywords (violence, NSFW, hate speech)
- Automatic safety negative prompts
- Human review for flagged content

---

### 5. AI Persona Update

**Endpoint:** `POST /api/persona/update`  
**Authentication:** Required (Bearer token)  
**Purpose:** Update AI personality traits (8 traits from AIPersona system)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Request Body:**
```json
{
  "trait": "curiosity",
  "value": 0.85
}
```

**Valid Traits:**
- `curiosity` (0.0 - 1.0)
- `empathy` (0.0 - 1.0)
- `formality` (0.0 - 1.0)
- `humor` (0.0 - 1.0)
- `optimism` (0.0 - 1.0)
- `creativity` (0.0 - 1.0)
- `assertiveness` (0.0 - 1.0)
- `patience` (0.0 - 1.0)

**Success Response (200):**
```json
{
  "success": true,
  "result": {
    "trait": "curiosity",
    "old_value": 0.75,
    "new_value": 0.85,
    "state_saved": true
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Invalid trait name or value"
}
```

**Governance Pipeline:**
```python
route_request(
    source="web",
    payload={
        "action": "persona.update",
        "trait": payload.get("trait"),
        "value": payload.get("value"),
        "token": token,
    },
)
```

**State Persistence:**
- Changes saved to `data/ai_persona/state.json`
- Real-time updates reflected in desktop app
- Audit log of all trait changes

---

## Security Middleware

### CORS Configuration

**Function:** `configure_cors(app)`  
**Location:** `app.core.security.middleware`

**Features:**
- Whitelist-based origin validation
- Credentials support (cookies, JWT)
- Pre-flight request handling
- Custom headers allowed

**Configuration:**
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://yourdomain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Length", "X-Request-ID"],
        "supports_credentials": True,
        "max_age": 3600
    }
})
```

### Rate Limiting

**Function:** `configure_rate_limiting(app)`  
**Location:** `app.core.security.middleware`

**Limits:**
- `/api/auth/login`: 10 requests per minute per IP
- `/api/ai/*`: 30 requests per minute per user
- `/api/*`: 100 requests per minute per IP

**Response on Rate Limit (429):**
```json
{
  "error": "rate-limit-exceeded",
  "message": "Too many requests. Try again in 30 seconds.",
  "retry_after": 30
}
```

---

## Error Handling

### Global Error Handler

**Implementation:**
```python
@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception(f"Unhandled exception: {e}")
    return jsonify(
        error="internal-server-error",
        message="An unexpected error occurred.",
        debug=str(e) if app.debug else None
    ), 500
```

**Error Response Format:**
```json
{
  "error": "error-code",
  "message": "Human-readable error message",
  "debug": "Stack trace (debug mode only)"
}
```

### Standard Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `missing-json` | 400 | Request body missing or invalid JSON |
| `invalid-credentials` | 401 | Username/password incorrect |
| `unauthorized` | 401 | Missing or invalid token |
| `forbidden` | 403 | Insufficient permissions |
| `rate-limit-exceeded` | 429 | Too many requests |
| `internal-server-error` | 500 | Unhandled exception |

---

## Development & Testing

### Running the Backend

```bash
# Development mode (port 5000)
cd web/backend
python app.py

# Production mode (gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Testing

**Test Files:**
- `tests/test_web_backend.py` (14 tests)

**Run Tests:**
```bash
pytest tests/test_web_backend.py -v
```

**Coverage:**
```bash
pytest tests/test_web_backend.py --cov=web.backend
```

### Environment Variables

**Required:**
```bash
# .env file
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-...
HUGGINGFACE_API_KEY=hf_...
```

---

## Deployment

### Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web.backend.app:app"]
```

**Docker Compose:**
```yaml
services:
  backend:
    build: ./web/backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data:/app/data
```

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Generate secure `SECRET_KEY` (32+ bytes)
- [ ] Configure CORS whitelist (remove `localhost`)
- [ ] Enable HTTPS (SSL/TLS certificates)
- [ ] Set up reverse proxy (Nginx/Caddy)
- [ ] Configure logging (JSON structured logs)
- [ ] Enable health checks (`/api/status`)
- [ ] Set up monitoring (Sentry, Prometheus)
- [ ] Database migration (if applicable)
- [ ] Backup strategy (daily database dumps)

---

## Best Practices

### 1. Always Use Governance Pipeline

**❌ Bad (Direct business logic):**
```python
@app.route("/api/user/profile")
def get_profile():
    user = UserManager.get_user(username)  # Direct call
    return jsonify(user)
```

**✅ Good (Governance pipeline):**
```python
@app.route("/api/user/profile")
def get_profile():
    response = route_request(
        source="web",
        payload={"action": "user.profile", "token": token}
    )
    return jsonify(response["result"]), 200
```

### 2. Extract Token from Headers

```python
auth_header = request.headers.get("Authorization", "")
token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None
```

### 3. Validate JSON Payload

```python
payload = request.get_json(silent=True)
if not payload:
    return jsonify(error="missing-json"), 400
```

### 4. Use Consistent Error Format

```python
return jsonify(
    status="error",
    error="error-code",
    message="Human-readable message"
), status_code
```

### 5. Log All Exceptions

```python
try:
    # operation
except Exception as e:
    logger.exception(f"Error in endpoint: {e}")
    return jsonify(error="internal-server-error"), 500
```

---

## Integration with Frontend

### Axios Client Setup

**Frontend (`lib/api-client.ts`):**
```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to all requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### Example API Call

```typescript
// Login
const response = await apiClient.post('/api/auth/login', {
  username: 'admin',
  password: 'open-sesame',
});
localStorage.setItem('authToken', response.data.token);

// AI Chat
const chatResponse = await apiClient.post('/api/ai/chat', {
  prompt: 'Hello, AI!',
  model: 'gpt-4',
});
console.log(chatResponse.data.result.response);
```

---

## Troubleshooting

### Issue: CORS Errors

**Symptom:** `Access-Control-Allow-Origin` error in browser console

**Solution:**
```python
# Add frontend origin to CORS whitelist
configure_cors(app, origins=["http://localhost:3000"])
```

### Issue: 401 Unauthorized

**Symptom:** All authenticated endpoints return 401

**Solution:**
1. Verify token is sent in `Authorization` header
2. Check token format: `Bearer <token>`
3. Confirm token hasn't expired

### Issue: 500 Internal Server Error

**Symptom:** Unhandled exceptions crashing the server

**Solution:**
1. Check logs: `tail -f logs/backend.log`
2. Enable debug mode: `FLASK_ENV=development`
3. Review stack trace in response

---

## Related Documentation

- [React Frontend Integration](./02_REACT_FRONTEND.md)
- [Deployment Guide](./03_DEPLOYMENT_GUIDE.md)
- [Security Best Practices](./04_SECURITY_PRACTICES.md)
- [Runtime Router](../core/RUNTIME_ROUTER.md)
- [AI Orchestrator](../core/AI_ORCHESTRATOR.md)

---

**Last Updated:** 2026-04-20  
**Maintainer:** Backend Team  
**Review Cycle:** Quarterly
