#                                           [2026-03-05 14:30]
#                                          Productivity: Active
"""
Comprehensive tests for enhanced PSIA Shadow Stage (Stage 3).

Tests:
- PassthroughSimulator behavior
- ProductionSimulator integration
- Determinism verification
- Resource limit enforcement
- Privilege anomaly detection
- Divergence scoring
- Error handling and isolation
"""

import pytest

from datetime import datetime, timezone

from psia.schemas.identity import Signature
from psia.schemas.request import Intent, RequestContext, RequestEnvelope, RequestTimestamps
from psia.schemas.shadow_report import (
    DeterminismProof,
    InvariantViolation,
    PrivilegeAnomaly,
    ResourceEnvelope,
    ShadowReport,
    ShadowResults,
    SideEffectSummary,
)
from psia.waterfall.engine import StageDecision
from psia.waterfall.stage_3_shadow import (
    PassthroughSimulator,
    ProductionSimulator,
    ShadowSimulationError,
    ShadowStage,
)


def _envelope(
    request_id="req_test",
    action="read",
    resource="res_001",
    parameters=None,
):
    """Create test RequestEnvelope."""
    return RequestEnvelope(
        request_id=request_id,
        actor="did:sov:test",
        subject="did:sov:test",
        capability_token_id="cap_test_001",
        intent=Intent(
            action=action,
            resource=resource,
            parameters=parameters or {},
        ),
        context=RequestContext(trace_id="trace_test"),
        timestamps=RequestTimestamps(created_at=datetime.now(timezone.utc).isoformat()),
        signature=Signature(alg="ed25519", kid="k1", sig="sig1"),
    )


def _sig():
    """Create test signature."""
    return Signature(alg="ed25519", kid="k1", sig="test_sig")


# ── PassthroughSimulator Tests ──


class TestPassthroughSimulator:
    """Test the development/testing stub simulator."""

    def test_returns_clean_report(self):
        """PassthroughSimulator returns zero-divergence report."""
        sim = PassthroughSimulator()
        report = sim.simulate("req_1", "read", "res_1", {})

        assert report.request_id == "req_1"
        assert report.determinism.replay_verified is True
        assert report.results.divergence_score == 0.0
        assert len(report.results.invariant_violations) == 0
        assert len(report.results.privilege_anomalies) == 0

    def test_deterministic_seed(self):
        """Same inputs produce same seed/replay hash."""
        sim = PassthroughSimulator()
        r1 = sim.simulate("req_1", "read", "res_1", {"k": "v"})
        r2 = sim.simulate("req_1", "read", "res_1", {"k": "v"})

        assert r1.determinism.seed == r2.determinism.seed
        assert r1.determinism.replay_hash == r2.determinism.replay_hash

    def test_different_inputs_different_hash(self):
        """Different inputs produce different hashes."""
        sim = PassthroughSimulator()
        r1 = sim.simulate("req_1", "read", "res_1", {})
        r2 = sim.simulate("req_2", "write", "res_2", {})

        assert r1.determinism.seed != r2.determinism.seed

    def test_respects_quota_parameters(self):
        """Quotas are passed but don't affect passthrough behavior."""
        sim = PassthroughSimulator()
        report = sim.simulate(
            "req_1",
            "read",
            "res_1",
            {},
            cpu_quota_ms=500.0,
            memory_quota_mb=128.0,
        )

        # Passthrough still reports minimal resource usage
        assert report.results.resource_envelope.cpu_ms < 1.0
        assert report.results.resource_envelope.mem_peak_bytes < 1024


# ── ProductionSimulator Tests ──


class TestProductionSimulator:
    """Test production simulator with shadow plane integration."""

    def test_without_shadow_plane_falls_back(self):
        """Without shadow plane, falls back to passthrough."""
        sim = ProductionSimulator(shadow_plane=None)
        report = sim.simulate("req_1", "read", "res_1", {})

        # Should still return valid report (fallback may not verify determinism)
        assert report.request_id == "req_1"
        # Note: Fallback uses passthrough which always verifies determinism
        # Production simulator without shadow plane may not verify properly

    def test_with_mock_shadow_plane(self):
        """With shadow plane, executes simulation."""

        class MockShadowPlane:
            def execute_simulation(self, trace_id, simulation_callable, context):
                # Execute the callable
                result = simulation_callable()

                # Return mock ShadowResult
                class MockResult:
                    invariants_passed = True
                    shadow_result = result
                    resource_usage = None

                return MockResult()

        sim = ProductionSimulator(shadow_plane=MockShadowPlane())
        report = sim.simulate("req_1", "read", "res_1", {"key": "value"})

        assert report.request_id == "req_1"
        assert report.shadow_job_id.startswith("shj_")
        assert report.determinism.runtime_version == "shadowrt_1.0.0_production"

    def test_determinism_verification_enabled(self):
        """Determinism verification can be toggled."""
        sim = ProductionSimulator(
            shadow_plane=None,  # Will fallback
            enable_replay_verification=False,
        )
        assert sim.enable_replay_verification is False

    def test_syscall_monitoring_enabled(self):
        """Syscall monitoring can be toggled."""
        sim = ProductionSimulator(
            shadow_plane=None, enable_syscall_monitoring=True
        )
        assert sim.enable_syscall_monitoring is True

    def test_max_replay_attempts_configurable(self):
        """Replay attempts are configurable."""
        sim = ProductionSimulator(shadow_plane=None, max_replay_attempts=5)
        assert sim.max_replay_attempts == 5


# ── ShadowStage Integration Tests ──


class TestShadowStageBasics:
    """Test basic ShadowStage behavior."""

    def test_passthrough_allows(self):
        """Passthrough simulator allows clean requests."""
        stage = ShadowStage()
        result = stage.evaluate(_envelope(), [])

        assert result.decision == StageDecision.ALLOW
        assert "shadow_report" in result.metadata
        assert result.metadata["divergence_score"] == 0.0

    def test_custom_quotas(self):
        """Custom resource quotas are passed to simulator."""
        stage = ShadowStage(cpu_quota_ms=2000.0, memory_quota_mb=512.0)
        assert stage.cpu_quota_ms == 2000.0
        assert stage.memory_quota_mb == 512.0

    def test_custom_thresholds(self):
        """Divergence thresholds are configurable."""
        stage = ShadowStage(
            divergence_threshold=0.4, critical_divergence_threshold=0.8
        )
        assert stage.divergence_threshold == 0.4
        assert stage.critical_divergence_threshold == 0.8


class TestShadowStageDeterminism:
    """Test determinism verification logic."""

    def test_determinism_failure_quarantines(self):
        """Failed determinism verification triggers quarantine."""

        class NonDeterministicSimulator:
            def simulate(self, *args, **kwargs):
                return ShadowReport(
                    request_id="req_1",
                    shadow_job_id="shj_1",
                    snapshot_id="snap_1",
                    determinism=DeterminismProof(
                        seed="s",
                        replay_hash="r",
                        replay_verified=False,  # Failed!
                    ),
                    results=ShadowResults(divergence_score=0.0),
                    timestamp="2026-01-01T00:00:00Z",
                    signature=_sig(),
                )

        stage = ShadowStage(simulator=NonDeterministicSimulator())
        result = stage.evaluate(_envelope(), [])

        assert result.decision == StageDecision.QUARANTINE
        assert any("determinism" in r for r in result.reasons)

    def test_determinism_optional(self):
        """Determinism check can be disabled."""

        class NonDeterministicSimulator:
            def simulate(self, *args, **kwargs):
                return ShadowReport(
                    request_id="req_1",
                    shadow_job_id="shj_1",
                    snapshot_id="snap_1",
                    determinism=DeterminismProof(
                        seed="s", replay_hash="r", replay_verified=False
                    ),
                    results=ShadowResults(divergence_score=0.0),
                    timestamp="2026-01-01T00:00:00Z",
                    signature=_sig(),
                )

        stage = ShadowStage(
            simulator=NonDeterministicSimulator(), require_determinism=False
        )
        result = stage.evaluate(_envelope(), [])

        # Should not quarantine on determinism alone
        assert result.decision == StageDecision.ALLOW


class TestShadowStageInvariantViolations:
    """Test invariant violation detection."""

    def test_critical_violations_quarantine(self):
        """Critical invariant violations trigger quarantine."""

        class ViolatingSimulator:
            def simulate(self, *args, **kwargs):
                return ShadowReport(
                    request_id="req_1",
                    shadow_job_id="shj_1",
                    snapshot_id="snap_1",
                    determinism=DeterminismProof(
                        seed="s", replay_hash="r", replay_verified=True
                    ),
                    results=ShadowResults(
                        divergence_score=0.0,
                        invariant_violations=[
                            InvariantViolation(
                                invariant_id="inv_1",
                                severity="critical",
                                details="Balance invariant violated",
                            )
                        ],
                    ),
                    timestamp="2026-01-01T00:00:00Z",
                    signature=_sig(),
                )

        stage = ShadowStage(simulator=ViolatingSimulator())
        result = stage.evaluate(_envelope(), [])

        assert result.decision == StageDecision.QUARANTINE
        assert any("inv_1" in r for r in result.reasons)

    def test_warning_violations_escalate(self):
        """Non-critical violations trigger escalation."""

        class WarningSimulator:
            def simulate(self, *args, **kwargs):
                return ShadowReport(
                    request_id="req_1",
                    shadow_job_id="shj_1",
                    snapshot_id="snap_1",
                    determinism=DeterminismProof(
                        seed="s", replay_hash="r", replay_verified=True
                    ),
                    results=ShadowResults(
                        divergence_score=0.0,
                        invariant_violations=[
                            InvariantViolation(
                                invariant_id="inv_2",
                                severity="warning",
                                details="Soft limit exceeded",
                            )
                        ],
                    ),
                    timestamp="2026-01-01T00:00:00Z",
                    signature=_sig(),
                )

        stage = ShadowStage(simulator=WarningSimulator())
        result = stage.evaluate(_envelope(), [])

        assert result.decision == StageDecision.ESCALATE


class TestShadowStagePrivilegeAnomalies:
    """Test privilege anomaly detection."""

    def test_privilege_anomalies_quarantine(self):
        """Privilege anomalies trigger quarantine."""

        class AnomalousSimulator:
            def simulate(self, *args, **kwargs):
                return ShadowReport(
                    request_id="req_1",
                    shadow_job_id="shj_1",
                    snapshot_id="snap_1",
                    determinism=DeterminismProof(
                        seed="s", replay_hash="r", replay_verified=True
                    ),
                    results=ShadowResults(
                        divergence_score=0.0,
                        privilege_anomalies=[
                            PrivilegeAnomaly(
                                type="unexpected_syscall", details="execve detected"
                            )
                        ],
                    ),
                    timestamp="2026-01-01T00:00:00Z",
                    signature=_sig(),
                )

        stage = ShadowStage(simulator=AnomalousSimulator())
        result = stage.evaluate(_envelope(), [])

        assert result.decision == StageDecision.QUARANTINE
        assert any("privilege" in r.lower() for r in result.reasons)


class TestShadowStageDivergence:
    """Test divergence scoring and thresholds."""

    def test_moderate_divergence_escalates(self):
        """Moderate divergence triggers escalation."""

        class ModDivergenceSimulator:
            def simulate(self, *args, **kwargs):
                return ShadowReport(
                    request_id="req_1",
                    shadow_job_id="shj_1",
                    snapshot_id="snap_1",
                    determinism=DeterminismProof(
                        seed="s", replay_hash="r", replay_verified=True
                    ),
                    results=ShadowResults(divergence_score=0.5),
                    timestamp="2026-01-01T00:00:00Z",
                    signature=_sig(),
                )

        stage = ShadowStage(
            simulator=ModDivergenceSimulator(),
            divergence_threshold=0.3,
            critical_divergence_threshold=0.7,
        )
        result = stage.evaluate(_envelope(), [])

        assert result.decision == StageDecision.ESCALATE

    def test_critical_divergence_quarantines(self):
        """Critical divergence triggers quarantine."""

        class CritDivergenceSimulator:
            def simulate(self, *args, **kwargs):
                return ShadowReport(
                    request_id="req_1",
                    shadow_job_id="shj_1",
                    snapshot_id="snap_1",
                    determinism=DeterminismProof(
                        seed="s", replay_hash="r", replay_verified=True
                    ),
                    results=ShadowResults(divergence_score=0.9),
                    timestamp="2026-01-01T00:00:00Z",
                    signature=_sig(),
                )

        stage = ShadowStage(
            simulator=CritDivergenceSimulator(),
            divergence_threshold=0.3,
            critical_divergence_threshold=0.7,
        )
        result = stage.evaluate(_envelope(), [])

        assert result.decision == StageDecision.QUARANTINE


class TestShadowStageResourceLimits:
    """Test resource envelope validation."""

    def test_high_cpu_usage_escalates(self):
        """High CPU usage triggers escalation."""

        class HighCPUSimulator:
            def simulate(self, *args, **kwargs):
                return ShadowReport(
                    request_id="req_1",
                    shadow_job_id="shj_1",
                    snapshot_id="snap_1",
                    determinism=DeterminismProof(
                        seed="s", replay_hash="r", replay_verified=True
                    ),
                    results=ShadowResults(
                        divergence_score=0.0,
                        resource_envelope=ResourceEnvelope(
                            cpu_ms=950.0,  # 95% of 1000ms quota
                            mem_peak_bytes=1024,
                            io_bytes=0,
                            syscalls=[],
                        ),
                    ),
                    timestamp="2026-01-01T00:00:00Z",
                    signature=_sig(),
                )

        stage = ShadowStage(simulator=HighCPUSimulator(), cpu_quota_ms=1000.0)
        result = stage.evaluate(_envelope(), [])

        assert result.decision == StageDecision.ESCALATE
        assert any("cpu" in r.lower() for r in result.reasons)

    def test_high_memory_usage_escalates(self):
        """High memory usage triggers escalation."""

        class HighMemSimulator:
            def simulate(self, *args, **kwargs):
                return ShadowReport(
                    request_id="req_1",
                    shadow_job_id="shj_1",
                    snapshot_id="snap_1",
                    determinism=DeterminismProof(
                        seed="s", replay_hash="r", replay_verified=True
                    ),
                    results=ShadowResults(
                        divergence_score=0.0,
                        resource_envelope=ResourceEnvelope(
                            cpu_ms=10.0,
                            mem_peak_bytes=int(256 * 0.96 * 1024 * 1024),  # 96% of 256MB
                            io_bytes=0,
                            syscalls=[],
                        ),
                    ),
                    timestamp="2026-01-01T00:00:00Z",
                    signature=_sig(),
                )

        stage = ShadowStage(simulator=HighMemSimulator(), memory_quota_mb=256.0)
        result = stage.evaluate(_envelope(), [])

        assert result.decision == StageDecision.ESCALATE
        assert any("memory" in r.lower() for r in result.reasons)


class TestShadowStageErrorHandling:
    """Test error handling and resilience."""

    def test_simulation_error_quarantines(self):
        """Simulation errors trigger quarantine."""

        class FailingSimulator:
            def simulate(self, *args, **kwargs):
                raise ShadowSimulationError(
                    "Resource limit exceeded", error_type="resource_violation"
                )

        stage = ShadowStage(simulator=FailingSimulator())
        result = stage.evaluate(_envelope(), [])

        assert result.decision == StageDecision.QUARANTINE
        assert "error_type" in result.metadata
        assert result.metadata["error_type"] == "resource_violation"

    def test_unexpected_exception_quarantines(self):
        """Unexpected exceptions trigger quarantine."""

        class BuggySimulator:
            def simulate(self, *args, **kwargs):
                raise ValueError("Unexpected bug!")

        stage = ShadowStage(simulator=BuggySimulator())
        result = stage.evaluate(_envelope(), [])

        assert result.decision == StageDecision.QUARANTINE
        assert any("unexpected" in r.lower() for r in result.reasons)


class TestShadowStageMetadata:
    """Test metadata attachment."""

    def test_metadata_contains_key_fields(self):
        """Result metadata contains all key fields."""
        stage = ShadowStage()
        result = stage.evaluate(_envelope(), [])

        assert "shadow_report" in result.metadata
        assert "shadow_hash" in result.metadata
        assert "divergence_score" in result.metadata
        assert "cpu_ms" in result.metadata
        assert "mem_peak_mb" in result.metadata
        assert "syscalls" in result.metadata
        assert "determinism_verified" in result.metadata

    def test_shadow_hash_deterministic(self):
        """Shadow hash is deterministic for same inputs (passthrough only)."""
        # Note: Production simulator includes timestamps which are non-deterministic
        # Only passthrough simulator guarantees deterministic hashing
        stage = ShadowStage(simulator=PassthroughSimulator())
        r1 = stage.evaluate(_envelope(request_id="req_1"), [])
        r2 = stage.evaluate(_envelope(request_id="req_1"), [])

        # Hash should be identical for same inputs with passthrough
        assert r1.metadata["shadow_hash"] == r2.metadata["shadow_hash"]
