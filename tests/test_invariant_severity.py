"""tests/test_invariant_severity.py — Upgrade 7: Invariant Severity Levels."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.core.invariant_severity import (
    InvariantSeverity,
    SeverityAwareInvariantEngine,
    get_severity_engine,
)


class TestInvariantSeverity:
    def test_info_does_not_prevent_execution(self):
        assert not InvariantSeverity.INFO.prevents_execution()

    def test_warn_does_not_prevent_execution(self):
        assert not InvariantSeverity.WARN.prevents_execution()

    def test_block_prevents_execution(self):
        assert InvariantSeverity.BLOCK.prevents_execution()

    def test_halt_prevents_execution(self):
        assert InvariantSeverity.HALT.prevents_execution()

    def test_escalate_prevents_execution(self):
        assert InvariantSeverity.ESCALATE.prevents_execution()

    def test_ordinal_ordering(self):
        assert InvariantSeverity.INFO < InvariantSeverity.WARN
        assert InvariantSeverity.WARN < InvariantSeverity.BLOCK
        assert InvariantSeverity.BLOCK < InvariantSeverity.HALT
        assert InvariantSeverity.HALT < InvariantSeverity.ESCALATE


class TestSeverityAwareInvariantEngine:
    def _engine_with(self, name, fn, sev):
        eng = SeverityAwareInvariantEngine()
        eng.register_fn(name, fn, severity_on_failure=sev, code=name.upper())
        return eng

    def test_passing_invariant_returns_info(self):
        eng = self._engine_with("always_pass", lambda ctx: True, InvariantSeverity.BLOCK)
        results = eng.evaluate_all({})
        assert results[0].passed
        assert results[0].severity == InvariantSeverity.INFO

    def test_warn_failure_does_not_block(self):
        eng = self._engine_with("warn_inv", lambda ctx: False, InvariantSeverity.WARN)
        results = eng.evaluate_all({})
        assert not eng.should_block_execution(results)

    def test_block_failure_blocks(self):
        eng = self._engine_with("block_inv", lambda ctx: False, InvariantSeverity.BLOCK)
        results = eng.evaluate_all({})
        assert eng.should_block_execution(results)

    def test_halt_failure_blocks(self):
        eng = self._engine_with("halt_inv", lambda ctx: False, InvariantSeverity.HALT)
        results = eng.evaluate_all({})
        assert eng.should_block_execution(results)

    def test_escalate_failure_blocks(self):
        eng = self._engine_with("esc_inv", lambda ctx: False, InvariantSeverity.ESCALATE)
        results = eng.evaluate_all({})
        assert eng.should_block_execution(results)

    def test_max_severity_correct(self):
        eng = SeverityAwareInvariantEngine()
        eng.register_fn("warn_one", lambda ctx: False, InvariantSeverity.WARN)
        eng.register_fn("halt_one", lambda ctx: False, InvariantSeverity.HALT)
        results = eng.evaluate_all({})
        assert eng.max_severity(results) == InvariantSeverity.HALT

    def test_default_engine_has_invariants(self):
        eng = get_severity_engine()
        assert len(eng._invariants) > 0

    def test_result_serializable(self):
        import json
        eng = self._engine_with("test_inv", lambda ctx: False, InvariantSeverity.BLOCK)
        results = eng.evaluate_all({})
        json.dumps(results[0].to_dict())  # must not raise

    def test_stale_continuity_blocks_by_default(self):
        """continuity_proof_fresh fails → BLOCK (no continuity_verified in context)."""
        eng = get_severity_engine()
        ctx = {"continuity_verified": False}
        results = eng.evaluate_all(ctx)
        failing = [r for r in results if not r.passed]
        assert any(r.severity.prevents_execution() for r in failing)

    def test_signing_key_mismatch_escalates(self):
        eng = get_severity_engine()
        ctx = {"continuity_verified": True, "signing_key_mismatch": True}
        results = eng.evaluate_all(ctx)
        failing = [r for r in results if not r.passed]
        assert any(r.severity == InvariantSeverity.ESCALATE for r in failing)
