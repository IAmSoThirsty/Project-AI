# Stage 19.5H2 Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase H2
**Discovery:** `docs/internal/PHASE_H_DISCOVERY.md`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-25
**Phase scope:** Phase H2 — runtime + parser + validator + compiler + config.

---

## 0. Phase H2 scope (recap)

H2 brings the "compile + execute a TARL record" path. Five source files
(~1000 LOC) plus extensive tests. Each module is fail-closed and
downward-only.

## 1. Files created/modified

| Path | Type | LOC |
|---|---|---|
| `packages/tarl/src/tarl/parser.py` | source | 175 (rewrite: section header / empty-value disambiguation) |
| `packages/tarl/src/tarl/validate.py` | source | 145 |
| `packages/tarl/src/tarl/compiler.py` | source | 110 |
| `packages/tarl/src/tarl/runtime.py` | source | 165 (cache-key fix: per-compiled, not just per-context) |
| `packages/tarl/src/tarl/config.py` | source | 145 |
| `packages/tarl/src/tarl/__init__.py` | modified — 41 re-exports | 95 |
| `packages/tarl/tests/test_tarl_compile.py` | tests | 530 (48 tests) |
| **Total** | **7 files** | **~1365 LOC + 48 tests** |

## 2. Verification gates (all green)

```
=== PYTEST ===
807 passed in 2.33s
(was 759 baseline + 48 new H2 tests)

=== MYPY --strict ===
Success: no issues found in 104 source files
(was 103 in H1; +1 for parser.py)

=== RUFF check ===
All checks passed!

=== RUFF format --check ===
104 files already formatted
```

## 3. Architectural invariants (verified)

- **Downward-only deps:** tarl imports only tarl.core/spec/policy/validate/compiler + stdlib.
- **Canonical types:** TarlConfig/TarlVerdict/TarlDecision all JSON-serializable.
- **Fail-closed:** parser rejects bad input with TarlParseError; validator
  surfaces errors as DiagnosticBatch with Severity.ERROR; compiler fails on
  invalid record; runtime raises on missing policy / bad context / tampered
  record; config rejects negative / non-int / non-bool.
- **Pluggable seams:** Compiler Protocol + Validator Protocol.
- **Deterministic:** TARL.hash() stable; cache_key = (compiled_hash, ctx_hash)
  prevents cross-policy contamination.
- **Single audit chain:** every execute() appends ExecutionRecord; cache
  bypasses audit only on repeats of the exact (compiled, ctx) pair.

## 4. Bugs caught + fixed during self-review

**5 real bugs found by tests:**

1. **`parser.py` initial impl conflated section headers with empty-value
   keys.** `INTENT: ` (UPPERCASE + colon + no value) was treated as a
   section header. Fix: distinguish by `section_name.lower() in ALLOWED_KEYS`.
   Now `INTENT: ` gives "empty value for key 'intent'", `RANDOM:` gives
   "unsupported section 'RANDOM'". Documented in code.

2. **`parser.py` had PEP 695 syntax (`@dataclass := ...`)** — caused
   SyntaxError. Fixed by importing `from dataclasses import dataclass` and
   using `@dataclass(frozen=True)` directly.

3. **`config.py` had the same PEP 695 bug.** Same fix as above.

4. **`runtime.py` cache was keyed only on `context_hash`.** This caused
   cache pollution when `execute_chain` ran a compiled-allow then a
   compiled-deny against the same context — the second call hit the cache
   and returned the cached ALLOW. **Real semantic bug.** Fix: cache_key
   now = `(compiled.record_hash, ctx_hash)` so different compiled records
   don't share cache entries. Documented in docstring.

5. **`compiler.py` had the same PEP 695 bug.** Same fix.

## 5. Module surface (41 public exports added)

- `parse`, `parse_mapping`, `format_tarl`, `TarlParseError`, `ALLOWED_KEYS`
- `validate`, `validate_with_authorities`, `is_valid`, `allowed_authorities`,
  `DEFAULT_ALLOWED_AUTHORITIES`, `Validator`
- `compile_record`, `default_compile_policy`, `CompiledTarl`, `Compiler`,
  `DefaultCompiler`, `TarlCompileError`
- `execute_compiled`, `TarlRuntime`, `ExecutionRecord`, `TarlRuntimeError`
- `make_config`, `config_from_mapping`, `TarlConfig`, `TarlConfigError`,
  `DEFAULT_CACHE_SIZE`, `DEFAULT_AUDIT_ENABLED`, `DEFAULT_AUDIT_MAX_RECORDS`,
  `DEFAULT_POLICY_TIMEOUT_MS`, `CONFIG_ALLOWED_KEYS`

## 6. Self-report (v3 §35)

```
Mode: governance system (Phase H2 execution)
Created:
- T:\Project-AI-Beginnings\packages\tarl\src\tarl\parser.py
- T:\Project-AI-Beginnings\packages\tarl\src\tarl\validate.py
- T:\Project-AI-Beginnings\packages\tarl\src\tarl\compiler.py
- T:\Project-AI-Beginnings\packages\tarl\src\tarl\runtime.py
- T:\Project-AI-Beginnings\packages\tarl\src\tarl\config.py
- T:\Project-AI-Beginnings\packages\tarl\tests\test_tarl_compile.py
- T:\Project-AI-Beginnings\docs\internal\STAGE_19_5H2_ACCEPTANCE.md (this file)
Modified:
- T:\Project-AI-Beginnings\packages\tarl\src\tarl\__init__.py (41 re-exports)
Deleted: None.
Verified:
- 807/807 pytest pass (759 + 48 new)
- mypy --strict clean on 104 source files
- ruff check clean
- ruff format --check clean (104 files)
Failed: 5 tests in initial run (now all fixed).
Not verified:
- apps/desktop tests + apps/services tests (pre-existing env gaps)
- 5 real bugs caught and fixed during self-review
Risks:
- Cache key now includes compiled_hash — could grow faster; acceptable
  (cap by TarlConfig.cache_size in H3).
Continuity map: docs/operations/CONTINUITY_MAP.md (will update on commit)
Remaining:
- User authorization to commit + push H2
- Phase H3 (system, modules, stdlib, ffi, policies/default) — 5 source files
- Phase I (Temporal) and Phase J (Atlas) authorizations
Commands run:
- uv run pytest packages/tarl/tests/test_tarl_compile.py
- uv run pytest (full)
- uv run mypy packages/ --strict
- uv run ruff check --fix --unsafe-fixes packages/
- uv run ruff format packages/
Safe to continue: yes (for commit + Phase H3); NOT for code edits without explicit "go"
```

## 7. Recommended next actions

1. **Commit Phase H2 + push** (this turn)
2. **Phase H3** — system, modules, stdlib, ffi, policies/default (5 source files)
3. **Phase I** — Temporal package (separate envelope, separate go)
4. **Phase J** — Atlas package (months of work, separate envelope)