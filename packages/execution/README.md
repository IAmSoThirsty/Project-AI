# Project-AI Execution

`ExecutionGate.submit_action()` is the package's sole actuation path. It evaluates AI-side
governance, consumes an exact scoped capability token, and only then invokes the supplied action.
Missing authority, non-`ALLOW` governance, evaluator faults, relay faults, and executor exceptions
all fail closed. Operator-side Arbiter/RLP output cannot bypass this gate.
