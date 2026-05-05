
from __future__ import annotations

from dataclasses import dataclass, field

from . import ast


@dataclass(frozen=True)
class Type:
    name: str
    args: tuple["Type", ...] = field(default_factory=tuple)

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


def reservoir(of: Type) -> Type:
    return Type("Reservoir", (of,))


def option(of: Type) -> Type:
    return Type("Quenched", (of,))


def task(of: Type) -> Type:
    return Type("Task", (of,))


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
        }
        return base.get(node.name, Type(node.name))
    if isinstance(node, ast.GenericType):
        base = "Reservoir" if node.base == "well" else node.base
        return Type(base, tuple(from_type_node(x) for x in node.args))
    if isinstance(node, ast.FunctionType):
        return Type("Function", tuple([from_type_node(x) for x in node.params] + [from_type_node(node.result)]))
    raise TypeError(f"unsupported type node: {node!r}")


def is_option(t: Type) -> bool:
    return t.name == "Quenched" and len(t.args) == 1


def option_inner(t: Type) -> Type:
    return t.args[0] if is_option(t) else ANY


def equals(a: Type, b: Type) -> bool:
    if a == b or a == ANY or b == ANY:
        return True
    if is_option(a) and is_option(b):
        return equals(option_inner(a), option_inner(b))
    return False
