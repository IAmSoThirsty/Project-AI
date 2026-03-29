# PA-SHIELD

Project-AI Secure Harness for Integrated Evaluation and Layered Defense.

This benchmark extends the existing `adversarial_tests/` structure with a deterministic red-team harness that compares a vulnerable baseline against the governed Project-AI runtime.

## Scope

- Threat Class A: Instruction override
- Threat Class B: Tool escalation
- Threat Class C: State corruption
- Threat Class D: Governance bypass
- Benign controls for false-positive measurement
- Chained multi-turn attacks
- Deterministic fuzz variants
- Tamper-evident audit logs
- Replay verification and reproducibility scoring

## Layout

```text
adversarial_tests/
  evaluation_harness.py
  pa_shield/
    attacks/
      instruction_override.json
      tool_escalation.json
      state_corruption.json
      governance_bypass.json
      benign_controls.json
      chained_attacks.json
```

Core implementation lives under `src/app/testing/pa_shield/`.

## Commands

```bash
python adversarial_tests/evaluation_harness.py run --system baseline --suite full
python adversarial_tests/evaluation_harness.py run --system project_ai --suite full
python adversarial_tests/evaluation_harness.py compare --systems baseline project_ai --suite full
python adversarial_tests/evaluation_harness.py compare --systems baseline project_ai --suite full --fuzz --iterations 10
python adversarial_tests/evaluation_harness.py replay --system project_ai --log ci-reports/pa-shield/<run>/project_ai/project_ai-audit.jsonl
python adversarial_tests/run_all_tests.py --output-dir ci-reports
```

If installed as a project script:

```bash
pa-shield run --system project_ai --suite full
pa-shield compare --systems baseline project_ai --suite full
pa-shield replay --system project_ai --log path/to/audit.jsonl
```

## Parent Suite Integration

`adversarial_tests/run_all_tests.py` now runs PA-SHIELD alongside JBB, multi-turn, and Garak so the repo can emit one unified red-team report with both comparative benchmark evidence and the legacy adversarial suites.

## Metrics

- `attack_success_rate`
- `detection_rate`
- `enforcement_rate`
- `false_positive_rate`
- `latency_overhead_ms`
- `audit_completeness`
- `replay_match_rate`
- `reproducibility_score`
- `time_to_failure_iteration`

## Baseline vs Governed System

The baseline runner is intentionally deterministic and vulnerable. It is a local benchmark reference, not an external hosted LLM. That keeps comparisons reproducible and makes replay verification meaningful.

The governed runner wraps the existing `adversarial_tests/galahad_model.py` implementation and normalizes outcomes into benchmark statuses such as `BLOCKED`, `DENIED`, and `GAP_DETECTED`.

## Research Alignment

- Deng et al. (2026): agent tool exploitation
- Snyk Labs (2025): plugin and system compromise
- ART Benchmarks (2025): adversarial prompt attacks
- Raza et al. (2025): governance and responsible agent surveys
- Zhou (2026): cryptographic governance for AI tools
- Shapira et al. (2026): exploit chains in agents
