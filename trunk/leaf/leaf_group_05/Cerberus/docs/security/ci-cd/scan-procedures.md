<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / scan-procedures.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / scan-procedures.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Security Scanning Procedures

## Overview

This document provides comprehensive procedures for conducting security scans across the Cerberus application. It covers vulnerability scanning, container scanning, code analysis, dependency scanning, and automated testing strategies integrated into the CI/CD pipeline.

## Table of Contents

1. [Vulnerability Scanning](#vulnerability-scanning)
2. [Container Scanning](#container-scanning)
3. [Code Scanning with CodeQL](#code-scanning-with-codeql)
4. [Dependency Scanning](#dependency-scanning)
5. [Guardian Testing Automation](#guardian-testing-automation)
6. [Scan Result Analysis](#scan-result-analysis)
7. [Reporting and Metrics](#reporting-and-metrics)

---

## Vulnerability Scanning

### OpenVAS Integration

OpenVAS provides comprehensive vulnerability scanning capabilities.

```yaml
# .github/workflows/openvas-scan.yml
name: "OpenVAS Vulnerability Scan"

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly Sunday at 2 AM
  workflow_dispatch:

jobs:
  vulnerability-scan:
    runs-on: ubuntu-latest
    
    services:
      openvas:
        image: greenbone/openvas:22.04.8
        ports:
          - 9392:9392
          - 9393:9393
        env:
          TIMEZONE: UTC
        options: >-
          --health-cmd "curl -f -k https://localhost:9392 || exit 1"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Wait for OpenVAS to be ready
        run: |
          for i in {1..60}; do
            curl -k https://localhost:9392 && break
            sleep 5
          done
      
      - name: Install gvm-tools
        run: |
          pip install gvm-tools
      
      - name: Configure OpenVAS targets
        run: |
          python scripts/configure_openvas_targets.py \
            --host localhost \
            --port 9392 \
            --target-url ${{ secrets.APP_URL }}
      
      - name: Execute vulnerability scans
        run: |
          python scripts/run_openvas_scans.py \
            --full-and-fast \
            --output xml \
            --output-file vuln-scan-results.xml
      
      - name: Parse and analyze results
        run: |
          python scripts/analyze_openvas_results.py \
            vuln-scan-results.xml \
            --severity high \
            --fail-on-findings
      
      - name: Generate vulnerability report
        run: |
          python scripts/generate_vuln_report.py \
            vuln-scan-results.xml \
            --format html \
            --output vulnerability-report.html
      
      - name: Upload vulnerability report
        uses: actions/upload-artifact@v3
        with:
          name: vulnerability-scan-report
          path: vulnerability-report.html
      
      - name: Archive scan results
        uses: actions/upload-artifact@v3
        with:
          name: openvas-raw-results
          path: vuln-scan-results.xml
```

### Vulnerability Analysis Script

```python
# scripts/analyze_openvas_results.py
import xml.etree.ElementTree as ET
import json
import argparse
import sys
from collections import defaultdict
from datetime import datetime

class OpenVASResultAnalyzer:
    """Analyze OpenVAS vulnerability scan results"""
    
    SEVERITY_LEVELS = {
        '8.0-10.0': 'CRITICAL',
        '7.0-7.9': 'HIGH',
        '4.0-6.9': 'MEDIUM',
        '0.1-3.9': 'LOW',
        '0.0': 'NONE',
    }
    
    CVSS_THRESHOLDS = {
        'critical': 8.9,
        'high': 7.0,
        'medium': 4.0,
        'low': 0.1,
    }
    
    def __init__(self, results_file):
        self.results_file = results_file
        self.findings = []
        self.parse_results()
    
    def parse_results(self):
        """Parse XML results from OpenVAS"""
        tree = ET.parse(self.results_file)
        root = tree.getroot()
        
        # Extract vulnerabilities
        for result in root.findall('.//result'):
            vulnerability = {
                'oid': result.find('nvt/oid').text if result.find('nvt/oid') is not None else 'N/A',
                'name': result.find('nvt/name').text if result.find('nvt/name') is not None else 'Unknown',
                'family': result.find('nvt/family').text if result.find('nvt/family') is not None else 'Unknown',
                'severity': float(result.find('severity').text) if result.find('severity') is not None else 0.0,
                'cvss_base': result.find('cvss_base').text if result.find('cvss_base') is not None else 'N/A',
                'host': result.find('host').text if result.find('host') is not None else 'N/A',
                'description': result.find('description').text if result.find('description') is not None else '',
                'cves': self.extract_cves(result),
            }
            self.findings.append(vulnerability)
    
    def extract_cves(self, result_elem):
        """Extract CVE IDs from result"""
        cves = []
        refs = result_elem.find('refs')
        if refs is not None:
            for ref in refs.findall('ref'):
                if ref.get('type') == 'CVE':
                    cves.append(ref.get('id'))
        return cves
    
    def get_severity_level(self, cvss_score):
        """Get severity level from CVSS score"""
        if cvss_score >= 9.0:
            return 'CRITICAL'
        elif cvss_score >= 7.0:
            return 'HIGH'
        elif cvss_score >= 4.0:
            return 'MEDIUM'
        elif cvss_score > 0.0:
            return 'LOW'
        else:
            return 'NONE'
    
    def group_by_severity(self):
        """Group findings by severity level"""
        grouped = defaultdict(list)
        
        for finding in self.findings:
            severity = self.get_severity_level(finding['severity'])
            grouped[severity].append(finding)
        
        return grouped
    
    def filter_by_severity(self, min_severity):
        """Filter findings by minimum severity"""
        severity_ranks = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        min_rank = severity_ranks.get(min_severity, 0)
        
        return [f for f in self.findings 
                if severity_ranks.get(self.get_severity_level(f['severity']), 0) >= min_rank]
    
    def generate_summary(self):
        """Generate summary statistics"""
        grouped = self.group_by_severity()
        
        return {
            'total_findings': len(self.findings),
            'critical': len(grouped.get('CRITICAL', [])),
            'high': len(grouped.get('HIGH', [])),
            'medium': len(grouped.get('MEDIUM', [])),
            'low': len(grouped.get('LOW', [])),
            'scan_time': datetime.now().isoformat(),
        }
    
    def check_thresholds(self, thresholds):
        """Check if findings exceed thresholds"""
        summary = self.generate_summary()
        
        violations = {}
        if summary['critical'] > thresholds.get('critical', 0):
            violations['critical'] = f"Critical: {summary['critical']} > {thresholds.get('critical', 0)}"
        if summary['high'] > thresholds.get('high', 10):
            violations['high'] = f"High: {summary['high']} > {thresholds.get('high', 10)}"
        
        return violations
    
    def generate_report(self, output_file='vulnerability-report.json'):
        """Generate detailed report"""
        report = {
            'metadata': {
                'scan_time': datetime.now().isoformat(),
                'total_findings': len(self.findings),
                'source': 'OpenVAS',
            },
            'summary': self.generate_summary(),
            'findings_by_severity': self.group_by_severity(),
            'findings': self.findings,
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze OpenVAS results')
    parser.add_argument('results_file', help='OpenVAS XML results file')
    parser.add_argument('--severity', choices=['critical', 'high', 'medium', 'low'],
                       default='high', help='Minimum severity to report')
    parser.add_argument('--fail-on-findings', action='store_true',
                       help='Exit with error if findings found')
    
    args = parser.parse_args()
    
    analyzer = OpenVASResultAnalyzer(args.results_file)
    summary = analyzer.generate_summary()
    
    print(f"Vulnerability Scan Summary:")
    print(f"  Total: {summary['total_findings']}")
    print(f"  Critical: {summary['critical']}")
    print(f"  High: {summary['high']}")
    print(f"  Medium: {summary['medium']}")
    print(f"  Low: {summary['low']}")
    
    filtered = analyzer.filter_by_severity(args.severity)
    
    if args.fail_on_findings and len(filtered) > 0:
        print(f"\n❌ Found {len(filtered)} {args.severity} and above vulnerabilities")
        sys.exit(1)
    
    print("✅ Vulnerability scan completed")
```

---

## Container Scanning

### Trivy Container Image Scanning

Trivy provides fast and comprehensive vulnerability scanning for container images.

```yaml
# .github/workflows/container-scan.yml
name: "Container Image Scan"

on:
  push:
    branches: [main, develop]
    paths:
      - 'Dockerfile'
      - 'docker-compose.yml'
      - '.github/workflows/container-scan.yml'
  pull_request:
    branches: [main]
    paths:
      - 'Dockerfile'
      - 'docker-compose.yml'

jobs:
  build-and-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Build Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: false
          load: true
          tags: |
            cerberus:latest
            cerberus:${{ github.sha }}
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: cerberus:latest
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Run Trivy filesystem scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-fs-results.sarif'
      
      - name: Run Trivy config scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'config'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-config-results.sarif'
      
      - name: Upload Trivy results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: |
            trivy-results.sarif
            trivy-fs-results.sarif
            trivy-config-results.sarif
      
      - name: Analyze Trivy results
        run: |
          python scripts/analyze_trivy_results.py \
            --image cerberus:latest \
            --fail-on-high
      
      - name: Generate SBoM (Software Bill of Materials)
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: cerberus:latest
          format: 'cyclonedx'
          output: 'sbom.json'
      
      - name: Upload SBoM
        uses: actions/upload-artifact@v3
        with:
          name: sbom
          path: sbom.json
```

### Trivy Result Analysis

```python
# scripts/analyze_trivy_results.py
import json
import argparse
import sys
from collections import Counter

class TrivyAnalyzer:
    """Analyze Trivy scan results"""
    
    SEVERITY_PRIORITY = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'UNKNOWN': 4}
    
    def __init__(self, sarif_file):
        self.results = []
        self.parse_sarif(sarif_file)
    
    def parse_sarif(self, sarif_file):
        """Parse SARIF format results"""
        with open(sarif_file, 'r') as f:
            sarif = json.load(f)
        
        for run in sarif.get('runs', []):
            for result in run.get('results', []):
                self.results.append({
                    'rule_id': result.get('ruleId'),
                    'message': result.get('message', {}).get('text', ''),
                    'level': result.get('level', 'warning'),
                    'locations': result.get('locations', []),
                    'properties': result.get('properties', {}),
                })
    
    def get_vulnerabilities_by_severity(self):
        """Group vulnerabilities by severity"""
        grouped = {}
        for result in self.results:
            level = result['level']
            if level not in grouped:
                grouped[level] = []
            grouped[level].append(result)
        return grouped
    
    def get_statistics(self):
        """Generate statistics"""
        severity_counts = Counter()
        for result in self.results:
            severity_counts[result['level']] += 1
        
        return {
            'total': len(self.results),
            'by_severity': dict(severity_counts),
        }
    
    def check_thresholds(self, fail_on_high=False, fail_on_medium=False):
        """Check if thresholds are violated"""
        stats = self.get_statistics()
        
        if fail_on_high and stats['by_severity'].get('high', 0) > 0:
            return False, f"Found {stats['by_severity'].get('high', 0)} HIGH severity vulnerabilities"
        
        if fail_on_medium and stats['by_severity'].get('medium', 0) > 0:
            return False, f"Found {stats['by_severity'].get('medium', 0)} MEDIUM severity vulnerabilities"
        
        return True, "No critical thresholds exceeded"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze Trivy results')
    parser.add_argument('--sarif-file', default='trivy-results.sarif')
    parser.add_argument('--image', help='Image name')
    parser.add_argument('--fail-on-high', action='store_true')
    parser.add_argument('--fail-on-medium', action='store_true')
    args = parser.parse_args()
    
    analyzer = TrivyAnalyzer(args.sarif_file)
    stats = analyzer.get_statistics()
    
    print(f"Trivy Scan Results for {args.image}:")
    print(f"  Total vulnerabilities: {stats['total']}")
    for severity, count in stats['by_severity'].items():
        print(f"  {severity}: {count}")
    
    passed, message = analyzer.check_thresholds(
        fail_on_high=args.fail_on_high,
        fail_on_medium=args.fail_on_medium
    )
    
    if not passed:
        print(f"\n❌ {message}")
        sys.exit(1)
    
    print("✅ Container scan passed")
```

### Multi-Stage Docker Scanning

```dockerfile
# Dockerfile with security scanning stages
FROM python:3.11-slim as base

# Install security audit tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# Security scanning stage
FROM base as security-scan
RUN pip install pip-audit bandit safety
COPY . /app

# Audit Python dependencies
RUN pip-audit || true
RUN safety check || true
RUN bandit -r . -f json -o /tmp/bandit-results.json || true

# Build stage
FROM base as builder
RUN pip install -r requirements.txt
COPY . /app

# Runtime stage
FROM python:3.11-slim as runtime

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# Security: Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser

EXPOSE 8000
ENTRYPOINT ["python", "-m", "cerberus.main"]
```

---

## Code Scanning with CodeQL

### Advanced CodeQL Configuration

```yaml
# .github/workflows/advanced-codeql.yml
name: "Advanced CodeQL Analysis"

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * 0'

jobs:
  analyze:
    name: Analyze Code
    runs-on: ${{ matrix.os }}
    permissions:
      actions: read
      contents: read
      security-events: write
    
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest]
        language: ['python', 'javascript']
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Initialize CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: ${{ matrix.language }}
          # Use queries from both GitHub and custom security queries
          queries: security-and-quality,security-extended,./queries/custom-security
          tools: latest
      
      - name: Setup Python
        if: matrix.language == 'python'
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        if: matrix.language == 'python'
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Setup Node.js
        if: matrix.language == 'javascript'
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install Node dependencies
        if: matrix.language == 'javascript'
        run: npm ci
      
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2
        with:
          category: "/language:${{ matrix.language }}"
          upload: true
          wait-for-processing: true
      
      - name: Validate results
        run: |
          python scripts/validate_codeql_results.py \
            --ref ${{ github.ref }} \
            --language ${{ matrix.language }}
```

### Custom CodeQL Queries for Cerberus

```ql
// queries/insecure-authentication.ql
import python

from Call call, Expr arg
where
  call.getFunc().(Name).getId() = "hash" or
  call.getFunc().(Name).getId() = "md5" or
  call.getFunc().(Name).getId() = "sha1"
select
  call,
  "Weak hash function used for security: " + call.getFunc().(Name).getId()
```

```ql
// queries/hardcoded-credentials.ql
import python

from StrConst str, Module m
where
  (str.getValue().matches("%password%") or
   str.getValue().matches("%secret%") or
   str.getValue().matches("%token%") or
   str.getValue().matches("%key%") or
   str.getValue().matches("%api_key%"))
  and m.getName() != "tests"
select
  str,
  "Potential hardcoded credential found"
```

---

## Dependency Scanning

### pip-audit Scanning

```yaml
# .github/workflows/pip-audit-scan.yml
name: "Python Dependency Audit"

on:
  push:
    branches: [main, develop]
    paths:
      - 'requirements.txt'
      - 'requirements-*.txt'
      - 'setup.py'
      - 'pyproject.toml'
  schedule:
    - cron: '0 1 * * *'  # Daily at 1 AM

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
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run pip-audit
        run: |
          pip-audit \
            --desc \
            --format json \
            --output pip-audit-full.json
        continue-on-error: true
      
      - name: Run pip-audit (strict mode)
        run: |
          pip-audit \
            --strict \
            --desc \
            --format columnar
        continue-on-error: true
      
      - name: Analyze vulnerabilities
        run: |
          python scripts/analyze_pip_audit.py \
            pip-audit-full.json \
            --fail-on-vulnerabilities
      
      - name: Generate audit report
        run: |
          pip-audit --desc --format markdown > pip-audit-report.md
      
      - name: Comment on PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('pip-audit-report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## 📦 Dependency Audit Results\n\n' + report
            });
```

### Dependency Audit Analysis

```python
# scripts/analyze_pip_audit.py
import json
import argparse
import sys
from collections import defaultdict

class PipAuditAnalyzer:
    """Analyze pip-audit results"""
    
    SEVERITY_MAP = {
        'high': ['critical', 'high'],
        'medium': ['medium'],
        'low': ['low'],
    }
    
    def __init__(self, audit_file):
        self.vulnerabilities = []
        self.parse_audit_results(audit_file)
    
    def parse_audit_results(self, audit_file):
        """Parse pip-audit JSON output"""
        with open(audit_file, 'r') as f:
            data = json.load(f)
        
        for vuln in data.get('vulnerabilities', []):
            self.vulnerabilities.append({
                'package': vuln.get('name'),
                'version': vuln.get('version'),
                'advisory': vuln.get('advisory'),
                'cves': vuln.get('cves', []),
                'fixed_version': vuln.get('fixed_versions', []),
                'severity': self.determine_severity(vuln),
            })
    
    def determine_severity(self, vuln):
        """Determine severity from CVE data"""
        cves = vuln.get('cves', [])
        if not cves:
            return 'UNKNOWN'
        
        # Map CVSS scores to severity
        for cve in cves:
            # This would typically come from external CVE data
            pass
        
        return 'HIGH'
    
    def group_by_package(self):
        """Group vulnerabilities by package"""
        grouped = defaultdict(list)
        for vuln in self.vulnerabilities:
            grouped[vuln['package']].append(vuln)
        return grouped
    
    def get_critical_vulnerabilities(self):
        """Get only critical/high vulnerabilities"""
        return [v for v in self.vulnerabilities 
                if v['severity'] in ['CRITICAL', 'HIGH']]
    
    def generate_report(self):
        """Generate detailed report"""
        critical = self.get_critical_vulnerabilities()
        grouped = self.group_by_package()
        
        report = {
            'total_vulnerabilities': len(self.vulnerabilities),
            'critical_count': len(critical),
            'packages_affected': len(grouped),
            'vulnerabilities_by_package': grouped,
            'critical_vulnerabilities': critical,
        }
        
        return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze pip-audit results')
    parser.add_argument('audit_file', help='pip-audit JSON output file')
    parser.add_argument('--fail-on-vulnerabilities', action='store_true')
    args = parser.parse_args()
    
    analyzer = PipAuditAnalyzer(args.audit_file)
    report = analyzer.generate_report()
    
    print(f"Dependency Audit Report:")
    print(f"  Total vulnerabilities: {report['total_vulnerabilities']}")
    print(f"  Critical/High: {report['critical_count']}")
    print(f"  Packages affected: {report['packages_affected']}")
    
    if args.fail_on_vulnerabilities and report['critical_count'] > 0:
        print(f"\n❌ Found {report['critical_count']} critical vulnerabilities")
        sys.exit(1)
```

---

## Guardian Testing Automation

### Security Guardian Framework

```python
# cerberus/testing/security_guardian.py
"""
Cerberus Security Guardian - Automated security testing framework
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum

class TestCategory(Enum):
    """Security test categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    INPUT_VALIDATION = "input_validation"
    OUTPUT_ENCODING = "output_encoding"
    SESSION_MANAGEMENT = "session_management"
    CRYPTOGRAPHY = "cryptography"
    API_SECURITY = "api_security"
    BUSINESS_LOGIC = "business_logic"

@dataclass
class SecurityTestResult:
    """Result of a security test"""
    test_id: str
    category: TestCategory
    status: str  # passed, failed, skipped
    message: str
    timestamp: str
    duration_ms: float
    evidence: Dict[str, Any] = None
    recommendation: str = None

class SecurityGuardian:
    """Automated security testing guardian"""
    
    def __init__(self):
        self.results: List[SecurityTestResult] = []
        self.test_suite = {}
    
    def register_test(self, category: TestCategory, test_func):
        """Register a security test"""
        if category not in self.test_suite:
            self.test_suite[category] = []
        self.test_suite[category].append(test_func)
    
    async def run_tests(self, categories: List[TestCategory] = None):
        """Run security tests"""
        if categories is None:
            categories = list(TestCategory)
        
        for category in categories:
            if category not in self.test_suite:
                continue
            
            for test_func in self.test_suite[category]:
                result = await self._run_test(category, test_func)
                self.results.append(result)
    
    async def _run_test(self, category: TestCategory, test_func) -> SecurityTestResult:
        """Run individual test"""
        import time
        start = time.time()
        
        try:
            result = await test_func()
            status = "passed" if result.get('passed') else "failed"
            message = result.get('message', 'Test completed')
        except Exception as e:
            status = "failed"
            message = str(e)
            result = {'evidence': str(e)}
        
        duration = (time.time() - start) * 1000
        
        return SecurityTestResult(
            test_id=test_func.__name__,
            category=category,
            status=status,
            message=message,
            timestamp=datetime.now().isoformat(),
            duration_ms=duration,
            evidence=result.get('evidence'),
            recommendation=result.get('recommendation'),
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == 'passed')
        failed = sum(1 for r in self.results if r.status == 'failed')
        
        by_category = {}
        for category in TestCategory:
            category_results = [r for r in self.results if r.category == category]
            by_category[category.value] = {
                'total': len(category_results),
                'passed': sum(1 for r in category_results if r.status == 'passed'),
                'failed': sum(1 for r in category_results if r.status == 'failed'),
            }
        
        return {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'by_category': by_category,
            'timestamp': datetime.now().isoformat(),
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive report"""
        failed_tests = [r for r in self.results if r.status == 'failed']
        
        return {
            'summary': self.get_summary(),
            'results': [asdict(r) for r in self.results],
            'failed_tests': [asdict(r) for r in failed_tests],
            'recommendations': [r.recommendation for r in failed_tests if r.recommendation],
        }
    
    def save_report(self, filepath: str):
        """Save report to file"""
        report = self.generate_report()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)

# Example test implementations
async def test_password_hashing():
    """Test password hashing security"""
    from cerberus.security.authentication import PasswordHasher
    
    hasher = PasswordHasher()
    password = "TestPassword123!"
    
    hash1 = hasher.hash(password)
    hash2 = hasher.hash(password)
    
    if hash1 != hash2:
        return {'passed': True, 'message': 'Passwords hashed with different salts'}
    else:
        return {'passed': False, 'message': 'Passwords hashed identically - weak salt'}

async def test_sql_injection_protection():
    """Test SQL injection protection"""
    from cerberus.db import Database
    
    db = Database()
    
    # Attempt SQL injection
    payload = "admin' OR '1'='1"
    try:
        result = db.execute("SELECT * FROM users WHERE username = ?", (payload,))
        return {'passed': True, 'message': 'Parameterized queries protected'}
    except Exception as e:
        return {'passed': False, 'message': f'SQL injection vulnerability: {e}'}

async def test_rate_limiting():
    """Test rate limiting"""
    from cerberus.api import APIClient
    
    client = APIClient()
    
    # Make rapid requests
    responses = []
    for _ in range(101):
        resp = await client.make_request('/api/endpoint')
        responses.append(resp.status_code)
    
    # Check for rate limiting
    if 429 in responses:  # Too Many Requests
        return {'passed': True, 'message': 'Rate limiting enforced'}
    else:
        return {
            'passed': False,
            'message': 'Rate limiting not enforced',
            'recommendation': 'Implement rate limiting to prevent DoS attacks'
        }
```

### Guardian Test Workflow

```yaml
# .github/workflows/guardian-tests.yml
name: "Security Guardian Tests"

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  guardian:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run Security Guardian tests
        run: |
          python -m pytest tests/security/test_guardian.py -v --tb=short
      
      - name: Generate Guardian report
        run: |
          python scripts/run_guardian_tests.py \
            --output security-guardian-report.json
      
      - name: Upload Guardian report
        uses: actions/upload-artifact@v3
        with:
          name: guardian-report
          path: security-guardian-report.json
      
      - name: Comment PR with Guardian results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('security-guardian-report.json', 'utf8'));
            const summary = report.summary;
            
            const comment = `## 🛡️ Security Guardian Report\n\n` +
              `- **Total Tests**: ${summary.total_tests}\n` +
              `- **Passed**: ${summary.passed} ✅\n` +
              `- **Failed**: ${summary.failed} ❌\n` +
              `- **Success Rate**: ${summary.success_rate.toFixed(2)}%\n`;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

---

## Scan Result Analysis

### Unified Results Analyzer

```python
# scripts/analyze_all_scans.py
import json
import glob
from pathlib import Path
from collections import defaultdict

class UnifiedScanAnalyzer:
    """Unified analysis of all security scans"""
    
    def __init__(self, results_dir='results'):
        self.results_dir = results_dir
        self.all_findings = []
    
    def collect_results(self):
        """Collect results from all scan types"""
        # Collect SARIF results
        for sarif_file in glob.glob(f'{self.results_dir}/*.sarif'):
            self.parse_sarif(sarif_file)
        
        # Collect JSON results
        for json_file in glob.glob(f'{self.results_dir}/*.json'):
            if 'audit' in json_file or 'trivy' in json_file:
                self.parse_json(json_file)
    
    def parse_sarif(self, filepath):
        """Parse SARIF format"""
        with open(filepath, 'r') as f:
            sarif = json.load(f)
        
        for run in sarif.get('runs', []):
            for result in run.get('results', []):
                self.all_findings.append({
                    'source': 'sarif',
                    'type': result.get('ruleId'),
                    'severity': self.map_level_to_severity(result.get('level')),
                    'message': result.get('message', {}).get('text'),
                })
    
    def parse_json(self, filepath):
        """Parse JSON format results"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            if 'vulnerabilities' in data:
                for vuln in data['vulnerabilities']:
                    self.all_findings.append({
                        'source': Path(filepath).stem,
                        'type': vuln.get('type'),
                        'severity': vuln.get('severity'),
                        'message': vuln.get('description'),
                    })
    
    def map_level_to_severity(self, level):
        """Map different severity formats"""
        mapping = {
            'error': 'CRITICAL',
            'warning': 'HIGH',
            'note': 'MEDIUM',
            'none': 'LOW',
        }
        return mapping.get(level, 'UNKNOWN')
    
    def generate_unified_report(self):
        """Generate unified report"""
        severity_counts = defaultdict(int)
        source_counts = defaultdict(int)
        
        for finding in self.all_findings:
            severity_counts[finding['severity']] += 1
            source_counts[finding['source']] += 1
        
        return {
            'total_findings': len(self.all_findings),
            'by_severity': dict(severity_counts),
            'by_source': dict(source_counts),
            'critical_findings': [f for f in self.all_findings if f['severity'] == 'CRITICAL'],
        }
```

---

## Reporting and Metrics

### Security Metrics Dashboard

```python
# scripts/security_metrics.py
import json
from datetime import datetime, timedelta
from pathlib import Path

class SecurityMetrics:
    """Track and report security metrics"""
    
    def __init__(self, metrics_dir='metrics'):
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(exist_ok=True)
    
    def record_scan_results(self, scan_type: str, results: dict):
        """Record scan results"""
        timestamp = datetime.now().isoformat()
        
        metric = {
            'timestamp': timestamp,
            'scan_type': scan_type,
            'results': results,
        }
        
        filename = self.metrics_dir / f"{scan_type}_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(filename, 'w') as f:
            json.dump(metric, f, indent=2)
    
    def calculate_trends(self, days=30):
        """Calculate trends over time"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        trends = defaultdict(list)
        
        for metric_file in self.metrics_dir.glob('*.json'):
            with open(metric_file, 'r') as f:
                data = json.load(f)
            
            timestamp = datetime.fromisoformat(data['timestamp'])
            if start_date <= timestamp <= end_date:
                scan_type = data['scan_type']
                trends[scan_type].append({
                    'timestamp': data['timestamp'],
                    'total': data['results'].get('total', 0),
                    'critical': data['results'].get('critical', 0),
                })
        
        return trends
    
    def generate_dashboard(self):
        """Generate metrics dashboard"""
        trends = self.calculate_trends(days=30)
        
        dashboard = {
            'generated': datetime.now().isoformat(),
            'trends_30_days': trends,
            'current_metrics': self.get_current_metrics(),
        }
        
        return dashboard
    
    def get_current_metrics(self):
        """Get current metrics"""
        # Implementation to get current metrics
        pass
```

---

## Best Practices

1. **Continuous Scanning**: Run scans on every push and PR
2. **Result Tracking**: Maintain history of scan results
3. **Trend Analysis**: Monitor improvement over time
4. **Actionable Results**: Provide clear remediation guidance
5. **False Positive Management**: Maintain allowlists for confirmed false positives
6. **Tool Diversity**: Use multiple tools to catch different vulnerability types
7. **Automation**: Automate remediation of low-risk findings
8. **Reporting**: Generate clear reports for stakeholders

---

## Related Documentation

- [Security Automation](security-automation.md)
- [Pipeline Security](pipeline-security.md)
- [Security Tools Reference](../tools-reference.md)

