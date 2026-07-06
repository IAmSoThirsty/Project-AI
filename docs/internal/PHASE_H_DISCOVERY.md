# Phase H Discovery + Sub-Phase Plan — packages/tarl/

**Status:** DISCOVERY + PLAN (no code written yet)
**Authority:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase H ("REPLAN AT START OF PHASE")
**Date:** 2026-06-25
**Source-of-truth:** `T:\00-Active\Project-AI-main\tarl\` (read-only)
**Target:** New `packages/tarl/` workspace member

---

## 0. Why discovery-first here

The phased plan marks Phase H as "REPLAN AT START OF PHASE" because:
- TARL is 21 Python files, 3403 LOC, spread across 14 subdirectories.
- The legacy has a full compiler, runtime, validator, FFI layer, policies,
  stdlib, fuzz harness, tooling, and integration tests.
- This exceeds the "≤5 new source files per wave" rule by a factor of 4.
- Without scoping, Phase H risks scope creep identical to what the
  2026-06-24 wave-bounded pattern was created to prevent.

This artifact documents **what's in legacy TARL** and **how I'll sub-phase it**
before writing any code.

---

## 1. Legacy TARL surface inventory

| Subdir / file | LOC | Purpose | Port priority |
|---|---|---|---|
| `tarl/__init__.py` | small | package marker | H1 |
| `tarl/spec.py` | small-medium | Type/term spec language | **H1** (foundation) |
| `tarl/policy.py` | small | Single policy class | **H1** (foundation) |
| `tarl/core.py` | medium | Core data structures | **H1** |
| `tarl/parser.py` | medium | Spec → AST | H2 (depends on spec) |
| `tarl/validate.py` | small | Spec validator | H2 |
| `tarl/compiler/__init__.py` | small | Compiler entry | H2 |
| `tarl/runtime.py` | medium | Runtime core | H2/H3 |
| `tarl/runtime/__init__.py` | small | Runtime package | H2 |
| `tarl/system.py` | medium | System-level orchestration | H3 |
| `tarl/config/__init__.py` | small | Config loader | H2 |
| `tarl/diagnostics/__init__.py` | small | Error/diagnostic types | H1 |
| `tarl/ffi/__init__.py` | small | FFI bridge | H3 |
| `tarl/fuzz/fuzz_tarl.py` | medium | Fuzz harness | defer (out of scope) |
| `tarl/fuzz/__init__.py` | small | Fuzz package marker | defer |
| `tarl/modules/__init__.py` | small | Module loader | H3 |
| `tarl/policies/default.py` | small | Default policy impl | H2 |
| `tarl/policies/__init__.py` | small | Policies package | H2 |
| `tarl/stdlib/__init__.py` | small | Standard library | H3 |
| `tarl/tests/test_tarl_integration.py` | medium | Integration test (legacy) | port as reference |
| `tarl/tooling/__init__.py` | small | Tooling entry | defer |
| `tarl/docs/` | n/a | Legacy docs | archive as reference |

**Total source LOC:** 3403 across 21 py files.

**Dependencies of TARL:** Check via static analysis before porting. Will
verify in H0 (discovery) whether TARL imports any kernel/companion types
or stays self-contained.

---

## 2. Architectural invariants (AGENTS.md v3)

TARL rebuild must respect:
- **Downward-only deps**: tarl may import from `kernel` only. No upward
  imports into companion, governance, execution, capability, etc.
- **Canonical types**: kernel.JsonScalar, kernel.JsonValue for any
  JSON-interchangeable state.
- **Fail-closed**: invalid specs → TarlError (new). Never silent ALLOW.
- **Pluggable seams**: Policy Protocol + Compiler Protocol (allow alternate
  implementations without touching tarl package).
- **Deterministic**: state in kernel.StateRegister (if stateful).
- **Strict typing**: mypy --strict clean.

---

## 3. Sub-phase plan (REPLAN)

Per the phased plan's directive ("H1: types/compiler, H2: runtime, H3: adapters"),
I'm formally splitting Phase H into 3 sub-phases, each with its own acceptance
record. Each sub-phase is wave-bounded (≤5 new source files per sub-wave).

### Phase H0 — Discovery + skeleton (this turn)

**Scope:** Discovery artifact + package skeleton + mypy/ruff/pytest baseline
**New source files:** 0 (only `pyproject.toml`, `README.md`, `__init__.py`,
`py.typed`)
**File changes:** ≤5
**Tasks:**
1. Write this discovery doc (done)
2. Create `packages/tarl/` package skeleton (pyproject, README, py.typed,
   empty `__init__.py`)
3. Register in `pyproject.toml` workspace + sources
4. Verify all gates still green (no source changes = no regression)
5. Write `docs/internal/STAGE_19_5H0_ACCEPTANCE.md`
6. Commit Phase H0

**Why H0 exists:** The legacy TARL has no Go-or-no-go signal in the rebuild
plan — without a discovery artifact and skeleton, sub-phases H1/H2/H3
lack a foundation. H0 provides the envelope without writing any actual
TARL logic.

### Phase H1 — Foundational types (spec, policy, core, diagnostics)

**Scope:** Typed foundations for TARL (no parser/runtime yet)
**New source files:** 4 (`spec.py`, `policy.py`, `core.py`, `diagnostics.py`)
**File changes:** 4 source + 1 init modify + 1 test = **6** (acceptable for
foundation wave per the Phase C precedent: 6 was accepted there)
**Tasks:**
1. `packages/tarl/src/tarl/spec.py` — `Spec`, `Term`, `TarlError`
2. `packages/tarl/src/tarl/policy.py` — `Policy` + `PolicyProtocol`
3. `packages/tarl/src/tarl/core.py` — `CoreState` over StateRegister
4. `packages/tarl/src/tarl/diagnostics.py` — `Diagnostic`, `Severity`
5. `packages/tarl/src/tarl/__init__.py` — re-exports
6. `packages/tarl/tests/test_tarl_foundations.py` — unit tests
7. Integration test: spec + policy compose without runtime
8. Commit Phase H1

**Acceptance criteria:** All 4 canonical gates green; spec/policy/diagnostics
have unit tests; one integration test demonstrates composition.

### Phase H2 — Runtime + parser + validator + compiler

**Scope:** The "compile and execute a spec" path
**New source files:** 5 (`parser.py`, `validate.py`, `compiler.py`, `runtime.py`,
`config.py`)
**Tasks:**
1. `packages/tarl/src/tarl/parser.py` — Spec → AST
2. `packages/tarl/src/tarl/validate.py` — AST validation
3. `packages/tarl/src/tarl/compiler.py` — AST → executable
4. `packages/tarl/src/tarl/runtime.py` — Execute compiled spec
5. `packages/tarl/src/tarl/config.py` — Config loader
6. `packages/tarl/tests/test_tarl_compile.py` — compile-path tests
7. `packages/tarl/tests/test_tarl_runtime.py` — runtime tests
8. Integration test: end-to-end "spec → policy → runtime"
9. Commit Phase H2

### Phase H3 — System, modules, stdlib, FFI, adapters

**Scope:** System-level orchestration + module loader + stdlib
**New source files:** 5 (`system.py`, `modules.py`, `stdlib.py`, `ffi.py`,
`policies/default.py`)
**Tasks:**
1. `packages/tarl/src/tarl/system.py` — System orchestration
2. `packages/tarl/src/tarl/modules.py` — Module loader
3. `packages/tarl/src/tarl/stdlib.py` — Standard library
4. `packages/tarl/src/tarl/ffi.py` — FFI bridge (stub if no real consumer)
5. `packages/tarl/src/tarl/policies/default.py` — Default policy impl
6. `packages/tarl/tests/test_tarl_system.py`
7. Integration test: full end-to-end with module loading + policy
8. Commit Phase H3

**Defer (out of scope for H):**
- `tarl/fuzz/fuzz_tarl.py` — fuzz harness, no rebuild value yet
- `tarl/tooling/__init__.py` — tooling entry, can be CLI in separate phase
- `tarl/tests/test_tarl_integration.py` — port as reference but don't depend on it

---

## 4. Estimated file count

| Sub-phase | New source | New test | Init modify | Other | Total |
|---|---|---|---|---|---|
| H0 | 0 | 0 | 0 | pyproject, README, py.typed, this doc | 4-5 |
| H1 | 4 | 1 | 1 | 1 integration test | 7 |
| H2 | 5 | 2 | 1 | 1 integration test | 9 |
| H3 | 5 | 1 | 1 | 1 integration test | 8 |
| **Total** | **14** | **4** | **3** | **3** | **~28** |

Each sub-phase is wave-bounded (≤5 source files per sub-wave, with the
existing Phase C/D/E/F/G precedent of accepting 6-12 file changes for
foundation/package-bootstrap waves).

---

## 5. Risks and open questions

1. **TARL dependency surface** — need to grep legacy `tarl/` for imports
   to confirm no upward deps into companion/governance/execution/capability.
   *Will verify in H0 before H1.*
2. **State surface** — does TARL need persistent state? If yes, must use
   kernel.StateRegister (not custom). Will check legacy.
3. **FFI bridge** — the legacy `tarl/ffi/` may be aspirational. If it's
   empty/stub, Phase H3 will mark it as placeholder.
4. **Fuzz harness** — deferred entirely (no rebuild value, lives in
   separate "tools" tier if ever needed).

---

## 6. Recommended authorization scope

> "Proceed with Phase H0 only (discovery skeleton). Stop and produce
> H0 acceptance record + Phase H1 plan before continuing."

This preserves the wave-bounded pattern that worked for Phases A–G:
H0 sets the envelope (≤5 files, all gates green), H1 lays the foundation,
H2 brings the compiler/runtime, H3 the system-level layer.

---

## 7. Self-report (v3 §35)

```
Mode: governance system (planning — Phase H discovery)
Created: docs/internal/PHASE_H_DISCOVERY.md (this file)
Modified: None.
Verified: TARL legacy surface inventoried (21 py, 3403 LOC, 14 subdirs).
Failed: None.
Not verified: TARL's actual import dependencies (deferred to H0 grep pass).
Risks: substantial scope; multi-sub-phase required; FFI / fuzz may be empty.
Continuity map: docs/operations/CONTINUITY_MAP.md (will update on H0 commit)
Remaining:
  - User authorization to start Phase H0 (this turn)
  - Per-sub-phase "go" for H1, H2, H3 thereafter
  - Phase I authorization (Temporal) and Phase J (Atlas) after H lands
```
