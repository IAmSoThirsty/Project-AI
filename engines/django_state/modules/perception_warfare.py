"""Perception warfare module.

Models information manipulation, epistemic collapse, and reality fragmentation.
"""

import logging
import random
from typing import Any

from ..kernel.irreversibility_laws import IrreversibilityLaws
from ..schemas.event_schema import ManipulationEvent
from ..schemas.state_schema import StateVector

logger = logging.getLogger(__name__)


class PerceptionWarfareModule:
    """Models information manipulation and epistemic attacks.
    
    Tracks manipulation campaigns, reality fragmentation, and epistemic collapse.
    """

    def __init__(self, laws: IrreversibilityLaws):
        """Initialize perception warfare module.
        
        Args:
            laws: Irreversibility laws instance
        """
        self.laws = laws

        # Campaign tracking
        self.active_campaigns: list[dict[str, Any]] = []
        self.completed_campaigns: list[dict[str, Any]] = []

        # Manipulation history
        self.manipulation_history: list[dict[str, Any]] = []

        # Reality fragmentation tracking
        self.reality_fragments = 1  # Number of divergent realities
        self.consensus_level = 1.0  # Degree of shared reality

        # Information environment
        self.information_quality = 0.8
        self.noise_level = 0.2

        logger.info("Perception warfare module initialized")

    def launch_manipulation_campaign(
        self,
        campaign_type: str = "misinformation",
        target_reach: float = 0.5,
        sophistication: float = 0.5,
        duration: int = 10,
    ) -> str:
        """Launch information manipulation campaign.
        
        Args:
            campaign_type: Type of manipulation
            target_reach: Target fraction of population
            sophistication: Detection difficulty
            duration: Campaign duration in ticks
            
        Returns:
            Campaign ID
        """
        campaign_id = f"campaign_{len(self.active_campaigns) + len(self.completed_campaigns) + 1}"

        campaign = {
            "campaign_id": campaign_id,
            "campaign_type": campaign_type,
            "target_reach": target_reach,
            "sophistication": sophistication,
            "duration": duration,
            "ticks_remaining": duration,
            "current_reach": 0.0,
        }

        self.active_campaigns.append(campaign)

        logger.info(f"Launched manipulation campaign: {campaign_id}, type={campaign_type}, reach={target_reach:.2f}")

        return campaign_id

    def process_active_campaigns(self, state: StateVector) -> list[ManipulationEvent]:
        """Process active manipulation campaigns for this tick.
        
        Args:
            state: Current state vector
            
        Returns:
            List of manipulation events generated
        """
        events = []
        campaigns_to_complete = []

        for campaign in self.active_campaigns:
            campaign["ticks_remaining"] -= 1

            # Gradually increase reach
            reach_increment = campaign["target_reach"] / campaign["duration"]
            campaign["current_reach"] = min(campaign["target_reach"], campaign["current_reach"] + reach_increment)

            # Generate manipulation event
            from ..schemas.event_schema import EventType

            event = ManipulationEvent(
                event_type=EventType.MANIPULATION,
                timestamp=state.timestamp,
                source="perception_warfare",
                description=f"Manipulation campaign {campaign['campaign_id']}: {campaign['campaign_type']}",
                manipulation_type=campaign["campaign_type"],
                reach=campaign["current_reach"],
                sophistication=campaign["sophistication"],
            )

            events.append(event)

            # Apply epistemic damage
            self.laws.apply_manipulation_impact(
                state,
                reach=campaign["current_reach"],
                sophistication=campaign["sophistication"],
            )

            # Record in history
            self.manipulation_history.append({
                "timestamp": state.timestamp,
                "campaign_id": campaign["campaign_id"],
                "type": campaign["campaign_type"],
                "reach": campaign["current_reach"],
                "sophistication": campaign["sophistication"],
                "event_id": event.event_id,
            })

            # Check if campaign complete
            if campaign["ticks_remaining"] <= 0:
                campaigns_to_complete.append(campaign)

        # Move completed campaigns
        for campaign in campaigns_to_complete:
            self.active_campaigns.remove(campaign)
            self.completed_campaigns.append(campaign)
            logger.info(f"Campaign completed: {campaign['campaign_id']}")

        return events

    def calculate_reality_fragmentation(self, state: StateVector) -> int:
        """Calculate number of divergent reality fragments.
        
        Args:
            state: Current state vector
            
        Returns:
            Number of reality fragments
        """
        # Base fragments from epistemic confidence
        if state.epistemic_confidence.value > 0.7:
            self.reality_fragments = 1
        elif state.epistemic_confidence.value > 0.5:
            self.reality_fragments = 2
        elif state.epistemic_confidence.value > 0.3:
            self.reality_fragments = 3 + int((0.5 - state.epistemic_confidence.value) * 10)
        else:
            self.reality_fragments = 5 + int((0.3 - state.epistemic_confidence.value) * 20)

        # Manipulation campaigns increase fragmentation
        active_campaigns_factor = len(self.active_campaigns)
        self.reality_fragments += active_campaigns_factor

        logger.debug(f"Reality fragments: {self.reality_fragments}")

        return self.reality_fragments

    def calculate_consensus_level(self, state: StateVector) -> float:
        """Calculate level of shared reality consensus.
        
        Args:
            state: Current state vector
            
        Returns:
            Consensus level (0.0 to 1.0)
        """
        # Base consensus from epistemic confidence
        self.consensus_level = state.epistemic_confidence.value

        # Reduce by reality fragmentation
        fragmentation_penalty = (self.reality_fragments - 1) * 0.1
        self.consensus_level -= fragmentation_penalty

        # Recent manipulation reduces consensus
        recent_manipulation = len([m for m in self.manipulation_history[-20:]])
        manipulation_penalty = min(recent_manipulation * 0.02, 0.3)
        self.consensus_level -= manipulation_penalty

        self.consensus_level = max(0.0, min(1.0, self.consensus_level))

        logger.debug(f"Reality consensus: {self.consensus_level:.4f}")

        return self.consensus_level

    def update_information_environment(self, state: StateVector) -> None:
        """Update information environment quality and noise.
        
        Args:
            state: Current state vector
        """
        # Information quality tracks epistemic confidence
        self.information_quality = state.epistemic_confidence.value * 0.9

        # Noise level inversely related to quality
        self.noise_level = 1.0 - self.information_quality

        # Active campaigns increase noise
        if self.active_campaigns:
            campaign_noise = sum(c["sophistication"] * c["current_reach"] for c in self.active_campaigns) / len(self.active_campaigns)
            self.noise_level = min(1.0, self.noise_level + campaign_noise * 0.3)
            self.information_quality = 1.0 - self.noise_level

        logger.debug(f"Information environment: quality={self.information_quality:.3f}, noise={self.noise_level:.3f}")

    def check_epistemic_collapse(self, state: StateVector) -> bool:
        """Check if epistemic collapse has occurred.
        
        Args:
            state: Current state vector
            
        Returns:
            True if epistemic collapse detected
        """
        threshold = self.laws.config.epistemic_collapse_threshold

        if state.epistemic_confidence.value < threshold:
            logger.critical(f"EPISTEMIC COLLAPSE: confidence {state.epistemic_confidence.value:.4f} < threshold {threshold:.4f}")
            return True

        # Also check for extreme fragmentation
        if self.reality_fragments > 10:
            logger.critical(f"EPISTEMIC COLLAPSE: extreme fragmentation {self.reality_fragments} fragments")
            return True

        return False

    def apply_perception_warfare_dynamics(self, state: StateVector) -> dict[str, Any]:
        """Apply perception warfare dynamics for this tick.
        
        Args:
            state: Current state vector
            
        Returns:
            Dictionary with dynamics results
        """
        # Process active campaigns
        manipulation_events = self.process_active_campaigns(state)

        # Update metrics
        fragments = self.calculate_reality_fragmentation(state)
        consensus = self.calculate_consensus_level(state)
        self.update_information_environment(state)

        # Check for epistemic collapse
        epistemic_collapse = self.check_epistemic_collapse(state)

        # Randomly launch new campaigns based on state
        campaign_launched = False
        new_campaign_id = None

        if not epistemic_collapse:
            # More campaigns likely when trust/legitimacy low
            campaign_prob = 0.1 + (1.0 - state.trust.value) * 0.2 + (1.0 - state.legitimacy.value) * 0.15

            if random.random() < campaign_prob:
                campaign_type = random.choice(["misinformation", "disinformation", "gaslighting"])
                target_reach = random.uniform(0.3, 0.8)
                sophistication = random.uniform(0.4, 0.9)
                duration = random.randint(5, 15)

                new_campaign_id = self.launch_manipulation_campaign(
                    campaign_type,
                    target_reach,
                    sophistication,
                    duration,
                )
                campaign_launched = True

        return {
            "manipulation_events": len(manipulation_events),
            "active_campaigns": len(self.active_campaigns),
            "reality_fragments": fragments,
            "consensus_level": consensus,
            "information_quality": self.information_quality,
            "noise_level": self.noise_level,
            "epistemic_collapse": epistemic_collapse,
            "campaign_launched": campaign_launched,
            "new_campaign_id": new_campaign_id,
        }

    def get_summary(self) -> dict[str, Any]:
        """Get module summary.
        
        Returns:
            Dictionary with module state
        """
        return {
            "active_campaigns": len(self.active_campaigns),
            "completed_campaigns": len(self.completed_campaigns),
            "total_manipulation_events": len(self.manipulation_history),
            "reality_fragments": self.reality_fragments,
            "consensus_level": self.consensus_level,
            "information_quality": self.information_quality,
            "noise_level": self.noise_level,
        }

    def reset(self) -> None:
        """Reset module to initial state."""
        self.__init__(self.laws)
        logger.info("Perception warfare module reset")
