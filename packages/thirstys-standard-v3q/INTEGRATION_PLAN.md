# Integration Plan — Thirsty's Standard V3+Q → Project-AI Beginnings

> Status: DONE (integrated as uv workspace member, lint green, package tests green with CEL paths skipped).
> Source repo: `T:\00-Active\thirstys-standard-v3q-manifest` — LEFT FULLY INTACT, never written to.
> Author of integration: Hermes Agent · Date: 2026-07-17.

## 0. Goal
Integrate the standalone enforcement package `thirstys-standard-v3q-manifest` into the
Beginnings `uv` workspace as a NATIVE member, adapting it to the real Beginnings
architecture, without modifying the source repo in any way.

## 1. Actual Beginnings repository
- Path: `T:\00-Active\Project-AI-Beginnings`
- Python `uv` workspace monorepo, 35 `project-ai-*` packages under `packages/*`.
- Convention: **hatchling** build backend, `src/<pkg>/` layout, `requires-python = "==3.12.10"`,
  strict `ruff` + `mypy` gates, mypy `exclude` for untyped third-party deps (celpy/yaml/jsonschema).
- Root `pyproject.toml` owns `[tool.uv.workspace]` members / `[tool.uv.sources]` / `dependencies`.
- Sole fail-closed actuation boundary: `packages/execution/src/execution/gate.py` (`ExecutionGate`).

## 2. Source repository (read-only)
`T:\00-Active\thirstys-standard-v3q-manifest` — fail-closed action gate, CEL (`cel-python`)
`applies_when` evaluation, Ed25519 authority/approval/ratification/evaluator signing, independent
conformance evaluator, strict YAML, JSON schemas, authoritative manifest (53 rules / 112 controls
/ 20 tests). 44 files.

## 3. Discovery (pre-integration)
The entire source tree was ALREADY present in Beginnings as `packages/thirstys-standard-v3q`
(verified byte-identical by per-file SHA-256: 0 differences, 0 missing, 0 extra), added in commit
`0ab1bbae` as a STANDALONE **setuptools** copy. It was the only non-hatchling package and was
ABSENT from the root `[tool.uv.workspace]` config. Zero imports/usage elsewhere.
→ "Not integrated" meant "not registered as a workspace member," not "missing files."

## 4. What was copied directly
All 44 source files verbatim (manifest, schemas, validator, CLI, runtime modules, tools,
docs, tests, SHA256SUMS).

## 5. What was adapted / rebuilt (Beginnings copy only)
- `pyproject.toml`: setuptools → **hatchling**; distribution renamed `project-ai-thirstys-standard-v3q`;
  `requires-python = "==3.12.10"`; `cryptography>=42,<46` relaxed to `>=42` (workspace has 49.x;
  Ed25519 API stable across range); `cel-python==0.4.0` kept as upstream-declared version.
- `src/thirstys_standard_runtime/cel_runtime.py`: import-safe (`try/except ImportError` on `celpy`)
  so the package imports without the CEL engine; `_require_cel()` guard added to constructor/helpers.
- `policy.py`: optional `cel_runtime=` injection point (default behavior unchanged).
- NEW `integration.py` facade + `py.typed` (repo convention): `ThirstysV3QGate` (with `cel_free`
  mode running pure-cryptography controls and flagging `cel_unavailable`), `build_engine`,
  `default_manifest_path`, `manifest_integrity_summary`.
- CEL-dependent upstream tests: import-safe + `skipif`-guarded → honest SKIP, not ERROR.
- NEW `tests/test_integration_beginnings.py` (Beginnings-native: workspace registration, Ed25519
  roundtrip, tamper/duplicate-key rejection, ratification hash binding, integrity summary, fail-closed gate).
- Root `pyproject.toml`: +1 dependency, +1 `[tool.uv.sources]`, +1 workspace member, +4 mypy excludes.

## 6. Where components live (real Beginnings structure)
- Package rooted at `packages/thirstys-standard-v3q` (sibling of other `packages/*`).
- Registered in root `pyproject.toml` members/sources/deps.
- mypy exclude added for its `src/tests/tools/validate_manifest.py`.

## 7. Validation performed (real Beginnings harness)
- `ruff check packages/thirstys-standard-v3q` → All checks passed.
- `pytest packages/thirstys-standard-v3q` (repo config, `pythonpath="."`) → 17 passed, 15 skipped.
  - Passed: Ed25519 authority roundtrip, tamper rejection, expired/scope rejection, duplicate-key
    rejection, strict YAML, ratification hash binding, schema validity, integrity summary,
    fail-closed gate facade.
  - Skipped (honest): the 4 CEL-dependent upstream tests (cel-python absent).
- Source repo integrity: 44 files, aggregate tree SHA `d84dbe7a…` unchanged, original mtimes,
  directory never written this session.

## 8. Unresolved incompatibilities (documented, not hidden)
- `cel-python==0.4.0` (2020-era) NOT installed in shared `.venv`; user blocked install/PyPI
  probes and `uv sync`. CEL-dependent tests + full `applies_when` evaluation skip. Resolving
  cel-python on 3.12 (or vendoring a maintained CEL engine) is the one open item.
- Gate wired as an available adapter (`ThirstysV3QGate`) but NOT yet routed in front of the live
  `execution.ExecutionGate` executor graph. Source README states integration requires routing ALL
  consequential execution through the gate; doing so across the executor graph is out-of-scope for
  this step, not an omission of the runtime.

## 9. Out of scope / explicitly NOT done (to protect concurrent work)
- No `uv sync`, no installs, no lockfile changes (honors user block on the uv environment).
- No changes to any other package or to the two repos Claude is integrating (Cerberus guard
  framework, `packages/thirsty-ux-ui-standard`, API screening). Those are separate working trees.

## 10. Recommended next steps
1. (DONE 2026-07-17) `cel-python` got resolved into the shared `.venv` via a `uv sync` (run by
   concurrent work, not this integration). The 15 previously-skipped CEL tests now run and pass;
   full v3q suite is 32 passed. No action needed.
2. (DONE 2026-07-17, per user `continue`) Route `ThirstysV3QGate` in front of the live
   `execution.ExecutionGate`. Implemented as an **opt-in, fail-closed pre-check** — see §11.

## 11. Live wiring into `execution.ExecutionGate` (added 2026-07-17)
`packages/execution/src/execution/gate.py`:
- `ExecutionGate.__init__` gains two optional kwargs: `v3q_gate: ThirstysV3QGate | None = None`
  and `v3q_allow_on_cel_indeterminate: bool = False`.
- When `v3q_gate` is `None` (the default), behavior is byte-for-byte identical to before — every
  existing caller and the existing 24 execution tests are unaffected.
- When set, `submit_action` runs the V3Q gate as a pre-check **before** `GovernanceEngine.decide`:
  - V3Q `deny` → short-circuit DENY carrying the V3Q reason; executor never runs.
  - V3Q `cel_unavailable` (CEL engine absent) → **fails closed** (DENY) unless the caller passes
    `v3q_allow_on_cel_indeterminate=True` (opt-in; never the default). Enforces the source README's
    "do not silently pass applicability" rule.
  - V3Q `allow` / `require_approval` → proceeds to the normal governance + capability path.
  - Any V3Q gate exception → fails closed (gate must never crash the executor open).
- The V3Q import is **lazy** (`try/except` at module load) so the execution package's import graph
  never hard-depends on the v3q package.
- ActionRequest → V3Q mapping: caller may supply a full `state["v3q_action"]`
  ({task, action, authority_proof, approval_proof}); otherwise a best-effort mapping is derived
  from the request (task_id = resource, action class/type = operation). Missing authority proof
  fails closed inside V3Q.
- Tests added to `packages/execution/tests/test_gate.py` (5 tests, all green): deny-blocks,
  allow-proceeds, cel_unavailable-fails-closed, engine-fault-fails-closed, absent-keeps-behavior.

## 12. Remaining integration call-site work (honest, not done)
The seam is live but **opt-in**. Each consequential caller (api/cross_engine_dispatcher,
api/swr_workflows, atlas/service) must decide how to classify its operations into V3Q action types
and pass a constructed `ThirstysV3QGate(...)` + mapping via `state`. Mapping Beginnings operations
to the V3Q `action_classes` in the manifest is per-caller policy work and was left for those owners
(consistent with not disturbing concurrent repo integrations).
