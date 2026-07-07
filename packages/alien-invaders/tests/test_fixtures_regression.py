"""Regression tests using the canonical 2026-12-27 simulation fixtures.

These fixtures are the output of a real alien_invaders run
(saved under
``packages/alien-invaders/tests/fixtures/sim_run_2026-12-27/``)
from a prior session. They serve as:

  1. A snapshot of the simulation's behavior in a known-good
     state (1-year run, 195 countries, "survival" outcome).
  2. Regression data: future engine changes that would alter
     the simulation's behavior in a way inconsistent with this
     snapshot should be caught (or at least surfaced).

The fixtures are JSON, not Python fixtures, so they can be
inspected by hand and compared against new runs without
re-executing the engine.

What's in the snapshot:
  - postmortem.json: full simulation_config, final_state,
    alien_metrics, validation_summary, outcome_classification
  - raw_data.json: per-tick events and validation history
  - annual.json: yearly summary
  - monthly_2026_10.json: monthly summary for 2026-10

Outcome: "survival" (0 alien control, 0 casualties, 8B
population stable, 6 alien ships in system at end of 1 year).
"""

from __future__ import annotations

import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "sim_run_2026-12-27"


def _load(name: str) -> dict:
    path = FIXTURES_DIR / name
    assert path.exists(), f"missing fixture: {name}"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def test_postmortem_outcome_is_survival() -> None:
    """The canonical 2026-12-27 run was classified 'survival'."""
    postmortem = _load("postmortem.json")
    assert postmortem["outcome_classification"] == "survival"
    assert postmortem["final_state"]["population_loss_pct"] == 0.0
    assert postmortem["final_state"]["total_casualties"] == 0
    assert postmortem["final_state"]["alien_control_pct"] == 0.0


def test_postmortem_config_is_standard_scenario() -> None:
    """The 2026-12-27 run used the 'standard' scenario preset."""
    postmortem = _load("postmortem.json")
    assert postmortem["simulation_config"]["scenario"] == "standard"
    assert postmortem["simulation_config"]["world"]["num_countries"] == 195
    assert postmortem["simulation_config"]["world"]["global_population"] == 8_000_000_000


def test_postmortem_validation_passed() -> None:
    """The 2026-12-27 run had no validation failures."""
    postmortem = _load("postmortem.json")
    assert postmortem["validation_summary"]["failed_validations"] == 0
    assert postmortem["validation_summary"]["conservation_violations"] == 0


def test_postmortem_ran_full_one_year() -> None:
    """The 2026-12-27 run covered ~360 days (1 year)."""
    postmortem = _load("postmortem.json")
    duration = postmortem["simulation_duration"]
    assert duration["total_days"] >= 360
    assert duration["start_date"].startswith("2026-01-01")
    assert duration["end_date"].startswith("2026-12")


def test_alien_metrics_reconnaissance_continued() -> None:
    """The reconnaissance-level alien contact grew to 6 ships by year-end."""
    postmortem = _load("postmortem.json")
    assert postmortem["alien_metrics"]["ships_in_system"] == 6
    # Contact was NOT established (the aliens did not commit to invasion).
    assert postmortem["alien_metrics"]["contact_established"] is False


def test_annual_summary_matches_postmortem_final_state() -> None:
    """annual.json and postmortem.json should agree on year-1 totals."""
    annual = _load("annual.json")
    postmortem = _load("postmortem.json")
    assert annual["year"] == 2026
    assert annual["summary"]["population_end"] == postmortem["final_state"]["global_population"]
    assert annual["summary"]["casualties_year"] == postmortem["final_state"]["total_casualties"]


def test_monthly_report_has_one_alien_escalation() -> None:
    """The 2026-10 monthly report captured the alien escalation event."""
    monthly = _load("monthly_2026_10.json")
    assert monthly["month"] == "2026_10"
    assert monthly["num_events"] == 1
    assert monthly["events"][0]["type"] == "alien_escalation"
    assert monthly["events"][0]["day"] == 300


def test_raw_data_validation_history_is_monthly() -> None:
    """The raw_data.json validation_history has ~12 monthly entries
    for a 1-year run."""
    raw = _load("raw_data.json")
    history = raw["validation_history"]
    # 12-13 monthly checkpoints for a 360-day run
    assert 12 <= len(history) <= 14
    # All entries are valid (this run was 0-failure)
    assert all(entry["is_valid"] for entry in history)
