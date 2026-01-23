# H.323 Network Design Patterns
Version 1.0 — Reference Architectures (Campus, Multi-Site, Hybrid Cloud)

## 1. Purpose
Defines the standard network design patterns for deploying secure H.323 across different enterprise topologies, ensuring consistent security, performance, and operational excellence.

## 2. Design Pattern Overview

### 2.1 Pattern Selection Criteria
| Pattern | Best For | Endpoints | Sites | Complexity |
|---------|----------|-----------|-------|------------|
| Campus | Single location | 50-500 | 1 | Low |
| Multi-Site | Distributed enterprise | 500-5000 | 2-50 | Medium |
| Hybrid Cloud | Cloud-first organizations | 100-10000 | Any | High |

### 2.2 Common Requirements (All Patterns)
- H.235.2/3/4/6 enforcement
- PKI-based identity
- SRTP media encryption
- VLAN segmentation
- QoS enforcement
- SIEM integration
- Redundancy (N+1 minimum)

---

## 3. Campus Design Pattern

### 3.1 Characteristics
**Scope**: Single physical location (campus, building, data center)

**Scale**:
- 50-500 endpoints
- 1-2 Gatekeepers (active/standby)
- 1-2 Gateways (N+1 redundancy)
- Optional MCU
- Single PKI infrastructure

**Advantages**:
- Simple topology
- Low latency
- Centralized management
- Lower cost

**Challenges**:
- Single point of failure (site-level)
- Limited geographic diversity

### 3.2 Logical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Campus Network                          │
│                                                              │
│  ┌──────────────┐     ┌──────────────┐                     │
│  │ Endpoint     │     │ Endpoint     │                     │
│  │ VLAN 50      │     │ VLAN 50      │                     │
│  └──────┬───────┘     └──────┬───────┘                     │
│         │                     │                              │
│         └─────────┬───────────┘                              │
│                   │                                          │
│         ┌─────────▼──────────┐                              │
│         │  Core Switch       │                              │
│         │  VLAN Routing      │                              │
│         │  QoS Enforcement   │                              │
│         └─────────┬──────────┘                              │
│                   │                                          │
│         ┌─────────▼──────────┐                              │
│         │  Gatekeeper        │                              │
│         │  (Active/Standby)  │                              │
│         └─────────┬──────────┘                              │
│                   │                                          │
│         ┌─────────▼──────────┐                              │
│         │  DMZ Firewall      │                              │
│         └─────────┬──────────┘                              │
│                   │                                          │
│         ┌─────────▼──────────┐                              │
│         │  Gateway (DMZ)     │                              │
│         │  PSTN/H.320/SIP    │                              │
│         └─────────┬──────────┘                              │
│                   │                                          │
│                   ▼                                          │
│           Carrier/PSTN                                       │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 VLAN Design
- **VLAN 50**: Endpoint voice/video
- **VLAN 60**: H.323 control (GK, MCU)
- **VLAN 70**: DMZ (Gateway)
- **VLAN 80**: Management
- **VLAN 90**: PKI/Infrastructure

### 3.4 Firewall Rules

**Endpoint VLAN → Gatekeeper**:
```
allow udp 1719,1718     # RAS
allow tcp 1720          # H.225
allow tcp 11000-11999   # H.245 range
```

**Endpoint VLAN → Gateway**:
```
allow tcp 1720          # H.225
allow tcp 11000-11999   # H.245
allow udp 16384-32767   # SRTP media
```

**Gateway DMZ → Carrier**:
```
allow tcp 5060-5061     # SIP (if applicable)
allow udp 5004-5005     # RTP to carrier (if SIP)
allow isdn/pri          # PSTN trunks
```

### 3.5 QoS Configuration

**Core Switch**:
```
class-map voice
  match dscp ef
  priority 33%

class-map video
  match dscp af41
  bandwidth 50%

class-map signaling
  match dscp cs3
  bandwidth 10%
```

### 3.6 Redundancy Strategy
- **Gatekeeper**: Active/Standby with shared database
- **Gateway**: N+1 (two gateways, one hot spare)
- **Network**: Dual uplinks, HSRP/VRRP
- **PKI**: Redundant OCSP responders

### 3.7 Deployment Steps
1. Provision VLANs and routing
2. Configure firewall ACLs
3. Deploy primary Gatekeeper
4. Deploy standby Gatekeeper
5. Configure GK clustering
6. Deploy gateways in DMZ
7. Configure gateway trunks
8. Issue PKI certificates
9. Deploy endpoints
10. Validate secure call flows

---

## 4. Multi-Site Design Pattern

### 4.1 Characteristics
**Scope**: Multiple physical locations connected via WAN

**Scale**:
- 500-5000 endpoints
- 1-2 GKs per site
- 1-2 Gateways per site
- WAN interconnect (MPLS, SD-WAN, VPN)
- Distributed PKI (or centralized with high availability)

**Advantages**:
- Geographic diversity
- Local survivability
- Scalability
- Disaster recovery

**Challenges**:
- Inter-site routing complexity
- WAN bandwidth management
- Multi-zone coordination

### 4.2 Logical Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      Site A (HQ)                            │
│  ┌────────────┐                                             │
│  │ GK-A       │◄──────────┐                                │
│  │ (Primary)  │            │                                │
│  └────┬───────┘            │                                │
│       │                    │                                │
│  ┌────▼───────┐       ┌────▼─────┐                         │
│  │ EPs (Site A)│       │ GW-A     │                         │
│  └────────────┘       └────┬─────┘                         │
└─────────────────────────────┼─────────────────────────────┘
                              │
                         WAN (MPLS/SD-WAN)
                         TLS/IPsec Tunnel
                              │
┌─────────────────────────────┼─────────────────────────────┐
│                      Site B (Branch)                        │
│  ┌────────────┐            │                                │
│  │ GK-B       │◄───────────┘                                │
│  │ (Secondary)│                                             │
│  └────┬───────┘                                             │
│       │                                                     │
│  ┌────▼───────┐       ┌──────────┐                         │
│  │ EPs (Site B)│       │ GW-B     │                         │
│  └────────────┘       └──────────┘                         │
└────────────────────────────────────────────────────────────┘
```

### 4.3 Inter-Site Routing

**LRQ/LCF Routing**:
- Site A GK queries Site B GK for unknown E.164 numbers
- Site B GK responds with routing information
- Call established via direct media or hairpinned through gateway

**Routing Rules**:
```
# GK-A routing table
+1408xxxxxxx → GK-B (Site B)
+1650xxxxxxx → GK-A local
+1800xxxxxxx → GW-A (PSTN)
```

### 4.4 WAN Security

**IPsec Tunnel** (Gatekeeper ↔ Gatekeeper):
```
ike version 2
crypto ikev2 proposal H323-IKE
  encryption aes-256-gcm
  integrity sha384
  group 19

crypto ipsec transform-set H323-IPSEC
  esp-aes-256-gcm
  esp-sha384-hmac
```

**Or TLS** (Alternative):
```
tls version 1.3
cipher suite TLS_AES_256_GCM_SHA384
mutual authentication required
```

### 4.5 QoS for WAN

**Traffic Shaping**:
```
policy-map WAN-OUT
  class voice
    priority 1000 kbps
    police rate 1000 kbps
  class video
    bandwidth 5000 kbps
    random-detect dscp-based
  class signaling
    bandwidth 500 kbps
```

**DSCP Marking**:
- Voice (EF): Highest priority
- Video (AF41): Guaranteed bandwidth
- Signaling (CS3): Protected from drops

### 4.6 Local Survivability

**Site Isolation Scenario**:
- WAN link to Site B fails
- GK-B continues to service local endpoints
- Local calls within Site B remain operational
- External calls reroute via GW-B (local PSTN)

**Fallback Behavior**:
```
if (gk-primary unreachable):
    register_with(gk-local)
    use_local_gateway_for_external_calls()
```

### 4.7 Deployment Steps
1. Deploy Campus pattern at each site
2. Establish WAN connectivity (MPLS/VPN)
3. Configure GK-to-GK TLS/IPsec
4. Configure LRQ/LCF routing
5. Test inter-site calls
6. Test local survivability (WAN failure simulation)
7. Document dial plan and routing rules

---

## 5. Hybrid Cloud Design Pattern

### 5.1 Characteristics
**Scope**: On-premises H.323 + cloud-based services (SIP trunking, cloud MCU, hosted voice)

**Scale**:
- 100-10000 endpoints
- On-prem GK/GW
- Cloud SIP trunks
- Cloud MCU (optional)
- Hybrid PKI (on-prem + cloud CA)

**Advantages**:
- Cloud scalability
- Cost efficiency (cloud trunking)
- Disaster recovery (cloud failover)
- Global reach

**Challenges**:
- Internet dependency
- Latency variability
- Security boundary complexity
- Vendor lock-in risk

### 5.2 Logical Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   On-Premises Network                       │
│                                                             │
│  ┌────────────┐     ┌────────────┐                         │
│  │ Endpoints  │     │ Gatekeeper │                         │
│  │ (On-Prem)  │────►│ (On-Prem)  │                         │
│  └────────────┘     └────┬───────┘                         │
│                          │                                  │
│                     ┌────▼────────┐                         │
│                     │ SBC/Gateway │                         │
│                     │ (DMZ)       │                         │
│                     └────┬────────┘                         │
│                          │                                  │
└──────────────────────────┼─────────────────────────────────┘
                           │
                      Internet
                    (TLS/SRTP)
                           │
┌──────────────────────────┼─────────────────────────────────┐
│                      Cloud Services                         │
│                          │                                  │
│  ┌───────────────────────▼──────────────┐                  │
│  │  Cloud SIP Trunk Provider            │                  │
│  │  (TLS + SRTP Required)               │                  │
│  └───────────────────┬──────────────────┘                  │
│                      │                                      │
│  ┌───────────────────▼──────────────────┐                  │
│  │  Cloud MCU (Optional)                │                  │
│  │  (Secure WebRTC/H.323 Bridge)        │                  │
│  └──────────────────────────────────────┘                  │
└────────────────────────────────────────────────────────────┘
```

### 5.3 SBC/Gateway Requirements

**Security Functions**:
- TLS for SIP signaling to cloud
- SRTP for media to cloud
- Topology hiding (no internal IPs exposed)
- SIP header manipulation
- DDoS protection
- Rate limiting

**Configuration Example**:
```
sbc-profile CLOUD-SIP
  sip-tls enabled
  srtp mandatory
  topology-hiding enabled
  media-anchor enabled
  max-calls 1000
  ddos-protection enabled
```

### 5.4 Cloud SIP Trunk Security

**TLS Configuration**:
```
sip-trunk CLOUD-PROVIDER
  destination sip.cloud-provider.com:5061
  transport tls
  tls-version 1.2+
  cipher-suite TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
  mutual-auth required
  certificate /etc/certs/gateway.pem
  ca-bundle /etc/certs/cloud-provider-ca.pem
```

**SRTP Configuration**:
```
media-profile CLOUD-SRTP
  crypto-suite AES_CM_128_HMAC_SHA1_80
  key-exchange sdes
  fallback-to-rtp deny
```

### 5.5 Cloud MCU Integration

**Use Case**: Large-scale conferences, webinar hosting

**Security Requirements**:
- WebRTC ↔ H.323 secure transcoding
- SRTP end-to-end where possible
- Cloud MCU must not access SRTP keys from on-prem calls
- Audit logging to on-prem SIEM

**Architecture**:
```
On-Prem EP → GK → SBC → Cloud MCU (TLS/SRTP)
                             ↓
                      WebRTC Participants
```

### 5.6 Hybrid PKI Model

**Option 1: Federated Trust**
- On-prem CA for internal endpoints
- Cloud provider CA for cloud services
- Cross-signed intermediate CAs

**Option 2: Centralized Cloud PKI**
- Cloud-based CA (e.g., AWS Private CA)
- On-prem components request certs via API
- CRL/OCSP hosted in cloud with high availability

**Recommendation**: Option 1 (Federated) for maximum control

### 5.7 Internet Connectivity Requirements

**Bandwidth**:
- Voice: 100 kbps per concurrent call
- Video (720p): 1.5 Mbps per concurrent call
- Video (1080p): 3 Mbps per concurrent call
- Overhead: +20% for signaling, retransmissions

**Latency**:
- Target: <50 ms (excellent)
- Acceptable: <150 ms (good)
- Maximum: <300 ms (usable)

**Packet Loss**:
- Target: <0.1%
- Acceptable: <1%
- Maximum: <3%

### 5.8 Disaster Recovery Scenario

**On-Prem Failure**:
1. GK fails
2. Endpoints failover to cloud-based registration service
3. Calls route via cloud SIP trunks
4. Internal calls use cloud MCU as bridge

**Cloud Failure**:
1. Cloud SIP trunk fails
2. Calls failover to on-prem PSTN gateway
3. On-prem MCU handles conferences

### 5.9 Deployment Steps
1. Deploy Campus or Multi-Site pattern on-prem
2. Provision cloud SIP trunk account
3. Configure SBC/Gateway for cloud connectivity
4. Establish TLS/SRTP to cloud
5. Configure PKI (federated or centralized)
6. Test cloud call flows (inbound/outbound)
7. Test failover scenarios (on-prem ↔ cloud)
8. Configure cloud MCU (if used)
9. Integrate cloud logs with on-prem SIEM

---

## 6. Design Pattern Comparison

| Feature | Campus | Multi-Site | Hybrid Cloud |
|---------|--------|------------|--------------|
| **Complexity** | Low | Medium | High |
| **Cost** | Low | Medium | Variable |
| **Scalability** | 50-500 EPs | 500-5000 EPs | 100-10000+ EPs |
| **Geographic Diversity** | None | High | Highest |
| **Cloud Integration** | None | Optional | Native |
| **Disaster Recovery** | Limited | Good | Excellent |
| **Internet Dependency** | None | Low | High |
| **Management Overhead** | Low | Medium | High |

---

## 7. Common Design Principles (All Patterns)

### 7.1 Security-First
- H.235.2/3/4/6 non-negotiable
- PKI mandatory
- Fail-closed on security failures
- Defense in depth (firewalls, VLANs, encryption)

### 7.2 High Availability
- N+1 redundancy minimum
- Active/standby Gatekeepers
- Redundant gateways
- Dual WAN links (multi-site, hybrid cloud)

### 7.3 Performance
- QoS enforcement everywhere
- Media path optimization (direct when secure)
- Codec selection based on bandwidth
- Latency/jitter monitoring

### 7.4 Observability
- SIEM integration
- Real-time dashboards
- Proactive alerting
- CDR collection and analysis

### 7.5 Compliance
- Regular security audits
- Certificate lifecycle management
- Configuration baselines
- Change control

---

## 8. Migration Strategies

### 8.1 Legacy H.323 → Secure H.323
1. Audit existing deployment
2. Issue PKI certificates
3. Enable H.235 in phases (zone-by-zone)
4. Enforce SRTP
5. Decommission insecure endpoints

### 8.2 SIP → H.323 (Hybrid)
1. Deploy H.323 GK/GW alongside SIP infrastructure
2. Configure SIP ↔ H.323 gateway
3. Migrate endpoints in phases
4. Maintain dual-stack during transition

### 8.3 On-Prem → Hybrid Cloud
1. Deploy SBC for cloud connectivity
2. Provision cloud SIP trunk
3. Route selected calls via cloud
4. Migrate endpoints to cloud registration (optional)
5. Decommission on-prem gateways (if desired)

---

## 9. Completion Criteria

A design is considered production-ready when:
- All H.235 profiles enforced
- All media is SRTP
- Redundancy validated (failover tests)
- QoS configured and tested
- SIEM integration verified
- Disaster recovery tested
- Documentation complete
- Operational runbook delivered
