# Deployment Blocker Profile Map

This map reclassifies the previously aggregate production blockers against the controlling
deployment model in [`DEPLOYMENT_MODEL.md`](DEPLOYMENT_MODEL.md).

| Existing item | P1 offline-first local | P2 hosted/Kubernetes | Disposition |
| --- | --- | --- | --- |
| Eight published-image signatures | Not required | Required when those registry images are the release artifact | P2 only; currently verified for the prior candidate |
| Registry SPDX/SLSA attestations | Not required for a local offline bundle | Required | P2 open |
| `main`/tag-bound registry release provenance | Not required for a locally identified offline artifact | Required | P2 open |
| External proof custody | Required as offline owner custody when a proof is mandatory | Required under the selected hosted custody process | Cross-profile; P1 uses local/offline custody |
| Retire superseded owner private material | Required | Required | Cross-profile owner security item |
| Exact V3Q owner ratification for a required runtime | Required if P1 enables required V3Q enforcement | Required | Cross-profile governance item |
| Production cluster/namespace | Not required | Required | P2 only |
| Target Helm overlay | Not required | Required | P2 only |
| Public ingress hostname/TLS | Not required; owner surfaces remain loopback-bound | Required when hosted ingress is selected | P2 only |
| Remote backup destination | Not required; encrypted local/removable custody is valid | Required if selected by P2 policy | P2 only |
| Cloud secret manager | Not required; DPAPI/passphrase local protection is valid | Deployment-specific | P2 only |
| Monitoring CRDs | Not required; local health/status/logs are required | Required for the current Helm monitoring design | P2 only |
| Paging route | Not required unless the owner selects one | Deployment-specific | P2 only |
| Cluster rollback rehearsal | Not required | Required | P2 only |
| Local install/upgrade/rollback/recovery rehearsal | Required | Also required for any local component | P1 gate |
| Local secret protection | Required | Required | Cross-profile; implementation differs |
| Local full-state backup/restore | Required | Hosted equivalent required | Cross-profile; implementation differs |
| Local health, logs, and truthful failure states | Required | Required | Cross-profile |
| CAB sign-off | Not inherent to the product | Required only if the owner selects that release process | P2/organizational only |
| Dependabot PRs against legacy `master` | Does not gate the identified P1 artifact | Release-process disposition | P2/repository maintenance |

## Current qualified state

- P1: v0.0.3 is the released, single-user Offline-First Local production product. Its
  implementation and acceptance are tracked in
  [`OFFLINE_FIRST_READINESS.md`](OFFLINE_FIRST_READINESS.md).
- P2: future optional work, unprovisioned and not authorized. Existing Helm/registry/CAB
  evidence remains useful only for that optional profile.
- The existing `tools/verify_pre_deployment.py` aggregate gate remains a P2-oriented diagnostic
  until it is explicitly made profile-aware. Its nonzero result cannot, by itself, decide P1.
