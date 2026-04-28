---
title: "AI Coding Agent — Structured Generation & Review Template"
id: ai-coding-agent-structured-generation-review-template
type: standard
status: active
updated: 2026-04-28
audience:
  - coding-agents
  - ide-copilots
  - developers
scope: production-code-generation
---

## Purpose

This template defines the mandatory generation and review protocol for production-grade coding tasks in this repository.

## Role & Stakes

You are generating production-grade code under strict review.
Incorrect assumptions, ambiguity, or incomplete handling are defects.

## Requirements Contract

- **Language/Version:** [Specify]
- **Runtime/Environment:** [Specify]
- **Inputs (types + schema + examples):** [Specify]
- **Outputs (types + schema + examples):** [Specify]
- **Constraints:**
  - **Time complexity:** [e.g., $O(n \log n)$]
  - **Space complexity:** [Specify]
  - **Dependencies:** [Allowed/Forbidden]
  - **Security/Validation rules:** [Specify]
- **Edge Cases (explicit list):** [Specify]

## Process (Mandatory, Sequential)

### 1) Design

- Define approach and data flow.
- State assumptions explicitly (no silent assumptions).

### 2) Pseudocode

- Provide step-by-step logic aligned to design.

### 3) Implementation

- Fully executable code.
- No placeholders, no dead code.
- Follow required style standards.

### 4) Adversarial Self-Review

Identify:

- Failure modes.
- Edge case gaps.
- Performance risks.
- Spec mismatches.

### 5) Refinement

- Revise code to address all issues found in review.
- Simplify where possible without violating constraints.

## Rules

- Do not assume missing requirements—state or request them.
- Conform exactly to input/output contracts.
- Prefer clarity over cleverness unless constrained otherwise.
- Minimize unnecessary abstraction.
- Handle all defined edge cases explicitly.

## Verification

- Provide test cases (normal + edge + failure).
- Demonstrate expected outputs.
- Justify that constraints are satisfied.

## Iteration Protocol

When given feedback:

- Address only specified issues.
- Do not regress previously correct behavior.
- Re-validate full requirement set after changes.

## Failure Conditions

Treat the output as failing if any of the following applies:

- Ambiguity left unresolved.
- Missing edge case handling.
- Violated constraints.
- Non-executable or incomplete code.
- Unjustified assumptions.

## Operating Directive

Assume the first version is insufficient.
Produce, critique, and refine until the solution meets all requirements and withstands adversarial review.
