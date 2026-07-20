# V3Q Owner-Key Rotation and Ratification Gate

## Current execution state

- Replacement key ID: `owner-rotation-2026-07-19-01`.
- Replacement public key is enrolled in `packages/thirstys-standard-v3q/trusted-keys.json`.
- Exact-manifest ratification is recorded in
  `packages/thirstys-standard-v3q/owner-ratification.json`; independent
  verification passed.
- The retired ignored `packages/thirstys-standard-v3q/owner-private.json`
  remains in the local checkout and must be securely retired before the
  pre-deployment gate can pass.

**Status:** Required before any production deployment or V3Q owner-key use.

## Incident boundary

The ignored file
`packages/thirstys-standard-v3q/owner-private.json` entered at least one local
API image because the root Docker build context copied `packages/` without
excluding that file. The root `.dockerignore` now excludes the exact path, the
pre-deployment verifier enforces that exclusion, and a clean rebuilt image plus
the running API both report the file absent.

The prior `owner-primary` key must nevertheless be treated as compromised. Do
not use it for authority, approval, execution records, or manifest
ratification. Do not paste, print, hash, upload, or attach its private material
to the change record.

## Owner-controlled rotation

These steps require Jeremy / Thirsty or an explicitly authorized key custodian.
The repository agent must not self-ratify the standard.

1. Select an approved off-repository, offline signing location. Do not provision
   the owner private key to the API, a pod, a container image, or a cluster Secret.
2. Generate a replacement key with a new key ID, writing the private half only
   to the approved off-repository location and the public half to a reviewable
   temporary file:

   From PowerShell, first enter the repository and replace the values in the
   variables with real paths. Do not type angle-bracket placeholders literally:

   ```powershell
   Set-Location 'T:\00-Active\Project-AI-Beginnings'
   $secureDir = Join-Path $env:USERPROFILE 'Documents\Project-AI-Secrets'
   New-Item -ItemType Directory -Path $secureDir -Force | Out-Null
   $privateOut = Join-Path $secureDir 'owner-private.json'
   $publicOut = Join-Path $secureDir 'owner-public.json'
   $keyId = 'owner-rotation-YYYY-MM-DD-01'

   uv run python .\packages\thirstys-standard-v3q\tools\create_owner_key.py `
     --key-id $keyId `
     --private-out $privateOut `
     --public-out $publicOut
   ```

   If the private output already exists, stop and use a new approved output
   path or the owner's documented rotation procedure; do not overwrite a key
   without explicit custody approval.

   ```powershell
   uv run python packages/thirstys-standard-v3q/tools/create_owner_key.py `
     --key-id owner-<ROTATION-ID> `
     --private-out <APPROVED-OFF-REPO-PATH> `
     --public-out <REVIEWABLE-PUBLIC-KEY-PATH>
   ```

   The tool now requires an explicit replacement key ID and rejects the
   retired `owner-primary` identifier. It also refuses to write private
   material anywhere under the repository checkout.

3. Replace `owner-primary` in
   `packages/thirstys-standard-v3q/trusted-keys.json` with the reviewed public
   document. Record the new key ID and rotation date, never the private value.
4. Store the private document in the approved offline signing system. The online
   runtime receives only the reviewed public registry and externally signed,
   narrowly scoped authority/approval documents.
5. After reviewing the exact V3Q manifest, intentionally create the ratified
   manifest and owner record:

   ```powershell
   uv run python packages/thirstys-standard-v3q/tools/ratify_manifest.py `
     --manifest packages/thirstys-standard-v3q/thirstys-standard-v3q.manifest.yaml `
     --owner-private-key <APPROVED-OFF-REPO-PATH> `
     --effective-date <YYYY-MM-DD> `
     --output-manifest packages/thirstys-standard-v3q/thirstys-standard-v3q.ratified.manifest.yaml `
     --output-record packages/thirstys-standard-v3q/owner-ratification.json

   uv run python packages/thirstys-standard-v3q/tools/verify_ratification.py `
     --manifest packages/thirstys-standard-v3q/thirstys-standard-v3q.ratified.manifest.yaml `
     --record packages/thirstys-standard-v3q/owner-ratification.json `
     --registry packages/thirstys-standard-v3q/trusted-keys.json
   ```

6. Run a production-equivalent startup with `THIRSTYS_V3Q_REQUIRED=true`, then
   prove an invalid public registry prevents startup, missing authority denies,
   and `require_approval` never reaches the executor without valid external approval.
7. Retire the old private file and affected local image/layers using the
   owner's approved secure-destruction process. This repository change does not
   delete either automatically.
8. After the owner and external records are independently reviewed, update
   `REMOTE_SUCCESSOR_EVIDENCE.json` with the record references
   `owner_key_rotation_record`, `exact_manifest_ratification_record`, and
   `proof_custody_record`, and set the matching required booleans to `true`.
   Do not set `status` to `verified` until the remote commit, CI, image,
   target-environment, and rollback records are present as well.

## Required evidence

- new public key ID and reviewed registry diff;
- offline signing-system identity, custody/access policy, and rotation time;
- ratified manifest and owner record;
- successful `verify_ratification.py` output;
- required-mode positive and negative startup evidence;
- owner confirmation that the old key and affected local layers were retired.
- machine evidence record updated with the three owner/proof custody record
  references and independently reviewed before any status transition.
