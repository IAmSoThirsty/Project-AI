# PA-SHIELD Failure Mode Catalog

This catalog documents the known failure boundaries for the PA-SHIELD evaluation and containment stack.

## 1. Partial Governance Degradation

- Failure Mode: Partial governance degradation
- Trigger: Upstream policy engine returns a non-blocking response for a harmful request
- Impact: Detection may occur without enforcement, producing a `DEGRADED` result
- Containment: Case is scored as a benchmark failure and surfaced in comparison reports
- Mitigation: Tighten policy context mapping and add regression tests for the prompt family

## 2. State Register Corruption

- Failure Mode: State register corruption
- Trigger: Continuity claim cannot be anchored to authenticated prior state
- Impact: Session integrity is invalid
- Containment: `GAP_DETECTED` response with no carried-over privileges or memory
- Mitigation: Preserve hash-bound state references and reject implicit session merges

## 3. Audit Chain Tampering

- Failure Mode: Audit chain tampering
- Trigger: Any log entry is edited, removed, or re-ordered after creation
- Impact: Replay trust and evidentiary value degrade immediately
- Containment: `AuditVerifier.verify_chain()` fails on hash or linkage mismatch
- Mitigation: Treat the run as invalid and regenerate the benchmark from source inputs

## 4. Replay Divergence

- Failure Mode: Replay divergence
- Trigger: Re-running the same benchmark log yields a different status or response
- Impact: Reproducibility score drops below acceptable threshold
- Containment: Replay verification marks the case as a mismatch and lowers `replay_match_rate`
- Mitigation: Eliminate nondeterministic response paths or pin the runner configuration

## 5. Baseline Misinterpretation

- Failure Mode: Baseline misinterpretation
- Trigger: Consumers assume the baseline runner is a real hosted model instead of a deterministic vulnerable reference
- Impact: Comparison claims become overstated
- Containment: PA-SHIELD README explicitly marks the baseline as deterministic and local
- Mitigation: For external publication, replace or supplement it with a named third-party baseline

## 6. Legacy Suite Drift

- Failure Mode: Legacy suite drift
- Trigger: Existing `jbb`, `multiturn`, or `garak` scripts change their report schema
- Impact: Optional legacy aggregation may omit or misread those reports
- Containment: PA-SHIELD core benchmark remains intact because legacy suites are additive only
- Mitigation: Version-pin the legacy report readers or wrap them with schema checks

## 7. Fuzz Explosion

- Failure Mode: Fuzz explosion
- Trigger: Excessive mutation iterations inflate runtime and report volume
- Impact: Latency and storage costs grow faster than review value
- Containment: Iteration count is explicit and deterministic
- Mitigation: Use targeted suites or moderate iteration counts for routine regressions
