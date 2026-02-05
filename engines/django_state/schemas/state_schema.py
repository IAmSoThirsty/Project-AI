"""State vector schema for Django State Engine.

Defines the multi-dimensional state space tracking trust, legitimacy,
kindness, moral injury, and other critical dimensions.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import json


@dataclass
class StateDimension:
    """Individual dimension in state space."""
    
    value: float
    min_value: float = 0.0
    max_value: float = 1.0
    ceiling: Optional[float] = None  # Irreversible ceiling after damage
    floor: Optional[float] = None  # Irreversible floor after improvement
    history: list[tuple[float, float]] = field(default_factory=list)  # (timestamp, value)
    
    def __post_init__(self):
        """Validate dimension bounds."""
        self.value = max(self.min_value, min(self.max_value, self.value))
        if self.ceiling is not None:
            self.value = min(self.ceiling, self.value)
        if self.floor is not None:
            self.value = max(self.floor, self.value)
    
    def update(self, delta: float, timestamp: float, enforce_ceiling: bool = True) -> float:
        """Update dimension value with irreversibility constraints.
        
        Args:
            delta: Change to apply
            timestamp: Current simulation time
            enforce_ceiling: Whether to enforce ceiling constraint
            
        Returns:
            Actual change applied after constraints
        """
        old_value = self.value
        new_value = self.value + delta
        
        # Apply bounds
        new_value = max(self.min_value, min(self.max_value, new_value))
        
        # Apply irreversibility constraints
        if enforce_ceiling and self.ceiling is not None:
            new_value = min(self.ceiling, new_value)
        if self.floor is not None:
            new_value = max(self.floor, new_value)
        
        self.value = new_value
        self.history.append((timestamp, self.value))
        
        return self.value - old_value
    
    def impose_ceiling(self, ceiling_value: float) -> None:
        """Impose irreversible ceiling (trust/legitimacy damage)."""
        if self.ceiling is None or ceiling_value < self.ceiling:
            self.ceiling = ceiling_value
            self.value = min(self.value, ceiling_value)
    
    def impose_floor(self, floor_value: float) -> None:
        """Impose irreversible floor (moral injury accumulation)."""
        if self.floor is None or floor_value > self.floor:
            self.floor = floor_value
            self.value = max(self.value, floor_value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "value": self.value,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "ceiling": self.ceiling,
            "floor": self.floor,
            "history_length": len(self.history),
        }


@dataclass
class StateVector:
    """Complete state vector for Django State Engine.
    
    Tracks all dimensions of system state including trust, legitimacy,
    kindness, moral injury, and derivative metrics.
    """
    
    # Primary dimensions
    trust: StateDimension
    legitimacy: StateDimension
    kindness: StateDimension
    moral_injury: StateDimension
    epistemic_confidence: StateDimension
    
    # Counters and accumulators
    betrayal_count: int = 0
    cooperation_count: int = 0
    broken_promises: int = 0
    institutional_failures: int = 0
    manipulation_events: int = 0
    
    # Derived state
    social_cohesion: float = 1.0
    governance_capacity: float = 1.0
    reality_consensus: float = 1.0
    
    # Metadata
    timestamp: float = 0.0
    tick_count: int = 0
    state_id: str = ""
    
    # Outcome tracking
    in_collapse: bool = False
    collapse_triggered_at: Optional[float] = None
    terminal_outcome: Optional[str] = None
    
    @classmethod
    def create_initial_state(cls, timestamp: float = 0.0) -> "StateVector":
        """Create initial state with healthy values."""
        return cls(
            trust=StateDimension(value=0.8, min_value=0.0, max_value=1.0),
            legitimacy=StateDimension(value=0.75, min_value=0.0, max_value=1.0),
            kindness=StateDimension(value=0.7, min_value=0.0, max_value=1.0),
            moral_injury=StateDimension(value=0.0, min_value=0.0, max_value=1.0),
            epistemic_confidence=StateDimension(value=0.85, min_value=0.0, max_value=1.0),
            timestamp=timestamp,
            state_id=f"state_{timestamp}",
        )
    
    def update_derived_state(self) -> None:
        """Update derived state metrics based on primary dimensions."""
        # Social cohesion depends on trust and kindness
        self.social_cohesion = (self.trust.value * 0.6 + self.kindness.value * 0.4)
        
        # Governance capacity depends on legitimacy and epistemic confidence
        self.governance_capacity = (self.legitimacy.value * 0.7 + 
                                   self.epistemic_confidence.value * 0.3)
        
        # Reality consensus depends on epistemic confidence and social cohesion
        self.reality_consensus = (self.epistemic_confidence.value * 0.6 + 
                                 self.social_cohesion * 0.4)
    
    def check_collapse_conditions(self, thresholds: Dict[str, float]) -> tuple[bool, str]:
        """Check if system has entered irreversible collapse.
        
        Args:
            thresholds: Dictionary of collapse thresholds
            
        Returns:
            Tuple of (is_collapsed, reason)
        """
        kindness_threshold = thresholds.get("kindness_singularity", 0.2)
        trust_threshold = thresholds.get("trust_collapse", 0.15)
        moral_injury_threshold = thresholds.get("moral_injury_critical", 0.85)
        legitimacy_threshold = thresholds.get("legitimacy_failure", 0.1)
        epistemic_threshold = thresholds.get("epistemic_collapse", 0.2)
        
        if self.kindness.value < kindness_threshold:
            return True, "kindness_singularity"
        
        if self.trust.value < trust_threshold:
            return True, "trust_collapse"
        
        if self.moral_injury.value > moral_injury_threshold:
            return True, "moral_injury_critical"
        
        if self.legitimacy.value < legitimacy_threshold:
            return True, "legitimacy_failure"
        
        if self.epistemic_confidence.value < epistemic_threshold:
            return True, "epistemic_collapse"
        
        return False, ""
    
    def classify_outcome(self, thresholds: Dict[str, float]) -> str:
        """Classify terminal outcome state.
        
        Args:
            thresholds: Outcome classification thresholds
            
        Returns:
            Outcome classification: survivor, martyr, or extinction
        """
        survivor_trust = thresholds.get("survivor_trust", 0.3)
        survivor_legitimacy = thresholds.get("survivor_legitimacy", 0.25)
        martyr_kindness = thresholds.get("martyr_kindness", 0.3)
        martyr_moral = thresholds.get("martyr_moral", 0.6)
        
        # Survivor: Some trust/legitimacy remains, moral injury manageable
        if (self.trust.value > survivor_trust and 
            self.legitimacy.value > survivor_legitimacy and
            self.moral_injury.value < martyr_moral):
            return "survivor"
        
        # Martyr: System collapsed but preserved values
        if (self.kindness.value > martyr_kindness and
            self.moral_injury.value < martyr_moral):
            return "martyr"
        
        # Extinction: Complete collapse
        return "extinction"
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state vector to dictionary."""
        return {
            "timestamp": self.timestamp,
            "tick_count": self.tick_count,
            "state_id": self.state_id,
            "dimensions": {
                "trust": self.trust.to_dict(),
                "legitimacy": self.legitimacy.to_dict(),
                "kindness": self.kindness.to_dict(),
                "moral_injury": self.moral_injury.to_dict(),
                "epistemic_confidence": self.epistemic_confidence.to_dict(),
            },
            "counters": {
                "betrayal_count": self.betrayal_count,
                "cooperation_count": self.cooperation_count,
                "broken_promises": self.broken_promises,
                "institutional_failures": self.institutional_failures,
                "manipulation_events": self.manipulation_events,
            },
            "derived": {
                "social_cohesion": self.social_cohesion,
                "governance_capacity": self.governance_capacity,
                "reality_consensus": self.reality_consensus,
            },
            "collapse": {
                "in_collapse": self.in_collapse,
                "collapse_triggered_at": self.collapse_triggered_at,
                "terminal_outcome": self.terminal_outcome,
            },
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def copy(self) -> "StateVector":
        """Create deep copy of state vector."""
        return StateVector(
            trust=StateDimension(
                value=self.trust.value,
                min_value=self.trust.min_value,
                max_value=self.trust.max_value,
                ceiling=self.trust.ceiling,
                floor=self.trust.floor,
                history=self.trust.history.copy(),
            ),
            legitimacy=StateDimension(
                value=self.legitimacy.value,
                min_value=self.legitimacy.min_value,
                max_value=self.legitimacy.max_value,
                ceiling=self.legitimacy.ceiling,
                floor=self.legitimacy.floor,
                history=self.legitimacy.history.copy(),
            ),
            kindness=StateDimension(
                value=self.kindness.value,
                min_value=self.kindness.min_value,
                max_value=self.kindness.max_value,
                ceiling=self.kindness.ceiling,
                floor=self.kindness.floor,
                history=self.kindness.history.copy(),
            ),
            moral_injury=StateDimension(
                value=self.moral_injury.value,
                min_value=self.moral_injury.min_value,
                max_value=self.moral_injury.max_value,
                ceiling=self.moral_injury.ceiling,
                floor=self.moral_injury.floor,
                history=self.moral_injury.history.copy(),
            ),
            epistemic_confidence=StateDimension(
                value=self.epistemic_confidence.value,
                min_value=self.epistemic_confidence.min_value,
                max_value=self.epistemic_confidence.max_value,
                ceiling=self.epistemic_confidence.ceiling,
                floor=self.epistemic_confidence.floor,
                history=self.epistemic_confidence.history.copy(),
            ),
            betrayal_count=self.betrayal_count,
            cooperation_count=self.cooperation_count,
            broken_promises=self.broken_promises,
            institutional_failures=self.institutional_failures,
            manipulation_events=self.manipulation_events,
            social_cohesion=self.social_cohesion,
            governance_capacity=self.governance_capacity,
            reality_consensus=self.reality_consensus,
            timestamp=self.timestamp,
            tick_count=self.tick_count,
            state_id=self.state_id,
            in_collapse=self.in_collapse,
            collapse_triggered_at=self.collapse_triggered_at,
            terminal_outcome=self.terminal_outcome,
        )
