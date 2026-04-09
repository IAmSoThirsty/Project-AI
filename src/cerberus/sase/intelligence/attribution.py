#                                           [2026-04-09 11:30]
#                                          Productivity: Active
"""
SASE - Sovereign Adversarial Signal Engine
L4: Attribution Engine

Feature extraction and vector construction for behavioral modeling.
Authenticated and hardened against adversarial temporal drift.
"""

import hashlib
import logging
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

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

    def to_dict(self) -> dict[str, Any]:
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

    def to_array(self) -> list[float]:
        """Convert to numerical array (for ML models)"""
        return [
            self.ASN_risk,
            self.Geo_anomaly_score,
            self.Token_sensitivity,
            self.Time_of_day_deviation,
            float(self.Historical_reuse_count) / 100.0,
            self.Infrastructure_entropy,
            float(int(self.Tor_flag)),
            float(int(self.VPS_flag)),
            self.NAT_density_estimate,
        ]


class FeatureExtractor:
    """
    Feature extraction from enriched events

    Converts raw event + enrichment into attribution feature vector.
    Hardened against memory exhaustion via bounded baselines.
    """

    def __init__(self, max_artifacts: int = 1000):
        # Historical baselines for anomaly detection
        self.geo_baselines: dict[str, dict[str, int]] = {}
        self.time_baselines: dict[str, list[int]] = {}
        self.max_artifacts = max_artifacts

        logger.info("L4 Feature Extractor initialized (max_artifacts=%d)", max_artifacts)

    def extract(self, event: Any, enrichment: Any) -> FeatureVector:
        """
        Extract feature vector from event + enrichment with UTC parity.
        """
        from ..core.deterministic import DeterministicSerializer
        from ..core.ingestion_gateway import IngestionError  # Internal import for typing if needed

        # Note: In a real restoration, AdversarialEvent and EnrichmentData types would be verified here.

        serializer = DeterministicSerializer()

        asn_risk = serializer.normalize_confidence(getattr(enrichment, "asn_risk_index", 0.5) or 0.5)
        geo_anomaly = serializer.normalize_confidence(
            self._calculate_geo_anomaly(getattr(event, "artifact_id", "UNKNOWN"), getattr(event, "geo_country", "UNKNOWN"))
        )
        token_sensitivity = serializer.normalize_confidence(
            getattr(enrichment, "token_sensitivity", 0.5) or 0.5
        )
        
        # Hardened UTC temporal extraction
        ts_ms = getattr(event, "ingest_timestamp", 0) or 0
        time_deviation = serializer.normalize_confidence(
            self._calculate_time_deviation(getattr(event, "artifact_id", "UNKNOWN"), ts_ms)
        )
        
        reuse_count = getattr(enrichment, "historical_reuse_count", 0)
        infrastructure_entropy = serializer.normalize_confidence(
            self._calculate_infrastructure_entropy(enrichment)
        )
        
        toolchain_fp = self._fingerprint_toolchain(getattr(event, "user_agent", "") or "")
        tor_flag = getattr(enrichment, "is_tor", False)
        vps_flag = getattr(enrichment, "infrastructure_type", "unknown") in ["vps", "cloud", "datacenter"]
        nat_density = serializer.normalize_confidence(
            self._estimate_nat_density(getattr(event, "source_ip", "0.0.0.0"))
        )

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

        logger.debug("Feature extraction complete (deterministic): %s", getattr(event, "event_id", "N/A"))

        return vector

    def _calculate_geo_anomaly(self, artifact_id: str, country: str) -> float:
        """Calculate geographic anomaly score with memory bounding."""
        if artifact_id not in self.geo_baselines:
            if len(self.geo_baselines) >= self.max_artifacts:
                self.geo_baselines.clear()  # Emergency eviction
            self.geo_baselines[artifact_id] = {}

        baseline = self.geo_baselines[artifact_id]
        baseline[country] = baseline.get(country, 0) + 1

        total = sum(baseline.values())
        country_freq = baseline[country] / total
        return 1.0 - min(1.0, country_freq)

    def _calculate_time_deviation(self, artifact_id: str, timestamp_ms: int) -> float:
        """Calculate time deviation with UTC parity and memory bounding."""
        if artifact_id not in self.time_baselines:
            if len(self.time_baselines) >= self.max_artifacts:
                self.time_baselines.clear()
            self.time_baselines[artifact_id] = []

        # UTC-aware hour extraction
        dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        hour = dt.hour

        baseline = self.time_baselines[artifact_id]
        baseline.append(hour)

        # Bounded sliding window (last 100 observations)
        if len(baseline) > 100:
            baseline.pop(0)

        if len(baseline) < 2:
            return 0.5

        mean_hour = sum(baseline) / len(baseline)
        variance = sum((h - mean_hour) ** 2 for h in baseline) / len(baseline)
        std = math.sqrt(variance)

        if std < 1e-6:
            z_score = 0.0
        else:
            z_score = abs(hour - mean_hour) / std

        return min(1.0, z_score / 3.0)

    def _calculate_infrastructure_entropy(self, enrichment: Any) -> float:
        """Calculate infrastructure entropy."""
        entropy = 0.0
        if getattr(enrichment, "is_tor", False):
            entropy += 0.4
        if getattr(enrichment, "is_vpn", False):
            entropy += 0.3
        if getattr(enrichment, "infrastructure_type", "unknown") in ["cloud", "vps"]:
            entropy += 0.3
        return min(1.0, entropy)

    def _fingerprint_toolchain(self, user_agent: str) -> str:
        """Fingerprint normalized toolchain."""
        normalized = user_agent.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()[:16]

    def _estimate_nat_density(self, ip: str) -> float:
        """Estimate NAT density (placeholder for future L behavioral history)."""
        return 0.3


class AttributionEngine:
    """
    L4: Attribution Engine
    Orchestrates feature extraction for all events.
    """

    def __init__(self):
        self.extractor = FeatureExtractor()
        logger.info("L4 Attribution Engine initialized")

    def attribute(self, event: Any, enrichment: Any) -> FeatureVector:
        """Generate attribution feature vector."""
        return self.extractor.extract(event, enrichment)


__all__ = ["FeatureVector", "FeatureExtractor", "AttributionEngine"]
