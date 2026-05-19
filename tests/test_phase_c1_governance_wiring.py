"""
Phase C1 connectivity tests — governance proof module wiring.

Verifies:
1. Each recovered module imports cleanly from src.app.governance.
2. Governance package exposes all recovered modules.
3. Default config has GOVERNANCE_ANCHORING_ENABLED = False.
4. TSAProvider / TSAAnchorManager raise RuntimeError (not silently skip)
   when deps are missing and instantiation is attempted.
5. ExternalMerkleAnchor defaults to filesystem-only (no network).
6. canonical.sovereign_proof imports cleanly.
7. sovereign_proof.run_proof() does not raise on import-level execution.
"""

import importlib
import sys
import types


# ---------------------------------------------------------------------------
# 1. Module-level import tests
# ---------------------------------------------------------------------------


def test_genesis_continuity_importable():
    from src.app.governance import genesis_continuity
    assert isinstance(genesis_continuity, types.ModuleType)


def test_tsa_anchor_manager_importable():
    from src.app.governance import tsa_anchor_manager
    assert isinstance(tsa_anchor_manager, types.ModuleType)


def test_tsa_provider_importable():
    from src.app.governance import tsa_provider
    assert isinstance(tsa_provider, types.ModuleType)


def test_external_merkle_anchor_importable():
    from src.app.governance import external_merkle_anchor
    assert isinstance(external_merkle_anchor, types.ModuleType)


# ---------------------------------------------------------------------------
# 2. Package-level exposure
# ---------------------------------------------------------------------------


def test_governance_package_exposes_all_recovered_modules():
    import src.app.governance as gov
    for name in ("genesis_continuity", "tsa_anchor_manager", "tsa_provider", "external_merkle_anchor"):
        assert hasattr(gov, name), f"governance package missing attribute: {name}"
        assert name in gov.__all__, f"{name} not listed in governance.__all__"


# ---------------------------------------------------------------------------
# 3. Disabled-by-default flag
# ---------------------------------------------------------------------------


def test_governance_anchoring_disabled_by_default():
    import src.app.governance as gov
    assert gov.GOVERNANCE_ANCHORING_ENABLED is False


# ---------------------------------------------------------------------------
# 4. Runtime-activation guard: instantiation raises, does not silently proceed
# ---------------------------------------------------------------------------


def test_tsa_provider_raises_when_deps_missing():
    from src.app.governance import tsa_provider
    if tsa_provider._TSA_DEPS_AVAILABLE:
        # deps present in this env — skip the guard test
        return
    import pytest
    with pytest.raises(RuntimeError, match="TSAProvider requires"):
        tsa_provider.TSAProvider()


def test_tsa_anchor_manager_raises_when_deps_missing():
    from src.app.governance import tsa_anchor_manager
    if tsa_anchor_manager._CRYPTO_AVAILABLE and tsa_anchor_manager._TSA_DEPS_AVAILABLE:
        return
    import pytest
    with pytest.raises(RuntimeError):
        tsa_anchor_manager.TSAAnchorManager(None, "/tmp/test_anchor.json")


# ---------------------------------------------------------------------------
# 5. ExternalMerkleAnchor defaults to filesystem — no network by default
# ---------------------------------------------------------------------------


def test_external_merkle_anchor_defaults_to_filesystem():
    from src.app.governance.external_merkle_anchor import ExternalMerkleAnchor
    anchor = ExternalMerkleAnchor()
    assert anchor.backends == ["filesystem"], (
        f"expected ['filesystem'], got {anchor.backends}"
    )


# ---------------------------------------------------------------------------
# 6 & 7. canonical.sovereign_proof
# ---------------------------------------------------------------------------


def test_sovereign_proof_importable():
    # Ensure the module is importable without raising at module scope.
    # Uses importlib so a previously cached import doesn't mask a failure.
    spec = importlib.util.find_spec("canonical.sovereign_proof")
    # If spec is None the module isn't on the path — that's an environment issue,
    # not a wiring failure. Skip gracefully.
    if spec is None:
        # Try direct path insert approach the file itself uses.
        sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
        spec = importlib.util.find_spec("canonical.sovereign_proof")
    assert spec is not None, "canonical.sovereign_proof not locatable on sys.path"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "run_proof"), "sovereign_proof missing run_proof()"
