"""
tarl.modules — TARL module loader.

The module system loads TARL modules by name from a registry. Each Module
has a name and a loader callable. The ModuleSystem holds the registry
and resolves imports, detecting circular dependencies.

This is the minimum surface from legacy `tarl/modules/__init__.py`
(160 LOC). Captures the typed primitive; defers advanced module system
patterns (namespacing, package managers) to a later wave.

Architectural invariants (AGENTS.md v3):
- Downward-only deps: tarl.modules imports only tarl.spec + stdlib.
- Fail-closed: missing modules raise TarlModuleError.
- Deterministic: same import order → same load sequence.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from tarl.spec import TarlError


class TarlModuleError(TarlError):
    """Raised when a TARL module cannot be loaded."""


@dataclass(frozen=True)
class Module:
    """A loaded TARL module.

    Attributes:
        name: Fully-qualified module name (e.g. "tarl.lib.io").
        loader: The callable that produced this module's exports.
        exports: Tuple of public symbol names exposed by this module.
    """

    name: str
    loader: Callable[..., object]
    exports: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise TarlModuleError(f"module name must be non-empty string, got {self.name!r}")
        if not callable(self.loader):
            raise TarlModuleError(f"loader must be callable, got {type(self.loader).__name__}")


@dataclass
class ModuleSystem:
    """Registry and resolver for TARL modules.

    Holds:
    - modules: dict of name → Module
    - loading: set of names currently being loaded (for cycle detection)
    """

    modules: dict[str, Module] = field(default_factory=dict)
    loading: set[str] = field(default_factory=set)

    def register(self, module: Module) -> None:
        """Register a module in the system."""
        if not isinstance(module, Module):
            raise TarlModuleError(f"module must be Module, got {type(module).__name__}")
        if module.name in self.modules:
            raise TarlModuleError(f"module {module.name!r} already registered")
        self.modules[module.name] = module

    def unregister(self, name: str) -> None:
        """Remove a module from the registry."""
        self.modules.pop(name, None)

    def has(self, name: str) -> bool:
        return name in self.modules

    def load(self, name: str) -> Module:
        """Resolve a module by name.

        Detects circular dependencies: if a module is currently being
        loaded, raises TarlModuleError.
        """
        if not isinstance(name, str) or not name.strip():
            raise TarlModuleError(f"module name must be non-empty string, got {name!r}")
        if name in self.loading:
            cycle = " -> ".join(sorted(self.loading | {name}))
            raise TarlModuleError(f"circular dependency detected: {cycle}")
        module = self.modules.get(name)
        if module is None:
            raise TarlModuleError(f"module {name!r} not registered")
        self.loading.add(name)
        try:
            return module
        finally:
            self.loading.discard(name)

    def names(self) -> tuple[str, ...]:
        """Return all registered module names (deterministic order)."""
        return tuple(sorted(self.modules.keys()))


def make_module(
    *,
    name: str,
    loader: Callable[..., object],
    exports: tuple[str, ...] | list[str] = (),
) -> Module:
    """Convenience: construct a Module with validation."""
    if isinstance(exports, list):
        exports_tuple: tuple[str, ...] = tuple(exports)
    elif isinstance(exports, tuple):
        exports_tuple = exports
    else:
        raise TarlModuleError(f"exports must be tuple or list, got {type(exports).__name__}")
    return Module(name=name, loader=loader, exports=exports_tuple)


def default_module_system() -> ModuleSystem:
    """Return an empty module system."""
    return ModuleSystem()


__all__ = [
    "Module",
    "ModuleSystem",
    "TarlModuleError",
    "default_module_system",
    "make_module",
]


def __getattr__(name: str) -> Any:  # pragma: no cover - only for unknown
    raise AttributeError(f"module 'tarl.modules' has no attribute {name!r}")
