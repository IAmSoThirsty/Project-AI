# Project-AI Execution

`ExecutionGate.submit_action()` is the package's sole actuation path. It
evaluates AI-side governance, consumes an exact scoped capability token,
and only then invokes the supplied action. Missing authority, non-`ALLOW`
governance, evaluator faults, relay faults, and executor exceptions all
fail closed. Operator-side Arbiter/RLP output cannot bypass this gate.

## When to use this package

You use the execution gate whenever you need to **actuate** something in
the real world. The gate is the only path through which governance +
authority combine to produce an action.

You do **not** use the execution gate for:
- Pure analysis (use `packages/atlas/`)
- State recording without side effects (use `packages/kernel/`)
- Read-only operations (the gate is for mutations)

## Public API

| Symbol | Purpose |
|---|---|
| `ExecutionGate` | The gate; instantiable with governance + capability + audit |
| `ExecutionResult` (frozen dataclass) | The result of `submit_action` — verdict, hash, reason |
| `submit_action(gate, action_request, token, executor)` | The sole actuation path |
| `get_execution_gate(...)` | Singleton factory for the default gate |
| `reset_execution_gate()` | Test/reset helper |

## The four-step gate

Every call to `submit_action` runs this pipeline. Any step that fails
short-circuits to `DENY`:

1. **Governance evaluation** — the request is evaluated against the
   constitutional rules and the governor set. Result is one of
   `ALLOW`, `DENY`, `ESCALATE`. Only `ALLOW` proceeds.
2. **Capability consumption** — the supplied token is consumed
   (single-use). The token's subject, operation, and resource must
   match the request exactly.
3. **Executor invocation** — the supplied callable runs with the
   request as input. Any exception is caught and converted to a
   `DENY` result.
4. **Audit emission** — the result is appended to the audit chain
   (if an audit relay is configured), with the result hash, action
   hash, and gate state.

## Fail-closed behavior

The gate fails closed on:

- Missing or invalid capability token → `DENY`, no executor call
- `DENY` or `ESCALATE` governance verdict → `DENY`, no executor call
- Governance evaluator exception → `DENY` (caller never sees the exception)
- Token scope mismatch → `DENY`
- Executor raises any exception → `DENY` (gate catches, returns)
- Audit relay exception → executor still ran, but result is `DENY` with
  reason noting the audit failure

## Dependency contract

Imports: `kernel` (canonical types) + `governance` + `capability` +
stdlib. Execution sits at the bottom of the application tier — every
actuation flows through it.

The API gateway (`packages/api/`), the CLI (`packages/cli/`), and the
companion identity flows all call into this gate. Operator-side
Arbiter/RLP **cannot** bypass the gate; their outputs must also be
routed through `submit_action` if they want to actuate.

## Architectural invariants

- The gate is the **sole** actuation path. There is no other
  `submit_action` in the codebase.
- A `DENY` from governance is **final** — no token can override it
  (the gate evaluates governance first, then capability).
- The executor is invoked **at most once** per `submit_action` call.
- The audit chain is **append-only**; the gate never modifies prior
  records.

## Source of truth

- `packages/execution/src/execution/__init__.py` — full export list
- `docs/architecture.md` §"Governance Model" — the 4-step pipeline
- `docs/security.md` §"Fail-closed execution gate" — the security
  contract the gate enforces
- `docs/runbooks/INCIDENT_RESPONSE.md` §"Capability token rejected" —
  the most common failure mode
