# API Documentation

## Overview

API documentation index for the Sovereign Governance Substrate platform. This directory contains OpenAPI specifications, API guides, and integration documentation.

## Documentation Structure

```
api/
├── openapi.yaml          # OpenAPI 3.0 specification
├── authentication.md     # Auth flows and tokens
├── rate-limiting.md      # Rate limit policies
├── webhooks.md          # Webhook integrations
└── examples/            # Request/response examples
```

## API Endpoints

### Core Services

#### Authentication API

- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/verify` - Token verification

#### Governance API

- `GET /api/v1/governance/policies` - List policies
- `POST /api/v1/governance/policies` - Create policy
- `GET /api/v1/governance/decisions` - List decisions
- `POST /api/v1/governance/vote` - Submit vote

#### Cognition API

- `POST /api/v1/cognition/infer` - ML inference
- `POST /api/v1/cognition/reason` - Reasoning query
- `POST /api/v1/cognition/validate` - Policy validation

#### PSIA API

- `GET /api/v1/psia/planes` - List planes
- `GET /api/v1/psia/capabilities` - Query capabilities
- `POST /api/v1/psia/enforce` - Enforce constraint

#### Security API

- `POST /api/v1/security/context` - Create security context
- `POST /api/v1/security/validate` - Validate operation
- `GET /api/v1/security/audit` - Query audit log

## Quick Start

### Authentication

```bash

# Login

curl -X POST https://api.sovereign.local/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Response

{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "expires_in": 3600
}
```

### Making Authenticated Requests

```bash
curl -X GET https://api.sovereign.local/api/v1/governance/policies \
  -H "Authorization: Bearer eyJhbGc..."
```

## OpenAPI Specification

The complete API specification is available in `openapi.yaml`. You can:

### View Interactive Docs

```bash

# Start documentation server

cd docs/api
python -m http.server 8080

# Visit http://localhost:8080

```

### Generate Client SDKs

```bash

# Generate Python client

openapi-generator-cli generate \
  -i openapi.yaml \
  -g python \
  -o clients/python

# Generate TypeScript client

openapi-generator-cli generate \
  -i openapi.yaml \
  -g typescript-axios \
  -o clients/typescript
```

## Rate Limiting

All API endpoints are rate-limited:

- **Standard**: 100 requests/minute
- **Authenticated**: 1000 requests/minute
- **Premium**: 10000 requests/minute

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640000000
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
    "request_id": "req_abc123"
  }
}
```

### Error Codes

- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error
- `503` - Service Unavailable

## Webhooks

Subscribe to events:
```bash
curl -X POST https://api.sovereign.local/api/v1/webhooks \
  -H "Authorization: Bearer eyJhbGc..." \
  -d '{
    "url": "https://your-app.com/webhook",
    "events": ["policy.created", "decision.made"],
    "secret": "webhook_secret_key"
  }'
```

## SDK Examples

### Python

```python
from sovereign_sdk import SovereignClient

client = SovereignClient(
    api_key="your_api_key",
    base_url="https://api.sovereign.local"
)

# Query policies

policies = client.governance.list_policies()

# Create decision

decision = client.governance.create_decision(
    policy_id="policy_123",
    context={"user_id": "user_456"}
)
```

### TypeScript

```typescript
import { SovereignClient } from '@sovereign/sdk';

const client = new SovereignClient({
  apiKey: 'your_api_key',
  baseURL: 'https://api.sovereign.local'
});

// Query policies
const policies = await client.governance.listPolicies();

// Create decision
const decision = await client.governance.createDecision({
  policyId: 'policy_123',
  context: { userId: 'user_456' }
});
```

## Testing

### Test Environment

```
Base URL: https://api-test.sovereign.local
API Key: test_key_abc123
```

### Postman Collection

Import the Postman collection from `examples/postman/sovereign-api.json`

## Versioning

API versions are specified in the URL path:

- `v1` - Current stable version
- `v2` - Beta version (breaking changes)

## Support

- API Documentation: https://docs.sovereign.local
- GitHub Issues: https://github.com/sovereign/issues
- Email: api-support@sovereign.local

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md)
