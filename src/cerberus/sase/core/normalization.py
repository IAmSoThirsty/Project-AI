"""
SASE - Sovereign Adversarial Signal Engine
L3: Event Normalization & Enrichment

Enriches events with attribution data while preserving raw event immutability.

ENRICHMENT MODULES:
- ASN Risk Index
- Tor Exit Node Detection
- Cloud Provider Classification
- Residential vs VPS
- Historical interaction correlation
- Token sensitivity mapping

INVARIANTS:
- No enrichment overwrites raw data
- Raw event hash preserved
- All enrichments version-tagged
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger("SASE.L3.Normalization")


class InfrastructureType(Enum):
    """Infrastructure classification"""

    RESIDENTIAL = "residential"
    VPS = "vps"
    CLOUD = "cloud"
    DATACENTER = "datacenter"
    TOR = "tor"
    VPN = "vpn"
    PROXY = "proxy"
    CORPORATE_NAT = "corporate_nat"
    UNKNOWN = "unknown"


@dataclass
class EnrichmentData:
    """Event enrichment metadata (L3)"""

    asn_risk_index: float | None = None  # 0.0-1.0
    is_tor: bool = False
    is_vpn: bool = False
    cloud_provider: str | None = None
    infrastructure_type: str | None = None
    historical_reuse_count: int = 0
    token_sensitivity: float | None = None  # 0.0-1.0
    enrichment_version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "asn_risk_index": self.asn_risk_index,
            "is_tor": self.is_tor,
            "is_vpn": self.is_vpn,
            "cloud_provider": self.cloud_provider,
            "infrastructure_type": self.infrastructure_type,
            "historical_reuse_count": self.historical_reuse_count,
            "token_sensitivity": self.token_sensitivity,
            "enrichment_version": self.enrichment_version,
        }


class ASNRiskIndexer:
    """
    ASN risk scoring

    Maintains risk index for Autonomous Systems
    """

    def __init__(self):
        # Known high-risk ASNs (example data)
        self.high_risk_asns: set[str] = {"AS12345", "AS67890"}  # Example malicious ASN

        # ASN risk scores (0.0-1.0)
        self.asn_scores: dict[str, float] = {}

    def get_risk_index(self, asn: str) -> float:
        """
        Get risk index for ASN

        Returns: 0.0 (safe) to 1.0 (very risky)
        """
        if asn in self.asn_scores:
            return self.asn_scores[asn]

        # Default scoring
        if asn in self.high_risk_asns:
            score = 0.9
        elif asn.startswith("AS"):
            # Heuristic: residential ASNs typically safer
            score = 0.3
        else:
            score = 0.5  # Unknown

        self.asn_scores[asn] = score
        return score

    def update_risk(self, asn: str, new_score: float):
        """Update ASN risk score (learning)"""
        self.asn_scores[asn] = max(0.0, min(1.0, new_score))
        logger.info(f"ASN risk updated: {asn} -> {new_score:.2f}")


class TorDetector:
    """
    Tor exit node detection

    Maintains current list of Tor exit nodes
    """

    def __init__(self):
        # TODO: Load from public Tor directory
        self.tor_exit_nodes: set[str] = set()
        self._load_tor_list()

    def _load_tor_list(self):
        """Load Tor exit node list"""
        # TODO: Fetch from https://check.torproject.org/exit-addresses
        # For now, maintain static example
        self.tor_exit_nodes = {"185.220.101.1", "185.220.101.2"}

    def is_tor_exit(self, ip: str) -> bool:
        """Check if IP is Tor exit node"""
        return ip in self.tor_exit_nodes


class CloudProviderClassifier:
    """
    Cloud provider and infrastructure classification

    Identifies AWS, Azure, GCP, and other cloud providers
    """

    def __init__(self):
        # ASN to cloud provider mapping
        self.cloud_asns: dict[str, str] = {
            "AS16509": "AWS",
            "AS14618": "AWS",
            "AS8075": "Microsoft Azure",
            "AS15169": "Google Cloud",
            "AS13335": "Cloudflare",
            "AS20940": "Akamai",
        }

        # IP ranges (TODO: implement CIDR matching)
        self.cloud_ranges: dict[str, str] = {}

    def classify(self, asn: str, ip: str = None) -> str | None:
        """Classify cloud provider"""
        return self.cloud_asns.get(asn)

    def classify_infrastructure(
        self, asn: str, ip: str, is_tor: bool, is_vpn: bool
    ) -> InfrastructureType:
        """Classify infrastructure type"""
        if is_tor:
            return InfrastructureType.TOR

        if is_vpn:
            return InfrastructureType.VPN

        cloud = self.classify(asn, ip)
        if cloud:
            return InfrastructureType.CLOUD

        # Heuristics for other types
        if asn.startswith("AS") and asn not in self.cloud_asns:
            # Likely residential or corporate
            return InfrastructureType.RESIDENTIAL

        return InfrastructureType.UNKNOWN


class HistoricalCorrelator:
    """
    Tracks historical artifact interactions

    Counts reuse of tokens/artifacts for pattern detection
    """

    def __init__(self):
        self.interaction_counts: dict[str, int] = {}  # artifact_id -> count
        self.ip_artifact_map: dict[str, set[str]] = {}  # ip -> {artifact_ids}

    def record_interaction(self, ip: str, artifact_id: str):
        """Record artifact interaction"""
        # Increment artifact reuse count
        self.interaction_counts[artifact_id] = (
            self.interaction_counts.get(artifact_id, 0) + 1
        )

        # Track IP-artifact associations
        if ip not in self.ip_artifact_map:
            self.ip_artifact_map[ip] = set()

        self.ip_artifact_map[ip].add(artifact_id)

        logger.debug(f"Interaction recorded: {ip} -> {artifact_id}")

    def get_reuse_count(self, artifact_id: str) -> int:
        """Get how many times artifact has been accessed"""
        return self.interaction_counts.get(artifact_id, 0)

    def get_ip_diversity(self, artifact_id: str) -> int:
        """Get how many unique IPs have accessed artifact"""
        unique_ips = sum(
            1 for ips in self.ip_artifact_map.values() if artifact_id in ips
        )
        return unique_ips


class TokenSensitivityMapper:
    """
    Maps tokens/artifacts to sensitivity levels

    Higher sensitivity = more valuable target
    """

    def __init__(self):
        self.sensitivity_map: dict[str, float] = (
            {}
        )  # artifact_id -> sensitivity (0.0-1.0)

    def set_sensitivity(self, artifact_id: str, sensitivity: float):
        """Set token sensitivity"""
        self.sensitivity_map[artifact_id] = max(0.0, min(1.0, sensitivity))

    def get_sensitivity(self, artifact_id: str) -> float:
        """Get token sensitivity"""
        return self.sensitivity_map.get(artifact_id, 0.5)  # Default: medium


class EventEnrichmentPipeline:
    """
    L3: Event Normalization & Enrichment Pipeline

    Enriches events without modifying raw data

    INVARIANTS ENFORCED:
    - Raw event hash never changes
    - Enrichment stored separately
    - All enrichments version-tagged
    """

    def __init__(self):
        self.asn_risk = ASNRiskIndexer()
        self.tor_detector = TorDetector()
        self.cloud_classifier = CloudProviderClassifier()
        self.historical_correlator = HistoricalCorrelator()
        self.token_sensitivity = TokenSensitivityMapper()

        logger.info("L3 enrichment pipeline initialized")

    def enrich(self, event: Any) -> EnrichmentData:
        """
        Enrich event with attribution data

        INVARIANT: Original event object is NOT modified
        Returns separate enrichment data structure
        """
        from .ingestion_gateway import AdversarialEvent

        if not isinstance(event, AdversarialEvent):
            raise TypeError("Event must be AdversarialEvent type")

        # Extract event data
        ip = event.source_ip
        asn = event.asn
        artifact_id = event.artifact_id

        # ASN risk indexing
        asn_risk_index = self.asn_risk.get_risk_index(asn)

        # Tor detection
        is_tor = self.tor_detector.is_tor_exit(ip)

        # TODO: VPN detection (requires external service)
        is_vpn = False

        # Cloud provider classification
        cloud_provider = self.cloud_classifier.classify(asn, ip)
        infrastructure_type = self.cloud_classifier.classify_infrastructure(
            asn, ip, is_tor, is_vpn
        ).value

        # Historical correlation
        self.historical_correlator.record_interaction(ip, artifact_id)
        historical_reuse_count = self.historical_correlator.get_reuse_count(artifact_id)

        # Token sensitivity
        token_sensitivity = self.token_sensitivity.get_sensitivity(artifact_id)

        # Create enrichment (separate from raw event)
        enrichment = EnrichmentData(
            asn_risk_index=asn_risk_index,
            is_tor=is_tor,
            is_vpn=is_vpn,
            cloud_provider=cloud_provider,
            infrastructure_type=infrastructure_type,
            historical_reuse_count=historical_reuse_count,
            token_sensitivity=token_sensitivity,
        )

        logger.info(f"Event enriched: {event.event_id}")
        logger.debug(f"  ASN risk: {asn_risk_index:.2f}")
        logger.debug(f"  Tor: {is_tor}, Cloud: {cloud_provider}")
        logger.debug(f"  Reuse count: {historical_reuse_count}")

        # INVARIANT CHECK: Verify raw event hash unchanged
        # (hash verification would go here in production)

        return enrichment


__all__ = [
    "InfrastructureType",
    "EnrichmentData",
    "ASNRiskIndexer",
    "TorDetector",
    "CloudProviderClassifier",
    "HistoricalCorrelator",
    "TokenSensitivityMapper",
    "EventEnrichmentPipeline",
]
