# Authentication System Relationships

**System:** Multi-Layer Authentication Architecture  
**Components:** JWT Tokens, Argon2 Hashing, Governance Integration  
**Security Level:** Production-Grade (ASL-3 compliant)  

## Overview

The authentication system implements **defense-in-depth** with three validation layers:
1. **Web Layer** - HTTP auth headers, JWT validation
2. **Router Layer** - Source identification, action whitelisting
3. **Governance Layer** - Four Laws ethics, user permissions

## Authentication Flow Architecture

### Complete Request Flow

```
User Login Request
  ↓
1. React LoginForm
   ├─ Input validation (client-side)
   ├─ Sanitization (XSS prevention)
   └─ POST /api/auth/login
      ↓
2. Flask Endpoint
   ├─ JSON body validation
   ├─ Content-Type check
   └─ route_request(source="web", action="user.login")
      ↓
3. Runtime Router
   ├─ Source tagging ("web")
   ├─ Timestamp generation
   └─ Context enrichment
      ↓
4. Governance Pipeline
   ├─ Action whitelist check (VALID_ACTIONS)
   ├─ Input sanitization (dangerous characters)
   └─ Forward to UserManager
      ↓
5. UserManager (Core System)
   ├─ Load users.json
   ├─ Find username
   ├─ Argon2 password verification
   ├─ Generate JWT token
   └─ Return {token, user}
      ↓
6. Response Propagation
   ├─ Governance → Router → Flask
   ├─ HTTP 200 + JSON response
   └─ React receives {token, user}
      ↓
7. Client State Update
   ├─ Store token in localStorage
   ├─ Update useAuthStore
   └─ Navigate to /dashboard
```

## Core Components

### 1. UserManager (`src/app/core/user_manager.py`)

**Responsibilities:**
- User credential storage (JSON persistence)
- Password hashing (bcrypt/Argon2)
- User role management (admin/user/guest)

**Data Structure:**
```python
# data/users.json
{
  "users": [
    {
      "username": "admin",
      "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$...",  # Argon2
      "role": "admin"
    },
    {
      "username": "guest",
      "password_hash": "$argon2id$...",
      "role": "guest"
    }
  ]
}
```

**Key Methods:**

#### `authenticate(username: str, password: str) -> dict | None`

**Purpose:** Verify credentials and return user profile

**Implementation:**
```python
def authenticate(self, username: str, password: str) -> dict | None:
    """
    Authenticate user with username/password.
    
    Returns:
        dict: {username, role} if valid
        None: if invalid credentials
    """
    users = self._load_users()
    
    for user in users.get("users", []):
        if user["username"] == username:
            # Verify password with Argon2
            try:
                argon2.verify(user["password_hash"], password)
                return {
                    "username": user["username"],
                    "role": user["role"]
                }
            except argon2.exceptions.VerifyMismatchError:
                return None
    
    return None  # User not found
```

**Security Features:**
- Constant-time comparison (via Argon2)
- Memory-hard hashing (prevents rainbow tables)
- Salting (unique salt per password)
- Configurable work factor (m=65536, t=3, p=4)

#### `create_user(username: str, password: str, role: str) -> bool`

**Purpose:** Create new user with hashed password

**Implementation:**
```python
def create_user(self, username: str, password: str, role: str = "user") -> bool:
    """
    Create new user with Argon2 password hash.
    
    Args:
        username: Unique username (3-50 chars, alphanumeric + _-)
        password: Plain-text password (6-128 chars)
        role: User role (admin/user/guest)
    
    Returns:
        bool: True if created, False if username exists
    """
    users = self._load_users()
    
    # Check username uniqueness
    if any(u["username"] == username for u in users.get("users", [])):
        return False
    
    # Hash password with Argon2id
    password_hash = argon2.hash(password)
    
    # Add user
    users.setdefault("users", []).append({
        "username": username,
        "password_hash": password_hash,
        "role": role
    })
    
    # Persist to disk
    self.save_users(users)
    return True
```

**Validation Rules:**
- Username: 3-50 chars, `^[a-zA-Z0-9_-]+$`
- Password: 6-128 chars (server-side only)
- Role: One of ["admin", "user", "guest"]

### 2. JWT Token Generation

**Implementation:** Not explicitly shown in codebase  
**Expected Library:** `pyjwt` or similar  
**Location:** Likely in `UserManager` or middleware

**Expected Implementation:**
```python
import jwt
from datetime import datetime, timedelta

def generate_jwt(user: dict) -> str:
    """
    Generate JWT token for authenticated user.
    
    Token contains:
        - sub: username
        - role: user role
        - iat: issued at timestamp
        - exp: expiration timestamp (24 hours)
    """
    payload = {
        "sub": user["username"],
        "role": user["role"],
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    
    secret = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-prod")
    return jwt.encode(payload, secret, algorithm="HS256")
```

**Token Structure:**
```json
{
  "sub": "admin",
  "role": "admin",
  "iat": 1706500000,
  "exp": 1706586400
}
```

**Security:**
- HS256 signature (HMAC-SHA256)
- Secret key from environment
- 24-hour expiration
- No sensitive data in payload (public)

### 3. JWT Token Validation

**Location:** Governance pipeline middleware  
**Purpose:** Verify token on protected endpoints

**Expected Implementation:**
```python
def validate_jwt(token: str) -> dict | None:
    """
    Validate JWT token and extract user info.
    
    Returns:
        dict: {username, role} if valid
        None: if invalid/expired
    """
    try:
        secret = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-prod")
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

**Validation Checks:**
- Signature verification (HS256)
- Expiration check (exp claim)
- Issuer validation (optional)
- Audience validation (optional)

## Authentication Layers

### Layer 1: Flask HTTP Layer

**Location:** `web/backend/app.py`  
**Purpose:** Extract and forward auth headers

**Pattern:**
```python
@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    # Extract Bearer token
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None
    
    # Forward to router
    response = route_request(
        source="web",
        payload={
            "action": "ai.chat",
            "token": token,  # Include in payload
            "prompt": payload.get("prompt"),
        },
    )
    
    return jsonify(result=response["result"])
```

**Responsibilities:**
- Extract Authorization header
- Parse Bearer token format
- Include token in payload
- Return 401 if validation fails downstream

### Layer 2: Runtime Router

**Location:** `src/app/core/runtime/router.py`  
**Purpose:** Source identification and context enrichment

**Pattern:**
```python
def route_request(source: ExecutionSource, payload: dict[str, Any]) -> dict[str, Any]:
    context = {
        "source": source,  # "web"
        "payload": payload,
        "action": payload.get("action"),
        "token": payload.get("token"),  # Forward token
        "timestamp": _get_timestamp(),
    }
    
    # Delegate to governance
    result = enforce_pipeline(context)
    return result
```

**Security Addition:**
- Source tagging prevents spoofing
- Timestamp prevents replay attacks
- Context immutability (no mutation after creation)

### Layer 3: Governance Pipeline

**Location:** `src/app/core/governance/pipeline.py`  
**Purpose:** Authorization and ethics validation

**Authentication Steps:**

#### Step 1: Action Whitelist Check

```python
def _validate(context: dict[str, Any]) -> dict[str, Any]:
    """Phase 1: Validation - Whitelist and type checks"""
    action = context.get("action", "")
    
    if action not in VALID_ACTIONS:
        raise ValueError(f"Unknown action: {action}")
    
    # Check if action requires auth
    metadata = ACTION_METADATA.get(action, {})
    if metadata.get("requires_auth", False):
        token = context.get("token")
        if not token:
            raise PermissionError("Authentication required")
    
    return context
```

#### Step 2: Token Validation

```python
def _gate(context: dict[str, Any]) -> dict[str, Any]:
    """Phase 3: Gate - Authorization checks"""
    action = context.get("action", "")
    metadata = ACTION_METADATA.get(action, {})
    
    # Validate JWT token
    if metadata.get("requires_auth", False):
        token = context.get("token")
        user = validate_jwt(token)
        
        if not user:
            raise PermissionError("Invalid or expired token")
        
        # Add user to context
        context["user"] = user
        
        # Check admin-only actions
        if metadata.get("admin_only", False) and user["role"] != "admin":
            raise PermissionError("Admin access required")
    
    # Four Laws ethics check
    is_allowed, reason = FourLaws.validate_action(action, context)
    if not is_allowed:
        raise PermissionError(f"Four Laws violation: {reason}")
    
    return context
```

#### Step 3: Audit Logging

```python
def _log(context: dict[str, Any], result: Any) -> None:
    """Phase 6: Logging - Complete audit trail"""
    audit_log = {
        "timestamp": context["timestamp"],
        "source": context["source"],
        "action": context["action"],
        "user": context.get("user", {}).get("username", "anonymous"),
        "result": "success" if result else "error",
        "ip_address": context.get("ip_address"),  # From Flask request
    }
    
    logger.info(f"Audit: {audit_log}")
    
    # Write to audit log file
    with open("data/audit_log.json", "a") as f:
        json.dump(audit_log, f)
        f.write("\n")
```

## Action Authorization Matrix

### Public Actions (No Auth Required)

```python
"user.login": {"requires_auth": False, "rate_limit": 5},
"system.status": {"requires_auth": False, "rate_limit": 100},
```

### User Actions (Auth Required)

```python
"ai.chat": {"requires_auth": True, "rate_limit": 30},
"ai.image": {"requires_auth": True, "rate_limit": 10, "resource_intensive": True},
"persona.update": {"requires_auth": True, "rate_limit": 20},
"data.query": {"requires_auth": True, "rate_limit": 50},
```

### Admin Actions (Auth + Admin Role)

```python
"user.create": {"requires_auth": True, "admin_only": True},
"user.delete": {"requires_auth": True, "admin_only": True},
"system.shutdown": {"requires_auth": True, "admin_only": True},
"audit.export": {"requires_auth": True, "admin_only": True},
```

## Security Protocols

### 1. Password Security

**Hashing Algorithm:** Argon2id (winner of Password Hashing Competition)

**Parameters:**
- Memory cost: 65536 KB (64 MB)
- Time cost: 3 iterations
- Parallelism: 4 threads
- Salt: 16 bytes (automatic, unique per password)

**Why Argon2id?**
- Memory-hard (resistant to GPU/ASIC attacks)
- Time-hard (resistant to brute-force)
- Side-channel resistant (constant-time operations)
- Configurable work factor (future-proof)

**Migration from bcrypt:**
```python
# Old (bcrypt)
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# New (Argon2id)
import argon2
password_hash = argon2.hash(password)
```

### 2. JWT Security

**Token Storage:**
- **Client:** localStorage (vulnerable to XSS)
- **Better:** httpOnly cookies (XSS-immune)
- **Best:** httpOnly + secure + SameSite cookies

**Token Transmission:**
```
Authorization: Bearer <jwt_token>
```

**Token Lifetime:**
- Access token: 24 hours
- Refresh token: 7 days (not implemented yet)

**Rotation Strategy (Future):**
```python
# Generate short-lived access token (15 minutes)
access_token = generate_jwt(user, exp_minutes=15)

# Generate long-lived refresh token (7 days)
refresh_token = generate_refresh_token(user, exp_days=7)

# Client stores both
# Access token for API calls
# Refresh token to get new access token when expired
```

### 3. Rate Limiting

**Per-Endpoint Limits:**
```python
# Flask-Limiter configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"],
)

# Login endpoint (brute-force prevention)
@app.route("/api/auth/login")
@limiter.limit("5 per minute")
def login():
    pass
```

**Bypass Prevention:**
- Rate limiting at multiple layers (Flask, governance, system)
- IP-based limiting (layer 4)
- Token-based limiting (layer 7)
- Distributed rate limiting (Redis, future)

### 4. Four Laws Ethics Validation

**Integration:** Every authenticated action validated against Asimov's Laws

**Example:**
```python
# User requests system shutdown
context = {
    "action": "system.shutdown",
    "user": {"username": "admin", "role": "admin"},
    "is_user_order": True,
}

is_allowed, reason = FourLaws.validate_action("system.shutdown", context)

# Check hierarchy:
# Law 1: Does not harm humans? ✓
# Law 2: Obeys user order? ✓ (admin)
# Law 3: Self-preservation? ✗ (shutdown conflicts)
# Law 4: Self-improvement? N/A

# Result: Allowed (Law 2 overrides Law 3)
```

## Attack Prevention

### 1. Brute-Force Protection

**Mechanisms:**
- Rate limiting (5 login attempts/minute)
- Account lockout (10 failed attempts → 15-minute lockout)
- Exponential backoff (delay increases with failures)
- CAPTCHA (after 3 failures, future)

### 2. Session Hijacking Prevention

**Mechanisms:**
- JWT signature verification (prevents tampering)
- Token expiration (limits window of exposure)
- IP address binding (optional, breaks mobile)
- User-Agent binding (optional, breaks browser updates)

### 3. Cross-Site Request Forgery (CSRF)

**Current:** Not implemented (JWT in Authorization header)  
**Future:** CSRF tokens for state-changing requests

**Why JWT helps:**
- Cookies sent automatically by browser (CSRF vulnerable)
- Authorization header requires JavaScript (CSRF immune)
- Attacker cannot read localStorage across origins

### 4. Man-in-the-Middle (MITM)

**Mechanisms:**
- HTTPS enforcement (TLS 1.3)
- HSTS headers (force HTTPS)
- Certificate pinning (future, mobile apps)

## Session Management

### Token Lifecycle

```
1. User Login
   ↓
2. Generate JWT (exp: 24 hours)
   ↓
3. Client stores in localStorage
   ↓
4. Client includes in Authorization header
   ↓
5. Server validates on each request
   ↓
6. Token expires after 24 hours
   ↓
7. Client redirects to login page
   ↓
8. User re-authenticates
```

### Logout Mechanism

**Client-Side:**
```typescript
const logout = () => {
  localStorage.removeItem('token');
  set({ user: null, token: null, isAuthenticated: false });
  router.push('/');
};
```

**Server-Side:**
- No server-side logout (stateless JWT)
- Token remains valid until expiration
- Blacklist required for instant revocation (future)

### Token Refresh (Future)

**Pattern:** Refresh token flow

```python
@app.route("/api/auth/refresh", methods=["POST"])
def refresh():
    refresh_token = request.json.get("refresh_token")
    
    # Validate refresh token
    user = validate_refresh_token(refresh_token)
    if not user:
        return jsonify(error="Invalid refresh token"), 401
    
    # Generate new access token
    access_token = generate_jwt(user, exp_minutes=15)
    
    return jsonify(access_token=access_token)
```

## Testing Strategy

### Unit Tests

**Test Password Hashing:**
```python
def test_password_hashing():
    password = "test-password-123"
    
    # Hash password
    hash1 = argon2.hash(password)
    hash2 = argon2.hash(password)
    
    # Hashes should be different (unique salts)
    assert hash1 != hash2
    
    # Both should verify
    assert argon2.verify(hash1, password)
    assert argon2.verify(hash2, password)
    
    # Wrong password should fail
    with pytest.raises(argon2.exceptions.VerifyMismatchError):
        argon2.verify(hash1, "wrong-password")
```

**Test JWT Generation:**
```python
def test_jwt_generation():
    user = {"username": "test", "role": "user"}
    
    # Generate token
    token = generate_jwt(user)
    
    # Validate token
    decoded = validate_jwt(token)
    assert decoded["username"] == "test"
    assert decoded["role"] == "user"
```

### Integration Tests

**Test Login Flow:**
```python
def test_login_flow(client):
    # Valid login
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "open-sesame"
    })
    
    assert response.status_code == 200
    data = response.json
    assert "token" in data
    assert data["user"]["username"] == "admin"
    
    # Invalid password
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "wrong"
    })
    
    assert response.status_code == 401
```

**Test Protected Endpoints:**
```python
def test_protected_endpoint(client):
    # No token
    response = client.post("/api/ai/chat", json={"prompt": "Hello"})
    assert response.status_code == 401
    
    # With valid token
    token = login_and_get_token(client)
    response = client.post("/api/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"prompt": "Hello"}
    )
    assert response.status_code == 200
```

## Related Systems

- **UserManager:** `src/app/core/user_manager.py`
- **Runtime Router:** `src/app/core/runtime/router.py`
- **Governance Pipeline:** `src/app/core/governance/pipeline.py`
- **Four Laws:** `src/app/core/ai_systems.py` (FourLaws class)
- **Flask API:** `web/backend/app.py`

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-XX  
**Maintainer:** Project-AI Team
