# Security System Overview

**Document:** 01_security_system_overview.md  
**Purpose:** High-level architecture and system relationships  
**Classification:** AGENT-054 Security Documentation

---

## System Architecture

Project-AI implements a multi-layered security architecture with 10 core systems arranged in concentric defense rings.

### Defense Rings (Outside → Inside)

```
┌─────────────────────────────────────────────────────────┐
│  RING 1: PERIMETER DEFENSE                              │
│  ├── Honeypot Detector (Attack Bait & Analysis)         │
│  ├── Threat Detection Engine (AI-powered Analysis)      │
│  └── Security Resources (Threat Intelligence)           │
└─────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────┐
│  RING 2: AUTHENTICATION & ACCESS CONTROL                │
│  ├── Authentication System (JWT + Argon2 + MFA)         │
│  └── OctoReflex (Constitutional Enforcement)            │
└─────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────┐
│  RING 3: INCIDENT RESPONSE & ADAPTIVE DEFENSE           │
│  ├── Incident Responder (Automated Response)            │
│  └── Cerberus Hydra (Exponential Defense Spawning)      │
└─────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────┐
│  RING 4: DATA PROTECTION & EMERGENCY                    │
│  ├── Encryption (7-Layer God-Tier)                      │
│  ├── Location Tracker (Encrypted Tracking)              │
│  └── Emergency Alert (Emergency Notification)           │
└─────────────────────────────────────────────────────────┘
```

---

## Core Systems Detailed

### 1. OctoReflex - Constitutional Enforcement Layer

**Location:** [[src/app/core/octoreflex.py|OctoReflex Implementation]]  
**Purpose:** Syscall-level constitutional rule enforcement  
**Lines of Code:** 554

#### Capabilities:
- **Enforcement Levels:** MONITOR, WARN, BLOCK, TERMINATE, ESCALATE
- **Violation Types:** 15 types (AGI Charter, [[src/app/core/ai_systems.py#FourLaws|Four Laws]], Directness Doctrine, TSCG)
- **Default Rules:** 12 constitutional enforcement rules
- **Integration:** All systems must validate actions through [[src/app/core/octoreflex.py|OctoReflex]]

#### Key Methods:
```python
octoreflex.validate_syscall(event: SyscallEvent) -> Tuple[bool, List[Violation]]
octoreflex.validate_action(action_type: str, context: Dict) -> Tuple[bool, List[Violation]]
octoreflex.get_enforcement_stats() -> Dict[str, Any]
```

#### Relationships:
- **Consumes:** System calls from all components
- **Produces:** Violation records, enforcement actions
- **Triggers:** [[src/app/core/incident_responder.py|Incident Responder]] (on BLOCK/TERMINATE/ESCALATE)

#### Implementation

**Primary Controls:**

- [[src/app/core/octoreflex.py|OctoReflex]] - Implements Constitutional Enforcement
- [[src/app/core/octoreflex.py|OctoReflex]] - Implements Trust Boundaries validation
- [[src/app/core/octoreflex.py|OctoReflex]] - Mitigates TARL Runtime Attack Surface
- [[src/app/core/octoreflex.py|OctoReflex]] - Mitigates Governance Bypass Attack Surface

**Related Systems:**

- [[src/app/core/ai_systems.py#FourLaws|Four Laws Ethics System]]
- [[docs/security_compliance/ASL_FRAMEWORK.md|Constitutional AI Framework]]

---

### 2. Cerberus Hydra - Exponential Defense System

**Location:** [[src/app/core/cerberus_hydra.py|Cerberus Hydra Implementation]]  
**Purpose:** Spawn 3x new defense agents on each bypass  
**Lines of Code:** 1000+ (multi-file)

#### Capabilities:
- **Spawning Ratio:** 3 agents per bypass (exponential growth)
- **Language Matrix:** 50 human languages × 50 programming languages
- **Lockdown Stages:** 25 progressive stages (see [[src/app/core/cerberus_lockdown_controller.py|Lockdown Controller]])
- **Runtime Management:** Health verification, process lifecycle (see [[src/app/core/cerberus_runtime_manager.py|Runtime Manager]])
- **Deterministic Selection:** Seeded by incident ID

#### Components:
```python
cerberus_hydra.py              # Core defense orchestrator
cerberus_agent_process.py      # Cross-language process management
cerberus_lockdown_controller.py # Progressive lockdown stages
cerberus_runtime_manager.py    # Runtime health verification
cerberus_template_renderer.py  # Safe code generation
```

#### Relationships:
- **Triggered By:** [[src/app/core/incident_responder.py|Incident Responder]] (on bypass detection)
- **Validates With:** [[src/app/core/octoreflex.py|OctoReflex]] (all spawned agents)
- **Integrates With:** [[kernel/threat_detection.py|Threat Detection]] (risk scoring)
- **Reports To:** [[src/app/core/security_operations_center.py|Security Operations Center]]

#### Implementation

**Primary Controls:**

- [[src/app/core/cerberus_hydra.py|Cerberus Hydra]] - Implements Exponential Defense Spawning
- [[src/app/core/cerberus_hydra.py|Cerberus Hydra]] - Implements Adaptive Defense Systems
- [[src/app/core/cerberus_hydra.py|Cerberus Hydra]] - Implements Defense-in-Depth (adaptive layer)

**Secondary Controls:**

- [[src/app/core/cerberus_lockdown_controller.py|Lockdown Controller]] - 25 progressive lockdown stages
- [[src/app/core/cerberus_runtime_manager.py|Runtime Manager]] - Health verification
- [[src/app/core/cerberus_agent_process.py|Agent Process Manager]] - Cross-language spawning

---

### 3. Encryption - Multi-Layer Protection

**Location:** [[utils/encryption/god_tier_encryption.py|7-Layer Encryption Implementation]]  
**Purpose:** Military-grade 7-layer encryption  
**Lines of Code:** 373

#### Encryption Layers:
1. **SHA-512 Hash** - Integrity verification
2. **[[src/app/integrations/encryption_fernet.py|Fernet]]** - Symmetric encryption (AES-128 + HMAC-SHA256)
3. **AES-256-GCM** - Military-grade authenticated encryption
4. **ChaCha20-Poly1305** - High-speed authenticated encryption
5. **AES-256-GCM (rotated)** - Double encryption with key rotation
6. **Quantum-resistant padding** - Random padding (256-768 bytes)
7. **HMAC-SHA512** - Authentication MAC (500K iterations)

#### Key Features:
- **Quantum Resistance:** Scrypt KDF with n=2^20
- **Key Sizes:** AES-256, RSA-4096, ECC-521, ChaCha20-256
- **Perfect Forward Secrecy:** Supported
- **Zero-Knowledge Architecture:** Supported

#### Relationships:
- **Used By:** [[src/app/core/location_tracker.py|Location Tracker]] (Fernet for location data)
- **Used By:** [[src/app/core/security/auth.py|Authentication]] (Token encryption)
- **Used By:** [[src/app/core/incident_responder.py|Incident Responder]] (Backup encryption)

#### Implementation

**Primary Controls:**

- [[utils/encryption/god_tier_encryption.py|7-Layer Encryption]] - Implements Encryption at Rest
- [[utils/encryption/god_tier_encryption.py|7-Layer Encryption]] - Implements Defense-in-Depth (data protection layer)
- [[utils/encryption/god_tier_encryption.py|7-Layer Encryption]] - Mitigates Sensitive Data Exposure (OWASP)

**Secondary Controls:**

- [[src/app/integrations/encryption_fernet.py|Fernet Encryption]] - Symmetric encryption for location and sensitive storage
- [[src/app/core/location_tracker.py|Location Tracker]] - Encrypted location history

---

### 4. Authentication - Identity & Access Management

**Location:** [[src/app/core/security/auth.py|JWT Authentication Implementation]]  
**Purpose:** JWT + Argon2 + MFA authentication  
**Lines of Code:** 577

#### Features:
- **Password Hashing:** Argon2id (memory-hard, quantum-resistant)
- **Token System:** JWT with HS256 (24h access, 30d refresh)
- **MFA Support:** TOTP (6-digit) + backup codes (8-digit) (see [[src/app/security/advanced/mfa_auth.py|MFA Implementation]])
- **Token Rotation:** Automatic refresh token rotation
- **Revocation:** Token blacklist + user-level revocation

#### Security Properties:
- **JWT Secret:** Environment-based (must be 32+ bytes)
- **Hash Algorithm:** Argon2id (fallback: [[src/app/core/user_manager.py|bcrypt]])
- **MFA Algorithm:** TOTP (RFC 6238) with 1-step window

#### Implementation

**Primary Controls:**

- [[src/app/core/security/auth.py|JWT Authentication]] - Implements Secure Session Management
- [[src/app/core/security/auth.py|JWT Authentication]] - Implements Secure Password Hashing (Argon2id)
- [[src/app/core/security/auth.py|JWT Authentication]] - Mitigates Broken Authentication (OWASP)
- [[src/app/core/security/auth.py|JWT Authentication]] - Mitigates Web API Attack Surface
- [[src/app/core/security/auth.py|JWT Authentication]] - Implements Defense-in-Depth (authentication layer)

**Secondary Controls:**

- [[src/app/security/advanced/mfa_auth.py|MFA Authentication]] - TOTP-based Multi-Factor Authentication
- [[src/app/core/user_manager.py|User Manager]] - bcrypt password hashing, user management
- **Backup Codes:** 10 codes, single-use

#### Relationships:
- **Integrates With:** [[src/app/core/octoreflex.py|OctoReflex]] (token validation)
- **Triggers:** [[src/app/core/incident_responder.py|Incident Responder]] (on auth failures)
- **Uses:** [[utils/encryption/god_tier_encryption.py|7-Layer Encryption]] (for sensitive data)

---

### 5. Honeypot Detector - Attack Analysis

**Location:** [[src/app/core/honeypot_detector.py|Honeypot Detector Implementation]]  
**Purpose:** Detect and analyze attacks via fake endpoints  
**Lines of Code:** 508

#### Detection Patterns:
- **SQL Injection:** 6 patterns
- **XSS:** 5 patterns
- **Path Traversal:** 4 patterns
- **Command Injection:** 3 patterns

#### Tool Fingerprinting:
- sqlmap, nikto, Burp Suite, Metasploit, nmap, Acunetix, OWASP ZAP

#### Attack Profiling:
```python
class AttackerProfile:
    ip_address: str
    attempt_count: int
    attack_types_used: list[str]
    tools_detected: list[str]
    sophistication_score: float  # 0-10 scale
    targeting_pattern: str       # "random", "targeted", "automated"
```

#### Relationships:
- **Feeds Data To:** [[kernel/threat_detection.py|Threat Detection Engine]]
- **Triggers:** [[src/app/core/incident_responder.py|Incident Responder]] (on high-severity attacks)
- **Integrates With:** [[src/app/core/security_resources.py|Security Resources]] (for pattern updates)

#### Implementation

**Primary Controls:**

- [[src/app/core/honeypot_detector.py|Honeypot Detector]] - Implements Honeypot-Based Detection
- [[src/app/core/honeypot_detector.py|Honeypot Detector]] - Implements Threat Signature Database

**Secondary Controls:**

- [[kernel/threat_detection.py|Threat Detection Engine]] - Attack analysis and behavioral profiling

---

### 6. Incident Responder - Automated Response

**Location:** [[src/app/core/incident_responder.py|Incident Responder Implementation]]  
**Purpose:** Execute automated defensive response workflows  
**Lines of Code:** 564

#### Response Actions:
```python
class ResponseAction(Enum):
    ISOLATE_COMPONENT = "isolate_component"
    BACKUP_DATA = "backup_data"
    RESTORE_FROM_BACKUP = "restore_from_backup"
    ALERT_TEAM = "alert_team"
    BLOCK_IP = "block_ip"
    KILL_SESSION = "kill_session"
    RESET_CREDENTIALS = "reset_credentials"
    ENABLE_MFA = "enable_mfa"
    QUARANTINE_FILE = "quarantine_file"
    LOG_FORENSICS = "log_forensics"
    ESCALATE = "escalate"
```

#### Severity-Based Response:
- **CRITICAL:** Isolate + Block IP + Backup + Alert + Trigger [[src/app/core/cerberus_hydra.py|Cerberus]]
- **HIGH:** Isolate + Block IP + Backup + Alert
- **MEDIUM:** Block IP + Alert
- **LOW:** Log only

#### Relationships:
- **Triggered By:** [[kernel/threat_detection.py|Threat Detection]], [[src/app/core/octoreflex.py|OctoReflex]], [[src/app/core/honeypot_detector.py|Honeypot]]
- **Triggers:** [[src/app/core/cerberus_hydra.py|Cerberus Hydra]] (on bypass), [[src/app/core/emergency_alert.py|Emergency Alert]]
- **Integrates With:** All security systems

#### Implementation

**Primary Controls:**

- [[src/app/core/incident_responder.py|Incident Responder]] - Implements Incident Response workflows
- [[src/app/core/incident_responder.py|Incident Responder]] - Implements Adaptive Defense Systems
- [[src/app/core/incident_responder.py|Incident Responder]] - Implements Forensics Logging

**Related Systems:**

- [[docs/security_compliance/INCIDENT_PLAYBOOK.md|Incident Response Playbook]]
- [[relationships/security/04_incident_response_chains.md|Incident Response Chains]]

---

### 7. Threat Detection Engine - AI Analysis

**Location:** [[kernel/threat_detection.py|Threat Detection Engine Implementation]]  
**Purpose:** AI-powered threat detection and behavioral analysis  
**Lines of Code:** 486

#### Detection Techniques:
1. **Pattern Matching:** Known attack signatures
2. **Behavioral Analysis:** Command velocity, sequence patterns
3. **ML Prediction:** CodexDeus integration (simulated)
4. **Anomaly Detection:** Statistical analysis (see [[src/app/core/security_monitoring.py|Security Monitoring]])

#### Threat Levels:
```python
class ThreatLevel(Enum):
    SAFE = 0         # Allow
    SUSPICIOUS = 1   # Monitor
    MALICIOUS = 2    # Deception mode
    CRITICAL = 3     # Isolate immediately
```

#### Attack Pattern Library:
- Privilege Escalation
- Data Exfiltration
- Reconnaissance
- Credential Access
- Persistence
- Lateral Movement

#### Relationships:
- **Consumes:** Data from [[src/app/core/honeypot_detector.py|Honeypot]], [[src/app/core/security_resources.py|Security Resources]]
- **Produces:** Threat assessments
- **Triggers:** [[src/app/core/incident_responder.py|Incident Responder]]

#### Implementation

**Primary Controls:**

- [[kernel/threat_detection.py|Threat Detection Engine]] - Implements Behavioral Analysis
- [[kernel/threat_detection.py|Threat Detection Engine]] - Implements Anomaly Detection

**Related Systems:**

- [[src/app/monitoring/security_metrics.py|Security Metrics]] - Real-time threat metrics
- [[docs/security_compliance/THREAT_MODEL.md|Threat Model Documentation]]

---

### 8. Security Resources - Threat Intelligence

**Location:** [[src/app/core/security_resources.py|Security Resources Implementation]]  
**Purpose:** Manage CTF/security repositories and threat intelligence  
**Lines of Code:** 132

#### Resource Categories:
- **CTF_Security:** PayloadsAllTheThings, SecLists, PENTESTING-BIBLE
- **Privacy_Tools:** Privacy guides, cryptography tools
- **Security_Learning:** Hacking guides, hardening guides

#### Features:
- GitHub API integration
- Repository details fetching
- User favorites management
- Category-based filtering

#### Relationships:
- **Provides Data To:** [[kernel/threat_detection.py|Threat Detection]], [[src/app/core/honeypot_detector.py|Honeypot]]
- **Updated By:** Security analysts, threat feeds

#### Implementation

**Primary Controls:**

- [[src/app/core/security_resources.py|Security Resources]] - Implements Threat Intelligence database
- [[src/app/core/security_resources.py|Security Resources]] - Implements Security Knowledge management

**Related Systems:**

- [[src/app/core/cybersecurity_knowledge.py|Cybersecurity Knowledge Base]] - Comprehensive security patterns
- [[source-docs/infrastructure/07-security-resources.md|Security Resources Guide]]

---

### 9. Location Tracker - Encrypted Tracking

**Location:** [[src/app/core/location_tracker.py|Location Tracker Implementation]]  
**Purpose:** Track user location with encryption  
**Lines of Code:** 137

#### Features:
- **IP Geolocation:** ipapi.co integration
- **GPS Tracking:** Geopy Nominatim integration
- **Encryption:** [[src/app/integrations/encryption_fernet.py|Fernet]] symmetric encryption
- **History Management:** Encrypted history storage

#### Data Structure:
```python
{
    "latitude": float,
    "longitude": float,
    "city": str,
    "region": str,
    "country": str,
    "timestamp": str,
    "source": "ip" | "gps"
}
```

#### Relationships:
- **Uses:** [[src/app/integrations/encryption_fernet.py|Fernet Encryption]]
- **Consumed By:** [[src/app/core/emergency_alert.py|Emergency Alert system]]

#### Implementation

**Primary Controls:**

- [[src/app/core/location_tracker.py|Location Tracker]] - Implements Encryption at Rest (location data)
- [[src/app/core/location_tracker.py|Location Tracker]] - Implements Data Protection (encrypted storage)

**Related:**

- [[source-docs/integrations/09-encryption-fernet.md|Fernet Encryption Guide]]

---

### 10. Emergency Alert - Emergency Notification

**Location:** [[src/app/core/emergency_alert.py|Emergency Alert Implementation]]  
**Purpose:** Send emergency alerts to registered contacts  
**Lines of Code:** 137

#### Features:
- **SMTP Integration:** Configurable mail server
- **Emergency Contacts:** Per-user contact lists
- **Location Integration:** Includes [[src/app/core/location_tracker.py|location data]] in alerts
- **Alert History:** JSON-based alert logging

#### Alert Format:
```
EMERGENCY ALERT
User: {username}
Time: {timestamp}
Location: {city, region, country, lat/long}
Message: {custom_message}
```

#### Relationships:
- **Triggered By:** [[src/app/core/incident_responder.py|Incident Responder]] (on critical events)
- **Uses:** [[src/app/core/location_tracker.py|Location Tracker]] (for emergency location)
- **Integrates With:** SMTP server (configurable)

#### Implementation

**Primary Controls:**

- [[src/app/core/emergency_alert.py|Emergency Alert]] - Implements Emergency Notification system
- [[src/app/core/emergency_alert.py|Emergency Alert]] - Implements Critical Event Response

---

## System Interaction Patterns

### Pattern 1: Attack Detection → Response

```
[Honeypot] detects attack
    ↓
[Threat Detection] analyzes pattern
    ↓
[Incident Responder] executes response
    ↓
[Cerberus Hydra] spawns defenders (if bypass)
```

### Pattern 2: Authentication Flow

```
[User] attempts login
    ↓
[Authentication] verifies credentials
    ↓
[OctoReflex] validates action
    ↓
[Access Granted] or [Incident Responder] triggered
```

### Pattern 3: Data Protection

```
[Sensitive Data] needs protection
    ↓
[Encryption] encrypts with 7 layers
    ↓
[Storage] encrypted at rest
    ↓
[Location Tracker] stores encrypted history
```

---

## Integration Points

### All Systems → OctoReflex
Every system must validate actions through OctoReflex for constitutional compliance.

### All Systems → Incident Responder
All systems can trigger incident response workflows for defensive actions.

### Threat Detection ← Honeypot + Security Resources
Threat Detection consumes data from Honeypot attacks and Security Resources intelligence.

### Emergency Alert ← Location Tracker + Incident Responder
Emergency Alert uses Location Tracker data when triggered by Incident Responder.

---

## Security Metrics

| System | Key Metric | Target |
|--------|-----------|--------|
| OctoReflex | Violations blocked | > 99% |
| Cerberus Hydra | Agent spawn rate | 3x on bypass |
| Encryption | Decryption failures | < 0.01% |
| Authentication | Token compromise rate | 0% |
| Honeypot | Attack detection rate | > 95% |
| Incident Responder | Response time | < 1s |
| Threat Detection | False positive rate | < 5% |
| Security Resources | Repository freshness | < 7 days |
| Location Tracker | Encryption integrity | 100% |
| Emergency Alert | Delivery success | > 98% |

---

## Cross-System Dependencies

### Data Infrastructure Integration
All security systems depend on robust data infrastructure for state management and persistence:

- [[../data/00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure Overview]] - Central data architecture supporting all security systems
- [[../data/01-PERSISTENCE-PATTERNS.md|Persistence Patterns]] - User credentials, attack signatures, agent state, incident logs, threat profiles
- [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]] - JWT tokens, location history, backups, emergency alerts, sensitive data
- [[../data/04-BACKUP-RECOVERY.md|Backup & Recovery]] - Forensic backups, incident preservation, data recovery workflows

### Monitoring & Observability Integration
Security systems generate comprehensive telemetry across all monitoring channels:

- [[../monitoring/01-logging-system.md|Logging System]] - Attack logs, authentication events, constitutional violations, agent spawning, emergency alerts
- [[../monitoring/02-metrics-system.md|Metrics System]] - Threat detection accuracy, response times, enforcement rates, agent counts, encryption performance
- [[../monitoring/05-performance-monitoring.md|Performance Monitoring]] - System latency, validation overhead, response execution time
- [[../monitoring/06-error-tracking.md|Error Tracking]] - Detection failures, authentication errors, encryption failures, integration issues
- [[../monitoring/10-alerting-system.md|Alerting System]] - Security alerts, incident notifications, emergency broadcasts, escalation triggers

### Configuration Management Integration
Security behavior is controlled through centralized configuration:

- [[../configuration/03_settings_validator_relationships.md|Settings Validator]] - Security thresholds, rate limits, IP blacklists, enforcement rules, lockdown stages
- [[../configuration/04_feature_flags_relationships.md|Feature Flags]] - Security features, defense mechanisms, integration toggles, key rotation
- [[../configuration/06_environment_variables_relationships.md|Environment Variables]] - API endpoints, network configuration, external service URLs, geolocation services
- [[../configuration/07_secrets_management_relationships.md|Secrets Management]] - Encryption keys, SMTP credentials, API tokens, MFA secrets, JWT signing keys

### System Orchestration Patterns

**1. Detection → Analysis → Enforcement → Response**
```
[Honeypot] → [Threat Detection] → [OctoReflex] → [Incident Responder]
     ↓              ↓                  ↓                ↓
[Logging]      [Metrics]         [Config]        [Alerting]
     ↓              ↓                  ↓                ↓
[Persistence]  [Dashboard]    [Validation]      [Emergency]
```

**2. Data Security Flow**
```
[User Data] → [Authentication] → [Encrypted] → [Persisted] → [Monitored]
                     ↓                ↓            ↓            ↓
              [JWT Tokens]    [Encryption]  [Persistence]  [Logging]
                     ↓                ↓            ↓            ↓
              [OctoReflex]    [7 Layers]    [Backup]      [Metrics]
```

**3. Incident Response Flow**
```
[Threat Detected] → [Severity Assessment] → [Response Workflow] → [Recovery]
        ↓                   ↓                      ↓                  ↓
   [Logging]           [Metrics]            [Actions]          [Backup]
        ↓                   ↓                      ↓                  ↓
   [Alerting]          [Dashboard]          [Isolation]        [Restore]
```

### Configuration Dependencies

| Security System | Configuration Sources | Secrets Required | Monitored Metrics |
|----------------|----------------------|------------------|-------------------|
| OctoReflex | Settings Validator, Feature Flags | None | Violations, Enforcement Rate |
| Cerberus Hydra | Feature Flags, Settings Validator | None | Agent Count, Spawn Rate |
| Encryption | Secrets Management | Encryption Keys | Encryption Time, Failures |
| Authentication | Secrets Management, Settings Validator | JWT Keys, MFA Secrets | Auth Failures, Token Issues |
| Honeypot | Settings Validator | None | Detection Rate, Attacks |
| Incident Responder | Settings Validator, Feature Flags | None | Response Time, Success Rate |
| Threat Detection | Settings Validator | None | Accuracy, False Positives |
| Security Resources | Environment Variables | API Keys | Repository Freshness |
| Location Tracker | Environment Variables, Secrets Management | Encryption Keys | Location Accuracy |
| Emergency Alert | Secrets Management, Environment Variables | SMTP Credentials | Delivery Success |

---

**Next:** [02_threat_models.md](./02_threat_models.md) - Detailed threat model relationships

---


---

## Related Security Documentation

- [[relationships\security\02_threat_models.md|02 threat models]]
- [[relationships\security\03_defense_layers.md|03 defense layers]]
- [[relationships\security\04_incident_response_chains.md|04 incident response chains]]

---
## 📁 Source Code References

This documentation references the following source files:

- [[kernel/threat_detection.py]]
- [[src/app/core/cerberus_agent_process.py]]
- [[src/app/core/cerberus_hydra.py]]
- [[src/app/core/cerberus_lockdown_controller.py]]
- [[src/app/core/cerberus_runtime_manager.py]]
- [[src/app/core/cerberus_template_renderer.py]]
- [[src/app/core/emergency_alert.py]]
- [[src/app/core/honeypot_detector.py]]
- [[src/app/core/incident_responder.py]]
- [[src/app/core/location_tracker.py]]
- [[src/app/core/octoreflex.py]]
- [[src/app/core/security_resources.py]]
- [[src/app/core/security/auth.py]]
- [[src/app/security/advanced/mfa_auth.py]]
- [[utils/encryption/god_tier_encryption.py]]

---
