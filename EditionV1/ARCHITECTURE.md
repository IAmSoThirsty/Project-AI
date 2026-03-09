Edition V1 Architecture Overview

- Central Monolith: All core components integrated into a single process to enable rapid iteration and governance enforcement.
- Governance Layer: Triumvirate-like governance (Galahad, Cerberus, Codex) with Sovereign Runtime enabling cryptographic commitments, policy bindings, and audit trails.
- Language Stack: Thirsty-Lang (orchestrator) + Shadow Thirst (dual-plane verification) + TSCG/TSCG-B encoding; TARL OS as security/runtime surface; OctoReflex kernel containment as optional infrastructure.
- End-to-End Sovereignty: Iron Path demonstrates a seven-stage cryptographic pipeline to produce a signed compliance bundle.
- Ambassador Surface: Public-facing surface that exposes a safe and auditable interface for public use; CTS posture supports production-level scale.
- Data & Identity: Config snapshots bound to policy state, role signatures, and hash-chain audit trails; identity management and access control integrated with governance.
- Risk Controls: Explicit handling of heavy subsystems (Unity, heavy Web assets) via phased gating and build-time toggles.

Data Flows (high level)

- Public request -> Ambassador Surface -> Governance Gate -> Execution Kernel -> Audit Trail -> Compliance Bundle Export
- On governance failure: halt, log, escalate per constitutional rules.
- Iron Path: data preparation -> model/artifact -> agent chain -> promotion -> rollback -> audit export -> verification
- Multi-Tenant CTS-5 Readiness
- Edition V1 is CTS-5 capable: it includes per-tenant governance, tenant isolation, and API key based surface, with a tenant-aware audit trail and cross-tenant policy bindings. This enables federation planning and incremental rollouts while maintaining a solid base for a public surface.
