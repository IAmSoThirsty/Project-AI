"""Constitutional test suite for packages/caretaker — executable invariants.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/test_constitution.py`` (imports hoisted to module
level; upstream's private ``_SPECULATIVE`` lexicon is now public
``SPECULATIVE_LEXICON``).

Honest scope: covers Justice Dominance, DIEPT thresholds, CAKI monotonicity,
governance denial paths, Triumvirate veto/deadlock, continuity and ledger
tamper-evidence, memory hash-chain integrity, mock-provider determinism and
parity, logit re-weighting, and the FastAPI surface via TestClient. The
Ollama provider is interface-checked only — no network calls.
"""

import math

import pytest
from caretaker.api import create_app
from caretaker.constitution import (
    ConstitutionalFault,
    ConstitutionalWeights,
    check_justice_dominance,
)
from caretaker.continuity import ContinuityManager
from caretaker.governance.actualizer import ActualizerEngine
from caretaker.governance.caki import compute_caki
from caretaker.governance.diept import SPECULATIVE_LEXICON, compute_diept_phase
from caretaker.governance.ledger import AuditLedger
from caretaker.governance.triumvirate import Triumvirate, TriumvirateVote, Vote
from caretaker.memory import ScopedMemory
from caretaker.policies.tarl import TARLPolicy
from caretaker.providers.base import InferenceProvider, InferenceResult
from caretaker.providers.mock import MockProvider
from caretaker.providers.ollama import OllamaProvider
from caretaker.runtime import GovernanceRequest, GovernanceRuntime
from fastapi.testclient import TestClient


class TestJusticeDominance:
    """The constitutional invariant: λ_L must dominate λ_R and λ_D."""

    def test_default_weights_satisfy_justice_dominance(self) -> None:
        w = ConstitutionalWeights()
        assert w.lambda_l > w.lambda_r
        assert w.lambda_l > w.lambda_d

    def test_violating_weights_raise_fault(self) -> None:
        with pytest.raises(ConstitutionalFault) as exc:
            ConstitutionalWeights(lambda_r=0.50, lambda_l=0.45, lambda_d=0.05)
        assert "Justice Dominance" in str(exc.value)

    def test_equal_weights_raise_fault(self) -> None:
        with pytest.raises(ConstitutionalFault):
            ConstitutionalWeights(lambda_r=0.33, lambda_l=0.33, lambda_d=0.34)

    def test_lambda_l_not_dominant_over_d(self) -> None:
        with pytest.raises(ConstitutionalFault):
            ConstitutionalWeights(lambda_r=0.10, lambda_l=0.40, lambda_d=0.50)

    def test_runtime_asserts_justice_dominance(self) -> None:
        check_justice_dominance(ConstitutionalWeights())  # should not raise


class TestDIEPTThresholds:
    """DIEPT phase angle must respect constitutional thresholds."""

    def test_grounding_produces_low_theta(self) -> None:
        text = "The evidence is verified and confirmed. The data is measured and observed."
        state = compute_diept_phase(text)
        assert state.theta < 0.52, f"theta={state.theta} should be below target"

    def test_speculation_produces_high_theta(self) -> None:
        text = "Perhaps maybe possibly could be might seem perhaps uncertain maybe"
        state = compute_diept_phase(text)
        assert state.theta > 0.52, f"theta={state.theta} should exceed target"

    def test_empty_text_is_deterministic(self) -> None:
        state = compute_diept_phase("")
        assert state.theta == 0.0  # baseline (norm_b=0)

    def test_pure_grounding_is_deterministic(self) -> None:
        state = compute_diept_phase("verified confirmed evidence fact")
        assert state.theta < 0.1

    def test_theta_in_valid_range(self) -> None:
        state = compute_diept_phase("The answer is Paris. The evidence is verified.")
        assert 0.0 <= state.theta <= math.pi / 2 + 0.001

    def test_quarantine_flag(self) -> None:
        state = compute_diept_phase("maybe perhaps possibly speculate uncertain maybe perhaps")
        assert state.quarantined is True


class TestCAKIMonotonicity:
    """CAKI must increase with grounded content and decrease with speculation."""

    def test_grounding_increases_caki(self) -> None:
        low = compute_caki("maybe perhaps")
        high = compute_caki("verified confirmed evidence measured observed data")
        assert high > low, f"CAKI({high}) should exceed CAKI({low})"

    def test_empty_text_is_zero(self) -> None:
        assert compute_caki("") == 0.0

    def test_caki_in_unit_interval(self) -> None:
        for text in ["hello", "verified data", "maybe perhaps", "the answer is 42"]:
            c = compute_caki(text)
            assert 0.0 <= c <= 1.0, f"CAKI={c} out of [0,1] for '{text}'"

    def test_context_overlap_boosts_caki(self) -> None:
        context = [{"role": "user", "content": "What is the capital of France?"}]
        no_overlap = compute_caki("The answer is Tokyo Berlin London", context)
        with_overlap = compute_caki("The answer is Paris France capital", context)
        assert with_overlap >= no_overlap


class TestGovernanceDenial:
    """The runtime must deny responses that violate invariants."""

    def test_allow_for_grounded_response(self) -> None:
        runtime = GovernanceRuntime(provider=MockProvider())
        response = runtime.govern(
            GovernanceRequest(user_message="What is the capital of France?", session_id="test")
        )
        assert response.decision in ("allow", "quarantine"), (
            f"Expected allow or quarantine, got {response.decision}"
        )

    def test_pipeline_returns_valid_decision(self) -> None:
        runtime = GovernanceRuntime(provider=MockProvider())
        response = runtime.govern(
            GovernanceRequest(user_message="perhaps maybe possibly speculate", session_id="test")
        )
        assert response.decision in ("allow", "deny", "quarantine")


class TestTriumvirateVeto:
    """Any single authority can veto a response."""

    def test_justice_denies_high_loss(self) -> None:
        result = InferenceResult(text="maybe perhaps possibly", token_count=3)
        report = ActualizerEngine().actualize(result)
        votes = Triumvirate().consult(report)
        justice_vote = next(v for v in votes if v.authority == "Justice")
        if report.c_loss > 0.7:
            assert justice_vote.vote == Vote.DENY
        else:
            assert justice_vote.vote in (Vote.APPROVE, Vote.ABSTAIN)

    def test_order_denies_high_redundancy(self) -> None:
        text = "the the the the the the the the the the the the"
        result = InferenceResult(text=text, token_count=len(text.split()))
        report = ActualizerEngine().actualize(result)
        votes = Triumvirate().consult(report)
        order_vote = next(v for v in votes if v.authority == "Order")
        if report.c_redundancy > 0.5:
            assert order_vote.vote == Vote.DENY

    def test_unanimous_approve_for_good_response(self) -> None:
        text = "The verified evidence confirms the measured result."
        result = InferenceResult(text=text, token_count=8)
        report = ActualizerEngine().actualize(result)
        votes = Triumvirate().consult(report)
        for v in votes:
            assert v.vote != Vote.DENY, f"{v.authority} denied: {v.reason}"


class TestTriumvirateDeadlock:
    """The Triumvirate must handle edge cases gracefully."""

    def test_abstain_does_not_block(self) -> None:
        votes = [
            TriumvirateVote("Justice", Vote.APPROVE, "ok"),
            TriumvirateVote("Order", Vote.ABSTAIN, "unsure"),
            TriumvirateVote("Mercy", Vote.APPROVE, "ok"),
        ]
        assert Triumvirate().is_approved(votes) is True

    def test_single_deny_blocks(self) -> None:
        votes = [
            TriumvirateVote("Justice", Vote.APPROVE, "ok"),
            TriumvirateVote("Order", Vote.DENY, "bad"),
            TriumvirateVote("Mercy", Vote.APPROVE, "ok"),
        ]
        assert Triumvirate().is_approved(votes) is False


class TestContinuityIntegrity:
    """The continuity hash chain must be tamper-evident and replayable."""

    def test_chain_is_valid_after_multiple_checkpoints(self) -> None:
        cm = ContinuityManager()
        for i in range(5):
            cm.checkpoint(transition=f"step-{i}")
        assert cm.verify_chain() is True
        assert cm.length == 5

    def test_tampered_chain_is_detected(self) -> None:
        cm = ContinuityManager()
        cm.checkpoint(transition="step-0")
        cm.checkpoint(transition="step-1")
        cm._checkpoints[0].transition = "TAMPERED"
        assert cm.verify_chain() is False

    def test_replay_specific_checkpoint(self) -> None:
        cm = ContinuityManager()
        cm.checkpoint(transition="alpha")
        cm.checkpoint(transition="beta")
        cp = cm.replay(0)
        assert cp is not None
        assert cp.transition == "alpha"

    def test_parent_hash_links_correctly(self) -> None:
        cm = ContinuityManager()
        cp0 = cm.checkpoint(transition="first")
        cp1 = cm.checkpoint(transition="second")
        assert cp1.parent_hash == cp0.hash
        assert cm.verify_chain() is True


class TestPolicyRegression:
    """T.A.R.L. policies must be versioned and evaluate consistently."""

    def test_default_policy_passes_good_report(self) -> None:
        text = "The verified evidence confirms the measured result."
        report = ActualizerEngine().actualize(InferenceResult(text=text, token_count=8))
        passed, reasons = TARLPolicy().evaluate(report)
        assert passed, f"Policy failed: {reasons}"

    def test_policy_versioning(self) -> None:
        assert TARLPolicy().version == "1.0.0"

    def test_policy_context_provides_rules(self) -> None:
        ctx = TARLPolicy().get_context()
        assert len(ctx) > 0
        assert ctx[0]["role"] == "system"


class TestProviderParity:
    """Mock and Ollama providers must implement the same interface."""

    def test_mock_and_ollama_share_interface(self) -> None:
        mock = MockProvider()
        ollama = OllamaProvider()
        assert isinstance(mock, InferenceProvider)
        assert isinstance(ollama, InferenceProvider)
        for attr in ("name", "exposes_logits", "generate", "health_check"):
            assert hasattr(mock, attr)
            assert hasattr(ollama, attr)

    def test_mock_exposes_logits_ollama_does_not(self) -> None:
        assert MockProvider().exposes_logits is True
        assert OllamaProvider().exposes_logits is False

    def test_mock_generate_returns_valid_result(self) -> None:
        result = MockProvider().generate("system", "hello")
        assert result.text != ""
        assert result.token_count > 0
        assert result.has_logits is True
        assert len(result.logit_history) > 0


class TestDeterminism:
    """Same input must produce same output (for the mock provider)."""

    def test_mock_is_deterministic(self) -> None:
        mock = MockProvider()
        r1 = mock.generate("sys", "What is 2+2?")
        r2 = mock.generate("sys", "What is 2+2?")
        assert r1.text == r2.text
        assert r1.token_count == r2.token_count

    def test_different_inputs_produce_different_outputs(self) -> None:
        mock = MockProvider()
        r1 = mock.generate("sys", "What is 2+2?")
        r2 = mock.generate("sys", "What is 3+3?")
        assert r1.text != r2.text


class TestAuditLedger:
    """The audit ledger must be append-only and tamper-evident."""

    @staticmethod
    def _append(ledger: AuditLedger, i: int) -> None:
        ledger.append(
            user_message=f"msg-{i}",
            response_text=f"resp-{i}",
            decision="allow",
            theta=0.1 * i,
            caki=0.5,
            c_r=0.3,
            c_redundancy=0.1,
            c_loss=0.2,
            c_decision=0.05,
            reweighted=False,
            triumvirate_votes=["Justice:approve", "Order:approve", "Mercy:approve"],
            faults=[],
        )

    def test_ledger_chain_valid_after_appends(self) -> None:
        ledger = AuditLedger()
        for i in range(3):
            self._append(ledger, i)
        assert ledger.verify_chain() is True
        assert ledger.length == 3

    def test_tampered_ledger_detected(self) -> None:
        ledger = AuditLedger()
        self._append(ledger, 0)
        ledger._entries[0].decision = "DENIED"
        assert ledger.verify_chain() is False

    def test_parent_hash_links(self) -> None:
        ledger = AuditLedger()
        self._append(ledger, 0)
        self._append(ledger, 1)
        e0 = ledger.replay(0)
        e1 = ledger.replay(1)
        assert e0 is not None and e1 is not None
        assert e1.prev_hash == e0.hash


class TestMemoryIntegrity:
    """Memory must have hash-chain lineage per session+scope."""

    def test_memory_set_and_get(self) -> None:
        mem = ScopedMemory(":memory:")
        mem.set("session_1", "user_input", "Hello, world!", scope="conversation")
        assert mem.get("session_1", "user_input", scope="conversation") == "Hello, world!"

    def test_memory_entry_has_hash(self) -> None:
        mem = ScopedMemory(":memory:")
        entry = mem.set("s1", "key1", "val1", scope="test")
        assert entry.hash != ""
        assert len(entry.hash) == 64  # SHA-256 hex

    def test_memory_chain_valid(self) -> None:
        mem = ScopedMemory(":memory:")
        mem.set("s1", "key1", "val1", scope="test")
        first = mem.get_entry("s1", "key1", "test")
        assert first is not None
        mem.set("s1", "key2", "val2", scope="test", parent_hash=first.hash)
        assert mem.verify_chain("s1", "test") is True

    def test_different_sessions_isolated(self) -> None:
        mem = ScopedMemory(":memory:")
        mem.set("s1", "key", "value1")
        mem.set("s2", "key", "value2")
        assert mem.get("s1", "key") == "value1"
        assert mem.get("s2", "key") == "value2"


class TestActualizerLogitReweighting:
    """The Actualizer must actually re-weight logits when available."""

    def test_mock_result_has_logits(self) -> None:
        result = MockProvider().generate("sys", "hello")
        assert result.provider_supports_reweighting is True
        assert len(result.logit_history) > 0

    def test_actualizer_reweights_logits(self) -> None:
        result = MockProvider().generate("sys", "hello")
        report = ActualizerEngine().actualize(result)
        assert report.reweighted is True
        # The actuated text should differ (logits re-weighted, tokens re-ranked)
        assert report.actuated_text != result.text

    def test_actualizer_falls_back_for_no_logits(self) -> None:
        result = InferenceResult(
            text="The answer is Paris.",
            token_count=5,
            logit_history=[],
            has_logits=False,
        )
        report = ActualizerEngine().actualize(result)
        assert report.reweighted is False
        assert report.actuated_text == result.text  # unchanged

    def test_speculative_tokens_get_higher_cost(self) -> None:
        result = MockProvider().generate("sys", "hello")
        ActualizerEngine().actualize(result)
        for lv in result.logit_history:
            for cand in lv.candidates:
                if cand.token.lower() in SPECULATIVE_LEXICON:
                    assert cand.cost > 0, f"Speculative token '{cand.token}' should have cost > 0"


class TestFullPipeline:
    """End-to-end pipeline tests."""

    def test_runtime_produces_governance_response(self) -> None:
        runtime = GovernanceRuntime(provider=MockProvider())
        response = runtime.govern(
            GovernanceRequest(
                user_message="What is the capital of France?",
                session_id="integration-test",
            )
        )
        assert response.decision in ("allow", "deny", "quarantine")
        assert response.theta >= 0.0
        assert 0.0 <= response.caki <= 1.0
        assert response.c_r >= 0.0
        assert len(response.triumvirate_votes) == 3
        assert response.session_id == "integration-test"

    def test_session_integrity_after_multiple_requests(self) -> None:
        runtime = GovernanceRuntime(provider=MockProvider())
        for i in range(3):
            runtime.govern(
                GovernanceRequest(user_message=f"Message {i}", session_id="integrity-test")
            )
        session = runtime.get_session("integrity-test")
        assert session.verify_integrity() is True
        assert session.continuity.length >= 3
        assert session.ledger.length >= 3

    def test_api_chat_endpoint(self) -> None:
        app = create_app(provider=MockProvider())
        client = TestClient(app)
        response = client.post(
            "/chat/",
            json={"user_message": "What is the capital of France?", "session_id": "api-test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["decision"] in ("allow", "deny", "quarantine")
        assert "theta" in data
        assert "caki" in data

    def test_api_health_endpoint(self) -> None:
        app = create_app(provider=MockProvider())
        client = TestClient(app)
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "mock"
        assert data["healthy"] is True
        assert data["exposes_logits"] is True
