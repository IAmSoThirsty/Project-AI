# Project AI - API Backend

## Quick Start

### Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### Start Development Server

```bash

# From project root

python start_api.py

# Or directly with uvicorn

uvicorn api.main:app --reload --port 8001
```

### Start Production Server

```bash
python start_api.py --prod
```

## API Endpoints

### Submit Intent

```http
POST /intent
Content-Type: application/json

{
  "actor": "human",
  "action": "read",
  "target": "data/analytics",
  "context": {},
  "origin": "web_frontend"
}
```

**Response (Allow):**
```json
{
  "message": "Intent accepted under governance",
  "governance": {
    "intent_hash": "abc123...",
    "tarl_version": "1.0",
    "votes": [
      {"pillar": "Galahad", "verdict": "allow", "reason": "Actor aligns with rule"},
      {"pillar": "Cerberus", "verdict": "allow", "reason": "No adversarial patterns"}
    ],
    "final_verdict": "allow",
    "timestamp": 1706380000.0
  }
}
```

**Response (Deny):**
```json
{
  "detail": {
    "message": "Governance denied this request",
    "governance": {
      "intent_hash": "def456...",
      "tarl_version": "1.0",
      "votes": [
        {"pillar": "Galahad", "verdict": "deny", "reason": "Actor not ethically authorized"}
      ],
      "final_verdict": "deny",
      "timestamp": 1706380000.0
    }
  }
}
```

### View TARL Rules

```http
GET /tarl
```

### Health Check

```http
GET /health
```

## Architecture

### Triumvirate Evaluation

1. **Galahad (Ethics)**: Validates actor authorization
2. **Cerberus (Security)**: Detects threats and high-risk actions
3. **CodexDeus (Arbitration)**: Final verdict based on votes

### TARL Rules (v1.0)

| Action | Allowed Actors | Risk | Default |
|--------|---------------|------|---------|
| read | human, agent | low | allow |
| write | human | medium | degrade |
| execute | system | high | deny |
| mutate | (none) | critical | deny |

### Decision Flow

```
Intent → TARL Rule Match → Galahad Vote → Cerberus Vote → CodexDeus Arbitration → Verdict
```

## Actor Types

- **human**: Human user
- **agent**: AI agent
- **system**: System process

## Action Types

- **read**: Read operation (low risk)
- **write**: Write operation (medium risk)
- **execute**: Execute operation (high risk)
- **mutate**: State mutation (critical risk)

## Verdicts

- **allow**: Action permitted
- **deny**: Action forbidden (403 response)
- **degrade**: Action allowed with degraded capabilities

## Examples

### Allowed Read (Human)

```bash
curl -X POST http://localhost:8001/intent \
  -H "Content-Type: application/json" \
  -d '{
    "actor": "human",
    "action": "read",
    "target": "/analytics/dashboard",
    "context": {"user_id": "123"},
    "origin": "web_ui"
  }'
```

### Denied Write (Agent)

```bash
curl -X POST http://localhost:8001/intent \
  -H "Content-Type: application/json" \
  -d '{
    "actor": "agent",
    "action": "write",
    "target": "/config/settings",
    "context": {},
    "origin": "automation"
  }'
```

### Critical Action (Blocked)

```bash
curl -X POST http://localhost:8001/intent \
  -H "Content-Type: application/json" \
  -d '{
    "actor": "agent",
    "action": "mutate",
    "target": "/governance/rules",
    "context": {},
    "origin": "api"
  }'
```

## Interactive API Documentation

Visit http://localhost:8001/docs for Swagger UI documentation.

## Production Deployment

### Using Gunicorn

```bash
gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001
```

### Using Docker

```bash
docker build -t project-ai-api -f api/Dockerfile .
docker run -p 8001:8001 project-ai-api
```

## Security Notes

- **Fail-Closed**: No TARL rule = automatic deny
- **Immutable Governance**: TARL rules are read-only at runtime
- **Audit Trail**: All decisions include cryptographic intent hash
- **CORS**: Configure `allow_origins` for production

## Testing

```bash

# Install test dependencies

pip install pytest httpx

# Run API tests

pytest tests/test_api.py -v
```

## Integration with Web Frontend

The API is designed to work with `web/index.html`. Configure the frontend to point to:
```javascript
const API_URL = 'http://localhost:8001';
```

## Environment Variables

```bash

# Optional configuration

export API_HOST=0.0.0.0
export API_PORT=8001
export API_WORKERS=4
export TARL_VERSION=1.0
```

## Governance Philosophy

> Every request must pass through governance. If governance is unclear, degraded, or unreachable, the system denies execution. No exceptions.

This backend implements that philosophy at the HTTP layer.
