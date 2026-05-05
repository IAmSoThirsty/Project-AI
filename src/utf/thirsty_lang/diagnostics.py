
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .token import Span


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


def nearest_word(word: str, candidates: Iterable[str], max_distance: int = 3) -> str | None:
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
