<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / security-automation.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / security-automation.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Security Automation Procedures

## Overview

This document outlines comprehensive security automation procedures integrated into the Cerberus CI/CD pipeline. Security automation ensures continuous monitoring, testing, and enforcement of security policies throughout the development lifecycle without manual intervention bottlenecks.

## Table of Contents

1. [Automated Testing](#automated-testing)
2. [SAST/DAST/SCA Integration](#sastdastsca-integration)
3. [Secret Scanning](#secret-scanning)
4. [Dependency Updates](#dependency-updates)
5. [Automated Incident Response](#automated-incident-response)
6. [GitHub Actions Workflows](#github-actions-workflows)
7. [Monitoring and Alerting](#monitoring-and-alerting)

---

## Automated Testing

### Security Test Integration

Security testing is integrated into every pull request and commit to ensure vulnerabilities are detected early.

#### Unit Security Tests

Automated unit tests verify security module functionality:

```python
# tests/security/test_authentication.py
import pytest
from unittest.mock import patch, MagicMock
from cerberus.security.authentication import (
    AuthenticationManager,
    PasswordValidator,
    MFAHandler
)

class TestAuthenticationSecurity:
    """Test authentication security controls"""
    
    def test_password_validation_complexity(self):
        """Verify password complexity requirements"""
        validator = PasswordValidator()
        
        # Test weak passwords are rejected
        weak_passwords = [
            "123456",
            "password",
            "abc123",
            "qwerty"
        ]
        
        for pwd in weak_passwords:
            assert not validator.is_valid(pwd), f"Weak password accepted: {pwd}"
        
        # Test strong passwords are accepted
        strong_password = "SecureP@ssw0rd2024!"
        assert validator.is_valid(strong_password)
    
    def test_password_hashing_security(self):
        """Verify passwords are properly hashed"""
        auth = AuthenticationManager()
        password = "TestPassword123!"
        
        hashed1 = auth.hash_password(password)
        hashed2 = auth.hash_password(password)
        
        # Hashes should be different (salt included)
        assert hashed1 != hashed2
        
        # Both should verify correctly
        assert auth.verify_password(password, hashed1)
        assert auth.verify_password(password, hashed2)
    
    def test_mfa_token_validation(self):
        """Verify MFA token validation"""
        mfa = MFAHandler()
        user_secret = mfa.generate_secret("user123")
        
        # Valid token should pass
        valid_token = mfa.generate_totp(user_secret)
        assert mfa.verify_totp(user_secret, valid_token)
        
        # Invalid token should fail
        assert not mfa.verify_totp(user_secret, "000000")
        
        # Expired tokens should fail
        import time
        time.sleep(31)  # TOTP expires after 30 seconds
        assert not mfa.verify_totp(user_secret, valid_token)
    
    def test_session_timeout(self):
        """Verify session timeout enforcement"""
        auth = AuthenticationManager()
        session = auth.create_session("user123")
        
        # Session should be valid initially
        assert auth.is_session_valid(session)
        
        # After timeout, session should be invalid
        with patch('time.time', return_value=time.time() + 3601):
            assert not auth.is_session_valid(session)
    
    def test_brute_force_protection(self):
        """Verify brute force attack protection"""
        auth = AuthenticationManager(max_attempts=3, lockout_duration=300)
        
        # Multiple failed attempts should trigger lockout
        for _ in range(3):
            auth.handle_failed_login("user123")
        
        # Account should be locked
        assert auth.is_account_locked("user123")

class TestAuthorizationSecurity:
    """Test authorization controls"""
    
    def test_role_based_access_control(self):
        """Verify RBAC enforcement"""
        from cerberus.security.authorization import AuthorizationManager
        
        authz = AuthorizationManager()
        
        # Admin role should have full permissions
        admin_perms = authz.get_role_permissions("admin")
        assert "delete_user" in admin_perms
        assert "delete_system" in admin_perms
        
        # User role should have limited permissions
        user_perms = authz.get_role_permissions("user")
        assert "delete_user" not in user_perms
        assert "read_profile" in user_perms
    
    def test_attribute_based_access_control(self):
        """Verify ABAC enforcement"""
        from cerberus.security.authorization import ABACEngine
        
        abac = ABACEngine()
        
        # Define policy: only engineers can access /api/internal
        policy = {
            "resource": "/api/internal",
            "attributes": {"department": "engineering"},
            "action": "read",
            "effect": "allow"
        }
        
        abac.add_policy(policy)
        
        # Engineer should have access
        assert abac.evaluate(
            resource="/api/internal",
            user_attrs={"department": "engineering"},
            action="read"
        )
        
        # Marketing should not have access
        assert not abac.evaluate(
            resource="/api/internal",
            user_attrs={"department": "marketing"},
            action="read"
        )
```

#### Integration Security Tests

```python
# tests/security/test_integration_security.py
import pytest
from cerberus.security.integration import SecurityIntegrationTest

class TestSecurityIntegration:
    """Integration tests for security controls"""
    
    @pytest.fixture
    def security_test(self):
        """Setup security testing environment"""
        return SecurityIntegrationTest()
    
    def test_secure_api_communication(self, security_test):
        """Verify API communication is secured"""
        # Test TLS enforcement
        response = security_test.make_request("/api/users", use_tls=False)
        assert response.status_code == 403  # Should reject HTTP
        
        # Test HSTS header
        response = security_test.make_request("/api/users", use_tls=True)
        assert response.headers.get("Strict-Transport-Security")
    
    def test_input_validation(self, security_test):
        """Verify input validation prevents injections"""
        # SQL injection attempt
        payload = {"username": "admin' OR '1'='1"}
        response = security_test.post("/api/login", payload)
        assert response.status_code == 400  # Should reject
        
        # XSS attempt
        payload = {"comment": "<script>alert('xss')</script>"}
        response = security_test.post("/api/comments", payload)
        assert response.status_code == 400
        
        # Command injection attempt
        payload = {"filename": "test.txt; rm -rf /"}
        response = security_test.post("/api/upload", payload)
        assert response.status_code == 400
    
    def test_rate_limiting(self, security_test):
        """Verify rate limiting is enforced"""
        # Make requests at high rate
        for i in range(101):  # Limit is 100/minute
            response = security_test.make_request(f"/api/endpoint{i}")
        
        # Should be rate limited
        response = security_test.make_request("/api/endpoint101")
        assert response.status_code == 429  # Too Many Requests
    
    def test_csrf_protection(self, security_test):
        """Verify CSRF tokens are required"""
        # Request without CSRF token should fail
        response = security_test.post("/api/action", {}, csrf_token=None)
        assert response.status_code == 403
        
        # Request with valid CSRF token should succeed
        csrf_token = security_test.get_csrf_token()
        response = security_test.post("/api/action", {}, csrf_token=csrf_token)
        assert response.status_code == 200
```

### Running Automated Tests

```bash
# Run all security tests
pytest tests/security/ -v

# Run specific test categories
pytest tests/security/test_authentication.py -v
pytest tests/security/test_integration_security.py -v

# Generate security test report
pytest tests/security/ --html=security-test-report.html --self-contained-html
```

---

## SAST/DAST/SCA Integration

### Static Application Security Testing (SAST)

SAST analyzes source code to identify vulnerabilities without executing the code.

#### CodeQL Integration

```yaml
# .github/workflows/codeql-analysis.yml
name: "CodeQL Analysis"

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: '0 2 * * 0'  # Weekly scan

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: ['python', 'javascript']

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Initialize CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: ${{ matrix.language }}
          queries: security-and-quality
      
      - name: Setup Python
        if: matrix.language == 'python'
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        if: matrix.language == 'python'
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2
        with:
          category: "/language:${{ matrix.language }}"
      
      - name: Upload SARIF results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: results.sarif
          wait-for-processing: true
```

#### Bandit for Python

```yaml
# .github/workflows/bandit-scan.yml
name: "Bandit Security Scan"

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  bandit:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Bandit
        run: pip install bandit[toml]
      
      - name: Run Bandit security scan
        run: |
          bandit -r cerberus/ -f json -o bandit-report.json
          bandit -r cerberus/ -f txt -o bandit-report.txt
        continue-on-error: true
      
      - name: Upload Bandit results
        uses: actions/upload-artifact@v3
        with:
          name: bandit-report
          path: |
            bandit-report.json
            bandit-report.txt
      
      - name: Comment PR with Bandit results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('bandit-report.json', 'utf8'));
            
            if (report.results.length > 0) {
              let comment = '## 🔒 Bandit Security Issues\n\n';
              report.results.forEach(issue => {
                comment += `- **${issue.severity}**: ${issue.issue_text}\n`;
                comment += `  File: ${issue.filename}:${issue.line_number}\n\n`;
              });
              
              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: comment
              });
            }
```

### Dynamic Application Security Testing (DAST)

```yaml
# .github/workflows/owasp-zap-scan.yml
name: "OWASP ZAP Scan"

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 3 * * 0'

jobs:
  zap-scan:
    runs-on: ubuntu-latest
    
    services:
      app:
        image: cerberus:latest
        ports:
          - 8000:8000
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Wait for app to be ready
        run: |
          for i in {1..30}; do
            curl -s http://localhost:8000/health && exit 0
            sleep 1
          done
          exit 1
      
      - name: Run OWASP ZAP scan
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: http://localhost:8000
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'
      
      - name: Upload ZAP results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: zap-report
          path: report_html.html
      
      - name: Check for high severity issues
        run: |
          # Parse ZAP report and fail if high severity issues found
          python scripts/check_zap_results.py report_html.html
```

### Software Composition Analysis (SCA)

```yaml
# .github/workflows/dependency-check.yml
name: "OWASP Dependency-Check"

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  dependency-check:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run OWASP Dependency-Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'Cerberus'
          path: '.'
          format: 'JSON'
          args: >
            --scan .
            --enable-experimental
            --enable-retired
            --exclude ./tests,./venv,./node_modules
      
      - name: Upload Dependency-Check results
        uses: actions/upload-artifact@v3
        with:
          name: dependency-check-report
          path: dependency-check-report.json
      
      - name: Parse and comment on vulnerabilities
        if: github.event_name == 'pull_request'
        run: python scripts/parse_dependency_check.py dependency-check-report.json
```

---

## Secret Scanning

### Native GitHub Secret Scanning

GitHub automatically scans repositories for secrets and credentials.

#### Configuration

```yaml
# .github/workflows/secret-scanning.yml
name: "Secret Scanning and Detection"

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  detect-secrets:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Install detect-secrets
        run: pip install detect-secrets
      
      - name: Scan for secrets
        run: |
          detect-secrets scan --baseline .secrets.baseline
        continue-on-error: true
      
      - name: Check for high-risk secrets
        run: |
          # Custom script to find AWS keys, API keys, tokens
          python scripts/find_secrets.py
      
      - name: Run TruffleHog scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --json --fail --max-depth 4
```

#### Secret Detection Script

```python
# scripts/find_secrets.py
import re
import os
import sys
from pathlib import Path

class SecretScanner:
    """Scan files for common secret patterns"""
    
    PATTERNS = {
        'aws_access_key': r'(?i)aws_access_key_id\s*=\s*[A-Z0-9]{20}',
        'aws_secret_key': r'(?i)aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40}',
        'github_token': r'ghp_[0-9a-zA-Z]{36}',
        'github_oauth': r'gho_[0-9a-zA-Z]{36}',
        'private_key': r'-----BEGIN [A-Z ]+ PRIVATE KEY-----',
        'api_key': r'api[_-]?key\s*[:=]\s*[A-Za-z0-9\-_]{32,}',
        'slack_token': r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*',
        'mongodb_uri': r'mongodb\+srv://[A-Za-z0-9_-]+:[A-Za-z0-9_@-]+',
        'database_password': r'password\s*[:=]\s*["\']?([A-Za-z0-9!@#$%^&*()_+=\-]{8,})["\']',
    }
    
    SKIP_DIRS = {'.git', '.github', 'node_modules', '__pycache__', '.venv', 'venv'}
    SKIP_FILES = {'.gitignore', '.env.example', 'secrets-template.yaml'}
    
    def __init__(self):
        self.findings = []
    
    def scan_directory(self, path='.'):
        """Recursively scan directory for secrets"""
        for root, dirs, files in os.walk(path):
            # Remove skip directories
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            
            for file in files:
                if file in self.SKIP_FILES:
                    continue
                
                filepath = os.path.join(root, file)
                self.scan_file(filepath)
    
    def scan_file(self, filepath):
        """Scan individual file for secrets"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                for pattern_name, pattern in self.PATTERNS.items():
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.findings.append({
                            'file': filepath,
                            'line': line_num,
                            'type': pattern_name,
                            'match': match.group(0)[:50]  # Truncate for safety
                        })
        except Exception as e:
            print(f"Error scanning {filepath}: {e}")
    
    def report(self):
        """Report findings"""
        if self.findings:
            print(f"\n❌ Found {len(self.findings)} potential secrets:\n")
            for finding in self.findings:
                print(f"  [{finding['type']}] {finding['file']}:{finding['line']}")
            sys.exit(1)
        else:
            print("\n✅ No secrets detected")

if __name__ == '__main__':
    scanner = SecretScanner()
    scanner.scan_directory()
    scanner.report()
```

### Branch Protection with Secret Scanning

```bash
# Configure branch protection via GitHub API
curl -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/owner/Cerberus/branches/main/protection \
  -d '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["CodeQL", "Bandit", "Secret Scanning"]
    },
    "enforce_admins": true,
    "required_pull_request_reviews": {
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": true,
      "required_approving_review_count": 2
    }
  }'
```

---

## Dependency Updates

### Automated Dependency Management

```yaml
# .github/workflows/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "03:00"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "python"
    allow:
      - dependency-type: "all"
    ignore:
      - dependency-name: "insecure-package"
    pull-request-branch-name:
      separator: "/"
    commit-message:
      prefix: "build(deps):"
    rebase-strategy: "disabled"

  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "03:30"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "javascript"

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "04:00"
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "docker"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "04:30"
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "github-actions"
```

### Automated Dependency Audit

```yaml
# .github/workflows/audit-dependencies.yml
name: "Audit Dependencies"

on:
  schedule:
    - cron: '0 1 * * *'
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install pip-audit
        run: pip install pip-audit
      
      - name: Audit Python dependencies
        run: |
          pip-audit --desc --format json -o pip-audit-report.json
        continue-on-error: true
      
      - name: Check for critical vulnerabilities
        run: |
          python scripts/check_pip_audit.py pip-audit-report.json
      
      - name: Audit npm dependencies
        if: hashFiles('package.json') != ''
        run: |
          npm audit --json > npm-audit-report.json
        continue-on-error: true
      
      - name: Upload audit reports
        uses: actions/upload-artifact@v3
        with:
          name: audit-reports
          path: |
            pip-audit-report.json
            npm-audit-report.json
      
      - name: Create issue for vulnerabilities
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Dependency vulnerabilities detected',
              body: 'Critical vulnerabilities found in dependencies. See artifacts for details.',
              labels: ['security', 'dependencies']
            });
```

---

## Automated Incident Response

### Vulnerability Detection Automation

```yaml
# .github/workflows/incident-response.yml
name: "Automated Incident Response"

on:
  workflow_run:
    workflows: ["CodeQL Analysis", "Bandit Security Scan", "OWASP Dependency-Check"]
    types: [completed]

jobs:
  analyze-findings:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
      security-events: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Download scan artifacts
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const artifacts = await github.rest.actions.listWorkflowRunArtifacts({
              owner: context.repo.owner,
              repo: context.repo.repo,
              run_id: context.payload.workflow_run.id,
            });
            
            for (const artifact of artifacts.data.artifacts) {
              console.log(`Found artifact: ${artifact.name}`);
            }
      
      - name: Process CodeQL alerts
        run: |
          python scripts/process_alerts.py \
            --source codeql \
            --severity high,critical \
            --action create-issue
      
      - name: Notify security team
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.teams.createDiscussionCommentInOrg({
              org: 'security-team',
              team_slug: 'core',
              discussion_number: 1,
              body: 'Critical security vulnerability detected in CI/CD pipeline'
            });
      
      - name: Auto-remediate high-risk findings
        run: python scripts/auto_remediate.py --risk-level high
      
      - name: Generate incident report
        run: |
          python scripts/generate_incident_report.py \
            --output-format markdown \
            --include-findings \
            --include-remediation
      
      - name: Upload incident report
        uses: actions/upload-artifact@v3
        with:
          name: incident-report
          path: incident-report.md
```

#### Auto-Remediation Script

```python
# scripts/auto_remediate.py
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

class IncidentResponder:
    """Automated incident response handler"""
    
    def __init__(self, risk_level='high'):
        self.risk_level = risk_level
        self.remediation_log = []
    
    def remediate_hardcoded_credentials(self, finding):
        """Remediate hardcoded credentials"""
        filepath = finding['file']
        
        # Check if file is a test or example file
        if 'test' in filepath or 'example' in filepath:
            return
        
        print(f"🔒 Rotating credentials in {filepath}")
        
        # Create issue for manual remediation
        self.create_remediation_issue(
            title=f"Rotate credentials in {filepath}",
            body=f"Hardcoded credentials detected and rotated.\n\nFile: {filepath}\nLine: {finding.get('line', 'N/A')}",
            labels=['security', 'credentials', 'auto-remediation']
        )
        
        self.remediation_log.append({
            'type': 'credential_rotation',
            'file': filepath,
            'timestamp': datetime.now().isoformat()
        })
    
    def remediate_dependency_vulnerability(self, finding):
        """Remediate vulnerable dependency"""
        package = finding['package']
        
        print(f"📦 Attempting to update {package}")
        
        # Create PR to update dependency
        self.create_update_pr(
            package=package,
            target_version=finding['recommended_version']
        )
    
    def remediate_code_injection(self, finding):
        """Remediate code injection vulnerability"""
        filepath = finding['file']
        line = finding['line']
        
        print(f"⚠️  Code injection risk detected in {filepath}:{line}")
        
        # Create high-priority issue
        self.create_remediation_issue(
            title=f"Critical: Potential code injection in {filepath}",
            body=f"Code injection vulnerability detected.\n\nFile: {filepath}\nLine: {line}\n\nAction required: Manual code review and remediation",
            labels=['security', 'critical', 'code-injection'],
            priority='urgent'
        )
    
    def create_remediation_issue(self, title, body, labels=None, priority='normal'):
        """Create issue for manual remediation"""
        import subprocess
        
        cmd = [
            'gh', 'issue', 'create',
            '--title', title,
            '--body', body
        ]
        
        if labels:
            cmd.extend(['--label', ','.join(labels)])
        
        subprocess.run(cmd, check=True)
    
    def create_update_pr(self, package, target_version):
        """Create PR to update package"""
        # Implementation for creating update PR
        pass
    
    def process_findings(self, findings_file):
        """Process findings and apply remediation"""
        with open(findings_file, 'r') as f:
            findings = json.load(f)
        
        for finding in findings:
            if finding['severity'] in ['high', 'critical']:
                if finding['type'] == 'hardcoded_credential':
                    self.remediate_hardcoded_credentials(finding)
                elif finding['type'] == 'vulnerable_dependency':
                    self.remediate_dependency_vulnerability(finding)
                elif finding['type'] == 'code_injection':
                    self.remediate_code_injection(finding)
    
    def save_log(self, output_file='remediation.log'):
        """Save remediation log"""
        with open(output_file, 'w') as f:
            json.dump(self.remediation_log, f, indent=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Automated incident response')
    parser.add_argument('--risk-level', default='high', help='Risk level threshold')
    parser.add_argument('--findings-file', default='findings.json')
    args = parser.parse_args()
    
    responder = IncidentResponder(risk_level=args.risk_level)
    responder.process_findings(args.findings_file)
    responder.save_log()
```

---

## GitHub Actions Workflows

### Master Security Workflow

```yaml
# .github/workflows/security-check.yml
name: "Comprehensive Security Check"

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: '0 0 * * 0'

jobs:
  security-matrix:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    
    strategy:
      matrix:
        security-check:
          - codeql
          - bandit
          - dependency-check
          - secret-scan
          - sca
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run ${{ matrix.security-check }}
        run: |
          case "${{ matrix.security-check }}" in
            codeql)
              echo "Running CodeQL..."
              # CodeQL execution
              ;;
            bandit)
              echo "Running Bandit..."
              pip install bandit
              bandit -r cerberus/
              ;;
            dependency-check)
              echo "Running Dependency Check..."
              # Dependency-check execution
              ;;
            secret-scan)
              echo "Running Secret Scan..."
              pip install detect-secrets
              detect-secrets scan
              ;;
            sca)
              echo "Running SCA..."
              pip install pip-audit
              pip-audit
              ;;
          esac
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: security-${{ matrix.security-check }}-results
          path: |
            results/
            reports/

  security-gates:
    runs-on: ubuntu-latest
    needs: security-matrix
    if: always()
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Download all results
        uses: actions/download-artifact@v3
      
      - name: Evaluate security gates
        run: python scripts/evaluate_gates.py
      
      - name: Enforce quality gates
        run: |
          if [ "${{ needs.security-matrix.result }}" = "failure" ]; then
            echo "❌ Security gates failed"
            exit 1
          fi
          echo "✅ All security gates passed"
```

---

## Monitoring and Alerting

### Security Dashboard

```python
# scripts/security_dashboard.py
import json
from datetime import datetime, timedelta
from collections import defaultdict

class SecurityDashboard:
    """Generate security metrics dashboard"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def collect_scan_results(self):
        """Collect results from all security scans"""
        scans = {
            'codeql': self.parse_codeql_results(),
            'bandit': self.parse_bandit_results(),
            'dependency_check': self.parse_dependency_results(),
            'secrets': self.parse_secret_results(),
        }
        return scans
    
    def parse_codeql_results(self):
        """Parse CodeQL results"""
        try:
            with open('results/codeql.sarif') as f:
                data = json.load(f)
                return {
                    'total_alerts': len(data.get('runs', [{}])[0].get('results', [])),
                    'critical': sum(1 for r in data.get('runs', [{}])[0].get('results', [])
                                   if r.get('level') == 'error'),
                    'high': sum(1 for r in data.get('runs', [{}])[0].get('results', [])
                               if r.get('level') == 'warning'),
                }
        except:
            return {'total_alerts': 0, 'critical': 0, 'high': 0}
    
    def parse_bandit_results(self):
        """Parse Bandit results"""
        try:
            with open('results/bandit.json') as f:
                data = json.load(f)
                return {
                    'total_issues': len(data.get('results', [])),
                    'critical': sum(1 for r in data.get('results', [])
                                   if r.get('severity') == 'HIGH'),
                    'high': sum(1 for r in data.get('results', [])
                               if r.get('severity') == 'MEDIUM'),
                }
        except:
            return {'total_issues': 0, 'critical': 0, 'high': 0}
    
    def parse_dependency_results(self):
        """Parse dependency check results"""
        try:
            with open('results/dependency-check.json') as f:
                data = json.load(f)
                return {
                    'total_vulnerabilities': len(data.get('dependencies', [])),
                    'critical': sum(1 for v in data.get('vulnerabilities', [])
                                   if v.get('severity') == 'CRITICAL'),
                }
        except:
            return {'total_vulnerabilities': 0, 'critical': 0}
    
    def parse_secret_results(self):
        """Parse secret scanning results"""
        try:
            with open('results/secrets.json') as f:
                data = json.load(f)
                return {
                    'total_secrets': len(data),
                    'active_secrets': sum(1 for s in data if not s.get('rotated')),
                }
        except:
            return {'total_secrets': 0, 'active_secrets': 0}
    
    def generate_report(self):
        """Generate security report"""
        scans = self.collect_scan_results()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_issues': sum(s.get('total_alerts', s.get('total_issues', s.get('total_vulnerabilities', 0)))
                                   for s in scans.values()),
                'critical_issues': sum(s.get('critical', 0) for s in scans.values()),
            },
            'scans': scans
        }
        
        return report
    
    def send_alerts(self, report):
        """Send alerts based on report"""
        critical = report['summary']['critical_issues']
        
        if critical > 0:
            self.send_slack_alert(f"🚨 {critical} critical security issues found!")
            self.send_email_alert(f"Security Alert: {critical} critical issues")
    
    def send_slack_alert(self, message):
        """Send Slack notification"""
        import os
        import requests
        
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        if webhook_url:
            requests.post(webhook_url, json={'text': message})
    
    def send_email_alert(self, subject):
        """Send email alert"""
        # Email implementation
        pass

if __name__ == '__main__':
    dashboard = SecurityDashboard()
    report = dashboard.generate_report()
    dashboard.send_alerts(report)
    
    with open('security-report.json', 'w') as f:
        json.dump(report, f, indent=2)
```

### Alerting Configuration

```yaml
# .github/workflows/security-alerts.yml
name: "Security Alerts"

on:
  workflow_run:
    workflows: ["Comprehensive Security Check"]
    types: [completed]

jobs:
  alert:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Send Slack notification
        uses: slackapi/slack-github-action@v1.24.0
        with:
          payload: |
            {
              "text": "🚨 Security check failed",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Security Alert*\n\nWorkflow: ${{ github.event.workflow_run.name }}\nStatus: ${{ github.event.workflow_run.conclusion }}\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.event.workflow_run.id }}|View Details>"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      
      - name: Create issue for investigation
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Security check failed - Investigation required',
              body: 'Automated security check failed. Review workflow run for details.',
              labels: ['security', 'urgent'],
              assignees: ['security-team']
            });
```

---

## Best Practices

1. **Continuous Monitoring**: Run security checks on every push and PR
2. **Automated Remediation**: Auto-remediate low-risk issues (dependency updates)
3. **Escalation Procedures**: Manual review for critical findings
4. **Feedback Loops**: Report results back to developers quickly
5. **Baseline Management**: Maintain security baselines and track improvements
6. **Tool Updates**: Keep security tools updated with latest rules
7. **Metrics Tracking**: Monitor security metrics over time

---

## Related Documentation

- [Pipeline Security](pipeline-security.md)
- [Scan Procedures](scan-procedures.md)
- [Security Tools Reference](../tools-reference.md)
- [Incident Response](../incident-response.md)

