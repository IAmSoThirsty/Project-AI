# Sovereign Compliance Evidence Pack: SOC2 / ISO 27001

This manifest provides a direct mapping of Project-AI's sovereign features to rigorous international security controls. This is **Regulator-Ready** evidence.

## 🛡️ Control Group 1: Logical Access (CC6.1 - CC6.3)

| Control ID | Project-AI Feature | Evidence File |
| :--- | :--- | :--- |
| **AC-1** | RBAC Enforcement via TARL | `governance/sovereign_runtime.thirsty` |
| **AC-2** | Ed25519-Signed Intent Verification | `api/openapi.json` (Security Schemes) |
| **AC-3** | Zero-Trust Network Isolation | `k8s/base/networkpolicy.yaml` |

## 📦 Control Group 2: System Operations (CC7.1 - CC7.5)

| Control ID | Project-AI Feature | Evidence File |
| :--- | :--- | :--- |
| **OP-1** | 7-Year Immutable Audit Stream | `terraform/cloud_wiring.tf` (Object Lock) |
| **OP-2** | Substrate-Level Integrity Verification | `octoreflex/octoreflex_manifest.thirsty` |
| **OP-3** | Automated Threat Detection | `terraform/cloud_wiring.tf` (GuardDuty) |

## 🧬 Control Group 3: Data Privacy & Sovereignty (CC8.1)

| Control ID | Project-AI Feature | Evidence File |
| :--- | :--- | :--- |
| **DP-1** | Total Telemetry Erasure | `PROJECT_STATUS.md` (Sovereign Laws) |
| **DP-2** | Sovereign Key Management | `terraform/cloud_wiring.tf` (KMS Key Rotation) |

## 🔍 Independent Audit Statement

> All Project-AI system transitions are anchored in the **Tier 0 Bedrock**, providing mathematical proof of execution versus policy alignment. This exceeds standard SOC2 requirements for "Point in Time" evidence and provides **Continuous Compliance Assurance**.
