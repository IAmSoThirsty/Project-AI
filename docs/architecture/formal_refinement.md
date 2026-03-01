# Formal Refinement Manifest: Requirements to Substrate

This manifest documents the **Refinement Path** from sovereign requirements through TARL policy to the OctoReflex implementation.

## 🔗 Traceability Matrix

| Requirement ID | Description | TARL Policy | Implementation Bridge | Verification |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-001** | Absolute User Sovereignty | `policy.sovereignty = STRICT` | `src/app/core/shadow_plane` | `sovereign_substrate.tla` |
| **REQ-002** | Reflexive Defense | `error.reflexive_halt = TRUE` | `octoreflex/octoreflex_manifest.thirsty` | `tests/test_reflex_halt` |
| **REQ-003** | Deterministic Audit | `audit.trail = SHA256_HASH` | `governance/audit_pipeline` | `cloud_wiring.tf` (Object Lock) |

## 📐 Formal Refined Layers

1. **L0 (Abstract)**: TLA+ High-Level Specification (`sovereign_substrate.tla`)
2. **L1 (Policy)**: TARL Governance Manifests (`governance/sovereign_runtime.thirsty`)
3. **L2 (Substrate)**: OctoReflex eBPF Containment (`octoreflex/`)
4. **L3 (Concrete)**: Python/Thirsty-Lang Implementation (`src/app/main.thirsty`)

> [!IMPORTANT]
> Any change to an L3 component must undergo a **Shadow Plane Verification** pass against L0 and L1 invariants before it is committed to the Primary Plane.
