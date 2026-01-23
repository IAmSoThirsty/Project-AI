# H.323 / H.235 Security Test Plan
## Version 1.0 — Validation & Certification Framework

## 1. Purpose

This test plan defines the full suite of tests required to validate:

- H.235 security enforcement across RAS, H.225, H.245, and RTP
- PKI correctness and certificate handling
- Secure signaling and media negotiation
- SRTP enforcement
- Gateway interworking security
- Network segmentation, ACLs, and QoS
- Operational resilience and failure handling

This plan is used for pre‑deployment certification, post‑change validation, and annual security audits.

## 2. Test Categories

1. PKI & Identity Tests
2. RAS Security Tests (H.235.2)
3. H.225 Signaling Security Tests (H.235.3)
4. H.245 Control Security Tests (H.235.4)
5. Media Security Tests (H.235.6 / SRTP)
6. Gateway Interworking Security Tests
7. Network Segmentation & Firewall Tests
8. QoS & Performance Tests
9. Operational Resilience Tests
10. Logging & Monitoring Tests

Each category includes test objectives, procedures, expected results, and pass/fail criteria.

## 3. PKI & Identity Tests

### 3.1 Certificate Validity Test

**Objective:** Ensure all components have valid certificates.

**Procedure:**
- Inspect certs on EP, GK, GW, MCU
- Validate SAN entries
- Validate expiration dates

**Expected Result:**
- All certs valid, trusted, and unexpired

**Pass/Fail:**
- Any invalid cert = FAIL

**Automation:**
```bash
# Using OpenSSL
openssl x509 -in endpoint.crt -text -noout | grep -E "(Subject|Not|DNS)"

# Using Project-AI tools
python h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance --config deployment_config.json
```

### 3.2 CRL/OCSP Validation Test

**Objective:** Confirm revocation checking works.

**Procedure:**
- Revoke a test certificate
- Attempt endpoint registration

**Expected Result:**
- Registration rejected

**Pass/Fail:**
- If revoked cert is accepted = FAIL

**Automation:**
```bash
# Test OCSP
openssl ocsp -issuer ca.crt -cert endpoint.crt -url http://ocsp.example.com

# Verify via simulation
python h323_sec_profile/H323_SEC_PROFILE_v1.py run-sim
```

### 3.3 Mutual TLS/IPsec Test

**Objective:** Validate secure transport.

**Procedure:**
- Initiate signaling between EP ↔ GK and EP ↔ GW

**Expected Result:**
- TLS/IPsec session established

**Pass/Fail:**
- Clear‑text signaling = FAIL

**Automation:**
```bash
# Capture and verify TLS
tcpdump -i eth0 -n 'tcp port 1720' -w signaling.pcap
tshark -r signaling.pcap -Y 'ssl.handshake'
```

## 4. RAS Security Tests (H.235.2)

### 4.1 Authenticated Registration Test

**Objective:** Validate RRQ/RCF with H.235 tokens.

**Procedure:**
- Register endpoint
- Inspect GK logs

**Expected Result:**
- Valid token accepted

**Pass/Fail:**
- Registration without token accepted = FAIL

**Automation:**
```bash
# Check registration logs
tail -f /var/log/gatekeeper.log | grep 'RRQ.*H.235'

# API check
curl -X GET "http://localhost:8080/registration/status?device_ip=<ep-ip>&..."
```

### 4.2 Anti‑Replay Test

**Objective:** Ensure timestamp/nonce enforcement.

**Procedure:**
- Replay a captured RRQ

**Expected Result:**
- GK rejects replay

**Pass/Fail:**
- Replay accepted = FAIL

**Automation:**
```bash
# Capture and replay
tcpdump -i eth0 -n 'udp port 1719' -w ras.pcap
# Replay tool would attempt to resend captured RRQ
```

### 4.3 Unauthorized Endpoint Test

**Objective:** Ensure GK rejects unknown endpoints.

**Procedure:**
- Attempt registration with untrusted cert

**Expected Result:**
- Registration rejected

**Pass/Fail:**
- Unauthorized EP accepted = FAIL

## 5. H.225 Signaling Security Tests (H.235.3)

### 5.1 Secure SETUP Test

**Objective:** Validate integrity/encryption of SETUP.

**Procedure:**
- Initiate call
- Capture signaling

**Expected Result:**
- SETUP protected by H.235.3 or TLS

**Pass/Fail:**
- Clear‑text SETUP = FAIL

**Automation:**
```bash
# Capture signaling
tcpdump -i eth0 -n 'tcp port 1720' -w setup.pcap

# Verify encryption (should not see clear H.323 ASN.1)
strings setup.pcap | grep -i "SETUP" && echo "FAIL: Clear text detected"
```

### 5.2 Downgrade Resistance Test

**Objective:** Ensure signaling cannot fall back to insecure mode.

**Procedure:**
- Force endpoint to request insecure signaling

**Expected Result:**
- GK rejects call

**Pass/Fail:**
- Insecure call accepted = FAIL

**Automation:**
```bash
# Log failed attempts
python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
    --event-type downgrade_attempt \
    --device-id test-ep \
    --outcome rejected
```

## 6. H.245 Control Security Tests (H.235.4)

### 6.1 Secure H.245 Channel Test

**Objective:** Validate encrypted H.245.

**Procedure:**
- Initiate call
- Inspect H.245 SecurityMode negotiation

**Expected Result:**
- H.245 encrypted

**Pass/Fail:**
- Clear‑text H.245 = FAIL

**Automation:**
```bash
# Capture H.245 negotiation
tcpdump -i eth0 -n 'tcp' -w h245.pcap
tshark -r h245.pcap -Y 'h245.SecurityMode'
```

### 6.2 Logical Channel Security Test

**Objective:** Ensure OLC messages carry SRTP keying.

**Procedure:**
- Capture H.245 OLC

**Expected Result:**
- SRTP keys present

**Pass/Fail:**
- Missing SRTP keys = FAIL

## 7. Media Security Tests (H.235.6 / SRTP)

### 7.1 SRTP Enforcement Test

**Objective:** Ensure all media is encrypted.

**Procedure:**
- Initiate call
- Capture RTP

**Expected Result:**
- SRTP only

**Pass/Fail:**
- RTP detected = FAIL

**Automation:**
```bash
# Capture media
tcpdump -i eth0 -n 'udp and portrange 16384-32767' -w media.pcap

# Verify SRTP (encrypted payload)
tshark -r media.pcap -Y 'rtp' -T fields -e rtp.payload | head -10

# If you can decode audio patterns, it's not encrypted = FAIL
```

### 7.2 SRTCP Integrity Test

**Objective:** Validate RTCP protection.

**Procedure:**
- Capture RTCP

**Expected Result:**
- SRTCP with integrity

**Pass/Fail:**
- Clear RTCP = FAIL

### 7.3 Media Path Firewall Test

**Objective:** Ensure only approved ports are used.

**Procedure:**
- Attempt media on non‑approved ports

**Expected Result:**
- Blocked

**Pass/Fail:**
- Media allowed on unauthorized ports = FAIL

**Automation:**
```bash
# Test unauthorized port
nc -u -v <remote-ip> 9999
# Should timeout/be blocked
```

## 8. Gateway Interworking Security Tests

### 8.1 IP‑Side Security Test

**Objective:** Ensure gateway uses full H.235 stack.

**Procedure:**
- Initiate call through gateway

**Expected Result:**
- Secure RAS, H.225, H.245, SRTP

**Pass/Fail:**
- Any insecure signaling/media = FAIL

**Automation:**
```bash
# Run full simulation through gateway
python h323_sec_profile/H323_SEC_PROFILE_v1.py run-sim

# API compliance check
curl -X POST http://localhost:8080/compliance/check -d '{...}'
```

### 8.2 Legacy‑Side Boundary Test

**Objective:** Validate gateway as crypto boundary.

**Procedure:**
- Inspect media on legacy side

**Expected Result:**
- Clear TDM/H.320 (expected)
- No leakage of SRTP keys

**Pass/Fail:**
- SRTP keys exposed = FAIL

### 8.3 Codec Mapping Test

**Objective:** Ensure correct transcoding.

**Procedure:**
- Call PSTN/H.320 endpoint

**Expected Result:**
- Correct codec mapping

**Pass/Fail:**
- Codec mismatch = FAIL

## 9. Network Segmentation & Firewall Tests

### 9.1 VLAN Isolation Test

**Objective:** Ensure endpoints cannot bypass GK/GW.

**Procedure:**
- Attempt direct EP ↔ EP signaling

**Expected Result:**
- Blocked

**Pass/Fail:**
- Direct signaling allowed = FAIL

**Automation:**
```bash
# Try direct connection (should fail)
telnet <other-ep-ip> 1720
# Connection should be refused/timeout
```

### 9.2 Firewall ACL Test

**Objective:** Validate only approved ports open.

**Procedure:**
- Scan EP, GK, GW

**Expected Result:**
- Only RAS, H.225/H.245, SRTP ranges open

**Pass/Fail:**
- Extra ports open = FAIL

**Automation:**
```bash
# Port scan
nmap -p 1-65535 <ep-ip>

# Expected open: 1718, 1719, 1720, 16384-32767
# All others should be filtered/closed
```

## 10. QoS & Performance Tests

### 10.1 DSCP Marking Test

**Objective:** Validate correct DSCP values.

**Procedure:**
- Capture packets

**Expected Result:**
- Signaling: CS3/AF31
- Voice: EF
- Video: AF41

**Pass/Fail:**
- Incorrect markings = FAIL

**Automation:**
```bash
# Capture with verbose output to see ToS/DSCP
tcpdump -i eth0 -vv -n 'host <ep-ip>' -c 100

# Check for EF (0xb8) for voice
tcpdump -i eth0 -vv -n 'ip[1] & 0xfc == 0xb8'
```

### 10.2 Jitter/Latency Test

**Objective:** Validate media quality.

**Procedure:**
- Run synthetic calls

**Expected Result:**
- Jitter < 30 ms
- Latency < 150 ms

**Pass/Fail:**
- Exceeds thresholds = FAIL

**Automation:**
```bash
# Continuous ping for latency
ping -c 100 <remote-ep> | tail -1

# Use iperf for jitter
iperf3 -c <remote-ep> -u -b 100k -t 30
```

## 11. Operational Resilience Tests

### 11.1 GK Failover Test

**Objective:** Validate redundancy.

**Procedure:**
- Fail primary GK

**Expected Result:**
- EPs re‑register to secondary

**Pass/Fail:**
- Registration fails = FAIL

**Automation:**
```bash
# Disable primary GK
systemctl stop gatekeeper

# Monitor re-registration
python h323_sec_profile/H323_SEC_PROFILE_v1.py reg-status \
    --device-ip <ep-ip> --snmp-user admin --auth-key <key> --priv-key <key>
```

### 11.2 Gateway Failover Test

**Objective:** Validate call continuity.

**Procedure:**
- Fail primary gateway

**Expected Result:**
- Calls reroute to secondary

**Pass/Fail:**
- Calls drop = FAIL

## 12. Logging & Monitoring Tests

### 12.1 SIEM Integration Test

**Objective:** Ensure logs reach SIEM.

**Procedure:**
- Trigger test events

**Expected Result:**
- Events appear in SIEM

**Pass/Fail:**
- Missing logs = FAIL

**Automation:**
```bash
# Generate test event
python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
    --event-type test_event \
    --device-id test-component \
    --outcome success

# Verify in SIEM
# (Use SIEM API or query interface)
```

### 12.2 Security Event Detection Test

**Objective:** Validate alerting.

**Procedure:**
- Trigger auth failure
- Trigger downgrade attempt

**Expected Result:**
- SOC receives alerts

**Pass/Fail:**
- No alert = FAIL

**Automation:**
```bash
# API to set threat level (triggers alerts)
curl -X POST http://localhost:8080/threat-level \
    -H "Content-Type: application/json" \
    -d '{"level": "critical"}'
```

## 13. Certification Criteria

A deployment is certified when:

- All mandatory tests pass
- No critical or high‑severity failures remain
- All PKI, signaling, and media security requirements met
- All gateways validated as secure crypto boundaries
- All logs and alerts verified

### Certification Process

1. **Pre-Certification Review**
   - Review all documentation
   - Verify test environment readiness
   
2. **Execute Test Plan**
   - Run all test categories
   - Document results in real-time
   
3. **Analysis**
   - Calculate compliance score
   - Identify critical failures
   
4. **Remediation** (if needed)
   - Fix identified issues
   - Re-test affected areas
   
5. **Final Certification**
   - Issue certification document
   - Schedule next audit

### Certification Validity

- **Standard Certification:** Valid for 12 months
- **Re-certification Required:** After major changes (GK/GW upgrades, PKI changes, network modifications)
- **Spot Audits:** Quarterly validation of critical controls

---

## Related Documentation

- [Secure-H323-Zone-Standard-v1.0.md](./Secure-H323-Zone-Standard-v1.0.md) - Requirements specification
- [Secure-H323-Implementation-Guide-v1.0.md](./Secure-H323-Implementation-Guide-v1.0.md) - Deployment procedures
- [Secure-H323-Operational-Runbook-v1.0.md](./Secure-H323-Operational-Runbook-v1.0.md) - Operations manual
- [H323-H235-Compliance-Matrix-v1.0.md](./H323-H235-Compliance-Matrix-v1.0.md) - Compliance requirements
- [H323_SEC_PROFILE_v1.py](./H323_SEC_PROFILE_v1.py) - Automation tools
- [project_ai_fastapi.py](./project_ai_fastapi.py) - REST API service

## Automation Integration

### Using Project-AI Tools

All tests should be supplemented with Project-AI automation tools:

```bash
# Pre-test validation
python h323_sec_profile/H323_SEC_PROFILE_v1.py run-sim

# Compliance check
python h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance \
    --config test_deployment_config.json

# Registration validation
python h323_sec_profile/H323_SEC_PROFILE_v1.py reg-status \
    --device-ip <device-ip> \
    --snmp-user <user> \
    --auth-key <key> \
    --priv-key <key>

# Event logging
python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
    --event-type test_execution \
    --device-id test-harness \
    --outcome pass
```

### Using REST API

```bash
# Start API service for test automation
cd h323_sec_profile
uvicorn project_ai_fastapi:app --host 0.0.0.0 --port 8080

# Automated compliance check
curl -X POST http://localhost:8080/compliance/check \
    -H "Content-Type: application/json" \
    -d '{
        "all_devices_support_h235": true,
        "mandatory_tls_on_h225": true,
        "srtp_everywhere": true,
        "has_logging": true,
        "pki_enforced": true
    }'

# Registration status check
curl -X GET "http://localhost:8080/registration/status?device_ip=<ip>&..."

# Log test results
curl -X POST http://localhost:8080/log \
    -H "Content-Type: application/json" \
    -d '{
        "event_type": "test_result",
        "device_id": "test-suite",
        "outcome": "pass",
        "details": {"test_id": "3.1", "test_name": "Certificate Validity"}
    }'
```

## Test Execution Checklist

- [ ] Test environment prepared and isolated
- [ ] All test tools installed and validated
- [ ] Backup of production configs taken
- [ ] Test plan reviewed with stakeholders
- [ ] Notification sent to affected parties
- [ ] All tests executed and documented
- [ ] Results analyzed and scored
- [ ] Failures remediated or documented
- [ ] Re-tests completed for failures
- [ ] Final certification issued
- [ ] Results archived for audit trail
