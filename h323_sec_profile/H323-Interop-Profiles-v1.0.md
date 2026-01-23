# H.323 Interop Profiles

Version 1.0 — Interworking Standards & Compatibility Requirements (SIP, H.320, PSTN, Multi-Zone)

## 1. Purpose

Defines the interoperability profiles for secure H.323 deployments when interacting with:

- SIP networks
- H.320 (ISDN) systems
- PSTN voice networks
- Multi-zone H.323 environments

Each profile specifies signaling behavior, media handling, security expectations, and gateway requirements.

---

## 2. SIP Interop Profile

### 2.1 Signaling Mapping

| H.323 | SIP | Notes |
|-------|-----|-------|
| H.225 SETUP | SIP INVITE | Call initiation |
| H.225 CALL PROCEEDING | SIP 100 Trying | Progress indication |
| H.225 ALERTING | SIP 180 Ringing / 183 Session Progress | Early media support |
| H.225 CONNECT | SIP 200 OK | Call answered |
| H.225 RELEASE COMPLETE | SIP BYE | Call termination |
| H.245 | SDP offer/answer | Media negotiation |
| RAS (ARQ/ACF) | None | H.323 admission control only |

### 2.2 Media Mapping

**Preferred**:

- SRTP ↔ SRTP (AES-128 or better)
- Symmetric codec (G.711 ↔ G.711, G.729 ↔ G.729, H.264 ↔ H.264)

**Fallback** (only if explicitly allowed by policy):

- SRTP ↔ RTP (H.323 side remains encrypted, SIP side cleartext)
- Must be logged as security downgrade

**Prohibited**:

- RTP ↔ RTP (both sides cleartext)

### 2.3 Security Requirements

**SIP Trunk Security**:

- TLS 1.2+ for SIP signaling
- SRTP with AES-128-GCM or AES-256-GCM
- SDES or DTLS-SRTP key exchange
- Certificate-based authentication

**H.323 Side Security**:

- H.235.2/3/4/6 mandatory
- SRTP non-negotiable
- Fail-closed on security negotiation failure

**Gateway Behavior**:

- Act as crypto boundary if SIP side is RTP
- Log all SRTP ↔ RTP mappings
- Alert on SIP trunk downgrade attempts

### 2.4 Codec Mapping

| H.323 Codec | SIP Codec | Bitrate |
|-------------|-----------|---------|
| G.711 µ-law | G.711 µ-law (PCMU) | 64 kbps |
| G.711 A-law | G.711 A-law (PCMA) | 64 kbps |
| G.729 | G.729 | 8 kbps |
| G.722 | G.722 | 64 kbps |
| H.264 | H.264 | Variable |
| H.263 | H.263 | Variable |

**Transcoding** (if required):

- G.729 ↔ G.711 (quality loss acceptable)
- H.263 ↔ H.264 (requires hardware acceleration)

### 2.5 SIP-Specific Considerations

**SDP Handling**:
```
# H.323 H.245 OLC → SIP SDP
v=0
o=- 1234567890 1234567890 IN IP4 10.1.1.100
s=H323 to SIP Call
c=IN IP4 10.1.1.100
t=0 0
m=audio 16384 RTP/SAVP 0 18
a=rtpmap:0 PCMU/8000
a=rtpmap:18 G729/8000
a=crypto:1 AES_CM_128_HMAC_SHA1_80 inline:BASE64_KEY
```

**SIP Response Codes**:

- 200 OK → H.225 CONNECT
- 486 Busy Here → H.225 RELEASE COMPLETE (Cause: UserBusy)
- 488 Not Acceptable Here → H.225 RELEASE COMPLETE (Cause: IncompatibleDestination)
- 503 Service Unavailable → H.225 RELEASE COMPLETE (Cause: TemporaryFailure)

---

## 3. H.320 Interop Profile

### 3.1 Signaling Mapping

| H.323 | H.320 | Notes |
|-------|-------|-------|
| H.225/H.245 | H.221/H.230/H.242 | Protocol conversion at gateway |
| RAS | None | H.323 admission control only |
| Capability Exchange | Terminal Capability Set (TCS) | Codec negotiation |
| OLC | Logical Channel Signaling (LCS) | Channel establishment |

### 3.2 Media Mapping

**Audio**:

- SRTP (H.323) ↔ H.221 Multiplex (H.320)
- G.711 ↔ G.711 (preferred)
- G.722 ↔ G.722 (wideband audio)
- G.728 ↔ G.728 (low delay)

**Video**:

- SRTP H.264 (H.323) ↔ H.261 Multiplex (H.320)
- H.263 ↔ H.263 (if supported)
- Resolution mapping:
  - 1080p (H.323) → CIF/4CIF (H.320)
  - 720p (H.323) → CIF (H.320)

**Data**:

- T.120 passthrough where supported
- H.239 (dual stream) → H.281 (far-end camera control)

### 3.3 Security Requirements

**H.323 Side (IP)**:

- H.235.2/3/4/6 mandatory
- SRTP AES-128 or better
- PKI-based authentication

**H.320 Side (ISDN)**:

- Inherently cleartext (TDM circuit)
- Physical security of ISDN trunks
- No SRTP keys exposed to H.320 side

**Gateway Role**:

- **Cryptographic boundary**: Encrypts/decrypts at IP/ISDN interface
- Secure key storage (SRTP keys never leave gateway)
- Tamper-evident logging

### 3.4 H.320-Specific Considerations

**Bonding/Aggregation**:

- 128 kbps (2×64 kbps ISDN channels)
- 384 kbps (6×64 kbps)
- 768 kbps (12×64 kbps)

**H.221 Frame Structure**:

- Frame alignment signal (FAS)
- Bit-rate allocation signal (BAS)
- Audio, video, and data multiplexed in single bitstream

**Interworking Challenges**:

- H.320 does not support encryption
- Codec mismatches require transcoding
- Latency higher due to ISDN circuit switching

---

## 4. PSTN Interop Profile

### 4.1 Signaling Mapping

| H.323 | PSTN | Notes |
|-------|------|-------|
| H.225 SETUP | ISDN Q.931 SETUP | Call setup |
| H.225 ALERTING | Q.931 ALERTING | Ringing |
| H.225 CONNECT | Q.931 CONNECT | Call answered |
| H.225 RELEASE COMPLETE | Q.931 RELEASE COMPLETE | Call termination |
| H.245 | Bearer Capability | Codec negotiation limited |

### 4.2 Media Mapping

**Audio Only** (PSTN is voice-only):

- SRTP G.711 (H.323) ↔ PCM G.711 (PSTN)
- µ-law (North America, Japan)
- A-law (Europe, rest of world)

**No Video Support**: PSTN is audio-only

### 4.3 Security Requirements

**H.323 Side (IP)**:

- H.235.2/3/4/6 mandatory
- SRTP G.711 AES-128 or better

**PSTN Side (TDM)**:

- Cleartext PCM (64 kbps TDM)
- Physical security of trunk interfaces
- Carrier-grade facility security

**Gateway Role**:

- Cryptographic boundary (SRTP ↔ PCM)
- No SRTP key exposure
- Call Detail Records (CDRs) mandatory

### 4.4 PSTN-Specific Considerations

**Trunk Types**:

- Analog (FXO/FXS)
- Digital T1 (24 channels, µ-law)
- Digital E1 (30 channels, A-law)
- PRI (ISDN Primary Rate Interface)

**Signaling Protocols**:

- ISDN Q.931 (PRI)
- Loop start / Ground start (analog)
- Robbed-bit signaling (T1 CAS)

**Cause Codes** (ITU-T Q.850):

- Normal Call Clearing (16)
- User Busy (17)
- No Answer (19)
- Call Rejected (21)
- Number Changed (22)

**CDR Requirements**:
```json
{
  "call_id": "abc123",
  "start_time": "2026-01-23T10:00:00Z",
  "end_time": "2026-01-23T10:05:30Z",
  "duration_seconds": 330,
  "source": "ep-101",
  "destination": "+18005551234",
  "codec": "G.711u",
  "gateway": "gw-pstn-01",
  "trunk": "PRI-1",
  "cause_code": 16
}
```

---

## 5. Multi-Zone H.323 Interop Profile

### 5.1 Signaling

**LRQ/LCF Routing**:

- Location Request (LRQ): Query remote zone for E.164 number
- Location Confirm (LCF): Return routing information
- Location Reject (LRJ): Number not found

**Example**:
```
Zone A (GK-A):
  - Local endpoints: +1-408-xxx-xxxx
  - Remote query: +1-650-xxx-xxxx → LRQ to GK-B

Zone B (GK-B):
  - Local endpoints: +1-650-xxx-xxxx
  - LCF response: Route to ep-branch-office-101
```

**Gatekeeper-to-Gatekeeper Security**:

- TLS 1.2+ or IPsec for GK ↔ GK signaling
- Mutual certificate authentication
- H.235 tokens for inter-zone calls

### 5.2 Security

**Within Each Zone**:

- H.235.2 for RAS
- H.235.3 for H.225
- H.235.4 for H.245
- H.235.6 for SRTP media

**Between Zones**:

- TLS/IPsec tunnel for GK ↔ GK signaling
- SRTP end-to-end for media (if direct)
- Gateway transcoding only if zones have incompatible codecs

**Trust Model**:

- Each zone has independent PKI
- Cross-signed intermediate CAs (federated trust)
- Or shared root CA (centralized trust)

### 5.3 Media

**Direct Media Path** (preferred):
```
EP (Zone A) ←SRTP→ EP (Zone B)
```

**Hairpinned Media Path** (fallback):
```
EP (Zone A) ←SRTP→ GW-A ←SRTP→ GW-B ←SRTP→ EP (Zone B)
```

**Transcoding** (only if necessary):
```
EP (Zone A, H.264) → GW-A → GW-B → EP (Zone B, H.263)
```

### 5.4 Multi-Zone Routing Table Example

**GK-A Routing**:
```
+1-408-xxx-xxxx → Local zone
+1-650-xxx-xxxx → GK-B (Zone B)
+1-212-xxx-xxxx → GK-C (Zone C)
+1-800-xxx-xxxx → GW-A (PSTN)
```

**GK-B Routing**:
```
+1-650-xxx-xxxx → Local zone
+1-408-xxx-xxxx → GK-A (Zone A)
+1-800-xxx-xxxx → GW-B (PSTN)
```

### 5.5 Multi-Zone Failure Scenarios

**Scenario 1: Inter-Zone Link Failure**

- Zone A cannot reach Zone B
- Calls to Zone B fail
- Local calls within each zone continue

**Scenario 2: Gatekeeper Failure**

- GK-B fails
- Zone B endpoints re-register to GK-B standby
- Inter-zone routing restored

**Scenario 3: Media Path Blocked**

- Direct media path fails (firewall issue)
- Fallback to hairpinned path through gateways
- Call quality may degrade

---

## 6. Gateway Configuration Examples

### 6.1 SIP Interop Gateway

```
interface sip-trunk CARRIER-SIP
  destination sip.carrier.com:5061
  transport tls
  authentication digest
  username gateway01
  password ********
  
media-profile sip-srtp
  crypto AES_CM_128_HMAC_SHA1_80
  key-exchange sdes
  fallback-to-rtp deny

codec-profile sip-codecs
  audio G.711u priority 1
  audio G.729 priority 2
  video H.264 priority 1
```

### 6.2 H.320 Interop Gateway

```
interface h320-trunk ISDN-PRI-1
  type isdn-pri
  channels 23
  signaling h221
  bonding 384kbps

codec-profile h320-codecs
  audio G.711 priority 1
  video H.261 priority 1
  video H.263 priority 2

transcode h264-to-h261
  input H.264
  output H.261
  resolution CIF
```

### 6.3 PSTN Interop Gateway

```
interface pstn-trunk T1-1
  type t1-pri
  framing esf
  line-coding b8zs
  channels 24
  signaling isdn-pri

codec-profile pstn-codecs
  audio G.711u priority 1

cdr-export
  destination siem.example.com
  transport syslog-tls
  format json
```

### 6.4 Multi-Zone Gateway

```
zone-peering zone-b
  remote-gk gk-b.example.com
  transport tls
  mutual-auth required
  certificate /etc/certs/gw-a.pem
  
routing
  +1-650-xxx-xxxx → zone-b
  +1-408-xxx-xxxx → local
  +1-800-xxx-xxxx → pstn-trunk
```

---

## 7. Interop Testing Requirements

### 7.1 SIP Interop Tests

- [ ] TLS signaling established
- [ ] SRTP media established (H.323 ↔ SIP)
- [ ] Codec negotiation (G.711, G.729, H.264)
- [ ] Call hold/resume
- [ ] Call transfer
- [ ] DTMF relay (RFC 2833 or SIP INFO)

### 7.2 H.320 Interop Tests

- [ ] ISDN trunk connectivity
- [ ] H.221 multiplexing
- [ ] H.261/H.263 video transcoding
- [ ] Audio quality validation
- [ ] Bonding/aggregation (384 kbps, 768 kbps)

### 7.3 PSTN Interop Tests

- [ ] PRI trunk up
- [ ] Outbound calls (SRTP → PCM)
- [ ] Inbound calls (PCM → SRTP)
- [ ] DTMF detection
- [ ] Caller ID (ANI/DNIS)
- [ ] CDR generation

### 7.4 Multi-Zone Interop Tests

- [ ] LRQ/LCF routing
- [ ] TLS between GKs
- [ ] SRTP end-to-end
- [ ] Inter-zone call setup
- [ ] Gateway failover (if hairpinned)

---

## 8. Compliance Criteria

An interop profile is compliant when:

- All H.323 side security enforced (H.235.2/3/4/6)
- All media encrypted on H.323 side (SRTP)
- Gateway acts as secure crypto boundary
- No SRTP keys leaked to legacy side
- All signaling mappings correct
- All codec mappings validated
- All failure scenarios tested
- Logs exported to SIEM
- CDRs generated for all calls
