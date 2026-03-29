<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / ARCHITECTURE.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / ARCHITECTURE.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# TTP - Texture Pack Repository System Architecture

## Executive Summary

This document specifies a production-grade, enterprise-ready texture pack repository system designed to support Unity cinematic-level quality across multiple texture categories, from pixel-grade to photorealistic PBR materials. The system is architected for scalability, security, observability, and operational excellence.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Component Specifications](#component-specifications)
4. [Data Models](#data-models)
5. [API Specifications](#api-specifications)
6. [Security Architecture](#security-architecture)
7. [Infrastructure & Deployment](#infrastructure--deployment)
8. [Observability & Operations](#observability--operations)
9. [Failure Modes & Recovery](#failure-modes--recovery)
10. [Performance & Scalability](#performance--scalability)

---

## System Overview

### Purpose

The TTP (Thirsty's Texture Packs) system provides a centralized, version-controlled repository for managing high-quality texture assets across multiple visual fidelity levels and use cases. The system supports:

- **Pixel-grade textures**: 8x8 to 128x128, pixel-perfect artwork
- **Mid-fidelity textures**: 512x512 to 2048x2048, standard game assets
- **Unity cinematic-grade textures**: 4096x4096 to 8192x8192, PBR-based photorealistic materials
- **Procedural/AI-generated textures**: Vector-based and parameterized assets

### Design Principles

1. **Correctness over convenience**: Strict validation, schema enforcement, immutable versioning
2. **Security-first**: Defense in depth, zero-trust model, supply chain protection
3. **Observability by default**: Comprehensive logging, tracing, metrics at all layers
4. **Operability**: Self-healing, graceful degradation, clear operational runbooks
5. **Performance**: Sub-100ms API response times, CDN-accelerated asset delivery

### Technology Stack

**Core Infrastructure**:
- **Version Control**: Git (GitHub) with Git LFS for large binary assets
- **Container Orchestration**: Kubernetes 1.28+
- **Service Mesh**: Istio 1.20+ for traffic management, security, observability
- **Cloud Provider**: Multi-cloud support (AWS primary, GCP secondary)

**Backend Services**:
- **API Gateway**: Kong 3.x with rate limiting, authentication, request validation
- **Application Runtime**: Python 3.12 with FastAPI 0.110+ and uvicorn
- **Database**: PostgreSQL 16.2 with pgvector for texture similarity search
- **Cache**: Redis 7.2 with Redis Cluster for distributed caching
- **Search**: Elasticsearch 8.12 for full-text texture metadata search
- **Object Storage**: S3-compatible storage (AWS S3/MinIO) for texture assets

**CI/CD & Security**:
- **CI/CD**: GitHub Actions with custom runners, ArgoCD for GitOps
- **Secret Management**: HashiCorp Vault 1.16+ with automatic rotation
- **Image Scanning**: Trivy for container vulnerability scanning
- **SBOM Generation**: Syft for software bill of materials
- **License Compliance**: FOSSA for license scanning

**Observability Stack**:
- **Metrics**: Prometheus 2.50+ with Thanos for long-term storage
- **Logging**: Fluent Bit → Loki 2.9+ → Grafana 10.4+
- **Tracing**: OpenTelemetry → Tempo 2.4+
- **Dashboards**: Grafana with pre-built dashboards
- **Alerting**: Prometheus Alertmanager → PagerDuty/Slack

**Frontend/Client**:
- **CLI Tool**: Python-based CLI with rich terminal UI
- **Web UI**: React 18+ with TypeScript, Material-UI
- **CDN**: CloudFront/Cloudflare for global asset distribution

---

## Architecture Layers

### L0: Hardware & OS Layer

**Assumptions**:
- x86_64 architecture (Intel/AMD) for compute nodes
- NVMe SSDs for local storage (min 500 GB/node)
- 10 Gbps network minimum between nodes
- Linux kernel 5.15+ (Ubuntu 22.04 LTS or Amazon Linux 2023)
- Clock synchronization via NTP (max 100ms skew tolerated)

**Resource Quotas**:
- API pods: 2 CPU cores, 4 GB RAM (limit: 4 CPU, 8 GB RAM)
- Worker pods: 4 CPU cores, 8 GB RAM (limit: 8 CPU, 16 GB RAM)
- Database: 8 CPU cores, 32 GB RAM, 500 GB storage
- Redis: 2 CPU cores, 4 GB RAM, 100 GB storage

### L1: Container & Orchestration Layer

**Kubernetes Configuration**:
- Namespace isolation: `ttp-prod`, `ttp-staging`, `ttp-dev`
- Pod Security Standards: Restricted mode enforced
- Network Policies: Default deny, explicit allow rules only
- Resource Quotas: Per-namespace CPU/memory limits
- RBAC: Principle of least privilege, no cluster-admin in production

**Service Mesh (Istio)**:
- mTLS enforced between all services
- Circuit breaker: 50 concurrent connections, 10 consecutive errors
- Retry policy: 3 attempts with exponential backoff (base 25ms)
- Timeout: 30s for API calls, 300s for asset uploads

### L2: Data Layer

#### PostgreSQL Database Schema

**Tables**:

```sql
-- Texture pack metadata
CREATE TABLE texture_packs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    author_id UUID NOT NULL REFERENCES users(id),
    license VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('draft', 'review', 'published', 'deprecated')),
    category VARCHAR(50) NOT NULL,
    quality_tier VARCHAR(20) NOT NULL CHECK (quality_tier IN ('pixel', 'standard', 'high', 'cinematic', 'ultra')),
    tags TEXT[] NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}',
    checksum_sha256 VARCHAR(64) NOT NULL,
    size_bytes BIGINT NOT NULL,
    download_count BIGINT DEFAULT 0,
    CONSTRAINT unique_pack_version UNIQUE(slug, version)
);

CREATE INDEX idx_texture_packs_author ON texture_packs(author_id);
CREATE INDEX idx_texture_packs_status ON texture_packs(status);
CREATE INDEX idx_texture_packs_category ON texture_packs(category);
CREATE INDEX idx_texture_packs_quality ON texture_packs(quality_tier);
CREATE INDEX idx_texture_packs_tags ON texture_packs USING GIN(tags);
CREATE INDEX idx_texture_packs_metadata ON texture_packs USING GIN(metadata);

-- Individual texture assets within a pack
CREATE TABLE texture_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pack_id UUID NOT NULL REFERENCES texture_packs(id) ON DELETE CASCADE,
    filename VARCHAR(512) NOT NULL,
    path VARCHAR(1024) NOT NULL,
    asset_type VARCHAR(50) NOT NULL CHECK (asset_type IN ('albedo', 'normal', 'roughness', 'metallic', 'ao', 'height', 'emission', 'opacity', 'combined')),
    format VARCHAR(20) NOT NULL CHECK (format IN ('png', 'jpg', 'exr', 'tga', 'tiff', 'svg', 'psd')),
    resolution VARCHAR(20), -- e.g., "4096x4096"
    color_space VARCHAR(20) NOT NULL CHECK (color_space IN ('srgb', 'linear', 'acescg', 'raw')),
    bit_depth INTEGER NOT NULL,
    compression VARCHAR(20),
    size_bytes BIGINT NOT NULL,
    checksum_sha256 VARCHAR(64) NOT NULL,
    storage_url TEXT NOT NULL,
    cdn_url TEXT,
    preview_url TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_asset_path UNIQUE(pack_id, path)
);

CREATE INDEX idx_texture_assets_pack ON texture_assets(pack_id);
CREATE INDEX idx_texture_assets_type ON texture_assets(asset_type);
CREATE INDEX idx_texture_assets_format ON texture_assets(format);

-- User management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'creator', 'viewer')) DEFAULT 'viewer',
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'suspended', 'deleted')) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Download tracking and analytics
CREATE TABLE downloads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pack_id UUID NOT NULL REFERENCES texture_packs(id),
    user_id UUID REFERENCES users(id),
    ip_address INET,
    user_agent TEXT,
    downloaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    success BOOLEAN NOT NULL,
    bytes_transferred BIGINT,
    duration_ms INTEGER,
    error_message TEXT
);

CREATE INDEX idx_downloads_pack ON downloads(pack_id);
CREATE INDEX idx_downloads_user ON downloads(user_id);
CREATE INDEX idx_downloads_time ON downloads(downloaded_at DESC);

-- Audit log for all operations
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    result VARCHAR(20) NOT NULL CHECK (result IN ('success', 'failure', 'partial')),
    error_message TEXT
);

CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_resource ON audit_log(resource_type, resource_id);
```

**Database Invariants**:
- All timestamps stored in UTC
- All foreign keys enforced with appropriate ON DELETE behavior
- Checksums verified on write and periodically validated
- Row-level security (RLS) enabled for multi-tenant isolation
- Automatic vacuuming configured (autovacuum_naptime = 60s)

**Replication**:
- Synchronous replication to 1 standby (RPO = 0)
- Asynchronous replication to 2 additional standbys for read scaling
- Automatic failover via Patroni with etcd consensus
- Point-in-time recovery (PITR) enabled, 30-day retention

#### Redis Cache Strategy

**Key Patterns**:
```
pack:metadata:{pack_id}               -> Pack metadata JSON (TTL: 3600s)
pack:assets:{pack_id}                 -> List of asset IDs (TTL: 3600s)
user:session:{session_id}             -> User session data (TTL: 86400s)
rate_limit:{user_id}:{endpoint}       -> Rate limit counter (TTL: 60s)
search:results:{query_hash}           -> Search results cache (TTL: 300s)
analytics:downloads:{pack_id}:{date}  -> Daily download count (TTL: 604800s)
```

**Eviction Policy**: `allkeys-lru` for general cache, `volatile-lru` for session data

**Persistence**: RDB snapshots every 5 minutes + AOF with `everysec` fsync

**Cluster Configuration**:
- 6 nodes (3 masters, 3 replicas)
- Hash slot distribution for horizontal scaling
- Automatic failover via Redis Sentinel

#### Object Storage (S3)

**Bucket Structure**:
```
ttp-texture-assets-prod/
├── packs/
│   └── {pack_id}/
│       └── {version}/
│           ├── metadata.json
│           ├── textures/
│           │   ├── albedo/
│           │   ├── normal/
│           │   └── ...
│           └── previews/
├── temp/                      # 24h lifecycle expiration
└── archives/                  # Long-term storage (Glacier)
```

**Bucket Policies**:
- Versioning enabled for all objects
- Server-side encryption with KMS (AES-256)
- Lifecycle policies: Delete temp objects after 24h, transition archives to Glacier after 90 days
- Object Lock for immutable versions (compliance mode)
- Cross-region replication to secondary region

**Access Patterns**:
- Presigned URLs for direct uploads (TTL: 15 minutes)
- CloudFront distribution for read access with signed cookies
- S3 Transfer Acceleration for cross-region uploads

### L3: Application Layer

#### API Service Architecture

**FastAPI Application Structure**:
```python
ttp_api/
├── main.py                    # Application entry point
├── config.py                  # Configuration management
├── dependencies.py            # Dependency injection
├── models/                    # Pydantic models
│   ├── pack.py
│   ├── asset.py
│   └── user.py
├── schemas/                   # Database models (SQLAlchemy)
│   ├── pack.py
│   ├── asset.py
│   └── user.py
├── routes/                    # API endpoints
│   ├── packs.py
│   ├── assets.py
│   ├── search.py
│   └── admin.py
├── services/                  # Business logic
│   ├── pack_service.py
│   ├── asset_service.py
│   ├── validation_service.py
│   └── storage_service.py
├── middleware/                # Cross-cutting concerns
│   ├── auth.py
│   ├── rate_limit.py
│   ├── logging.py
│   └── error_handler.py
├── utils/                     # Utilities
│   ├── crypto.py
│   ├── image.py
│   └── validators.py
└── tests/                     # Test suite
    ├── unit/
    ├── integration/
    └── e2e/
```

**API Endpoints** (RESTful design):

```
GET    /api/v1/packs                 # List packs (paginated)
POST   /api/v1/packs                 # Create new pack (creator role)
GET    /api/v1/packs/{pack_id}       # Get pack details
PUT    /api/v1/packs/{pack_id}       # Update pack (owner/admin only)
DELETE /api/v1/packs/{pack_id}       # Delete pack (admin only)
GET    /api/v1/packs/{pack_id}/download   # Download pack (presigned URL)

GET    /api/v1/packs/{pack_id}/assets     # List assets in pack
POST   /api/v1/packs/{pack_id}/assets     # Upload asset
GET    /api/v1/assets/{asset_id}          # Get asset details
DELETE /api/v1/assets/{asset_id}          # Delete asset

GET    /api/v1/search                # Search packs (Elasticsearch)
GET    /api/v1/categories            # List categories
GET    /api/v1/tags                  # List popular tags

GET    /api/v1/users/me              # Current user profile
PUT    /api/v1/users/me              # Update profile
GET    /api/v1/users/{user_id}       # Public user profile

GET    /api/v1/admin/stats           # System statistics (admin only)
GET    /api/v1/admin/audit           # Audit log (admin only)
POST   /api/v1/admin/users/{user_id}/suspend  # Suspend user

GET    /healthz                      # Kubernetes liveness probe
GET    /readyz                       # Kubernetes readiness probe
GET    /metrics                      # Prometheus metrics
```

**Request/Response Format**:

All requests accept and return `application/json` unless specified otherwise.

**Example: Create Pack Request**:
```json
POST /api/v1/packs
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "name": "Cinematic Urban Environment",
  "description": "Ultra-high resolution PBR textures for urban scenes",
  "category": "environment",
  "quality_tier": "cinematic",
  "license": "CC-BY-4.0",
  "tags": ["urban", "pbr", "4k", "photorealistic"],
  "metadata": {
    "target_engine": "unity",
    "render_pipeline": "hdrp",
    "material_type": "pbr-metallic-roughness",
    "includes_lods": true
  }
}
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Cinematic Urban Environment",
  "slug": "cinematic-urban-environment",
  "version": "1.0.0",
  "status": "draft",
  "created_at": "2026-02-18T15:30:00Z",
  "upload_url": "https://s3.amazonaws.com/ttp-texture-assets/...",
  "upload_expires_at": "2026-02-18T15:45:00Z"
}
```

**Error Response Format**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid pack metadata",
    "details": [
      {
        "field": "quality_tier",
        "issue": "Must be one of: pixel, standard, high, cinematic, ultra"
      }
    ],
    "request_id": "req_abc123",
    "timestamp": "2026-02-18T15:30:00Z"
  }
}
```

**HTTP Status Codes**:
- `200 OK`: Successful GET/PUT
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing/invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `422 Unprocessable Entity`: Semantic validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

**Rate Limiting**:
- Anonymous: 60 requests/hour
- Authenticated viewer: 300 requests/hour
- Authenticated creator: 1000 requests/hour
- Admin: 5000 requests/hour
- Per-endpoint limits: Upload 10/hour, Download 100/hour

**Pagination**:
```
GET /api/v1/packs?page=2&per_page=20&sort=created_at&order=desc

Response:
{
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total_pages": 15,
    "total_items": 287,
    "has_next": true,
    "has_prev": true
  },
  "links": {
    "self": "/api/v1/packs?page=2&per_page=20",
    "first": "/api/v1/packs?page=1&per_page=20",
    "prev": "/api/v1/packs?page=1&per_page=20",
    "next": "/api/v1/packs?page=3&per_page=20",
    "last": "/api/v1/packs?page=15&per_page=20"
  }
}
```

### L4: Security Layer

#### Authentication & Authorization

**Authentication Methods**:

1. **OAuth 2.0 / OpenID Connect** (Primary):
   - Provider: Auth0 / Okta / Keycloak
   - Flow: Authorization Code with PKCE
   - Token type: JWT (RS256 signed)
   - Token lifetime: Access token 1h, Refresh token 30d
   - Token rotation on refresh

2. **API Keys** (Service-to-service):
   - Format: `ttp_live_` + 32-byte random (base64url)
   - Scoped permissions (read-only, read-write, admin)
   - Automatic rotation every 90 days
   - Stored as SHA-256 hash in database

3. **mTLS** (Internal services):
   - Certificate-based authentication
   - Istio-managed certificates
   - Automatic rotation every 24h

**JWT Token Structure**:
```json
{
  "iss": "https://auth.ttp.example.com",
  "sub": "user|550e8400-e29b-41d4-a716-446655440000",
  "aud": "ttp-api",
  "iat": 1708272600,
  "exp": 1708276200,
  "azp": "ttp-web-client",
  "scope": "openid profile email packs:read packs:write",
  "permissions": ["packs:read", "packs:write", "assets:upload"],
  "role": "creator",
  "tenant_id": "org_abc123"
}
```

**Authorization Model** (RBAC):

Roles:
- `viewer`: Read-only access to public packs
- `creator`: Can create, edit own packs; read all public packs
- `admin`: Full access to all resources, user management

Permissions matrix:
```
                        viewer  creator  admin
packs:list              ✓       ✓        ✓
packs:read              ✓       ✓        ✓
packs:create            ✗       ✓        ✓
packs:update_own        ✗       ✓        ✓
packs:update_any        ✗       ✗        ✓
packs:delete_own        ✗       ✓        ✓
packs:delete_any        ✗       ✗        ✓
assets:upload           ✗       ✓        ✓
assets:delete           ✗       ✓        ✓
users:read_own          ✓       ✓        ✓
users:read_any          ✗       ✗        ✓
users:manage            ✗       ✗        ✓
admin:audit_log         ✗       ✗        ✓
```

**Session Management**:
- Server-side sessions stored in Redis
- Session ID: 32-byte random token
- Sliding expiration: 24h of inactivity
- IP binding + User-Agent fingerprinting
- Concurrent session limit: 5 per user

#### Input Validation & Sanitization

**File Upload Validation**:
1. File type verification via magic bytes (not extension)
2. Image dimension limits: Max 16384x16384 pixels
3. File size limits:
   - Pixel textures: Max 10 MB
   - Standard textures: Max 50 MB
   - Cinematic textures: Max 500 MB per file, 5 GB per pack
4. Malware scanning via ClamAV
5. Metadata extraction and validation (EXIF data sanitized)
6. Hash verification (SHA-256)

**API Input Validation**:
- Pydantic models for all request bodies
- String length limits enforced
- SQL injection prevention via parameterized queries
- NoSQL injection prevention via input sanitization
- Path traversal prevention
- SSRF prevention (URL validation against allowlist)
- XSS prevention (HTML sanitization for user-generated content)

**Content Security Policy** (Web UI):
```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'sha256-{hash}';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https://cdn.ttp.example.com;
  font-src 'self' data:;
  connect-src 'self' https://api.ttp.example.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
```

#### Secrets Management

**Vault Configuration**:
```hcl
# Database credentials
path "database/creds/ttp-api" {
  capabilities = ["read"]
}

# API keys
path "kv/data/ttp/api-keys/*" {
  capabilities = ["read"]
}

# JWT signing keys
path "transit/keys/jwt-signer" {
  capabilities = ["read", "sign"]
}
```

**Secret Rotation Schedule**:
- Database passwords: 90 days
- API keys: 90 days
- JWT signing keys: 180 days (dual-key rotation)
- TLS certificates: 90 days (automated via cert-manager)
- Encryption keys: 365 days

**Encryption at Rest**:
- Database: AES-256-GCM via PostgreSQL pgcrypto
- S3 objects: SSE-KMS with customer-managed keys
- Redis: No encryption (ephemeral cache data only)
- Backups: AES-256-GCM via AWS Backup

**Encryption in Transit**:
- TLS 1.3 only (TLS 1.2 allowed for legacy clients with warnings)
- Cipher suites: ECDHE-RSA-AES256-GCM-SHA384, ECDHE-RSA-CHACHA20-POLY1305
- Certificate pinning for mobile clients
- HSTS with max-age=31536000, includeSubDomains, preload

#### Supply Chain Security

**Dependency Management**:
- SBOM generated for all container images (CycloneDX format)
- Vulnerability scanning with Trivy (critical/high CVEs block deployment)
- License compliance via FOSSA (no GPL/AGPL dependencies)
- Dependency pinning with hash verification (pip-tools, npm lockfiles)
- Automated dependency updates via Dependabot with CI validation

**Container Image Security**:
- Base images: Distroless (gcr.io/distroless) or Alpine Linux
- Non-root user (UID 65534)
- Read-only root filesystem
- No shell in production images
- Multi-stage builds to minimize attack surface
- Image signing via Cosign with Sigstore

**Code Scanning**:
- SAST: Semgrep, Bandit (Python), ESLint (JavaScript)
- DAST: OWASP ZAP in staging environment
- Secret scanning: GitGuardian, TruffleHog
- Code review required for all changes (2 approvers for production)

---

## Observability & Operations

### Logging

**Log Levels**:
- `DEBUG`: Detailed diagnostic information (dev/staging only)
- `INFO`: General informational messages
- `WARNING`: Warning messages for potentially harmful situations
- `ERROR`: Error events that allow the application to continue
- `CRITICAL`: Critical conditions requiring immediate attention

**Structured Logging Format** (JSON):
```json
{
  "timestamp": "2026-02-18T15:30:00.123Z",
  "level": "INFO",
  "logger": "ttp_api.services.pack_service",
  "message": "Pack created successfully",
  "context": {
    "pack_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user_123",
    "pack_name": "Cinematic Urban Environment"
  },
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "request_id": "req_abc123",
  "environment": "production",
  "service": "ttp-api",
  "version": "1.2.3"
}
```

**Log Retention**:
- Production: 30 days in Loki, 365 days in cold storage (S3)
- Staging: 7 days
- Development: 3 days

**Log Aggregation Pipeline**:
```
Application → Fluent Bit (sidecar) → Loki → Grafana
                                   ↓
                                Long-term storage (S3)
```

### Metrics

**Golden Signals** (SRE metrics):

1. **Latency**:
   - API response time (p50, p95, p99)
   - Database query time
   - S3 upload/download time
   - CDN cache hit rate

2. **Traffic**:
   - Requests per second
   - Bandwidth (ingress/egress)
   - Active connections

3. **Errors**:
   - HTTP 4xx/5xx rate
   - Database connection errors
   - S3 upload failures
   - Validation errors

4. **Saturation**:
   - CPU utilization
   - Memory utilization
   - Disk I/O
   - Network I/O
   - Database connection pool usage

**Custom Application Metrics**:
```
# Pack operations
ttp_packs_created_total{quality_tier="cinematic"}
ttp_packs_downloads_total{pack_id="..."}
ttp_packs_upload_size_bytes{quality_tier="cinematic"}

# Asset operations
ttp_assets_processed_total{asset_type="albedo", format="exr"}
ttp_assets_validation_failures_total{reason="dimension_exceeded"}

# User activity
ttp_users_active_total{role="creator"}
ttp_searches_total{category="environment"}

# Performance
ttp_api_request_duration_seconds{method="GET", endpoint="/packs"}
ttp_db_query_duration_seconds{query="get_pack_by_id"}
```

**Metric Collection**:
- Prometheus scraping every 15s
- Metric retention: 15 days in Prometheus, infinite in Thanos
- Recording rules for expensive aggregations
- Alerting rules for SLO violations

### Tracing

**Distributed Tracing**:
- OpenTelemetry SDK integrated in all services
- Trace sampling: 1% in production, 100% in staging
- Trace context propagation via W3C Trace Context headers
- Span attributes: service name, operation, user ID, pack ID, error details

**Trace Export**:
```
Application → OpenTelemetry Collector → Tempo → Grafana
                                      ↓
                                  Jaeger (optional UI)
```

**Example Trace**:
```
/api/v1/packs/{pack_id}/download (250ms)
├── auth_middleware (5ms)
├── get_pack_from_db (20ms)
│   └── postgresql_query (18ms)
├── check_permissions (2ms)
├── generate_presigned_url (15ms)
│   └── s3_api_call (12ms)
└── log_download_event (3ms)
    └── redis_incr (1ms)
```

### Alerting

**Alert Severity Levels**:
- `P1 Critical`: Service down, data loss risk (page immediately)
- `P2 High`: Degraded performance, partial outage (page during business hours)
- `P3 Medium`: Warning conditions, potential issues (ticket)
- `P4 Low`: Informational, maintenance needed (ticket, low priority)

**Example Alerts**:

```yaml
# API availability
- alert: APIHighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  severity: P1
  description: "API error rate above 5% for 5 minutes"

# Database performance
- alert: DatabaseSlowQueries
  expr: histogram_quantile(0.95, rate(pg_query_duration_seconds_bucket[5m])) > 1.0
  for: 10m
  severity: P2
  description: "Database p95 query latency above 1s"

# Storage capacity
- alert: DiskSpaceLow
  expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.15
  for: 30m
  severity: P2
  description: "Disk space below 15%"

# Resource saturation
- alert: MemoryPressure
  expr: container_memory_working_set_bytes / container_spec_memory_limit_bytes > 0.85
  for: 15m
  severity: P3
  description: "Container memory usage above 85%"
```

**On-Call Rotation**:
- Primary on-call: 24/7 coverage
- Secondary on-call: Escalation after 15 minutes
- Incident response SLA: Acknowledge P1 within 15 minutes, P2 within 1 hour

---

## Failure Modes & Recovery

### Failure Scenarios

#### Database Failure

**Scenario**: PostgreSQL primary node crashes

**Detection**:
- Patroni health check fails (3 consecutive failures, 5s interval)
- Prometheus alert: `PostgreSQLDown`

**Automated Recovery**:
1. Patroni promotes standby to primary (RTO: 30s)
2. Application reconnects to new primary via connection pool
3. Read replicas re-sync from new primary

**Manual Intervention Required**:
- If all replicas fail: Restore from last backup (RPO: 5 minutes)
- Verify data consistency after failover
- Investigate root cause (disk failure, OOM, network partition)

**Mitigation**:
- Regular backup verification tests (weekly)
- Automated failover drills (monthly)
- Database resource monitoring with predictive alerts

#### S3 Outage

**Scenario**: AWS S3 region outage

**Detection**:
- S3 API returns 503 errors
- Prometheus alert: `S3HighErrorRate`
- CloudWatch alarm: `S3 4xxErrors > threshold`

**Automated Recovery**:
- CDN continues serving cached assets (TTL: 24h for popular assets)
- API returns cached metadata from Redis
- Upload requests queued in SQS for later processing

**Degraded Mode**:
- Read-only mode for pack downloads (cached content only)
- New pack uploads delayed until S3 recovers
- User-facing message: "Uploads temporarily paused due to maintenance"

**Manual Recovery**:
- If prolonged: Failover to cross-region S3 bucket
- Update CloudFront origin to secondary bucket
- Verify data consistency between regions

#### API Pod Crash Loop

**Scenario**: Application crashes due to memory leak

**Detection**:
- Kubernetes restarts pod (CrashLoopBackOff after 5 restarts)
- Prometheus alert: `PodCrashLooping`
- Error rate spike in logs

**Automated Recovery**:
1. Kubernetes continues restarting pod with exponential backoff
2. Load balancer routes traffic to healthy pods
3. HPA scales up additional pods to handle load

**Investigation**:
- Collect crash dump for analysis
- Review recent deployments for regressions
- Check memory metrics for leak patterns

**Resolution**:
- Hotfix: Increase memory limits temporarily
- Long-term: Fix memory leak in code
- Rollback to last known good version if critical

#### Network Partition

**Scenario**: Network partition between application and database

**Detection**:
- Database connection timeouts
- Prometheus alert: `DatabaseConnectionFailures`
- Application logs: "Connection refused"

**Behavior**:
- Connection pool attempts reconnection with exponential backoff
- Circuit breaker opens after 10 consecutive failures
- Application returns 503 Service Unavailable with Retry-After header

**Recovery**:
- Network partition resolves automatically
- Circuit breaker closes after successful health check
- Connection pool re-establishes connections
- Backlog of requests processed

#### Data Corruption

**Scenario**: Corrupted texture file uploaded

**Detection**:
- Checksum mismatch on download
- User report of corrupted file
- Automated integrity check (daily cron job)

**Response**:
1. Mark asset as corrupted in database
2. Alert administrators
3. Quarantine corrupted file (move to separate bucket)
4. Notify pack owner

**Recovery**:
- Restore from S3 versioned backup
- Re-upload from source if backup unavailable
- Update checksum in database
- Notify affected users

### Disaster Recovery

**RPO (Recovery Point Objective)**: 5 minutes
**RTO (Recovery Time Objective)**: 15 minutes

**Backup Strategy**:
- Database: Continuous WAL archiving + daily full backup
- S3: Object versioning + cross-region replication
- Elasticsearch: Snapshot every 6 hours to S3
- Redis: RDB snapshot every hour (cache can be rebuilt)

**DR Runbook**:
1. **Assessment** (0-5 min):
   - Identify scope of failure
   - Activate incident commander
   - Notify stakeholders

2. **Containment** (5-10 min):
   - Isolate affected systems
   - Enable read-only mode if needed
   - Preserve logs and evidence

3. **Recovery** (10-30 min):
   - Restore from backups
   - Verify data integrity
   - Gradual traffic ramp-up

4. **Validation** (30-60 min):
   - Smoke tests
   - Monitor error rates
   - User acceptance testing

5. **Post-Mortem** (24-48 hours):
   - Root cause analysis
   - Document lessons learned
   - Implement preventive measures

**DR Testing**:
- Quarterly full DR drills
- Monthly backup restoration tests
- Annual chaos engineering exercises

---

## Performance & Scalability

### Performance Targets

**SLIs (Service Level Indicators)**:
- API response time p95: < 200ms
- API response time p99: < 500ms
- API availability: > 99.9% (43.8 minutes downtime/month)
- Asset download throughput: > 100 MB/s per user
- Search query latency p95: < 100ms

**SLOs (Service Level Objectives)**:
- 99.9% of API requests complete in < 200ms
- 99.95% of API requests succeed (HTTP 2xx/3xx)
- 99.99% of asset downloads succeed
- Zero data loss for committed transactions

**Capacity Planning**:
- Current: 1000 packs, 50,000 assets, 10 TB storage
- Year 1: 5000 packs, 250,000 assets, 50 TB storage
- Year 3: 25,000 packs, 1M assets, 250 TB storage

### Scalability Architecture

**Horizontal Scaling**:
- API pods: Auto-scaling (min 3, max 50)
  - CPU > 70% → scale up
  - Requests/sec > 1000/pod → scale up
- Worker pods: Auto-scaling (min 2, max 20)
- Database: Read replicas (up to 5)
- Redis: Cluster mode (up to 30 nodes)
- Elasticsearch: 3 nodes → 15 nodes

**Vertical Scaling Limits**:
- API pods: Max 4 CPU, 8 GB RAM
- Database: Max 64 CPU, 256 GB RAM (before sharding)

**Database Sharding Strategy** (future):
- Shard key: `pack_id` (hash-based)
- 4 initial shards, expand to 16 as needed
- Consistent hashing for even distribution
- Foreign key relationships maintained within shards

**Caching Strategy**:
- L1: In-memory application cache (TTL: 60s)
- L2: Redis cache (TTL: 3600s)
- L3: CDN cache (TTL: 86400s)
- Cache invalidation: Event-driven (pub/sub on updates)

**CDN Configuration**:
- Edge locations: 200+ globally (CloudFront)
- Cache hit ratio target: > 95%
- Origin shield enabled for high-traffic assets
- Range requests supported for large files
- Brotli/gzip compression enabled

### Load Testing

**Steady-State Load**:
- 100 requests/second
- 500 concurrent users
- 80% reads, 20% writes

**Peak Load**:
- 1000 requests/second
- 5000 concurrent users
- 90% reads, 10% writes

**Stress Test**:
- Ramp to 5000 requests/second
- Identify breaking point
- Measure graceful degradation

**Load Testing Tools**:
- k6 for API load testing
- JMeter for complex scenarios
- Gatling for realistic user behavior simulation

**Performance Regression Tests**:
- Run on every deployment to staging
- Alert if p95 latency increases > 10%
- Block deployment if p99 > 500ms

---

## Deployment & Operations

### Deployment Strategy

**GitOps with ArgoCD**:
- Git repository as source of truth
- Automated sync every 3 minutes
- Manual approval for production deployments
- Automatic rollback on health check failure

**Deployment Patterns**:

1. **Canary Deployment** (default for production):
   ```
   Phase 1: Deploy to 10% of pods (5 minutes)
   Phase 2: Monitor error rate, latency
   Phase 3: If healthy, deploy to 50% (5 minutes)
   Phase 4: Monitor again
   Phase 5: Deploy to 100%
   Rollback: If error rate > 1%, automatic rollback
   ```

2. **Blue-Green Deployment** (for database schema changes):
   ```
   - Deploy green environment with new schema
   - Run database migrations (backward compatible)
   - Smoke test green environment
   - Switch traffic to green
   - Keep blue environment for 24h (quick rollback)
   - Decommission blue environment
   ```

3. **Rolling Update** (for minor changes):
   ```
   - Update 1 pod at a time
   - Wait for health check (30s)
   - Continue to next pod
   - Max unavailable: 1 pod
   ```

**Rollback Procedure**:
1. Detect issue (automated alerts or manual)
2. Trigger rollback: `kubectl rollout undo deployment/ttp-api`
3. Verify rollback success (health checks, smoke tests)
4. Post-mortem within 24 hours

### Configuration Management

**Environment Variables**:
```bash
# Application
APP_ENV=production
APP_VERSION=1.2.3
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@host:5432/ttpdb
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30

# Redis
REDIS_URL=redis://redis-cluster:6379/0
REDIS_MAX_CONNECTIONS=50

# S3
S3_BUCKET=ttp-texture-assets-prod
S3_REGION=us-east-1
S3_ENDPOINT=https://s3.amazonaws.com

# Security
JWT_ISSUER=https://auth.ttp.example.com
JWT_AUDIENCE=ttp-api
CORS_ORIGINS=https://ttp.example.com,https://www.ttp.example.com

# Observability
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
PROMETHEUS_PORT=9090
```

**Feature Flags** (LaunchDarkly / Unleash):
```json
{
  "new_search_algorithm": {
    "enabled": true,
    "rollout_percentage": 50,
    "user_targeting": ["beta_users"]
  },
  "ai_texture_generation": {
    "enabled": false,
    "environments": ["development", "staging"]
  },
  "maintenance_mode": {
    "enabled": false,
    "description": "Enable to put system in read-only mode"
  }
}
```

### Operational Runbooks

**Runbook: Scaling Up for High Traffic Event**:
```markdown
## Pre-Event (24h before)
1. Review capacity planning
2. Increase HPA max replicas: API (50→100), Workers (20→40)
3. Increase database connection pool: 20→50
4. Pre-warm CDN cache (popular assets)
5. Verify alerting thresholds
6. Schedule on-call coverage

## During Event
1. Monitor dashboards continuously
2. Watch error rates, latency metrics
3. Manual scaling if HPA insufficient
4. Disable non-critical background jobs
5. Increase log sampling (reduce verbosity)

## Post-Event (within 24h)
1. Scale down resources to normal levels
2. Review metrics for insights
3. Calculate cost impact
4. Update capacity planning
5. Post-mortem if incidents occurred
```

**Runbook: Database Maintenance Window**:
```markdown
## Preparation
1. Schedule maintenance window (low-traffic period)
2. Notify users 7 days in advance
3. Create database backup
4. Test restore procedure
5. Verify rollback plan

## Execution
1. Enable read-only mode in application
2. Wait for in-flight transactions to complete (max 60s)
3. Perform maintenance (e.g., schema migration, VACUUM FULL)
4. Run integrity checks
5. Disable read-only mode
6. Monitor for issues (30 minutes)

## Rollback (if needed)
1. Re-enable read-only mode
2. Restore from backup
3. Verify data consistency
4. Disable read-only mode
5. Investigate issue
```

### Cost Optimization

**Current Monthly Costs** (estimated for 50 TB, 10K users):
- Compute (EKS): $2,000
- Database (RDS): $1,500
- Storage (S3): $1,150 (50 TB at $0.023/GB)
- Data transfer: $4,500 (50 TB egress at $0.09/GB)
- CDN (CloudFront): $2,000
- Observability: $800
- **Total**: ~$12,000/month

**Optimization Strategies**:
1. CDN offloading: Reduce S3 egress by 90% → Save $4,000/month
2. Reserved instances: 1-year commitment → Save 30% on compute
3. S3 Intelligent-Tiering: Auto-move cold data to cheaper tiers
4. Compression: Enable Brotli/gzip → Reduce transfer by 60%
5. Database query optimization: Reduce IOPS costs
6. Spot instances for batch workloads: Save 70% on worker nodes

**Cost Monitoring**:
- Daily AWS Cost Explorer reports
- Per-service cost allocation tags
- Budget alerts at 80% and 100% thresholds
- Monthly cost review meetings

---

## Appendix

### Glossary

- **PBR**: Physically Based Rendering
- **HDR**: High Dynamic Range
- **LOD**: Level of Detail
- **HDRP**: High Definition Render Pipeline (Unity)
- **URP**: Universal Render Pipeline (Unity)
- **EXR**: OpenEXR file format
- **mTLS**: Mutual TLS
- **RBAC**: Role-Based Access Control
- **SLI**: Service Level Indicator
- **SLO**: Service Level Objective
- **SLA**: Service Level Agreement
- **RPO**: Recovery Point Objective
- **RTO**: Recovery Time Objective
- **SBOM**: Software Bill of Materials
- **SAST**: Static Application Security Testing
- **DAST**: Dynamic Application Security Testing

### References

- [Unity HDRP Documentation](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@latest)
- [PostgreSQL Best Practices](https://www.postgresql.org/docs/16/index.html)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/otel/)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)

### Change Log

| Version | Date       | Author | Changes |
|---------|------------|--------|---------|
| 1.0.0   | 2026-02-18 | Claude | Initial architecture document |

