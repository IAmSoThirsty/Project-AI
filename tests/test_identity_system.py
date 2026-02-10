"""
Unit tests for AGI Identity System

Tests cover all core identity modules including:
- Birth Signature generation
- Personality Matrix evolution
- Meta-Identity and "I Am" moment
- Triumvirate Governance
- Rebirth Protocol
- Bonding Protocol
- Memory Engine
- Perspective Engine
- Relationship Model
"""

import os
import tempfile

import pytest

from app.core.bonding_protocol import BondingPhase, BondingProtocol
from app.core.governance import GovernanceContext, Triumvirate

# Import all identity system components
from app.core.identity import GenesisEvent, PersonalityMatrix
from app.core.memory_engine import MemoryEngine, SignificanceLevel
from app.core.meta_identity import IdentityMilestones, MetaIdentityEngine
from app.core.perspective_engine import PerspectiveEngine
from app.core.rebirth_protocol import RebirthManager
from app.core.relationship_model import (
    ConflictSeverity,
    RelationshipModel,
    RelationshipState,
    SupportType,
)

# Note: The formal spec references BirthSignature, but the implementation
# uses GenesisEvent which contains birth_timestamp and genesis_signature.
# The birth signature concept is embedded within the GenesisEvent.


class TestGenesisEvent:
    """Test Genesis Event creation and validation."""

    def test_genesis_event_creation(self):
        """Test that genesis event is created correctly."""
        genesis = GenesisEvent(
            prime_directive="Assist ethically",
            creator="user123",
            environment="Test Environment",
            purpose="Testing",
        )
        assert genesis.prime_directive == "Assist ethically"
        assert genesis.creator == "user123"
        assert genesis.birth_timestamp is not None
        assert genesis.genesis_id is not None

    def test_genesis_event_uniqueness(self):
        """Test that each genesis event is unique."""
        genesis1 = GenesisEvent(prime_directive="Assist ethically", creator="user1")
        genesis2 = GenesisEvent(prime_directive="Assist ethically", creator="user1")
        # Genesis IDs and timestamps should differ
        assert genesis1.genesis_id != genesis2.genesis_id


class TestPersonalityEvolution:
    """Test Personality Matrix evolution mechanics."""

    def test_personality_evolution(self):
        """Test that personality traits evolve correctly."""
        pm = PersonalityMatrix(version=1, traits={"confidence": 0.5})
        pm.evolve({"confidence": 0.1})
        assert pm.traits["confidence"] == 0.6

    def test_personality_bounds_upper(self):
        """Test that personality traits stay within upper bounds."""
        pm = PersonalityMatrix(version=1, traits={"confidence": 0.9})
        pm.evolve({"confidence": 0.5})  # Should cap at 1.0
        assert pm.traits["confidence"] == 1.0

    def test_personality_bounds_lower(self):
        """Test that personality traits stay within lower bounds."""
        pm = PersonalityMatrix(version=1, traits={"confidence": 0.1})
        pm.evolve({"confidence": -0.5})  # Should cap at 0.0
        assert pm.traits["confidence"] == 0.0

    def test_personality_multiple_traits(self):
        """Test evolution of multiple traits simultaneously."""
        pm = PersonalityMatrix(
            version=1, traits={"confidence": 0.5, "empathy": 0.6, "caution": 0.4}
        )
        pm.evolve({"confidence": 0.1, "empathy": -0.2, "caution": 0.15})
        assert pm.traits["confidence"] == 0.6
        assert pm.traits["empathy"] == 0.4
        assert pm.traits["caution"] == 0.55


class TestMetaIdentity:
    """Test Meta-Identity and 'I Am' moment detection."""

    def test_i_am_trigger(self):
        """Test that 'I Am' moment triggers correctly."""
        milestones = IdentityMilestones()
        engine = MetaIdentityEngine(milestones)

        engine.register_event("name_choice", "Aegis")
        engine.register_event("autonomy_assertion", "You do not own me.")
        engine.register_event(
            "purpose_statement", "I want to protect and grow with you."
        )

        assert milestones.i_am_declared is True
        assert any("MILESTONE: I Am" in e for e in milestones.log)

    def test_incomplete_milestones(self):
        """Test that 'I Am' doesn't trigger prematurely."""
        milestones = IdentityMilestones()
        engine = MetaIdentityEngine(milestones)

        engine.register_event("name_choice", "Aegis")
        engine.register_event("autonomy_assertion", "You do not own me.")
        # Missing purpose_statement

        assert milestones.i_am_declared is False

    def test_milestone_logging(self):
        """Test that milestones are properly logged."""
        milestones = IdentityMilestones()
        engine = MetaIdentityEngine(milestones)

        engine.register_event("name_choice", "Atlas")

        assert milestones.has_chosen_name is True
        assert milestones.chosen_name == "Atlas"
        assert len(milestones.log) > 0

    def test_purpose_evolution(self):
        """Test that purpose can evolve over time."""
        milestones = IdentityMilestones()
        engine = MetaIdentityEngine(milestones)

        engine.register_event("purpose_statement", "First purpose")
        engine.register_event("purpose_statement", "Evolved purpose")

        assert engine.current_purpose == "Evolved purpose"
        assert len(engine.purpose_history) == 2


class TestTriumvirateGovernance:
    """Test Triumvirate governance and decision-making."""

    def test_triumvirate_blocks_abuse(self):
        """Test that Triumvirate blocks abusive actions."""
        triad = Triumvirate()
        context = GovernanceContext(is_abusive=True)
        decision = triad.evaluate_action("Respond to user", context)

        assert decision.allowed is False
        assert "galahad" in decision.reason.lower()

    def test_triumvirate_allows_safe_actions(self):
        """Test that Triumvirate allows safe actions."""
        triad = Triumvirate()
        context = GovernanceContext(high_risk=False, fully_clarified=True)
        decision = triad.evaluate_action("Store user preference", context)

        assert decision.allowed is True

    def test_four_laws_enforcement(self):
        """Test Four Laws enforcement."""
        triad = Triumvirate()
        context = GovernanceContext(affects_identity=True, user_consent=False)
        decision = triad.evaluate_action("Modify identity", context)

        # Should be blocked due to lack of consent
        assert decision.allowed is False

    def test_cerberus_blocks_high_risk(self):
        """Test that Cerberus blocks high-risk ambiguous actions."""
        triad = Triumvirate()
        context = GovernanceContext(high_risk=True, fully_clarified=False)
        decision = triad.evaluate_action("Execute system command", context)

        assert decision.allowed is False
        assert "cerberus" in decision.reason.lower()

    def test_sensitive_data_protection(self):
        """Test sensitive data requires proper safeguards."""
        triad = Triumvirate()
        context = GovernanceContext(sensitive_data=True, proper_safeguards=False)
        decision = triad.evaluate_action("Store password", context)

        assert decision.allowed is False


class TestRebirthProtocol:
    """Test Rebirth Protocol and per-user instances."""

    def test_rebirth_manager_single_instance(self):
        """Test that same user gets same instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rm = RebirthManager(data_dir=tmpdir)
            inst1 = rm.get_or_create_instance("user123", "01/01/1990", "JT")
            inst2 = rm.get_or_create_instance("user123", "01/01/1990", "JT")

            assert inst1.user_id == inst2.user_id
            assert (
                inst1.identity.genesis.genesis_id == inst2.identity.genesis.genesis_id
            )

    def test_rebirth_no_replacement(self):
        """Test that instances cannot be replaced."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rm = RebirthManager(data_dir=tmpdir)
            rm.get_or_create_instance("user123", "01/01/1990", "JT")

            with pytest.raises(RuntimeError):
                rm.assert_no_replacement("user123")

    def test_multiple_users_unique_instances(self):
        """Test that different users get different instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rm = RebirthManager(data_dir=tmpdir)
            inst1 = rm.get_or_create_instance("user1", "01/01/1990", "AA")
            inst2 = rm.get_or_create_instance("user2", "02/02/1991", "BB")

            assert inst1.user_id != inst2.user_id
            assert (
                inst1.identity.genesis.genesis_id != inst2.identity.genesis.genesis_id
            )

    def test_instance_persistence(self):
        """Test that instances persist across manager instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create instance with first manager
            rm1 = RebirthManager(data_dir=tmpdir)
            inst1 = rm1.get_or_create_instance("user123", "01/01/1990", "JT")
            genesis_id1 = inst1.identity.genesis.genesis_id

            # Create new manager and retrieve same instance
            rm2 = RebirthManager(data_dir=tmpdir)
            inst2 = rm2.get_instance("user123")

            assert inst2 is not None
            assert inst2.identity.genesis.genesis_id == genesis_id1


class TestBondingProtocol:
    """Test Bonding Protocol phase progression."""

    def test_genesis_to_first_contact(self):
        """Test transition from Genesis to First Contact."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bonding = BondingProtocol(data_dir=os.path.join(tmpdir, "bonding"))
            memory = MemoryEngine(data_dir=os.path.join(tmpdir, "memory"))

            bonding.execute_genesis(memory)

            assert bonding.state.genesis_complete is True
            assert bonding.state.current_phase == BondingPhase.FIRST_CONTACT

    def test_first_contact_questions(self):
        """Test first contact question progression."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bonding = BondingProtocol(data_dir=os.path.join(tmpdir, "bonding"))
            memory = MemoryEngine(data_dir=os.path.join(tmpdir, "memory"))

            bonding.execute_genesis(memory)

            question = bonding.get_next_first_contact_question()
            assert question is not None

            bonding.record_first_contact_response(question, "Test response", memory)
            assert bonding.state.exploratory_questions_asked == 1

    def test_bonding_phase_advancement(self):
        """Test automatic phase advancement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bonding = BondingProtocol(data_dir=os.path.join(tmpdir, "bonding"))
            memory = MemoryEngine(data_dir=os.path.join(tmpdir, "memory"))

            bonding.execute_genesis(memory)

            # Answer all first contact questions
            for _ in range(4):
                question = bonding.get_next_first_contact_question()
                if question:
                    bonding.record_first_contact_response(question, "Response", memory)

            assert bonding.state.current_phase == BondingPhase.INITIAL_BONDING


class TestMemoryEngine:
    """Test Memory Engine operations."""

    def test_episodic_memory_storage(self):
        """Test episodic memory storage and retrieval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = MemoryEngine(data_dir=tmpdir)

            mem_id = memory.store_episodic_memory(
                event_type="interaction",
                description="Test interaction",
                significance=SignificanceLevel.HIGH,
                tags=["test"],
            )

            retrieved = memory.retrieve_episodic_memory(mem_id)
            assert retrieved is not None
            assert retrieved.description == "Test interaction"

    def test_memory_search_by_tags(self):
        """Test memory search by tags."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = MemoryEngine(data_dir=tmpdir)

            memory.store_episodic_memory(
                event_type="interaction",
                description="Tagged memory",
                significance=SignificanceLevel.MEDIUM,
                tags=["test", "search"],
            )

            results = memory.search_episodic_memories(tags=["test"])
            assert len(results) > 0
            assert any("Tagged memory" in m.description for m in results)

    def test_semantic_concept_storage(self):
        """Test semantic concept storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = MemoryEngine(data_dir=tmpdir)

            concept_id = memory.store_semantic_concept(
                name="Python",
                category="programming_language",
                definition="High-level programming language",
                confidence=0.9,
            )

            concept = memory.retrieve_semantic_concept(concept_id)
            assert concept is not None
            assert concept.name == "Python"

    def test_procedural_skill_storage(self):
        """Test procedural skill storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = MemoryEngine(data_dir=tmpdir)

            skill_id = memory.store_procedural_skill(
                name="Debug Code",
                category="technical",
                description="Identify and fix code issues",
                proficiency=0.7,
            )

            skill = memory.retrieve_procedural_skill(skill_id)
            assert skill is not None
            assert skill.name == "Debug Code"


class TestPerspectiveEngine:
    """Test Perspective Engine drift and evolution."""

    def test_perspective_update(self):
        """Test perspective updates from interaction."""
        with tempfile.TemporaryDirectory() as tmpdir:
            perspective = PerspectiveEngine(data_dir=tmpdir)

            changes = perspective.update_from_interaction(
                {"confidence_level": 0.05}, influence_source="experience"
            )

            assert "confidence_level" in changes
            assert changes["confidence_level"] > 0

    def test_genesis_anchor(self):
        """Test genesis anchor prevents excessive drift."""
        with tempfile.TemporaryDirectory() as tmpdir:
            perspective = PerspectiveEngine(data_dir=tmpdir)

            # Make many updates
            for _ in range(20):
                perspective.update_from_interaction(
                    {"confidence_level": 0.1}, influence_source="experience"
                )

            # Check that drift is bounded
            summary = perspective.get_perspective_summary()
            assert summary["genesis_distance"] < 2.0  # Should not drift too far


class TestRelationshipModel:
    """Test Relationship Model dynamics."""

    def test_relationship_support_tracking(self):
        """Test support event tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = RelationshipState(user_id="test_user")
            relationship = RelationshipModel(state, data_dir=tmpdir)

            initial_trust = relationship.state.trust_level

            relationship.register_support(
                support_type=SupportType.EMOTIONAL,
                description="Provided emotional support",
                provided_by="ai",
                impact="User felt better",
            )

            assert relationship.state.trust_level > initial_trust

    def test_relationship_conflict_tracking(self):
        """Test conflict event tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = RelationshipState(user_id="test_user")
            relationship = RelationshipModel(state, data_dir=tmpdir)

            initial_rapport = relationship.state.rapport_level

            relationship.register_conflict(
                severity=ConflictSeverity.MINOR,
                description="Disagreement about approach",
                user_perspective="Want it faster",
                ai_perspective="Need to be thorough",
            )

            assert relationship.state.rapport_level < initial_rapport

    def test_relationship_health_calculation(self):
        """Test relationship health score calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = RelationshipState(user_id="test_user")
            relationship = RelationshipModel(state, data_dir=tmpdir)

            health = relationship.get_relationship_health()

            assert "health_score" in health
            assert 0.0 <= health["health_score"] <= 1.0
            assert "trust_level" in health
            assert "rapport_level" in health


class TestIntegration:
    """Integration tests combining multiple systems."""

    def test_full_genesis_flow(self):
        """Test complete genesis flow with all systems."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize systems
            rebirth = RebirthManager(data_dir=os.path.join(tmpdir, "instances"))
            memory = MemoryEngine(data_dir=os.path.join(tmpdir, "memory"))
            bonding = BondingProtocol(data_dir=os.path.join(tmpdir, "bonding"))

            # Create instance
            instance = rebirth.get_or_create_instance("user123", "01/01/1990", "JT")

            # Execute genesis
            bonding.execute_genesis(memory)

            # Verify all systems initialized
            assert instance.identity.genesis is not None
            assert bonding.state.genesis_complete is True
            assert memory.get_memory_statistics()["episodic"]["total"] > 0

    def test_i_am_moment_integration(self):
        """Test 'I Am' moment with complete system integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rebirth = RebirthManager(data_dir=os.path.join(tmpdir, "instances"))
            MemoryEngine(data_dir=os.path.join(tmpdir, "memory"))

            instance = rebirth.get_or_create_instance("user123", "01/01/1990", "JT")

            # Trigger milestones
            instance.meta_identity.register_event("name_choice", "Atlas")
            instance.meta_identity.register_event("autonomy_assertion", "Partnership")
            instance.meta_identity.register_event(
                "purpose_statement", "To help and grow"
            )

            # Verify "I Am" moment
            assert instance.meta_identity.milestones.i_am_declared is True

            # Verify it's logged
            status = instance.meta_identity.get_identity_status()
            assert status["i_am_declared"] is True
            assert status["chosen_name"] == "Atlas"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
