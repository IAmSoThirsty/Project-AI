#!/usr/bin/env python3
"""Run the canonical Thirsty interpreter smoke test."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for candidate in (ROOT, ROOT / "src"):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

from thirsty_lang.interpreter_smoke import (  # noqa: E402
    format_thirsty_interpreter_smoke_result,
    run_thirsty_interpreter_smoke,
)


def main() -> int:
    """Execute the smoke test and print a short report."""

    result = run_thirsty_interpreter_smoke()
    print("=" * 80)
    print("THIRSTY INTERPRETER SMOKE TEST")
    print("=" * 80)
    print(format_thirsty_interpreter_smoke_result(result))
    print("=" * 80)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
