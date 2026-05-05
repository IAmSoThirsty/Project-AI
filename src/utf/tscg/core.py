from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Iterable

CORE_SYMBOLS = {
    "COG": "cognition proposal",
    "DNT": "delta non-terminal / mutation proposal",
    "SHD": "deterministic shadow simulation",
    "INV": "invariant engine",
    "CAP": "capability authorization",
    "QRM": "quorum",
    "COM": "canonical commit",
    "ANC": "anchor",
    "RFX": "reflex containment",
}

TOKEN_RE = re.compile(r"\s*(->|\^|\|\||\(|\)|,|[A-Za-z_][A-Za-z0-9_]*|\d+)\s*")


@dataclass
class Symbol:
    name: str
    args: list[str] = field(default_factory=list)


@dataclass
class Pipeline:
    items: list["Expr"]


@dataclass
class Combine:
    op: str
    left: "Expr"
    right: "Expr"


Expr = Symbol | Pipeline | Combine


class Parser:
    def __init__(self, text: str):
        self.tokens = [t for t in TOKEN_RE.findall(text) if t.strip()]
        self.i = 0

    def parse(self) -> Expr:
        expr = self._pipeline()
        if self.i != len(self.tokens):
            raise ValueError(f"unexpected trailing token {self.tokens[self.i]!r}")
        return expr

    def _pipeline(self) -> Expr:
        items = [self._combine()]
        while self._match("->"):
            items.append(self._combine())
        if len(items) == 1:
            return items[0]
        return Pipeline(items)

    def _combine(self) -> Expr:
        expr = self._primary()
        while self._match("^", "||"):
            op = self.tokens[self.i - 1]
            right = self._primary()
            expr = Combine(op, expr, right)
        return expr

    def _primary(self) -> Expr:
        if self._match("("):
            expr = self._pipeline()
            self._expect(")")
            return expr
        name = self._expect_ident()
        args = []
        if self._match("("):
            if not self._check(")"):
                args.append(self._expect_atom())
                while self._match(","):
                    args.append(self._expect_atom())
            self._expect(")")
        return Symbol(name, args)

    def _expect_atom(self) -> str:
        if self.i >= len(self.tokens):
            raise ValueError("unexpected end of input")
        tok = self.tokens[self.i]
        self.i += 1
        return tok

    def _expect_ident(self) -> str:
        tok = self._expect_atom()
        if tok in {"->", "^", "||", "(", ")", ","}:
            raise ValueError(f"expected symbol, found {tok!r}")
        return tok

    def _match(self, *values: str) -> bool:
        if self.i < len(self.tokens) and self.tokens[self.i] in values:
            self.i += 1
            return True
        return False

    def _check(self, value: str) -> bool:
        return self.i < len(self.tokens) and self.tokens[self.i] == value

    def _expect(self, value: str) -> str:
        if not self._match(value):
            got = self.tokens[self.i] if self.i < len(self.tokens) else "<eof>"
            raise ValueError(f"expected {value!r}, found {got!r}")
        return value


def parse(text: str) -> Expr:
    return Parser(text).parse()


def canonical(expr: Expr) -> str:
    if isinstance(expr, Symbol):
        if expr.args:
            return f"{expr.name}({','.join(expr.args)})"
        return expr.name
    if isinstance(expr, Pipeline):
        return " -> ".join(canonical(x) for x in expr.items)
    if isinstance(expr, Combine):
        return f"{canonical(expr.left)} {expr.op} {canonical(expr.right)}"
    raise TypeError(expr)


def checksum(expr: Expr) -> str:
    return hashlib.sha256(canonical(expr).encode("utf-8")).hexdigest()


def validate(expr: Expr) -> None:
    for sym in iter_symbols(expr):
        if sym.name not in CORE_SYMBOLS and sym.name not in {"ING", "LED", "SAFE", "MUT", "SEL", "QRM_LINEAR", "QRM_STATIC"}:
            raise ValueError(f"undefined TSCG symbol '{sym.name}'")


def iter_symbols(expr: Expr) -> Iterable[Symbol]:
    if isinstance(expr, Symbol):
        yield expr
    elif isinstance(expr, Pipeline):
        for item in expr.items:
            yield from iter_symbols(item)
    elif isinstance(expr, Combine):
        yield from iter_symbols(expr.left)
        yield from iter_symbols(expr.right)
