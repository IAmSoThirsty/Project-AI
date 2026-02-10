# Secure H.323 Zone Standard

## Version 1.0 — Enterprise Architecture Specification

## 1. Purpose

This standard defines the mandatory security, architecture, operational, and interoperability requirements for all H.323 deployments within the enterprise. It ensures:

- Full‑stack protection of RAS, H.225, H.245, and RTP
- Mandatory use of H.235 security profiles
- Secure interworking with PSTN, ISDN/H.320, and SIP via gateways
- Consistent PKI‑based identity and trust
- Hardened network segmentation and firewalling
- Auditable, policy‑driven call admission and bandwidth control

This standard applies to all endpoints, gatekeepers, gateways, MCUs, and supporting infrastructure.

## 2. Scope

This standard governs:

- H.323 endpoints (room systems, soft clients, IP phones)
- Gatekeepers (GK)
- H.323 gateways (H.320/PSTN/SIP interworking)
- MCUs
- Voice/Video VLANs and DMZs
- PKI infrastructure supporting H.235
- Monitoring, logging, and operational controls

## 3. Architecture Overview

### 3.1 Logical Components

1. **Endpoints (EPs)**
   - Support H.225, H.245, RAS, RTP/SRTP, H.235
   - Identified by H.323 ID and/or E.164 alias

1. **Gatekeeper (GK)**
   - Central authority for address resolution, admission control, bandwidth management
   - Enforces H.235 security policies

1. **Gateway (GW)**
   - Interworks H.323 ↔ PSTN/ISDN/H.320/SIP
   - Acts as the cryptographic boundary between secure IP and legacy domains

1. **MCU**
   - Multipoint control; treated as a secure endpoint

### 3.2 Zone Definition

A Secure H.323 Zone consists of:

- All endpoints
- Gatekeeper(s)
- Gateways
- MCUs
- Supporting PKI and network infrastructure

All components must comply with this standard.

## 4. Security Model

### 4.1 Mandatory H.235 Profiles

| Protocol | Security Profile | Purpose |
|----------|-----------------|---------|
| RAS | H.235.2 | Authentication of registration and admission requests |
| H.225 (Call Signaling) | H.235.3 or H.235.4 | Mutual authentication, integrity protection |
| H.245 (Control) | H.235.3 or H.235.4 | Secure capability exchange |
| RTP (Media) | H.235.6 (SRTP) | Encryption and integrity of voice/video streams |

**Transport Security:**

- H.225/H.245 **MUST** use TLS or IPsec
- SRTP **MUST** use AES-128 or stronger

### 4.2 Downgrade Policy

- Calls must be rejected if required H.235 profiles cannot be negotiated.
- Exceptions must be explicitly configured for legacy interop and logged.

## 5. PKI Requirements

### 5.1 CA Hierarchy

- Offline Root CA
- Intermediate Voice/Video CA (issues all H.323‑related certs)

### 5.2 Certificates

All H.323 components must have:

- X.509 certificates issued by the Voice/Video CA
- Proper SAN entries (FQDN, endpoint ID)
- Validity periods aligned with enterprise policy

### 5.3 Revocation

- CRL or OCSP checking is mandatory
- Failure to validate → fail‑closed

## 6. Network Architecture

### 6.1 Segmentation

- Voice/Video VLANs for endpoints
- DMZ VLAN for gateways
- Management VLAN for GK/GW/MCU administration

### 6.2 Firewall Requirements

**EP VLAN → GK:**

- Allow RAS (UDP 1719/1718)
- Allow H.225/H.245 (TCP 1720/TLS + fixed H.245 range)

**EP VLAN → GW (inside interface):**

- Allow H.225/H.245
- Allow SRTP media ports (fixed UDP range)

**GK → GW:**

- Allow RAS, H.225

**DMZ → Carrier/Legacy:**

- Only carrier‑required signaling/media

### 6.3 QoS

- Signaling: CS3/AF31
- Voice: EF
- Video: AF41

## 7. Gatekeeper Requirements

### 7.1 RAS Security

- Require H.235.2 tokens for RRQ, ARQ, DRQ
- Enforce timestamp + nonce anti‑replay

### 7.2 Signaling Security

- Enforce H.235.3/4 or TLS/IPsec
- Reject non‑secure signaling unless explicitly whitelisted

### 7.3 Admission Control

- Bandwidth limits per call and per endpoint
- Max concurrent calls per endpoint and per gateway

### 7.4 Address Resolution

- Maintain authoritative mapping of H.323 IDs and E.164 aliases
- Route PSTN/H.320 calls to designated gateways

### 7.5 Logging

- Log all RAS events, security failures, and downgrades
- Forward logs to SIEM

## 8. Gateway Requirements

### 8.1 System Hardening

- Disable unused services
- Restrict management access to admin VLAN
- Enforce strong authentication

### 8.2 PKI

- Install gateway cert from Voice/Video CA
- Enable mutual TLS/IPsec with GK and EPs

### 8.3 H.323 Security

- Use H.235.2 for RAS
- Use H.235.3/4 for H.225/H.245
- Require SRTP (H.235.6) for media

### 8.4 Legacy Side

- Treat PSTN/ISDN/H.320 as untrusted
- Protect physical and logical access to trunks

### 8.5 Logging

- Generate CDRs
- Log all security negotiation failures

## 9. Endpoint Requirements

### 9.1 PKI

- Install device/user cert
- Validate CA chain and revocation

### 9.2 RAS

- Register with GK using H.235.2 tokens

### 9.3 Signaling

- Require secure H.225/H.245
- Prefer TLS/IPsec transport

### 9.4 Media

- Require SRTP
- Disable weak ciphers

### 9.5 Local Security

- Lock admin UI
- Disable unnecessary features (auto‑answer, external control)

## 10. Monitoring & Operations

### 10.1 Time Sync

- All components must use secure NTP

### 10.2 Logging

- Centralize GK, GW, EP logs
- Correlate RAS, signaling, and media events

### 10.3 Alerting

Trigger alerts for:

- Authentication failures
- H.235 negotiation failures
- Security downgrades
- Abnormal call volumes

### 10.4 Change Control

High‑risk changes requiring formal approval:

- PKI updates
- Cipher suite changes
- GK/GW firmware upgrades

## 11. Compliance

All H.323 components must pass:

- Security configuration audit
- PKI validation test
- H.235 negotiation test
- SRTP enforcement test
- Firewall/ACL verification

Non‑compliant systems must be isolated until remediated.

## 12. Exceptions

Exceptions must:

- Be documented
- Be approved by enterprise security
- Be time‑bounded
- Be logged and monitored

## 13. Revision Control

- Version 1.0 — Initial release
- Updates require architecture board approval

---

## Related Documentation

- [PROJECT-AI-Security-Philosophy.txt](./PROJECT-AI-Security-Philosophy.txt) - High-level security philosophy and principles
- [H323_SEC_PROFILE_v1.py](./H323_SEC_PROFILE_v1.py) - Implementation of security profiles v1/v2/v3
- [project_ai_fastapi.py](./project_ai_fastapi.py) - REST API service for security management

## Implementation Notes

This standard is implemented by the Project-AI H.323 Security Capability Profile system:

- **V1 (Baseline)**: Implements core PKI, H.235 profiles, and compliance framework
- **V2 (Adaptive)**: Adds certificate pinning, anomaly detection, and policy adaptation
- **V3 (Self-Evolving)**: Adds autonomous policy generation and predictive threat modeling

Use the CLI tool `h323secctl` or the FastAPI service to validate compliance with this standard.
