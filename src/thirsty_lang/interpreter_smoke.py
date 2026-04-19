"""Shared smoke test utilities for the Thirsty interpreter."""

from __future__ import annotations

from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from textwrap import dedent
from unittest.mock import patch

from src.thirsty_lang.src.thirsty_interpreter import ThirstyInterpreter

SMOKE_INPUT = "Quencher"
SMOKE_PROGRAM = dedent(
    """
    drink greeting = "Hello"
    drink count = 42
    drink hydrated = true
    drink temperature = 98.6
    sip username
    pour greeting
    pour count
    pour hydrated
    pour temperature
    pour username
    """
).strip()
SMOKE_EXPECTED_OUTPUT = ["Hello", "42", "True", "98.6", SMOKE_INPUT]
SMOKE_EXPECTED_VARIABLES = {
    "greeting": "Hello",
    "count": 42,
    "hydrated": True,
    "temperature": 98.6,
    "username": SMOKE_INPUT,
}


@dataclass(frozen=True)
class ThirstyInterpreterSmokeResult:
    """Result payload for the Thirsty interpreter smoke check."""

    passed: bool
    output: list[str]
    variables: dict[str, object]
    expected_output: list[str]
    expected_variables: dict[str, object]


def run_thirsty_interpreter_smoke() -> ThirstyInterpreterSmokeResult:
    """Run a deterministic smoke test against the current interpreter surface."""

    interpreter = ThirstyInterpreter()
    stdout_capture = StringIO()

    with patch("builtins.input", return_value=SMOKE_INPUT):
        with redirect_stdout(stdout_capture):
            output = interpreter.interpret(SMOKE_PROGRAM)

    variables = interpreter.get_variables()
    passed = output == SMOKE_EXPECTED_OUTPUT and variables == SMOKE_EXPECTED_VARIABLES
    return ThirstyInterpreterSmokeResult(
        passed=passed,
        output=output,
        variables=variables,
        expected_output=SMOKE_EXPECTED_OUTPUT,
        expected_variables=SMOKE_EXPECTED_VARIABLES,
    )


def format_thirsty_interpreter_smoke_result(
    result: ThirstyInterpreterSmokeResult,
) -> str:
    """Render a concise report for CLI usage."""

    status = "PASS" if result.passed else "FAIL"
    lines = [
        f"Status: {status}",
        f"Expected output: {result.expected_output}",
        f"Actual output:   {result.output}",
        f"Expected vars:   {result.expected_variables}",
        f"Actual vars:     {result.variables}",
    ]
    return "\n".join(lines)
