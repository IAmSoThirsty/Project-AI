"""
Layer 4: Bayesian Claim Engine for PROJECT ATLAS Ω

Implements Bayesian legitimacy scoring for claims with evidence-based weighting,
driver dependency tracking, and automatic agency penalties.

Formula: P = normalize(EL × WDP × StackPenalty)

Where:
- EL = Evidence Legitimacy
- WDP = Weighted Driver Posterior
- StackPenalty = Stack-specific penalty multiplier

Production-grade with full audit logging and constitutional enforcement.
"""

import logging
import math
from datetime import datetime
from enum import Enum
from typing import Any

from atlas.audit.trail import AuditCategory, AuditLevel, get_audit_trail
from atlas.config.loader import get_config_loader
from atlas.governance.constitutional_kernel import get_constitutional_kernel

logger = logging.getLogger(__name__)


class ClaimType(Enum):
    """Types of claims in the system."""
    FACTUAL = "factual"
    PREDICTIVE = "predictive"
    AGENCY = "agency"  # Intent/conspiracy claims - automatically penalized
    CAUSAL = "causal"
    CORRELATIONAL = "correlational"
    NORMATIVE = "normative"


class EvidenceTier(Enum):
    """Evidence quality tiers."""
    TIER_A = "TierA"  # Peer-reviewed / official audited
    TIER_B = "TierB"  # Government statistical archives
    TIER_C = "TierC"  # Reputable institutional reporting
    TIER_D = "TierD"  # Media / secondary analysis


class BayesianClaimEngine:
    """
    Layer 4: Bayesian Claim Engine
    
    Calculates probabilistic legitimacy of claims using evidence-based Bayesian
    inference with automatic penalties for low-quality evidence or agency claims.
    """

    def __init__(self):
        """Initialize the Bayesian claim engine."""
        self.audit = get_audit_trail()
        self.config = get_config_loader()
        self.kernel = get_constitutional_kernel()

        # Load penalty configuration
        penalties_config = self.config.get("penalties")
        self.stack_penalties = self._load_stack_penalties(penalties_config)

        # Evidence tier weights
        self.tier_weights = {
            EvidenceTier.TIER_A: 1.0,
            EvidenceTier.TIER_B: 0.85,
            EvidenceTier.TIER_C: 0.65,
            EvidenceTier.TIER_D: 0.40
        }

        # Agency penalty multiplier
        self.agency_penalty_multiplier = 0.5  # Halves posterior for agency claims

        logger.info("BayesianClaimEngine initialized")

        self.audit.log_event(
            category=AuditCategory.SYSTEM,
            level=AuditLevel.INFORMATIONAL,
            operation="bayesian_engine_initialized",
            actor="BAYESIAN_ENGINE",
            details={
                "tier_weights": {k.value: v for k, v in self.tier_weights.items()},
                "agency_penalty": self.agency_penalty_multiplier
            }
        )

    def _load_stack_penalties(self, penalties_config: dict[str, Any]) -> dict[str, float]:
        """Load stack-specific penalty multipliers."""
        stack_penalties_config = penalties_config.get("stack_penalties", {})

        penalties = {
            "RS": 1.0,  # Reality Stack - no penalty
            "TS-0": 1.0,  # Timeline stacks - no penalty
            "TS-1": 1.0,
            "TS-2": 0.95,  # Slight uncertainty penalty for far projections
            "TS-3": 0.90,
            "SS": 0.0  # Simulation Stack - claims have no legitimacy
        }

        return penalties

    def calculate_claim_posterior(self,
                                   claim: dict[str, Any],
                                   evidence: list[dict[str, Any]],
                                   driver_context: dict[str, float],
                                   stack: str = "RS") -> float:
        """
        Calculate Bayesian posterior for a claim.
        
        Formula: P = normalize(EL × WDP × StackPenalty)
        
        Args:
            claim: Claim object
            evidence: List of evidence objects supporting the claim
            driver_context: Current driver values relevant to the claim
            stack: Stack context (RS, TS-*, SS)
            
        Returns:
            Posterior probability [0, 1]
        """
        logger.debug("Calculating posterior for claim %s", claim.get('id', 'unknown'))

        # 1. Calculate Evidence Legitimacy (EL)
        evidence_legitimacy = self._calculate_evidence_legitimacy(evidence)

        # 2. Calculate Weighted Driver Posterior (WDP)
        driver_posterior = self._calculate_driver_posterior(claim, driver_context)

        # 3. Apply stack penalty
        stack_penalty = self.stack_penalties.get(stack, 1.0)

        # 4. Apply agency penalty if applicable
        agency_penalty = 1.0
        claim_type = claim.get("claim_type", "")
        if claim_type == ClaimType.AGENCY.value or claim_type == "AGENCY":
            # Check if TierA/B evidence exists
            has_high_tier = any(
                ev.get("tier") in ["TierA", "TierB"]
                for ev in evidence
            )

            if not has_high_tier:
                agency_penalty = self.agency_penalty_multiplier

                self.audit.log_event(
                    category=AuditCategory.VALIDATION,
                    level=AuditLevel.HIGH_PRIORITY,
                    operation="agency_penalty_applied",
                    actor="BAYESIAN_ENGINE",
                    details={
                        "claim_id": claim.get("id"),
                        "reason": "Agency claim without TierA/B evidence",
                        "penalty_multiplier": agency_penalty
                    }
                )

        # 5. Calculate raw posterior
        raw_posterior = evidence_legitimacy * driver_posterior * stack_penalty * agency_penalty

        # 6. Normalize to [0, 1]
        posterior = self._normalize(raw_posterior)

        # 7. Apply decay if claim is old
        posterior = self._apply_temporal_decay(posterior, claim)

        # 8. Log calculation
        self.audit.log_event(
            category=AuditCategory.OPERATION,
            level=AuditLevel.STANDARD,
            operation="claim_posterior_calculated",
            actor="BAYESIAN_ENGINE",
            details={
                "claim_id": claim.get("id"),
                "claim_type": claim_type,
                "evidence_legitimacy": evidence_legitimacy,
                "driver_posterior": driver_posterior,
                "stack_penalty": stack_penalty,
                "agency_penalty": agency_penalty,
                "raw_posterior": raw_posterior,
                "final_posterior": posterior,
                "stack": stack
            }
        )

        return posterior

    def _calculate_evidence_legitimacy(self, evidence: list[dict[str, Any]]) -> float:
        """
        Calculate evidence legitimacy score.
        
        Args:
            evidence: List of evidence objects
            
        Returns:
            Evidence legitimacy score [0, 1]
        """
        if not evidence:
            return 0.1  # Minimal legitimacy without evidence

        # Weight evidence by tier
        weighted_sum = 0.0
        total_weight = 0.0

        for ev in evidence:
            tier_str = ev.get("tier", "TierD")

            # Convert string to enum
            try:
                tier = EvidenceTier(tier_str)
            except ValueError:
                tier = EvidenceTier.TIER_D  # Default to lowest

            weight = self.tier_weights[tier]
            confidence = ev.get("confidence", 0.5)

            weighted_sum += weight * confidence
            total_weight += weight

        if total_weight == 0:
            return 0.1

        # Average weighted evidence
        legitimacy = weighted_sum / len(evidence)

        # Bonus for multiple high-tier sources
        tier_a_count = sum(1 for ev in evidence if ev.get("tier") == "TierA")
        if tier_a_count >= 2:
            legitimacy *= 1.1  # 10% bonus for multiple peer-reviewed sources

        # Cap at 1.0
        return min(legitimacy, 1.0)

    def _calculate_driver_posterior(self,
                                     claim: dict[str, Any],
                                     driver_context: dict[str, float]) -> float:
        """
        Calculate driver-weighted posterior.
        
        Measures how well the claim aligns with current driver values.
        
        Args:
            claim: Claim object
            driver_context: Current driver values
            
        Returns:
            Driver posterior [0, 1]
        """
        driver_dependencies = claim.get("driver_dependencies", [])

        if not driver_dependencies:
            return 0.7  # Neutral if no driver dependencies

        # Calculate alignment with each driver
        alignments = []

        for dep in driver_dependencies:
            driver_name = dep.get("driver")
            expected_range = dep.get("expected_range", [0.0, 1.0])

            if driver_name in driver_context:
                actual_value = driver_context[driver_name]

                # Check if actual falls within expected range
                min_val, max_val = expected_range

                if min_val <= actual_value <= max_val:
                    # Perfect alignment
                    alignment = 1.0
                else:
                    # Calculate distance from range
                    if actual_value < min_val:
                        distance = min_val - actual_value
                    else:
                        distance = actual_value - max_val

                    # Exponential decay of alignment with distance
                    alignment = math.exp(-distance * 2.0)

                alignments.append(alignment)

        if not alignments:
            return 0.7

        # Average alignment across all driver dependencies
        return sum(alignments) / len(alignments)

    def _normalize(self, value: float) -> float:
        """Normalize value to [0, 1] range."""
        return max(0.0, min(1.0, value))

    def _apply_temporal_decay(self, posterior: float, claim: dict[str, Any]) -> float:
        """
        Apply temporal decay to posterior based on claim age.
        
        Args:
            posterior: Current posterior
            claim: Claim object with timestamp
            
        Returns:
            Decayed posterior
        """
        decay_half_life = claim.get("decay_half_life")

        if not decay_half_life:
            return posterior  # No decay

        timestamp_str = claim.get("timestamp")
        if not timestamp_str:
            return posterior

        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            age_days = (datetime.utcnow() - timestamp.replace(tzinfo=None)).days

            # Exponential decay: P(t) = P_0 * exp(-ln(2) * t / half_life)
            decay_factor = math.exp(-math.log(2) * age_days / decay_half_life)

            return posterior * decay_factor

        except Exception as e:
            logger.warning("Error applying temporal decay: %s", e)
            return posterior

    def process_claim(self,
                      claim: dict[str, Any],
                      evidence: list[dict[str, Any]],
                      driver_context: dict[str, float],
                      stack: str = "RS") -> dict[str, Any]:
        """
        Process a claim through the Bayesian engine.
        
        Args:
            claim: Claim object
            evidence: Supporting evidence
            driver_context: Current driver values
            stack: Stack context
            
        Returns:
            Processed claim with posterior probability
        """
        # Calculate posterior
        posterior = self.calculate_claim_posterior(claim, evidence, driver_context, stack)

        # Update claim object
        if "bayesian_analysis" not in claim:
            claim["bayesian_analysis"] = {}

        claim["bayesian_analysis"]["posterior"] = posterior
        claim["bayesian_analysis"]["calculated_at"] = datetime.utcnow().isoformat()
        claim["bayesian_analysis"]["stack"] = stack
        claim["bayesian_analysis"]["evidence_count"] = len(evidence)

        # Add evidence vector for reference
        claim["evidence_vector"] = [
            {
                "source": ev.get("source", "unknown"),
                "tier": ev.get("tier", "TierD"),
                "confidence": ev.get("confidence", 0.5)
            }
            for ev in evidence
        ]

        return claim

    def influence_agent_perception(self,
                                    claims: list[dict[str, Any]],
                                    agent_state: dict[str, Any]) -> dict[str, Any]:
        """
        Update agent perception based on claim posteriors.
        
        Claims with high posterior influence agent's worldview.
        
        Args:
            claims: List of processed claims
            agent_state: Agent state object
            
        Returns:
            Updated agent state
        """
        if "perception" not in agent_state:
            agent_state["perception"] = {}

        perception = agent_state["perception"]

        for claim in claims:
            posterior = claim.get("bayesian_analysis", {}).get("posterior", 0.0)

            # Only claims with posterior > 0.5 influence perception
            if posterior > 0.5:
                category = claim.get("category", "general")

                if category not in perception:
                    perception[category] = []

                perception[category].append({
                    "claim_id": claim.get("id"),
                    "statement": claim.get("statement", "")[:100],  # Truncate
                    "posterior": posterior,
                    "influence_weight": posterior  # Direct mapping for now
                })

        # Update timestamp
        agent_state["perception_updated_at"] = datetime.utcnow().isoformat()

        return agent_state

    def get_high_posterior_claims(self,
                                   claims: list[dict[str, Any]],
                                   threshold: float = 0.7) -> list[dict[str, Any]]:
        """
        Get claims with posterior above threshold.
        
        Args:
            claims: List of claims
            threshold: Minimum posterior
            
        Returns:
            Filtered list of high-confidence claims
        """
        return [
            claim for claim in claims
            if claim.get("bayesian_analysis", {}).get("posterior", 0.0) >= threshold
        ]


# Global instance
_global_bayesian_engine: BayesianClaimEngine | None = None


def get_bayesian_engine() -> BayesianClaimEngine:
    """Get the global Bayesian claim engine instance."""
    global _global_bayesian_engine

    if _global_bayesian_engine is None:
        _global_bayesian_engine = BayesianClaimEngine()

    return _global_bayesian_engine


def reset_bayesian_engine() -> None:
    """Reset the global engine (for testing)."""
    global _global_bayesian_engine
    _global_bayesian_engine = None


if __name__ == "__main__":
    # Test Bayesian claim engine
    import json
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    engine = BayesianClaimEngine()

    # Test claim
    claim = {
        "id": "CLM-TEST-001",
        "statement": "Economic indicator X is rising",
        "claim_type": "factual",
        "timestamp": datetime.utcnow().isoformat(),
        "driver_dependencies": [
            {
                "driver": "economic_power",
                "expected_range": [0.6, 0.9]
            }
        ]
    }

    # Evidence
    evidence = [
        {"tier": "TierA", "source": "IMF Report 2026", "confidence": 0.95},
        {"tier": "TierB", "source": "Federal Reserve Data", "confidence": 0.90}
    ]

    # Driver context
    drivers = {
        "economic_power": 0.75,
        "political_influence": 0.65
    }

    # Process claim
    processed_claim = engine.process_claim(claim, evidence, drivers, "RS")

    print("Processed Claim:")
    print(json.dumps(processed_claim, indent=2))

    print(f"\nPosterior: {processed_claim['bayesian_analysis']['posterior']:.3f}")
