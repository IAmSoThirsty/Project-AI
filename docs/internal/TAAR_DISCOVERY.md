# TAAR Discovery: TAAR-Agent-Taskforce Port

Per user directive 2026-07-09 ("copy this repo:
T:\01-Projects\TAAR-Agent-Taskforce, leaving the original intact, and
integrate the copy into Project-AI Beginnings"), this phase ports the
standalone TAAR repo into `packages/taar` as a first-class uv
workspace package.

## Source provenance

- Outer path `T:\01-Projects\TAAR-Agent-Taskforce` is a wrapper; the
  real git root is the nested `TAAR-Agent-Taskforce\` directory.
- Source HEAD at copy time: `7b51966317f64c7b1fe277e0db0935c5e460704c`
  (branch `main`, working tree clean before and after the copy —
  verified with `git -C <source> status --porcelain`).
- Upstream identity: `taar-agent-taskforce` v0.1.0 on PyPI,
  https://github.com/IAmSoThirsty/TAAR.
- The source repo was never written to (read-only input).

## What TAAR is

TAAR ("Thirsty's Active Agent Runner") is a local-first, governed
multi-agent runner: reader agents ("checks") emit hash-sealed evidence
bundles; writer agents render Markdown reports citing evidence hashes;
an append-only JSONL audit spine records every admission/denial; a
classification lattice (OPEN < CONTROLLED < RESTRICTED < SECRET <
PHANTOM < BLACK) escalates and never auto-downgrades. Headline
feature: the GitHub Workflow Guardian (`taar workflows scan|explain|
classify|harden|evidence`). Report-only and fail-closed by design —
merge/push/deploy/patch capabilities are structurally rejected at
registry validation.

**Positioning in Beginnings: operator-side, like `arbiter`/`rlp`.**
TAAR holds no Project-AI governance authority (Thirsty V3 rules
29-32: no governance claims without enforcement proof). It never
imports the kernel → governance → capability → execution chain —
enforced by `tests/test_taar_integration.py`.

## Constraints honored

Per pitfall 1 (trust source over memory): every claim about source
layout was verified against the source tree at SHA 7b51966.

Per pitfall 11 (state what changed): all deviations from the source
are listed under "Adaptations" below; everything else is a
byte-faithful copy.

Per pitfall 43 (workspace vs external PyPI deps): pyyaml/typer/rich
are external PyPI deps already present in uv.lock (6.0.3 / 0.26.7 /
15.0.0); `project-ai-taar` itself is a workspace source.

Per the repo command rules: no inline `python -c` (scratch scripts
used), no heredoc file creation, robocopy used for the copy with
`.git/build/egg-info/__pycache__/.pytest_cache/.project-ai/.github`
excluded.

## Waves

- **W1 copy/layout** — robocopy to `packages/taar/`, rearrange to src
  layout: `taar/` → `src/taar/`, `checks/` → `src/taar/checks/`,
  `writers/` → `src/taar/writers/` (the setuptools package-dir remap
  becomes a physical layout). `registry/` + `taar.toml` stay at
  package root (test fixtures resolve them via `parents[1]`).
  `action.yml`, `taar-self-test.yml`, and the two scheduler `.ps1`
  scripts moved to `reference/` (inert provenance). Dropped: source
  `pyproject.toml` (replaced), `LICENSE`, `.gitignore`,
  `tests/__init__.py`, PyPI `publish.yml` (Beginnings does not publish
  TAAR).
- **W2 packaging** — new hatchling `pyproject.toml`
  (`project-ai-taar` 0.0.0.dev0, script `taar = "taar.cli:main"`);
  root pyproject registration in dependencies + uv sources + workspace
  members; `.gitignore` gains `.project-ai/` (TAAR runtime state);
  `src/taar/py.typed` added.
- **W3 lint/type** — ruff (I001, UP017, UP042 StrEnum, B904, SIM102,
  RUF005, W291 via named `MD_HARD_BREAK` constant preserving markdown
  hard breaks byte-for-byte) and mypy strict brought to zero errors
  WITHOUT adding taar to the root mypy exclude list. The legacy
  sys.modules import bridge in `taar/__init__.py` deleted (dead after
  the physical move). `from tests.conftest import edit_yaml` (relied
  on the source's `pythonpath=["."]`) moved to
  `tests/taar_test_helpers.py`. One dead comparison removed in
  `executor.py` (`agent.class_ == QUARANTINE` inside the WRITER
  branch, provably always False). Fake `ghp_` token in
  `test_swarm_behavior.py` now built by concatenation so secret
  scanners never see a literal token.
- **W4 tests** — all 87 upstream tests pass under repo pytest with
  `-> None` annotations added; new `tests/test_taar_integration.py`
  (7 tests: import surface, entry point, seed data, fail-closed
  registry, end-to-end heartbeat-reader round trip in tmp_path,
  dependency-direction guard).
- **W5 docs/commit** — this document, continuity map session block,
  single `feat(taar)` commit with 4-gate verification footer.

## Adaptations (complete list of behavior-relevant edits)

1. `(str, Enum)` → `StrEnum` for the four enums in `models.py`
   (ruff UP042). All serialization goes through `.value`; the 87
   contract tests (which assert exact report/YAML content) pass
   unchanged.
2. `executor.py` WRITER branch: dead `agent.class_ == QUARANTINE`
   comparison removed (mypy comparison-overlap); boolean result
   identical.
3. Report templates: trailing-double-space markdown hard breaks moved
   into a `MD_HARD_BREAK` constant; rendered output byte-identical.
4. Typing-only changes everywhere else (annotations, casts,
   loop-variable renames in `registry.py`); no logic changes.

## Not ported / follow-ups

- PyPI publishing workflow (stays in the standalone repo).
- `docs/operations/PROJECT_AI_MASTER_CONTINUITY_TRACEABILITY_MATRIX.md`
  line "No current executable TAAR orchestrator found" is now stale —
  fix in a later chore commit.
- AGENTS.md operator-side package list (`arbiter`, `rlp`) could
  mention `taar`; AGENTS.md is binding and is not edited without
  explicit user approval.
- Optionally add `taar` to the pre-commit mypy hook `files:` regex
  (strict mypy passes today).
