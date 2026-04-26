# Security Boundary Query

**Purpose:** Visualize security zones, trust boundaries, and privilege escalation paths  
**Performance Target:** <2 seconds  
**Data Source:** YAML frontmatter metadata + security documentation

---

## Query 1: Security Zones

Maps all security zones and their trust levels.

```dataview
TABLE 
    file.link AS "Component",
    security-boundary AS "Security Zone",
    trust-level AS "Trust Level",
    access-control AS "Access Control",
    architectural-layer AS "Layer"
FROM "docs" OR ".github" OR "archive"
WHERE security-boundary != null OR trust-level != null
SORT trust-level DESC, security-boundary ASC
```

---

## Query 2: Trust Boundaries

Identifies boundaries between different trust levels.

```dataview
TABLE 
    file.link AS "Boundary",
    security-boundary AS "Zone",
    authentication-method AS "Auth Required",
    authorization-level AS "Authorization",
    boundary-enforcement AS "Enforcement Mechanism"
FROM "docs" OR ".github"
WHERE security-boundary != null AND (authentication-method != null OR authorization-level != null)
SORT security-boundary ASC, authorization-level DESC
```

---

## Query 3: Privilege Escalation Paths

Identifies components that can elevate privileges.

```dataview
TABLE 
    file.link AS "Component",
    authorization-level AS "Required Level",
    privilege-escalation AS "Escalation Method",
    approval-required AS "Approval Required",
    audit-logging AS "Audit Logging"
FROM "docs" OR ".github" OR "archive"
WHERE privilege-escalation != null OR authorization-level = "Admin" OR authorization-level = "System"
SORT authorization-level DESC
```

---

## Query 4: Public Attack Surface

Identifies publicly accessible components (highest risk).

```dataview
TABLE 
    file.link AS "Component",
    security-boundary AS "Zone",
    authentication-method AS "Auth",
    input-validation AS "Input Validation",
    attack-surface AS "Attack Surface"
FROM "docs" OR ".github" OR "archive"
WHERE security-boundary = "Public" OR trust-level = "Untrusted" OR contains(tags, "public-api")
SORT attack-surface DESC, file.name ASC
```

---

## Query 5: Security Controls Inventory

Catalogs all security controls (auth, encryption, validation, monitoring).

```dataview
TABLE 
    file.link AS "Security Control",
    security-control-type AS "Type",
    protection-level AS "Protection Level",
    implemented-in AS "Implementation",
    status AS "Status"
FROM "docs" OR ".github" OR "archive"
WHERE security-control-type != null OR contains(tags, "security-control")
SORT security-control-type ASC, protection-level DESC
```

---

## Query 6: Cross-Boundary Data Flows

Tracks data crossing security zone boundaries (potential vulnerability).

```dataview
TABLE 
    file.link AS "Data Flow",
    source-zone AS "Source Zone",
    destination-zone AS "Destination Zone",
    encryption-method AS "Encryption",
    validation-performed AS "Validated"
FROM "docs" OR ".github"
WHERE source-zone != null AND destination-zone != null AND source-zone != destination-zone
SORT source-zone ASC, destination-zone ASC
```

---

## Query 7: Authentication Mechanisms

Inventories all authentication methods across the system.

```dataview
TABLE 
    file.link AS "Component",
    authentication-method AS "Auth Method",
    credential-storage AS "Credential Storage",
    session-management AS "Session Management",
    mfa-enabled AS "MFA"
FROM "docs" OR ".github" OR "archive"
WHERE authentication-method != null
SORT authentication-method ASC
```

---

## Query 8: Authorization Matrix

Shows authorization levels and access control policies.

```dataview
TABLE 
    file.link AS "Resource",
    authorization-level AS "Required Level",
    access-control AS "Access Control",
    resource-type AS "Resource Type",
    rbac-enabled AS "RBAC"
FROM "docs" OR ".github" OR "archive"
WHERE authorization-level != null OR access-control != null
SORT authorization-level DESC, resource-type ASC
```

---

## Query 9: Sensitive Operations

Identifies high-risk operations requiring special security controls.

```dataview
TABLE 
    file.link AS "Operation",
    risk-level AS "Risk Level",
    authorization-level AS "Auth Level",
    approval-required AS "Approval Required",
    audit-logging AS "Audit Logging",
    rate-limiting AS "Rate Limiting"
FROM "docs" OR ".github" OR "archive"
WHERE risk-level = "High" OR risk-level = "Critical" OR approval-required = true
SORT risk-level DESC
```

---

## Query 10: Security Vulnerabilities

Tracks known vulnerabilities and their remediation status.

```dataview
TABLE 
    file.link AS "Vulnerability",
    vulnerability-type AS "Type",
    severity AS "Severity",
    affected-components AS "Affected",
    remediation-status AS "Status"
FROM "docs" OR "archive" OR ".github"
WHERE vulnerability-type != null OR severity != null OR contains(tags, "vulnerability")
SORT severity DESC, remediation-status ASC
```

---

## Query 11: Encryption Inventory

Catalogs all encryption implementations (at rest, in transit, in use).

```dataview
TABLE 
    file.link AS "Component",
    encryption-method AS "Method",
    encryption-stage AS "Stage",
    key-management AS "Key Management",
    algorithm-strength AS "Strength"
FROM "docs" OR ".github" OR "archive"
WHERE encryption-method != null OR encryption-stage != null
SORT encryption-stage ASC, algorithm-strength DESC
```

---

## Query 12: Security Monitoring

Identifies components with security monitoring and alerting.

```dataview
TABLE 
    file.link AS "Component",
    security-monitoring AS "Monitoring",
    audit-logging AS "Audit Logging",
    alert-threshold AS "Alert Threshold",
    incident-response AS "Incident Response"
FROM "docs" OR ".github" OR "archive"
WHERE security-monitoring = true OR audit-logging = true OR contains(tags, "monitoring")
SORT security-monitoring DESC, audit-logging DESC
```

---

## Query 13: Input Validation Points

Maps where user input is validated (critical for injection prevention).

```dataview
TABLE 
    file.link AS "Validation Point",
    input-validation AS "Validation Type",
    sanitization-method AS "Sanitization",
    security-boundary AS "Boundary",
    validation-library AS "Library"
FROM "docs" OR ".github"
WHERE input-validation != null OR sanitization-method != null
SORT security-boundary ASC
```

---

## Query 14: Security Testing Coverage

Shows which components have security testing (penetration tests, audits).

```dataview
TABLE 
    file.link AS "Component",
    security-testing AS "Testing Type",
    last-audit-date AS "Last Audit",
    penetration-tested AS "Pen Tested",
    security-score AS "Security Score"
FROM "docs" OR ".github" OR "archive"
WHERE security-testing != null OR penetration-tested = true
SORT last-audit-date DESC
```

---

## Query 15: Secrets Management

Tracks how secrets are stored and managed.

```dataview
TABLE 
    file.link AS "Secret",
    secret-type AS "Type",
    storage-method AS "Storage",
    rotation-policy AS "Rotation",
    access-control AS "Access Control"
FROM "docs" OR ".github" OR "archive"
WHERE secret-type != null OR contains(tags, "secrets")
SORT secret-type ASC
```

---

## Query 16: Security Policy Compliance

Shows compliance with security policies and frameworks.

```dataview
TABLE 
    file.link AS "Component",
    security-framework AS "Framework",
    compliance-status AS "Status",
    policy-violations AS "Violations",
    remediation-plan AS "Remediation"
FROM "docs" OR ".github" OR "archive"
WHERE security-framework != null OR compliance-status != null
SORT compliance-status ASC, security-framework ASC
```

---

## Usage Instructions

### Running Queries

1. **Open Obsidian** in the Project-AI vault
2. **Create a security analysis note**
3. **Copy any query** above into the note
4. **Enter Reading View** (Ctrl+E or Cmd+E)
5. **Dataview renders results** automatically

### Interpreting Results

- **Security Zone:** Public, Internal, Core, Kernel (increasing trust)
- **Trust Level:** Untrusted, Low, Medium, High, Critical
- **Authorization Level:** Public, Authenticated, User, Admin, System
- **Risk Level:** Low, Medium, High, Critical
- **Attack Surface:** External, API, GUI, CLI, Internal

### Performance Optimization

If queries run slowly:

1. **Narrow scope:** `FROM "docs/security"` for security-specific docs
2. **Add LIMIT:** Cap at 50-100 results
3. **Filter by tags:** Use `tags` for targeted queries
4. **Cache results:** Save snapshots for audit trails

### Common Use Cases

1. **Security Audit:** Run Query 10 (Vulnerabilities) + Query 14 (Testing)
2. **Attack Surface Analysis:** Query 4 (Public Attack Surface)
3. **Privilege Review:** Query 3 (Escalation Paths) + Query 8 (Authorization)
4. **Data Protection:** Query 11 (Encryption) + Query 6 (Cross-Boundary)
5. **Compliance:** Query 16 (Policy Compliance)

---

## Metadata Requirements

For accurate results, ensure security documentation has:

```yaml
---
# Security Zones
security-boundary: "Public" | "Internal" | "Core" | "Kernel"
trust-level: "Untrusted" | "Low" | "Medium" | "High" | "Critical"
attack-surface: "External" | "API" | "GUI" | "CLI" | "Internal" | "None"

# Authentication & Authorization
authentication-method: "None" | "Password" | "JWT" | "API Key" | "OAuth2" | "Certificate"
authorization-level: "Public" | "Authenticated" | "User" | "Admin" | "System"
access-control: "None" | "User-Based" | "RBAC" | "ABAC" | "MAC"
mfa-enabled: true | false
rbac-enabled: true | false

# Trust Boundaries
boundary-enforcement: "Firewall" | "Auth Gateway" | "Input Validation" | "Encryption"
source-zone: "Public"
destination-zone: "Core"
validation-performed: true | false

# Privilege Escalation
privilege-escalation: "Master Password" | "Admin Approval" | "Sudo" | "Impersonation"
approval-required: true | false
audit-logging: true | false

# Security Controls
security-control-type: "Authentication" | "Authorization" | "Encryption" | "Validation" | "Monitoring"
protection-level: "Basic" | "Standard" | "Enhanced" | "Maximum"
implemented-in: "src/app/core/user_manager.py:123-456"

# Input Validation
input-validation: "Schema Validation" | "Sanitization" | "Type Checking" | "Range Validation"
sanitization-method: "html_escape" | "SQL Parameterization" | "Path Validation"
validation-library: "pydantic" | "marshmallow" | "custom"

# Encryption
encryption-method: "Fernet" | "AES-256" | "bcrypt" | "TLS" | "SHA-256" | "None"
encryption-stage: "At Rest" | "In Transit" | "In Memory" | "In Use"
key-management: "Environment Variable" | "KMS" | "Hardcoded" | "User-Provided"
algorithm-strength: "Weak" | "Standard" | "Strong" | "Military-Grade"

# Credentials
credential-storage: "Hashed (bcrypt)" | "Encrypted (Fernet)" | "Plaintext" | "None"
session-management: "JWT" | "Cookie" | "Token" | "None"
rotation-policy: "Never" | "Monthly" | "Quarterly" | "On Breach"

# Risk Assessment
risk-level: "Low" | "Medium" | "High" | "Critical"
rate-limiting: true | false
incident-response: "Automated" | "Manual" | "None"

# Vulnerabilities
vulnerability-type: "SQL Injection" | "XSS" | "CSRF" | "Path Traversal" | "Command Injection"
severity: "Low" | "Medium" | "High" | "Critical"
affected-components: ["component-1", "component-2"]
remediation-status: "Not Started" | "In Progress" | "Completed" | "Accepted Risk"

# Monitoring & Auditing
security-monitoring: true | false
alert-threshold: "Failed logins > 5" | "Admin actions" | "Data exports"

# Security Testing
security-testing: "Unit Tests" | "Integration Tests" | "Penetration Test" | "Security Audit"
last-audit-date: 2026-04-20
penetration-tested: true | false
security-score: 85 (0-100)

# Compliance
security-framework: "OWASP Top 10" | "Asimov's Laws" | "NIST" | "ISO 27001"
compliance-status: "Compliant" | "Partial" | "Non-Compliant"
policy-violations: ["Hardcoded credentials in config.py"]
remediation-plan: "Migrate to environment variables by 2026-05-01"

# Secrets
secret-type: "API Key" | "Password" | "Private Key" | "Token"
storage-method: "Environment Variable" | "Encrypted File" | "KMS" | "Hardcoded"
---
```

---

## Example Output

### Query 1: Security Zones

| Component | Security Zone | Trust Level | Access Control | Layer |
|-----------|---------------|-------------|----------------|-------|
| `[[Kernel]]` | Kernel | Critical | MAC | Infrastructure |
| `[[User Manager]]` | Core | High | RBAC | Core |
| `[[Web API]]` | Public | Untrusted | JWT | GUI |

### Query 3: Privilege Escalation Paths

| Component | Required Level | Escalation Method | Approval Required | Audit Logging |
|-----------|----------------|-------------------|-------------------|---------------|
| `[[Command Override]]` | System | Master Password | true | true |
| `[[Learning Approval]]` | Admin | Guardian Approval | true | true |

### Query 4: Public Attack Surface

| Component | Zone | Auth | Input Validation | Attack Surface |
|-----------|------|------|------------------|----------------|
| `[[Web API Login]]` | Public | Password | Schema + Sanitization | External |
| `[[Chat Interface]]` | Internal | JWT | Intent Detection | GUI |

### Query 10: Security Vulnerabilities

| Vulnerability | Type | Severity | Affected | Status |
|---------------|------|----------|----------|--------|
| `[[ISSUE_B324_MD5]]` | Weak Hash | Medium | `[command_override.py]` | Completed |
| `[[Shell Injection]]` | Command Injection | High | `[emergency_alert.py]` | Completed |

---

## Integration with Other Queries

- **Combine with Data Flow:** Validate encryption on sensitive data flows
- **Combine with Integration Points:** Check auth at integration boundaries
- **Combine with Dependency Graph:** Trace privilege through dependency chains

---

## Security Documentation Reference

See these files for detailed security information:
- `SECURITY.md` - Security policy and vulnerability reporting
- `SECURITY_VULNERABILITY_ASSESSMENT_REPORT.md` - Comprehensive security audit
- `INPUT_VALIDATION_SECURITY_AUDIT.md` - Input validation analysis
- `AUTHENTICATION_SECURITY_AUDIT_REPORT.md` - Authentication mechanisms
- `DATA_ENCRYPTION_PRIVACY_AUDIT_REPORT.md` - Encryption implementation

---

**Query Performance:** All queries optimized to run in <2 seconds  
**Last Updated:** 2026-04-20  
**Maintained By:** AGENT-096 (Relationship Queries Specialist)
