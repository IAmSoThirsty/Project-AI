---
title: Security Middleware
category: api
layer: security-layer
audience: [maintainer]
status: production
classification: technical-reference
confidence: verified
requires: [01-API-OVERVIEW.md, 06-FLASK-WEB-BACKEND.md]
time_estimate: 10min
last_updated: 2025-06-09
version: 1.0.0
---

# Security Middleware

## Purpose

CORS and rate limiting configuration for Flask web backend.

**File**: `src/app/core/security/middleware.py` (96 lines)

---

## CORS Configuration

```python
def configure_cors(app, allowed_origins: list[str] | None = None):
    """
    Configure Cross-Origin Resource Sharing
    
    Default allowed origins:
    - http://localhost:3000  (React dev server)
    - http://localhost:5173  (Vite dev server)
    
    Production: Set explicit origins only
    """
    from flask_cors import CORS
    
    if allowed_origins is None:
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:5173"
        ]
    
    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"]
    )
```

**Production Configuration**:
```python
configure_cors(app, allowed_origins=[
    "https://app.project-ai.com",
    "https://dashboard.project-ai.com"
])
```

---

## Rate Limiting

```python
def configure_rate_limiting(app):
    """
    Configure rate limits per endpoint
    
    Limits:
    - Authentication: 5/minute
    - API calls: 100/minute
    - Image generation: 10/hour
    """
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per minute"],
        storage_uri="memory://"
    )
    
    app.limiter = limiter  # Store for decorator usage
```

**Endpoint-Specific Limits**:
```python
@app.route("/api/auth/login")
@app.limiter.limit("5 per minute")
def login():
    ...

@app.route("/api/ai/image")
@app.limiter.limit("10 per hour")
def ai_image():
    ...
```

---

## Request Sanitization

```python
class RequestSanitizer:
    """Sanitize incoming requests to prevent attacks"""
    
    @staticmethod
    def sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
        """Remove dangerous headers"""
        dangerous = ["X-Forwarded-For", "X-Real-IP"]
        return {k: v for k, v in headers.items() if k not in dangerous}
    
    @staticmethod
    def validate_content_type(content_type: str | None) -> bool:
        """Validate content type is allowed"""
        allowed = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data"
        ]
        if not content_type:
            return False
        
        base_type = content_type.split(";")[0].strip()
        return base_type in allowed
```

---

## Related Documentation
- **[01-API-OVERVIEW.md](./01-API-OVERVIEW.md)** - Architecture
- **[06-FLASK-WEB-BACKEND.md](./06-FLASK-WEB-BACKEND.md)** - Flask endpoints
