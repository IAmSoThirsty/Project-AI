# project-ai-convergence

Shadow-Thirst (6th tier) convergence harness across all Thirsty-Lang
tier specs in Project-AI Beginnings.

Per `docs/internal/PHASE_T_DISCOVERY.md` Phase T7: the 6th tier is
a meta-validation surface that runs all 5 prior tier specs (T2, T3,
T5, T5b) and confirms they converge on a single truth.

## What this package does

`convergence.shadow_thirst.run_convergence()` loads each tier spec:

  - **T1** (workspace dep + smoke): meta-wiring, no language spec
  - **T2** (governance `.tarl` policy): bundled with `project-ai-governance`
  - **T3** (security `.thirst` proof obligations): bundled with `project-ai-security`
  - **T4** (operator CLI sub-app): meta-wiring, no language spec
  - **T5** (atlas `.tscg` spec): bundled with `project-ai-atlas`
  - **T5b** (SWR `.tscg-b` spec): bundled with `project-ai-swr`

For each, the harness builds a `TierWitness` with the canonical
form, source SHA-256, canonical SHA-256, and a structural
convergence check. The combined `convergence_hash` (SHA-256 of
the concatenation of all witnesses' canonical SHA-256s) is the
single proof that the integration is internally consistent.

## What convergence means here

For T7, "convergence" means:

  1. All 6 tier witnesses are constructible.
  2. All 4 language-tier specs (T2, T3, T5, T5b) have stable
     canonical forms and valid SHA-256 hashes.
  3. All 4 language-tier specs pass the structural pass
     (alpha-renamed AST equality; trivially satisfied because
     each spec is its own canonical).
  4. The combined `convergence_hash` is deterministic across
     successive runs.

## What's NOT in T7

  - **Z3 symbolic pass**: requires `thirsty-lang[analysis]` extras.
    Deferred to T7.5.
  - **Execute-and-compare pass**: requires a sandboxed interpreter
    and seeded inputs. Deferred to T7.5.

These are documented in `docs/internal/PHASE_T_DISCOVERY.md`
Phase T7 as the post-integration hardening scope.

## Architectural invariants (AGENTS.md v3)

- **Downward-only deps**: convergence imports atlas, governance,
  security, swr (the 4 packages with language specs) and the
  thirsty-lang dep.
- **Fail-closed**: a non-converging integration is never silently
  bypassed. `ConvergenceError` is raised on any failure that
  prevents the harness from running.
