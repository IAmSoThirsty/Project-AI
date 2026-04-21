# 05: CI/CD Pipeline Relationships

**Document**: GitHub Actions CI/CD Workflows  
**System**: Automated Testing, Matrix Builds, Security Scanning, Deployment  
**Related Systems**: Docker, Kubernetes, Release Automation, Desktop Packaging

---


## Navigation

**Location**: `relationships\deployment\05_cicd_pipelines.md`

**Parent**: [[relationships\deployment\README.md]]


## CI/CD Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS CI/CD PIPELINE                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────┐                         │
│  │      Trigger Events                │                         │
│  │                                    │                         │
│  │  • push (main, develop)            │                         │
│  │  • pull_request (any branch)       │                         │
│  │  • schedule (cron)                 │                         │
│  │  • workflow_dispatch (manual)      │                         │
│  │  • release (published)             │                         │
│  └──────────────┬─────────────────────┘                         │
│                 │                                                │
│                 ↓                                                │
│  ┌──────────────────────────────────────────────┐               │
│  │          Workflow: codex-deus-ultimate       │               │
│  │                                              │               │
│  │  Job 1: Lint                                │               │
│  │  ├─ ruff check .                            │               │
│  │  ├─ mypy src/                               │               │
│  │  └─ black --check src/                      │               │
│  │                                              │               │
│  │  Job 2: Security Scan                       │               │
│  │  ├─ bandit -r src/                          │               │
│  │  ├─ pip-audit                               │               │
│  │  └─ trivy fs .                              │               │
│  │                                              │               │
│  │  Job 3: Test (Matrix)                       │               │
│  │  ├─ Python 3.11                             │               │
│  │  ├─ Python 3.12                             │               │
│  │  └─ pytest tests/ --cov                     │               │
│  │                                              │               │
│  │  Job 4: Build Docker                        │               │
│  │  ├─ docker build -t projectai/backend:$SHA │               │
│  │  └─ docker push                             │               │
│  │                                              │               │
│  │  Job 5: Deploy (if main branch)            │               │
│  │  ├─ Deploy to Staging (auto)               │               │
│  │  └─ Deploy to Prod (manual approval)        │               │
│  └──────────────────────────────────────────────┘               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Dependency Graph

```
Trigger Event (push to main)
    ↓
Checkout Code
    ↓
┌───────────────────┬────────────────────┬──────────────────┐
│                   │                    │                  │
↓                   ↓                    ↓                  ↓
Lint Job      Security Job         Test Job          Build Job
│                   │                    │                  │
├─ ruff             ├─ bandit            ├─ pytest          ├─ docker build
├─ mypy             ├─ pip-audit         ├─ coverage       └─ docker push
└─ black            └─ trivy             └─ upload                │
│                   │                    │                        │
└───────────────────┴────────────────────┴────────────────────────┘
                            ↓
                    All Jobs Pass?
                            │
                ┌───────────┴───────────┐
                ↓                       ↓
            Yes (main)              No (PR)
                │                       │
                ↓                       └─→ Block Merge
        Deploy to Staging
                │
                ↓
        Smoke Tests Pass?
                │
                ↓
        Manual Approval Gate
                │
                ↓
        Deploy to Production
```

## Matrix Build Strategy

### Python Version Matrix
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
    os: [ubuntu-latest, windows-latest, macos-latest]
  fail-fast: false

steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v4
    with:
      python-version: ${{ matrix.python-version }}
  - run: pip install -r requirements.txt
  - run: pytest tests/
```

### Matrix Execution Flow
```
Matrix Configuration
    ↓ expands to
6 Parallel Jobs:
    ├─ ubuntu-latest + Python 3.11
    ├─ ubuntu-latest + Python 3.12
    ├─ windows-latest + Python 3.11
    ├─ windows-latest + Python 3.12
    ├─ macos-latest + Python 3.11
    └─ macos-latest + Python 3.12
        ↓ each runs
        - Setup Python
        - Install Dependencies
        - Run Tests
        ↓ aggregate results
        All Pass → Continue
        Any Fail → Block (fail-fast: false)
```

## Secret Management

### GitHub Secrets Flow
```
Repository Settings
    ↓ secrets
GitHub Secrets (encrypted at rest)
    ├─ DOCKER_HUB_USER
    ├─ DOCKER_HUB_TOKEN
    ├─ OPENAI_API_KEY (for tests)
    ├─ KUBECONFIG (base64)
    └─ VAULT_TOKEN
        ↓ accessed in workflow
        ${{ secrets.DOCKER_HUB_TOKEN }}
        ↓ injected as
        Environment Variable (masked in logs)
        ↓ used by
        Docker Login, kubectl, deployment scripts
        ↓ never exposed
        Logs show: ***
```

### Environment-Specific Secrets
```
Environments:
    ├─ development
    │   └─ Secrets: DEV_DB_URL, DEV_API_KEY
    ├─ staging
    │   └─ Secrets: STAGING_DB_URL, STAGING_API_KEY
    └─ production
        └─ Secrets: PROD_DB_URL, PROD_API_KEY
            ↓ selected via
            environment: production
            ↓ requires
            Manual Approval (protection rules)
```

## Caching Strategy

### Dependency Caching
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

### Cache Hit/Miss Flow
```
Action: Restore Cache
    ↓ generates key
    linux-pip-abc123 (hash of requirements.txt)
    ↓ searches
    GitHub Cache Storage
        ├─→ Cache Hit (exact match)
        │   ↓ restores
        │   ~/.cache/pip from cache
        │   ↓ skips
        │   pip download (saves 2-3 min)
        │
        └─→ Cache Miss
            ↓ fallback to
            Restore-keys: linux-pip-
            ↓ partial restore
            Some packages cached
            ↓ downloads
            Only new/updated packages
            ↓ saves cache
            For next run
```

### Docker Layer Caching
```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and Push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: projectai/backend:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Artifact Management

### Upload/Download Flow
```
Build Job
    ↓ creates
    Artifacts:
        ├─ dist/ (Python packages)
        ├─ coverage.xml (test coverage)
        └─ trivy-report.sarif (security scan)
    ↓ uploads
    actions/upload-artifact@v3
    ↓ stores
    GitHub Artifacts (90 day retention)
        ↓ accessible by
        Deploy Job
        ↓ downloads
        actions/download-artifact@v3
        ↓ uses
        Artifacts for deployment
```

### SARIF Upload (Security)
```
Bandit Security Scan
    ↓ generates
    bandit-report.sarif
    ↓ uploads
    github/codeql-action/upload-sarif@v2
    ↓ processes
    Security Alerts
    ↓ displays in
    GitHub Security Tab
        ↓ creates
        Security Alerts (if vulnerabilities)
        ↓ notifies
        CODEOWNERS
```

## Branch Protection Rules

```
Branch: main
    ├─ Require pull request reviews (1 approver)
    ├─ Require status checks to pass:
    │   ├─ Lint (ruff, mypy)
    │   ├─ Security (bandit, trivy)
    │   ├─ Tests (Python 3.11, 3.12)
    │   └─ Build (Docker)
    ├─ Require signed commits
    ├─ Require linear history
    └─ Include administrators (no bypass)
        ↓ enforces
        All PRs must pass CI before merge
```

## Deployment Workflows

### Staging Deployment
```yaml
deploy-staging:
  if: github.ref == 'refs/heads/main'
  needs: [lint, security, test, build]
  runs-on: ubuntu-latest
  environment: staging
  steps:
    - name: Deploy to K8s Staging
      run: |
        echo "${{ secrets.KUBECONFIG_STAGING }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
        kubectl set image deployment/project-ai \
          backend=projectai/backend:${{ github.sha }} \
          -n staging
        kubectl rollout status deployment/project-ai -n staging
```

### Production Deployment
```yaml
deploy-production:
  needs: deploy-staging
  runs-on: ubuntu-latest
  environment:
    name: production
    url: https://projectai.com
  steps:
    - name: Manual Approval Required
      # Configured in GitHub Environment settings
      
    - name: Blue-Green Deploy
      run: |
        # Deploy to green environment
        helm upgrade project-ai ./helm/project-ai \
          --namespace production \
          --set image.tag=${{ github.sha }} \
          --set environment=green \
          --wait
        
        # Run smoke tests
        ./scripts/smoke-tests.sh production-green
        
        # Switch traffic to green
        kubectl patch service project-ai \
          -p '{"spec":{"selector":{"version":"green"}}}' \
          -n production
```

## Scheduled Workflows

### Dependency Update (Weekly)
```yaml
name: Dependency Update
on:
  schedule:
    - cron: '0 2 * * MON'  # Every Monday 2 AM UTC
  workflow_dispatch:

jobs:
  update-deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Update Python Dependencies
        run: |
          pip install pip-tools
          pip-compile requirements.in > requirements.txt
      
      - name: Update npm Dependencies
        run: |
          cd web/frontend
          npm update
          npm audit fix
      
      - name: Create PR
        uses: peter-evans/create-pull-request@v5
        with:
          title: "chore: Update dependencies"
          branch: deps/automated-update
          labels: dependencies,automated
```

### Security Scan (Daily)
```yaml
name: Security Scan
on:
  schedule:
    - cron: '0 1 * * *'  # Daily 1 AM UTC

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy
        run: |
          docker run --rm -v $PWD:/src aquasec/trivy:latest \
            fs /src --severity CRITICAL,HIGH
      
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r src/ -f sarif -o bandit-report.sarif
      
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: bandit-report.sarif
```

## Workflow Reusability

### Reusable Workflow (Caller)
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  workflow_dispatch:
    inputs:
      environment:
        required: true
        type: choice
        options: [staging, production]

jobs:
  deploy:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: ${{ inputs.environment }}
    secrets: inherit
```

### Reusable Workflow (Callee)
```yaml
# .github/workflows/reusable-deploy.yml
name: Reusable Deploy
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
    secrets:
      KUBECONFIG:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to K8s
        run: |
          kubectl set image deployment/project-ai \
            backend=projectai/backend:${{ github.sha }}
```

## Notification Integration

### Slack Notifications
```yaml
- name: Notify Slack on Failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "❌ CI Pipeline Failed",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Workflow*: ${{ github.workflow }}\n*Branch*: ${{ github.ref }}\n*Commit*: ${{ github.sha }}"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Performance Optimization

### Conditional Job Execution
```yaml
test-frontend:
  if: contains(github.event.head_commit.modified, 'web/frontend/')
  runs-on: ubuntu-latest
  steps:
    - run: npm test

test-backend:
  if: contains(github.event.head_commit.modified, 'src/')
  runs-on: ubuntu-latest
  steps:
    - run: pytest tests/
```

### Parallel Job Execution
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    # runs in parallel with test
    
  test:
    runs-on: ubuntu-latest
    # runs in parallel with lint
    
  deploy:
    needs: [lint, test]
    # waits for both lint and test
```

## Related Systems

- `02_docker_relationships.md` - Docker builds in CI
- `03_kubernetes_orchestration.md` - K8s deployments
- `06_release_automation.md` - GitHub Release workflows
- `10_deployment_pipeline_maps.md` - Full pipeline visualization

---

**Status**: ✅ Complete  
**Coverage**: GitHub Actions workflows, matrix builds, security scanning, deployment automation  
**Key Workflows**: codex-deus-ultimate.yml, security scans, scheduled updates
