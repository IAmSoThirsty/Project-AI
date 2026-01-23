## 7. Configuration Baselines

### Gatekeeper Baseline
- Mandatory TLS for H.225
- Mandatory H.235.2 tokens for RAS
- Reject endpoints without valid SAN/FQDN
- Enforce CRL/OCSP checks
- Enforce bandwidth and call admission policies
- Log all ARQ/ACF, LRQ/LCF, RRQ/RCF

### Gateway Baseline
- Must terminate SRTP on IP side
- Must enforce codec policy (G.711 mandatory, others optional)
- Must enforce signaling security (H.235.3)
- Must isolate PSTN/ISDN interfaces from IP zone
- Must log IAM/ACM/ANM/REL/CLR events

### Endpoint Baseline
- Must support H.235.1/2/3/4/6
- Must support SRTP AES‑128 or AES‑256
- Must validate GK certificate
- Must restrict dynamic port ranges
- Must rotate keys per call

## 8. Failure & Redundancy Behavior

### Gatekeeper Failover
- Endpoints must maintain alternate GK list
- RRQ retry timers defined
- Calls in progress continue (GK not in media path)

### Gateway Failover
- GK must reroute ARQ to alternate GW
- Media re-establishment rules defined
- PSTN fallback behavior documented

### Certificate Failures
- Hard fail on expired certs
- Soft fail on unreachable OCSP (configurable)
- Mandatory logging of all failures

### Media Path Failures
- SRTP rekeying behavior
- H.245 channel renegotiation rules
- Graceful fallback to audio‑only

## 9. Compliance Requirements

### 10.1 Mandatory Protocol & Security Requirements
- All H.323 devices MUST support H.235.1/2/3/4/6.
- All H.225 signaling MUST be protected with TLS or H.235.3 integrity mechanisms.
- All media MUST use SRTP with AES-128 or stronger.
- All devices MUST authenticate using enterprise-issued X.509 certificates.
- All devices MUST validate CRL/OCSP status for every certificate.
- All RAS messages MUST include H.235.2 tokens for authentication and replay protection.
- All endpoints MUST register to the Gatekeeper before placing or receiving calls.

### 10.2 Mandatory Topology & Routing Requirements
- All endpoints MUST reside in dedicated voice/video VLANs.
- All gateways MUST reside in a DMZ VLAN with strict firewall boundaries.
- All PSTN/ISDN access MUST traverse the gateway; no direct endpoint access permitted.
- All dynamic port ranges MUST be explicitly defined and enforced.

### 10.3 Mandatory Operational Requirements
- All certificate failures MUST be logged.
- All call setup events MUST be logged.
- All devices MUST support secure firmware updates.
- All devices MUST rotate SRTP keys per call.

## 10. Management-Plane Security

### 11.1 Administrative Access
- All administrative interfaces MUST use secure protocols:
    - SSHv2 (password auth disabled; key-based only)
    - HTTPS/TLS 1.2+
    - SNMPv3 (authPriv mode)
- Default credentials MUST be disabled.
- Role-based access control (RBAC) MUST be enforced on GK, GW, and MCU.
- Administrative access MUST be restricted to management VLANs only.

### 11.2 Configuration Management
- All configuration changes MUST be logged with timestamp, admin ID, and device ID.
- All devices MUST support signed firmware images.
- All devices MUST support secure backup/restore of configuration.

### 11.3 Monitoring & Telemetry
- SNMPv3 MUST be used for performance and health monitoring.
- Syslog over TLS MUST be used for centralized logging.
- NetFlow/IPFIX SHOULD be enabled for traffic visibility.
- All devices MUST expose metrics for:
    - Registration status
    - Call counts
    - Bandwidth usage
    - SRTP encryption status

## 11. Logging & Audit Schema

### 12.1 Gatekeeper Logging Requirements
The GK MUST log:
- All RAS events (GRQ/GCF, RRQ/RCF, ARQ/ACF, LRQ/LCF)
- All certificate validation events
- All admission decisions (allowed/denied)
- All endpoint registration changes
- All failover events

### 12.2 Gateway Logging Requirements
The GW MUST log:
- All H.225 call setup events
- All H.245 negotiation events
- All SRTP keying events
- All PSTN/ISDN signaling events (IAM, ACM, ANM, REL, CLR)
- All certificate validation events
- All codec negotiation outcomes

### 12.3 Endpoint Logging Requirements
Endpoints SHOULD log:
- Registration success/failure
- Certificate validation results
- Call setup attempts
- Media negotiation results
- SRTP status

### 12.4 Log Format & Retention
- Logs MUST include timestamp, device ID, event type, and outcome.
- Logs MUST be retained for a minimum of 12 months.
- Logs MUST be exportable in JSON or syslog format.
- Logs MUST be protected from tampering (WORM storage recommended).
