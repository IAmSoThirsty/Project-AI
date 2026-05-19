"""
Recovered Engine Registry — Phase C3A

Central inventory of recovered standalone engines. Engines listed here
are REGISTERED (visible, metadata-described) but NOT ACTIVATED.

Design constraints:
- This module never imports engine code. Import triggers are deferred to
  activation time, which requires explicit config.
- Module-availability is checked with importlib.util.find_spec only —
  no module is exec'd during registry initialization.
- Heavy dependencies (jsonschema, cryptography, cffi) are documented in
  known_blockers, not imported.
- All engines default to enabled=False, status="recovered_unactivated".

To activate an engine, a caller must:
  1. Set the entry's `enabled` flag to True in application config.
  2. Resolve all known_blockers listed in the entry.
  3. Call the engine's own initialization path explicitly.

The registry does NOT do this automatically.
"""

from __future__ import annotations

import importlib.util
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class EngineEntry:
    """Metadata descriptor for a recovered engine.

    No engine code is imported to construct this. All fields are static
    metadata plus a runtime-safe availability probe.
    """

    name: str
    path: str                            # filesystem path relative to project root
    module_path: str                     # Python dotted import path
    status: str                          # always "recovered_unactivated" until explicitly changed
    enabled: bool                        # False until activation config is set
    import_mode: str                     # "lazy" — never auto-imported
    known_blockers: list[str]
    activation_requires_explicit_config: bool
    module_locatable: bool = field(init=False)  # filled by __post_init__

    def __post_init__(self) -> None:
        # find_spec checks if the module is discoverable without importing it.
        # This is safe even when the engine has broken dependencies.
        try:
            spec = importlib.util.find_spec(self.module_path)
            self.module_locatable = spec is not None
        except (ModuleNotFoundError, ValueError):
            self.module_locatable = False

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "module_path": self.module_path,
            "status": self.status,
            "enabled": self.enabled,
            "import_mode": self.import_mode,
            "known_blockers": self.known_blockers,
            "activation_requires_explicit_config": self.activation_requires_explicit_config,
            "module_locatable": self.module_locatable,
        }


# ---------------------------------------------------------------------------
# Registry definitions — pure metadata, no engine code executed
# ---------------------------------------------------------------------------

ENGINES: dict[str, EngineEntry] = {
    "atlas": EngineEntry(
        name="atlas",
        path="engines/atlas/",
        module_path="engines.atlas",
        status="recovered_unactivated",
        enabled=False,
        import_mode="lazy",
        known_blockers=[
            "C3B AUDITED. Two copies: atlas/ (authoritative, top-level) and "
            "engines/atlas/ (mirror). All intra-Atlas imports use 'from atlas.*' — "
            "requires repo root on sys.path, NOT engines/ on sys.path.",
            "engines/ must NOT be added to sys.path globally — it shadows atlas/ "
            "with engines/atlas/ causing ambiguous resolution. Use "
            "AtlasIsolatedContext (scripts/verify/verify_atlas_isolation.py) only.",
            "numpy not installed: 7 files fail on import "
            "(failure_surveillance.py, sensitivity_analyzer.py, driver_engine_10d.py, "
            "temporal_graph.py, agent_simulator.py, monte_carlo_engine.py, "
            "timeline_divergence.py).",
            "scipy not installed: sensitivity_analyzer.py additionally blocked.",
            "jsonschema broken (rpds.rpds missing): schemas/validator.py unimportable. "
            "Cascades to atlas/__init__.py — full atlas package import fails.",
            "CLI entry point (engines/atlas/cli/atlas_cli.py) depends on "
            "schemas/validator.py which is blocked by jsonschema breakage.",
            "Minimum to unblock: pip install numpy scipy rpds-py (or jsonschema upgrade).",
        ],
        activation_requires_explicit_config=True,
    ),
    "hydra_50": EngineEntry(
        name="hydra_50",
        path="engines/hydra_50/",
        module_path="engines.hydra_50",
        status="recovered_unactivated",
        enabled=False,
        import_mode="lazy",
        known_blockers=[
            "C3C-R1 COMPLETE. 585/585 hydra tests pass (0 failures). "
            "Engine core logic is intact. cerberus_hydra.py is clean. "
            "API drift, missing convenience methods, and stale test expectations "
            "were all resolved. Full repair log: recovery/PHASE_C3C_R1_HYDRA_REPAIR_SUMMARY.txt.",
            "Pre-existing runtime wiring NOT introduced by C3C-R1: "
            "src/app/core/hydra_50_integration.py (top-level import at module load), "
            "src/app/cli/hydra_50_cli.py (lazy inside function bodies), "
            "src/app/core/hydra_50_deep_integration.py (lazy, class-instantiation-gated), "
            "src/app/core/security_enforcer.py (lazy, enable_cerberus_hydra=False default), "
            "src/app/gui/hydra_50_panel.py (lazy inside widget render methods). "
            "None of these activate through the engine registry.",
            "Stub scenarios (S21/S31/S41 and others in ranges S12-S20, S22-S30, S32-S40, S42-S50) "
            "use placeholder trigger keys and minimal evaluate_escalation() stubs. "
            "Full scenario implementation is post-C3C-R1 work.",
            "Activation prerequisite: resolve hydra_50_integration.py top-level import "
            "(it constructs Hydra50Engine at call time but the import executes unconditionally). "
            "Minimum: gate that module behind an explicit activation flag before enabling.",
        ],
        activation_requires_explicit_config=True,
    ),
    "sovereign_war_room": EngineEntry(
        name="sovereign_war_room",
        path="engines/sovereign_war_room/",
        module_path="engines.sovereign_war_room",
        status="recovered_unactivated",
        enabled=False,
        import_mode="lazy",
        known_blockers=[
            "C3D-R1 COMPLETE. swr/crypto.py module-level cryptography imports removed. "
            "All 4 imports (Fernet, default_backend, hashes, PBKDF2HMAC) moved inside "
            "CryptoEngine.__init__(). CryptoUnavailableError(RuntimeError) added as "
            "controlled sentinel. pyo3_runtime.PanicException caught via except BaseException "
            "and re-raised cleanly. Importing swr package no longer panics. "
            "Full repair log: recovery/PHASE_C3D_R1_SWR_CRYPTO_REPAIR_SUMMARY.txt.",
            "DEPENDENCY PREFLIGHT SATISFIED in current environment. "
            "cffi 1.17.1 installed; _cffi_backend available. "
            "CryptoEngine() constructs without error (verified 2026-05-19). "
            "Engine remains recovered_unactivated pending explicit activation review. "
            "Note: cffi 2.x removed _cffi_backend; cffi<2 (specifically 1.17.1) required. "
            "Next phase: C3D-R2 controlled smoke test before any activation consideration.",
            "No __init__.py at top level — engines.sovereign_war_room is a namespace "
            "package. All import paths safe post-C3D-R1. "
            "CLI (engines/sovereign_war_room/cli.py) has top-level 'from swr import "
            "SovereignWarRoom' — import is safe; SovereignWarRoom() constructs cleanly "
            "in this environment (cffi 1.17.1 present).",
            "Activation requires explicit decision: set enabled=True and "
            "ENGINE_REGISTRY_ACTIVATION_ENABLED=True. "
            "Do not activate until C3D-R2 smoke test passes. "
            "C3D-R2 scope: controlled SovereignWarRoom() instantiation, "
            "load_scenarios(), execute one scenario — no production traffic.",
        ],
        activation_requires_explicit_config=True,
    ),
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# Global activation gate — all engines are off unless explicitly enabled.
ENGINE_REGISTRY_ACTIVATION_ENABLED: bool = False


def get_engine(name: str) -> EngineEntry | None:
    """Return registry entry for a named engine, or None if not registered."""
    return ENGINES.get(name)


def list_engines() -> list[str]:
    """Return names of all registered engines."""
    return list(ENGINES.keys())


def list_enabled_engines() -> list[str]:
    """Return names of engines where enabled=True. Empty by default."""
    return [name for name, entry in ENGINES.items() if entry.enabled]


def is_engine_locatable(name: str) -> bool:
    """Return True if the engine's package is discoverable (not imported, just spec-checked)."""
    entry = ENGINES.get(name)
    return entry.module_locatable if entry else False
