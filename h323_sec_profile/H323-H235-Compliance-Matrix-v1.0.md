# H.323 / H.235 Compliance Matrix

## Version 1.0 — Enterprise Certification Grid

## 1. Purpose

This matrix defines every requirement an H.323 deployment must meet to be considered compliant with:

- Secure H.323 Zone Standard
- Secure H.323 Implementation Guide
- Secure H.323 Operational Runbook
- H.235 security profiles (2, 3, 4, 6, 7)
- Enterprise PKI and network security policies

Each requirement is mapped to:

- Component (EP, GK, GW, MCU, Network, PKI)
- Requirement Type (Security, PKI, Network, Operational)
- Mandatory/Optional
- Verification Method
- Pass/Fail Criteria

This is the authoritative compliance document for audits and certification.

## 2. Compliance Matrix

Below is the full matrix, organized by category.

### 2.1 PKI & Identity Compliance

| ID | Requirement | Component | Type | M/O | Verification Method | Pass Criteria | Fail Criteria |
|----|------------|-----------|------|-----|-------------------|---------------|---------------|
| PKI-001 | Valid X.509 certificate installed | EP, GK, GW, MCU | PKI | M | Inspect certificate | Valid cert from Voice/Video CA | Invalid, expired, or self-signed |
| PKI-002 | Certificate contains proper SAN | EP, GK, GW, MCU | PKI | M | openssl x509 -text | SAN includes FQDN + H.323 ID | Missing SAN |
| PKI-003 | Certificate key strength ≥ RSA 2048 or ECC P-256 | EP, GK, GW, MCU | PKI | M | openssl x509 -text | Key meets minimum | Weak key |
| PKI-004 | CA chain complete and trusted | EP, GK, GW, MCU | PKI | M | Verify trust store | Full chain to Root CA | Broken chain |
| PKI-005 | CRL/OCSP checking enabled | EP, GK, GW, MCU | Security | M | Config inspection | CRL/OCSP configured | Disabled |
| PKI-006 | Revoked certificates rejected | EP, GK, GW, MCU | Security | M | Test with revoked cert | Registration/call rejected | Revoked cert accepted |
| PKI-007 | Certificate expiry monitoring | All | Operational | M | Check monitoring system | Alerts for certs expiring <30 days | No monitoring |
| PKI-008 | Certificate renewal process documented | PKI | Operational | M | Review procedures | Documented process exists | No documentation |

### 2.2 RAS Security Compliance (H.235.2)

| ID | Requirement | Component | Type | M/O | Verification Method | Pass Criteria | Fail Criteria |
|----|------------|-----------|------|-----|-------------------|---------------|---------------|
| RAS-001 | H.235.2 tokens required for RRQ | GK | Security | M | GK config + logs | All RRQ require valid tokens | Tokenless RRQ accepted |
| RAS-002 | H.235.2 tokens required for ARQ | GK | Security | M | GK config + logs | All ARQ require valid tokens | Tokenless ARQ accepted |
| RAS-003 | H.235.2 tokens required for DRQ | GK | Security | M | GK config + logs | All DRQ require valid tokens | Tokenless DRQ accepted |
| RAS-004 | Timestamp validation enabled | GK | Security | M | GK config | Timestamp checked | No timestamp validation |
| RAS-005 | Nonce anti-replay enabled | GK | Security | M | GK config + test | Replay rejected | Replay accepted |
| RAS-006 | Unauthorized endpoints rejected | GK | Security | M | Test with untrusted cert | Registration rejected | Unauthorized EP accepted |
| RAS-007 | RAS ports (1718/1719) firewalled | Network | Security | M | Firewall rules | Only authorized access | Open to all |
| RAS-008 | RAS events logged | GK | Operational | M | Check logs | RRQ/ARQ/DRQ logged | No logging |

### 2.3 H.225 Signaling Security Compliance (H.235.3)

| ID | Requirement | Component | Type | M/O | Verification Method | Pass Criteria | Fail Criteria |
|----|------------|-----------|------|-----|-------------------|---------------|---------------|
| H225-001 | H.235.3 security mandatory | EP, GK, GW | Security | M | Config + packet capture | All H.225 protected | Clear-text H.225 |
| H225-002 | TLS/IPsec transport enabled | EP, GK, GW | Security | M | Config + packet capture | TLS/IPsec established | Clear-text transport |
| H225-003 | SETUP message encrypted | EP, GW | Security | M | Packet capture | SETUP protected | Clear-text SETUP |
| H225-004 | CONNECT message encrypted | EP, GW | Security | M | Packet capture | CONNECT protected | Clear-text CONNECT |
| H225-005 | Downgrade to insecure rejected | GK | Security | M | Test insecure request | Call rejected | Insecure call accepted |
| H225-006 | Strong cipher suites only | EP, GK, GW | Security | M | Config inspection | AES-128+ only | Weak ciphers enabled |
| H225-007 | H.225 port (1720) firewalled | Network | Security | M | Firewall rules | Only authorized access | Open to all |
| H225-008 | Call setup events logged | GK, GW | Operational | M | Check logs | SETUP/CONNECT logged | No logging |

### 2.4 H.245 Control Security Compliance (H.235.4)

| ID | Requirement | Component | Type | M/O | Verification Method | Pass Criteria | Fail Criteria |
|----|------------|-----------|------|-----|-------------------|---------------|---------------|
| H245-001 | H.235.4 security mandatory | EP, GW | Security | M | Config + packet capture | All H.245 protected | Clear-text H.245 |
| H245-002 | SecurityMode negotiation required | EP, GW | Security | M | Packet capture + logs | SecurityMode negotiated | No negotiation |
| H245-003 | OLC messages encrypted | EP, GW | Security | M | Packet capture | OLC protected | Clear-text OLC |
| H245-004 | SRTP keys in secure OLC | EP, GW | Security | M | H.245 inspection | SRTP keys present | Missing SRTP keys |
| H245-005 | Logical channels require SRTP | EP, GW | Security | M | Config + verification | All channels use SRTP | RTP channels allowed |
| H245-006 | H.245 port range firewalled | Network | Security | M | Firewall rules | Only authorized range | Unrestricted |
| H245-007 | Capability exchange logged | EP, GW | Operational | M | Check logs | Capabilities logged | No logging |

### 2.5 Media Security Compliance (H.235.6 / SRTP)

| ID | Requirement | Component | Type | M/O | Verification Method | Pass Criteria | Fail Criteria |
|----|------------|-----------|------|-----|-------------------|---------------|---------------|
| SRTP-001 | SRTP mandatory for all media | EP, GW, MCU | Security | M | Packet capture | All media is SRTP | RTP detected |
| SRTP-002 | AES-128 or stronger | EP, GW, MCU | Security | M | Config inspection | AES-128+ configured | Weak ciphers |
| SRTP-003 | SRTCP for RTCP | EP, GW, MCU | Security | M | Packet capture | RTCP encrypted | Clear RTCP |
| SRTP-004 | No RTP fallback allowed | EP, GW, MCU | Security | M | Config inspection | RTP disabled | RTP fallback enabled |
| SRTP-005 | Media ports firewalled | Network | Security | M | Firewall rules | Fixed range (16384-32767) | Unrestricted |
| SRTP-006 | Key rotation supported | EP, GW, MCU | Security | O | Config inspection | Key rotation available | Not supported |
| SRTP-007 | Media encryption logged | GW | Operational | M | Check logs | SRTP status logged | No logging |

### 2.6 Gateway Interworking Compliance

| ID | Requirement | Component | Type | M/O | Verification Method | Pass Criteria | Fail Criteria |
|----|------------|-----------|------|-----|-------------------|---------------|---------------|
| GW-001 | IP-side uses full H.235 stack | GW | Security | M | Config + testing | All H.235 profiles active | Any profile missing |
| GW-002 | Gateway is crypto boundary | GW | Security | M | Architecture review | SRTP ↔ TDM conversion | SRTP keys exposed |
| GW-003 | Legacy side physically secured | GW | Security | M | Physical inspection | Trunk access controlled | Unsecured access |
| GW-004 | Codec mapping configured | GW | Network | M | Config inspection | Proper transcoding | Codec mismatch |
| GW-005 | CDR generation enabled | GW | Operational | M | Check CDRs | All calls generate CDRs | No CDRs |
| GW-006 | Gateway in DMZ VLAN | Network | Security | M | Network diagram | GW in DMZ | GW in EP VLAN |
| GW-007 | Redundant gateways deployed | GW | Operational | O | Inventory | ≥2 gateways | Single gateway |
| GW-008 | Failover tested | GW | Operational | M | Failover test | Calls continue | Calls drop |

### 2.7 Network Segmentation & Firewall Compliance

| ID | Requirement | Component | Type | M/O | Verification Method | Pass Criteria | Fail Criteria |
|----|------------|-----------|------|-----|-------------------|---------------|---------------|
| NET-001 | Voice/Video VLAN for EPs | Network | Network | M | Network config | Dedicated VLAN | Shared VLAN |
| NET-002 | DMZ VLAN for GWs | Network | Network | M | Network config | Dedicated DMZ | GW in EP VLAN |
| NET-003 | Management VLAN for admin | Network | Network | M | Network config | Dedicated mgmt VLAN | Admin on prod VLAN |
| NET-004 | EP cannot reach EP directly | Network | Security | M | Test direct connection | Blocked by firewall | Direct connection works |
| NET-005 | Firewall rules documented | Network | Operational | M | Review documentation | Rules documented | No documentation |
| NET-006 | Only approved ports open | Network | Security | M | Port scan | Expected ports only | Extra ports open |
| NET-007 | ACLs reviewed quarterly | Network | Operational | M | Review schedule | Regular reviews | No reviews |
| NET-008 | Network diagram current | Network | Operational | M | Review diagram | Up to date | Outdated |

### 2.8 QoS Compliance

| ID | Requirement | Component | Type | M/O | Verification Method | Pass Criteria | Fail Criteria |
|----|------------|-----------|------|-----|-------------------|---------------|---------------|
| QOS-001 | DSCP marking: Signaling CS3/AF31 | Network | Network | M | Packet capture | Correct marking | Incorrect/missing |
| QOS-002 | DSCP marking: Voice EF | Network | Network | M | Packet capture | EF marking | Incorrect/missing |
| QOS-003 | DSCP marking: Video AF41 | Network | Network | M | Packet capture | AF41 marking | Incorrect/missing |
| QOS-004 | Priority queuing enabled | Network | Network | M | Config inspection | Queues configured | No QoS |
| QOS-005 | Bandwidth limits enforced | GK | Network | M | GK config | Per-call limits set | No limits |
| QOS-006 | Jitter < 30ms | Network | Network | M | Performance test | Meets threshold | Exceeds threshold |
| QOS-007 | Latency < 150ms | Network | Network | M | Performance test | Meets threshold | Exceeds threshold |
| QOS-008 | Packet loss < 1% | Network | Network | M | Performance test | Meets threshold | Exceeds threshold |

### 2.9 Operational Compliance

| ID | Requirement | Component | Type | M/O | Verification Method | Pass Criteria | Fail Criteria |
|----|------------|-----------|------|-----|-------------------|---------------|---------------|
| OPS-001 | NTP sync on all components | All | Operational | M | Check time sources | All synced | Unsynchronized |
| OPS-002 | Daily health checks performed | All | Operational | M | Review logs | Checks documented | No checks |
| OPS-003 | Weekly log review | All | Operational | M | Review process | Reviews documented | No reviews |
| OPS-004 | Monthly security audit | All | Operational | M | Audit schedule | Regular audits | No audits |
| OPS-005 | Incident response plan | All | Operational | M | Review plan | Plan exists | No plan |
| OPS-006 | Change control process | All | Operational | M | Review process | Process documented | No process |
| OPS-007 | Backup/restore procedures | GK, GW | Operational | M | Test restore | Successful restore | Restore fails |
| OPS-008 | Redundancy validated | GK, GW | Operational | M | Failover test | Failover works | Failover fails |

### 2.10 Logging & Monitoring Compliance

| ID | Requirement | Component | Type | M/O | Verification Method | Pass Criteria | Fail Criteria |
|----|------------|-----------|------|-----|-------------------|---------------|---------------|
| LOG-001 | Centralized logging configured | All | Operational | M | Check log forwarding | All logs to SIEM | Local only |
| LOG-002 | Security events logged | All | Security | M | Check logs | Events captured | Missing events |
| LOG-003 | Authentication failures logged | GK | Security | M | Test + verify logs | Failures logged | No logging |
| LOG-004 | Downgrade attempts logged | GK, GW | Security | M | Test + verify logs | Attempts logged | No logging |
| LOG-005 | CDRs generated for all calls | GW | Operational | M | Check CDR records | All calls have CDRs | Missing CDRs |
| LOG-006 | Alerting configured | All | Operational | M | Test alerts | Alerts received | No alerts |
| LOG-007 | Log retention ≥ 90 days | All | Operational | M | Check retention policy | Meets requirement | <90 days |
| LOG-008 | Logs protected from tampering | All | Security | M | Review log security | Encrypted/signed logs | Unprotected |

## 3. Compliance Scoring

### 3.1 Scoring Model

- **100% compliance** = fully certified
- **95–99%** = certified with minor exceptions
- **80–94%** = conditional certification (must remediate)
- **<80%** = non‑compliant

**Calculation:**
```
Compliance Score = (Passed Mandatory Requirements / Total Mandatory Requirements) × 100
```

### 3.2 Critical Failures

Any of the following = **automatic failure** (regardless of score):

- Clear‑text H.225 or H.245 (H225-001, H245-001)
- RTP instead of SRTP (SRTP-001)
- Invalid or expired certificates (PKI-001)
- Disabled CRL/OCSP (PKI-005)
- Unauthorized endpoints accepted (RAS-006)
- Firewall allows direct EP ↔ EP signaling (NET-004)
- Downgrade to insecure allowed (H225-005)
- SRTP keys missing in OLC (H245-004)

## 4. Certification Process

### Step 1: Preparation

- Gather configs, diagrams, certs, logs
- Review all documentation
- Prepare test environment
- Notify stakeholders

### Step 2: Execution

- Perform all tests in this matrix
- Document results in real-time
- Capture evidence (logs, screenshots, packet captures)

### Step 3: Scoring

- Assign pass/fail per requirement
- Calculate compliance score
- Identify critical failures

### Step 4: Review

- Architecture board reviews results
- Discuss exceptions and remediation plans
- Approve certification or remediation timeline

### Step 5: Certification

- Issue compliance certificate (if passed)
- Document valid period (12 months)
- Schedule next audit

### Step 6: Remediation

- Fix failures
- Re‑test affected requirements
- Update documentation

## 5. Completion Criteria

A deployment is **fully compliant** when:

- All mandatory requirements pass
- No critical failures exist
- All H.235 profiles enforced (2, 3, 4, 6)
- All media is SRTP
- All PKI checks pass
- All network segmentation validated
- All logs and alerts verified
- Compliance score ≥ 95%

## 6. Using Project-AI Tools for Compliance

### Automated Compliance Validation

```bash

# Run comprehensive compliance check

python h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance \
    --config deployment_config.json

# Expected output format:

# PASS or detailed list of failures

```

### Sample Deployment Configuration

```json
{
  "all_devices_support_h235": true,
  "mandatory_tls_on_h225": true,
  "srtp_everywhere": true,
  "has_logging": true,
  "pki_enforced": true,
  "components": {
    "gatekeepers": ["gk1.example.com", "gk2.example.com"],
    "gateways": ["gw1.example.com", "gw2.example.com"],
    "endpoints": ["ep1.example.com", "..."]
  },
  "security_profiles": {
    "h235_2_ras": true,
    "h235_3_h225": true,
    "h235_4_h245": true,
    "h235_6_srtp": true
  }
}
```

### API-Based Validation

```bash

# Start API service

cd h323_sec_profile
uvicorn project_ai_fastapi:app --host 0.0.0.0 --port 8080

# Check compliance via API

curl -X POST http://localhost:8080/compliance/check \
    -H "Content-Type: application/json" \
    -d @deployment_config.json

# Log compliance results

curl -X POST http://localhost:8080/log \
    -H "Content-Type: application/json" \
    -d '{
        "event_type": "compliance_check",
        "device_id": "audit-system",
        "outcome": "pass",
        "details": {"score": 100, "critical_failures": 0}
    }'
```

### Continuous Monitoring

```bash

# Daily compliance validation

0 2 * * * /usr/bin/python /opt/h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance --config /etc/h323/prod_config.json >> /var/log/h323_compliance.log 2>&1

# Weekly detailed audit

0 3 * * 0 /opt/scripts/weekly_h323_audit.sh
```

---

## Related Documentation

- [H323-H235-Security-Test-Plan-v1.0.md](./H323-H235-Security-Test-Plan-v1.0.md) - Detailed test procedures
- [Secure-H323-Zone-Standard-v1.0.md](./Secure-H323-Zone-Standard-v1.0.md) - Requirements specification
- [Secure-H323-Implementation-Guide-v1.0.md](./Secure-H323-Implementation-Guide-v1.0.md) - Deployment guide
- [Secure-H323-Operational-Runbook-v1.0.md](./Secure-H323-Operational-Runbook-v1.0.md) - Operations manual
- [H323_SEC_PROFILE_v1.py](./H323_SEC_PROFILE_v1.py) - Automation tools
- [project_ai_fastapi.py](./project_ai_fastapi.py) - REST API service

## Appendix A: Compliance Report Template

```
═══════════════════════════════════════════════════════════════
H.323 / H.235 COMPLIANCE AUDIT REPORT
═══════════════════════════════════════════════════════════════

Audit Date: [DATE]
Auditor: [NAME]
Deployment: [ENVIRONMENT]

EXECUTIVE SUMMARY
-----------------
Total Requirements: [N]
Mandatory Requirements: [M]
Passed: [P]
Failed: [F]
Compliance Score: [SCORE]%

Certification Status: [PASS/CONDITIONAL/FAIL]
Critical Failures: [Y/N]

DETAILED RESULTS
----------------
[Table of all requirements with pass/fail status]

CRITICAL FAILURES
-----------------
[List any critical failures that result in automatic failure]

REMEDIATION PLAN
----------------
[Details of how failures will be addressed]

CERTIFICATION
-------------
[Approved/Denied]
Valid Until: [DATE]
Next Audit: [DATE]

Signatures:
__________________  __________________  __________________
Security Lead       Architecture Lead   Operations Lead
```
