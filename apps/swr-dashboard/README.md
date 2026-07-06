# SWR Dashboard

Flask web dashboard for the Project-AI Sovereign War Room (SWR).

## What this is

A read-only web UI over the SWR core (the `WarRoomCore` facade ported in
J6.1). The dashboard shows:

- Total scenarios, results, AI systems, cryptographic proofs
- Leaderboard (top AI systems by Sovereign Resilience Score)
- Test scenarios, filterable by round (1-5)
- Recent results with compliance status

The dashboard is **view-only**. The CLI (`swr.cli`) and the FastAPI
gateway (`packages/api`) are the write surfaces — they run scenarios and
record results. The dashboard is for operators to see the current state.

## Run it

```bash
# from the repo root
uv run python -m project_ai_swr_dashboard
# navigate to http://localhost:5000
```

Or, using the installed entry point:

```bash
uv run project-ai-swr-dashboard
```

## Architecture

- `app.py` — Flask app, factory pattern, builds a governed `WarRoomCore`
  on first request (same shape as `swr.cli.get_swr()`: default
  allow-all governance, capability authority, execution gate).
- `templates/dashboard.html` — single-page UI, vanilla JS, fetches the
  JSON API routes below.

### API routes

| Route | Method | Returns |
|-------|--------|---------|
| `/` | GET | The dashboard HTML |
| `/api/scenarios?round=N` | GET | List of scenarios, optional round filter |
| `/api/leaderboard?limit=N` | GET | Top-N leaderboard |
| `/api/results?system_id=&round=` | GET | Results filtered by system/round |
| `/api/systems/<id>/performance` | GET | Per-system performance metrics |
| `/api/stats` | GET | Top-line counts (scenarios, results, systems, proofs) |

## Port provenance

This is the **J3.8** port. The legacy `engines/sovereign_war_room/web/`
app was adapted to the canonical Beginnings surface:

- `from swr import SovereignWarRoom` → `from swr import WarRoomCore`
  (the J6.1 facade is the canonical SWR entry point)
- Module-level `swr = SovereignWarRoom()` → lazy `get_swr()` factory
  (avoids importing the governance stack at module load time)
- Removed `sys.path` insertion (workspace package import)
- HTML/CSS/JS: identical to legacy (the user-authored UI is not touched)

## See also

- `packages/swr/README.md` — the SWR core (WarRoomCore)
- `packages/swr/src/swr/cli.py` — the CLI surface (same governed stack
  factory as the dashboard)
- `docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md` §5 — the inventory
  slice that named this port
