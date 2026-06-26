"""
hydra_50.scenario — Threat scenario typed value.

A ThreatScenario is the typed primitive for a single threat scenario:
id, category, current severity, current escalation level. This is the
minimum surface from legacy `engines/hydra_50/` (51 scenarios, 4
enums, 6+ dataclasses) — captures the invariants, defers the full
scenario library to a later wave.

Architectural invariants (AGENTS.md):
- Downward-only deps: hydra_50.scenario imports only kernel + stdlib.
- Canonical types: kernel.JsonScalar, kernel.JsonValue.
- Fail-closed: invalid categories / severities raise Hydra50Error.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TypedDict

from kernel import JsonValue

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


# Allowed scenario categories (subset of legacy ScenarioCategory; minimum).
ALLOWED_CATEGORIES: frozenset[str] = frozenset(
    {
        "ai_reality_flood",
        "autonomous_trading_war",
        "internet_fragmentation",
        "synthetic_identity",
        "cognitive_load",
        "model_weight_poisoning",
        "deepfake_legal",
        "currency_confidence",
        "energy_blocs",
        "insurance_market_failure",
    }
)


# Allowed severities (subset of legacy EscalationLevel; minimum).
ALLOWED_SEVERITIES: frozenset[str] = frozenset({"latent", "emerging", "critical", "terminal"})


class Hydra50Error(ValueError):
    """Raised when a hydra_50 input is invalid."""


# ---------------------------------------------------------------------------
# Typed scenario
# ---------------------------------------------------------------------------


class ThreatScenario(TypedDict):
    """Typed shape of a threat scenario (id + classification + current state).

    Immutable from the consumer's perspective; constructed via
    make_scenario().
    """

    scenario_id: str
    category: str
    severity: str
    description: str
    escalation_level: int


def make_scenario(
    *,
    scenario_id: str,
    category: str,
    severity: str,
    description: str,
    escalation_level: int,
) -> ThreatScenario:
    """Construct a validated ThreatScenario.

    Raises Hydra50Error on any invalid input.
    """
    if not scenario_id.strip():
        raise Hydra50Error("scenario_id must not be empty")
    if category not in ALLOWED_CATEGORIES:
        raise Hydra50Error(
            f"category must be one of {sorted(ALLOWED_CATEGORIES)}, got {category!r}"
        )
    if severity not in ALLOWED_SEVERITIES:
        raise Hydra50Error(
            f"severity must be one of {sorted(ALLOWED_SEVERITIES)}, got {severity!r}"
        )
    if not description.strip():
        raise Hydra50Error("description must not be empty")
    if escalation_level < 0:
        raise Hydra50Error(f"escalation_level must be >= 0, got {escalation_level!r}")
    return ThreatScenario(
        scenario_id=scenario_id,
        category=category,
        severity=severity,
        description=description,
        escalation_level=escalation_level,
    )


def scenario_to_dict(scenario: ThreatScenario) -> dict[str, JsonValue]:
    """Convert a ThreatScenario to a JSON-serializable dict."""
    return {
        "scenario_id": scenario["scenario_id"],
        "category": scenario["category"],
        "severity": scenario["severity"],
        "description": scenario["description"],
        "escalation_level": scenario["escalation_level"],
    }


def scenario_from_mapping(mapping: Mapping[str, object]) -> ThreatScenario:
    """Construct a ThreatScenario from a dict-like input.

    Validates that all required fields are present with correct types.
    """
    sid = mapping.get("scenario_id")
    cat = mapping.get("category")
    sev = mapping.get("severity")
    desc = mapping.get("description")
    lvl = mapping.get("escalation_level")
    if not isinstance(sid, str):
        raise Hydra50Error("scenario_id must be a string")
    if not isinstance(cat, str):
        raise Hydra50Error("category must be a string")
    if not isinstance(sev, str):
        raise Hydra50Error("severity must be a string")
    if not isinstance(desc, str):
        raise Hydra50Error("description must be a string")
    if not isinstance(lvl, int) or isinstance(lvl, bool):
        raise Hydra50Error("escalation_level must be a non-bool int")
    return make_scenario(
        scenario_id=sid,
        category=cat,
        severity=sev,
        description=desc,
        escalation_level=lvl,
    )


__all__ = [
    "ALLOWED_CATEGORIES",
    "ALLOWED_SEVERITIES",
    "Hydra50Error",
    "ThreatScenario",
    "make_scenario",
    "scenario_from_mapping",
    "scenario_to_dict",
]
