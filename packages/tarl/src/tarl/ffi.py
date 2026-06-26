"""
tarl.ffi — TARL Foreign Function Interface (FFI) bridge.

The FFI bridge allows TARL code to invoke external Python callables in a
type-safe way. Each ForeignFunction wraps an external callable with
explicit input/output type assertions. The FFIBridge holds the registry.

This is the minimum surface from legacy `tarl/ffi/__init__.py` (149 LOC).
Captures the typed primitive; defers C-library bindings to a later wave
(legacy FFI is aspirational and not deeply exercised).

Architectural invariants (AGENTS.md v3):
- Downward-only deps: tarl.ffi imports only tarl.spec + stdlib.
- Fail-closed: missing FFI bindings raise TarlFFIError; foreign calls
  that violate type assertions raise TarlFFIError.
- Deterministic: registry order preserved.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from tarl.spec import TarlError


class TarlFFIError(TarlError):
    """Raised when a TARL FFI operation fails."""


@dataclass(frozen=True)
class ForeignFunction:
    """A wrapper for an external callable.

    Attributes:
        name: FFI binding name.
        arg_types: Tuple of expected argument types (or "object" for any).
        ret_type: Expected return type (or "object").
        func: The actual Python callable.
    """

    name: str
    arg_types: tuple[type[object], ...]
    ret_type: type[object]
    func: Callable[..., object]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise TarlFFIError(f"ffi name must be non-empty string, got {self.name!r}")
        if not isinstance(self.arg_types, tuple):
            raise TarlFFIError(f"arg_types must be tuple, got {type(self.arg_types).__name__}")
        if not isinstance(self.ret_type, type):
            raise TarlFFIError(f"ret_type must be type, got {type(self.ret_type).__name__}")
        if not callable(self.func):
            raise TarlFFIError(f"func must be callable, got {type(self.func).__name__}")

    def call(self, *args: object) -> object:
        """Invoke the foreign function with type-checked args.

        Raises TarlFFIError if arg types don't match or the function
        returns the wrong type.
        """
        if len(args) != len(self.arg_types):
            raise TarlFFIError(
                f"ffi {self.name!r} expects {len(self.arg_types)} args, got {len(args)}"
            )
        for i, (arg, expected) in enumerate(zip(args, self.arg_types, strict=False)):
            # Allow object as wildcard
            if expected is object:
                continue
            # Special handling for bool (which is subclass of int)
            if expected is bool and isinstance(arg, bool):
                continue
            if not isinstance(arg, expected):
                raise TarlFFIError(
                    f"ffi {self.name!r} arg[{i}]: expected "
                    f"{expected.__name__}, got {type(arg).__name__}"
                )
        result = self.func(*args)
        if not isinstance(result, self.ret_type):
            # Allow bool/int subclass matches
            if (self.ret_type is int and isinstance(result, bool)) or (
                self.ret_type is bool and isinstance(result, int)
            ):
                pass
            else:
                raise TarlFFIError(
                    f"ffi {self.name!r} returned "
                    f"{type(result).__name__}, expected {self.ret_type.__name__}"
                )
        return result


@dataclass(frozen=True)
class FFIBridge:
    """A registry of foreign function bindings."""

    bindings: tuple[ForeignFunction, ...]

    def __post_init__(self) -> None:
        names = [b.name for b in self.bindings]
        if len(names) != len(set(names)):
            duplicates = {n for n in names if names.count(n) > 1}
            raise TarlFFIError(f"duplicate ffi binding names: {sorted(duplicates)}")

    def get(self, name: str) -> ForeignFunction:
        """Look up a binding by name."""
        if not isinstance(name, str):
            raise TarlFFIError(f"name must be str, got {type(name).__name__}")
        for b in self.bindings:
            if b.name == name:
                return b
        raise TarlFFIError(f"unknown ffi binding: {name!r}")

    def has(self, name: str) -> bool:
        """Return True if a binding with this name exists."""
        if not isinstance(name, str):
            return False
        return any(b.name == name for b in self.bindings)

    def names(self) -> tuple[str, ...]:
        """Return all binding names (deterministic order)."""
        return tuple(b.name for b in self.bindings)

    def call(self, name: str, *args: object) -> object:
        """Look up and invoke a binding by name."""
        return self.get(name).call(*args)


def make_ffi(bindings: list[ForeignFunction]) -> FFIBridge:
    """Construct an FFIBridge from a list of ForeignFunction."""
    if not isinstance(bindings, list):
        raise TarlFFIError(f"bindings must be list, got {type(bindings).__name__}")
    for i, b in enumerate(bindings):
        if not isinstance(b, ForeignFunction):
            raise TarlFFIError(f"bindings[{i}] must be ForeignFunction, got {type(b).__name__}")
    return FFIBridge(bindings=tuple(bindings))


def default_ffi() -> FFIBridge:
    """Return an empty FFI bridge (no bindings)."""
    return FFIBridge(bindings=())


__all__ = [
    "FFIBridge",
    "ForeignFunction",
    "TarlFFIError",
    "default_ffi",
    "make_ffi",
]


def __getattr__(name: str) -> Any:  # pragma: no cover - only for unknown
    raise AttributeError(f"module 'tarl.ffi' has no attribute {name!r}")
