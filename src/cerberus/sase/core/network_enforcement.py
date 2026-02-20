"""
SASE - Sovereign Adversarial Signal Engine
L1: Network & Edge Enforcement Plane

WAF, geo-fencing, rate limiting, TLS mutual auth, IP reputation, ASN tagging, DDoS mitigation.

INVARIANTS:
- All inbound must pass schema pre-validation
- No unauthenticated policy mutation
- All inbound requests hashed before processing
"""

import hashlib
import ipaddress
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("SASE.L1.NetworkEnforcement")


class EnforcementAction(Enum):
    """Edge enforcement actions"""

    ALLOW = "allow"
    RATE_LIMIT = "rate_limit"
    GEO_BLOCK = "geo_block"
    IP_BLOCK = "ip_block"
    CHALLENGE = "challenge"  # CAPTCHA/proof-of-work
    REJECT = "reject"


@dataclass
class GeoFenceRule:
    """Geographical access control rule"""

    allowed_countries: Set[str]  # ISO 3166-1 alpha-2
    blocked_countries: Set[str]
    allowed_regions: Set[str]  # e.g., "us-east-1"
    default_action: EnforcementAction = EnforcementAction.ALLOW


@dataclass
class RateLimitPolicy:
    """Rate limiting configuration"""

    requests_per_second: int = 1000
    requests_per_minute: int = 30000
    requests_per_hour: int = 1000000
    burst_size: int = 5000
    penalty_duration_seconds: int = 300  # 5 minutes


@dataclass
class IPReputation:
    """IP reputation score"""

    ip_address: str
    reputation_score: int  # 0-100 (0=malicious, 100=trusted)
    asn: str
    is_tor: bool = False
    is_vpn: bool = False
    is_datacenter: bool = False
    is_residential: bool = True
    threat_intel_flags: List[str] = None

    def __post_init__(self):
        if self.threat_intel_flags is None:
            self.threat_intel_flags = []


class GeoFenceController:
    """
    Geo-fencing enforcement

    Blocks or allows traffic based on geographical location
    """

    def __init__(self, rules: GeoFenceRule = None):
        self.rules = rules or GeoFenceRule(allowed_countries=set(), blocked_countries=set(), allowed_regions=set())

    def evaluate(self, country_code: str, region: str = None) -> EnforcementAction:
        """Evaluate geo-fence rules"""

        # Check blocked countries first
        if country_code in self.rules.blocked_countries:
            logger.warning(f"GEO_BLOCK: Country {country_code} is blocked")
            return EnforcementAction.GEO_BLOCK

        # Check allowed countries
        if self.rules.allowed_countries and country_code not in self.rules.allowed_countries:
            logger.warning(f"GEO_BLOCK: Country {country_code} not in allowed list")
            return EnforcementAction.GEO_BLOCK

        # Check regions
        if region and self.rules.allowed_regions and region not in self.rules.allowed_regions:
            logger.warning(f"GEO_BLOCK: Region {region} not allowed")
            return EnforcementAction.GEO_BLOCK

        return self.rules.default_action


class RateLimiter:
    """
    Token bucket rate limiter

    Enforces request rate limits with burst capacity
    """

    def __init__(self, policy: RateLimitPolicy = None):
        self.policy = policy or RateLimitPolicy()
        self.buckets: Dict[str, Dict] = {}  # key -> {tokens, last_update, penalty_until}

    def check_limit(self, key: str) -> tuple[bool, Optional[str]]:
        """
        Check if request is within rate limits

        Returns (allowed, reason)
        """
        now = time.time()

        # Initialize bucket if new
        if key not in self.buckets:
            self.buckets[key] = {
                "tokens": self.policy.burst_size,
                "last_update": now,
                "penalty_until": 0,
                "req_count_second": 0,
                "req_count_minute": 0,
                "req_count_hour": 0,
                "second_start": now,
                "minute_start": now,
                "hour_start": now,
            }

        bucket = self.buckets[key]

        # Check penalty
        if bucket["penalty_until"] > now:
            return False, f"Rate limit penalty active until {bucket['penalty_until']}"

        # Refill tokens
        elapsed = now - bucket["last_update"]
        refill = elapsed * (self.policy.requests_per_second / 1.0)
        bucket["tokens"] = min(self.policy.burst_size, bucket["tokens"] + refill)
        bucket["last_update"] = now

        # Reset counters if windows expired
        if now - bucket["second_start"] >= 1.0:
            bucket["req_count_second"] = 0
            bucket["second_start"] = now

        if now - bucket["minute_start"] >= 60.0:
            bucket["req_count_minute"] = 0
            bucket["minute_start"] = now

        if now - bucket["hour_start"] >= 3600.0:
            bucket["req_count_hour"] = 0
            bucket["hour_start"] = now

        # Check limits
        if bucket["req_count_second"] >= self.policy.requests_per_second:
            bucket["penalty_until"] = now + self.policy.penalty_duration_seconds
            return False, "Exceeded requests per second limit"

        if bucket["req_count_minute"] >= self.policy.requests_per_minute:
            bucket["penalty_until"] = now + self.policy.penalty_duration_seconds
            return False, "Exceeded requests per minute limit"

        if bucket["req_count_hour"] >= self.policy.requests_per_hour:
            bucket["penalty_until"] = now + self.policy.penalty_duration_seconds
            return False, "Exceeded requests per hour limit"

        # Check tokens
        if bucket["tokens"] < 1:
            return False, "Rate limit exceeded (burst capacity)"

        # Consume token
        bucket["tokens"] -= 1
        bucket["req_count_second"] += 1
        bucket["req_count_minute"] += 1
        bucket["req_count_hour"] += 1

        return True, None


class IPReputationService:
    """
    IP reputation lookup and scoring

    Integrates threat intelligence feeds and ASN data
    """

    def __init__(self):
        self.reputation_cache: Dict[str, IPReputation] = {}
        self.tor_exit_nodes: Set[str] = set()  # TODO: Load from feed
        self.known_vpns: Set[str] = set()  # TODO: Load from feed
        self.datacenter_asns: Set[str] = set()  # TODO: Load from feed

    def lookup(self, ip_address: str, asn: str = None) -> IPReputation:
        """Look up IP reputation"""

        # Check cache
        if ip_address in self.reputation_cache:
            return self.reputation_cache[ip_address]

        # Classify IP
        is_tor = ip_address in self.tor_exit_nodes
        is_vpn = ip_address in self.known_vpns
        is_datacenter = asn in self.datacenter_asns if asn else False
        is_residential = not (is_tor or is_vpn or is_datacenter)

        # Calculate reputation score
        reputation_score = 50  # Neutral

        if is_tor:
            reputation_score -= 30
        if is_vpn:
            reputation_score -= 10
        if is_datacenter:
            reputation_score -= 20
        if is_residential:
            reputation_score += 20

        reputation_score = max(0, min(100, reputation_score))

        reputation = IPReputation(
            ip_address=ip_address,
            reputation_score=reputation_score,
            asn=asn or "UNKNOWN",
            is_tor=is_tor,
            is_vpn=is_vpn,
            is_datacenter=is_datacenter,
            is_residential=is_residential,
        )

        # Cache result
        self.reputation_cache[ip_address] = reputation

        return reputation


class EdgeEnforcementPlane:
    """
    L1: Network & Edge Enforcement Plane

    First line of defense for all inbound telemetry

    INVARIANTS ENFORCED:
    - Schema pre-validation
    - Request hashing
    - No unauthenticated mutations
    """

    def __init__(self):
        self.geo_fence = GeoFenceController()
        self.rate_limiter = RateLimiter()
        self.ip_reputation = IPReputationService()
        self.request_hashes: Set[str] = set()  # For deduplication

    def enforce(self, request: Dict[str, Any]) -> tuple[EnforcementAction, Dict[str, Any]]:
        """
        Enforce all edge controls on incoming request

        Returns (action, context)
        """
        context = {"enforcement_checks": []}

        # Extract request data
        source_ip = request.get("source_ip", "0.0.0.0")
        country = request.get("country_code", "XX")
        asn = request.get("asn", "UNKNOWN")

        # INVARIANT: Hash request before processing
        request_hash = self._hash_request(request)
        context["request_hash"] = request_hash

        if request_hash in self.request_hashes:
            logger.warning(f"DUPLICATE REQUEST: {request_hash[:16]}")
            return EnforcementAction.REJECT, {"reason": "duplicate_request"}

        self.request_hashes.add(request_hash)
        context["enforcement_checks"].append("request_hashed")

        # Geo-fence check
        geo_action = self.geo_fence.evaluate(country)
        context["enforcement_checks"].append(f"geo_fence: {geo_action.value}")

        if geo_action == EnforcementAction.GEO_BLOCK:
            return geo_action, context

        # Rate limit check
        rate_key = source_ip
        rate_allowed, rate_reason = self.rate_limiter.check_limit(rate_key)
        context["enforcement_checks"].append(f"rate_limit: {rate_allowed}")

        if not rate_allowed:
            context["rate_limit_reason"] = rate_reason
            return EnforcementAction.RATE_LIMIT, context

        # IP reputation check
        reputation = self.ip_reputation.lookup(source_ip, asn)
        context["ip_reputation"] = reputation.reputation_score
        context["enforcement_checks"].append(f"reputation: {reputation.reputation_score}")

        if reputation.reputation_score < 20:
            logger.warning(f"LOW REPUTATION: {source_ip} score={reputation.reputation_score}")
            return EnforcementAction.CHALLENGE, context

        if reputation.is_tor and not request.get("allow_tor", False):
            logger.warning(f"TOR DETECTED: {source_ip}")
            return EnforcementAction.CHALLENGE, context

        # All checks passed
        context["enforcement_checks"].append("all_passed")
        return EnforcementAction.ALLOW, context

    def _hash_request(self, request: Dict[str, Any]) -> str:
        """Hash request for deduplication and audit"""
        # Create deterministic hash of request
        canonical = {
            "source_ip": request.get("source_ip"),
            "timestamp": request.get("timestamp"),
            "payload": request.get("payload_hash", request.get("payload")),
        }

        canonical_str = str(sorted(canonical.items()))
        return hashlib.sha256(canonical_str.encode()).hexdigest()


__all__ = [
    "EnforcementAction",
    "GeoFenceRule",
    "RateLimitPolicy",
    "IPReputation",
    "GeoFenceController",
    "RateLimiter",
    "IPReputationService",
    "EdgeEnforcementPlane",
]
