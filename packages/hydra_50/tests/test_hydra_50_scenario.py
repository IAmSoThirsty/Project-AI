"""Unit tests for hydra_50.scenario."""

from __future__ import annotations

import pytest

from hydra_50 import (
    ALLOWED_CATEGORIES,
    ALLOWED_SEVERITIES,
    Hydra50Error,
    make_scenario,
    scenario_from_mapping,
    scenario_to_dict,
)


def _valid_kwargs() -> dict[str, object]:
    return {
        "scenario_id": "scn-001",
        "category": "ai_reality_flood",
        "severity": "emerging",
        "description": "Synthetic media saturation",
        "escalation_level": 1,
    }


# ---------------------------------------------------------------------------
# make_scenario
# ---------------------------------------------------------------------------


def test_make_scenario_constructs_valid() -> None:
    s = make_scenario(**_valid_kwargs())  # type: ignore[arg-type]
    assert s["scenario_id"] == "scn-001"
    assert s["category"] == "ai_reality_flood"
    assert s["escalation_level"] == 1


def test_make_scenario_rejects_empty_id() -> None:
    bad = _valid_kwargs()
    bad["scenario_id"] = ""
    with pytest.raises(Hydra50Error, match="scenario_id"):
        make_scenario(**bad)  # type: ignore[arg-type]


def test_make_scenario_rejects_unknown_category() -> None:
    bad = _valid_kwargs()
    bad["category"] = "flying_saucers"
    with pytest.raises(Hydra50Error, match="category"):
        make_scenario(**bad)  # type: ignore[arg-type]


def test_make_scenario_rejects_unknown_severity() -> None:
    bad = _valid_kwargs()
    bad["severity"] = "apocalyptic"
    with pytest.raises(Hydra50Error, match="severity"):
        make_scenario(**bad)  # type: ignore[arg-type]


def test_make_scenario_rejects_empty_description() -> None:
    bad = _valid_kwargs()
    bad["description"] = ""
    with pytest.raises(Hydra50Error, match="description"):
        make_scenario(**bad)  # type: ignore[arg-type]


def test_make_scenario_rejects_negative_level() -> None:
    bad = _valid_kwargs()
    bad["escalation_level"] = -1
    with pytest.raises(Hydra50Error, match="escalation_level"):
        make_scenario(**bad)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# dict round-trip
# ---------------------------------------------------------------------------


def test_scenario_to_dict_is_json_serializable() -> None:
    s = make_scenario(**_valid_kwargs())  # type: ignore[arg-type]
    d = scenario_to_dict(s)
    assert d["scenario_id"] == "scn-001"
    assert d["category"] == "ai_reality_flood"


def test_scenario_from_mapping_round_trip() -> None:
    s = make_scenario(**_valid_kwargs())  # type: ignore[arg-type]
    d = scenario_to_dict(s)
    s2 = scenario_from_mapping(d)
    assert s2["scenario_id"] == s["scenario_id"]
    assert s2["escalation_level"] == s["escalation_level"]


def test_scenario_from_mapping_rejects_non_string_id() -> None:
    with pytest.raises(Hydra50Error, match="scenario_id"):
        scenario_from_mapping({"scenario_id": 123})


def test_scenario_from_mapping_rejects_non_int_level() -> None:
    with pytest.raises(Hydra50Error, match="escalation_level"):
        scenario_from_mapping(
            {
                "scenario_id": "x",
                "category": "ai_reality_flood",
                "severity": "latent",
                "description": "x",
                "escalation_level": "two",
            }
        )


def test_scenario_from_mapping_rejects_bool_as_int() -> None:
    with pytest.raises(Hydra50Error, match="escalation_level"):
        scenario_from_mapping(
            {
                "scenario_id": "x",
                "category": "ai_reality_flood",
                "severity": "latent",
                "description": "x",
                "escalation_level": True,
            }
        )


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_allowed_categories_includes_required_set() -> None:
    for c in (
        "ai_reality_flood",
        "autonomous_trading_war",
        "model_weight_poisoning",
    ):
        assert c in ALLOWED_CATEGORIES


def test_allowed_severities_includes_required_set() -> None:
    for s in ("latent", "emerging", "critical", "terminal"):
        assert s in ALLOWED_SEVERITIES
