# Thirsty's Standard V3 + Q Machine-Readable Enforcement Package

## Status

**Standard:** `3.1.0-rc1`  
**Manifest:** `1.1.0-rc1`  
**Lifecycle:** `draft_unratified`  
**Reference runtime enforcement:** implemented and verified  
**Common Expression Language execution:** implemented and verified  
**Independent evaluator:** implemented and verified  
**Ed25519 authority authentication:** implemented and verified  
**Owner ratification:** pending owner-controlled cryptographic signature

> This package is reference implementation evidence, not current deployment
> approval. The Project-AI successor remains fail-closed until owner rotation,
> exact-manifest ratification, external proof custody, and remote evidence are
> independently verified.

The verification claims above apply to the included reference implementation and automated test environment. They do not claim that the gate is already wired into Project-AI, an agent host, CI, deployment infrastructure, or every external tool path.

## What is now executable

The package includes:

- A fail-closed runtime action gate.
- CEL compilation and execution for every unique `applies_when` expression in the manifest.
- Ed25519-signed authority, approval, execution-record, evaluator-report, and ratification documents.
- Scope, action, expiry, trust-key, tamper, retry, and revision-drift checks.
- An independent evaluator that executes in a separate process, verifies the actor's signed record, checks evidence admissibility, independently executes CEL applicability, and signs its report with a distinct evaluator key.
- Strict YAML parsing that rejects duplicate keys.
- JSON Schemas for authority proofs, action requests, execution records, trusted key registries, conformance reports, and owner ratification records.
- Owner ratification tooling that binds a signature to the exact manifest SHA-256, version, effective date, and ratification statement.

## Install

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Verify the release

```bash
python validate_manifest.py thirstys-standard-v3q.manifest.yaml
python validate_manifest.py conformance-report.example.yaml
python -m thirstys_standard_runtime.cli cel-verify thirstys-standard-v3q.manifest.yaml
pytest -q tests
```

Recorded standalone artifact test status:

```text
23 passed
```

The current Project-AI workspace suite contains 46 V3Q package tests, including
the owner-key rotation safety tests. The recorded 23-test result remains the
original standalone artifact evidence and does not establish owner ratification.

The recorded evidence is in:

- `docs/verification/VERIFICATION_REPORT.md`
- `docs/verification/verification-evidence.json`
- `docs/verification/pytest-junit.xml`
- `SHA256SUMS`

## Runtime gate

The gate takes a task, action request, signed authority proof, and when required a separately signed approval proof. Unknown authority, unknown action classes, invalid signatures, expired proof, scope mismatch, unknown external outcomes, and revision drift fail closed.

```bash
thirstys-standard gate \
  --manifest thirstys-standard-v3q.manifest.yaml \
  --registry trusted-keys.json \
  --task task.json \
  --action action.json \
  --authority authority-proof.json \
  --approval action-approval.json
```

A denied action is not passed to the executor callback in the reference engine.

## Independent evaluation

```bash
thirstys-standard evaluate \
  --manifest thirstys-standard-v3q.manifest.yaml \
  --record signed-execution-record.json \
  --registry trusted-keys.json \
  --evaluator-identity evaluator-identity.json \
  --evaluator-private-key /secure/path/evaluator-private.json \
  --output signed-conformance-report.json
```

The evaluator refuses to certify an actor with the same identity or process and signs the report with a separate trust key.

## Owner ratification

Owner ratification is deliberately not self-issued by the package or by the AI that created it. Jeremy / Thirsty must control the private key and intentionally sign the exact release.

Create the key outside the repository:

```bash
python tools/create_owner_key.py \
  --key-id owner-<ROTATION-ID> \
  --private-out /secure/off-repo/owner-private.json \
  --public-out owner-public.json
```

Add the public key to a trusted-key registry. Never place the private key in this package, Git, chat, email, continuity records, or logs.

Ratify the exact manifest:

```bash
python tools/ratify_manifest.py \
  --manifest thirstys-standard-v3q.manifest.yaml \
  --owner-private-key /secure/off-repo/owner-private.json \
  --effective-date YYYY-MM-DD \
  --output-manifest thirstys-standard-v3q.ratified.manifest.yaml \
  --output-record owner-ratification.json
```

Verify it:

```bash
python tools/verify_ratification.py \
  --manifest thirstys-standard-v3q.ratified.manifest.yaml \
  --record owner-ratification.json \
  --registry trusted-keys.json
```

Until that succeeds with an owner-controlled key, the standard remains `draft_unratified`.

## Core files

- `thirstys-standard-v3q.manifest.yaml` - authoritative V3 + Q manifest.
- `thirstys-standard-manifest.schema.json` - manifest JSON Schema.
- `src/thirstys_standard_runtime/` - executable CEL, authority, gate, evaluation, and ratification runtime.
- `conformance-report.schema.json` - signed independent report contract.
- `schemas/` - supporting cryptographic and execution schemas.
- `tests/` - adversarial and integration verification tests.
- `docs/operations/CONTINUITY_MAP.md` - durable work state.

## Remaining integration boundary

The reference gate must still be placed in front of the actual side-effect executor in the target agent or Project-AI runtime. A caller that bypasses the gate is not governed by it. Integration therefore requires routing all consequential execution through this gate, protecting the trusted-key registry, isolating evaluator keys, and making evaluator results consequential.
