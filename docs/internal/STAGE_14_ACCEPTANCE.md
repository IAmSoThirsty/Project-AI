# Stage 14 Web Portal Acceptance

**Status:** ACCEPTED FOR DEVELOPMENT

## Required Evidence

- [x] Separate documentation and proof portal production builds.
- [x] Shared OMPT-derived visual system with responsive navigation.
- [x] Live public liveness, replay, and 21 DOI records from the API.
- [x] Token-bound read-only audit viewer with no governance authority.
- [x] Operator token is cleared immediately after each audit request.
- [x] Honest loading, empty, unavailable, and `not_run` states.
- [x] ESLint passes with zero warnings.
- [x] TypeScript and both Vite production builds pass.
- [x] Vitest: documentation `2 passed`; proof `2 passed`.
- [x] Browser page identity, non-blank DOM, framework-overlay, and console checks pass.
- [x] DOI filter, audit loading, token clearing, and mobile navigation interactions pass.
- [x] Desktop `1280x720` and mobile `390x844` layouts have zero horizontal overflow.

The in-app Browser screenshot operation timed out during four capture attempts,
including explicit desktop viewport and visible-browser retries. This is an
environment/tooling issue and does not block the DOM, interaction, console, or
computed-layout evidence above, but screenshot comparison evidence is not
available for this gate and must not be inferred.

The npm workspace uses the SemVer spelling `0.0.0-dev0`; it maps to the
repository's canonical PEP 440 development version `0.0.0.dev0` and is not a
release or publication version.
