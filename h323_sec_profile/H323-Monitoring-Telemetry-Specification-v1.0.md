# Monitoring & Telemetry Specification for Secure H.323 Deployments

## Version 1.0 — Observability, Metrics, Alerts, and Data Flows

## 1. Purpose

This specification defines the complete monitoring, telemetry, and alerting framework required to maintain visibility, detect anomalies, and ensure the security and performance of:

- H.323 endpoints
- Gatekeepers
- Gateways
- MCUs
- PKI infrastructure
- Network segmentation
- QoS and media paths

It ensures that all components are continuously observable and that deviations from secure operation are detected immediately.

## 2. Monitoring Architecture Overview

### 2.1 Core Monitoring Components

- SIEM (Security Information & Event Management)
- NMS (Network Monitoring System)
- Voice/Video Monitoring System
- PKI Monitoring
- Syslog collectors
- Packet capture sensors (strategic points)
- QoS monitoring tools

### 2.2 Required Data Sources

- Gatekeeper logs
- Gateway logs
- Endpoint logs (where supported)
- Firewall logs
- Switch/router telemetry
- PKI logs
- NTP logs
- SRTP/RTP packet captures
- SIP/H.320 trunk logs (if applicable)

### 2.3 Monitoring Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    H.323 Zone Components                        │
│  ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐                 │
│  │  EP  │    │  GK  │    │  GW  │    │ MCU  │                 │
│  └──┬───┘    └──┬───┘    └──┬───┘    └──┬───┘                 │
│     │           │           │           │                       │
│     └───────────┴───────────┴───────────┘                       │
│                     │                                           │
│             Logs & Metrics                                      │
└─────────────────────┼───────────────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
    ┌────▼────┐              ┌────▼────┐
    │ Syslog  │              │  SNMP   │
    │Collector│              │Collector│
    └────┬────┘              └────┬────┘
         │                         │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │                         │
    ┌────▼────┐  ┌────▼────┐  ┌──▼──────┐
    │  SIEM   │  │   NMS   │  │ Voice/  │
    │         │  │         │  │ Video   │
    │         │  │         │  │Monitor  │
    └────┬────┘  └────┬────┘  └──┬──────┘
         │            │           │
         └────────────┴───────────┘
                      │
              ┌───────▼────────┐
              │   Dashboards   │
              │   & Alerting   │
              └────────────────┘
```

## 3. Gatekeeper Monitoring Specification

### 3.1 Required Metrics

| Metric | Unit | Collection Interval | Threshold |
|--------|------|---------------------|-----------|
| Registration count (RRQ/RCF) | count | 1 minute | N/A |
| Admission requests (ARQ/ACF) | count/min | 1 minute | Alert if > baseline + 50% |
| Disengage events (DRQ/DCF) | count | 1 minute | N/A |
| Bandwidth allocation | Mbps | 1 minute | Alert if > 80% |
| Call routing decisions | count | 1 minute | N/A |
| H.235 token validation success rate | % | 1 minute | Alert if < 95% |
| Security downgrade attempts | count | Real-time | Alert on any |
| Failed registrations | count | Real-time | Alert if > 5/min |
| Failed calls | count | 1 minute | Alert if > 10/min |

### 3.2 Required Logs

- **RAS logs** - All RRQ, ARQ, DRQ with outcomes
- **H.225 signaling logs** - SETUP, CONNECT, RELEASE with H.235 status
- **H.245 negotiation logs** - SecurityMode, OLC with SRTP status
- **SecurityMode negotiation logs** - All attempts and outcomes
- **Certificate validation logs** - Success/failure with reasons

**Log Format:**
```json
{
  "timestamp": "2026-01-23T11:00:00Z",
  "component": "gatekeeper",
  "event_type": "ras_registration",
  "source_ip": "10.100.1.50",
  "endpoint_id": "ep1.voice.example.com",
  "h235_token": "valid",
  "certificate_valid": true,
  "outcome": "RCF",
  "details": {
    "bandwidth_requested": "512kbps",
    "ttl": 3600
  }
}
```

### 3.3 Required Alerts

| Alert | Severity | Trigger Condition | Action |
|-------|----------|-------------------|--------|
| Authentication failures | High | > 5 failures in 5 min from same EP | Block EP, investigate |
| Repeated registration failures | Medium | > 10 failures in 10 min | Check PKI, time sync |
| Downgrade attempts | Critical | Any H.235 downgrade attempt | Immediate SOC escalation |
| Certificate validation failures | High | Any cert validation failure | PKI team notification |
| GK process failure | Critical | GK service down | Immediate failover |
| Excessive ARQ denials | Medium | > 20% ARQ denied | Check bandwidth allocation |

**Using Project-AI Tools:**
```bash

# Monitor GK registration status

python h323_sec_profile/H323_SEC_PROFILE_v1.py reg-status \
    --device-ip <gk-ip> \
    --snmp-user admin \
    --auth-key <key> \
    --priv-key <key>

# Log monitoring event

python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
    --event-type monitoring_check \
    --device-id gk1 \
    --outcome success
```

## 4. Gateway Monitoring Specification

### 4.1 Required Metrics

| Metric | Unit | Collection Interval | Threshold |
|--------|------|---------------------|-----------|
| Active calls | count | 1 minute | Alert if > capacity |
| Trunk utilization (PSTN/ISDN/H.320/SIP) | % | 1 minute | Alert if > 80% |
| Codec usage | distribution | 5 minutes | N/A |
| Transcoding load | % CPU | 1 minute | Alert if > 80% |
| SRTP session count | count | 1 minute | Must equal active calls |
| Packet loss (IP side) | % | 1 minute | Alert if > 1% |
| Jitter | ms | 1 minute | Alert if > 30ms |
| Latency | ms | 1 minute | Alert if > 150ms |
| CPU usage | % | 1 minute | Alert if > 80% |
| Memory usage | % | 1 minute | Alert if > 85% |

### 4.2 Required Logs

- **H.225/H.245 logs** - All signaling with H.235 status
- **SRTP negotiation logs** - All H.245 OLC with SRTP keys
- **Trunk signaling logs** - Q.931, SIP, H.320 events
- **CDRs (Call Detail Records)** - All calls with codec, duration, trunk
- **Security events** - All H.235 failures, downgrade attempts
- **Certificate validation logs** - All validation attempts

**CDR Format:**
```json
{
  "timestamp": "2026-01-23T11:00:00Z",
  "call_id": "abc123",
  "source": "ep1.voice.example.com",
  "destination": "+14085551234",
  "gateway": "gw1.voice.example.com",
  "trunk": "PRI-1",
  "codec": "G.711u",
  "h235_profiles": ["2", "3", "4", "6"],
  "srtp": true,
  "duration_seconds": 180,
  "outcome": "success"
}
```

### 4.3 Required Alerts

| Alert | Severity | Trigger Condition | Action |
|-------|----------|-------------------|--------|
| SRTP negotiation failures | Critical | Any SRTP failure | Immediate investigation |
| RTP detected instead of SRTP | Critical | RTP packets detected | Block media, escalate |
| Trunk failures | High | Trunk down > 1 minute | Failover, carrier notification |
| Gateway registration failures | High | Cannot register with GK | Check PKI, network |
| Certificate expiration | High | Cert expires < 7 days | Renew immediately |
| CPU/memory thresholds exceeded | Medium | > 80% for 5 minutes | Capacity planning |
| Unauthorized signaling attempts | Critical | Insecure signaling detected | Block source |

## 5. Endpoint Monitoring Specification

### 5.1 Required Metrics

| Metric | Unit | Collection Interval | Threshold |
|--------|------|---------------------|-----------|
| Registration status | boolean | 5 minutes | Alert if unregistered |
| Call success rate | % | 5 minutes | Alert if < 95% |
| SRTP status | boolean | Per call | Must be true |
| Codec usage | distribution | 5 minutes | N/A |
| Packet loss | % | Per call | Alert if > 1% |
| Jitter | ms | Per call | Alert if > 30ms |
| Latency | ms | Per call | Alert if > 150ms |
| Firmware version | string | Daily | Alert if non-compliant |

### 5.2 Required Logs

- **Registration logs** - All RRQ attempts with H.235 token status
- **SecurityMode negotiation logs** - All attempts with outcomes
- **Media path logs** - SRTP status, codecs, quality metrics
- **Certificate validation logs** - All validation attempts

### 5.3 Required Alerts

| Alert | Severity | Trigger Condition | Action |
|-------|----------|-------------------|--------|
| Registration failure | High | Cannot register for > 5 min | Check PKI, network |
| Certificate expiration | High | Cert expires < 30 days | Renew certificate |
| SRTP disabled or failing | Critical | SRTP not negotiated | Block endpoint |
| Firmware out of compliance | Medium | Old firmware version | Schedule update |

## 6. Network Monitoring Specification

### 6.1 Required Metrics

| Metric | Unit | Collection Interval | Threshold |
|--------|------|---------------------|-----------|
| VLAN health | status | 1 minute | Alert on down |
| Interface errors | count | 1 minute | Alert if increasing |
| Packet loss | % | 1 minute | Alert if > 1% |
| Jitter | ms | 1 minute | Alert if > 30ms |
| Latency | ms | 1 minute | Alert if > 150ms |
| DSCP marking compliance | % | 5 minutes | Alert if < 95% |
| Queue utilization | % | 1 minute | Alert if > 80% |
| Firewall hit counts | count/min | 1 minute | Track trends |

### 6.2 Required Logs

- **Firewall logs** - All allow/deny with source, dest, port, protocol
- **Switch logs** - STP changes, port errors, VLAN changes
- **Router logs** - QoS drops, shaping events, routing changes
- **NAT logs** - All NAT translations (if applicable)

### 6.3 Required Alerts

| Alert | Severity | Trigger Condition | Action |
|-------|----------|-------------------|--------|
| QoS queue congestion | High | Queue > 80% for 5 min | Investigate bandwidth |
| DSCP mis‑marking | Medium | < 95% correct marking | Check QoS config |
| Firewall rule violations | High | Unexpected denies | Review rules |
| VLAN bleed‑through | Critical | Cross-VLAN traffic | Immediate isolation |
| Excessive packet loss | High | > 1% loss sustained | Check physical layer |

## 7. PKI Monitoring Specification

### 7.1 Required Metrics

| Metric | Unit | Collection Interval | Threshold |
|--------|------|---------------------|-----------|
| Certificates expiring 30 days | count | Daily | Alert if > 0 |
| Certificates expiring 7 days | count | Daily | Critical if > 0 |
| CRL/OCSP availability | % uptime | 1 minute | Alert if < 99.9% |
| Certificate issuance volume | count/day | Daily | Track trends |
| Revocation events | count | Real-time | Alert on each |

### 7.2 Required Logs

- **CA issuance logs** - All certificate issuances with requestor
- **CA revocation logs** - All revocations with reason
- **OCSP responder logs** - All OCSP queries with outcomes
- **CRL publishing logs** - All CRL updates

### 7.3 Required Alerts

| Alert | Severity | Trigger Condition | Action |
|-------|----------|-------------------|--------|
| Certificate expiring < 30 days | Medium | Any cert < 30 days | Schedule renewal |
| Certificate expiring < 7 days | High | Any cert < 7 days | Urgent renewal |
| CRL/OCSP unreachable | Critical | Service down > 1 min | Immediate restoration |
| Invalid certificate presented | High | Validation failure | Investigate source |
| PKI service failure | Critical | CA service down | Emergency PKI response |

## 8. SRTP & Media Path Monitoring

### 8.1 Required Metrics

| Metric | Unit | Collection Interval | Threshold |
|--------|------|---------------------|-----------|
| SRTP session count | count | 1 minute | Must equal active calls |
| Packet loss | % | Per call | Alert if > 1% |
| Jitter | ms | Per call | Alert if > 30ms |
| Latency | ms | Per call | Alert if > 150ms |
| SRTCP integrity failures | count | Real-time | Alert on any |
| Media port utilization | % | 1 minute | Alert if > 80% |

### 8.2 Required Logs

- **SRTP negotiation logs** - All H.245 OLC with SRTP status
- **H.245 OLC logs** - All OpenLogicalChannel with keys
- **Media path logs** - Source, dest, ports, codec, quality

### 8.3 Required Alerts

| Alert | Severity | Trigger Condition | Action |
|-------|----------|-------------------|--------|
| RTP detected | Critical | Any RTP packet | Immediate escalation |
| SRTP negotiation failure | Critical | H.245 OLC without SRTP | Block call |
| High jitter/latency | Medium | > thresholds sustained | Check network path |
| One‑way media | High | Media only one direction | Check firewall/NAT |
| Media path blocked | High | No media received | Check network |

## 9. Security Monitoring Specification

### 9.1 Required Security Events

- H.235 token failures
- Signaling downgrade attempts
- Unauthorized endpoint registration attempts
- Gateway compromise indicators
- Firewall bypass attempts
- Certificate validation failures
- Time sync failures (NTP drift)
- Anomalous call patterns
- Unexpected protocol changes

### 9.2 Required Alerts

**Critical:**

- Clear‑text H.225 or H.245 detected
- RTP detected instead of SRTP
- PKI compromise indicators
- Unauthorized endpoint accepted
- Gateway compromise detected
- Firewall bypass successful

**High:**

- Repeated H.235 failures (> 5 in 5 min)
- Gateway trunk anomalies
- Certificate expiration < 24 hours
- Sustained QoS degradation
- Unusual call patterns

**Medium:**

- CRL/OCSP unreachable
- NTP drift > 1 second
- Single H.235 failure
- Configuration drift detected

**Low:**

- Endpoint misconfigurations
- Non-critical log anomalies
- Minor QoS variations

## 10. Telemetry Collection Points

### 10.1 Mandatory Sensors

**Packet Capture Sensors:**

- EP VLAN (sample 1% of traffic or full for security events)
- GK interface (full capture of signaling)
- GW inside interface (full capture)
- GW outside interface (full capture)
- DMZ firewall (full capture)

**Syslog Collection:**

- All H.323 components → Centralized syslog
- Firewall logs → SIEM
- Network device logs → NMS

**SNMP Collection:**

- Interface statistics (all network devices)
- H.323 component health (GK, GW, EP where supported)
- QoS queue statistics

### 10.2 Required Data Retention

| Data Type | Retention Period | Storage Type |
|-----------|------------------|--------------|
| Signaling logs | 1 year | Compressed archive |
| Media metadata | 90 days | Database |
| Packet captures | 7–30 days | Rolling archive |
| PKI logs | 1–7 years | Compliance archive |
| Firewall logs | 1 year | Compressed archive |
| CDRs | 7 years | Database + archive |
| Security events | 7 years | SIEM |

## 11. Dashboards

### 11.1 Required Dashboards

**1. Secure Call Success Rate Dashboard**

- Total calls (last hour, day, week)
- Success rate
- Failure breakdown (RAS, signaling, media, PKI)
- H.235 enforcement rate (should be 100%)
- SRTP usage rate (should be 100%)

**2. Registration Health Dashboard**

- Total registered endpoints
- Registration success rate
- H.235.2 token validation rate
- Certificate validation status
- Failed registrations (real-time)

**3. SRTP Enforcement Dashboard**

- Active SRTP sessions
- RTP sessions (should be 0)
- SRTP negotiation success rate
- H.245 OLC statistics
- Media encryption compliance

**4. Gateway Trunk Utilization Dashboard**

- Trunk usage per gateway
- Active calls per trunk
- Codec distribution
- Transcoding load
- Trunk failure events

**5. PKI Certificate Expiry Dashboard**

- Certificates expiring < 90 days
- Certificates expiring < 30 days
- Certificates expiring < 7 days
- CRL/OCSP availability
- Recent revocations

**6. QoS Health Dashboard**

- Packet loss trends
- Jitter trends
- Latency trends
- DSCP marking compliance
- Queue utilization

**7. Security Events Overview Dashboard**

- H.235 failures (last hour, day)
- Downgrade attempts
- Certificate failures
- Firewall violations
- Anomalous patterns

**8. Endpoint Compliance Status Dashboard**

- Registered endpoints
- Firmware compliance
- Certificate validity
- SRTP enforcement
- Configuration compliance

## 12. Reporting Requirements

### 12.1 Daily Reports

- Registration failures (summary and details)
- SRTP failures (must be 0)
- Gateway trunk status
- Firewall denies (unexpected)
- H.235 security events

### 12.2 Weekly Reports

- Certificate expiry (< 30 days)
- QoS performance trends
- Security events summary
- Call volume and success rates
- Capacity utilization

### 12.3 Monthly Reports

- PKI audit (issuances, revocations, expirations)
- Firmware compliance status
- Network segmentation audit
- Security posture summary
- Capacity planning recommendations

## 13. Completion Criteria

Monitoring is considered compliant when:

- ✅ All required logs flow to SIEM
- ✅ All required metrics are collected
- ✅ All required alerts are active and tested
- ✅ All dashboards are populated with real-time data
- ✅ All retention policies enforced
- ✅ All sensors operational
- ✅ 99.9% collection success rate
- ✅ Alert response procedures documented
- ✅ Dashboard access configured for all teams

---

## Using Project-AI Tools for Monitoring

### Automated Monitoring Checks

```bash

# Daily compliance check

python h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance \
    --config monitoring_config.json

# Registration monitoring

python h323_sec_profile/H323_SEC_PROFILE_v1.py reg-status \
    --device-ip <device-ip> \
    --snmp-user admin \
    --auth-key <key> \
    --priv-key <key>

# Simulation test for validation

python h323_sec_profile/H323_SEC_PROFILE_v1.py run-sim
```

### API-Based Monitoring

```bash

# Start monitoring API

cd h323_sec_profile
uvicorn project_ai_fastapi:app --host 0.0.0.0 --port 8080

# Query registration status

curl -X GET "http://localhost:8080/registration/status?device_ip=<ip>&..."

# Log monitoring events

curl -X POST http://localhost:8080/log \
    -H "Content-Type: application/json" \
    -d '{
        "event_type": "monitoring_check",
        "device_id": "monitoring-system",
        "outcome": "success",
        "details": {"checks_passed": 25, "checks_total": 25}
    }'

# Set threat level based on monitoring

curl -X POST http://localhost:8080/threat-level \
    -H "Content-Type: application/json" \
    -d '{"level": "normal"}'
```

### Continuous Monitoring Script

```bash

#!/bin/bash

# H.323 Continuous Monitoring Script

INTERVAL=300  # 5 minutes

while true; do

    # Check GK status

    python h323_sec_profile/H323_SEC_PROFILE_v1.py reg-status \
        --device-ip $GK_IP \
        --snmp-user admin \
        --auth-key $AUTH_KEY \
        --priv-key $PRIV_KEY

    # Check compliance

    python h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance \
        --config /etc/h323/monitoring_config.json

    # Log monitoring cycle

    python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
        --event-type monitoring_cycle \
        --device-id monitoring-system \
        --outcome success

    sleep $INTERVAL
done
```

---

## Related Documentation

- [Secure-H323-Operational-Runbook-v1.0.md](./Secure-H323-Operational-Runbook-v1.0.md) - Operations procedures
- [H323-Incident-Response-Playbook-v1.0.md](./H323-Incident-Response-Playbook-v1.0.md) - Incident response
- [H323-H235-Security-Test-Plan-v1.0.md](./H323-H235-Security-Test-Plan-v1.0.md) - Security testing
- [H323-H235-Compliance-Matrix-v1.0.md](./H323-H235-Compliance-Matrix-v1.0.md) - Compliance requirements
- [Secure-H323-Hardening-Checklist-v1.0.md](./Secure-H323-Hardening-Checklist-v1.0.md) - Hardening procedures

## Appendix: Monitoring Configuration Template

```yaml
monitoring_config:
  siem:
    host: siem.example.com
    port: 514
    protocol: syslog
    tls: true

  components:
    gatekeepers:

      - id: gk1.voice.example.com

        ip: 10.100.1.10
        snmp: true
        syslog: true
        metrics_interval: 60

    gateways:

      - id: gw1.voice.example.com

        ip: 10.200.1.10
        snmp: true
        syslog: true
        cdrs: true
        metrics_interval: 60

    endpoints:

      - range: 10.100.2.0/24

        snmp: false
        syslog: where_supported
        metrics_interval: 300

  alerts:
    critical:

      - cleartext_signaling
      - rtp_detected
      - pki_compromise
      - unauthorized_endpoint

    high:

      - repeated_h235_failures
      - certificate_expiring_7days
      - trunk_failure

    medium:

      - crl_ocsp_unreachable
      - ntp_drift
      - qos_degradation

  retention:
    signaling_logs: 365d
    media_metadata: 90d
    packet_captures: 30d
    pki_logs: 2555d  # 7 years
    firewall_logs: 365d
```
