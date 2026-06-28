# Project-AI Governance

This is the AI-side governance layer. It evaluates kernel invariants before governor votes, honors
unilateral veto, preserves `ESCALATE`, and denies on missing governors or evaluator faults. It
returns canonical kernel decisions with hash-bound evidence. It does not execute actions or issue
capabilities.

`ConstitutionalKernel` is an opt-in invariant callable for legacy constitutional runtime checks.
It plugs into `kernel.InvariantEngine`, so sludge-to-Reality-Stack state, unaudited projection
inputs, seed omissions, hash mismatch, graph drift, out-of-bounds parameters, and temporal skew are
denied before governor votes and before `ExecutionGate` can consume a capability.

`AsymmetricSecurityGovernor` is an opt-in fail-closed governor for security-critical actions. It
requires twelve explicit security proofs and vetoes missing, malformed, false, or unexpected
evidence. Its deterministic catalog reconstructs the published nine-category, 312-vector matrix
for acceptance testing; it does not claim to recover unpublished legacy payloads.
