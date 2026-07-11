# provenance.md — authorship, evidence-based only

Audit date: 2026-07-10 · HEAD `656a26dbb245d5d2dbd2626389e9204737698882`
All statements below are backed by git metadata in `raw/` (items 8–17). No
ownership is inferred beyond what git records. AI-*assisted* work is not counted
as independent authorship by any tool.

## Two different populations — do not conflate them

The repository's authorship looks very different depending on which commits you
count, so both are reported.

### A. Current branch / delivered trunk (HEAD, `chore/warning-cleanup-utc-artifacts`)
- 192 commits (item 11). Git author attribution: **192 / 192 (100%) Owner**
  (Jeremy Karrick / IAmSoThirsty). No commit on this line is authored by a bot or
  AI-agent identity.
- Local `main` was fast-forwarded to this same HEAD during this session (local
  only, not pushed). `origin/master` (remote trunk) is a different, older commit
  `9fc3c93e` and was not touched.

### B. All reachable refs (every branch/remote in this clone)
- 2,528 commits (item 12) across 11 distinct identities. By category (item 15):
  | commits | category |
  |--------:|----------|
  | 1,344 | Owner (Jeremy Karrick / IAmSoThirsty / Thirsty / Quencher) |
  | 1,007 | AI agent — GitHub Copilot (`copilot-swe-agent[bot]`) |
  |    85 | AI agent — Claude / Anthropic (`anthropic-code-agent[bot]`, `Claude`) |
  |    49 | AI agent — Google Jules (`google-labs-jules[bot]`) |
  |    36 | GitHub automation (`github-actions[bot]`) |
  |     7 | Dependabot (`dependabot[bot]`) |
- So across ALL history, **1,141 / 2,528 (45%) commits were authored directly by
  AI-agent identities** — but almost entirely on experimental/remote branches
  (`codex/*`, `jules-*`, copilot branches), NOT on the delivered trunk.

## Architectural authorship vs. writing

- Git shows the owner (Jeremy Karrick / IAmSoThirsty) as the first committer
  (`4acf92a9`, 2026-06-19, "[Stage 0] Bootstrap") and the dominant trunk author.
  This supports **owner as architect / integrator of record**. It does not, by
  itself, prove line-by-line human authorship of every owner-attributed commit.
- Many owner-attributed commits on the trunk carry `Co-Authored-By: Claude …`
  trailers (this includes the current session's commits `db5c0d9`…`656a26d`,
  authored as the owner with a Claude co-author trailer). These are **AI-assisted,
  human-owned** by git attribution. Per the audit rules they are counted under the
  owner, and the AI tool is NOT credited with independent ownership.

## Bot / automation

- `github-actions[bot]` (36) — CI automation commits.
- `dependabot[bot]` (7) — dependency-update automation.
- These are machine-generated maintenance commits, not authored engineering.

## External human contributors

- None identified. Every non-bot, non-AI identity resolves to the owner's known
  aliases (see `raw/14_normalized_identities.txt`, which lists every identity and
  its assigned category for audit). `External / unclassified human` = 0 commits.

## Third-party / imported / vendored content (not original authorship)

- **Imported history**: commits such as `ee6c52e3`, `e5c9f1c8`, `314bc1be`,
  `88e76c74`, `809c97fa` port files from external vault/legacy snapshots
  ("vault-recovery", "recover from …"). This content is relocated, not authored
  here.
- **Byte-preserved / reference trees** (258 files): `packages/_staging`,
  `packages/security/reference`, `packages/rlp/governance_framework`,
  `docs/reference` (55 PDFs), `docs/internal/frozen-history`. Preserved inputs and
  reference material, not fresh source.
- **Dependencies**: 3 tracked lockfiles (`uv.lock`, `pnpm-lock.yaml`, …) pin
  external packages; the resolved packages themselves live in the excluded
  `.venv/` (14,919 files) and `node_modules/` (99,927 files).
- **Submodules**: none (`.gitmodules` absent). **SPDX headers**: 0. **License
  files**: 4.

## Generated (not authored)

- `data/knowledge/` — 462 MB of generated ML index/corpus (gitignored,
  rebuildable). Counted in bytes, flagged as generated.
- `.venv`, `node_modules`, `target`, `build`, `dist`, `__pycache__`,
  `.mypy_cache`, `.ruff_cache` — 120,176 excluded generated/dependency files.

## One-line provenance conclusion

By git evidence, Project-AI-Beginnings is a 21-day-old, owner-architected
monorepo whose delivered trunk is 100% owner-attributed (much of it AI-assisted
via Co-Authored-By trailers), while its wider all-refs history additionally
contains ~1,141 AI-agent-authored commits on experimental branches; there are no
external human contributors and no submodules in evidence.
