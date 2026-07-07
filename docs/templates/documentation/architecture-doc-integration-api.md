---
title: "<%tp.file.title%>"
id: "<%tp.file.title.toLowerCase().replace(/\s+/g, '-')%>"
type: "specification"
version: "1.0.0"
created_date: "<%tp.date.now("YYYY-MM-DD")%>"
updated_date: "<%tp.date.now("YYYY-MM-DD")%>"
status: "draft"
author: 
  name: "<%tp.user.name || 'Integration Team'%>"
category: "architecture"
tags:
  - "architecture"
  - "integration"
  - "api"
  - "external-service"
classification: "internal"
audience: ["developer", "architect"]
service_name: ""
api_version: ""
authentication_method: ""
endpoints: []
summary: "Integration specification for <%`${await tp.system.prompt('Service name (e.g., OpenAI GPT-4):') || '[Service]'}`%> documenting API contracts, authentication, and error handling."
---

# <%tp.file.title%>

> **Service:** <%`${await tp.system.prompt('Service name:') || '[Service]'}`%>  
> **API Version:** <%`${await tp.system.prompt('API version:') || 'v1'}`%>  
> **Auth Method:** <%`${await tp.system.prompt('Auth method (API Key/OAuth/JWT):') || 'API Key'}`%>

## Integration Overview

**Service Provider:** [Provider name]
**Purpose:** [Why we integrate with this service]
**Integration Type:** [REST API/GraphQL/WebSocket/gRPC]
**Base URL:** `https://api.example.com/v1`

## Authentication

**Method:** <%`${await tp.system.prompt('Auth method:') || 'API Key'}`%>

**Configuration:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SERVICE_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
```

**Environment Setup:**
```bash
# Required in .env
SERVICE_API_KEY=your_api_key_here
```

## API Endpoints

### Endpoint 1: [Name]

**Method:** `POST`  
**Path:** `/endpoint/path`  
**Purpose:** [What this endpoint does]

**Request:**
```json
{
  "parameter1": "value",
  "parameter2": 123
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "result": "value"
  }
}
```

**Response (Error):**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

**Python Example:**
```python
import requests

response = requests.post(
    "https://api.example.com/v1/endpoint/path",
    headers=headers,
    json={"parameter1": "value", "parameter2": 123}
)

if response.status_code == 200:
    data = response.json()
    print(f"Result: {data['data']['result']}")
else:
    error = response.json()["error"]
    print(f"Error: {error['message']}")
```

## Error Handling

**Error Codes:**

| Code | HTTP Status | Description | Action |
|------|-------------|-------------|--------|
| `INVALID_API_KEY` | 401 | Invalid authentication | Check API key |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Implement backoff |
| `INTERNAL_ERROR` | 500 | Service error | Retry with backoff |

**Retry Strategy:**
```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(3)
)
def call_api(endpoint: str, payload: dict):
    response = requests.post(endpoint, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
```

## Rate Limits

**Limits:**
- Requests per minute: [Number]
- Requests per day: [Number]
- Concurrent requests: [Number]

**Implementation:**
```python
from time import sleep

class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.last_call = 0
    
    def wait_if_needed(self):
        # Implementation
        pass
```

## Security Considerations

- Never log API keys
- Use environment variables for credentials
- Implement request signing (if required)
- Validate SSL certificates

## Testing

**Mock Server:**
```python
from unittest.mock import Mock, patch

@patch('requests.post')
def test_api_call(mock_post):
    mock_post.return_value.json.return_value = {"status": "success"}
    result = call_api("/endpoint", {"test": "data"})
    assert result["status"] == "success"
```

## Related Documentation

- [[architecture-doc-integration-patterns]]: General integration patterns
- [[guide-api-usage]]: API usage guide

---

**Document Status:** Draft  
**Next Review:** [Date]

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

