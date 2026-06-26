# project-ai-hydra-50

Threat scenario surface for Project-AI Beginnings. Closes Q6 from
`docs/operations/LEGACY_GAP_INVENTORY.md` §8.

Minimum viable port of legacy `engines/hydra_50/` (10 files, ~27,000
LOC). Captures the typed surface and fail-closed primitives only — the
full 51-scenario library is deferred to a later wave.

## Architectural invariants (AGENTS.md)

- **Downward-only deps**: hydra_50 imports only kernel + governance +
  execution + stdlib. No upward imports.
- **Canonical types**: kernel.JsonScalar, kernel.JsonValue, kernel.StateRegister.
- **Fail-closed**: invalid scenarios / unknown escalation levels raise
  Hydra50Error; never silent ALLOW.
- **Pluggable seams**: ScenarioEvaluator Protocol allows alternate
  decision logic.
- **Deterministic**: state in kernel.StateRegister for revision tracking.

## Modules

- `scenario` — `ThreatScenario` typed value: id, category, severity,
  current escalation level. Categories and severities are typed.
- `escalation` — `EscalationLadder` over `kernel.StateRegister`:
  state machine advancing scenarios through escalation levels
  (latent → emerging → critical → terminal).
- `evaluator` — `ScenarioEvaluator` + `EvaluationStrategy` Protocol:
  fail-closed gate evaluating scenario readiness against current state.
