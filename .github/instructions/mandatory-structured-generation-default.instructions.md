---
description: "MANDATORY default coding protocol for all agents: requirements contract, design, pseudocode, implementation, adversarial self-review, refinement, and verification."
applyTo: "**"
---

# Mandatory Structured Generation & Adversarial Review Default

This instruction applies to **all coding agents and IDE copilots** in this repository.

It is the default protocol for any task that generates, modifies, or reviews implementation code.

## Required Requirements Contract (No Silent Assumptions)

Before implementation, explicitly establish:

- Language and version.
- Runtime and environment.
- Input contract (types, schema, examples).
- Output contract (types, schema, examples).
- Constraints:
  - Time complexity target.
  - Space complexity target.
  - Dependency allow/deny rules.
  - Security and validation requirements.
- Explicit edge-case list.

If any contract field is missing or ambiguous, state the gap and request clarification before coding.

## Required Sequential Process (Mandatory Order)

1. **Design**
   - Define approach and data flow.
   - State assumptions explicitly.
2. **Pseudocode**
   - Provide step-by-step logic aligned to design.
3. **Implementation**
   - Produce complete executable code.
   - No placeholders, no dead code.
4. **Adversarial Self-Review**
   - Identify failure modes, edge-case gaps, performance risks, and spec mismatches.
5. **Refinement**
   - Revise to close discovered gaps without violating constraints.

The first version is assumed insufficient. At least one critique-and-refine pass is required.

## Required Verification Gate

Before completion, provide:

- Normal, edge, and failure-path tests.
- Expected outputs.
- Constraint compliance justification (complexity/security/validation).
- Confirmation that no unresolved assumptions remain.

## Iteration Protocol (Feedback)

When given feedback:

- Address only specified issues.
- Do not regress previously correct behavior.
- Re-validate the full requirement contract after changes.

## Failure Conditions (Output Rejected)

Treat output as non-compliant if any apply:

- Ambiguity remains unresolved.
- Edge-case handling is missing.
- Constraints are violated.
- Code is non-executable or incomplete.
- Assumptions are unjustified.

## Enforcement

Any coding output that skips this protocol is non-compliant with repository governance and must be regenerated.
