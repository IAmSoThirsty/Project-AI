"""Honeypot Detection System.

Implements honeypot endpoints and attack detection for defensive security.
Monitors fake vulnerable endpoints to detect and study attackers without
retaliating.

Features:
- Fake vulnerable endpoints (SQL injection, XSS, file upload, etc.)
- Attack pattern detection and fingerprinting
- Attacker behavior analysis
- Integration with IP blocking system
- Forensic data collection for law enforcement
- Threat intelligence generation

Defensive only - no offensive capabilities.
"""

import json
import logging
import re
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, UTC
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AttackType(Enum):
    """Types of attacks detected."""

    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    FILE_UPLOAD = "file_upload"
    AUTHENTICATION_BYPASS = "authentication_bypass"
    XXSS = "xxss"
    CSRF = "csrf"
    DESERIALIZATION = "deserialization"
    SSRF = "ssrf"
    XXE = "xxe"
    LDAP_INJECTION = "ldap_injection"
    UNKNOWN = "unknown"


@dataclass
class AttackAttempt:
    """Record of an attack attempt on honeypot."""

    attempt_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    ip_address: str = ""
    endpoint: str = ""
    attack_type: str = AttackType.UNKNOWN.value
    method: str = ""  # HTTP method
    payload: str = ""
    user_agent: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"
    fingerprint: str = ""  # Attack signature
    tool_detected: str | None = None  # e.g., "sqlmap", "nikto"
    action_taken: str = "logged"


@dataclass
class AttackerProfile:
    """Profile of an attacker based on behavior."""

    ip_address: str
    first_seen: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    attempt_count: int = 0
    attack_types_used: list[str] = field(default_factory=list)
    tools_detected: list[str] = field(default_factory=list)
    sophistication_score: float = 0.0  # 0-10 scale
    targeting_pattern: str = "random"  # "random", "targeted", "automated"
    blocked: bool = False


class HoneypotDetector:
    """
    Honeypot Detection System.

    Implements fake vulnerable endpoints to detect attackers.
    Collects forensic data without engaging in offensive actions.
    """

    def __init__(self, data_dir: str = "data/security/honeypot"):
        """
        Initialize honeypot detector.

        Args:
            data_dir: Directory for persistence
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # State
        self.attack_attempts: list[AttackAttempt] = []
        self.attacker_profiles: dict[str, AttackerProfile] = {}

        # Attack pattern signatures
        self.sql_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bor\b\s+\d+\s*=\s*\d+)",
            r"(\bselect\b.*\bfrom\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(;.*--)",
            r"(\bexec\b|\bexecute\b)",
        ]

        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"onerror\s*=",
            r"onload\s*=",
            r"<iframe",
        ]

        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e/",
            r"%252e%252e",
        ]

        self.command_injection_patterns = [
            r"[;&|].*\b(ls|cat|rm|wget|curl)\b",
            r"\$\(.*\)",
            r"`.*`",
        ]

        # Tool fingerprints
        self.tool_signatures = {
            "sqlmap": ["sqlmap", "User-Agent: sqlmap"],
            "nikto": ["nikto", "User-Agent: Nikto"],
            "burp": ["Burp Suite", "User-Agent: Burp"],
            "metasploit": ["Metasploit", "User-Agent: Metasploit"],
            "nmap": ["Nmap Scripting Engine"],
            "acunetix": ["Acunetix"],
            "zap": ["OWASP ZAP"],
        }

        # Persistence
        self.attempts_file = self.data_dir / "attack_attempts.json"
        self.profiles_file = self.data_dir / "attacker_profiles.json"

        # Load state
        self._load_state()

        logger.info("Honeypot Detection System initialized")
        logger.info(f"  Attack patterns: SQL, XSS, Path Traversal, Command Injection")
        logger.info(f"  Tool detection: {len(self.tool_signatures)} signatures")

    def analyze_request(
        self,
        ip_address: str,
        endpoint: str,
        method: str,
        payload: str,
        user_agent: str = "",
        headers: dict[str, str] | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> AttackAttempt | None:
        """
        Analyze a request for attack patterns.

        Args:
            ip_address: Source IP
            endpoint: Endpoint accessed
            method: HTTP method
            payload: Request payload/body
            user_agent: User agent string
            headers: Request headers
            parameters: Request parameters

        Returns:
            AttackAttempt if attack detected, None otherwise
        """
        headers = headers or {}
        parameters = parameters or {}

        # Detect attack type
        attack_types = []

        # Check for SQL injection
        for pattern in self.sql_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                attack_types.append(AttackType.SQL_INJECTION.value)
                break

        # Check for XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                attack_types.append(AttackType.XSS.value)
                break

        # Check for path traversal
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, payload, re.IGNORECASE) or re.search(pattern, endpoint, re.IGNORECASE):
                attack_types.append(AttackType.PATH_TRAVERSAL.value)
                break

        # Check for command injection
        for pattern in self.command_injection_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                attack_types.append(AttackType.COMMAND_INJECTION.value)
                break

        # If no specific attack detected but suspicious, mark as unknown
        if not attack_types and self._is_suspicious(payload, endpoint, user_agent):
            attack_types.append(AttackType.UNKNOWN.value)

        # If attack detected, record it
        if attack_types:
            attack_type = attack_types[0]  # Primary attack type

            # Detect tool
            tool_detected = self._detect_tool(user_agent, headers, payload)

            # Calculate severity
            severity = self._calculate_severity(attack_type, tool_detected)

            # Create fingerprint
            fingerprint = self._create_fingerprint(attack_type, payload, tool_detected)

            # Record attack attempt
            attempt = AttackAttempt(
                ip_address=ip_address,
                endpoint=endpoint,
                attack_type=attack_type,
                method=method,
                payload=payload[:1000],  # Limit payload size
                user_agent=user_agent,
                headers=headers,
                parameters=parameters,
                severity=severity,
                fingerprint=fingerprint,
                tool_detected=tool_detected,
                action_taken="logged",
            )

            self.attack_attempts.append(attempt)
            self._update_attacker_profile(ip_address, attack_type, tool_detected)
            self._save_state()

            logger.warning(
                f"Attack detected: {attack_type} from {ip_address} on {endpoint}"
            )
            if tool_detected:
                logger.warning(f"  Tool detected: {tool_detected}")

            return attempt

        return None

    def _is_suspicious(self, payload: str, endpoint: str, user_agent: str) -> bool:
        """Check if request is suspicious even if no specific attack detected."""
        suspicious_indicators = [
            "eval(",
            "base64_decode",
            "system(",
            "exec(",
            "passthru(",
            "shell_exec(",
            "../../",
            "%00",  # Null byte
            "0x",  # Hex encoding
        ]

        # Check payload
        payload_lower = payload.lower()
        for indicator in suspicious_indicators:
            if indicator in payload_lower:
                return True

        # Check endpoint
        endpoint_lower = endpoint.lower()
        suspicious_endpoints = [
            "admin", "backup", "config", "database", "phpinfo",
            "shell", "upload", "xmlrpc", "wp-admin"
        ]
        for suspicious in suspicious_endpoints:
            if suspicious in endpoint_lower:
                return True

        # Empty or suspicious user agent
        if not user_agent or user_agent in ["", "-", "python-requests", "curl"]:
            return True

        return False

    def _detect_tool(
        self, user_agent: str, headers: dict[str, str], payload: str
    ) -> str | None:
        """Detect scanning/attack tool being used."""
        search_text = f"{user_agent} {str(headers)} {payload}".lower()

        for tool_name, signatures in self.tool_signatures.items():
            for signature in signatures:
                if signature.lower() in search_text:
                    return tool_name

        return None

    def _calculate_severity(self, attack_type: str, tool_detected: str | None) -> str:
        """Calculate severity of attack."""
        # Base severity by attack type
        high_severity = [
            AttackType.SQL_INJECTION.value,
            AttackType.COMMAND_INJECTION.value,
            AttackType.DESERIALIZATION.value,
        ]

        medium_severity = [
            AttackType.XSS.value,
            AttackType.SSRF.value,
            AttackType.XXE.value,
        ]

        if attack_type in high_severity:
            severity = "high"
        elif attack_type in medium_severity:
            severity = "medium"
        else:
            severity = "low"

        # Increase severity if automated tool detected
        if tool_detected and severity != "high":
            severity = "high" if severity == "medium" else "medium"

        return severity

    def _create_fingerprint(
        self, attack_type: str, payload: str, tool_detected: str | None
    ) -> str:
        """Create attack fingerprint for tracking."""
        import hashlib

        # Create fingerprint from attack characteristics
        fp_data = f"{attack_type}:{tool_detected or 'manual'}:{payload[:100]}"
        return hashlib.sha256(fp_data.encode()).hexdigest()[:16]

    def _update_attacker_profile(
        self, ip_address: str, attack_type: str, tool_detected: str | None
    ) -> None:
        """Update attacker profile based on new attack."""
        if ip_address not in self.attacker_profiles:
            self.attacker_profiles[ip_address] = AttackerProfile(ip_address=ip_address)

        profile = self.attacker_profiles[ip_address]
        profile.last_seen = datetime.now(UTC).isoformat()
        profile.attempt_count += 1

        if attack_type not in profile.attack_types_used:
            profile.attack_types_used.append(attack_type)

        if tool_detected and tool_detected not in profile.tools_detected:
            profile.tools_detected.append(tool_detected)

        # Calculate sophistication score
        profile.sophistication_score = self._calculate_sophistication(profile)

        # Determine targeting pattern
        profile.targeting_pattern = self._determine_pattern(profile)

    def _calculate_sophistication(self, profile: AttackerProfile) -> float:
        """Calculate attacker sophistication (0-10 scale)."""
        score = 0.0

        # Variety of attack types (max 3 points)
        score += min(len(profile.attack_types_used) * 0.5, 3.0)

        # Use of tools (max 3 points)
        score += min(len(profile.tools_detected) * 1.0, 3.0)

        # Persistence (max 4 points)
        if profile.attempt_count > 100:
            score += 4.0
        elif profile.attempt_count > 50:
            score += 3.0
        elif profile.attempt_count > 20:
            score += 2.0
        elif profile.attempt_count > 10:
            score += 1.0

        return min(score, 10.0)

    def _determine_pattern(self, profile: AttackerProfile) -> str:
        """Determine if attacks are random, targeted, or automated."""
        if len(profile.tools_detected) > 0:
            return "automated"
        elif len(profile.attack_types_used) > 3:
            return "targeted"
        else:
            return "random"

    def get_statistics(self) -> dict[str, Any]:
        """Get honeypot statistics."""
        total_attempts = len(self.attack_attempts)

        # Count by attack type
        attack_type_counts = defaultdict(int)
        for attempt in self.attack_attempts:
            attack_type_counts[attempt.attack_type] += 1

        # Count by tool
        tool_counts = defaultdict(int)
        for attempt in self.attack_attempts:
            if attempt.tool_detected:
                tool_counts[attempt.tool_detected] += 1

        return {
            "total_attack_attempts": total_attempts,
            "unique_attackers": len(self.attacker_profiles),
            "attack_types": dict(attack_type_counts),
            "tools_detected": dict(tool_counts),
            "recent_attempts_24h": self._count_recent_attempts(24),
            "blocked_attackers": sum(
                1 for p in self.attacker_profiles.values() if p.blocked
            ),
        }

    def _count_recent_attempts(self, hours: int) -> int:
        """Count attacks in last N hours."""
        from datetime import timedelta

        cutoff = datetime.now(UTC) - timedelta(hours=hours)
        count = 0

        for attempt in self.attack_attempts:
            attempt_time = datetime.fromisoformat(attempt.timestamp)
            if attempt_time > cutoff:
                count += 1

        return count

    def get_attacker_profiles(self) -> list[dict[str, Any]]:
        """Get all attacker profiles."""
        return [asdict(profile) for profile in self.attacker_profiles.values()]

    def get_high_threat_attackers(self) -> list[dict[str, Any]]:
        """Get attackers with high sophistication or attempt count."""
        high_threat = [
            asdict(profile)
            for profile in self.attacker_profiles.values()
            if profile.sophistication_score >= 7.0 or profile.attempt_count >= 50
        ]
        return sorted(high_threat, key=lambda x: x["sophistication_score"], reverse=True)

    def _load_state(self) -> None:
        """Load state from disk."""
        try:
            if self.attempts_file.exists():
                with open(self.attempts_file) as f:
                    attempt_data = json.load(f)
                    # Load last 10000 attempts
                    self.attack_attempts = [
                        AttackAttempt(**a) for a in attempt_data[-10000:]
                    ]
                logger.info(f"Loaded {len(self.attack_attempts)} attack attempts")

            if self.profiles_file.exists():
                with open(self.profiles_file) as f:
                    profile_data = json.load(f)
                    self.attacker_profiles = {
                        ip: AttackerProfile(**data) for ip, data in profile_data.items()
                    }
                logger.info(f"Loaded {len(self.attacker_profiles)} attacker profiles")

        except Exception as e:
            logger.error(f"Error loading honeypot state: {e}")

    def _save_state(self) -> None:
        """Save state to disk."""
        try:
            # Save attempts (keep last 10000)
            with open(self.attempts_file, "w") as f:
                attempt_data = [asdict(a) for a in self.attack_attempts[-10000:]]
                json.dump(attempt_data, f, indent=2)

            # Save profiles
            with open(self.profiles_file, "w") as f:
                profile_data = {
                    ip: asdict(profile)
                    for ip, profile in self.attacker_profiles.items()
                }
                json.dump(profile_data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving honeypot state: {e}")
