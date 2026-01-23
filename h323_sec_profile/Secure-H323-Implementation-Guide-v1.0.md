# Secure H.323 Implementation Guide

## Version 1.0 — Deployment & Configuration Manual

## 1. Purpose

This guide provides the step‑by‑step implementation instructions for deploying a fully secure H.323 environment aligned with the Secure H.323 Zone Standard. It covers:

- Gatekeeper deployment
- Gateway deployment
- Endpoint configuration
- PKI integration
- Network segmentation
- Security enforcement
- Interworking with PSTN/H.320/SIP

This is the how‑to companion to the what defined in the Standard.

## 2. Prerequisites

### 2.1 Infrastructure

- Redundant Gatekeepers (GK1/GK2)
- One or more Gateways (GW1/GW2) in a Voice/Video DMZ
- H.323 endpoints (room systems, soft clients, IP phones)
- Optional MCU
- Enterprise PKI (Root CA + Voice/Video Intermediate CA)
- Secure NTP servers
- Firewalls capable of granular ACLs and DSCP enforcement

### 2.2 Software Requirements

- H.323 stack supporting H.235.2/3/4/6
- SRTP support
- TLS/IPsec support for signaling
- Logging export (syslog/SIEM integration)

## 3. PKI Implementation

### 3.1 Certificate Authority Setup

1. Create offline Root CA.
1. Create Voice/Video Intermediate CA.
1. Configure CRL distribution points and OCSP responders.
1. Publish CA certificates to enterprise trust stores.

### 3.2 Certificate Templates

Create templates for:

- Gatekeeper
- Gateway
- Endpoint (device or user)
- MCU

**Template requirements:**

- Key usage: Digital Signature, Key Encipherment
- Extended key usage: ClientAuth, ServerAuth
- SAN: FQDN + H.323 ID (if supported)
- Minimum RSA 2048 or ECC P‑256

### 3.3 Certificate Enrollment

**Gatekeepers** enroll via SCEP or manual CSR.

**Gateways** enroll via CSR.

**Endpoints** enroll via:

- MDM (soft clients)
- Manual CSR (room systems)
- Auto‑provisioning (IP phones)

## 4. Gatekeeper Deployment

### 4.1 Installation

1. Install GK software or appliance.
1. Import CA chain.
1. Install GK certificate.
1. Enable CRL/OCSP checking.
1. Configure secure NTP.

### 4.2 RAS Configuration

- Enable H.235.2 for RRQ/ARQ/DRQ.
- Require certificate‑based tokens.
- Enable timestamp + nonce validation.
- Set registration TTL (e.g., 3600 seconds).

### 4.3 Signaling Security

- Enable H.235.3 for H.225.
- Enable H.235.4 for H.245.
- Enable TLS/IPsec for signaling transport.
- Reject non‑secure signaling.

### 4.4 Address Resolution

- Define H.323 ID → IP mappings.
- Define E.164 → endpoint mappings.
- Define E.164 → gateway mappings for PSTN/H.320.

### 4.5 Admission Control

- Configure bandwidth per call (e.g., 512 kbps).
- Configure max calls per endpoint.
- Configure max calls per gateway.
- Enable call model (direct or gatekeeper‑routed).

### 4.6 Logging

- Enable RAS logging.
- Enable security event logging.
- Forward logs to SIEM.

## 5. Gateway Deployment

### 5.1 Installation

1. Place gateway in Voice/Video DMZ.
1. Import CA chain.
1. Install gateway certificate.
1. Enable CRL/OCSP.
1. Configure secure NTP.

### 5.2 H.323 Security

- Enable H.235.2 for RAS.
- Enable H.235.3/4 for H.225/H.245.
- Enable TLS/IPsec for signaling.
- Require SRTP (H.235.6) for media.

### 5.3 Legacy Side Configuration

- Configure ISDN PRI/T1/E1 or analog trunks.
- Configure H.320 stack if applicable.
- Map codecs:
  - IP side: G.711/G.729/H.263
  - Legacy side: PCM/H.221/H.261/H.263

### 5.4 Routing

- Configure E.164 ranges for PSTN/H.320.
- Configure GK as call control authority.
- Enable LRQ/LCF processing.

### 5.5 Logging

- Enable CDRs.
- Enable security logs.
- Forward to SIEM.

## 6. Endpoint Deployment

### 6.1 Certificate Installation

- Import CA chain.
- Install endpoint certificate.
- Enable CRL/OCSP.

### 6.2 RAS Configuration

- Configure GK address (FQDN preferred).
- Enable H.235.2 tokens.
- Enable auto‑registration.

### 6.3 Signaling Security

- Enable H.235.3/4.
- Enable TLS/IPsec.
- Require secure signaling.

### 6.4 Media Security

- Enable SRTP.
- Disable RTP fallback.
- Restrict to AES‑based ciphers.

### 6.5 Codec Configuration

- Audio: G.711 mandatory; G.729 optional.
- Video: H.263/H.26x as required.
- Set max bitrate per policy.

### 6.6 Local Security

- Lock admin UI.
- Disable auto‑answer unless required.
- Disable external control unless required.

## 7. Network Implementation

### 7.1 VLANs

- Create Voice/Video VLANs for endpoints.
- Create DMZ VLAN for gateways.
- Create Management VLAN for GK/GW/MCU.

### 7.2 Firewall Rules

**EP → GK:**

- Allow UDP 1719/1718
- Allow TCP 1720/TLS
- Allow H.245 port range

**EP → GW:**

- Allow H.225/H.245
- Allow SRTP media ports

**GK → GW:**

- Allow RAS + H.225

**DMZ → Carrier:**

- Allow only required trunk signaling/media

### 7.3 QoS

- Mark signaling as CS3/AF31.
- Mark voice as EF.
- Mark video as AF41.
- Enable priority queuing.

## 8. Verification Steps

### 8.1 Registration

- EP registers with GK using H.235.2.
- GK logs RRQ/RCF with valid token.

### 8.2 Secure Call Setup

- SETUP/CONNECT protected by H.235.3.
- H.245 SecurityMode negotiation succeeds.
- Logical channels open with SRTP keys.

### 8.3 Media Verification

- RTP packets are SRTP.
- No fallback to clear RTP.
- RTCP is SRTCP.

### 8.4 Gateway Interworking

- IP side: SRTP.
- Legacy side: TDM/H.320.
- Codec mapping correct.

## 9. Completion Criteria

Deployment is considered complete when:

- All endpoints register securely.
- All calls negotiate H.235.3/4/6.
- All media is SRTP.
- Gateways interwork securely.
- All logs flow to SIEM.
- All firewall rules validated.

---

## Related Documentation

- [Secure-H323-Zone-Standard-v1.0.md](./Secure-H323-Zone-Standard-v1.0.md) - Enterprise architecture specification defining requirements
- [PROJECT-AI-Security-Philosophy.txt](./PROJECT-AI-Security-Philosophy.txt) - High-level security philosophy and principles
- [H323_SEC_PROFILE_v1.py](./H323_SEC_PROFILE_v1.py) - Implementation of security profiles v1/v2/v3
- [project_ai_fastapi.py](./project_ai_fastapi.py) - REST API service for security management

## Using Project-AI Tools for Deployment

### Compliance Verification

Use the `h323secctl` CLI tool to verify compliance with this implementation guide:

```bash
# Check deployment compliance
python h323_sec_profile/H323_SEC_PROFILE_v1.py check-compliance --config deployment_config.json

# Query registration status
python h323_sec_profile/H323_SEC_PROFILE_v1.py reg-status \
    --device-ip 192.168.1.100 \
    --snmp-user admin \
    --auth-key authkey123 \
    --priv-key privkey456
```

### API-Based Monitoring

Start the FastAPI service for real-time compliance monitoring:

```bash
cd h323_sec_profile
uvicorn project_ai_fastapi:app --host 0.0.0.0 --port 8080
```

**API Endpoints:**

- `POST /compliance/check` - Validate deployment against standard
- `GET /registration/status` - Query device registration status
- `POST /log` - Submit security events
- `POST /threat-level` - Update threat level for adaptive security
- `POST /evolve` - Trigger self-evolving security cycle

### Configuration Example

Sample deployment configuration file (`deployment_config.json`):

```json
{
  "all_devices_support_h235": true,
  "mandatory_tls_on_h225": true,
  "srtp_everywhere": true,
  "has_logging": true,
  "pki_enforced": true,
  "gatekeepers": [
    {
      "id": "gk1",
      "address": "gk1.voice.example.com",
      "redundant": true
    },
    {
      "id": "gk2",
      "address": "gk2.voice.example.com",
      "redundant": true
    }
  ],
  "gateways": [
    {
      "id": "gw1",
      "address": "gw1.dmz.example.com",
      "e164_ranges": ["+1408555####"]
    }
  ],
  "security_profiles": {
    "v1_baseline": true,
    "v2_adaptive": true,
    "v3_self_evolving": false
  }
}
```

## Troubleshooting

### Common Issues

**Registration Failures:**

- Verify PKI chain is complete and trusted
- Check H.235.2 token generation
- Verify timestamp synchronization (NTP)
- Check firewall rules for RAS ports

**Call Setup Failures:**

- Verify H.235.3/4 negotiation
- Check TLS/IPsec configuration
- Verify SRTP key exchange
- Check codec compatibility

**Media Issues:**

- Verify SRTP is negotiated (not RTP)
- Check firewall rules for media ports
- Verify QoS markings
- Check bandwidth allocation

**Gateway Interworking:**

- Verify codec mapping configuration
- Check E.164 routing tables
- Verify trunk configuration
- Check CDR generation

### Log Analysis

Use the simulation harness to test security negotiation:

```bash
# Run full security simulation
python h323_sec_profile/H323_SEC_PROFILE_v1.py run-sim
```

Expected output: `SIM_OK` indicates all security profiles are properly configured.
