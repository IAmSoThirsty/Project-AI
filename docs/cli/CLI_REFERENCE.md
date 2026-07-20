# CLI Reference

> Canonical operator reference for the Project-AI `project-ai` CLI.
> Source of truth: `packages/cli/src/project_ai_cli/app.py`. The CLI
> communicates only with the HTTP gateway; it does not import governance,
> capability, execution, Arbiter, or RLP internals.

**Status:** live reference for the v0.0.3 successor CLI.
**Entrypoint:** `project-ai` (installed via `uv run pip install -e packages/cli`)
**Help:** `project-ai --help` (Typer-generated)

---

## 0. Configuration

The CLI is a thin client to the HTTP gateway. Two env vars control it:

| Env var | Default | Required for | Description |
|---|---|---|---|
| `PROJECT_AI_API_URL` | `http://127.0.0.1:8000` | all commands | Base URL of the API gateway |
| `PROJECT_AI_API_TOKEN` | (none) | protected commands | Bearer token sent as `Authorization: Bearer <token>` |

The token can also be passed via `--api-token <token>` on a per-call basis
(not recommended — leaks to shell history and process listings).

The CLI exits non-zero (`Typer.Exit(code=1)`) on:
- Network error to the gateway
- Non-2xx HTTP response
- Invalid input (bad UUID, missing file, etc.)
- Gateway auth failure (missing/invalid token for a protected command)

---

## 1. Public commands (no token required)

### `project-ai version`

Prints the development version string. No network call.

```
$ project-ai version
0.0.3
```

### `project-ai health`

Calls `GET /health/live` and prints the response.

```
$ project-ai health
{
  "status": "live",
  "version": "0.0.3"
}
```

Exit code: 0 if the gateway is live, non-zero on network error.

### `project-ai dois`

Calls `GET /dois` and prints the DOI catalog.

```
$ project-ai dois | python -m json.tool
{
  "dois": [
    {"title": "...", "doi": "...", "domain": "...", "url": "..."}
  ]
}
```

### `project-ai replay`

Calls `GET /replay/status` and prints the canonical-replay status.

```
$ project-ai replay
{
  "replay": {
    "bundle_count": 0,
    "last_verified_at": null,
    "chain_intact": true
  }
}
```

`chain_intact: true` is a prerequisite for production readiness. A `false`
response indicates the audit chain has been broken — see
`docs/runbooks/INCIDENT_RESPONSE.md` for the recovery procedure.

### `project-ai atlas-status`

Calls `GET /atlas/status` and prints the Atlas subordination notice.

```
$ project-ai atlas-status
{
  "subordination_notice": "Atlas is an analytical projection service ..."
}
```

---

## 2. Protected commands (require `PROJECT_AI_API_TOKEN`)

All protected commands fail with a clear error if the token env var is unset
or the gateway returns 401/503.

### `project-ai audit`

Calls `GET /audit?limit=N` and prints the last N audit records.

```
$ project-ai audit --limit 20
{
  "events": [
    {"event": "chimera.verdict", "hash": "...", "ts": "..."},
    ...
  ]
}
```

`--limit` is bounded `[1, 500]` (matches the gateway's query validation).

### `project-ai verdict`

Calls `POST /chimera/verdict` to relay a governance verdict to the audit
log. The CLI does not make governance decisions; it only records them.

```
$ project-ai verdict act-001 ALLOW --source manual-test
{
  "event": "chimera.verdict",
  "hash": "..."
}
```

Arguments:
- `action_id` (positional, required) — action identifier
- `outcome` (positional, required) — one of `ALLOW`, `DENY`, `ESCALATE`
- `--source` (optional, default `operator-cli`) — evidence source string

### `project-ai canary`

Calls `POST /chimera/canary` to relay a tripped canary. Reads the canary
value from a file via `--value-file` (never from a CLI argument) to keep
tripped canaries out of shell history and process listings.

```
$ echo -n "tripwire-2026-06-30-aaa" > /tmp/canary.txt
$ project-ai canary --value-file /tmp/canary.txt --context smoke-test
{
  "event": "chimera.canary",
  "hash": "..."
}
$ rm /tmp/canary.txt
```

### `project-ai atlas-sludge`

Calls `POST /atlas/sludge` to generate a Sludge Stack (SS-only) fictional
narrative from a Reality Stack snapshot. Reads the snapshot from
`--snapshot-file` (JSON file). Does not grant authority or actuate a
decision.

```
$ cat > /tmp/snapshot.json <<'EOF'
{
  "rs_snapshot": {"actor": "operator-test", "domain": "smoke"},
  "archetypes": ["hidden_elites"]
}
EOF
$ project-ai atlas-sludge --snapshot-file /tmp/snapshot.json
{
  "hash": "...",
  "narrative": {
    "narrative_id": "...",
    "archetypes": ["hidden_elites"],
    "stack": "SS",
    "source_snapshot_sha256": "...",
    "content": "..."
  }
}
$ rm /tmp/snapshot.json
```

`--archetype` (repeatable) lets you pick one or more `NarrativeArchetype`
values; if omitted, defaults are used. Valid values are in
`packages/atlas/src/atlas/sludge_sandbox.py`.

---

## 3. Global flags

These apply to every subcommand:

| Flag | Default | Description |
|---|---|---|
| `--api-url URL` | `$PROJECT_AI_API_URL` or `http://127.0.0.1:8000` | Override gateway URL |
| `--api-token TOKEN` | `$PROJECT_AI_API_TOKEN` | Override bearer token (prefer env var) |
| `--timeout SECONDS` | 30.0 | Request timeout (range `0.1..300.0`) |
| `--help` | — | Show Typer-generated help for the command |

---

## 4. Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Network error, non-2xx HTTP response, gateway auth failure, invalid input |
| 2 | Typer usage error (bad flag, missing required argument) |

---

## 5. Source of truth

This document is generated by reading the Typer command definitions in
`packages/cli/src/project_ai_cli/app.py`. If a command changes shape,
flag, or behavior, **update this file in the same commit**.

The CLI's own `--help` is always authoritative:
```
$ project-ai --help
$ project-ai <subcommand> --help
```
