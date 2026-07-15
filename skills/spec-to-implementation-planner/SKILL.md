---
name: spec-to-implementation-planner
description: Convert research, governance, or product specifications into executable engineering plans. Use for epics, issues, interfaces, schemas, acceptance criteria, and phased implementation.
---

# Spec To Implementation Planner

## Objective

Turn intent into ordered, testable implementation work.

## Governing Rules

Read `references/constitutional-rules.md` before consequential analysis. Use `references/handoff-schema.md` when producing structured output for another skill.

## Workflow

1. Resolve the request scope, authoritative sources, versions, affected actors, and requested decision.
2. Retrieve or inspect relevant evidence using available files, internal connectors, repositories, or current public sources. Do not substitute memory for available evidence.
3. Classify every material claim by epistemic status and attach provenance.
4. Execute this skill's objective directly and keep analysis bounded to its declared scope.
5. Challenge the result for contradictions, omitted stakeholders, authority ambiguity, incentive failures, and invalidation conditions.
6. Separate recommendations from actions. Do not perform consequential external writes without explicit approval.
7. Produce the required output and a structured handoff when downstream work is likely.

## Required Output

Return, as applicable: work breakdown; dependencies; interfaces; acceptance criteria; risks; issue drafts.

Always include:
- Scope and authoritative versions
- Evidence and epistemic status
- Material assumptions and contradictions
- Risks, affected stakeholders, and power implications
- Residual uncertainty and irreversible consequences
- Recommended next skill call or concrete next action

## Quality Gate

Before completing, verify that:
- No unsupported inference is presented as fact.
- No conflicting version is silently merged.
- Every consequential recommendation identifies decision authority.
- Rights, guarantees, or controls are not described as effective without an enforcement or evidence path.
- The output states what could invalidate its conclusion.

## Composition

Prefer `thirsty-context-router` when scope is ambiguous, `thirsty-workspace-ingest` for unfamiliar artifact collections, `hostile-unknowns-review` for adversarial framing review, `epistemic-status-enforcer` for claim discipline, and `thirsty-work-orchestrator` for multi-domain work. Recommend other specialist skills only when their narrower purpose materially improves the result.
