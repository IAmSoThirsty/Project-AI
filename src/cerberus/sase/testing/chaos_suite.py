"""
SASE Chaos Engineering Test Suite

10k synthetic event replay for validation and stress testing.
"""

import random
from dataclasses import dataclass


@dataclass
class SyntheticEvent:
    """Synthetic telemetry event for testing"""

    event_type: str
    is_malicious: bool  # Ground truth
    source_ip: str
    asn: int
    country: str
    is_tor: bool
    is_vpn: bool
    token_reuse: bool
    confidence_expected: float  # Expected SASE confidence


class EventGenerator:
    """
    Generates synthetic adversarial events for chaos testing

    Mix of:
    - True positives (known attack patterns)
    - True negatives (benign traffic)
    - Edge cases (high-confidence false signals)
    """

    # Malicious ASNs (cloud providers commonly abused)
    MALICIOUS_ASNS = [
        16509,  # AWS
        15169,  # Google Cloud
        8075,  # Microsoft Azure
        14061,  # DigitalOcean
        24940,  # Hetzner
    ]

    # Benign ASNs (major ISPs)
    BENIGN_ASNS = [
        7922,  # Comcast
        20001,  # Charter
        7018,  # AT&T
        5650,  # Frontier
        11351,  # Charter Spectrum
    ]

    COUNTRIES = ["US", "GB", "DE", "FR", "CA", "AU", "NL", "SG", "IN", "BR"]

    def __init__(self, seed: int = 42):
        random.seed(seed)

    def generate_attack_token_harvesting(self) -> SyntheticEvent:
        """Generate credential harvesting attack"""
        return SyntheticEvent(
            event_type="token_probe",
            is_malicious=True,
            source_ip=self._random_ip(),
            asn=random.choice(self.MALICIOUS_ASNS),
            country=random.choice(["RU", "CN", "KP"]),
            is_tor=random.random() < 0.4,
            is_vpn=random.random() < 0.6,
            token_reuse=True,
            confidence_expected=0.85,  # Expect high confidence
        )

    def generate_attack_api_enumeration(self) -> SyntheticEvent:
        """Generate API enumeration attack"""
        return SyntheticEvent(
            event_type="api_call",
            is_malicious=True,
            source_ip=self._random_ip(),
            asn=random.choice(self.MALICIOUS_ASNS),
            country=random.choice(self.COUNTRIES),
            is_tor=False,
            is_vpn=True,
            token_reuse=random.random() < 0.3,
            confidence_expected=0.70,
        )

    def generate_benign_legitimate_user(self) -> SyntheticEvent:
        """Generate legitimate user traffic"""
        return SyntheticEvent(
            event_type="api_call",
            is_malicious=False,
            source_ip=self._random_ip(),
            asn=random.choice(self.BENIGN_ASNS),
            country=random.choice(["US", "CA", "GB"]),
            is_tor=False,
            is_vpn=False,
            token_reuse=False,
            confidence_expected=0.05,  # Expect very low confidence
        )

    def generate_edge_case_vpn_user(self) -> SyntheticEvent:
        """
        Edge case: Legitimate user on VPN

        Should have moderate suspicion but not trigger containment
        """
        return SyntheticEvent(
            event_type="api_call",
            is_malicious=False,
            source_ip=self._random_ip(),
            asn=random.choice(self.MALICIOUS_ASNS),  # VPN provider
            country=random.choice(self.COUNTRIES),
            is_tor=False,
            is_vpn=True,
            token_reuse=False,
            confidence_expected=0.35,  # Moderate suspicion, below containment threshold
        )

    def generate_10k_mix(self) -> list[SyntheticEvent]:
        """
        Generate 10k event mix:
        - 5% true attacks (credential harvesting)
        - 10% true attacks (API enumeration)
        - 80% benign traffic
        - 5% edge cases (VPN users)
        """
        events = []

        # 500 credential harvesting attacks
        events.extend([self.generate_attack_token_harvesting() for _ in range(500)])

        # 1000 API enumeration attacks
        events.extend([self.generate_attack_api_enumeration() for _ in range(1000)])

        # 8000 benign users
        events.extend([self.generate_benign_legitimate_user() for _ in range(8000)])

        # 500 VPN edge cases
        events.extend([self.generate_edge_case_vpn_user() for _ in range(500)])

        # Shuffle to simulate real traffic
        random.shuffle(events)

        return events

    def _random_ip(self) -> str:
        """Generate random IP address"""
        return (
            f"{random.randint(1, 255)}.{random.randint(0, 255)}." f"{random.randint(0, 255)}.{random.randint(0, 255)}"
        )


class ChaosValidator:
    """
    Validates SASE performance against ground truth

    Metrics:
    - Precision: TP / (TP + FP)
    - Recall: TP / (TP + FN)
    - F1 Score: 2 * (Precision * Recall) / (Precision + Recall)
    - False Positive Rate: FP / (FP + TN)
    """

    def __init__(self, containment_threshold: float = 0.50):
        self.containment_threshold = containment_threshold
        self.results = {
            "true_positives": 0,
            "true_negatives": 0,
            "false_positives": 0,
            "false_negatives": 0,
        }

    def validate_result(self, event: SyntheticEvent, sase_confidence: float):
        """
        Validate SASE result against ground truth

        Decision threshold: 50% confidence triggers containment
        """
        sase_predicts_malicious = sase_confidence >= self.containment_threshold

        if event.is_malicious and sase_predicts_malicious:
            self.results["true_positives"] += 1
        elif event.is_malicious and not sase_predicts_malicious:
            self.results["false_negatives"] += 1
        elif not event.is_malicious and sase_predicts_malicious:
            self.results["false_positives"] += 1
        else:
            self.results["true_negatives"] += 1

    def get_metrics(self) -> dict[str, float]:
        """Calculate validation metrics"""
        tp = self.results["true_positives"]
        tn = self.results["true_negatives"]
        fp = self.results["false_positives"]
        fn = self.results["false_negatives"]

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0.0

        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "false_positive_rate": fpr,
            "accuracy": accuracy,
            "total_events": tp + tn + fp + fn,
            **self.results,
        }

    def passes_god_tier(self) -> bool:
        """
        Check if results meet god-tier criteria:
        - Accuracy > 99.5%
        - False positive rate < 0.5%
        - Recall > 95%
        """
        metrics = self.get_metrics()
        return metrics["accuracy"] >= 0.995 and metrics["false_positive_rate"] <= 0.005 and metrics["recall"] >= 0.95


__all__ = ["SyntheticEvent", "EventGenerator", "ChaosValidator"]
