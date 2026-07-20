# Operational Continuity Map

## Current State

> Historical snapshot boundary: this copied continuity record predates the
> replacement owner key and exact-manifest ratification. The active continuity
> record is `packages/thirstys-standard-v3q/docs/operations/CONTINUITY_MAP.md`.

Thirsty's Standard V3 + Q now has a machine-readable manifest and an executable reference enforcement package. The release is `3.1.0-rc1` / manifest `1.1.0-rc1` and remains `draft_unratified`.

## Files Inspected

- `Thirsty's Standard v3.pdf`, Sections 1-41.
- Q hostile-gap review from the preceding conversation.
- The original manifest package, schemas, example report, validator, README, and continuity record.

## Files Created

- `pyproject.toml`
- `requirements.txt`
- `src/thirstys_standard_runtime/__init__.py`
- `src/thirstys_standard_runtime/strict_yaml.py`
- `src/thirstys_standard_runtime/canonical.py`
- `src/thirstys_standard_runtime/cel_runtime.py`
- `src/thirstys_standard_runtime/authority.py`
- `src/thirstys_standard_runtime/policy.py`
- `src/thirstys_standard_runtime/evaluator.py`
- `src/thirstys_standard_runtime/ratification.py`
- `src/thirstys_standard_runtime/cli.py`
- `schemas/authority-proof.schema.json`
- `schemas/action-request.schema.json`
- `schemas/execution-record.schema.json`
- `schemas/ratification-record.schema.json`
- `schemas/trusted-key-registry.schema.json`
- `tools/create_owner_key.py`
- `tools/ratify_manifest.py`
- `tools/verify_ratification.py`
- `tests/conftest.py`
- `tests/test_manifest_integrity.py`
- `tests/test_cel_runtime.py`
- `tests/test_authority.py`
- `tests/test_policy_engine.py`
- `tests/test_independent_evaluator.py`
- `tests/test_ratification_mechanism.py`
- `tests/test_schema_examples.py`
- `docs/verification/VERIFICATION_REPORT.md`
- `docs/verification/verification-evidence.json`
- `docs/verification/pytest-junit.xml`
- `SHA256SUMS`

## Files Modified

- `thirstys-standard-v3q.manifest.yaml`
- `thirstys-standard-manifest.schema.json`
- `conformance-report.schema.json`
- `conformance-report.example.yaml`
- `validate_manifest.py`
- `README.md`
- `docs/operations/CONTINUITY_MAP.md`

## Commands Run

- Installed and executed `cel-python==0.4.0`.
- Validated the manifest and report schemas.
- Compiled all eight unique CEL conditions.
- Executed the runtime, authority, evaluator, ratification, schema, and integrity test suite.
- Compiled Python sources and verified runtime module imports.
- Generated JUnit and machine-readable verification evidence.
- Generated SHA-256 checksums and rebuilt the release ZIP.

## Tests / Verification

- Strict YAML parse and duplicate-key rejection: passed.
- Manifest JSON Schema validation: passed.
- Example report JSON Schema validation: passed.
- Inventory: 53 rules, 112 controls, 20 declared adversarial tests, 8 unique CEL expressions.
- CEL compilation and semantic execution: passed.
- Fail-closed runtime action gate: passed.
- Denied action does not reach executor: passed.
- Consequential action requires separately signed approval: passed.
- Unknown outcome retry denial: passed.
- Revision drift denial: passed.
- Ed25519 signature acceptance: passed.
- Tamper rejection: passed.
- Expiry rejection: passed.
- Scope and action restriction: passed.
- Independent evaluator separate-process behavior: passed.
- Actor execution-record signature verification: passed.
- Evaluator report signature verification: passed.
- Evidence admissibility check: passed.
- Ratification signature and exact-manifest hash binding mechanism: passed.
- Recorded standalone automated suite: 23 passed. Current Project-AI workspace
  package suite: 46 passed, including owner-key rotation safety tests.
- Owner ratification of this release: not verified.
- Live Project-AI or agent-host integration: not verified because no target runtime was supplied.

## Completed Work

- Implemented runtime enforcement as a callable gate and executor wrapper.
- Implemented actual CEL evaluation using `cel-python` rather than a placeholder parser.
- Implemented independent evaluation with a distinct process, identity, and signing key.
- Implemented Ed25519 trust-key, authority proof, approval, actor-record, evaluator-report, and ratification verification.
- Implemented owner-controlled ratification tools without generating or storing an owner private key in the package.
- Updated the manifest's implementation status without falsely changing its lifecycle to ratified.

## Known Failures

None in the recorded automated verification run.

## Blockers

- Owner ratification requires Jeremy / Thirsty to create and control an Ed25519 private key and sign the exact release manifest.
- End-to-end enforcement in Project-AI requires a concrete execution boundary where every consequential tool call is routed through the gate.

## Risks

- A host application can bypass governance if it can invoke tools without the gate.
- Trusted-key registries and evaluator private keys require protected storage and revocation procedures.
- The schema URLs remain proposed URIs until published at a canonical location.
- The reference evaluator is logically separate in tests; production independence should use process or service isolation plus separate credentials and deployment control.

## Pending Work

- Owner key enrollment and ratification signature.
- Project-AI or agent-host integration.
- CI workflow that runs the verification suite on every manifest/runtime change.
- Canonical schema publication.
- Production key storage, rotation, revocation, and recovery policy.

## Next Recommended Action

Ratify only after reviewing the release. Then integrate `RuntimePolicyEngine.enforce()` at the single mandatory side-effect boundary and make a signed independent conformance report a release/deployment requirement.

## Safe to Continue

Yes. The package is safe to inspect and test. Do not claim the standard is ratified or live-enforced until the two blockers above are resolved.
