"""
Thirsty's Honeypot Swarm Defense (T.H.S.D.) - Turn Weakness Into Strength

CONCEPT: The weakest link in security is HUMANS (trust, error, predictability).
Instead of trying to eliminate this weakness, we turn it into BAIT.

REAL-WORLD ANALOGY: Honeybee Hive Defense
- Bees protect the hive by SWARMING attackers
- Weak individuals become STRONG through COLLECTIVE ACTION
- The more you attack, the MORE defenders appear
- Attackers face COGNITIVE OVERLOAD from confusion

SECURITY INNOVATION:
1. Deploy DECOY systems that LOOK like weak links
2. Policy violations trigger SWARM RESPONSE
3. Collective intelligence from all network nodes
4. Adaptive escalation - attacks make defense STRONGER
5. Cognitive warfare - can't tell real from fake
"""

import logging
import time
import random
import hashlib
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ThreatLevel(Enum):
    """Threat escalation levels"""

    SCOUT = "scout"  # 1-2 violations
    PROBE = "probe"  # 3-5 violations
    ATTACK = "attack"  # 6-10 violations
    SIEGE = "siege"  # 11-20 violations
    SWARM = "swarm"  # 21+ violations - FULL RESPONSE


class DecoyType(Enum):
    """Types of honeypot decoys"""

    FAKE_ADMIN_PANEL = "fake_admin_panel"
    FAKE_DATABASE = "fake_database"
    FAKE_API_ENDPOINT = "fake_api_endpoint"
    FAKE_SSH_SERVER = "fake_ssh_server"
    FAKE_CONFIG_FILE = "fake_config_file"
    FAKE_CREDENTIAL = "fake_credential"
    FAKE_NETWORK_SHARE = "fake_network_share"


@dataclass
class Attacker:
    """Tracked attacker profile"""

    ip_address: str
    first_seen: datetime
    last_seen: datetime
    violation_count: int = 0
    threat_level: ThreatLevel = ThreatLevel.SCOUT
    accessed_decoys: Set[str] = field(default_factory=set)
    attack_patterns: List[str] = field(default_factory=list)
    cognitive_overload_score: float = 0.0


@dataclass
class DecoyNode:
    """Honeypot decoy that looks like weak link"""

    decoy_id: str
    decoy_type: DecoyType
    believability_score: float  # 0.0-1.0, how "real" it looks
    access_count: int = 0
    triggered_by: Set[str] = field(default_factory=set)
    is_hot: bool = False  # Currently being probed


class ThirstysHoneypotSwarmDefense:
    """
    Thirsty's Honeypot Swarm Defense (THSD) - Biological Security

    THE WEAKEST LINK STRATEGY:
    Instead of hardening weak points, we CREATE intentional weak points (decoys)
    that ATTRACT attackers. When attacker takes the bait, the SWARM responds.

    KEY INNOVATION:
    The more you attack, the MORE decoys appear. Eventually, attacker faces:
    - 100+ fake admin panels
    - 1000+ fake credentials
    - Infinite rabbit holes
    - Cognitive overload - can't tell real from fake

    BIOLOGICAL INSPIRATION:
    - Honeybees: Weak individuals, strong collective
    - Ants: Decoy nests, mislead predators
    - Fish schools: Confusion through overwhelming numbers
    - Immune system: Learns and adapts from attacks
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

        # Attacker tracking
        self.attackers: Dict[str, Attacker] = {}

        # Decoy deployment
        self.decoys: Dict[str, DecoyNode] = {}
        self.base_decoy_count = self.config.get("base_decoy_count", 10)

        # Swarm parameters
        self.swarm_multiplier = self.config.get("swarm_multiplier", 3.0)
        self.escalation_threshold = self.config.get("escalation_threshold", 3)

        # Collective intelligence
        self.network_threat_score = 0.0
        self.global_decoy_effectiveness = {}

        # Initialize base decoys
        self._deploy_base_decoys()

    def _deploy_base_decoys(self):
        """Deploy initial honeypot decoys"""
        # Create believable weak links
        decoy_configs = [
            (DecoyType.FAKE_ADMIN_PANEL, 0.85, "Looks like WordPress admin"),
            (DecoyType.FAKE_DATABASE, 0.75, "MySQL with default creds"),
            (DecoyType.FAKE_SSH_SERVER, 0.90, "SSH with common usernames"),
            (DecoyType.FAKE_API_ENDPOINT, 0.80, "API with no auth"),
            (DecoyType.FAKE_CONFIG_FILE, 0.95, ".env file with secrets"),
        ]

        for i, (decoy_type, believability, desc) in enumerate(decoy_configs):
            for j in range(self.base_decoy_count // len(decoy_configs)):
                decoy_id = f"{decoy_type.value}_{i}_{j}"
                self.decoys[decoy_id] = DecoyNode(
                    decoy_id=decoy_id,
                    decoy_type=decoy_type,
                    believability_score=believability,
                )

        self.logger.info(f"Deployed {len(self.decoys)} base honeypot decoys")

    def detect_policy_violation(
        self, source_ip: str, violation_type: str, details: Dict
    ) -> Dict:
        """
        Detect policy violation and trigger swarm response

        KEY ALGORITHM:
        1. Track attacker
        2. Escalate threat level based on violations
        3. Deploy MORE decoys as threat increases
        4. Create cognitive overload
        5. Eventually, attacker can't find real target
        """
        # Track or create attacker profile
        if source_ip not in self.attackers:
            self.attackers[source_ip] = Attacker(
                ip_address=source_ip,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
            )

        attacker = self.attackers[source_ip]
        attacker.violation_count += 1
        attacker.last_seen = datetime.now()
        attacker.attack_patterns.append(violation_type)

        # Escalate threat level
        old_level = attacker.threat_level
        attacker.threat_level = self._calculate_threat_level(attacker.violation_count)

        # SWARM RESPONSE: Deploy more decoys as threat escalates
        if attacker.threat_level != old_level:
            self._escalate_swarm_response(source_ip, attacker.threat_level)

        # Calculate cognitive overload
        attacker.cognitive_overload_score = self._calculate_cognitive_overload(attacker)

        self.logger.warning(
            f"Policy violation detected: {source_ip} | "
            f"Level: {attacker.threat_level.value} | "
            f"Violations: {attacker.violation_count} | "
            f"Overload: {attacker.cognitive_overload_score:.2f}"
        )

        return {
            "attacker_ip": source_ip,
            "threat_level": attacker.threat_level.value,
            "violation_count": attacker.violation_count,
            "cognitive_overload": attacker.cognitive_overload_score,
            "active_decoys": len(self.decoys),
            "swarm_active": attacker.threat_level
            in [ThreatLevel.SIEGE, ThreatLevel.SWARM],
        }

    def _calculate_threat_level(self, violation_count: int) -> ThreatLevel:
        """Escalate threat level based on violations"""
        if violation_count >= 21:
            return ThreatLevel.SWARM
        elif violation_count >= 11:
            return ThreatLevel.SIEGE
        elif violation_count >= 6:
            return ThreatLevel.ATTACK
        elif violation_count >= 3:
            return ThreatLevel.PROBE
        else:
            return ThreatLevel.SCOUT

    def _escalate_swarm_response(self, source_ip: str, threat_level: ThreatLevel):
        """
        SWARM ESCALATION - The more you attack, the more decoys appear

        This is the KEY INNOVATION:
        - Scout level: 10 decoys
        - Probe level: 30 decoys
        - Attack level: 90 decoys
        - Siege level: 270 decoys
        - Swarm level: 810+ decoys (COGNITIVE OVERLOAD)
        """
        # Calculate target decoy count based on threat
        multipliers = {
            ThreatLevel.SCOUT: 1,
            ThreatLevel.PROBE: 3,
            ThreatLevel.ATTACK: 9,
            ThreatLevel.SIEGE: 27,
            ThreatLevel.SWARM: 81,
        }

        target_count = self.base_decoy_count * multipliers[threat_level]
        current_count = len(self.decoys)

        if current_count < target_count:
            new_decoys = target_count - current_count
            self._spawn_decoys(new_decoys, threat_level)

            self.logger.warning(
                f"SWARM ESCALATION: {source_ip} | "
                f"Level: {threat_level.value} | "
                f"Deployed {new_decoys} new decoys | "
                f"Total: {len(self.decoys)} decoys"
            )

    def _spawn_decoys(self, count: int, threat_level: ThreatLevel):
        """Spawn additional decoys to confuse attacker"""
        # Higher threat = more diverse decoy types
        decoy_variety = len(DecoyType) if threat_level == ThreatLevel.SWARM else 3

        for i in range(count):
            decoy_type = random.choice(list(DecoyType)[:decoy_variety])

            # Generate unique decoy ID
            decoy_hash = hashlib.sha256(
                f"{decoy_type.value}_{time.time()}_{i}".encode()
            ).hexdigest()[:12]

            decoy_id = f"{decoy_type.value}_{decoy_hash}"

            # Slightly randomize believability
            base_believability = 0.75
            believability = base_believability + random.uniform(-0.1, 0.15)
            believability = min(0.99, max(0.5, believability))

            self.decoys[decoy_id] = DecoyNode(
                decoy_id=decoy_id,
                decoy_type=decoy_type,
                believability_score=believability,
            )

    def _calculate_cognitive_overload(self, attacker: Attacker) -> float:
        """
        Calculate cognitive overload score

        The more decoys the attacker has accessed, the MORE confused
        they become.
        Eventually they can't tell real from fake - MISSION ACCOMPLISHED.
        """
        # Base confusion from number of decoys accessed
        decoy_confusion = len(attacker.accessed_decoys) / 10.0

        # Pattern chaos - inconsistent attack patterns indicate confusion
        pattern_diversity = len(set(attacker.attack_patterns)) / max(
            len(attacker.attack_patterns), 1
        )
        pattern_chaos = pattern_diversity * 2.0

        # Time-based fatigue
        time_active = (attacker.last_seen - attacker.first_seen).total_seconds()
        fatigue_factor = min(time_active / 3600, 1.0)  # Cap at 1 hour

        overload_score = decoy_confusion + pattern_chaos + fatigue_factor
        return min(overload_score, 10.0)

    def access_decoy(self, decoy_id: str, source_ip: str) -> Dict:
        """
        Record decoy access - attacker took the bait!

        This is GOLD - we now know:
        1. Attacker fell for the trap
        2. What type of attacks they're attempting
        3. We can serve them MORE convincing decoys
        """
        if decoy_id not in self.decoys:
            return {"error": "Unknown decoy"}

        decoy = self.decoys[decoy_id]
        decoy.access_count += 1
        decoy.triggered_by.add(source_ip)
        decoy.is_hot = True

        # Update attacker profile
        if source_ip in self.attackers:
            self.attackers[source_ip].accessed_decoys.add(decoy_id)

        self.logger.critical(
            f"DECOY TRIGGERED: {decoy_id} | "
            f"Type: {decoy.decoy_type.value} | "
            f"Attacker: {source_ip} | "
            f"Believability: {decoy.believability_score:.2f}"
        )

        return {
            "decoy_id": decoy_id,
            "decoy_type": decoy.decoy_type.value,
            "attacker_trapped": True,
            "serve_more_decoys": True,  # Feed them more bait!
        }

    def get_swarm_status(self) -> Dict:
        """Get current swarm defense status"""
        threat_distribution = {level: 0 for level in ThreatLevel}
        for attacker in self.attackers.values():
            threat_distribution[attacker.threat_level] += 1

        return {
            "total_attackers_tracked": len(self.attackers),
            "active_decoys": len(self.decoys),
            "threat_distribution": {k.value: v for k, v in threat_distribution.items()},
            "swarm_active": any(
                a.threat_level == ThreatLevel.SWARM for a in self.attackers.values()
            ),
            "max_cognitive_overload": max(
                (a.cognitive_overload_score for a in self.attackers.values()),
                default=0.0,
            ),
        }

    def get_decoy_recommendations(self, source_ip: str) -> List[str]:
        """
        Get list of decoys to show attacker

        COGNITIVE WARFARE:
        Show them SO MANY fake targets they can't find the real one
        """
        if source_ip not in self.attackers:
            # Unknown attacker - show minimal decoys
            return list(self.decoys.keys())[:5]

        attacker = self.attackers[source_ip]

        # Higher threat = more decoys shown
        decoy_counts = {
            ThreatLevel.SCOUT: 10,
            ThreatLevel.PROBE: 50,
            ThreatLevel.ATTACK: 200,
            ThreatLevel.SIEGE: 500,
            ThreatLevel.SWARM: len(self.decoys),  # SHOW THEM EVERYTHING
        }

        limit = decoy_counts[attacker.threat_level]

        # Prioritize decoys they haven't seen (keep them guessing)
        unseen_decoys = [
            d for d in self.decoys.keys() if d not in attacker.accessed_decoys
        ]

        # Mix unseen with high-believability decoys
        recommendations = unseen_decoys[: limit // 2]

        high_believability = sorted(
            self.decoys.values(),
            key=lambda d: d.believability_score,
            reverse=True,
        )[: limit // 2]

        recommendations.extend([d.decoy_id for d in high_believability])

        return recommendations[:limit]


# Example integration with existing firewall
def integrate_with_firewall(firewall_backend):
    """
    Integration example for existing firewall systems

    Instead of blocking on first violation, we TRAP and CONFUSE
    """
    swarm_defense = ThirstysHoneypotSwarmDefense()

    def enhanced_policy_check(source_ip, action, context):
        # Original firewall check
        original_result = firewall_backend.check_policy(source_ip, action, context)

        if not original_result["allowed"]:
            # Policy violation detected - trigger swarm
            swarm_response = swarm_defense.detect_policy_violation(
                source_ip=source_ip, violation_type=action, details=context
            )

            # Instead of blocking, redirect to decoys
            if swarm_response["swarm_active"]:
                decoy_list = swarm_defense.get_decoy_recommendations(source_ip)
                return {
                    "allowed": False,
                    "redirect_to_decoys": decoy_list,
                    "cognitive_overload_active": True,
                }

        return original_result

    return enhanced_policy_check
