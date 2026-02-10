# REST API Specification

## Overview

Project-AI exposes a RESTful API built with Flask, providing programmatic access to all core features including AI chat, image generation, learning paths, data analysis, and user management.

## Base URL

```
Development: http://localhost:5000
Production: https://api.project-ai.com
```

## Authentication

All API endpoints (except `/api/auth/*`) require authentication via JWT tokens.

### Authentication Header

```http
Authorization: Bearer <jwt_token>
```

## API Endpoints

### Authentication Endpoints

#### POST /api/auth/register

Register a new user account.

**Request**:
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!"
}
```

**Response** (201 Created):
```json
{
  "message": "User registered successfully",
  "user_id": "usr_1234567890",
  "username": "alice",
  "email": "alice@example.com"
}
```

**Errors**:
- `400`: Validation error (passwords don't match, weak password, etc.)
- `409`: Username or email already exists

#### POST /api/auth/login

Authenticate user and obtain JWT tokens.

**Request**:
```json
{
  "username": "alice",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "user_id": "usr_1234567890",
    "username": "alice",
    "email": "alice@example.com"
  }
}
```

**Errors**:
- `401`: Invalid credentials
- `429`: Too many failed login attempts

#### POST /api/auth/refresh

Refresh access token using refresh token.

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Errors**:
- `401`: Invalid or expired refresh token

#### POST /api/auth/logout

Revoke access and refresh tokens.

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

### User Endpoints

#### GET /api/users/me

Get current user profile.

**Response** (200 OK):
```json
{
  "user_id": "usr_1234567890",
  "username": "alice",
  "email": "alice@example.com",
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-02-08T14:22:00Z",
  "preferences": {
    "theme": "dark",
    "language": "en",
    "notifications_enabled": true
  }
}
```

#### PUT /api/users/me

Update current user profile.

**Request**:
```json
{
  "email": "alice.new@example.com",
  "preferences": {
    "theme": "light",
    "language": "en"
  }
}
```

**Response** (200 OK):
```json
{
  "message": "Profile updated successfully",
  "user": {
    "user_id": "usr_1234567890",
    "username": "alice",
    "email": "alice.new@example.com",
    "preferences": {
      "theme": "light",
      "language": "en"
    }
  }
}
```

### AI Chat Endpoints

#### POST /api/chat/message

Send a message to AI and get response.

**Request**:
```json
{
  "message": "What is quantum computing?",
  "conversation_id": "conv_abc123",
  "persona": "helpful_assistant",
  "context": {
    "previous_topic": "physics"
  }
}
```

**Response** (200 OK):
```json
{
  "conversation_id": "conv_abc123",
  "message_id": "msg_xyz789",
  "response": "Quantum computing is a type of computing that uses quantum bits or 'qubits'...",
  "persona": "helpful_assistant",
  "timestamp": "2024-02-08T14:30:00Z",
  "metadata": {
    "model": "gpt-4",
    "tokens_used": 245,
    "response_time_ms": 1234
  }
}
```

**Errors**:
- `400`: Invalid message or context
- `429`: Rate limit exceeded
- `503`: AI service unavailable

#### GET /api/chat/conversations

List user's chat conversations.

**Query Parameters**:
- `page` (integer, default: 1): Page number
- `per_page` (integer, default: 20, max: 100): Items per page
- `sort` (string, default: "updated_desc"): Sort order

**Response** (200 OK):
```json
{
  "conversations": [
    {
      "conversation_id": "conv_abc123",
      "title": "Quantum Computing Discussion",
      "message_count": 15,
      "created_at": "2024-02-08T10:00:00Z",
      "updated_at": "2024-02-08T14:30:00Z",
      "persona": "helpful_assistant"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_items": 42,
    "total_pages": 3
  }
}
```

#### GET /api/chat/conversations/:id

Get conversation details and messages.

**Response** (200 OK):
```json
{
  "conversation_id": "conv_abc123",
  "title": "Quantum Computing Discussion",
  "created_at": "2024-02-08T10:00:00Z",
  "updated_at": "2024-02-08T14:30:00Z",
  "persona": "helpful_assistant",
  "messages": [
    {
      "message_id": "msg_1",
      "role": "user",
      "content": "What is quantum computing?",
      "timestamp": "2024-02-08T10:00:00Z"
    },
    {
      "message_id": "msg_2",
      "role": "assistant",
      "content": "Quantum computing is...",
      "timestamp": "2024-02-08T10:00:05Z",
      "metadata": {
        "model": "gpt-4",
        "tokens_used": 245
      }
    }
  ]
}
```

### Image Generation Endpoints

#### POST /api/images/generate

Generate an image from text prompt.

**Request**:
```json
{
  "prompt": "A serene mountain landscape at sunset",
  "style": "photorealistic",
  "size": "1024x1024",
  "backend": "huggingface",
  "negative_prompt": "blurry, low quality"
}
```

**Response** (202 Accepted):
```json
{
  "generation_id": "gen_abc123",
  "status": "processing",
  "estimated_time_seconds": 45,
  "status_url": "/api/images/status/gen_abc123"
}
```

**Errors**:
- `400`: Invalid prompt or parameters
- `403`: Content filter violation
- `429`: Rate limit exceeded

#### GET /api/images/status/:generation_id

Get status of image generation.

**Response** (200 OK) - Processing:
```json
{
  "generation_id": "gen_abc123",
  "status": "processing",
  "progress": 65,
  "estimated_time_remaining_seconds": 15
}
```

**Response** (200 OK) - Completed:
```json
{
  "generation_id": "gen_abc123",
  "status": "completed",
  "image_url": "https://storage.project-ai.com/images/gen_abc123.png",
  "thumbnail_url": "https://storage.project-ai.com/images/gen_abc123_thumb.png",
  "metadata": {
    "prompt": "A serene mountain landscape at sunset",
    "style": "photorealistic",
    "size": "1024x1024",
    "backend": "huggingface",
    "generation_time_seconds": 42.5,
    "created_at": "2024-02-08T14:35:00Z"
  }
}
```

**Response** (200 OK) - Failed:
```json
{
  "generation_id": "gen_abc123",
  "status": "failed",
  "error": "Content filter violation",
  "error_code": "CONTENT_FILTER",
  "retry_after_seconds": 60
}
```

#### GET /api/images/history

Get user's image generation history.

**Query Parameters**:
- `page` (integer, default: 1)
- `per_page` (integer, default: 20, max: 100)
- `status` (string): Filter by status (completed, failed, processing)

**Response** (200 OK):
```json
{
  "generations": [
    {
      "generation_id": "gen_abc123",
      "prompt": "A serene mountain landscape at sunset",
      "style": "photorealistic",
      "status": "completed",
      "image_url": "https://storage.project-ai.com/images/gen_abc123.png",
      "thumbnail_url": "https://storage.project-ai.com/images/gen_abc123_thumb.png",
      "created_at": "2024-02-08T14:35:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_items": 127,
    "total_pages": 7
  }
}
```

### Learning Path Endpoints

#### POST /api/learning/paths

Generate a personalized learning path.

**Request**:
```json
{
  "category": "machine_learning",
  "skill_level": "beginner",
  "time_commitment_hours": 10,
  "learning_style": "hands_on"
}
```

**Response** (201 Created):
```json
{
  "path_id": "path_xyz789",
  "category": "machine_learning",
  "skill_level": "beginner",
  "estimated_duration_days": 30,
  "modules": [
    {
      "module_id": "mod_1",
      "title": "Introduction to Machine Learning",
      "description": "Learn the basics of ML...",
      "difficulty": "beginner",
      "estimated_hours": 3,
      "topics": ["supervised learning", "linear regression"],
      "resources": [
        {
          "type": "video",
          "title": "ML Basics",
          "url": "https://...",
          "duration_minutes": 45
        },
        {
          "type": "article",
          "title": "Understanding Linear Regression",
          "url": "https://..."
        }
      ]
    }
  ],
  "created_at": "2024-02-08T14:40:00Z"
}
```

#### GET /api/learning/paths

List user's learning paths.

**Response** (200 OK):
```json
{
  "paths": [
    {
      "path_id": "path_xyz789",
      "category": "machine_learning",
      "skill_level": "beginner",
      "progress_percent": 45,
      "modules_completed": 3,
      "modules_total": 8,
      "created_at": "2024-02-08T14:40:00Z",
      "last_accessed": "2024-02-09T10:15:00Z"
    }
  ]
}
```

#### PUT /api/learning/paths/:path_id/progress

Update progress on a learning path.

**Request**:
```json
{
  "module_id": "mod_1",
  "status": "completed",
  "time_spent_minutes": 180
}
```

**Response** (200 OK):
```json
{
  "message": "Progress updated successfully",
  "path_id": "path_xyz789",
  "module_id": "mod_1",
  "status": "completed",
  "overall_progress_percent": 52
}
```

### Data Analysis Endpoints

#### POST /api/data/analyze

Upload and analyze a dataset.

**Request** (multipart/form-data):
```
file: dataset.csv
analysis_type: exploratory
```

**Response** (202 Accepted):
```json
{
  "analysis_id": "analysis_123",
  "status": "processing",
  "estimated_time_seconds": 120,
  "status_url": "/api/data/status/analysis_123"
}
```

#### GET /api/data/status/:analysis_id

Get analysis status and results.

**Response** (200 OK) - Completed:
```json
{
  "analysis_id": "analysis_123",
  "status": "completed",
  "file_name": "dataset.csv",
  "summary": {
    "rows": 1000,
    "columns": 15,
    "numeric_columns": 10,
    "categorical_columns": 5,
    "missing_values": 23
  },
  "visualizations": [
    {
      "type": "correlation_heatmap",
      "url": "https://storage.project-ai.com/viz/analysis_123_heatmap.png"
    },
    {
      "type": "distribution_plots",
      "url": "https://storage.project-ai.com/viz/analysis_123_dist.png"
    }
  ],
  "insights": [
    "Strong positive correlation between columns A and B (0.92)",
    "Column C has 15% missing values",
    "Data suggests 3 distinct clusters"
  ],
  "completed_at": "2024-02-08T14:50:00Z"
}
```

## Error Response Format

All error responses follow this structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    },
    "request_id": "req_abc123",
    "timestamp": "2024-02-08T14:30:00Z"
  }
}
```

### Error Codes

- `VALIDATION_ERROR`: Request validation failed
- `AUTHENTICATION_ERROR`: Authentication failed or token invalid
- `AUTHORIZATION_ERROR`: User lacks permission for this action
- `RATE_LIMIT_ERROR`: Rate limit exceeded
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `CONTENT_FILTER`: Content violates content policy
- `SERVICE_UNAVAILABLE`: External service unavailable
- `INTERNAL_ERROR`: Internal server error

## Rate Limiting

Rate limits are applied per user per endpoint:

| Endpoint Category | Rate Limit |
|-------------------|------------|
| Authentication | 10 requests/min |
| Chat Messages | 100 requests/hour |
| Image Generation | 20 requests/hour |
| Learning Paths | 50 requests/hour |
| Data Analysis | 10 requests/hour |
| Other Endpoints | 1000 requests/hour |

**Rate Limit Headers**:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1707401400
```

## Pagination

Paginated endpoints support these query parameters:

- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)
- `sort`: Sort field (varies by endpoint)
- `order`: Sort order (`asc` or `desc`)

**Pagination Response**:
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total_items": 127,
    "total_pages": 7,
    "has_next": true,
    "has_prev": true,
    "next_page": 3,
    "prev_page": 1
  }
}
```

## Webhooks

Configure webhooks to receive event notifications.

### POST /api/webhooks

Create a webhook endpoint.

**Request**:
```json
{
  "url": "https://your-app.com/webhooks",
  "events": [
    "image.generated",
    "analysis.completed",
    "learning.module_completed"
  ],
  "secret": "your_webhook_secret"
}
```

### Webhook Payload

```json
{
  "event": "image.generated",
  "data": {
    "generation_id": "gen_abc123",
    "user_id": "usr_1234567890",
    "image_url": "https://storage.project-ai.com/images/gen_abc123.png",
    "created_at": "2024-02-08T14:35:00Z"
  },
  "timestamp": "2024-02-08T14:35:05Z",
  "webhook_id": "webhook_456",
  "signature": "sha256=..."
}
```

## SDK Examples

### Python

```python
import requests

class ProjectAIClient:
    def __init__(self, api_key: str, base_url: str = "https://api.project-ai.com"):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def chat(self, message: str, conversation_id: str = None) -> dict:
        """Send a chat message"""
        response = self.session.post(
            f"{self.base_url}/api/chat/message",
            json={
                "message": message,
                "conversation_id": conversation_id
            }
        )
        response.raise_for_status()
        return response.json()
    
    def generate_image(self, prompt: str, style: str = "photorealistic") -> dict:
        """Generate an image"""
        response = self.session.post(
            f"{self.base_url}/api/images/generate",
            json={
                "prompt": prompt,
                "style": style
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_image_status(self, generation_id: str) -> dict:
        """Check image generation status"""
        response = self.session.get(
            f"{self.base_url}/api/images/status/{generation_id}"
        )
        response.raise_for_status()
        return response.json()

# Usage
client = ProjectAIClient(api_key="your_api_key")

# Chat with AI
response = client.chat("What is machine learning?")
print(response["response"])

# Generate image
generation = client.generate_image("A beautiful sunset")
print(f"Generation ID: {generation['generation_id']}")

# Check status
status = client.get_image_status(generation["generation_id"])
if status["status"] == "completed":
    print(f"Image URL: {status['image_url']}")
```

### JavaScript/TypeScript

```typescript
class ProjectAIClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(apiKey: string, baseUrl: string = 'https://api.project-ai.com') {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  private async request(endpoint: string, options: RequestInit = {}): Promise<any> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  async chat(message: string, conversationId?: string): Promise<any> {
    return this.request('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
  }

  async generateImage(prompt: string, style: string = 'photorealistic'): Promise<any> {
    return this.request('/api/images/generate', {
      method: 'POST',
      body: JSON.stringify({ prompt, style }),
    });
  }

  async getImageStatus(generationId: string): Promise<any> {
    return this.request(`/api/images/status/${generationId}`);
  }
}

// Usage
const client = new ProjectAIClient('your_api_key');

// Chat
const chatResponse = await client.chat('What is machine learning?');
console.log(chatResponse.response);

// Generate image
const generation = await client.generateImage('A beautiful sunset');
console.log(`Generation ID: ${generation.generation_id}`);
```

## Versioning

API version is specified in the URL path:

```
/v1/api/chat/message
/v2/api/chat/message (future version)
```

Current version: **v1** (default, can be omitted)

## OpenAPI Specification

Full OpenAPI 3.0 specification available at:
```
GET /api/openapi.json
GET /api/docs (Swagger UI)
```
