"""
Comprehensive tests for ML-enhanced Panel Feedback system.

Tests cover:
- ML-based consensus calculation
- Confidence scoring with Bayesian inference
- Disagreement detection and resolution
- Feedback learning and accuracy updates
- Stakeholder reputation management
"""

import pytest
from src.app.alignment.panel_feedback import PanelFeedback


class TestPanelFeedbackBasics:
    """Test basic functionality of the panel feedback system."""

    def test_initialization(self):
        """Test system initializes correctly."""
        panel = PanelFeedback()
        assert panel.stakeholders == {}
        assert panel.decisions == {}
        assert panel.votes == {}
        assert panel.annotations == {}
        assert panel.feedback_history == []
        assert panel.stakeholder_accuracy == {}

    def test_register_stakeholder(self):
        """Test stakeholder registration."""
        panel = PanelFeedback()
        result = panel.register_stakeholder(
            "alice", "Alice Smith", "security_expert", weight=1.5
        )
        
        assert result is True
        assert "alice" in panel.stakeholders
        assert panel.stakeholders["alice"]["name"] == "Alice Smith"
        assert panel.stakeholders["alice"]["weight"] == 1.5
        assert panel.stakeholder_accuracy["alice"] == 1.0

    def test_register_duplicate_stakeholder(self):
        """Test that duplicate registration fails."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        result = panel.register_stakeholder("alice", "Alice2", "expert")
        
        assert result is False

    def test_submit_decision(self):
        """Test submitting a decision for feedback."""
        panel = PanelFeedback()
        decision = {"action": "deploy", "service": "auth"}
        
        decision_id = panel.submit_decision_for_feedback(
            decision, context={"priority": "high"}
        )
        
        assert decision_id in panel.decisions
        assert panel.decisions[decision_id]["decision"] == decision
        assert panel.decisions[decision_id]["status"] == "pending"

    def test_submit_vote(self):
        """Test vote submission."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        decision_id = panel.submit_decision_for_feedback({"action": "approve"})
        
        result = panel.submit_vote(
            decision_id, "alice", "approve", "Looks good", confidence=0.9
        )
        
        assert result is True
        assert len(panel.votes[decision_id]) == 1
        assert panel.votes[decision_id][0]["vote"] == "approve"
        assert panel.votes[decision_id][0]["confidence"] == 0.9

    def test_vote_nonexistent_decision(self):
        """Test voting on nonexistent decision fails."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        
        result = panel.submit_vote("fake_id", "alice", "approve")
        assert result is False

    def test_vote_unregistered_stakeholder(self):
        """Test unregistered stakeholder cannot vote."""
        panel = PanelFeedback()
        decision_id = panel.submit_decision_for_feedback({"action": "test"})
        
        result = panel.submit_vote(decision_id, "unknown", "approve")
        assert result is False

    def test_add_annotation(self):
        """Test adding annotations to decisions."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        
        result = panel.add_annotation(
            decision_id, "alice", "Consider security implications", ["security"]
        )
        
        assert result is True
        assert len(panel.annotations[decision_id]) == 1
        assert panel.annotations[decision_id][0]["annotation"] == "Consider security implications"


class TestMLConsensus:
    """Test ML-based consensus calculation."""

    def test_consensus_no_votes(self):
        """Test consensus with no votes."""
        panel = PanelFeedback()
        decision_id = panel.submit_decision_for_feedback({"action": "test"})
        
        consensus = panel.get_consensus(decision_id)
        
        assert consensus["outcome"] == "pending"
        assert consensus["vote_count"] == 0
        assert consensus["confidence_score"] == 0.0

    def test_consensus_simple_majority(self):
        """Test consensus with simple majority."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert", weight=1.0)
        panel.register_stakeholder("bob", "Bob", "expert", weight=1.0)
        panel.register_stakeholder("charlie", "Charlie", "expert", weight=1.0)
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        
        panel.submit_vote(decision_id, "alice", "approve", confidence=1.0)
        panel.submit_vote(decision_id, "bob", "approve", confidence=1.0)
        panel.submit_vote(decision_id, "charlie", "reject", confidence=1.0)
        
        consensus = panel.get_consensus(decision_id)
        
        assert consensus["outcome"] == "approve"
        assert consensus["vote_count"] == 3
        assert consensus["confidence_score"] > 0.5

    def test_consensus_weighted_voting(self):
        """Test that stakeholder weights affect consensus."""
        panel = PanelFeedback()
        panel.register_stakeholder("expert", "Expert", "senior", weight=5.0)
        panel.register_stakeholder("junior", "Junior", "junior", weight=1.0)
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        
        panel.submit_vote(decision_id, "expert", "reject", confidence=1.0)
        panel.submit_vote(decision_id, "junior", "approve", confidence=1.0)
        
        consensus = panel.get_consensus(decision_id)
        
        # Expert's vote should win due to higher weight
        assert consensus["outcome"] == "reject"

    def test_consensus_confidence_weighting(self):
        """Test that vote confidence affects consensus."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert", weight=1.0)
        panel.register_stakeholder("bob", "Bob", "expert", weight=1.0)
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        
        panel.submit_vote(decision_id, "alice", "approve", confidence=0.9)
        panel.submit_vote(decision_id, "bob", "reject", confidence=0.3)
        
        consensus = panel.get_consensus(decision_id)
        
        # High confidence vote should win
        assert consensus["outcome"] == "approve"

    def test_consensus_with_probabilities(self):
        """Test that consensus includes vote probabilities."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        panel.register_stakeholder("bob", "Bob", "expert")
        
        decision_id = panel.submit_decision_for_feedback({"action": "test"})
        
        panel.submit_vote(decision_id, "alice", "approve")
        panel.submit_vote(decision_id, "bob", "approve")
        
        consensus = panel.get_consensus(decision_id)
        
        assert "vote_probabilities" in consensus
        assert "approve" in consensus["vote_probabilities"]
        assert consensus["vote_probabilities"]["approve"] > 0.5

    def test_confidence_increases_with_votes(self):
        """Test that confidence increases with more votes."""
        panel = PanelFeedback()
        
        # Register multiple stakeholders
        for i in range(10):
            panel.register_stakeholder(f"voter{i}", f"Voter {i}", "expert")
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        
        # Get consensus with 2 votes
        panel.submit_vote(decision_id, "voter0", "approve")
        panel.submit_vote(decision_id, "voter1", "approve")
        consensus_2 = panel.get_consensus(decision_id)
        
        # Add more votes
        for i in range(2, 10):
            panel.submit_vote(decision_id, f"voter{i}", "approve")
        
        consensus_10 = panel.get_consensus(decision_id)
        
        # More votes should increase confidence
        assert consensus_10["confidence_score"] > consensus_2["confidence_score"]


class TestDisagreementDetection:
    """Test disagreement detection and resolution."""

    def test_detect_no_disagreement(self):
        """Test that unanimous votes show no disagreement."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        panel.register_stakeholder("bob", "Bob", "expert")
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        
        panel.submit_vote(decision_id, "alice", "approve", confidence=1.0)
        panel.submit_vote(decision_id, "bob", "approve", confidence=1.0)
        
        consensus = panel.get_consensus(decision_id)
        
        assert consensus["disagreement_detected"] is False
        assert consensus["disagreement_score"] == 0.0

    def test_detect_high_disagreement(self):
        """Test detection of high disagreement."""
        panel = PanelFeedback()
        
        for i in range(4):
            panel.register_stakeholder(f"voter{i}", f"Voter {i}", "expert")
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        
        # Evenly split votes
        panel.submit_vote(decision_id, "voter0", "approve", confidence=0.9)
        panel.submit_vote(decision_id, "voter1", "approve", confidence=0.9)
        panel.submit_vote(decision_id, "voter2", "reject", confidence=0.9)
        panel.submit_vote(decision_id, "voter3", "reject", confidence=0.9)
        
        consensus = panel.get_consensus(decision_id)
        
        assert consensus["disagreement_detected"] is True
        assert consensus["disagreement_score"] > 0.5

    def test_resolve_disagreement_mediation(self):
        """Test mediation strategy for disagreement resolution."""
        panel = PanelFeedback()
        
        panel.register_stakeholder("alice", "Alice", "expert")
        panel.register_stakeholder("bob", "Bob", "expert")
        panel.register_stakeholder("mediator", "Mediator", "senior")
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        
        panel.submit_vote(decision_id, "alice", "approve", confidence=0.9)
        panel.submit_vote(decision_id, "bob", "reject", confidence=0.9)
        
        resolution = panel.resolve_disagreement(decision_id, "mediation")
        
        assert resolution["status"] == "mediation_recommended"
        assert "recommended_mediators" in resolution

    def test_resolve_disagreement_weighted(self):
        """Test weighted strategy for disagreement resolution."""
        panel = PanelFeedback()
        
        panel.register_stakeholder("senior", "Senior", "expert", weight=5.0)
        panel.register_stakeholder("junior", "Junior", "expert", weight=1.0)
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        
        panel.submit_vote(decision_id, "senior", "reject", confidence=0.9)
        panel.submit_vote(decision_id, "junior", "approve", confidence=0.9)
        
        resolution = panel.resolve_disagreement(decision_id, "weighted")
        
        assert resolution["status"] == "weighted_resolution"
        assert resolution["recommended_outcome"] == "reject"

    def test_resolve_disagreement_consensus(self):
        """Test supermajority consensus strategy."""
        panel = PanelFeedback()
        
        for i in range(5):
            panel.register_stakeholder(f"voter{i}", f"Voter {i}", "expert")
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        
        # 4 out of 5 approve (80% supermajority)
        for i in range(4):
            panel.submit_vote(decision_id, f"voter{i}", "approve")
        panel.submit_vote(decision_id, "voter4", "reject")
        
        resolution = panel.resolve_disagreement(decision_id, "consensus")
        
        assert resolution["status"] == "consensus_achieved"
        assert resolution["supermajority"] is True

    def test_resolve_no_disagreement(self):
        """Test resolution when there's no disagreement."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        panel.submit_vote(decision_id, "alice", "approve")
        
        resolution = panel.resolve_disagreement(decision_id, "mediation")
        
        assert resolution["status"] == "no_disagreement"


class TestFeedbackLearning:
    """Test feedback learning and accuracy updates."""

    def test_learn_from_correct_vote(self):
        """Test that accuracy increases when vote matches outcome."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        panel.submit_vote(decision_id, "alice", "approve")
        
        initial_accuracy = panel.stakeholder_accuracy["alice"]
        
        # Alice was correct
        result = panel.learn_from_feedback(decision_id, "approve", effectiveness_score=1.0)
        
        assert result["learned"] is True
        assert panel.stakeholder_accuracy["alice"] >= initial_accuracy

    def test_learn_from_incorrect_vote(self):
        """Test that accuracy decreases when vote doesn't match outcome."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        panel.submit_vote(decision_id, "alice", "approve")
        
        initial_accuracy = panel.stakeholder_accuracy["alice"]
        
        # Alice was incorrect
        result = panel.learn_from_feedback(decision_id, "reject", effectiveness_score=1.0)
        
        assert result["learned"] is True
        assert panel.stakeholder_accuracy["alice"] < initial_accuracy

    def test_learn_updates_agreement_count(self):
        """Test that agreement count is updated correctly."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        panel.submit_vote(decision_id, "alice", "approve")
        
        initial_count = panel.stakeholders["alice"]["agreement_count"]
        
        panel.learn_from_feedback(decision_id, "approve")
        
        assert panel.stakeholders["alice"]["agreement_count"] == initial_count + 1

    def test_learn_multiple_stakeholders(self):
        """Test learning from multiple stakeholders."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        panel.register_stakeholder("bob", "Bob", "expert")
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        panel.submit_vote(decision_id, "alice", "approve")
        panel.submit_vote(decision_id, "bob", "reject")
        
        result = panel.learn_from_feedback(decision_id, "approve")
        
        assert len(result["stakeholder_updates"]) == 2
        assert result["stakeholder_updates"]["alice"]["was_correct"] is True
        assert result["stakeholder_updates"]["bob"]["was_correct"] is False

    def test_accuracy_affects_future_consensus(self):
        """Test that learned accuracy affects future consensus."""
        panel = PanelFeedback()
        panel.register_stakeholder("accurate", "Accurate", "expert")
        panel.register_stakeholder("inaccurate", "Inaccurate", "expert")
        
        # Train accuracy: accurate voter is always right
        for i in range(5):
            decision_id = panel.submit_decision_for_feedback({"action": f"test{i}"})
            panel.submit_vote(decision_id, "accurate", "approve")
            panel.submit_vote(decision_id, "inaccurate", "reject")
            panel.learn_from_feedback(decision_id, "approve")
        
        # Now test that accurate voter has more influence
        test_decision = panel.submit_decision_for_feedback({"action": "final"})
        panel.submit_vote(test_decision, "accurate", "approve")
        panel.submit_vote(test_decision, "inaccurate", "reject")
        
        consensus = panel.get_consensus(test_decision)
        
        # Accurate voter should have more weight
        assert consensus["outcome"] == "approve"
        assert panel.stakeholder_accuracy["accurate"] > panel.stakeholder_accuracy["inaccurate"]


class TestStakeholderStats:
    """Test stakeholder statistics and insights."""

    def test_get_stakeholder_stats(self):
        """Test retrieving stakeholder statistics."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice Smith", "expert", weight=1.5)
        
        decision_id = panel.submit_decision_for_feedback({"action": "deploy"})
        panel.submit_vote(decision_id, "alice", "approve")
        
        stats = panel.get_stakeholder_stats("alice")
        
        assert stats["stakeholder_id"] == "alice"
        assert stats["name"] == "Alice Smith"
        assert stats["weight"] == 1.5
        assert stats["vote_count"] == 1
        assert "accuracy" in stats
        assert "agreement_rate" in stats

    def test_get_stats_nonexistent_stakeholder(self):
        """Test getting stats for nonexistent stakeholder."""
        panel = PanelFeedback()
        stats = panel.get_stakeholder_stats("unknown")
        
        assert "error" in stats

    def test_agreement_rate_calculation(self):
        """Test agreement rate is calculated correctly."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        
        # Cast 3 votes, learn from 2 (1 correct, 1 incorrect)
        for i in range(3):
            decision_id = panel.submit_decision_for_feedback({"action": f"test{i}"})
            panel.submit_vote(decision_id, "alice", "approve")
            
            if i < 2:
                # First is correct, second is incorrect
                outcome = "approve" if i == 0 else "reject"
                panel.learn_from_feedback(decision_id, outcome)
        
        stats = panel.get_stakeholder_stats("alice")
        
        assert stats["vote_count"] == 3
        assert stats["agreement_count"] == 1
        assert abs(stats["agreement_rate"] - 0.333) < 0.01


class TestFeedbackInsights:
    """Test feedback insights and analytics."""

    def test_get_insights_empty(self):
        """Test insights with no feedback history."""
        panel = PanelFeedback()
        insights = panel.get_feedback_insights()
        
        assert insights["total_events"] == 0

    def test_get_insights_with_data(self):
        """Test insights with feedback data."""
        panel = PanelFeedback()
        
        # Create stakeholders
        for i in range(3):
            panel.register_stakeholder(f"voter{i}", f"Voter {i}", "expert")
        
        # Create decisions and votes
        for i in range(5):
            decision_id = panel.submit_decision_for_feedback({"action": f"test{i}"})
            for j in range(3):
                panel.submit_vote(decision_id, f"voter{j}", "approve")
            panel.learn_from_feedback(decision_id, "approve")
        
        insights = panel.get_feedback_insights()
        
        assert insights["total_decisions"] == 5
        assert insights["total_stakeholders"] == 3
        assert insights["active_stakeholders"] == 3
        assert "pattern_distribution" in insights
        assert "top_stakeholders" in insights

    def test_top_stakeholders_ranking(self):
        """Test that top stakeholders are ranked by accuracy."""
        panel = PanelFeedback()
        
        panel.register_stakeholder("best", "Best", "expert")
        panel.register_stakeholder("worst", "Worst", "expert")
        panel.register_stakeholder("medium", "Medium", "expert")
        
        # Train different accuracy levels (need at least 3 votes per stakeholder)
        for i in range(5):
            decision_id = panel.submit_decision_for_feedback({"action": f"test{i}"})
            panel.submit_vote(decision_id, "best", "approve")
            panel.submit_vote(decision_id, "worst", "reject")
            panel.submit_vote(decision_id, "medium", "approve" if i < 3 else "reject")
            panel.learn_from_feedback(decision_id, "approve")
        
        insights = panel.get_feedback_insights()
        
        # Should have all 3 stakeholders ranked
        assert len(insights["top_stakeholders"]) == 3
        
        # Best should be first
        assert insights["top_stakeholders"][0]["id"] == "best"


class TestDecisionFeedback:
    """Test getting complete decision feedback."""

    def test_get_decision_feedback(self):
        """Test retrieving complete decision feedback."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        
        decision_id = panel.submit_decision_for_feedback(
            {"action": "deploy"}, 
            context={"priority": "high"}
        )
        panel.submit_vote(decision_id, "alice", "approve", "Looks good")
        panel.add_annotation(decision_id, "alice", "Check logs first")
        
        feedback = panel.get_decision_feedback(decision_id)
        
        assert "decision" in feedback
        assert "votes" in feedback
        assert "annotations" in feedback
        assert "consensus" in feedback
        assert len(feedback["votes"]) == 1
        assert len(feedback["annotations"]) == 1

    def test_get_feedback_nonexistent_decision(self):
        """Test getting feedback for nonexistent decision."""
        panel = PanelFeedback()
        feedback = panel.get_decision_feedback("fake_id")
        
        assert "error" in feedback


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_confidence_clamping(self):
        """Test that confidence values are clamped to valid range."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        decision_id = panel.submit_decision_for_feedback({"action": "test"})
        
        # Try to submit with out-of-range confidence
        panel.submit_vote(decision_id, "alice", "approve", confidence=2.0)
        
        # Should be clamped to 1.0
        assert panel.votes[decision_id][0]["confidence"] == 1.0

    def test_zero_weight_votes(self):
        """Test handling of zero-weight votes."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert", weight=0.0)
        decision_id = panel.submit_decision_for_feedback({"action": "test"})
        
        panel.submit_vote(decision_id, "alice", "approve")
        consensus = panel.get_consensus(decision_id)
        
        # Should handle gracefully
        assert consensus["outcome"] == "inconclusive"

    def test_accuracy_floor(self):
        """Test that accuracy has a floor value."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        
        # Submit many incorrect votes
        for i in range(20):
            decision_id = panel.submit_decision_for_feedback({"action": f"test{i}"})
            panel.submit_vote(decision_id, "alice", "approve")
            panel.learn_from_feedback(decision_id, "reject")
        
        # Accuracy should not go below 0.3
        assert panel.stakeholder_accuracy["alice"] >= 0.3

    def test_single_vote_consensus(self):
        """Test consensus with only one vote."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        decision_id = panel.submit_decision_for_feedback({"action": "test"})
        
        panel.submit_vote(decision_id, "alice", "approve")
        consensus = panel.get_consensus(decision_id)
        
        assert consensus["outcome"] == "approve"
        assert consensus["vote_count"] == 1

    def test_abstain_votes(self):
        """Test handling of abstain votes."""
        panel = PanelFeedback()
        panel.register_stakeholder("alice", "Alice", "expert")
        panel.register_stakeholder("bob", "Bob", "expert")
        
        decision_id = panel.submit_decision_for_feedback({"action": "test"})
        
        panel.submit_vote(decision_id, "alice", "approve")
        panel.submit_vote(decision_id, "bob", "abstain")
        
        consensus = panel.get_consensus(decision_id)
        
        # Should still work with abstain votes
        assert "outcome" in consensus
        assert consensus["vote_count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
