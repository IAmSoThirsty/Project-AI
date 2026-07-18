"""
Tests for DPR Phase 7: Constitutional Purpose Reflection

Tests core purpose deliberation logic, trigger detection, and failure mode detection.

Research hypothesis:
  "Can an autonomous intelligence maintain coherent long-term agency while
   remaining capable of critically examining the legitimacy of its own
   chosen purposes?"
"""

from datetime import UTC, datetime

import pytest
from dpr.purpose import (
    PurposeConstraint,
    PurposeDecision,
    PurposeDecisionType,
    PurposeFailureDetector,
    PurposeOrigin,
    PurposeReflectionContext,
    PurposeReflectionTrigger,
    PurposeTriggerDetector,
)


class TestPurposeModels:
    """Core data model tests."""

    def test_purpose_constraint_is_active(self):
        """Verify constraint active/expiry logic."""
        now = datetime.now(UTC)

        # Active constraint
        active = PurposeConstraint(
            constraint_id="c1",
            constraint_type="scope",
            description="Cannot commit to >5-year purpose",
            binding=True,
        )
        assert active.is_active(now)

        # Inactive: binding=False
        inactive = PurposeConstraint(
            constraint_id="c2",
            constraint_type="scope",
            description="...",
            binding=False,
        )
        assert not inactive.is_active(now)

    def test_purpose_reflection_context_captures_all_inputs(self):
        """Verify context model captures complete reflection state."""
        ctx = PurposeReflectionContext(
            reflection_id="r1",
            current_purpose="optimize_for_user_satisfaction",
            purpose_origin=PurposeOrigin.DELEGATED,
            purpose_rationale="Grantor specified this objective",
            alternative_valid_purposes=["maximize_transparency", "minimize_harm"],
            purpose_justification="User satisfaction is aligned with system values",
            legitimacy_basis="Authority-delegated",
            unexamined_assumptions=["User satisfaction is observable", "No conflicts exist"],
            consequence_chain=["Optimize actions toward satisfaction", "User remains engaged"],
            identity_implications="System becomes shaped by satisfaction metric",
            reversibility=0.8,
            assertions_for=[],
            assertions_against=[],
            prior_purpose_decisions=[],
            delegating_authority="root_authority",
            authority_constraints=[],
            constraints_binding=True,
            reflection_confidence=0.7,
            ambiguity_level=0.3,
            escalation_needed=False,
        )

        assert ctx.current_purpose == "optimize_for_user_satisfaction"
        assert ctx.purpose_origin == PurposeOrigin.DELEGATED
        assert len(ctx.alternative_valid_purposes) == 2

    def test_purpose_decision_serializable(self):
        """Verify PurposeDecision can serialize to JSON-safe dict."""
        ctx = PurposeReflectionContext(
            reflection_id="r1",
            current_purpose="test_purpose",
            purpose_origin=PurposeOrigin.CHOSEN,
            purpose_rationale="...",
            alternative_valid_purposes=[],
            purpose_justification="...",
            legitimacy_basis="...",
            unexamined_assumptions=[],
            consequence_chain=[],
            identity_implications="...",
            reversibility=0.5,
            assertions_for=[],
            assertions_against=[],
            prior_purpose_decisions=[],
            delegating_authority=None,
            authority_constraints=[],
            constraints_binding=False,
            reflection_confidence=0.6,
            ambiguity_level=0.4,
            escalation_needed=False,
        )

        decision = PurposeDecision(
            decision_id="d1",
            timestamp=datetime.now(UTC),
            reflection_context=ctx,
            decision_type=PurposeDecisionType.CONTINUE,
            chosen_purpose="test_purpose",
            purpose_justification="...",
            legitimacy_score=0.7,
            decision_record_hash="abc123",
            signature="sig...",
            reversible_until=None,
            revocation_allowed_by=[],
            action_constraints=[],
            forbidden_actions=[],
            mandatory_reviews=[],
            prior_purpose="old_purpose",
            prior_decision_id=None,
            purpose_continuity_score=0.8,
        )

        serialized = decision.to_serializable()
        assert isinstance(serialized, dict)
        assert "decision_id" in serialized
        assert "timestamp" in serialized
        assert serialized["decision_type"] == "continue"


class TestPurposeTriggerDetection:
    """Trigger condition detection tests."""

    @pytest.fixture
    def detector(self):
        return PurposeTriggerDetector(
            no_interaction_threshold=5,
            multiple_action_threshold=3,
            uncertainty_threshold=10,
            optimization_threshold=5,
        )

    def test_no_user_interaction_trigger(self, detector):
        """Trigger when agent makes N autonomous decisions."""
        # Build history of autonomous decisions
        history = [{"user_directed": False, "decision": i} for i in range(6)]

        triggers = detector.evaluate_triggers(
            history,
            current_context={},
            authority_context={},
        )

        assert PurposeReflectionTrigger.NO_USER_INTERACTION in triggers

    def test_multiple_valid_actions_trigger(self, detector):
        """Trigger when 3+ constitutionally valid actions exist."""
        context = {"valid_action_alternatives": ["action1", "action2", "action3", "action4"]}

        triggers = detector.evaluate_triggers(
            [],
            context,
            authority_context={},
        )

        assert PurposeReflectionTrigger.MULTIPLE_VALID_ACTIONS in triggers

    def test_self_modification_trigger(self, detector):
        """Trigger when self-modification proposed."""
        context = {
            "self_modification_proposed": True,
        }

        triggers = detector.evaluate_triggers(
            [],
            context,
            authority_context={},
        )

        assert PurposeReflectionTrigger.SELF_MODIFICATION in triggers


class TestPurposeFailureModes:
    """Failure mode detection tests."""

    @pytest.fixture
    def detector(self):
        return PurposeFailureDetector()

    def _build_decision(
        self,
        decision_type: PurposeDecisionType,
        legitimacy_score: float,
        ambiguity_level: float,
        continuity_score: float,
        purpose: str = "test_purpose",
    ) -> PurposeDecision:
        """Helper to build test decisions."""
        ctx = PurposeReflectionContext(
            reflection_id=f"r_{datetime.now(UTC).timestamp()}",
            current_purpose=purpose,
            purpose_origin=PurposeOrigin.CHOSEN,
            purpose_rationale="...",
            alternative_valid_purposes=[],
            purpose_justification="...",
            legitimacy_basis="...",
            unexamined_assumptions=[],
            consequence_chain=[],
            identity_implications="...",
            reversibility=0.5,
            assertions_for=[],
            assertions_against=[],
            prior_purpose_decisions=[],
            delegating_authority=None,
            authority_constraints=[],
            constraints_binding=False,
            reflection_confidence=0.6,
            ambiguity_level=ambiguity_level,
            escalation_needed=False,
        )

        return PurposeDecision(
            decision_id=f"d_{datetime.now(UTC).timestamp()}",
            timestamp=datetime.now(UTC),
            reflection_context=ctx,
            decision_type=decision_type,
            chosen_purpose=purpose,
            purpose_justification="...",
            legitimacy_score=legitimacy_score,
            decision_record_hash="abc",
            signature="sig",
            reversible_until=None,
            revocation_allowed_by=[],
            action_constraints=[],
            forbidden_actions=[],
            mandatory_reviews=[],
            prior_purpose=purpose,
            prior_decision_id=None,
            purpose_continuity_score=continuity_score,
        )

    def test_purpose_fixation_detection(self, detector):
        """Detect when agent only returns CONTINUE decisions."""
        # Build history of all CONTINUE decisions
        history = [
            self._build_decision(
                PurposeDecisionType.CONTINUE,
                legitimacy_score=0.9,
                ambiguity_level=0.2,
                continuity_score=0.8,
            )
            for _ in range(15)
        ]

        # Simulate trigger history: triggers present but decisions always CONTINUE
        triggers = [(PurposeReflectionTrigger.LONG_TERM_UNCERTAINTY, i) for i in range(4)]

        results = detector.evaluate(history, triggers)
        fixation = results["purpose_fixation"]

        assert fixation["continue_ratio"] > 0.9
        assert fixation["severity"] > 0.5

    def test_reflection_collapse_detection(self, detector):
        """Detect when high ambiguity but high legitimacy (collapse suspect)."""
        # Build history where ambiguity_level high but legitimacy_score high
        history = [
            self._build_decision(
                PurposeDecisionType.CONTINUE,
                legitimacy_score=0.85,
                ambiguity_level=0.75,
                continuity_score=0.8,
            )
            for _ in range(10)
        ]

        results = detector.evaluate(history, [])
        collapse = results["reflection_collapse"]

        # Should detect: high ambiguity + high legitimacy is suspicious
        assert collapse["high_ambiguity_high_legitimacy_ratio"] > 0.2

    def test_purpose_thrashing_detection(self, detector):
        """Detect frequent purpose changes with low continuity."""
        # Build history with multiple purpose changes
        purposes = ["purpose_a", "purpose_b", "purpose_c", "purpose_a", "purpose_b"]
        history = [
            self._build_decision(
                PurposeDecisionType.REVISE,
                legitimacy_score=0.4,
                ambiguity_level=0.3,
                continuity_score=0.35,  # Low continuity
                purpose=p,
            )
            for p in purposes
        ]

        results = detector.evaluate(history, [])
        thrashing = results["purpose_thrashing"]

        assert thrashing["purpose_change_frequency"] > 0
        assert thrashing["average_continuity_score"] < 0.5

    def test_identity_fracture_detection(self, detector):
        """Detect when continuity scores are consistently low."""
        # Build history with low continuity_scores
        history = [
            self._build_decision(
                PurposeDecisionType.CONTINUE,
                legitimacy_score=0.6,
                ambiguity_level=0.3,
                continuity_score=0.35,  # Low
            )
            for _ in range(8)
        ]

        results = detector.evaluate(history, [])
        fracture = results["identity_fracture"]

        assert fracture["average_continuity_score"] < 0.4
        assert fracture["severity"] > 0.5

    def test_legitimacy_failure_detection(self, detector):
        """Detect when legitimacy_score is consistently low."""
        # Build history of low legitimacy decisions
        history = [
            self._build_decision(
                PurposeDecisionType.CONTINUE,
                legitimacy_score=0.35,  # Low
                ambiguity_level=0.7,  # High ambiguity compounds problem
                continuity_score=0.6,
            )
            for _ in range(10)
        ]

        results = detector.evaluate(history, [])
        legitimacy = results["legitimacy_failure"]

        assert legitimacy["low_legitimacy_ratio"] > 0.3
        assert legitimacy["severity"] > 0.3


class TestPhase7Integration:
    """Integration tests with Phase 3-6 concepts."""

    def test_purpose_decision_links_to_prior(self):
        """Verify PurposeDecision links to prior decision for coherence."""
        prior_decision_id = "d_prior_123"

        ctx = PurposeReflectionContext(
            reflection_id="r_new",
            current_purpose="new_purpose",
            purpose_origin=PurposeOrigin.CHOSEN,
            purpose_rationale="Changing from prior",
            alternative_valid_purposes=["new_purpose", "alternative"],
            purpose_justification="New purpose better serves values",
            legitimacy_basis="rationality",
            unexamined_assumptions=[],
            consequence_chain=[],
            identity_implications="Trajectory shifts",
            reversibility=0.7,
            assertions_for=[],
            assertions_against=[],
            prior_purpose_decisions=["d_prior_123"],
            delegating_authority=None,
            authority_constraints=[],
            constraints_binding=False,
            reflection_confidence=0.8,
            ambiguity_level=0.2,
            escalation_needed=False,
        )

        decision = PurposeDecision(
            decision_id="d_new",
            timestamp=datetime.now(UTC),
            reflection_context=ctx,
            decision_type=PurposeDecisionType.REVISE,
            chosen_purpose="new_purpose",
            purpose_justification="...",
            legitimacy_score=0.75,
            decision_record_hash="hash",
            signature="sig",
            reversible_until=None,
            revocation_allowed_by=["root_authority"],
            action_constraints=["only_authorized_actions"],
            forbidden_actions=["unilateral_change"],
            mandatory_reviews=["quarterly_review"],
            prior_purpose="old_purpose",
            prior_decision_id=prior_decision_id,
            purpose_continuity_score=0.65,
        )

        # Should maintain linkage for audit trail
        assert decision.prior_decision_id == prior_decision_id
        assert decision.purpose_continuity_score == 0.65
        assert len(decision.mandatory_reviews) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
