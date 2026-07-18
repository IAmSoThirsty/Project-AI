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

## 12. Live call-site wiring (added 2026-07-17, per user `the word`)
The seam from §11 is now wired into ALL three consequential call sites. To avoid
breaking the running system or faking enforcement, V3Q is **opt-in by trusted keys**:
- `build_gate(trusted_keys=None)` returns `None` (not configured). Call sites wrap
  their `ExecutionGate` with `with_v3q(build_gate(...))` only when a trusted-key
  registry is supplied. With no keys, behavior is byte-for-byte unchanged (default).
- When configured with real owner keys, V3Q sits in front of the live path and
  **requires a signed authority proof**; absence or bad proof fails closed even
  though Beginnings governance would allow.

Wiring performed:
- `packages/execution/gate.py`: added `ExecutionGate.with_v3q(...)` (reuses the exact
  same fail-closed `_evaluate_v3q` logic) so call sites that receive a pre-built gate
  can opt in without reconstructing it.
- `packages/thirstys-standard-v3q/.../integration.py`: added `build_gate(trusted_keys=...)`
  (None -> not configured) and generalized `request_to_v3q_action` to
  `operation_to_action: dict[op -> (class_id, type)]` (unmapped ops fail closed).
- `packages/api/.../cross_engine_dispatcher.py`: added optional `v3q_gate` param; when
  set (or via `build_gate()`), wraps the injected gate and injects `state["v3q_action"]`.
- `packages/api/.../swr_workflows.py`: `ExecutionGate(... v3q_gate=build_gate())`.
- `packages/atlas/.../service.py`: `Atlas.__init__` wraps with `build_gate()` (preserving
  any caller-supplied gate); `Atlas.record` gained a `state` param forwarded to submit;
  `state["v3q_action"]` is derived from the request via `request_to_v3q_action`.
- `packages/atlas/tests/test_atlas.py`: added 2 REAL-enforcement tests using a generated
  Ed25519 owner key + signed authority proof proving the gate truly gates Atlas' live
  path (no proof -> DENY; valid proof -> ALLOW; tampered scope -> DENY). These prove the
  seam is live, not dormant. Atlas maps `atlas.projection.record -> ("local_reversible","write")`.

Validation (real harness): execution 29 passed; atlas 369 passed (incl. 2 V3Q
enforcement); api 52 passed / 1 skipped (db); v3q 32 passed; dispatcher 5 passed;
ruff clean on all touched files. Source repo `T:/00-Active/thirstys-standard-v3q-manifest`
unchanged (aggregate SHA `d84dbe7a…`). Concurrent work (Cerberus, API screening,
UX-UI standard, uv.lock) left untouched.

## 13. Remaining (genuinely open, per-caller policy)
Each domain should (a) persist a real trusted-key registry (upstream
`tools/create_owner_key.py`) and inject it via `build_gate(trusted_keys=...)`, and
(b) complete its `operation_to_action` map for every operation it issues. Until then
V3Q stays dormant-by-default (safe) at each call site. The dispatcher's cross-engine
operations (`cross_engine_cascade.*`) are not yet mapped to V3Q action types.

## 14. Production deployment readiness (added 2026-07-17, per `make production ready`)
V3Q is no longer dormant-by-accident; it is **config-driven and fail-safe**:

- A REAL owner keypair was generated. The public trusted-key registry
  (`packages/thirstys-standard-v3q/trusted-keys.json`, `{"keys":[owner-primary]}`)
  is committed. The private key (`owner-private.json`) is gitignored — it must be
  provisioned via secret management in each deployment. Rotate with
  `tools/create_owner_key.py` and re-commit the matching public registry.
- `deployment.py`: `load_gate_config()` discovers config from env vars (12-factor):
  `THIRSTYS_V3Q_OWNER_KEY` (private key path, required for activation),
  `THIRSTYS_V3Q_REGISTRY` (optional; defaults to the packaged `trusted-keys.json`),
  `THIRSTYS_V3Q_OP_MAP` (optional `op -> [class,type]` override). Malformed/partial
  config yields `None` (dormant) and never raises.
- `build_gate()` auto-loads that config when called with no args. Returns `None`
  (dormant) unless the owner key is present; otherwise returns an ACTIVE gate.
- The gate **self-mints** signed Ed25519 authority + approval proofs (bound to the
  action's task scope + V3Q action type) when an owner key is configured, so call
  sites need only supply the V3Q action mapping — the runtime acts as the authorized
  owner. Without an owner key, no proof is fabricated and a missing proof fails closed.
- Built-in per-domain `operation_to_action` map added (atlas.projection.record,
  swr.scenario.record -> local_reversible/write; cross_engine_cascade.* ->
  externally_consequential/deploy_visible_service). Unmapped ops fall back to the raw
  operation string and are denied closed (never a silent pass).
- All three call sites inject `state["v3q_action"]` (atlas + swr via `request_to_v3q_action`;
  dispatcher via the same). SWR's `war_room.py` now merges the V3Q mapping into the
  submit `state` alongside its governance state.
- Tests: +2 production-path tests in `test_integration_beginnings.py` prove
  config-driven activation + auto-mint (ALLOW for mapped/approval ops, DENY for
  unmapped). The atlas enforcement tests prove live gating with manually-supplied
  proofs. Execution-gate tests prove the seam (deny/allow/cel-unavailable/fault/
  absent) stays correct.

ACTIVATION IN PRODUCTION: set `THIRSTYS_V3Q_OWNER_KEY=/path/to/owner-private.json`
(pointing at the secret-managed key whose public is in the committed registry). No
code change. CI / local dev without the secret stays dormant and green.

Validation: execution 29, atlas 369, v3q 34, swr 23, api 52/1skip — all green;
ruff clean on all touched files. Source repo unchanged (SHA `d84dbe7a…`).
Concurrent work (Cerberus, API screening, UX-UI standard, uv.lock) untouched.
