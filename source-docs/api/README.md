# API Documentation Index

## Overview

Comprehensive documentation for Project-AI's multi-path API architecture (FastAPI + Flask + Desktop).

**Total Documents**: 12  
**Coverage**: Routes, controllers, middleware, security, validation, client examples

---

## Quick Navigation

### Core API Architecture
1. **[01-API-OVERVIEW.md](./01-API-OVERVIEW.md)** ⭐  
   Complete architecture overview, multi-path design, request flows, security model

### FastAPI Backend (Port 8001)
2. **[02-FASTAPI-MAIN-ROUTES.md](./02-FASTAPI-MAIN-ROUTES.md)**  
   Governance endpoints, TARL enforcement, Triumvirate voting, audit logs

3. **[03-SAVE-POINTS-API.md](./03-SAVE-POINTS-API.md)**  
   Time-travel state management, auto-save service, restore operations

4. **[04-OPENCLAW-LEGION-API.md](./04-OPENCLAW-LEGION-API.md)**  
   Legion agent integration, OpenClaw message processing, capability registry

5. **[05-CONTRARIAN-FIREWALL-API.md](./05-CONTRARIAN-FIREWALL-API.md)**  
   Advanced threat detection (Phase 2 placeholder)

### Flask Web Backend (Port 5000)
6. **[06-FLASK-WEB-BACKEND.md](./06-FLASK-WEB-BACKEND.md)**  
   Web application adapter, React UI integration

### Core Infrastructure
7. **[07-RUNTIME-ROUTER.md](./07-RUNTIME-ROUTER.md)**  
   Multi-path coordination layer, source routing

8. **[08-GOVERNANCE-PIPELINE.md](./08-GOVERNANCE-PIPELINE.md)** ⭐  
   6-phase enforcement (validate, simulate, gate, execute, commit, log)

### Security & Authentication
9. **[09-SECURITY-AUTH.md](./09-SECURITY-AUTH.md)** ⭐  
   JWT tokens, Argon2 hashing, MFA (TOTP), token revocation

10. **[10-SECURITY-MIDDLEWARE.md](./10-SECURITY-MIDDLEWARE.md)**  
    CORS configuration, rate limiting

11. **[11-INPUT-VALIDATION.md](./11-INPUT-VALIDATION.md)**  
    Sanitization, schema validation, attack prevention

### Integration
12. **[12-API-CLIENT-EXAMPLES.md](./12-API-CLIENT-EXAMPLES.md)**  
    Python/JavaScript/cURL clients, React hooks, error handling

---

## By Audience

### **Integrators** (Building against the API)
Start here:
- [01-API-OVERVIEW.md](./01-API-OVERVIEW.md) - Architecture overview
- [12-API-CLIENT-EXAMPLES.md](./12-API-CLIENT-EXAMPLES.md) - Client implementations
- [02-FASTAPI-MAIN-ROUTES.md](./02-FASTAPI-MAIN-ROUTES.md) - Endpoint reference
- [09-SECURITY-AUTH.md](./09-SECURITY-AUTH.md) - Authentication flow

### **Maintainers** (Modifying the API)
Focus on:
- [08-GOVERNANCE-PIPELINE.md](./08-GOVERNANCE-PIPELINE.md) - Core enforcement logic
- [07-RUNTIME-ROUTER.md](./07-RUNTIME-ROUTER.md) - Request routing
- [11-INPUT-VALIDATION.md](./11-INPUT-VALIDATION.md) - Validation logic
- [03-SAVE-POINTS-API.md](./03-SAVE-POINTS-API.md) - State management

### **Experts** (System design decisions)
Deep dives:
- [01-API-OVERVIEW.md](./01-API-OVERVIEW.md) - Multi-path architecture
- [08-GOVERNANCE-PIPELINE.md](./08-GOVERNANCE-PIPELINE.md) - 6-phase pipeline
- [09-SECURITY-AUTH.md](./09-SECURITY-AUTH.md) - Cryptographic implementation
- [04-OPENCLAW-LEGION-API.md](./04-OPENCLAW-LEGION-API.md) - Agent integration

---

## By Topic

### **Authentication & Authorization**
- [09-SECURITY-AUTH.md](./09-SECURITY-AUTH.md) - JWT, Argon2, MFA
- [10-SECURITY-MIDDLEWARE.md](./10-SECURITY-MIDDLEWARE.md) - CORS, rate limits
- [11-INPUT-VALIDATION.md](./11-INPUT-VALIDATION.md) - Input sanitization

### **Governance & Compliance**
- [02-FASTAPI-MAIN-ROUTES.md](./02-FASTAPI-MAIN-ROUTES.md) - TARL enforcement
- [08-GOVERNANCE-PIPELINE.md](./08-GOVERNANCE-PIPELINE.md) - Pipeline phases
- [07-RUNTIME-ROUTER.md](./07-RUNTIME-ROUTER.md) - Multi-path coordination

### **External Integrations**
- [04-OPENCLAW-LEGION-API.md](./04-OPENCLAW-LEGION-API.md) - Legion agent
- [12-API-CLIENT-EXAMPLES.md](./12-API-CLIENT-EXAMPLES.md) - Client libraries
- [06-FLASK-WEB-BACKEND.md](./06-FLASK-WEB-BACKEND.md) - Web UI

### **State Management**
- [03-SAVE-POINTS-API.md](./03-SAVE-POINTS-API.md) - Time-travel saves
- [08-GOVERNANCE-PIPELINE.md](./08-GOVERNANCE-PIPELINE.md) - Commit phase

---

## Quick Start

### 1. **Understand the Architecture**
```bash
# Read this first
cat 01-API-OVERVIEW.md
```

### 2. **Start the APIs**
```bash
# FastAPI (governance-first)
python start_api.py
# Access: http://localhost:8001
# Docs: http://localhost:8001/docs

# Flask (web adapter)
cd web/backend && flask run
# Access: http://localhost:5000
```

### 3. **Test Authentication**
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secure123"}'

# Store token
TOKEN="eyJhbGc..."

# Test AI chat
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"prompt": "Hello AI"}'
```

### 4. **Integrate a Client**
See [12-API-CLIENT-EXAMPLES.md](./12-API-CLIENT-EXAMPLES.md) for Python/JS/cURL examples.

---

## Key Concepts

### **Multi-Path Architecture**
Three execution paths coexist WITHOUT forced unification:
- **FastAPI** (8001): Governance-first, TARL-enforced
- **Flask** (5000): Web adapter, routes through governance
- **Desktop**: Direct Python module integration

### **Governance Pipeline**
ALL requests flow through 6 phases:
1. **Validate** - Action registry + sanitization
2. **Simulate** - Impact prediction
3. **Gate** - Authorization (JWT, roles, Four Laws)
4. **Execute** - Actual operation
5. **Commit** - Atomic state persistence
6. **Log** - Complete audit trail

### **Security Model**
- **Authentication**: JWT (HS256) with 24h expiration
- **Passwords**: Argon2id (memory-hard, GPU-resistant)
- **MFA**: TOTP (RFC 6238) with backup codes
- **Rate Limiting**: Per-endpoint (5-100/min)
- **Input Validation**: XSS, SQL injection, path traversal prevention

---

## File Locations

| Documentation | Implementation |
|---------------|----------------|
| [02-FASTAPI-MAIN-ROUTES.md](./02-FASTAPI-MAIN-ROUTES.md) | `api/main.py` (468 lines) |
| [03-SAVE-POINTS-API.md](./03-SAVE-POINTS-API.md) | `api/save_points_routes.py` (91 lines) |
| [04-OPENCLAW-LEGION-API.md](./04-OPENCLAW-LEGION-API.md) | `integrations/openclaw/api_endpoints.py` (185 lines) |
| [06-FLASK-WEB-BACKEND.md](./06-FLASK-WEB-BACKEND.md) | `web/backend/app.py` (176 lines) |
| [07-RUNTIME-ROUTER.md](./07-RUNTIME-ROUTER.md) | `src/app/core/runtime/router.py` (93 lines) |
| [08-GOVERNANCE-PIPELINE.md](./08-GOVERNANCE-PIPELINE.md) | `src/app/core/governance/pipeline.py` (600+ lines) |
| [09-SECURITY-AUTH.md](./09-SECURITY-AUTH.md) | `src/app/core/security/auth.py` (577 lines) |
| [10-SECURITY-MIDDLEWARE.md](./10-SECURITY-MIDDLEWARE.md) | `src/app/core/security/middleware.py` (96 lines) |
| [11-INPUT-VALIDATION.md](./11-INPUT-VALIDATION.md) | `src/app/core/governance/validators.py` (111 lines) |

---

## API Versions

| Version | Date | Changes |
|---------|------|---------|
| **2.0.0** | 2025-06-09 | Multi-path architecture, governance pipeline, MFA |
| 1.5.0 | 2025-05-15 | JWT authentication, refresh tokens |
| 1.0.0 | 2025-04-01 | Initial FastAPI implementation with TARL |

---

## Related Documentation

### Core System Docs
- **[../PROGRAM_SUMMARY.md](../PROGRAM_SUMMARY.md)** - Complete architecture (600+ lines)
- **[../DEVELOPER_QUICK_REFERENCE.md](../DEVELOPER_QUICK_REFERENCE.md)** - GUI component API
- **[../.github/instructions/ARCHITECTURE_QUICK_REF.md](../.github/instructions/ARCHITECTURE_QUICK_REF.md)** - Visual diagrams

### Other Layers
- **[../core/](../core/)** - Core systems (AI, user management, learning)
- **[../gui/](../gui/)** - PyQt6 desktop UI
- **[../agents/](../agents/)** - AI agent modules

---

## Support

### Troubleshooting
- **API not starting**: Check `python --version` (require 3.11+), `pip install -r requirements.txt`
- **401 Unauthorized**: Token expired, call `/api/auth/login` again
- **403 Forbidden**: Governance denied, check audit logs with `GET /audit`
- **429 Rate Limited**: Wait before retrying, adjust rate limits in middleware

### Monitoring
- **FastAPI**: http://localhost:8001/health
- **Flask**: http://localhost:5000/api/status
- **Logs**: Check `logs/` directory and console output

### Documentation Issues
File issues at: https://github.com/IAmSoThirsty/Project-AI/issues

---

## Mission Completion

**AGENT-045: API Layers Documentation Specialist**

✅ **Objective**: Document API routes, endpoints, request/response handlers (12 modules)

**Deliverables**:
1. ✅ 01-API-OVERVIEW.md - Complete architecture overview
2. ✅ 02-FASTAPI-MAIN-ROUTES.md - Core governance endpoints
3. ✅ 03-SAVE-POINTS-API.md - Time-travel state management
4. ✅ 04-OPENCLAW-LEGION-API.md - Legion agent integration
5. ✅ 05-CONTRARIAN-FIREWALL-API.md - Advanced threat detection (placeholder)
6. ✅ 06-FLASK-WEB-BACKEND.md - Web adapter
7. ✅ 07-RUNTIME-ROUTER.md - Multi-path coordination
8. ✅ 08-GOVERNANCE-PIPELINE.md - 6-phase enforcement
9. ✅ 09-SECURITY-AUTH.md - JWT + Argon2 + MFA
10. ✅ 10-SECURITY-MIDDLEWARE.md - CORS + rate limiting
11. ✅ 11-INPUT-VALIDATION.md - Sanitization + schemas
12. ✅ 12-API-CLIENT-EXAMPLES.md - Python/JS/cURL examples

**Total Lines**: ~30,000+ words across 12 comprehensive documents

**Status**: ✅ MISSION COMPLETE
