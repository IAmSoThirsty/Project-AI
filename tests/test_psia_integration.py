"""
PSIA End-to-End Integration Tests.

Verifies cross-plane interactions:
    1. Bootstrap → Genesis → ReadinessGate → OPERATIONAL
    2. Full request lifecycle: waterfall → gate → canonical commit → ledger
    3. Failure detection → circuit breaker → SAFE-HALT escalation
    4. Autoimmune dampener integration with gate decisions
    5. SafeHalt → write blocking → read passthrough → reset
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from psia.bootstrap.genesis import GenesisCoordinator, GenesisStatus
from psia.bootstrap.readiness import NodeStatus, ReadinessGate
from psia.bootstrap.safe_halt import HaltReason, SafeHaltController, SafeHaltError
from psia.canonical.capability_authority import CapabilityAuthority
from psia.canonical.commit_coordinator import CanonicalStore, CommitCoordinator
from psia.canonical.ledger import DurableLedger, ExecutionRecord
from psia.invariants import ROOT_INVARIANTS
from psia.observability.autoimmune_dampener import AutoimmuneDampener
from psia.observability.failure_detector import CircuitState, FailureDetector
from psia.schemas.capability import CapabilityScope
from psia.schemas.identity import Signature
from psia.schemas.request import (
    Intent,
    RequestContext,
    RequestEnvelope,
    RequestTimestamps,
)
from psia.waterfall.engine import WaterfallEngine
from psia.waterfall.stage_0_structural import StructuralStage
from psia.waterfall.stage_1_signature import SignatureStage
from psia.waterfall.stage_2_behavioral import BehavioralStage
from psia.waterfall.stage_3_shadow import ShadowStage
from psia.waterfall.stage_4_gate import GateStage
from psia.waterfall.stage_5_commit import CommitStage
from psia.waterfall.stage_6_memory import MemoryStage

# ── Helpers ───────────────────────────────────────────────────────────


def _sig() -> Signature:
    return Signature(alg="ed25519", kid="k1", sig="test_sig")


def _record(request_id: str, idx: int = 0, **kwargs) -> ExecutionRecord:
    return ExecutionRecord(
        record_id=kwargs.get("record_id", f"rec_{request_id}_{idx}"),
        request_id=request_id,
        actor=kwargs.get("actor", "did:project-ai:alice"),
        action=kwargs.get("action", "read"),
        resource=kwargs.get("resource", "data://test"),
        decision=kwargs.get("decision", "allow"),
        commit_id=kwargs.get("commit_id"),
        diff_hash=kwargs.get("diff_hash"),
    )


def _envelope(request_id: str = "req_int_001") -> RequestEnvelope:
    return RequestEnvelope(
        request_id=request_id,
        actor="did:project-ai:alice",
        subject="did:project-ai:alice",
        capability_token_id="cap_001",
        intent=Intent(action="read", resource="data://test", parameters={}),
        context=RequestContext(trace_id="trace_int_001"),
        timestamps=RequestTimestamps(created_at=datetime.now(timezone.utc).isoformat()),
        signature=_sig(),
    )


def _full_engine() -> WaterfallEngine:
    return WaterfallEngine(
        structural_stage=StructuralStage(),
        signature_stage=SignatureStage(),
        behavioral_stage=BehavioralStage(),
        shadow_stage=ShadowStage(),
        gate_stage=GateStage(),
        commit_stage=CommitStage(),
        memory_stage=MemoryStage(),
    )


# ═══════════════════════════════════════════════════════════════════
#  Bootstrap → Operational Flow
# ═══════════════════════════════════════════════════════════════════


class TestBootstrapToOperational:
    """Verify the full boot sequence: Genesis → Readiness → OPERATIONAL."""

    def test_full_boot_sequence(self):
        genesis = GenesisCoordinator(node_id="integration-node")
        result = genesis.execute()
        assert result.status == GenesisStatus.COMPLETED
        assert genesis.is_completed

        gate = ReadinessGate()
        gate.register_genesis_check(genesis)
        gate.register_check(
            "invariants_loaded",
            lambda: (len(ROOT_INVARIANTS) == 9, f"{len(ROOT_INVARIANTS)} invariants"),
        )

        report = gate.evaluate()
        assert report.status == NodeStatus.OPERATIONAL
        assert report.all_passed is True
        assert gate.is_operational

    def test_genesis_not_completed_blocks_boot(self):
        genesis = GenesisCoordinator()
        gate = ReadinessGate()
        gate.register_genesis_check(genesis)
        report = gate.evaluate()
        assert report.status == NodeStatus.FAILED
        assert not gate.is_operational


# ═══════════════════════════════════════════════════════════════════
#  Request Lifecycle: Pipeline → Canonical → Ledger
# ═══════════════════════════════════════════════════════════════════


class TestRequestLifecycle:
    """Tests the full request path through the PSIA stack."""

    def test_waterfall_to_canonical_commit(self):
        engine = _full_engine()
        wf_result = engine.process(_envelope())
        assert wf_result.is_allowed

        store = CanonicalStore()
        coordinator = CommitCoordinator(store=store)
        commit_result = coordinator.commit(
            request_id="req_int_001",
            mutations={
                "requests/req_int_001": {
                    "request_id": "req_int_001",
                    "status": "approved",
                }
            },
        )
        assert commit_result.status.value == "committed"

        val = store.get("requests/req_int_001")
        assert val is not None
        assert val.value["status"] == "approved"

        ledger = DurableLedger()
        ledger.append(_record("req_int_001"))
        assert ledger.total_records >= 1

    def test_commit_then_ledger_audit(self):
        store = CanonicalStore()
        coordinator = CommitCoordinator(store=store)
        ledger = DurableLedger()

        for i in range(3):
            coordinator.commit(
                request_id=f"req_{i}",
                mutations={f"key_{i}": {"value": i}},
            )
            ledger.append(_record(f"req_{i}", idx=i))

        assert store.get("key_0").value["value"] == 0
        assert store.get("key_2").value["value"] == 2
        assert ledger.total_records == 3


# ═══════════════════════════════════════════════════════════════════
#  Failure Detection → SAFE-HALT Escalation
# ═══════════════════════════════════════════════════════════════════


class TestFailureToSafeHalt:
    """Verify that cascading failures trigger SAFE-HALT."""

    def test_cascade_triggers_safe_halt(self):
        halt_ctrl = SafeHaltController()
        cascades = []

        def on_cascade(alert):
            cascades.append(alert)
            halt_ctrl.trigger_halt(
                HaltReason.UNRECOVERABLE_ERROR,
                details=f"Cascade: {alert.affected_components}",
            )

        fd = FailureDetector(
            failure_threshold=0.5,
            cascade_threshold=2,
            on_cascade=on_cascade,
        )

        for _ in range(3):
            fd.record_failure("canonical")
        for _ in range(3):
            fd.record_failure("ledger")

        assert len(cascades) == 1
        assert halt_ctrl.is_halted

        with pytest.raises(SafeHaltError):
            halt_ctrl.check_write_allowed()

        halt_ctrl.check_read_allowed()

    def test_single_component_failure_no_halt(self):
        halt_ctrl = SafeHaltController()
        fd = FailureDetector(
            failure_threshold=0.5,
            cascade_threshold=2,
            on_cascade=lambda a: halt_ctrl.trigger_halt(HaltReason.UNRECOVERABLE_ERROR),
        )

        for _ in range(3):
            fd.record_failure("canonical")

        assert fd.check_circuit("canonical") == CircuitState.OPEN
        assert not halt_ctrl.is_halted

    def test_recovery_after_halt(self):
        halt_ctrl = SafeHaltController()
        halt_ctrl.trigger_halt(HaltReason.INVARIANT_VIOLATION, details="INV-ROOT-9")
        assert halt_ctrl.is_halted

        halt_ctrl.reset(authorized_by="admin@psia.local")
        assert not halt_ctrl.is_halted
        halt_ctrl.check_write_allowed()


# ═══════════════════════════════════════════════════════════════════
#  Autoimmune Dampener Integration
# ═══════════════════════════════════════════════════════════════════


class TestAutoimmuneDampenerIntegration:

    def test_dampener_suppresses_overaggressive_rule(self):
        dampener = AutoimmuneDampener(
            target_fp_rate=0.1,
            cooldown_decisions=3,
            adjustment_step=0.15,
            min_sensitivity=0.2,
        )

        for _ in range(6):
            dampener.record_decision("rule_overzealous", denied=True)
            dampener.record_false_positive("rule_overzealous")

        sensitivity = dampener.get_sensitivity("rule_overzealous")
        assert sensitivity < 1.0

        assert dampener.should_apply_rule("rule_overzealous", 0.4) is False

    def test_dampener_preserves_good_rules(self):
        dampener = AutoimmuneDampener(
            target_fp_rate=0.1,
            cooldown_decisions=5,
        )

        for _ in range(10):
            dampener.record_decision("rule_good", denied=True)
        dampener.record_false_positive("rule_good")

        sensitivity = dampener.get_sensitivity("rule_good")
        assert sensitivity >= 0.9


# ═══════════════════════════════════════════════════════════════════
#  Capability Authority → Canonical Commit Flow
# ═══════════════════════════════════════════════════════════════════


class TestCapabilityAuthorityIntegration:

    def test_issue_then_revoke(self):
        authority = CapabilityAuthority()
        token = authority.issue(
            subject="did:psia:agent:007",
            scopes=[CapabilityScope(resource="data://classified/*", actions=["read"])],
        )
        assert authority.is_valid(token.token_id)

        authority.revoke(token.token_id, reason="mission_complete")
        assert not authority.is_valid(token.token_id)

    def test_token_in_canonical_store(self):
        authority = CapabilityAuthority()
        store = CanonicalStore()

        token = authority.issue(
            subject="did:psia:agent:008",
            scopes=[
                CapabilityScope(
                    resource="policy://registry/*", actions=["read", "write"]
                )
            ],
        )

        coordinator = CommitCoordinator(store=store)
        coordinator.commit(
            request_id="token_issue",
            mutations={
                f"tokens/{token.token_id}": {
                    "token_id": token.token_id,
                    "subject": token.subject,
                    "status": "active",
                }
            },
        )

        stored = store.get(f"tokens/{token.token_id}")
        assert stored.value["subject"] == "did:psia:agent:008"
        assert stored.value["status"] == "active"


# ═══════════════════════════════════════════════════════════════════
#  Full Stack Integration
# ═══════════════════════════════════════════════════════════════════


class TestFullStackIntegration:
    """End-to-end test: boot → process → commit → observe → halt → recover."""

    def test_full_lifecycle(self):
        # ── BOOTSTRAP ──
        genesis = GenesisCoordinator(node_id="fullstack-node")
        genesis.execute()

        gate = ReadinessGate()
        gate.register_genesis_check(genesis)
        report = gate.evaluate()
        assert report.status == NodeStatus.OPERATIONAL

        # ── OBSERVABILITY SETUP ──
        halt_ctrl = SafeHaltController()
        fd = FailureDetector(
            failure_threshold=0.5,
            cascade_threshold=3,
            on_cascade=lambda a: halt_ctrl.trigger_halt(HaltReason.UNRECOVERABLE_ERROR),
        )
        fd.register_component("waterfall")
        fd.register_component("canonical")
        fd.register_component("ledger")

        # ── PROCESS REQUESTS ──
        engine = _full_engine()
        store = CanonicalStore()
        coordinator = CommitCoordinator(store=store)
        ledger = DurableLedger()

        for i in range(5):
            wf_result = engine.process(_envelope(request_id=f"req_{i:04d}"))
            fd.record_success("waterfall")

            coordinator.commit(
                request_id=f"req_{i:04d}",
                mutations={f"req_{i:04d}": {"result": "allowed"}},
            )
            fd.record_success("canonical")

            ledger.append(_record(f"req_{i:04d}", idx=i))
            fd.record_success("ledger")

        # ── VERIFY STATE ──
        assert store.get("req_0000") is not None
        assert store.get("req_0004") is not None
        assert ledger.total_records == 5
        assert fd.open_circuit_count() == 0
        assert not halt_ctrl.is_halted

        # ── SIMULATE FAILURE ──
        halt_ctrl.trigger_halt(
            HaltReason.ADMINISTRATIVE,
            details="Planned maintenance",
            triggered_by="admin",
        )
        assert halt_ctrl.is_halted

        with pytest.raises(SafeHaltError):
            halt_ctrl.check_write_allowed()

        # ── RECOVER ──
        halt_ctrl.reset(authorized_by="admin@psia.local")
        assert not halt_ctrl.is_halted
        halt_ctrl.check_write_allowed()

        # ── FINAL AUDIT ──
        assert halt_ctrl.halt_count == 1
        events = halt_ctrl.halt_events
        assert events[0].reason == HaltReason.ADMINISTRATIVE
        assert events[0].triggered_by == "admin"
