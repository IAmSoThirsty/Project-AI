# Verification Report

## Artifact

- Standard: `3.1.0-rc1`
- Manifest: `1.1.0-rc1`
- Source lifecycle: `draft_unratified`
- Ratified artifact: `thirstys-standard-v3q.ratified.manifest.yaml`, effective `2026-07-19`
- Verification environment: Python 3.13.5 on Linux x86_64
- CEL implementation: `cel-python==0.4.0`
- Recorded automated result: `23 passed`, `0 failed`, `0 errors`, `0 skipped`
- Current Project-AI workspace package result: `46 passed`; the recorded
  standalone result above remains historical artifact evidence.
- Current Project-AI checkout hygiene: **Passed locally** — the retired ignored
  `owner-private.json` is absent from the checkout after being moved into
  restricted off-repository custody. Independent key-retirement and custody
  proof remains unavailable, so the production pre-deployment gate remains
  fail-closed.

## Direct result

| Requested item | Result | Boundary |
|---|---|---|
| Runtime enforcement | **Verified — reference implementation** | The fail-closed gate blocks missing or invalid authority, unknown action classes, absent consequential-action approval, unknown-outcome retries, and revision drift. A denied action is not delivered to the executor. It is not yet integrated into Project-AI or another live execution host. |
| Common Expression Language execution | **Verified** | All eight unique manifest conditions compile and execute through `cel-python==0.4.0`; expected true and false outcomes are tested. |
| Independent evaluator behavior | **Verified — reference implementation** | The evaluator runs in a separate operating-system process, has a distinct identity and signing key, verifies the actor's signed execution record, independently checks CEL applicability and evidence, and signs its report. Production service isolation is not deployed. |
| Cryptographic authority authentication | **Verified — mechanism** | Ed25519 authority proofs are accepted only with a trusted active key, authorized purpose, valid signature, current validity period, matching action, and matching scope. Tampering, expiry, and scope violations are rejected. Replacement public key `owner-rotation-2026-07-19-01` is enrolled for ratification; private custody remains external. |
| Owner ratification | **Verified for exact artifact** | `owner-ratification.json` signs the exact `thirstys-standard-v3q.ratified.manifest.yaml` and `verify_ratification.py` passes against the replacement registry. This does not approve production deployment or prove external proof custody. |

## Evidence executed

### Manifest and schema integrity

- Strict YAML loading passed.
- Duplicate YAML keys are rejected.
- Manifest JSON Schema validation passed.
- Conformance-report JSON Schema validation passed.
- All supporting JSON Schemas passed schema validation.
- Identifier inventory passed: 53 unique rules, 112 unique controls, and 20 unique declared conformance tests.
- Every control test reference resolves.

### Runtime enforcement

The test suite proves:

- Missing authority fails closed.
- Denied actions do not reach the executor callback.
- Authenticated read-only actions can execute.
- Externally consequential actions require a separately signed approval proof.
- Unknown external outcomes cannot be retried blindly.
- Expected/current revision mismatch blocks the write.
- Known action types cannot be downgraded to a safer action class.
- Approval proofs are bound to action IDs and their nonces are consumed once execution begins.
- Executor exceptions are recorded as unknown outcomes rather than false failures or successes.

### CEL execution

The runtime compiled and executed these condition forms:

- `true`
- `task.response_shape == 'binary'`
- `task.requires_continuity == true`
- task-mode membership conditions
- task-risk membership conditions
- production-readiness claim condition
- governance claim condition

The tests include both positive and negative evaluations, not compilation alone.

### Independent evaluator

The integration test creates separate actor and evaluator Ed25519 keypairs, signs an execution record as the actor, launches the evaluator through a new process, and verifies that:

- evaluator identity differs from actor identity;
- evaluator process ID differs from actor process ID;
- actor record signature validates;
- required evidence is independently checked;
- an actor cannot mark an applicable control as not applicable;
- the declared actor key ID must match the cryptographically verified signing key;
- CEL applicability is independently executed;
- a schema-valid conformance report is emitted;
- the report signature validates against the evaluator key.

### Cryptographic authority

The tests verify:

- valid Ed25519 proof acceptance;
- modified signed content rejection;
- expired proof rejection;
- scope mismatch rejection;
- action restriction enforcement;
- separation of authority and approval signature purposes.

The release artifact contains no private owner key. The retired ignored
`owner-private.json` is absent from the current Project-AI checkout after being
moved into restricted off-repository custody; this report does not read or use
the retained file. The production pre-deployment gate remains fail-closed until
independent retirement and custody proof is available.

### Ratification mechanism

The mechanism test changes a manifest to ratified state in a temporary test workspace, signs a ratification record, verifies owner identity and signature, and binds the record to the exact manifest SHA-256. Modifying the manifest after signature causes verification failure.

The generated owner record now ratifies the exact release artifact. The source
manifest remains the draft input; the ratified artifact and replacement public
registry are the signed release evidence.

## Remaining deployment conditions after ratification

The local ratification requirement is now satisfied by:

1. Replacement key `owner-rotation-2026-07-19-01`, controlled outside the repository.
2. The corresponding public key enrolled in the trusted-key registry for the `ratification` purpose.
3. Effective date `2026-07-19`.
4. `owner-ratification.json` generated against the exact ratified manifest hash.
5. Successful execution of `tools/verify_ratification.py`.

Production deployment remains blocked until the retired local private file is
securely removed, external proof custody is recorded, and the remote successor
CI/signature/attestation, target-environment, overlay, backup, monitoring, and
rollback approvals are independently available.

## Integration limitation

The package now contains real enforcement code, but governance becomes live only when the host cannot bypass it. Every consequential tool call must pass through the gate, the trusted-key registry must be protected, and independent evaluator results must have operational consequence. Until that integration is demonstrated, the correct claim is **verified reference enforcement**, not **live system enforcement**.

## Evidence files

- `verification-evidence.json` — machine-readable result and test inventory.
- `pytest-junit.xml` — test-run evidence.
- `pytest-output.txt` — concise test output.
- `manifest-validation.txt` — manifest and identifier validation output.
- `report-validation.txt` — example report validation output.
- `cel-validation.txt` — CEL compilation output.
- `runtime-import-check.txt` — installed runtime and dependency import check.
- `SHA256SUMS` — release file checksums.
