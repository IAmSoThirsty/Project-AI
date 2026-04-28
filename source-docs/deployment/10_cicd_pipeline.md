# CI/CD Pipeline and Automated Deployment

## Overview

Project-AI uses GitHub Actions for continuous integration and deployment, with automated testing, security scanning, multi-platform builds, Docker image publishing, and Kubernetes deployments. This document covers the complete CI/CD pipeline architecture, workflow files, and deployment automation.

## CI/CD Architecture

### Pipeline Stages

```
CI/CD Pipeline Flow/
├── 1. Code Quality (Pre-Build)
│   ├── Linting (Ruff, ESLint)
│   ├── Type Checking (mypy)
│   ├── Code Formatting (Black, Prettier)
│   └── Security Scanning (Bandit, npm audit)
├── 2. Testing
│   ├── Unit Tests (pytest, Jest)
│   ├── Integration Tests (pytest-integration)
│   ├── E2E Tests (Playwright)
│   └── Coverage Report (>80% required)
├── 3. Security Scanning
│   ├── Dependency Audit (pip-audit, npm audit)
│   ├── SAST (Bandit, CodeQL)
│   ├── Secret Detection (TruffleHog)
│   └── License Compliance (pip-licenses)
├── 4. Build
│   ├── Docker Images (multi-arch)
│   ├── Desktop Binaries (Windows, macOS, Linux)
│   ├── Android APKs (all ABIs)
│   └── Web Assets (React build)
├── 5. Image Scanning
│   ├── Vulnerability Scan (Trivy, Grype)
│   ├── SBOM Generation (Syft)
│   └── Image Signing (Cosign)
├── 6. Artifact Publishing
│   ├── Docker Registry (Docker Hub, ECR, ACR)
│   ├── GitHub Releases (binaries)
│   ├── NPM Registry (web packages)
│   └── Play Store (Android)
└── 7. Deployment
    ├── Development (auto-deploy on push)
    ├── Staging (auto-deploy on tag)
    ├── Production (manual approval)
    └── Rollback (automated on failure)
```

## GitHub Actions Workflows

### Main CI Pipeline

**Location**: `.github/workflows/ci.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:  # Manual trigger

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'
  JAVA_VERSION: '17'

jobs:
  # ===== CODE QUALITY =====
  code-quality:
    name: Code Quality Checks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Cache Python dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: ${{ runner.os }}-pip-
      
      - name: Install linting tools
        run: |
          pip install ruff black isort mypy bandit safety
      
      - name: Run Ruff (linter)
        run: ruff check . --output-format=github
      
      - name: Check code formatting (Black)
        run: black --check .
      
      - name: Check import sorting (isort)
        run: isort --check-only .
      
      - name: Type checking (mypy)
        run: mypy . --ignore-missing-imports --no-error-summary
        continue-on-error: true
      
      - name: Security scan (Bandit)
        run: mkdir -p test-artifacts && bandit -r src/ -f json -o test-artifacts/bandit-report.json
        continue-on-error: true
      
      - name: Upload Bandit results
        uses: actions/upload-artifact@v3
        with:
          name: bandit-report
          path: test-artifacts/bandit-report.json

  # ===== TESTING =====
  test-backend:
    name: Backend Tests (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run tests with coverage
        run: |
          pytest tests/ -v \
            --cov=. \
            --cov-report=xml \
            --cov-report=html \
            --cov-report=term \
            --cov-fail-under=80
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: backend-py${{ matrix.python-version }}
          name: backend-coverage
      
      - name: Upload coverage artifacts
        uses: actions/upload-artifact@v3
        with:
          name: coverage-report-py${{ matrix.python-version }}
          path: htmlcov/

  test-frontend:
    name: Frontend Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: web/frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd web/frontend
          npm ci
      
      - name: Run linter (ESLint)
        run: |
          cd web/frontend
          npm run lint
      
      - name: Run tests (Jest)
        run: |
          cd web/frontend
          npm run test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./web/frontend/coverage/coverage-final.json
          flags: frontend
          name: frontend-coverage

  # ===== SECURITY SCANNING =====
  security-scan:
    name: Security Scanning
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run TruffleHog (secret detection)
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD
      
      - name: Dependency audit (pip-audit)
        run: |
          pip install pip-audit
          pip-audit -r requirements.txt --desc --format json -o pip-audit-report.json
        continue-on-error: true
      
      - name: NPM audit
        run: |
          cd web/frontend
          npm audit --json > ../../npm-audit-report.json
        continue-on-error: true
      
      - name: Upload security reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            pip-audit-report.json
            npm-audit-report.json

  # ===== DOCKER BUILD =====
  docker-build:
    name: Build Docker Images
    runs-on: ubuntu-latest
    needs: [code-quality, test-backend]
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: projectai/desktop
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=projectai/desktop:buildcache
          cache-to: type=registry,ref=projectai/desktop:buildcache,mode=max
      
      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: projectai/desktop:${{ github.sha }}
          format: cyclonedx-json
          output-file: sbom.json
      
      - name: Upload SBOM
        uses: actions/upload-artifact@v3
        with:
          name: sbom
          path: sbom.json

  # ===== IMAGE SCANNING =====
  trivy-scan:
    name: Trivy Container Scan
    runs-on: ubuntu-latest
    needs: docker-build
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'projectai/desktop:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
      
      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Fail on critical vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'projectai/desktop:${{ github.sha }}'
          exit-code: '1'
          severity: 'CRITICAL'

  # ===== ANDROID BUILD =====
  android-build:
    name: Build Android APK
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: ${{ env.JAVA_VERSION }}
          distribution: 'temurin'
      
      - name: Cache Gradle dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
      
      - name: Build debug APK
        run: ./gradlew :legion_mini:assembleDebug
      
      - name: Build release APK
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew :legion_mini:assembleRelease
      
      - name: Upload APK artifacts
        uses: actions/upload-artifact@v3
        with:
          name: android-apks
          path: |
            android/legion_mini/build/outputs/apk/debug/*.apk
            android/legion_mini/build/outputs/apk/release/*.apk

  # ===== DESKTOP BUILD =====
  desktop-build:
    name: Build Desktop (${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        include:
          - os: ubuntu-latest
            artifact: linux
          - os: windows-latest
            artifact: windows
          - os: macos-latest
            artifact: macos
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: desktop/package-lock.json
      
      - name: Install dependencies
        run: |
          cd desktop
          npm install
      
      - name: Build desktop app
        run: |
          cd desktop
          npm run build
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: desktop-${{ matrix.artifact }}
          path: desktop/release/*

  # ===== DEPLOYMENT =====
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [docker-build, trivy-scan]
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging.projectai.com
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBECONFIG_STAGING }}
      
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/backend \
            backend=projectai/desktop:${{ github.sha }} \
            -n project-ai-staging
          kubectl rollout status deployment/backend -n project-ai-staging
      
      - name: Smoke test
        run: |
          curl -f https://staging.projectai.com/api/health || exit 1

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [docker-build, trivy-scan]
    if: startsWith(github.ref, 'refs/tags/v')
    environment:
      name: production
      url: https://projectai.com
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBECONFIG_PROD }}
      
      - name: Blue-Green Deployment
        run: |
          # Deploy to green environment
          kubectl apply -f k8s/prod/backend-green.yaml -n project-ai-prod
          kubectl wait --for=condition=available deployment/backend-green -n project-ai-prod --timeout=300s
          
          # Switch traffic to green
          kubectl patch service backend-service -n project-ai-prod \
            -p '{"spec":{"selector":{"version":"green"}}}'
          
          # Wait for traffic to stabilize
          sleep 60
          
          # Scale down blue environment
          kubectl scale deployment/backend-blue --replicas=0 -n project-ai-prod
      
      - name: Smoke test
        run: |
          curl -f https://projectai.com/api/health || exit 1
      
      - name: Rollback on failure
        if: failure()
        run: |
          # Switch back to blue
          kubectl patch service backend-service -n project-ai-prod \
            -p '{"spec":{"selector":{"version":"blue"}}}'
          kubectl scale deployment/backend-blue --replicas=3 -n project-ai-prod
```

## Deployment Strategies

### Rolling Update (Default)

**Configuration**:
```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Max 1 extra pod during update
      maxUnavailable: 0  # Always maintain full capacity
```

**Characteristics**:
- Zero downtime
- Gradual rollout
- Automatic rollback on failure
- Default Kubernetes strategy

### Blue-Green Deployment

**Blue Environment** (`k8s/prod/backend-blue.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: project-ai
      version: blue
  template:
    metadata:
      labels:
        app: project-ai
        version: blue
    spec:
      containers:
      - name: backend
        image: projectai/desktop:v1.0.0
```

**Green Environment** (`k8s/prod/backend-green.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: project-ai
      version: green
  template:
    metadata:
      labels:
        app: project-ai
        version: green
    spec:
      containers:
      - name: backend
        image: projectai/desktop:v1.1.0  # New version
```

**Service Selector Switch**:
```bash
# Current: blue (v1.0.0)
kubectl patch service backend-service \
  -p '{"spec":{"selector":{"version":"blue"}}}'

# Switch to: green (v1.1.0)
kubectl patch service backend-service \
  -p '{"spec":{"selector":{"version":"green"}}}'
```

**Advantages**:
- Instant rollback (switch selector back)
- Full testing before switch
- Zero downtime

**Disadvantages**:
- 2x resource usage (both environments running)

### Canary Deployment

**Canary Deployment** (10% traffic to new version):

```yaml
# Primary deployment (90% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-stable
spec:
  replicas: 9
  template:
    metadata:
      labels:
        app: project-ai
        track: stable
        version: v1.0.0

---
# Canary deployment (10% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-canary
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: project-ai
        track: canary
        version: v1.1.0

---
# Service routes to both
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: project-ai  # Matches both stable and canary
  ports:
  - port: 80
    targetPort: 8000
```

**Gradual Rollout** (with Flagger):

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: backend
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  progressDeadlineSeconds: 300
  service:
    port: 80
    targetPort: 8000
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m
```

## Artifact Publishing

### Docker Hub

**Automated Publishing** (included in ci.yml):

```yaml
- name: Log in to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    push: true
    tags: |
      projectai/desktop:latest
      projectai/desktop:v${{ github.ref_name }}
```

### GitHub Releases

**Create Release** (`.github/workflows/release.yml`):

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          path: artifacts/
      
      - name: Create checksums
        run: |
          cd artifacts
          sha256sum */* > checksums.txt
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            artifacts/**/*
            artifacts/checksums.txt
          body: |
            ## What's Changed
            - Full changelog: https://github.com/IAmSoThirsty/Project-AI/compare/v1.0.0...v1.1.0
            
            ## Downloads
            - Windows: `Project-AI-Setup-${{ github.ref_name }}.exe`
            - macOS: `Project-AI-${{ github.ref_name }}.dmg`
            - Linux: `Project-AI-${{ github.ref_name }}.AppImage`
            - Android: `legion-mini-${{ github.ref_name }}.apk`
          draft: false
          prerelease: false
```

## Monitoring and Alerting

### Slack Notifications

**Workflow** (`.github/workflows/notify.yml`):

```yaml
name: Deployment Notifications

on:
  workflow_run:
    workflows: ["CI/CD Pipeline"]
    types:
      - completed

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Send Slack notification
        uses: slackapi/slack-github-action@v1
        with:
          channel-id: 'C01234567'
          payload: |
            {
              "text": "Deployment ${{ github.workflow }} - ${{ job.status }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Deployment Status*: ${{ job.status }}\n*Environment*: ${{ github.ref_name }}\n*Commit*: <${{ github.event.head_commit.url }}|${{ github.sha }}>"
                  }
                }
              ]
            }
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

## Rollback Procedures

### Automated Rollback (on failure)

```yaml
- name: Deploy to production
  id: deploy
  run: |
    kubectl set image deployment/backend backend=projectai/desktop:${{ github.sha }}
    kubectl rollout status deployment/backend --timeout=300s

- name: Rollback on failure
  if: failure() && steps.deploy.conclusion == 'failure'
  run: |
    kubectl rollout undo deployment/backend
    kubectl rollout status deployment/backend
```

### Manual Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/backend -n project-ai-prod

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=3 -n project-ai-prod

# Check rollout history
kubectl rollout history deployment/backend -n project-ai-prod
```

## Environment Management

### GitHub Environments

**Configure in**: Settings → Environments

**Staging Environment**:
- Auto-deploy on push to `develop`
- Required reviewers: None
- Deployment branches: `develop`

**Production Environment**:
- Deploy on tags: `v*`
- Required reviewers: 2 team members
- Wait timer: 30 minutes
- Deployment branches: `main`

### Secrets Management

**GitHub Secrets** (Settings → Secrets):
```
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
KUBECONFIG_STAGING
KUBECONFIG_PROD
KEYSTORE_PASSWORD
KEY_PASSWORD
SLACK_BOT_TOKEN
```

## Performance Optimization

### Caching Strategies

**1. Dependency Caching**:
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

**2. Docker Layer Caching**:
```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=registry,ref=projectai/desktop:buildcache
    cache-to: type=registry,ref=projectai/desktop:buildcache,mode=max
```

**3. Artifact Reuse**:
```yaml
- uses: actions/download-artifact@v3
  with:
    name: test-results
    path: test-results/
```

### Parallel Jobs

```yaml
jobs:
  test-backend:
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
        os: [ubuntu-latest, windows-latest]
    # Runs 4 jobs in parallel (2 versions × 2 OSes)
```

## Related Documentation

- `01_docker_architecture.md` - Container builds
- `07_container_security.md` - Security scanning
- `09_kubernetes_orchestration.md` - Kubernetes deployment

## References

- **GitHub Actions**: https://docs.github.com/en/actions
- **Docker Build Push Action**: https://github.com/docker/build-push-action
- **Trivy Action**: https://github.com/aquasecurity/trivy-action
- **Kubernetes Deployment Strategies**: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
