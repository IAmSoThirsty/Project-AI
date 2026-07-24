# SAFE-HALT Recovery Runbook

**Purpose.** The exact, audited sequence to clear a SAFE-HALT and resume standard
execution. Before this was built, the halt surfaces were fail-closed/terminal with no
in-repo recovery path (see the SAFE_HALT row in
`PROJECT_AI_MASTER_CONTINUITY_TRACEABILITY_MATRIX.md`). There are three distinct halt
surfaces; identify which one you are in, then follow its sequence.

> Fail-closed by design: every recovery below requires a non-blank authorizing identity
> and is recorded to an audit chain. There is no silent resume.

---

## 1. Repo-wide SAFE-HALT (`kernel.SafeHaltController`)

The constitutional stop state (PSIA v1 §8.3). While halted, every write (each actuation
routed through `execution.ExecutionGate.submit_action`) is blocked and returns `DENY`
with reason `system in SAFE-HALT: …`; reads pass through. The halt is **monotonic** —
it stays in force until an explicit reset.

**How to tell you are here:** actuations return `Outcome.DENY` with a `system in SAFE-HALT`
reason, and `controller.is_halted` is `True`. `controller.active_halt` gives the reason
(one of `HaltReason`: `INVARIANT_VIOLATION`, `UNRECOVERABLE_ERROR`, `ADMINISTRATIVE`,
`SECURITY_INCIDENT`, `CHAIN_CORRUPTION`, `KEY_COMPROMISE`).

**Recovery sequence:**

1. **Diagnose first.** Read `controller.active_halt` (reason, details, `triggered_by`) and
   the `system.safe_halt.entered` event on the `EventSpine`. Resolve the underlying cause
   before clearing — a reset while the cause persists will simply re-halt.
2. **Authorize and reset.** Call:

   ```python
   controller.reset(authorized_by="<operator-identity>")  # -> True when a halt was cleared
   ```

   A blank `authorized_by` raises `SafeHaltError` (fail-closed). The reset appends a
   `system.safe_halt.exited` event (with `cleared_sequence`) to the audit chain.
3. **Confirm resumed.** `controller.is_halted` is now `False`; re-submit the blocked action
   and confirm it reaches governance. The full halt/reset trail remains in
   `controller.history`.

`reset` is idempotent: calling it when not halted returns `False` and changes nothing.

---

## 2. Companion NIRL loop (`companion.nirl.NIRLController`)

The companion reflex state machine can enter the terminal `safe_halt` state from any active
state. Its **sole sanctioned exit** is `safe_halt → recovering → idle`; there is no direct
`safe_halt → idle`/`listening` edge (any such attempt raises `NIRLTransitionError`).

**Recovery sequence** (each step carries `expected_revision` for optimistic concurrency, and
via `BondedCompanion` routes through `ExecutionGate` — so it is also blocked while surface 1
is halted; clear that first):

1. `controller.request_transition("recovering", expected_revision=<rev>)`
2. `controller.request_transition("idle", expected_revision=<rev+1>)`

The companion is then back at `idle` (`DEFAULT_STATE`) and may resume normal progression
(`idle → listening → …`).

---

## 3. DPR deliberation loop guards (`dpr.pipeline.DeliberationEngine`)

Most DPR `SAFE_HALT` verdicts are per-decision (pure functions of the request context): fix
the offending input and the next `decide()` proceeds — nothing to clear. The exception is
the **loop-limit** guards (escalation / deferral / delay), which keep persistent per-`(actor,
action)` counters; once a key exceeds its limit, every subsequent `decide()` for that key
force-halts.

**Recovery sequence:**

- Targeted (one actor/action pair):

  ```python
  engine.reset_loop_counters(
      authorized_by="<operator-identity>",
      actor_id="<actor>",
      action_name="<action>",
  )  # -> number of keys cleared
  ```

- Full reset (all keys): omit both `actor_id` and `action_name`.

Providing exactly one of `actor_id`/`action_name` is rejected (ambiguous scope); a blank
`authorized_by` is rejected. The reset is recorded on the engine's audit chain
(`decision: "LOOP_COUNTERS_RESET"`). The next `decide()` for the cleared key(s) no longer
force-halts.

---

## Quick reference

| Surface | Frozen because | Recovery call | Audit event |
|---|---|---|---|
| Repo-wide | Monotonic write-block | `SafeHaltController.reset(authorized_by)` | `system.safe_halt.exited` |
| NIRL | Terminal `safe_halt` state | `request_transition("recovering")` → `request_transition("idle")` | via ExecutionGate audit chain |
| DPR | Latched loop counters | `DeliberationEngine.reset_loop_counters(authorized_by=…)` | `LOOP_COUNTERS_RESET` chain entry |
