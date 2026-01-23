# Incident Response Playbook for H.323 Security Events

## Version 1.0 — Detection, Containment, Eradication, Recovery

## 1. Purpose

This playbook defines the end‑to‑end incident response workflow for all security events involving:

- H.235 authentication failures
- Signaling downgrade attempts
- SRTP failures
- Certificate or PKI issues
- Gateway compromise or trunk abuse
- Unauthorized endpoint activity
- Network segmentation violations
- QoS degradation affecting confidentiality or integrity

It is designed for SOC, NOC, PKI, and Voice/Video Engineering teams.

## 2. Incident Severity Classification

### 2.1 Critical Severity (P1)

**Immediate threat to confidentiality, integrity, or availability.**

**Examples:**

- Clear‑text H.225 or H.245 detected
- RTP instead of SRTP
- Compromised gateway
- PKI compromise
- Unauthorized endpoint successfully registered
- Firewall bypass enabling EP ↔ EP direct signaling

**Response Time:** Immediate (< 15 minutes)

### 2.2 High Severity (P2)

**Security controls degraded but not fully bypassed.**

**Examples:**

- Repeated H.235 token failures
- Failed SecurityMode negotiation
- Certificate expiration within 24 hours
- Trunk instability affecting secure interworking

**Response Time:** < 1 hour

### 2.3 Medium Severity (P3)

**Operational issues with potential security impact.**

**Examples:**

- CRL/OCSP unreachable
- NTP drift > 1 second
- QoS degradation affecting media integrity

**Response Time:** < 4 hours

### 2.4 Low Severity (P4)

**Minor issues requiring routine remediation.**

**Examples:**

- Endpoint misconfiguration
- Non‑critical log anomalies

**Response Time:** < 24 hours

## 3. Roles & Responsibilities

### 3.1 SOC (Security Operations Center)

- Lead incident triage
- Analyze logs and alerts
- Coordinate containment actions
- Escalate to PKI/Voice teams
- Document incident timeline

### 3.2 NOC (Network Operations Center)

- Validate firewall, VLAN, QoS integrity
- Assist with containment and isolation
- Monitor network health
- Execute network-level remediation

### 3.3 Voice/Video Engineering

- Validate GK/GW/EP configurations
- Perform signaling/media analysis
- Restore secure call flows
- Execute component-level remediation

### 3.4 PKI Team

- Validate certificate integrity
- Revoke compromised certificates
- Issue replacement certificates
- Restore CRL/OCSP services

## 4. Incident Response Workflow

### 4.1 Phase 1 — Detection

**Detection Sources:**

- SIEM alerts
- GK logs (RAS failures, downgrades)
- GW logs (H.235 failures, trunk issues)
- Endpoint logs
- Firewall logs
- Packet captures (SRTP/RTP detection)

**Immediate Actions:**

1. Classify severity
1. Notify SOC lead
1. Open incident ticket
1. Begin log preservation
1. Initiate appropriate response based on severity

**Using Project-AI Tools:**
```bash
# Log incident detection
python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
    --event-type incident_detected \
    --device-id <affected-component> \
    --outcome investigating

# API logging
curl -X POST http://localhost:8080/log \
    -H "Content-Type: application/json" \
    -d '{
        "event_type": "security_incident",
        "device_id": "gk1.voice.example.com",
        "outcome": "detected",
        "details": {"severity": "P1", "type": "cleartext_signaling"}
    }'
```

### 4.2 Phase 2 — Triage

**Key Questions:**

- Is signaling secure?
- Is media encrypted?
- Are certificates valid?
- Is the gateway behaving normally?
- Is the issue isolated or widespread?

**Data to Collect:**

- GK RAS logs
- H.225/H.245 captures
- SRTP/RTP captures
- Gateway CDRs
- Firewall logs
- Certificate status

**Analysis Commands:**
```bash
# Check registration status
python h323_sec_profile/H323_SEC_PROFILE_v1.py reg-status \
    --device-ip <device-ip> \
    --snmp-user admin \
    --auth-key <key> \
    --priv-key <key>

# Run compliance check
python h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance \
    --config deployment_config.json
```

### 4.3 Phase 3 — Containment

**Containment Actions (Based on Severity)**

**Critical (P1):**

- Immediately block affected endpoint(s) at firewall
- Disable endpoint registration in GK
- Remove gateway from service if compromised
- Revoke certificates if needed
- Force signaling to secure mode only

**High (P2):**

- Restrict affected VLAN
- Disable insecure cipher suites
- Force re‑registration of endpoints
- Restart signaling stack on GK/GW

**Medium (P3):**

- Correct NTP drift
- Restore CRL/OCSP availability
- Adjust QoS queues

**Low (P4):**

- Apply configuration fixes
- Update endpoint firmware

**Containment Logging:**
```bash
# Log containment actions
python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
    --event-type incident_contained \
    --device-id <component> \
    --outcome success
```

### 4.4 Phase 4 — Eradication

**Tasks:**

- Remove malicious or unauthorized endpoints
- Revoke compromised certificates
- Patch GK/GW/EP firmware
- Correct misconfigurations
- Replace compromised keys
- Restore firewall ACL integrity
- Validate VLAN isolation

**Validation:**
```bash
# Verify security profiles
python h323_sec_profile/H323_SEC_PROFILE_v1.py run-sim

# Check compliance post-remediation
python h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance \
    --config deployment_config.json
```

### 4.5 Phase 5 — Recovery

**Recovery Steps:**

1. Reintroduce gateway into service
1. Re‑enable endpoint registration
1. Validate secure signaling (H.235.3/4)
1. Validate SRTP media (H.235.6)
1. Validate RAS authentication (H.235.2)
1. Perform controlled test calls
1. Monitor for recurrence (72 hours)

**Recovery Validation:**
```bash
# Test secure call setup
python h323_sec_profile/H323_SEC_PROFILE_v1.py run-sim

# API validation
curl -X POST http://localhost:8080/compliance/check \
    -H "Content-Type: application/json" \
    -d @deployment_config.json
```

## 5. Detailed Playbooks for Common Incidents

### 5.1 Incident: Clear‑Text H.225 or H.245 Detected (Critical - P1)

**Symptoms:**

- Packet capture shows unencrypted signaling
- GK logs show insecure call attempts
- Endpoint reports "security mode failed"

**Actions:**

1. **Immediate Containment (< 5 minutes)**

   ```bash
   # Block affected endpoint at firewall
   # (Platform-specific firewall command)
   
   # Disable in GK
   # (Platform-specific GK command)
   ```

1. **Triage (< 15 minutes)**
   - Capture signaling packets
   - Review GK security logs
   - Identify affected endpoints

1. **Investigation**
   - Validate endpoint certificate
   - Validate GK/GW TLS/IPsec configuration
   - Check for configuration drift
   - Review recent changes

1. **Eradication**
   - Force secure signaling mode on GK
   - Update endpoint configuration
   - Patch firmware if needed

1. **Recovery**
   - Re-enable endpoint with secure config
   - Perform test call
   - Monitor for 72 hours

1. **Documentation**

   ```bash
   python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
       --event-type incident_resolved \
       --device-id <endpoint> \
       --outcome success
   ```

### 5.2 Incident: RTP Detected Instead of SRTP (Critical - P1)

**Symptoms:**

- RTP packets visible in capture
- Missing SRTP keying in OLC
- Gateway media path failure
- Clear audio patterns in packet dump

**Actions:**

1. **Immediate Containment**
   - Block media ports for affected endpoint/gateway
   - Terminate active calls

1. **Triage**

   ```bash
   # Capture media packets
   tcpdump -i eth0 -n 'udp and portrange 16384-32767' -w media.pcap
   
   # Analyze RTP vs SRTP
   tshark -r media.pcap -Y 'rtp'
   ```

1. **Investigation**
   - Validate H.245 OLC negotiation
   - Check SRTP configuration on EP and GW
   - Review H.235.6 support
   - Check cipher suite compatibility

1. **Eradication**
   - Enable SRTP on endpoint
   - Disable RTP fallback
   - Update gateway SRTP config
   - Force AES-128+ ciphers

1. **Recovery**
   - Restart media channels
   - Perform test call with packet capture
   - Verify SRTP encryption

### 5.3 Incident: H.235 Token Failures (High - P2)

**Symptoms:**

- RRQ/ARQ rejected
- "Invalid token" in GK logs
- Repeated authentication failures
- Endpoint cannot register

**Actions:**

1. **Triage**

   ```bash
   # Check GK logs
   tail -f /var/log/gatekeeper.log | grep "token"
   
   # Verify endpoint status
   python h323_sec_profile/H323_SEC_PROFILE_v1.py reg-status \
       --device-ip <endpoint-ip> \
       --snmp-user admin --auth-key <key> --priv-key <key>
   ```

1. **Investigation**
   - Validate endpoint certificate

   ```bash
   openssl x509 -in endpoint.crt -text -noout
   ```

   - Check endpoint time sync

   ```bash
   ntpq -p
   ```

   - Check GK time sync
   - Validate CRL/OCSP availability

   ```bash
   openssl ocsp -issuer ca.crt -cert endpoint.crt -url http://ocsp.example.com
   ```

1. **Remediation**
   - Correct time synchronization
   - Renew certificate if expired
   - Restore CRL/OCSP if unreachable
   - Re‑register endpoint

1. **Recovery**
   - Monitor successful registration
   - Verify H.235.2 token acceptance

### 5.4 Incident: Gateway Compromise (Critical - P1)

**Symptoms:**

- Unexpected signaling patterns
- Unauthorized trunk usage
- Certificate mismatch
- SIEM alerts for anomalous behavior
- Unusual CDR patterns

**Actions:**

1. **Immediate Containment (< 5 minutes)**
   - Isolate gateway VLAN
   - Block gateway at firewall
   - Disable all trunk groups
   - Alert SOC lead and Voice Engineering

1. **Investigation**
   - Inspect gateway configuration
   - Review gateway logs
   - Analyze CDRs for unauthorized calls
   - Check for unauthorized configuration changes
   - Perform forensic analysis

1. **Eradication**
   - Revoke gateway certificate
   - Rebuild gateway from known-good backup or baseline
   - Apply latest firmware patches
   - Review and harden configuration

1. **Recovery**
   - Reissue gateway certificate
   - Restore trunk configuration
   - Reintroduce gateway to DMZ
   - Perform extensive testing
   - Monitor continuously for 7 days

1. **Post-Incident**
   - Full security audit
   - Review access logs
   - Update hardening procedures
   - Consider network segmentation improvements

### 5.5 Incident: PKI Failure (High - P2)

**Symptoms:**

- CRL/OCSP unreachable
- Certificate validation errors across multiple components
- Expired certificates
- CA service unavailable

**Actions:**

1. **Immediate Assessment**
   - Determine scope (single component vs. widespread)
   - Check CA service status
   - Verify CRL/OCSP availability

1. **Containment**
   - If CA compromised: Emergency PKI incident
   - If CRL/OCSP down: Restore service immediately
   - If certificates expired: Renew critical components first (GK, GW)

1. **Recovery Priority Order**
   1. Restore CRL/OCSP services
   1. Renew GK certificates
   1. Renew GW certificates
   1. Renew EP certificates
   1. Validate full trust chain

1. **Validation**

   ```bash
   # Test certificate chain
   openssl verify -CAfile ca-chain.crt gk.crt
   
   # Test OCSP
   openssl ocsp -issuer ca.crt -cert gk.crt -url http://ocsp.example.com
   
   # Re-register endpoints
   python h323_sec_profile/H323_SEC_PROFILE_v1.py reg-status \
       --device-ip <device-ip> --snmp-user admin --auth-key <key> --priv-key <key>
   ```

### 5.6 Incident: Firewall Bypass / Network Segmentation Violation (Critical - P1)

**Symptoms:**

- Direct EP ↔ EP signaling detected
- Endpoint traffic bypassing GK
- Cross-VLAN leakage
- DMZ isolation breach

**Actions:**

1. **Immediate Containment**
   - Block affected VLANs
   - Review and restore firewall rules
   - Isolate affected endpoints

1. **Investigation**
   - Review firewall configuration changes
   - Check for misconfigurations
   - Analyze traffic flows
   - Identify root cause

1. **Remediation**
   - Restore correct firewall ACLs
   - Verify VLAN isolation
   - Test segmentation
   - Block all unauthorized paths

1. **Validation**
   - Attempt direct EP-to-EP connection (should fail)
   - Verify all traffic routes through GK
   - Confirm DMZ isolation

## 6. Post‑Incident Activities

### 6.1 Documentation

**Required Documentation:**

- Full incident timeline
- Root cause analysis
- Impact assessment
- Remediation steps taken
- Lessons learned
- Preventive actions

**Template:**
```
═══════════════════════════════════════════════════════════════
H.323 SECURITY INCIDENT REPORT
═══════════════════════════════════════════════════════════════

Incident ID: [ID]
Date/Time: [TIMESTAMP]
Severity: [P1/P2/P3/P4]
Status: [Resolved/Ongoing]

SUMMARY
-------
[Brief description of the incident]

TIMELINE
--------
[Detailed timeline of detection, response, and resolution]

AFFECTED COMPONENTS
-------------------
- Component: [Name]
  Impact: [Description]
  Status: [Resolved/Monitoring]

ROOT CAUSE
----------
[Detailed root cause analysis]

CONTAINMENT ACTIONS
-------------------
[Actions taken to contain the incident]

ERADICATION ACTIONS
-------------------
[Actions taken to remove the threat]

RECOVERY ACTIONS
----------------
[Actions taken to restore normal operations]

LESSONS LEARNED
---------------
[Key takeaways and improvements identified]

PREVENTIVE ACTIONS
------------------
[Actions to prevent recurrence]

SIGN-OFF
--------
SOC Lead: _________________ Date: _______
Voice Engineering: ________ Date: _______
Security Lead: ____________ Date: _______
```

### 6.2 Lessons Learned

**Identify gaps in:**

- PKI infrastructure and processes
- Network segmentation
- GK/GW/EP configuration
- Monitoring and alerting
- Operational processes
- Training and procedures

### 6.3 Preventive Actions

**Update Security Controls:**

- Update hardening checklist
- Update firewall rules
- Update PKI policies
- Update monitoring thresholds
- Update alert definitions

**Process Improvements:**

- Review change management
- Enhance training
- Update runbooks
- Improve documentation

## 7. Completion Criteria

An incident is considered fully resolved when:

- ✅ All secure signaling and media paths restored
- ✅ All compromised components remediated
- ✅ All certificates validated
- ✅ All logs verified and analyzed
- ✅ No recurrence for 72 hours
- ✅ Documentation completed
- ✅ Lessons learned reviewed
- ✅ Preventive actions implemented
- ✅ Post-incident report approved
- ✅ Stakeholders notified

---

## Related Documentation

- [Secure-H323-Hardening-Checklist-v1.0.md](./Secure-H323-Hardening-Checklist-v1.0.md) - Hardening procedures
- [Secure-H323-Operational-Runbook-v1.0.md](./Secure-H323-Operational-Runbook-v1.0.md) - Operations manual
- [H323-H235-Security-Test-Plan-v1.0.md](./H323-H235-Security-Test-Plan-v1.0.md) - Security testing
- [H323-H235-Compliance-Matrix-v1.0.md](./H323-H235-Compliance-Matrix-v1.0.md) - Compliance requirements
- [Gateway-Interworking-Security-Profile-v1.0.md](./Gateway-Interworking-Security-Profile-v1.0.md) - Gateway security

## Appendix: Quick Reference - Incident Response Commands

### Detection & Triage

```bash
# Check component status
python h323_sec_profile/H323_SEC_PROFILE_v1.py reg-status --device-ip <ip> --snmp-user admin --auth-key <key> --priv-key <key>

# Run compliance check
python h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance --config config.json

# Run simulation test
python h323_sec_profile/H323_SEC_PROFILE_v1.py run-sim
```

### Packet Analysis

```bash
# Capture signaling
tcpdump -i eth0 -n 'tcp port 1720' -w signaling.pcap

# Capture media
tcpdump -i eth0 -n 'udp and portrange 16384-32767' -w media.pcap

# Analyze for clear-text
tshark -r signaling.pcap -Y 'h225'
tshark -r media.pcap -Y 'rtp'
```

### Certificate Validation

```bash
# Check certificate
openssl x509 -in cert.crt -text -noout

# Verify chain
openssl verify -CAfile ca-chain.crt component.crt

# Test OCSP
openssl ocsp -issuer ca.crt -cert component.crt -url http://ocsp.example.com
```

### Incident Logging

```bash
# Log incident event
python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
    --event-type security_incident \
    --device-id <component> \
    --outcome <status>

# API logging
curl -X POST http://localhost:8080/log \
    -H "Content-Type: application/json" \
    -d '{"event_type":"incident","device_id":"<id>","outcome":"<status>","details":{...}}'
```
