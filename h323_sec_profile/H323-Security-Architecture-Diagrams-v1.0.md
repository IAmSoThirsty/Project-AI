# H.323 Security Architecture Diagram Specification

## Version 1.0 — Structural, Logical, and Data‑Flow Blueprint

## 1. Purpose

This specification defines the canonical architecture diagrams for a secure H.323 deployment, including:

- Logical architecture
- Physical topology
- Trust boundaries
- Signaling and media flows
- PKI trust relationships
- Gateway interworking paths
- VLAN, firewall, and DMZ segmentation

These specifications allow architects, engineers, and vendors to produce consistent, accurate diagrams across documentation, audits, and design reviews.

## 2. Diagram Types

This specification defines six required diagram types:

1. **Logical Architecture Diagram**
1. **Physical Network Topology Diagram**
1. **Security Trust Boundary Diagram**
1. **Signaling Flow Diagram** (RAS + H.225 + H.245)
1. **Media Flow Diagram** (SRTP + Legacy Interworking)
1. **PKI Trust & Certificate Flow Diagram**

Each diagram type is defined below with:

- Required components
- Required relationships
- Required annotations
- Required security markings

## 3. Logical Architecture Diagram Specification

### 3.1 Required Components

- H.323 Endpoints (EPs)
- Gatekeeper (GK)
- Gateways (GW)
- MCUs
- Enterprise PKI (Root CA, Intermediate CA)
- NTP servers
- SIEM / Logging infrastructure

### 3.2 Required Logical Groupings

**H.323 Zone containing:**

- EPs
- GK
- MCUs

**Voice/Video DMZ containing:**

- Gateways
- SBCs (if SIP interworking exists)

**Carrier / Legacy Domain containing:**

- PSTN
- ISDN/H.320
- SIP trunks

### 3.3 Required Annotations

- "H.323 Zone = Trusted Domain"
- "DMZ = Semi‑Trusted Boundary"
- "Carrier/Legacy = Untrusted Domain"
- "Gateway = Cryptographic Boundary"

### 3.4 Logical Architecture Diagram Template

```
╔════════════════════════════════════════════════════════════════╗
║                    TRUSTED H.323 ZONE                          ║
║  ┌──────────────────────────────────────────────────────┐     ║
║  │                                                       │     ║
║  │   ┌─────────┐  ┌─────────┐  ┌─────────┐            │     ║
║  │   │  EP-1   │  │  EP-2   │  │  EP-N   │            │     ║
║  │   │ (H.323) │  │ (H.323) │  │ (H.323) │            │     ║
║  │   └────┬────┘  └────┬────┘  └────┬────┘            │     ║
║  │        │            │            │                   │     ║
║  │        └────────────┼────────────┘                   │     ║
║  │                     │                                │     ║
║  │                ┌────▼────┐                           │     ║
║  │                │   GK    │ ◄── H.235.2 RAS Auth     │     ║
║  │                │  (PKI)  │                           │     ║
║  │                └────┬────┘                           │     ║
║  │                     │                                │     ║
║  │                ┌────▼────┐                           │     ║
║  │                │   MCU   │                           │     ║
║  │                │ (H.323) │                           │     ║
║  │                └─────────┘                           │     ║
║  │                                                       │     ║
║  └───────────────────┬───────────────────────────────────┘     ║
║                      │ H.235.3/4 (TLS)                        ║
╚══════════════════════▼════════════════════════════════════════╝
                       │
        ┌──────────────┴──────────────┐
        │   CRYPTOGRAPHIC BOUNDARY    │
        │      (Firewall + ACLs)      │
        └──────────────┬──────────────┘
                       │
╔══════════════════════▼════════════════════════════════════════╗
║                  SEMI-TRUSTED DMZ                              ║
║  ┌────────────────────────────────────────────────────┐       ║
║  │                                                     │       ║
║  │              ┌─────────────────┐                   │       ║
║  │              │  Gateway (GW)   │                   │       ║
║  │              │                 │                   │       ║
║  │              │ - Inside: H.323 │                   │       ║
║  │              │   (H.235 Full)  │                   │       ║
║  │              │                 │                   │       ║
║  │              │ - Outside: TDM/ │                   │       ║
║  │              │   H.320/SIP     │                   │       ║
║  │              └────────┬────────┘                   │       ║
║  │                       │                            │       ║
║  └───────────────────────┼────────────────────────────┘       ║
║                          │ Legacy Signaling/Media             ║
╚══════════════════════════▼════════════════════════════════════╝
                           │
        ┌──────────────────┴──────────────────┐
        │      CARRIER/LEGACY BOUNDARY        │
        │    (Physical + Carrier Security)    │
        └──────────────────┬──────────────────┘
                           │
╔══════════════════════════▼════════════════════════════════════╗
║                  UNTRUSTED LEGACY DOMAIN                       ║
║  ┌────────────────────────────────────────────────────┐       ║
║  │                                                     │       ║
║  │   ┌─────────┐   ┌──────────┐   ┌─────────────┐   │       ║
║  │   │  PSTN   │   │  H.320   │   │  SIP Trunk  │   │       ║
║  │   │ (TDM)   │   │  (ISDN)  │   │  (Carrier)  │   │       ║
║  │   └─────────┘   └──────────┘   └─────────────┘   │       ║
║  │                                                     │       ║
║  └─────────────────────────────────────────────────────┘       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

Supporting Infrastructure (All Zones):
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PKI (CA)    │  │  NTP Servers │  │   SIEM/Logs  │
│  - Root CA   │  │  (Secure)    │  │  (Central)   │
│  - Voice CA  │  │              │  │              │
│  - CRL/OCSP  │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

## 4. Physical Network Topology Diagram Specification

### 4.1 Required Network Elements

- Access switches (endpoint VLANs)
- Distribution switches
- Core switches
- Firewalls (inside, DMZ, outside)
- Routers (WAN, carrier edge)

### 4.2 Required VLANs

- Voice/Video Endpoint VLAN(s) (VLAN 100)
- H.323 Control VLAN (optional)
- DMZ VLAN(s) (VLAN 200)
- Management VLAN (VLAN 300)
- PKI/Infrastructure VLAN (VLAN 400)

### 4.3 Required Interfaces

- EP → Access Switch
- Access Switch → Distribution/Core
- Core → GK
- Core → DMZ Firewall
- DMZ Firewall → Gateway
- Gateway → Carrier Edge

### 4.4 Required Labels

- "SRTP Media Path"
- "Secure Signaling Path (TLS/IPsec)"
- "RAS Path (H.235.2)"
- "Legacy Media Path (Unencrypted)"

### 4.5 Physical Topology Diagram Template

```
Enterprise Network Physical Topology

┌─────────────────────────────────────────────────────────────────┐
│                    Enterprise Campus                            │
│                                                                 │
│  Building A                     Building B                      │
│  ┌───────────────┐             ┌───────────────┐              │
│  │               │             │               │              │
│  │  EP  EP  EP   │             │  EP  EP  EP   │              │
│  │   │   │   │   │             │   │   │   │   │              │
│  │  ┌┴───┴───┴┐  │             │  ┌┴───┴───┴┐  │              │
│  │  │ Access  │  │             │  │ Access  │  │              │
│  │  │ Switch  │  │             │  │ Switch  │  │              │
│  │  │VLAN 100 │  │             │  │VLAN 100 │  │              │
│  │  └────┬────┘  │             │  └────┬────┘  │              │
│  └───────┼───────┘             └───────┼───────┘              │
│          │                             │                       │
│          └──────────┬──────────────────┘                       │
│                     │                                          │
│              ┌──────▼──────┐                                   │
│              │Distribution │                                   │
│              │   Switch    │                                   │
│              └──────┬──────┘                                   │
│                     │                                          │
│              ┌──────▼──────────────────┐                       │
│              │   Core Switch Layer     │                       │
│              │  - VLAN 100: Endpoints  │                       │
│              │  - VLAN 200: DMZ        │                       │
│              │  - VLAN 300: Mgmt       │                       │
│              │  - VLAN 400: Infra      │                       │
│              └──────┬──────────────────┘                       │
│                     │                                          │
│         ┌───────────┼───────────┐                              │
│         │           │           │                              │
│    ┌────▼────┐ ┌───▼────┐ ┌───▼─────┐                         │
│    │   GK    │ │  MCU   │ │   PKI   │                         │
│    │VLAN 100 │ │VLAN100 │ │ VLAN400 │                         │
│    └─────────┘ └────────┘ └─────────┘                         │
│                     │                                          │
└─────────────────────┼──────────────────────────────────────────┘
                      │
               ┌──────▼──────┐
               │  Firewall   │ ◄── Inside FW
               │  (Inside)   │
               │  ACLs + IDS │
               └──────┬──────┘
                      │
┌─────────────────────▼──────────────────────────────────────────┐
│                    Voice/Video DMZ (VLAN 200)                   │
│                                                                 │
│                  ┌─────────────────┐                            │
│                  │   Gateway (GW)  │                            │
│                  │                 │                            │
│                  │ Inside IF:      │                            │
│                  │  10.200.1.10    │                            │
│                  │ VLAN 200        │                            │
│                  │                 │                            │
│                  │ Outside IF:     │                            │
│                  │  198.51.100.10  │                            │
│                  └────────┬────────┘                            │
│                           │                                     │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                     ┌──────▼──────┐
                     │  Firewall   │ ◄── Outside FW
                     │  (Outside)  │
                     │  ACLs + IPS │
                     └──────┬──────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     Carrier Edge                                │
│                                                                 │
│    ┌──────────┐        ┌──────────┐       ┌──────────┐        │
│    │ T1/PRI   │        │  H.320   │       │   SIP    │        │
│    │  Trunk   │        │  Trunk   │       │  Trunk   │        │
│    └─────┬────┘        └─────┬────┘       └─────┬────┘        │
│          │                   │                   │             │
└──────────┼───────────────────┼───────────────────┼─────────────┘
           │                   │                   │
           └───────────────────┴───────────────────┘
                               │
                          Carrier Network
```

## 5. Security Trust Boundary Diagram Specification

### 5.1 Required Trust Zones

**Trusted Zone:**

- EPs
- GK
- MCUs

**Semi‑Trusted Zone:**

- Gateways
- SBCs

**Untrusted Zone:**

- PSTN
- ISDN/H.320
- Carrier SIP

### 5.2 Required Boundary Markings

- "Boundary: Secure H.323 Signaling (H.235.3/4)"
- "Boundary: Secure Media (H.235.6 SRTP)"
- "Boundary: Legacy Clear Media"

### 5.3 Required Security Controls

- Mutual TLS/IPsec
- H.235 token validation
- Firewall ACLs
- VLAN isolation
- PKI trust anchors

### 5.4 Trust Boundary Diagram Template

```
Security Trust Boundaries

╔═══════════════════════════════════════════════════════════════╗
║                  TRUSTED ZONE (GREEN)                          ║
║  Trust Level: HIGH                                             ║
║  Security: Full H.235 Suite                                    ║
║                                                                ║
║    Endpoints ──► Gatekeeper ──► MCU                            ║
║    (H.235.2/3/4/6 + TLS/IPsec)                                ║
║                                                                ║
║  Security Controls:                                            ║
║  • Mutual TLS authentication                                   ║
║  • H.235 tokens (certificate-based)                            ║
║  • SRTP with AES-128+                                          ║
║  • PKI trust chain validation                                  ║
║  • CRL/OCSP checking                                           ║
╚═══════════════════════════════════════════════════════════════╝
                           │
        ═══════════════════▼═══════════════════
        ║   SECURITY BOUNDARY #1              ║
        ║   - Firewall with ACLs              ║
        ║   - VLAN segmentation               ║
        ║   - TLS inspection (optional)       ║
        ║   - IDS/IPS monitoring              ║
        ═══════════════════▼═══════════════════
                           │
╔═══════════════════════════════════════════════════════════════╗
║              SEMI-TRUSTED ZONE (YELLOW)                        ║
║  Trust Level: MEDIUM                                           ║
║  Security: Crypto Boundary                                     ║
║                                                                ║
║              ┌──────────────────────┐                          ║
║              │      Gateway         │                          ║
║              │                      │                          ║
║              │  Inside: H.235 Full  │                          ║
║              │  Outside: Legacy     │                          ║
║              └──────────────────────┘                          ║
║                                                                ║
║  Security Controls:                                            ║
║  • SRTP ↔ Clear media conversion                               ║
║  • H.323 ↔ Legacy protocol conversion                          ║
║  • No SRTP key leakage                                         ║
║  • Physical trunk security                                     ║
║  • DMZ isolation                                               ║
╚═══════════════════════════════════════════════════════════════╝
                           │
        ═══════════════════▼═══════════════════
        ║   SECURITY BOUNDARY #2              ║
        ║   - Firewall (restrictive)          ║
        ║   - Carrier-only ACLs               ║
        ║   - Physical trunk security         ║
        ║   - IPS monitoring                  ║
        ═══════════════════▼═══════════════════
                           │
╔═══════════════════════════════════════════════════════════════╗
║                 UNTRUSTED ZONE (RED)                           ║
║  Trust Level: LOW                                              ║
║  Security: None (Carrier-grade only)                           ║
║                                                                ║
║    PSTN ──── H.320 ──── SIP Trunk                              ║
║    (Clear signaling and media)                                 ║
║                                                                ║
║  Security Controls:                                            ║
║  • Physical access control                                     ║
║  • Carrier-provided security                                   ║
║  • No enterprise data exposed                                  ║
║  • Call detail logging                                         ║
╚═══════════════════════════════════════════════════════════════╝
```

## 6. Signaling Flow Diagram Specification

This diagram must show all signaling flows:

### 6.1 RAS (H.225.0 RAS)

- GRQ/GCF
- RRQ/RCF
- ARQ/ACF
- DRQ/DCF

**Annotations:**

- "Protected by H.235.2 (auth + integrity + anti‑replay)"

### 6.2 H.225 (Q.931‑like)

- SETUP
- CALL PROCEEDING
- ALERTING
- CONNECT
- RELEASE COMPLETE

**Annotations:**

- "Protected by H.235.3 or TLS/IPsec"

### 6.3 H.245

- SecurityModeCommand / SecurityModeAck
- TerminalCapabilitySet / Ack
- MasterSlaveDetermination
- OpenLogicalChannel / Ack
- EndSessionCommand

**Annotations:**

- "Protected by H.235.4 (integrity + encryption)"
- "OLC carries SRTP keying (H.235.6)"

### 6.4 Signaling Flow Diagram Template

```
H.323 Secure Signaling Flow

Endpoint (EP)         Gatekeeper (GK)        Gateway (GW)      PSTN/Legacy
    │                      │                      │                │
    │                      │                      │                │
    │──── GRQ ──────────►│                      │                │
    │◄─── GCF ───────────│                      │                │
    │   (Discovery)        │                      │                │
    │                      │                      │                │
    │──── RRQ ──────────►│                      │                │
    │   + H.235.2 Token   │                      │                │
    │◄─── RCF ───────────│                      │                │
    │   (Registered)       │                      │                │
    │                      │                      │                │
    │──── ARQ ──────────►│                      │                │
    │   (Call Request)    │                      │                │
    │◄─── ACF ───────────│                      │                │
    │   (Call Approved)   │                      │                │
    │                      │                      │                │
    │──── SETUP (H.225) ─────────────────────►│                │
    │   [H.235.3 Protected / TLS Encrypted]     │                │
    │                      │                      │                │
    │                      │                      │── Q.931 SETUP ──►│
    │                      │                      │   (Legacy)       │
    │                      │                      │                │
    │                      │                      │◄─ ALERTING ─────│
    │◄──── ALERTING ──────────────────────────│                │
    │   [H.235.3 Protected]                     │                │
    │                      │                      │                │
    │                      │                      │◄─ CONNECT ──────│
    │◄──── CONNECT ───────────────────────────│                │
    │   [H.235.3 Protected]                     │                │
    │                      │                      │                │
    │──── H.245 SecurityModeCommand ──────────►│                │
    │◄─── H.245 SecurityModeAck ──────────────│                │
    │   [H.235.4 Protected]                     │                │
    │                      │                      │                │
    │──── H.245 OLC ─────────────────────────►│                │
    │   + SRTP keys [H.235.6]                   │                │
    │◄─── H.245 OLC Ack ──────────────────────│                │
    │                      │                      │                │
    │═════ SRTP Media ═══════════════════════►│                │
    │                      │                      │                │
    │                      │                      │═══ PCM ════════►│
    │                      │                      │   (Clear)       │
    │                      │                      │                │
    │──── RELEASE ───────────────────────────►│                │
    │◄─── RELEASE COMPLETE ────────────────────│                │
    │                      │                      │                │
    │──── DRQ ──────────►│                      │                │
    │◄─── DCF ───────────│                      │                │
    │   (Unregister)       │                      │                │
    │                      │                      │                │

Legend:
────► : Signaling message
═════► : Media flow
[H.235.x] : Security protection
```

## 7. Media Flow Diagram Specification

### 7.1 IP‑Side Media (Enterprise)

- SRTP audio
- SRTP video
- SRTCP control

**Annotations:**

- "Encrypted media (H.235.6)"
- "AES‑based cipher suite"

### 7.2 Gateway Media Mapping

- SRTP ↔ PCM (PSTN)
- SRTP ↔ H.221 multiplex (H.320)
- SRTP ↔ RTP/SRTP (SIP)

### 7.3 Legacy Media

- "Unencrypted TDM/H.320 media"
- "Carrier‑grade physical security only"

### 7.4 Media Flow Diagram Template

```
H.323 Secure Media Flow

┌──────────────────────────────────────────────────────────────┐
│                   Enterprise H.323 Zone                       │
│  ┌────────────┐                           ┌────────────┐     │
│  │ Endpoint A │                           │ Endpoint B │     │
│  │            │                           │            │     │
│  │ Audio: G.711│                          │ Audio: G.711│    │
│  │ Video: H.264│                          │ Video: H.264│    │
│  └─────┬──────┘                           └──────┬─────┘     │
│        │                                         │           │
│        │ SRTP (AES-128)                          │           │
│        │ Port: 16384-32767                       │           │
│        │                                         │           │
│        └──────────────►GK◄───────────────────────┘           │
│           [H.235.6]    │    [H.235.6]                        │
│                        │                                     │
└────────────────────────┼─────────────────────────────────────┘
                         │
                         │ Firewall
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                      DMZ Zone                                │
│               ┌────────────────┐                             │
│               │   Gateway      │                             │
│               │                │                             │
│  SRTP In ────►│   SRTP→PCM    │───► PCM Out                 │
│  (AES-128)    │   SRTP→H.221  │     (Clear)                 │
│               │   SRTP→RTP    │                             │
│               │                │                             │
│               │  Transcoding:  │                             │
│               │  G.711, G.729  │                             │
│               │  H.263, H.264  │                             │
│               └────────┬───────┘                             │
│                        │                                     │
└────────────────────────┼─────────────────────────────────────┘
                         │
                         │ Carrier Border
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                   Legacy/Carrier Domain                      │
│                                                              │
│   ┌──────────┐      ┌───────────┐      ┌──────────┐        │
│   │   PSTN   │      │   H.320   │      │   SIP    │        │
│   │          │      │           │      │          │        │
│   │ PCM      │      │ H.221 Mux │      │ RTP/SRTP │        │
│   │ (64kbps) │      │ (Clear)   │      │ (Carrier)│        │
│   └──────────┘      └───────────┘      └──────────┘        │
│                                                              │
└──────────────────────────────────────────────────────────────┘

Media Security Summary:
┌───────────────────────────────────────────────────────────┐
│ Zone          │ Protocol  │ Encryption │ Key Management   │
├───────────────┼───────────┼────────────┼──────────────────┤
│ Enterprise    │ SRTP      │ AES-128+   │ H.245 OLC        │
│ DMZ           │ SRTP/Clear│ N/A        │ Transcoding      │
│ Legacy/Carrier│ RTP/PCM   │ None       │ N/A              │
└───────────────────────────────────────────────────────────┘
```

## 8. PKI Trust & Certificate Flow Diagram Specification

### 8.1 Required PKI Components

- Offline Root CA
- Voice/Video Intermediate CA
- CRL/OCSP servers

### 8.2 Required Certificate Flows

- EP → CA (enrollment)
- GK → CA (enrollment)
- GW → CA (enrollment)
- EP/GK/GW → CRL/OCSP (revocation checks)

### 8.3 Required Trust Relationships

- EP trusts CA chain
- GK trusts CA chain
- GW trusts CA chain
- Mutual TLS between:
  - EP ↔ GK
  - EP ↔ GW
  - GK ↔ GW

### 8.4 Required Annotations

- "Certificate‑based H.235 tokens"
- "Mutual TLS authentication"
- "Fail‑closed on revocation failure"

### 8.5 PKI Trust Diagram Template

```
PKI Trust & Certificate Flow

┌─────────────────────────────────────────────────────────────────┐
│                      PKI Infrastructure                         │
│                                                                 │
│                    ┌──────────────────┐                         │
│                    │   Offline Root   │                         │
│                    │      CA          │                         │
│                    │   (Rarely Used)  │                         │
│                    └────────┬─────────┘                         │
│                             │ Signs                             │
│                             ▼                                   │
│                    ┌──────────────────┐                         │
│                    │  Voice/Video CA  │                         │
│                    │  (Intermediate)  │                         │
│                    │   Issues Certs   │                         │
│                    └────────┬─────────┘                         │
│                             │                                   │
│          ┌──────────────────┼──────────────────┐                │
│          │                  │                  │                │
│          ▼                  ▼                  ▼                │
│   ┌───────────┐      ┌───────────┐     ┌───────────┐           │
│   │  CRL      │      │   OCSP    │     │  Cert     │           │
│   │  Server   │      │  Responder│     │  Portal   │           │
│   └───────────┘      └───────────┘     └───────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │   EP    │     │   GK    │     │   GW    │
    │         │     │         │     │         │
    │ 1. CSR  │     │ 1. CSR  │     │ 1. CSR  │
    │    ▼    │     │    ▼    │     │    ▼    │
    │ 2. Cert │     │ 2. Cert │     │ 2. Cert │
    │    Issued│     │    Issued│     │    Issued│
    └────┬────┘     └────┬────┘     └────┬────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
              Trust Relationships:
         ┌────────────────────────────┐
         │                            │
         │  EP ◄──Mutual TLS──► GK   │
         │  EP ◄──Mutual TLS──► GW   │
         │  GK ◄──Mutual TLS──► GW   │
         │                            │
         └────────────────────────────┘

Certificate Validation Flow:
┌───────────────────────────────────────────────────────────┐
│  1. EP initiates connection                               │
│  2. EP presents certificate                               │
│  3. GK validates:                                         │
│     a. Certificate signed by trusted CA                   │
│     b. Certificate not expired                            │
│     c. SAN matches identity                               │
│     d. Check CRL/OCSP (not revoked)                       │
│  4. GK presents certificate                               │
│  5. EP validates GK certificate (same steps)              │
│  6. Mutual TLS established                                │
│  7. H.235 tokens exchanged (certificate-based)            │
└───────────────────────────────────────────────────────────┘

Revocation Checking:
    Device ──1. Check cert status──► CRL Server
           ◄─2. CRL response────────
           ──3. Alternative check──► OCSP Responder
           ◄─4. OCSP response───────

    If revoked or unreachable: FAIL CLOSED
```

## 9. Diagram Rendering Rules

### 9.1 Colors

- **Trusted Zone:** Green (#00FF00)
- **Semi‑Trusted Zone:** Yellow (#FFFF00)
- **Untrusted Zone:** Red (#FF0000)
- **Secure Signaling:** Blue (#0000FF) lines
- **Secure Media:** Purple (#800080) lines
- **Legacy Media:** Gray (#808080) lines

### 9.2 Shapes

- **Endpoints:** Rounded rectangles
- **Gatekeeper:** Hexagon
- **Gateway:** Double‑bordered rectangle
- **PKI:** Shield icon
- **Firewalls:** Brick wall icon
- **MCU:** Octagon
- **Switches:** Rectangle with grid pattern

### 9.3 Line Styles

- **Solid line** = signaling
- **Dashed line** = media
- **Double line** = encrypted
- **Single line** = unencrypted
- **Arrow** = direction of flow
- **Bidirectional arrow** = two-way communication

### 9.4 Font and Label Guidelines

- **Component labels:** Bold, 12pt
- **Security annotations:** Italic, 10pt, red for security requirements
- **Protocol labels:** Normal, 10pt, blue for secure protocols
- **Zone labels:** Bold, 14pt, colored per zone trust level

## 10. Compliance Requirements

A diagram is compliant when:

- ✅ All required components appear
- ✅ All trust boundaries are shown with clear demarcation
- ✅ All signaling and media flows are correctly labeled
- ✅ All H.235 protections are annotated
- ✅ All VLANs and firewalls are represented
- ✅ All PKI trust relationships are shown
- ✅ No ambiguous or missing flows exist
- ✅ Color coding follows specification
- ✅ Line styles indicate encryption status
- ✅ All security boundaries are explicitly marked

### Validation Checklist

- [ ] Logical architecture includes all zones
- [ ] Physical topology shows all VLANs
- [ ] Trust boundaries clearly delineated
- [ ] All signaling flows show H.235 protection
- [ ] Media flows distinguish SRTP from clear
- [ ] PKI relationships complete (enrollment + revocation)
- [ ] Gateway shown as crypto boundary
- [ ] Color coding consistent throughout
- [ ] All annotations present and accurate
- [ ] Diagram legend provided

---

## Related Documentation

- [Secure-H323-Zone-Standard-v1.0.md](./Secure-H323-Zone-Standard-v1.0.md) - Architecture requirements
- [Secure-H323-Implementation-Guide-v1.0.md](./Secure-H323-Implementation-Guide-v1.0.md) - Implementation details
- [Gateway-Interworking-Security-Profile-v1.0.md](./Gateway-Interworking-Security-Profile-v1.0.md) - Gateway specifications
- [H323-H235-Security-Test-Plan-v1.0.md](./H323-H235-Security-Test-Plan-v1.0.md) - Testing procedures
- [H323-H235-Compliance-Matrix-v1.0.md](./H323-H235-Compliance-Matrix-v1.0.md) - Compliance requirements

## Appendix: Diagram Tools and Formats

### Recommended Tools

- **Visio / Lucidchart:** For detailed network diagrams
- **Draw.io / diagrams.net:** For quick architecture diagrams
- **PlantUML:** For text-based sequence diagrams
- **ASCII/Text:** For documentation and version control
- **Network Notepad:** For physical topology

### Export Formats

- **PDF:** For documentation and presentations
- **PNG/SVG:** For web and reports
- **VSDX:** For Visio interchange
- **XML:** For tool-agnostic storage
- **ASCII:** For text-based version control

### Version Control

All diagrams should be:

- Version controlled (Git recommended)
- Reviewed during architecture changes
- Updated within 30 days of implementation changes
- Approved by security and architecture teams
