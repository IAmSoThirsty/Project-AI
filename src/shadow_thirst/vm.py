"""Shadow Thirst VM — stack-based interpreter for BytecodeModule."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shadow_thirst.bytecode import BytecodeModule, BytecodeFunction, Op


# ── Execution state ───────────────────────────────────────────────────────────


@dataclass
class PlaneState:
    return_value: Any = None
    variables: dict[str, Any] = field(default_factory=dict)


@dataclass
class DualExecutionFrame:
    name: str
    primary: PlaneState = field(default_factory=PlaneState)
    shadow: PlaneState = field(default_factory=PlaneState)
    _shadow_active: bool = False
    divergence_detected: bool = False
    divergence_magnitude: float = 0.0

    def activate_shadow(self) -> None:
        self._shadow_active = True

    def __post_init__(self) -> None:
        if not isinstance(self.primary, PlaneState):
            self.primary = PlaneState()
        if not isinstance(self.shadow, PlaneState):
            self.shadow = PlaneState()


# ── VM ────────────────────────────────────────────────────────────────────────


class VMError(Exception):
    pass


def _run_instructions(
    instructions: list,
    variables: dict[str, Any],
) -> Any:
    stack: list[Any] = []

    def pop() -> Any:
        if not stack:
            raise VMError("Stack underflow")
        return stack.pop()

    for instr in instructions:
        op = instr.op

        if op == Op.LOAD_CONST:
            stack.append(instr.arg)

        elif op == Op.LOAD_VAR:
            name = instr.arg
            if name not in variables:
                raise VMError(f"Undefined variable: {name!r}")
            stack.append(variables[name])

        elif op == Op.STORE_VAR:
            variables[instr.arg] = pop()

        elif op == Op.ADD:
            b, a = pop(), pop()
            stack.append(a + b)

        elif op == Op.SUB:
            b, a = pop(), pop()
            stack.append(a - b)

        elif op == Op.MUL:
            b, a = pop(), pop()
            stack.append(a * b)

        elif op == Op.DIV:
            b, a = pop(), pop()
            stack.append(a / b)

        elif op == Op.EQ:
            b, a = pop(), pop()
            stack.append(a == b)

        elif op == Op.NE:
            b, a = pop(), pop()
            stack.append(a != b)

        elif op == Op.LT:
            b, a = pop(), pop()
            stack.append(a < b)

        elif op == Op.LE:
            b, a = pop(), pop()
            stack.append(a <= b)

        elif op == Op.GT:
            b, a = pop(), pop()
            stack.append(a > b)

        elif op == Op.GE:
            b, a = pop(), pop()
            stack.append(a >= b)

        elif op == Op.AND:
            b, a = pop(), pop()
            stack.append(bool(a) and bool(b))

        elif op == Op.OR:
            b, a = pop(), pop()
            stack.append(bool(a) or bool(b))

        elif op == Op.NOT:
            stack.append(not pop())

        elif op == Op.POP:
            pop()

        elif op == Op.RETURN:
            return pop()

    return stack[-1] if stack else None


class ShadowAwareVM:
    def __init__(self, enable_shadow: bool = False) -> None:
        self._enable_shadow = enable_shadow
        self._program: BytecodeModule | None = None
        self._stats: dict[str, Any] = {"shadow_activations": 0, "executions": 0}
        self._func_index: dict[str, BytecodeFunction] = {}

    def load_program(self, program: BytecodeModule) -> None:
        self._program = program
        self._func_index = {f.name: f for f in program.functions}

    def execute(self, func_name: str, args: dict[str, Any] | None = None) -> Any:
        if self._program is None:
            raise VMError("No program loaded")
        func = self._func_index.get(func_name)
        if func is None:
            raise VMError(f"Unknown function: {func_name!r}")

        variables: dict[str, Any] = dict(args or {})
        self._stats["executions"] += 1

        # Run primary block
        primary_result = _run_instructions(func.primary_bytecode, dict(variables))

        # Run shadow block if enabled and present
        shadow_result = None
        if self._enable_shadow and func.shadow_bytecode:
            shadow_vars: dict[str, Any] = dict(variables)
            shadow_result = _run_instructions(func.shadow_bytecode, shadow_vars)
            self._stats["shadow_activations"] += 1

        return primary_result

    def get_stats(self) -> dict[str, Any]:
        return dict(self._stats)
