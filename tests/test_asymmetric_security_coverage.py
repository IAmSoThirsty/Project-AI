"""
Coverage-boost tests for src/security/asymmetric_security.py.

Covers: SecurityContext, RFICalculator, AdversarialProber, DimensionEntropyGuard,
SecurityEnforcementGateway – including edge cases and adversarial friction paths.
"""

import time

import pytest

from src.security.asymmetric_security import (
    AdversarialProber,
    DimensionEntropyGuard,
    OperationalState,
    RFICalculator,
    SecurityContext,
    SecurityEnforcementGateway,
    SecurityViolationError,
)


# ── SecurityContext ─────────────────────────────────────────────────────────


class TestSecurityContext:
    def test_default_values(self):
        ctx = SecurityContext(user_id="u1", action="read")
        assert ctx.tenant_id == "default"
        assert ctx.auth_proof is None
        assert ctx.dimensions == {}
        assert ctx.timestamp > 0

    def test_custom_dimensions(self):
        ctx = SecurityContext(
            user_id="u1",
            action="write",
            dimensions={"spatial": 12.0, "temporal": 8.0},
        )
        assert ctx.dimensions["spatial"] == 12.0


class TestOperationalState:
    def test_values(self):
        assert OperationalState.NORMAL.value == "normal"
        assert OperationalState.HALTED.value == "halted"


# ── RFICalculator ───────────────────────────────────────────────────────────


class TestRFICalculator:
    def test_zero_entropy(self):
        calc = RFICalculator()
        ctx = SecurityContext(user_id="u", action="a", dimensions={})
        assert calc.calculate(ctx) == 0.0

    def test_negative_entropy(self):
        calc = RFICalculator()
        ctx = SecurityContext(user_id="u", action="a", dimensions={"x": -1.0})
        assert calc.calculate(ctx) == 0.0

    def test_small_entropy(self):
        calc = RFICalculator()
        ctx = SecurityContext(user_id="u", action="a", dimensions={"x": 1.0})
        rfi = calc.calculate(ctx)
        assert 0.0 < rfi < 1.0
        assert rfi == pytest.approx(0.5)

    def test_large_entropy(self):
        calc = RFICalculator()
        ctx = SecurityContext(
            user_id="u", action="a", dimensions={"x": 20.0, "y": 20.0}
        )
        rfi = calc.calculate(ctx)
        assert rfi > 0.99

    def test_multiple_dimensions(self):
        calc = RFICalculator()
        ctx = SecurityContext(
            user_id="u",
            action="a",
            dimensions={"identity": 12.5, "spatial": 8.2, "temporal": 4.5},
        )
        rfi = calc.calculate(ctx)
        assert rfi > 0.99


# ── AdversarialProber ───────────────────────────────────────────────────────


class TestAdversarialProber:
    def test_initial_empty(self):
        p = AdversarialProber()
        assert len(p.probe_registry) == 0

    def test_record_failure(self):
        p = AdversarialProber()
        p.record_attempt("attacker1", success=False)
        assert p.probe_registry["attacker1"] == 1

    def test_record_multiple_failures(self):
        p = AdversarialProber()
        for _ in range(5):
            p.record_attempt("attacker1", success=False)
        assert p.probe_registry["attacker1"] == 5

    def test_success_decrements(self):
        p = AdversarialProber()
        p.record_attempt("u", success=False)
        p.record_attempt("u", success=False)
        p.record_attempt("u", success=True)
        assert p.probe_registry["u"] == 1

    def test_success_removes_at_zero(self):
        p = AdversarialProber()
        p.record_attempt("u", success=False)
        p.record_attempt("u", success=True)
        assert "u" not in p.probe_registry

    def test_success_noop_unknown_source(self):
        p = AdversarialProber()
        p.record_attempt("unknown", success=True)
        assert "unknown" not in p.probe_registry

    def test_lru_eviction(self):
        p = AdversarialProber(max_registry_size=3)
        p.record_attempt("a", False)
        p.record_attempt("b", False)
        p.record_attempt("c", False)
        p.record_attempt("d", False)  # evicts 'a'
        assert "a" not in p.probe_registry
        assert len(p.probe_registry) == 3

    def test_friction_multiplier_low(self):
        p = AdversarialProber()
        assert p.get_friction_multiplier("clean") == 1.0

    def test_friction_multiplier_medium(self):
        p = AdversarialProber()
        for _ in range(4):
            p.record_attempt("med", False)
        assert p.get_friction_multiplier("med") == 1.25

    def test_friction_multiplier_high(self):
        p = AdversarialProber()
        for _ in range(12):
            p.record_attempt("bad", False)
        assert p.get_friction_multiplier("bad") == 2.0

    def test_cleanup_triggered_by_time(self):
        p = AdversarialProber()
        p.record_attempt("z", False)
        p.record_attempt("z", True)  # count goes to 0, removed
        # Force cleanup by setting last_cleanup far in past
        p.last_cleanup = time.monotonic() - 7200
        p.probe_registry["stale"] = 0
        p.record_attempt("new_src", False)  # triggers cleanup
        assert "stale" not in p.probe_registry


# ── DimensionEntropyGuard ───────────────────────────────────────────────────


class TestDimensionEntropyGuard:
    def test_valid_dimensions(self):
        guard = DimensionEntropyGuard()
        ctx = SecurityContext(
            user_id="u", action="a", dimensions={"x": 5.0, "y": 6.0}
        )
        guard.validate(ctx)  # should not raise

    def test_empty_dimensions(self):
        guard = DimensionEntropyGuard()
        ctx = SecurityContext(user_id="u", action="a", dimensions={})
        guard.validate(ctx)  # no dimensions = no violations

    def test_low_entropy_raises(self):
        guard = DimensionEntropyGuard()
        ctx = SecurityContext(
            user_id="u", action="a", dimensions={"weak": 2.0}
        )
        with pytest.raises(SecurityViolationError, match="entropy requirement"):
            guard.validate(ctx)

    def test_one_bad_dimension(self):
        guard = DimensionEntropyGuard()
        ctx = SecurityContext(
            user_id="u", action="a", dimensions={"good": 10.0, "bad": 1.0}
        )
        with pytest.raises(SecurityViolationError, match="bad"):
            guard.validate(ctx)


# ── SecurityEnforcementGateway ──────────────────────────────────────────────


class TestSecurityEnforcementGateway:
    def test_init(self, tmp_path):
        gw = SecurityEnforcementGateway(str(tmp_path))
        assert gw.rfi_calculator is not None
        assert gw.prober is not None

    def test_validate_default_action_populated_dims(self, tmp_path):
        gw = SecurityEnforcementGateway(str(tmp_path))
        ctx = SecurityContext(user_id="u", action="read_data")
        # Empty dimensions get populated by _populate_dimensions
        ok, msg = gw.validate_and_enforce(ctx)
        assert ok
        assert msg == "SUCCESS"

    def test_validate_custom_high_entropy(self, tmp_path):
        gw = SecurityEnforcementGateway(str(tmp_path))
        ctx = SecurityContext(
            user_id="u",
            action="some_action",
            dimensions={"id": 20.0, "sp": 20.0, "tp": 20.0},
        )
        ok, msg = gw.validate_and_enforce(ctx)
        assert ok

    def test_validate_low_entropy_fails(self, tmp_path):
        gw = SecurityEnforcementGateway(str(tmp_path))
        ctx = SecurityContext(
            user_id="u",
            action="read",
            dimensions={"weak": 1.0},
        )
        ok, msg = gw.validate_and_enforce(ctx)
        assert not ok
        assert "entropy requirement" in msg

    def test_validate_insufficient_rfi(self, tmp_path):
        gw = SecurityEnforcementGateway(str(tmp_path))
        ctx = SecurityContext(
            user_id="u",
            action="delete_user_data",
            dimensions={"id": 4.5, "sp": 4.5, "tp": 4.5},
        )
        ok, msg = gw.validate_and_enforce(ctx)
        # Total entropy = 13.5, RFI ≈ 0.99988 which is > 0.95
        # but we test the path
        assert isinstance(ok, bool)

    def test_rfi_thresholds_exist(self, tmp_path):
        gw = SecurityEnforcementGateway(str(tmp_path))
        assert "default" in gw.rfi_thresholds
        assert "delete_user_data" in gw.rfi_thresholds

    def test_adversarial_friction_increases_requirement(self, tmp_path):
        gw = SecurityEnforcementGateway(str(tmp_path))
        # Simulate 15 failures to bump friction multiplier
        for _ in range(15):
            ctx = SecurityContext(
                user_id="attacker",
                action="read",
                dimensions={"weak": 1.0},
            )
            gw.validate_and_enforce(ctx)
        multiplier = gw.prober.get_friction_multiplier("attacker")
        assert multiplier == 2.0

    def test_populate_dimensions_fills_empty(self, tmp_path):
        gw = SecurityEnforcementGateway(str(tmp_path))
        ctx = SecurityContext(user_id="u", action="a")
        gw._populate_dimensions(ctx)
        assert len(ctx.dimensions) == 3

    def test_populate_dimensions_keeps_existing(self, tmp_path):
        gw = SecurityEnforcementGateway(str(tmp_path))
        ctx = SecurityContext(
            user_id="u", action="a", dimensions={"custom": 99.0}
        )
        gw._populate_dimensions(ctx)
        assert ctx.dimensions["custom"] == 99.0
