# Security Scanning Integration - CI/CD Automation

**Status**: READY FOR DEPLOYMENT | **Date**: 2026-04-09

## Overview

This document provides comprehensive CI/CD pipeline integration for automated security scanning of dependencies, container images, and code. All scans enforce **ZERO critical/high vulnerabilities** policy.

## Security Scanning Tools

### Python Dependencies

- **pip-audit**: Official PyPA vulnerability scanner (OSV database)
- **safety**: Python dependency security scanner (Safety DB)
- **bandit**: Python code security linter (SAST)

### Node.js Dependencies

- **npm audit**: Official npm vulnerability scanner
- **audit-ci**: Automated audit with CI/CD integration

### Container Security

- **Trivy**: Comprehensive container/IaC scanner (Aqua Security)
- **Grype**: Vulnerability scanner for container images (Anchore)

### SAST (Static Application Security Testing)

- **Semgrep**: Fast, customizable SAST
- **CodeQL**: GitHub's semantic code analysis

## GitHub Actions Workflow

Create `.github/workflows/security-scan.yml`:

```yaml
name: Security Dependency Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:

    # Run weekly on Monday at 09:00 UTC

    - cron: '0 9 * * 1'
  workflow_dispatch: # Manual trigger

env:
  PYTHON_VERSION: '3.10'
  NODE_VERSION: '18'

jobs:
  python-security-scan:
    name: Python Dependencies Security
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write # For SARIF upload
    
    steps:

      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Install security scanning tools
        run: |
          pip install --upgrade pip
          pip install pip-audit safety bandit[toml]
      
      - name: Run pip-audit (OSV Database)
        id: pip-audit
        run: |
          pip-audit -r requirements.txt \
            --format json \
            --output pip-audit-report.json \
            || echo "vulnerabilities_found=true" >> $GITHUB_OUTPUT
          
          # Also generate SARIF for GitHub Security tab

          pip-audit -r requirements.txt \
            --format cyclonedx-json \
            --output pip-audit-sbom.json || true
        continue-on-error: true
      
      - name: Run Safety scan
        id: safety
        run: |
          safety scan \
            --json \
            --output safety-report.json \
            || echo "vulnerabilities_found=true" >> $GITHUB_OUTPUT
        continue-on-error: true
      
      - name: Run Bandit SAST
        run: |
          bandit -r src/ -f json -o bandit-report.json || true
          bandit -r src/ -f sarif -o bandit-report.sarif || true
      
      - name: Upload Bandit SARIF to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: bandit-report.sarif
          category: bandit-sast
      
      - name: Scan all microservices
        run: |
          echo "Scanning microservices..."
          FAILED_SERVICES=""
          for service in emergent-microservices/*/; do
            if [ -f "$service/requirements.txt" ]; then
              echo "Scanning $service"
              pip-audit -r "$service/requirements.txt" || FAILED_SERVICES="$FAILED_SERVICES $service"
            fi
          done
          
          if [ -n "$FAILED_SERVICES" ]; then
            echo "❌ Vulnerabilities found in: $FAILED_SERVICES"
            exit 1
          fi
      
      - name: Check for critical/high vulnerabilities
        if: steps.pip-audit.outputs.vulnerabilities_found == 'true'
        run: |
          echo "❌ SECURITY POLICY VIOLATION: Critical or High vulnerabilities detected!"
          echo "Review pip-audit-report.json and safety-report.json"
          cat pip-audit-report.json | jq '.dependencies[] | select(.vulns | length > 0)'
          exit 1
      
      - name: Upload security reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: python-security-reports
          path: |
            pip-audit-report.json
            safety-report.json
            bandit-report.json
            pip-audit-sbom.json
          retention-days: 90

  nodejs-security-scan:
    name: Node.js Dependencies Security
    runs-on: ubuntu-latest
    
    steps:

      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run npm audit
        id: npm-audit
        run: |
          npm audit --json > npm-audit-report.json || true
          
          # Check for critical/high

          CRITICAL=$(cat npm-audit-report.json | jq '.metadata.vulnerabilities.critical')
          HIGH=$(cat npm-audit-report.json | jq '.metadata.vulnerabilities.high')
          
          if [ "$CRITICAL" -gt 0 ] || [ "$HIGH" -gt 0 ]; then
            echo "❌ Found $CRITICAL critical and $HIGH high vulnerabilities"
            npm audit
            exit 1
          fi
          echo "✅ No critical or high vulnerabilities found"
      
      - name: Upload npm audit report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: nodejs-security-reports
          path: npm-audit-report.json
          retention-days: 90

  docker-security-scan:
    name: Docker Image Security
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    
    steps:

      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Build Docker image
        run: |
          docker build -t sovereign-substrate:${{ github.sha }} -f Dockerfile .
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: sovereign-substrate:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1' # Fail on critical/high
      
      - name: Upload Trivy SARIF to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: trivy-results.sarif
          category: trivy-container-scan
      
      - name: Run Trivy with JSON output
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: sovereign-substrate:${{ github.sha }}
          format: 'json'
          output: 'trivy-results.json'
      
      - name: Scan all microservice images
        run: |
          SERVICES=(
            "sovereign-data-vault"
            "ai-mutation-governance-firewall"
            "autonomous-compliance"
            "trust-graph-engine"
            "autonomous-incident-reflex-system"
            "autonomous-negotiation-agent"
            "verifiable-reality"
          )
          
          for service in "${SERVICES[@]}"; do
            echo "Building and scanning $service..."
            docker build -t "$service:${{ github.sha }}" \
              -f "emergent-microservices/$service/Dockerfile" \
              "emergent-microservices/$service/" || continue
            
            trivy image \
              --severity CRITICAL,HIGH \
              --exit-code 1 \
              "$service:${{ github.sha }}" || {
                echo "❌ Vulnerabilities found in $service"
                exit 1
              }
          done
      
      - name: Upload Trivy reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: docker-security-reports
          path: trivy-results.*
          retention-days: 90

  codeql-analysis:
    name: CodeQL SAST
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read
    
    steps:

      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: python, javascript
          queries: security-extended
      
      - name: Autobuild
        uses: github/codeql-action/autobuild@v3
      
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          category: codeql-sast

  semgrep-sast:
    name: Semgrep SAST
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read
    
    steps:

      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/python
            p/owasp-top-ten
            p/jwt
            p/dockerfile
          publishToken: ${{ secrets.SEMGREP_APP_TOKEN }}
          generateSarif: true
      
      - name: Upload Semgrep SARIF
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: semgrep.sarif
          category: semgrep-sast

  security-policy-check:
    name: Security Policy Enforcement
    needs: [python-security-scan, nodejs-security-scan, docker-security-scan]
    runs-on: ubuntu-latest
    if: always()
    
    steps:

      - name: Download all reports
        uses: actions/download-artifact@v4
      
      - name: Enforce zero critical/high policy
        run: |
          echo "🔒 SECURITY POLICY: Zero Critical/High Vulnerabilities"
          
          # Check Python

          if [ -f python-security-reports/pip-audit-report.json ]; then
            VULN_COUNT=$(cat python-security-reports/pip-audit-report.json | \
              jq '[.dependencies[].vulns[]] | length')
            
            if [ "$VULN_COUNT" -gt 0 ]; then
              echo "❌ POLICY VIOLATION: $VULN_COUNT Python vulnerabilities"
              exit 1
            fi
          fi
          
          # Check Node.js

          if [ -f nodejs-security-reports/npm-audit-report.json ]; then
            CRITICAL=$(cat nodejs-security-reports/npm-audit-report.json | \
              jq '.metadata.vulnerabilities.critical // 0')
            HIGH=$(cat nodejs-security-reports/npm-audit-report.json | \
              jq '.metadata.vulnerabilities.high // 0')
            
            if [ "$CRITICAL" -gt 0 ] || [ "$HIGH" -gt 0 ]; then
              echo "❌ POLICY VIOLATION: Critical=$CRITICAL High=$HIGH"
              exit 1
            fi
          fi
          
          echo "✅ POLICY COMPLIANT: Zero critical/high vulnerabilities"
```

## Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-yaml
      - id: detect-private-key
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.8
    hooks:
      - id: bandit
        args: ['-r', 'src/', '-ll']  # Low severity threshold

  - repo: https://github.com/returntocorp/semgrep
    rev: v1.66.2
    hooks:
      - id: semgrep
        args: ['--config', 'auto', '--error']

  - repo: local
    hooks:
      - id: pip-audit
        name: pip-audit
        entry: pip-audit
        language: system
        files: requirements.*\.txt$
        pass_filenames: false
        args: ['-r', 'requirements.txt']

      - id: npm-audit
        name: npm-audit
        entry: npm audit
        language: system
        files: package(-lock)?\.json$
        pass_filenames: false

```

Install hooks:
```bash
pip install pre-commit
pre-commit install
```

## Dependabot Configuration

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:

  # Python dependencies

  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "security"
    commit-message:
      prefix: "security"
      include: "scope"
    groups:
      security-updates:
        patterns:
          - "cryptography"
          - "pyjwt"
          - "python-jose"
          - "gunicorn"
          - "starlette"
          - "fastapi"
    # Auto-approve security patches
    allow:
      - dependency-type: "direct"
        update-type: "security"

  # Node.js dependencies

  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "security"

  # Docker base images

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    reviewers:
      - "security-team"
    labels:
      - "docker"
      - "security"

  # GitHub Actions

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    labels:
      - "ci-cd"
      - "security"

```

## Local Development Scripts

Create `scripts/security-check.sh`:

```bash
#!/bin/bash
set -e

echo "🔒 Running comprehensive security checks..."

# Python dependencies

echo "📦 Scanning Python dependencies..."
pip-audit -r requirements.txt || {
  echo "❌ Python vulnerabilities found!"
  exit 1
}

# Microservices

echo "🔧 Scanning microservices..."
for service in emergent-microservices/*/requirements.txt; do
  echo "  - Scanning $service"
  pip-audit -r "$service" || {
    echo "❌ Vulnerabilities in $service"
    exit 1
  }
done

# Node.js

if [ -f package.json ]; then
  echo "📦 Scanning Node.js dependencies..."
  npm audit --audit-level=high || {
    echo "❌ Node.js vulnerabilities found!"
    exit 1
  }
fi

# Code security (Bandit)

echo "🔍 Running SAST with Bandit..."
bandit -r src/ -ll || {
  echo "⚠️ Security issues found in code"
  exit 1
}

# Docker images (if Trivy installed)

if command -v trivy &> /dev/null; then
  echo "🐳 Scanning Docker images..."
  docker build -t security-check:latest -f Dockerfile .
  trivy image --severity CRITICAL,HIGH --exit-code 1 security-check:latest || {
    echo "❌ Docker image vulnerabilities found!"
    exit 1
  }
fi

echo "✅ All security checks passed!"
```

Make executable:
```bash
chmod +x scripts/security-check.sh
```

## Continuous Monitoring

### Security Dashboard

- **GitHub Security**: View all vulnerabilities at `https://github.com/{org}/{repo}/security`
- **Dependabot Alerts**: Auto-created issues for vulnerable dependencies
- **Code Scanning**: SARIF upload from Bandit, CodeQL, Semgrep

### Notification Channels

```yaml

# .github/workflows/security-notifications.yml

name: Security Notifications

on:
  schedule:

    - cron: '0 10 * * *' # Daily at 10:00 UTC

jobs:
  security-summary:
    runs-on: ubuntu-latest
    steps:

      - name: Get security alerts
        uses: actions/github-script@v7
        with:
          script: |
            const alerts = await github.rest.dependabot.listAlertsForRepo({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'open',
              severity: 'critical,high'
            });
            
            if (alerts.data.length > 0) {
              // Send to Slack/Teams/Email
              console.log(`⚠️ ${alerts.data.length} critical/high alerts`);
              // Add notification logic here
            }
```

## Security Metrics

Track these KPIs:

- **Time to Patch**: Critical <24h, High <72h
- **Vulnerability Density**: Vulns per 1000 LOC
- **MTTR (Mean Time to Remediate)**: Average patch time
- **Coverage**: % of dependencies scanned
- **False Positive Rate**: Manual review required

## Compliance & Reporting

### Weekly Security Report

```bash
#!/bin/bash

# scripts/weekly-security-report.sh

echo "# Weekly Security Report - $(date +%Y-%m-%d)"
echo ""
echo "## Python Dependencies"
pip-audit -r requirements.txt --format json | \
  jq '.dependencies | length' | \
  xargs -I {} echo "Total packages scanned: {}"

echo ""
echo "## Node.js Dependencies"
npm audit --json | \
  jq '.metadata.dependencies' | \
  xargs -I {} echo "Total packages scanned: {}"

echo ""
echo "## Docker Images"
trivy image --quiet sovereign-substrate:latest | \
  grep "Total:" || echo "No vulnerabilities found"
```

### Audit Trail

- All security scans logged to CI/CD artifacts (90-day retention)
- SARIF results uploaded to GitHub Security tab
- Dependency SBOMs generated for compliance

## Emergency Response

### Critical Vulnerability Protocol

1. **Detection**: Automated alerts via Dependabot/Security advisories
2. **Assessment**: Security team reviews CVSS, exploitability, impact
3. **Patching**: 
   - P0 (CVSS ≥9.0): Immediate patch + emergency deployment
   - P1 (CVSS ≥7.0): Patch within 72 hours
4. **Verification**: Re-run all security scans
5. **Communication**: Notify stakeholders via security bulletin

### Rollback Plan

```bash

# If patch causes regression

git revert <security-patch-commit>

# Mitigate with WAF rules or network restrictions

# Re-patch with alternative fix

```

## Summary

✅ **Automated Scanning**: Weekly + on every PR  
✅ **Zero Tolerance**: Critical/High vulnerabilities block deployment  
✅ **Comprehensive Coverage**: Python, Node.js, Docker, SAST  
✅ **Continuous Monitoring**: Dependabot + Security advisories  
✅ **Fast Response**: <24h critical patch SLA  

**Next Steps**:

1. Merge `.github/workflows/security-scan.yml`
2. Enable Dependabot alerts
3. Configure pre-commit hooks
4. Run initial scan: `./scripts/security-check.sh`
5. Monitor GitHub Security tab daily

---

**Maintained by**: Security Team  
**Last Updated**: 2026-04-09  
**Review Cadence**: Monthly
