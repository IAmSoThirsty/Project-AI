"""Human forces module.

Models individual agency, cooperation/defection dynamics, and human behavior.
"""

import logging
import random
from typing import Dict, Any, List, Optional
from ..schemas.state_schema import StateVector
from ..schemas.event_schema import BetrayalEvent, CooperationEvent
from ..kernel.irreversibility_laws import IrreversibilityLaws

logger = logging.getLogger(__name__)


class HumanForcesModule:
    """Models human agency and cooperation/defection dynamics.
    
    Tracks individual and collective behavior patterns including cooperation
    propensity, defection likelihood, and social dynamics.
    """
    
    def __init__(self, laws: IrreversibilityLaws):
        """Initialize human forces module.
        
        Args:
            laws: Irreversibility laws instance
        """
        self.laws = laws
        
        # Population tracking
        self.population_size = 1000  # Abstract population units
        self.cooperators = int(self.population_size * 0.7)
        self.defectors = int(self.population_size * 0.3)
        
        # Behavior history
        self.cooperation_history: List[int] = []
        self.defection_history: List[int] = []
        self.betrayal_history: List[Dict[str, Any]] = []
        
        # Game theory parameters
        self.cooperation_payoff = 3.0
        self.defection_payoff = 5.0
        self.mutual_cooperation_payoff = 4.0
        self.mutual_defection_payoff = 1.0
        
        logger.info(f"Human forces module initialized: {self.cooperators} cooperators, {self.defectors} defectors")
    
    def simulate_cooperation_decision(self, state: StateVector) -> tuple[int, int]:
        """Simulate cooperation vs defection decisions based on state.
        
        Uses game theory and state conditions to determine cooperation levels.
        
        Args:
            state: Current state vector
            
        Returns:
            Tuple of (cooperators, defectors) for this round
        """
        # Base cooperation probability from kindness and trust
        base_cooperation_prob = (state.kindness.value * 0.6 + state.trust.value * 0.4)
        
        # Adjust for social cohesion
        cooperation_prob = base_cooperation_prob * state.social_cohesion
        
        # Calculate expected switches
        defectors_to_cooperators = 0
        cooperators_to_defectors = 0
        
        # Some defectors may become cooperators if conditions improve
        if cooperation_prob > 0.5:
            switch_rate = (cooperation_prob - 0.5) * 0.2
            defectors_to_cooperators = int(self.defectors * switch_rate)
        
        # Some cooperators may defect if conditions worsen
        if cooperation_prob < 0.4:
            switch_rate = (0.4 - cooperation_prob) * 0.3
            cooperators_to_defectors = int(self.cooperators * switch_rate)
        
        # Apply switches
        self.cooperators = self.cooperators + defectors_to_cooperators - cooperators_to_defectors
        self.defectors = self.defectors - defectors_to_cooperators + cooperators_to_defectors
        
        # Ensure valid counts
        self.cooperators = max(0, min(self.population_size, self.cooperators))
        self.defectors = self.population_size - self.cooperators
        
        # Record history
        self.cooperation_history.append(self.cooperators)
        self.defection_history.append(self.defectors)
        
        logger.debug(f"Cooperation decision: {self.cooperators} cooperators ({self.cooperators/self.population_size:.2%}), {self.defectors} defectors")
        
        return self.cooperators, self.defectors
    
    def generate_cooperation_events(self, state: StateVector, count: int = 1) -> List[CooperationEvent]:
        """Generate cooperation events based on current cooperation levels.
        
        Args:
            state: Current state vector
            count: Number of events to generate
            
        Returns:
            List of cooperation events
        """
        from ..schemas.event_schema import EventType
        
        events = []
        cooperation_rate = self.cooperators / self.population_size
        
        for i in range(count):
            # Magnitude based on cooperation rate
            magnitude = cooperation_rate * random.uniform(0.5, 1.0)
            
            # Reciprocity more likely with high trust
            reciprocity = random.random() < state.trust.value
            
            event = CooperationEvent(
                event_type=EventType.COOPERATION,
                timestamp=state.timestamp,
                source="human_forces",
                description=f"Cooperation event {i+1}: magnitude {magnitude:.2f}",
                magnitude=magnitude,
                reciprocity=reciprocity,
                participants=[f"agent_{random.randint(1, self.population_size)}" for _ in range(2)],
            )
            events.append(event)
        
        logger.debug(f"Generated {count} cooperation events")
        return events
    
    def evaluate_betrayal_risk(self, state: StateVector) -> float:
        """Evaluate current risk of betrayal occurring.
        
        Args:
            state: Current state vector
            
        Returns:
            Betrayal risk probability (0.0 to 1.0)
        """
        # Use irreversibility laws to calculate base probability
        base_prob = self.laws.calculate_betrayal_probability(state)
        
        # Adjust for defector population
        defector_factor = (self.defectors / self.population_size) * 0.5
        
        # Adjust for recent betrayal history
        recent_betrayals = sum(1 for b in self.betrayal_history[-10:] if b.get("severity", 0) > 0.5)
        history_factor = min(recent_betrayals * 0.1, 0.3)
        
        total_risk = base_prob + defector_factor + history_factor
        total_risk = min(total_risk, 1.0)
        
        logger.debug(f"Betrayal risk: {total_risk:.4f} (base: {base_prob:.4f}, defectors: {defector_factor:.4f}, history: {history_factor:.4f})")
        
        return total_risk
    
    def generate_betrayal_event(
        self,
        state: StateVector,
        severity: Optional[float] = None,
        visibility: Optional[float] = None,
    ) -> BetrayalEvent:
        """Generate a betrayal event.
        
        Args:
            state: Current state vector
            severity: Optional specific severity (random if None)
            visibility: Optional specific visibility (random if None)
            
        Returns:
            BetrayalEvent instance
        """
        from ..schemas.event_schema import EventType
        
        if severity is None:
            severity = random.uniform(0.3, 0.9)
        
        if visibility is None:
            # Visibility correlates with epistemic confidence (harder to hide with good information)
            visibility = 0.5 + (state.epistemic_confidence.value * 0.3) + random.uniform(-0.2, 0.2)
            visibility = max(0.0, min(1.0, visibility))
        
        event = BetrayalEvent(
            event_type=EventType.BETRAYAL,
            timestamp=state.timestamp,
            source="human_forces",
            description=f"Betrayal event: severity {severity:.2f}, visibility {visibility:.2f}",
            severity=severity,
            visibility=visibility,
            perpetrator=f"agent_{random.randint(1, self.population_size)}",
            victim=f"agent_{random.randint(1, self.population_size)}",
        )
        
        # Record in history
        self.betrayal_history.append({
            "timestamp": state.timestamp,
            "severity": severity,
            "visibility": visibility,
            "event_id": event.event_id,
        })
        
        logger.info(f"Generated betrayal event: severity={severity:.2f}, visibility={visibility:.2f}")
        
        return event
    
    def apply_cooperation_dynamics(self, state: StateVector) -> Dict[str, Any]:
        """Apply cooperation dynamics for this tick.
        
        Simulates cooperation decisions and potentially generates events.
        
        Args:
            state: Current state vector
            
        Returns:
            Dictionary with dynamics results
        """
        # Simulate cooperation decisions
        cooperators, defectors = self.simulate_cooperation_decision(state)
        
        # Check if cooperation events should occur
        cooperation_rate = cooperators / self.population_size
        events_to_generate = 0
        
        if cooperation_rate > 0.6 and random.random() < cooperation_rate:
            events_to_generate = random.randint(1, 3)
        
        cooperation_events = []
        if events_to_generate > 0:
            cooperation_events = self.generate_cooperation_events(state, events_to_generate)
            
            # Apply cooperation boosts
            for event in cooperation_events:
                self.laws.apply_cooperation_boost(state, event.magnitude)
        
        # Check for betrayal risk
        betrayal_risk = self.evaluate_betrayal_risk(state)
        betrayal_occurred = random.random() < betrayal_risk
        
        betrayal_event = None
        if betrayal_occurred:
            betrayal_event = self.generate_betrayal_event(state)
            # Apply betrayal impact
            self.laws.apply_betrayal_impact(state, betrayal_event.severity)
        
        return {
            "cooperators": cooperators,
            "defectors": defectors,
            "cooperation_rate": cooperation_rate,
            "cooperation_events": len(cooperation_events),
            "betrayal_risk": betrayal_risk,
            "betrayal_occurred": betrayal_occurred,
            "betrayal_event": betrayal_event,
        }
    
    def get_cooperation_trend(self, window: int = 10) -> str:
        """Get cooperation trend over recent history.
        
        Args:
            window: Number of recent ticks to analyze
            
        Returns:
            Trend description: "increasing", "decreasing", or "stable"
        """
        if len(self.cooperation_history) < window:
            return "insufficient_data"
        
        recent = self.cooperation_history[-window:]
        first_half = sum(recent[:window//2]) / (window//2)
        second_half = sum(recent[window//2:]) / (window - window//2)
        
        diff = second_half - first_half
        
        if diff > self.population_size * 0.05:
            return "increasing"
        elif diff < -self.population_size * 0.05:
            return "decreasing"
        else:
            return "stable"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get module summary.
        
        Returns:
            Dictionary with module state
        """
        cooperation_rate = self.cooperators / self.population_size if self.population_size > 0 else 0.0
        
        return {
            "population_size": self.population_size,
            "cooperators": self.cooperators,
            "defectors": self.defectors,
            "cooperation_rate": cooperation_rate,
            "total_betrayals": len(self.betrayal_history),
            "cooperation_trend": self.get_cooperation_trend(),
        }
    
    def reset(self) -> None:
        """Reset module to initial state."""
        self.__init__(self.laws)
        logger.info("Human forces module reset")
