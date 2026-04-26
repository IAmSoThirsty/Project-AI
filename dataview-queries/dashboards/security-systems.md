# Security Systems Dashboard

**Purpose:** Monitor authentication, encryption, password security, location tracking encryption, and security audit status

**Core Systems:** UserManager (bcrypt), LocationTracker (Fernet), EmergencyAlert, CommandOverride

**Last Updated:** `= dateformat(this.file.mtime, "yyyy-MM-dd HH:mm")`

---

## Security System Status

```dataview
TABLE WITHOUT ID
  system-name as "System",
  security-level as "Level",
  encryption-type as "Encryption",
  last-audit as "Last Audit",
  vulnerabilities as "Vulnerabilities"
FROM "docs/security"
WHERE system-type = "security"
SORT security-level DESC, vulnerabilities ASC
```

---

## Authentication Systems

```dataview
TABLE WITHOUT ID
  auth-system as "System",
  hash-algorithm as "Algorithm",
  implementation-file as "File",
  strength-rating as "Strength",
  status as "Status"
FROM "docs/security/auth"
WHERE contains(tags, "authentication")
SORT strength-rating DESC
```

---

## Encryption Systems

```dataview
TABLE WITHOUT ID
  system as "System",
  encryption-method as "Method",
  key-management as "Key Mgmt",
  data-encrypted as "Data Type",
  compliance as "Compliance"
FROM "docs/security/encryption"
WHERE contains(tags, "encryption") OR contains(tags, "cryptography")
SORT system ASC
```

---

## Recent Security Events

```dataview
TABLE WITHOUT ID
  event-type as "Event",
  severity as "Severity",
  system as "System",
  timestamp as "Timestamp",
  resolution-status as "Status"
FROM "docs/security/events"
WHERE event-category = "security"
SORT timestamp DESC, severity DESC
LIMIT 20
```

---

## Security Audit Findings

```dataview
TABLE WITHOUT ID
  finding-id as "ID",
  severity as "Severity",
  category as "Category",
  description as "Description",
  remediation-status as "Status",
  date-found as "Found"
FROM "docs/security/audits"
WHERE finding-type = "security"
SORT severity DESC, date-found DESC
LIMIT 25
```

---

## Password Security Analysis

```dataview
TABLE WITHOUT ID
  component as "Component",
  hash-type as "Hash Type",
  salt as "Salted",
  iterations as "Iterations",
  upgrade-needed as "Upgrade"
FROM "docs/security/passwords"
WHERE contains(tags, "password-security")
SORT upgrade-needed DESC, component ASC
```

---

## Vulnerability Scan Results

```dataview
TABLE WITHOUT ID
  scan-date as "Scan Date",
  scanner as "Scanner",
  critical as "Critical",
  high as "High",
  medium as "Medium",
  low as "Low"
FROM "docs/security/scans"
WHERE scan-type = "vulnerability"
SORT scan-date DESC
LIMIT 15
```

---

## Security Dependencies

```dataview
TABLE WITHOUT ID
  dependency as "Dependency",
  version as "Version",
  security-rating as "Rating",
  known-cves as "Known CVEs",
  update-available as "Update Available"
FROM "docs/security/dependencies"
WHERE security-critical = true
SORT length(known-cves) DESC, security-rating ASC
```

---

## Access Control Matrix

```dataview
TABLE WITHOUT ID
  user-role as "Role",
  permissions as "Permissions",
  restricted-actions as "Restrictions",
  override-capability as "Override",
  audit-level as "Audit"
FROM "docs/security/access-control"
WHERE contains(tags, "rbac") OR contains(tags, "access-control")
SORT user-role ASC
```

---

## Encryption Key Management

```dataview
TABLE WITHOUT ID
  key-name as "Key",
  algorithm as "Algorithm",
  key-length as "Length",
  rotation-schedule as "Rotation",
  last-rotated as "Last Rotated"
FROM "docs/security/keys"
WHERE key-type = "encryption"
SORT last-rotated ASC
```

---

## Security Configuration Files

```dataview
LIST
FROM "data" OR "config"
WHERE (contains(file.name, "security") OR contains(file.name, "auth") OR contains(file.name, "encryption")) AND contains(file.ext, "json")
SORT file.name ASC
```

---

## Security Test Coverage

```dataview
TABLE WITHOUT ID
  test-suite as "Test Suite",
  coverage as "Coverage %",
  security-tests as "Security Tests",
  penetration-tests as "Pen Tests",
  last-run as "Last Run"
FROM "docs/testing/security"
WHERE test-type = "security"
SORT coverage DESC
```

---

## Incident Response Status

```dataview
TABLE WITHOUT ID
  incident-id as "ID",
  incident-type as "Type",
  severity as "Severity",
  status as "Status",
  assigned-to as "Assigned",
  time-to-resolution as "TTR"
FROM "docs/security/incidents"
WHERE incident-category = "security"
SORT severity DESC, status ASC
LIMIT 15
```

---

## Compliance & Standards

```dataview
TABLE WITHOUT ID
  standard as "Standard",
  compliance-status as "Status",
  coverage as "Coverage %",
  gaps as "Gaps",
  next-audit as "Next Audit"
FROM "docs/compliance"
WHERE compliance-type = "security"
SORT compliance-status ASC, coverage ASC
```

---

## Security Hardening Checklist

```dataview
TASK
FROM "docs/security/hardening"
WHERE contains(tags, "security-hardening") AND !completed
SORT priority DESC
```

---

## Open Security Issues

```dataview
TABLE WITHOUT ID
  issue-id as "ID",
  severity as "Severity",
  title as "Title",
  assigned-to as "Assigned",
  created-date as "Created",
  sla-deadline as "SLA"
FROM "docs/issues"
WHERE issue-type = "security" AND status != "closed"
SORT severity DESC, created-date ASC
```

---

## Related Documentation

```dataview
TABLE WITHOUT ID
  file.link as "Document",
  security-domain as "Domain",
  criticality as "Criticality",
  dateformat(file.mtime, "yyyy-MM-dd") as "Updated"
FROM "docs/security" OR "docs"
WHERE contains(tags, "security") OR contains(file.name, "SECURITY")
SORT criticality DESC, file.mtime DESC
LIMIT 15
```

---

## Quick Actions

- 🔐 [[User Authentication|View Auth System]]
- 🔒 [[Encryption Systems|View Encryption]]
- 🔑 [[Password Security|View Password Mgmt]]
- 🛡️ [[Security Audits|View Audit History]]
- 🚨 [[Security Incidents|View Incidents]]
- 📋 [[Compliance Status|View Compliance]]

---

**Query Performance:** Target <1s | **Data Sources:** docs/security, docs/compliance, src/app/core/user_manager.py | **Refresh:** Real-time
