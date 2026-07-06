# Thirsty-Lang Integration Discovery

**Status:** DISCOVERY + PLAN (no source code written yet)
**Authority:** User directive 2026-06-30 — "make it the domain sovereign language"
**Source:** `C:\Users\Quencher\Desktop\Github\Personal Repo's\thirsty_lang_exploration_0754` (read-only)
**Target:** `T:\Project-AI-Beginnings`
**Date:** 2026-06-30

---

## 0. What "integrated" means here

The user directive: **integrated (not transferred, not copied) and USED
to write the code for this repo.** That means:

- Thirsty-Lang is consumed as a **PyPI dependency** (or a workspace
  source pin), the same way the strategy doc's Stage 0 decision
  intended. It is not vendored into `packages/`.
- The six tiers are **exercised by Beginnings** — at minimum:
  - policy files written in the appropriate tier (`.tarl`, `.thirst`,
    `.tscg`, etc.)
  - capability tokens / governance verdicts / audit chains delegated
    to the language's runtime where applicable
  - the API gateway and CLI surface Thirsty-Lang CLI tools
- The canonical `project-ai-*` Python packages **keep their Python
  implementation** (they are the runtime) but **delegate domain
  semantics** to the language (policy authoring, governance proofs,
  capability contracts, etc.)

This is NOT a rewrite of Beginnings in Thirsty-Lang. The Python
packages are the engine; the language is the policy and proof surface.

---

## 1. The six tiers (from the source)

The source declares six CLIs (matching the "six tier family" framing):

| # | Tier | CLI | Python entrypoint | Purpose |
|---|---|---|---|---|
| 1 | `thirsty-lang` | `thirsty` | `utf.thirsty_lang.cli:main` | Base language — lexer, parser, AST, interpreter, type system, module system, package manager, formatter, linter, proof obligations |
| 2 | `thirst-of-gods` | `thirst-of-gods` | `utf.thirst_of_gods.cli:main` | Higher-order — divinity tier; refines `thirsty` for advanced cases |
| 3 | `tscg` | `tscg` | `utf.tscg.cli:main` | Third tier |
| 4 | `tscg-b` | `tscg-b` | `utf.tscg_b.cli:main` | Fourth tier |
| 5 | `tarl` | `tarl` (+ `tarl-lsp`) | `utf.tarl.cli:main` / `utf.tarl.lsp:main` | Policy tier — broker, authority, runtime, durable state, escalation, linter, LSP. **This is the most relevant to Beginnings.** |
| 6 | `shadow-thirst` | `shadow-thirst` | `utf.shadow_thirst.cli:main` | Sixth tier — convergence |

Source tree (`src/utf/`): 50+ Python files across the 6 subpackages.
Tests: 20+ test files in `tests/`. Examples in `examples/`.

The `governance/` subdir adds:
- `iron_path.py` — the deterministic governance path
- `sovereign_runtime.py` — runtime
- `triumvirate_server.py` — triumvirate server

**Existing PyPI version:** 0.8.1 (wheel + sdist available in
`thirsty_lang_exploration_0754/dist/`).

---

## 2. Beginnings current state (verified 2026-06-30)

| Item | Current state |
|---|---|
| Root `pyproject.toml` dependencies | 16 `project-ai-*` packages; **no `thirsty-lang` dep** |
| `uv.lock` | **no `thirsty-lang` entry** |
| `grep -r "import thirsty\|from thirsty" packages/ apps/ tools/` | **zero hits** |
| Existing PyPI pin in repo | none — the strategy doc mentioned `thirsty-lang==0.1.4` but it was never executed |
| Python version | 3.12.10 (workspace pin) vs `thirsty-lang` requires `>=3.11` — **compatible** |
| Build backend | uv (hatchling per package) vs `thirsty-lang` uses setuptools — **independent** |
| `cryptography` dep | `thirsty-lang` requires `cryptography>=41.0`; check whether Beginnings already pulls it transitively |
| License | `thirsty-lang` is Apache-2.0; Beginnings is MIT — **compatible** |

**Net:** Beginnings has **zero coupling** to Thirsty-Lang today.
Integration is greenfield.

---

## 3. Mapping: Thirsty-Lang tiers -> Beginnings packages

The natural fit (per Thirsty-Lang's design — policy + proof + audit
sit on top of the kernel):

| Beginnings package | Natural Thirsty-Lang use |
|---|---|
| `kernel` | (kernel) — kernel types stay in Python; **TARL policy files** (`.tarl`) describe the invariant / verdict semantics in a machine-checkable form |
| `governance` | **TARL** — the canonical governance policy is a TARL document; the Python engine consumes it via the `utf.tarl.runtime` interface |
| `capability` | **TARL authority** — capability contracts are TARL policy; the Python HMAC tokens reference TARL-issued tokens |
| `execution` | **TARL broker + escalation** — execution paths are gated by TARL-evaluated policy; failures route through `tarl.escalation` |
| `companion` | (no direct fit) — companion state is revisioned data, not policy |
| `atlas` | **TSCG** — the deterministic analytical projection specs (sensitivity, bayesian, graph) are written in TSCG so they're machine-verified before runtime |
| `swr` | **TSCG-B** — scenario definitions are TSCG-B; the Python `WarRoom` consumes them |
| `temporal` | (no direct fit) — workflow orchestration is orchestration, not policy |
| `tarl` (existing Beginnings package) | **This must be renamed** to avoid collision with the language's TARL tier. Suggest `project-ai-grammar` or `project-ai-compiler` (legacy TARL was about Thirsty Action / Rule Language anyway — same root) |
| `companion`, `security`, `cerberus`, `hydra_50`, `arbiter`, `rlp` | These are operator-side or auxiliary; integration is via policy contracts only |

---

## 4. Integration model options

### Option A — **Thirsty-Lang as a PyPI dep** (recommended for first wave)

- Add `thirsty-lang==0.8.1` to root `pyproject.toml` `[project].dependencies`
- Run `uv lock` to update `uv.lock`
- Wire one package first (canonical choice: `governance`) to use TARL
- The 6 tier CLIs become available on `$PATH` after `uv sync`
- Pro: minimal disruption, idiomatic
- Con: requires trusting the 0.8.1 wheel; need to verify SHA-256

### Option B — **Workspace source pin** (rebuild-in-place)

- Clone the language repo into the Beginnings workspace as a member
- Add `[tool.uv.sources] thirsty-lang = { workspace = true }` (3-place
  registration per skill pitfall 34)
- Pro: in-tree, no PyPI trust gap
- Con: pulls a 50-file dep into the monorepo; workspace graph gets
  fatter

### Option C — **Hybrid: PyPI dep + workspace copy of policy examples**

- `thirsty-lang` from PyPI (runtime)
- Workspace copy of just the `.tarl` / `.thirst` / `.tscg` example
  files (the policy artifacts that Beginnings writes), as
  `docs/policy/*.tarl` etc.
- Pro: language is external, policies are in-tree
- Con: need to keep the policy examples in sync with the language's
  grammar (manual sync)

**Default for first wave:** Option A. Switch to B or C only if a
specific need surfaces.

---

## 5. Concrete deliverables (per sub-phase)

Per the wave-budget rule (≤5 new files per wave) and the discovery-first
pattern, this is a multi-wave effort. Sub-phases:

### Phase T0 — Envelope (this turn's commit)

- This discovery doc (1 file)
- No source changes
- Acceptance: `STAGE_19_5T0_ACCEPTANCE.md`

### Phase T1 — Add `thirsty-lang` as a workspace dep

- Modify root `pyproject.toml` to add `thirsty-lang==0.8.1` to
  `[project].dependencies` AND to `[tool.uv.sources]` per pitfall 43
  (verify both alphabetical and chronological sections)
- Run `uv lock` and commit the updated `uv.lock`
- Add 1-2 smoke tests that import the 6 tier CLIs as Python modules
  to confirm the dep works in the venv
- Acceptance: `uv run python -c "import utf; import utf.tarl; import
  utf.thirsty_lang; print('ok')"` succeeds; 1347 tests still pass

### Phase T2 — Author canonical `.tarl` policy for `governance`

- Write `docs/policy/governance.tarl` describing the canonical verdict
  set (ALLOW / DENY / ESCALATE) and the constitutional rule set
- Wire `packages/governance` to load and evaluate it via
  `utf.tarl.runtime`
- Add unit tests for the policy evaluation path
- Acceptance: governance engine can answer a verdict for a simple
  test case using the TARL policy

### Phase T3 — Author `.thirst` proof obligations for the audit chain

- Write the proof-of-integrity contract for the audit chain as a
  `.thirst` document
- Wire `packages/security` to verify the chain against the proof
  obligations
- Acceptance: chain verification invokes the language's proof engine

### Phase T4 — Wire the 6 CLIs into the operator CLI

- Add `project-ai thirsty-policy` and related commands to
  `packages/cli/src/project_ai_cli/app.py`
- Each command delegates to the corresponding `utf.*.cli:main`
- Acceptance: `project-ai thirsty-policy --help` works; tests pass

### Phase T5 — Write canonical `.tscg` / `.tscg-b` specs for atlas / swr

- Author the analytical projection specs and scenario definitions in
  the appropriate tiers
- Wire atlas and swr to consume them
- Acceptance: a scenario can be run end-to-end using a `.tscg-b`
  spec

### Phase T6 — Rename the Beginnings `tarl` package

- Per §3, the existing `packages/tarl/` collides with the language's
  TARL tier. Rename to `packages/grammar/` (or similar) and update all
  imports, tests, and `pyproject.toml` workspace entries.
- This is a wave of its own because of the import-graph blast radius.

### Phase T7 — Author Shadow-Thirst convergence harness

- The 6th tier is for convergence. The natural use is a "shadow
  mode" that runs the canonical gate in parallel with an experimental
  gate and reports drift.
- Acceptance: shadow mode can run on the canonical replay and emit a
  drift report.

**Sub-phases T1–T7 are individual waves, each gated green, each
requiring explicit "go T<sub-phase-name>" before source is written.**

---

## 6. What's NOT in this scope

- **Rewriting the existing `project-ai-*` packages in Thirsty-Lang**
  — they are the runtime; the language is the policy/proof surface
- **Replacing the Python interpreter** for the canonical stack — Python
  3.12.10 stays; Thirsty-Lang is consumed as a Python package
- **Modifying the language's source** — the language is at version
  0.8.1 and stable; we don't fork it
- **Six-tier compliance certification** — that would require a
  separate, much longer engagement

---

## 7. Risks

1. **PyPI trust gap** — `thirsty-lang==0.8.1` is on PyPI but the
   version has a `Development Status :: 3 - Alpha` classifier. Verify
   the wheel's SHA-256 before pinning. Document the pin in
   `docs/reference/MERGE_PROVENANCE.md` (extend with the language
   entry).
2. **Name collision: `tarl` package vs `tarl` language tier** — Phase
   T6 is dedicated to resolving this. Must be done before the
   `governance` package starts using TARL imports (otherwise the
   Python module namespace gets `tarl.runtime` ambiguity).
3. **Python version** — workspace pins 3.12.10; language requires
   3.11+. Compatible. But the language's mypy is configured for
   3.11, not 3.12. May produce `unused-ignore` warnings on the
   language's own modules when we run `uv run mypy packages/ --strict`
   with the language as a dep. Mitigate with a scope-exclude
   (`exclude = ["packages/_staging"]`) or by tolerating the warnings.
4. **`cryptography` version conflict** — `thirsty-lang` requires
   `cryptography>=41.0`; verify what Beginnings already pulls.
5. **Six-tier adoption is irreversible** — once we author canonical
   policy in `.tarl` form, the Python engine depends on TARL
   evaluation. Per the Subordination contract, the language is a tool
   (not a peer of the kernel), so this is acceptable — but it locks
   in the language as a runtime dep.

---

## 8. Honest disclosure

**This is discovery + plan only. NO source code has been written or
modified.** The `T:\Project-AI-Beginnings` working tree is clean at
HEAD `8c3f802d` (last commit was the Wave 3b docs closure). The
Thirsty-Lang source at `C:\Users\Quencher\Desktop\Github\Personal
Repo's\thirsty_lang_exploration_0754` was not touched.

**No file moves. No file copies. No PyPI install. No source import.**

The next step is your call. Recommended order:
1. **`go T1`** — add `thirsty-lang==0.8.1` as a dep, lock, smoke-test
2. **`go T6`** — resolve the `tarl` package name collision first (so
   the Python namespace is unambiguous when T2 wires governance)
3. **`go T2`** — author the canonical governance policy in `.tarl`
4. Then T3, T4, T5, T7 in any order

Each `go T<sub-phase>` triggers the corresponding sub-phase:
discovery doc + source + tests + integration + acceptance + commit.
Same J1/J2 pattern.

---

## 9. Verification

```bash
# 1. Beginnings is clean
cd T:/00-Active/Project-AI-Beginnings
git status --short                                # must be empty
git log --oneline -1                              # 8c3f802d (or later)

# 2. The Thirsty-Lang source is intact and on 0.8.1
cd "C:/Users/Quencher/Desktop/Github/Personal Repo's/thirsty_lang_exploration_0754"
git status --short                                # (don't care; read-only)
grep "^version" pyproject.toml                    # 0.8.1

# 3. Beginnings has no Thirsty-Lang dep yet (this envelope doesn't add one)
grep "thirsty" T:/00-Active/Project-AI-Beginnings/pyproject.toml || echo "no thirsty dep yet - expected"
grep "thirsty" T:/00-Active/Project-AI-Beginnings/uv.lock 2>/dev/null | head -5 || echo "no thirsty in lock - expected"
```

If the verification reproduces the expected outputs, the discovery
envelope is sound and you can authorize the next sub-phase.
