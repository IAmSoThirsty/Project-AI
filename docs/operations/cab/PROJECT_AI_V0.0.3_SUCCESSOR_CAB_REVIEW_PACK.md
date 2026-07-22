# Project-AI v0.0.3 Successor CAB Review Pack

**Prepared:** 2026-07-20
**Repository:** `IAmSoThirsty/Project-AI`
**Candidate:** immutable successor code commit `eaed9905cacc02e2fb98e3cc92356e8d160e593e`; the active branch also contains gate-report and documentation follow-ups
**Decision:** **DEPLOYMENT NOT AUTHORIZED**

This is the current CAB entry point for the v0.0.3 successor. The candidate
is pushed and successor CI, vulnerability scanning, and image publication are
green in runs `29731671162`, `29731671150`, and `29731685685`. Independent
cosign v3.1.2 and raw OCI checks verify all eight digest-bound signatures; the
certificate identity is the unmerged agent branch, not an approved release ref.
No cosign SPDX/SLSA attestations are present (0/8). It is not a production
release: supply-chain proof custody, target approval, and deployment controls
remain unverified.

The active successor branch follow-up head `e5724025` also passed CI run
`29718283865` and vulnerability scan `29718283860`; those runs cover the
gate-report/documentation follow-ups and do not replace the immutable candidate
evidence above.

The remote default `master` currently resolves to `9fc3c93e6abd02a14bd141fab4d3ef772fa090bf`,
not this successor. Its active scheduled Codex Deus workflow is failing before
checkout because repository policy rejects unpinned actions such as
`actions/checkout@v4` and `actions/download-artifact@v4`.
The observed scheduled failures are runs `29709754498`, `29698528738`, and
`29686790959`.

## Local evidence

- Optional connected-service usage is now governed by
  `OPTIONAL_SERVICE_USAGE.json`: every named service is replaceable, activated
  explicitly, and prohibited from becoming a core or governance dependency.
  The tracked repository remains the canonical evidence and continuity source.

| Gate | Result |
|---|---|
| Python suite | `3482 passed, 5 skipped`; zero failures, warnings, XFAIL, or XPASS |
| Branch coverage | `87.32%` across eight batches; threshold `80%` |
| Canonical/frozen provenance | `5/5` replay; `2264/2264` frozen sections |
| Static/type gates | Ruff, format, canonical MyPy (`175` files), and strict Temporal/Waterfall-adapter MyPy pass |
| Workflow supply-chain pinning | All `103` local remote-action references use full commit SHAs |
| Compose | `9/9` local services healthy with security settings verified when Docker is available |
| Helm | Lint passes; production render verifies `47` manifests and eight digest-pinned images |
| Web/Rust/Android/Desktop | Local acceptance gates pass; release artifacts remain unsigned or working-tree evidence |
| Waterfall | Standalone `309` tests; copied Project-AI replay `313` tests, no warnings |
| Pre-deployment verifier | **Fail-closed** while independent successor evidence, approved ingress, and remote-backup configuration remain unresolved; owner-private checkout exclusion now passes |
| V3Q manifest review snapshot | `3ea08a2cf1244c4c0b4a9045aef4b5e5ac59ed9e82d7e03aa315d0d56fdcf09c` source hash; canonical ratified hash `15c8e4ba51dd4e3d0e562da670848d4c62e2ee98ac3983429aac8a3ff44db80f`; `owner-ratification.json` verifies the exact ratified artifact. Unsigned successor revision `1.2.0-rc1` (`1da097e1cb7773d296446aa651e9791cd005ca5d0159f0a3ff969b2b5f4b66f0`) supersedes it pending owner signature |
| Machine-readable successor evidence | `REMOTE_SUCCESSOR_EVIDENCE.json` has `status: missing`. Signatures for all eight digests are now independently verified (cosign v3.1.2, digest-pinned verifier image, plus a cosign-independent OCI referrers check); attestations remain genuinely absent and provenance is branch-scoped. Gate remains closed until release provenance, attestations, owner/proof custody, approved overlay, backup, monitoring-CRD, dependency, target-environment, and rollback fields are evidenced |

### Supply-chain correction — 2026-07-20

The earlier finding that "independent signature/attestation checks returned no registry
referrers" was **half right, and the signature half was wrong**.

- **Signatures exist and verify — 8/8.** The `no signatures found` result came from
  cosign v2.6.0, which reads only the legacy `sha256-<digest>.sig` tag. This pipeline
  runs cosign 3.x, which publishes a Sigstore bundle through the OCI 1.1 referrers
  mechanism; on ghcr.io that lands on a suffix-less `sha256-<digest>` fallback tag.
  Re-verified with cosign v3.1.2 from a digest-pinned image, with subject-digest binding
  confirmed for every image. **Verification requires cosign >= 3.0.**
- **Attestations were genuinely never produced.** `cosign attest` existed nowhere; the
  `publish-sbom` job was two `echo` statements behind `if: always()`. Confirmed absent
  0/8 for both `spdxjson` and `slsaprovenance`, and 404 via `gh attestation verify`.
- **New blocker — branch provenance.** All eight digests were signed from the unmerged
  branch `agent/production-readiness-2026-07-19` via `workflow_dispatch`, not from `main`
  or a release tag. The workflow's own identity pattern ended in `@.*$`, which accepts
  any ref, so it could not detect this.

Full evidence: `docs/operations/cab/EXTERNAL_AUDITOR_EVIDENCE_2026-07-20.md`, section
"Correction — 2026-07-20". Declared format: `tools/supply_chain_policy.json`.

Local evidence is necessary but is not production authorization.

For a complete current-state diagnostic, run
`uv run python tools/verify_pre_deployment.py --report`. The report evaluates
all gates and lists every blocker; it does not alter the strict fail-closed
deployment gate.

## Release-blocking conditions

- [ ] Retired `owner-primary` private material and affected local layers are
      securely retired through the approved custody process.
- [x] The exact final V3Q manifest is owner-ratified; replacement key
      `owner-rotation-2026-07-19-01` is enrolled; `verify_ratification.py` passes.
      The signed 1.1.0 artifact still contains embedded `pending_owner_signature`
      text and is preserved unchanged as historical evidence.
- [ ] The V3Q successor revision that removes the ratification contradiction is
      owner-signed. Revision `1.2.0-rc1` exists and is internally consistent, the
      preparation defect in `prepare_ratified_manifest()` is fixed and
      regression-tested, but the successor is **UNSIGNED**: the owner private key
      is off-repository and must not be handled by an agent. **Owner-blocked.**
- [ ] External proof issuance and custody are demonstrated for required-mode
      execution; the online runtime must not self-authorize.
- [x] The remediation is committed, pushed, and tested by successor CI and
      vulnerability scanning on immutable candidate `eaed9905`.
- [ ] The remote default-branch workflow failure is resolved or explicitly
      retired; candidate-branch CI is green, but default-branch workflow health
      remains an independent CAB review item.
- [x] All eight image digests have independently verifiable cosign **signatures**
      for candidate `eaed9905`. Re-verified 2026-07-20 with cosign v3.1.2 run from
      a digest-pinned OCI image, plus a cosign-independent OCI referrers layout
      check, with subject-digest binding confirmed for each. The earlier "no
      registry referrers" result was a cosign v2.6.0 format limitation.
      **Verification requires cosign >= 3.0.**
- [ ] All eight image digests have digest-bound SPDX/SLSA **attestations**.
      Confirmed absent 0/8 for both predicate types; `gh attestation verify`
      returns 404. The pipeline never produced them — `cosign attest` was absent
      and the `publish-sbom` job only ran `echo` statements. `cosign attest` is
      now implemented but has never executed. Attestations are created at build
      time and **cannot be applied retroactively to these digests**; a re-publish
      is required. **Owner decision.**
- [ ] The eight candidate digests carry **release provenance**. All eight were
      signed from the unmerged branch `agent/production-readiness-2026-07-19` via
      `workflow_dispatch`, not from `main` or a `v*` tag. Their certificate SAN
      binds to that branch ref. The workflow's identity pattern ended in `@.*$`,
      which accepts any ref, so its own verification could not detect this. A
      re-publish from an approved ref resolves this and the attestation gap
      together. **Owner decision.**
- [ ] Matching CodeQL/Checkov/Trivy and language dependency evidence is
      complete for the same immutable candidate.
- [ ] An approved production cluster, context, namespace, Helm release,
      maintenance window, implementer, rollback owner, approver, support owner,
      paging route, secret manager, and acceptance authority are recorded.
- [ ] Prometheus Operator CRDs are installed in the approved target; a
      server-side Helm dry run, deployment smoke, alert delivery, backup/restore,
      and rollback rehearsal pass there.
- [ ] Dependabot PRs #509 and #510 receive an owner-approved disposition.
      Their current check sets include the failing remote Codex Deus workflow;
      PR #510 also reports a CircleCI error.

## Independent auditor record

See [EXTERNAL_AUDITOR_EVIDENCE_2026-07-20.md](EXTERNAL_AUDITOR_EVIDENCE_2026-07-20.md)
for the exact registry commands and the discrepancy between the publish-job
claims and current externally observable signature/attestation state.

## Authoritative records

- [Pre-deployment checklist](../../deployment/PRE_DEPLOYMENT_CHECKLIST.md)
- [Release evidence bundle](RELEASE_EVIDENCE_BUNDLE.md) (historical v0.0.2
  record plus successor working-tree evidence)
- [V3Q owner-key rotation runbook](V3Q_OWNER_KEY_ROTATION.md)
- [Production deployment details](PRODUCTION_DEPLOYMENT_DETAILS.md)
- [Rollback runbook](ROLLBACK_RUNBOOK.md)
- [Continuity map](../CONTINUITY_MAP.md)

Until every unchecked condition is evidenced on the same immutable successor,
the CAB decision remains **do not deploy**.
