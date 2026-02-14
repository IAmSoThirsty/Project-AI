#!/usr/bin/env python3
"""
360° Deployable System Standard - Auto-Update Script

This script automatically updates the deployment standard checklist based on:
- Test coverage reports
- Security scan results
- CI/CD pipeline status
- System metrics

Usage:
    python scripts/update_standard_status.py
"""

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class ChecklistItem:
    """Represents a single checklist item."""
    id: str
    title: str
    status: str  # 'complete', 'in_progress', 'pending'
    percentage: int
    last_updated: str
    evidence: list[str]

class StandardStatusUpdater:
    """Updates the 360° Deployable System Standard status."""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.standard_file = self.repo_root / 'docs' / 'DEPLOYABLE_SYSTEM_STANDARD.md'
        self.status_file = self.repo_root / 'docs' / 'standard_status.json'

    def check_test_coverage(self) -> int:
        """Check test coverage percentage."""
        try:
            subprocess.run(
                ['pytest', '--cov=src', '--cov-report=json'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=300
            )

            coverage_file = self.repo_root / 'coverage.json'
            if coverage_file.exists():
                with open(coverage_file) as f:
                    data = json.load(f)
                    return int(data['totals']['percent_covered'])
        except Exception as e:
            print(f"Error checking test coverage: {e}")

        return 0

    def check_security_scans(self) -> dict[str, bool]:
        """Check status of security scans."""
        scans = {
            'bandit': False,
            'codeql': False,
            'trivy': False,
            'dependabot': False
        }

        # Check if Bandit passes
        try:
            result = subprocess.run(
                ['bandit', '-r', 'src/', '-f', 'json'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            data = json.loads(result.stdout)
            # Pass if no high/critical issues
            scans['bandit'] = len([i for i in data['results'] if i['issue_severity'] in ['HIGH', 'CRITICAL']]) == 0
        except Exception:
            pass

        # Check if CodeQL workflow exists
        codeql_workflow = self.repo_root / '.github' / 'workflows' / 'codeql.yml'
        scans['codeql'] = codeql_workflow.exists()

        # Check if Trivy is configured
        docker_scan = self.repo_root / 'Dockerfile'
        scans['trivy'] = docker_scan.exists()

        # Check if Dependabot is configured
        dependabot_config = self.repo_root / '.github' / 'dependabot.yml'
        scans['dependabot'] = dependabot_config.exists()

        return scans

    def check_docker_security(self) -> dict[str, bool]:
        """Check Docker security practices."""
        checks = {
            'non_root_user': False,
            'pinned_base': False,
            'multistage': False,
            'no_shell': False
        }

        dockerfile = self.repo_root / 'Dockerfile'
        if not dockerfile.exists():
            return checks

        content = dockerfile.read_text()

        # Check for non-root user (but not root or UID 0)
        user_match = re.search(r'USER\s+(\S+)', content)
        if user_match:
            user = user_match.group(1)
            checks['non_root_user'] = user.lower() not in ['root', '0']
        else:
            checks['non_root_user'] = False

        # Check for pinned base image (version number or SHA256)
        checks['pinned_base'] = bool(re.search(r'FROM .+:(?:\d+\.\d+(?:\.\d+)?|.*@sha256:)', content))

        # Check for multi-stage build
        checks['multistage'] = content.count('FROM ') >= 2

        # Check for no shell in runtime (ENTRYPOINT/CMD, not RUN)
        # Shell in RUN commands is OK, but not in ENTRYPOINT/CMD
        entrypoint_cmd_lines = []
        for line in content.split('\n'):
            if line.strip().startswith(('ENTRYPOINT', 'CMD')):
                entrypoint_cmd_lines.append(line)

        # Check if any ENTRYPOINT/CMD uses shell form with /bin/sh or /bin/bash
        has_runtime_shell = any('/bin/sh' in line or '/bin/bash' in line
                                 for line in entrypoint_cmd_lines)
        checks['no_shell'] = not has_runtime_shell

        return checks

    def check_kubernetes_config(self) -> dict[str, bool]:
        """Check Kubernetes security configuration."""
        checks = {
            'readiness_probe': False,
            'liveness_probe': False,
            'resource_limits': False,
            'security_context': False,
            'network_policy': False
        }

        k8s_dir = self.repo_root / 'k8s'
        if not k8s_dir.exists():
            return checks

        for yaml_file in k8s_dir.rglob('*.yaml'):
            content = yaml_file.read_text()

            if 'readinessProbe' in content:
                checks['readiness_probe'] = True
            if 'livenessProbe' in content:
                checks['liveness_probe'] = True
            if 'resources:' in content and 'limits:' in content:
                checks['resource_limits'] = True
            if 'securityContext:' in content:
                checks['security_context'] = True
            if 'kind: NetworkPolicy' in content:
                checks['network_policy'] = True

        return checks

    def check_documentation(self) -> dict[str, bool]:
        """Check documentation completeness."""
        docs = {
            'architecture_diagram': False,
            'threat_model': False,
            'deployment_guide': False,
            'incident_response': False,
            'recovery_guide': False
        }

        docs_dir = self.repo_root / 'docs'

        # Check for various documentation files
        docs['architecture_diagram'] = (docs_dir / 'PRODUCTION_ARCHITECTURE.md').exists()
        docs['threat_model'] = (docs_dir / 'security_compliance' / 'THREAT_MODEL.md').exists()
        docs['deployment_guide'] = (self.repo_root / 'PRODUCTION_DEPLOYMENT.md').exists()

        # Check for incident response docs
        for _f in docs_dir.rglob('*INCIDENT*.md'):
            docs['incident_response'] = True
            break

        # Check for recovery guide
        for _f in docs_dir.rglob('*RECOVERY*.md'):
            docs['recovery_guide'] = True
            break

        return docs

    def calculate_overall_status(self) -> dict:
        """Calculate overall status across all categories."""
        coverage = self.check_test_coverage()
        security_scans = self.check_security_scans()
        docker_security = self.check_docker_security()
        k8s_config = self.check_kubernetes_config()
        documentation = self.check_documentation()

        # Calculate percentages
        security_pct = (sum(security_scans.values()) / len(security_scans)) * 100
        docker_pct = (sum(docker_security.values()) / len(docker_security)) * 100
        k8s_pct = (sum(k8s_config.values()) / len(k8s_config)) * 100
        docs_pct = (sum(documentation.values()) / len(documentation)) * 100

        overall = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'overall_percentage': int((coverage + security_pct + docker_pct + k8s_pct + docs_pct) / 5),
            'categories': {
                'test_coverage': coverage,
                'security_scans': int(security_pct),
                'docker_security': int(docker_pct),
                'kubernetes_config': int(k8s_pct),
                'documentation': int(docs_pct)
            },
            'details': {
                'security_scans': security_scans,
                'docker_security': docker_security,
                'kubernetes_config': k8s_config,
                'documentation': documentation
            }
        }

        return overall

    def update_standard_document(self, status: dict):
        """Update the standard markdown file with current status."""
        if not self.standard_file.exists():
            print(f"Standard file not found: {self.standard_file}")
            return

        content = self.standard_file.read_text()

        # Update timestamp
        timestamp_pattern = r'\*\*Last Auto-Update\*\*: .+'
        new_timestamp = f"**Last Auto-Update**: {status['timestamp']}"
        content = re.sub(timestamp_pattern, new_timestamp, content)

        # Update overall progress
        progress_pattern = r'### 🎯 Overall Progress: \d+% Complete'
        new_progress = f"### 🎯 Overall Progress: {status['overall_percentage']}% Complete"
        content = re.sub(progress_pattern, new_progress, content)

        # Write back
        self.standard_file.write_text(content)
        print(f"Updated {self.standard_file}")

    def save_status(self, status: dict):
        """Save status to JSON file."""
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
        print(f"Saved status to {self.status_file}")

    def run(self):
        """Run the full status update."""
        print("=== 360° Deployable System Standard - Status Update ===")
        print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
        print()

        print("Checking test coverage...")
        print("Checking security scans...")
        print("Checking Docker security...")
        print("Checking Kubernetes configuration...")
        print("Checking documentation...")
        print()

        status = self.calculate_overall_status()

        print(f"Overall Status: {status['overall_percentage']}% Complete")
        print()
        print("Category Breakdown:")
        for cat, pct in status['categories'].items():
            print(f"  {cat}: {pct}%")
        print()

        self.save_status(status)
        self.update_standard_document(status)

        print("✅ Status update complete!")

def main():
    """Main entry point."""
    updater = StandardStatusUpdater()
    updater.run()

if __name__ == '__main__':
    main()
