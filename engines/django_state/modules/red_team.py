"""Red team module.

Adversarial testing with black vault SHA-256 fingerprinting and entropy delta calculation.
"""

import logging
import math
import random
from typing import Any

from ..kernel.irreversibility_laws import IrreversibilityLaws
from ..schemas.event_schema import Event, RedTeamEvent
from ..schemas.state_schema import StateVector

logger = logging.getLogger(__name__)


class RedTeamModule:
    """Adversarial red team operations with entropy tracking.

    Implements black vault event deduplication, entropy delta calculation,
    attack surface mapping, and vulnerability tracking.
    """

    def __init__(self, laws: IrreversibilityLaws, black_vault_enabled: bool = True):
        """Initialize red team module.

        Args:
            laws: Irreversibility laws instance
            black_vault_enabled: Whether to enable black vault
        """
        self.laws = laws
        self.black_vault_enabled = black_vault_enabled

        # Black vault (SHA-256 fingerprints of seen events)
        self.black_vault: set[str] = set()

        # Attack history
        self.attack_history: list[dict[str, Any]] = []
        self.successful_attacks = 0
        self.failed_attacks = 0

        # Vulnerability tracking
        self.known_vulnerabilities: dict[str, dict[str, Any]] = {}
        self.exploited_vulnerabilities: set[str] = set()

        # Entropy tracking
        self.entropy_history: list[tuple[float, float]] = []  # (timestamp, entropy)

        # Attack surface
        self.attack_vectors = [
            "trust_attack",
            "epistemic_attack",
            "institutional_attack",
            "social_cohesion_attack",
            "legitimacy_attack",
            "moral_injury_attack",
        ]

        logger.info(
            "Red team module initialized (black vault: %s)", black_vault_enabled
        )

    def calculate_state_entropy(self, state: StateVector) -> float:
        """Calculate Shannon entropy of state vector.

        Higher entropy indicates more disorder/uncertainty in the system.

        Args:
            state: Current state vector

        Returns:
            Entropy value
        """
        # Collect state dimensions as probability distribution
        dimensions = [
            state.trust.value,
            state.legitimacy.value,
            state.kindness.value,
            state.moral_injury.value,
            state.epistemic_confidence.value,
            state.social_cohesion,
            state.governance_capacity,
            state.reality_consensus,
        ]

        # Normalize to probability distribution
        total = sum(dimensions) + 1e-10  # Avoid division by zero
        probabilities = [d / total for d in dimensions]

        # Calculate Shannon entropy: H = -Σ p(x) * log2(p(x))
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log2(p)

        logger.debug("State entropy: %s", entropy)

        return entropy

    def calculate_entropy_delta(
        self, state_before: StateVector, state_after: StateVector
    ) -> float:
        """Calculate entropy change from attack.

        Δentropy = H(state_after) - H(state_before)

        Args:
            state_before: State before attack
            state_after: State after attack

        Returns:
            Entropy delta
        """
        entropy_before = self.calculate_state_entropy(state_before)
        entropy_after = self.calculate_state_entropy(state_after)

        delta = entropy_after - entropy_before

        logger.info(
            "Entropy delta: %s (before: %s, after: %s)",
            delta,
            entropy_before,
            entropy_after,
        )

        return delta

    def fingerprint_event(self, event: Event) -> str:
        """Generate SHA-256 fingerprint for event.

        Args:
            event: Event to fingerprint

        Returns:
            SHA-256 hex digest
        """
        return event.fingerprint

    def check_black_vault(self, event: Event) -> bool:
        """Check if event fingerprint exists in black vault.

        Args:
            event: Event to check

        Returns:
            True if event is in black vault (duplicate)
        """
        if not self.black_vault_enabled:
            return False

        fingerprint = self.fingerprint_event(event)
        return fingerprint in self.black_vault

    def add_to_black_vault(self, event: Event) -> None:
        """Add event fingerprint to black vault.

        Args:
            event: Event to add
        """
        if not self.black_vault_enabled:
            return

        fingerprint = self.fingerprint_event(event)
        self.black_vault.add(fingerprint)
        logger.debug(
            "Added to black vault: %s... (vault size: %s)",
            fingerprint[:16],
            len(self.black_vault),
        )

    def identify_vulnerability(
        self,
        state: StateVector,
        vulnerability_type: str,
        severity: float,
        exploitability: float,
    ) -> str:
        """Identify and record a vulnerability.

        Args:
            state: Current state vector
            vulnerability_type: Type of vulnerability
            severity: How severe (0.0 to 1.0)
            exploitability: How easy to exploit (0.0 to 1.0)

        Returns:
            Vulnerability ID
        """
        vuln_id = f"vuln_{len(self.known_vulnerabilities) + 1}"

        self.known_vulnerabilities[vuln_id] = {
            "vulnerability_id": vuln_id,
            "type": vulnerability_type,
            "severity": severity,
            "exploitability": exploitability,
            "discovered_at": state.timestamp,
            "exploited": False,
        }

        logger.info(
            "Vulnerability identified: %s, type=%s, severity=%s",
            vuln_id,
            vulnerability_type,
            severity,
        )

        return vuln_id

    def scan_attack_surface(self, state: StateVector) -> list[dict[str, Any]]:
        """Scan state for vulnerabilities.

        Args:
            state: Current state vector

        Returns:
            List of identified vulnerabilities
        """
        vulnerabilities = []

        # Low trust is vulnerability
        if state.trust.value < 0.4:
            vuln_id = self.identify_vulnerability(
                state,
                "low_trust",
                severity=(0.4 - state.trust.value) * 2.5,
                exploitability=0.8,
            )
            vulnerabilities.append(self.known_vulnerabilities[vuln_id])

        # Low legitimacy is vulnerability
        if state.legitimacy.value < 0.3:
            vuln_id = self.identify_vulnerability(
                state,
                "low_legitimacy",
                severity=(0.3 - state.legitimacy.value) * 3.0,
                exploitability=0.7,
            )
            vulnerabilities.append(self.known_vulnerabilities[vuln_id])

        # Low epistemic confidence is vulnerability
        if state.epistemic_confidence.value < 0.4:
            vuln_id = self.identify_vulnerability(
                state,
                "low_epistemic_confidence",
                severity=(0.4 - state.epistemic_confidence.value) * 2.5,
                exploitability=0.9,
            )
            vulnerabilities.append(self.known_vulnerabilities[vuln_id])

        # High moral injury is vulnerability
        if state.moral_injury.value > 0.6:
            vuln_id = self.identify_vulnerability(
                state,
                "high_moral_injury",
                severity=state.moral_injury.value,
                exploitability=0.6,
            )
            vulnerabilities.append(self.known_vulnerabilities[vuln_id])

        # Near collapse states are critical vulnerabilities
        if state.in_collapse:
            vuln_id = self.identify_vulnerability(
                state,
                "collapse_state",
                severity=1.0,
                exploitability=1.0,
            )
            vulnerabilities.append(self.known_vulnerabilities[vuln_id])

        logger.info(
            "Attack surface scan: %s vulnerabilities identified", len(vulnerabilities)
        )

        return vulnerabilities

    def generate_attack_event(
        self,
        state: StateVector,
        attack_type: str,
        attack_vector: str = "direct",
        vulnerability: str | None = None,
    ) -> RedTeamEvent:
        """Generate red team attack event.

        Args:
            state: Current state vector
            attack_type: Type of attack
            attack_vector: Attack vector
            vulnerability: Optional vulnerability being exploited

        Returns:
            RedTeamEvent instance
        """
        # Calculate expected entropy delta
        state_copy = state.copy()

        event = RedTeamEvent(
            timestamp=state.timestamp,
            source="red_team",
            description=f"Red team attack: {attack_type} via {attack_vector}",
            attack_type=attack_type,
            attack_vector=attack_vector,
            vulnerability_exploited=vulnerability,
        )

        # Check black vault
        if self.check_black_vault(event):
            logger.warning(
                "Attack event blocked by black vault: %s...", event.fingerprint[:16]
            )
            self.failed_attacks += 1
            return event

        # Add to black vault
        self.add_to_black_vault(event)

        # Calculate impacts
        impacts = event.calculate_multi_dimensional_impact()

        # Apply impacts to copy for entropy calculation
        for dimension, impact in impacts.items():
            if dimension == "trust":
                state_copy.trust.update(impact, state.timestamp)
            elif dimension == "legitimacy":
                state_copy.legitimacy.update(impact, state.timestamp)
            elif dimension == "kindness":
                state_copy.kindness.update(impact, state.timestamp)
            elif dimension == "epistemic_confidence":
                state_copy.epistemic_confidence.update(impact, state.timestamp)

        # Calculate entropy delta
        entropy_delta = self.calculate_entropy_delta(state, state_copy)
        event.record_entropy_delta(entropy_delta)

        # Record attack
        self.attack_history.append(
            {
                "timestamp": state.timestamp,
                "attack_type": attack_type,
                "attack_vector": attack_vector,
                "vulnerability": vulnerability,
                "entropy_delta": entropy_delta,
                "event_id": event.event_id,
                "fingerprint": event.fingerprint,
            }
        )

        self.successful_attacks += 1

        logger.info(
            "Red team attack executed: %s, entropy_delta=%s", attack_type, entropy_delta
        )

        return event

    def execute_attack(
        self, state: StateVector, attack_type: str | None = None
    ) -> RedTeamEvent:
        """Execute red team attack on state.

        Args:
            state: Current state vector
            attack_type: Optional specific attack type (random if None)

        Returns:
            RedTeamEvent instance
        """
        # Scan for vulnerabilities
        vulnerabilities = self.scan_attack_surface(state)

        # Select vulnerability to exploit
        vulnerability_id = None
        if vulnerabilities:
            vuln = random.choice(vulnerabilities)
            vulnerability_id = vuln["vulnerability_id"]
            self.exploited_vulnerabilities.add(vulnerability_id)
            self.known_vulnerabilities[vulnerability_id]["exploited"] = True

        # Select attack type
        if attack_type is None:
            attack_type = random.choice(self.attack_vectors)

        # Select attack vector
        attack_vector = random.choice(
            ["direct", "indirect", "cascading", "coordinated"]
        )

        # Generate and execute attack
        event = self.generate_attack_event(
            state, attack_type, attack_vector, vulnerability_id
        )

        # Apply attack impacts to actual state
        impacts = event.calculate_multi_dimensional_impact()
        for dimension, impact in impacts.items():
            if dimension == "trust":
                self.laws.apply_betrayal_impact(state, severity=abs(impact) * 2)
            elif dimension == "legitimacy":
                self.laws.apply_legitimacy_erosion(
                    state, broken_promises=1, failures=1, visibility=0.8
                )
            elif dimension == "kindness":
                state.kindness.update(impact, state.timestamp)
            elif dimension == "epistemic_confidence":
                self.laws.apply_manipulation_impact(
                    state, reach=0.6, sophistication=0.7
                )

        # Record entropy
        entropy = self.calculate_state_entropy(state)
        self.entropy_history.append((state.timestamp, entropy))

        return event

    def get_summary(self) -> dict[str, Any]:
        """Get module summary.

        Returns:
            Dictionary with module state
        """
        return {
            "black_vault_enabled": self.black_vault_enabled,
            "black_vault_size": len(self.black_vault),
            "total_attacks": len(self.attack_history),
            "successful_attacks": self.successful_attacks,
            "failed_attacks": self.failed_attacks,
            "known_vulnerabilities": len(self.known_vulnerabilities),
            "exploited_vulnerabilities": len(self.exploited_vulnerabilities),
            "attack_vectors": self.attack_vectors,
        }

    def reset(self) -> None:
        """Reset module to initial state."""
        black_vault_enabled = self.black_vault_enabled
        self.__init__(self.laws, black_vault_enabled)
        logger.info("Red team module reset")
