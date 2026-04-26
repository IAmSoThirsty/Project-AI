# Container Security, Hardening, and Image Scanning

## Overview

Project-AI containerized deployments require comprehensive security hardening to protect against vulnerabilities, supply chain attacks, and runtime exploits. This document covers Docker/Kubernetes security best practices, image scanning workflows, secrets management, and compliance standards.

## Security Threat Model

### Container Attack Vectors

```
Attack Surface/
├── Image Supply Chain
│   ├── Base image vulnerabilities (CVEs)
│   ├── Malicious dependencies (npm, pip)
│   ├── Build-time injection
│   └── Registry tampering
├── Runtime Exploits
│   ├── Container escape
│   ├── Privilege escalation
│   ├── Resource exhaustion (DoS)
│   └── Network attacks
├── Data Exposure
│   ├── Hardcoded secrets
│   ├── Exposed environment variables
│   ├── Volume misconfigurations
│   └── Log leakage
└── Orchestration Layer
    ├── Kubernetes RBAC bypass
    ├── Pod security policy violations
    ├── Service mesh vulnerabilities
    └── etcd access
```

## Dockerfile Hardening

### Multi-Stage Build Security

**Secure Dockerfile** (root):

```dockerfile
# Stage 1: Builder (trusted base)
FROM python:3.11-slim@sha256:abc123... as builder

# Run as non-root during build
USER nobody
WORKDIR /build

# Install only build dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9 \
    libssl-dev=3.0.2-0ubuntu1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (cache optimization)
COPY --chown=nobody:nogroup requirements.txt .

# Build wheels (no cache, reproducible)
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels \
    -r requirements.txt

# Verify wheel integrity
RUN pip install safety && \
    safety check --json -r requirements.txt || exit 1

# Stage 2: Runtime (minimal)
FROM python:3.11-slim@sha256:abc123...

# Create non-root user
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Set working directory with ownership
WORKDIR /app
RUN chown appuser:appuser /app

# Copy wheels from builder
COPY --from=builder --chown=appuser:appuser /build/wheels /wheels

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3=3.0.2-0ubuntu1 \
    libffi8=3.4.2-4 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python packages
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# Copy application with restricted permissions
COPY --chown=appuser:appuser src/ /app/src/
COPY --chown=appuser:appuser data/ /app/data/

# Set read-only filesystem (immutable)
RUN chmod -R 555 /app/src && \
    chmod -R 755 /app/data

# Drop to non-root user
USER appuser

# Set security environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Health check (no root required)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Expose port (non-privileged port >1024)
EXPOSE 8000

# Run as non-root
CMD ["python", "-m", "app.main"]
```

### Security Best Practices

**1. Pin Base Image Versions**:
```dockerfile
# Bad: Latest tag (mutable, breaks reproducibility)
FROM python:3.11-slim

# Good: SHA256 digest (immutable, verifiable)
FROM python:3.11-slim@sha256:abc123def456...
```

**2. Minimize Image Layers**:
```dockerfile
# Bad: Multiple RUN commands (more layers = larger image)
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y libssl-dev

# Good: Combine into single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libssl-dev \
    && rm -rf /var/lib/apt/lists/*
```

**3. Remove Build Tools**:
```dockerfile
# Install build deps, build, then remove in same layer
RUN apt-get update && apt-get install -y build-essential \
    && pip install -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*
```

**4. Use .dockerignore**:
```dockerignore
# Prevent secrets from entering build context
.env
*.key
*.pem
.git
.github
*.md
tests/
```

**5. Scan for Secrets**:
```bash
# Before building, scan for accidentally committed secrets
docker run -v $(pwd):/path trufflesecurity/trufflehog:latest git file:///path
```

## Image Scanning and Vulnerability Management

### Trivy Scanning

**Installation**:
```bash
# Homebrew
brew install aquasecurity/trivy/trivy

# Docker
docker pull aquasecurity/trivy:latest
```

**Scan Docker Image**:
```bash
# Scan local image
trivy image projectai/desktop:latest

# Scan with severity filtering
trivy image --severity CRITICAL,HIGH projectai/desktop:latest

# Output JSON report
trivy image -f json -o trivy-report.json projectai/desktop:latest

# Scan with exit code (fail CI on vulnerabilities)
trivy image --exit-code 1 --severity CRITICAL projectai/desktop:latest
```

**Scan Dockerfile**:
```bash
# Static analysis of Dockerfile
trivy config Dockerfile
```

**Automated Scanning in CI/CD** (`.github/workflows/trivy-scan.yml`):

```yaml
name: Trivy Container Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  trivy-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker image
        run: docker build -t projectai/desktop:${{ github.sha }} .
      
      - name: Run Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'projectai/desktop:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
      
      - name: Upload results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Fail on high/critical vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'projectai/desktop:${{ github.sha }}'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'
```

### Grype Scanning

**Alternative scanner with comprehensive CVE database**:

```bash
# Install Grype
brew tap anchore/grype
brew install grype

# Scan image
grype projectai/desktop:latest

# JSON output
grype -o json projectai/desktop:latest > grype-report.json

# Only show fixed vulnerabilities
grype --only-fixed projectai/desktop:latest
```

### Clair Scanning

**PostgreSQL-backed vulnerability scanner**:

```yaml
# docker-compose.yml for Clair
services:
  clair:
    image: quay.io/projectquay/clair:latest
    ports:
      - "6060:6060"
    depends_on:
      - postgres
    environment:
      CLAIR_CONF: /config/config.yaml
      CLAIR_MODE: combo

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: password
```

## Secrets Management

### Never Hardcode Secrets

**Bad**:
```dockerfile
# NEVER do this
ENV OPENAI_API_KEY=sk-1234567890abcdef
ENV DATABASE_PASSWORD=supersecret123
```

**Good**: Use Docker secrets or environment injection

### Docker Secrets (Swarm/Kubernetes)

**Docker Swarm**:
```bash
# Create secret
echo "sk-1234567890abcdef" | docker secret create openai_api_key -

# Use in service
docker service create \
  --name project-ai \
  --secret openai_api_key \
  projectai/desktop:latest
```

**In Container**:
```python
# Read from /run/secrets/openai_api_key
with open('/run/secrets/openai_api_key', 'r') as f:
    api_key = f.read().strip()
```

### Kubernetes Secrets

**Create Secret**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: project-ai-secrets
type: Opaque
stringData:
  openai-api-key: sk-1234567890abcdef
  database-password: supersecret123
```

**Mount in Pod**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: project-ai
spec:
  containers:
  - name: app
    image: projectai/desktop:latest
    env:
    - name: OPENAI_API_KEY
      valueFrom:
        secretKeyRef:
          name: project-ai-secrets
          key: openai-api-key
    volumeMounts:
    - name: secrets
      mountPath: /run/secrets
      readOnly: true
  volumes:
  - name: secrets
    secret:
      secretName: project-ai-secrets
```

### HashiCorp Vault Integration

**Vault Injector** (Kubernetes):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: project-ai
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "project-ai"
    vault.hashicorp.com/agent-inject-secret-openai: "secret/data/project-ai/openai"
spec:
  serviceAccountName: project-ai
  containers:
  - name: app
    image: projectai/desktop:latest
```

**Application Code**:
```python
# Read from Vault-injected file
with open('/vault/secrets/openai', 'r') as f:
    secrets = json.load(f)
    api_key = secrets['data']['api_key']
```

## Runtime Security

### Docker Security Options

**Secure Container Run**:
```bash
docker run -d \
  --name project-ai \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  --security-opt no-new-privileges:true \
  --user 1000:1000 \
  --pids-limit 100 \
  --memory 2g \
  --cpus 2 \
  --restart unless-stopped \
  projectai/desktop:latest
```

**Explanation**:
- `--read-only`: Immutable filesystem (prevents runtime modification)
- `--tmpfs /tmp`: Temporary writable space (cleared on restart)
- `--cap-drop ALL`: Drop all Linux capabilities
- `--cap-add NET_BIND_SERVICE`: Allow binding to port 80 (if needed)
- `--security-opt no-new-privileges`: Prevent privilege escalation
- `--user 1000:1000`: Run as non-root user
- `--pids-limit 100`: Prevent fork bombs
- `--memory 2g`: Prevent memory exhaustion
- `--cpus 2`: Prevent CPU starvation

### AppArmor Profile

**Custom Profile** (`apparmor/project-ai`):
```
#include <tunables/global>

profile project-ai flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  # Allow network
  network inet tcp,
  network inet udp,

  # Allow reading specific files
  /app/** r,
  /app/data/** rw,

  # Deny write to application code
  deny /app/src/** w,

  # Allow Python interpreter
  /usr/bin/python3 rix,
  /usr/lib/python3.11/** r,

  # Deny sensitive system access
  deny /proc/sys/kernel/** rw,
  deny /sys/** rw,

  # Allow logging
  /var/log/project-ai/** rw,
}
```

**Load Profile**:
```bash
sudo apparmor_parser -r -W /etc/apparmor.d/project-ai
docker run --security-opt apparmor=project-ai projectai/desktop:latest
```

### Seccomp Profile

**Restrict Syscalls** (`seccomp/project-ai.json`):
```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": [
        "read", "write", "open", "close", "stat", "fstat",
        "lstat", "poll", "lseek", "mmap", "mprotect", "munmap",
        "brk", "rt_sigaction", "rt_sigprocmask", "ioctl",
        "access", "socket", "connect", "accept", "bind", "listen"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

**Use Profile**:
```bash
docker run --security-opt seccomp=seccomp/project-ai.json projectai/desktop:latest
```

## Kubernetes Pod Security

### Pod Security Standards

**Baseline Policy** (`k8s/pod-security-policy.yaml`):
```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: project-ai-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: true
```

**Apply to Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: project-ai
spec:
  template:
    metadata:
      annotations:
        container.apparmor.security.beta.kubernetes.io/app: runtime/default
    spec:
      serviceAccountName: project-ai
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: app
        image: projectai/desktop:latest
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
              - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: data
          mountPath: /app/data
      volumes:
      - name: tmp
        emptyDir: {}
      - name: data
        persistentVolumeClaim:
          claimName: project-ai-data
```

### Network Policies

**Restrict Traffic**:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: project-ai-netpol
spec:
  podSelector:
    matchLabels:
      app: project-ai
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx-ingress
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
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
  - to:  # Allow OpenAI API
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 169.254.0.0/16  # Block metadata service
    ports:
    - protocol: TCP
      port: 443
```

## Compliance and Auditing

### CIS Docker Benchmark

**Automated Audit**:
```bash
# Docker Bench Security
docker run -it --net host --pid host --userns host --cap-add audit_control \
  -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
  -v /var/lib:/var/lib \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/lib/systemd:/usr/lib/systemd \
  -v /etc:/etc \
  --label docker_bench_security \
  docker/docker-bench-security
```

**Key Checks**:
- 1.1.1: Ensure a separate partition for containers exists
- 2.1: Restrict network traffic between containers
- 4.1: Create a user for the container
- 5.1: Verify container content and build operations
- 5.10: Do not use the `--privileged` flag

### SBOM (Software Bill of Materials)

**Generate SBOM with Syft**:
```bash
# Install Syft
brew install syft

# Generate SBOM for image
syft projectai/desktop:latest -o json > sbom.json

# Generate CycloneDX format
syft projectai/desktop:latest -o cyclonedx-json > sbom-cyclonedx.json

# Generate SPDX format
syft projectai/desktop:latest -o spdx-json > sbom-spdx.json
```

**CI/CD Integration**:
```yaml
- name: Generate SBOM
  run: |
    syft projectai/desktop:${{ github.sha }} -o cyclonedx-json > sbom.json

- name: Upload SBOM
  uses: actions/upload-artifact@v3
  with:
    name: sbom
    path: sbom.json
```

### Image Signing (Cosign)

**Sign Docker Image**:
```bash
# Generate keys
cosign generate-key-pair

# Sign image
cosign sign --key cosign.key projectai/desktop:latest

# Verify signature
cosign verify --key cosign.pub projectai/desktop:latest
```

**Admission Controller** (Kubernetes):
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: config-image-policy
  namespace: cosign-system
data:
  policy: |
    images:
    - glob: "projectai/*"
      keyless:
        url: https://fulcio.sigstore.dev
        identities:
        - issuer: https://github.com/login/oauth
          subject: https://github.com/IAmSoThirsty/Project-AI
```

## Monitoring and Incident Response

### Runtime Security Monitoring (Falco)

**Falco Rules** (`falco-rules.yaml`):
```yaml
- rule: Unauthorized Container Access
  desc: Detect unauthorized access to Project-AI container
  condition: >
    container.image.repository = "projectai/desktop" and
    proc.name = "bash" and
    proc.aname[2] != "docker"
  output: "Unauthorized shell access (user=%user.name container=%container.name)"
  priority: WARNING

- rule: Sensitive File Access
  desc: Detect access to sensitive files
  condition: >
    container.image.repository = "projectai/desktop" and
    (fd.name glob "/app/data/*.json" or fd.name glob "/run/secrets/*") and
    (open_write or open_read)
  output: "Sensitive file accessed (user=%user.name file=%fd.name)"
  priority: INFO
```

### Log Aggregation

**Centralized Logging** (Fluentd):
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/project-ai-*.log
      pos_file /var/log/fluentd-project-ai.pos
      tag kubernetes.project-ai
      <parse>
        @type json
      </parse>
    </source>

    <filter kubernetes.project-ai>
      @type grep
      <regexp>
        key log
        pattern /(ERROR|CRITICAL|security)/
      </regexp>
    </filter>

    <match kubernetes.project-ai>
      @type elasticsearch
      host elasticsearch.logging.svc.cluster.local
      port 9200
      index_name project-ai-logs
    </match>
```

## Security Checklist

### Pre-Deployment

- [ ] Base image pinned to SHA256 digest
- [ ] Multi-stage build (no build tools in final image)
- [ ] Non-root user created and used
- [ ] No hardcoded secrets
- [ ] `.dockerignore` configured
- [ ] Trivy/Grype scan passed (no critical/high CVEs)
- [ ] SBOM generated
- [ ] Image signed with Cosign
- [ ] Seccomp/AppArmor profiles created

### Runtime

- [ ] Read-only root filesystem
- [ ] Resource limits (CPU, memory) set
- [ ] Capabilities dropped (`--cap-drop ALL`)
- [ ] No new privileges (`--security-opt no-new-privileges`)
- [ ] Network policies applied (Kubernetes)
- [ ] Pod Security Policy enforced
- [ ] Secrets injected (not hardcoded)
- [ ] Logging to centralized system
- [ ] Monitoring with Falco/Prometheus

### Ongoing

- [ ] Weekly vulnerability scans
- [ ] Monthly base image updates
- [ ] Quarterly security audits
- [ ] Incident response plan documented
- [ ] Security training for team

## Related Documentation

- `01_docker_architecture.md` - Container structure
- `08_configuration_management.md` - Secrets handling
- `10_cicd_docker_pipeline.md` - Automated scanning

## References

- **OWASP Docker Top 10**: https://owasp.org/www-project-docker-top-10/
- **CIS Docker Benchmark**: https://www.cisecurity.org/benchmark/docker
- **Kubernetes Security**: https://kubernetes.io/docs/concepts/security/
- **Trivy**: https://aquasecurity.github.io/trivy/
- **Falco**: https://falco.org/docs/
