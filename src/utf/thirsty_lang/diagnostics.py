from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .token import Span


# Canonical registry of all THIRSTY-Exxx codes.
# Source of truth for THIRSTY_ERROR_CODES.md.
ERROR_CODES: dict[str, str] = {
    "THIRSTY-E001": "Unexpected token",
    "THIRSTY-E002": "Undefined variable",
    "THIRSTY-E003": "Type mismatch",
    "THIRSTY-E004": "Missing return statement",
    "THIRSTY-E005": "Immutable variable reassignment",
    "THIRSTY-E006": "Invalid operation for type",
    "THIRSTY-E007": "Module not found",
    "THIRSTY-E008": "Unknown module function",
    "THIRSTY-E009": "Argument count mismatch",
    "THIRSTY-E010": "Division by zero",
    "THIRSTY-E011": "Index out of bounds",
    "THIRSTY-E012": "Null dereference (empty access without guard)",
    "THIRSTY-E013": "Unknown attribute on object",
    "THIRSTY-E014": "Duplicate symbol definition",
    "THIRSTY-E015": "Invalid import path",
    "THIRSTY-E016": "Circular import detected",
    "THIRSTY-E017": "Expected expression",
    "THIRSTY-E018": "Unexpected end of input",
    "THIRSTY-E019": "Invalid string escape sequence",
    "THIRSTY-E020": "Class not found",
    "THIRSTY-E021": "Method not found on class",
    "THIRSTY-E022": "Condition must evaluate to Bool",
    "THIRSTY-E023": "Loop count must be a non-negative Int",
    "THIRSTY-E024": "Return type mismatch",
    "THIRSTY-E025": "Unhandled spillage (uncaught throw)",
    "THIRSTY-E026": "Shield violation: sanitize required before use",
    "THIRSTY-E027": "Armor constraint violated",
    "THIRSTY-E028": "Mutation without validated_canonical",
    "THIRSTY-E029": "Shadow Thirst promotion rejected",
    "THIRSTY-E030": "Invalid TARL policy expression",
    "THIRSTY-E031": "TARL policy denied execution",
    "THIRSTY-E032": "TARL policy escalated (requires human review)",
    "THIRSTY-E033": "TSCG expression invalid",
    "THIRSTY-E034": "Pipe target must be a callable",
    "THIRSTY-E035": "Await used outside async glass",
    "THIRSTY-E036": "Invalid generic type argument count",
    "THIRSTY-E037": "Struct field missing in constructor",
    "THIRSTY-E038": "Enum variant not exhaustively matched",
    "THIRSTY-E039": "Interface method not implemented",
    "THIRSTY-E040": "Result[T,E] used outside spillage context",
    "THIRSTY-E050": "Governance annotation violation (requires clause)",
    "THIRSTY-E901": "condense called on empty value",
}


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            ins = cur[j - 1] + 1
            dele = prev[j] + 1
            sub = prev[j - 1] + (ca != cb)
            cur.append(min(ins, dele, sub))
        prev = cur
    return prev[-1]


def nearest_word(
    word: str, candidates: Iterable[str], max_distance: int = 3
) -> str | None:
    scored = []
    for cand in candidates:
        d = levenshtein(word, cand)
        if d <= max_distance:
            scored.append((d, cand))
    if not scored:
        return None
    scored.sort(key=lambda item: (item[0], item[1]))
    return scored[0][1]


@dataclass
class ThirstyError(Exception):
    code: str
    message: str
    span: Span

    def __str__(self) -> str:
        return f"{self.code}: {self.message} at {self.span.file}:{self.span.line}:{self.span.column}"


@dataclass
class DiagnosticBundle(Exception):
    errors: list[ThirstyError]

    def __str__(self) -> str:
        return "\n\n".join(str(e) for e in self.errors)


def format_error(err: ThirstyError, source: str | None = None) -> str:
    line_text = ""
    marker = ""
    if source is not None:
        lines = source.splitlines()
        if 1 <= err.span.line <= len(lines):
            line_text = lines[err.span.line - 1]
            start = max(err.span.column - 1, 0)
            end = max(err.span.end_column - 1, start + 1)
            marker = " " * start + "^" * max(1, end - start)
    out = [
        f"error[{err.code}]: {err.message}",
        f"  --> {err.span.file}:{err.span.line}:{err.span.column}",
    ]
    if line_text:
        out += ["   |", f"{err.span.line:>2} | {line_text}", f"   | {marker}"]
    return "\n".join(out)


def format_bundle(bundle: DiagnosticBundle, source: str | None = None) -> str:
    return "\n\n".join(format_error(err, source) for err in bundle.errors)
