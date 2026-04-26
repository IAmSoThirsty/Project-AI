# API Routes & Controllers Relationships

**System:** Flask REST API + Governance Pipeline Routing  
**Pattern:** Thin adapter → Router → Governance → Controllers  

## Overview

Project-AI uses a **hybrid routing architecture** where Flask endpoints act as thin adapters, routing all requests through a centralized governance pipeline to domain-specific controllers.

## Routing Architecture

### Three-Layer Routing Model

```
Layer 1: Flask Routes (HTTP Interface)
   ↓
Layer 2: Runtime Router (Governance Entry Point)
   ↓
Layer 3: Domain Controllers (Business Logic)
```

## Layer 1: Flask Routes

### Route Registry

**Location:** `web/backend/app.py`

#### Authentication Routes

##### `POST /api/auth/login`
- **Controller:** UserManager.authenticate()
- **Action:** `user.login`
- **Auth:** Public
- **Rate Limit:** 5/minute
- **Returns:** JWT token + user profile

**Request:**
```json
{
  "username": "admin",
  "password": "open-sesame"
}
```

**Response:**
```json
{
  "status": "ok",
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "username": "admin",
    "role": "admin"
  }
}
```

#### AI Routes

##### `POST /api/ai/chat`
- **Controller:** AIOrchestrator.run_ai()
- **Action:** `ai.chat`
- **Auth:** Required (Bearer token)
- **Rate Limit:** 30/minute
- **Provider Fallback:** OpenAI → HuggingFace → Perplexity → Local

**Request:**
```json
{
  "prompt": "Explain quantum computing",
  "model": "gpt-4",
  "provider": "openai"
}
```

**Response:**
```json
{
  "result": "Quantum computing is...",
  "metadata": {
    "provider": "openai",
    "model": "gpt-4",
    "tokens": 150,
    "latency_ms": 1200
  }
}
```

##### `POST /api/ai/image`
- **Controller:** ImageGenerator.generate()
- **Action:** `ai.image`
- **Auth:** Required (Bearer token)
- **Rate Limit:** 10/hour
- **Backends:** Stable Diffusion 2.1, DALL-E 3

**Request:**
```json
{
  "prompt": "Cyberpunk city at night",
  "size": "1024x1024",
  "style": "cyberpunk",
  "provider": "huggingface"
}
```

**Response:**
```json
{
  "result": {
    "image_url": "data:image/png;base64,...",
    "style": "cyberpunk",
    "size": "1024x1024"
  },
  "metadata": {
    "provider": "huggingface",
    "model": "stable-diffusion-2-1",
    "generation_time_ms": 15000
  }
}
```

#### Persona Routes

##### `POST /api/persona/update`
- **Controller:** AIPersona.update_trait()
- **Action:** `persona.update`
- **Auth:** Required (Bearer token)
- **Rate Limit:** 20/minute
- **State:** Persisted to data/ai_persona/state.json

**Request:**
```json
{
  "trait": "creativity",
  "value": 0.8
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "trait": "creativity",
    "old_value": 0.5,
    "new_value": 0.8
  }
}
```

#### System Routes

##### `GET /api/status`
- **Controller:** None (direct response)
- **Action:** Health check
- **Auth:** Public
- **Purpose:** Service discovery, uptime monitoring

**Response:**
```json
{
  "status": "ok",
  "component": "web-backend"
}
```

## Layer 2: Runtime Router

### Router Function

**Location:** `src/app/core/runtime/router.py`

**Signature:**
```python
def route_request(source: ExecutionSource, payload: dict[str, Any]) -> dict[str, Any]
```

**ExecutionSource Types:**
- `"web"` - Flask HTTP requests
- `"desktop"` - PyQt6 GUI actions
- `"cli"` - Command-line interface
- `"agent"` - AI agent operations
- `"temporal"` - Temporal workflow activities
- `"test"` - Unit/integration tests

### Routing Phases

#### Phase 1: Context Enrichment

```python
context = {
    "source": source,              # "web"
    "payload": payload,            # Original request data
    "action": payload.get("action"),  # "ai.chat"
    "user": payload.get("user", {}),  # User info from JWT
    "config": payload.get("config", {}),  # Config overrides
    "timestamp": _get_timestamp(),     # ISO 8601 UTC
}
```

#### Phase 2: Governance Pipeline

```python
result = enforce_pipeline(context)
```

**Governance Phases:**
1. **Validation** - Input sanitization, type checking
2. **Simulation** - Shadow execution for impact analysis
3. **Gate** - Authorization checks (Four Laws, permissions)
4. **Execution** - Actual operation via controllers
5. **Commit** - State persistence with rollback
6. **Logging** - Complete audit trail

#### Phase 3: Response Formation

```python
return {
    "status": "success",
    "result": result,
    "metadata": {
        "source": source,
        "action": context["action"],
        "timestamp": context["timestamp"],
    },
}
```

## Layer 3: Domain Controllers

### Controller Registry

#### UserManager Controller

**Location:** `src/app/core/user_manager.py`

**Actions:**
- `user.login` → `authenticate(username, password)`
- `user.create` → `create_user(username, password, role)`
- `user.update` → `update_user(username, updates)`
- `user.delete` → `delete_user(username)`

**State Management:**
- Persistence: `data/users.json`
- Format: JSON array of user objects
- Locking: File-level locking (JSON atomic writes)

#### AIOrchestrator Controller

**Location:** `src/app/core/ai/orchestrator.py`

**Actions:**
- `ai.chat` → `run_ai(AIRequest(task_type="chat", ...))`
- `ai.image` → `run_ai(AIRequest(task_type="image", ...))`
- `ai.code` → `run_ai(AIRequest(task_type="completion", ...))`
- `ai.analyze` → `run_ai(AIRequest(task_type="analysis", ...))`

**Provider Fallback:**
```python
providers = ["openai", "huggingface", "perplexity", "local"]

for provider in providers:
    try:
        response = _call_provider(provider, request)
        if response.status == "success":
            return response
    except Exception as e:
        last_error = e
        continue
```

#### AIPersona Controller

**Location:** `src/app/core/ai_systems.py` (AIPersona class)

**Actions:**
- `persona.update` → `update_trait(trait, value)`
- `persona.query` → `get_current_state()`
- `persona.reset` → `reset_to_defaults()`

**State Management:**
- Persistence: `data/ai_persona/state.json`
- 8 Traits: creativity, empathy, humor, formality, curiosity, caution, assertiveness, optimism
- Mood tracking: positive, neutral, negative

#### ImageGenerator Controller

**Location:** `src/app/core/image_generator.py`

**Actions:**
- `ai.image` → `generate(prompt, backend, style, size)`

**Content Filtering:**
```python
BLOCKED_KEYWORDS = [
    "violence", "gore", "nsfw", "explicit",
    "hate", "discrimination", "illegal",
    # ... 15+ keywords total
]

def check_content_filter(self, prompt: str) -> tuple[bool, str]:
    for keyword in BLOCKED_KEYWORDS:
        if keyword in prompt.lower():
            return False, f"Blocked keyword: {keyword}"
    return True, ""
```

**Style Presets:**
```python
STYLE_PRESETS = {
    "photorealistic": "photorealistic, high detail, 8k",
    "digital_art": "digital art, trending on artstation",
    "oil_painting": "oil painting, canvas, brushstrokes",
    "watercolor": "watercolor, soft colors, artistic",
    "anime": "anime style, manga, cel shaded",
    "sketch": "pencil sketch, hand drawn, rough lines",
    "abstract": "abstract art, geometric, non-representational",
    "cyberpunk": "cyberpunk, neon, futuristic, dystopian",
    "fantasy": "fantasy art, magical, ethereal",
    "minimalist": "minimalist, simple, clean lines",
}
```

## Action Whitelisting

### Valid Actions Registry

**Location:** `src/app/core/governance/pipeline.py`

```python
VALID_ACTIONS = {
    # AI Operations
    "ai.chat", "ai.image", "ai.code", "ai.analyze",
    
    # User Management
    "user.login", "user.logout", "user.create", "user.update", "user.delete",
    
    # Persona Operations
    "persona.update", "persona.query", "persona.reset",
    
    # Agent Operations
    "agent.execute", "agent.plan", "agent.validate",
    
    # Temporal Operations
    "temporal.workflow.validate", "temporal.workflow.execute",
    "temporal.activity.validate", "temporal.activity.execute",
    
    # System Operations
    "system.status", "system.config", "system.shutdown",
    
    # Data Operations
    "data.query", "data.update", "data.export",
    
    # Learning Operations
    "learning.request", "learning.approve", "learning.deny",
    
    # Dashboard Operations (governed desktop actions)
    "codex.fix", "codex.activate", "codex.qa",
    "access.grant", "audit.export", "agents.toggle",
}
```

### Action Metadata

```python
ACTION_METADATA = {
    "ai.chat": {
        "requires_auth": True,
        "rate_limit": 30,
        "resource_intensive": False
    },
    "ai.image": {
        "requires_auth": True,
        "rate_limit": 10,
        "resource_intensive": True
    },
    "user.login": {
        "requires_auth": False,
        "rate_limit": 5,
        "resource_intensive": False
    },
    "user.delete": {
        "requires_auth": True,
        "admin_only": True,
        "resource_intensive": False
    },
    "system.shutdown": {
        "requires_auth": True,
        "admin_only": True,
        "resource_intensive": False
    },
}
```

## Request Flow Examples

### Example 1: AI Chat Request

```
1. React Component
   LoginForm → useAuthStore.login("admin", "password")

2. Fetch API Call
   POST http://localhost:5000/api/auth/login
   Body: {"username": "admin", "password": "open-sesame"}

3. Flask Endpoint
   @app.route("/api/auth/login", methods=["POST"])
   def login():
       payload = request.get_json()
       response = route_request(source="web", payload={
           "action": "user.login",
           "username": payload["username"],
           "password": payload["password"]
       })
       return jsonify(response)

4. Runtime Router
   route_request(source="web", payload={...})
   → context = {source: "web", action: "user.login", ...}
   → enforce_pipeline(context)

5. Governance Pipeline
   enforce_pipeline(context)
   → _validate(context)      # Input sanitization
   → _simulate(context)      # Impact analysis
   → _gate(context)          # Authorization
   → _execute(context)       # Business logic
   → _commit(context, result) # State persistence
   → _log(context, result)   # Audit trail

6. UserManager Controller
   UserManager.authenticate(username, password)
   → Load data/users.json
   → Find user by username
   → Verify password with Argon2
   → Generate JWT token
   → Return {token, user}

7. Response Propagation
   Governance → Router → Flask → React
   {
     "status": "success",
     "result": {
       "token": "eyJhbGc...",
       "user": {"username": "admin", "role": "admin"}
     },
     "metadata": {"source": "web", "action": "user.login"}
   }

8. React State Update
   useAuthStore.setState({
     user: data.user,
     token: data.token,
     isAuthenticated: true
   })
   localStorage.setItem("token", data.token)
   router.push("/dashboard")
```

### Example 2: Image Generation Request

```
1. React Dashboard
   ImageGenerationTab → Submit form

2. Fetch API Call
   POST http://localhost:5000/api/ai/image
   Headers: {Authorization: "Bearer eyJhbGc..."}
   Body: {
     "prompt": "Cyberpunk city at night",
     "size": "1024x1024",
     "style": "cyberpunk"
   }

3. Flask Endpoint
   @app.route("/api/ai/image", methods=["POST"])
   def ai_image():
       token = extract_bearer_token(request)
       payload = request.get_json()
       
       response = route_request(source="web", payload={
           "action": "ai.image",
           "task_type": "image",
           "prompt": payload["prompt"],
           "size": payload["size"],
           "token": token
       })
       
       return jsonify(response)

4. Runtime Router
   route_request(source="web", payload={...})
   → enforce_pipeline(context)

5. Governance Pipeline
   _validate(context)
   → Check action in VALID_ACTIONS
   → Check requires_auth (yes)
   → Sanitize prompt input
   
   _gate(context)
   → Validate JWT token
   → Extract user from token
   → Check Four Laws (harmlessness)
   
   _execute(context)
   → Route to AIOrchestrator
   → Task type: "image"
   → Provider: auto-fallback

6. AI Orchestrator
   run_ai(AIRequest(
       task_type="image",
       prompt="Cyberpunk city at night",
       provider=None  # Auto-fallback
   ))
   
   → Try OpenAI DALL-E 3
   → Try HuggingFace Stable Diffusion
   → Return first successful result

7. Image Generator
   generate(prompt, backend="huggingface", style="cyberpunk")
   → check_content_filter(prompt)  # ✓ Pass
   → Apply style preset: "cyberpunk, neon, futuristic"
   → Call HuggingFace API
   → Receive image bytes
   → Convert to base64
   → Save to generation history
   → Return image_url

8. Response Propagation
   Governance → Router → Flask → React
   {
     "status": "success",
     "result": {
       "image_url": "data:image/png;base64,...",
       "style": "cyberpunk",
       "size": "1024x1024"
     },
     "metadata": {
       "provider": "huggingface",
       "model": "stable-diffusion-2-1",
       "generation_time_ms": 15000
     }
   }

9. React UI Update
   Display image in ImageGenerationRightPanel
   Show metadata (provider, generation time)
   Enable save/copy buttons
```

## Error Handling

### Error Propagation Chain

```
Controller Exception
  ↓
Governance Pipeline Catch
  ↓
Router Error Response
  ↓
Flask JSON Error
  ↓
React Error Display
```

### Error Response Format

```json
{
  "status": "error",
  "result": null,
  "error": "Invalid credentials",
  "metadata": {
    "source": "web",
    "action": "user.login",
    "timestamp": "2026-01-15T10:30:00Z"
  }
}
```

### HTTP Status Codes

- `200 OK` - Success
- `400 Bad Request` - Invalid JSON or missing fields
- `401 Unauthorized` - Invalid credentials or token
- `403 Forbidden` - Four Laws violation or insufficient permissions
- `404 Not Found` - Unknown route
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - System failure

## Performance Optimization

### Request Path Overhead

**Total overhead:** ~15ms (excluding controller execution)
- Flask endpoint: < 1ms
- Router: < 1ms
- Governance pipeline: 5-10ms
  - Validation: 1ms
  - Simulation: 2ms
  - Gate: 2ms
  - Execution: (varies)
  - Commit: 2ms
  - Logging: 1ms

### Caching Strategy

**Not implemented at route level** - caching handled by:
- AI Orchestrator (provider response caching)
- Controllers (state caching)
- External CDN/proxy (static assets)

## Related Systems

- **Flask API:** `web/backend/app.py`
- **Runtime Router:** `src/app/core/runtime/router.py`
- **Governance Pipeline:** `src/app/core/governance/pipeline.py`
- **AI Orchestrator:** `src/app/core/ai/orchestrator.py`
- **UserManager:** `src/app/core/user_manager.py`
- **AIPersona:** `src/app/core/ai_systems.py`
- **ImageGenerator:** `src/app/core/image_generator.py`

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-XX  
**Maintainer:** Project-AI Team
