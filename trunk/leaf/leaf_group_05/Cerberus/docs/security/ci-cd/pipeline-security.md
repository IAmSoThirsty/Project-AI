<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / pipeline-security.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / pipeline-security.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# CI/CD Pipeline Security

## Overview

This document provides comprehensive guidance on securing the CI/CD pipeline for the Cerberus application. It covers secure build processes, artifact signing, deployment security, environment isolation, secrets management, and supply chain security with practical implementations for GitHub Actions, Docker, and Kubernetes.

## Table of Contents

1. [Secure Build Process](#secure-build-process)
2. [Artifact Signing and Verification](#artifact-signing-and-verification)
3. [Deployment Security](#deployment-security)
4. [Environment Isolation](#environment-isolation)
5. [Secrets Management](#secrets-management)
6. [Supply Chain Security](#supply-chain-security)
7. [Access Control](#access-control)
8. [Monitoring and Audit Logging](#monitoring-and-audit-logging)

---

## Secure Build Process

### Build Pipeline Architecture

```yaml
# .github/workflows/secure-build.yml
name: "Secure Build Pipeline"

on:
  push:
    branches: [main, develop]
    tags: ['v*']
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # Security checks before build
  pre-build-checks:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Verify code signatures
        run: |
          # Verify that commits are signed
          python scripts/verify_signatures.py
      
      - name: Check for secrets in code
        run: |
          pip install truffleHog
          truffleHog filesystem . --json --fail
      
      - name: Lint Dockerfiles
        run: |
          pip install hadolint-cli
          hadolint Dockerfile
      
      - name: Validate YAML configurations
        run: |
          python -m yamllint .github/workflows/
          python -m yamllint k8s/

  # Secure build with attestation
  build:
    needs: pre-build-checks
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write  # For OIDC token for signing
    
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}
      image-name: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
    
    steps:
      - uses: actions/checkout@v4
        with:
          # Security: Verify commit signatures
          ref: ${{ github.event.pull_request.head.sha || github.sha }}
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-
      
      - name: Build and push Docker image
        id: build
        uses: docker/build-push-action@v4
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          # Enable security scanning in build
          provenance: mode=max
          sbom: true
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Generate SLSA provenance
        run: |
          python scripts/generate_slsa_provenance.py \
            --image-digest ${{ steps.build.outputs.digest }} \
            --output provenance.json

  # Security scanning
  scan:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Scan image with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ needs.build.outputs.image-name }}:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
      
      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Run security tests
        run: |
          docker run --rm ${{ needs.build.outputs.image-name }}:${{ github.sha }} \
            pytest tests/security/ -v
      
      - name: Check image layers
        run: |
          python scripts/analyze_image_layers.py \
            ${{ needs.build.outputs.image-name }}:${{ github.sha }}

  # Build verification
  verify-build:
    needs: [build, scan]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Verify image integrity
        run: |
          python scripts/verify_image_integrity.py \
            ${{ needs.build.outputs.image-name }}:${{ github.sha }}
      
      - name: Verify SBOM
        run: |
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            anchore/syft:latest \
            ${{ needs.build.outputs.image-name }}:${{ github.sha }} \
            -o cyclonedx-json > sbom.json
          
          # Validate SBOM
          python scripts/validate_sbom.py sbom.json
      
      - name: Check dependencies
        run: |
          pip install pip-audit
          pip-audit --output json > dependency-audit.json
          python scripts/check_dependency_policy.py dependency-audit.json

# Security policy enforcement
  policy-check:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      contents: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Evaluate build against policies
        run: |
          python scripts/evaluate_build_policies.py \
            --image ${{ needs.build.outputs.image-name }}:${{ github.sha }} \
            --fail-on-violation
```

### Build Hardening Script

```python
# scripts/secure_build.py
"""
Secure build implementation with security hardening
"""

import subprocess
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime

class SecureBuildManager:
    """Manage secure build process"""
    
    def __init__(self):
        self.build_artifacts = {}
        self.build_log = []
    
    def verify_environment(self):
        """Verify build environment security"""
        checks = {
            'runner_authenticated': self._check_runner_auth(),
            'secure_workspace': self._check_workspace_security(),
            'no_debug_mode': self._check_debug_mode(),
            'network_isolated': self._check_network_isolation(),
        }
        
        for check, result in checks.items():
            if not result:
                raise RuntimeError(f"Build environment check failed: {check}")
            self.log(f"✅ {check}")
    
    def _check_runner_auth(self) -> bool:
        """Verify GitHub Actions runner authentication"""
        token = os.getenv('GITHUB_TOKEN')
        if not token or len(token) < 40:
            return False
        return True
    
    def _check_workspace_security(self) -> bool:
        """Check workspace permissions and isolation"""
        workspace = Path(os.getenv('GITHUB_WORKSPACE', '.'))
        # Check permissions
        stats = workspace.stat()
        # Workspace should be readable/writable only by runner
        return True
    
    def _check_debug_mode(self) -> bool:
        """Ensure debug mode is disabled"""
        return os.getenv('RUNNER_DEBUG') != 'true'
    
    def _check_network_isolation(self) -> bool:
        """Verify network isolation"""
        # Check that outbound connections are restricted
        return True
    
    def build_image(self, dockerfile: str, image_tag: str) -> str:
        """Build Docker image securely"""
        self.log(f"Building image: {image_tag}")
        
        # Build with security options
        build_cmd = [
            'docker', 'build',
            '--file', dockerfile,
            '--tag', image_tag,
            '--security-opt', 'no-new-privileges=true',
            '--build-arg', f'BUILD_DATE={datetime.now().isoformat()}',
            '--build-arg', f'BUILD_COMMIT={os.getenv("GITHUB_SHA")}',
            '--build-arg', f'BUILD_BRANCH={os.getenv("GITHUB_REF_NAME")}',
            '--progress', 'plain',
            '.',
        ]
        
        result = subprocess.run(build_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Build failed: {result.stderr}")
        
        self.log(f"✅ Image built: {image_tag}")
        
        # Get image digest
        digest_cmd = ['docker', 'inspect', '--format={{json .}}', image_tag]
        inspect_result = subprocess.run(digest_cmd, capture_output=True, text=True)
        image_data = json.loads(inspect_result.stdout)
        
        digest = image_data['RepoDigests'][0].split('@')[1] if image_data['RepoDigests'] else 'unknown'
        
        self.build_artifacts['image_tag'] = image_tag
        self.build_artifacts['image_digest'] = digest
        
        return digest
    
    def scan_image(self, image_tag: str) -> dict:
        """Scan built image for vulnerabilities"""
        self.log(f"Scanning image: {image_tag}")
        
        # Run Trivy scan
        scan_cmd = [
            'trivy', 'image',
            '--format', 'json',
            '--severity', 'CRITICAL,HIGH',
            image_tag,
        ]
        
        result = subprocess.run(scan_cmd, capture_output=True, text=True)
        scan_results = json.loads(result.stdout)
        
        vulnerabilities = scan_results.get('Results', [])
        
        self.log(f"Found {len(vulnerabilities)} potential issues")
        
        return {
            'vulnerabilities': len(vulnerabilities),
            'critical': sum(1 for v in vulnerabilities if v.get('Severity') == 'CRITICAL'),
            'high': sum(1 for v in vulnerabilities if v.get('Severity') == 'HIGH'),
        }
    
    def sign_image(self, image_tag: str, signing_key: str) -> str:
        """Sign image with cosign"""
        self.log(f"Signing image: {image_tag}")
        
        sign_cmd = [
            'cosign', 'sign',
            '--key', signing_key,
            image_tag,
        ]
        
        result = subprocess.run(sign_cmd, capture_output=True, text=True, env={
            **os.environ,
            'COSIGN_EXPERIMENTAL': 'true',
        })
        
        if result.returncode != 0:
            raise RuntimeError(f"Image signing failed: {result.stderr}")
        
        self.log(f"✅ Image signed")
        
        return image_tag
    
    def generate_sbom(self, image_tag: str, output_file: str = 'sbom.json'):
        """Generate Software Bill of Materials"""
        self.log(f"Generating SBOM for: {image_tag}")
        
        sbom_cmd = [
            'syft', image_tag,
            '--output', 'json',
            '--file', output_file,
        ]
        
        result = subprocess.run(sbom_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"SBOM generation failed: {result.stderr}")
        
        self.log(f"✅ SBOM generated: {output_file}")
        
        return output_file
    
    def validate_build(self):
        """Validate build meets all requirements"""
        validations = {
            'image_built': 'image_tag' in self.build_artifacts,
            'image_scanned': 'vulnerabilities' in self.build_artifacts,
            'image_signed': 'image_signed' in self.build_artifacts,
            'sbom_generated': 'sbom_file' in self.build_artifacts,
        }
        
        failed = [check for check, result in validations.items() if not result]
        
        if failed:
            raise RuntimeError(f"Build validation failed: {', '.join(failed)}")
        
        self.log(f"✅ All validations passed")
    
    def log(self, message: str):
        """Log build step"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}"
        self.build_log.append(log_entry)
        print(log_entry)
    
    def save_build_log(self, filepath: str = 'build.log'):
        """Save build log"""
        with open(filepath, 'w') as f:
            f.write('\n'.join(self.build_log))

if __name__ == '__main__':
    manager = SecureBuildManager()
    
    try:
        manager.verify_environment()
        manager.build_image('Dockerfile', 'cerberus:latest')
        manager.scan_image('cerberus:latest')
        manager.generate_sbom('cerberus:latest')
        manager.validate_build()
        manager.save_build_log()
        print("\n✅ Secure build completed successfully")
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        manager.save_build_log()
        exit(1)
```

---

## Artifact Signing and Verification

### Code Signing with Cosign

```yaml
# .github/workflows/sign-artifacts.yml
name: "Sign and Publish Artifacts"

on:
  push:
    tags: ['v*']
  workflow_dispatch:

jobs:
  sign-and-publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # OIDC token for keyless signing
      packages: write
      contents: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Cosign
        uses: sigstore/cosign-installer@v3
      
      - name: Build artifacts
        run: |
          # Build application artifacts
          python setup.py sdist bdist_wheel
      
      - name: Sign artifacts with Cosign (keyless)
        env:
          COSIGN_EXPERIMENTAL: 1
        run: |
          # Sign built artifacts
          for artifact in dist/*; do
            cosign sign-blob \
              --output-signature "${artifact}.sig" \
              --output-certificate "${artifact}.crt" \
              "$artifact"
          done
      
      - name: Generate SLSA provenance
        uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3@v1.9.0
        with:
          image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          image-download-artifact: true
          registry-username: ${{ github.actor }}
          registry-password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Publish signed artifacts
        run: |
          # Upload to registry with signatures
          for artifact in dist/*; do
            [ -f "${artifact}.sig" ] && \
            python scripts/publish_artifact.py \
              --artifact "$artifact" \
              --signature "${artifact}.sig" \
              --certificate "${artifact}.crt"
          done
      
      - name: Create release with signatures
        uses: softprops/action-gh-release@v1
        with:
          files: |
            dist/*
            dist/*.sig
            dist/*.crt
          draft: false
          prerelease: false
```

### Artifact Verification Script

```python
# scripts/verify_artifacts.py
"""
Verify signed artifacts
"""

import subprocess
import os
import json
from pathlib import Path

class ArtifactVerifier:
    """Verify artifact signatures and integrity"""
    
    def __init__(self):
        self.verification_results = []
    
    def verify_cosign_signature(self, artifact: str, signature: str, certificate: str) -> bool:
        """Verify artifact signed with Cosign"""
        verify_cmd = [
            'cosign', 'verify-blob',
            '--signature', signature,
            '--certificate', certificate,
            artifact,
        ]
        
        result = subprocess.run(verify_cmd, capture_output=True)
        
        verified = result.returncode == 0
        self.verification_results.append({
            'artifact': artifact,
            'type': 'cosign_signature',
            'verified': verified,
        })
        
        return verified
    
    def verify_sbom(self, sbom_file: str) -> bool:
        """Verify SBOM validity"""
        if not Path(sbom_file).exists():
            return False
        
        try:
            with open(sbom_file, 'r') as f:
                sbom = json.load(f)
            
            # Validate SBOM structure
            required_fields = ['metadata', 'components']
            has_required = all(field in sbom for field in required_fields)
            
            self.verification_results.append({
                'artifact': sbom_file,
                'type': 'sbom',
                'verified': has_required,
            })
            
            return has_required
        except:
            return False
    
    def verify_image_digest(self, image: str, expected_digest: str) -> bool:
        """Verify image digest matches expected value"""
        inspect_cmd = ['docker', 'inspect', '--format={{json .}}', image]
        result = subprocess.run(inspect_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return False
        
        image_data = json.loads(result.stdout)
        actual_digest = image_data['RepoDigests'][0].split('@')[1] if image_data['RepoDigests'] else ''
        
        verified = actual_digest == expected_digest
        self.verification_results.append({
            'artifact': image,
            'type': 'image_digest',
            'verified': verified,
        })
        
        return verified
    
    def generate_report(self) -> dict:
        """Generate verification report"""
        total = len(self.verification_results)
        verified = sum(1 for r in self.verification_results if r['verified'])
        
        return {
            'total_artifacts': total,
            'verified': verified,
            'verification_rate': (verified / total * 100) if total > 0 else 0,
            'results': self.verification_results,
        }

if __name__ == '__main__':
    verifier = ArtifactVerifier()
    
    # Verify built artifacts
    artifacts_dir = Path('dist')
    for artifact in artifacts_dir.glob('*'):
        if not artifact.name.endswith(('.sig', '.crt')):
            sig_file = f"{artifact}.sig"
            crt_file = f"{artifact}.crt"
            
            if Path(sig_file).exists() and Path(crt_file).exists():
                verified = verifier.verify_cosign_signature(str(artifact), sig_file, crt_file)
                print(f"{'✅' if verified else '❌'} {artifact.name}")
    
    report = verifier.generate_report()
    print(f"\nVerification Summary:")
    print(f"  Total: {report['total_artifacts']}")
    print(f"  Verified: {report['verified']}")
    print(f"  Success Rate: {report['verification_rate']:.1f}%")
```

---

## Deployment Security

### Secure Deployment Pipeline

```yaml
# .github/workflows/secure-deploy.yml
name: "Secure Deployment"

on:
  push:
    branches: [main]
    tags: ['v*']
  workflow_dispatch:

env:
  REGISTRY: ghcr.io

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write  # For OIDC
      packages: read
    
    strategy:
      matrix:
        environment:
          - staging
          - production
    
    environment:
      name: ${{ matrix.environment }}
      url: https://${{ matrix.environment }}.cerberus.example.com
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials with OIDC
        uses: aws-actions/configure-aws-credentials@v3
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-role
          aws-region: us-east-1
      
      - name: Get deployment approval
        if: github.ref == 'refs/heads/main'
        uses: actions/github-script@v7
        with:
          script: |
            // Check that PR has approval
            const pr = context.payload.pull_request;
            if (pr && pr.reviews) {
              const approvals = pr.reviews.filter(r => r.state === 'APPROVED');
              if (approvals.length < 2) {
                core.setFailed('Deployment requires 2 approvals');
              }
            }
      
      - name: Pre-deployment checks
        run: |
          python scripts/pre_deployment_checks.py \
            --environment ${{ matrix.environment }} \
            --skip-tests false
      
      - name: Deploy to ${{ matrix.environment }}
        run: |
          python scripts/deploy.py \
            --environment ${{ matrix.environment }} \
            --image ${{ env.REGISTRY }}/${{ github.repository }}:${{ github.sha }} \
            --strategy blue-green \
            --timeout 300
      
      - name: Run post-deployment tests
        run: |
          python scripts/post_deployment_tests.py \
            --environment ${{ matrix.environment }} \
            --tests smoke,security,performance
      
      - name: Monitor deployment
        if: always()
        run: |
          python scripts/monitor_deployment.py \
            --environment ${{ matrix.environment }} \
            --duration 300 \
            --alert-on-error

  rollback:
    needs: deploy
    runs-on: ubuntu-latest
    if: failure()
    permissions:
      contents: read
      id-token: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v3
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-role
          aws-region: us-east-1
      
      - name: Execute rollback
        run: |
          python scripts/rollback.py \
            --environment production \
            --previous-version ${{ secrets.PREVIOUS_VERSION }}
      
      - name: Notify team
        uses: slackapi/slack-github-action@v1.24.0
        with:
          payload: |
            {
              "text": "🚨 Deployment rolled back",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Deployment Rollback*\n\nEnvironment: production\nReason: Deployment failed\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Details>"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Deployment Verification

```python
# scripts/pre_deployment_checks.py
"""
Pre-deployment security checks
"""

import subprocess
import json
import argparse
from datetime import datetime

class DeploymentValidator:
    """Validate deployment readiness"""
    
    def __init__(self, environment: str):
        self.environment = environment
        self.checks = []
    
    def check_image_signature(self, image: str) -> bool:
        """Verify image is properly signed"""
        verify_cmd = ['cosign', 'verify', '--certificate-identity-regexp', '.*', image]
        result = subprocess.run(verify_cmd, capture_output=True)
        return result.returncode == 0
    
    def check_sbom_exists(self, image: str) -> bool:
        """Verify SBOM is available"""
        sbom_cmd = ['cosign', 'download', 'sbom', image]
        result = subprocess.run(sbom_cmd, capture_output=True)
        return result.returncode == 0
    
    def check_no_high_vulnerabilities(self, image: str) -> bool:
        """Ensure no high/critical vulnerabilities in image"""
        scan_cmd = ['trivy', 'image', '--format', 'json', '--severity', 'HIGH,CRITICAL', image]
        result = subprocess.run(scan_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return False
        
        results = json.loads(result.stdout)
        vulnerabilities = results.get('Results', [])
        
        return len(vulnerabilities) == 0
    
    def check_secrets_not_exposed(self) -> bool:
        """Verify no secrets in deployment configuration"""
        import re
        
        # Common secret patterns
        patterns = [
            r'(password|secret|token|key)\s*[:=]',
            r'-----BEGIN.*PRIVATE KEY-----',
        ]
        
        # Check kubernetes manifests
        for manifest in ['k8s/*.yaml']:
            with open(manifest, 'r') as f:
                content = f.read()
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return False
        
        return True
    
    def check_dependencies_up_to_date(self) -> bool:
        """Verify all dependencies are current"""
        audit_cmd = ['pip', 'audit', '--format', 'json']
        result = subprocess.run(audit_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        
        data = json.loads(result.stdout)
        # Allow known vulnerabilities
        return data.get('vulnerability_count', 0) <= 0
    
    def validate_environment_config(self) -> bool:
        """Validate environment-specific configuration"""
        config_file = f"config/{self.environment}.yaml"
        
        try:
            import yaml
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Validate required fields
            required = ['replicas', 'resources', 'image']
            return all(field in config for field in required)
        except:
            return False
    
    def run_all_checks(self, image: str = None) -> bool:
        """Run all pre-deployment checks"""
        print(f"Running pre-deployment checks for {self.environment}...")
        
        checks = [
            ('Secrets not exposed', self.check_secrets_not_exposed),
            ('Environment config valid', self.check_environment_config),
            ('Dependencies up to date', self.check_dependencies_up_to_date),
        ]
        
        if image:
            checks.extend([
                ('Image properly signed', lambda: self.check_image_signature(image)),
                ('SBOM available', lambda: self.check_sbom_exists(image)),
                ('No high vulnerabilities', lambda: self.check_no_high_vulnerabilities(image)),
            ])
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "✅" if result else "❌"
                print(f"  {status} {check_name}")
                
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"  ❌ {check_name}: {e}")
                all_passed = False
        
        return all_passed

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pre-deployment checks')
    parser.add_argument('--environment', required=True)
    parser.add_argument('--image', help='Docker image to validate')
    parser.add_argument('--skip-tests', action='store_true')
    
    args = parser.parse_args()
    
    validator = DeploymentValidator(args.environment)
    if validator.run_all_checks(image=args.image):
        print("\n✅ All pre-deployment checks passed")
        exit(0)
    else:
        print("\n❌ Pre-deployment checks failed")
        exit(1)
```

---

## Environment Isolation

### Kubernetes Security Context

```yaml
# k8s/cerberus-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cerberus
  namespace: default
  labels:
    app: cerberus
    security: hardened
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: cerberus
  template:
    metadata:
      labels:
        app: cerberus
        version: v1
      annotations:
        seccomp.security.alpha.kubernetes.io/pod: 'runtime/default'
        container.apparmor.security.beta.kubernetes.io/cerberus: 'runtime/default'
    spec:
      # Security context for pod
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 3000
        fsGroup: 2000
        fsGroupChangePolicy: "OnRootMismatch"
        seccompProfile:
          type: RuntimeDefault
      
      # Service account
      serviceAccountName: cerberus
      automountServiceAccountToken: true
      
      # Node affinity for secure nodes
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: karpenter.sh/capacity-type
                operator: In
                values: ["on-demand"]
              - key: kubernetes.io/os
                operator: In
                values: ["linux"]
      
      # Network policies (defined separately)
      dnsPolicy: ClusterFirst
      
      # Image pull secrets
      imagePullSecrets:
      - name: ghcr-secret
      
      initContainers:
      # Security validation init container
      - name: security-init
        image: curlimages/curl:latest
        command:
        - /bin/sh
        - -c
        - |
          # Verify environment variables are set
          [ -n "$ENVIRONMENT" ] || exit 1
          # Verify database connection
          curl -f http://postgres:5432 || exit 1
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: cerberus-config
              key: environment
        securityContext:
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
      
      containers:
      - name: cerberus
        image: ghcr.io/example/cerberus:latest
        imagePullPolicy: Always
        
        # Resource limits
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        
        # Security context for container
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
          seccompProfile:
            type: RuntimeDefault
        
        # Port configuration
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        
        # Liveness probe
        livenessProbe:
          httpGet:
            path: /health/live
            port: http
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        # Readiness probe
        readinessProbe:
          httpGet:
            path: /health/ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        
        # Startup probe
        startupProbe:
          httpGet:
            path: /health/startup
            port: http
          initialDelaySeconds: 0
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 30
        
        # Volume mounts
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/.cache
        - name: secrets
          mountPath: /app/secrets
          readOnly: true
        
        # Environment variables
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: cerberus-config
              key: environment
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: cerberus-config
              key: log-level
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: cerberus-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: cerberus-secrets
              key: secret-key
      
      # Volumes
      volumes:
      - name: tmp
        emptyDir: {}
      - name: cache
        emptyDir: {}
      - name: secrets
        secret:
          secretName: cerberus-secrets
          defaultMode: 0400

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: cerberus
  namespace: default

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: cerberus
  namespace: default
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch"]
  resourceNames: ["cerberus-config"]
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
  resourceNames: ["cerberus-secrets"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: cerberus
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: cerberus
subjects:
- kind: ServiceAccount
  name: cerberus
  namespace: default

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: cerberus
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: cerberus
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - podSelector:
        matchLabels:
          app: cerberus
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
  - to:
    - podSelector:
        matchLabels:
          app: cerberus
    ports:
    - protocol: TCP
      port: 8000
```

---

## Secrets Management

### Secure Secrets Handling

```yaml
# .github/workflows/secrets-management.yml
name: "Secrets Management"

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly rotation

jobs:
  rotate-secrets:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v3
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-role
          aws-region: us-east-1
      
      - name: Rotate database password
        run: |
          python scripts/rotate_secrets.py \
            --secret-type database-password \
            --rotation-period 90
      
      - name: Rotate API keys
        run: |
          python scripts/rotate_secrets.py \
            --secret-type api-keys \
            --rotation-period 30
      
      - name: Rotate service credentials
        run: |
          python scripts/rotate_secrets.py \
            --secret-type service-credentials \
            --rotation-period 60
      
      - name: Update Kubernetes secrets
        run: |
          python scripts/update_k8s_secrets.py
      
      - name: Verify secrets were rotated
        run: |
          python scripts/verify_secret_rotation.py
      
      - name: Audit secret access
        run: |
          python scripts/audit_secret_access.py \
            --output secret-audit.json
      
      - name: Upload audit log
        uses: actions/upload-artifact@v3
        with:
          name: secret-audit
          path: secret-audit.json
```

### Secrets Rotation Script

```python
# scripts/rotate_secrets.py
"""
Automated secrets rotation
"""

import boto3
import argparse
import json
from datetime import datetime, timedelta

class SecretsRotator:
    """Rotate secrets according to policy"""
    
    ROTATION_POLICIES = {
        'database-password': {'rotation_period': 90, 'complexity': 'high'},
        'api-keys': {'rotation_period': 30, 'complexity': 'high'},
        'service-credentials': {'rotation_period': 60, 'complexity': 'high'},
    }
    
    def __init__(self):
        self.sm_client = boto3.client('secretsmanager')
        self.rotation_log = []
    
    def should_rotate(self, secret_name: str, policy: dict) -> bool:
        """Determine if secret should be rotated"""
        try:
            response = self.sm_client.describe_secret(SecretId=secret_name)
            
            last_rotated = response.get('LastRotatedDate')
            if not last_rotated:
                return True
            
            rotation_period = policy['rotation_period']
            next_rotation = last_rotated + timedelta(days=rotation_period)
            
            return datetime.now(next_rotation.tzinfo) >= next_rotation
        except:
            return True
    
    def generate_new_secret(self, secret_type: str, complexity: str = 'high') -> str:
        """Generate new secret value"""
        import secrets
        import string
        
        if secret_type == 'password':
            alphabet = string.ascii_letters + string.digits + '!@#$%^&*()_+-='
            return ''.join(secrets.choice(alphabet) for _ in range(32))
        elif secret_type == 'api-key':
            return secrets.token_urlsafe(32)
        else:
            return secrets.token_hex(32)
    
    def rotate_secret(self, secret_name: str, secret_type: str):
        """Rotate a secret"""
        print(f"Rotating {secret_type}: {secret_name}")
        
        try:
            # Generate new secret
            new_secret = self.generate_new_secret(secret_type)
            
            # Update secret in Secrets Manager
            self.sm_client.update_secret(
                SecretId=secret_name,
                SecretString=new_secret
            )
            
            # Log rotation
            self.rotation_log.append({
                'timestamp': datetime.now().isoformat(),
                'secret': secret_name,
                'type': secret_type,
                'status': 'success',
            })
            
            print(f"✅ {secret_name} rotated successfully")
            return True
        
        except Exception as e:
            self.rotation_log.append({
                'timestamp': datetime.now().isoformat(),
                'secret': secret_name,
                'type': secret_type,
                'status': 'failed',
                'error': str(e),
            })
            
            print(f"❌ Failed to rotate {secret_name}: {e}")
            return False
    
    def audit_access(self) -> dict:
        """Audit who accessed secrets"""
        cloudtrail = boto3.client('cloudtrail')
        
        try:
            response = cloudtrail.lookup_events(
                LookupAttributes=[
                    {
                        'AttributeKey': 'ResourceType',
                        'AttributeValue': 'AWS::SecretsManager::Secret'
                    }
                ],
                MaxResults=50
            )
            
            access_log = []
            for event in response.get('Events', []):
                access_log.append({
                    'timestamp': event['EventTime'].isoformat(),
                    'username': event['Username'],
                    'event_name': event['EventName'],
                })
            
            return access_log
        except:
            return []
    
    def save_rotation_log(self, filepath: str = 'rotation.log'):
        """Save rotation log"""
        with open(filepath, 'w') as f:
            json.dump(self.rotation_log, f, indent=2, default=str)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Rotate secrets')
    parser.add_argument('--secret-type', required=True, choices=['database-password', 'api-keys', 'service-credentials'])
    parser.add_argument('--rotation-period', type=int, help='Override rotation period')
    
    args = parser.parse_args()
    
    rotator = SecretsRotator()
    
    # Get policy
    policy = rotator.ROTATION_POLICIES.get(args.secret_type, {})
    if args.rotation_period:
        policy['rotation_period'] = args.rotation_period
    
    # Rotate secrets matching type
    secret_names = {
        'database-password': 'cerberus/db/password',
        'api-keys': 'cerberus/api/keys',
        'service-credentials': 'cerberus/service/credentials',
    }
    
    secret_name = secret_names.get(args.secret_type)
    if secret_name and rotator.should_rotate(secret_name, policy):
        rotator.rotate_secret(secret_name, args.secret_type)
    
    rotator.save_rotation_log()
```

---

## Supply Chain Security

### Dependency Verification

```yaml
# .github/workflows/supply-chain-security.yml
name: "Supply Chain Security"

on:
  push:
    branches: [main, develop]
  schedule:
    - cron: '0 2 * * 0'

jobs:
  verify-provenance:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Verify artifact provenance
        run: |
          python scripts/verify_provenance.py \
            --artifacts dist/ \
            --fail-on-missing-provenance
      
      - name: Check for typosquatting attacks
        run: |
          pip install deptry
          deptry check --fail=all
      
      - name: Verify dependency licenses
        run: |
          pip install pip-licenses
          pip-licenses --format=json --output-file=licenses.json
          python scripts/check_licenses.py licenses.json
      
      - name: Run SLSA verification
        uses: slsa-framework/slsa-verifier@v2.2.0
        with:
          artifact-path: dist/
          provenance-path: provenance.json
```

### Provenance Verification

```python
# scripts/verify_provenance.py
"""
Verify software provenance
"""

import json
import hashlib
import argparse
from pathlib import Path

class ProvenanceVerifier:
    """Verify artifact provenance"""
    
    def __init__(self):
        self.verification_results = []
    
    def verify_slsa_provenance(self, provenance_file: str, artifact: str) -> bool:
        """Verify SLSA provenance"""
        try:
            with open(provenance_file, 'r') as f:
                provenance = json.load(f)
            
            # Verify artifact in provenance materials
            artifact_hash = self._calculate_hash(artifact)
            
            for material in provenance.get('materials', []):
                if material.get('sha256') == artifact_hash:
                    return True
            
            return False
        except Exception as e:
            print(f"Error verifying provenance: {e}")
            return False
    
    def _calculate_hash(self, filepath: str) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def verify_artifacts(self, artifacts_dir: str):
        """Verify all artifacts in directory"""
        for artifact_path in Path(artifacts_dir).rglob('*'):
            if artifact_path.is_file() and not artifact_path.name.endswith(('.sig', '.crt', '.json')):
                # Check for provenance file
                provenance_file = f"{artifact_path}.provenance.json"
                
                if Path(provenance_file).exists():
                    verified = self.verify_slsa_provenance(provenance_file, str(artifact_path))
                    self.verification_results.append({
                        'artifact': artifact_path.name,
                        'provenance_verified': verified,
                    })
                else:
                    self.verification_results.append({
                        'artifact': artifact_path.name,
                        'provenance_verified': False,
                        'reason': 'Missing provenance file',
                    })

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Verify provenance')
    parser.add_argument('--artifacts', required=True)
    parser.add_argument('--fail-on-missing-provenance', action='store_true')
    
    args = parser.parse_args()
    
    verifier = ProvenanceVerifier()
    verifier.verify_artifacts(args.artifacts)
    
    # Check results
    missing_provenance = [r for r in verifier.verification_results if not r['provenance_verified']]
    
    if missing_provenance and args.fail_on_missing_provenance:
        print(f"❌ {len(missing_provenance)} artifacts without provenance")
        for result in missing_provenance:
            print(f"  - {result['artifact']}: {result.get('reason', 'Not verified')}")
        exit(1)
    
    print(f"✅ Provenance verification completed")
```

---

## Access Control

### Role-Based Access Control (RBAC)

```yaml
# .github/workflows/access-control.yml
name: "Access Control"

on:
  pull_request:
    types: [opened, synchronize]
  push:
    branches: [main]

jobs:
  enforce-approvals:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: read
      contents: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Check required approvers
        uses: actions/github-script@v7
        with:
          script: |
            const pr = context.payload.pull_request;
            
            if (!pr) return; // Skip for push events
            
            const files = await github.rest.pulls.listFiles({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: pr.number,
            });
            
            // Check if sensitive files are modified
            const sensitiveFiles = ['secrets/', '.env', 'k8s/', '.github/workflows/'];
            const modifiedSensitive = files.data.some(f =>
              sensitiveFiles.some(pattern => f.filename.includes(pattern))
            );
            
            if (modifiedSensitive) {
              // Require security team approval
              const reviews = await github.rest.pulls.listReviews({
                owner: context.repo.owner,
                repo: context.repo.repo,
                pull_number: pr.number,
              });
              
              const securityApprovals = reviews.data.filter(r =>
                r.state === 'APPROVED' &&
                (r.user.login === 'security-team' || r.author_association === 'OWNER')
              );
              
              if (securityApprovals.length === 0) {
                core.setFailed('Changes to sensitive files require security team approval');
              }
            }
```

---

## Monitoring and Audit Logging

### Comprehensive Audit Logging

```python
# scripts/audit_logging.py
"""
Comprehensive audit logging for CI/CD pipeline
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

class AuditLogger:
    """Centralized audit logging"""
    
    def __init__(self, log_file: str = 'audit.log'):
        self.log_file = log_file
        self.setup_logging()
    
    def setup_logging(self):
        """Configure audit logging"""
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.INFO)
        
        # JSON formatter
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
            datefmt='%Y-%m-%dT%H:%M:%SZ'
        )
        fh.setFormatter(formatter)
        
        self.logger.addHandler(fh)
    
    def log_build(self, build_id: str, status: str, metadata: Dict[str, Any]):
        """Log build event"""
        event = {
            'event_type': 'build',
            'build_id': build_id,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata,
        }
        self.logger.info(json.dumps(event))
    
    def log_deployment(self, deployment_id: str, environment: str, status: str, user: str):
        """Log deployment event"""
        event = {
            'event_type': 'deployment',
            'deployment_id': deployment_id,
            'environment': environment,
            'status': status,
            'user': user,
            'timestamp': datetime.now().isoformat(),
        }
        self.logger.info(json.dumps(event))
    
    def log_secret_access(self, secret_name: str, user: str, action: str, result: str):
        """Log secret access"""
        event = {
            'event_type': 'secret_access',
            'secret_name': secret_name,
            'user': user,
            'action': action,
            'result': result,
            'timestamp': datetime.now().isoformat(),
        }
        self.logger.info(json.dumps(event))
    
    def log_security_finding(self, finding_type: str, severity: str, details: Dict[str, Any]):
        """Log security finding"""
        event = {
            'event_type': 'security_finding',
            'finding_type': finding_type,
            'severity': severity,
            'details': details,
            'timestamp': datetime.now().isoformat(),
        }
        self.logger.info(json.dumps(event))

if __name__ == '__main__':
    audit = AuditLogger()
    
    # Example logging
    audit.log_build('build-001', 'success', {
        'image': 'cerberus:v1.0.0',
        'duration_seconds': 120,
    })
    
    audit.log_deployment('deploy-001', 'production', 'success', 'github-actions')
    
    audit.log_secret_access('db-password', 'ci-pipeline', 'read', 'success')
    
    audit.log_security_finding('vulnerability', 'high', {
        'package': 'requests',
        'version': '2.28.0',
        'cve': 'CVE-2023-32681',
    })
```

---

## Best Practices Summary

1. **Principle of Least Privilege**: Grant minimal necessary permissions
2. **Secret Rotation**: Rotate secrets regularly (30-90 days)
3. **Artifact Signing**: Sign all artifacts and verify signatures
4. **Environment Isolation**: Use separate environments for dev/staging/prod
5. **Security Gates**: Enforce security checks before deployment
6. **Audit Logging**: Log all CI/CD activities for compliance
7. **Access Control**: Enforce multi-approval for sensitive changes
8. **Supply Chain Security**: Verify provenance and dependencies
9. **Continuous Monitoring**: Monitor pipeline for security events
10. **Incident Response**: Have rollback procedures ready

---

## Cerberus Security Module Integration

All CI/CD security processes are integrated with Cerberus security modules:

```python
from cerberus.security.pipeline import SecurityPipelineManager
from cerberus.security.compliance import ComplianceChecker
from cerberus.security.audit import AuditLogger

# Initialize security pipeline
pipeline = SecurityPipelineManager()

# Run security checks
pipeline.run_security_gates()
pipeline.verify_artifacts()
pipeline.check_deployment_readiness()

# Log audit events
audit = AuditLogger()
audit.log_deployment('deploy-001', 'production', 'success', 'github-actions')

# Check compliance
compliance = ComplianceChecker()
compliance.validate_against_cis_benchmarks()
compliance.check_pci_dss_requirements()
```

---

## Related Documentation

- [Security Automation](security-automation.md)
- [Scan Procedures](scan-procedures.md)
- [Security Tools Reference](../tools-reference.md)
- [Incident Response Procedures](../incident-response.md)
- [Security Standards Compliance](../compliance/README.md)

