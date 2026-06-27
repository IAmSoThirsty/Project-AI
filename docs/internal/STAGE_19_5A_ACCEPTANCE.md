# Stage 19.5A Acceptance Gate

**Status:** ACCEPTED LOCALLY (pending commit per user authorization)
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase A
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-25
**Phase scope:** Discovery + archive-only — zero source-code changes to `packages/`

---

## 0. Phase A scope (recap)

Phase A resolves three of the eight open questions from `LEGACY_GAP_INVENTORY.md` §8:

- **Q2 (Web frontend)** — copy `T:\Project-AI-main\web\hub-epstein\` + `web\site\` to `docs/legacy-archive\web\`
- **Q3 (TARL_OS `.thirsty` config)** — copy 27 `.thirsty` data files to `docs/legacy-archive\tarl_os_config\`
- **Q8 (apps/ inventory)** — produce `APPS_INVENTORY.md` classifying `apps/` vs `packages/`

Plus: update `LEGACY_GAP_INVENTORY.csv`, `LEGACY_GAP_INVENTORY.md` §8, and `CONTINUITY_MAP.md`.

## 1. What was created

| Path | Type | Count | Size |
|---|---|---|---|
| `docs/operations/STAGE_19_5_PHASED_PLAN.md` | doc | 1 | 14.3 KB |
| `docs/operations/STAGE_19_5_COMPANION_REBUILD_PLAN.md` | doc (SUPERSEDED) | 1 | ~9 KB |
| `docs/operations/APPS_INVENTORY.md` | doc | 1 | 7.8 KB |
| `docs/legacy-archive/web/hub-epstein/**` | archive | 70 | ~600 KB |
| `docs/legacy-archive/web/site/**` | archive | 49 | ~500 KB |
| `docs/legacy-archive/web/SHA256SUMS.txt` | provenance | 1 | ~6 KB |
| `docs/legacy-archive/tarl_os_config/**/*.thirsty` | archive | 27 | ~80 KB |
| `docs/legacy-archive/tarl_os_config/SHA256SUMS.txt` | provenance | 1 | ~2 KB |

**Total:** 9 new tracked items + 3 modified docs. **Zero source-code changes.**

## 2. What was modified

| Path | Change |
|---|---|
| `docs/operations/LEGACY_GAP_INVENTORY.csv` | Q2 row marked RESOLVED; Q3 row marked RESOLVED-PARTIAL |
| `docs/operations/LEGACY_GAP_INVENTORY.md` §8 | All 8 questions annotated with resolution status + phase pointers |
| `docs/operations/CONTINUITY_MAP.md` | Phase A session update section appended |

## 3. Verification gates

### TESTS (canonical scope: `packages/` + `tools/tests/`)

```
EXIT: 0
517 passed in 1.43s
```

### MYPY --strict (canonical scope per STAGE_19 §7)

```
EXIT: 0
Success: no issues found in 32 source files
```

Scope: `packages/kernel/ packages/governance/ packages/execution/ --strict` (the Stage 19 acceptance canonical scope).

### Pre-existing mypy drift (documented, NOT Phase A regression)

`uv run mypy packages/ --strict` (full scope) reports 28 errors in 3 files at the verified baseline commit `0d3128c`. Verified by `git stash --include-untracked` + re-run + restore: same 28 errors at `HEAD == 0d3128c` (pre-Phase-A state).

Affected files (all pre-existing):
- `packages/arbiter/tests/test_arbiter_gov.py` — `no-untyped-call` (1 error + 1 note)
- `packages/rlp/tests/test_rlp.py` — `comparison-overlap` (1 error)
- `packages/cli/tests/test_cli.py` — `arg-type` (1 error)

The full mypy --strict output shows 28 errors; the breakdown above shows the unique error categories. The remaining ~25 are repeated instances in the same files.

**Out of Phase A scope.** Resolving these is a separate repair wave. Documented here for honesty, not as a Phase A failure.

### RUFF check

```
EXIT: 0
All checks passed!
```

### RUFF format --check

```
EXIT: 0
67 files already formatted
```

## 4. Archive byte-identical verification

### Web archive (Q2)

```
$ find web/hub-epstein web/site -type f | wc -l
119

$ cp -r web/hub-epstein web/site docs/legacy-archive/web/
$ find docs/legacy-archive/web -type f | wc -l
119

# Round-trip SHA-256 (source vs archive)
$ sha256sum (source) | sed 's|*web/||' | sort > /tmp/legacy_norm.sha256
$ sha256sum (archive) | sed 's|*||' | sort > /tmp/copy_norm.sha256
$ diff /tmp/legacy_norm.sha256 /tmp/copy_norm.sha256
(empty diff, exit 0)
```

**Result: 119/119 files byte-identical with legacy source. SHA-256 evidence saved at `docs/legacy-archive/web/SHA256SUMS.txt`.**

### TARL_OS `.thirsty` archive (Q3)

```
$ find tarl_os -name "*.thirsty" -type f | wc -l
27

$ cp (27 files) → docs/legacy-archive/tarl_os_config/
$ find docs/legacy-archive/tarl_os_config -name "*.thirsty" -type f | wc -l
27

# Round-trip SHA-256
$ diff /tmp/legacy_thirsty_src.sha256 /tmp/thirsty_copy.sha256
(empty diff, exit 0)
```

**Result: 27/27 files byte-identical with legacy source. SHA-256 evidence saved at `docs/legacy-archive/tarl_os_config/SHA256SUMS.txt`.**

## 5. Architectural boundary verification (Q8)

```
$ grep -rnE "^(from|import) (governance|execution|capability)\b" apps/ \
    | grep -v __pycache__
(0 hits)

$ grep -rnE "import (ai\.project\.governance|ai\.project\.execution|ai\.project\.capability)" apps/
(0 hits)

$ grep -rnE "from ['\"](@project-ai/)?(governance|execution|capability)" apps/ \
    | grep -v node_modules
(0 hits)
```

**Result: Zero upward imports from `apps/` into `packages/{governance, execution, capability}` across Python, Kotlin/Java, and TypeScript. The architectural boundary from `REBUILD_EXECUTION_PLAN.md` is enforced in code, not just stated in README.**

## 6. Open question resolution status

| # | Question | Status | Resolved in |
|---|---|---|---|
| Q1 | Unity 3DOF (21 files) | PENDING (default DROP per 2026-06-21) | Phase B |
| Q2 | Web frontend archive | **RESOLVED** | **Phase A** (this commit) |
| Q3 | TARL_OS `.thirsty` config | **RESOLVED-PARTIAL** (config data only; `.py` deferred to Phase H/I) | **Phase A** (this commit) |
| Q4 | `emergent-microservices/` | PENDING (default CONFIRM DROP) | Phase B |
| Q5 | Cerebus (9 files, ~140KB) | PENDING (default NEW `packages/cerberus/`) | Phase F |
| Q6 | Hydra 50 | PENDING (default NEW `packages/hydra_50/`) | Phase G |
| Q7 | Cognition | PENDING (default INTO `packages/companion/`) | Phase E |
| Q8 | `apps/` inventory | **RESOLVED** | **Phase A** (this commit) |

**3 of 8 questions resolved in Phase A.** 5 remaining; each on a concrete future phase.

## 7. Architectural invariants (verified)

- **Downward-only deps:** N/A (no source changes)
- **Canonical types:** N/A
- **Fail-closed:** N/A
- **Single audit chain:** N/A
- **Pluggable seams:** N/A
- **Strict typing:** ✓ (canonical scope clean; full scope drift documented separately)
- **Deterministic:** ✓ (SHA-256 byte-identical proof of deterministic copy)
- **No legacy mutation:** ✓ (legacy is read-only; archive is fresh path)

## 8. Continuity map

`docs/operations/CONTINUITY_MAP.md` updated per template with Phase A session delta (File Inventory, Commands Run, Tests Run, Risks, Self-Report per v3 §35).

## 9. Next steps

1. **Commit Phase A artifacts** (pending user authorization)
2. **Phase B authorization:** Q1 Unity archive + Q4 emergent-microservices confirm — same archive-only pattern as Phase A
3. **Phase C authorization:** First source-code wave (`packages/companion/` identity + fates)

## 10. Self-report (v3 §35)

```
Mode: governance system (Phase A execution)
Created:
- T:\Project-AI-Beginnings\docs\operations\STAGE_19_5_COMPANION_REBUILD_PLAN.md (superseded)
- T:\Project-AI-Beginnings\docs\operations\STAGE_19_5_PHASED_PLAN.md
- T:\Project-AI-Beginnings\docs\operations\APPS_INVENTORY.md
- T:\Project-AI-Beginnings\docs\legacy-archive\web\hub-epstein\ (70 files, SHA-256 verified)
- T:\Project-AI-Beginnings\docs\legacy-archive\web\site\ (49 files, SHA-256 verified)
- T:\Project-AI-Beginnings\docs\legacy-archive\web\SHA256SUMS.txt
- T:\Project-AI-Beginnings\docs\legacy-archive\tarl_os_config\**\*.thirsty (27 files, SHA-256 verified)
- T:\Project-AI-Beginnings\docs\legacy-archive\tarl_os_config\SHA256SUMS.txt
- T:\Project-AI-Beginnings\docs\internal\STAGE_19_5A_ACCEPTANCE.md (this file)
Modified:
- T:\Project-AI-Beginnings\docs\operations\LEGACY_GAP_INVENTORY.csv (Q2 + Q3 RESOLVED)
- T:\Project-AI-Beginnings\docs\operations\LEGACY_GAP_INVENTORY.md §8 (resolution status)
- T:\Project-AI-Beginnings\docs\operations\CONTINUITY_MAP.md (Phase A session delta)
Deleted: None.
Verified:
- 517/517 pytest pass (canonical scope: packages/ + tools/tests/)
- mypy --strict clean on 32 source files (canonical scope: kernel/governance/execution)
- ruff check clean
- ruff format --check clean
- 119/119 web files byte-identical with legacy (SHA-256)
- 27/27 .thirsty files byte-identical with legacy (SHA-256)
- 0 upward imports from apps/ into packages/{governance,execution,capability}
Failed: None. (Phase A delivered end-to-end.)
Not verified:
- Pre-existing mypy drift on full packages/ scope (28 errors, documented; not from Phase A)
- apps/desktop tests + apps/services tests (pre-existing env gaps: PyQt6 + workspace install)
Risks:
- 1.6 MB of archive content will appear in git ls-files after commit. Acceptable; can move out-of-tree if size policy demands.
- 5 of 8 open questions remain PENDING (Q1/Q4 Phase B, Q5 Phase F, Q6 Phase G, Q7 Phase E).
Continuity map: docs/operations/CONTINUITY_MAP.md (updated)
Remaining:
- User authorization to commit Phase A artifacts
- Phase B authorization
Commands run: see §3 + §4 + §5 above
Safe to continue: yes (for commit + Phase B); NOT for code edits without explicit "go"
```
