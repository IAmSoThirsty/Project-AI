
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    EOF = auto()
    IDENT = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    DOT = auto()
    ARROW = auto()
    QUESTION = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    BANG = auto()
    ASSIGN = auto()
    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()
    AND = auto()
    OR = auto()
    PIPE = auto()
    PLUS_EQ = auto()

    # keywords
    DRINK = auto()
    POUR = auto()
    SIP = auto()
    THIRSTY = auto()
    HYDRATED = auto()
    THIRST = auto()
    QUENCH = auto()
    REFILL = auto()
    TIMES = auto()
    GLASS = auto()
    RESERVOIR = auto()
    WELL = auto()
    OF = auto()
    FLOOD = auto()
    DRIP = auto()
    EVAPORATE = auto()
    CONDENSE = auto()
    FOUNTAIN = auto()
    RETURN = auto()
    PARCHED = auto()
    QUENCHED = auto()
    EMPTY = auto()
    MUT = auto()
    IMPORT = auto()
    FROM = auto()
    AS = auto()
    SHIELD = auto()
    SANITIZE = auto()
    ARMOR = auto()
    MORPH = auto()
    DETECT = auto()
    DEFEND = auto()

    CASCADE = auto()
    THIS = auto()
    NEW = auto()
    PUBLIC = auto()
    PRIVATE = auto()
    AWAIT = auto()
    SPILLAGE = auto()
    CLEANUP = auto()
    FINALLY = auto()
    ERROR = auto()
    THROW = auto()

    POLICY = auto()
    WHEN = auto()
    ALLOW = auto()
    DENY = auto()
    ESCALATE = auto()

    MUTATION = auto()
    VALIDATED_CANONICAL = auto()
    INVARIANT = auto()
    SHADOW = auto()
    CANONICAL = auto()
    PROMOTE = auto()
    REJECT = auto()


KEYWORDS = {
    "drink": TokenType.DRINK,
    "pour": TokenType.POUR,
    "sip": TokenType.SIP,
    "thirsty": TokenType.THIRSTY,
    "hydrated": TokenType.HYDRATED,
    "thirst": TokenType.THIRST,
    "quench": TokenType.QUENCH,
    "refill": TokenType.REFILL,
    "times": TokenType.TIMES,
    "glass": TokenType.GLASS,
    "reservoir": TokenType.RESERVOIR,
    "well": TokenType.WELL,
    "of": TokenType.OF,
    "flood": TokenType.FLOOD,
    "drip": TokenType.DRIP,
    "evaporate": TokenType.EVAPORATE,
    "condense": TokenType.CONDENSE,
    "fountain": TokenType.FOUNTAIN,
    "return": TokenType.RETURN,
    "parched": TokenType.PARCHED,
    "quenched": TokenType.QUENCHED,
    "empty": TokenType.EMPTY,
    "mut": TokenType.MUT,
    "import": TokenType.IMPORT,
    "from": TokenType.FROM,
    "as": TokenType.AS,
    "shield": TokenType.SHIELD,
    "sanitize": TokenType.SANITIZE,
    "armor": TokenType.ARMOR,
    "morph": TokenType.MORPH,
    "detect": TokenType.DETECT,
    "defend": TokenType.DEFEND,
    "cascade": TokenType.CASCADE,
    "this": TokenType.THIS,
    "new": TokenType.NEW,
    "public": TokenType.PUBLIC,
    "private": TokenType.PRIVATE,
    "await": TokenType.AWAIT,
    "spillage": TokenType.SPILLAGE,
    "cleanup": TokenType.CLEANUP,
    "finally": TokenType.FINALLY,
    "error": TokenType.ERROR,
    "throw": TokenType.THROW,
    "policy": TokenType.POLICY,
    "when": TokenType.WHEN,
    "ALLOW": TokenType.ALLOW,
    "DENY": TokenType.DENY,
    "ESCALATE": TokenType.ESCALATE,
    "mutation": TokenType.MUTATION,
    "validated_canonical": TokenType.VALIDATED_CANONICAL,
    "invariant": TokenType.INVARIANT,
    "shadow": TokenType.SHADOW,
    "canonical": TokenType.CANONICAL,
    "promote": TokenType.PROMOTE,
    "reject": TokenType.REJECT,
}


@dataclass(slots=True)
class Span:
    file: str
    line: int
    column: int
    end_line: int
    end_column: int

    def merge(self, other: "Span") -> "Span":
        return Span(self.file, self.line, self.column, other.end_line, other.end_column)


@dataclass(slots=True)
class Token:
    kind: TokenType
    lexeme: str
    value: object | None
    span: Span
