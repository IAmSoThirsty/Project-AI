#!/usr/bin/env python3
"""Smoke verifier for the Thirsty-lang Python interpreter."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

for path in (ROOT, SRC):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from thirsty_lang.src.thirsty_interpreter import ThirstyInterpreter


def main() -> int:
    """Run a small interpreter smoke check and report the result."""
    interpreter = ThirstyInterpreter()
    output = interpreter.interpret("\n".join(['drink water = "thirsty"', "pour water"]))

    if output != ["thirsty"]:
        print(
            f"THIRSTY_INTERPRETER_SMOKE_FAIL: expected ['thirsty'], got {output!r}",
            file=sys.stderr,
        )
        return 1

    if interpreter.get_variables().get("water") != "thirsty":
        print(
            "THIRSTY_INTERPRETER_SMOKE_FAIL: variable state did not persist",
            file=sys.stderr,
        )
        return 1

    print("THIRSTY_INTERPRETER_SMOKE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
