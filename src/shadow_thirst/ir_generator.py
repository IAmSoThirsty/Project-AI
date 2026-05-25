"""Shadow Thirst IR generator — converts AST Program to IR."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shadow_thirst.parser import FunctionDef, Program, Block


@dataclass
class IRBasicBlock:
    statements: list[Any] = field(default_factory=list)


@dataclass
class IRFunction:
    name: str
    parameters: list[Any]
    return_type: str
    primary_blocks: list[IRBasicBlock]
    shadow_blocks: list[IRBasicBlock]
    invariant_blocks: list[IRBasicBlock]
    activation_predicate: Any
    divergence_policy: str | None
    mutation_boundary: str | None

    @property
    def has_shadow(self) -> bool:
        return len(self.shadow_blocks) > 0

    @property
    def has_invariants(self) -> bool:
        return len(self.invariant_blocks) > 0


@dataclass
class IR:
    functions: list[IRFunction] = field(default_factory=list)


def _block_to_ir(block: Block | None) -> list[IRBasicBlock]:
    if block is None:
        return []
    return [IRBasicBlock(statements=list(block.statements))]


def generate_ir(program: Program) -> IR:
    functions: list[IRFunction] = []
    for func in program.functions:
        ir_func = IRFunction(
            name=func.name,
            parameters=list(func.parameters),
            return_type=func.return_type,
            primary_blocks=_block_to_ir(func.primary_block),
            shadow_blocks=_block_to_ir(func.shadow_block),
            invariant_blocks=_block_to_ir(func.invariants),
            activation_predicate=func.activation_predicate,
            divergence_policy=func.divergence_policy,
            mutation_boundary=func.mutation_boundary,
        )
        functions.append(ir_func)
    return IR(functions=functions)
