# API Request/Response Sequence Diagram

## Overview
This diagram illustrates the complete web API request/response flow, from client request through authentication, rate limiting, governance validation, business logic execution, and response delivery with comprehensive error handling.

## Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    participant Client as Web Client<br/>(React Frontend)
    participant CORS as CORS Middleware
    participant RateLimit as Rate Limiter
    participant Auth as Auth Middleware
    participant Router as Runtime Router
    participant Gov as Triumvirate
    participant Handler as Request Handler
    participant UserMgr as UserManager
    participant AIOrch as AI Orchestrator
    participant DB as Data Store (JSON)
    participant Logger as Audit Logger
    
    Note over Client,Logger: Web API Request/Response Flow
    
    %% Client Request
    Client->>CORS: POST /api/ai/chat<br/>Headers: Authorization, Content-Type<br/>Body: {message, context}
    activate CORS
    
    %% CORS Check
    CORS->>CORS: Verify origin against whitelist
    
    alt Origin Not Allowed
        CORS-->>Client: 403 Forbidden<br/>{error: "CORS violation"}
        Note over Client: Request blocked
    else Origin Allowed
        CORS->>CORS: Set CORS headers:<br/>- Access-Control-Allow-Origin<br/>- Access-Control-Allow-Methods<br/>- Access-Control-Allow-Headers
        
        CORS->>RateLimit: Forward request
        deactivate CORS
        activate RateLimit
        
        %% Rate Limiting
        RateLimit->>RateLimit: Check IP/token rate limit<br/>(100 req/hour per IP)
        
        alt Rate Limit Exceeded
            RateLimit-->>Client: 429 Too Many Requests<br/>{error: "Rate limit exceeded",<br/>retry_after: 3600}
            Note over Client: Retry after cooldown
        else Within Rate Limit
            RateLimit->>RateLimit: Increment request counter
            
            RateLimit->>Auth: Forward request
            deactivate RateLimit
            activate Auth
            
            %% Authentication
            Auth->>Auth: Extract Bearer token from header
            
            alt No Token
                Auth-->>Client: 401 Unauthorized<br/>{error: "Missing authentication"}
            else Invalid Token
                Auth->>Auth: Verify JWT signature
                Auth-->>Client: 401 Unauthorized<br/>{error: "Invalid token"}
            else Valid Token
                Auth->>Auth: Decode JWT payload
                Auth->>Auth: Extract user_id, role, exp
                Auth->>Auth: Check token expiration
                
                alt Token Expired
                    Auth-->>Client: 401 Unauthorized<br/>{error: "Token expired"}
                else Token Valid
                    Auth->>Auth: Load user context (role, permissions)
                    
                    Auth->>Router: Forward request + user context
                    deactivate Auth
                    activate Router
                    
                    %% Runtime Router
                    Router->>Logger: Log request (user, endpoint, timestamp)
                    activate Logger
                    Logger-->>Router: Request logged
                    deactivate Logger
                    
                    Router->>Router: Parse request payload:<br/>- Extract action: "ai.chat"<br/>- Extract parameters<br/>- Validate JSON schema
                    
                    alt Invalid Payload
                        Router-->>Client: 400 Bad Request<br/>{error: "Invalid request format"}
                    else Valid Payload
                        %% Governance Validation
                        Router->>Gov: validate_request(action, user, context)
                        activate Gov
                        
                        par Triumvirate Evaluation
                            Gov->>Gov: Galahad: Check user welfare
                            Gov->>Gov: Cerberus: Assess security risks
                            Gov->>Gov: Codex: Verify logical consistency
                        end
                        
                        alt Request Blocked
                            Gov-->>Router: BLOCKED (reason, severity)
                            deactivate Gov
                            
                            Router->>Logger: Log blocked request
                            activate Logger
                            Logger-->>Router: Block logged
                            deactivate Logger
                            
                            Router-->>Client: 403 Forbidden<br/>{error: "Request blocked",<br/>reason: "[governance reason]"}
                            
                        else Request Approved
                            Gov-->>Router: APPROVED (decision summary)
                            deactivate Gov
                            
                            %% Route to Handler
                            Router->>Handler: Route to /api/ai/chat handler
                            activate Handler
                            
                            alt Action: ai.chat
                                Handler->>AIOrch: generate_response(message, user_context)
                                activate AIOrch
                                
                                AIOrch->>AIOrch: Build prompt with context
                                AIOrch->>AIOrch: Call OpenAI API (GPT-4)
                                
                                alt OpenAI Success
                                    AIOrch-->>Handler: AI response + metadata
                                else OpenAI Failure
                                    AIOrch->>AIOrch: Fallback to OpenRouter
                                    AIOrch-->>Handler: Fallback response + metadata
                                end
                                deactivate AIOrch
                                
                                Handler->>DB: Store interaction in episodic memory
                                activate DB
                                DB-->>Handler: Interaction stored
                                deactivate DB
                                
                                Handler-->>Router: Response: {status: "success",<br/>result: {message, metadata}}
                                deactivate Handler
                                
                            else Action: user.login
                                Handler->>UserMgr: login(username, password)
                                activate UserMgr
                                
                                UserMgr->>DB: Load users.json
                                activate DB
                                DB-->>UserMgr: User data
                                deactivate DB
                                
                                UserMgr->>UserMgr: Verify password (pbkdf2_sha256)
                                
                                alt Login Failed
                                    UserMgr->>UserMgr: Increment failed attempts
                                    UserMgr->>DB: Save lockout state
                                    activate DB
                                    DB-->>UserMgr: State saved
                                    deactivate DB
                                    
                                    UserMgr-->>Handler: Login failed
                                    Handler-->>Router: Response: {status: "error",<br/>error: "Invalid credentials"}
                                else Login Success
                                    UserMgr->>UserMgr: Generate JWT token
                                    UserMgr->>UserMgr: Reset failed attempts
                                    UserMgr->>DB: Save user state
                                    activate DB
                                    DB-->>UserMgr: State saved
                                    deactivate DB
                                    
                                    UserMgr-->>Handler: Login successful (token, user)
                                    deactivate UserMgr
                                    Handler-->>Router: Response: {status: "success",<br/>result: {token, user}}
                                end
                                deactivate Handler
                            end
                            
                            %% Response Processing
                            Router->>Logger: Log successful response
                            activate Logger
                            Logger-->>Router: Response logged
                            deactivate Logger
                            
                            Router->>Router: Format response with metadata:<br/>- Execution time<br/>- Request ID<br/>- Timestamp
                            
                            Router-->>Client: 200 OK<br/>{status: "success",<br/>result: {...},<br/>metadata: {...}}
                            deactivate Router
                            
                            Note over Client: Request completed successfully
                        end
                    end
                end
            end
        end
    end
    
    %% Error Handling (Alternative Flows)
    Note over Client,Logger: Error Scenarios
    
    alt Network Timeout
        Client->>CORS: Request
        activate CORS
        CORS->>CORS: Timeout after 30s
        CORS-->>Client: 504 Gateway Timeout<br/>{error: "Request timeout"}
        deactivate CORS
    end
    
    alt Server Error
        Client->>Router: Request
        activate Router
        Router->>Handler: Route request
        activate Handler
        Handler->>Handler: Unexpected exception
        Handler-->>Router: Exception details
        deactivate Handler
        
        Router->>Logger: Log error (stack trace)
        activate Logger
        Logger-->>Router: Error logged
        deactivate Logger
        
        Router-->>Client: 500 Internal Server Error<br/>{error: "Server error",<br/>request_id: "abc123"}
        deactivate Router
        Note over Client: User sees generic error,<br/>admins see full trace in logs
    end
```

## Key Components

### Flask Web Application (`src/app/interfaces/web/app.py`)
- **Framework**: Flask 3.x with CORS and rate limiting
- **Endpoints**: `/api/auth/login`, `/api/ai/chat`, `/api/status`
- **Middleware**: CORS, rate limiting, authentication
- **Routing**: Delegates to Runtime Router for governance integration

### CORS Middleware (`src/app/core/security/middleware.py`)
- **Origin Whitelist**: Configurable allowed origins (default: localhost:3000, production domain)
- **Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Headers**: Authorization, Content-Type, X-Request-ID
- **Credentials**: Supports cookies and Authorization headers

### Rate Limiter (`src/app/core/security/middleware.py`)
- **Implementation**: Flask-Limiter with Redis backend (or in-memory for dev)
- **Limits**: 100 requests/hour per IP, 1000 requests/hour per authenticated user
- **Strategy**: Sliding window with exponential backoff
- **Response**: 429 with `Retry-After` header

### Auth Middleware (`src/app/core/security/middleware.py`)
- **Token Type**: JWT (JSON Web Tokens)
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Payload**: user_id, username, role, exp (expiration), iat (issued at)
- **Expiration**: 24 hours (configurable)
- **Secret**: Loaded from environment (JWT_SECRET)

### Runtime Router (`src/app/core/runtime/router.py`)
- **Central Routing**: All API requests route through governance pipeline
- **Action Mapping**: Maps API actions to internal handlers
- **Context Injection**: Adds user context, request metadata
- **Error Handling**: Standardized error responses

### Request Handler
- **Action-Based**: Different handlers for different actions (ai.chat, user.login, etc.)
- **Business Logic**: Delegates to core systems (AIOrchestrator, UserManager)
- **Response Formatting**: Standardized JSON response structure
- **Error Translation**: Converts exceptions to user-friendly messages

### Audit Logger (`src/app/core/security/audit.py`)
- **Comprehensive Logging**: All requests, responses, errors logged
- **Structured Format**: JSON logs with timestamp, user, action, result
- **Security Events**: Authentication failures, governance blocks, rate limit hits
- **Retention**: 90 days (configurable)

## API Endpoints

### `/api/auth/login` (POST)
**Request**:
```json
{
  "username": "alice",
  "password": "SecurePass123!"
}
```

**Success Response (200)**:
```json
{
  "status": "ok",
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "username": "alice",
    "role": "user"
  }
}
```

**Error Response (401)**:
```json
{
  "status": "error",
  "success": false,
  "error": "invalid-credentials",
  "message": "Invalid username or password (3 attempts remaining)"
}
```

### `/api/ai/chat` (POST)
**Request**:
```json
{
  "message": "Explain quantum computing",
  "context": {
    "conversation_id": "conv-12345",
    "user_preferences": {"tone": "educational"}
  }
}
```

**Headers**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Success Response (200)**:
```json
{
  "status": "success",
  "result": {
    "message": "Quantum computing harnesses quantum mechanics...",
    "metadata": {
      "model": "gpt-4",
      "tokens": 247,
      "conversation_id": "conv-12345"
    }
  },
  "metadata": {
    "request_id": "req-abc123",
    "execution_time_ms": 1850,
    "timestamp": "2024-01-15T10:30:45Z"
  }
}
```

**Error Response (403)**:
```json
{
  "status": "error",
  "error": "governance-blocked",
  "reason": "Request contains potential misinformation trigger (Cerberus)",
  "request_id": "req-abc123"
}
```

### `/api/status` (GET)
**Response (200)**:
```json
{
  "status": "ok",
  "component": "web-backend",
  "version": "1.0.0",
  "uptime_seconds": 86400
}
```

## Security Layers

| Layer | Purpose | Implementation | Failure Response |
|-------|---------|----------------|------------------|
| **CORS** | Prevent unauthorized origins | Origin whitelist validation | 403 Forbidden |
| **Rate Limiting** | Prevent abuse | 100 req/hr per IP | 429 Too Many Requests |
| **Authentication** | Verify user identity | JWT token validation | 401 Unauthorized |
| **Authorization** | Check permissions | Role-based access control | 403 Forbidden |
| **Governance** | Ethical/safety validation | Triumvirate council | 403 Forbidden (blocked) |
| **Input Validation** | Prevent injection | JSON schema validation | 400 Bad Request |
| **Audit Logging** | Track all actions | Structured logs | N/A (always logs) |

## Error Response Format

All errors follow this structure:
```json
{
  "status": "error",
  "error": "error-code",
  "message": "Human-readable description",
  "request_id": "req-abc123",
  "timestamp": "2024-01-15T10:30:45Z",
  "details": {
    // Optional: Additional context (not shown to all users)
  }
}
```

## HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| **200** | OK | Successful request |
| **400** | Bad Request | Invalid JSON, missing parameters, schema violation |
| **401** | Unauthorized | Missing/invalid/expired token |
| **403** | Forbidden | CORS violation, governance block, insufficient permissions |
| **404** | Not Found | Endpoint doesn't exist |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Unexpected server exception |
| **504** | Gateway Timeout | Request timeout (30s) |

## Performance Metrics

- **Average Response Time**: 200-500ms (without AI generation)
- **AI Chat Response Time**: 2-5 seconds (with OpenAI GPT-4)
- **CORS Check**: <5ms
- **Rate Limit Check**: <10ms (Redis) / <1ms (in-memory)
- **JWT Validation**: <20ms
- **Governance Validation**: 150-300ms
- **Audit Logging**: <20ms
- **Total Overhead**: 200-350ms (non-AI requests)

## Rate Limiting Strategy

### Per-IP Limits
- **Anonymous Users**: 100 requests/hour
- **Cooldown**: 1 hour after limit exceeded
- **Storage**: Redis (production) or in-memory (dev)

### Per-User Limits (Authenticated)
- **Regular Users**: 1000 requests/hour
- **Admin Users**: 5000 requests/hour
- **API Keys**: 10,000 requests/hour

### Endpoint-Specific Limits
- `/api/auth/login`: 10 attempts/hour (per IP)
- `/api/ai/chat`: 100 requests/hour (per user)
- `/api/data/upload`: 20 requests/hour (per user)

## JWT Token Structure

**Header**:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload**:
```json
{
  "user_id": "user-12345",
  "username": "alice",
  "role": "user",
  "iat": 1705315845,
  "exp": 1705402245
}
```

**Signature**:
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  JWT_SECRET
)
```

## CORS Configuration

**Development**:
```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
```

**Production**:
```python
ALLOWED_ORIGINS = [
    "https://project-ai.example.com",
    "https://app.project-ai.example.com"
]
```

**Preflight Handling**:
```http
OPTIONS /api/ai/chat HTTP/1.1
Origin: http://localhost:3000

HTTP/1.1 204 No Content
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400
```

## Error Handling Examples

### Authentication Error
**Request**: Missing Authorization header
**Response**:
```json
{
  "status": "error",
  "error": "missing-authentication",
  "message": "Authorization header required",
  "request_id": "req-abc123"
}
```

### Governance Block
**Request**: AI chat with harmful content
**Response**:
```json
{
  "status": "error",
  "error": "governance-blocked",
  "reason": "Request violates Law 1 (Human Welfare): Potential harm to third party",
  "council": "Galahad",
  "severity": "HIGH",
  "request_id": "req-abc124"
}
```

### Rate Limit Exceeded
**Request**: 101st request in 1 hour
**Response**:
```json
{
  "status": "error",
  "error": "rate-limit-exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 3540,
  "request_id": "req-abc125"
}
```

### Server Error
**Request**: Internal exception during processing
**Response**:
```json
{
  "status": "error",
  "error": "server-error",
  "message": "An unexpected error occurred. Support has been notified.",
  "request_id": "req-abc126"
}
```

## Usage in Documentation

Referenced in:
- **Web API Reference** (`docs/api/reference.md`)
- **Authentication Guide** (`docs/api/authentication.md`)
- **Security Best Practices** (`docs/security/api-security.md`)
- **Integration Guide** (`docs/integration/web-api.md`)

## Testing

Covered by:
- `tests/api/test_auth_endpoints.py`
- `tests/api/test_chat_endpoints.py`
- `tests/api/test_middleware.py`
- `tests/integration/test_api_flow.py`
- `tests/security/test_rate_limiting.py`
- `tests/security/test_cors.py`

## Related Diagrams

- [User Login Sequence](./01-user-login-sequence.md) - Desktop login flow (compare with API login)
- [AI Chat Interaction Sequence](./02-ai-chat-interaction-sequence.md) - Core chat logic (used by API)
- [Governance Validation Sequence](./03-governance-validation-sequence.md) - Governance in API requests
- [Security Alert Sequence](./04-security-alert-sequence.md) - Automated security monitoring of API
