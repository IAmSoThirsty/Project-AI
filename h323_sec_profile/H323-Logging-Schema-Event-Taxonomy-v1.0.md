# H.323 Logging Schema & Event Taxonomy
Version 1.0 — Standardized Log Fields, Event Types, and Severity Model

## 1. Purpose
Defines the canonical logging schema for all H.323 components, ensuring consistent event structure, severity classification, and SIEM ingestion across the enterprise.

## 2. Core Log Categories
1. RAS Events
2. H.225 Signaling Events
3. H.245 Control Events
4. Media Events (SRTP/RTP)
5. Security Events (H.235)
6. PKI Events
7. Gateway Events
8. Network Events
9. System Events

## 3. Standard Log Fields

### 3.1 Mandatory Fields
Every log entry MUST include:
- **timestamp**: ISO 8601 UTC timestamp (e.g., `2026-01-23T10:30:45.123Z`)
- **component_type**: `gatekeeper`, `gateway`, `endpoint`, `mcu`
- **component_id**: Unique identifier (hostname, IP, or H.323 ID)
- **event_category**: RAS, H225, H245, MEDIA, SECURITY, PKI, GATEWAY, NETWORK, SYSTEM
- **event_type**: Specific event name (e.g., `RRQ`, `SRTP_ESTABLISHED`, `CERT_EXPIRED`)
- **severity**: CRITICAL, ERROR, WARN, INFO, DEBUG
- **outcome**: SUCCESS, FAILURE, PARTIAL

### 3.2 Optional Fields
Contextual information based on event type:
- **source_id**: Originating endpoint/component
- **dest_id**: Destination endpoint/component
- **call_id**: H.323 call identifier
- **conference_id**: Conference identifier (for MCU)
- **reason_code**: H.225 cause code or error code
- **reason_text**: Human-readable explanation
- **h235_token_valid**: true/false (for RAS events)
- **cipher_suite**: Negotiated cipher (for SRTP events)
- **certificate_serial**: X.509 certificate serial number
- **ip_src**: Source IP address
- **ip_dst**: Destination IP address
- **bandwidth_kbps**: Allocated bandwidth
- **codec**: Audio/video codec in use

### 3.3 Example Log Entry (JSON)
```json
{
  "timestamp": "2026-01-23T10:30:45.123Z",
  "component_type": "gatekeeper",
  "component_id": "gk-primary.example.com",
  "event_category": "RAS",
  "event_type": "RRQ",
  "severity": "INFO",
  "outcome": "SUCCESS",
  "source_id": "ep-conference-room-101",
  "h235_token_valid": true,
  "ip_src": "10.1.50.25",
  "reason_text": "Endpoint registered successfully"
}
```

## 4. Event Taxonomy

### 4.1 RAS Events

#### Registration Events
- **RRQ** (Registration Request)
  - Severity: INFO (success), ERROR (failure)
  - Fields: source_id, h235_token_valid, ip_src
  - Outcome: SUCCESS, FAILURE
  
- **RCF** (Registration Confirm)
  - Severity: INFO
  - Fields: source_id, ttl_seconds
  
- **RRJ** (Registration Reject)
  - Severity: ERROR
  - Fields: source_id, reason_code, reason_text

#### Admission Events
- **ARQ** (Admission Request)
  - Severity: INFO (success), WARN (denied)
  - Fields: source_id, dest_id, bandwidth_kbps, call_id
  
- **ACF** (Admission Confirm)
  - Severity: INFO
  - Fields: call_id, bandwidth_allocated_kbps
  
- **ARJ** (Admission Reject)
  - Severity: WARN
  - Fields: call_id, reason_code (e.g., "BANDWIDTH_EXCEEDED")

#### Disengage Events
- **DRQ** (Disengage Request)
  - Severity: INFO
  - Fields: call_id, reason_code
  
- **DCF** (Disengage Confirm)
  - Severity: INFO

### 4.2 H.225 Signaling Events

- **SETUP**
  - Severity: INFO (secure), ERROR (insecure)
  - Fields: source_id, dest_id, call_id, h235_mode
  
- **CALL_PROCEEDING**
  - Severity: INFO
  
- **ALERTING**
  - Severity: INFO
  
- **CONNECT**
  - Severity: INFO (secure), CRITICAL (insecure)
  - Fields: call_id, encryption_enabled
  
- **RELEASE_COMPLETE**
  - Severity: INFO
  - Fields: call_id, reason_code, duration_seconds

- **H225_SECURITY_MODE_NEGOTIATION**
  - Severity: INFO (success), ERROR (failure)
  - Fields: call_id, h235_profile, outcome

### 4.3 H.245 Control Events

- **TERMINAL_CAPABILITY_SET**
  - Severity: INFO
  - Fields: source_id, codec_list
  
- **MASTER_SLAVE_DETERMINATION**
  - Severity: DEBUG
  
- **OPEN_LOGICAL_CHANNEL**
  - Severity: INFO (SRTP), CRITICAL (RTP)
  - Fields: call_id, media_type, srtp_enabled, cipher_suite
  
- **CLOSE_LOGICAL_CHANNEL**
  - Severity: INFO
  
- **H245_SECURITY_MODE**
  - Severity: INFO (success), ERROR (failure)
  - Fields: call_id, h235_4_enabled, outcome

### 4.4 Media Events

- **SRTP_ESTABLISHED**
  - Severity: INFO
  - Fields: call_id, cipher_suite, key_length_bits
  
- **RTP_FALLBACK_DETECTED**
  - Severity: CRITICAL
  - Fields: call_id, source_id, dest_id, reason_text
  
- **MEDIA_PATH_BLOCKED**
  - Severity: ERROR
  - Fields: call_id, ip_src, ip_dst, reason_text
  
- **PACKET_LOSS_THRESHOLD_EXCEEDED**
  - Severity: WARN
  - Fields: call_id, packet_loss_percent, threshold_percent
  
- **JITTER_THRESHOLD_EXCEEDED**
  - Severity: WARN
  - Fields: call_id, jitter_ms, threshold_ms
  
- **SRTCP_INTEGRITY_FAILURE**
  - Severity: ERROR
  - Fields: call_id, source_id

### 4.5 Security Events (H.235)

- **H235_TOKEN_VALIDATION_SUCCESS**
  - Severity: INFO
  - Fields: source_id, token_type
  
- **H235_TOKEN_VALIDATION_FAILURE**
  - Severity: ERROR
  - Fields: source_id, reason_code, reason_text
  
- **H235_DOWNGRADE_ATTEMPT**
  - Severity: CRITICAL
  - Fields: source_id, attempted_mode, required_mode
  
- **H235_REPLAY_ATTACK_DETECTED**
  - Severity: CRITICAL
  - Fields: source_id, ip_src, timestamp_drift_seconds
  
- **CLEARTEXT_SIGNALING_DETECTED**
  - Severity: CRITICAL
  - Fields: source_id, dest_id, call_id
  
- **CLEARTEXT_MEDIA_DETECTED**
  - Severity: CRITICAL
  - Fields: call_id, ip_src, ip_dst

### 4.6 PKI Events

- **CERTIFICATE_VALIDATED**
  - Severity: INFO
  - Fields: certificate_serial, subject_dn, issuer_dn
  
- **CERTIFICATE_VALIDATION_FAILURE**
  - Severity: ERROR
  - Fields: certificate_serial, reason_code, reason_text
  
- **CERTIFICATE_EXPIRING_SOON**
  - Severity: WARN
  - Fields: certificate_serial, subject_dn, days_until_expiry
  
- **CERTIFICATE_EXPIRED**
  - Severity: ERROR
  - Fields: certificate_serial, subject_dn, expired_date
  
- **CERTIFICATE_REVOKED**
  - Severity: ERROR
  - Fields: certificate_serial, revocation_date, reason_code
  
- **CRL_OCSP_UNREACHABLE**
  - Severity: ERROR
  - Fields: ocsp_url, reason_text
  
- **TRUST_CHAIN_FAILURE**
  - Severity: ERROR
  - Fields: certificate_serial, reason_text

### 4.7 Gateway Events

- **TRUNK_UP**
  - Severity: INFO
  - Fields: trunk_id, trunk_type (PSTN, ISDN, H320, SIP)
  
- **TRUNK_DOWN**
  - Severity: ERROR
  - Fields: trunk_id, reason_text
  
- **CODEC_TRANSCODING**
  - Severity: INFO
  - Fields: call_id, codec_in, codec_out
  
- **GATEWAY_SRTP_TERMINATION**
  - Severity: INFO
  - Fields: call_id, cipher_suite
  
- **GATEWAY_REGISTRATION_FAILURE**
  - Severity: ERROR
  - Fields: gateway_id, gatekeeper_id, reason_text
  
- **CDR_GENERATED**
  - Severity: INFO
  - Fields: call_id, duration_seconds, source_id, dest_id, codec

### 4.8 Network Events

- **FIREWALL_BLOCK**
  - Severity: WARN
  - Fields: ip_src, ip_dst, port_src, port_dst, rule_id
  
- **QOS_QUEUE_CONGESTION**
  - Severity: WARN
  - Fields: queue_name, utilization_percent
  
- **DSCP_MISMATCH**
  - Severity: WARN
  - Fields: expected_dscp, actual_dscp, ip_src
  
- **VLAN_ISOLATION_VIOLATION**
  - Severity: CRITICAL
  - Fields: source_vlan, dest_vlan, ip_src, ip_dst

### 4.9 System Events

- **SERVICE_STARTED**
  - Severity: INFO
  - Fields: service_name, version
  
- **SERVICE_STOPPED**
  - Severity: WARN
  - Fields: service_name, reason_text
  
- **CONFIGURATION_CHANGED**
  - Severity: INFO
  - Fields: admin_id, change_description
  
- **HEALTH_CHECK_FAILURE**
  - Severity: ERROR
  - Fields: check_name, reason_text

## 5. Severity Model

### 5.1 CRITICAL
**Definition**: Immediate threat to confidentiality, integrity, or availability requiring instant action.

**Examples**:
- Cleartext H.225 or H.245 signaling detected
- RTP detected instead of SRTP
- H.235 downgrade attempt
- VLAN isolation violation
- PKI compromise
- Unauthorized endpoint accepted

**Response Time**: Immediate (SOC alerted, automated containment)

### 5.2 ERROR
**Definition**: Security control failure or operational issue requiring prompt attention.

**Examples**:
- Registration failures (RRJ)
- SRTP negotiation failure
- Certificate validation failure
- Certificate expired
- Trust chain failure
- Gateway registration failure
- Trunk down

**Response Time**: Within 1 hour

### 5.3 WARN
**Definition**: Potential security or operational issue requiring investigation.

**Examples**:
- Certificate expiring within 30 days
- Admission request denied (ARJ) due to bandwidth
- Packet loss threshold exceeded
- Jitter threshold exceeded
- QoS queue congestion
- CRL/OCSP temporarily unreachable

**Response Time**: Within 4 hours

### 5.4 INFO
**Definition**: Normal operational events for auditing and troubleshooting.

**Examples**:
- Successful registration (RCF)
- Successful call setup (CONNECT)
- SRTP established
- Certificate validated
- Trunk up
- Normal call teardown

**Response Time**: Routine review

### 5.5 DEBUG
**Definition**: Detailed diagnostic information for troubleshooting.

**Examples**:
- Capability exchange details
- Master/slave determination
- Internal state transitions

**Response Time**: N/A (developer use only)

## 6. SIEM Integration Requirements

### 6.1 Log Format
- **Primary Format**: JSON (structured)
- **Fallback Format**: CEF (Common Event Format)
- **Transport**: Syslog over TLS (RFC 5425)

### 6.2 Required Mappings
Map H.323 events to SIEM categories:
- RAS/H.225/H.245 → Authentication/Access
- SRTP/RTP → Data Loss Prevention
- H.235 Security → Intrusion Detection
- PKI → Identity Management
- Gateway → Network Security
- Firewall → Perimeter Defense

### 6.3 Retention Requirements
- CRITICAL: 7 years
- ERROR: 3 years
- WARN: 1 year
- INFO: 90 days
- DEBUG: 7 days

## 7. Alerting Rules

### 7.1 Critical Alerts (Immediate)
- `event_type == "CLEARTEXT_SIGNALING_DETECTED"`
- `event_type == "CLEARTEXT_MEDIA_DETECTED"`
- `event_type == "H235_DOWNGRADE_ATTEMPT"`
- `event_type == "VLAN_ISOLATION_VIOLATION"`
- `event_type == "H235_REPLAY_ATTACK_DETECTED"`

### 7.2 High-Priority Alerts (1 hour)
- `event_type == "CERTIFICATE_EXPIRED"`
- `event_type == "TRUST_CHAIN_FAILURE"`
- `event_type == "GATEWAY_REGISTRATION_FAILURE" AND outcome == "FAILURE"`
- `event_type == "RRJ" AND count > 5 in 5 minutes`

### 7.3 Medium-Priority Alerts (4 hours)
- `event_type == "CERTIFICATE_EXPIRING_SOON" AND days_until_expiry < 7`
- `event_type == "TRUNK_DOWN"`
- `event_type == "QOS_QUEUE_CONGESTION" AND utilization_percent > 90`

## 8. Log Aggregation & Correlation

### 8.1 Call Flow Correlation
Correlate all events with same `call_id`:
1. ARQ → ACF
2. SETUP → CONNECT
3. OLC → SRTP_ESTABLISHED
4. RELEASE_COMPLETE → DRQ → DCF

### 8.2 Security Incident Correlation
Correlate security events by `source_id` and time window:
- Multiple H235_TOKEN_VALIDATION_FAILURE within 5 minutes → potential attack
- RRJ followed by CLEARTEXT_SIGNALING_DETECTED → downgrade attack

### 8.3 Performance Correlation
Correlate performance events:
- PACKET_LOSS_THRESHOLD_EXCEEDED + JITTER_THRESHOLD_EXCEEDED → QoS issue
- Multiple TRUNK_DOWN events → carrier issue

## 9. Compliance Requirements

### 9.1 Audit Trail Completeness
Every call MUST have:
- Registration event (RRQ/RCF)
- Admission event (ARQ/ACF)
- Call setup event (SETUP/CONNECT)
- Security mode negotiation (H235)
- Media establishment (SRTP_ESTABLISHED)
- Call teardown (RELEASE_COMPLETE, DRQ/DCF)

### 9.2 Tamper Evidence
All logs MUST:
- Include cryptographic signatures (HMAC-SHA256)
- Be shipped to SIEM within 60 seconds
- Be immutable once written

### 9.3 Privacy Compliance
Logs MUST NOT include:
- Full phone numbers (mask: +1-800-555-XXXX)
- User personal data beyond H.323 ID
- SRTP keying material

## 10. Implementation Guidance

### 10.1 Gatekeeper Logging
```python
import json
import logging
from datetime import datetime

def log_ras_event(event_type, source_id, outcome, **kwargs):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "component_type": "gatekeeper",
        "component_id": "gk-primary.example.com",
        "event_category": "RAS",
        "event_type": event_type,
        "severity": "INFO" if outcome == "SUCCESS" else "ERROR",
        "outcome": outcome,
        "source_id": source_id,
        **kwargs
    }
    logging.info(json.dumps(entry))
```

### 10.2 Gateway Logging
```python
def log_gateway_event(event_type, severity, **kwargs):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "component_type": "gateway",
        "component_id": "gw-dmz-01.example.com",
        "event_category": "GATEWAY",
        "event_type": event_type,
        "severity": severity,
        **kwargs
    }
    logging.info(json.dumps(entry))
```

## 11. Completion Criteria
Logging is compliant when:
- All components emit events in standard schema
- All required fields present
- Severity model correctly applied
- Logs reach SIEM within 60 seconds
- Alerting rules configured
- Retention policies enforced
- Correlation rules active
