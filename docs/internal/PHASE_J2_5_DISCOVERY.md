# Phase J2.5 Discovery — constitutional kernel integration

**Status:** LOCALLY IMPLEMENTED 2026-06-28
**Authority:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J, J1 audit
**Date:** 2026-06-28
**Author:** Codex (Quencher session)

---

## 0. Context

The J1 audit identified constitutional-kernel integration as the next open gap
after J2.4 graph construction closed.

The preserved legacy implementation is:

- `packages/_staging/atlas/governance/constitutional_kernel.py`

The canonical runtime already has the correct enforcement route:

- `kernel.InvariantEngine`
- `governance.GovernanceEngine`
- `execution.ExecutionGate`

J2.5 therefore should not introduce a parallel constitutional authority. The
correct integration is a governance invariant that runs before governor votes
and before execution can consume a capability.

---

## 1. Legacy checks ported

The canonical J2.5 slice ports the legacy checks that can be enforced through
the current `ActionRequest + state` boundary:

- sludge data entering Reality Stack (`RS`)
- narrative probability without evidence vectors
- projection/simulation/timeline input without hash/source metadata
- agency claims without TierA/TierB evidence
- projection/simulation/timeline without deterministic seed
- metadata hash mismatch
- influence graph hash/lineage drift
- bounded parameter and driver values
- monotonic timestep and temporal year consistency

Legacy Atlas-specific audit trail calls were not ported. Canonical evidence is
captured by `GovernanceResult` and `ExecutionGate` event records.

---

## 2. Canonical module

| Path | Purpose |
|---|---|
| `packages/governance/src/governance/constitutional_kernel.py` | stateful `ConstitutionalKernel` invariant callable |
| `packages/governance/tests/test_constitutional_kernel.py` | invariant unit tests |
| `tests/test_constitutional_kernel_execution_integration.py` | execution-gate denial integration test |

Public exports:

- `ViolationType`
- `PARAMETER_BOUNDS`
- `ConstitutionalKernel`
- `constitutional_state_hash`
- `get_constitutional_kernel`
- `reset_constitutional_kernel`

---

## 3. Integration decision

`ConstitutionalKernel` implements the `kernel.Invariant` callable shape:

```text
(ActionRequest, Mapping[str, object]) -> InvariantViolation | None
```

This means:

- `GovernanceEngine.decide()` evaluates constitutional checks before governor
  votes.
- BLOCKING/CRITICAL invariant violations become DENY decisions with hash-bound
  governance evidence.
- `ExecutionGate.submit_action()` sees the DENY before capability consumption
  or executor invocation.
- The implementation stays subordinate to the existing execution path.

---

## 4. Verification summary

See `docs/internal/STAGE_19_5J2_5_ACCEPTANCE.md` for command evidence.

Local evidence at implementation time:

- Targeted constitutional tests: 14 passed.
- Governance/execution package scope: 406 passed.
- Full pytest: 1420 passed.
- CI-shaped mypy: clean on 90 source files.
- Coverage: 89.92%, threshold 80%.
- Canonical replay: 5/5 invariants passed.
- Frozen history: 2264/2264 sections verified.

---

## 5. Remaining J2 work

J2.5 is locally implemented. The next open J1 audit gap is J2.6 failure
surveillance, unless the user pivots.
