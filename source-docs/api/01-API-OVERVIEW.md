---
title: API Architecture Overview
category: api
layer: api-layer
audience: [integrator, maintainer, expert]
status: production
classification: technical-reference
confidence: verified
requires: [PROGRAM_SUMMARY.md, DEVELOPER_QUICK_REFERENCE.md]
time_estimate: 30min
last_updated: 2025-06-09
version: 2.0.0
---

# API Architecture Overview

## Purpose

Project-AI implements a multi-path API architecture supporting three distinct execution contexts:

1. **FastAPI Backend** (Port 8001) - Governance-first, TARL-enforced REST API
2. **Flask Web Backend** (Port 5000) - Web application API adapter
3. **Desktop Internal API** - Direct Python module integration

This document provides architectural overview and navigation to detailed API documentation.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT INTERFACES                          │
├─────────────┬─────────────────┬─────────────────┬──────────────┤
│   Web UI    │   Mobile App    │   Desktop GUI   │   CLI Tools  │
│ (React/JS)  │   (OpenClaw)    │    (PyQt6)      │  (Python)    │
└──────┬──────┴────────┬────────┴────────┬────────┴──────┬───────┘
       │               │                 │               │
       ▼               ▼                 ▼               ▼
┌──────────────────────────────────────────────────────────────────┐
│                       API LAYER (3 Paths)                        │
├──────────────────┬───────────────────┬──────────────────────────┤
│  FastAPI         │  Flask            │  Direct Integration      │
│  (Port 8001)     │  (Port 5000)      │  (Python Modules)        │
│  ├─ TARL         │  ├─ Auth          │  ├─ LeatherBook UI       │
│  ├─ Triumvirate  │  ├─ Chat          │  ├─ Dashboard Handlers   │
│  ├─ Save Points  │  ├─ Image Gen     │  └─ Direct AI Systems    │
│  ├─ OpenClaw     │  └─ Persona       │                          │
│  └─ Firewall     │                   │                          │
└────────┬─────────┴─────────┬─────────┴──────────────┬───────────┘
         │                   │                        │
         ▼                   ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RUNTIME ROUTER (Unified)                     │
│                app.core.runtime.router.py                       │
│  • Routes: web/desktop/cli/agent/temporal/test                 │
│  • Ensures ALL paths flow through governance                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  GOVERNANCE PIPELINE (Hard Gate)                │
│               app.core.governance.pipeline.py                   │
│  1. Validate  → Input sanitization, type checking              │
│  2. Simulate  → Shadow execution, impact analysis              │
│  3. Gate      → Four Laws, permissions, TARL                   │
│  4. Execute   → Actual operation                               │
│  5. Commit    → State persistence with rollback                │
│  6. Log       → Complete audit trail                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI ORCHESTRATOR & SYSTEMS                    │
│  • 6 AI Systems (FourLaws, Persona, Memory, Learning, etc.)    │
│  • OpenAI/OpenRouter Integration                               │
│  • Image Generation (DALL-E, Stable Diffusion)                 │
│  • User Management (Argon2, JWT)                               │
│  • Command Override System                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Design Principles

### 1. **Multi-Path Sovereignty**

Three execution paths coexist **WITHOUT** forced unification:

- **FastAPI**: Governance-first, TARL-enforced, ideal for external integrations
- **Flask**: Lightweight web adapter, routes through governance via router
- **Desktop**: Direct module integration, maximum performance

**Key Insight**: Router is a **coordination layer**, not a single entry point.

### 2. **Governance-First Design**

ALL API requests flow through the **Governance Pipeline** (`app.core.governance.pipeline`):

```python
def enforce_pipeline(context: dict[str, Any]) -> Any:
    """
    6-Phase Pipeline:
    1. Validate   - Input sanitization, action registry check
    2. Simulate   - Shadow execution for impact prediction
    3. Gate       - Authorization (Four Laws, TARL, permissions)
    4. Execute    - Actual operation
    5. Commit     - State persistence with rollback
    6. Log        - Audit trail
    """
```

**Security Guarantee**: No direct system access bypassing governance.

### 3. **Action Registry Pattern**

All valid API actions are whitelisted in `VALID_ACTIONS`:

```python
VALID_ACTIONS = {
    # AI Operations
    "ai.chat", "ai.image", "ai.code", "ai.analyze",
    
    # User Management
    "user.login", "user.logout", "user.create", "user.update",
    
    # Persona Operations
    "persona.update", "persona.query", "persona.reset",
    
    # ... 43+ registered actions
}
```

**Security Guarantee**: Unknown actions are rejected at validation phase.

### 4. **Production-Grade Security**

- **Authentication**: JWT tokens (HS256) + Argon2id password hashing
- **Rate Limiting**: Configurable per-endpoint (5/min auth, 100/min API)
- **CORS**: Strict origin control
- **Input Sanitization**: HTML entity encoding, null byte removal, path traversal prevention
- **MFA Support**: TOTP (pyotp) with backup codes
- **Token Revocation**: Blacklist + refresh token rotation

---

## API Endpoint Categories

### **1. FastAPI Backend (Port 8001)**

Main governance-first API with TARL enforcement.

**Base URL**: `http://localhost:8001`

| Category | Endpoints | Documentation |
|----------|-----------|---------------|
| Governance | `/intent`, `/execute`, `/tarl`, `/audit` | [02-FASTAPI-MAIN-ROUTES.md](./02-FASTAPI-MAIN-ROUTES.md) |
| Save Points | `/api/savepoints/*` | [03-SAVE-POINTS-API.md](./03-SAVE-POINTS-API.md) |
| OpenClaw | `/openclaw/*` | [04-OPENCLAW-LEGION-API.md](./04-OPENCLAW-LEGION-API.md) |
| Firewall | `/api/firewall/*` | [05-CONTRARIAN-FIREWALL-API.md](./05-CONTRARIAN-FIREWALL-API.md) |
| Health | `/health`, `/` | [02-FASTAPI-MAIN-ROUTES.md](./02-FASTAPI-MAIN-ROUTES.md) |

### **2. Flask Web Backend (Port 5000)**

Lightweight web application API adapter.

**Base URL**: `http://localhost:5000`

| Category | Endpoints | Documentation |
|----------|-----------|---------------|
| Status | `/api/status` | [06-FLASK-WEB-BACKEND.md](./06-FLASK-WEB-BACKEND.md) |
| Auth | `/api/auth/login` | [06-FLASK-WEB-BACKEND.md](./06-FLASK-WEB-BACKEND.md) |
| AI Chat | `/api/ai/chat` | [06-FLASK-WEB-BACKEND.md](./06-FLASK-WEB-BACKEND.md) |
| AI Image | `/api/ai/image` | [06-FLASK-WEB-BACKEND.md](./06-FLASK-WEB-BACKEND.md) |
| Persona | `/api/persona/update` | [06-FLASK-WEB-BACKEND.md](./06-FLASK-WEB-BACKEND.md) |

### **3. Desktop Internal API**

Direct Python module integration (no HTTP).

| Module | Purpose | Documentation |
|--------|---------|---------------|
| `runtime.router` | Multi-path coordination | [07-RUNTIME-ROUTER.md](./07-RUNTIME-ROUTER.md) |
| `governance.pipeline` | Universal enforcement | [08-GOVERNANCE-PIPELINE.md](./08-GOVERNANCE-PIPELINE.md) |
| `security.auth` | JWT + Argon2 + MFA | [09-SECURITY-AUTH.md](./09-SECURITY-AUTH.md) |
| `security.middleware` | CORS + Rate Limiting | [10-SECURITY-MIDDLEWARE.md](./10-SECURITY-MIDDLEWARE.md) |

---

## Request Flow Examples

### Example 1: Web UI → Flask → Governance → AI System

```
1. User submits chat prompt via React UI
   ↓
2. POST /api/ai/chat (Flask endpoint)
   ↓
3. route_request(source="web", payload={action: "ai.chat", ...})
   ↓
4. enforce_pipeline(context)
   ├─ Validate: Sanitize prompt, check action registry
   ├─ Simulate: Predict resource usage (network: high)
   ├─ Gate: Check JWT token, verify permissions
   ├─ Execute: Call IntelligenceEngine.chat()
   ├─ Commit: Log conversation to memory system
   └─ Log: Audit trail entry
   ↓
5. Return JSON response to Flask
   ↓
6. Return HTTP 200 to React UI
```

### Example 2: Desktop UI → Direct Integration

```
1. User clicks "Generate Image" button in PyQt6
   ↓
2. dashboard_handlers.handle_generate_image()
   ↓
3. route_request(source="desktop", payload={action: "ai.image", ...})
   ↓
4. enforce_pipeline(context)
   ├─ Validate: Content filter check, style validation
   ├─ Simulate: Predict resource usage (cpu: high, memory: high)
   ├─ Gate: Check command override state
   ├─ Execute: ImageGenerator.generate()
   ├─ Commit: Save to data/images/
   └─ Log: Generation history entry
   ↓
5. Return image path to dashboard
   ↓
6. Display image in right panel
```

### Example 3: External Integration → FastAPI → Governance

```
1. OpenClaw agent sends message
   ↓
2. POST /openclaw/message (FastAPI endpoint)
   ↓
3. Legion agent processes through Triumvirate
   ↓
4. route_request(source="agent", payload={action: "agent.execute", ...})
   ↓
5. enforce_pipeline(context)
   ├─ Validate: Check capability ID against registry
   ├─ Simulate: Predict threat level (Cerberus)
   ├─ Gate: TARL enforcement (Galahad, Cerberus, CodexDeus)
   ├─ Execute: Capability execution via orchestrator
   ├─ Commit: EED memory storage
   └─ Log: Audit entry with governance metadata
   ↓
6. Return JSON response to OpenClaw
```

---

## Security Model

### Authentication Flow

```
┌──────────┐    POST /api/auth/login      ┌──────────────┐
│  Client  │────────────────────────────►│   Flask API   │
│          │  {username, password}        │               │
└──────────┘                              └───────┬───────┘
                                                  │
                                   route_request("user.login")
                                                  │
                                                  ▼
                                        ┌──────────────────┐
                                        │  Runtime Router  │
                                        └────────┬─────────┘
                                                 │
                                                 ▼
                                        ┌──────────────────┐
                                        │ Governance Gate  │
                                        │ 1. Validate input│
                                        │ 2. Check registry│
                                        └────────┬─────────┘
                                                 │
                                                 ▼
                                        ┌──────────────────┐
                                        │  User Manager    │
                                        │ 1. Argon2 verify │
                                        │ 2. Generate JWT  │
                                        │ 3. Create session│
                                        └────────┬─────────┘
                                                 │
                                    Return: {token, user, role}
                                                 │
┌──────────┐                                    ▼
│  Client  │◄─────────────────────────────────────
│  Stores  │  HTTP 200 {token, user}
│   JWT    │
└──────────┘
```

### Authorization Flow

```
┌──────────┐    POST /api/ai/chat         ┌──────────────┐
│  Client  │────────────────────────────►│   Flask API   │
│          │  Authorization: Bearer ...   │               │
└──────────┘                              └───────┬───────┘
                                                  │
                                   Extract JWT from header
                                                  │
                                                  ▼
                                        ┌──────────────────┐
                                        │  verify_jwt_token│
                                        │ 1. Check blacklist│
                                        │ 2. Verify signature│
                                        │ 3. Check expiration│
                                        └────────┬─────────┘
                                                 │
                                          Valid? ├─No──► HTTP 401
                                                 │
                                                Yes
                                                 │
                                                 ▼
                                        ┌──────────────────┐
                                        │ Governance Gate  │
                                        │ 1. Check action  │
                                        │ 2. Verify role   │
                                        │ 3. Apply TARL    │
                                        └────────┬─────────┘
                                                 │
                                          Allowed? ├─No──► HTTP 403
                                                 │
                                                Yes
                                                 │
                                                 ▼
                                        [Execute Action]
```

---

## Error Handling Strategy

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | Success | Request completed successfully |
| 201 | Created | Resource created (e.g., save point) |
| 400 | Bad Request | Validation failed, missing fields |
| 401 | Unauthorized | Invalid/expired token, auth failed |
| 403 | Forbidden | TARL denied, insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Execution failed, uncaught exception |

### Error Response Format

**Standard Error Response**:
```json
{
  "status": "error",
  "error": "validation-failed",
  "message": "Missing required field: username",
  "metadata": {
    "source": "web",
    "action": "user.login",
    "timestamp": "2025-06-09T12:34:56.789Z"
  }
}
```

**Governance Denial Response**:
```json
{
  "status": "error",
  "error": "governance-denied",
  "message": "Execution denied by governance",
  "governance": {
    "intent_hash": "abc123...",
    "tarl_version": "1.0",
    "votes": [
      {"pillar": "Galahad", "verdict": "allow", "reason": "..."},
      {"pillar": "Cerberus", "verdict": "deny", "reason": "High-risk action blocked"}
    ],
    "final_verdict": "deny",
    "timestamp": 1717934096.789
  }
}
```

---

## Performance Characteristics

### Latency Benchmarks

| Endpoint | P50 | P95 | P99 | Notes |
|----------|-----|-----|-----|-------|
| `/api/status` | 5ms | 10ms | 15ms | Health check |
| `/api/auth/login` | 200ms | 350ms | 500ms | Argon2 hashing |
| `/api/ai/chat` | 2s | 5s | 10s | OpenAI API latency |
| `/api/ai/image` | 30s | 60s | 90s | Stable Diffusion |
| `/openclaw/message` | 500ms | 1.5s | 3s | Full governance pipeline |
| `/api/savepoints/create` | 100ms | 250ms | 500ms | File I/O + compression |

### Throughput

- **FastAPI**: 1000+ req/sec (simple endpoints), 10-50 req/sec (AI operations)
- **Flask**: 500+ req/sec (WSGI), 2000+ req/sec (with Gunicorn workers)
- **Desktop**: No HTTP overhead, direct function calls

### Resource Usage

- **Memory**: 200MB baseline + 500MB per AI operation + 1GB per image generation
- **CPU**: Minimal except image generation (95%+ utilization for 20-60s)
- **Network**: OpenAI/OpenRouter API calls (100KB-5MB per request)

---

## Development Workflows

### Starting the APIs

**FastAPI (Development)**:
```bash
python start_api.py
# or
uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
```

**FastAPI (Production)**:
```bash
python start_api.py --prod
# or
gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

**Flask (Development)**:
```bash
cd web/backend
flask run --host 0.0.0.0 --port 5000
```

**Flask (Production)**:
```bash
gunicorn web.backend.app:app --workers 4 --bind 0.0.0.0:5000
```

### Testing APIs

**Health Check**:
```bash
# FastAPI
curl http://localhost:8001/health

# Flask
curl http://localhost:5000/api/status
```

**Authentication**:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secure123"}'
```

**Authenticated Request**:
```bash
TOKEN="eyJhbGc..."  # From login response

curl -X POST http://localhost:5000/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"prompt": "Hello, AI!", "model": "gpt-4", "provider": "openai"}'
```

### API Documentation

- **FastAPI Swagger UI**: http://localhost:8001/docs
- **FastAPI ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json
- **Postman Collection**: `api/project-ai.postman_collection.json`

---

## Related Documentation

### API Implementation Details

1. **[02-FASTAPI-MAIN-ROUTES.md](./02-FASTAPI-MAIN-ROUTES.md)** - Core governance endpoints
2. **[03-SAVE-POINTS-API.md](./03-SAVE-POINTS-API.md)** - Save/restore system state
3. **[04-OPENCLAW-LEGION-API.md](./04-OPENCLAW-LEGION-API.md)** - Legion agent integration
4. **[05-CONTRARIAN-FIREWALL-API.md](./05-CONTRARIAN-FIREWALL-API.md)** - Advanced threat detection
5. **[06-FLASK-WEB-BACKEND.md](./06-FLASK-WEB-BACKEND.md)** - Web application adapter
6. **[07-RUNTIME-ROUTER.md](./07-RUNTIME-ROUTER.md)** - Multi-path coordination
7. **[08-GOVERNANCE-PIPELINE.md](./08-GOVERNANCE-PIPELINE.md)** - Universal enforcement
8. **[09-SECURITY-AUTH.md](./09-SECURITY-AUTH.md)** - JWT + Argon2 + MFA
9. **[10-SECURITY-MIDDLEWARE.md](./10-SECURITY-MIDDLEWARE.md)** - CORS + rate limiting
10. **[11-INPUT-VALIDATION.md](./11-INPUT-VALIDATION.md)** - Sanitization + schemas
11. **[12-API-CLIENT-EXAMPLES.md](./12-API-CLIENT-EXAMPLES.md)** - Python/JS/cURL examples

### Core System Documentation

- **[PROGRAM_SUMMARY.md](../PROGRAM_SUMMARY.md)** - Complete architecture (600+ lines)
- **[DEVELOPER_QUICK_REFERENCE.md](../DEVELOPER_QUICK_REFERENCE.md)** - GUI component API
- **[.github/instructions/ARCHITECTURE_QUICK_REF.md](../.github/instructions/ARCHITECTURE_QUICK_REF.md)** - Visual diagrams

---

## Quick Reference

### Key Files

| File | Purpose | LOC |
|------|---------|-----|
| `api/main.py` | FastAPI application | 468 |
| `api/save_points_routes.py` | Save Points API | 91 |
| `integrations/openclaw/api_endpoints.py` | Legion API | 185 |
| `web/backend/app.py` | Flask adapter | 176 |
| `src/app/core/runtime/router.py` | Multi-path router | 93 |
| `src/app/core/governance/pipeline.py` | Governance pipeline | 600+ |
| `src/app/core/security/auth.py` | Authentication | 577 |
| `src/app/core/security/middleware.py` | Security middleware | 96 |
| `src/app/core/governance/validators.py` | Input validation | 111 |

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...                    # OpenAI API key
JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')

# Optional
HUGGINGFACE_API_KEY=hf_...               # For Stable Diffusion
FERNET_KEY=$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')
SMTP_USERNAME=...                        # For email alerts
SMTP_PASSWORD=...                        # For email alerts
```

### Common Actions

| Action | Description | Auth Required | Rate Limit |
|--------|-------------|---------------|------------|
| `ai.chat` | AI conversation | Yes | 30/min |
| `ai.image` | Image generation | Yes | 10/hour |
| `user.login` | Authentication | No | 5/min |
| `user.create` | User registration | Admin | 10/hour |
| `persona.update` | AI personality | Yes | 100/min |
| `agent.execute` | Agent operation | Yes | 50/min |

---

## Version History

- **v2.0.0** (2025-06-09): Multi-path architecture, governance pipeline, MFA support
- **v1.5.0** (2025-05-15): JWT authentication, refresh tokens
- **v1.0.0** (2025-04-01): Initial FastAPI implementation with TARL

---

**Next**: See [02-FASTAPI-MAIN-ROUTES.md](./02-FASTAPI-MAIN-ROUTES.md) for FastAPI endpoint details.
