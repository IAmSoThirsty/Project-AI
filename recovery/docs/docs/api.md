# API Guide

## Overview

The Sovereign Governance Substrate exposes a comprehensive REST API for interacting with governance, cognition, security, and operational systems.

**Base URL**: `https://api.sovereign.local/api/v1`

## Authentication

### API Key Authentication

```bash
curl -X GET https://api.sovereign.local/api/v1/policies \
  -H "X-API-Key: your_api_key_here"
```

### JWT Token Authentication

```bash

# 1. Login to get token

curl -X POST https://api.sovereign.local/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Response:

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "token_type": "Bearer"
}

# 2. Use token in subsequent requests

curl -X GET https://api.sovereign.local/api/v1/policies \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Core API Endpoints

### Governance API

#### List Policies

```bash
GET /api/v1/governance/policies
```

**Response:**
```json
{
  "policies": [
    {
      "id": "policy_123",
      "name": "Data Privacy Policy",
      "version": "1.0",
      "status": "active",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

#### Create Policy

```bash
POST /api/v1/governance/policies
Content-Type: application/json

{
  "name": "New Policy",
  "description": "Policy description",
  "rules": {
    "data_retention_days": 90,
    "require_approval": true
  },
  "jurisdictions": ["US", "EU"]
}
```

#### Make Governance Decision

```bash
POST /api/v1/governance/decide
Content-Type: application/json

{
  "policy_id": "policy_123",
  "context": {
    "user_id": "user_456",
    "action": "data_export",
    "jurisdiction": "US"
  }
}
```

**Response:**
```json
{
  "decision_id": "dec_789",
  "result": "approved",
  "reasoning": "User has export permission in US jurisdiction",
  "metadata": {
    "confidence": 0.95,
    "policy_version": "1.0"
  }
}
```

### Cognition API

#### Run Inference

```bash
POST /api/v1/cognition/infer
Content-Type: application/json

{
  "model": "policy_classifier",
  "input": {
    "text": "User requests data export"
  },
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 100
  }
}
```

**Response:**
```json
{
  "inference_id": "inf_123",
  "result": {
    "classification": "data_access",
    "confidence": 0.92,
    "recommendations": ["verify_jurisdiction", "check_consent"]
  },
  "execution_time_ms": 45
}
```

#### Reasoning Query

```bash
POST /api/v1/cognition/reason
Content-Type: application/json

{
  "query": "Can user access PII data in EU jurisdiction?",
  "context": {
    "user_id": "user_456",
    "jurisdiction": "EU",
    "data_type": "PII"
  }
}
```

### Security API

#### Create Security Context

```bash
POST /api/v1/security/context
Content-Type: application/json

{
  "user_id": "user_123",
  "operation": "data_export",
  "resource": "customer_data",
  "metadata": {
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
  }
}
```

**Response:**
```json
{
  "context_id": "ctx_789",
  "security_level": "high",
  "constraints": {
    "rate_limit": "100/hour",
    "encryption_required": true,
    "audit_required": true
  },
  "expires_at": "2026-01-01T01:00:00Z"
}
```

#### Validate Operation

```bash
POST /api/v1/security/validate
Content-Type: application/json

{
  "context_id": "ctx_789",
  "operation": {
    "action": "export",
    "resource": "customer_data",
    "parameters": {"format": "csv"}
  }
}
```

**Response:**
```json
{
  "validation_id": "val_456",
  "result": "approved",
  "security_checks": {
    "authorization": "passed",
    "rate_limit": "passed",
    "jurisdiction": "passed"
  },
  "audit_log_id": "audit_123"
}
```

#### Query Audit Log

```bash
GET /api/v1/security/audit?start_time=2026-01-01T00:00:00Z&end_time=2026-01-02T00:00:00Z&user_id=user_123
```

### PSIA (Plane-Specific Intelligence Architecture) API

#### List Planes

```bash
GET /api/v1/psia/planes
```

**Response:**
```json
{
  "planes": [
    {
      "id": "plane_governance",
      "name": "Governance Plane",
      "status": "active",
      "capabilities": ["policy_enforcement", "decision_making"]
    },
    {
      "id": "plane_cognition",
      "name": "Cognition Plane",
      "status": "active",
      "capabilities": ["inference", "reasoning", "learning"]
    }
  ]
}
```

#### Query Capabilities

```bash
GET /api/v1/psia/capabilities?plane_id=plane_governance
```

#### Enforce Constraint

```bash
POST /api/v1/psia/enforce
Content-Type: application/json

{
  "plane_id": "plane_governance",
  "constraint": {
    "type": "rate_limit",
    "parameters": {"max_requests": 100, "window_seconds": 60}
  },
  "target": "user_123"
}
```

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Missing required field: user_id",
    "details": {
      "field": "user_id",
      "constraint": "required"
    },
    "request_id": "req_abc123",
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

### HTTP Status Codes

- `200 OK` - Request succeeded
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

## Rate Limiting

All API endpoints are rate-limited per user/API key:

- **Standard Tier**: 100 requests/minute
- **Professional Tier**: 1,000 requests/minute
- **Enterprise Tier**: 10,000 requests/minute

**Rate Limit Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640000000
```

## Pagination

List endpoints support pagination:

```bash
GET /api/v1/policies?page=2&per_page=50
```

**Response includes pagination metadata:**
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 50,
    "total_pages": 10,
    "total_items": 500,
    "has_next": true,
    "has_prev": true
  }
}
```

## Filtering and Sorting

```bash

# Filter by status

GET /api/v1/policies?status=active

# Sort by created_at

GET /api/v1/policies?sort=created_at&order=desc

# Multiple filters

GET /api/v1/policies?status=active&jurisdiction=US&sort=name
```

## Webhooks

Subscribe to events for real-time notifications:

```bash
POST /api/v1/webhooks
Content-Type: application/json

{
  "url": "https://your-app.com/webhook",
  "events": ["policy.created", "decision.made", "security.violation"],
  "secret": "webhook_secret_key"
}
```

**Webhook Payload:**
```json
{
  "event": "policy.created",
  "timestamp": "2026-01-01T00:00:00Z",
  "data": {
    "policy_id": "policy_123",
    "name": "New Policy"
  },
  "signature": "sha256=..."
}
```

## SDK Examples

### Python SDK

```python
from sovereign_sdk import SovereignClient

# Initialize client

client = SovereignClient(
    api_key="your_api_key",
    base_url="https://api.sovereign.local"
)

# Make governance decision

decision = client.governance.decide(
    policy_id="policy_123",
    context={"user_id": "user_456", "action": "data_export"}
)

print(f"Decision: {decision.result}")
print(f"Reasoning: {decision.reasoning}")
```

### TypeScript SDK

```typescript
import { SovereignClient } from '@sovereign/sdk';

const client = new SovereignClient({
  apiKey: 'your_api_key',
  baseURL: 'https://api.sovereign.local'
});

// Run cognition inference
const inference = await client.cognition.infer({
  model: 'policy_classifier',
  input: { text: 'User requests data export' }
});

console.log(inference.result);
```

## See Also

- [OpenAPI Specification](openapi.yaml)
- [Authentication Guide](authentication.md)
- [Rate Limiting Details](rate-limiting.md)
- [Webhook Integration](webhooks.md)

---
*Generated by Fleet B Phase 2 Enhanced Documentation Generator*
