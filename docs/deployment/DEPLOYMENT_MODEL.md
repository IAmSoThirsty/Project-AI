# Project-AI Deployment Model

**Authority:** Owner decision, 2026-07-25.
**Product profile:** P1 - Offline-First Local.
**Secondary profile:** P2 - Hosted/Kubernetes and cloud publication (optional, not the product).
**Released production version:** v0.0.3 for a single Windows user.

## Controlling product definition

Project-AI is a local, offline-first system. Its primary production deployment runs on the
owner's machine, binds owner-facing services to `127.0.0.1`, retains its authoritative data
locally, and performs its core governed workflows without an internet connection.

Kubernetes, public ingress, cloud secret managers, registry publication, remote monitoring
operators, hosted databases, SaaS integrations, and organizational CAB processes are additive
deployment choices. Their absence cannot block P1 readiness. They may gate a separately selected
P2 deployment, but P2 is not the default product and is not required to operate P1.

## P1 - Offline-First Local

The released P1 product provides:

1. A portable offline installation artifact containing every required container image and local
   runtime file, with a manifest and SHA-256 integrity record.
2. A deterministic owner start path that performs preflight, initializes protected local
   credentials, starts the stack without registry pulls, waits for readiness, and gives the exact
   local Control Center destination.
3. Core governance, Control Center, audit, SWR, Atlas, TAAR, persistence, and recovery functions
   on local-only networks with no cloud service as the sole authority or state holder.
4. Local PostgreSQL and audit/SWR persistence with an encrypted, integrity-checked full-state
   backup and a fail-closed restore path.
5. Account-bound or passphrase-protected local secrets that are absent from `.env`, client
   bundles, logs, evidence receipts, and container environment variables.
6. A tested local upgrade, rollback, backup, and recovery procedure for the artifact actually
   distributed.
7. Local health, readiness, service state, logs, truthful degraded states, and evidence receipts.
8. A documented stop path that retains or explicitly removes local data according to the owner's
   chosen action.

P1 does not require:

- a production Kubernetes cluster or namespace;
- a public hostname, TLS ingress, or internet-facing listener;
- a cloud secret manager;
- Kubernetes monitoring CRDs or a paging SaaS;
- a remote backup service (encrypted removable media or owner-selected offline custody is valid);
- a container-registry release, registry attestations, or cloud publication;
- a corporate CAB or fictional multi-person approval body.

## P2 - Hosted/Kubernetes and cloud publication

P2 is an optional secondary profile. It includes Helm/Kubernetes deployment, public or private
hosted ingress, registry-published images, registry signatures and attestations, production
cluster monitoring, remote backup targets, hosted secret management, maintenance windows,
paging routes, and any owner-selected release approval process.

P2 remains unprovisioned. P2 gaps must remain visible and fail closed when P2 is selected, but
they do not downgrade or prohibit a verified P1 release.

## Optional integrations

The boundary in
[`OPTIONAL_SERVICE_USAGE.md`](../operations/cab/OPTIONAL_SERVICE_USAGE.md) remains controlling:
connected services are replaceable transport, mirror, or convenience adapters. No connected
service may be the sole holder of governance authority, continuity, release evidence, recovery
data, or a runnable local gate.

## Readiness claims

Readiness and release claims are always profile-qualified:

- `v0.0.3 is released for P1 offline-first local production operation` is the current
  qualified claim. Its exact acceptance and distribution evidence is recorded in
  [`OFFLINE_FIRST_READINESS.md`](OFFLINE_FIRST_READINESS.md).
- `P2 unprovisioned` is not a defect in P1 and is not shorthand for "Project-AI is not
  production-ready."
- A P1 result does not authorize P2 deployment, publication, or public network exposure.

## Owner decision record

Jeremy Karrick, sole repository owner, explicitly established on 2026-07-25 that the product is
the local offline-first system. Owner's Cockpit controls are additive to that product. Kubernetes,
cloud, hosted infrastructure, and organizational processes are optional profiles and must not be
treated as universal production blockers.
