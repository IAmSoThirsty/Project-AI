---
title: Flask Web Backend API
category: api
layer: api-layer
audience: [integrator, maintainer]
status: production
classification: technical-reference
confidence: verified
requires: [01-API-OVERVIEW.md, 07-RUNTIME-ROUTER.md]
time_estimate: 15min
last_updated: 2025-06-09
version: 2.0.0
---

# Flask Web Backend API

## Purpose

Lightweight web application adapter routing React UI requests through governance pipeline.

**File**: `web/backend/app.py` (176 lines)  
**Port**: 5000  
**Stack**: Flask + CORS + Rate Limiting

---

## Endpoints

### `/api/status` - Health Check
```bash
curl http://localhost:5000/api/status
# Response: {"status": "ok", "component": "web-backend"}
```

### `/api/auth/login` - Authentication
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secure123"}'

# Response:
{
  "status": "ok",
  "success": true,
  "token": "eyJhbGc...",
  "user": {"username": "admin", "role": "admin"}
}
```

**Routes through**: `route_request(source="web", payload={action: "user.login"}) → Governance → UserManager → JWT token`

### `/api/ai/chat` - AI Conversation
```bash
TOKEN="eyJhbGc..."
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"prompt": "Hello AI", "model": "gpt-4", "provider": "openai"}'

# Response:
{
  "result": "Hello! How can I assist you today?",
  "metadata": {"model": "gpt-4", "tokens": 15}
}
```

**Routes through**: Governance → IntelligenceEngine → OpenAI

### `/api/ai/image` - Image Generation
```bash
curl -X POST http://localhost:5000/api/ai/image \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"prompt": "cyberpunk city", "size": "1024x1024", "provider": "huggingface"}'
```

### `/api/persona/update` - AI Personality
```bash
curl -X POST http://localhost:5000/api/persona/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"trait": "curiosity", "value": 8}'
```

---

## Security Configuration

```python
# CORS (web/backend/app.py)
configure_cors(app)  # Allows localhost:3000, localhost:5173

# Rate Limiting
configure_rate_limiting(app)  # 100/min default
```

---

## Related Documentation
- **[01-API-OVERVIEW.md](./01-API-OVERVIEW.md)** - Architecture
- **[07-RUNTIME-ROUTER.md](./07-RUNTIME-ROUTER.md)** - Request routing
- **[09-SECURITY-AUTH.md](./09-SECURITY-AUTH.md)** - JWT implementation
