# project-ai-temporal

Temporal-style workflow orchestration for Project-AI Beginnings.

Sub-phased rebuild of legacy `temporal/` (8 Python files, 2459 LOC, 2
subdirs). Closes C4 from STAGE_19 §9.

## Sub-phase plan

- **I0 (this envelope)**: discovery + skeleton (no source)
- **I1**: typed dataclasses + activity definitions
- **I2**: triumvirate workflow + atomic security
- **I3**: enhanced security + security agent workflows

See `docs/internal/PHASE_I_DISCOVERY.md` for the full plan.

## Architectural decisions

The legacy depends on the external `temporalio` SDK. To avoid adding
a heavy runtime dependency to the minimum viable port, Phase I captures
the **workflow/activity SHAPE** as typed Protocols without decorators:

- Activity = typed Python function with `Activity` Protocol
- Workflow = orchestration of activities via `Workflow` Protocol
- Decorators (`@activity.defn`, `@workflow.defn`) deferred to a later
  wave when real SDK integration is needed (Option A or B in the
  discovery doc).

## Architectural invariants (AGENTS.md v3)

- **Downward-only deps**: temporal imports only kernel + stdlib.
- **Canonical types**: kernel.JsonScalar, kernel.JsonValue.
- **Fail-closed**: invalid workflow inputs raise TemporalError.
- **Pluggable seams**: Activity Protocol + Workflow Protocol.
- **Deterministic**: same input → same output.
- **Strict typing**: mypy --strict clean.