# Gateway Interworking Security Profile

## Version 1.0 — H.323 ↔ H.320 / PSTN / SIP Security Specification

## 1. Purpose

This document defines the security, signaling, media, PKI, and operational requirements for all gateways that interconnect the secure H.323 zone with:

- PSTN (analog, T1/E1, PRI)
- ISDN / H.320
- Carrier SIP trunks
- Other H.323 zones

It ensures that:

- The IP side of the gateway is fully protected by H.235
- The legacy side is treated as untrusted and isolated
- The gateway acts as a cryptographic boundary
- All interworking preserves enterprise security posture

## 2. Gateway Role in the Secure H.323 Zone

### 2.1 Functional Role

The gateway:

- Terminates secure H.323 on the enterprise side
- Terminates legacy signaling/media on the external side
- Performs codec translation, protocol conversion, and media transcoding
- Enforces security policy at the boundary

### 2.2 Security Role

The gateway is the trust boundary:

**Inside (enterprise):**

- H.235.2 (RAS auth)
- H.235.3 (H.225 integrity/encryption)
- H.235.4 (H.245 integrity/encryption)
- H.235.6 (SRTP media)
- TLS/IPsec transport

**Outside (legacy):**

- Clear TDM/H.320/SIP depending on carrier
- Protected by physical, logical, and carrier‑grade controls

## 3. Security Requirements

### 3.1 Mandatory H.235 Profiles (IP Side)

| Protocol | H.235 Profile | Transport | Cipher Requirements |
|----------|---------------|-----------|---------------------|
| RAS | H.235.2 | UDP | Certificate-based tokens |
| H.225 | H.235.3 | TLS/IPsec | AES-128+ |
| H.245 | H.235.4 | TLS/IPsec | AES-128+ |
| RTP/Media | H.235.6 (SRTP) | UDP | AES-128+ |

**Enforcement:**

- All IP-side signaling and media **MUST** use the profiles above
- Downgrade to insecure mode **MUST** be rejected
- Security negotiation failures **MUST** be logged and alerted

### 3.2 Legacy Side Requirements

- PSTN/ISDN/H.320/SIP traffic is **not encrypted**
- Gateway must ensure no SRTP keys or secure signaling leaks
- Gateway must enforce strict separation between secure and insecure domains
- Physical access to trunk interfaces must be controlled
- Carrier connections must use dedicated circuits or VPNs

## 4. Signaling Interworking

### 4.1 H.323 ↔ PSTN

**Signaling Mapping:**

- H.225/Q.931 ↔ ISDN Q.931
- H.245 ↔ ISDN bearer capability negotiation
- SRTP ↔ PCM (G.711)
- Cause codes mapped per ITU‑T Q.850

**Call Flow:**
```
Enterprise EP → H.225/TLS → Gateway → Q.931 → PSTN
              ← H.225/TLS ←         ← Q.931 ←

SRTP Media → Gateway → PCM → PSTN
           ← Gateway ← PCM ←
```

**Security Considerations:**

- H.225 SETUP from EP is encrypted (H.235.3)
- Gateway decrypts, validates, converts to Q.931
- Gateway ensures no H.323 security tokens leak to PSTN
- SRTP is decrypted to PCM at gateway boundary

### 4.2 H.323 ↔ H.320

**Signaling Mapping:**

- H.225/H.245 ↔ H.221/H.230/H.242
- Video: H.263/H.261 transcoding
- Audio: G.711/G.722 ↔ H.320 audio formats

**Call Flow:**
```
Enterprise EP → H.225/H.245/TLS → Gateway → H.221/H.230 → H.320 EP
              ←                  ←         ←             ←

SRTP Media → Gateway → H.221 Mux → H.320 EP
           ← Gateway ← H.221 Mux ←
```

**Security Considerations:**

- Full H.235 stack on H.323 side
- H.320 side uses H.221 security (if any)
- Gateway is crypto boundary
- No SRTP keys exposed to H.320 side

### 4.3 H.323 ↔ SIP

**Signaling Mapping:**

- H.225 ↔ SIP INVITE/200/ACK
- H.245 ↔ SDP negotiation
- SRTP ↔ SRTP (if carrier supports)
- SRTP ↔ RTP (if carrier requires clear)
- SIP 183/180 ↔ ALERTING/PROCEEDING

**Call Flow:**
```
Enterprise EP → H.225/TLS → Gateway → SIP/TLS → SIP Trunk
              ←            ←         ←          ←

SRTP → Gateway → SRTP/RTP → SIP Trunk
     ← Gateway ←           ←
```

**Security Considerations:**

- H.323 side always uses H.235
- SIP side may use SRTP (preferred) or RTP (if required)
- If SIP carrier doesn't support SRTP, gateway transcodes SRTP ↔ RTP
- Gateway logs whether carrier leg is SRTP or RTP

## 5. Media Interworking

### 5.1 IP Side (Enterprise)

**Mandatory Requirements:**

- SRTP mandatory
- AES‑128 or AES‑256
- SRTCP integrity required
- Media ports restricted to approved ranges (16384-32767)
- No RTP fallback allowed

### 5.2 Legacy Side

**Protocol-Specific:**

**PSTN:**

- PCM (G.711 µ‑law/A‑law)
- 64 kbps per channel
- No encryption

**ISDN/H.320:**

- H.221 multiplexed media
- Video: H.261/H.263
- Audio: G.711/G.722/G.728
- Data: T.120 (optional)

**SIP:**

- RTP or SRTP depending on carrier capability
- Codecs negotiated via SDP
- DTMF via RFC 2833

### 5.3 Transcoding Requirements

**Audio Transcoding:**

- G.711 ↔ PCM (passthrough)
- G.729 ↔ PCM (transcode required)
- G.722 ↔ PCM (transcode required)
- AMR ↔ G.711 (for SIP carriers)

**Video Transcoding:**

- H.263/H.264 ↔ H.261/H.263 (H.320)
- Resolution scaling as needed
- Bitrate adaptation based on trunk capacity

**Data Passthrough:**

- T.120 passthrough where supported
- FECC (Far End Camera Control) in H.320

**Performance Requirements:**

- Transcoding latency < 50ms
- No audio/video sync issues
- CPU/DSP resources monitored

## 6. PKI Requirements

### 6.1 Certificates

**Gateway Certificate Requirements:**

- Device certificate issued by Voice/Video CA
- Key strength: RSA 2048+ or ECC P-256+
- Validity period: Per enterprise policy (typically 1 year)

**SAN Extensions Must Include:**

- FQDN (e.g., gw1.voice.example.com)
- Gateway role identifier (e.g., h323-pstn-gateway)
- IP address (optional, for legacy compatibility)

**Key Usage:**

- Digital Signature
- Key Encipherment

**Extended Key Usage:**

- Server Authentication
- Client Authentication

### 6.2 Trust Stores

**Trusted CAs:**

- Enterprise Root CA
- Voice/Video Intermediate CA
- No third-party CAs on inside interface

**Revocation Checking:**

- CRL distribution point configured
- OCSP responder configured
- Revocation checking **MUST NOT** be disabled
- Fail-closed on revocation check failure

### 6.3 Mutual Authentication

**Gateway ↔ Gatekeeper:**

- Mutual TLS/IPsec required
- Certificate-based authentication
- H.235.2 tokens for RAS

**Gateway ↔ Endpoint (if direct):**

- Mutual TLS/IPsec required
- H.235.3/4 for signaling
- H.235.6 for media

**Gateway ↔ Carrier:**

- Per carrier requirements
- May use IP ACLs, shared secrets, or certificates
- Document carrier authentication method

## 7. Network Architecture Requirements

### 7.1 Placement

**DMZ Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                     Enterprise Network                       │
│  ┌──────────────────────────────────────────────────┐       │
│  │         Secure H.323 Zone (VLAN 100)            │       │
│  │   Endpoints ──┐                                  │       │
│  │   Endpoints ──┼── Gatekeeper (VLAN 100)         │       │
│  │   MCU ────────┘                                  │       │
│  └────────────────┬─────────────────────────────────┘       │
│                   │                                          │
│                   │ Firewall                                 │
│                   │                                          │
│  ┌────────────────▼─────────────────────────────────┐       │
│  │       Voice/Video DMZ (VLAN 200)                 │       │
│  │                                                   │       │
│  │   ┌─────────────────────────────────┐            │       │
│  │   │         Gateway                 │            │       │
│  │   │  - Inside IF: 10.200.1.10      │            │       │
│  │   │  - Outside IF: 198.51.100.10   │            │       │
│  │   └────────┬───────────────▲────────┘            │       │
│  └────────────┼───────────────┼───────────────────┘       │
└───────────────┼───────────────┼───────────────────────────┘
                │               │
                │  Firewall     │
                │               │
     ┌──────────▼───────────────┼──────────────┐
     │      Carrier Border      │              │
     │                          │              │
     │  ┌───────────────────────▼──────┐      │
     │  │  PSTN / ISDN / SIP Trunk     │      │
     │  └──────────────────────────────┘      │
     └─────────────────────────────────────────┘
```

**Requirements:**

- Gateway must reside in Voice/Video DMZ (VLAN 200)
- Inside interface connects to H.323 zone
- Outside interface connects to PSTN/ISDN/SIP carrier
- Management interface on separate management VLAN

### 7.2 Firewall Rules

**Inside Interface (to H.323 Zone):**

| Source | Destination | Protocol | Port | Purpose |
|--------|-------------|----------|------|---------|
| EP VLAN | Gateway | UDP | 1718/1719 | RAS |
| EP VLAN | Gateway | TCP | 1720 | H.225 |
| EP VLAN | Gateway | TCP | TLS | H.225/TLS |
| EP VLAN | Gateway | TCP | H.245 range | H.245 |
| EP VLAN | Gateway | UDP | 16384-32767 | SRTP |
| Gateway | GK | UDP | 1718/1719 | RAS |
| Gateway | GK | TCP | 1720 | H.225 |

**Outside Interface (to Carrier):**

| Source | Destination | Protocol | Port | Purpose |
|--------|-------------|----------|------|---------|
| Gateway | Carrier | TCP | 5060/5061 | SIP (if applicable) |
| Gateway | Carrier | UDP | 5060 | SIP (if applicable) |
| Gateway | Carrier | UDP | 10000-20000 | RTP/SRTP media (carrier range) |
| Gateway | Carrier | PRI/T1 | N/A | ISDN signaling |

**Deny Rules:**

- Block all enterprise IP ranges from outside interface
- Block all carrier IP ranges from inside interface
- Drop all traffic not explicitly allowed

### 7.3 VLAN Segmentation

**Requirements:**

- Gateway must not share VLANs with endpoints
- Management VLAN must be isolated from production
- No routing between EP VLAN and carrier directly

**VLAN Assignment:**

- VLAN 100: Secure H.323 Zone (Endpoints, GK, MCU)
- VLAN 200: Voice/Video DMZ (Gateways)
- VLAN 300: Management (Admin access only)

## 8. Operational Requirements

### 8.1 Monitoring

**Required Logging:**

- RAS events (RRQ, ARQ, DRQ, RCF, ACF, DCF)
- H.225/H.245 security mode negotiation
- SRTP negotiation status
- Trunk status (up/down, utilization)
- Codec mapping per call
- Call failures with cause codes
- Certificate validation results
- Security downgrade attempts

**Log Destinations:**

- Local syslog
- Centralized SIEM
- CDR repository

**Log Format:**
```json
{
  "timestamp": "2026-01-23T10:49:00Z",
  "event_type": "call_setup",
  "gateway_id": "gw1.voice.example.com",
  "source": "ep1.voice.example.com",
  "destination": "+14085551234",
  "h235_profiles": ["2", "3", "4", "6"],
  "srtp_active": true,
  "codec": "G.711u",
  "trunk": "PRI-1",
  "outcome": "success"
}
```

### 8.2 Health Checks

**Daily Checks:**

- Trunk status (all trunks operational)
- Secure signaling status (H.235 active)
- SRTP active on IP side
- Registration with GK successful
- Certificate validity (not expired)
- CPU/memory utilization < 80%

**Weekly Checks:**

- Log review for security events
- Certificate expiry check (alert if <30 days)
- Firmware version check
- Backup configuration

**Monthly Checks:**

- Full security audit
- PKI validation test
- Failover test
- Capacity planning review

**Automation:**
```bash

# Daily gateway health check

python h323_sec_profile/H323_SEC_PROFILE_v1.py reg-status \
    --device-ip <gateway-ip> \
    --snmp-user admin \
    --auth-key <key> \
    --priv-key <key>

# API health check

curl -X GET "http://localhost:8080/registration/status?device_ip=<gateway-ip>&..."
```

## 9. Failure Handling

### 9.1 Security Downgrade Attempt

**Scenario:** Endpoint or carrier attempts insecure signaling

**Response:**

1. Gateway rejects connection
1. GK logs downgrade attempt
1. SOC alerted immediately
1. Incident investigation initiated

**Logging:**
```bash
python h323_sec_profile/H323_SEC_PROFILE_v1.py log-event \
    --event-type security_downgrade \
    --device-id gw1 \
    --outcome rejected
```

### 9.2 Trunk Failure

**Scenario:** Primary trunk fails

**Response:**

1. Failover to secondary trunk (automatic)
1. GK reroutes new calls to alternate gateway
1. Active calls continue on remaining trunks
1. NOC alerted
1. Carrier notified

**Validation:**
```bash

# Check trunk status

snmpwalk -v3 -u admin <gateway-ip> trunkStatus
```

### 9.3 Certificate Failure

**Scenario:** Gateway certificate expires or is revoked

**Response:**

1. Gateway fails closed (reject all calls)
1. SOC alerted immediately
1. PKI team notified
1. Certificate renewed/reissued
1. Gateway restarted after cert installation

**Prevention:**

- Certificate expiry monitoring (30-day alert)
- Automated renewal process
- Test certificates in staging first

## 10. Compliance Requirements

A gateway is compliant when:

- ✅ All H.235 profiles enforced on IP side
- ✅ All IP‑side media is SRTP
- ✅ All signaling is encrypted/integrity‑protected
- ✅ Legacy side isolated in DMZ
- ✅ PKI validated (valid certs, CRL/OCSP enabled)
- ✅ Logs exported to SIEM
- ✅ Firewall segmentation verified
- ✅ No critical security violations
- ✅ Regular health checks passing
- ✅ Failover tested successfully

**Validation:**
```bash

# Run compliance check

python h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance \
    --config gateway_deployment_config.json

# Expected result: PASS with no critical failures

```

**Sample Configuration:**
```json
{
  "component_type": "gateway",
  "gateway_id": "gw1.voice.example.com",
  "all_devices_support_h235": true,
  "mandatory_tls_on_h225": true,
  "srtp_everywhere": true,
  "has_logging": true,
  "pki_enforced": true,
  "dmz_placement": true,
  "firewall_segmentation": true,
  "trunk_types": ["PRI", "SIP"],
  "interworking_protocols": ["PSTN", "H.320", "SIP"]
}
```

---

## Related Documentation

- [Secure-H323-Zone-Standard-v1.0.md](./Secure-H323-Zone-Standard-v1.0.md) - Overall zone requirements
- [Secure-H323-Implementation-Guide-v1.0.md](./Secure-H323-Implementation-Guide-v1.0.md) - Gateway deployment procedures (Section 5)
- [Secure-H323-Operational-Runbook-v1.0.md](./Secure-H323-Operational-Runbook-v1.0.md) - Gateway operations (Section 5.2)
- [H323-H235-Security-Test-Plan-v1.0.md](./H323-H235-Security-Test-Plan-v1.0.md) - Gateway security tests (Section 8)
- [H323-H235-Compliance-Matrix-v1.0.md](./H323-H235-Compliance-Matrix-v1.0.md) - Gateway compliance (Section 2.6)
- [H323_SEC_PROFILE_v1.py](./H323_SEC_PROFILE_v1.py) - Automation tools
- [project_ai_fastapi.py](./project_ai_fastapi.py) - REST API service

## Appendix A: Carrier Integration Checklist

### PSTN/ISDN Integration

- [ ] Trunk type determined (analog, T1/E1, PRI)
- [ ] Signaling protocol configured (Q.931, Q.SIG)
- [ ] DID ranges assigned and routed
- [ ] Emergency services (911/E911) tested
- [ ] Caller ID delivery verified
- [ ] Codec preferences configured
- [ ] Echo cancellation tuned
- [ ] DTMF handling verified

### H.320 Integration

- [ ] H.320 stack enabled
- [ ] Video codec compatibility verified (H.261/H.263)
- [ ] Audio codec compatibility verified
- [ ] H.221 multiplexing configured
- [ ] FECC (camera control) tested
- [ ] T.120 data channel tested (if required)
- [ ] Bandwidth settings configured
- [ ] Call setup time acceptable

### SIP Trunk Integration

- [ ] Carrier SIP trunk details obtained
- [ ] SIP registration configured (if required)
- [ ] SRTP preference communicated to carrier
- [ ] SDP offer/answer tested
- [ ] Codec negotiation validated
- [ ] DTMF relay method configured (RFC 2833 vs SIP INFO)
- [ ] Emergency services verified
- [ ] Failover trunk configured
- [ ] Quality monitoring enabled

## Appendix B: Troubleshooting Guide

### Issue: Gateway Cannot Register with Gatekeeper

**Symptoms:**

- RRQ rejected
- H.235.2 token validation fails

**Resolution:**

1. Verify gateway certificate validity
1. Check time synchronization (NTP)
1. Validate CRL/OCSP reachability
1. Review GK logs for rejection reason
1. Test mutual TLS connectivity

### Issue: Calls Fail at Gateway

**Symptoms:**

- SETUP rejected
- No media path established

**Resolution:**

1. Check trunk status
1. Verify codec compatibility
1. Validate firewall rules
1. Check SRTP negotiation
1. Review cause codes in logs

### Issue: Poor Call Quality Through Gateway

**Symptoms:**

- Choppy audio
- Video artifacts
- Echo

**Resolution:**

1. Check jitter/latency
1. Verify QoS markings
1. Review codec selection
1. Check transcoding CPU load
1. Tune echo cancellation
1. Validate bandwidth allocation

## Appendix C: Gateway Configuration Templates

### Cisco IOS Gateway Example

```
! H.323 Gateway Configuration
interface GigabitEthernet0/0
 description Inside Interface to H.323 Zone
 ip address 10.200.1.10 255.255.255.0

interface GigabitEthernet0/1
 description Outside Interface to Carrier
 ip address 198.51.100.10 255.255.255.0

! H.323 Configuration
gateway
 security h235-enable
 timer receive-rtp 1200

! H.235 Security
h323 h235 encryption aes128
h323 h235 authentication required

! Gatekeeper Registration
interface GigabitEthernet0/0
 h323-gateway voip interface
 h323-gateway voip id gk1.voice.example.com
 h323-gateway voip h323-id gw1.voice.example.com
 h323-gateway voip bind srcaddr 10.200.1.10

! SRTP Configuration
voice service voip
 media flow-around
 media disable-detailed-stats
 srtp-crypto 1 AES_CM_128_HMAC_SHA1_80

! Certificate Configuration
crypto pki trustpoint VoiceVideoCA
 enrollment terminal
 revocation-check crl ocsp
 rsakeypair gw1-keypair 2048
```

**Note:** Actual configuration varies by platform and firmware version. Consult vendor documentation for platform-specific syntax.
