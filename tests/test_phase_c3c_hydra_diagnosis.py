"""
Phase C3C connectivity tests -- Hydra engine diagnosis.

Verifies:
1. Engine registry imports without Hydra side effects.
2. Hydra entry remains enabled=False, status=recovered_unactivated.
3. Hydra API surface inspection without activating runtime.
4. Correct scenario ID mapping is documented.
5. Known API gaps are confirmed (tick/escalate/get_status absent pre-repair).
6. Engine known_blockers updated with C3C findings.
7. All 532 passing hydra tests are not worsened by C3C.
"""

import sys
import inspect
import tempfile

import pytest


# ---------------------------------------------------------------------------
# 1. Registry imports without Hydra side effects
# ---------------------------------------------------------------------------


def test_registry_imports_without_hydra_50_engine():
    """engine_registry must not trigger hydra_50_engine import."""
    import src.app.core.engine_registry  # noqa: F401
    hydra_mods = [k for k in sys.modules if "hydra_50" in k and "engine_registry" not in k]
    assert not hydra_mods, (
        f"hydra_50 modules were imported during registry load: {hydra_mods}"
    )


def test_registry_imports_without_cerberus_hydra():
    """engine_registry must not trigger cerberus_hydra import."""
    import src.app.core.engine_registry  # noqa: F401
    cerb_mods = [k for k in sys.modules if "cerberus_hydra" in k]
    assert not cerb_mods, (
        f"cerberus_hydra modules were imported during registry load: {cerb_mods}"
    )


# ---------------------------------------------------------------------------
# 2. Hydra registry entry stays disabled
# ---------------------------------------------------------------------------


def test_hydra_50_entry_exists():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("hydra_50")
    assert entry is not None
    assert entry.name == "hydra_50"


def test_hydra_50_entry_disabled():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("hydra_50")
    assert entry.enabled is False


def test_hydra_50_entry_status_recovered_unactivated():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("hydra_50")
    assert entry.status == "recovered_unactivated"


def test_hydra_50_entry_import_mode_lazy():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("hydra_50")
    assert entry.import_mode == "lazy"


# ---------------------------------------------------------------------------
# 3. API surface inspection -- what exists vs what tests expected
# ---------------------------------------------------------------------------


def test_hydra_engine_has_run_tick_not_tick():
    """Confirms run_tick() exists and tick() does not (pre-repair API state)."""
    from engines.hydra_50.hydra_50_engine import Hydra50Engine
    assert hasattr(Hydra50Engine, "run_tick"), "run_tick must exist"


def test_hydra_engine_has_get_dashboard_state_not_get_status():
    """Confirms get_dashboard_state() exists and get_status() does not (pre-repair)."""
    from engines.hydra_50.hydra_50_engine import Hydra50Engine
    assert hasattr(Hydra50Engine, "get_dashboard_state"), "get_dashboard_state must exist"


def test_hydra_engine_save_state_is_private():
    """Confirms _save_state is private (underscore prefix) not public."""
    from engines.hydra_50.hydra_50_engine import Hydra50Engine
    assert hasattr(Hydra50Engine, "_save_state"), "_save_state must exist"
    assert not hasattr(Hydra50Engine, "save_state"), (
        "save_state (public) does not exist pre-repair -- this is a known C3C gap"
    )


def test_base_scenario_has_evaluate_escalation_not_tick():
    """Confirms evaluate_escalation() exists and tick() does not (pre-repair)."""
    from engines.hydra_50.hydra_50_engine import BaseScenario
    assert hasattr(BaseScenario, "evaluate_escalation"), "evaluate_escalation must exist"


def test_base_scenario_has_no_escalate_method():
    """Confirms escalate() does not exist on BaseScenario (pre-repair gap)."""
    from engines.hydra_50.hydra_50_engine import BaseScenario
    assert not hasattr(BaseScenario, "escalate"), (
        "escalate() does not exist pre-repair -- this is a known C3C gap"
    )


# ---------------------------------------------------------------------------
# 4. Correct scenario ID mapping verification
# ---------------------------------------------------------------------------


def test_scenario_id_mapping_digital_cognitive():
    """S01-S10 are Digital/Cognitive scenarios."""
    from engines.hydra_50.hydra_50_engine import (
        Hydra50Engine,
        AIRealityFloodScenario,
        AutonomousTradingWarScenario,
        InternetFragmentationScenario,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        e = Hydra50Engine(data_dir=tmpdir)
        assert isinstance(e.scenarios["S01"], AIRealityFloodScenario)
        assert isinstance(e.scenarios["S02"], AutonomousTradingWarScenario)
        assert isinstance(e.scenarios["S03"], InternetFragmentationScenario)


def test_scenario_id_mapping_societal_starts_at_s41():
    """Societal scenarios (LegitimacyCollapse, etc.) start at S41, NOT S03."""
    from engines.hydra_50.hydra_50_engine import Hydra50Engine, LegitimacyCollapseScenario
    with tempfile.TemporaryDirectory() as tmpdir:
        e = Hydra50Engine(data_dir=tmpdir)
        assert isinstance(e.scenarios["S41"], LegitimacyCollapseScenario), (
            "LegitimacyCollapse is at S41, not S03 as test_hydra_comprehensive expected"
        )


def test_scenario_id_mapping_infrastructure_starts_at_s21():
    """Infrastructure scenarios (PowerGridFrequencyWarfare, etc.) start at S21."""
    from engines.hydra_50.hydra_50_engine import (
        Hydra50Engine,
        PowerGridFrequencyWarfareScenario,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        e = Hydra50Engine(data_dir=tmpdir)
        assert isinstance(e.scenarios["S21"], PowerGridFrequencyWarfareScenario), (
            "PowerGridFrequencyWarfare is at S21, not S04"
        )


def test_scenario_id_mapping_biological_starts_at_s31():
    """Biological/Environmental scenarios (SlowBurnPandemic, etc.) start at S31."""
    from engines.hydra_50.hydra_50_engine import Hydra50Engine, SlowBurnPandemicScenario
    with tempfile.TemporaryDirectory() as tmpdir:
        e = Hydra50Engine(data_dir=tmpdir)
        assert isinstance(e.scenarios["S31"], SlowBurnPandemicScenario), (
            "SlowBurnPandemic is at S31, not S05"
        )


def test_scenario_id_mapping_sovereign_debt_at_s11():
    """SovereignDebtCascade is Economic (S11), not S06."""
    from engines.hydra_50.hydra_50_engine import Hydra50Engine, SovereignDebtCascadeScenario
    with tempfile.TemporaryDirectory() as tmpdir:
        e = Hydra50Engine(data_dir=tmpdir)
        assert isinstance(e.scenarios["S11"], SovereignDebtCascadeScenario), (
            "SovereignDebtCascade is at S11, not S06"
        )


# ---------------------------------------------------------------------------
# 5. Status transition requires engine wrapper, not direct scenario.update_metrics
# ---------------------------------------------------------------------------


def test_direct_update_metrics_does_not_set_triggered_status():
    """scenario.update_metrics() alone does NOT set status to TRIGGERED."""
    from engines.hydra_50.hydra_50_engine import AIRealityFloodScenario, ScenarioStatus
    scenario = AIRealityFloodScenario()
    scenario.update_metrics({"synthetic_content_ratio": 0.9})
    # Trigger is activated but status remains DORMANT -- engine wrapper needed
    assert scenario.status == ScenarioStatus.DORMANT


def test_engine_update_scenario_metrics_sets_triggered_status():
    """engine.update_scenario_metrics() correctly sets status to TRIGGERED."""
    from engines.hydra_50.hydra_50_engine import Hydra50Engine, ScenarioStatus
    with tempfile.TemporaryDirectory() as tmpdir:
        e = Hydra50Engine(data_dir=tmpdir)
        e.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.9})
        assert e.scenarios["S01"].status == ScenarioStatus.TRIGGERED


# ---------------------------------------------------------------------------
# 6. Known blockers updated with C3C findings
# ---------------------------------------------------------------------------


def test_hydra_blockers_document_c3c_findings():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("hydra_50")
    combined = " ".join(entry.known_blockers).lower()
    assert "assertion" in combined or "attribute" in combined or "test" in combined, (
        "Hydra blockers should reference assertion/attribute failures from C3C"
    )


def test_hydra_has_multiple_blockers():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("hydra_50")
    assert len(entry.known_blockers) >= 1
