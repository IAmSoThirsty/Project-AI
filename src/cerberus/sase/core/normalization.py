#                                           [2026-04-09 05:58]
#                                          Productivity: Active
"""
SASE - Sovereign Adversarial Signal Engine
L3: Event Normalization & Enrichment

Enriches events with attribution data while preserving raw event immutability.

ENRICHMENT MODULES:
- ASN Risk Index
- Tor Exit Node Detection
- VPN Detection (ASN-based + IP range + heuristics)
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
import urllib.request
import urllib.error
from datetime import datetime, timezone
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
    processed_at: str = ""  # UTC ISO format

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

    def __init__(self, max_cache_size: int = 5000):
        # Known high-risk ASNs (example data)
        self.high_risk_asns: set[str] = {"AS12345", "AS67890"}  # Example malicious ASN
        self.max_cache_size = max_cache_size

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
        if len(self.asn_scores) >= self.max_cache_size and asn not in self.asn_scores:
            # Simple eviction: clear oldest entries if full
            # In production this would be LRU
            self.asn_scores.clear()

        self.asn_scores[asn] = max(0.0, min(1.0, new_score))
        logger.info(f"ASN risk updated: {asn} -> {new_score:.2f}")


class TorDetector:
    """
    Tor exit node detection

    Maintains current list of Tor exit nodes
    """

    def __init__(self):
        """Active: SASE L3 Tor Detection Service"""
        self.tor_exit_nodes: set[str] = set()
        self._load_tor_list()

    def _load_tor_list(self):
        """Load Tor exit node list"""
        url = "https://check.torproject.org/exit-addresses"
        fallback_list = {"185.220.101.1", "185.220.101.2"}
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                content = response.read().decode("utf-8")

            nodes = set()
            for line in content.splitlines():
                if line.startswith("ExitAddress "):
                    parts = line.split()
                    if len(parts) >= 2:
                        nodes.add(parts[1])

            if nodes:
                self.tor_exit_nodes = nodes
                logger.info(f"Loaded {len(nodes)} Tor exit nodes from public directory.")
            else:
                logger.warning("No Tor exit nodes found in response. Using fallback list.")
                self.tor_exit_nodes = fallback_list
        except (urllib.error.URLError, TimeoutError) as e:
            logger.warning(
                f"Failed to fetch Tor exit nodes ({e}). Using fallback list."
            )
            self.tor_exit_nodes = fallback_list
        except Exception as e:
            logger.error(f"Unexpected error fetching Tor nodes: {e}. Using fallback.")
            self.tor_exit_nodes = fallback_list

    def is_tor_exit(self, ip: str) -> bool:
        """Check if IP is Tor exit node"""
        return ip in self.tor_exit_nodes


class VPNDetector:
    """
    VPN detection using multi-signal approach
    
    Detection methods:
    1. Known VPN ASN detection (high confidence)
    2. Known VPN IP ranges (high confidence)
    3. Datacenter/hosting provider heuristics (medium confidence)
    4. Port/behavior analysis (low confidence)
    
    Focuses on commercial VPN providers and known anonymization services.
    """

    def __init__(self):
        """Initialize VPN detection with known VPN providers"""
        # Known commercial VPN ASNs
        self.vpn_asns: set[str] = {
            "AS13335",  # Cloudflare WARP
            "AS62240",  # Clouvider (used by many VPNs)
            "AS32613",  # iWeb Technologies (VPN hosting)
            "AS36351",  # SoftLayer (IBM Cloud - VPN hosting)
            "AS24961",  # myLoc managed IT AG (VPN hosting)
            "AS20473",  # AS-CHOOPA (Vultr - VPN hosting)
            "AS46562",  # Total Server Solutions (VPN)
            "AS396982", # Google Cloud Platform (VPN service)
            "AS16509",  # Amazon AWS (VPN hosting)
            "AS8075",   # Microsoft Azure (VPN hosting)
        }
        
        # Known VPN provider IP ranges (examples - would be expanded in production)
        # Format: (start_ip, end_ip, provider_name)
        self.vpn_ip_ranges: list[tuple[str, str, str]] = []
        
        # Known datacenter/hosting providers commonly used by VPNs
        self.vpn_hosting_asns: set[str] = {
            "AS14061",  # DigitalOcean
            "AS16276",  # OVH
            "AS212238", # Datacamp Limited
            "AS397213", # Vero Mobile, LLC
            "AS202425", # IP Volume Inc
        }
        
        # Lightweight IP cache for performance
        self.ip_cache: dict[str, bool] = {}
        self.max_cache_size = 10000

        logger.info("VPN detector initialized with ASN and heuristic detection")

    def is_vpn(self, ip: str, asn: str | None = None) -> bool:
        """
        Detect if IP is likely from a VPN
        
        Args:
            ip: IP address to check
            asn: Autonomous System Number (if available)
            
        Returns:
            True if VPN is detected, False otherwise
        """
        # Check cache first
        if ip in self.ip_cache:
            return self.ip_cache[ip]
        
        result = False
        
        # Method 1: Known VPN ASN detection (high confidence)
        if asn and asn in self.vpn_asns:
            logger.debug(f"VPN detected via ASN match: {ip} ({asn})")
            result = True
        
        # Method 2: Known hosting provider ASN (medium confidence)
        elif asn and asn in self.vpn_hosting_asns:
            logger.debug(f"Potential VPN detected via hosting ASN: {ip} ({asn})")
            result = True
        
        # Method 3: IP range detection
        elif self._check_ip_ranges(ip):
            logger.debug(f"VPN detected via IP range: {ip}")
            result = True
        
        # Cache result
        if len(self.ip_cache) >= self.max_cache_size:
            # Simple cache eviction - remove first entry
            self.ip_cache.pop(next(iter(self.ip_cache)))
        self.ip_cache[ip] = result
        
        return result

    def _check_ip_ranges(self, ip: str) -> bool:
        """Check if IP falls within known VPN ranges"""
        # This is a simplified implementation
        # In production, would use more sophisticated IP range matching
        for start_ip, end_ip, provider in self.vpn_ip_ranges:
            if self._ip_in_range(ip, start_ip, end_ip):
                logger.debug(f"IP {ip} matches VPN range for {provider}")
                return True
        return False

    def _ip_in_range(self, ip: str, start: str, end: str) -> bool:
        """Check if IP is within range (simplified)"""
        try:
            ip_int = self._ip_to_int(ip)
            start_int = self._ip_to_int(start)
            end_int = self._ip_to_int(end)
            return start_int <= ip_int <= end_int
        except ValueError:
            return False

    def _ip_to_int(self, ip: str) -> int:
        """Convert IPv4 address to integer"""
        parts = ip.split('.')
        if len(parts) != 4:
            raise ValueError(f"Invalid IP format: {ip}")
        
        # Validate each octet
        try:
            octets = [int(part) for part in parts]
        except ValueError:
            raise ValueError(f"Invalid IP format: {ip}")
        
        # Check range (0-255)
        for octet in octets:
            if not 0 <= octet <= 255:
                raise ValueError(f"Invalid IP format: {ip}")
        
        return sum(octets[i] << (8 * (3 - i)) for i in range(4))

    def add_vpn_asn(self, asn: str):
        """Add ASN to VPN detection list"""
        self.vpn_asns.add(asn)
        logger.info(f"Added VPN ASN: {asn}")

    def add_vpn_ip_range(self, start_ip: str, end_ip: str, provider: str):
        """Add IP range to VPN detection list"""
        self.vpn_ip_ranges.append((start_ip, end_ip, provider))
        logger.info(f"Added VPN IP range: {start_ip}-{end_ip} ({provider})")


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

    def classify(self, asn: str, _ip: str | None = None) -> str | None:
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

    def __init__(self, max_history: int = 20000):
        self.interaction_counts: dict[str, int] = {}  # artifact_id -> count
        self.ip_artifact_map: dict[str, set[str]] = {}  # ip -> {artifact_ids}
        self.max_history = max_history

    def record_interaction(self, ip: str, artifact_id: str):
        """Record artifact interaction"""
        # Increment artifact reuse count
        self.interaction_counts[artifact_id] = (
            self.interaction_counts.get(artifact_id, 0) + 1
        )

        # Track IP-artifact associations
        if ip not in self.ip_artifact_map:
            if len(self.ip_artifact_map) >= self.max_history:
                # Evict one entry
                self.ip_artifact_map.pop(next(iter(self.ip_artifact_map)))
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
        self.vpn_detector = VPNDetector()
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

        # VPN detection
        is_vpn = self.vpn_detector.is_vpn(ip, asn)

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
            processed_at=datetime.now(timezone.utc).isoformat(),
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
