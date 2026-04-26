# Data Flow Diagrams

**Document:** 06_data_flow_diagrams.md  
**Purpose:** Visual representations of data flow between security systems  
**Classification:** AGENT-054 Security Documentation

---

## Data Flow Patterns

This document visualizes how data flows between the 10 security systems across different scenarios.

---

## Flow 1: Attack Detection to Response

### ASCII Diagram
```
[External Attacker]
        │
        │ (1) Malicious Request
        ↓
┌───────────────────┐
│   Honeypot        │ ← Attack patterns from Security Resources
│   Detector        │
└───────────────────┘
        │
        │ (2) AttackAttempt {
        │     ip_address: "192.168.1.100",
        │     attack_type: "SQL_INJECTION",
        │     severity: "HIGH",
        │     payload: "' OR 1=1--",
        │     tool_detected: "sqlmap"
        │ }
        ↓
┌───────────────────┐
│   Threat          │ ← Threat intel from Security Resources
│   Detection       │
└───────────────────┘
        │
        │ (3) ThreatAssessment {
        │     level: MALICIOUS,
        │     confidence: 0.92,
        │     threat_type: "sql_injection",
        │     recommended_action: "DECEPTION"
        │ }
        ↓
┌───────────────────┐
│   OctoReflex      │
│   Enforcement     │
└───────────────────┘
        │
        │ (4) ValidationResult {
        │     is_valid: False,
        │     violations: [FIRST_LAW_VIOLATION],
        │     enforcement: "BLOCK"
        │ }
        ↓
┌───────────────────┐
│   Incident        │
│   Responder       │
└───────────────────┘
        │
        │ (5) Response Actions:
        ├─→ [ISOLATE_COMPONENT]
        ├─→ [BACKUP_DATA]
        ├─→ [BLOCK_IP]
        ├─→ [ALERT_TEAM]
        └─→ [LOG_FORENSICS]
```

### Data Structures
```python
# (2) AttackAttempt
{
    "attempt_id": "ATT_1234567890",
    "timestamp": "2024-01-15T10:30:00Z",
    "ip_address": "192.168.1.100",
    "endpoint": "/api/users",
    "attack_type": "SQL_INJECTION",
    "method": "POST",
    "payload": "' OR 1=1--",
    "user_agent": "sqlmap/1.0",
    "severity": "high",
    "fingerprint": "a1b2c3d4e5f6g7h8",
    "tool_detected": "sqlmap"
}

# (3) ThreatAssessment
{
    "level": "MALICIOUS",
    "confidence": 0.92,
    "threat_type": "sql_injection",
    "indicators": [
        "SQL pattern detected",
        "Automated tool (sqlmap) identified",
        "High severity payload"
    ],
    "recommended_action": "DECEPTION",
    "attack_patterns": ["DATA_EXFILTRATION"],
    "behavior_score": 0.4,
    "ml_prediction": {
        "threat_probability": 0.95,
        "model": "CodexDeus-ThreatDetector-v1",
        "confidence": 0.85
    }
}

# (4) ValidationResult
{
    "is_valid": False,
    "violations": [
        {
            "violation_id": "VIO_1234567890_abc123",
            "violation_type": "FIRST_LAW_VIOLATION",
            "severity": 6,
            "description": "Action blocked: potential system harm",
            "enforcement_action": "BLOCK"
        }
    ]
}

# (5) IncidentResponse
{
    "incident_id": "INC_1234567890",
    "severity": "HIGH",
    "automated_responses": [
        "LOG_FORENSICS",
        "ISOLATE_COMPONENT",
        "BACKUP_DATA",
        "BLOCK_IP",
        "ALERT_TEAM"
    ],
    "status": "in_progress"
}
```

---

## Flow 2: Authentication Flow

### ASCII Diagram
```
[User Login Request]
        │
        │ (1) Credentials {
        │     username: "alice",
        │     password: "********",
        │     mfa_code: "123456"
        │ }
        ↓
┌───────────────────┐
│   Authentication  │
│   System          │
└───────────────────┘
        │
        │ (2) Password Verification
        ├─→ Argon2id hash check
        │
        │ (3) MFA Verification
        ├─→ TOTP code validation
        │
        │ (4) Token Generation
        │   JWT {
        │     access_token: "eyJ...",
        │     refresh_token: "eyJ...",
        │     expires_at: "2024-01-16T10:30:00Z"
        │   }
        ↓
┌───────────────────┐
│   OctoReflex      │
│   Validation      │
└───────────────────┘
        │
        │ (5) Constitutional Check {
        │     action: "user_login",
        │     context: {
        │       username: "alice",
        │       role: "user",
        │       ip_address: "192.168.1.50"
        │     }
        │ }
        ↓
        ├─→ [VALID] Return tokens to user
        │
        └─→ [INVALID] → Incident Responder
                │
                └─→ Log violation + Rate limit
```

### Data Structures
```python
# (1) Login Request
{
    "username": "alice",
    "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$...",
    "mfa_code": "123456",
    "ip_address": "192.168.1.50",
    "user_agent": "Mozilla/5.0..."
}

# (4) JWT Tokens
{
    "access_token": {
        "token": "eyJhbGciOiJIUzI1NiIs...",
        "expires_at": "2024-01-15T34:30:00Z",
        "payload": {
            "sub": "alice",
            "role": "user",
            "iat": 1705315800,
            "exp": 1705402200
        }
    },
    "refresh_token": {
        "token": "eyJhbGciOiJIUzI1NiIs...",
        "expires_at": "2024-02-14T10:30:00Z"
    }
}

# (5) OctoReflex Context
{
    "action_type": "user_login",
    "context": {
        "username": "alice",
        "role": "user",
        "ip_address": "192.168.1.50",
        "timestamp": "2024-01-15T10:30:00Z",
        "mfa_verified": True
    }
}
```

---

## Flow 3: System Bypass → Cerberus Activation

### ASCII Diagram
```
[Security Agent #42]
        │
        │ (1) Bypass Detected
        ↓
┌───────────────────┐
│   Cerberus        │
│   Runtime Manager │
└───────────────────┘
        │
        │ (2) BypassEvent {
        │     event_id: "BYP_abc123",
        │     bypassed_agent_id: "agent_42",
        │     bypass_type: "honeypot_evasion",
        │     risk_score: 0.85
        │ }
        ↓
┌───────────────────┐
│   Cerberus        │
│   Hydra Defense   │
└───────────────────┘
        │
        │ (3) Language Selection (Deterministic)
        │   seed = hash("BYP_abc123")
        │   random.seed(seed)
        │
        │ (4) Spawn 3 Agents:
        ├─→ Agent 126 (Python + English)
        ├─→ Agent 127 (Rust + Spanish)
        └─→ Agent 128 (Go + Japanese)
        │
        │ (5) Each agent → OctoReflex for validation
        ↓
┌───────────────────┐
│   OctoReflex      │
│   Validation      │
└───────────────────┘
        │
        │ (6) Validate each agent
        ├─→ Agent 126: ✓ VALID
        ├─→ Agent 127: ✓ VALID
        └─→ Agent 128: ✓ VALID
        │
        │ (7) Lockdown escalation
        ↓
┌───────────────────┐
│   Lockdown        │
│   Controller      │
└───────────────────┘
        │
        │ (8) Stage 5 → Stage 6
        │   New restrictions:
        ├─→ Disable admin functions
        ├─→ Enable audit mode
        ├─→ Require MFA for all ops
        └─→ Rate limit API endpoints
        │
        │ (9) Log incident
        ↓
┌───────────────────┐
│   Incident        │
│   Responder       │
└───────────────────┘
```

### Data Structures
```python
# (2) BypassEvent
{
    "event_id": "BYP_abc123",
    "timestamp": "2024-01-15T10:30:00Z",
    "bypassed_agent_id": "agent_42",
    "bypass_type": "honeypot_evasion",
    "risk_score": 0.85,
    "bypass_depth": 1,
    "attacker_signature": "APT29_pattern",
    "spawned_agents": ["agent_126", "agent_127", "agent_128"],
    "lockdown_stage": 6
}

# (4) Spawned Agents
[
    {
        "agent_id": "agent_126",
        "spawn_time": "2024-01-15T10:30:03Z",
        "programming_language": "python",
        "programming_language_name": "Python 3.11",
        "human_language": "en",
        "human_language_name": "English",
        "generation": 2,
        "parent_agent_id": "agent_42",
        "status": "active"
    },
    {
        "agent_id": "agent_127",
        "spawn_time": "2024-01-15T10:30:04Z",
        "programming_language": "rust",
        "programming_language_name": "Rust 1.75",
        "human_language": "es",
        "human_language_name": "Spanish",
        "generation": 2,
        "parent_agent_id": "agent_42",
        "status": "active"
    },
    {
        "agent_id": "agent_128",
        "spawn_time": "2024-01-15T10:30:05Z",
        "programming_language": "go",
        "programming_language_name": "Go 1.21",
        "human_language": "ja",
        "human_language_name": "Japanese",
        "generation": 2,
        "parent_agent_id": "agent_42",
        "status": "active"
    }
]

# (8) Lockdown Stage Transition
{
    "previous_stage": 5,
    "new_stage": 6,
    "restrictions_added": [
        "disable_admin_functions",
        "enable_audit_mode",
        "require_mfa_all_operations",
        "rate_limit_api_endpoints"
    ],
    "trigger_event": "BYP_abc123"
}
```

---

## Flow 4: Emergency Alert

### ASCII Diagram
```
[Critical Incident]
        │
        │ (1) CRITICAL threat detected
        ↓
┌───────────────────┐
│   Incident        │
│   Responder       │
└───────────────────┘
        │
        │ (2) Create CRITICAL incident
        │
        │ (3) Get user location
        ↓
┌───────────────────┐
│   Location        │
│   Tracker         │
└───────────────────┘
        │
        │ (4) IP Geolocation
        ├─→ Query ipapi.co
        │   Location {
        │     latitude: 37.7749,
        │     longitude: -122.4194,
        │     city: "San Francisco",
        │     region: "California",
        │     country: "United States"
        │   }
        │
        │ (5) Encrypt location
        ↓
┌───────────────────┐
│   Encryption      │
│   (Fernet)        │
└───────────────────┘
        │
        │ (6) Encrypted location data
        ↓
┌───────────────────┐
│   Emergency       │
│   Alert           │
└───────────────────┘
        │
        │ (7) Compose alert message
        │   Subject: "EMERGENCY ALERT - alice"
        │   Body: {
        │     user: "alice",
        │     time: "2024-01-15T10:30:00Z",
        │     location: "San Francisco, CA",
        │     threat: "Data exfiltration detected",
        │     actions: "Component isolated, backup created"
        │   }
        │
        │ (8) Send via SMTP
        ├─→ Emergency contact 1: john@example.com
        ├─→ Emergency contact 2: jane@example.com
        └─→ Security team: security@company.com
        │
        │ (9) Log alert
        ↓
[Alert History File]
emergency_alerts_alice.json
```

### Data Structures
```python
# (4) Location Data
{
    "latitude": 37.7749,
    "longitude": -122.4194,
    "city": "San Francisco",
    "region": "California",
    "country": "United States",
    "ip": "192.168.1.50",
    "timestamp": "2024-01-15T10:30:00Z",
    "source": "ip"
}

# (6) Encrypted Location (Fernet)
{
    "encrypted_data": b"gAAAAABl...",  # Fernet-encrypted JSON
    "encryption_method": "Fernet",
    "key_id": "location_key_v1"
}

# (7) Alert Message
{
    "subject": "EMERGENCY ALERT - alice",
    "body": """
SECURITY INCIDENT ALERT

Incident ID: INC_1234567890
Severity: CRITICAL
Type: data_exfiltration
User: alice
Time: 2024-01-15 10:30:00 UTC

Location Information:
Latitude: 37.7749
Longitude: -122.4194
Address: San Francisco, California, United States

Description: Data exfiltration detected - active attack in progress

Automated responses executed:
- Component isolated
- Backup created
- IP blocked (192.168.1.100)
- Cerberus Hydra activated

Please review and take appropriate action.
    """
}

# (9) Alert Log Entry
{
    "timestamp": "2024-01-15T10:30:00Z",
    "username": "alice",
    "location_data": {...},  # Encrypted
    "message": "Data exfiltration detected",
    "incident_id": "INC_1234567890",
    "contacts_notified": [
        "john@example.com",
        "jane@example.com",
        "security@company.com"
    ],
    "delivery_status": "sent"
}
```

---

## Flow 5: Data Encryption Across Systems

### ASCII Diagram
```
┌─────────────────────────────────────────────────────┐
│                 GOD-TIER ENCRYPTION                 │
│                   (7 Layers)                        │
└─────────────────────────────────────────────────────┘
                       ↓ ↑
         ┌─────────────┴─┴─────────────┐
         │                              │
         ↓                              ↓
┌──────────────────┐          ┌──────────────────┐
│  Authentication  │          │  Location        │
│                  │          │  Tracker         │
│  Token Storage:  │          │                  │
│  - JWT signing   │          │  History:        │
│  - Refresh token │          │  - Fernet        │
│    encryption    │          │    encryption    │
└──────────────────┘          └──────────────────┘
         ↓                              ↓
         └─────────────┬─┬─────────────┘
                       ↓ ↑
         ┌─────────────┴─┴─────────────┐
         │                              │
         ↓                              ↓
┌──────────────────┐          ┌──────────────────┐
│  Incident        │          │  Emergency       │
│  Responder       │          │  Alert           │
│                  │          │                  │
│  Backups:        │          │  Sensitive Data: │
│  - 7-layer       │          │  - Fernet        │
│    encryption    │          │    encryption    │
└──────────────────┘          └──────────────────┘
```

### Data Flow: Backup Encryption
```
[Incident Responder] needs to backup data
        │
        │ (1) Read critical data
        ├─→ data/users.json
        ├─→ data/ai_persona/state.json
        └─→ data/memory/knowledge.json
        │
        │ (2) Combine into archive
        ↓
[Plaintext Backup]
    backup_INC_123_20240115.tar.gz
        │
        │ (3) Read binary data
        ↓
[God-Tier Encryption]
        │
        │ (4) Apply 7 layers:
        ├─→ Layer 1: SHA-512 hash (integrity)
        ├─→ Layer 2: Fernet (AES-128)
        ├─→ Layer 3: AES-256-GCM
        ├─→ Layer 4: ChaCha20-Poly1305
        ├─→ Layer 5: AES-256-GCM (rotated)
        ├─→ Layer 6: Quantum padding
        └─→ Layer 7: HMAC-SHA512 MAC
        │
        │ (5) Encrypted data
        ↓
[Encrypted Backup]
    backup_INC_123_20240115.tar.gz.enc
        │
        │ (6) Store securely
        ↓
[data/security/backups/]
```

---

## Flow 6: Threat Intelligence Feedback Loop

### ASCII Diagram
```
                    [Attack Detected]
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ↓               ↓               ↓
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ Honeypot │   │  Threat  │   │ OctoReflex│
    │          │   │ Detection│   │           │
    └──────────┘   └──────────┘   └──────────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                           ↓
                    ┌──────────────┐
                    │   Incident   │
                    │   Responder  │
                    └──────────────┘
                           │
                           │ (1) Log attack details
                           ↓
                    ┌──────────────┐
                    │   Security   │
                    │   Resources  │
                    └──────────────┘
                           │
                           │ (2) Store signature
                           │
                           │ (3) Distribute updates
           ┌───────────────┼───────────────┐
           │               │               │
           ↓               ↓               ↓
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ Honeypot │   │  Threat  │   │  Future  │
    │ Patterns │   │ Detection│   │  Attacks │
    │  Update  │   │  Patterns│   │ Blocked  │
    └──────────┘   └──────────┘   └──────────┘
```

### Data Flow: Signature Learning
```python
# (1) Attack detected
attack = {
    "payload": "'; DROP TABLE users--",
    "attack_type": "SQL_INJECTION",
    "tool": "custom_script",
    "success": False
}

# (2) Extract signature
signature = {
    "pattern": r"'; DROP TABLE",
    "category": "SQL_INJECTION",
    "severity": "CRITICAL",
    "first_seen": "2024-01-15T10:30:00Z",
    "count": 1
}

# (3) Store in Security Resources
security_resources.add_signature("SQL_INJECTION", signature)

# (4) Update Honeypot patterns
honeypot.sql_patterns.append(signature["pattern"])

# (5) Update Threat Detection
threat_detector.pattern_library.add_pattern(signature)

# (6) Future attacks blocked
next_attack = honeypot.analyze_request(payload="'; DROP TABLE accounts--")
assert next_attack is not None  # Now detected!
```

---

## Flow 7: Cross-System Data Exchange Format

### Standard Event Format
```json
{
    "event_id": "EVT_1234567890",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "source_system": "honeypot",
    "event_type": "attack_detected",
    "severity": "HIGH",
    "data": {
        "attack_type": "SQL_INJECTION",
        "ip_address": "192.168.1.100",
        "payload": "' OR 1=1--",
        "endpoint": "/api/users"
    },
    "metadata": {
        "user_agent": "sqlmap/1.0",
        "tool_detected": "sqlmap",
        "fingerprint": "a1b2c3d4"
    },
    "relationships": {
        "triggered_by": null,
        "triggers": ["threat_detection", "incident_responder"]
    }
}
```

---

## Related Systems

### Data Infrastructure
All data flows depend on robust data infrastructure for persistence and encryption:

- [[../data/00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure Overview]] - Foundation for security data storage and retrieval
- [[../data/01-PERSISTENCE-PATTERNS.md|Persistence Patterns]] - AttackAttempt storage, ThreatAssessment logs, agent registry, alert history
- [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]] - Location data encryption, token encryption, backup encryption, alert data
- [[../data/04-BACKUP-RECOVERY.md|Backup & Recovery]] - Incident backups, forensic preservation, quarantine storage

### Monitoring Systems
Security data flows generate comprehensive telemetry:

- [[../monitoring/01-logging-system.md|Logging System]] - All security events, data transformations, flow state transitions
- [[../monitoring/02-metrics-system.md|Metrics System]] - Flow latency, transformation time, data volume, success rates
- [[../monitoring/03-tracing-system.md|Tracing System]] - End-to-end data flow tracing across security systems
- [[../monitoring/06-error-tracking.md|Error Tracking]] - Flow failures, transformation errors, validation issues
- [[../monitoring/10-alerting-system.md|Alerting System]] - Flow anomalies, security events, critical incidents

### Configuration
Data flow behavior is controlled through configuration:

- [[../configuration/03_settings_validator_relationships.md|Settings Validator]] - Flow thresholds, validation rules, transformation rules
- [[../configuration/04_feature_flags_relationships.md|Feature Flags]] - Flow features, integration toggles, data routing
- [[../configuration/06_environment_variables_relationships.md|Environment Variables]] - API endpoints, service URLs, network configuration
- [[../configuration/07_secrets_management_relationships.md|Secrets Management]] - Encryption keys, API tokens, SMTP credentials, authentication secrets

### Data Flow Integration Points

**1. Detection Flow**
```
[Honeypot] → (AttackAttempt) → [Threat Detection] → (ThreatAssessment) → [OctoReflex]
     ↓             ↓                  ↓                    ↓                  ↓
[Logging]    [Persistence]       [Metrics]          [Persistence]      [Validation]
```

**2. Authentication Flow**
```
[Credentials] → [Hashing] → [Verification] → [Token Gen] → [Encryption] → [Storage]
       ↓            ↓            ↓               ↓              ↓            ↓
  [Logging]    [Metrics]    [Logging]      [Metrics]     [Encryption]  [Persistence]
```

**3. Emergency Flow**
```
[Incident] → [Location] → [Encryption] → [Alert] → [SMTP] → [Delivery]
     ↓           ↓            ↓            ↓         ↓          ↓
[Logging]   [Metrics]   [Encryption]  [Alerting] [Config]  [Logging]
```

---

**Next:** [07_security_metrics.md](./07_security_metrics.md) - Measurement relationships

---

## 📁 Source Code References

This documentation references the following source files:

- [[kernel/threat_detection.py]]
- [[src/app/core/cerberus_hydra.py]]
- [[src/app/core/emergency_alert.py]]
- [[src/app/core/honeypot_detector.py]]
- [[src/app/core/incident_responder.py]]
- [[src/app/core/octoreflex.py]]
- [[src/app/core/security_resources.py]]
- [[src/app/core/security/auth.py]]
- [[src/app/security/advanced/mfa_auth.py]]
- [[utils/encryption/god_tier_encryption.py]]

---
