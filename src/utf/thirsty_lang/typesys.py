from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from . import ast


@dataclass(frozen=True)
class Type:
    name: str
    args: tuple[Type, ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        if not self.args:
            return self.name
        return f"{self.name}[{', '.join(map(str, self.args))}]"


INT = Type("Int")
FLOAT = Type("Float")
BOOL = Type("Bool")
STRING = Type("String")
VOID = Type("Void")
ANY = Type("Any")
ERROR = Type("Error")

# Phase 3 built-in opaque handle types (used by thirst::net)
CONNECTION = Type("Connection")
SERVER = Type("Server")


def reservoir(of: Type) -> Type:
    return Type("Reservoir", (of,))


def option(of: Type) -> Type:
    return Type("Quenched", (of,))


def task(of: Type) -> Type:
    return Type("Task", (of,))


def result(ok: Type, err: Type) -> Type:
    """Result[T, E] — the success/failure union type."""
    return Type("Result", (ok, err))


def governed(inner: Type) -> Type:
    """Governed[T] — wraps a type produced by a governance-annotated function."""
    return Type("Governed", (inner,))


# ------------------------------------------------------------------
# User-defined type descriptors (Phase 3A)
# ------------------------------------------------------------------

@dataclass
class EnumType:
    """Descriptor for an `enum` declaration."""
    name: str
    variants: List[str]

    def as_type(self) -> Type:
        return Type(self.name)


@dataclass
class StructField:
    name: str
    type_: Type
    optional: bool = False


@dataclass
class StructType:
    """Descriptor for a `struct` declaration."""
    name: str
    fields: List[StructField]

    def as_type(self) -> Type:
        return Type(self.name)


@dataclass
class InterfaceMethod:
    name: str
    param_types: List[Type]
    return_type: Type


@dataclass
class InterfaceType:
    """Descriptor for an `interface` declaration."""
    name: str
    methods: List[InterfaceMethod]

    def as_type(self) -> Type:
        return Type(self.name)


# ------------------------------------------------------------------
# Authority levels for governance annotations (Phase 3B)
# ------------------------------------------------------------------

AUTHORITY_LEVELS = ["AC1", "AC2", "AC3", "AC4", "AC5"]

AUTHORITY_CLASS = EnumType("AuthorityClass", AUTHORITY_LEVELS)


# ------------------------------------------------------------------
# Type resolution
# ------------------------------------------------------------------

# Registry for user-defined types (populated by checker at analysis time)
_USER_TYPES: Dict[str, EnumType | StructType | InterfaceType] = {}


def register_type(descriptor: EnumType | StructType | InterfaceType) -> None:
    _USER_TYPES[descriptor.name] = descriptor


def lookup_user_type(name: str) -> Optional[EnumType | StructType | InterfaceType]:
    return _USER_TYPES.get(name)


def from_type_node(node: ast.TypeNode) -> Type:
    if isinstance(node, ast.NamedType):
        base = {
            "Int": INT,
            "Float": FLOAT,
            "Bool": BOOL,
            "String": STRING,
            "Void": VOID,
            "Any": ANY,
            "Error": ERROR,
            "Connection": CONNECTION,
            "Server": SERVER,
        }
        if node.name in base:
            return base[node.name]
        # Check user-defined types
        ud = _USER_TYPES.get(node.name)
        if ud is not None:
            return ud.as_type()
        return Type(node.name)
    if isinstance(node, ast.GenericType):
        base_name = "Reservoir" if node.base == "well" else node.base
        args = tuple(from_type_node(x) for x in node.args)
        # Validate known generic forms
        if base_name == "Result" and len(args) != 2:
            raise TypeError("Result[T, E] requires exactly two type arguments")
        if base_name in ("Quenched", "Task", "Governed", "Reservoir") and len(args) != 1:
            raise TypeError(f"{base_name}[T] requires exactly one type argument")
        return Type(base_name, args)
    if isinstance(node, ast.FunctionType):
        return Type(
            "Function",
            tuple(
                [from_type_node(x) for x in node.params] + [from_type_node(node.result)]
            ),
        )
    raise TypeError(f"unsupported type node: {node!r}")


def is_option(t: Type) -> bool:
    return t.name == "Quenched" and len(t.args) == 1


def option_inner(t: Type) -> Type:
    return t.args[0] if is_option(t) else ANY


def is_result(t: Type) -> bool:
    return t.name == "Result" and len(t.args) == 2


def result_ok(t: Type) -> Type:
    return t.args[0] if is_result(t) else ANY


def result_err(t: Type) -> Type:
    return t.args[1] if is_result(t) else ERROR


def is_governed(t: Type) -> bool:
    return t.name == "Governed" and len(t.args) == 1


def governed_inner(t: Type) -> Type:
    return t.args[0] if is_governed(t) else ANY


def equals(a: Type, b: Type) -> bool:
    if a == b or a == ANY or b == ANY:
        return True
    if is_option(a) and is_option(b):
        return equals(option_inner(a), option_inner(b))
    if is_result(a) and is_result(b):
        return equals(result_ok(a), result_ok(b)) and equals(result_err(a), result_err(b))
    if is_governed(a) and is_governed(b):
        return equals(governed_inner(a), governed_inner(b))
    # Governed[T] is assignment-compatible with T (unwrapping is implicit)
    if is_governed(a):
        return equals(governed_inner(a), b)
    if is_governed(b):
        return equals(a, governed_inner(b))
    return False
