"""semantic_collision.py — Upgrade 17: Cross-Plane Semantic Collision Detection.

Tracks ingress_intent_hash, shadow_intent_hash, execution_intent_hash.
If semantic intent differs materially across planes → DENY/BLOCK + MISMATCHED_INTENT violation.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Hamming distance threshold (on hex digest nibbles) for "material" mismatch
_MISMATCH_THRESHOLD = 4   # nibbles that differ out of first 16


def _intent_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:32]


def _nibble_distance(h1: str, h2: str) -> int:
    """Count differing nibbles between two equal-length hex strings."""
    min_len = min(len(h1), len(h2))
    return sum(1 for a, b in zip(h1[:min_len], h2[:min_len]) if a != b)


@dataclass
class IntentPlanes:
    """The three intent planes tracked across a governed execution."""

    ingress_intent_hash: str    # hash of raw request as received
    shadow_intent_hash: str     # hash of intent after pre-processing / normalization
    execution_intent_hash: str  # hash of intent at point of execution binding


@dataclass
class SemanticCollisionResult:
    """Result of cross-plane intent comparison."""

    collision_detected: bool
    mismatch_plane: str          # which planes diverged
    ingress_vs_shadow_distance: int
    shadow_vs_execution_distance: int
    ingress_vs_execution_distance: int
    violation_type: str
    recommendation: str
    planes: IntentPlanes


def detect_semantic_collision(
    ingress_text: str,
    shadow_text: str,
    execution_text: str,
    threshold: int = _MISMATCH_THRESHOLD,
) -> SemanticCollisionResult:
    """Compare intent hashes across the three planes.

    Returns SemanticCollisionResult with collision_detected=True if any
    pair of planes exceeds the threshold.
    """
    h_in = _intent_hash(ingress_text)
    h_sh = _intent_hash(shadow_text)
    h_ex = _intent_hash(execution_text)

    planes = IntentPlanes(h_in, h_sh, h_ex)

    d_in_sh = _nibble_distance(h_in, h_sh)
    d_sh_ex = _nibble_distance(h_sh, h_ex)
    d_in_ex = _nibble_distance(h_in, h_ex)

    collision = (d_in_sh > threshold) or (d_sh_ex > threshold) or (d_in_ex > threshold)
    mismatch_plane = ""
    if d_in_sh > threshold:
        mismatch_plane = "ingress↔shadow"
    elif d_sh_ex > threshold:
        mismatch_plane = "shadow↔execution"
    elif d_in_ex > threshold:
        mismatch_plane = "ingress↔execution"

    violation = "MISMATCHED_INTENT" if collision else "NONE"
    recommendation = (
        "DENY — semantic intent shifted across planes, possible prompt injection or context manipulation"
        if collision else "ALLOW — intent consistent across planes"
    )

    if collision:
        logger.warning(
            "SemanticCollision: %s d_in_sh=%d d_sh_ex=%d d_in_ex=%d",
            mismatch_plane, d_in_sh, d_sh_ex, d_in_ex,
        )

    return SemanticCollisionResult(
        collision_detected=collision,
        mismatch_plane=mismatch_plane,
        ingress_vs_shadow_distance=d_in_sh,
        shadow_vs_execution_distance=d_sh_ex,
        ingress_vs_execution_distance=d_in_ex,
        violation_type=violation,
        recommendation=recommendation,
        planes=planes,
    )


__all__ = [
    "IntentPlanes",
    "SemanticCollisionResult",
    "detect_semantic_collision",
]
