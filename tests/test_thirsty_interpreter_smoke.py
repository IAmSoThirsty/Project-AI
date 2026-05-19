#                                           [2026-04-02 00:00]
#                                          Productivity: Active
"""Smoke test for the Thirsty-lang Python interpreter."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

for path in (ROOT, SRC):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from thirsty_lang.src.thirsty_interpreter import ThirstyInterpreter


def test_thirsty_interpreter_smoke():
    """Basic parse/execute round-trip should work for declarations and output."""
    interpreter = ThirstyInterpreter()

    output = interpreter.interpret(
        '\n'.join(
            [
                'drink water = "thirsty"',
                "pour water",
                "pour 7",
            ]
        )
    )

    assert output == ["thirsty", "7"]
    assert interpreter.get_variables()["water"] == "thirsty"
