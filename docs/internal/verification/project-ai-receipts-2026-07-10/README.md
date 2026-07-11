# Project-AI-Beginnings — Audit Receipt (2026-07-10)

Evidence-backed measurement of the repository at Git HEAD
`656a26dbb245d5d2dbd2626389e9204737698882` (branch
`chore/warning-cleanup-utc-artifacts`), taken 2026-07-10. Every figure traces to
a raw command output in `raw/`; the exact command, timestamp, working directory,
HEAD, and tool version for each is in `commands.log`. Read-only: this audit wrote
only inside this directory. No estimates, no repository self-claims used.

## Principal verified measurements

| Measurement | Value | Source |
|---|---:|---|
| Physical files (incl. `.git`) | 123,193 | analyze.py / raw/02 |
| — of which `node_modules` | 99,927 | raw/36 |
| — of which `.venv` | 14,919 | raw/36 |
| Git-tracked files (`git ls-files`) | 2,852 | raw/01b |
| Files after standard exclusions | 2,877 | raw/03 |
| — under `docs/` | 2,000 (70%) | raw/04 |
| Excluded (cache/dep/build/generated) | 120,176 | raw/03,36 |
| Repo size excl. `.git` | 604,984,183 B (~577 MB) | raw/06 |
| — untracked generated `data/knowledge/` | ~462 MB (84%) | raw/39 |
| `.git` object DB (pack) | 199.59 MiB, 46,014 objects, 5 packs | raw/07 |
| Total lines (scc / cloc) | 1,155,111 / 1,078,633 code | raw/18a,18b |
| — Markdown | ~606,667 | raw/18a |
| — JSON (data) | ~344,938 | raw/18a |
| — Python (source) | 84,753 (scc) / 75,352 (cloc) | raw/18a,18b |
| Test files | 148 | raw/21 |
| Python test functions (`def test_`) | 2,166 | raw/22 |
| pytest collected/passed | 2,509 passed, 1 xfailed, 0 failed | raw/24 |
| pytest exit code / runtime | 0 / 72.68 s | raw/24 |
| First commit | `4acf92a9` · 2026-06-19 · Jeremy Karrick | raw/08 |
| HEAD commit | `656a26db` · 2026-07-10 · Jeremy Karrick | raw/09 |
| Elapsed calendar days | 21 | raw/10 |
| Commits — current branch | 192 | raw/11 |
| Commits — all reachable refs | 2,528 | raw/12 |
| Distinct commit identities | 11 | raw/13,14 |
| Python packages / apps / crates | 34 / 6 / 1 | raw/28 |
| GitHub workflows | 3 | raw/29 |
| Helm charts / templates / k8s kinds | 1 / 12 / 12 kinds | raw/30 |
| PDF documents | 55 | raw/32 |
| Submodules / license files | 0 / 4 | raw/33,41 |
| Prometheus-matched files | 168 (≈2 real config) | raw/34 |
| Archive SHA-256 | `be4b128d…a63a343` | archive/ |

## Provenance (git-evidence only; see provenance.md)

- **Current branch (delivered trunk):** 192 commits, **100% owner-attributed**
  (Jeremy Karrick / IAmSoThirsty). Much of it AI-*assisted* (Co-Authored-By:
  Claude trailers) — counted under the owner, not the AI tool.
- **All refs (2,528 commits):** Owner 1,344; AI agents 1,141 (Copilot 1,007,
  Claude/Anthropic 85, Google Jules 49); GitHub automation 36; Dependabot 7. The
  AI-agent-authored commits sit on experimental/remote branches, not the trunk.
- **External human contributors: 0.** **Submodules: 0.** **SPDX headers: 0.**
- Imported/vendored: 258 reference/byte-preserved files + vault-recovery imported
  history; dependencies resolved into excluded `.venv`/`node_modules`.

## Quality & validation (as configured by the repo)

| Gate | Result |
|---|---|
| pytest | 2,509 passed / 1 xfailed / 0 failed / 0 error · exit 0 |
| ruff check | PASS (repo, receipt dir excluded) |
| ruff format --check | PASS (425 files formatted) |
| mypy (pre-commit hook) | PASS |
| ESLint (`pnpm web:lint`, configured) | 230 problems (mostly eslint v10 flat-config migration) |
| bandit (optional, py3.12) | 2,923 findings — 5 high / 30 med / 2,888 low (asserts/subprocess) |
| pyright (optional, scoped sample) | 1 error in packages/kernel/src/kernel |
| black | N/A — not configured; only available copy is Python 3.11 (cannot parse 3.12) |
| semgrep | available, not run (auto config requires telemetry) |

## What the numbers mean (do not read file count as engineering volume)

The repository is **documentation-dominated**: 2,000 of 2,877 kept files (70%)
are under `docs/`, and Markdown is ~607K of the ~1.1M code-lines. JSON *data*
adds ~345K lines. **Actual Python source is ~75K–85K lines across ~480–500
files, concentrated in `packages/`.** The 577 MB working-tree size is ~84%
untracked generated ML data (`data/knowledge/`). "168 Prometheus files" are
almost all Markdown *mentions* — real Prometheus integration is 2 Helm CRs
(PrometheusRule + ServiceMonitor). The 123k physical-file figure is 99.9k
`node_modules` + 14.9k `.venv` dependency files, not authored content.

## Integrity

- `git fsck --full`: no non-dangling errors (dangling objects only — normal).
- `git status --short`: clean working tree at audit start (this receipt dir was
  untracked and is the only addition).
- `git count-objects`: **11 stray `.git/objects/**/tmp_obj_*` files (5.45 KiB)** —
  leftover temp objects (not corruption; not created by this audit). Safe to
  `git prune`/`git gc` at the owner's discretion (not done — audit is read-only).

## Caveats

- **Read-only side effect:** running the repo test suite (required, item 24)
  causes 3 tracked files —
  `packages/emp-defense/src/emp_defense/artifacts/{events,final_state,summary}.json`
  — to be rewritten by the emp-defense simulation tests. This is a property of
  those tests, not the audit. The files were **restored to HEAD** after
  measurement; the working tree is clean apart from this receipt directory.
- **Branch/tag note:** during earlier user-directed work in this same session,
  local `main` was fast-forwarded to HEAD (local only, not pushed) and an
  annotated tag `taar-verify-2026-07-10` was created. Those are prior actions,
  not part of this read-only audit; the audit modified no branches, tags, source,
  dependency, or config files.
- Tokei unavailable (Windows build failure); semgrep not run (telemetry); black
  invalid (Python 3.11 vs 3.12); PyPI resolvability not checked (no network).
  ESLint uses a v10 global that surfaces flat-config migration errors. See
  `exclusions.txt` and `summary.json.static_analysis` for details.
- Category split (item 19) is heuristic (path/name based); language line counts
  (scc/cloc) are the authoritative source for the source/docs/data breakdown.

## Files in this receipt

`README.md` (this) · `summary.json` · `summary.csv` · `provenance.md` ·
`exclusions.txt` · `environment.txt` · `commands.log` · `SHA256SUMS.txt` ·
`fs_metrics.json` · `git_activity.json` · `inventory.json` ·
`analyze.py` `aggregate.py` `inventory.py` `synthesize.py` `collect.ps1` (harness) ·
`archive/project-ai-HEAD.tar.gz` (deterministic `git archive` of HEAD) ·
`raw/` (per-measurement raw outputs + `pytest-junit.xml`).

Verify integrity: `sha256sum -c SHA256SUMS.txt` from this directory.
