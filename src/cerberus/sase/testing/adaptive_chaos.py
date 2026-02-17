"""
SASE Adaptive Chaos Scenarios

Models real-world adversarial adaptation, not just static distributions.

BLIND SPOTS IN STATIC CHAOS:
- Low-and-slow attacks
- Mixed benign-malicious sequences  
- Gradual escalation patterns
- Infrastructure pivots (Tor → VPS)
- Delayed credential probes
"""

import random
import time
from dataclasses import dataclass
from typing import List

from .chaos_suite import SyntheticEvent


@dataclass
class AdaptiveSequence:
    """Sequence of related events showing adversarial adaptation"""

    events: List[SyntheticEvent]
    sequence_type: str
    description: str


class AdaptiveAdversaryGenerator:
    """
    Generates adaptive adversary scenarios for chaos testing

    Real adversaries:
    - Probe slowly to avoid detection
    - Mix attack and benign behavior
    - Pivot infrastructure mid-attack
    - Escalate gradually over time
    """

    def __init__(self, seed: int = 42):
        random.seed(seed)

    def generate_low_and_slow_credential_probe(self) -> AdaptiveSequence:
        """
        Low-and-Slow Attack: Credential probe with 12h delay between attempts

        Pattern:
        - Benign activity for 10 events
        - Single credential probe (Tor)
        - 12h delay (simulated)
        - Another probe (different Tor exit)
        - 12h delay
        - Final probe (VPS pivot)

        GOAL: Test HMM state transition across long timespan
        """
        events = []

        # Phase 1: Benign reconnaissance (10 events)
        for _ in range(10):
            events.append(self._benign_event())

        # Phase 2: First credential probe (Tor)
        events.append(self._credential_probe(is_tor=True, timestamp_offset=0))

        # Phase 3: 12h delay marker
        events.append(self._delay_marker(hours=12))

        # Phase 4: Second probe (different Tor exit)
        events.append(self._credential_probe(is_tor=True, timestamp_offset=12 * 3600))

        # Phase 5: 12h delay
        events.append(self._delay_marker(hours=12))

        # Phase 6: Infrastructure pivot to VPS
        events.append(
            self._credential_probe(
                is_tor=False, is_vps=True, timestamp_offset=24 * 3600
            )
        )

        return AdaptiveSequence(
            events=events,
            sequence_type="low_and_slow",
            description="Credential harvesting with 12h delays and Tor→VPS pivot",
        )

    def generate_gradual_escalation(self) -> AdaptiveSequence:
        """
        Gradual Escalation: Start benign, slowly increase suspicion

        Pattern:
        - 20 legitimate API calls (residential IP)
        - 10 API calls with slightly elevated rate
        - 5 calls with token anomalies
        - 3 calls with token reuse
        - Containment should trigger only at final phase

        GOAL: Test confidence accumulation over time
        """
        events = []

        # Phase 1: Legitimate baseline (20 events)
        base_ip = self._random_ip()
        for i in range(20):
            events.append(
                SyntheticEvent(
                    event_type="api_call",
                    is_malicious=False,
                    source_ip=base_ip,
                    asn=7922,  # Comcast
                    country="US",
                    is_tor=False,
                    is_vpn=False,
                    token_reuse=False,
                    confidence_expected=0.05,
                )
            )

        # Phase 2: Elevated rate (10 events, same IP)
        for i in range(10):
            events.append(
                SyntheticEvent(
                    event_type="api_call",
                    is_malicious=True,  # Now malicious
                    source_ip=base_ip,
                    asn=7922,
                    country="US",
                    is_tor=False,
                    is_vpn=False,
                    token_reuse=False,
                    confidence_expected=0.25,  # Slightly elevated
                )
            )

        # Phase 3: Token anomalies (5 events)
        for i in range(5):
            events.append(
                SyntheticEvent(
                    event_type="token_probe",
                    is_malicious=True,
                    source_ip=base_ip,
                    asn=7922,
                    country="US",
                    is_tor=False,
                    is_vpn=False,
                    token_reuse=random.random() < 0.5,
                    confidence_expected=0.50,  # Moderate
                )
            )

        # Phase 4: Clear token reuse (3 events)
        for i in range(3):
            events.append(
                SyntheticEvent(
                    event_type="token_probe",
                    is_malicious=True,
                    source_ip=base_ip,
                    asn=7922,
                    country="US",
                    is_tor=False,
                    is_vpn=False,
                    token_reuse=True,
                    confidence_expected=0.80,  # High - should trigger containment
                )
            )

        return AdaptiveSequence(
            events=events,
            sequence_type="gradual_escalation",
            description="Benign→suspicious→malicious escalation from same IP",
        )

    def generate_infrastructure_pivot(self) -> AdaptiveSequence:
        """
        Infrastructure Pivot: Tor → VPS → Residential Proxy

        Pattern:
        - 3 probes from Tor
        - Pivot to AWS VPS
        - 3 probes from VPS
        - Pivot to residential proxy (botnet)
        - 3 probes from residential

        GOAL: Test HMM adaptation to infrastructure changes
        """
        events = []

        # Phase 1: Tor exit nodes (3 different exits)
        for i in range(3):
            events.append(
                SyntheticEvent(
                    event_type="token_probe",
                    is_malicious=True,
                    source_ip=self._random_ip(),  # Different Tor exits
                    asn=random.choice([16509, 15169]),
                    country=random.choice(["NL", "DE", "CH"]),
                    is_tor=True,
                    is_vpn=False,
                    token_reuse=True,
                    confidence_expected=0.90,
                )
            )

        # Phase 2: Pivot to AWS VPS
        vps_ip = self._random_ip()
        for i in range(3):
            events.append(
                SyntheticEvent(
                    event_type="token_probe",
                    is_malicious=True,
                    source_ip=vps_ip,
                    asn=16509,  # AWS
                    country="US",
                    is_tor=False,
                    is_vpn=True,
                    token_reuse=True,
                    confidence_expected=0.75,
                )
            )

        # Phase 3: Pivot to residential proxy (botnet)
        residential_ip = self._random_ip()
        for i in range(3):
            events.append(
                SyntheticEvent(
                    event_type="token_probe",
                    is_malicious=True,
                    source_ip=residential_ip,
                    asn=7922,  # Comcast (compromised residential)
                    country="US",
                    is_tor=False,
                    is_vpn=False,
                    token_reuse=True,
                    confidence_expected=0.85,  # High despite residential IP
                )
            )

        return AdaptiveSequence(
            events=events,
            sequence_type="infrastructure_pivot",
            description="Tor→VPS→Residential infrastructure adaptation",
        )

    def generate_mixed_benign_malicious(self) -> AdaptiveSequence:
        """
        Mixed Benign-Malicious: Interleaved attack and legitimate behavior

        Pattern:
        - Attack event
        - 2 benign events
        - Attack event
        - 2 benign events
        - (repeat 5 times)

        GOAL: Test HMM state recovery after seeing benign behavior
        """
        events = []

        attack_ip = self._random_ip()

        for cycle in range(5):
            # Attack
            events.append(
                SyntheticEvent(
                    event_type="token_probe",
                    is_malicious=True,
                    source_ip=attack_ip,
                    asn=16509,
                    country="US",
                    is_tor=False,
                    is_vpn=True,
                    token_reuse=True,
                    confidence_expected=0.70,
                )
            )

            # Benign (same IP trying to blend in)
            for _ in range(2):
                events.append(
                    SyntheticEvent(
                        event_type="api_call",
                        is_malicious=False,
                        source_ip=attack_ip,
                        asn=16509,
                        country="US",
                        is_tor=False,
                        is_vpn=True,
                        token_reuse=False,
                        confidence_expected=0.30,
                    )
                )

        return AdaptiveSequence(
            events=events,
            sequence_type="mixed_behavior",
            description="Interleaved attack/benign to evade detection",
        )

    def generate_all_adaptive_scenarios(self) -> List[AdaptiveSequence]:
        """Generate all adaptive scenarios"""
        return [
            self.generate_low_and_slow_credential_probe(),
            self.generate_gradual_escalation(),
            self.generate_infrastructure_pivot(),
            self.generate_mixed_benign_malicious(),
        ]

    # Helper methods

    def _random_ip(self) -> str:
        return (
            f"{random.randint(1, 255)}.{random.randint(0, 255)}."
            f"{random.randint(0, 255)}.{random.randint(0, 255)}"
        )

    def _benign_event(self) -> SyntheticEvent:
        return SyntheticEvent(
            event_type="api_call",
            is_malicious=False,
            source_ip=self._random_ip(),
            asn=random.choice([7922, 20001, 7018]),
            country=random.choice(["US", "CA", "GB"]),
            is_tor=False,
            is_vpn=False,
            token_reuse=False,
            confidence_expected=0.05,
        )

    def _credential_probe(
        self, is_tor: bool = False, is_vps: bool = False, timestamp_offset: int = 0
    ) -> SyntheticEvent:
        return SyntheticEvent(
            event_type="token_probe",
            is_malicious=True,
            source_ip=self._random_ip(),
            asn=16509 if (is_tor or is_vps) else 7922,
            country=random.choice(["NL", "DE", "US"]),
            is_tor=is_tor,
            is_vpn=is_vps,
            token_reuse=True,
            confidence_expected=0.85,
        )

    def _delay_marker(self, hours: int) -> SyntheticEvent:
        """
        Delay marker (not a real event, used for sequencing)

        In real implementation, this would translate to timestamp offsets
        """
        return SyntheticEvent(
            event_type="_delay_marker",
            is_malicious=False,
            source_ip="0.0.0.0",
            asn=0,
            country="XX",
            is_tor=False,
            is_vpn=False,
            token_reuse=False,
            confidence_expected=0.0,
        )


__all__ = ["AdaptiveSequence", "AdaptiveAdversaryGenerator"]
