## 3. Security Architecture

### 3.1 H.235 Security Profiles Utilized

- H.235.1: Baseline security (Authentication Framework)
- H.235.2: Registration/Admission (RAS) security, integrity, authentication, replay protection
- H.235.3: Signaling channel security (H.225), including TLS for Q.931
- H.235.4: H.245 Message Security (negotiation of encryption, authentication)
- H.235.6: Secure key management for SRTP (audio/video payload protection, AES-GCM recommended)

All critical messages (registration, admission, signaling, media channel setup) must be signed, authenticated, and, where required, encrypted per profile.

### 3.2 PKI Certificate Requirements
- Issued to: Gatekeepers, Gateways, Endpoints (user/device-bound), MCUs
- Contents:
  - X.509 v3 with `subjectAltName` (FQDN)
  - Key usages: `digitalSignature`, `keyEncipherment`
  - Extended USAGE: `clientAuth`, `serverAuth`
- Trust model:
  - All zone devices trust the enterprise root CA
  - CRL and/or OCSP must be reachable for real-time revocation status checking

---

## 4. Network & Topology Requirements

### 4.1 Segmentation
- Endpoints: On dedicated Voice/Video VLAN(s)
- Gateways: In a tightly firewalled DMZ VLAN
- Gatekeeper: In a secure core VLAN
- No direct access between endpoint and PSTN; all calls traverse the gateway
- Firewall rules: Must strictly limit access to defined protocols/ports (RAS, H.225, H.245, SRTP)

### 4.2 Firewall Rules (Minimum Set)

| Protocol      | Port(s)   | Direction      | Source        | Destination        | Description                     |
|---------------|-----------|---------------|---------------|--------------------|---------------------------------|
| RAS (UDP)     | 1719      | bi-directional | EP, GW        | Gatekeeper         | Discovery, registration         |
| H.225 (TCP)   | 1720      | bi-directional | EP, GW        | EP, GW, Gatekeeper | Call setup/signaling            |
| H.245 (TCP)   | dynamic   | bi-directional | EP, GW, MCU   | EP, GW, MCU        | Media/control negotiation       |
| SRTP (UDP)    | dynamic   | uni-directional| EP, GW, MCU   | EP, GW, MCU        | Secure audio/video streams      |
| TLS           | 443/Other | bi-directional | All H.323 dev | All H.323 dev      | Certificate validation (CRL/OCSP)|

- Define and restrict dynamic port ranges for H.245/SRTP via policy and endpoint configuration.

---

## 5. Full-Security Call Flow: H.323 ↔ Gateway ↔ H.320/PSTN

### Phase 0 – Trust Bootstrap
- Devices securely enroll with enterprise PKI; provisioned with proper certificates and CRL/OCSP path.
- Gatekeeper is configured as the authority for the H.323 zone; all endpoints, gateways, MCUs register to it.
- Gateway registers as egress for H.320/ISDN/PSTN.

### Phase 1 – RAS Discovery & Registration (H.235.2)
| Step | Message | Sender | Receiver | Security Notes            |
|------|---------|--------|----------|---------------------------|
| 1    | GRQ     | EP     | GK       | H.235 token (signed)      |
| 2    | GCF     | GK     | EP       |                           |
| 3    | RRQ     | EP     | GK       | Full message signature    |
| 4    | RCF     | GK     | EP       |                           |
| 5    | RRQ     | GW     | GK       |                           |
| 6    | RCF     | GK     | GW       |                           |
- All registration/admission messages use H.235 tokens for authentication and replay protection.

### Phase 2 – Secure Call Setup: Admission & Location (H.235.2)
| Step | Message | Sender | Receiver | Security Notes                |
|------|---------|--------|----------|-------------------------------|
| 1    | ARQ     | EP     | GK       | destAlias = PSTN/H.320 #, H.235|
| 2    | LRQ     | GK     | GW       |                               |
| 3    | LCF     | GW     | GK       |                               |
| 4    | ACF     | GK     | EP       | Includes GW address, signed   |

### Phase 3 – H.225 Call Setup (H.235.3 / TLS if possible)
| Step | Message     | Sender | Receiver     | Security Notes                  |
|------|-------------|--------|-------------|---------------------------------|
| 1    | SETUP       | EP     | GW          | SecurityCapabilities + cryptoTokens (H.235.3/TLS) |
| 2    | CALL PROCEED| GW     | EP          |                                 |
| 3    | SETUP/IAM   | GW     | LEG (PSTN)  |                                 |
| 4    | ALERTING    | LEG    | GW          |                                 |
| 5    | ALERTING    | GW     | EP          |                                 |
| 6    | CONNECT     | LEG    | GW          |                                 |
| 7    | CONNECT     | GW     | EP          | With cryptoTokens (H.235.3)     |

### Phase 4 – H.245 Security Negotiation (H.235.4)
| Step | Message               | Sender | Receiver | Security Notes           |
|------|----------------------|--------|----------|--------------------------|
| 1    | SecurityModeCommand  | EP     | GW       | Propose AES/HMAC, signed |
| 2    | SecurityModeAck      | GW     | EP       | Accepts/declines         |
| 3    | TCS/MSD (encrypted)  | EP<->GW|          | Capabilities exchange    |

### Phase 5 – Logical Channel + SRTP Keying (H.235.6)
| Step | Message                 | Sender | Receiver | Security                                     |
|------|------------------------|--------|----------|----------------------------------------------|
| 1    | OLC (audio, SRTP keys) | EP     | GW       | Audio (mandatory, G.711 or better)           |
| 2    | OLC Ack                | GW     | EP       |                                              |
| 3    | OLC (video, SRTP keys) | EP     | GW       | Video (optional, H.263/H.264)                |
| 4    | OLC Ack                | GW     | EP       |                                              |
- All keying data must use H.235.6 syntax and be encrypted in transmission.

### Phase 6 – Media Flow
- Media (SRTP): EP ↔ GW: Encrypted RTP streams, keys/algorithms established in H.235.6, using AES-128/256 for confidentiality, HMAC-SHA for integrity.

---

## 6. Threat Model & Security Guarantees

### Threats Addressed
- Impersonation of endpoints, gateways, or gatekeepers
- Replay attacks on RAS and H.225
- Downgrade attacks on H.245 capability negotiation
- Media interception (SRTP prevents this)
- Unauthorized PSTN breakout
- Rogue gateway insertion
- Certificate spoofing or stale CRLs
- Signaling tampering (H.235.3)

### Threats Not Addressed (By Design)
- PSTN‑side confidentiality (legacy TDM is clear)
- Endpoint compromise (malware, physical access)
- QoS degradation or congestion attacks
- Carrier‑side ISUP manipulation

### Security Guarantees
- Mutual authentication across all H.323 entities
- Integrity for RAS, H.225, H.245
- Confidentiality for media (SRTP)
- Non‑repudiation via signed tokens
- Deterministic trust boundary at the gateway
