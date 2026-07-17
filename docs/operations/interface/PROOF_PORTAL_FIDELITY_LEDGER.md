# Proof Portal Fidelity Ledger

- **Status:** Implemented and visually verified 2026-07-17.
- **Scope:** `apps/web/proof-portal` — Live evidence (dashboard surfaces),
  Authority boundaries (instance contract + module matrix), Audit evidence
  (token-gated viewer with event filter and offset paging).
- **Definition applied:** every figure on screen originates from a live gateway
  response; zero hardcoded narrative claims. No pixel-identical concept exists
  for these screens; fidelity is design-system fidelity against the existing
  portal shell.

## Live QA environment

- Real gateway: `uv run python -m project_ai_api.server` on `127.0.0.1:8000`
  with a QA audit relay and machine token; seeded with two canonical verdicts
  (ALLOW, DENY) and one Sludge generation before capture.
- Real browser: Chromium via `playwright-cli` 0.1.17 (session-isolated), Vite
  dev server on `127.0.0.1:4174` proxying `/api` to the gateway.

## Evidence (inspected with the image viewer during capture)

Renders under
`C:\Users\Quencher\.claude\visualizations\2026\07\17\project-ai-portals\`:

- `proof-status-desktop.png` (1536×1024): four dashboard surfaces with live
  metrics — gateway `0.0.0.DEV0`, replay honestly `0/5 INVARIANTS` (not run in
  QA), audit chain `3 ENTRIES`, `21 DOI RECORDS`.
- `proof-boundaries-desktop.png` (1536×1024, post-fix): the three frozen
  negative-capability tiles, human-access/governed-execution path rows, live
  module authority matrix, `LOCAL_SOVEREIGN` deployment pill.
- `proof-audit-desktop.png` (1536×1024): chain-verified pill, cleared token
  field, live tallies (0 denials / 0 canaries / 2 canonical verdicts),
  "3 matching of 3 verified entries".
- `proof-status-mobile.png`, `proof-audit-mobile.png` (390×844).

## Measurements and cleanliness

- Desktop `document.documentElement.scrollWidth = 1536` after the fix below;
  narrow layout `scrollWidth = 390` (no horizontal overflow).
- Final browser console: 0 errors, 0 warnings. Network log: 0 responses with
  4xx/5xx status.

## Problems found by this QA and fixed before commit

1. **Favicon 404** — both proof and docs portals lacked a favicon, producing a
   real console error on every load. Fixed with the shared shield
   `favicon.svg` + `<link rel="icon">` in each portal's `index.html`.
2. **Boundaries tile overflow** — `browser_execution_capability: false` could
   not wrap, forcing the `.proof-stats` grid wider than the 1536 px viewport
   (page `scrollWidth` exceeded the viewport; third tile clipped). Fixed in
   `apps/web/shared/src/styles.css`: `repeat(3, minmax(0, 1fr))`,
   `min-width: 0` on tiles, `overflow-wrap: anywhere` on tile values.
   Re-measured 1536 exactly after the fix.

## Honest scope

- QA replay status was `not_run` — the page correctly showed `0/5`; a `pass`
  state render was not captured this session.
- Assistive-technology acceptance (NVDA/VoiceOver) and full accessibility
  automation for these two portals were not executed this session.
