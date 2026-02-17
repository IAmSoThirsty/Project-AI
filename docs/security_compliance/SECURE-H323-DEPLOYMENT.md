## 12. Logging & Audit Schema

### 12.1 Gatekeeper Logging Requirements

The GK MUST log:

- All RAS events (GRQ/GCF, RRQ/RCF, ARQ/ACF, LRQ/LCF)
- All certificate validation events
- All admission decisions (allowed/denied)
- All endpoint registration changes
- All failover events

### 12.2 Gateway Logging Requirements

The GW MUST log:

- All H.225 call setup events
- All H.245 negotiation events
- All SRTP keying events
- All PSTN/ISDN signaling events (IAM, ACM, ANM, REL, CLR)
- All certificate validation events
- All codec negotiation outcomes

### 12.3 Endpoint Logging Requirements

Endpoints SHOULD log:

- Registration success/failure
- Certificate validation results
- Call setup attempts
- Media negotiation results
- SRTP status

### 12.4 Log Format & Retention

- Logs MUST include timestamp, device ID, event type, and outcome.
- Logs MUST be retained for a minimum of 12 months.
- Logs MUST be exportable in JSON or syslog format.
- Logs MUST be protected from tampering (WORM storage recommended).

## 13. Performance & Capacity Requirements

### 13.1 Gatekeeper Performance

- GK MUST support:
  - ≥ 5,000 concurrent registrations
  - ≥ 100 call setups per second
  - < 150 ms ARQ/ACF response time
- GK SHOULD support horizontal failover clustering.

### 13.2 Gateway Performance

- GW MUST support:
  - ≥ 500 concurrent calls (scalable by model)
  - SRTP encryption at line rate
  - < 200 ms call setup delay added by gateway
- GW SHOULD support DSP resource pooling for codec translation.

### 13.3 Endpoint Performance

- Endpoints MUST support:
  - SRTP AES‑128 at full media bandwidth
  - H.245 negotiation within < 300 ms
  - Jitter buffer adaptation for variable network conditions

### 13.4 Network Performance

- End‑to‑end latency target: < 150 ms one‑way
- Jitter target: < 30 ms
- Packet loss target: < 1%
- QoS markings:
  - SRTP: DSCP 46 (EF)
  - Signaling: DSCP 24 (CS3)

## 14. Reference Topology Diagram

```mermaid
graph TD
  subgraph Core VLAN
    GK[Gatekeeper]
  end
  subgraph Endpoint VLAN
    EP1[Endpoint-1]
    EPn[Endpoint-n]
    MCU[MCU (optional)]
  end
  subgraph Gateway DMZ
    GW[Gateway: IP / Legacy]
    ISDN[ISDN Switch]
    PSTN[PSTN]
  end
  GK <-->|RAS/H.225/H.245 (TLS/H.235)| EP1
  GK <-->|RAS/H.225/H.245 (TLS/H.235)| EPn
  GK <-->|RAS/H.225/H.245 (TLS/H.235)| GW
  EP1 <-->|SRTP| GW
  EPn <-->|SRTP| GW
  MCU <-->|SRTP| GW
  GW <-->|ISUP/Q.931, TDM| ISDN
  GW <-->|ISUP/(PSTN)| PSTN
```

## 15. References

- [ITU-T H.323](https://www.itu.int/rec/T-REC-H.323)
- [ITU-T H.235](https://www.itu.int/rec/T-REC-H.235)
- [RFC 3711: SRTP](https://datatracker.ietf.org/doc/html/rfc3711)
- [PKI Best Practices](https://www.rfc-editor.org/rfc/rfc3647)

______________________________________________________________________

*This specification provides a repeatable, auditable, production-ready blueprint for secure, interoperable H.323 enterprise deployments—including hardened gateway interworking, PKI security, and full H.235 protocol enforcement.*
