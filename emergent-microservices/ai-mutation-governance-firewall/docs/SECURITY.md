# Security

## AI Mutation Governance Firewall - Security Documentation

### Authentication

**Method**: both

#### API Key Security

- API keys stored in Kubernetes secrets
- Constant-time comparison prevents timing attacks
- Keys rotated quarterly
- Failed attempts logged and monitored
#### JWT Security

- Tokens expire after 24 hours
- Signature verification required
- Clock skew tolerance: 10 seconds
- Issuer validation enforced
### Authorization

- Role-Based Access Control (RBAC)
- Roles: Viewer, Editor, Admin
- Deny-by-default policy
### Rate Limiting

- 250 requests/minute per client
- Burst allowance: 500
- Token bucket algorithm
- Per-IP and per-user tracking

### Input Validation

- Pydantic schema validation
- Max request body size: 1MB
- Unknown fields rejected
- SQL injection prevention
- XSS prevention

### Network Security

- TLS 1.3 required in production
- NetworkPolicy restricts pod communication
- Egress filtering enabled
- Internal services not exposed

### Secrets Management

- Secrets stored in Kubernetes Secrets
- Never logged or exposed in errors
- Rotated regularly
- Access audited

### Security Scanning

- Dependency vulnerability scanning (Trivy)
- Container image scanning
- Secret scanning (Gitleaks)
- SAST with Bandit
- Critical vulnerabilities block deployment

### Compliance

- Audit logging enabled
- Data encryption at rest
- TLS encryption in transit
- No PII in logs

### Security Contacts

Report security issues to: security@example.com
