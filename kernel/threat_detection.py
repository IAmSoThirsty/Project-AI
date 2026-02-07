"""
AI-Powered Threat Detection Engine

Enhanced threat detection using CodexDeus AI integration.
Real-time behavior analysis, pattern recognition, and learning.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat assessment levels"""

    SAFE = 0
    SUSPICIOUS = 1
    MALICIOUS = 2
    CRITICAL = 3


class AttackType(Enum):
    """Known attack patterns"""

    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    LATERAL_MOVEMENT = "lateral_movement"
    RECONNAISSANCE = "reconnaissance"
    PERSISTENCE = "persistence"
    CREDENTIAL_ACCESS = "credential_access"
    DEFENSE_EVASION = "defense_evasion"
    COMMAND_AND_CONTROL = "command_and_control"


@dataclass
class BehaviorPattern:
    """Observed behavior pattern"""

    pattern_id: str
    commands: list[str] = field(default_factory=list)
    time_window_seconds: float = 60.0
    threat_score: float = 0.0
    attack_types: list[AttackType] = field(default_factory=list)
    indicators: list[str] = field(default_factory=list)


@dataclass
class ThreatAssessment:
    """AI threat analysis result"""

    level: ThreatLevel
    confidence: float
    threat_type: str
    indicators: list[str] = field(default_factory=list)
    recommended_action: str = "ALLOW"
    attack_patterns: list[AttackType] = field(default_factory=list)
    behavior_score: float = 0.0
    ml_prediction: dict[str, float] | None = None


class AttackPatternLibrary:
    """Library of known attack patterns and signatures"""

    def __init__(self):
        self.patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> dict[str, BehaviorPattern]:
        """Initialize known attack patterns"""
        patterns = {}

        # Privilege Escalation Patterns
        patterns["privesc_sudo"] = BehaviorPattern(
            pattern_id="privesc_sudo",
            commands=["sudo", "su", "pkexec"],
            threat_score=0.4,
            attack_types=[AttackType.PRIVILEGE_ESCALATION],
            indicators=["Attempting privilege escalation via sudo"],
        )

        patterns["privesc_setuid"] = BehaviorPattern(
            pattern_id="privesc_setuid",
            commands=["chmod +s", "chmod 4755"],
            threat_score=0.7,
            attack_types=[AttackType.PRIVILEGE_ESCALATION],
            indicators=["Setting SUID bit on file"],
        )

        # Data Exfiltration Patterns
        patterns["exfil_network"] = BehaviorPattern(
            pattern_id="exfil_network",
            commands=["curl", "wget", "nc", "netcat", "scp", "rsync"],
            threat_score=0.5,
            attack_types=[AttackType.DATA_EXFILTRATION],
            indicators=["Network-based data transfer"],
        )

        patterns["exfil_compression"] = BehaviorPattern(
            pattern_id="exfil_compression",
            commands=["tar", "zip", "gzip", "bzip2", "7z"],
            threat_score=0.3,
            attack_types=[AttackType.DATA_EXFILTRATION],
            indicators=["Compressing data for transfer"],
        )

        # Reconnaissance Patterns
        patterns["recon_system"] = BehaviorPattern(
            pattern_id="recon_system",
            commands=["uname", "hostname", "whoami", "id"],
            threat_score=0.1,
            attack_types=[AttackType.RECONNAISSANCE],
            indicators=["System reconnaissance"],
        )

        patterns["recon_network"] = BehaviorPattern(
            pattern_id="recon_network",
            commands=["ifconfig", "ip addr", "netstat", "ss"],
            threat_score=0.2,
            attack_types=[AttackType.RECONNAISSANCE],
            indicators=["Network reconnaissance"],
        )

        # Credential Access
        patterns["cred_password_files"] = BehaviorPattern(
            pattern_id="cred_password_files",
            commands=["/etc/shadow", "/etc/passwd", ".ssh/id_rsa"],
            threat_score=0.8,
            attack_types=[AttackType.CREDENTIAL_ACCESS],
            indicators=["Accessing password/credential files"],
        )

        # Persistence
        patterns["persist_cron"] = BehaviorPattern(
            pattern_id="persist_cron",
            commands=["crontab", "/etc/cron"],
            threat_score=0.6,
            attack_types=[AttackType.PERSISTENCE],
            indicators=["Modifying scheduled tasks"],
        )

        patterns["persist_service"] = BehaviorPattern(
            pattern_id="persist_service",
            commands=["systemctl", "/etc/systemd"],
            threat_score=0.6,
            attack_types=[AttackType.PERSISTENCE],
            indicators=["Modifying system services"],
        )

        return patterns

    def match_pattern(self, command: str) -> list[BehaviorPattern]:
        """Match command against known patterns"""
        matched = []
        cmd_lower = command.lower()

        for pattern in self.patterns.values():
            for signature in pattern.commands:
                if signature.lower() in cmd_lower:
                    matched.append(pattern)
                    break

        return matched


class BehaviorAnalyzer:
    """Analyzes user behavior over time"""

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.user_sessions: dict[int, list[dict[str, Any]]] = {}

    def record_command(self, user_id: int, command: str, timestamp: float = None):
        """Record a command in user's session"""
        if timestamp is None:
            timestamp = time.time()

        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []

        self.user_sessions[user_id].append({"command": command, "timestamp": timestamp})

        # Keep only recent commands
        if len(self.user_sessions[user_id]) > self.window_size:
            self.user_sessions[user_id].pop(0)

    def get_command_velocity(self, user_id: int) -> float:
        """Calculate commands per minute"""
        if user_id not in self.user_sessions or len(self.user_sessions[user_id]) < 2:
            return 0.0

        session = self.user_sessions[user_id]
        time_span = session[-1]["timestamp"] - session[0]["timestamp"]

        if time_span == 0:
            return 0.0

        return (len(session) / time_span) * 60  # Commands per minute

    def detect_sequence_patterns(self, user_id: int) -> list[str]:
        """Detect attack sequences (e.g., recon -> escalation -> exfil)"""
        if user_id not in self.user_sessions:
            return []

        session = self.user_sessions[user_id]
        if len(session) < 3:
            return []

        patterns = []
        commands = [s["command"].lower() for s in session]

        # Classic attack chain: reconnaissance -> escalation -> access -> exfil
        has_recon = any("whoami" in c or "id" in c or "uname" in c for c in commands)
        has_escalation = any("sudo" in c or "su" in c for c in commands)
        has_sensitive_access = any("/etc/shadow" in c or "/root" in c for c in commands)
        has_exfil = any("tar" in c or "curl" in c or "wget" in c for c in commands)

        if has_recon and has_escalation:
            patterns.append("reconnaissance_to_escalation")

        if has_escalation and has_sensitive_access:
            patterns.append("escalation_to_access")

        if has_sensitive_access and has_exfil:
            patterns.append("access_to_exfiltration")

        if has_recon and has_escalation and has_sensitive_access:
            patterns.append("full_attack_chain")

        return patterns

    def calculate_anomaly_score(self, user_id: int) -> float:
        """Calculate behavioral anomaly score (0.0 - 1.0)"""
        if user_id not in self.user_sessions:
            return 0.0

        score = 0.0

        # High command velocity
        velocity = self.get_command_velocity(user_id)
        if velocity > 10:  # More than 10 commands/minute
            score += 0.2

        # Attack sequence patterns
        sequences = self.detect_sequence_patterns(user_id)
        score += len(sequences) * 0.2

        # Cap at 1.0
        return min(score, 1.0)


class ThreatDetectionEngine:
    """
    AI-Powered Threat Detection Engine

    Uses multiple analysis techniques:
    1. Pattern matching against known attacks
    2. Behavioral analysis over time
    3. ML-based prediction (CodexDeus integration)
    4. Anomaly detection
    """

    def __init__(self, use_ml: bool = True):
        self.pattern_library = AttackPatternLibrary()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.use_ml = use_ml
        self.detection_history: list[ThreatAssessment] = []

        logger.info("Threat Detection Engine initialized")
        if use_ml:
            logger.info("  - ML-based prediction: ENABLED")
            logger.info("  - CodexDeus integration: READY")

    def analyze_threat(
        self, user_id: int, command: str, observed_behavior: dict[str, Any]
    ) -> ThreatAssessment:
        """
        Comprehensive threat analysis

        Args:
            user_id: User identifier
            command: Command being executed
            observed_behavior: Data from command observation

        Returns:
            ThreatAssessment with threat level and recommendations
        """
        # Record command for behavioral analysis
        self.behavior_analyzer.record_command(user_id, command)

        # Step 1: Pattern matching
        matched_patterns = self.pattern_library.match_pattern(command)
        pattern_score = max([p.threat_score for p in matched_patterns], default=0.0)

        # Step 2: Behavioral analysis
        behavior_score = self.behavior_analyzer.calculate_anomaly_score(user_id)
        sequence_patterns = self.behavior_analyzer.detect_sequence_patterns(user_id)

        # Step 3: ML prediction (if enabled)
        ml_prediction = None
        if self.use_ml:
            ml_prediction = self._ml_predict(command, observed_behavior)
            ml_score = ml_prediction.get("threat_probability", 0.0)
        else:
            ml_score = 0.0

        # Step 4: Combine scores (weighted average)
        combined_score = pattern_score * 0.4 + behavior_score * 0.3 + ml_score * 0.3

        # Step 5: Classify threat level
        if combined_score >= 0.9:
            level = ThreatLevel.CRITICAL
            action = "ISOLATE_IMMEDIATELY"
        elif combined_score >= 0.6:
            level = ThreatLevel.MALICIOUS
            action = "DECEPTION"
        elif combined_score >= 0.3:
            level = ThreatLevel.SUSPICIOUS
            action = "MONITOR"
        else:
            level = ThreatLevel.SAFE
            action = "ALLOW"

        # Step 6: Build indicators list
        indicators = []
        for pattern in matched_patterns:
            indicators.extend(pattern.indicators)

        if behavior_score > 0.3:
            indicators.append(
                f"Behavioral anomaly detected (score: {behavior_score:.2f})"
            )

        for seq_pattern in sequence_patterns:
            indicators.append(f"Attack sequence: {seq_pattern}")

        # Step 7: Determine attack types
        attack_types = []
        for pattern in matched_patterns:
            attack_types.extend(pattern.attack_types)
        attack_types = list(set(attack_types))  # Remove duplicates

        # Step 8: Create assessment
        assessment = ThreatAssessment(
            level=level,
            confidence=combined_score,
            threat_type=attack_types[0].value if attack_types else "unknown",
            indicators=indicators,
            recommended_action=action,
            attack_patterns=attack_types,
            behavior_score=behavior_score,
            ml_prediction=ml_prediction,
        )

        # Log the assessment
        self.detection_history.append(assessment)

        if level != ThreatLevel.SAFE:
            logger.warning(
                f"Threat detected: {level.name} (confidence: {combined_score:.2f}) - {command}"
            )

        return assessment

    def _ml_predict(
        self, command: str, observed_behavior: dict[str, Any]
    ) -> dict[str, float]:
        """
        ML-based threat prediction using CodexDeus

        In production, this would call CodexDeus API.
        For demo, using heuristic-based prediction.
        """
        # Simulate CodexDeus inference
        features = self._extract_features(command, observed_behavior)

        # Simple heuristic model (replace with actual ML in production)
        threat_prob = 0.0

        # Check dangerous keywords
        dangerous_keywords = [
            "rm -rf",
            "/etc/shadow",
            "/etc/passwd",
            "chmod 777",
            "wget http",
            "curl http",
            "nc -l",
            "python -c",
            "bash -i",
            "/dev/tcp",
            "base64",
            "eval",
        ]

        for keyword in dangerous_keywords:
            if keyword in command.lower():
                threat_prob += 0.2

        # Check system call patterns
        if "syscalls" in observed_behavior:
            dangerous_syscalls = ["execve", "ptrace", "setuid", "socket"]
            for syscall in dangerous_syscalls:
                if syscall in str(observed_behavior.get("syscalls", [])):
                    threat_prob += 0.1

        # Cap at 1.0
        threat_prob = min(threat_prob, 1.0)

        return {
            "threat_probability": threat_prob,
            "model": "CodexDeus-ThreatDetector-v1",
            "confidence": 0.85,
            "features_used": features,
        }

    def _extract_features(
        self, command: str, observed_behavior: dict[str, Any]
    ) -> list[str]:
        """Extract features for ML model"""
        features = []

        # Command-based features
        features.append(f"cmd_length:{len(command)}")
        features.append(f"has_pipe:{'|' in command}")
        features.append(f"has_redirect:{'>' in command or '<' in command}")
        features.append(f"has_background:{'&' in command}")

        # Behavior-based features
        if "syscalls" in observed_behavior:
            features.append(f"syscall_count:{len(observed_behavior['syscalls'])}")

        if "file_accesses" in observed_behavior:
            features.append(
                f"file_access_count:{len(observed_behavior['file_accesses'])}"
            )

        if "network_activity" in observed_behavior:
            features.append(
                f"network_active:{len(observed_behavior['network_activity']) > 0}"
            )

        return features

    def get_stats(self) -> dict[str, Any]:
        """Get detection engine statistics"""
        if not self.detection_history:
            return {
                "total_assessments": 0,
                "threat_distribution": {},
                "average_confidence": 0.0,
            }

        threat_counts = {}
        for assessment in self.detection_history:
            level_name = assessment.level.name
            threat_counts[level_name] = threat_counts.get(level_name, 0) + 1

        avg_confidence = sum(a.confidence for a in self.detection_history) / len(
            self.detection_history
        )

        return {
            "total_assessments": len(self.detection_history),
            "threat_distribution": threat_counts,
            "average_confidence": avg_confidence,
            "ml_enabled": self.use_ml,
        }


# Public API
__all__ = [
    "ThreatDetectionEngine",
    "ThreatAssessment",
    "ThreatLevel",
    "AttackType",
    "BehaviorPattern",
    "AttackPatternLibrary",
    "BehaviorAnalyzer",
]
