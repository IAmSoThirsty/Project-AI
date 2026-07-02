# J5 Discovery: Atlas Safeguards + Config + Schemas Port

Per user directive 2026-07-01 ("all-in integration, drive
wave-by-wave") and `docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md`
section 6 (Atlas staging residue), this phase ports the
remaining critical Atlas modules that are not yet in
canonical:

- **Epistemic Safeguards** (CRITICAL safety layer) -
    `packages/atlas/src/atlas/safeguards/epistemic_safeguards.py`
- **Config Loader + 6 YAML configs** - runtime-tunable config
- **Schemas Validator + 6 JSON schemas** - schema validation
    for evidence, claims, opinions, organizations, world
    state, projection packs, influence graphs

All three modules are currently NOT in canonical
(`packages/atlas/src/atlas/` has no `safeguards/`,
`config/`, or `schemas/` subpackages). The legacy has them
in 2 locations:
- `/t/Project-AI-main/atlas/` (older)
- `/t/Project-AI-main/engines/atlas/` (newer, May 19 2026)

Per pitfall 1 (trust source files over memory), the canonical
source is the `engines/` copy. The `atlas/` copy is older
(but identical in surface).

Per pitfall 11 (state what changed), each wave introduces
new code in `packages/atlas/src/atlas/{safeguards,config,schemas}/`
plus a comprehensive integration test in `tests/`. The atlas
package init will be updated to expose the new public surface.

Per pitfall 16 (pre-existing baseline drift), the 10 mypy
errors are pre-existing and unchanged. The J5 work should
add zero new mypy drift.

Per pitfall 35 (pre-existing functional packages), the atlas
package is already functional. J5 adds new subpackages but
does not modify existing surface.

Per pitfall 43 (workspace vs external PyPI deps), PyYAML is
needed for the config loader. It is a standard PyPI dep.
jsonschema is needed for the schema validator. Both are
PyPI deps that should go in `packages/atlas/pyproject.toml`
dependencies.

Per pitfall 47 (hermes-verify scripts at tempdir), the J5
hermes-verify scripts will follow the v2 pattern.

Per pitfall 66 (no inline -c), all hermes-verify logic will
be written to file then `uv run python <file>`.

---

## Scope

### J5.1 - Epistemic Safeguards (CRITICAL SAFETY LAYER)

**Legacy:** `/t/Project-AI-main/engines/atlas/safeguards/epistemic_safeguards.py`
(~586 LOC)

**Public surface (8 classes + 1 factory):**
- `DecisionBasis` enum (4 values: INFORMED_BY_ATLAS,
  INFORMED_AND_VALIDATED, INDEPENDENT_OF_ATLAS,
  CONTRADICTS_ATLAS)
- `Decision` dataclass (record of decision with ATLAS
  involvement tracking)
- `EpistemicGravityMitigation` class (prevent cognitive
  anchoring to ATLAS outputs)
- `QueryType` enum (4 values: NORMATIVE, PREDICTIVE,
  DESCRIPTIVE, META)
- `QueryValidation` dataclass (result of query validation)
- `PromptFramingGuards` class (mechanical rejection of
  normative queries)
- `ResponsibilityClause` dataclass (non-transferable
  responsibility clause)
- `OutputRecord` dataclass (record of generated output)
- `ResponsibilityBoundaryEnforcement` class (enforce
  non-transferable responsibility)
- `EpistemicSafeguardSystem` class (unified safeguard
  facade, combines all 3 safeguards)
- `get_epistemic_safeguards()` factory (singleton)

**Subordination notice:** "CRITICAL: These safeguards
protect against ATLAS Ω becoming de facto authority."

**Estimated tests:** ~30 tests

### J5.2 - Config Loader + 6 YAML Configs

**Legacy:** `/t/Project-AI-main/engines/atlas/config/loader.py`
(~200 LOC) + 6 YAML files:
- `drivers.yaml` (driver coefficients)
- `penalties.yaml` (penalty values)
- `safety.yaml` (safety thresholds)
- `seeds.yaml` (default seeds)
- `stacks.yaml` (stack definitions)
- `thresholds.yaml` (operational thresholds)

**Public surface:**
- `ConfigLoader` class with `load_config(name)` + `merge_overrides`
  + `validate_config` + `save_config` methods
- `get_config_loader()` factory
- 6 YAML config files copied to
  `packages/atlas/src/atlas/config/*.yaml`

**Estimated tests:** ~15 tests

### J5.3 - Schemas Validator + 6 JSON Schemas

**Legacy:** `/t/Project-AI-main/engines/atlas/schemas/validator.py`
(~300 LOC) + 6 JSON schema files:
- `claim.schema.json`
- `influence_graph.schema.json`
- `opinion.schema.json`
- `organization.schema.json`
- `projection_pack.schema.json`
- `world_state.schema.json`

**Public surface:**
- `SchemaValidator` class with `validate_claim` +
  `validate_world_state` + `validate_opinion` +
  `validate_organization` + `validate_projection_pack` +
  `validate_influence_graph` + `validate_any` methods
- `get_schema_validator()` factory
- 6 JSON schema files copied to
  `packages/atlas/src/atlas/schemas/*.json`

**Estimated tests:** ~18 tests

---

## Out of scope (J5)

- The remaining staging residue items (ingester, tier
  classifier, normalizer, projections simulator, scorer,
  calculator, council) - these are not safety-critical and
  are deferred to a future phase
- The "epistemic safeguards" overlap with J2.5
  constitutional kernel - they are DISTINCT layers (one is
  about cognitive anchoring, the other about constitutional
  principles)
- The atlas `bayesian.py` and `driver_engine.py` are
  already in canonical (J2.3, J2.4b) - SUPERSEDED status,
  no work needed

---

## Wave plan

| Wave | Module | LOC est | Tests est | Commits |
|---|---|---|---|---|
| J5.0 | envelope (this doc) | - | 0 | 1 |
| J5.1 | safeguards/epistemic_safeguards.py | 586 | 30 | 1 |
| J5.2 | config/loader.py + 6 YAML | 200 | 15 | 1 |
| J5.3 | schemas/validator.py + 6 JSON | 300 | 18 | 1 |
| **Total** | | **~1086** | **~63** | **4** |

J5 will be 4 commits, ~1086 new LOC, ~63 new tests, 0 new
mypy drift.

After J5: 5 of the 8 staging residue items remain
(non-critical: ingester, tier_classifier, normalizer,
projections simulator, scorer, calculator, council). The
"critical safety layer" and "runtime-tunable config" and
"schema validator" gaps will be closed.

---

## Architectural invariants (THIRSTYS STANDARDS V3)

- **Port specifically for Beginnings**: every port is in
  `packages/atlas/src/atlas/`. Use frozen dataclasses per
  the J3 pattern; match existing atlas style.
- **Audit trail integration**: the canonical atlas exposes
  `get_audit_trail` at the top level
  (`from atlas import get_audit_trail`). The legacy used
  `from atlas.audit.trail import get_audit_trail`. J5 uses
  the canonical import.
- **YAML/JSON dependencies**: PyYAML and jsonschema are
  PyPI deps. They should be added to
  `packages/atlas/pyproject.toml` `[project].dependencies`
  per pitfall 43.
- **Tests are first-class**: ~63 new tests cover public
  surface + edge cases + invariants + safety semantics +
  factory singletons.
- **T7 convergence preserved**: hash unchanged at
  `3eda3256049339cb069354cc81ee7c51d88e3e41e81ea707e5bf3d3e14ba478c`.
- **Honest scope corrections**: documented in each commit
  message, including limitations and what was simplified.

---

## Verification plan

Each wave:
1. Write the source file
2. Write the integration test
3. Run J5.x tests in isolation
4. Run full pytest
5. Run mypy on the new file + full
6. Run ruff + format
7. Update atlas package init to expose new public surface
8. Re-run all gates
9. Commit + push
10. hermes-verify script (v2 pattern)
11. Re-verify canonical gates
