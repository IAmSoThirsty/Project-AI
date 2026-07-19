"""Project-AI Sovereign War Room public interface."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from swr.core import DEFAULT_TOKEN_TTL, WarRoomCore, scenario_to_dict
from swr.scenario import Difficulty, Scenario, ScenarioLibrary, ScenarioType
from swr.war_room import RECORD_OPERATION, ScenarioResult, SovereignWarRoom, keyword_score

# Phase T5b: the SWR package is specified in TSCG-B (4th tier).
# Lazy import so a missing thirsty-lang dep does not crash the
# rest of the package; the spec is opt-in.
try:
    from swr.tscg_b_spec import (
        EXPECTED_SHA256_HEX,
        EXPECTED_TEXT,
        TSCGBSWRSpec,
        TSCGBSWRSpecError,
        load_spec,
    )

    _TSCG_B_IMPORT_ERROR: str | None = None
except ImportError as _import_error:  # pragma: no cover - fail-closed
    _TSCG_B_IMPORT_ERROR = str(_import_error)
    EXPECTED_TEXT = None  # type: ignore[assignment,misc]
    EXPECTED_SHA256_HEX = None  # type: ignore[assignment,misc]
    TSCGBSWRSpec = None  # type: ignore[assignment,misc]
    TSCGBSWRSpecError = None  # type: ignore[assignment,misc]
    load_spec = None  # type: ignore[assignment]

try:
    __version__ = _pkg_version("project-ai-swr")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "DEFAULT_TOKEN_TTL",
    "EXPECTED_SHA256_HEX",
    "EXPECTED_TEXT",
    "RECORD_OPERATION",
    "Difficulty",
    "Scenario",
    "ScenarioLibrary",
    "ScenarioResult",
    "ScenarioType",
    "SovereignWarRoom",
    "TSCGBSWRSpec",
    "TSCGBSWRSpecError",
    "WarRoomCore",
    "keyword_score",
    "load_spec",
    "scenario_to_dict",
]
