"""
SASE - Sovereign Adversarial Signal Engine
L4: Attribution Engine

Feature extraction and vector construction for behavioral modeling.

FEATURE VECTOR (X):
{
    'ASN_risk': float,
    'Geo_anomaly_score': float,
    'Token_sensitivity': float,
    'Time_of_day_deviation': float,
    'Historical_reuse_count': int,
    'Infrastructure_entropy': float,
    'Toolchain_fingerprint': str,
    'Tor_flag': bool,
    'VPS_flag': bool,
    'NAT_density_estimate': float
}
"""

import hashlib
import logging
import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger("SASE.L4.Attribution")


@dataclass
class FeatureVector:
    """
    Attribution feature vector for behavioral modeling

    All features normalized to 0.0-1.0 range except where noted
    """

    ASN_risk: float  # 0.0-1.0
    Geo_anomaly_score: float  # 0.0-1.0
    Token_sensitivity: float  # 0.0-1.0
    Time_of_day_deviation: float  # 0.0-1.0
    Historical_reuse_count: int  # Raw count
    Infrastructure_entropy: float  # 0.0-1.0
    Toolchain_fingerprint: str  # Hash
    Tor_flag: bool
    VPS_flag: bool
    NAT_density_estimate: float  # 0.0-1.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "ASN_risk": self.ASN_risk,
            "Geo_anomaly_score": self.Geo_anomaly_score,
            "Token_sensitivity": self.Token_sensitivity,
            "Time_of_day_deviation": self.Time_of_day_deviation,
            "Historical_reuse_count": self.Historical_reuse_count,
            "Infrastructure_entropy": self.Infrastructure_entropy,
            "Toolchain_fingerprint": self.Toolchain_fingerprint,
            "Tor_flag": self.Tor_flag,
            "VPS_flag": self.VPS_flag,
            "NAT_density_estimate": self.NAT_density_estimate,
        }

    def to_array(self) -> list:
        """Convert to numerical array (for ML models)"""
        return [
            self.ASN_risk,
            self.Geo_anomaly_score,
            self.Token_sensitivity,
            self.Time_of_day_deviation,
            float(self.Historical_reuse_count) / 100.0,  # Normalize
            self.Infrastructure_entropy,
            float(int(self.Tor_flag)),
            float(int(self.VPS_flag)),
            self.NAT_density_estimate,
        ]


class FeatureExtractor:
    """
    Feature extraction from enriched events

    Converts raw event + enrichment into attribution feature vector
    """

    def __init__(self):
        # Historical baselines for anomaly detection
        self.geo_baselines: Dict[str, Dict[str, int]] = {}  # artifact_id -> {country: count}
        self.time_baselines: Dict[str, list] = {}  # artifact_id -> [timestamps]

        logger.info("Feature extractor initialized")

    def extract(self, event: Any, enrichment: Any) -> FeatureVector:
        """
        Extract feature vector from event + enrichment

        Args:
            event: AdversarialEvent
            enrichment: EnrichmentData

        Returns:
            FeatureVector for attribution
        """
        from ..core.deterministic import DeterministicSerializer
        from ..core.ingestion_gateway import AdversarialEvent
        from ..core.normalization import EnrichmentData

        if not isinstance(event, AdversarialEvent):
            raise TypeError("Event must be AdversarialEvent")

        if not isinstance(enrichment, EnrichmentData):
            raise TypeError("Enrichment must be EnrichmentData")

        # Extract features with DETERMINISTIC precision
        # All floats normalized to 6 decimal places for reproducibility
        serializer = DeterministicSerializer()

        asn_risk = serializer.normalize_confidence(enrichment.asn_risk_index or 0.5)
        geo_anomaly = serializer.normalize_confidence(self._calculate_geo_anomaly(event.artifact_id, event.geo.country))
        token_sensitivity = serializer.normalize_confidence(enrichment.token_sensitivity or 0.5)
        time_deviation = serializer.normalize_confidence(
            self._calculate_time_deviation(event.artifact_id, event.ingest_timestamp)
        )
        reuse_count = enrichment.historical_reuse_count
        infrastructure_entropy = serializer.normalize_confidence(self._calculate_infrastructure_entropy(enrichment))
        toolchain_fp = self._fingerprint_toolchain(event.user_agent or "")
        tor_flag = enrichment.is_tor
        vps_flag = enrichment.infrastructure_type in ["vps", "cloud", "datacenter"]
        nat_density = serializer.normalize_confidence(self._estimate_nat_density(event.source_ip))

        vector = FeatureVector(
            ASN_risk=asn_risk,
            Geo_anomaly_score=geo_anomaly,
            Token_sensitivity=token_sensitivity,
            Time_of_day_deviation=time_deviation,
            Historical_reuse_count=reuse_count,
            Infrastructure_entropy=infrastructure_entropy,
            Toolchain_fingerprint=toolchain_fp,
            Tor_flag=tor_flag,
            VPS_flag=vps_flag,
            NAT_density_estimate=nat_density,
        )

        logger.debug(f"Feature extraction complete (deterministic): {event.event_id}")

        return vector

    def _calculate_geo_anomaly(self, artifact_id: str, country: str) -> float:
        """
        Calculate geographic anomaly score

        How unusual is this country for this artifact?
        """
        if artifact_id not in self.geo_baselines:
            self.geo_baselines[artifact_id] = {}

        baseline = self.geo_baselines[artifact_id]

        # Update baseline
        baseline[country] = baseline.get(country, 0) + 1

        # Calculate anomaly
        total = sum(baseline.values())
        country_freq = baseline[country] / total
        # Normalize to 0-1 (higher = more anomalous)
        anomaly_score = 1.0 - min(1.0, country_freq)

        return anomaly_score

    def _calculate_time_deviation(self, artifact_id: str, timestamp_ms: int) -> float:
        """
        Calculate time-of-day deviation

        How unusual is this access time?
        """
        if artifact_id not in self.time_baselines:
            self.time_baselines[artifact_id] = []

        # Extract hour of day
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        hour = dt.hour

        baseline = self.time_baselines[artifact_id]
        baseline.append(hour)

        # Keep last 100 observations
        if len(baseline) > 100:
            baseline = baseline[-100:]
            self.time_baselines[artifact_id] = baseline

        # Calculate mean and std
        if len(baseline) < 2:
            return 0.5  # Not enough data

        mean_hour = sum(baseline) / len(baseline)
        variance = sum((h - mean_hour) ** 2 for h in baseline) / len(baseline)
        std = math.sqrt(variance)

        # Z-score
        if std < 1e-6:
            z_score = 0.0
        else:
            z_score = abs(hour - mean_hour) / std

        # Convert to 0-1 range (3 sigma rule)
        deviation = min(1.0, z_score / 3.0)

        return deviation

    def _calculate_infrastructure_entropy(self, enrichment) -> float:
        """
        Calculate infrastructure entropy

        Mixing of infrastructure types indicates scanning/automation
        """
        # Simple heuristic: diverse infrastructure = higher entropy
        entropy = 0.0

        if enrichment.is_tor:
            entropy += 0.4
        if enrichment.is_vpn:
            entropy += 0.3
        if enrichment.infrastructure_type in ["cloud", "vps"]:
            entropy += 0.3

        return min(1.0, entropy)

    def _fingerprint_toolchain(self, user_agent: str) -> str:
        """
        Fingerprint toolchain from User-Agent

        Returns hash of normalized UA string
        """
        # Normalize and hash
        normalized = user_agent.lower().strip()
        fp_hash = hashlib.md5(normalized.encode()).hexdigest()
        return fp_hash[:16]

    def _estimate_nat_density(self, ip: str) -> float:
        """
        Estimate NAT density (multiple users behind single IP)

        TODO: Implement using IP behavioral history
        """
        # Placeholder: corporate NATs tend to have high density
        return 0.3  # Default: medium density


class AttributionEngine:
    """
    L4: Attribution Engine

    Orchestrates feature extraction for all events
    """

    def __init__(self):
        self.extractor = FeatureExtractor()
        logger.info("L4 Attribution Engine initialized")

    def attribute(self, event: Any, enrichment: Any) -> FeatureVector:
        """
        Generate attribution feature vector

        This vector feeds into L5 (Behavioral Model) and L6 (Bayesian Scoring)
        """
        return self.extractor.extract(event, enrichment)


__all__ = ["FeatureVector", "FeatureExtractor", "AttributionEngine"]
