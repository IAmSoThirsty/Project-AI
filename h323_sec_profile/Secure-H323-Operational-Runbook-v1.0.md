# Secure H.323 Operational Runbook

## Version 1.0 — Operations, Maintenance, and Troubleshooting Manual

## 1. Purpose

This runbook defines the operational procedures, daily/weekly/monthly tasks, incident handling, and troubleshooting workflows required to maintain a secure, reliable H.323 environment aligned with:

- Secure H.323 Zone Standard
- Secure H.323 Implementation Guide
- Enterprise PKI and network security policies

This is the operations manual for administrators, NOC/SOC teams, and voice/video engineers.

## 2. Roles and Responsibilities

### 2.1 Voice/Video Engineering

- Maintain GK, GW, MCU configurations
- Manage endpoint provisioning
- Oversee PKI integration
- Perform capacity planning and QoS tuning

### 2.2 Network Operations (NOC)

- Maintain VLANs, ACLs, firewall rules
- Monitor QoS, latency, jitter, packet loss
- Ensure SRTP media paths remain stable

### 2.3 Security Operations (SOC)

- Monitor logs for security events
- Investigate authentication failures
- Respond to H.235 negotiation failures
- Validate certificate revocation and expiry

### 2.4 PKI Administrators

- Manage CA hierarchy
- Issue/revoke certificates
- Maintain CRL/OCSP availability

## 3. Daily Operations

### 3.1 Gatekeeper Health Checks

- Verify GK processes are running
- Confirm RAS port (1719/1718) is reachable
- Check registration counts (RRQ/RCF)
- Validate no unauthorized endpoints are attempting registration
- Review logs for:
  - Failed H.235 tokens
  - Rejected ARQs
  - Bandwidth limit hits

**Using Project-AI Tools:**

```bash
# Check registration status for all endpoints
python h323_sec_profile/H323_SEC_PROFILE_v1.py reg-status \
    --device-ip <gk-ip> \
    --snmp-user admin \
    --auth-key <auth-key> \
    --priv-key <priv-key>
```

### 3.2 Gateway Health Checks

- Verify gateway is reachable on inside and outside interfaces
- Confirm trunk status (ISDN/H.320/PSTN/SIP)
- Check active call count
- Validate SRTP is active for all IP‑side calls
- Review logs for:
  - SecurityMode negotiation failures
  - Codec mismatch errors
  - Trunk congestion

**Using Project-AI Tools:**

```bash
# Query gateway status via API
curl -X GET "http://localhost:8080/registration/status?device_ip=<gw-ip>&snmp_user=admin&auth_key=<key>&priv_key=<key>"
```

### 3.3 Endpoint Health Checks

- Confirm endpoints are registered
- Validate certificate status (not expired)
- Check for secure signaling (H.235.3/4)
- Confirm SRTP is enabled

### 3.4 Network Health Checks

- Monitor latency/jitter/packet loss
- Validate QoS queues are not congested
- Confirm firewall rules have not changed unexpectedly

## 4. Weekly Operations

### 4.1 Certificate Validation

- Check for certificates expiring within 30 days
- Validate CRL/OCSP availability
- Confirm endpoints can reach revocation servers

### 4.2 Log Review

- Review GK/GW logs for:
  - Authentication failures
  - Security downgrades
  - Repeated call failures
- Review SIEM alerts for anomalies

**Using Project-AI Tools:**

```bash
# Log security event for tracking
python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
    --event-type weekly_audit \
    --device-id gk-primary \
    --outcome success
```

### 4.3 Capacity Review

- Analyze call volume trends
- Check gateway trunk utilization
- Review bandwidth usage per VLAN

## 5. Monthly Operations

### 5.1 Patch and Firmware Review

- Check for GK/GW/MCU firmware updates
- Validate endpoint software versions
- Apply patches in maintenance windows

### 5.2 Security Audit

- Validate H.235 enforcement
- Confirm SRTP is mandatory
- Review firewall ACLs for drift
- Validate TLS/IPsec configurations

**Using Project-AI Tools:**

```bash
# Run compliance check
python h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance \
    --config /etc/h323/deployment_config.json
```

**Via API:**

```bash
curl -X POST "http://localhost:8080/compliance/check" \
  -H "Content-Type: application/json" \
  -d '{
    "all_devices_support_h235": true,
    "mandatory_tls_on_h225": true,
    "srtp_everywhere": true,
    "has_logging": true,
    "pki_enforced": true
  }'
```

### 5.3 PKI Audit

- Review CA logs
- Validate certificate issuance and revocation
- Confirm no stale or unused certificates remain active

## 6. Incident Response Procedures

### 6.1 Authentication Failures (H.235.2)

**Symptoms:**

- RRQ rejected
- ARQ rejected
- "Invalid token" or "timestamp mismatch"

**Actions:**

1. Check endpoint certificate validity
1. Verify endpoint time sync
1. Confirm GK time sync
1. Validate CRL/OCSP availability
1. Re‑register endpoint

**Diagnostic Commands:**

```bash
# Check endpoint certificate
openssl x509 -in endpoint.crt -text -noout

# Verify NTP sync
ntpq -p

# Test OCSP
openssl ocsp -issuer ca.crt -cert endpoint.crt -url http://ocsp.example.com
```

### 6.2 Signaling Security Failures (H.235.3/4)

**Symptoms:**

- SETUP rejected
- H.245 SecurityMode negotiation fails
- Calls downgraded to non‑secure signaling

**Actions:**

1. Verify endpoint supports required H.235 profiles
1. Confirm TLS/IPsec is enabled
1. Check cipher suite compatibility
1. Review GK logs for policy enforcement
1. Restart signaling stack if needed

**Using Project-AI Tools:**

```bash
# Run simulation to test H.235 profiles
python h323_sec_profile/H323_SEC_PROFILE_v1.py run-sim
```

### 6.3 Media Security Failures (H.235.6 / SRTP)

**Symptoms:**

- RTP instead of SRTP
- One‑way audio/video
- Media path blocked

**Actions:**

1. Confirm SRTP is enabled on EP and GW
1. Validate H.245 OLC includes SRTP keys
1. Check firewall for blocked SRTP ports
1. Verify NAT traversal (if applicable)
1. Restart media channels

**Diagnostic Commands:**

```bash
# Capture media packets
tcpdump -i eth0 -n 'udp port 16384-32767' -w media.pcap

# Verify SRTP (encrypted packets should not show clear audio patterns)
tshark -r media.pcap -Y 'rtp'
```

### 6.4 Gateway Interworking Failures

**Symptoms:**

- PSTN/H.320 calls fail
- Codec mismatch
- Trunk congestion

**Actions:**

1. Check trunk status (ISDN/H.320/SIP)
1. Validate codec mapping
1. Confirm GK routing rules
1. Review gateway logs for cause codes
1. Test call from gateway directly

### 6.5 QoS or Network Degradation

**Symptoms:**

- Choppy audio
- Video artifacts
- High jitter

**Actions:**

1. Check DSCP markings
1. Validate queue utilization
1. Check for WAN congestion
1. Review switch port errors
1. Run packet captures if needed

**Diagnostic Commands:**

```bash
# Check interface statistics
show interface stats

# Monitor QoS queues
show policy-map interface

# Capture with QoS markings
tcpdump -i eth0 -vv -n 'ip[1] & 0xfc == 0xb8'  # EF marking
```

## 7. Troubleshooting Playbooks

### 7.1 Endpoint Cannot Register

**Troubleshooting Steps:**

1. **Ping GK**

   ```bash
   ping gk.voice.example.com
   ```

1. **Validate certificate**

   ```bash
   openssl x509 -in endpoint.crt -text -noout | grep -E "(Subject|Not)"
   ```

1. **Check CRL/OCSP**

   ```bash
   openssl ocsp -issuer ca.crt -cert endpoint.crt -url http://ocsp.example.com
   ```

1. **Confirm H.235 token generation**
   - Check endpoint logs for token creation
   - Verify shared secrets or certificates

1. **Review GK logs**

   ```bash
   tail -f /var/log/gatekeeper.log | grep RRQ
   ```

1. **Reboot endpoint**
   - Power cycle or soft reboot
   - Monitor registration process

### 7.2 Call Fails at Setup

**Troubleshooting Steps:**

1. Check SETUP/CONNECT logs
1. Validate H.225 security
1. Confirm GK routing
1. Check gateway availability
1. Validate endpoint codec support

**Using Project-AI Tools:**

```bash
# Log the failure event
python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
    --event-type call_setup_failure \
    --device-id <endpoint-id> \
    --outcome failed
```

### 7.3 No Media / One‑Way Media

**Troubleshooting Steps:**

1. **Validate SRTP negotiation**
   - Check H.245 logs for SRTP key exchange
   
1. **Check firewall for blocked media ports**

   ```bash
   # Test media port connectivity
   nc -u -v <remote-ip> 16384
   ```

1. **Confirm NAT traversal**
   - Check for STUN/TURN configuration
   - Verify port forwarding rules

1. **Validate gateway media mapping**
   - Review gateway media configuration
   - Check codec transcoding settings

1. **Run packet capture**

   ```bash
   tcpdump -i eth0 -n 'udp and port > 16383 and port < 32768' -w media-debug.pcap
   ```

### 7.4 Poor Quality Media

**Troubleshooting Steps:**

1. **Check QoS**

   ```bash
   # Verify DSCP markings
   tcpdump -i eth0 -vv -n 'udp and host <endpoint-ip>'
   ```

1. **Validate bandwidth availability**
   - Check link utilization
   - Review bandwidth allocation

1. **Review jitter/latency**

   ```bash
   # Continuous ping test
   ping -i 0.02 <remote-endpoint> | awk '{print $7}' | cut -d= -f2
   ```

1. **Check for duplex mismatches**

   ```bash
   # Check interface status
   ethtool eth0
   ```

1. **Validate endpoint CPU load**
   - Check endpoint system resources
   - Review background processes

## 8. Maintenance Windows

### 8.1 Required for:

- GK/GW firmware updates
- PKI certificate renewals
- Firewall ACL changes
- VLAN/QoS modifications
- Major endpoint software updates

### 8.2 Procedure

1. **Notify stakeholders**
   - Send advance notice (24-48 hours)
   - Schedule maintenance window

1. **Backup GK/GW configs**

   ```bash
   # Backup gatekeeper config
   tar czf gk-backup-$(date +%Y%m%d).tar.gz /etc/gatekeeper/
   
   # Backup gateway config
   tar czf gw-backup-$(date +%Y%m%d).tar.gz /etc/gateway/
   ```

1. **Apply changes**
   - Execute planned changes
   - Document each step

1. **Validate registration**

   ```bash
   python h323_sec_profile/H323_SEC_PROFILE_v1.py reg-status \
       --device-ip <endpoint-ip> \
       --snmp-user admin \
       --auth-key <key> \
       --priv-key <key>
   ```

1. **Validate secure call setup**
   - Make test calls between endpoints
   - Verify H.235.3/4 negotiation

1. **Validate SRTP media**
   - Confirm media encryption
   - Check audio/video quality

1. **Document results**

   ```bash
   python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
       --event-type maintenance_completed \
       --device-id maintenance-window \
       --outcome success
   ```

## 9. Documentation Requirements

- Maintain inventory of all endpoints
- Maintain certificate issuance logs
- Maintain GK/GW configuration archives
- Maintain network diagrams
- Maintain incident logs

**Using Project-AI Tools:**

All operational events should be logged using the CLI or API:

```bash
# CLI logging
python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
    --event-type <type> \
    --device-id <device> \
    --outcome <outcome>

# API logging
curl -X POST "http://localhost:8080/log" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "maintenance",
    "device_id": "gk-primary",
    "outcome": "success",
    "details": {"task": "firmware_update"}
  }'
```

## 10. Completion Criteria

Operations are considered compliant when:

- All endpoints register securely
- All calls negotiate H.235.3/4/6
- All media is SRTP
- All logs flow to SIEM
- All PKI checks pass
- All network paths are validated

**Automated Compliance Check:**

```bash
# Run full compliance validation
python h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance \
    --config /etc/h323/deployment_config.json

# Expected output: "PASS" if all criteria met
```

---

## Related Documentation

- [Secure-H323-Zone-Standard-v1.0.md](./Secure-H323-Zone-Standard-v1.0.md) - Enterprise architecture specification
- [Secure-H323-Implementation-Guide-v1.0.md](./Secure-H323-Implementation-Guide-v1.0.md) - Deployment procedures
- [PROJECT-AI-Security-Philosophy.txt](./PROJECT-AI-Security-Philosophy.txt) - Security philosophy and principles
- [H323_SEC_PROFILE_v1.py](./H323_SEC_PROFILE_v1.py) - Automation tools (CLI: h323secctl)
- [project_ai_fastapi.py](./project_ai_fastapi.py) - REST API service

## Quick Reference Card

### Emergency Contacts

| Role | Contact | Phone | Email |
|------|---------|-------|-------|
| Voice/Video Engineering Lead | TBD | TBD | TBD |
| NOC Manager | TBD | TBD | TBD |
| SOC Manager | TBD | TBD | TBD |
| PKI Administrator | TBD | TBD | TBD |

### Critical Commands

```bash
# Health check simulation
python h323_sec_profile/H323_SEC_PROFILE_v1.py run-sim

# Compliance validation
python h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance --config config.json

# Registration status
python h323_sec_profile/H323_SEC_PROFILE_v1.py reg-status \
    --device-ip <ip> --snmp-user admin --auth-key <key> --priv-key <key>

# Log event
python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
    --event-type <type> --device-id <id> --outcome <result>
```

### API Endpoints

```bash
# Start API service
cd h323_sec_profile
uvicorn project_ai_fastapi:app --host 0.0.0.0 --port 8080

# Compliance check
curl -X POST http://localhost:8080/compliance/check -H "Content-Type: application/json" -d '{...}'

# Registration status
curl -X GET "http://localhost:8080/registration/status?device_ip=<ip>&..."

# Log event
curl -X POST http://localhost:8080/log -H "Content-Type: application/json" -d '{...}'

# Set threat level (v2)
curl -X POST http://localhost:8080/threat-level -H "Content-Type: application/json" -d '{"level": "elevated"}'

# Self-evolving cycle (v3)
curl -X POST http://localhost:8080/evolve -H "Content-Type: application/json" -d '{"events": [...]}'
```
