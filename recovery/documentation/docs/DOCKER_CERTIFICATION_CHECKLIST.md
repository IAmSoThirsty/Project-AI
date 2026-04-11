# Docker Production Certification Checklist

**Sovereign-Governance-Substrate**  
**Print this page for sprint tracking**

---

## ☑️ DAY 1: CRITICAL SECURITY FIXES (8 hours)

### Task 1.1: SHA-256 Pin All Base Images (2 hours)

- [ ] Get SHA digests for all base images
- [ ] Update Dockerfile.sovereign (2 FROM statements)
- [ ] Update microservices/ai-mutation-governance-firewall/Dockerfile
- [ ] Update microservices/trust-graph-engine/Dockerfile
- [ ] Update microservices/sovereign-data-vault/Dockerfile
- [ ] Update microservices/autonomous-compliance/Dockerfile
- [ ] Update microservices/autonomous-incident-reflex-system/Dockerfile
- [ ] Update microservices/autonomous-negotiation-agent/Dockerfile
- [ ] Update microservices/verifiable-reality/Dockerfile
- [ ] Update microservices/i-believe-in-you/Dockerfile
- [ ] Verify: `grep -r "FROM.*@sha256:" . | wc -l` = 20+

**Owner:** _____________  **Due:** Day 1, 11:00 AM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 1.2: Add Non-Root User to Dockerfile.sovereign (1 hour)

- [ ] Add `RUN groupadd -r sovereign && useradd -r -g sovereign sovereign`
- [ ] Add `RUN chown -R sovereign:sovereign /app`
- [ ] Add `USER sovereign` before ENTRYPOINT
- [ ] Build: `docker build -f Dockerfile.sovereign -t sovereign:test .`
- [ ] Verify: `docker run --rm sovereign:test whoami` (expect: sovereign)

**Owner:** _____________  **Due:** Day 1, 12:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 1.3: Add Health Check to Dockerfile.sovereign (1 hour)

- [ ] Install curl in runtime stage
- [ ] Add HEALTHCHECK directive
- [ ] Add EXPOSE 8000
- [ ] Build and test
- [ ] Verify: Health check appears in `docker inspect`

**Owner:** _____________  **Due:** Day 1, 1:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 1.4: Make Security Scans Blocking (2 hours)

- [ ] Update `.github/workflows/tk8s-civilization-pipeline.yml`
- [ ] Add `severity: 'CRITICAL,HIGH'`
- [ ] Add `exit-code: '1'`
- [ ] Add `ignore-unfixed: false`
- [ ] Update `.github/workflows/project-ai-monolith.yml`
- [ ] Test with intentionally vulnerable package
- [ ] Commit changes

**Owner:** _____________  **Due:** Day 1, 3:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 1.5: Build and Validate All Images (2 hours)

- [ ] Build Dockerfile: `docker build -f Dockerfile -t project-ai:rc1 .`
- [ ] Build Dockerfile.sovereign: `docker build -f Dockerfile.sovereign -t sovereign:rc1 .`
- [ ] Build Dockerfile.test: `docker build -f Dockerfile.test -t test:rc1 .`
- [ ] Trivy scan project-ai:rc1 (0 CRITICAL/HIGH)
- [ ] Trivy scan sovereign:rc1 (0 CRITICAL/HIGH)
- [ ] Verify non-root users (all containers)
- [ ] Verify health checks (main + sovereign)

**Owner:** _____________  **Due:** Day 1, 5:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

## ☑️ DAY 2: IMAGE SIZE OPTIMIZATION (8 hours)

### Task 2.1: Dependency Audit (2 hours)

- [ ] Run pipdeptree on current image
- [ ] Generate package-sizes.txt
- [ ] Identify ML libraries (torch, tensorflow) - remove if unused
- [ ] Identify dev tools (pytest, black, ruff) - move to dev requirements
- [ ] Document findings in issue/ticket

**Owner:** _____________  **Due:** Day 2, 11:00 AM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 2.2: Create requirements-runtime.txt (1 hour)

- [ ] Copy requirements.txt to requirements-runtime.txt
- [ ] Remove test packages (pytest, pytest-asyncio, pytest-cov)
- [ ] Remove dev packages (black, flake8, mypy, ruff)
- [ ] Remove unused ML packages
- [ ] Update Dockerfile to use requirements-runtime.txt

**Owner:** _____________  **Due:** Day 2, 12:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 2.3: Externalize Data Directory (2 hours)

- [ ] Update Dockerfile COPY to only migrations/schemas
- [ ] Update docker-compose.yml with volume mounts
- [ ] Create volumes section in docker-compose.yml
- [ ] Test application startup with external volumes
- [ ] Document volume mount requirements

**Owner:** _____________  **Due:** Day 2, 2:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 2.4: Add Layer Cleanup Commands (2 hours)

- [ ] Add `rm -rf /wheels` after pip install
- [ ] Add `__pycache__` cleanup
- [ ] Add `.pyc` cleanup
- [ ] Add `tests/` directory removal
- [ ] Add `docs/` directory removal
- [ ] Test that application still works

**Owner:** _____________  **Due:** Day 2, 4:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 2.5: Build and Measure (1 hour)

- [ ] Rebuild: `docker build -f Dockerfile -t project-ai:optimized .`
- [ ] Measure size: `docker images | grep project-ai`
- [ ] Run docker history for layer breakdown
- [ ] Verify size < 500MB
- [ ] Document before/after metrics

**Owner:** _____________  **Due:** Day 2, 5:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

**Target:** Image size reduced from 1.12GB to <500MB ✅

---

## ☑️ DAY 3: PRODUCTION CONFIGURATION (8 hours)

### Task 3.1: Implement Graceful Shutdown (3 hours)

- [ ] Install tini in Dockerfile
- [ ] Update ENTRYPOINT to use tini
- [ ] Add signal handlers to launcher.py
- [ ] Add signal handlers to boot_sovereign.py
- [ ] Test graceful shutdown: `docker kill --signal=SIGTERM`
- [ ] Verify shutdown logs show "graceful shutdown"

**Owner:** _____________  **Due:** Day 3, 12:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 3.2: Add Resource Limits (2 hours)

- [ ] Add deploy.resources to project-ai service
- [ ] Add deploy.resources to all 8 microservices
- [ ] Add ulimits configuration
- [ ] Add stop_grace_period to all services
- [ ] Test with docker-compose up

**Owner:** _____________  **Due:** Day 3, 2:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 3.3: Fix Microservice Health Checks (2 hours)

- [ ] Update all microservices to use httpx (not requests)
- [ ] OR install curl and update health check
- [ ] Test health check: `docker run -d <service> && docker inspect`
- [ ] Verify all 8 microservices
- [ ] Document health check pattern

**Owner:** _____________  **Due:** Day 3, 4:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 3.4: Convert CMD to ENTRYPOINT (1 hour)

- [ ] Update Dockerfile main application
- [ ] Update all 8 microservice Dockerfiles
- [ ] Test command override: `docker run <image> --help`
- [ ] Verify default behavior unchanged

**Owner:** _____________  **Due:** Day 3, 5:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

## ☑️ DAY 4: STANDARDIZATION (6 hours)

### Task 4.1: Create Shared Base Image (3 hours)

- [ ] Create emergent-microservices/_common/Dockerfile.base
- [ ] Add common dependencies (fastapi, uvicorn, gunicorn)
- [ ] Build base image
- [ ] Push to registry
- [ ] Test base image

**Owner:** _____________  **Due:** Day 4, 12:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 4.2: Update Microservice Dockerfiles (2 hours)

- [ ] Update ai-mutation-governance-firewall
- [ ] Update trust-graph-engine
- [ ] Update sovereign-data-vault
- [ ] Update autonomous-compliance
- [ ] Update autonomous-incident-reflex-system
- [ ] Update autonomous-negotiation-agent
- [ ] Update verifiable-reality
- [ ] Update i-believe-in-you
- [ ] Build all and verify

**Owner:** _____________  **Due:** Day 4, 2:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 4.3: Document Build Process (1 hour)

- [ ] Create emergent-microservices/BUILD.md
- [ ] Document base image usage
- [ ] Document build order
- [ ] Add local development instructions
- [ ] Add production deployment reference

**Owner:** _____________  **Due:** Day 4, 3:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

## ☑️ DAY 5: VALIDATION & CERTIFICATION (4 hours)

### Task 5.1: Build Time Benchmarking (2 hours)

- [ ] Create scripts/benchmark-builds.sh
- [ ] Run no-cache builds (Dockerfile, Dockerfile.sovereign, Dockerfile.test)
- [ ] Run cached builds
- [ ] Measure image sizes
- [ ] Document results in build-benchmarks.txt
- [ ] Verify all builds < 5 minutes

**Owner:** _____________  **Due:** Day 5, 11:00 AM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 5.2: E2E Testing (1 hour)

- [ ] Create scripts/e2e-docker-test.sh
- [ ] Test docker-compose build
- [ ] Test docker-compose up
- [ ] Test all health endpoints (main + 8 microservices)
- [ ] Test graceful shutdown
- [ ] Verify all tests pass

**Owner:** _____________  **Due:** Day 5, 12:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 5.3: Security Validation (30 minutes)

- [ ] Create scripts/security-validation.sh
- [ ] Scan all images with Trivy
- [ ] Verify non-root users (all containers)
- [ ] Scan for secrets in layers
- [ ] Document results

**Owner:** _____________  **Due:** Day 5, 1:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

### Task 5.4: Production Certification (30 minutes)

- [ ] Update DOCKER_ARCHITECTURE_REPORT.md with final scores
- [ ] Document remediation summary
- [ ] Fill production certification checklist
- [ ] Get Security Team sign-off
- [ ] Get Platform Engineering sign-off
- [ ] Get DevOps Lead sign-off
- [ ] Get SRE Lead sign-off

**Owner:** _____________  **Due:** Day 5, 2:00 PM  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Blocked

---

## 📊 FINAL VALIDATION CHECKLIST

### Security ✅

- [ ] All base images SHA-256 pinned (10/10)
- [ ] All containers run as non-root (10/10)
- [ ] No secrets in image layers
- [ ] Trivy scans: CRITICAL=0, HIGH=0
- [ ] SBOM generated for all images
- [ ] Docker Content Trust enabled (optional)

### Performance ✅

- [ ] Main image size < 500MB
- [ ] Build time < 5 minutes (first build)
- [ ] Build time < 2 minutes (cached)
- [ ] Layer cache efficiency > 70%

### Reliability ✅

- [ ] Health checks application-aware (10/10)
- [ ] Graceful shutdown implemented (SIGTERM)
- [ ] Resource limits defined (all services)
- [ ] Multi-platform builds verified (amd64, arm64)

### Operational ✅

- [ ] Image tagging strategy documented
- [ ] Rollback procedure tested
- [ ] Monitoring metrics exposed (Prometheus)
- [ ] Logs structured (JSON format)

### Compliance ✅

- [ ] CIS Docker Benchmark 80%+ compliance
- [ ] SLSA Level 3 build provenance
- [ ] Dockerfile linting (Hadolint) passing
- [ ] All 8 microservices standardized

---

## 🎯 SUCCESS CRITERIA

**Production Readiness Score: 95/100** ✅

### Before Remediation

- Image Size: 1.12GB ❌
- SHA-256 Coverage: 30% ❌
- Security Score: 78/100 ⚠️
- Production Ready: NO ❌

### After Remediation

- Image Size: <500MB ✅
- SHA-256 Coverage: 100% ✅
- Security Score: 95/100 ✅
- Production Ready: YES ✅

---

## 📝 SIGN-OFF

**Security Team Lead**  
Name: ________________  
Signature: ________________  
Date: ________________

**Platform Engineering Lead**  
Name: ________________  
Signature: ________________  
Date: ________________

**DevOps Lead**  
Name: ________________  
Signature: ________________  
Date: ________________

**SRE Lead**  
Name: ________________  
Signature: ________________  
Date: ________________

---

**Certification Date:** ________________  
**Production Deployment Approved:** ☑️ YES | ☐ NO  
**Next Review Date:** ________________

---

**Document Version:** 1.0  
**Created:** 2026-01-09  
**Sprint Duration:** 5 days  
**Total Effort:** 32 engineering hours
