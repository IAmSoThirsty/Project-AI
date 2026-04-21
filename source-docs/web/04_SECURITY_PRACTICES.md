---
type: security-guide
module: web
tags: [security, authentication, jwt, cors, rate-limiting, owasp]
created: 2026-04-20
status: production
related_systems: [flask-backend, nextjs-frontend, middleware]
stakeholders: [security-team, backend-team, devops-team]
platform: web
dependencies: [flask-cors, flask-limiter, pyjwt, argon2-cffi]
---

# Web Security Best Practices

**Purpose:** Comprehensive security guidelines for Project-AI web application  
**Scope:** Authentication, authorization, input validation, CORS, rate limiting, OWASP Top 10  
**Standards:** OWASP, NIST, CWE

---

## Table of Contents

1. [Security Architecture](#security-architecture)
2. [Authentication & Authorization](#authentication--authorization)
3. [Input Validation & Sanitization](#input-validation--sanitization)
4. [CORS Configuration](#cors-configuration)
5. [Rate Limiting](#rate-limiting)
6. [CSRF Protection](#csrf-protection)
7. [XSS Prevention](#xss-prevention)
8. [SQL Injection Prevention](#sql-injection-prevention)
9. [Secrets Management](#secrets-management)
10. [OWASP Top 10 Mitigation](#owasp-top-10-mitigation)

---

## Security Architecture

### Defense in Depth Strategy

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Network Security (Firewall, CDN)                   │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: Application Gateway (Rate Limiting, WAF)           │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: Web Server (Nginx HTTPS, Security Headers)         │
├─────────────────────────────────────────────────────────────┤
│ Layer 4: Middleware (CORS, Auth, Input Validation)          │
├─────────────────────────────────────────────────────────────┤
│ Layer 5: Governance Pipeline (Four Laws, Content Filter)    │
├─────────────────────────────────────────────────────────────┤
│ Layer 6: Business Logic (Core Systems)                      │
├─────────────────────────────────────────────────────────────┤
│ Layer 7: Data Layer (Encrypted Storage, Audit Logs)         │
└─────────────────────────────────────────────────────────────┘
```

### Security Principles

1. **Zero Trust:** Never trust, always verify
2. **Least Privilege:** Minimum permissions required
3. **Defense in Depth:** Multiple security layers
4. **Fail Secure:** Default to deny on errors
5. **Separation of Concerns:** Security logic isolated from business logic

---

## Authentication & Authorization

### JWT Token-Based Authentication

**Architecture:**
```
Client Request → Extract Token → Verify Signature → Check Expiration → Authorize Action
```

#### Token Generation (Backend)

**File:** `app/core/security/auth.py`

```python
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional

SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
TOKEN_EXPIRATION_HOURS = 24

def generate_jwt_token(username: str, role: str) -> str:
    """
    Generate JWT token with expiration.
    
    Security features:
    - Unique JTI (JWT ID) for token revocation
    - Expiration time (24 hours)
    - Role-based access control
    - Cryptographic signature (HS256)
    """
    payload = {
        'sub': username,             # Subject (username)
        'role': role,                # User role (superuser, user)
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS),
        'iat': datetime.utcnow(),    # Issued at
        'jti': secrets.token_urlsafe(32)  # Unique token ID
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(token: str) -> Optional[Dict]:
    """
    Verify JWT token and return payload.
    
    Returns None if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None
```

#### Password Hashing (Argon2)

**✅ Secure (Current Implementation):**
```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=2,          # Number of iterations
    memory_cost=65536,    # Memory usage (64 MB)
    parallelism=4,        # Number of threads
    hash_len=32,          # Hash length in bytes
    salt_len=16           # Salt length in bytes
)

def hash_password(password: str) -> str:
    """Hash password using Argon2."""
    return ph.hash(password)

def verify_password(password_hash: str, password: str) -> bool:
    """Verify password against hash."""
    try:
        ph.verify(password_hash, password)
        
        # Rehash if parameters changed
        if ph.check_needs_rehash(password_hash):
            return hash_password(password)
        
        return True
    except VerifyMismatchError:
        return False
```

**❌ Insecure (NEVER use):**
```python
# Plain text storage
password = "open-sesame"  # CRITICAL VULNERABILITY

# SHA-256 without salt
import hashlib
password_hash = hashlib.sha256(password.encode()).hexdigest()  # VULNERABLE TO RAINBOW TABLES

# bcrypt with low work factor
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(4))  # TOO WEAK (use 12+)
```

#### Role-Based Access Control (RBAC)

**Decorator:**
```python
from functools import wraps
from flask import request, jsonify

def require_auth(required_role: Optional[str] = None):
    """
    Authentication decorator with optional role check.
    
    Usage:
        @app.route('/api/admin/users')
        @require_auth(required_role='superuser')
        def admin_users():
            return jsonify(users)
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Extract token
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify(error="unauthorized", message="Missing or invalid token"), 401
            
            token = auth_header.replace("Bearer ", "")
            
            # Verify token
            payload = verify_jwt_token(token)
            if not payload:
                return jsonify(error="unauthorized", message="Invalid or expired token"), 401
            
            # Check role
            if required_role and payload.get("role") != required_role:
                return jsonify(error="forbidden", message="Insufficient permissions"), 403
            
            # Inject user into request context
            request.user = payload
            
            return f(*args, **kwargs)
        return wrapper
    return decorator
```

**Usage:**
```python
@app.route("/api/admin/stats")
@require_auth(required_role="superuser")
def admin_stats():
    return jsonify(stats)

@app.route("/api/user/profile")
@require_auth()
def user_profile():
    return jsonify(user=request.user)
```

#### Token Revocation (Black List)

**Implementation:**
```python
from datetime import datetime
import redis

# Redis for token blacklist
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def revoke_token(jti: str, exp: datetime):
    """Add token to blacklist until expiration."""
    ttl = int((exp - datetime.utcnow()).total_seconds())
    redis_client.setex(f"blacklist:{jti}", ttl, "1")

def is_token_revoked(jti: str) -> bool:
    """Check if token is blacklisted."""
    return redis_client.exists(f"blacklist:{jti}") > 0

# Usage in verify_jwt_token
def verify_jwt_token(token: str) -> Optional[Dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check blacklist
        if is_token_revoked(payload.get("jti")):
            logger.warning(f"Revoked token used: {payload.get('jti')}")
            return None
        
        return payload
    except jwt.InvalidTokenError:
        return None
```

---

## Input Validation & Sanitization

### Validation Strategy

**1. Frontend Validation (UX only, NOT security):**
```typescript
// Client-side validation (TypeScript)
const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
const passwordMinLength = 8;

function validateInput(username: string, password: string) {
  if (!usernameRegex.test(username)) {
    return { valid: false, error: "Username must be 3-20 alphanumeric characters" };
  }
  if (password.length < passwordMinLength) {
    return { valid: false, error: "Password must be at least 8 characters" };
  }
  return { valid: true };
}
```

**2. Backend Validation (SECURITY-CRITICAL):**
```python
from typing import Optional, Tuple
import re

def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username format.
    
    Rules:
    - 3-20 characters
    - Alphanumeric + underscore only
    - No leading/trailing whitespace
    """
    if not username:
        return False, "Username is required"
    
    username = username.strip()
    
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be 3-20 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, None

def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Rules:
    - 8+ characters
    - At least 1 uppercase
    - At least 1 lowercase
    - At least 1 number
    - At least 1 special character
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least 1 uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least 1 lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least 1 number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least 1 special character"
    
    return True, None
```

### HTML Sanitization (XSS Prevention)

**Using bleach library:**
```python
import bleach

ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong', 'p', 'br', 'a']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

def sanitize_html(html: str) -> str:
    """
    Sanitize HTML to prevent XSS attacks.
    
    Strips all tags except whitelisted ones.
    Removes all JavaScript event handlers.
    """
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

# Usage
user_input = '<script>alert("XSS")</script><p>Hello</p>'
safe_output = sanitize_html(user_input)
# Result: '<p>Hello</p>'
```

### Path Traversal Prevention

```python
import os
from pathlib import Path

BASE_DIR = Path("/app/data")

def safe_file_access(user_path: str) -> Optional[Path]:
    """
    Prevent path traversal attacks (../ sequences).
    
    Returns None if path is outside BASE_DIR.
    """
    try:
        # Resolve absolute path
        resolved_path = (BASE_DIR / user_path).resolve()
        
        # Check if path is within BASE_DIR
        if not resolved_path.is_relative_to(BASE_DIR):
            logger.warning(f"Path traversal attempt: {user_path}")
            return None
        
        return resolved_path
    except Exception as e:
        logger.error(f"Path validation error: {e}")
        return None

# Usage
@app.route("/api/file/<path:filename>")
def get_file(filename):
    safe_path = safe_file_access(filename)
    if not safe_path:
        return jsonify(error="invalid-path"), 400
    
    return send_file(safe_path)
```

---

## CORS Configuration

### Production CORS Setup

**File:** `app/core/security/middleware.py`

```python
from flask_cors import CORS
from flask import Flask

def configure_cors(app: Flask):
    """
    Configure CORS with security best practices.
    
    Features:
    - Whitelist-based origins (NO wildcards in production)
    - Credentials support (cookies, Authorization header)
    - Preflight caching (1 hour)
    - Exposed headers for pagination
    """
    
    # PRODUCTION: Whitelist specific origins
    ALLOWED_ORIGINS = [
        "https://your-domain.com",
        "https://www.your-domain.com",
        "https://app.your-domain.com",
    ]
    
    # DEVELOPMENT: Allow localhost
    if app.config.get("ENV") == "development":
        ALLOWED_ORIGINS.extend([
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ])
    
    CORS(app, resources={
        r"/api/*": {
            "origins": ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Content-Type",
                "Authorization",
                "X-Requested-With",
            ],
            "expose_headers": [
                "Content-Range",
                "X-Total-Count",
                "X-Request-ID",
            ],
            "supports_credentials": True,  # Allow cookies/auth
            "max_age": 3600,  # Preflight cache (1 hour)
        }
    })
```

**❌ Insecure CORS (NEVER use):**
```python
# Wildcard origin with credentials
CORS(app, origins="*", supports_credentials=True)  # VULNERABILITY

# Allow all methods and headers
CORS(app, origins="*", methods="*", allow_headers="*")  # OVERLY PERMISSIVE
```

---

## Rate Limiting

### Flask-Limiter Configuration

**Implementation:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="redis://localhost:6379"  # Use Redis for distributed rate limiting
)

# Per-endpoint rate limits
@app.route("/api/auth/login", methods=["POST"])
@limiter.limit("10 per minute")  # Prevent brute force
def login():
    pass

@app.route("/api/ai/chat", methods=["POST"])
@limiter.limit("30 per minute")  # Prevent API abuse
def ai_chat():
    pass

@app.route("/api/ai/image", methods=["POST"])
@limiter.limit("5 per minute")  # Image gen is expensive
def ai_image():
    pass

# Custom key function (per user instead of per IP)
def get_user_key():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    payload = verify_jwt_token(token)
    return payload.get("sub") if payload else get_remote_address()

@app.route("/api/user/profile")
@limiter.limit("60 per minute", key_func=get_user_key)
def user_profile():
    pass
```

### Rate Limit Headers

**Response headers:**
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1619478000
```

**Custom error handler:**
```python
@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify(
        error="rate-limit-exceeded",
        message="Too many requests. Please try again later.",
        retry_after=e.description
    ), 429
```

---

## CSRF Protection

### Token-Based CSRF (Synchronizer Token Pattern)

**Backend:**
```python
from flask_wtf.csrf import CSRFProtect, generate_csrf

csrf = CSRFProtect(app)

# Exempt API endpoints (using JWT instead)
csrf.exempt("api")

# Generate CSRF token for forms
@app.route("/api/csrf-token")
def get_csrf_token():
    return jsonify(csrf_token=generate_csrf())
```

**Frontend:**
```typescript
// Fetch CSRF token
const response = await fetch('/api/csrf-token');
const { csrf_token } = await response.json();

// Include in form submission
const formData = new FormData();
formData.append('csrf_token', csrf_token);
formData.append('username', username);
```

### Double Submit Cookie Pattern (Alternative)

**Backend:**
```python
import secrets
from flask import make_response

@app.route("/api/login", methods=["POST"])
def login():
    # Verify CSRF token matches cookie
    csrf_token = request.headers.get("X-CSRF-Token")
    csrf_cookie = request.cookies.get("csrf_token")
    
    if not csrf_token or csrf_token != csrf_cookie:
        return jsonify(error="csrf-token-mismatch"), 403
    
    # Process login...
    response = make_response(jsonify(success=True))
    
    # Set new CSRF token
    new_csrf_token = secrets.token_urlsafe(32)
    response.set_cookie("csrf_token", new_csrf_token, httponly=True, secure=True, samesite="Strict")
    
    return response
```

---

## XSS Prevention

### Content Security Policy (CSP)

**Nginx configuration:**
```nginx
add_header Content-Security-Policy "
    default-src 'self';
    script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
    img-src 'self' data: https:;
    font-src 'self' https://fonts.gstatic.com;
    connect-src 'self' https://api.your-domain.com;
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
" always;
```

### Output Encoding

**Always escape user-generated content:**
```python
from markupsafe import escape

@app.route("/api/user/<username>")
def user_page(username):
    # Escape username to prevent XSS
    safe_username = escape(username)
    return jsonify(username=safe_username)
```

**React auto-escapes by default:**
```tsx
// Safe (React escapes automatically)
<div>{userInput}</div>

// Unsafe (bypasses escaping)
<div dangerouslySetInnerHTML={{ __html: userInput }} />  // AVOID
```

---

## SQL Injection Prevention

### Parameterized Queries (ALWAYS)

**✅ Secure (Parameterized):**
```python
# SQLAlchemy ORM (safe by default)
user = db.session.query(User).filter_by(username=username).first()

# Raw SQL with parameters
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
```

**❌ Insecure (String concatenation):**
```python
# NEVER DO THIS
query = f"SELECT * FROM users WHERE username = '{username}'"  # SQL INJECTION VULNERABILITY
cursor.execute(query)
```

### Input Validation

```python
def validate_sql_input(value: str) -> bool:
    """
    Validate input doesn't contain SQL injection attempts.
    
    Note: This is defense-in-depth. Use parameterized queries as primary defense.
    """
    dangerous_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
        r"(--|;|/\*|\*/|xp_|sp_)",
        r"('|\"|`)",
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            logger.warning(f"Potential SQL injection attempt: {value}")
            return False
    
    return True
```

---

## Secrets Management

### Environment Variables (Recommended)

**✅ Secure:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable not set")

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
```

**❌ Insecure:**
```python
# NEVER hardcode secrets
SECRET_KEY = "my-secret-key-123"  # CRITICAL VULNERABILITY
API_KEY = "sk-proj-..."  # EXPOSED SECRET
```

### .env File Security

**Add to `.gitignore`:**
```gitignore
.env
.env.local
.env.production
*.pem
*.key
secrets/
```

### Encrypted Secrets (Fernet)

```python
from cryptography.fernet import Fernet

# Generate key (once)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
encrypted = cipher.encrypt(b"sensitive-data")

# Decrypt
decrypted = cipher.decrypt(encrypted)
```

---

## OWASP Top 10 Mitigation

### 1. Broken Access Control

**Mitigation:**
- ✅ JWT token authentication
- ✅ RBAC decorators (`@require_auth`)
- ✅ Token expiration (24 hours)
- ✅ Token revocation (blacklist)

### 2. Cryptographic Failures

**Mitigation:**
- ✅ Argon2 password hashing
- ✅ HTTPS/TLS for all traffic
- ✅ Fernet encryption for sensitive data
- ✅ Secure random token generation (`secrets` module)

### 3. Injection

**Mitigation:**
- ✅ Parameterized queries (SQLAlchemy)
- ✅ Input validation (regex, length checks)
- ✅ HTML sanitization (bleach)
- ✅ Path traversal prevention

### 4. Insecure Design

**Mitigation:**
- ✅ Governance pipeline (Four Laws validation)
- ✅ Defense in depth (7 security layers)
- ✅ Fail-secure defaults
- ✅ Rate limiting on all endpoints

### 5. Security Misconfiguration

**Mitigation:**
- ✅ `DEBUG=False` in production
- ✅ Security headers (CSP, X-Frame-Options)
- ✅ CORS whitelist (no wildcards)
- ✅ Regular dependency updates

### 6. Vulnerable Components

**Mitigation:**
- ✅ Automated dependency scanning (`pip-audit`, `npm audit`)
- ✅ GitHub Dependabot enabled
- ✅ Regular updates via CI/CD
- ✅ Pinned versions in `requirements.txt`

### 7. Identification & Authentication Failures

**Mitigation:**
- ✅ Strong password policy (8+ chars, complexity)
- ✅ Argon2 hashing (time/memory cost)
- ✅ JWT with expiration
- ✅ Rate limiting on login (10 attempts/min)

### 8. Software & Data Integrity Failures

**Mitigation:**
- ✅ Code signing (Git commit signatures)
- ✅ Dependency integrity (package lock files)
- ✅ Audit logs for all sensitive operations
- ✅ Immutable deployments (Docker images)

### 9. Security Logging & Monitoring

**Mitigation:**
- ✅ Structured logging (JSON format)
- ✅ Sentry error tracking
- ✅ Audit logs for auth events
- ✅ UptimeRobot monitoring

### 10. Server-Side Request Forgery (SSRF)

**Mitigation:**
- ✅ URL validation (whitelist domains)
- ✅ No user-controlled redirect URLs
- ✅ Network segmentation (private subnets)
- ✅ Metadata endpoint blocking (169.254.169.254)

---

## Security Checklist

### Pre-Production

- [ ] All secrets in environment variables
- [ ] `DEBUG=False` in production
- [ ] HTTPS enabled (SSL/TLS certificates)
- [ ] CORS whitelist configured (no wildcards)
- [ ] Rate limiting enabled on all endpoints
- [ ] JWT expiration set (24 hours)
- [ ] Argon2 password hashing enabled
- [ ] Input validation on all endpoints
- [ ] SQL parameterized queries only
- [ ] Security headers configured (CSP, X-Frame-Options)
- [ ] Dependency scanning enabled (pip-audit, npm audit)
- [ ] Error messages don't leak sensitive info
- [ ] Audit logging enabled
- [ ] Monitoring configured (Sentry, UptimeRobot)

### Post-Production

- [ ] Penetration testing completed
- [ ] Security audit performed
- [ ] Incident response plan documented
- [ ] Backup strategy tested
- [ ] Security team trained
- [ ] Bug bounty program considered

---

## Related Documentation

- [Flask Backend API](./01_FLASK_BACKEND_API.md)
- [Deployment Guide](./03_DEPLOYMENT_GUIDE.md)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

**Last Updated:** 2026-04-20  
**Maintainer:** Security Team  
**Review Cycle:** Monthly
