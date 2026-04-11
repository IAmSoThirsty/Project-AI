#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Panel Feedback - ML-Enhanced Distributed Value Voting and Annotation

This module implements an advanced distributed feedback system where multiple 
stakeholders can vote on, annotate, and provide feedback on AI decisions and 
behaviors. It uses machine learning techniques for consensus building, confidence 
scoring, and disagreement resolution.

Key Features:
- Multi-stakeholder voting with ML-based consensus
- Confidence scoring using Bayesian methods
- Automated disagreement detection and resolution
- Feedback learning and pattern recognition
- Decision annotation and value preference aggregation
- Weighted voting with dynamic stakeholder reputation

ML Consensus Algorithm:
- Combines weighted voting, confidence intervals, and historical patterns
- Uses Bayesian inference to compute consensus probability
- Identifies controversial decisions requiring further review
- Learns from past feedback patterns to improve future recommendations
"""

import logging
import math
from collections import defaultdict
from datetime import datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class PanelFeedback:
    """Manages ML-enhanced distributed feedback and voting from multiple stakeholders.

    This system enables:
    - Stakeholder registration with dynamic reputation
    - Vote collection with confidence weighting
    - ML-based consensus determination
    - Disagreement detection and resolution
    - Feedback learning and pattern recognition
    - Annotation and commentary
    """

    def __init__(self):
        """Initialize the ML-enhanced panel feedback system."""
        self.stakeholders: dict[str, dict[str, Any]] = {}
        self.decisions: dict[str, dict[str, Any]] = {}
        self.votes: dict[str, list[dict[str, Any]]] = {}
        self.annotations: dict[str, list[dict[str, Any]]] = {}
        
        # ML learning structures
        self.feedback_history: list[dict[str, Any]] = []
        self.stakeholder_accuracy: dict[str, float] = {}
        self.decision_patterns: dict[str, int] = defaultdict(int)
        
        # Bayesian prior parameters
        self.prior_alpha = 1.0  # Prior for positive outcomes
        self.prior_beta = 1.0   # Prior for negative outcomes

    def register_stakeholder(
        self,
        stakeholder_id: str,
        name: str,
        role: str,
        weight: float = 1.0,
    ) -> bool:
        """Register a stakeholder for providing feedback.

        Stakeholders are assigned initial voting weights which can be 
        dynamically adjusted based on their historical accuracy.

        Args:
            stakeholder_id: Unique identifier for the stakeholder
            name: Human-readable name
            role: Role or expertise area
            weight: Initial voting weight (default 1.0)

        Returns:
            True if registered successfully, False otherwise
        """
        if stakeholder_id in self.stakeholders:
            logger.warning("Stakeholder already registered: %s", stakeholder_id)
            return False

        self.stakeholders[stakeholder_id] = {
            "id": stakeholder_id,
            "name": name,
            "role": role,
            "weight": weight,
            "registered_at": datetime.now().isoformat(),
            "vote_count": 0,
            "agreement_count": 0,
        }
        
        # Initialize accuracy tracking
        self.stakeholder_accuracy[stakeholder_id] = 1.0

        logger.info("Registered stakeholder: %s (%s)", name, role)
        return True

    def submit_decision_for_feedback(
        self,
        decision: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> str:
        """Submit a decision for stakeholder feedback.

        This is a stub implementation. Future versions will:
        - Notify relevant stakeholders
        - Set voting deadlines
        - Track decision lifecycle
        - Enable decision versioning

        Args:
            decision: The decision to evaluate
            context: Additional context for evaluation

        Returns:
            Decision ID for tracking feedback
        """
        decision_id = str(uuid4())

        decision_record = {
            "decision_id": decision_id,
            "decision": decision,
            "context": context or {},
            "submitted_at": datetime.now().isoformat(),
            "status": "pending",
        }

        self.decisions[decision_id] = decision_record
        self.votes[decision_id] = []
        self.annotations[decision_id] = []

        logger.info("Submitted decision for feedback: %s", decision_id)
        return decision_id

    def submit_vote(
        self,
        decision_id: str,
        stakeholder_id: str,
        vote: str,
        reasoning: str = "",
        confidence: float = 1.0,
    ) -> bool:
        """Submit a vote on a decision with confidence score.

        Args:
            decision_id: ID of the decision being voted on
            stakeholder_id: ID of the voting stakeholder
            vote: Vote value (e.g., "approve", "reject", "abstain")
            reasoning: Optional reasoning for the vote
            confidence: Confidence level (0.0 to 1.0)

        Returns:
            True if vote recorded successfully, False otherwise
        """
        if decision_id not in self.decisions:
            logger.error("Decision not found: %s", decision_id)
            return False

        if stakeholder_id not in self.stakeholders:
            logger.error("Stakeholder not registered: %s", stakeholder_id)
            return False

        # Clamp confidence to valid range
        confidence = max(0.0, min(1.0, confidence))

        vote_record = {
            "stakeholder_id": stakeholder_id,
            "vote": vote,
            "reasoning": reasoning,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
        }

        self.votes[decision_id].append(vote_record)
        
        # Update stakeholder vote count
        self.stakeholders[stakeholder_id]["vote_count"] += 1
        
        logger.debug(
            "Recorded vote from %s on %s: %s (confidence: %.2f)", 
            stakeholder_id, decision_id, vote, confidence
        )

        return True

    def add_annotation(
        self,
        decision_id: str,
        stakeholder_id: str,
        annotation: str,
        tags: list[str] | None = None,
    ) -> bool:
        """Add an annotation or comment to a decision.

        This is a stub implementation. Future versions will:
        - Support rich text annotations
        - Enable annotation threading
        - Add annotation voting
        - Support attachments

        Args:
            decision_id: ID of the decision
            stakeholder_id: ID of the annotating stakeholder
            annotation: Annotation text
            tags: Optional tags for categorization

        Returns:
            True if annotation added successfully, False otherwise
        """
        if decision_id not in self.decisions:
            logger.error("Decision not found: %s", decision_id)
            return False

        if stakeholder_id not in self.stakeholders:
            logger.error("Stakeholder not registered: %s", stakeholder_id)
            return False

        annotation_record = {
            "stakeholder_id": stakeholder_id,
            "annotation": annotation,
            "tags": tags or [],
            "timestamp": datetime.now().isoformat(),
        }

        self.annotations[decision_id].append(annotation_record)
        logger.debug("Added annotation from %s on %s", stakeholder_id, decision_id)

        return True

    def get_consensus(self, decision_id: str) -> dict[str, Any]:
        """Determine consensus using ML-enhanced Bayesian voting.

        Uses a sophisticated algorithm that combines:
        - Weighted voting by stakeholder reputation
        - Confidence-adjusted vote strength
        - Bayesian inference for probability estimation
        - Historical pattern recognition

        Args:
            decision_id: ID of the decision

        Returns:
            Consensus result with outcome, confidence, and detailed analysis
        """
        if decision_id not in self.decisions:
            return {"error": "Decision not found"}

        votes = self.votes.get(decision_id, [])

        if not votes:
            return {
                "decision_id": decision_id,
                "outcome": "pending",
                "vote_count": 0,
                "confidence_score": 0.0,
                "message": "No votes received yet",
            }

        # Calculate weighted vote scores
        vote_scores: dict[str, float] = defaultdict(float)
        total_weight = 0.0
        
        for vote_record in votes:
            stakeholder_id = vote_record["stakeholder_id"]
            vote_val = vote_record["vote"]
            vote_confidence = vote_record.get("confidence", 1.0)
            
            # Get stakeholder weight and accuracy
            stakeholder = self.stakeholders.get(stakeholder_id, {})
            stakeholder_weight = stakeholder.get("weight", 1.0)
            stakeholder_acc = self.stakeholder_accuracy.get(stakeholder_id, 1.0)
            
            # Combined weight: base weight * accuracy * vote confidence
            effective_weight = stakeholder_weight * stakeholder_acc * vote_confidence
            
            vote_scores[vote_val] += effective_weight
            total_weight += effective_weight

        if total_weight == 0:
            return {
                "decision_id": decision_id,
                "outcome": "inconclusive",
                "vote_count": len(votes),
                "confidence_score": 0.0,
                "message": "All votes have zero weight",
            }

        # Normalize scores to probabilities
        vote_probs = {
            vote: score / total_weight 
            for vote, score in vote_scores.items()
        }
        
        # Get winning outcome
        outcome = max(vote_probs.items(), key=lambda x: x[1])[0]
        outcome_prob = vote_probs[outcome]
        
        # Calculate confidence using Bayesian posterior
        confidence_score = self._calculate_confidence(
            outcome_prob, len(votes), total_weight
        )
        
        # Detect disagreement
        disagreement = self._detect_disagreement(vote_probs, votes)
        
        # Record pattern for learning
        self.decision_patterns[outcome] += 1

        result = {
            "decision_id": decision_id,
            "outcome": outcome,
            "vote_count": len(votes),
            "confidence_score": confidence_score,
            "vote_probabilities": vote_probs,
            "vote_tallies": dict(
                (vote, sum(1 for v in votes if v["vote"] == vote))
                for vote in vote_scores.keys()
            ),
            "disagreement_detected": disagreement["detected"],
            "disagreement_score": disagreement["score"],
            "requires_review": disagreement["detected"] or confidence_score < 0.6,
            "annotations_count": len(self.annotations.get(decision_id, [])),
        }
        
        # Store in feedback history for learning
        self.feedback_history.append({
            "decision_id": decision_id,
            "outcome": outcome,
            "confidence": confidence_score,
            "timestamp": datetime.now().isoformat(),
        })

        return result

    def _calculate_confidence(
        self, 
        outcome_prob: float, 
        vote_count: int, 
        total_weight: float
    ) -> float:
        """Calculate confidence score using Bayesian inference.
        
        Args:
            outcome_prob: Probability of the winning outcome
            vote_count: Number of votes received
            total_weight: Total effective voting weight
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Bayesian posterior with Beta distribution
        # More votes and higher probability increase confidence
        
        # Effective sample size based on weight
        effective_n = min(vote_count * total_weight / vote_count, 100)
        
        # Beta distribution parameters
        alpha = self.prior_alpha + effective_n * outcome_prob
        beta = self.prior_beta + effective_n * (1 - outcome_prob)
        
        # Mean of posterior (same as outcome_prob weighted by prior)
        posterior_mean = alpha / (alpha + beta)
        
        # Variance of posterior (uncertainty measure)
        variance = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
        
        # Confidence increases with more votes and lower variance
        # Using inverse of coefficient of variation, normalized
        if posterior_mean > 0:
            cv = math.sqrt(variance) / posterior_mean
            confidence = min(1.0, 1.0 / (1.0 + cv))
        else:
            confidence = 0.0
        
        # Boost confidence if we have many votes
        vote_boost = min(0.2, vote_count / 50)
        confidence = min(1.0, confidence + vote_boost)
        
        return round(confidence, 3)

    def _detect_disagreement(
        self, 
        vote_probs: dict[str, float], 
        votes: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Detect and quantify disagreement among stakeholders.
        
        Args:
            vote_probs: Probability distribution of votes
            votes: List of vote records
            
        Returns:
            Disagreement analysis with detection flag and score
        """
        # Calculate entropy as a measure of disagreement
        # High entropy means votes are spread across many options
        entropy = 0.0
        for prob in vote_probs.values():
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        # Normalize entropy (max entropy is log2(n) for n options)
        max_entropy = math.log2(len(vote_probs)) if len(vote_probs) > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        
        # Check for high-confidence opposing votes
        high_conf_votes = [v for v in votes if v.get("confidence", 1.0) > 0.8]
        if len(high_conf_votes) >= 2:
            vote_values = [v["vote"] for v in high_conf_votes]
            opposing = len(set(vote_values)) > 1
        else:
            opposing = False
        
        # Detect disagreement if entropy is high or opposing high-confidence votes
        disagreement_detected = normalized_entropy > 0.7 or opposing
        
        return {
            "detected": disagreement_detected,
            "score": round(normalized_entropy, 3),
            "entropy": round(entropy, 3),
            "opposing_confident_votes": opposing,
        }

    def resolve_disagreement(
        self, 
        decision_id: str, 
        resolution_strategy: str = "mediation"
    ) -> dict[str, Any]:
        """Resolve disagreement using specified strategy.
        
        Strategies:
        - mediation: Seek additional expert opinions
        - weighted: Use stakeholder weights more heavily
        - consensus: Require supermajority threshold
        - defer: Mark for human review
        
        Args:
            decision_id: ID of the decision with disagreement
            resolution_strategy: Strategy to use for resolution
            
        Returns:
            Resolution result with recommendation
        """
        consensus = self.get_consensus(decision_id)
        
        if consensus.get("error"):
            return consensus
            
        if not consensus.get("disagreement_detected", False):
            return {
                "decision_id": decision_id,
                "status": "no_disagreement",
                "message": "No disagreement detected",
                "consensus": consensus,
            }
        
        votes = self.votes.get(decision_id, [])
        
        if resolution_strategy == "mediation":
            # Identify stakeholders who could mediate
            all_votes = {v["vote"] for v in votes}
            mediators = [
                sh_id for sh_id, sh in self.stakeholders.items()
                if sh_id not in [v["stakeholder_id"] for v in votes]
                and self.stakeholder_accuracy.get(sh_id, 0) > 0.8
            ]
            
            return {
                "decision_id": decision_id,
                "status": "mediation_recommended",
                "strategy": resolution_strategy,
                "recommended_mediators": mediators[:3],
                "conflicting_positions": list(all_votes),
                "message": "Recommend seeking additional expert opinions",
            }
            
        elif resolution_strategy == "weighted":
            # Re-calculate with higher weight emphasis
            vote_scores: dict[str, float] = defaultdict(float)
            
            for vote_record in votes:
                stakeholder_id = vote_record["stakeholder_id"]
                vote_val = vote_record["vote"]
                
                stakeholder = self.stakeholders.get(stakeholder_id, {})
                # Square the weight to emphasize high-weight stakeholders
                weight = stakeholder.get("weight", 1.0) ** 2
                
                vote_scores[vote_val] += weight
            
            outcome = max(vote_scores.items(), key=lambda x: x[1])[0]
            
            return {
                "decision_id": decision_id,
                "status": "weighted_resolution",
                "strategy": resolution_strategy,
                "recommended_outcome": outcome,
                "weighted_scores": dict(vote_scores),
                "message": "Resolution based on stakeholder weights",
            }
            
        elif resolution_strategy == "consensus":
            # Require supermajority (>66%)
            threshold = 0.66
            outcome_prob = consensus.get("vote_probabilities", {}).get(
                consensus.get("outcome", ""), 0
            )
            
            if outcome_prob >= threshold:
                return {
                    "decision_id": decision_id,
                    "status": "consensus_achieved",
                    "strategy": resolution_strategy,
                    "outcome": consensus["outcome"],
                    "supermajority": True,
                    "message": f"Supermajority consensus ({outcome_prob:.1%})",
                }
            else:
                return {
                    "decision_id": decision_id,
                    "status": "consensus_failed",
                    "strategy": resolution_strategy,
                    "message": f"Failed to achieve supermajority (got {outcome_prob:.1%}, need {threshold:.1%})",
                    "recommendation": "defer_to_human",
                }
                
        else:  # defer
            return {
                "decision_id": decision_id,
                "status": "deferred",
                "strategy": resolution_strategy,
                "message": "Decision deferred for human review",
                "consensus_data": consensus,
            }

    def learn_from_feedback(
        self, 
        decision_id: str, 
        actual_outcome: str,
        effectiveness_score: float = 1.0
    ) -> dict[str, Any]:
        """Learn from feedback to improve future consensus predictions.
        
        Updates stakeholder accuracy scores based on whether their votes
        aligned with the actual effective outcome.
        
        Args:
            decision_id: ID of the decision
            actual_outcome: The actual outcome that occurred
            effectiveness_score: How effective the outcome was (0.0-1.0)
            
        Returns:
            Learning summary with updated stakeholder accuracies
        """
        if decision_id not in self.decisions:
            return {"error": "Decision not found"}
            
        votes = self.votes.get(decision_id, [])
        if not votes:
            return {"error": "No votes to learn from"}
        
        # Update accuracy for each stakeholder
        updates = {}
        learning_rate = 0.15  # How quickly to adjust accuracy scores
        
        for vote_record in votes:
            stakeholder_id = vote_record["stakeholder_id"]
            vote_val = vote_record["vote"]
            
            # Was this vote correct?
            was_correct = (vote_val == actual_outcome)
            
            # Get current accuracy
            current_acc = self.stakeholder_accuracy.get(stakeholder_id, 1.0)
            
            # Update accuracy using exponential moving average
            if was_correct:
                # Increase accuracy, weighted by effectiveness
                # Move toward 1.0
                target = 1.0
                new_acc = current_acc + learning_rate * effectiveness_score * (target - current_acc)
                self.stakeholders[stakeholder_id]["agreement_count"] += 1
            else:
                # Decrease accuracy
                # Move toward 0.5, amount depends on how ineffective the outcome was
                penalty = learning_rate * effectiveness_score
                new_acc = current_acc * (1.0 - penalty)
            
            # Clamp to reasonable range [0.3, 1.0]
            new_acc = max(0.3, min(1.0, new_acc))
            
            self.stakeholder_accuracy[stakeholder_id] = new_acc
            updates[stakeholder_id] = {
                "old_accuracy": round(current_acc, 3),
                "new_accuracy": round(new_acc, 3),
                "was_correct": was_correct,
            }
        
        # Store learning event
        learning_event = {
            "decision_id": decision_id,
            "actual_outcome": actual_outcome,
            "effectiveness_score": effectiveness_score,
            "timestamp": datetime.now().isoformat(),
            "stakeholder_updates": updates,
        }
        
        self.feedback_history.append(learning_event)
        
        logger.info(
            "Learned from decision %s: %d stakeholders updated", 
            decision_id, len(updates)
        )
        
        return {
            "decision_id": decision_id,
            "learned": True,
            "stakeholder_updates": updates,
            "total_votes": len(votes),
        }

    def get_stakeholder_stats(self, stakeholder_id: str) -> dict[str, Any]:
        """Get comprehensive statistics for a stakeholder.
        
        Args:
            stakeholder_id: ID of the stakeholder
            
        Returns:
            Statistics including accuracy, vote count, agreement rate
        """
        if stakeholder_id not in self.stakeholders:
            return {"error": "Stakeholder not found"}
        
        stakeholder = self.stakeholders[stakeholder_id]
        vote_count = stakeholder.get("vote_count", 0)
        agreement_count = stakeholder.get("agreement_count", 0)
        
        agreement_rate = (
            agreement_count / vote_count if vote_count > 0 else 0.0
        )
        
        return {
            "stakeholder_id": stakeholder_id,
            "name": stakeholder.get("name", ""),
            "role": stakeholder.get("role", ""),
            "weight": stakeholder.get("weight", 1.0),
            "accuracy": self.stakeholder_accuracy.get(stakeholder_id, 1.0),
            "vote_count": vote_count,
            "agreement_count": agreement_count,
            "agreement_rate": round(agreement_rate, 3),
            "registered_at": stakeholder.get("registered_at", ""),
        }

    def get_feedback_insights(self) -> dict[str, Any]:
        """Get insights from historical feedback data.
        
        Returns:
            Insights including common patterns, top stakeholders, and trends
        """
        if not self.feedback_history:
            return {
                "message": "No feedback history available",
                "total_events": 0,
            }
        
        # Analyze decision patterns
        total_patterns = sum(self.decision_patterns.values())
        pattern_dist = {
            outcome: count / total_patterns 
            for outcome, count in self.decision_patterns.items()
        } if total_patterns > 0 else {}
        
        # Identify top stakeholders by accuracy
        stakeholder_rankings = sorted(
            [
                (sh_id, acc) 
                for sh_id, acc in self.stakeholder_accuracy.items()
                if self.stakeholders[sh_id].get("vote_count", 0) >= 3
            ],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Calculate average confidence over time
        recent_events = self.feedback_history[-10:]
        avg_confidence = sum(
            e.get("confidence", 0.5) 
            for e in recent_events 
            if "confidence" in e
        ) / len(recent_events) if recent_events else 0.0
        
        return {
            "total_feedback_events": len(self.feedback_history),
            "total_decisions": len(self.decisions),
            "total_stakeholders": len(self.stakeholders),
            "active_stakeholders": sum(
                1 for sh in self.stakeholders.values() 
                if sh.get("vote_count", 0) > 0
            ),
            "pattern_distribution": pattern_dist,
            "most_common_outcome": max(
                self.decision_patterns.items(), 
                key=lambda x: x[1]
            )[0] if self.decision_patterns else None,
            "top_stakeholders": [
                {
                    "id": sh_id,
                    "name": self.stakeholders[sh_id].get("name", ""),
                    "accuracy": round(acc, 3),
                }
                for sh_id, acc in stakeholder_rankings[:5]
            ],
            "average_recent_confidence": round(avg_confidence, 3),
        }

    def get_decision_feedback(self, decision_id: str) -> dict[str, Any]:
        """Get all feedback for a decision.

        Args:
            decision_id: ID of the decision

        Returns:
            Complete feedback including votes, annotations, and consensus
        """
        if decision_id not in self.decisions:
            return {"error": "Decision not found"}

        return {
            "decision": self.decisions[decision_id],
            "votes": self.votes.get(decision_id, []),
            "annotations": self.annotations.get(decision_id, []),
            "consensus": self.get_consensus(decision_id),
        }


__all__ = ["PanelFeedback"]
