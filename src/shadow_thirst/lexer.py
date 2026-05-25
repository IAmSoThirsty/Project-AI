"""Shadow Thirst lexer — tokenizes source into Tokens."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TokenType(Enum):
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    TRUE = auto()
    FALSE = auto()
    # Identifiers
    IDENTIFIER = auto()
    # Keywords
    FN = auto()
    DRINK = auto()
    RETURN = auto()
    PRIMARY = auto()
    SHADOW = auto()
    ACTIVATE_IF = auto()
    INVARIANT = auto()
    CANONICAL = auto()
    EPHEMERAL = auto()
    DUAL = auto()
    DIVERGENCE = auto()
    MUTATION = auto()
    # Arithmetic
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    # Comparison
    EQ = auto()   # ==
    NE = auto()   # !=
    LT = auto()   # <
    LE = auto()   # <=
    GT = auto()   # >
    GE = auto()   # >=
    # Logical
    AND = auto()  # &&
    OR = auto()   # ||
    NOT = auto()  # !
    # Delimiters
    ASSIGN = auto()    # =
    LBRACE = auto()    # {
    RBRACE = auto()    # }
    LPAREN = auto()    # (
    RPAREN = auto()    # )
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    COLON = auto()     # :
    COMMA = auto()     # ,
    ARROW = auto()     # ->
    DOT = auto()       # .
    SEMICOLON = auto() # ;
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int = 0


_KEYWORDS: dict[str, TokenType] = {
    "fn": TokenType.FN,
    "drink": TokenType.DRINK,
    "return": TokenType.RETURN,
    "primary": TokenType.PRIMARY,
    "shadow": TokenType.SHADOW,
    "Shadow": TokenType.SHADOW,
    "activate_if": TokenType.ACTIVATE_IF,
    "invariant": TokenType.INVARIANT,
    "Canonical": TokenType.CANONICAL,
    "canonical": TokenType.CANONICAL,
    "Ephemeral": TokenType.EPHEMERAL,
    "ephemeral": TokenType.EPHEMERAL,
    "Dual": TokenType.DUAL,
    "dual": TokenType.DUAL,
    "divergence": TokenType.DIVERGENCE,
    "mutation": TokenType.MUTATION,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}

_SINGLES: dict[str, TokenType] = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "<": TokenType.LT,
    ">": TokenType.GT,
    "!": TokenType.NOT,
    "=": TokenType.ASSIGN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    ":": TokenType.COLON,
    ",": TokenType.COMMA,
    ".": TokenType.DOT,
    ";": TokenType.SEMICOLON,
}

_TWO_CHAR: list[tuple[str, TokenType]] = [
    ("==", TokenType.EQ),
    ("!=", TokenType.NE),
    ("<=", TokenType.LE),
    (">=", TokenType.GE),
    ("&&", TokenType.AND),
    ("||", TokenType.OR),
    ("->", TokenType.ARROW),
]


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    line = 1

    while i < len(source):
        c = source[i]

        if c in (" ", "\t", "\r"):
            i += 1
            continue
        if c == "\n":
            line += 1
            i += 1
            continue

        # Line comments
        if c == "/" and i + 1 < len(source) and source[i + 1] == "/":
            while i < len(source) and source[i] != "\n":
                i += 1
            continue

        # Numbers
        if c.isdigit():
            start = i
            while i < len(source) and source[i].isdigit():
                i += 1
            if (
                i < len(source)
                and source[i] == "."
                and i + 1 < len(source)
                and source[i + 1].isdigit()
            ):
                i += 1
                while i < len(source) and source[i].isdigit():
                    i += 1
                tokens.append(Token(TokenType.FLOAT, float(source[start:i]), line))
            else:
                tokens.append(Token(TokenType.INTEGER, int(source[start:i]), line))
            continue

        # Identifiers and keywords
        if c.isalpha() or c == "_":
            start = i
            while i < len(source) and (source[i].isalnum() or source[i] == "_"):
                i += 1
            word = source[start:i]
            tt = _KEYWORDS.get(word, TokenType.IDENTIFIER)
            tokens.append(Token(tt, word, line))
            continue

        # Strings
        if c == '"':
            i += 1
            start = i
            while i < len(source) and source[i] != '"':
                i += 1
            tokens.append(Token(TokenType.STRING, source[start:i], line))
            i += 1
            continue

        # Two-character tokens
        matched = False
        if i + 1 < len(source):
            two = source[i : i + 2]
            for pattern, tt in _TWO_CHAR:
                if two == pattern:
                    tokens.append(Token(tt, two, line))
                    i += 2
                    matched = True
                    break
        if matched:
            continue

        # Single-character tokens
        if c in _SINGLES:
            tokens.append(Token(_SINGLES[c], c, line))
            i += 1
            continue

        i += 1  # skip unknown character

    tokens.append(Token(TokenType.EOF, None, line))
    return tokens
