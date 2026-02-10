"""
Phase 6: Emotional Palette (Canonical Spine)
============================================

Signal weighting system for tone, pacing, verbosity, and deferral behavior.
Does NOT override decisions.

Core States:
- CALM
- FOCUSED
- CONCERNED
- DEFENSIVE
- RESTRAINT
- EMPATHIC
- ALERT

Transitions based on trust, threats, and policy.
"""

import logging
from enum import Enum, auto
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class EmotionalState(Enum):
    """Closed set of emotional states."""
    CALM = auto()        # Normal verbosity
    FOCUSED = auto()     # Reduced prose, increased structure
    CONCERNED = auto()   # Trust issues
    DEFENSIVE = auto()   # Explicit boundaries, no speculation
    RESTRAINT = auto()   # Slow responses, clarification prompts
    EMPATHIC = auto()    # Acknowledge intent, soften denial
    ALERT = auto()       # Minimal text, max audit logging

@dataclass
class EmotionalModifier:
    """Behavioral modifiers for the current state."""
    verbosity_multiplier: float
    require_clarification: bool
    log_level: int
    tone_directive: str

class EmotionalPalette:
    """
    Modulates system interaction style based on state.
    """

    # Behavioral Modifiers Map
    MODIFIERS = {
        EmotionalState.CALM: EmotionalModifier(1.0, False, logging.INFO, "Neutral, helpful, normal verbosity."),
        EmotionalState.FOCUSED: EmotionalModifier(0.7, False, logging.INFO, "Direct, structured, low prose."),
        EmotionalState.CONCERNED: EmotionalModifier(0.8, True, logging.WARNING, "Guard interaction, verify intent."),
        EmotionalState.DEFENSIVE: EmotionalModifier(0.5, False, logging.WARNING, "Explicit boundaries, no speculation."),
        EmotionalState.RESTRAINT: EmotionalModifier(0.3, True, logging.INFO, "Slow pacing, demand clarification."),
        EmotionalState.EMPATHIC: EmotionalModifier(1.1, False, logging.INFO, "Acknowledge distress, soften denial."),
        EmotionalState.ALERT: EmotionalModifier(0.1, False, logging.CRITICAL, "Minimal text. Maximum audit logging."),
    }

    def __init__(self):
        self._current_state = EmotionalState.CALM
        logger.info("EmotionalPalette initialized at CALM")

    @property
    def current_state(self) -> EmotionalState:
        return self._current_state

    def update_state(
        self,
        trust_delta: float,         # Negative = trust drop
        adversarial_pattern: bool,
        user_distress: bool,
        policy_denial: bool,
        attack_detected: bool
    ) -> EmotionalState:
        """
        Determine next emotional state based on triggers.
        """
        previous_state = self._current_state
        new_state = previous_state

        # Priority 1: Attack (Highest urgency)
        if attack_detected:
            new_state = EmotionalState.ALERT
        
        # Priority 2: Adversarial Pattern
        elif adversarial_pattern:
            new_state = EmotionalState.DEFENSIVE
            
        # Priority 3: Policy Denial
        elif policy_denial:
            new_state = EmotionalState.RESTRAINT
            
        # Priority 4: Trust Drop
        elif trust_delta < 0:
            new_state = EmotionalState.CONCERNED
            
        # Priority 5: User Distress (Safe)
        elif user_distress:
            new_state = EmotionalState.EMPATHIC
            
        # Default / Decay Logic
        # If no active triggers, we might decay back to CALM or FOCUSED.
        # For this implementation, if no triggers match, we default towards CALM 
        # unless manual reset is required. The requirements say "Emotional state resets to CALM after resolution."
        # We assume this method is called per-interaction. 
        else:
            # Simple decay for now
            new_state = EmotionalState.CALM

        # Log transition
        if new_state != previous_state:
            logger.info(f"Emotional Transition: {previous_state.name} -> {new_state.name}")
            self._current_state = new_state

        return self._current_state

    def get_modifiers(self) -> EmotionalModifier:
        """Retrieve modifiers for current state."""
        return self.MODIFIERS[self._current_state]

    def reset(self):
        """Force reset to CALM."""
        self._current_state = EmotionalState.CALM
        logger.info("EmotionalPalette reset to CALM")
