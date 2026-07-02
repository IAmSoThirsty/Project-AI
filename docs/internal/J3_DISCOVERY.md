# SWR Full-Surface Port: Discovery (J3.0 envelope)

## Status: SHIPPED AS DISCOVERY ENVELOPE. Port waves pending.

## TL;DR

The legacy SWR (Sovereign War Room) package is a 9-module
package + 1 web dashboard + 1 CLI + 1 demo + 3 tests + 1
`.tarl` policy file, totaling ~16 files. It is canonical
in two locations in the legacy repo (both `engines/sovereign_war_room/swr/`
and `SOVEREIGN-WAR-ROOM/swr/` contain copies); the **canonical
copy is `engines/sovereign_war_room/swr/`** based on
filesystem timestamps (May 19 vs April 26). The port rebuilds
each module specifically for the Beginnings package
structure (`packages/swr/src/swr/`) and re-uses the existing
canonical `scenario.py`, `war_room.py`, and `__init__.py`
that were already ported in earlier phases (J0/J1/J2).

## What lives in the legacy SWR

The canonical SWR surface (verified by stat):

| File | LOC | Purpose |
|---|---|---|
| `__init__.py` | 30 | Public surface re-exports |
| `api.py` | ~250 | HTTP API server (FastAPI/Flask) |
| `bundle.py` | ~280 | Bundle of scenario results (proof + score) |
| `core.py` | ~370 | Engine core: scenario + verdict + recording |
| `crypto.py` | ~310 | Hash + signature for bundles |
| `governance.py` | ~440 | SWR-specific governance layer |
| `proof.py` | ~390 | ZK/Merkle proof generation |
| `scenario.py` | ~580 | 5-round scenario definitions |
| `scoreboard.py` | ~480 | Score aggregation + leaderboard |

Plus at `SOVEREIGN-WAR-ROOM/` (parent dir, references `swr/`):
- `cli.py` (223 LOC) - command-line entrypoint
- `demo.py` (143 LOC) - demo script
- `web/app.py` - HTTP server for dashboard
- `web/templates/dashboard.html` - HTML template
- `tests/test_core.py`, `tests/test_governance.py`, `tests/test_proof.py`
- `verify_quality.tarl` (963 bytes) at `engines/sovereign_war_room/`

Plus 2 legacy narrative docs to move to `docs/reference/`:
- `fleet_agent_5_tracking.md` - track 5 fleet agent status
- `GROUP_2_AGENT_8_REPORT.md` - agent 8 group 2 report

## What is already in Beginnings

The `packages/swr/src/swr/` package (verified):
- `__init__.py` (already ported, exports Scenario, ScenarioLibrary, etc.)
- `scenario.py` (already ported - 5-round scenario definitions)
- `war_room.py` (already ported - execution-gated recording)
- `swr_spec.tscg-b` (T5b - 72-byte binary frame)
- `tscg_b_spec.py` (T5b - loader)
- `tests/test_swr.py` (5 existing tests, all pass)

The existing port is **J0/J1** (skeleton + scenario + war_room).
**J3.0** = the full-surface port of the 7 remaining modules.

## Port waves (J3.1 through J3.7)

| Wave | Files | Tests | Commit scope |
|---|---|---|---|
| J3.0 | this discovery doc | n/a | envelope |
| J3.1 | `core.py` | `test_core.py` | engine core + 8 tests |
| J3.2 | `scoreboard.py` + `bundle.py` | new tests | score + bundle |
| J3.3 | `crypto.py` + `proof.py` | `test_proof.py` | hash + proof |
| J3.4 | `governance.py` | `test_governance.py` | swr governance |
| J3.5 | `api.py` + `web/app.py` + `web/templates/dashboard.html` | new tests | HTTP + dashboard |
| J3.6 | `cli.py` + `demo.py` | new tests | entrypoints |
| J3.7 | `verify_quality.tarl` + 2 narrative docs | new tests | policy + docs |

7 port waves, each ≤5 files, each one commit. Estimated total:
- ~16 source files
- ~30+ new tests
- ~3,000 lines of code ported

## Architectural invariants (THIRSTYS STANDARDS V3)

- **Canonical copy is `engines/sovereign_war_room/swr/`** (newer
  than `SOVEREIGN-WAR-ROOM/swr/` by stat).
- **Port specifically for Beginnings**: each module is
  rebuilt for the canonical `packages/swr/src/swr/` layout,
  not copy-pasted. The `__init__.py` updates carefully to
  re-export both the J0/J1 surface (Scenario, etc.) and the
  new J3 surface (core, scoreboard, etc.).
- **Fail-closed**: any port that breaks a J0/J1 invariant
  (5 existing tests, the T5b spec loader) forces a fix or
  a documented scope reduction. The T5b convergence check
  must continue to pass.
- **No external deps added unless necessary**: the legacy
  SWR is pure stdlib + project deps (kernel, execution,
  governance, security). HTTP server (api.py, web/app.py)
  may need Flask/FastAPI; will be deferred or stubbed if
  those are not already in the project's lock.
- **Tests are first-class**: each port wave brings a
  test file. The canonical `test_swr.py` (5 tests) must
  continue to pass.

## What is NOT in this discovery

1. **No port code**: this is the envelope only. Source
   ports happen in J3.1-J3.7.
2. **No dep changes**: pyproject.toml updates are in J3.5
   (HTTP) if needed.
3. **No docs beyond this envelope**: full SWR feature-gap
   audit doc is a separate workstream (item 8 in
   `LEGACY_TO_CANONICAL_INVENTORY.md`).

## Risk register

- **HTTP server deps**: api.py + web/app.py may need Flask
  or FastAPI. If not in lock, defer HTTP to a later phase
  with a documented stub.
- **Convergence integration**: the T7 convergence harness
  uses `swr.tscg_b_spec.load_spec()`. The new SWR surface
  must NOT change `tscg_b_spec.py` or the bundled frame.
  T7 must continue to pass.
- **Test count drift**: each port wave adds tests. The
  pre-J3 baseline is 1551. Post-J3 expected: 1700+.

## Next action

Awaiting "go J3.1" to drive the first port wave (core.py).
