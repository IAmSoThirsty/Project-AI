# Project-AI v0.0.3 Successor CAB Review Pack

**Prepared:** 2026-07-19
**Repository:** `IAmSoThirsty/Project-AI`
**Candidate:** local successor working tree at `82aa1476657e16a1d38caccba38357c83380a3e3`
**Decision:** **DEPLOYMENT NOT AUTHORIZED**

This is the current CAB entry point for the v0.0.3 successor. The candidate is
not yet an immutable release: the working tree is dirty, `HEAD` still equals
the published v0.0.2 commit, and no successor remote CI, signature, or
attestation evidence exists.

The remote default `master` currently resolves to `9fc3c93e6abd02a14bd141fab4d3ef772fa090bf`,
not this successor. Its active scheduled Codex Deus workflow is failing before
checkout because repository policy rejects unpinned actions such as
`actions/checkout@v4` and `actions/download-artifact@v4`.
The observed scheduled failures are runs `29709754498`, `29698528738`, and
`29686790959`.

## Local evidence

| Gate | Result |
|---|---|
| Python suite | `3406 passed, 5 skipped`; zero failures, warnings, XFAIL, or XPASS |
| Branch coverage | `87.32%` across eight batches; threshold `80%` |
| Canonical/frozen provenance | `5/5` replay; `2264/2264` frozen sections |
| Static/type gates | Ruff, format, canonical MyPy (`175` files), and strict Temporal/Waterfall-adapter MyPy pass |
| Workflow supply-chain pinning | All `103` local remote-action references use full commit SHAs |
| Compose | `9/9` local services healthy with security settings verified when Docker is available |
| Helm | Lint passes; production render verifies `47` manifests and eight digest-pinned images |
| Web/Rust/Android/Desktop | Local acceptance gates pass; release artifacts remain unsigned or working-tree evidence |
| Waterfall | Standalone `309` tests; copied Project-AI replay `313` tests, no warnings |
| Pre-deployment verifier | **Fail-closed** while owner-private material, remote successor evidence, approved ingress, and remote-backup configuration remain unresolved |
| Draft V3Q manifest review snapshot | `3ea08a2cf1244c4c0b4a9045aef4b5e5ac59ed9e82d7e03aa315d0d56fdcf09c` SHA-256 for `packages/thirstys-standard-v3q/thirstys-standard-v3q.manifest.yaml` | Review aid only; owner ratification must sign the exact final ratified-manifest hash |
| Machine-readable successor evidence | `REMOTE_SUCCESSOR_EVIDENCE.json` currently has `status: missing` | Gate remains closed until owner, remote, overlay, backup, monitoring-CRD, dependency, and target-environment fields are evidenced and independently reviewed |

Local evidence is necessary but is not production authorization.

For a complete current-state diagnostic, run
`uv run python tools/verify_pre_deployment.py --report`. The report evaluates
all gates and lists every blocker; it does not alter the strict fail-closed
deployment gate.

## Release-blocking conditions

- [ ] Owner-controlled `owner-primary` key is rotated offline, retired, and
      replaced only through the approved secret/key custody process.
- [ ] The exact final V3Q manifest is owner-ratified; the replacement public
      key is enrolled; `verify_ratification.py` passes against that exact hash.
- [ ] External proof issuance and custody are demonstrated for required-mode
      execution; the online runtime must not self-authorize.
- [ ] The remediation is committed, pushed, and tested by successor CI on the
      exact immutable revision.
- [ ] The remote default-branch workflow failure is resolved or explicitly
      retired; all active remote workflows must satisfy full-SHA action pinning
      before remote evidence is treated as green.
- [ ] All eight image digests have independently verified cosign signatures,
      SBOM/provenance attestations, and matching CodeQL/Checkov/Trivy and
      language dependency evidence.
- [ ] An approved production cluster, context, namespace, Helm release,
      maintenance window, implementer, rollback owner, approver, support owner,
      paging route, secret manager, and acceptance authority are recorded.
- [ ] Prometheus Operator CRDs are installed in the approved target; a
      server-side Helm dry run, deployment smoke, alert delivery, backup/restore,
      and rollback rehearsal pass there.
- [ ] Dependabot PRs #509 and #510 receive an owner-approved disposition.
      Their current check sets include the failing remote Codex Deus workflow;
      PR #510 also reports a CircleCI error.

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
