# Deployment Freeze Notice

**Issued:** 2026-05-18  
**Status:** ACTIVE  
**Lift Conditions:** See checklist below

## Scope

The following operations are **frozen** until all lift conditions are met:

| Operation | Frozen? | Reason |
|-----------|---------|--------|
| `git push` to production branch | YES | Secrets not yet rotated |
| `docker push` to any registry | YES | Image may embed unrotated secrets |
| Docker Build Cloud builds | YES | Cloud builder must not receive secrets |
| Helm / K8s deploy | YES | Downstream of frozen images |
| Release tagging (`git tag`) | YES | No release until CI is green + secrets rotated |

Local development (`docker compose build`, `docker compose up`) is **permitted** for testing only.

## Lift Conditions

All must be true before the freeze is lifted:

- [ ] All secrets rotated per `SECRET_INCIDENT_2026-05-18.md`
- [ ] CI pipeline passes on `master` with all critical jobs green:
  - CodeQL
  - Bandit
  - Secret scanning
  - Dependency security audit
  - Python tests
  - Integration tests
  - Governance regression tests
- [ ] `docker compose build api` completes locally without error
- [ ] Health endpoints (`/health/live`, `/health/ready`) respond 200 in local container
- [ ] This file updated to status **LIFTED** with date

## Authority

Only the repository owner may lift this freeze by updating the status field above and checking all boxes.
