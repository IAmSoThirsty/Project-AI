"""PSIA shadow operational semantics — deterministic execution model (paper §7)."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class DeterminismClass(str, Enum):
    FULLY_DETERMINISTIC = "fully_deterministic"
    NON_DETERMINISTIC = "non_deterministic"
    EPSILON_DETERMINISTIC = "epsilon_deterministic"


@dataclass
class SealedContext:
    seed: int
    logical_clock_start: int
    io_table: dict
    env: dict

    @classmethod
    def from_inputs(cls, inputs_hash: str) -> SealedContext:
        digest = hashlib.sha256(inputs_hash.encode("utf-8")).hexdigest()
        seed = int(digest, 16)  # always > 0 for any non-empty hash
        return cls(
            seed=seed,
            logical_clock_start=0,
            io_table={},
            env={},
        )


@dataclass
class TraceStep:
    step_id: int
    operation: str
    args: tuple
    result: Any


@dataclass
class ExecutionTrace:
    trace_id: str
    context_seed: int
    steps: list[TraceStep] = field(default_factory=list)
    _sealed_hash: str = field(default="", init=False, repr=False)

    def add_step(self, operation: str, args: tuple, result: Any) -> None:
        step_id = len(self.steps)
        self.steps.append(TraceStep(step_id=step_id, operation=operation, args=args, result=result))

    def seal(self) -> str:
        step_hashes = b""
        for s in self.steps:
            raw = json.dumps(
                {"step_id": s.step_id, "op": s.operation, "args": str(s.args), "result": str(s.result)},
                sort_keys=True,
            ).encode("utf-8")
            step_hashes += hashlib.sha256(raw).digest()
        prefix = str(self.context_seed).encode("utf-8")
        self._sealed_hash = hashlib.sha256(prefix + step_hashes).hexdigest()
        return self._sealed_hash


class DeterminismOracle:
    def __init__(self) -> None:
        self.verification_log: list[dict] = []

    def verify_determinism(
        self,
        program: Callable[[SealedContext, dict], ExecutionTrace],
        ctx: SealedContext,
        snapshot: dict,
    ) -> tuple[DeterminismClass, ExecutionTrace]:
        trace1 = program(ctx, snapshot)
        hash1 = trace1.seal()

        trace2 = program(ctx, snapshot)
        hash2 = trace2.seal()

        if hash1 == hash2:
            classification = DeterminismClass.FULLY_DETERMINISTIC
        else:
            classification = DeterminismClass.NON_DETERMINISTIC

        self.verification_log.append({
            "classification": classification,
            "hash1": hash1,
            "hash2": hash2,
        })
        return classification, trace1
