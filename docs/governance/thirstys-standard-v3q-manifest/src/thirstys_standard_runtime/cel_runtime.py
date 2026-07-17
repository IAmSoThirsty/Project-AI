from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from celpy import Environment, celtypes


class CELExecutionError(RuntimeError):
    pass


def _to_cel(value: Any) -> Any:
    if isinstance(value, dict):
        return celtypes.MapType({celtypes.StringType(str(k)): _to_cel(v) for k, v in value.items()})
    if isinstance(value, list):
        return celtypes.ListType([_to_cel(v) for v in value])
    if isinstance(value, tuple):
        return celtypes.ListType([_to_cel(v) for v in value])
    if isinstance(value, bool):
        return celtypes.BoolType(value)
    if isinstance(value, int) and not isinstance(value, bool):
        return celtypes.IntType(value)
    if isinstance(value, float):
        return celtypes.DoubleType(value)
    if isinstance(value, str):
        return celtypes.StringType(value)
    if value is None:
        return None
    return value


@dataclass(frozen=True)
class CELResult:
    expression: str
    value: bool


class CELRuntime:
    def __init__(self) -> None:
        self._environment = Environment()
        self._programs: dict[str, Any] = {}

    def compile(self, expression: str) -> Any:
        try:
            ast = self._environment.compile(expression)
            program = self._environment.program(ast)
        except Exception as exc:
            raise CELExecutionError(f"CEL compilation failed for {expression!r}: {exc}") from exc
        self._programs[expression] = program
        return program

    def evaluate(self, expression: str, activation: dict[str, Any]) -> CELResult:
        program = self._programs.get(expression) or self.compile(expression)
        converted = {name: _to_cel(value) for name, value in activation.items()}
        try:
            result = program.evaluate(converted)
        except Exception as exc:
            raise CELExecutionError(f"CEL evaluation failed for {expression!r}: {exc}") from exc
        if isinstance(result, Exception):
            raise CELExecutionError(f"CEL returned an error for {expression!r}: {result}")
        if not isinstance(result, (bool, celtypes.BoolType)):
            raise CELExecutionError(f"CEL condition did not return bool for {expression!r}: {result!r}")
        return CELResult(expression=expression, value=bool(result))

    def compile_manifest_conditions(self, manifest: dict[str, Any]) -> list[str]:
        expressions = sorted({control["applies_when"] for rule in manifest["rules"] for control in rule["controls"]})
        for expression in expressions:
            self.compile(expression)
        return expressions

    def control_applies(self, control: dict[str, Any], task: dict[str, Any], claims: list[dict[str, Any]] | None = None) -> bool:
        expression = control.get("applies_when", "true")
        claims = claims or []
        if "claim." in expression:
            return any(self.evaluate(expression, {"task": task, "claim": claim}).value for claim in claims)
        return self.evaluate(expression, {"task": task, "claim": {}}).value
