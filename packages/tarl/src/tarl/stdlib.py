"""
tarl.stdlib — TARL standard library surface.

The standard library provides a registry of built-in operations available
to TARL programs. Each BuiltInFunction has a name, optional arity, and
a callable. The StandardLibrary aggregates them into a registry.

This is the minimum surface from legacy `tarl/stdlib/__init__.py`
(197 LOC). Captures the typed primitive; defers built-in implementations
to a later wave.

Architectural invariants (AGENTS.md v3):
- Downward-only deps: tarl.stdlib imports only stdlib.
- Fail-closed: missing built-ins raise TarlStdlibError; never silent.
- Canonical types: BuiltInFunction is immutable (frozen dataclass).
- Deterministic: registry order preserved.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from tarl.spec import TarlError


class TarlStdlibError(TarlError):
    """Raised when a TARL stdlib operation fails."""


@dataclass(frozen=True)
class BuiltInFunction:
    """A single built-in function.

    Attributes:
        name: The function's name (e.g. "len").
        arity: The expected number of arguments (-1 = variadic).
        func: The actual Python callable.
    """

    name: str
    arity: int
    func: Callable[..., object]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise TarlStdlibError(f"built-in name must be non-empty string, got {self.name!r}")
        if not isinstance(self.arity, int) or isinstance(self.arity, bool):
            raise TarlStdlibError(f"arity must be int, got {type(self.arity).__name__}")
        if self.arity < -1:
            raise TarlStdlibError(f"arity must be >= -1, got {self.arity}")
        if not callable(self.func):
            raise TarlStdlibError(f"func must be callable, got {type(self.func).__name__}")


@dataclass(frozen=True)
class StandardLibrary:
    """A registry of built-in functions.

    Constructed via make_stdlib() with a list of BuiltInFunction.
    """

    builtins: tuple[BuiltInFunction, ...]

    def __post_init__(self) -> None:
        names = [b.name for b in self.builtins]
        if len(names) != len(set(names)):
            duplicates = {n for n in names if names.count(n) > 1}
            raise TarlStdlibError(f"duplicate built-in names: {sorted(duplicates)}")

    def get(self, name: str) -> BuiltInFunction:
        """Look up a built-in by name. Raises TarlStdlibError if missing."""
        if not isinstance(name, str):
            raise TarlStdlibError(f"name must be str, got {type(name).__name__}")
        for b in self.builtins:
            if b.name == name:
                return b
        raise TarlStdlibError(f"unknown built-in: {name!r}")

    def has(self, name: str) -> bool:
        """Return True if a built-in with this name exists."""
        if not isinstance(name, str):
            return False
        return any(b.name == name for b in self.builtins)

    def names(self) -> tuple[str, ...]:
        """Return all built-in names (deterministic order)."""
        return tuple(b.name for b in self.builtins)

    def call(self, name: str, *args: object, **kwargs: object) -> object:
        """Look up and invoke a built-in by name."""
        builtin = self.get(name)
        if builtin.arity >= 0 and (len(args) + len(kwargs)) != builtin.arity:
            raise TarlStdlibError(
                f"built-in {name!r} expects {builtin.arity} args, got {len(args) + len(kwargs)}"
            )
        return builtin.func(*args, **kwargs)


def make_stdlib(builtins: list[BuiltInFunction]) -> StandardLibrary:
    """Construct a StandardLibrary from a list of BuiltInFunction."""
    if not isinstance(builtins, list):
        raise TarlStdlibError(f"builtins must be list, got {type(builtins).__name__}")
    for i, b in enumerate(builtins):
        if not isinstance(b, BuiltInFunction):
            raise TarlStdlibError(f"builtins[{i}] must be BuiltInFunction, got {type(b).__name__}")
    return StandardLibrary(builtins=tuple(builtins))


# Default standard library: minimal set of utilities.
def _builtin_len(x: object) -> int:
    if not hasattr(x, "__len__"):
        raise TarlStdlibError(f"object of type {type(x).__name__} has no len()")
    return len(x)


def _builtin_str(x: object) -> str:
    return str(x)


def _builtin_int(x: object) -> int:
    if isinstance(x, bool):
        return int(x)
    if not isinstance(x, int):
        result: int
        try:
            result = int(x)  # type: ignore[call-overload]
        except (TypeError, ValueError) as error:
            raise TarlStdlibError(f"cannot convert {type(x).__name__} to int: {error}") from error
        return result
    return x


def _builtin_max(*args: object) -> object:
    if not args:
        raise TarlStdlibError("max() requires at least one argument")
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        return max(args[0])
    return max(*args)  # type: ignore[call-overload]


def _builtin_min(*args: object) -> object:
    if not args:
        raise TarlStdlibError("min() requires at least one argument")
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        return min(args[0])
    return min(*args)  # type: ignore[call-overload]


DEFAULT_STDLIB: StandardLibrary = make_stdlib(
    [
        BuiltInFunction("len", 1, _builtin_len),
        BuiltInFunction("str", 1, _builtin_str),
        BuiltInFunction("int", 1, _builtin_int),
        BuiltInFunction("max", -1, _builtin_max),
        BuiltInFunction("min", -1, _builtin_min),
    ]
)


__all__ = [
    "DEFAULT_STDLIB",
    "BuiltInFunction",
    "StandardLibrary",
    "TarlStdlibError",
    "make_stdlib",
]


def __getattr__(name: str) -> Any:  # pragma: no cover - only for unknown
    raise AttributeError(f"module 'tarl.stdlib' has no attribute {name!r}")
