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
            "Package name collision: 'atlas/' top-level dir shadows 'engines/atlas/' "
            "when PYTHONPATH includes project root — atlas CLI resolves wrong package.",
            "CLI entry point (engines/atlas/cli/atlas_cli.py) untested in this env.",
            "No runtime src/ wiring — only docs and README reference atlas.",
            "Requires C3B: import path audit and PYTHONPATH isolation before activation.",
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
            "engines/hydra_50/cerberus_hydra.py has assertion and attribute errors "
            "in test_hydra_comprehensive.py (27 tests, mixed pass/fail).",
            "Not imported by src/ runtime — test-suite-only references.",
            "Requires C3C: assertion/attribute failures must be diagnosed before activation.",
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
            "_cffi_backend not installed in this environment — cryptography package "
            "panics at pyo3 level when imported, bypassing try/except ImportError.",
            "No __init__.py (namespace package) — module_path resolves as namespace "
            "but submodules may fail to import.",
            "CLI (engines/sovereign_war_room/cli.py) crashes on import due to "
            "cryptography/_cffi_backend pyo3 panic.",
            "Requires C3D: _cffi_backend / cryptography dependency isolation "
            "before any submodule import is safe.",
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
