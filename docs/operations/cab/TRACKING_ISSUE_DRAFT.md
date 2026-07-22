# Tracking Issue Draft — Release and Approve the v0.0.2 Successor

**Suggested title:** Release and close CAB blocker evidence for the Project-AI v0.0.2 successor
**Suggested priority:** High / release-blocking
**Suggested labels:** `release`, `operations`, `security`, `cab`
**External issue created:** No

## Description

Complete and attach the evidence required to make a CAB decision on a successor
to Project-AI v0.0.2. v0.0.2 commit
`82aa1476657e16a1d38caccba38357c83380a3e3` is superseded and must not be used
as the deploy candidate. Immutable successor code candidate
`eaed9905cacc02e2fb98e3cc92356e8d160e593e` is pushed and has green successor
CI/vulnerability runs `29731671162` and `29731671150`.
The current repository-local CAB pack is at
`docs/operations/cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md`.
The v0.0.2 pack remains a historical supersession record.

Current disposition: **v0.0.2 superseded; deployment not authorized**.

## Blockers

- [x] Repair the local Python coverage memory path and Compose verifier import
      failure; prove 87.32% combined coverage and 9/9 local runtime health.
- [x] Choose and apply successor version v0.0.3 across all first-party version
      surfaces and add release tag/digest agreement gates.
- [x] Commit/push the remediation and obtain green remote CI/security workflows
      on immutable candidate `eaed9905`.
- [ ] Record environment, cluster/context, namespace, Helm release, maintenance
      window/timezone, freeze check, change owner, implementer, rollback owner +
      backup, approver, support owner, and acceptance authority.
- [ ] Replace placeholder production host/TLS/storage/secret inputs in an
      approved environment overlay; verify secret-manager provenance without
      exposing values.
- [ ] Securely retire the compromised local V3Q `owner-primary` private key and
      affected local image layers under the owner's approved process. Replacement
      public key `owner-rotation-2026-07-19-01` is already tracked.
- [ ] Keep replacement owner authority outside the online runtime; attach
      evidence for external, narrowly scoped authority/approval proof issuance.
- [ ] Prove a `require_approval` result never reaches the executor without a
      valid external approval proof.
- [x] Obtain Jeremy / Thirsty's signature over the exact V3Q release manifest
      and verify the ratification record. Required-mode startup evidence remains
      pending.
- [x] Independently verify all eight image signatures and subject-digest
      bindings from publish run `29731685685` with cosign v3.1.2 and raw OCI
      checks; the certificates are branch-provenance only.
- [ ] Re-publish from `main` or a release tag and attach digest-bound SPDX/SLSA
      attestations; current attestations are absent 0/8 and cannot be added
      retroactively.
- [x] Add pinned CodeQL/Checkov workflows; pass local Checkov, Python OSV, and
      Node audits; remediate vulnerable setuptools 82.0.1 to 83.0.0.
- [ ] Attach successful remote CodeQL, Checkov, Trivy, Rust, Python, and Node
      evidence tied to immutable successor `eaed9905`.
- [x] Resolve repository monitoring namespace/job/metric mismatches and expose
      real API Prometheus series.
- [ ] Configure real Alertmanager routes; prove dashboard queries and a test
      page in the target.
- [ ] Perform server-side dry run and reviewed manifest diff in the target.
- [ ] Confirm the target cluster has the Prometheus Operator
      `ServiceMonitor` and `PrometheusRule` CRDs. A prior local
      `docker-desktop` server-side rehearsal failed closed without them; Docker
      Desktop is now running locally, but no approved production target exists.
      Rerun the full production-values Helm dry run after the prerequisite is
      present.
- [ ] Prove backup and restore, then rehearse Helm rollback to a certified
      known-good revision; record duration and data/audit effects.
- [x] Add and locally exercise governed audit/SWR backup and restore utilities;
      production PVC/remote restore and Helm rollback rehearsal remain open.
- [ ] Run target health, metrics, core-flow, authorization-denial, governance,
      audit-chain, persistence, and alert-delivery acceptance checks.
- [ ] Record disposition/risk acceptance for Dependabot PRs #509 and #510.
- [ ] Send stakeholder/support notices and record named acceptance sign-off.
- [ ] Confirm the standalone `T:\\01-Projects\\Thirstys-waterfall` product remains
      independently usable and attach its release/owner evidence.
- [x] Review `packages/thirstys-waterfall/PROVENANCE.md`, rerun its 312-test
      replay suite, and attach the Project-AI rebuild/adapter evidence. Local
      evidence is recorded in the CAB release bundle; target proof remains
      separate.
- [ ] Attach an authenticated Project-AI route and target-environment proof for
      the shared Waterfall authority contract; until then the adapter remains
      fail-closed.
- [x] Implement the local machine-authenticated Waterfall status/operation API
      routes with V3Q-wired adapter checks, audit receipts, and OpenAPI evidence.
- [x] Implement ADR-002 durable per-program machine credentials: schema version
      5 on both account backends, owner/MFA issuance, route scopes, revocation,
      audit attribution, focused tests, and OpenAPI baseline.
- [x] Exercise SQLite-to-PostgreSQL schema/data migration against a disposable
      PostgreSQL 16 container, including preservation and scoped authentication
      of a hashed machine credential.
- [ ] Run the ADR-002 migration against the approved PostgreSQL target; provision
      per-program secrets and attach only ids/scopes/secret references.

## Evidence links to attach

- Green candidate CI run
- Publish run and eight image digest/signature outputs
- SBOM/provenance and security scan artifacts
- Target render/diff/dry-run output
- Backup identifier and restore proof
- Rollback rehearsal log
- Health, metrics, smoke, governance, audit, dashboard, and alert test output
- Communications timestamps and acceptance/CAB decision

## Definition of done

- Every approval condition in the CAB pack is checked with an immutable evidence
  link or explicitly accepted exception with owner and expiry.
- Formal change, deployment, rollback, monitoring, dependency, and support
  records contain no unresolved operator fields.
- CAB decision and deployment authorization are recorded by the named authority.
