# Repository Intelligence Operations

Repository intelligence is a local, read-only search surface over selected Project-AI
source and documentation. The API never creates, refreshes, or writes an index.
Build and refresh operations are explicit offline commands.

The implementation plan is [`plans/repository-intelligence.md`](../../plans/repository-intelligence.md).

## Configuration

The existing FastAPI service reads these optional environment variables at startup:

| Variable | Default | Meaning |
|---|---|---|
| `PROJECT_AI_REPOSITORY_ROOT` | current working directory | Repository root to inspect and search. |
| `PROJECT_AI_REPOSITORY_INDEX` | `$PROJECT_AI_REPOSITORY_ROOT/data/repository-intelligence` | Persisted index directory. |

Paths are expanded but are not created by the API. Set both variables explicitly for
an operator process whose working directory is not the repository root:

```powershell
$env:PROJECT_AI_REPOSITORY_ROOT = 'T:\00-Active\Project-AI-Beginnings'
$env:PROJECT_AI_REPOSITORY_INDEX = 'T:\00-Active\Project-AI-Beginnings\data\repository-intelligence'
```

The scanner uses deterministic lexical chunks and preserves relative path, language,
line range, SHA-256, and excerpt provenance. Its built-in policy excludes dependency
and generated trees, caches, build/output artifacts, secrets and secret-like names,
binary/non-UTF-8 files, unsupported extensions, symlinks, and files over the configured
maximum size. The current scanner constants are defined in
[`knowledge.repository`](../../packages/knowledge/src/knowledge/repository.py).

## Create or refresh the index offline

Run from the repository root with the project environment:

```powershell
uv run python -m knowledge.repository_cli build `
  --root . `
  --output data\repository-intelligence
```

The command writes `manifest.json`, `status.json`, and `records.json` only under the
specified output directory. It is safe to repeat when source changes; the index is
deterministic and refreshes the snapshot. Inspect readiness without rebuilding:

```powershell
uv run python -m knowledge.repository_cli status `
  --root . `
  --output data\repository-intelligence
```

A successful status has `state: "ready"` (or `"empty"` for a repository with no
eligible content) and `stale: false`. A changed, missing, corrupt, or incompatible
index is reported explicitly. Rebuild it offline before relying on search results.

## Read-only API

The existing service host exposes two GET routes under `/repository-intelligence`:

- `GET /repository-intelligence/status` reports schema version, state, configured
  root/index paths, indexed and excluded counts, exclusion reasons, and stale state.
- `GET /repository-intelligence/search?query=<text>&limit=<1-50>` returns ranked
  grounded results with `path`, `language`, `start_line`, `end_line`, `sha256`,
  `excerpt`, and `score`.

Safe examples:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/repository-intelligence/status'
Invoke-RestMethod 'http://127.0.0.1:8000/repository-intelligence/search?query=repository%20scanner&limit=3'
```

A normal status response resembles:

```json
{
  "state": "ready",
  "indexed_files": 4917,
  "indexed_chunks": 16326,
  "excluded_files": 544,
  "stale": false
}
```

A search response contains the requested query and a `results` array. Empty queries
or limits outside 1 through 50 are rejected. If the index is missing, corrupt, or
stale, search returns an explicit service-unavailable response rather than silently
searching an empty or old snapshot.

## Operating boundary and limitations

- The routes are GET-only and authority-free; they do not execute repository code,
  issue commands, mutate source files, or refresh artifacts.
- Results are lexical and deterministic. They are useful for grounded local lookup,
  not a complete semantic code-understanding or dependency-analysis system.
- Only eligible UTF-8 text files are indexed, and exclusions are intentional; an
  absent path does not prove that its content never existed.
- Search results are tied to the indexed snapshot. Check `stale` before using them,
  and refresh offline after source changes.
- The API exposes source excerpts and hashes for provenance. Do not point it at a
  repository containing material that the operator is not authorized to disclose.

See the service integration in
[`project_ai_services.repository_intelligence`](../../apps/services/src/project_ai_services/repository_intelligence.py)
and the offline CLI in
[`knowledge.repository_cli`](../../packages/knowledge/src/knowledge/repository_cli.py).

## Evidence authority and superseded snapshots

The authoritative evidence for the current index is always the live
`data/repository-intelligence/status.json` produced by the offline `build`/`status`
commands above. Ad-hoc captures of verification sequences are historical snapshots of
the moment they were taken and are invalidated by any later source or documentation
change.

**Formal supersession (2026-07-24):** `data/repository-intelligence/final-verification.log`
is superseded as current evidence. It records an older snapshot (`indexed_files=4918`,
`indexed_chunks=16329`, `excluded_files=544`, root fingerprint `5948ed28…`) that no
longer matches the live index. The file is retained unchanged as historical provenance
and must not be rewritten; there is no repository-defined command that regenerates it.
Consumers of index evidence must read the live `status.json` (or the `status` CLI
output) instead. This supersession is recorded in the continuity map
(`docs/operations/CONTINUITY_MAP.md`).
