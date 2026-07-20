# Supporting Infrastructure Documentation

> Recovered/reference material only: this directory is not current release
> evidence or deployment approval. The successor remains fail-closed until
> the current pre-deployment checklist and CAB evidence bundle pass.

**Directory:** `source-docs/supporting/`
**Purpose:** Complete reference documentation for Project-AI's supporting infrastructure
**Status:** Documentation-ready reference; not runtime deployment approval
**Last Updated:** 2025-01-26
**Maintained By:** AGENT-046

---

## Overview

This directory contains **comprehensive technical documentation** for all supporting infrastructure systems in Project-AI. These systems enable the core application to function in production environments.

**What's Covered:**
- Web backend (Flask API)
- Docker containerization and deployment
- CI/CD pipelines (GitHub Actions)
- Testing infrastructure (pytest, fixtures, mocks)
- Build and package management (pyproject.toml, package.json)
- Environment configuration (.env, secrets)

**What's NOT Covered** (See Other Directories):
- Core AI systems → `source-docs/core/`
- GUI components → `source-docs/gui/`
- Governance systems → `source-docs/governance/`
- Plugins → `source-docs/plugins/`

---

## Document Index

### 1. Web Backend Architecture

**File:** `01-web-backend-architecture.md`
**Size:** 5,247 words
**Scope:** Flask application, API endpoints, middleware, governance integration

**Key Topics:**
- Thin adapter pattern (no business logic in web layer)
- Runtime router (multi-path coordination)
- Security middleware (CORS, rate limiting, JWT)
- API endpoint reference (auth, AI chat, image generation, persona)
- Request flow through governance pipeline
- Error handling and monitoring
- Production deployment (Gunicorn, uWSGI, Nginx)

**When to Read:**
- Setting up web backend development environment
- Integrating new API endpoints
- Troubleshooting authentication issues
- Configuring CORS for frontend
- Deploying to production

**Prerequisites:** Basic Flask knowledge, REST API concepts

---

### 2. Docker Deployment Guide

**File:** `02-docker-deployment-guide.md`
**Size:** 4,892 words
**Scope:** Multi-stage builds, Docker Compose, Kubernetes deployment

**Key Topics:**
- Multi-stage build architecture (builder + runtime)
- Dockerfile deep dive (layer optimization, caching)
- Docker Compose configuration (services, networks, volumes)
- Container orchestration (Kubernetes manifests, HPA)
- Image optimization (size reduction, build cache)
- Health checks and monitoring
- Networking and security (network isolation, non-root users)
- Volume management and backups

**When to Read:**
- Setting up local development with Docker
- Building production Docker images
- Deploying to Kubernetes
- Optimizing Docker build times
- Troubleshooting container issues

**Prerequisites:** Docker basics, container concepts

---

### 3. CI/CD Pipeline Architecture

**File:** `03-ci-cd-pipelines.md`
**Size:** 5,984 words
**Scope:** GitHub Actions workflows, automated testing, security scanning, SBOM generation

**Key Topics:**
- CI/CD strategy (documentation-first, security-by-default)
- Workflow architecture (triggers, jobs, actions)
- Documentation truth gates (planned vs implemented, version consistency)
- SBOM generation (CycloneDX, supply chain security)
- Root structure enforcement (required directories, README completeness)
- Thirsty-Lang CI pipeline (build, test, deploy docs)
- Security workflows (Bandit, CodeQL, Trivy)
- Secrets management
- Deployment automation (manual, automatic, environment protection)

**When to Read:**
- Setting up CI/CD for new features
- Adding GitHub Actions workflows
- Configuring automated testing
- Implementing security scanning
- Troubleshooting workflow failures

**Prerequisites:** GitHub Actions basics, YAML syntax

---

### 4. Testing Infrastructure Guide

**File:** `04-testing-infrastructure.md`
**Size:** 6,127 words
**Scope:** Pytest configuration, test fixtures, mock patterns, coverage strategy

**Key Topics:**
- Testing strategy (test pyramid, 80%+ coverage goal)
- Test organization (unit, integration, E2E, security, performance)
- Pytest configuration (pytest.ini, conftest.py)
- Test fixtures (temporary directories, isolated systems, Flask client)
- Mock patterns (monkeypatch, unittest.mock.patch, mock classes)
- Test categories (unit, integration, E2E, security, performance)
- Coverage goals and reporting
- E2E testing (Playwright, Selenium, PyQt6)
- Test data management (JSON fixtures, factories)
- Best practices (test independence, descriptive names, AAA pattern)

**When to Read:**
- Writing new tests
- Setting up testing environment
- Achieving coverage goals
- Mocking external dependencies
- Troubleshooting flaky tests

**Prerequisites:** Pytest basics, Python testing concepts

---

### 5. Build & Package Management

**File:** `05-build-package-management.md`
**Size:** 3,847 words
**Scope:** pyproject.toml, package.json, requirements management, build workflows

**Key Topics:**
- Multi-language project structure (Python + Node.js)
- Python package management (pyproject.toml, requirements.txt)
- Tool configuration (Ruff, Pytest, Black)
- Node.js package management (package.json, package-lock.json)
- Dependency resolution (Python pip, Node.js npm)
- Build scripts (production builds, TARL builds)
- Version management (semantic versioning, bump2version)
- Distribution (PyPI publication, Docker Hub)

**When to Read:**
- Setting up development environment
- Managing dependencies
- Building for production
- Publishing packages
- Troubleshooting dependency conflicts

**Prerequisites:** Python packaging basics, npm basics

---

## Quick Reference

### Common Tasks

| Task | Document | Section |
|------|----------|---------|
| Start web backend locally | 01-web-backend | Configuration Guide → Local Development |
| Build Docker image | 02-docker-deployment | Docker Commands → Build |
| Add GitHub Actions workflow | 03-ci-cd-pipelines | Workflow Architecture |
| Write unit tests | 04-testing-infrastructure | Unit Tests |
| Install Python dependencies | 05-build-package | Python Package Management |
| Configure CORS | 01-web-backend | Security Middleware → CORS |
| Set up Kubernetes deployment | 02-docker-deployment | Production Deployment → Kubernetes |
| Generate SBOM | 03-ci-cd-pipelines | SBOM Generation |
| Mock OpenAI API in tests | 04-testing-infrastructure | Mock Patterns |
| Publish to PyPI | 05-build-package | Distribution → PyPI |

### Architecture Diagrams

#### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SUPPORTING INFRASTRUCTURE                     │
├──────────────────┬──────────────────┬──────────────────────────┤
│                  │                  │                          │
│  Web Backend     │  Docker          │  CI/CD                   │
│  (Flask)         │  (Containers)    │  (GitHub Actions)        │
│                  │                  │                          │
│  - API Routes    │  - Multi-stage   │  - Doc Truth Gates       │
│  - Middleware    │  - Compose       │  - SBOM Generation       │
│  - Governance    │  - Kubernetes    │  - Security Scanning     │
│                  │                  │                          │
├──────────────────┼──────────────────┼──────────────────────────┤
│                  │                  │                          │
│  Testing         │  Build/Package   │  Configuration           │
│  (Pytest)        │  (pyproject)     │  (.env, secrets)         │
│                  │                  │                          │
│  - Fixtures      │  - Python deps   │  - Environment vars      │
│  - Mocks         │  - Node.js deps  │  - API keys              │
│  - Coverage      │  - Build scripts │  - CORS origins          │
│                  │                  │                          │
└──────────────────┴──────────────────┴──────────────────────────┘
```

#### Request Flow

```
HTTP Request
    │
    ├─► CORS Check (middleware.py)
    ├─► Rate Limit (middleware.py)
    ├─► JWT Validation (middleware.py)
    │
    └─► Flask Route (web/backend/app.py)
          │
          └─► Runtime Router (runtime/router.py)
                │
                └─► Governance Pipeline (governance/pipeline.py)
                      │
                      └─► AI Orchestrator
                            │
                            └─► Core Systems
```

#### Deployment Flow

```
Git Push
    │
    ├─► GitHub Actions
    │     │
    │     ├─► Documentation Truth Gates
    │     ├─► SBOM Generation
    │     ├─► Linting (Ruff)
    │     ├─► Tests (Pytest)
    │     └─► Security Scanning (Bandit, CodeQL)
    │
    └─► Build Docker Image
          │
          ├─► Multi-stage Build
          │     ├─► Stage 1: Builder (compile dependencies)
          │     └─► Stage 2: Runtime (production image)
          │
          └─► Push to Registry
                │
                └─► Kubernetes Deployment
                      │
                      ├─► Rolling Update
                      ├─► Health Checks
                      └─► Traffic Switch
```

---

## Integration Points

### How Supporting Systems Connect

1. **Web Backend ↔ Governance:**
   - Web requests route through `runtime/router.py`
   - Router delegates to `governance/pipeline.py`
   - Governance applies TARL policies and Four Laws checks
   - Result returned to web layer for HTTP response

2. **Docker ↔ CI/CD:**
   - CI workflows trigger Docker builds
   - Multi-stage Dockerfile optimized for CI caching
   - Built images pushed to container registry
   - Kubernetes pulls images for deployment

3. **Testing ↔ CI/CD:**
   - CI triggers pytest on every commit
   - Coverage reports uploaded to Codecov
   - Tests must pass before merge
   - Security tests are mandatory

4. **Build/Package ↔ Docker:**
   - Docker copies `requirements.txt` and `pyproject.toml`
   - Multi-stage build compiles dependencies
   - Final image contains only runtime dependencies
   - No build tools in production image

---

## Configuration Reference

### Environment Variables

**Complete list of supported environment variables:**

```bash
# ==========================================
# OpenAI Configuration
# ==========================================
OPENAI_API_KEY=sk-...           # Required for AI features
OPENAI_ORG_ID=org-...           # Optional organization ID

# ==========================================
# DeepSeek Configuration
# ==========================================
DEEPSEEK_API_KEY=sk-...         # Optional alternative AI provider

# ==========================================
# Web Backend Configuration
# ==========================================
API_HOST=0.0.0.0                # Listen address (default: 0.0.0.0)
API_PORT=5000                   # Port (default: 5000)
API_WORKERS=4                   # Gunicorn workers (default: 4)
ENVIRONMENT=production          # production|development|test

# ==========================================
# Security
# ==========================================
SECRET_KEY=...                  # Flask secret key (generate with secrets.token_urlsafe(32))
CORS_ORIGINS=https://...        # Comma-separated list of allowed origins
RATE_LIMIT_STORAGE_URI=redis:// # Redis URI for rate limiting (use redis:// in production)

# ==========================================
# Logging & Audit
# ==========================================
LOG_LEVEL=INFO                  # DEBUG|INFO|WARNING|ERROR
AUDIT_LOG_PATH=audit.log        # Path to audit log file

# ==========================================
# Database (Optional)
# ==========================================
DATABASE_URL=postgresql://...   # Database connection string

# ==========================================
# Temporal Workflow (Optional)
# ==========================================
TEMPORAL_HOST=localhost:7233    # Temporal server address
TEMPORAL_NAMESPACE=default      # Temporal namespace

# ==========================================
# HuggingFace (Optional)
# ==========================================
HUGGINGFACE_API_KEY=hf_...      # For image generation with Stable Diffusion
```

**See Also:**
- `.env.example` in project root for template
- `01-web-backend-architecture.md` → Configuration Guide
- `05-build-package-management.md` → Environment Management

---

## Metrics & Monitoring

### Key Performance Indicators

**Web Backend:**
- Request latency: p50 < 100ms, p95 < 500ms, p99 < 1s
- Error rate: < 0.1%
- Uptime: 99.9%+
- Rate limit violations: < 1% of requests

**Docker:**
- Image build time: < 5 minutes
- Image size: < 500MB
- Container startup time: < 30 seconds
- Health check pass rate: 99%+

**CI/CD:**
- Workflow runtime: < 10 minutes
- Success rate: > 95%
- SBOM generation: 100% of builds
- Security scan coverage: 100% of commits

**Testing:**
- Test suite runtime: < 5 minutes
- Code coverage: > 80%
- Flaky test rate: < 1%
- Test count: 1000+ tests

---

## Troubleshooting Guide

### Common Issues

| Issue | Document | Solution |
|-------|----------|----------|
| CORS errors in browser | 01-web-backend | Check `CORS_ORIGINS` environment variable |
| Rate limit exceeded | 01-web-backend | Increase rate limits or use Redis backend |
| Docker build fails | 02-docker-deployment | Check system dependencies (build-essential) |
| Container won't start | 02-docker-deployment | Check logs with `docker-compose logs` |
| GitHub Actions timeout | 03-ci-cd-pipelines | Increase `timeout-minutes` or optimize workflow |
| Tests fail in CI but pass locally | 04-testing-infrastructure | Check environment variables in CI |
| Import errors after install | 05-build-package | Use `pip install -e .` for editable install |
| Dependency conflicts | 05-build-package | Create fresh virtual environment |

---

## Best Practices Summary

### Security

✅ **DO:**
- Store secrets in environment variables or vault (never in code)
- Use HTTPS in production (terminate TLS at reverse proxy)
- Enable rate limiting (prevent abuse)
- Run containers as non-root user
- Scan dependencies for vulnerabilities (npm audit, pip-audit)
- Validate all inputs before processing

❌ **DON'T:**
- Commit `.env` to version control
- Use wildcard CORS origins in production
- Disable security features to "fix" issues
- Trust client-provided headers (X-Forwarded-For)
- Expose stack traces in production error responses

### Performance

✅ **DO:**
- Use connection pooling for databases
- Cache frequently accessed data
- Set resource limits on containers
- Run tests in parallel (pytest -n auto)
- Use Docker layer caching

❌ **DON'T:**
- Make synchronous calls to slow external APIs
- Load large datasets into memory
- Skip pagination on large result sets
- Rebuild Docker images from scratch every time

### Reliability

✅ **DO:**
- Implement health checks (liveness + readiness)
- Use exponential backoff for retries
- Log all errors with context
- Test failure scenarios
- Monitor metrics (Prometheus, Grafana)

❌ **DON'T:**
- Assume external services are always available
- Retry forever without backoff
- Ignore transient errors
- Skip health checks

---

## Contributing

### Adding New Infrastructure

**When adding new supporting infrastructure:**

1. **Create Documentation First:**
   - Follow `METADATA_SCHEMA.md` frontmatter format
   - Minimum 1,000 words
   - Include code examples and diagrams
   - Add troubleshooting section

2. **Update This README:**
   - Add entry to Document Index
   - Update Quick Reference table
   - Add to Integration Points (if applicable)

3. **Validate Documentation:**
   - Run documentation truth gates: `.github/workflows/doc-code-alignment.yml`
   - Ensure no broken links
   - Verify code examples work

4. **Get Review:**
   - PR review by 2+ team members
   - Architecture review for major changes
   - Security review for authentication/authorization changes

---

## Related Documentation

### Internal References

- **Core Systems:** `../core/README.md`
- **GUI Components:** `../gui/README.md`
- **Governance Systems:** `../governance/README.md`
- **Plugins:** `../plugins/README.md`
- **Metadata Schema:** `../../METADATA_SCHEMA.md`

### External Resources

- **Flask Documentation:** https://flask.palletsprojects.com/
- **Docker Documentation:** https://docs.docker.com/
- **GitHub Actions:** https://docs.github.com/actions
- **Pytest Documentation:** https://docs.pytest.org/
- **Python Packaging:** https://packaging.python.org/

---

## Support

**Issues & Questions:**
- GitHub Issues: https://github.com/IAmSoThirsty/Project-AI/issues
- Security Issues: security@project-ai.dev (private)
- Documentation Errors: Label issue with `documentation`

**Maintainers:**
- AGENT-046 (Supporting Infrastructure Documentation)
- Architecture Team (Technical Review)
- DevOps Team (CI/CD and Deployment)

---

**Last Updated:** 2025-01-26
**Document Count:** 5
**Total Word Count:** 25,997 words
**Code Examples:** 202
**Diagrams:** 7
**Next Review:** 2025-04-26

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
