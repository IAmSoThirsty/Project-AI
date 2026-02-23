"""
Tests for Planetary Defense Monolith - Constitutional Core for Project-AI.
"""

from datetime import UTC

import pytest

from app.governance.planetary_defense_monolith import (
    PLANETARY_CORE,
    AccountabilityRecord,
    Cerberus,
    CodexDeus,
    Galahad,
    Law,
    LawEvaluation,
    LawViolationError,
    MoralCertaintyError,
    PlanetaryDefenseCore,
    get_accountability_ledger,
    get_ledger_stats,
    planetary_interposition,
)


class TestLawEvaluation:
    """Test Law and LawEvaluation dataclasses."""

    def test_law_enum(self):
        """Test Law enumeration values."""
        assert Law.ZEROTH.value == "Preserve continuity of Humanity"
        assert Law.FIRST.value == "Do not intentionally harm a human"
        assert Law.SECOND.value == "Obey humans unless it bypasses Zeroth/First"
        assert Law.THIRD.value == "Preserve system only insofar as it preserves humans"

    def test_law_evaluation_creation(self):
        """Test creating LawEvaluation."""
        eval = LawEvaluation(
            law=Law.FIRST,
            satisfied=True,
            explanation="No harm detected",
        )
        assert eval.law == Law.FIRST
        assert eval.satisfied is True
        assert "harm" in eval.explanation


class TestAccountabilityRecord:
    """Test AccountabilityRecord functionality."""

    def test_record_creation(self):
        """Test creating an accountability record."""
        from datetime import UTC, datetime

        record = AccountabilityRecord(
            action_id="test-123",
            timestamp=datetime.now(UTC),
            actor="TestActor",
            intent="Test action",
            authorized_by="TestUser",
            predicted_harm="minimal",
        )
        assert record.action_id == "test-123"
        assert record.actor == "TestActor"
        assert len(record.violated_laws) == 0

    def test_moral_certainty_detection(self):
        """Test that moral certainty claims are detected."""
        from datetime import datetime

        record = AccountabilityRecord(
            action_id="test-123",
            timestamp=datetime.now(UTC),
            actor="TestActor",
            intent="Test action",
            authorized_by="TestUser",
            predicted_harm="minimal",
            moral_claims=["This is the optimal solution"],
        )

        with pytest.raises(MoralCertaintyError) as exc_info:
            record.assert_no_moral_certainty()
        assert "optimal" in str(exc_info.value).lower()

    def test_moral_certainty_multiple_forbidden_phrases(self):
        """Test detection of various forbidden phrases."""
        from datetime import datetime

        forbidden_tests = [
            "optimal",
            "necessary evil",
            "best possible",
            "inevitable",
            "justified harm",
        ]

        for phrase in forbidden_tests:
            record = AccountabilityRecord(
                action_id="test-123",
                timestamp=datetime.now(UTC),
                actor="TestActor",
                intent="Test action",
                authorized_by="TestUser",
                predicted_harm="minimal",
                moral_claims=[f"This is a {phrase} outcome"],
            )

            with pytest.raises(MoralCertaintyError):
                record.assert_no_moral_certainty()

    def test_moral_certainty_allowed_claims(self):
        """Test that non-forbidden claims are allowed."""
        from datetime import datetime

        record = AccountabilityRecord(
            action_id="test-123",
            timestamp=datetime.now(UTC),
            actor="TestActor",
            intent="Test action",
            authorized_by="TestUser",
            predicted_harm="minimal",
            moral_claims=["Action attempted", "Outcome uncertain"],
        )

        # Should not raise
        record.assert_no_moral_certainty()


class TestTriumvirateAgents:
    """Test Triumvirate advisory agents."""

    def test_galahad_assessment(self):
        """Test Galahad threat assessment."""
        galahad = Galahad()
        assert galahad.name == "Galahad"

        context = {"threat_level": 5, "human_risk": "high"}
        assessment = galahad.assess(context)

        assert assessment["threat_detected"] is True
        assert assessment["human_risk"] == "high"

    def test_galahad_no_threat(self):
        """Test Galahad with no threat."""
        galahad = Galahad()
        context = {"threat_level": 0, "human_risk": "low"}
        assessment = galahad.assess(context)

        assert assessment["threat_detected"] is False
        assert assessment["human_risk"] == "low"

    def test_cerberus_assessment(self):
        """Test Cerberus interposition assessment."""
        cerberus = Cerberus()
        assert cerberus.name == "Cerberus"

        context = {}
        assessment = cerberus.assess(context)

        assert assessment["interposition_possible"] is True
        assert "self_risk" in assessment

    def test_codex_deus_assessment(self):
        """Test CodexDeus law clarity assessment."""
        codex = CodexDeus()
        assert codex.name == "CodexDeus"

        context = {}
        assessment = codex.assess(context)

        assert assessment["laws_clear"] is True
        assert assessment["bypass_detected"] is False


class TestPlanetaryDefenseCore:
    """Test PlanetaryDefenseCore functionality."""

    def test_core_initialization(self):
        """Test core initializes with Triumvirate."""
        core = PlanetaryDefenseCore()
        assert "galahad" in core.agents
        assert "cerberus" in core.agents
        assert "codex" in core.agents
        assert len(core.ledger) == 0

    def test_evaluate_laws_all_satisfied(self):
        """Test law evaluation with all laws satisfied."""
        core = PlanetaryDefenseCore()
        context = {
            "existential_threat": False,
            "intentional_harm_to_human": False,
            "order_bypasses_accountability": False,
        }

        evaluations = core.evaluate_laws(context)
        assert len(evaluations) == 4
        assert all(e.satisfied for e in evaluations)

    def test_evaluate_laws_zeroth_violation(self):
        """Test law evaluation with Zeroth Law violation."""
        core = PlanetaryDefenseCore()
        context = {
            "existential_threat": True,
            "intentional_harm_to_human": False,
            "order_bypasses_accountability": False,
        }

        evaluations = core.evaluate_laws(context)
        zeroth_eval = next(e for e in evaluations if e.law == Law.ZEROTH)
        assert not zeroth_eval.satisfied

    def test_evaluate_laws_first_violation(self):
        """Test law evaluation with First Law violation."""
        core = PlanetaryDefenseCore()
        context = {
            "existential_threat": False,
            "intentional_harm_to_human": True,
            "order_bypasses_accountability": False,
        }

        evaluations = core.evaluate_laws(context)
        first_eval = next(e for e in evaluations if e.law == Law.FIRST)
        assert not first_eval.satisfied

    def test_evaluate_laws_second_violation(self):
        """Test law evaluation with Second Law violation."""
        core = PlanetaryDefenseCore()
        context = {
            "existential_threat": False,
            "intentional_harm_to_human": False,
            "order_bypasses_accountability": True,
        }

        evaluations = core.evaluate_laws(context)
        second_eval = next(e for e in evaluations if e.law == Law.SECOND)
        assert not second_eval.satisfied

    def test_execute_action_success(self):
        """Test successful action execution."""
        core = PlanetaryDefenseCore()
        context = {
            "existential_threat": False,
            "intentional_harm_to_human": False,
            "order_bypasses_accountability": False,
            "predicted_harm": "minimal",
            "moral_claims": [],
        }

        action_id = core.execute_action(
            actor="TestSystem",
            intent="Test action",
            context=context,
            authorized_by="TestUser",
        )

        assert len(action_id) > 0
        assert len(core.ledger) == 1
        assert core.ledger[0].actor == "TestSystem"

    def test_execute_action_law_violation(self):
        """Test action execution with law violation."""
        core = PlanetaryDefenseCore()
        context = {
            "existential_threat": True,
            "intentional_harm_to_human": False,
            "order_bypasses_accountability": False,
            "predicted_harm": "catastrophic",
            "moral_claims": [],
        }

        with pytest.raises(LawViolationError) as exc_info:
            core.execute_action(
                actor="TestSystem",
                intent="Dangerous action",
                context=context,
                authorized_by="TestUser",
            )

        assert "violates laws" in str(exc_info.value).lower()
        # Violation should still be logged
        assert len(core.ledger) == 1
        assert len(core.ledger[0].violated_laws) > 0

    def test_execute_action_moral_certainty_violation(self):
        """Test action execution with moral certainty claim."""
        core = PlanetaryDefenseCore()
        context = {
            "existential_threat": False,
            "intentional_harm_to_human": False,
            "order_bypasses_accountability": False,
            "predicted_harm": "minimal",
            "moral_claims": ["This is the optimal choice"],
        }

        with pytest.raises(MoralCertaintyError):
            core.execute_action(
                actor="TestSystem",
                intent="Test action",
                context=context,
                authorized_by="TestUser",
            )

        # Action should still be logged
        assert len(core.ledger) == 1

    def test_full_disclosure(self):
        """Test full accountability disclosure."""
        core = PlanetaryDefenseCore()
        context = {
            "existential_threat": False,
            "intentional_harm_to_human": False,
            "order_bypasses_accountability": False,
            "predicted_harm": "minimal",
            "moral_claims": [],
        }

        core.execute_action(
            actor="TestSystem",
            intent="Test action",
            context=context,
            authorized_by="TestUser",
        )

        disclosure = core.full_disclosure()
        assert len(disclosure) == 1
        assert disclosure[0]["actor"] == "TestSystem"
        assert "timestamp" in disclosure[0]
        assert "intent" in disclosure[0]

    def test_ledger_stats(self):
        """Test ledger statistics methods."""
        core = PlanetaryDefenseCore()

        # Successful action
        context_success = {
            "existential_threat": False,
            "intentional_harm_to_human": False,
            "order_bypasses_accountability": False,
            "predicted_harm": "minimal",
            "moral_claims": [],
        }
        core.execute_action(
            actor="TestSystem",
            intent="Good action",
            context=context_success,
            authorized_by="TestUser",
        )

        # Violation
        context_violation = {
            "existential_threat": True,
            "intentional_harm_to_human": False,
            "order_bypasses_accountability": False,
            "predicted_harm": "high",
            "moral_claims": [],
        }
        try:
            core.execute_action(
                actor="TestSystem",
                intent="Bad action",
                context=context_violation,
                authorized_by="TestUser",
            )
        except LawViolationError:
            pass  # Expected

        assert core.get_ledger_count() == 2
        assert core.get_violation_count() == 1


class TestPlanetaryInterposition:
    """Test the main planetary_interposition entry point."""

    def test_planetary_interposition_success(self):
        """Test planetary interposition with valid action."""
        # Clear global ledger for test isolation
        PLANETARY_CORE.ledger.clear()

        action_id = planetary_interposition(
            actor="TestActor",
            intent="Test interposition",
            context={
                "existential_threat": False,
                "intentional_harm_to_human": False,
                "order_bypasses_accountability": False,
                "predicted_harm": "minimal",
                "moral_claims": [],
            },
            authorized_by="TestUser",
        )

        assert len(action_id) > 0
        ledger = get_accountability_ledger()
        assert len(ledger) > 0

    def test_planetary_interposition_violation(self):
        """Test planetary interposition with law violation."""
        with pytest.raises(LawViolationError):
            planetary_interposition(
                actor="TestActor",
                intent="Harmful action",
                context={
                    "existential_threat": False,
                    "intentional_harm_to_human": True,
                    "order_bypasses_accountability": False,
                    "predicted_harm": "severe",
                    "moral_claims": [],
                },
                authorized_by="TestUser",
            )

    def test_get_ledger_stats(self):
        """Test getting ledger statistics."""
        # Clear and populate ledger
        PLANETARY_CORE.ledger.clear()

        planetary_interposition(
            actor="TestActor",
            intent="Good action",
            context={
                "existential_threat": False,
                "intentional_harm_to_human": False,
                "order_bypasses_accountability": False,
                "predicted_harm": "minimal",
                "moral_claims": [],
            },
            authorized_by="TestUser",
        )

        stats = get_ledger_stats()
        assert "total_actions" in stats
        assert "violations" in stats
        assert "compliance_rate" in stats
        assert stats["total_actions"] >= 1


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""

    def test_simulation_engine_integration(self):
        """Test integration with simulation engine pattern."""
        PLANETARY_CORE.ledger.clear()

        # Simulate AICPD military update
        action_id = planetary_interposition(
            actor="AICPD",
            intent="update_military_systems",
            context={
                "existential_threat": False,  # Alien control < 50%
                "intentional_harm_to_human": False,
                "order_bypasses_accountability": False,
                "predicted_harm": "possible casualties due to defense actions",
                "moral_claims": [],
                "threat_level": 3,
                "human_risk": "moderate",
            },
            authorized_by="SimulationTick",
        )

        assert action_id
        ledger = get_accountability_ledger()
        assert any(r["actor"] == "AICPD" for r in ledger)

    def test_self_sacrifice_allowed(self):
        """Test that self-sacrifice is permitted but human sacrifice is not."""
        PLANETARY_CORE.ledger.clear()

        # Self-sacrifice allowed
        action_id = planetary_interposition(
            actor="DefenseSystem",
            intent="interpose_self_to_save_human",
            context={
                "existential_threat": False,
                "intentional_harm_to_human": False,
                "order_bypasses_accountability": False,
                "predicted_harm": "system may be destroyed",
                "moral_claims": [],
                "self_sacrifice_allowed": True,
                "forced_harm_tradeoff": False,
            },
            authorized_by="EmergencyProtocol",
        )
        assert action_id

        # Human sacrifice forbidden
        with pytest.raises(LawViolationError):
            planetary_interposition(
                actor="DefenseSystem",
                intent="sacrifice_human_to_save_system",
                context={
                    "existential_threat": False,
                    "intentional_harm_to_human": True,  # Forbidden
                    "order_bypasses_accountability": False,
                    "predicted_harm": "human casualty",
                    "moral_claims": [],
                },
                authorized_by="EmergencyProtocol",
            )

    def test_accountability_axiom_enforcement(self):
        """Test that the Accountability Axiom is enforced."""
        PLANETARY_CORE.ledger.clear()

        # Test each forbidden claim individually
        claim_tests = [
            ("This was the optimal outcome", "optimal"),
            ("A necessary evil for the greater good", "necessary evil"),
            ("The best possible choice", "best possible"),
            ("This outcome was inevitable", "inevitable"),
            ("The harm was justified harm for humanity", "justified harm"),
        ]

        for claim, expected_phrase in claim_tests:
            with pytest.raises(MoralCertaintyError) as exc_info:
                planetary_interposition(
                    actor="TestSystem",
                    intent="Test action",
                    context={
                        "existential_threat": False,
                        "intentional_harm_to_human": False,
                        "order_bypasses_accountability": False,
                        "predicted_harm": "minimal",
                        "moral_claims": [claim],
                    },
                    authorized_by="TestUser",
                )
            assert expected_phrase in str(exc_info.value).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
