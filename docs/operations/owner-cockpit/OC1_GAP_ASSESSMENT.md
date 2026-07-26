# Owner's Cockpit OC-1 Gap Assessment

**Standard:** TS3-OCS-1.0
**Source requirements:** `docs/standards/owner-cockpit/REQUIREMENTS.json` (144 unique IDs)
**Assessment date:** 2026-07-25
**Product profile:** P1 offline-first local
**Assessment verdict:** Supporting implementation present; full OC-1 acceptance is not complete.

The Owner's Cockpit standard is additive to the P1 product. It does not redefine Kubernetes,
hosted publication, cloud infrastructure, or external integrations as product prerequisites.

## Implemented and evidenced

- Exact local destination: `http://127.0.0.1:4175`.
- Double-click offline start, status, stop, and offline-install entry points.
- Local instance identity and authentication assurances on the sign-in surface.
- Command Center orientation strip: environment, version, deployment mode, actor, current
  condition, and next safe action.
- API, docs, proof, and Control Center live-status probes.
- Nine-service health and container-hardening verification.
- Protected local secrets, encrypted backup/restore, and offline upgrade/rollback controls.
- Browser DOM verification of the unauthenticated local sign-in surface.
- Automated Control Center lint, unit/component tests, and production build.

## Not verified

- A signed-in owner journey could not be run because no authenticated browser session or owner
  password was available; existing accounts were not reset or bypassed.
- Owner-only approval, replay, denial, and recovery journeys remain manual acceptance work.
- Human usability and accessibility acceptance by Jeremy is not recorded.
- TS3-OCS-1.0 has not been ratified by the owner. Its 144 requirement records therefore remain
  candidate traceability data, not a claim of full conformance.

## Minimum closeout

1. Jeremy signs in at the local Control Center.
2. Run one Atlas or SWR owner journey through completion and retain its receipt/evidence ID.
3. Repeat after a stop/start and confirm the earlier receipt remains visible.
4. Record manual accessibility/usability results.
5. Ratify or reject TS3-OCS-1.0 explicitly in `RATIFICATION_RECORD.md`.
