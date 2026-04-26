# Request Flow & State Propagation

**System:** End-to-End Request Processing  
**Layers:** 7-layer architecture from HTTP to State  
**Pattern:** Unidirectional flow with governance checkpoints  

## Complete Request Flow

### Layer-by-Layer Breakdown

```
[L1] React Component (Client)
  ↓ User Action (click, form submit)
[L2] Store Action (useAuthStore.login)
  ↓ API Call (fetch)
[L3] Flask Endpoint (HTTP handler)
  ↓ Request parsing, header extraction
[L4] Runtime Router (source tagging)
  ↓ Context enrichment
[L5] Governance Pipeline (6 phases)
  ↓ Validation → Simulation → Gate → Execute → Commit → Log
[L6] Domain Controller (business logic)
  ↓ AI Orchestrator / UserManager / etc.
[L7] State Persistence (JSON files)
  ↓ Atomic writes, file locking
Response Propagation (reverse order)
  ↓ L7 → L6 → L5 → L4 → L3 → L2 → L1
React Component (UI update)
```

## Example 1: User Login Flow

### Complete Trace

#### Step 1: User Action (React)

**Component:** `LoginForm.tsx`

```typescript
const handleSubmit = async (e: FormEvent) => {
  e.preventDefault();
  
  // Client-side validation
  const sanitized = sanitizeInput(username.trim());
  const usernameError = validateUsername(sanitized);
  const passwordError = validatePassword(password);
  
  if (usernameError || passwordError) {
    setErrors({ username: usernameError, password: passwordError });
    return;
  }
  
  // Call store action
  try {
    await login(sanitized, password);
  } catch (error) {
    setErrors({ general: (error as ApiError).message });
  }
};
```

**Timing:** < 1ms (synchronous validation)

#### Step 2: Store Action (Zustand)

**Store:** `useAuthStore` (expected implementation)

```typescript
login: async (username, password) => {
  set({ isLoading: true, error: null });
  
  try {
    const response = await fetch('http://localhost:5000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Login failed');
    }
    
    const data = await response.json();
    
    set({
      user: data.user,
      token: data.token,
      isAuthenticated: true,
      isLoading: false,
    });
    
    // Persist token
    localStorage.setItem('token', data.token);
  } catch (error) {
    set({
      error: { message: (error as Error).message },
      isLoading: false,
    });
    throw error;
  }
}
```

**Timing:** 50-200ms (network latency + server processing)

#### Step 3: Flask Endpoint

**File:** `web/backend/app.py`

```python
@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate user via governance pipeline."""
    # Parse JSON body
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify(error="missing-json", message="Request must include JSON body."), 400
    
    # Route through governance pipeline
    response = route_request(
        source="web",
        payload={
            "action": "user.login",
            "username": payload.get("username"),
            "password": payload.get("password"),
        },
    )
    
    if response["status"] == "success":
        role = response["result"].get("role", "user")
        username = response["result"].get("username")
        return jsonify(
            status="ok",
            success=True,
            token=response["result"]["token"],
            user={"username": username, "role": role},
        ), 200
    else:
        return jsonify(
            status="error",
            success=False,
            error="invalid-credentials",
            message=response.get("error", "Authentication failed"),
        ), 401
```

**Timing:** < 1ms (parsing + routing)

#### Step 4: Runtime Router

**File:** `src/app/core/runtime/router.py`

```python
def route_request(source: ExecutionSource, payload: dict[str, Any]) -> dict[str, Any]:
    """Route requests through governance pipeline."""
    logger.info(f"Routing request from {source}: {payload.get('action', 'unknown')}")
    
    # Build execution context
    context = {
        "source": source,  # "web"
        "payload": payload,
        "action": payload.get("action", ""),  # "user.login"
        "user": payload.get("user", {}),
        "config": payload.get("config", {}),
        "timestamp": _get_timestamp(),  # "2026-01-15T10:30:00Z"
    }
    
    try:
        # Route through governance → AI orchestrator → systems
        result = enforce_pipeline(context)
        
        return {
            "status": "success",
            "result": result,
            "metadata": {
                "source": source,
                "action": context["action"],
                "timestamp": context["timestamp"],
            },
        }
    
    except Exception as e:
        logger.error(f"Request routing failed for {source}: {e}")
        return {
            "status": "error",
            "result": None,
            "error": str(e),
            "metadata": {
                "source": source,
                "action": context.get("action", "unknown"),
                "timestamp": context["timestamp"],
            },
        }
```

**Timing:** < 1ms (context building)

#### Step 5: Governance Pipeline

**File:** `src/app/core/governance/pipeline.py`

```python
def enforce_pipeline(context: dict[str, Any]) -> Any:
    """Execute 6-phase governance pipeline."""
    logger.info(f"Governance pipeline: {context.get('action')} from {context.get('source')}")
    
    try:
        # Phase 1: Validation
        validated_context = _validate(context)
        # - Check action in VALID_ACTIONS
        # - Sanitize string inputs
        # - Type validation
        # Timing: 1-2ms
        
        # Phase 2: Simulation
        simulated_context = _simulate(validated_context)
        # - Shadow execution
        # - Impact analysis
        # - Rollback preparation
        # Timing: 2-3ms
        
        # Phase 3: Gate
        gated_context = _gate(simulated_context)
        # - Authentication check (JWT validation for protected actions)
        # - Authorization check (role-based access)
        # - Four Laws ethics validation
        # Timing: 2-3ms (no JWT for login)
        
        # Phase 4: Execution
        result = _execute(gated_context)
        # - Route to UserManager.authenticate()
        # - Load users.json
        # - Verify password with Argon2
        # - Generate JWT token
        # Timing: 10-20ms (Argon2 intentionally slow)
        
        # Phase 5: Commit
        _commit(gated_context, result)
        # - Persist state changes (if any)
        # - Rollback on failure
        # Timing: < 1ms (login doesn't persist state)
        
        # Phase 6: Logging
        _log(gated_context, result)
        # - Append to audit log
        # - Record timestamp, user, action, result
        # Timing: 1-2ms
        
        return result
    
    except Exception as e:
        logger.error(f"Governance pipeline failed: {e}")
        raise
```

**Total Timing:** 15-30ms

#### Step 6: Domain Controller (UserManager)

**File:** `src/app/core/user_manager.py`

```python
def authenticate(self, username: str, password: str) -> dict | None:
    """Authenticate user with username/password."""
    users = self._load_users()  # Load data/users.json
    
    for user in users.get("users", []):
        if user["username"] == username:
            try:
                # Verify password with Argon2 (10-20ms)
                argon2.verify(user["password_hash"], password)
                
                # Generate JWT token
                token = generate_jwt({
                    "username": user["username"],
                    "role": user["role"]
                })
                
                return {
                    "username": user["username"],
                    "role": user["role"],
                    "token": token
                }
            except argon2.exceptions.VerifyMismatchError:
                return None
    
    return None  # User not found
```

**Timing:** 10-20ms (Argon2 verification)

#### Step 7: Response Propagation

**Reverse flow through all layers:**

```
UserManager returns:
{
  "username": "admin",
  "role": "admin",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
  ↓
Governance Pipeline phase 6 logs result
  ↓
Governance returns to Router
  ↓
Router wraps in metadata:
{
  "status": "success",
  "result": {"username": "admin", "role": "admin", "token": "..."},
  "metadata": {"source": "web", "action": "user.login", "timestamp": "..."}
}
  ↓
Flask transforms to HTTP response:
HTTP 200 OK
{
  "status": "ok",
  "success": true,
  "token": "...",
  "user": {"username": "admin", "role": "admin"}
}
  ↓
Store receives response and updates state:
set({
  user: {username: "admin", role: "admin"},
  token: "...",
  isAuthenticated: true,
  isLoading: false
})
  ↓
React components re-render (all useAuthStore subscribers)
  ↓
HomePage detects isAuthenticated: true
  ↓
router.push('/dashboard')
  ↓
User sees dashboard
```

**Total Request Time:** 50-200ms

## Example 2: AI Chat Request Flow

### Abbreviated Trace

#### Step 1-3: React → Store → Flask

Same pattern as login, different endpoint.

#### Step 4-5: Router → Governance

```python
context = {
    "source": "web",
    "action": "ai.chat",
    "token": "eyJhbGc...",  # Extracted from Authorization header
    "prompt": "Explain quantum computing",
    "model": "gpt-4",
    "timestamp": "2026-01-15T10:30:00Z"
}

# Governance checks:
# 1. Validate: action in VALID_ACTIONS ✓
# 2. Simulate: check impact (none for chat)
# 3. Gate:
#    - JWT validation ✓
#    - Role check (user/admin) ✓
#    - Four Laws: harmless prompt ✓
# 4. Execute: route to AI Orchestrator
```

#### Step 6: AI Orchestrator

**File:** `src/app/core/ai/orchestrator.py`

```python
def run_ai(request: AIRequest) -> AIResponse:
    """Execute AI request with provider fallback."""
    providers = ["openai", "huggingface", "perplexity", "local"]
    
    for provider in providers:
        try:
            logger.info(f"Trying provider: {provider}")
            response = _call_provider(provider, request)
            
            if response.status == "success":
                return response  # First successful provider wins
        except Exception as e:
            logger.warning(f"Provider {provider} failed: {e}")
            continue
    
    raise RuntimeError("All AI providers failed")

def _call_provider(provider: AIProvider, request: AIRequest) -> AIResponse:
    """Call specific AI provider."""
    if provider == "openai":
        import openai
        
        response = openai.ChatCompletion.create(
            model=request.model or "gpt-4",
            messages=[{"role": "user", "content": request.prompt}],
            max_tokens=500,
        )
        
        return AIResponse(
            status="success",
            result=response.choices[0].message.content,
            provider_used="openai",
            metadata={
                "model": response.model,
                "tokens": response.usage.total_tokens,
                "latency_ms": 1200
            }
        )
    # ... other providers ...
```

**Timing:** 200-2000ms (OpenAI API latency)

#### Step 7: State Propagation

**No state change** (chat is stateless unless history stored)

```
AI Orchestrator returns:
{
  "status": "success",
  "result": "Quantum computing is a type of computation that...",
  "provider_used": "openai",
  "metadata": {"model": "gpt-4", "tokens": 150, "latency_ms": 1200}
}
  ↓
Governance → Router → Flask → Store → React
  ↓
React displays AI response in chat panel
```

**Total Request Time:** 250-2500ms

## State Propagation Patterns

### Pattern 1: Optimistic Updates

**Concept:** Update UI immediately, rollback on error

```typescript
const sendMessage = async (prompt: string) => {
  // Optimistic update
  set((state) => ({
    chatHistory: [
      ...state.chatHistory,
      { role: 'user', content: prompt },
      { role: 'assistant', content: 'Thinking...', loading: true }
    ]
  }));
  
  try {
    const response = await fetch('/api/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
    
    const data = await response.json();
    
    // Replace loading message with real response
    set((state) => ({
      chatHistory: state.chatHistory.map((msg, idx) =>
        idx === state.chatHistory.length - 1
          ? { role: 'assistant', content: data.result, loading: false }
          : msg
      )
    }));
  } catch (error) {
    // Rollback optimistic update
    set((state) => ({
      chatHistory: state.chatHistory.slice(0, -2),  // Remove user + loading messages
      error: 'Failed to send message'
    }));
  }
};
```

### Pattern 2: Server-Side Rendering (SSR)

**Next.js Server Component:**

```typescript
// app/dashboard/page.tsx (Server Component)
async function DashboardPage() {
  // Fetch data on server
  const stats = await fetch('http://localhost:5000/api/stats', {
    cache: 'no-store'  // Fresh data every request
  }).then(r => r.json());
  
  return (
    <Dashboard stats={stats}>
      {/* Client components */}
    </Dashboard>
  );
}
```

**Benefit:** Faster initial page load, SEO-friendly

### Pattern 3: Real-Time Updates (Future)

**WebSocket Integration:**

```typescript
// Store with WebSocket
const useRealtimeStore = create((set) => ({
  messages: [],
  ws: null,
  
  connect: () => {
    const ws = new WebSocket('ws://localhost:5000/ws');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      set((state) => ({
        messages: [...state.messages, data]
      }));
    };
    
    set({ ws });
  },
  
  send: (message: string) => {
    get().ws?.send(JSON.stringify({ type: 'chat', content: message }));
  }
}));
```

**Server (Flask-SocketIO):**

```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('chat')
def handle_chat(data):
    # Process message
    response = ai_orchestrator.run(data['content'])
    
    # Broadcast to all clients
    emit('message', {
        'role': 'assistant',
        'content': response,
        'timestamp': datetime.utcnow().isoformat()
    }, broadcast=True)
```

## Performance Metrics

### Request Timing Breakdown

**Login Request:**
- Client validation: < 1ms
- Network latency: 10-50ms
- Flask parsing: < 1ms
- Router: < 1ms
- Governance: 5-10ms
- UserManager (Argon2): 10-20ms
- Response formation: < 1ms
- Network return: 10-50ms
- Store update: < 1ms
- React render: 5-10ms

**Total:** 50-150ms

**AI Chat Request:**
- Client → Flask: 10-50ms
- Governance: 5-10ms
- AI Orchestrator (OpenAI): 200-2000ms
- Response: 10-50ms
- React render: 5-10ms

**Total:** 230-2120ms (dominated by AI provider)

### Optimization Strategies

**1. Request Batching**
```typescript
const batchedRequests = [];
let timeout;

const batchRequest = (request) => {
  batchedRequests.push(request);
  
  clearTimeout(timeout);
  timeout = setTimeout(async () => {
    await fetch('/api/batch', {
      method: 'POST',
      body: JSON.stringify(batchedRequests)
    });
    batchedRequests.length = 0;
  }, 100);  // Batch every 100ms
};
```

**2. Response Caching**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_ai_response(prompt: str) -> str:
    return ai_orchestrator.run(prompt)
```

**3. Parallel Requests**
```typescript
const [user, stats, history] = await Promise.all([
  fetch('/api/user'),
  fetch('/api/stats'),
  fetch('/api/history')
]);
```

## Related Systems

- **React Components:** `web/components/`
- **State Management:** `web/lib/store.ts` (expected)
- **Flask API:** `web/backend/app.py`
- **Runtime Router:** `src/app/core/runtime/router.py`
- **Governance Pipeline:** `src/app/core/governance/pipeline.py`
- **AI Orchestrator:** `src/app/core/ai/orchestrator.py`
- **UserManager:** `src/app/core/user_manager.py`

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-XX  
**Maintainer:** Project-AI Team
