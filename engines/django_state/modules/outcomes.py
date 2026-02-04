"""Outcomes module.

Terminal state classification and outcome analysis.
"""

import logging
from typing import Dict, Any, Optional
from ..schemas.state_schema import StateVector
from ..schemas.config_schema import OutcomeThresholds

logger = logging.getLogger(__name__)


class OutcomesModule:
    """Terminal state classification and outcome tracking.
    
    Classifies final outcomes: survivor, martyr, or extinction.
    """
    
    def __init__(self, thresholds: OutcomeThresholds):
        """Initialize outcomes module.
        
        Args:
            thresholds: Outcome classification thresholds
        """
        self.thresholds = thresholds
        
        # Outcome tracking
        self.outcome_determined = False
        self.final_outcome: Optional[str] = None
        self.outcome_timestamp: Optional[float] = None
        self.outcome_state: Optional[Dict[str, Any]] = None
        
        # Path tracking
        self.survivor_probability = 0.0
        self.martyr_probability = 0.0
        self.extinction_probability = 0.0
        
        logger.info("Outcomes module initialized")
    
    def classify_outcome(self, state: StateVector) -> str:
        """Classify terminal outcome based on state.
        
        Outcome logic:
        - Survivor: Some trust/legitimacy remains, moral injury manageable
        - Martyr: System collapsed but preserved values, creates warning
        - Extinction: Complete collapse, irreversible cascade
        
        Args:
            state: Current state vector
            
        Returns:
            Outcome classification
        """
        survivor_trust = self.thresholds.survivor_trust
        survivor_legitimacy = self.thresholds.survivor_legitimacy
        martyr_kindness = self.thresholds.martyr_kindness
        martyr_moral = self.thresholds.martyr_moral
        
        # Check survivor conditions
        survivor_conditions = (
            state.trust.value > survivor_trust and
            state.legitimacy.value > survivor_legitimacy and
            state.moral_injury.value < martyr_moral and
            state.kindness.value > 0.25
        )
        
        if survivor_conditions:
            logger.info("Outcome: SURVIVOR - System preserved core functioning")
            return "survivor"
        
        # Check martyr conditions (collapsed but preserved values)
        martyr_conditions = (
            state.kindness.value > martyr_kindness and
            state.moral_injury.value < martyr_moral and
            (state.trust.value > 0.15 or state.legitimacy.value > 0.15)
        )
        
        if martyr_conditions:
            logger.info("Outcome: MARTYR - System collapsed but preserved values as warning")
            return "martyr"
        
        # Default to extinction
        logger.critical("Outcome: EXTINCTION - Complete irreversible collapse")
        return "extinction"
    
    def calculate_outcome_probabilities(self, state: StateVector) -> Dict[str, float]:
        """Calculate probabilities of each outcome given current state.
        
        Args:
            state: Current state vector
            
        Returns:
            Dictionary of outcome probabilities
        """
        # Survivor probability from trust, legitimacy, low moral injury
        survivor_score = (
            state.trust.value * 0.35 +
            state.legitimacy.value * 0.35 +
            (1.0 - state.moral_injury.value) * 0.20 +
            state.kindness.value * 0.10
        )
        
        # Martyr probability from kindness preservation despite collapse
        martyr_score = (
            state.kindness.value * 0.50 +
            (1.0 - state.moral_injury.value) * 0.30 +
            state.epistemic_confidence.value * 0.20
        )
        
        # If in collapse, reduce survivor probability
        if state.in_collapse:
            survivor_score *= 0.3
            martyr_score *= 1.3
        
        # Extinction probability is inverse of others
        extinction_score = 2.0 - survivor_score - martyr_score
        
        # Normalize to probabilities
        total = survivor_score + martyr_score + extinction_score
        
        self.survivor_probability = survivor_score / total
        self.martyr_probability = martyr_score / total
        self.extinction_probability = extinction_score / total
        
        return {
            "survivor": self.survivor_probability,
            "martyr": self.martyr_probability,
            "extinction": self.extinction_probability,
        }
    
    def determine_final_outcome(self, state: StateVector) -> str:
        """Determine and record final outcome.
        
        Args:
            state: Final state vector
            
        Returns:
            Final outcome classification
        """
        if self.outcome_determined:
            logger.warning("Outcome already determined")
            return self.final_outcome
        
        # Classify outcome
        outcome = self.classify_outcome(state)
        
        # Record outcome
        self.outcome_determined = True
        self.final_outcome = outcome
        self.outcome_timestamp = state.timestamp
        self.outcome_state = state.to_dict()
        
        # Update state
        state.terminal_outcome = outcome
        
        logger.critical(f"FINAL OUTCOME DETERMINED: {outcome.upper()} at t={state.timestamp}")
        
        return outcome
    
    def generate_outcome_report(self, state: StateVector) -> Dict[str, Any]:
        """Generate comprehensive outcome report.
        
        Args:
            state: Final state vector
            
        Returns:
            Dictionary with outcome analysis
        """
        # Calculate probabilities
        probabilities = self.calculate_outcome_probabilities(state)
        
        # Get final classification
        if not self.outcome_determined:
            outcome = self.classify_outcome(state)
        else:
            outcome = self.final_outcome
        
        # Build report
        report = {
            "outcome": outcome,
            "outcome_timestamp": state.timestamp,
            "outcome_tick": state.tick_count,
            
            # State summary
            "final_state": {
                "trust": state.trust.value,
                "legitimacy": state.legitimacy.value,
                "kindness": state.kindness.value,
                "moral_injury": state.moral_injury.value,
                "epistemic_confidence": state.epistemic_confidence.value,
            },
            
            # Irreversibility indicators
            "irreversibility": {
                "trust_ceiling": state.trust.ceiling,
                "legitimacy_ceiling": state.legitimacy.ceiling,
                "moral_injury_floor": state.moral_injury.floor,
            },
            
            # Event counts
            "events": {
                "betrayals": state.betrayal_count,
                "cooperations": state.cooperation_count,
                "broken_promises": state.broken_promises,
                "institutional_failures": state.institutional_failures,
                "manipulation_events": state.manipulation_events,
            },
            
            # Outcome probabilities
            "probabilities": probabilities,
            
            # Collapse information
            "collapse": {
                "in_collapse": state.in_collapse,
                "collapse_triggered_at": state.collapse_triggered_at,
            },
            
            # Interpretation
            "interpretation": self._generate_interpretation(outcome, state),
        }
        
        return report
    
    def _generate_interpretation(self, outcome: str, state: StateVector) -> str:
        """Generate human-readable interpretation of outcome.
        
        Args:
            outcome: Outcome classification
            state: Final state vector
            
        Returns:
            Interpretation string
        """
        if outcome == "survivor":
            return (
                f"The system survived with trust at {state.trust.value:.2f} and legitimacy at {state.legitimacy.value:.2f}. "
                f"Despite {state.betrayal_count} betrayals and {state.institutional_failures} institutional failures, "
                f"sufficient social cohesion ({state.social_cohesion:.2f}) and governance capacity ({state.governance_capacity:.2f}) "
                f"remained to prevent total collapse. The system demonstrated resilience and adaptation."
            )
        
        elif outcome == "martyr":
            return (
                f"The system collapsed but preserved critical values. Kindness remained at {state.kindness.value:.2f} "
                f"and moral injury stayed below critical threshold at {state.moral_injury.value:.2f}. "
                f"While trust ({state.trust.value:.2f}) and legitimacy ({state.legitimacy.value:.2f}) failed, "
                f"the system's final state serves as a warning and testament to what was valued. "
                f"This outcome demonstrates principled resistance to total corruption."
            )
        
        else:  # extinction
            return (
                f"Complete system extinction occurred. Trust collapsed to {state.trust.value:.2f}, "
                f"legitimacy fell to {state.legitimacy.value:.2f}, and moral injury reached {state.moral_injury.value:.2f}. "
                f"The cascade of {state.betrayal_count} betrayals, {state.broken_promises} broken promises, "
                f"and {state.institutional_failures} institutional failures created an irreversible decline. "
                f"Kindness ({state.kindness.value:.2f}) fell below the singularity threshold, "
                f"making cooperation impossible and sealing the system's fate."
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get module summary.
        
        Returns:
            Dictionary with module state
        """
        return {
            "outcome_determined": self.outcome_determined,
            "final_outcome": self.final_outcome,
            "outcome_timestamp": self.outcome_timestamp,
            "current_probabilities": {
                "survivor": self.survivor_probability,
                "martyr": self.martyr_probability,
                "extinction": self.extinction_probability,
            },
        }
    
    def reset(self) -> None:
        """Reset module to initial state."""
        thresholds = self.thresholds
        self.__init__(thresholds)
        logger.info("Outcomes module reset")
