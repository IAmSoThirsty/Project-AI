## 2. Architecture Overview

### 2.1 Core Components

- **Gatekeeper (GK):** Central policy engine for the zone, handles endpoint registration, call admission, address resolution, and bandwidth/security enforcement.
- **Gateways (GW):** Bridges the H.323 zone with external networks (PSTN, ISDN/H.320). Responsible for protocol, codec, signaling, and security boundary translation.
- **Endpoints (EP):** User devices—their signaling, authentication, and media handling must fully support H.323 and H.235.
- **MCU (Multipoint Control Unit):** Optional, hosts multi-party conferences securely within the zone.

### 2.2 Zone Model

A **zone** contains:
- All endpoints, gateways, MCUs
- ≥1 Gatekeeper (high-availability recommended)
- Gatekeepers are solely responsible for:
    - Address mapping (H.323 IDs, E.164 aliases)
    - Admission control (policy, authorization, CAC [Call Admission Control])
    - Security enforcement (H.235 profiles, PKI validation)
    - Bandwidth/resource management
- Gateways enforce security boundary between:
    - Secure IP (H.323) and TDM (H.320/ISDN/PSTN, etc.)
    - Interworking and codec translation
