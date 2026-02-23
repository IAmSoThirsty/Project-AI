"""
Comprehensive test suite for PSIA Phase 5: Bootstrap + Lifecycle.

Covers:
    - GenesisCoordinator: key generation, anchor creation, idempotent re-execution
    - ReadinessGate: check registration, evaluation, status transitions
    - SafeHaltController: halt trigger, write blocking, reset, in-flight tracking
"""

from __future__ import annotations

import pytest

from psia.bootstrap.genesis import (
    GenesisCoordinator,
    GenesisStatus,
)
from psia.bootstrap.readiness import (
    ReadinessGate,
    NodeStatus,
)
from psia.bootstrap.safe_halt import (
    SafeHaltController,
    SafeHaltError,
    HaltReason,
)


# ═══════════════════════════════════════════════════════════════════
#  GenesisCoordinator Tests
# ═══════════════════════════════════════════════════════════════════

class TestGenesisCoordinator:

    def test_genesis_executes(self):
        gc = GenesisCoordinator(node_id="test-node")
        result = gc.execute()
        assert result.status == GenesisStatus.COMPLETED
        assert gc.is_completed

    def test_generates_all_keys(self):
        gc = GenesisCoordinator(components=["a", "b", "c"])
        result = gc.execute()
        assert len(result.keys_generated) == 3
        assert "a" in gc.keys
        assert "c" in gc.keys

    def test_default_components(self):
        gc = GenesisCoordinator()
        result = gc.execute()
        assert len(result.keys_generated) == 7  # DEFAULT_COMPONENTS

    def test_anchor_created(self):
        gc = GenesisCoordinator()
        result = gc.execute()
        assert result.anchor is not None
        assert result.anchor.node_id == "psia-node-01"
        assert len(result.anchor.key_ids) == 7

    def test_attestation_created(self):
        gc = GenesisCoordinator()
        result = gc.execute(binary_hash="abc123", config_hash="def456")
        assert result.attestation is not None
        assert result.attestation.binary_hash == "abc123"
        assert result.attestation.config_hash == "def456"

    def test_idempotent_reexecution(self):
        gc = GenesisCoordinator()
        r1 = gc.execute()
        r2 = gc.execute()
        assert r1.status == GenesisStatus.COMPLETED
        assert r2.status == GenesisStatus.COMPLETED
        assert r1.anchor.anchor_id == r2.anchor.anchor_id

    def test_anchor_hash_deterministic(self):
        gc = GenesisCoordinator()
        gc.execute()
        h1 = gc.anchor.compute_hash()
        h2 = gc.anchor.compute_hash()
        assert h1 == h2
        assert len(h1) == 64

    def test_custom_invariants(self):
        gc = GenesisCoordinator()
        r1 = gc.execute(invariant_definitions=["INV-1", "INV-2"])
        assert r1.attestation.invariant_hash != ""

    def test_status_progression(self):
        gc = GenesisCoordinator()
        assert gc.status == GenesisStatus.NOT_STARTED
        gc.execute()
        assert gc.status == GenesisStatus.COMPLETED


# ═══════════════════════════════════════════════════════════════════
#  ReadinessGate Tests
# ═══════════════════════════════════════════════════════════════════

class TestReadinessGate:

    def test_no_checks_operational(self):
        gate = ReadinessGate()
        report = gate.evaluate()
        assert report.status == NodeStatus.OPERATIONAL
        assert report.all_passed is True

    def test_passing_check(self):
        gate = ReadinessGate()
        gate.register_check("pass1", lambda: (True, "OK"))
        report = gate.evaluate()
        assert report.status == NodeStatus.OPERATIONAL
        assert len(report.checks) == 1
        assert report.checks[0].passed is True

    def test_critical_failure_blocks(self):
        gate = ReadinessGate(strict=True)
        gate.register_check("fail1", lambda: (False, "bad"), critical=True)
        report = gate.evaluate()
        assert report.status == NodeStatus.FAILED
        assert report.critical_failures == 1

    def test_non_critical_failure_degrades(self):
        gate = ReadinessGate()
        gate.register_check("warn1", lambda: (False, "meh"), critical=False)
        report = gate.evaluate()
        assert report.status == NodeStatus.DEGRADED
        assert report.warnings == 1

    def test_mixed_checks(self):
        gate = ReadinessGate()
        gate.register_check("ok", lambda: (True, "fine"))
        gate.register_check("warn", lambda: (False, "meh"), critical=False)
        report = gate.evaluate()
        assert report.status == NodeStatus.DEGRADED
        assert report.critical_failures == 0
        assert report.warnings == 1

    def test_exception_in_check_counts_as_failure(self):
        gate = ReadinessGate()
        def bad_check():
            raise RuntimeError("boom")
        gate.register_check("boom", bad_check)
        report = gate.evaluate()
        assert report.status == NodeStatus.FAILED
        assert report.checks[0].passed is False
        assert "boom" in report.checks[0].message

    def test_genesis_check_pass(self):
        class FakeGenesis:
            is_completed = True
        gate = ReadinessGate()
        gate.register_genesis_check(FakeGenesis())
        report = gate.evaluate()
        assert report.status == NodeStatus.OPERATIONAL

    def test_genesis_check_fail(self):
        class FakeGenesis:
            is_completed = False
            status = "not_started"
        gate = ReadinessGate()
        gate.register_genesis_check(FakeGenesis())
        report = gate.evaluate()
        assert report.status == NodeStatus.FAILED

    def test_ledger_check(self):
        class FakeLedger:
            sealed_block_count = 3
            def verify_chain(self):
                return True
        gate = ReadinessGate()
        gate.register_ledger_check(FakeLedger())
        report = gate.evaluate()
        assert report.status == NodeStatus.OPERATIONAL

    def test_is_operational_property(self):
        gate = ReadinessGate()
        gate.register_check("ok", lambda: (True, "fine"))
        gate.evaluate()
        assert gate.is_operational is True

    def test_last_report(self):
        gate = ReadinessGate()
        assert gate.last_report is None
        gate.evaluate()
        assert gate.last_report is not None


# ═══════════════════════════════════════════════════════════════════
#  SafeHaltController Tests
# ═══════════════════════════════════════════════════════════════════

class TestSafeHaltController:

    def test_initial_state(self):
        ctrl = SafeHaltController()
        assert ctrl.is_halted is False
        assert ctrl.halt_count == 0

    def test_trigger_halt(self):
        ctrl = SafeHaltController()
        event = ctrl.trigger_halt(HaltReason.INVARIANT_VIOLATION, details="INV-ROOT-4 broken")
        assert ctrl.is_halted is True
        assert event.reason == HaltReason.INVARIANT_VIOLATION
        assert "INV-ROOT-4" in event.details

    def test_write_blocked_after_halt(self):
        ctrl = SafeHaltController()
        ctrl.trigger_halt(HaltReason.SECURITY_INCIDENT)
        with pytest.raises(SafeHaltError, match="SAFE-HALT"):
            ctrl.check_write_allowed()

    def test_read_allowed_after_halt(self):
        ctrl = SafeHaltController()
        ctrl.trigger_halt(HaltReason.ADMINISTRATIVE)
        ctrl.check_read_allowed()  # should not raise

    def test_write_allowed_before_halt(self):
        ctrl = SafeHaltController()
        ctrl.check_write_allowed()  # should not raise

    def test_halt_idempotent(self):
        ctrl = SafeHaltController()
        ctrl.trigger_halt(HaltReason.ADMINISTRATIVE)
        ctrl.trigger_halt(HaltReason.CHAIN_CORRUPTION)
        assert ctrl.halt_count == 2
        assert ctrl.is_halted is True

    def test_reset(self):
        ctrl = SafeHaltController()
        ctrl.trigger_halt(HaltReason.ADMINISTRATIVE)
        assert ctrl.reset(authorized_by="admin") is True
        assert ctrl.is_halted is False
        ctrl.check_write_allowed()  # should not raise

    def test_reset_without_halt(self):
        ctrl = SafeHaltController()
        assert ctrl.reset() is False

    def test_in_flight_tracking(self):
        ctrl = SafeHaltController()
        ctrl.register_in_flight()
        ctrl.register_in_flight()
        assert ctrl.in_flight_count == 2
        ctrl.complete_in_flight()
        assert ctrl.in_flight_count == 1

    def test_halt_aborts_in_flight(self):
        ctrl = SafeHaltController()
        ctrl.register_in_flight()
        ctrl.register_in_flight()
        event = ctrl.trigger_halt(HaltReason.UNRECOVERABLE_ERROR)
        assert event.in_flight_aborted == 2
        assert ctrl.in_flight_count == 0

    def test_on_halt_callback(self):
        events = []
        ctrl = SafeHaltController(on_halt=lambda e: events.append(e))
        ctrl.trigger_halt(HaltReason.KEY_COMPROMISE)
        assert len(events) == 1
        assert events[0].reason == HaltReason.KEY_COMPROMISE

    def test_on_reset_callback(self):
        resets = []
        ctrl = SafeHaltController(on_reset=lambda: resets.append(True))
        ctrl.trigger_halt(HaltReason.ADMINISTRATIVE)
        ctrl.reset()
        assert len(resets) == 1

    def test_halt_events_list(self):
        ctrl = SafeHaltController()
        ctrl.trigger_halt(HaltReason.ADMINISTRATIVE, triggered_by="admin")
        events = ctrl.halt_events
        assert len(events) == 1
        assert events[0].triggered_by == "admin"
