# API Documentation

## Autonomous Compliance-as-Code Engine API Reference

**Base URL**: `/api/v1`

## Authentication

### API Key

Include in header:
```
X-API-Key: your-api-key
```
### JWT Token

Include in header:
```
Authorization: Bearer your-jwt-token
```
## Endpoints

### Health Checks

#### GET /health
Basic health check

#### GET /health/ready
Readiness check for load balancer

#### GET /health/live
Liveness check for Kubernetes

### Items API

#### GET /api/v1/items
List all items with pagination

**Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20, max: 100)

**Response:** 200 OK
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

#### POST /api/v1/items
Create a new item

**Request Body:**
```json
{
  "name": "Item Name",
  "description": "Optional description"
}
```

**Response:** 201 Created

#### GET /api/v1/items/{item_id}
Get a specific item

**Response:** 200 OK

#### PUT /api/v1/items/{item_id}
Update an item

**Response:** 200 OK

#### DELETE /api/v1/items/{item_id}
Delete an item

**Response:** 204 No Content

## Error Responses

All errors follow this format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

### Error Codes

- `VALIDATION_ERROR` (400): Invalid request data
- `AUTHENTICATION_ERROR` (401): Authentication required or failed
- `AUTHORIZATION_ERROR` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `CONFLICT` (409): Resource conflict (e.g., duplicate)
- `RATE_LIMIT_EXCEEDED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error
- `DATABASE_ERROR` (500): Database operation failed
