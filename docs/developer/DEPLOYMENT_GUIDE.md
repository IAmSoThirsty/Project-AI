# Secure AI Deployment Lifecycle - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying Project-AI with comprehensive security controls across all phases of the deployment lifecycle.

## Table of Contents

1. [Phase 1: Local Development Setup](#phase-1-local-development-setup)
1. [Phase 2: Testing and Validation](#phase-2-testing-and-validation)
1. [Phase 3: Cloud Deployment Preparation](#phase-3-cloud-deployment-preparation)
1. [Phase 4: Production Deployment](#phase-4-production-deployment)
1. [Phase 5: Post-Deployment Monitoring](#phase-5-post-deployment-monitoring)
1. [Phase 6: Ongoing Maintenance](#phase-6-ongoing-maintenance)

______________________________________________________________________

## Phase 1: Local Development Setup

### 1.1 Environment Preparation

```bash

# Create virtual environment

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies

pip install -r requirements.txt

# Verify installation

python -c "from app.security import EnvironmentHardening; print('Security framework imported successfully')"
```

### 1.2 Environment Hardening

```python

# scripts/setup_environment.py

from app.security import EnvironmentHardening

hardening = EnvironmentHardening()

# Run comprehensive validation

is_valid, issues = hardening.validate_environment()

if issues:
    print("Security issues detected:")
    for issue in issues:
        print(f"  - {issue}")

    # Apply fixes

    hardening.harden_sys_path()
    hardening.secure_directory_structure()

    print("\nFixes applied. Re-running validation...")
    is_valid, issues = hardening.validate_environment()

if is_valid:
    print("✓ Environment is secure and ready")
else:
    print("⚠ Manual intervention required:")
    for issue in issues:
        print(f"  - {issue}")
    exit(1)

# Generate report

report = hardening.get_validation_report()
with open("security_report.json", "w") as f:
    import json
    json.dump(report, f, indent=2)
```

Run the setup:

```bash
python scripts/setup_environment.py
```

### 1.3 Configuration

Create `.env` file:

```bash

# Security

FERNET_KEY=<generate using: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">

# AWS (for cloud deployment)

AWS_REGION=us-east-1

# Do not set AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY - use IAM roles

# Monitoring

SECURITY_SNS_TOPIC=arn:aws:sns:us-east-1:123456789012:security-alerts
CLOUDWATCH_NAMESPACE=ProjectAI/Security

# Application

DATABASE_PATH=data/secure.db
MAX_UPLOAD_SIZE=104857600  # 100MB
```

### 1.4 Directory Structure

Ensure all required directories exist with proper permissions:

```bash

# Create directories

mkdir -p data/{ai_persona,memory,learning_requests,black_vault_secure,audit_logs,secure_backups}

# Set permissions (Unix/Linux/macOS)

chmod 700 data data/*

# Verify

ls -la data/
```

______________________________________________________________________

## Phase 2: Testing and Validation

### 2.1 Unit Tests

Run comprehensive security tests:

```bash

# All security tests

pytest tests/test_security_phase1.py tests/test_security_phase2.py -v

# With coverage report

pytest tests/test_security_phase*.py --cov=app.security --cov-report=html --cov-report=term

# View coverage report

open htmlcov/index.html  # Or your browser
```

Expected output:

```
======================== 61 passed, 1 skipped in 1.0s =========================
```

### 2.2 Integration Tests

Test security integration with main application:

```python

# tests/test_security_integration.py

import pytest
from app.security import (
    EnvironmentHardening,
    SecureDataParser,
    SecureDatabaseManager,
    SecurityMonitor,
)

def test_full_security_stack():
    """Test complete security stack integration."""

    # 1. Environment

    hardening = EnvironmentHardening()
    assert hardening.validate_environment()[0]

    # 2. Data parsing

    parser = SecureDataParser()
    result = parser.parse_json('{"test": "data"}')
    assert result.validated

    # 3. Database

    db = SecureDatabaseManager(":memory:")
    user_id = db.insert_user("testuser", "hash")
    assert user_id > 0

    # 4. Monitoring

    monitor = SecurityMonitor()
    monitor.log_security_event("test", "low", "test", "Test event")
    assert len(monitor.event_log) == 1
```

### 2.3 Penetration Testing

Run security-specific tests:

```bash

# SQL injection tests

pytest tests/test_security_phase2.py::TestSecureDatabaseManager::test_sql_injection_prevention -v

# XXE attack tests

pytest tests/test_security_phase1.py::TestSecureDataParser::test_xml_xxe_detection -v

# Fuzzing tests

pytest tests/test_security_phase2.py::TestRuntimeFuzzer -v
```

### 2.4 Performance Testing

Stress test security components:

```bash

# High-volume tests

pytest tests/test_security_phase2.py::TestSecurityStress -v

# Concurrent access

pytest tests/test_security_phase2.py::TestSecurityStress::test_concurrent_database_access -v
```

______________________________________________________________________

## Phase 3: Cloud Deployment Preparation

### 3.1 AWS IAM Setup

Create IAM role with minimal permissions (PoLP):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::project-ai-data/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:project-ai-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "cloudwatch:namespace": "ProjectAI/Security"
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:us-east-1:*:security-alerts"
    }
  ]
}
```

Create role:

```bash
aws iam create-role \
  --role-name ProjectAI-EC2-Role \
  --assume-role-policy-document file://trust-policy.json

aws iam put-role-policy \
  --role-name ProjectAI-EC2-Role \
  --policy-name ProjectAI-Security-Policy \
  --policy-document file://security-policy.json
```

### 3.2 AWS Secrets Manager

Store sensitive configuration:

```bash

# Create secret

aws secretsmanager create-secret \
  --name project-ai-secrets \
  --description "Project-AI application secrets" \
  --secret-string file://secrets.json

# Enable automatic rotation (optional)

aws secretsmanager rotate-secret \
  --secret-id project-ai-secrets \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRotation
```

secrets.json:

```json
{
  "fernet_key": "...",
  "database_encryption_key": "...",
  "api_keys": {
    "openai": "sk-...",
    "huggingface": "hf_..."
  }
}
```

### 3.3 S3 Bucket Setup

Create secure S3 bucket:

```bash

# Create bucket

aws s3 mb s3://project-ai-data --region us-east-1

# Enable versioning

aws s3api put-bucket-versioning \
  --bucket project-ai-data \
  --versioning-configuration Status=Enabled

# Enable encryption

aws s3api put-bucket-encryption \
  --bucket project-ai-data \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Block public access

aws s3api put-public-access-block \
  --bucket project-ai-data \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# Enable logging

aws s3api put-bucket-logging \
  --bucket project-ai-data \
  --bucket-logging-status '{
    "LoggingEnabled": {
      "TargetBucket": "project-ai-logs",
      "TargetPrefix": "s3-access/"
    }
  }'
```

### 3.4 CloudWatch Setup

Create CloudWatch dashboard:

```bash
aws cloudwatch put-dashboard \
  --dashboard-name ProjectAI-Security \
  --dashboard-body file://cloudwatch-dashboard.json
```

cloudwatch-dashboard.json:

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["ProjectAI/Security", "SecurityEvent_authentication_failure"],
          [".", "SecurityEvent_data_poisoning"]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "Security Events"
      }
    }
  ]
}
```

Create alarms:

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name ProjectAI-HighAuthFailures \
  --alarm-description "Alert on high authentication failures" \
  --metric-name SecurityEvent_authentication_failure \
  --namespace ProjectAI/Security \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:security-alerts
```

### 3.5 SNS Topic Setup

Create SNS topic for alerts:

```bash

# Create topic

aws sns create-topic --name security-alerts

# Subscribe email

aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:security-alerts \
  --protocol email \
  --notification-endpoint security@example.com

# Confirm subscription (check email)

```

______________________________________________________________________

## Phase 4: Production Deployment

### 4.1 EC2 Instance Launch

```bash

# Launch instance with IAM role

aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --iam-instance-profile Name=ProjectAI-EC2-Role \
  --security-group-ids sg-xxxxx \
  --subnet-id subnet-xxxxx \
  --user-data file://user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ProjectAI-Production}]'
```

user-data.sh:

```bash

#!/bin/bash

set -e

# Update system

apt-get update && apt-get upgrade -y

# Install Python 3.11

apt-get install -y python3.12 python3.12-venv python3-pip

# Create app user

useradd -m -s /bin/bash projectai

# Clone repository

cd /opt
git clone https://github.com/yourorg/Project-AI.git
cd Project-AI

# Setup virtual environment

python3.12 -m venv venv
source venv/bin/activate

# Install dependencies

pip install -r requirements.txt

# Set permissions

chown -R projectai:projectai /opt/Project-AI
chmod 700 /opt/Project-AI/data

# Run environment hardening

su - projectai -c "cd /opt/Project-AI && source venv/bin/activate && python scripts/setup_environment.py"

# Start application

systemctl enable projectai
systemctl start projectai
```

### 4.2 Docker Deployment (Alternative)

Dockerfile:

```dockerfile
FROM python:3.12-slim

# Security: Run as non-root

RUN useradd -m -u 1000 projectai

WORKDIR /app

# Copy requirements first (layer caching)

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application

COPY --chown=projectai:projectai . .

# Set secure permissions

RUN chmod 700 /app/data

# Switch to non-root user

USER projectai

# Healthcheck

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "from app.security import EnvironmentHardening; EnvironmentHardening().validate_environment()" || exit 1

# Start application

CMD ["python", "-m", "app.main"]
```

Build and deploy:

```bash

# Build

docker build -t project-ai:latest .

# Run with security

docker run -d \
  --name project-ai \
  --read-only \
  --tmpfs /tmp \
  --security-opt=no-new-privileges \
  --cap-drop=ALL \
  -e AWS_REGION=us-east-1 \
  -v /opt/project-ai/data:/app/data:rw \
  project-ai:latest
```

### 4.3 Kubernetes Deployment (Optional)

deployment.yaml:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: project-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: project-ai
  template:
    metadata:
      labels:
        app: project-ai
    spec:
      serviceAccountName: project-ai-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:

      - name: project-ai

        image: project-ai:latest
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:

            - ALL

        env:

        - name: AWS_REGION

          value: us-east-1
        volumeMounts:

        - name: data

          mountPath: /app/data

        - name: tmp

          mountPath: /tmp
        resources:
          limits:
            memory: "2Gi"
            cpu: "1000m"
          requests:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:

            - python
            - -c
            - "from app.security import EnvironmentHardening; EnvironmentHardening().validate_environment()"

          initialDelaySeconds: 30
          periodSeconds: 60
      volumes:

      - name: data

        persistentVolumeClaim:
          claimName: project-ai-data

      - name: tmp

        emptyDir: {}
```

______________________________________________________________________

## Phase 5: Post-Deployment Monitoring

### 5.1 Verify Deployment

```bash

# SSH into instance

ssh -i key.pem ubuntu@instance-ip

# Check application logs

sudo journalctl -u projectai -f

# Verify security

sudo -u projectai /opt/Project-AI/venv/bin/python << 'EOF'
from app.security import EnvironmentHardening, SecurityMonitor

# Check environment

hardening = EnvironmentHardening()
is_valid, issues = hardening.validate_environment()
print(f"Environment valid: {is_valid}")
if issues:
    print(f"Issues: {issues}")

# Check monitoring

monitor = SecurityMonitor()
monitor.log_security_event(
    event_type="deployment_verification",
    severity="low",
    source="deployment",
    description="Deployment verification check"
)
print(f"Monitoring working: {len(monitor.event_log) > 0}")
EOF
```

### 5.2 CloudWatch Verification

Check CloudWatch console:

```bash

# View metrics

aws cloudwatch get-metric-statistics \
  --namespace ProjectAI/Security \
  --metric-name SecurityEvent_deployment_verification \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum

# Check alarms

aws cloudwatch describe-alarms \
  --alarm-names ProjectAI-HighAuthFailures
```

### 5.3 Security Audit

Run post-deployment security audit:

```python

# scripts/audit_deployment.py

from app.security import AWSSecurityManager, SecurityMonitor
import json

# Initialize

aws = AWSSecurityManager()
monitor = SecurityMonitor()

# Audit IAM permissions

audit = aws.audit_iam_permissions()
print("IAM Audit:")
print(json.dumps(audit, indent=2, default=str))

# Validate PoLP

required_permissions = [
    "s3:GetObject",
    "s3:PutObject",
    "secretsmanager:GetSecretValue",
    "cloudwatch:PutMetricData",
    "sns:Publish"
]

if aws.validate_polp(required_permissions):
    print("✓ PoLP validated")
else:
    print("⚠ Overly permissive IAM role detected")

# Check recent security events

stats = monitor.get_event_statistics(time_window=3600)
print(f"\nSecurity events (last hour): {stats['total_events']}")
print(f"By severity: {stats['by_severity']}")

# Check for anomalies

anomalies = monitor.detect_anomalies()
if anomalies:
    print(f"⚠ Anomalies detected: {anomalies}")
else:
    print("✓ No anomalies detected")
```

______________________________________________________________________

## Phase 6: Ongoing Maintenance

### 6.1 Daily Tasks

**Automated Monitoring** (via CloudWatch/SNS):

- Check security event dashboard
- Review critical/high severity alerts
- Verify backup completion

**Manual Checks**:

```bash

# Check application health

curl https://api.example.com/health

# Review CloudWatch dashboard

# https://console.aws.amazon.com/cloudwatch/home#dashboards:name=ProjectAI-Security

```

### 6.2 Weekly Tasks

**Security Log Review**:

```python

# scripts/weekly_review.py

from app.security import SecurityMonitor

monitor = SecurityMonitor()

# Get last week's events

week_stats = monitor.get_event_statistics(time_window=7*24*3600)

print("Weekly Security Report")
print("=" * 50)
print(f"Total events: {week_stats['total_events']}")
print(f"\nBy severity:")
for severity, count in week_stats['by_severity'].items():
    print(f"  {severity}: {count}")

print(f"\nBy type:")
for event_type, count in sorted(week_stats['by_type'].items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {event_type}: {count}")

# Check for anomalies

anomalies = monitor.detect_anomalies(time_window=7*24*3600, threshold=50)
if anomalies:
    print(f"\n⚠ Anomalies detected:")
    for anomaly in anomalies:
        print(f"  {anomaly['event_type']}: {anomaly['count']} occurrences")
```

**Database Audit**:

```python

# scripts/audit_database.py

from app.security import SecureDatabaseManager

db = SecureDatabaseManager()

# Get recent audit log

log = db.get_audit_log(limit=100)

print(f"Recent database actions: {len(log)}")

# Group by action

actions = {}
for entry in log:
    action = entry['action']
    actions[action] = actions.get(action, 0) + 1

print("\nActions:")
for action, count in sorted(actions.items(), key=lambda x: x[1], reverse=True):
    print(f"  {action}: {count}")
```

### 6.3 Monthly Tasks

- **Dependency Updates**: Review and update dependencies

```bash
pip list --outdated
pip install --upgrade package-name
pytest  # Re-run tests
```

- **Threat Signature Updates**: Add new threat indicators

```python
from app.security import SecurityMonitor

monitor = SecurityMonitor()

# Add new threat signatures

monitor.add_threat_signature(
    "APT-New-Campaign",
    ["malicious-domain.com", "bad-hash-abc123"]
)
```

- **Secret Rotation**: Rotate sensitive credentials

```bash

# Rotate secrets

aws secretsmanager rotate-secret --secret-id project-ai-secrets

# Update application (zero-downtime)

systemctl reload projectai
```

### 6.4 Quarterly Tasks

- **IAM Permission Review**: Audit and minimize permissions

```python
from app.security import AWSSecurityManager

aws = AWSSecurityManager()
audit = aws.audit_iam_permissions()

# Review attached policies

for policy in audit['attached_policies']:
    print(f"Review policy: {policy['PolicyName']}")
```

- **Penetration Testing**: Run comprehensive security tests

```bash

# Full test suite

pytest tests/test_security_*.py -v

# Security-specific tests

pytest tests/ -k security -v

# Generate coverage report

pytest --cov=app --cov-report=html
```

- **Security Training**: Update team on new threats and procedures

### 6.5 Annual Tasks

- **Third-Party Security Audit**: Engage external security firm
- **Disaster Recovery Test**: Verify backup/restore procedures
- **Compliance Review**: Ensure OWASP/NIST/CERT compliance
- **Architecture Review**: Assess security architecture changes

______________________________________________________________________

## Incident Response

### Security Incident Procedure

1. **Detection**: CloudWatch alarm or SNS alert
1. **Analysis**: Review logs and metrics
1. **Containment**: Isolate affected resources
1. **Eradication**: Remove threat
1. **Recovery**: Restore normal operations
1. **Lessons Learned**: Update procedures

### Example Incident: Authentication Attack

```python

# Automated response to high auth failures

from app.security import SecurityMonitor

monitor = SecurityMonitor()

# Detect anomaly

anomalies = monitor.detect_anomalies(threshold=10)

for anomaly in anomalies:
    if anomaly['event_type'] == 'authentication_failure':

        # Extract attacker IPs from metadata

        recent_events = [
            e for e in monitor.event_log
            if e.event_type == 'authentication_failure'
        ]

        attacker_ips = set()
        for event in recent_events[-20:]:  # Last 20 failures
            if 'ip' in event.metadata:
                attacker_ips.add(event.metadata['ip'])

        print(f"Attacker IPs: {attacker_ips}")

        # Block at firewall (manual or automated)

        for ip in attacker_ips:
            print(f"Block IP: {ip}")

            # aws ec2 authorize-security-group-ingress ...

```

______________________________________________________________________

## Troubleshooting

### Common Issues

**Issue**: CloudWatch metrics not appearing

```bash

# Check IAM permissions

aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:role/ProjectAI-EC2-Role \
  --action-names cloudwatch:PutMetricData

# Check logs

grep "CloudWatch" /var/log/projectai.log
```

**Issue**: SNS alerts not received

```bash

# Check subscription

aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:123456789012:security-alerts

# Check delivery

aws sns get-subscription-attributes \
  --subscription-arn arn:aws:sns:...
```

**Issue**: High false positive rate

```python

# Adjust thresholds

from app.security import SecurityMonitor

monitor = SecurityMonitor()

# Increase anomaly threshold

anomalies = monitor.detect_anomalies(threshold=20)  # Was 10
```

______________________________________________________________________

## Conclusion

Following this deployment guide ensures Project-AI is deployed with comprehensive security controls at every phase. Regular monitoring and maintenance are essential to maintaining a strong security posture.

For questions or issues, consult:

- `/docs/SECURITY_FRAMEWORK.md` - Security framework documentation
- `/tests/test_security_*.py` - Security test examples
- Internal security team or <security@example.com>

**Document Version**: 1.0 **Last Updated**: 2025-12-31
