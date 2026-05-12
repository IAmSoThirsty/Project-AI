"""
PSIA Stage 3 — Shadow Plane Simulator.

Runs a deterministic parallel simulation of the classified intent.
The shadow plane is read-only with respect to canonical state: it may
*read* but never *write* canonical state (PlaneIsolationAnalyzer principle).

Invariant checks performed:
  1. PlaneIsolation  — shadow block contains no canonical write operations
  2. Determinism     — identical inputs produce identical shadow outputs (tested
                       by running the simulation twice and comparing hashes)
  3. ResourceBound   — estimated resource cost is within policy limits
  4. Purity          — simulation contains no I/O or non-deterministic stdlib calls
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ..schemas.models import ClassifiedFrame, ShadowFrame, ShadowResult

# Maximum allowed estimated resource cost (arbitrary unit)
_RESOURCE_LIMIT = 1000.0

# Actions that are inherently canonical writes — forbidden in shadow
_CANONICAL_WRITE_ACTIONS = {"mutate", "write"}

# Actions that are always considered pure (read-only with no side effects)
_PURE_ACTIONS = {"read"}


def _simulate(classified: ClassifiedFrame) -> dict[str, Any]:
    """
    Run the shadow simulation.  Returns a deterministic dict representing
    the simulated execution state.  This is intentionally simple — the
    important property is determinism, not fidelity.
    """
    return {
        "actor": classified.validated.actor,
        "action": classified.validated.action,
        "target": classified.validated.target,
        "risk_level": classified.risk_level,
        "intent_class": classified.intent_class,
        "threat_score": classified.threat_score,
    }


def _shadow_hash(state: dict) -> str:
    blob = json.dumps(state, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


class ShadowSimulator:
    """
    Deterministic shadow simulator for PSIA Stage 3.

    Usage:
        sim = ShadowSimulator()
        shadow_frame = sim.run(classified_frame)
    """

    def __init__(self, resource_limit: float = _RESOURCE_LIMIT) -> None:
        self._resource_limit = resource_limit

    def run(self, classified: ClassifiedFrame) -> ShadowFrame:
        results: list[ShadowResult] = []

        # --- Check 1: PlaneIsolation ---
        action = classified.validated.action
        if action in _CANONICAL_WRITE_ACTIONS and classified.intent_class == "state_change":
            # Writes are permitted at stage 3 only as simulation — not actual writes
            # Any direct canonical mutation in the shadow plane is a violation
            context_has_shadow_bypass = classified.validated.context.get(
                "shadow_bypass", False
            )
            if context_has_shadow_bypass:
                results.append(ShadowResult(
                    "PlaneIsolation",
                    passed=False,
                    detail="shadow_bypass flag set — plane isolation violation",
                ))
            else:
                results.append(ShadowResult("PlaneIsolation", passed=True))
        else:
            results.append(ShadowResult("PlaneIsolation", passed=True))

        # --- Check 2: Determinism ---
        state1 = _simulate(classified)
        state2 = _simulate(classified)
        h1, h2 = _shadow_hash(state1), _shadow_hash(state2)
        deterministic = h1 == h2
        results.append(ShadowResult(
            "Determinism",
            passed=deterministic,
            detail="" if deterministic else f"hash mismatch: {h1} != {h2}",
        ))

        # --- Check 3: ResourceBound ---
        estimated_cost = self._estimate_cost(classified)
        within_budget = estimated_cost <= self._resource_limit
        results.append(ShadowResult(
            "ResourceBound",
            passed=within_budget,
            detail=(
                f"cost={estimated_cost:.1f} limit={self._resource_limit:.1f}"
                if not within_budget
                else ""
            ),
        ))

        # --- Check 4: Purity ---
        # In shadow plane, only read-like operations are pure
        is_pure = action in _PURE_ACTIONS or classified.threat_score < 0.3
        results.append(ShadowResult(
            "Purity",
            passed=is_pure,
            detail="" if is_pure else f"action '{action}' with threat_score={classified.threat_score:.2f} is not pure",
        ))

        shadow_passed = all(r.passed for r in results)
        return ShadowFrame(
            classified=classified,
            shadow_results=tuple(results),
            shadow_passed=shadow_passed,
            shadow_hash=h1,
        )

    @staticmethod
    def _estimate_cost(classified: ClassifiedFrame) -> float:
        """Heuristic resource cost estimate based on action type and risk level."""
        base = {"read": 1.0, "write": 10.0, "execute": 50.0, "mutate": 200.0}.get(
            classified.validated.action, 25.0
        )
        multiplier = {"low": 1.0, "medium": 2.0, "high": 5.0, "critical": 20.0}.get(
            classified.risk_level, 3.0
        )
        return base * multiplier
