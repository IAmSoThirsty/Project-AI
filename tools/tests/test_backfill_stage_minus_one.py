from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "backfill_stage_minus_one.py"
SPEC = importlib.util.spec_from_file_location("backfill_stage_minus_one", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_extract_dois_normalizes_full_and_bare_urls() -> None:
    text = "https://doi.org/10.5281/zenodo.123 and 10.5281/zenodo.456"
    assert MODULE.extract_dois(text) == {"123", "456"}


def test_disposition_keeps_migration_sources_visible() -> None:
    result = MODULE.disposition("src/app/core/execution_gate.py")
    assert "scheduled" in result
    assert "frozen history" in result


def test_disposition_excludes_runtime_state() -> None:
    assert MODULE.disposition("data/runtime/state.json") == "excluded generated/runtime state"
