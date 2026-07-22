# External CAB/V3Q Audit Evidence — 2026-07-20

**Auditor:** `codex-external-auditor` (independent checkout and registry review)
**Scope:** Project-AI successor candidate `eaed9905cacc02e2fb98e3cc92356e8d160e593e`
**Repository:** `IAmSoThirsty/Project-AI`
**Decision:** **Do not deploy. Evidence remains incomplete.**

## Evidence independently confirmed

- GitHub repository access and branch identity were confirmed with the GitHub
  connector and `gh`; the successor branch points to the candidate commit.
- CI `29731671162`, vulnerability scan `29731671150`, and publish run
  `29731685685` completed successfully for the candidate commit.
- The publish job completed all eight image builds, SBOM/provenance build step,
  and its image-verification job.
- The V3Q owner-ratification record was independently checked with
  `verify_ratification.py`; the exact ratified manifest signature and hash
  verified successfully.
- The ratified manifest is internally inconsistent: its top-level status and
  implementation marker say `ratified`/verified, while embedded text and the
  embedded ratification object still say `pending_owner_signature`. The
  verifier passes, but the artifact should be re-issued and re-ratified before
  production use rather than silently editing the signed manifest.
- Docker Desktop was started and its Linux engine reached `running`. No
  production cluster, namespace, secret store, or remote backup target was
  inferred from that local engine.

## Registry re-check

The publish log records these candidate image digests:

| Image | Digest |
|---|---|
| api | `sha256:e878d233dd09535aa5b6356612eb0ecfd169bb98ebf751264284eec44276e502` |
| docs-portal | `sha256:c11615b6bbe65c01e93aaad30d7e0d46478425bbbd70f9b1ad8d4b95bb4e9deb` |
| proof-portal | `sha256:0924c2649b52674ffeb81a430f014b5fa557126daa058f315f159a6298f8566c` |
| operator-console | `sha256:2bb32bf3924cb425452945b5f64a86996f74fba488dbd36ada164b75a5f3dfdb` |
| swr | `sha256:092700a29793adc9def0f8743ea6dd18e4e758f1af441aea496f017b5947e4b3` |
| atlas | `sha256:b90a86b936caf26b0d87baf511fc47472ee563f35af73ac39560979a31eaf595` |
| arbiter-rlp | `sha256:b327cc7464e1370d3d129e29fee1266602a9e7711330efa5dc0f93e1c70af888` |
| genesis | `sha256:4507977282eea0ff48c36160b387ce3a3638676803b219b696ad6b0b51048ffb` |

Independent checks were run with cosign v2.6.0 after authenticating to GHCR:

```text
cosign verify <each image>@<recorded digest>
result: no signatures found (all eight images)
docker manifest inspect <digest>.sig
result: manifest unknown
docker manifest inspect <digest>.att
result: manifest unknown
gh attestation verify ... --bundle-from-oci
result: no attestations found in the OCI registry
```

This conflicts with the publish job's successful log output. The job log is
retained as owner/operator workflow evidence, but it is not promoted to
independent signature or attestation proof until a fresh registry verification
against the same immutable digests succeeds.

The checked-in publish workflow also states that Buildx SBOM and provenance
attestations are informational and are not independently cosign-signed. The
strict gate therefore correctly keeps both image-signature and SBOM-attestation
fields unresolved.

## Remaining CAB blockers

1. Independent cosign signatures and digest-bound SBOM/provenance attestations
   are not observable from the registry at audit time.
2. Secure retirement/custody of the former owner private key and external proof
   custody are not independently evidenced.
3. The signed V3Q artifact has contradictory embedded ratification status and
   needs a corrected, re-ratified manifest.
4. Production target, namespace, ingress/TLS overlay, secret source, owners,
   maintenance window, paging route, and acceptance authority remain TBD.
5. Remote backup/restore, Prometheus Operator CRDs and alert delivery, and
   rollback rehearsal remain unrun against an approved target.
6. Dependabot PRs #509 and #510 remain open with failing/cancelled checks; no
   owner-approved disposition is recorded in the independently inspected PR
   state.

Until those items are evidenced on the same immutable candidate, the V3Q/CAB
decision remains **do not deploy**.

---

## Correction — 2026-07-20, post-audit registry re-verification

**Everything above this line is preserved verbatim as the original audit record.**
The observations in it were correct for the tool the auditor used. One *conclusion*
drawn from them was not, and one finding was understated. Both are corrected here.

**The audit decision does not change: do not deploy.**

### Correction 1 — signatures DO exist; cosign 2.6.0 cannot read them

The "no signatures found" result was a **verifier format limitation**, not a missing
signature.

`.github/workflows/publish.yaml` pinned `sigstore/cosign-installer@6f9f177…` (v4.1.2),
which installs **cosign 3.x**. cosign 3 defaults to the **Sigstore bundle format**
published through the **OCI 1.1 referrers** mechanism. `ghcr.io` returns
`MANIFEST_UNKNOWN` for `/v2/<repo>/referrers/<digest>`, so cosign falls back to a
`sha256-<digest>` tag — **with no `.sig` suffix**. cosign 2.6.0 looks only for the
legacy `sha256-<digest>.sig` tag, which is intentionally never written under that
format. The auditor's `manifest unknown` for `<digest>.sig` and `<digest>.att` is the
**expected** result, not evidence of absence.

Re-verified 2026-07-20 against all eight digests with cosign **v3.1.2**, run from an
OCI image pinned by digest (`ghcr.io/sigstore/cosign/cosign@sha256:d91bc4e7e95e…`) —
deliberately a different distribution channel from the signer's GitHub-release tarball:

```text
cosign verify --certificate-identity-regexp <anchored> \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  ghcr.io/iamsothirsty/project-ai-<image>@<digest>
result: 8/8 verified
  - cosign claims validated
  - transparency-log existence verified offline
  - code-signing certificate verified against trusted CA
```

Confirmed independently of cosign by reading raw registry bytes over the plain OCI
distribution API and decoding the bundle with `openssl` (`tools/verify_supply_chain.py
--layer registry`, 8/8 pass):

| Property | Observed value |
|---|---|
| Referrer artifactType | `application/vnd.dev.sigstore.bundle.v0.3+json` |
| Bundle layer | sigstore bundle v0.3, DSSE envelope, 11 627 bytes (api) |
| DSSE payload type | `application/vnd.in-toto+json` |
| Statement subject digest | matches the image index digest for all eight |
| Signature predicate | `https://sigstore.dev/cosign/sign/v1` |
| Certificate issuer | `O=sigstore.dev, CN=sigstore-intermediate` |
| OIDC issuer (OID 1.3.6.1.4.1.57264.1.1) | `https://token.actions.githubusercontent.com` |
| Certificate validity | `2026-07-20T09:32:04Z` → `09:42:04Z` (10 min ephemeral) |
| Rekor transparency log | 1 entry, `logIndex 2205380115` |

The signatures are real, digest-bound, transparency-logged, and Fulcio-issued.

### Correction 2 — NEW FINDING: the signing identity is an unmerged agent branch

Not identified in the original audit. The certificate SAN for all eight digests is:

```text
URI:https://github.com/IAmSoThirsty/Project-AI/.github/workflows/publish.yaml
    @refs/heads/agent/production-readiness-2026-07-19
```

The eight production-candidate images were built and signed from an **unmerged working
branch** via `workflow_dispatch` (version `manual-20260720-eaed990`) — not from
`refs/heads/main` and not from a `refs/tags/v*` release tag.

The workflow's own verification used the identity pattern `…/publish\.yaml@.*$`. The
trailing `@.*$` accepts a signature issued to **any** git ref, so the pipeline could not
distinguish a reviewed release build from an arbitrary branch build. **These digests are
cryptographically valid but carry branch provenance, not release provenance.** This is
now a distinct release blocker.

### Correction 3 — attestations were genuinely never produced (audit understated)

The original audit was right that no attestations are retrievable, but the cause is worse
than "informational only":

- The `publish-sbom` job was named "Generate and attach SBOMs" and its **only** steps
  were two `echo` statements. It generated nothing and attached nothing, held
  `packages: write` for no reason, and `if: always()` kept it green even when every build
  job failed.
- `cosign attest` appeared **nowhere** in the repository. Neither did
  `actions/attest-build-provenance`.
- BuildKit `provenance: mode=max` + `sbom: true` do write a real attestation manifest into
  the image index (`vnd.docker.reference.type: attestation-manifest`) carrying in-toto
  layers with predicate types `https://spdx.dev/Document` and
  `https://slsa.dev/provenance/v1`. These are genuine but are neither cosign nor GitHub
  attestations, so no standard verifier reads them.

Re-confirmed 2026-07-20 with cosign v3.1.2 — **0/8 for both predicate types**:

```text
cosign verify-attestation --type spdxjson        → 0 verified, 8 absent
cosign verify-attestation --type slsaprovenance  → 0 verified, 8 absent
  Error: none of the attestations matched the predicate type: spdxjson,
         found: https://sigstore.dev/cosign/sign/v1
gh attestation verify oci://…@sha256:e878d233…   → HTTP 404 (no GitHub attestations)
```

### Why the workflow reported success without independently retrievable evidence

1. `verify-images` ran `cosign verify` with the **same cosign 3 binary that wrote the
   signature**, so a format/compatibility defect was structurally undetectable.
2. `verify-images` verified by **tag**, not by the digest that was signed, and carried
   `if: always()`.
3. `verify_publish_workflow()` substring-matched five strings, none signing-related —
   every cosign step could have been deleted without failing the gate.
4. `verify_remote_successor_evidence()` only checked that `signature_verifications` and
   `sbom_attestations` were **non-empty lists**. The entries that satisfied it literally
   read `"cosign v2.6.0 no signatures found"`.
5. No test anywhere executed cosign or asserted the signing steps existed.

### Blocker disposition after this correction

| # | Original blocker | Status now |
|---|---|---|
| 1 | Signatures and attestations not observable | **Split.** Signatures: **RESOLVED** — 8/8 independently verified. Attestations: **STILL OPEN** — genuinely never produced. |
| — | *(new)* Branch provenance | **OPEN** — the eight digests were signed from an unmerged agent branch. |
| 2 | Owner key retirement / proof custody | **OPEN** — unchanged. |
| 3 | Contradictory V3Q ratification status | **PARTIAL** — unsigned successor revision 1.2.0-rc1 created and the preparation defect fixed; ratification is owner-blocked, gate stays blocked. |
| 4 | Production target, ingress, secrets, owners, window, paging, acceptance | **OPEN** — unchanged. |
| 5 | Backup/restore, monitoring CRDs, rollback rehearsal | **OPEN** — unchanged. |
| 6 | Dependabot PRs #509 / #510 | **OPEN** — unchanged. |

### Owner decision required

Attestations are produced at **build time** and cannot be applied retroactively. The eight
recorded digests can therefore **never** satisfy the attestation requirement without a
re-publish. `sbom_attestations_verified` stays `false`. The owner must choose to either
re-publish under the corrected workflow from an approved ref — which also resolves the
branch-provenance blocker — or record an explicit accepted-gap decision.

A second open decision: this revision implements attestation via `cosign attest`. Using
`actions/attest-build-provenance` instead would be verifiable with `gh attestation verify`
— the exact command this audit ran — and would not depend on the referrers mechanism that
caused this incident. Recorded in `tools/supply_chain_policy.json` as a rejected
alternative rather than discarded silently.

**The V3Q/CAB decision remains: do not deploy.**
