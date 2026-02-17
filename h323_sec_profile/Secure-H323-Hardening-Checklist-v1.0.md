# Secure H.323 Hardening Checklist

## Version 1.0 — Gatekeeper, Gateway, Endpoint, Network, PKI

## 1. Gatekeeper (GK) Hardening Checklist

### 1.1 PKI & Identity

- [ ] Install X.509 certificate from Voice/Video Intermediate CA
- [ ] Import full CA chain (Root + Intermediate)
- [ ] Enable CRL/OCSP checking
- [ ] Enforce fail‑closed on revocation failure
- [ ] SAN includes correct FQDN

### 1.2 RAS Security (H.235.2)

- [ ] Require H.235.2 tokens for RRQ
- [ ] Require H.235.2 tokens for ARQ
- [ ] Require H.235.2 tokens for DRQ
- [ ] Enforce timestamp + nonce validation
- [ ] Reject endpoints with invalid or missing tokens

### 1.3 Signaling Security (H.235.3/4)

- [ ] Enable H.225 integrity + encryption
- [ ] Enable H.245 integrity + encryption
- [ ] Enable TLS/IPsec for signaling transport
- [ ] Reject insecure signaling attempts
- [ ] Log all downgrade attempts

### 1.4 Admission Control

- [ ] Configure per‑call bandwidth limits
- [ ] Configure per‑endpoint call limits
- [ ] Configure per‑gateway call limits
- [ ] Enforce call model (direct or gatekeeper‑routed)

### 1.5 Address Resolution

- [ ] Define H.323 ID → IP mappings
- [ ] Define E.164 → endpoint mappings
- [ ] Define E.164 → gateway mappings
- [ ] Validate LRQ/LCF routing rules

### 1.6 Logging & Monitoring

- [ ] Enable RAS logging
- [ ] Enable signaling security logging
- [ ] Forward logs to SIEM
- [ ] Enable alerting for auth failures
- [ ] Enable alerting for security downgrades

## 2. Gateway (GW) Hardening Checklist

### 2.1 System Hardening

- [ ] Disable unused services
- [ ] Restrict management to admin VLAN
- [ ] Enforce strong admin authentication
- [ ] Enable secure NTP
- [ ] Apply latest firmware

### 2.2 PKI

- [ ] Install gateway certificate
- [ ] Import CA chain
- [ ] Enable CRL/OCSP
- [ ] Enforce mutual TLS with GK
- [ ] Enforce mutual TLS with endpoints (if direct signaling)

### 2.3 H.323 Security

- [ ] Enable H.235.2 for RAS
- [ ] Enable H.235.3 for H.225
- [ ] Enable H.235.4 for H.245
- [ ] Require SRTP (H.235.6) for media
- [ ] Reject insecure signaling/media

### 2.4 Legacy Side

- [ ] Configure ISDN/H.320/PSTN trunks
- [ ] Validate codec mapping
- [ ] Ensure no SRTP keys leak to legacy side
- [ ] Enforce physical security on trunk interfaces

### 2.5 Network Placement

- [ ] Inside interface in Voice/Video DMZ
- [ ] Outside interface to carrier/legacy
- [ ] No direct access from endpoint VLANs
- [ ] Firewall restricts all non‑required ports

### 2.6 Logging

- [ ] Enable CDRs
- [ ] Enable security logs
- [ ] Forward logs to SIEM
- [ ] Enable alerts for trunk failures
- [ ] Enable alerts for H.235 negotiation failures

## 3. Endpoint (EP) Hardening Checklist

### 3.1 PKI

- [ ] Install device/user certificate
- [ ] Import CA chain
- [ ] Enable CRL/OCSP
- [ ] Enforce certificate‑based identity

### 3.2 RAS

- [ ] Configure GK address (FQDN preferred)
- [ ] Enable H.235.2 tokens
- [ ] Enable auto‑registration
- [ ] Reject insecure RAS

### 3.3 Signaling

- [ ] Enable H.235.3 for H.225
- [ ] Enable H.235.4 for H.245
- [ ] Enable TLS/IPsec
- [ ] Reject insecure signaling

### 3.4 Media

- [ ] Enable SRTP
- [ ] Disable RTP fallback
- [ ] Restrict to AES‑based ciphers
- [ ] Enable SRTCP integrity

### 3.5 Codec & Bandwidth

- [ ] Enable G.711 (mandatory)
- [ ] Enable optional codecs (G.729, H.263/H.26x)
- [ ] Set max bitrate per policy

### 3.6 Local Security

- [ ] Lock admin UI
- [ ] Disable auto‑answer unless required
- [ ] Disable external control unless required
- [ ] Enforce strong local passwords

## 4. Network Hardening Checklist

### 4.1 VLAN Segmentation

- [ ] Voice/Video VLANs for endpoints
- [ ] DMZ VLAN for gateways
- [ ] Management VLAN for GK/GW/MCU
- [ ] PKI/Infrastructure VLAN

### 4.2 Firewall Rules

**EP → GK:**

- [ ] Allow RAS (UDP 1719/1718)
- [ ] Allow H.225/H.245 (TCP 1720/TLS + fixed H.245 range)

**EP → GW:**

- [ ] Allow H.225/H.245
- [ ] Allow SRTP media ports

**GK → GW:**

- [ ] Allow RAS + H.225

**DMZ → Carrier:**

- [ ] Allow only carrier‑required signaling/media

### 4.3 ACL Enforcement

- [ ] Block EP ↔ EP direct signaling
- [ ] Block unauthorized ports
- [ ] Block legacy domain from reaching H.323 zone

### 4.4 QoS

- [ ] Mark signaling as CS3/AF31
- [ ] Mark voice as EF
- [ ] Mark video as AF41
- [ ] Enable priority queuing

## 5. PKI Hardening Checklist

### 5.1 CA Infrastructure

- [ ] Offline Root CA
- [ ] Voice/Video Intermediate CA
- [ ] Secure CRL/OCSP endpoints
- [ ] Harden CA servers

### 5.2 Certificate Lifecycle

- [ ] Enforce certificate expiration policy
- [ ] Revoke unused certificates
- [ ] Monitor upcoming expirations
- [ ] Validate certificate issuance logs

### 5.3 Trust Enforcement

- [ ] Fail‑closed on revocation failure
- [ ] Enforce mutual TLS
- [ ] Enforce certificate‑based H.235 tokens

## 6. Monitoring & Logging Hardening Checklist

### 6.1 SIEM Integration

- [ ] Forward GK logs
- [ ] Forward GW logs
- [ ] Forward endpoint logs (where supported)
- [ ] Forward PKI logs
- [ ] Forward firewall logs

### 6.2 Alerting

- [ ] Authentication failures
- [ ] Security downgrades
- [ ] Trunk failures
- [ ] Certificate failures
- [ ] QoS degradation

### 6.3 Time Sync

- [ ] All components use secure NTP
- [ ] Drift < 1 second

## 7. Compliance & Audit Hardening Checklist

### 7.1 Annual Audit

- [ ] PKI audit
- [ ] Firewall audit
- [ ] H.235 enforcement audit
- [ ] SRTP enforcement audit
- [ ] Network segmentation audit

### 7.2 Change Control

- [ ] Document all GK/GW changes
- [ ] Document PKI changes
- [ ] Document firewall changes
- [ ] Maintain rollback plans

---

## Using Project-AI Tools for Hardening Validation

### Automated Compliance Check

```bash

# Validate hardening configuration

python h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance \
    --config hardening_config.json
```

### Sample Hardening Configuration

```json
{
  "component": "gatekeeper",
  "pki": {
    "certificate_installed": true,
    "ca_chain_complete": true,
    "crl_ocsp_enabled": true,
    "fail_closed": true
  },
  "ras_security": {
    "h235_2_required": true,
    "timestamp_validation": true,
    "nonce_validation": true
  },
  "signaling_security": {
    "h225_protected": true,
    "h245_protected": true,
    "tls_ipsec_enabled": true,
    "reject_insecure": true
  },
  "logging": {
    "ras_logging": true,
    "security_logging": true,
    "siem_forwarding": true
  }
}
```

### Checklist Validation API

```bash

# Start API service

cd h323_sec_profile
uvicorn project_ai_fastapi:app --host 0.0.0.0 --port 8080

# Validate checklist items

curl -X POST http://localhost:8080/compliance/check \
    -H "Content-Type: application/json" \
    -d @hardening_config.json
```

### Logging Hardening Actions

```bash

# Log hardening task completion

python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
    --event-type hardening_task \
    --device-id gk1 \
    --outcome completed

# Log via API

curl -X POST http://localhost:8080/log \
    -H "Content-Type: application/json" \
    -d '{
        "event_type": "hardening_checklist_completed",
        "device_id": "gk1.voice.example.com",
        "outcome": "success",
        "details": {"tasks_completed": 25, "tasks_total": 25}
    }'
```

---

## Related Documentation

- [Secure-H323-Zone-Standard-v1.0.md](./Secure-H323-Zone-Standard-v1.0.md) - Security requirements
- [Secure-H323-Implementation-Guide-v1.0.md](./Secure-H323-Implementation-Guide-v1.0.md) - Implementation procedures
- [H323-H235-Compliance-Matrix-v1.0.md](./H323-H235-Compliance-Matrix-v1.0.md) - Compliance requirements
- [H323-H235-Security-Test-Plan-v1.0.md](./H323-H235-Security-Test-Plan-v1.0.md) - Validation tests
- [Secure-H323-Operational-Runbook-v1.0.md](./Secure-H323-Operational-Runbook-v1.0.md) - Operations manual

## Appendix: Hardening Completion Report Template

```
═══════════════════════════════════════════════════════════════
SECURE H.323 HARDENING COMPLETION REPORT
═══════════════════════════════════════════════════════════════

Component: [GK/GW/EP/Network]
Date: [DATE]
Engineer: [NAME]

SUMMARY
-------
Total Items: [N]
Completed: [M]
Not Applicable: [X]
Pending: [P]
Completion %: [%]

GATEKEEPER HARDENING
--------------------
PKI & Identity: [X/Y] ✓
RAS Security: [X/Y] ✓
Signaling Security: [X/Y] ✓
Admission Control: [X/Y] ✓
Address Resolution: [X/Y] ✓
Logging & Monitoring: [X/Y] ✓

GATEWAY HARDENING
-----------------
System Hardening: [X/Y] ✓
PKI: [X/Y] ✓
H.323 Security: [X/Y] ✓
Legacy Side: [X/Y] ✓
Network Placement: [X/Y] ✓
Logging: [X/Y] ✓

ENDPOINT HARDENING
------------------
PKI: [X/Y] ✓
RAS: [X/Y] ✓
Signaling: [X/Y] ✓
Media: [X/Y] ✓
Codec & Bandwidth: [X/Y] ✓
Local Security: [X/Y] ✓

NETWORK HARDENING
-----------------
VLAN Segmentation: [X/Y] ✓
Firewall Rules: [X/Y] ✓
ACL Enforcement: [X/Y] ✓
QoS: [X/Y] ✓

PKI HARDENING
-------------
CA Infrastructure: [X/Y] ✓
Certificate Lifecycle: [X/Y] ✓
Trust Enforcement: [X/Y] ✓

MONITORING & LOGGING
--------------------
SIEM Integration: [X/Y] ✓
Alerting: [X/Y] ✓
Time Sync: [X/Y] ✓

PENDING ITEMS
-------------
[List any pending items with target completion dates]

DEVIATIONS
----------
[Document any approved deviations from the checklist]

VALIDATION
----------
Compliance Check: [PASS/FAIL]
Security Test: [PASS/FAIL]

APPROVAL
--------
__________________  __________________  __________________
Engineer            Security Lead       Operations Lead

Date: [DATE]        Date: [DATE]        Date: [DATE]
```
