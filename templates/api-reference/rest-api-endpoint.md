---
title: "API: <% tp.file.title %>"
created: <% tp.date.now("YYYY-MM-DD") %>
type: documentation
doc_type: api-reference
template_type: api-documentation
api_name: <% tp.system.prompt("API endpoint name (e.g., /users/{id})") %>
http_method: <% tp.system.suggester(["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"], ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]) %>
api_version: <% tp.system.prompt("API version (e.g., v1, v2)", "v1") %>
status: <% tp.system.suggester(["✅ Stable", "🚧 Beta", "⚠️ Deprecated", "📝 Draft"], ["stable", "beta", "deprecated", "draft"]) %>
tags: [template, api-reference, rest-api, endpoint, templater, <% tp.frontmatter.http_method %>]
last_verified: <% tp.date.now("YYYY-MM-DD") %>
template_status: current
related_systems: [templater, obsidian]
stakeholders: [developers, api-team, technical-writers]
complexity_level: intermediate
demonstrates: [api-documentation, rest-api, request-response, error-handling, authentication]
runnable: true
estimated_completion: 25
requires: [templater-plugin]
review_cycle: quarterly
area: [api, development]
audience: [developer, api-consumer]
what: "REST API endpoint documentation template with request/response schemas, authentication, examples, and error codes"
who: "API developers, technical writers, API consumers"
when: "When documenting new REST API endpoints or updating existing endpoint documentation"
where: "docs/api/ or API reference documentation"
why: "Ensures consistent, comprehensive API endpoint documentation with clear contracts, examples, and error handling"
---

# 🔌 API Endpoint: <% tp.file.title %>

## 📋 Endpoint Overview

**Endpoint:** `<% tp.frontmatter.api_name %>`  
**Method:** `<% tp.frontmatter.http_method %>`  
**Version:** <% tp.frontmatter.api_version %>  
**Status:** <% tp.frontmatter.status %>  
**Rate Limit:** <% tp.system.prompt("Rate limit (e.g., 100 requests/minute)", "100/min") %>  
**Last Updated:** <% tp.date.now("YYYY-MM-DD") %>

### Description
<% tp.system.prompt("What does this endpoint do? (1-2 sentences)") %>

### Use Cases
- <% tp.system.prompt("Use case 1") %>
- <% tp.system.prompt("Use case 2") %>
- <% tp.system.prompt("Use case 3") %>

---

## 🎯 Request Specification

### Endpoint URL

**Base URL:** `<% tp.system.prompt("Base URL (e.g., https://api.example.com)", "https://api.example.com") %>`  
**Full URL:** `<% tp.system.prompt("Base URL") %><% tp.frontmatter.api_name %>`

**URL Pattern:**
```
<% tp.frontmatter.http_method %> /<% tp.system.prompt("api_version") %>/<% tp.system.prompt("resource") %>/{<% tp.system.prompt("path_parameter", "id") %>}
```

---

### Path Parameters

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `<% tp.system.prompt("param1 (e.g., id, userId)") %>` | <% tp.system.suggester(["string", "integer", "uuid"], ["string", "integer", "uuid"]) %> | ✓ | <% tp.system.prompt("Parameter description") %> | <% tp.system.prompt("Constraints (e.g., >0, valid UUID)") %> |
| `param2` | type | ✗ | Description | Constraints |

**Example:**
```
GET /v1/users/12345
```

---

### Query Parameters

| Parameter | Type | Required | Default | Description | Example |
|-----------|------|----------|---------|-------------|---------|
| `<% tp.system.prompt("query_param1 (e.g., limit)") %>` | <% tp.system.suggester(["string", "integer", "boolean", "array"], ["string", "integer", "boolean", "array"]) %> | ✗ | <% tp.system.prompt("Default value", "10") %> | <% tp.system.prompt("Description") %> | `?limit=20` |
| `param2` | type | ✗ | default | Description | Example |

**Query String Example:**
```
?limit=20&offset=0&sort=created_at&order=desc
```

---

### Request Headers

| Header | Required | Description | Example |
|--------|----------|-------------|---------|
| `Authorization` | ✓ | Authentication token | `Bearer eyJhbGciOiJIUzI1NiIs...` |
| `Content-Type` | ✓ | Request content type | `application/json` |
| `Accept` | ✗ | Response content type | `application/json` |
| `<% tp.system.prompt("Custom header (e.g., X-Request-ID)") %>` | <% tp.system.suggester(["✓", "✗"], ["yes", "no"]) %> | <% tp.system.prompt("Header description") %> | <% tp.system.prompt("Example value") %> |

---

### Request Body (for POST/PUT/PATCH)

**Content-Type:** `application/json`

**Schema:**
```json
{
  "<% tp.system.prompt("field1") %>": "<% tp.system.prompt("type (e.g., string, number)") %>",
  "field2": "type",
  "field3": {
    "nested_field1": "type",
    "nested_field2": "type"
  },
  "field4": ["array", "of", "values"]
}
```

**Field Descriptions:**
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `<% tp.system.prompt("field1") %>` | <% tp.system.prompt("type") %> | ✓ | <% tp.system.prompt("Constraints (e.g., min 3 chars, max 255)") %> | <% tp.system.prompt("Description") %> |
| `field2` | type | ✗ | Constraints | Description |
| `field3.nested_field1` | type | ✓ | Constraints | Description |

**Validation Rules:**
- <% tp.system.prompt("Validation rule 1 (e.g., field1 must be unique)") %>
- Validation rule 2
- Validation rule 3

**Example Request Body:**
```json
{
  "<% tp.system.prompt("field1") %>": "<% tp.system.prompt("example value") %>",
  "field2": "example_value",
  "field3": {
    "nested_field1": "value",
    "nested_field2": "value"
  }
}
```

---

## 🔐 Authentication & Authorization

### Authentication

**Type:** <% tp.system.suggester(["Bearer Token (JWT)", "API Key", "OAuth 2.0", "Basic Auth", "None"], ["bearer", "apikey", "oauth2", "basic", "none"]) %>

**Header Format:**
```
Authorization: Bearer <YOUR_ACCESS_TOKEN>
```

**Token Requirements:**
- Token type: <% tp.system.prompt("Token type (e.g., JWT, OAuth2 access token)") %>
- Token expiration: <% tp.system.prompt("Expiration time (e.g., 3600 seconds)") %>
- Refresh available: <% tp.system.suggester(["Yes", "No"], ["yes", "no"]) %>

### Authorization

**Required Permissions:**
| Permission | Scope | Description |
|------------|-------|-------------|
| `<% tp.system.prompt("permission1 (e.g., users:read)") %>` | <% tp.system.prompt("Scope (e.g., user, admin)") %> | <% tp.system.prompt("What this allows") %> |
| `permission2` | Scope | Description |

**Authorization Example:**
```json
// JWT payload must contain:
{
  "sub": "user_id",
  "permissions": ["<% tp.system.prompt("permission1") %>", "permission2"],
  "exp": 1737625800
}
```

---

## ✅ Response Specification

### Success Response

**Status Code:** `<% tp.system.suggester(["200 OK", "201 Created", "202 Accepted", "204 No Content"], ["200", "201", "202", "204"]) %>`

**Response Headers:**
| Header | Description | Example |
|--------|-------------|---------|
| `Content-Type` | Response content type | `application/json` |
| `X-Request-ID` | Request tracking ID | `req-abc-123` |
| `X-RateLimit-Limit` | Rate limit maximum | `100` |
| `X-RateLimit-Remaining` | Remaining requests | `95` |
| `X-RateLimit-Reset` | Reset timestamp | `1737625800` |

**Response Schema:**
```json
{
  "success": true,
  "data": {
    "<% tp.system.prompt("response_field1") %>": "<% tp.system.prompt("type/value") %>",
    "response_field2": "value",
    "response_field3": {
      "nested_field": "value"
    }
  },
  "meta": {
    "request_id": "req-abc-123",
    "timestamp": "2026-01-23T10:30:00Z",
    "version": "<% tp.frontmatter.api_version %>"
  }
}
```

**Field Descriptions:**
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `success` | boolean | No | Request success indicator |
| `data.<% tp.system.prompt("field1") %>` | <% tp.system.prompt("type") %> | <% tp.system.suggester(["Yes", "No"], ["yes", "no"]) %> | <% tp.system.prompt("Description") %> |
| `data.field2` | type | No | Description |
| `meta.request_id` | string | No | Unique request identifier |

**Example Success Response:**
```json
{
  "success": true,
  "data": {
    "<% tp.system.prompt("field1") %>": "<% tp.system.prompt("example value") %>",
    "field2": "example_value",
    "created_at": "2026-01-23T10:30:00Z",
    "updated_at": "2026-01-23T10:30:00Z"
  },
  "meta": {
    "request_id": "req-abc-123",
    "timestamp": "2026-01-23T10:30:00Z",
    "version": "v1"
  }
}
```

---

### Error Responses

**Error Response Schema:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": [
      {
        "field": "field_name",
        "message": "Field-specific error"
      }
    ]
  },
  "meta": {
    "request_id": "req-abc-123",
    "timestamp": "2026-01-23T10:30:00Z",
    "version": "v1"
  }
}
```

**Error Codes:**

| Status Code | Error Code | Message | Cause | Resolution |
|-------------|------------|---------|-------|------------|
| 400 | `INVALID_REQUEST` | Invalid request format | Malformed JSON or missing required fields | Check request format and required fields |
| 401 | `UNAUTHORIZED` | Authentication required | Missing or invalid auth token | Provide valid authentication token |
| 403 | `FORBIDDEN` | Insufficient permissions | User lacks required permissions | Request appropriate permissions |
| 404 | `NOT_FOUND` | Resource not found | Resource with given ID doesn't exist | Verify resource ID |
| 409 | `CONFLICT` | Resource conflict | Duplicate resource or state conflict | Check for existing resource |
| 422 | `VALIDATION_ERROR` | Validation failed | Request validation failed | Fix validation errors in request |
| 429 | `RATE_LIMIT_EXCEEDED` | Rate limit exceeded | Too many requests | Wait before retrying |
| 500 | `INTERNAL_ERROR` | Internal server error | Server-side error | Contact support with request_id |
| 503 | `SERVICE_UNAVAILABLE` | Service unavailable | Service temporarily down | Retry after delay |

**Example Error Response (400):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "<% tp.system.prompt("field_name") %>",
        "message": "<% tp.system.prompt("Validation error message") %>"
      }
    ]
  },
  "meta": {
    "request_id": "req-abc-123",
    "timestamp": "2026-01-23T10:30:00Z",
    "version": "v1"
  }
}
```

**Example Error Response (401):**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired authentication token"
  },
  "meta": {
    "request_id": "req-def-456",
    "timestamp": "2026-01-23T10:30:00Z"
  }
}
```

---

## 📝 Code Examples

### cURL

```bash
# Basic request
curl -X <% tp.frontmatter.http_method %> \
  '<% tp.system.prompt("Full endpoint URL") %>' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
<% if tp.frontmatter.http_method in ["POST", "PUT", "PATCH"] %>  -d '{
    "<% tp.system.prompt("field1") %>": "<% tp.system.prompt("value1") %>",
    "field2": "value2"
  }'
<% endif %>
# Expected response: 200 OK
```

### Python (requests)

```python
import requests

url = "<% tp.system.prompt("Full endpoint URL") %>"
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN",
    "Content-Type": "application/json"
}
<% if tp.frontmatter.http_method in ["POST", "PUT", "PATCH"] %>
payload = {
    "<% tp.system.prompt("field1") %>": "<% tp.system.prompt("value1") %>",
    "field2": "value2"
}

response = requests.<% tp.frontmatter.http_method.lower() %>(url, json=payload, headers=headers)
<% else %>
response = requests.<% tp.frontmatter.http_method.lower() %>(url, headers=headers)
<% endif %>

if response.status_code == 200:
    data = response.json()
    print(f"Success: {data}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### JavaScript (fetch)

```javascript
const url = '<% tp.system.prompt("Full endpoint URL") %>';
const options = {
  method: '<% tp.frontmatter.http_method %>',
  headers: {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
    'Content-Type': 'application/json'
  }<% if tp.frontmatter.http_method in ["POST", "PUT", "PATCH"] %>,
  body: JSON.stringify({
    '<% tp.system.prompt("field1") %>': '<% tp.system.prompt("value1") %>',
    'field2': 'value2'
  })
<% endif %>
};

fetch(url, options)
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('Success:', data);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### Node.js (axios)

```javascript
const axios = require('axios');

const config = {
  method: '<% tp.frontmatter.http_method.lower() %>',
  url: '<% tp.system.prompt("Full endpoint URL") %>',
  headers: {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
    'Content-Type': 'application/json'
  }<% if tp.frontmatter.http_method in ["POST", "PUT", "PATCH"] %>,
  data: {
    '<% tp.system.prompt("field1") %>': '<% tp.system.prompt("value1") %>',
    'field2': 'value2'
  }
<% endif %>
};

axios(config)
  .then(response => {
    console.log('Success:', response.data);
  })
  .catch(error => {
    console.error('Error:', error.response?.data || error.message);
  });
```

---

## 🧪 Testing

### Test Cases

#### Test Case 1: Successful Request
```python
def test_successful_request():
    """Test successful API request."""
    response = client.<% tp.frontmatter.http_method.lower() %>(
        "<% tp.frontmatter.api_name %>",
        headers={"Authorization": f"Bearer {valid_token}"},
        <% if tp.frontmatter.http_method in ["POST", "PUT", "PATCH"] %>json=valid_payload<% endif %>
    )
    
    assert response.status_code == <% tp.system.prompt("Expected status code", "200") %>
    assert response.json()["success"] is True
    assert "<% tp.system.prompt("expected_field") %>" in response.json()["data"]
```

#### Test Case 2: Missing Authentication
```python
def test_missing_authentication():
    """Test request without authentication."""
    response = client.<% tp.frontmatter.http_method.lower() %>(
        "<% tp.frontmatter.api_name %>"
    )
    
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
```

#### Test Case 3: Invalid Input
```python
def test_invalid_input():
    """Test request with invalid input."""
    invalid_payload = {
        "<% tp.system.prompt("field1") %>": ""  # Invalid: empty string
    }
    
    response = client.<% tp.frontmatter.http_method.lower() %>(
        "<% tp.frontmatter.api_name %>",
        headers={"Authorization": f"Bearer {valid_token}"},
        json=invalid_payload
    )
    
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
```

#### Test Case 4: Rate Limiting
```python
def test_rate_limiting():
    """Test rate limit enforcement."""
    # Make requests until rate limit
    for i in range(150):  # Exceeds 100/min limit
        response = client.<% tp.frontmatter.http_method.lower() %>(
            "<% tp.frontmatter.api_name %>",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
    
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "X-RateLimit-Reset" in response.headers
```

---

## 📊 Performance & Limits

### Performance Characteristics

**Expected Performance:**
| Metric | Target | Notes |
|--------|--------|-------|
| Response Time (p50) | <% tp.system.prompt("P50 target (e.g., <100ms)", "100ms") %> | 50th percentile |
| Response Time (p95) | <% tp.system.prompt("P95 target (e.g., <500ms)", "500ms") %> | 95th percentile |
| Response Time (p99) | <% tp.system.prompt("P99 target (e.g., <1000ms)", "1000ms") %> | 99th percentile |
| Throughput | <% tp.system.prompt("Throughput (e.g., 1000 req/sec)", "1000 req/sec") %> | Maximum sustained |

### Rate Limits

**Rate Limit Configuration:**
- **Anonymous:** <% tp.system.prompt("Anonymous limit", "10 requests/minute") %>
- **Authenticated:** <% tp.system.prompt("Authenticated limit", "100 requests/minute") %>
- **Premium:** <% tp.system.prompt("Premium limit", "1000 requests/minute") %>

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1737625800
```

**Rate Limit Exceeded Handling:**
```python
# Implement exponential backoff
import time

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        response = func()
        
        if response.status_code != 429:
            return response
        
        # Wait before retrying
        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
        wait_time = max(reset_time - time.time(), 0)
        
        print(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}")
        time.sleep(wait_time)
    
    raise Exception("Max retries exceeded")
```

### Payload Limits

**Size Constraints:**
- Maximum request body size: <% tp.system.prompt("Max request size (e.g., 1MB)", "1MB") %>
- Maximum response body size: <% tp.system.prompt("Max response size (e.g., 10MB)", "10MB") %>
- Maximum array length: <% tp.system.prompt("Max array items (e.g., 1000)", "1000") %>
- Maximum string length: <% tp.system.prompt("Max string length (e.g., 10000 chars)", "10000") %>

---

## 🔄 Versioning & Deprecation

### API Version

**Current Version:** <% tp.frontmatter.api_version %>  
**Version Strategy:** <% tp.system.suggester(["URL Path (/v1/)", "Header (Accept-Version)", "Query Parameter (?version=1)"], ["path", "header", "query"]) %>

**Supported Versions:**
| Version | Status | Support Until | Notes |
|---------|--------|---------------|-------|
| v1 | ✅ Active | - | Current version |
| v2 | 🚧 Beta | - | Next version |
| v0 | ⚠️ Deprecated | <% tp.system.prompt("Deprecation date", "N/A") %> | Legacy |

### Deprecation Notice

**Status:** <% tp.system.suggester(["✅ Active", "⚠️ Deprecated", "🔒 Sunset"], ["active", "deprecated", "sunset"]) %>

**If deprecated:**
- Deprecation date: <% tp.system.prompt("When deprecated?", "N/A") %>
- Sunset date: <% tp.system.prompt("When will it be removed?", "N/A") %>
- Replacement endpoint: <% tp.system.prompt("Replacement API", "N/A") %>
- Migration guide: [[<% tp.system.prompt("Migration guide link", "N/A") %>]]

---

## 📚 Related Documentation

### Internal Links
- [[API Overview]] - Complete API documentation
- [[Authentication Guide]] - Authentication details
- [[Rate Limiting Guide]] - Rate limit policies
- [[Error Handling Guide]] - Error handling best practices
- Related Endpoints: [[<% tp.system.prompt("Related endpoint 1") %>]], [[Endpoint 2]]

### External Resources
- **API Portal:** <% tp.system.prompt("API portal URL", "N/A") %>
- **Interactive Docs:** <% tp.system.prompt("Swagger/OpenAPI URL", "N/A") %>
- **Postman Collection:** <% tp.system.prompt("Postman collection URL", "N/A") %>
- **SDK Documentation:** <% tp.system.prompt("SDK docs URL", "N/A") %>

---

## 🔄 Change Log

### <% tp.date.now("YYYY-MM-DD") %> - v<% tp.system.prompt("Version", "1.0.0") %>
- Initial endpoint documentation
- <% tp.system.prompt("Change 1") %>
- Change 2

### [Date] - v[Version]
- Change description
- Breaking changes (if any)
- Migration notes

---

## 📊 Metrics

**Endpoint Usage:**
- **Requests (30d):** <% tp.system.prompt("Request count", "N/A") %>
- **Avg Response Time:** <% tp.system.prompt("Avg time", "N/A") %>
- **Error Rate:** <% tp.system.prompt("Error rate %", "N/A") %>
- **Success Rate:** <% tp.system.prompt("Success rate %", "N/A") %>

---

**Document Version:** 1.0  
**Template Version:** 1.0  
**Last Updated:** <% tp.date.now("YYYY-MM-DD HH:mm") %>  
**Next Review:** <% tp.date.now("YYYY-MM-DD", 90) %>

---

*This document was created using the Project-AI REST API Endpoint Template.*  
*Template location: `templates/api-reference/rest-api-endpoint.md`*
