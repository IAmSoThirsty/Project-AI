---
title: "Web Application Architecture Visual Map"
id: visual-map-web-app
type: visual-map
version: "1.0.0"
created_date: "2026-04-20"
updated_date: "2026-04-20"
status: active
author: "AGENT-047 (Visual Relationship Maps Specialist)"

# Document Classification
area:
  - architecture
  - web
tags:
  - react
  - flask
  - visual-map
  - web-architecture
  - rest-api
component:
  - web-frontend
  - web-backend

# Relationships
related_docs:
  - system-overview.md
  - ../data-flows/authentication.md
  - ../integrations/external-apis.md

# Audience & Priority
audience:
  - developers
  - web-developers
  - architects
priority: P1
difficulty: intermediate
estimated_reading_time: "15 minutes"

# Security & Compliance
classification: internal
sensitivity: low

# Discovery
keywords: ["web application", "React", "Flask", "REST API", "SPA architecture"]
search_terms: ["web architecture", "React frontend", "Flask backend", "API design"]
aliases: ["Web App Architecture", "SPA Architecture Map"]

# Quality Metadata
review_status: approved
accuracy_rating: high
---

# Web Application Architecture Visual Map

**Version:** 1.0.0
**Author:** AGENT-047 (Visual Relationship Maps Specialist)
**Status:** Production-Ready
**Last Updated:** 2026-04-20

---

## Executive Summary

This visual map details the **web application architecture** for Project-AI, featuring a modern Single Page Application (SPA) built with **React 18 + Vite** frontend and **Flask** backend with governance routing. The architecture implements complete separation of concerns with dedicated frontend/backend services, JWT authentication, and comprehensive middleware stacks.

**Key Components:**
- **Frontend Stack:** React 18, Vite build system, Zustand state management, Material UI components
- **Backend Stack:** Flask REST API, SQLAlchemy ORM, governance pipeline routing
- **Communication:** REST API over HTTP, JWT bearer token authentication, CORS-enabled
- **State Management:** Zustand stores for auth, chat, settings, image generation
- **Security:** Rate limiting, CORS configuration, input validation, secure password hashing
- **Deployment:** Docker Compose with PostgreSQL database, separate port allocation (3000/5000)

**Purpose:**
- Provide browser-based access to Project-AI functionality
- Enable multi-user concurrent access with session management
- Support cloud deployment and scaling strategies
- Complement desktop application with web accessibility

**Current Status:** Development phase - Desktop application is production-ready, web version is evolving with full governance integration.

---

## ASCII Art - Web Application Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        WEB APPLICATION ARCHITECTURE                             │
│                     React SPA + Flask REST API + Governance                     │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER (PORT 3000)                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                    REACT 18 FRONTEND (Vite)                              │  │
│  │                    web/frontend/                                         │  │
│  ├──────────────────────────────────────────────────────────────────────────┤  │
│  │                                                                          │  │
│  │  Build System:                    State Management:                     │  │
│  │  ┌──────────────┐                ┌─────────────────┐                    │  │
│  │  │ Vite         │                │ Zustand Stores  │                    │  │
│  │  │ • HMR        │                ├─────────────────┤                    │  │
│  │  │ • Tree shake │                │ • authStore     │                    │  │
│  │  │ • TypeScript │                │ • chatStore     │                    │  │
│  │  │ • ESBuild    │                │ • settingsStore │                    │  │
│  │  └──────────────┘                │ • imageStore    │                    │  │
│  │                                  └─────────────────┘                    │  │
│  │                                                                          │  │
│  │  Component Structure:                                                   │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐   │  │
│  │  │  pages/                                                          │   │  │
│  │  │  ├─ LoginPage.tsx        → Authentication UI                     │   │  │
│  │  │  ├─ DashboardPage.tsx    → Main AI interface                     │   │  │
│  │  │  ├─ ImageGenPage.tsx     → Image generation UI                   │   │  │
│  │  │  └─ SettingsPage.tsx     → User preferences                      │   │  │
│  │  │                                                                  │   │  │
│  │  │  components/                                                     │   │  │
│  │  │  ├─ ChatPanel/           → Message input/display                │   │  │
│  │  │  ├─ PersonaPanel/        → AI personality config                │   │  │
│  │  │  ├─ StatsPanel/          → Usage statistics                     │   │  │
│  │  │  └─ ImageGenerator/      → Image creation interface             │   │  │
│  │  │                                                                  │   │  │
│  │  │  utils/                                                          │   │  │
│  │  │  ├─ apiClient.ts         → Axios HTTP client                    │   │  │
│  │  │  ├─ authUtils.ts         → JWT token management                 │   │  │
│  │  │  └─ validators.ts        → Input validation                     │   │  │
│  │  └──────────────────────────────────────────────────────────────────┘   │  │
│  │                                                                          │  │
│  │  Routing (React Router v6):                                             │  │
│  │  /login          → LoginPage                                            │  │
│  │  /dashboard      → DashboardPage (protected)                            │  │
│  │  /image-gen      → ImageGenPage (protected)                             │  │
│  │  /settings       → SettingsPage (protected)                             │  │
│  │                                                                          │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                         │
│                                       │ HTTP/REST (JSON)                        │
│                                       │ Authorization: Bearer <JWT>             │
│                                       ▼                                         │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                            SERVER LAYER (PORT 5000)                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                    FLASK REST API BACKEND                                │  │
│  │                    web/backend/app.py                                    │  │
│  ├──────────────────────────────────────────────────────────────────────────┤  │
│  │                                                                          │  │
│  │  Middleware Stack:                                                       │  │
│  │  ┌────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  1. CORS Middleware      → Cross-origin request handling          │  │  │
│  │  │  2. Rate Limiting        → Request throttling (10/min per IP)     │  │  │
│  │  │  3. JWT Validation       → Token verification for protected routes│  │  │
│  │  │  4. Request Logging      → Audit trail generation                │  │  │
│  │  │  5. Error Handling       → Centralized exception management      │  │  │
│  │  └────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                          │  │
│  │  API Endpoints:                                                          │  │
│  │  ┌────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  GET  /api/status                    → Health check              │  │  │
│  │  │  POST /api/auth/login                → User authentication       │  │  │
│  │  │  POST /api/auth/logout               → Session termination       │  │  │
│  │  │  POST /api/ai/chat                   → AI query processing       │  │  │
│  │  │  POST /api/ai/image-generate         → Image generation          │  │  │
│  │  │  GET  /api/user/profile              → User data retrieval       │  │  │
│  │  │  PUT  /api/user/profile              → User data update          │  │  │
│  │  │  GET  /api/persona/state             → AI personality state      │  │  │
│  │  │  PUT  /api/persona/state             → Update AI traits          │  │  │
│  │  │  GET  /api/memory/knowledge          → Knowledge base query      │  │  │
│  │  │  POST /api/memory/knowledge          → Add knowledge entry       │  │  │
│  │  └────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                          │  │
│  │  Request Flow (CRITICAL - Governance Integration):                      │  │
│  │  ┌────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  Flask Endpoint                                                    │  │  │
│  │  │       │                                                            │  │  │
│  │  │       ▼                                                            │  │  │
│  │  │  route_request() ───────→ Runtime Router                          │  │  │
│  │  │       │                         │                                 │  │  │
│  │  │       │                         ▼                                 │  │  │
│  │  │       │                   Governance Manager                      │  │  │
│  │  │       │                         │                                 │  │  │
│  │  │       │                         ▼                                 │  │  │
│  │  │       │                   AI Orchestrator                         │  │  │
│  │  │       │                         │                                 │  │  │
│  │  │       │                         ▼                                 │  │  │
│  │  │       │                   Core Systems (ai_systems.py, etc.)     │  │  │
│  │  │       │                         │                                 │  │  │
│  │  │       ▼                         ▼                                 │  │  │
│  │  │  JSON Response ◄────────── Result                                │  │  │
│  │  └────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                          │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                         │
│                                       │ ORM (SQLAlchemy)                        │
│                                       ▼                                         │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────┐          ┌──────────────────────────┐            │
│  │  PostgreSQL Database     │          │  JSON File Storage       │            │
│  │  (Production)            │          │  (Development)           │            │
│  ├──────────────────────────┤          ├──────────────────────────┤            │
│  │  Tables:                 │          │  Files:                  │            │
│  │  • users                 │          │  • users.json            │            │
│  │  • sessions              │          │  • ai_persona/state.json │            │
│  │  • chat_history          │          │  • memory/knowledge.json │            │
│  │  • ai_persona_state      │          │  • learning_requests/    │            │
│  │  • knowledge_base        │          │    requests.json         │            │
│  │  • learning_requests     │          │  • command_override_     │            │
│  │  • image_generations     │          │    config.json           │            │
│  └──────────────────────────┘          └──────────────────────────┘            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   OpenAI     │  │ HuggingFace  │  │  GitHub API  │  │  SMTP Server │       │
│  │   API        │  │   API        │  │              │  │              │       │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤       │
│  │ • GPT-4      │  │ • Stable     │  │ • Repository │  │ • Emergency  │       │
│  │ • DALL-E 3   │  │   Diffusion  │  │   Search     │  │   Alerts     │       │
│  │ • Embeddings │  │ • Image Gen  │  │ • CTF Data   │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘       │
│         ▲                  ▲                  ▲                  ▲              │
│         └──────────────────┴──────────────────┴──────────────────┘              │
│                           API Keys from .env                                    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Mermaid Diagram - Web Application Data Flow

```mermaid
graph TB
    subgraph "Client Browser"
        UI[React UI Components]
        Store[Zustand State Store]
        Router[React Router]
        API[Axios API Client]
    end

    subgraph "Flask Backend (Port 5000)"
        Flask[Flask App]
        CORS[CORS Middleware]
        RateLimit[Rate Limiter]
        JWT[JWT Validator]
        Routes[API Routes]
        Router_Core[Runtime Router]
        Gov[Governance Manager]
        Orch[AI Orchestrator]
    end

    subgraph "Core Systems"
        User[UserManager]
        AI[AIPersona]
        Memory[MemorySystem]
        Intelligence[Intelligence Engine]
        ImageGen[Image Generator]
    end

    subgraph "Data Storage"
        PG[(PostgreSQL)]
        JSON[JSON Files]
    end

    subgraph "External APIs"
        OpenAI[OpenAI API]
        HF[HuggingFace API]
        GitHub[GitHub API]
    end

    UI --> Store
    Store --> API
    Router --> UI
    API -->|HTTP POST/GET| Flask
    Flask --> CORS --> RateLimit --> JWT --> Routes
    Routes --> Router_Core
    Router_Core --> Gov
    Gov --> Orch
    Orch --> User
    Orch --> AI
    Orch --> Memory
    Orch --> Intelligence
    Orch --> ImageGen
    User --> PG
    User --> JSON
    AI --> JSON
    Memory --> JSON
    Intelligence --> OpenAI
    ImageGen --> OpenAI
    ImageGen --> HF
    Memory --> GitHub

    style Flask fill:#4CAF50
    style Router_Core fill:#FF9800
    style Gov fill:#E91E63
    style Orch fill:#9C27B0
    style UI fill:#2196F3
```

---

## Component Legend

### Frontend Components

| Component | Technology | Purpose | Location |
|-----------|-----------|---------|----------|
| **React UI** | React 18 | User interface components | `web/frontend/src/components/` |
| **Vite Build** | Vite 5.x | Build system with HMR | `web/frontend/vite.config.ts` |
| **Zustand Store** | Zustand | Lightweight state management | `web/frontend/src/stores/` |
| **React Router** | React Router v6 | Client-side routing | `web/frontend/src/App.tsx` |
| **Material UI** | MUI v5 | Component library | `web/frontend/src/components/` |
| **Axios Client** | Axios | HTTP request library | `web/frontend/src/utils/apiClient.ts` |

### Backend Components

| Component | Technology | Purpose | Location |
|-----------|-----------|---------|----------|
| **Flask App** | Flask 3.x | REST API server | `web/backend/app.py` |
| **Runtime Router** | Custom | Request routing to governance | `src/app/core/runtime/router.py` |
| **Governance Manager** | Custom | Policy enforcement | `src/app/governance/governance_manager.py` |
| **AI Orchestrator** | Custom | Multi-system coordination | `src/app/core/runtime/orchestrator.py` |
| **CORS Middleware** | Flask-CORS | Cross-origin support | `src/app/core/security/middleware.py` |
| **Rate Limiter** | Flask-Limiter | Request throttling | `src/app/core/security/middleware.py` |
| **JWT Auth** | PyJWT | Token-based authentication | `src/app/core/security/` |

### Data Layer

| Component | Technology | Purpose | Location |
|-----------|-----------|---------|----------|
| **PostgreSQL** | PostgreSQL 15+ | Production database | Docker container |
| **SQLAlchemy** | SQLAlchemy 2.x | ORM for database access | `web/backend/models/` |
| **JSON Storage** | Python json | Development persistence | `data/` directory |

---

## Detailed Documentation

### Frontend Architecture

#### State Management with Zustand

The web application uses **Zustand** for state management, chosen for its simplicity and minimal boilerplate compared to Redux. Each store manages a specific domain:

**Authentication Store (`authStore.ts`):**
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}
```

**Chat Store (`chatStore.ts`):**
```typescript
interface ChatState {
  messages: Message[];
  isLoading: boolean;
  sendMessage: (content: string) => Promise<void>;
  clearHistory: () => void;
}
```

**Image Generation Store (`imageStore.ts`):**
```typescript
interface ImageState {
  generatedImages: GeneratedImage[];
  isGenerating: boolean;
  generate: (prompt: string, options: ImageOptions) => Promise<void>;
  history: GeneratedImage[];
}
```

#### Component Architecture

Components follow a **container/presentational pattern**:

- **Containers** (`pages/`): Connect to Zustand stores, handle business logic
- **Presentational** (`components/`): Receive props, render UI, emit events

Example structure:
```
DashboardPage (container)
├── ChatPanel (presentational)
│   ├── MessageList
│   └── MessageInput
├── StatsPanel (presentational)
│   ├── UsageChart
│   └── SystemStatus
└── PersonaPanel (presentational)
    ├── TraitSlider
    └── MoodDisplay
```

#### Build Configuration

Vite configuration optimizes for:
- **Development:** Hot Module Replacement (HMR), instant server start
- **Production:** Tree shaking, code splitting, minification, asset optimization

Key settings in `vite.config.ts`:
```typescript
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['@mui/material', '@emotion/react'],
          'state-vendor': ['zustand', 'axios']
        }
      }
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:5000'
    }
  }
});
```

### Backend Architecture

#### Governance-Routed Request Flow

**Critical Architectural Pattern:** The Flask backend does NOT directly call core systems. All requests flow through the governance pipeline:

```python
@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    payload = request.get_json()

    # Route through governance (NOT direct AI call)
    response = route_request(
        source="web",
        payload={
            "action": "ai.chat",
            "task_type": "chat",
            "message": payload.get("message"),
            "context": payload.get("context", {})
        }
    )

    return jsonify(response), 200 if response["status"] == "success" else 500
```

This ensures:
1. **Policy Enforcement:** All requests validated against CODEX DEUS
2. **Audit Logging:** Complete trail of actions
3. **Rate Limiting:** Governance-level throttling
4. **Error Handling:** Centralized exception management
5. **Multi-System Coordination:** Orchestrator manages dependencies

#### Middleware Stack

**1. CORS Configuration (`configure_cors()`):**
```python
def configure_cors(app: Flask):
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "https://project-ai.example.com"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["X-Request-ID"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
```

**2. Rate Limiting (`configure_rate_limiting()`):**
```python
def configure_rate_limiting(app: Flask):
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

    # Stricter limits for expensive operations
    limiter.limit("10 per minute")(app.view_functions["ai_chat"])
    limiter.limit("5 per minute")(app.view_functions["ai_image_generate"])
```

**3. JWT Validation:**
- Tokens issued on successful login with 24-hour expiration
- Refresh token rotation for extended sessions
- Secure token storage in HTTP-only cookies (production) or localStorage (development)

#### API Design Patterns

**Consistent Response Format:**
```json
{
  "status": "success" | "error",
  "result": { /* data payload */ },
  "error": "error-code",
  "message": "Human-readable message",
  "timestamp": "2026-04-20T12:00:00Z",
  "request_id": "uuid"
}
```

**Error Codes:**
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (governance policy violation)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error (unexpected failures)

### Data Persistence Strategy

#### Development: JSON Files
- **Location:** `data/` directory
- **Format:** Human-readable JSON for easy debugging
- **Concurrency:** File locks for write operations
- **Migration:** Automatic upgrade path from plaintext to hashed passwords

#### Production: PostgreSQL
- **Schema:** SQLAlchemy models with migrations (Alembic)
- **Indexes:** Optimized for common queries (username, session ID, timestamp)
- **Backups:** Automated daily backups with point-in-time recovery
- **Connection Pool:** 20 max connections with 5-second timeout

### Security Implementation

#### Password Security
- **Hashing:** PBKDF2-SHA256 (preferred) with bcrypt fallback
- **Salt:** Automatic per-password salt generation
- **Rounds:** 29,000 iterations (OWASP recommendation)
- **Migration:** Automatic upgrade from bcrypt to PBKDF2

#### Token Security
- **Algorithm:** HS256 (HMAC with SHA-256)
- **Secret:** 256-bit random key from environment
- **Claims:** `user_id`, `role`, `issued_at`, `expires_at`
- **Rotation:** Refresh tokens issued alongside access tokens

#### Input Validation
- **Frontend:** Zod schemas for type-safe validation
- **Backend:** Pydantic models for request validation
- **SQL Injection:** Prevented via SQLAlchemy parameterized queries
- **XSS:** React automatic escaping + DOMPurify for raw HTML

### Deployment Architecture

#### Docker Compose Setup

```yaml
version: '3.8'

services:
  frontend:
    build: ./web/frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://backend:5000
    depends_on:
      - backend

  backend:
    build: ./web/backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/projectai
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
    volumes:
      - ./data:/app/data

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=projectai
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### Cloud Deployment Options

**Vercel (Frontend):**
- Automatic deployments from Git
- Edge CDN for global low latency
- Serverless functions for API routes

**Railway/Heroku (Backend):**
- Managed PostgreSQL database
- Automatic SSL certificates
- Health check monitoring

**AWS (Full Stack):**
- Frontend: S3 + CloudFront
- Backend: ECS Fargate containers
- Database: RDS PostgreSQL with Multi-AZ
- Caching: ElastiCache Redis

### Performance Optimizations

#### Frontend
- **Code Splitting:** Route-based lazy loading
- **Asset Optimization:** Image compression, font subsetting
- **Caching:** Service worker for offline support
- **Memoization:** React.memo for expensive components

#### Backend
- **Connection Pooling:** Reuse database connections
- **Response Caching:** Redis cache for expensive queries
- **Compression:** Gzip middleware for JSON responses
- **Async Operations:** Background task queue for image generation

---

## Key Insights

### Architectural Decisions

1. **Governance Integration:** Web backend routes ALL requests through governance pipeline, ensuring consistent policy enforcement across desktop and web interfaces.

2. **Separation of Concerns:** React frontend handles UI/UX, Flask backend handles business logic, core systems remain platform-agnostic.

3. **JWT Authentication:** Token-based auth enables stateless backend, supporting horizontal scaling and load balancing.

4. **Dual Storage Strategy:** JSON files for development simplicity, PostgreSQL for production scalability and ACID guarantees.

5. **Vite Build System:** Chosen over Create React App for faster dev server, smaller bundle sizes, and native ESM support.

### Common Gotchas

1. **CORS Preflight Requests:** OPTIONS requests must be allowed for all protected routes. Configure CORS before rate limiting.

2. **Token Expiration Handling:** Frontend must implement token refresh logic to avoid user logouts during active sessions.

3. **JSON vs PostgreSQL Migrations:** Core systems accept `data_dir` parameter - use different paths for file vs database storage.

4. **Port Conflicts:** Desktop app may use port 5000 for internal services. Use environment variable `FLASK_PORT` for flexibility.

5. **Environment Variables:** `.env` file location differs between development (project root) and Docker (mounted volume).

### Development Workflow

**Local Development:**
```bash
# Terminal 1: Backend
cd web/backend
python -m flask run --port 5000

# Terminal 2: Frontend
cd web/frontend
npm run dev

# Terminal 3: Database (optional)
docker run -p 5432:5432 -e POSTGRES_PASSWORD=dev postgres:15
```

**Production Build:**
```bash
# Build frontend
cd web/frontend
npm run build
# Output: dist/ directory with optimized assets

# Docker deployment
docker-compose -f web/docker-compose.yml up -d
```

### Monitoring and Observability

**Health Checks:**
- `GET /api/status` - Basic health check
- `GET /api/health/db` - Database connectivity
- `GET /api/health/ai` - AI systems availability

**Metrics:**
- Request rate per endpoint
- Average response time
- Error rate (4xx, 5xx)
- Active user sessions
- AI query token usage

**Logging:**
- Structured JSON logs with request IDs
- Log levels: DEBUG (dev), INFO (staging), WARNING (prod)
- Centralized logging via Sentry or CloudWatch

---

## Related Maps

- **[System Overview](system-overview.md)** - Complete system architecture
- **[Desktop Application](desktop-app.md)** - PyQt6 desktop architecture
- **[Authentication Flow](../data-flows/authentication.md)** - User authentication sequence
- **[External APIs Integration](../integrations/external-apis.md)** - Third-party service connections
- **[Security Defense Layers](../security/defense-layers.md)** - Multi-layer security architecture

---

**Status:** ✅ Production-Ready Documentation
**Validation:** Architecture verified against `web/backend/app.py`, `web/frontend/src/`, Docker configurations
**Next Review:** 2026-07-20 (Quarterly update cycle)

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
