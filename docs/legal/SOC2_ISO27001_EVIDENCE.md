# Sovereign SOC2/ISO27001 Evidence Pack & Control Mapping

**Version**: 1.0.0-EVIDENCE
**Status**: GENERATED (Cryptographically Authenticated)

## 1. Access Control (CC6.x / ISO 27001:2013 A.9)

- **Control**: Access to production environments is restricted and audited.
- **Project-AI Implementation**: Enforced via **Kyverno Admission Controller** (`sovereign_policy.yaml`). All image signatures are verified against the Sovereign Master Key. Manual shell access is blocked by policy.
- **Evidence**: [sovereign_policy.yaml](file:///c:/Users/Quencher/.gemini/antigravity/scratch/sovereign-repos/Project-AI/k8s/base/sovereign_policy.yaml)

## 2. Integrity & Monitoring (CC7.x / ISO 27001:2013 A.12)

- **Control**: System changes are detected and authorized.
- **Project-AI Implementation**: **Shadow Thirst Dual-Plane Verification** monitors every sensitive state transition. Divergence results in an immediate reflexive halt.
- **Evidence**: [security_proof_protocol_reasoning.md](file:///c:/Users/Quencher/.gemini/antigravity/scratch/sovereign-repos/Project-AI/docs/formal/security_proof_protocol_reasoning.md)

## 3. Data Retention & Disposal (CC1.x / ISO 27001:2013 A.8)

- **Control**: Data is retained and disposed of according to policy.
- **Project-AI Implementation**: **AWS S3 Object Lock (Compliance Mode)** enforces a 7-year non-erasable retention period for audit logs.
- **Evidence**: [cloud_wiring.tf](file:///c:/Users/Quencher/.gemini/antigravity/scratch/sovereign-repos/Project-AI/terraform/cloud_wiring.tf)

## 4. Cryptographic Protection (ISO 27001:2013 A.18)

- **Control**: Cryptographic controls are used to protect information.
- **Project-AI Implementation**: **Thirsty-Lang CryptoAgilityManager** governs algorithm rotation. All events are signed with Ed25519.
- **Evidence**: [crypto_agility.thirsty](file:///c:/Users/Quencher/.gemini/antigravity/scratch/sovereign-repos/Project-AI/src/app/core/crypto_agility.thirsty)
