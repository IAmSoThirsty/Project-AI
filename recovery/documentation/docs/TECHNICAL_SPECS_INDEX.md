<!--                                         [2026-03-04 09:48] -->
<!--                                        Productivity: Active -->


# Project-AI: Technical Specifications Index



## For Engineers Only: The Concrete Directory

---



## 🔧 1. Kernel & Substrate (OctoReflex)

| Component | Primary Source | Specification Doc |
| :--- | :--- | :--- |
| **OctoReflex eBPF** | [octoreflex/](../octoreflex/) | [OCTOREFLEX_SPEC.md](architecture/OCTOREFLEX_SPEC.md) |
| **Hardware Isolation** | [tarl_os/kernel/](../tarl_os/kernel/) | [HARDWARE_ISOLATION.md](architecture/HARDWARE_ISOLATION.md) |
| **Legion Bridge** | [verify_legion_bridge.py](../verify_legion_bridge.py) | [LEGION_BRIDGE_PROTOCOL.md](architecture/LEGION_BRIDGE_PROTOCOL.md) |



## 🛡️ 2. Security & Enforcement (T.A.R.L.)

| Protocol | Primary Source | Core Specs |
| :--- | :--- | :--- |
| **Asymmetric Engine** | [asymmetric_security_engine.py](../src/app/core/asymmetric_security_engine.py) | [THIRSTYS_SECURITY_COMPLETE.md](internal/archive/root-summaries/THIRSTYS_SECURITY_COMPLETE.md) |
| **Enforcement Gateway** | [asymmetric_enforcement_gateway.py](../src/app/security/asymmetric_enforcement_gateway.py) | [GATEWAY_SPEC.md](security_compliance/GATEWAY_SPEC.md) |
| **T-SECA / GHOST** | [tseca_ghost_protocol.py](../src/app/security/tseca_ghost_protocol.py) | [IMPLEMENTATION_SUMMARY.md](internal/archive/root-summaries/IMPLEMENTATION_SUMMARY.md) |



## 💎 3. Language & Grammar (TSCG)

| Feature | Implementation | Documentation |
| :--- | :--- | :--- |
| **Compiler IR** | [src/shadow_thirst/](../src/shadow_thirst/) | [SHADOW_THIRST_IR.md](architecture/SHADOW_THIRST_IR.md) |
| **Symbolic Grammar** | [build.tarl](../build.tarl) | [TSCG_SPEC.md](architecture/TSCG_SPEC.md) |
| **Binary Encoding** | [TSCG-B (v1.0)](https://doi.org/10.5281/zenodo.18826409) | [TSCG_B_SPECIFICATION_v1.0.md](spec/TSCG_B_SPECIFICATION_v1.0.md) |
| **Active Resistance** | [tarl_os/](../tarl_os/) | [TARL_ARCHITECTURE.md](architecture/TARL_ARCHITECTURE.md) |



## 🖥️ 4. Application & Interface

| UI Layer | Repository Location | Tech Stack |
| :--- | :--- | :--- |
| **Desktop UI** | [desktop/](../desktop/) | PyQt6 (Leather Book Aesthetics) |
| **Web UI** | [web/](../web/) | React / p5.js (Renaissance Movement) |
| **CLI Tools** | [scripts/](../scripts/) | Python 3.12+ |

---



## 🧪 5. Verification & Proofs

* **Sovereign Verification**: [verification_report.md](verification_report.md)
* **Unit Tests**: `pytest /tests/`
* **Security Validation**: `python validate_thirstys_security.py`

---
*EOF: Integrity Signal Verified.*
