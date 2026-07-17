# Documentation Portal Fidelity Ledger

- **Status:** Implemented and visually verified 2026-07-17.
- **Scope:** `apps/web/docs-portal` — Overview (live gateway panel + frozen
  path count), Architecture (pipeline + live module catalog), API contract
  (frozen OpenAPI baseline reference), Decisions (ADR reader), Publications
  (DOI catalog).
- **Definition applied:** every figure on screen originates from a live
  gateway response or a test-enforced frozen repository artifact; zero
  hardcoded narrative claims. The contract page renders
  `docs/api/openapi-baseline.json` — the exact file locked by
  `test_openapi_baseline_matches_runtime` — so the page cannot drift from the
  runtime without the test suite failing first.

## Live QA environment

Same stack as the proof-portal ledger: real gateway on `127.0.0.1:8000`
(seeded audit relay), Vite dev server on `127.0.0.1:4173`, Chromium via
`playwright-cli` 0.1.17.

## Evidence (inspected with the image viewer during capture)

Renders under
`C:\Users\Quencher\.claude\visualizations\2026\07\17\project-ai-portals\`:

- `docs-overview-desktop.png` (1536×1024): live gateway rows plus the
  `openapi-baseline` frozen-path count row.
- `docs-contract-desktop.png` (1536×1024): baseline title/version, the
  `46 PATHS / 51 OPERATIONS` pill computed from the frozen file, both
  securityScheme tiles (machineBearer, sessionCookie) with their runtime
  descriptions, and the freeze-test provenance line.
- `docs-decisions-desktop.png` (1536×1024): ADR-001 and ADR-002 rendered from
  the repository markdown through the in-house renderer.
- `docs-contract-mobile.png` (390×844).

## Measurements and cleanliness

- Desktop `scrollWidth = 1536`; narrow `scrollWidth = 390` (no horizontal
  overflow on the contract listing).
- Final browser console: 0 errors, 0 warnings. Network log: 0 responses with
  4xx/5xx status.

## Problems found by this QA and fixed before commit

Shared with the proof portal: missing favicon (console 404) fixed with
`public/favicon.svg` + `<link rel="icon">`; `.proof-stats` overflow fix in the
shared stylesheet also constrains this portal's securityScheme tiles.

## Honest scope

- The Docker image build for this portal (with the new
  `docs/api` + `docs/architecture/decisions` COPY layers) passed on
  2026-07-17; the running container was not smoke-served this session.
- Assistive-technology acceptance and full accessibility automation for this
  portal were not executed this session.
