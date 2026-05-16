"""
PSIA — Plane Separation / Isolation Architecture

A 7-stage, 6-plane defense pipeline with monotonically increasing strictness.
No input that passes stage N can bypass stage N+1.

Planes:
  0 — Entry       Raw untrusted input
  1 — Validated   Schema-checked, type-safe
  2 — Classified  Intent and risk level assigned
  3 — Shadow      Parallel simulation (non-mutating)
  4 — Governed    Triumvirate + governance annotation check
  5 — Canonical   Authoritative state (append-only)
  6 — Sealed      Merkle-anchored, Ed25519-signed

Stages:
  0 — Ingestion      Accept raw input, reject malformed frames
  1 — Schema         Validate structure against Pydantic schemas
  2 — Classification  Classify intent: actor, action, risk_level
  3 — Shadow         Run shadow simulation; check invariants
  4 — Governance     Triumvirate constitutional evaluation
  5 — Canonical      Write to append-only canonical log
  6 — Seal           Merkle-root block seal + Ed25519 anchor

Usage:
    from psia.core import Pipeline, PipelineResult
    result = Pipeline().run(raw_input_dict)
    assert result.sealed_hash is not None
"""

from .core import Pipeline, PipelineResult, PipelineStageError

__all__ = ["Pipeline", "PipelineResult", "PipelineStageError"]
