# Project-AI v0.0.3 Successor CAB Review Pack

**Prepared:** 2026-07-20
**Repository:** `IAmSoThirsty/Project-AI`
**Candidate:** immutable successor code commit `6684828d23b08beaac77aee5efadc532bed23181`; the active branch also contains documentation-only follow-ups
**Decision:** **DEPLOYMENT NOT AUTHORIZED**

This is the current CAB entry point for the v0.0.3 successor. The candidate
is pushed and immutable successor CI plus vulnerability scans are green in
runs `29716300475` and `29716300404`. It is not a production release: image
signatures, attestations, proof custody, target approval, and deployment
controls remain unverified.

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
| Pre-deployment verifier | **Fail-closed** while owner-private material, external successor evidence, approved ingress, and remote-backup configuration remain unresolved |
| V3Q manifest review snapshot | `3ea08a2cf1244c4c0b4a9045aef4b5e5ac59ed9e82d7e03aa315d0d56fdcf09c` source hash; canonical ratified hash `15c8e4ba51dd4e3d0e562da670848d4c62e2ee98ac3983429aac8a3ff44db80f` | `owner-ratification.json` verifies the exact ratified artifact |
| Machine-readable successor evidence | `REMOTE_SUCCESSOR_EVIDENCE.json` currently has `status: missing` | Gate remains closed until owner, remote, overlay, backup, monitoring-CRD, dependency, and target-environment fields are evidenced and independently reviewed |

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
- [ ] External proof issuance and custody are demonstrated for required-mode
      execution; the online runtime must not self-authorize.
- [x] The remediation is committed, pushed, and tested by successor CI and
      vulnerability scanning on immutable candidate `6684828d`.
- [ ] The remote default-branch workflow failure is resolved or explicitly
      retired; candidate-branch CI is green, but default-branch workflow health
      remains an independent CAB review item.
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
