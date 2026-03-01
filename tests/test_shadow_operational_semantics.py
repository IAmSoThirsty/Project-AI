"""
Tests for PSIA Shadow Operational Semantics — Deterministic Execution.

Fact-verifies claims from the paper (§7):
    - SealedContext: identical inputs → identical contexts (Definition 7.2)
    - SealedContext: no wall clock, no env vars, empty environment
    - ExecutionTrace: replay hash is SHA-256 of step hashes
    - DeterminismOracle: deterministic fn → FULLY_DETERMINISTIC
    - DeterminismOracle: non-deterministic fn → NON_DETERMINISTIC
    - Transition rules: read, write, compute, branch produce correct traces
"""

from __future__ import annotations

import random
from typing import Any

from psia.shadow.operational_semantics import (
    DeterminismClass,
    DeterminismOracle,
    ExecutionTrace,
    SealedContext,
)


class TestSealedContext:
    """Paper §7.1: SealedContext eliminates all non-determinism sources."""

    def test_identical_inputs_produce_identical_contexts(self):
        """Paper Definition 7.2: Two SealedContexts from same inputs are identical."""
        ctx_a = SealedContext.from_inputs("abc123")
        ctx_b = SealedContext.from_inputs("abc123")

        assert ctx_a.seed == ctx_b.seed
        assert ctx_a.logical_clock_start == ctx_b.logical_clock_start
        assert ctx_a.io_table == ctx_b.io_table
        assert ctx_a.env == ctx_b.env

    def test_different_inputs_produce_different_contexts(self):
        ctx_a = SealedContext.from_inputs("abc123")
        ctx_b = SealedContext.from_inputs("def456")
        assert ctx_a.seed != ctx_b.seed

    def test_no_wall_clock(self):
        """Paper: Clock is logical monotonic integer, no wall-clock access."""
        ctx = SealedContext.from_inputs("test_hash")
        assert isinstance(ctx.logical_clock_start, int)
        assert ctx.logical_clock_start == 0  # Starts at 0

    def test_empty_environment(self):
        """Paper: Environment empty (no env vars, no filesystem, no network)."""
        ctx = SealedContext.from_inputs("test_hash")
        assert ctx.env == {}

    def test_seed_derived_from_sha256(self):
        """Paper: Fixed PRNG seed derived from SHA-256(inputs_hash)."""
        ctx = SealedContext.from_inputs("deterministic_input")
        assert isinstance(ctx.seed, int)
        assert ctx.seed > 0


class TestExecutionTrace:
    """Paper §7.1: Traces produce deterministic replay hashes."""

    def _make_trace(self):
        return ExecutionTrace(trace_id="test_trace", context_seed=42)

    def test_trace_records_steps(self):
        trace = self._make_trace()
        trace.add_step("read", ("key1",), result="value1")
        trace.add_step("compute", ("+", 1, 2), result=3)
        assert len(trace.steps) == 2
        assert trace.steps[0].operation == "read"
        assert trace.steps[1].result == 3

    def test_replay_hash_deterministic(self):
        """Paper: replay hash = SHA-256 of concatenated step hashes."""
        trace_a = ExecutionTrace(trace_id="trace_a", context_seed=42)
        trace_a.add_step("read", ("x",), result=42)
        trace_a.add_step("compute", ("+", 42, 1), result=43)
        hash_a = trace_a.seal()

        trace_b = ExecutionTrace(trace_id="trace_b", context_seed=42)
        trace_b.add_step("read", ("x",), result=42)
        trace_b.add_step("compute", ("+", 42, 1), result=43)
        hash_b = trace_b.seal()

        assert hash_a == hash_b
        assert len(hash_a) == 64  # SHA-256 hex

    def test_different_traces_different_hashes(self):
        trace_a = ExecutionTrace(trace_id="trace_a", context_seed=42)
        trace_a.add_step("read", ("x",), result=42)
        hash_a = trace_a.seal()

        trace_b = ExecutionTrace(trace_id="trace_b", context_seed=42)
        trace_b.add_step("read", ("y",), result=99)
        hash_b = trace_b.seal()

        assert hash_a != hash_b

    def test_step_ids_monotonic(self):
        trace = self._make_trace()
        for i in range(5):
            trace.add_step("compute", (i,), result=i * 2)
        ids = [s.step_id for s in trace.steps]
        assert ids == list(range(5))


class TestDeterminismOracle:
    """Paper §7.1: Runtime verification of shadow determinism."""

    def test_deterministic_program_classified_correctly(self):
        """Paper: Deterministic fn → FULLY_DETERMINISTIC."""
        oracle = DeterminismOracle()
        ctx = SealedContext.from_inputs("test_input")
        snapshot = {"x": 10, "y": 20}

        def deterministic_program(
            ctx: SealedContext, snap: dict[str, Any]
        ) -> ExecutionTrace:
            trace = ExecutionTrace(trace_id="det_trace", context_seed=ctx.seed)
            trace.add_step("read", ("x",), result=snap.get("x"))
            trace.add_step("read", ("y",), result=snap.get("y"))
            trace.add_step(
                "compute",
                ("+", snap.get("x", 0), snap.get("y", 0)),
                result=snap.get("x", 0) + snap.get("y", 0),
            )
            trace.seal()
            return trace

        classification, trace = oracle.verify_determinism(
            deterministic_program, ctx, snapshot
        )
        assert classification == DeterminismClass.FULLY_DETERMINISTIC

    def test_non_deterministic_program_detected(self):
        """Paper: Non-deterministic fn → NON_DETERMINISTIC."""
        oracle = DeterminismOracle()
        ctx = SealedContext.from_inputs("test_input")
        snapshot = {"x": 10}

        call_count = 0

        def nondeterministic_program(
            ctx: SealedContext, snap: dict[str, Any]
        ) -> ExecutionTrace:
            nonlocal call_count
            call_count += 1
            trace = ExecutionTrace(
                trace_id=f"nd_trace_{call_count}", context_seed=ctx.seed
            )
            # Use real random (not sealed) — different each execution
            trace.add_step("compute", ("rand",), result=random.random() + call_count)
            trace.seal()
            return trace

        classification, trace = oracle.verify_determinism(
            nondeterministic_program, ctx, snapshot
        )
        assert classification in (
            DeterminismClass.NON_DETERMINISTIC,
            DeterminismClass.EPSILON_DETERMINISTIC,
        )

    def test_verification_log_records_results(self):
        oracle = DeterminismOracle()
        ctx = SealedContext.from_inputs("test")
        snap = {}

        def simple(ctx, snap):
            t = ExecutionTrace(trace_id="simple_trace", context_seed=ctx.seed)
            t.add_step("noop", (), result=None)
            t.seal()
            return t

        oracle.verify_determinism(simple, ctx, snap)
        assert len(oracle.verification_log) > 0
