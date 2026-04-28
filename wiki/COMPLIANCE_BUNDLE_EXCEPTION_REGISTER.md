---
title: "Compliance Bundle Exception Register"
status: active
created: 2026-04-27
scope: compliance-bundle
author: GitHub Copilot
---

## Purpose

Track known compliance-bundle control exceptions with explicit risk, evidence, and closure criteria.

---

## Exceptions

### CB-EX-001 — Compliance bundle export is stage-coupled

- **Status:** Closed
- **Severity:** High
- **First observed:** 2026-04-27
- **Closed on:** 2026-04-27
- **Owner:** Governance / Runtime Engineering
- **Impacted controls:**
  - CB-001 Artifact completeness
  - CB-010 Independent attestation readiness
  - SOC2 CC7.2, SOC2 CC8.1, ISO 27001 A.12.4.1

#### Description

`compliance_bundle.json` generation was previously coupled to the `audit_export` pipeline stage.
This is now resolved by an execution-finalization contract that ensures bundle export for every successful Iron Path run.

#### Technical Evidence

1. **Resolution implementation**
   - `governance/iron_path.py`: added `_ensure_compliance_bundle()` and invoked it in `execute()` after successful stage execution.
   - `governance/sovereign_runtime.py`: `export_compliance_bundle(output_path)` remains the canonical export primitive.
2. **Regression lock**
   - `tests/test_iron_path.py`: added test `test_execute_exports_compliance_bundle_without_audit_stage`.
3. **Verification evidence**
   - Post-fix suite: `tests/test_sovereign_verifier.py tests/test_iron_path.py tests/test_iron_path_executor.py` => **44 passed, 0 failed**.
4. **Verifier robustness hardening**
   - `governance/sovereign_verifier.py`: signature authority mapping now separates verifiable vs unverifiable (truncated/redacted) evidence and only fails on true cryptographic verification failures.
   - `tests/test_sovereign_verifier.py`: added regression tests for unverifiable signature evidence accounting and invalid full-signature failure handling.

#### Risk

- **Operational risk:** compliance verification can be skipped unintentionally by pipeline composition.
- **Audit risk:** inconsistent evidence generation across runs.
- **Governance risk:** attestation availability is not guaranteed per run.

#### Temporary Compensating Control

Retired upon closure.

#### Closure Criteria

Exception is closed because all required criteria are satisfied:

1. Compliance bundle emission is guaranteed for governed runs by policy/contract (not optional by stage omission), **or**
2. Pipeline validation hard-fails if a run marked as compliance-required omits bundle export stage.
3. Verifier test suite passes for bundle availability assumptions.
4. Documentation updated with deterministic export contract.

#### Tracking Metadata

- **Decision type:** Control exception (temporary)
- **Escalation path:** Governance Lead -> Security/Compliance Lead
- **Review cadence:** Weekly until closed

---

## Change Log

- **2026-04-27:** Created register and opened CB-EX-001 based on Iron Path/verifier evidence.
- **2026-04-27:** Closed CB-EX-001 after implementing execution-finalization compliance bundle export and passing post-fix verification suites.
- **2026-04-27:** Added verifier hardening evidence and updated suite result count (44/44 passing).
