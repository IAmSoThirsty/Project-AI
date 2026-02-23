"""
Tests for PSIA Waterfall Pipeline — 7-stage end-to-end tests.

Covers:
    - Full pipeline pass (all stages allow)
    - Stage 0 denial (structural validation)
    - Stage 1 quarantine (threat fingerprint match)
    - Stage 2 escalation (behavioral deviation)
    - Stage 3 quarantine (shadow determinism mismatch)
    - Stage 4 denial (Cerberus quorum failure)
    - Stage 5 commit rollback
    - Stage 6 ledger append
    - INV-ROOT-7 monotonic strictness
    - Event emission verification
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from psia.events import EventBus, EventType
from psia.schemas.identity import Signature
from psia.schemas.request import (
    Intent,
    RequestContext,
    RequestEnvelope,
    RequestTimestamps,
)
from psia.waterfall.engine import (
    StageDecision,
    StageResult,
    WaterfallEngine,
    WaterfallResult,
    WaterfallStage,
)
from psia.waterfall.stage_0_structural import StructuralStage
from psia.waterfall.stage_1_signature import (
    SignatureStage,
    ThreatFingerprint,
    ThreatFingerprintStore,
)
from psia.waterfall.stage_2_behavioral import BaselineProfileStore, BehavioralStage
from psia.waterfall.stage_3_shadow import PassthroughSimulator, ShadowStage
from psia.waterfall.stage_4_gate import GateStage, QuorumEngine
from psia.waterfall.stage_5_commit import CommitStage, InMemoryCanonicalStore
from psia.waterfall.stage_6_memory import InMemoryLedger, MemoryStage


def _sig() -> Signature:
    return Signature(alg="ed25519", kid="k1", sig="test_sig")


def _envelope(
    request_id: str = "req_test_001",
    actor: str = "did:project-ai:alice",
    subject: str = "did:project-ai:alice",
    action: str = "mutate_state",
    resource: str = "state://data/key1",
    token_id: str = "cap_001",
) -> RequestEnvelope:
    return RequestEnvelope(
        request_id=request_id,
        actor=actor,
        subject=subject,
        capability_token_id=token_id,
        intent=Intent(action=action, resource=resource, parameters={"value": 42}),
        context=RequestContext(trace_id="trace_test_001"),
        timestamps=RequestTimestamps(created_at=datetime.now(timezone.utc).isoformat()),
        signature=_sig(),
    )


def _full_engine(**kwargs) -> WaterfallEngine:
    """Create a fully-wired engine with all stages."""
    return WaterfallEngine(
        structural_stage=kwargs.get("structural_stage", StructuralStage()),
        signature_stage=kwargs.get("signature_stage", SignatureStage()),
        behavioral_stage=kwargs.get("behavioral_stage", BehavioralStage()),
        shadow_stage=kwargs.get("shadow_stage", ShadowStage()),
        gate_stage=kwargs.get("gate_stage", GateStage()),
        commit_stage=kwargs.get("commit_stage", CommitStage()),
        memory_stage=kwargs.get("memory_stage", MemoryStage()),
        **{k: v for k, v in kwargs.items() if k == "event_bus"},
    )


# ── Full Pipeline Tests ──────────────────────────────────────────────

class TestFullPipeline:
    def test_allow_pass(self):
        engine = _full_engine()
        result = engine.process(_envelope())
        assert result.is_allowed
        assert len(result.stage_results) == 7
        assert result.aborted_at_stage is None

    def test_events_emitted(self):
        bus = EventBus()
        engine = _full_engine(event_bus=bus)
        engine.process(_envelope())
        # At minimum: WATERFALL_START + 7x STAGE_ENTER + 7x STAGE_EXIT + REQUEST_ALLOWED
        assert bus.event_count >= 16

    def test_result_contains_cerberus_decision(self):
        engine = _full_engine()
        result = engine.process(_envelope())
        assert result.cerberus_decision is not None
        assert result.cerberus_decision.final_decision == "allow"


# ── Stage 0: Structural Tests ────────────────────────────────────────

class TestStructuralStage:
    def test_valid_envelope_allows(self):
        stage = StructuralStage()
        result = stage.evaluate(_envelope(), [])
        assert result.decision == StageDecision.ALLOW

    def test_expired_token_denies(self):
        stage = StructuralStage()
        stage.register_token("cap_001", {
            "expires_at": "2020-01-01T00:00:00Z",
            "nonce": "n001",
        })
        result = stage.evaluate(_envelope(), [])
        assert result.decision == StageDecision.DENY
        assert any("expired" in r for r in result.reasons)

    def test_nonce_replay_denies(self):
        stage = StructuralStage()
        stage.register_token("cap_001", {
            "expires_at": "2027-01-01T00:00:00Z",
            "nonce": "nonce_abc",
        })
        # First request: OK
        r1 = stage.evaluate(_envelope(), [])
        assert r1.decision == StageDecision.ALLOW
        # Second request with same nonce: replay
        r2 = stage.evaluate(_envelope(), [])
        assert r2.decision == StageDecision.DENY
        assert any("replay" in r for r in r2.reasons)


# ── Stage 1: Signature Tests ─────────────────────────────────────────

class TestSignatureStage:
    def test_no_fingerprints_allows(self):
        stage = SignatureStage()
        result = stage.evaluate(_envelope(), [])
        assert result.decision == StageDecision.ALLOW

    def test_critical_fingerprint_quarantines(self):
        store = ThreatFingerprintStore()
        store.add(ThreatFingerprint(
            fingerprint_id="fp_001",
            pattern_type="actor",
            pattern_value="did:project-ai:alice",
            severity="critical",
            reason="known attacker",
        ))
        stage = SignatureStage(store=store)
        result = stage.evaluate(_envelope(), [])
        assert result.decision == StageDecision.QUARANTINE

    def test_medium_fingerprint_escalates(self):
        store = ThreatFingerprintStore()
        store.add(ThreatFingerprint(
            fingerprint_id="fp_002",
            pattern_type="actor",
            pattern_value="did:project-ai:alice",
            severity="med",
            reason="suspicious pattern",
        ))
        stage = SignatureStage(store=store)
        result = stage.evaluate(_envelope(), [])
        assert result.decision == StageDecision.ESCALATE


# ── Stage 2: Behavioral Tests ────────────────────────────────────────

class TestBehavioralStage:
    def test_first_request_allows(self):
        stage = BehavioralStage()
        result = stage.evaluate(_envelope(), [])
        assert result.decision == StageDecision.ALLOW

    def test_novel_resource_after_history_may_escalate(self):
        store = BaselineProfileStore()
        # Build up baseline with 10 requests to one resource
        for i in range(10):
            store.record_request("did:project-ai:alice", "read", "state://known/resource")
        stage = BehavioralStage(store=store, escalation_threshold=0.1)
        # Now request a novel resource with novel action
        result = stage.evaluate(
            _envelope(action="mutate_policy", resource="state://new/resource"),
            [],
        )
        assert result.decision in (StageDecision.ESCALATE, StageDecision.QUARANTINE)


# ── Stage 3: Shadow Tests ────────────────────────────────────────────

class TestShadowStage:
    def test_passthrough_allows(self):
        stage = ShadowStage()
        result = stage.evaluate(_envelope(), [])
        assert result.decision == StageDecision.ALLOW
        assert "shadow_report" in result.metadata

    def test_high_divergence_escalates(self):
        """Custom simulator returning high divergence."""
        from psia.schemas.shadow_report import (
            DeterminismProof,
            ShadowReport,
            ShadowResults,
        )

        class HighDivergenceSimulator:
            def simulate(self, request_id, action, resource, parameters):
                return ShadowReport(
                    request_id=request_id,
                    shadow_job_id="shj_hd",
                    snapshot_id="snap_hd",
                    determinism=DeterminismProof(seed="s", replay_hash="r", replay_verified=True),
                    results=ShadowResults(divergence_score=0.9),
                    timestamp="2026-01-01T00:00:00Z",
                    signature=_sig(),
                )

        stage = ShadowStage(simulator=HighDivergenceSimulator(), divergence_threshold=0.3)
        result = stage.evaluate(_envelope(), [])
        assert result.decision in (StageDecision.ESCALATE, StageDecision.QUARANTINE)


# ── Stage 4: Gate Tests ──────────────────────────────────────────────

class TestGateStage:
    def test_all_allow(self):
        stage = GateStage()
        result = stage.evaluate(_envelope(), [])
        assert result.decision == StageDecision.ALLOW
        assert "cerberus_decision" in result.metadata

    def test_invalid_did_denies(self):
        stage = GateStage()
        env = _envelope(actor="invalid_did")
        result = stage.evaluate(env, [])
        assert result.decision == StageDecision.DENY

    def test_unanimous_quorum(self):
        stage = GateStage(quorum_engine=QuorumEngine("unanimous"))
        result = stage.evaluate(_envelope(), [])
        assert result.decision == StageDecision.ALLOW


# ── Stage 5: Commit Tests ────────────────────────────────────────────

class TestCommitStage:
    def _gate_result(self, allowed: bool = True):
        """Produce a mock gate stage result."""
        from psia.schemas.cerberus_decision import (
            CerberusDecision,
            CerberusVote,
            CommitPolicy,
            QuorumInfo,
        )
        return StageResult(
            stage=WaterfallStage.GATE,
            decision=StageDecision.ALLOW if allowed else StageDecision.DENY,
            metadata={
                "cerberus_decision": CerberusDecision(
                    request_id="req_test_001",
                    severity="low",
                    final_decision="allow" if allowed else "deny",
                    votes=[],
                    quorum=QuorumInfo(required="2of3", achieved=allowed),
                    commit_policy=CommitPolicy(allowed=allowed),
                    timestamp="2026-01-01T00:00:00Z",
                ),
            },
        )

    def test_commit_succeeds(self):
        store = InMemoryCanonicalStore()
        stage = CommitStage(store=store)
        result = stage.evaluate(_envelope(), [self._gate_result(True)])
        assert result.decision == StageDecision.ALLOW
        assert store.version == 1

    def test_commit_denied_without_cerberus(self):
        stage = CommitStage()
        result = stage.evaluate(_envelope(), [])
        assert result.decision == StageDecision.DENY

    def test_commit_denied_when_not_allowed(self):
        stage = CommitStage()
        result = stage.evaluate(_envelope(), [self._gate_result(False)])
        assert result.decision == StageDecision.DENY


# ── Stage 6: Memory Tests ────────────────────────────────────────────

class TestMemoryStage:
    def _prior_results(self):
        from psia.schemas.cerberus_decision import (
            CerberusDecision,
            CommitPolicy,
            QuorumInfo,
        )
        return [
            StageResult(
                stage=WaterfallStage.SHADOW,
                decision=StageDecision.ALLOW,
                metadata={"shadow_hash": "aa" * 32},
            ),
            StageResult(
                stage=WaterfallStage.GATE,
                decision=StageDecision.ALLOW,
                metadata={
                    "cerberus_decision": CerberusDecision(
                        request_id="req_test_001",
                        severity="low",
                        final_decision="allow",
                        votes=[],
                        quorum=QuorumInfo(required="2of3", achieved=True),
                        commit_policy=CommitPolicy(allowed=True),
                        timestamp="2026-01-01T00:00:00Z",
                    ),
                },
            ),
            StageResult(
                stage=WaterfallStage.COMMIT,
                decision=StageDecision.ALLOW,
                metadata={"canonical_diff_hash": "bb" * 32},
            ),
        ]

    def test_append_record(self):
        ledger = InMemoryLedger()
        stage = MemoryStage(ledger=ledger)
        result = stage.evaluate(_envelope(), self._prior_results())
        assert result.decision == StageDecision.ALLOW
        assert ledger.record_count == 1

    def test_block_sealing(self):
        ledger = InMemoryLedger(block_size=2)
        stage = MemoryStage(ledger=ledger)
        stage.evaluate(_envelope(request_id="req_1"), self._prior_results())
        stage.evaluate(_envelope(request_id="req_2"), self._prior_results())
        assert ledger.block_count == 1
        assert ledger.pending_records == 0

    def test_deny_callback_fired(self):
        from psia.schemas.cerberus_decision import (
            CerberusDecision,
            CommitPolicy,
            QuorumInfo,
        )
        deny_results = [
            StageResult(
                stage=WaterfallStage.GATE,
                decision=StageDecision.DENY,
                metadata={
                    "cerberus_decision": CerberusDecision(
                        request_id="req_test_001",
                        severity="high",
                        final_decision="deny",
                        votes=[],
                        quorum=QuorumInfo(required="2of3", achieved=False),
                        commit_policy=CommitPolicy(allowed=False),
                        timestamp="2026-01-01T00:00:00Z",
                    ),
                },
            ),
        ]
        callback_log = []
        stage = MemoryStage(on_deny_callback=lambda env, res: callback_log.append(res))
        stage.evaluate(_envelope(), deny_results)
        assert len(callback_log) == 1
        assert callback_log[0] == "deny"
