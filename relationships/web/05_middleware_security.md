# Middleware & Security Relationships

**System:** Multi-Layer Security Architecture  
**Components:** CORS, Rate Limiting, Input Sanitization, JWT Validation, Four Laws Ethics  

## Overview

Project-AI implements **defense-in-depth security** with five middleware layers:
1. **HTTP Middleware** - CORS, rate limiting, header validation
2. **Router Middleware** - Source tagging, context enrichment
3. **Governance Middleware** - Input sanitization, action whitelisting
4. **Auth Middleware** - JWT validation, role-based access control
5. **Ethics Middleware** - Four Laws validation

## Middleware Stack

```
HTTP Request
  ↓
[1] HTTP Middleware (Flask-CORS, Flask-Limiter)
  ↓
[2] Flask Route Handler
  ↓
[3] Router Middleware (Source tagging, timestamping)
  ↓
[4] Governance Middleware (Validation, sanitization)
  ↓
[5] Auth Middleware (JWT validation, RBAC)
  ↓
[6] Ethics Middleware (Four Laws)
  ↓
Controller Execution
  ↓
Response
```

## Layer 1: HTTP Middleware

### CORS Configuration

**Location:** `src/app/core/security/middleware.py`

```python
def configure_cors(app: Any, allowed_origins: list[str] | None = None) -> None:
    """Configure CORS with strict origin control."""
    from flask_cors import CORS
    
    if allowed_origins is None:
        allowed_origins = [
            "http://localhost:3000",  # Next.js dev
            "http://localhost:5173",  # Vite dev
        ]
    
    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
```

**Security Features:**
- **Whitelisted origins** - Only specified domains allowed
- **Credentials support** - Allows cookies and Authorization headers
- **Method restriction** - Only necessary HTTP methods
- **Header restriction** - Only Content-Type and Authorization

**CORS Headers:**
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
```

### Rate Limiting

**Location:** `src/app/core/security/middleware.py`

```python
def configure_rate_limiting(app: Any) -> None:
    """Configure rate limiting for Flask app."""
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,  # Rate limit by IP
        default_limits=["100 per minute"],
        storage_uri="memory://",
    )
    
    app.limiter = limiter  # Store for decorator usage
```

**Rate Limits by Endpoint:**
- `/api/auth/login`: 5/minute (brute-force prevention)
- `/api/ai/chat`: 30/minute (conversation limit)
- `/api/ai/image`: 10/hour (resource-intensive)
- `/api/persona/update`: 20/minute (state mutation limit)
- Default: 100/minute (general API calls)

**Rate Limit Response:**
```json
HTTP 429 Too Many Requests
{
  "error": "ratelimit",
  "message": "5 per 1 minute"
}
```

### Request Sanitization

**Location:** `src/app/core/security/middleware.py`

```python
class RequestSanitizer:
    """Sanitize incoming requests to prevent attacks."""
    
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
        if not content_type:
            return False
        
        base_type = content_type.split(";")[0].strip()
        return base_type in allowed
```

**Attack Prevention:**
- **Header injection** - Remove dangerous headers
- **Content-Type confusion** - Validate MIME types
- **Request smuggling** - Strict content parsing

## Layer 2: Router Middleware

### Source Tagging

**Location:** `src/app/core/runtime/router.py`

```python
def route_request(source: ExecutionSource, payload: dict[str, Any]) -> dict[str, Any]:
    """Route requests with source identification."""
    context = {
        "source": source,  # "web", "desktop", "cli", "agent", "temporal", "test"
        "payload": payload,
        "action": payload.get("action", ""),
        "timestamp": _get_timestamp(),  # ISO 8601 UTC
    }
    
    result = enforce_pipeline(context)
    return result
```

**Security Benefits:**
- **Source authentication** - Prevents spoofing
- **Audit trail** - Tracks request origin
- **Policy enforcement** - Different rules per source

### Context Enrichment

```python
context = {
    "source": "web",
    "payload": original_payload,
    "action": "ai.chat",
    "user": {"username": "admin", "role": "admin"},
    "token": "eyJhbGc...",
    "timestamp": "2026-01-15T10:30:00Z",
    "ip_address": request.remote_addr,  # From Flask
    "user_agent": request.headers.get("User-Agent"),
}
```

## Layer 3: Governance Middleware

### Input Validation

**Location:** `src/app/core/governance/pipeline.py`

```python
def _validate(context: dict[str, Any]) -> dict[str, Any]:
    """Phase 1: Validation - Input sanitization and type checks."""
    action = context.get("action", "")
    
    # Action whitelist check
    if action not in VALID_ACTIONS:
        raise ValueError(f"Unknown action: {action}")
    
    # Sanitize string inputs
    payload = context.get("payload", {})
    for key, value in payload.items():
        if isinstance(value, str):
            payload[key] = _sanitize_string(value)
    
    # Type validation
    _validate_types(context)
    
    return context
```

**Sanitization Rules:**
```python
def _sanitize_string(s: str) -> str:
    """Remove dangerous characters from string inputs."""
    # Remove HTML/XML tags
    s = re.sub(r'<[^>]+>', '', s)
    
    # Remove SQL injection patterns
    s = re.sub(r'(--|;|\bOR\b|\bAND\b)', '', s, flags=re.IGNORECASE)
    
    # Remove command injection patterns
    s = re.sub(r'[;&|`$(){}]', '', s)
    
    # Normalize whitespace
    s = ' '.join(s.split())
    
    return s.strip()
```

### Action Whitelisting

```python
VALID_ACTIONS = {
    "ai.chat", "ai.image", "ai.code", "ai.analyze",
    "user.login", "user.logout", "user.create", "user.update", "user.delete",
    "persona.update", "persona.query", "persona.reset",
    # ... 40+ whitelisted actions
}

# Any action not in this set is rejected
if action not in VALID_ACTIONS:
    raise ValueError(f"Unknown action: {action}")
```

### Simulation Phase

```python
def _simulate(context: dict[str, Any]) -> dict[str, Any]:
    """Phase 2: Simulation - Shadow execution for impact analysis."""
    action = context.get("action", "")
    
    # Check if action modifies state
    is_mutating = action in [
        "user.create", "user.delete", "user.update",
        "persona.update", "system.shutdown",
    ]
    
    if is_mutating:
        # Simulate execution in sandbox
        sandbox_result = _simulate_in_sandbox(context)
        
        # Check for dangerous side effects
        if sandbox_result.get("destructive", False):
            logger.warning(f"Destructive action detected: {action}")
    
    return context
```

## Layer 4: Auth Middleware

### JWT Validation

**Location:** `src/app/core/governance/pipeline.py`

```python
def _gate(context: dict[str, Any]) -> dict[str, Any]:
    """Phase 3: Gate - Authorization checks."""
    action = context.get("action", "")
    metadata = ACTION_METADATA.get(action, {})
    
    # Check if auth required
    if metadata.get("requires_auth", False):
        token = context.get("token")
        if not token:
            raise PermissionError("Authentication required")
        
        # Validate JWT
        user = validate_jwt(token)
        if not user:
            raise PermissionError("Invalid or expired token")
        
        context["user"] = user
        
        # Check admin-only actions
        if metadata.get("admin_only", False):
            if user.get("role") != "admin":
                raise PermissionError("Admin access required")
    
    return context
```

**JWT Validation Function:**
```python
def validate_jwt(token: str) -> dict | None:
    """Validate JWT token and extract user info."""
    try:
        import jwt
        secret = os.getenv("JWT_SECRET_KEY", "dev-secret")
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        
        return {
            "username": payload["sub"],
            "role": payload["role"],
        }
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError:
        logger.error("JWT token invalid")
        return None
```

### Role-Based Access Control (RBAC)

```python
ACTION_METADATA = {
    # Public actions
    "user.login": {"requires_auth": False},
    "system.status": {"requires_auth": False},
    
    # User actions
    "ai.chat": {"requires_auth": True},
    "ai.image": {"requires_auth": True},
    "persona.update": {"requires_auth": True},
    
    # Admin actions
    "user.create": {"requires_auth": True, "admin_only": True},
    "user.delete": {"requires_auth": True, "admin_only": True},
    "system.shutdown": {"requires_auth": True, "admin_only": True},
}
```

**RBAC Decision Matrix:**

| Action | Public | User | Admin |
|--------|--------|------|-------|
| user.login | ✓ | ✓ | ✓ |
| system.status | ✓ | ✓ | ✓ |
| ai.chat | ✗ | ✓ | ✓ |
| ai.image | ✗ | ✓ | ✓ |
| persona.update | ✗ | ✓ | ✓ |
| user.create | ✗ | ✗ | ✓ |
| user.delete | ✗ | ✗ | ✓ |
| system.shutdown | ✗ | ✗ | ✓ |

## Layer 5: Ethics Middleware

### Four Laws Validation

**Location:** `src/app/core/ai_systems.py` (FourLaws class)

```python
class FourLaws:
    """Immutable ethics framework (Asimov's Laws)."""
    
    @staticmethod
    def validate_action(action: str, context: dict[str, Any]) -> tuple[bool, str]:
        """
        Validate action against Four Laws hierarchy.
        
        Laws (in order of priority):
        1. Do no harm to humans
        2. Obey human orders (unless conflicts with Law 1)
        3. Protect own existence (unless conflicts with Laws 1-2)
        4. Self-improvement (unless conflicts with Laws 1-3)
        """
        # Law 1: Human safety
        if context.get("endangers_humanity", False):
            return False, "Law 1 violation: Action endangers humans"
        
        # Law 2: Obey orders (if Law 1 satisfied)
        if context.get("is_user_order", True):
            # Check if order conflicts with Law 1
            if _check_harm_potential(action, context):
                return False, "Law 1 overrides user order"
            return True, "Law 2: Obeying user order"
        
        # Law 3: Self-preservation (if Laws 1-2 satisfied)
        if action == "system.shutdown":
            if not context.get("is_user_order", False):
                return False, "Law 3 violation: Self-preservation"
        
        # Law 4: Self-improvement (if Laws 1-3 satisfied)
        if action.startswith("learning."):
            if not _check_knowledge_safety(context):
                return False, "Law 1 overrides learning request"
        
        return True, "All laws satisfied"
```

**Ethics Gate Integration:**
```python
def _gate(context: dict[str, Any]) -> dict[str, Any]:
    """Phase 3: Gate - Authorization and ethics checks."""
    # ... JWT validation ...
    
    # Four Laws ethics check
    action = context.get("action", "")
    is_allowed, reason = FourLaws.validate_action(action, context)
    
    if not is_allowed:
        raise PermissionError(f"Four Laws violation: {reason}")
    
    return context
```

## Security Headers

### Production Security Headers

**Location:** Flask app configuration

```python
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    return response
```

**Header Descriptions:**
- **X-Content-Type-Options** - Prevents MIME-sniffing
- **X-Frame-Options** - Prevents clickjacking
- **X-XSS-Protection** - Browser XSS filter
- **Strict-Transport-Security** - Forces HTTPS
- **Content-Security-Policy** - Restricts resource loading

## Attack Prevention

### SQL Injection Prevention

**Defense:**
- No SQL database (JSON file storage)
- Input sanitization removes SQL patterns
- Parameterized queries (if SQL added)

### XSS Prevention

**Defense:**
- Input sanitization removes HTML tags
- React auto-escapes output
- CSP header restricts inline scripts

### CSRF Prevention

**Defense:**
- JWT in Authorization header (not cookies)
- SameSite cookie attribute (future)
- CSRF tokens (future)

### Command Injection Prevention

**Defense:**
- Input sanitization removes shell metacharacters
- No system() or exec() calls with user input
- Subprocess allowlist (if needed)

### Path Traversal Prevention

**Defense:**
- No file path handling from user input
- Absolute paths only
- Sandboxed file operations

## Audit Logging

### Complete Audit Trail

**Location:** `src/app/core/governance/pipeline.py`

```python
def _log(context: dict[str, Any], result: Any) -> None:
    """Phase 6: Logging - Complete audit trail."""
    audit_entry = {
        "timestamp": context["timestamp"],
        "source": context["source"],
        "action": context["action"],
        "user": context.get("user", {}).get("username", "anonymous"),
        "result": "success" if result else "error",
        "ip_address": context.get("ip_address"),
        "user_agent": context.get("user_agent"),
    }
    
    logger.info(f"Audit: {json.dumps(audit_entry)}")
    
    # Append to audit log file
    with open("data/audit_log.json", "a") as f:
        json.dump(audit_entry, f)
        f.write("\n")
```

**Audit Log Format:**
```json
{
  "timestamp": "2026-01-15T10:30:00Z",
  "source": "web",
  "action": "ai.chat",
  "user": "admin",
  "result": "success",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 ..."
}
```

## Error Handling

### Secure Error Responses

```python
try:
    result = enforce_pipeline(context)
except ValueError as e:
    # Validation error (400)
    return {"status": "error", "error": "validation", "message": str(e)}
except PermissionError as e:
    # Auth error (401/403)
    return {"status": "error", "error": "permission", "message": str(e)}
except Exception as e:
    # System error (500)
    logger.error(f"System error: {e}", exc_info=True)
    return {"status": "error", "error": "system", "message": "Internal error"}
```

**Security Principle:** Never leak system details in error messages

## Performance Impact

### Middleware Overhead

- CORS check: < 1ms
- Rate limiting: < 1ms
- Input sanitization: 1-2ms
- JWT validation: 2-3ms
- Four Laws check: 1-2ms
- Audit logging: 1-2ms

**Total overhead:** ~10ms per request

### Optimization Strategies

- Cache JWT validation results (5 minutes)
- Batch audit log writes (every 10 seconds)
- Use Redis for rate limiting (distributed systems)

## Related Systems

- **Flask Middleware:** `web/backend/app.py`
- **Security Middleware:** `src/app/core/security/middleware.py`
- **Governance Pipeline:** `src/app/core/governance/pipeline.py`
- **Four Laws:** `src/app/core/ai_systems.py`
- **UserManager:** `src/app/core/user_manager.py`

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-XX  
**Maintainer:** Project-AI Team
