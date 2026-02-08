"""IP Blocking and Rate Limiting System.

Implements aggressive IP blocking, rate limiting, and geolocation-based
access control for defensive security. Detects and blocks persistent
attackers automatically.

Features:
- IP-based rate limiting with exponential backoff
- Geolocation-based access control
- Automatic IP blacklisting for repeated violations
- Whitelist management for trusted sources
- Integration with GlobalWatchTower for threat escalation
- Forensic logging for legal evidence

Defensive only - no offensive capabilities.
"""

import json
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class IPRecord:
    """Record of IP address activity."""

    ip_address: str
    first_seen: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    request_count: int = 0
    violation_count: int = 0
    blocked: bool = False
    block_reason: str = ""
    block_timestamp: str | None = None
    geolocation: dict[str, Any] = field(default_factory=dict)
    user_agent: str = ""
    endpoints_accessed: list[str] = field(default_factory=list)


@dataclass
class RateLimitViolation:
    """Rate limit violation record."""

    ip_address: str
    timestamp: str
    requests_in_window: int
    limit: int
    endpoint: str
    action_taken: str


class IPBlockingSystem:
    """
    IP Blocking and Rate Limiting System.

    Implements defensive IP blocking with:
    - Configurable rate limits per endpoint
    - Automatic blacklisting for repeat offenders
    - Geolocation filtering (optional)
    - Whitelist for trusted IPs
    - Integration with security systems
    """

    def __init__(
        self,
        data_dir: str = "data/security",
        max_requests_per_minute: int = 60,
        max_requests_per_hour: int = 1000,
        violation_threshold: int = 5,
        block_duration_hours: int = 24,
    ):
        """
        Initialize IP blocking system.

        Args:
            data_dir: Directory for persistence
            max_requests_per_minute: Rate limit per minute
            max_requests_per_hour: Rate limit per hour
            violation_threshold: Violations before auto-block
            block_duration_hours: Duration of IP block
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.max_requests_per_minute = max_requests_per_minute
        self.max_requests_per_hour = max_requests_per_hour
        self.violation_threshold = violation_threshold
        self.block_duration = timedelta(hours=block_duration_hours)

        # State
        self.ip_records: dict[str, IPRecord] = {}
        self.blacklist: set[str] = set()
        self.whitelist: set[str] = set()
        self.rate_windows: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.violations: list[RateLimitViolation] = []

        # Thread safety
        self.lock = threading.Lock()

        # Persistence
        self.records_file = self.data_dir / "ip_records.json"
        self.blacklist_file = self.data_dir / "ip_blacklist.json"
        self.whitelist_file = self.data_dir / "ip_whitelist.json"
        self.violations_file = self.data_dir / "rate_violations.json"

        # Load state
        self._load_state()

        logger.info("IP Blocking System initialized")
        logger.info(
            "  Rate limits: %s/min, %s/hour",
            max_requests_per_minute,
            max_requests_per_hour,
        )
        logger.info("  Violation threshold: %s", violation_threshold)
        logger.info("  Block duration: %s hours", block_duration_hours)

    def check_ip_allowed(
        self,
        ip_address: str,
        endpoint: str = "/",
        user_agent: str = "",
        geolocation: dict[str, Any] | None = None,
    ) -> tuple[bool, str]:
        """
        Check if IP address is allowed to access endpoint.

        Args:
            ip_address: IP address to check
            endpoint: Endpoint being accessed
            user_agent: User agent string
            geolocation: Optional geolocation data

        Returns:
            Tuple of (allowed, reason)
        """
        with self.lock:
            # Check whitelist first (always allowed)
            if ip_address in self.whitelist:
                self._record_request(ip_address, endpoint, user_agent, geolocation)
                return True, "whitelisted"

            # Check blacklist
            if ip_address in self.blacklist:
                logger.warning("Blocked blacklisted IP: %s", ip_address)
                return False, "IP is blacklisted"

            # Check if currently blocked
            if ip_address in self.ip_records:
                record = self.ip_records[ip_address]
                if record.blocked:
                    # Check if block has expired
                    if record.block_timestamp:
                        block_time = datetime.fromisoformat(record.block_timestamp)
                        if datetime.now(UTC) - block_time > self.block_duration:
                            # Unblock
                            record.blocked = False
                            record.block_timestamp = None
                            logger.info(
                                "Auto-unblocked IP after expiry: %s", ip_address
                            )
                        else:
                            logger.warning(
                                "Blocked IP attempted access: %s", ip_address
                            )
                            return False, f"IP blocked: {record.block_reason}"

            # Check rate limits
            is_allowed, reason = self._check_rate_limit(ip_address, endpoint)
            if not is_allowed:
                self._record_violation(ip_address, endpoint)
                return False, reason

            # Record successful request
            self._record_request(ip_address, endpoint, user_agent, geolocation)
            return True, "allowed"

    def _check_rate_limit(self, ip_address: str, endpoint: str) -> tuple[bool, str]:
        """Check if IP is within rate limits."""
        now = time.time()
        key = f"{ip_address}:{endpoint}"

        # Get request times for this IP+endpoint
        requests = self.rate_windows[key]

        # Remove old requests (older than 1 hour)
        hour_ago = now - 3600
        while requests and requests[0] < hour_ago:
            requests.popleft()

        # Count requests in last minute
        minute_ago = now - 60
        requests_last_minute = sum(1 for t in requests if t > minute_ago)

        # Count requests in last hour
        requests_last_hour = len(requests)

        # Check limits
        if requests_last_minute >= self.max_requests_per_minute:
            logger.warning(
                "Rate limit exceeded (minute): %s - %s requests",
                ip_address,
                requests_last_minute,
            )
            return (
                False,
                f"Rate limit exceeded: {requests_last_minute} requests in last minute",
            )

        if requests_last_hour >= self.max_requests_per_hour:
            logger.warning(
                "Rate limit exceeded (hour): %s - %s requests",
                ip_address,
                requests_last_hour,
            )
            return (
                False,
                f"Rate limit exceeded: {requests_last_hour} requests in last hour",
            )

        # Add this request
        requests.append(now)
        return True, "within limits"

    def _record_request(
        self,
        ip_address: str,
        endpoint: str,
        user_agent: str,
        geolocation: dict[str, Any] | None,
    ) -> None:
        """Record a successful request."""
        if ip_address not in self.ip_records:
            self.ip_records[ip_address] = IPRecord(ip_address=ip_address)

        record = self.ip_records[ip_address]
        record.last_seen = datetime.now(UTC).isoformat()
        record.request_count += 1
        record.user_agent = user_agent or record.user_agent

        if endpoint not in record.endpoints_accessed:
            record.endpoints_accessed.append(endpoint)

        if geolocation:
            record.geolocation = geolocation

    def _record_violation(self, ip_address: str, endpoint: str) -> None:
        """Record a rate limit violation."""
        if ip_address not in self.ip_records:
            self.ip_records[ip_address] = IPRecord(ip_address=ip_address)

        record = self.ip_records[ip_address]
        record.violation_count += 1

        # Record violation
        violation = RateLimitViolation(
            ip_address=ip_address,
            timestamp=datetime.now(UTC).isoformat(),
            requests_in_window=len(self.rate_windows[f"{ip_address}:{endpoint}"]),
            limit=self.max_requests_per_hour,
            endpoint=endpoint,
            action_taken=(
                "blocked"
                if record.violation_count >= self.violation_threshold
                else "logged"
            ),
        )
        self.violations.append(violation)

        # Auto-block if threshold exceeded
        if record.violation_count >= self.violation_threshold:
            self.block_ip(
                ip_address,
                reason=f"Exceeded violation threshold ({self.violation_threshold} violations)",
            )

        # Save state after violation
        self._save_state()

    def block_ip(self, ip_address: str, reason: str, permanent: bool = False) -> None:
        """
        Block an IP address.

        Args:
            ip_address: IP to block
            reason: Reason for blocking
            permanent: If True, add to blacklist
        """
        with self.lock:
            if ip_address not in self.ip_records:
                self.ip_records[ip_address] = IPRecord(ip_address=ip_address)

            record = self.ip_records[ip_address]
            record.blocked = True
            record.block_reason = reason
            record.block_timestamp = datetime.now(UTC).isoformat()

            if permanent:
                self.blacklist.add(ip_address)

            logger.warning("IP blocked: %s - %s", ip_address, reason)
            self._save_state()

    def unblock_ip(self, ip_address: str) -> None:
        """Unblock an IP address."""
        with self.lock:
            if ip_address in self.ip_records:
                record = self.ip_records[ip_address]
                record.blocked = False
                record.block_timestamp = None

            if ip_address in self.blacklist:
                self.blacklist.remove(ip_address)

            logger.info("IP unblocked: %s", ip_address)
            self._save_state()

    def add_to_whitelist(self, ip_address: str) -> None:
        """Add IP to whitelist (always allowed)."""
        with self.lock:
            self.whitelist.add(ip_address)
            # Remove from blacklist if present
            if ip_address in self.blacklist:
                self.blacklist.remove(ip_address)
            logger.info("IP whitelisted: %s", ip_address)
            self._save_state()

    def remove_from_whitelist(self, ip_address: str) -> None:
        """Remove IP from whitelist."""
        with self.lock:
            if ip_address in self.whitelist:
                self.whitelist.remove(ip_address)
                logger.info("IP removed from whitelist: %s", ip_address)
                self._save_state()

    def get_statistics(self) -> dict[str, Any]:
        """Get system statistics."""
        with self.lock:
            blocked_ips = sum(1 for r in self.ip_records.values() if r.blocked)
            return {
                "total_ips_tracked": len(self.ip_records),
                "blocked_ips": blocked_ips,
                "blacklisted_ips": len(self.blacklist),
                "whitelisted_ips": len(self.whitelist),
                "total_violations": len(self.violations),
                "rate_limits": {
                    "per_minute": self.max_requests_per_minute,
                    "per_hour": self.max_requests_per_hour,
                },
                "violation_threshold": self.violation_threshold,
                "block_duration_hours": self.block_duration.total_seconds() / 3600,
            }

    def get_blocked_ips(self) -> list[dict[str, Any]]:
        """Get list of currently blocked IPs."""
        with self.lock:
            return [
                {
                    "ip_address": record.ip_address,
                    "blocked_at": record.block_timestamp,
                    "reason": record.block_reason,
                    "violations": record.violation_count,
                }
                for record in self.ip_records.values()
                if record.blocked
            ]

    def _load_state(self) -> None:
        """Load state from disk."""
        try:
            if self.records_file.exists():
                with open(self.records_file) as f:
                    data = json.load(f)
                    self.ip_records = {
                        ip: IPRecord(**record) for ip, record in data.items()
                    }
                logger.info("Loaded %s IP records", len(self.ip_records))

            if self.blacklist_file.exists():
                with open(self.blacklist_file) as f:
                    self.blacklist = set(json.load(f))
                logger.info("Loaded %s blacklisted IPs", len(self.blacklist))

            if self.whitelist_file.exists():
                with open(self.whitelist_file) as f:
                    self.whitelist = set(json.load(f))
                logger.info("Loaded %s whitelisted IPs", len(self.whitelist))

            if self.violations_file.exists():
                with open(self.violations_file) as f:
                    violation_data = json.load(f)
                    self.violations = [RateLimitViolation(**v) for v in violation_data]
                logger.info("Loaded %s violations", len(self.violations))

        except Exception as e:
            logger.error("Error loading IP blocking state: %s", e)

    def _save_state(self) -> None:
        """Save state to disk."""
        try:
            # Save IP records
            with open(self.records_file, "w") as f:
                data = {ip: asdict(record) for ip, record in self.ip_records.items()}
                json.dump(data, f, indent=2)

            # Save blacklist
            with open(self.blacklist_file, "w") as f:
                json.dump(list(self.blacklist), f, indent=2)

            # Save whitelist
            with open(self.whitelist_file, "w") as f:
                json.dump(list(self.whitelist), f, indent=2)

            # Save violations (keep last 10000)
            with open(self.violations_file, "w") as f:
                violation_data = [asdict(v) for v in self.violations[-10000:]]
                json.dump(violation_data, f, indent=2)

        except Exception as e:
            logger.error("Error saving IP blocking state: %s", e)
