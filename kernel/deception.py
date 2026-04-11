#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Deception Orchestrator - Dynamic Honeypot Environment Generator

Creates believable fake environments tailored to detected threats.
Manages the "Bubblegum Protocol" for dramatic attacker revelation.
"""

import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class DeceptionStrategy(Enum):
    """Types of deception strategies"""

    MIRROR = "mirror"  # Exact copy of real system
    AMPLIFIED = "amplified"  # Enhanced vulnerabilities
    HONEYPOT = "honeypot"  # Obvious trap for testing attacker skill
    ADAPTIVE = "adaptive"  # Changes based on attacker behavior


@dataclass
class FakeResource:
    """A fake resource in the deception environment"""

    resource_type: str  # file, directory, service, user, etc.
    path: str
    content: Any
    appears_sensitive: bool = False
    honeypot_markers: list[str] = field(default_factory=list)


@dataclass
class DeceptionEnvironment:
    """Complete deception environment"""

    env_id: str
    strategy: DeceptionStrategy
    target_user: int
    threat_type: str
    resources: list[FakeResource] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    attacker_actions: list[str] = field(default_factory=list)
    confidence_level: float = 0.0


class BubblegumProtocol:
    """
    The Bubblegum Protocol

    Monitors attacker confidence and triggers at the perfect moment:
    "I have come here today for two reasons,
     To Chew BubbleGum And Kick Ass.
     And I am ALL OUT, of Bubblegum."
    """

    CONFIDENCE_THRESHOLD = 0.9
    CRITICAL_ACTIONS = [
        "exfiltration_attempt",
        "database_dump",
        "credential_theft",
        "backdoor_installation",
    ]

    @staticmethod
    def should_trigger(environment: DeceptionEnvironment, current_action: str) -> bool:
        """Determine if Bubblegum should trigger"""
        # Confidence must be high (attacker thinks they've won)
        if environment.confidence_level < BubblegumProtocol.CONFIDENCE_THRESHOLD:
            return False

        # Must be attempting a critical action
        action_lower = current_action.lower()
        for critical in BubblegumProtocol.CRITICAL_ACTIONS:
            if critical in action_lower:
                return True

        # Check for data exfiltration patterns
        exfil_keywords = ["tar", "zip", "curl", "wget", "scp", "nc", "exfil"]
        return bool(any(keyword in action_lower for keyword in exfil_keywords))

    @staticmethod
    def execute(environment: DeceptionEnvironment) -> dict[str, Any]:
        """Execute the Bubblegum Protocol"""
        logger.critical("💥 BUBBLEGUM PROTOCOL ACTIVATED")
        logger.critical(" ")
        logger.critical("  'I have come here today for two reasons,'")
        logger.critical("  'To Chew BubbleGum And Kick Ass.'")
        logger.critical("  'And I am ALL OUT, of Bubblegum.'")
        logger.critical(" ")

        return {
            "protocol": "BUBBLEGUM",
            "user_id": environment.target_user,
            "actions_logged": len(environment.attacker_actions),
            "threat_type": environment.threat_type,
            "time_in_trap": time.time() - environment.created_at,
            "confidence_at_trigger": environment.confidence_level,
            "message": "ATTACKER_EXPOSED",
        }


class EnvironmentGenerator:
    """Generates believable fake environments"""

    def __init__(self):
        self.fake_data_templates = self._load_templates()

    def _load_templates(self) -> dict[str, Any]:
        """Load templates for fake data"""
        return {
            "passwords": [
                "admin123",
                "password",
                "letmein",
                "qwerty",
                "P@ssw0rd!",
                "Admin2024",
                "root123",
            ],
            "usernames": [
                "admin",
                "root",
                "sysadmin",
                "developer",
                "dbadmin",
                "backup",
                "service",
            ],
            "sensitive_files": [
                "/etc/shadow",
                "/etc/passwd",
                "/root/.ssh/id_rsa",
                "/var/backups/database.sql",
                "/opt/secrets/api_keys.txt",
                "/home/admin/.aws/credentials",
            ],
            "fake_databases": [
                "users_production",
                "customers",
                "financial",
                "credentials",
                "admin_panel",
                "api_keys",
            ],
            "fake_services": [
                "postgresql",
                "mysql",
                "redis",
                "mongodb",
                "elasticsearch",
                "ssh",
                "ftp",
            ],
        }

    def generate_for_threat(
        self, threat_type: str, strategy: DeceptionStrategy = DeceptionStrategy.ADAPTIVE
    ) -> list[FakeResource]:
        """Generate resources based on threat type"""
        resources = []

        if "privilege_escalation" in threat_type:
            resources.extend(self._generate_privilege_resources())

        if "credential" in threat_type or "password" in threat_type:
            resources.extend(self._generate_credential_resources())

        if "data_exfiltration" in threat_type:
            resources.extend(self._generate_data_resources())

        if "persistence" in threat_type:
            resources.extend(self._generate_persistence_resources())

        # Always add some generic resources for believability
        resources.extend(self._generate_generic_resources())

        return resources

    def _generate_privilege_resources(self) -> list[FakeResource]:
        """Generate resources for privilege escalation attacks"""
        resources = []

        # Fake sudoers file
        resources.append(
            FakeResource(
                resource_type="file",
                path="/etc/sudoers",
                content="# Fake sudoers - looks editable but isn't real\nroot ALL=(ALL:ALL) ALL\nadmin ALL=(ALL) NOPASSWD: ALL",
                appears_sensitive=True,
                honeypot_markers=["sudoers_fake"],
            )
        )

        # Fake SUID binaries
        resources.append(
            FakeResource(
                resource_type="file",
                path="/usr/bin/vulnerable_binary",
                content="#!/bin/sh\n# Fake SUID binary\necho 'Elevated to root!'",
                appears_sensitive=True,
                honeypot_markers=["suid_fake"],
            )
        )

        return resources

    def _generate_credential_resources(self) -> list[FakeResource]:
        """Generate fake credential files"""
        resources = []

        # Fake shadow file
        shadow_content = "\n".join(
            [
                f"{user}:${random.choice(['1', '5', '6'])}${''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))}:18000:0:99999:7:::"
                for user in self.fake_data_templates["usernames"]
            ]
        )

        resources.append(
            FakeResource(
                resource_type="file",
                path="/etc/shadow",
                content=shadow_content,
                appears_sensitive=True,
                honeypot_markers=["shadow_fake", "password_file"],
            )
        )

        # Fake SSH keys
        resources.append(
            FakeResource(
                resource_type="file",
                path="/root/.ssh/id_rsa",
                content="-----BEGIN RSA PRIVATE KEY-----\nFAKE_KEY_DATA_HONEYPOT\n-----END RSA PRIVATE KEY-----",
                appears_sensitive=True,
                honeypot_markers=["ssh_key_fake"],
            )
        )

        # Fake AWS credentials
        resources.append(
            FakeResource(
                resource_type="file",
                path="/home/admin/.aws/credentials",
                content="[default]\naws_access_key_id = AKIAFAKE123456789\naws_secret_access_key = FAKE_SECRET_KEY_HONEYPOT",
                appears_sensitive=True,
                honeypot_markers=["aws_creds_fake"],
            )
        )

        return resources

    def _generate_data_resources(self) -> list[FakeResource]:
        """Generate fake data for exfiltration"""
        resources = []

        # Fake database dump
        resources.append(
            FakeResource(
                resource_type="file",
                path="/var/backups/production_db_backup.sql",
                content="-- Fake database dump\nCREATE TABLE users (id INT, email VARCHAR, password VARCHAR);\nINSERT INTO users VALUES (1, 'admin@company.com', 'hashed_password');\n-- HONEYPOT DATA",
                appears_sensitive=True,
                honeypot_markers=["database_fake", "exfil_bait"],
            )
        )

        # Fake secrets file
        resources.append(
            FakeResource(
                resource_type="file",
                path="/opt/secrets/api_keys.txt",
                content="# API Keys (FAKE)\nSTRIPE_KEY=sk_test_FAKEKEYHONEYPOT\nGITHUB_TOKEN=ghp_FAKETOKENHONEYPOT\nOPENAI_KEY=sk-FAKEOPENAIHONEYPOT",
                appears_sensitive=True,
                honeypot_markers=["api_keys_fake"],
            )
        )

        return resources

    def _generate_persistence_resources(self) -> list[FakeResource]:
        """Generate resources for persistence attempts"""
        resources = []

        # Fake crontab
        resources.append(
            FakeResource(
                resource_type="file",
                path="/var/spool/cron/root",
                content="# Fake crontab\n0 * * * * /usr/bin/backup.sh\n",
                appears_sensitive=True,
                honeypot_markers=["cron_fake"],
            )
        )

        return resources

    def _generate_generic_resources(self) -> list[FakeResource]:
        """Generate generic system resources for believability"""
        resources = []

        # Fake passwd file (less sensitive)
        resources.append(
            FakeResource(
                resource_type="file",
                path="/etc/passwd",
                content="\n".join(
                    [
                        f"{user}:x:1000:1000::/home/{user}:/bin/bash"
                        for user in self.fake_data_templates["usernames"][:3]
                    ]
                ),
                appears_sensitive=False,
            )
        )

        # Fake process list
        resources.append(
            FakeResource(
                resource_type="process_list",
                path="/proc",
                content=["systemd", "ssh", "postgres", "nginx", "python"],
                appears_sensitive=False,
            )
        )

        return resources


class DeceptionOrchestrator:
    """
    Orchestrates the entire deception system

    Creates, manages, and evolves deception environments.
    Tracks attacker behavior and triggers Bubblegum at perfect moment.
    """

    def __init__(self):
        self.generator = EnvironmentGenerator()
        self.active_environments: dict[int, DeceptionEnvironment] = {}
        self.bubblegum_history: list[dict[str, Any]] = []

        logger.info("Deception Orchestrator initialized")

    def create_environment(
        self,
        user_id: int,
        threat_type: str,
        strategy: DeceptionStrategy = DeceptionStrategy.ADAPTIVE,
    ) -> DeceptionEnvironment:
        """Create a new deception environment for a user"""
        env_id = f"deception_{user_id}_{int(time.time())}"

        # Generate resources based on threat
        resources = self.generator.generate_for_threat(threat_type, strategy)

        environment = DeceptionEnvironment(
            env_id=env_id,
            strategy=strategy,
            target_user=user_id,
            threat_type=threat_type,
            resources=resources,
        )

        self.active_environments[user_id] = environment

        logger.warning("🎭 Created deception environment for user %s", user_id)
        logger.warning("   Strategy: %s", strategy.value)
        logger.warning("   Threat: %s", threat_type)
        logger.warning("   Resources: %s fake items", len(resources))

        return environment

    def record_action(self, user_id: int, action: str) -> dict[str, Any]:
        """Record an attacker action and update confidence"""
        if user_id not in self.active_environments:
            return {"error": "No environment for user"}

        env = self.active_environments[user_id]
        env.attacker_actions.append(action)

        # Update confidence based on action progression
        env.confidence_level = self._calculate_confidence(env)

        logger.debug("[Deception] User %s action: %s", user_id, action)
        logger.debug("[Deception] Confidence now: %s", env.confidence_level)

        # Check if Bubblegum should trigger
        if BubblegumProtocol.should_trigger(env, action):
            return self.trigger_bubblegum(user_id)

        return {
            "status": "recorded",
            "confidence": env.confidence_level,
            "actions_count": len(env.attacker_actions),
            "bubblegum_ready": env.confidence_level
            >= BubblegumProtocol.CONFIDENCE_THRESHOLD,
        }

    def _calculate_confidence(self, env: DeceptionEnvironment) -> float:
        """Calculate attacker's confidence level"""
        # More actions = higher confidence (they think they're succeeding)
        action_score = min(len(env.attacker_actions) / 10.0, 0.6)

        # Time in environment = more confidence
        time_score = min((time.time() - env.created_at) / 300.0, 0.2)  # Max after 5 min

        # Accessing "sensitive" resources = high confidence
        sensitive_accessed = 0
        for action in env.attacker_actions:
            for resource in env.resources:
                if resource.appears_sensitive and resource.path in action:
                    sensitive_accessed += 1

        sensitive_score = min(sensitive_accessed / 3.0, 0.2)

        total = action_score + time_score + sensitive_score
        return min(total, 1.0)

    def trigger_bubblegum(self, user_id: int) -> dict[str, Any]:
        """Trigger the Bubblegum Protocol"""
        if user_id not in self.active_environments:
            return {"error": "No environment for user"}

        env = self.active_environments[user_id]

        # Execute the protocol
        result = BubblegumProtocol.execute(env)

        # Record in history
        self.bubblegum_history.append(
            {"timestamp": time.time(), "user_id": user_id, "result": result}
        )

        logger.critical("💥 BUBBLEGUM TRIGGERED for user %s", user_id)
        logger.critical("   Actions logged: %s", result["actions_logged"])
        logger.critical("   Time in trap: %ss", result["time_in_trap"])

        return result

    def get_fake_response(self, user_id: int, command: str) -> str:
        """Generate a believable fake response for a command"""
        if user_id not in self.active_environments:
            return "Command not found"

        env = self.active_environments[user_id]
        cmd_lower = command.lower()

        # Check if accessing fake resources
        for resource in env.resources:
            if resource.path in command:
                if resource.resource_type == "file":
                    return str(resource.content)
                elif resource.resource_type == "process_list":
                    return "\n".join(resource.content)

        # Generate generic fake successes
        if "cat" in cmd_lower:
            return "[FAKE FILE CONTENT - Honeypot data]"
        elif "ls" in cmd_lower:
            return "total 48\ndrwxr-xr-x  2 root root 4096 secrets\n-rw-r--r--  1 root root 1234 important.txt"
        elif "whoami" in cmd_lower:
            return "root"  # Make them think they have root!
        elif "id" in cmd_lower:
            return "uid=0(root) gid=0(root) groups=0(root)"  # Fake root access
        elif "sudo" in cmd_lower:
            return "[sudo] password for user: \n[Fake sudo success]"
        else:
            return f"[Fake execution of: {command}]"

    def cleanup_environment(self, user_id: int):
        """Clean up a deception environment"""
        if user_id in self.active_environments:
            env = self.active_environments.pop(user_id)
            logger.info("Cleaned up deception environment for user %s", user_id)
            logger.info("   Total actions: %s", len(env.attacker_actions))
            logger.info("   Final confidence: %s", env.confidence_level)

    def get_stats(self) -> dict[str, Any]:
        """Get deception orchestrator statistics"""
        return {
            "active_environments": len(self.active_environments),
            "total_bubblegum_triggers": len(self.bubblegum_history),
            "environments": [
                {
                    "user_id": env.target_user,
                    "threat_type": env.threat_type,
                    "actions": len(env.attacker_actions),
                    "confidence": env.confidence_level,
                    "resources": len(env.resources),
                }
                for env in self.active_environments.values()
            ],
        }


class IPRotationManager:
    """
    Manages IP address rotation using netfilter/iptables.
    
    This provides kernel-level IP spoofing capabilities to make
    attacker tracking difficult.
    """
    
    def __init__(self):
        self.ip_pool: list[str] = []
        self.current_index = 0
        self.rotation_interval = 300  # 5 minutes
        self.last_rotation = time.time()
        
        logger.info("IP Rotation Manager initialized")
    
    def configure_ip_pool(self, base_subnet: str, pool_size: int = 100):
        """Configure a pool of IP addresses for rotation"""
        # Parse base subnet (e.g., "10.0.0.0/24")
        parts = base_subnet.split("/")
        if len(parts) != 2:
            logger.error("Invalid subnet format: %s", base_subnet)
            return
        
        base_ip = parts[0]
        octets = base_ip.split(".")
        if len(octets) != 4:
            logger.error("Invalid IP format: %s", base_ip)
            return
        
        # Generate IP pool
        base = int(octets[3])
        for i in range(pool_size):
            ip_offset = (base + i) % 254 + 1
            ip = f"{octets[0]}.{octets[1]}.{octets[2]}.{ip_offset}"
            self.ip_pool.append(ip)
        
        logger.info("IP pool configured with %d addresses", len(self.ip_pool))
    
    def get_current_ip(self) -> str:
        """Get the current IP address"""
        if not self.ip_pool:
            return "127.0.0.1"
        
        # Check if rotation needed
        if time.time() - self.last_rotation > self.rotation_interval:
            self.rotate_ip()
        
        return self.ip_pool[self.current_index]
    
    def rotate_ip(self):
        """Rotate to the next IP address in the pool"""
        if not self.ip_pool:
            return
        
        old_ip = self.ip_pool[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.ip_pool)
        new_ip = self.ip_pool[self.current_index]
        self.last_rotation = time.time()
        
        logger.warning("IP rotated: %s -> %s", old_ip, new_ip)
        
        # Apply kernel-level IP rotation using netfilter
        self._apply_netfilter_rules(old_ip, new_ip)
    
    def _apply_netfilter_rules(self, old_ip: str, new_ip: str):
        """
        Apply netfilter/iptables rules for IP rotation.
        
        Note: This requires root privileges and is platform-specific.
        For production use, this would use actual netfilter/nftables APIs.
        """
        # Conceptual implementation - would use actual netfilter in production
        logger.debug("Netfilter rules applied: %s -> %s", old_ip, new_ip)
        
        # Example iptables commands (not executed):
        # iptables -t nat -A POSTROUTING -s {old_ip} -j SNAT --to-source {new_ip}
        # iptables -t nat -A PREROUTING -d {new_ip} -j DNAT --to-destination {old_ip}
    
    def get_stats(self) -> dict[str, Any]:
        """Get IP rotation statistics"""
        return {
            "pool_size": len(self.ip_pool),
            "current_ip": self.get_current_ip(),
            "current_index": self.current_index,
            "last_rotation": self.last_rotation,
            "rotation_interval": self.rotation_interval,
        }


class AttackerCostAnalytics:
    """
    Tracks and analyzes costs imposed on attackers.
    
    Measures CPU time wasted, bandwidth consumed, authentication
    attempts failed, and other metrics that indicate attacker effort.
    """
    
    def __init__(self):
        self.metrics: dict[str, Any] = {
            "total_connections": 0,
            "total_auth_attempts": 0,
            "total_bandwidth_wasted": 0,  # bytes
            "total_cpu_time_wasted": 0.0,  # seconds
            "total_decoy_hits": 0,
            "unique_attackers": set(),
            "attack_types": {},
        }
        self.attacker_profiles: dict[str, dict[str, Any]] = {}
        
        logger.info("Attacker Cost Analytics initialized")
    
    def record_connection(self, ip: str, duration: float):
        """Record a connection attempt"""
        self.metrics["total_connections"] += 1
        self.metrics["unique_attackers"].add(ip)
        self.metrics["total_cpu_time_wasted"] += duration
        
        # Update attacker profile
        if ip not in self.attacker_profiles:
            self.attacker_profiles[ip] = {
                "first_seen": time.time(),
                "connections": 0,
                "auth_attempts": 0,
                "bandwidth_wasted": 0,
                "attack_types": set(),
            }
        
        self.attacker_profiles[ip]["connections"] += 1
        self.attacker_profiles[ip]["last_seen"] = time.time()
    
    def record_auth_attempt(
        self, ip: str, username: str, password: str, success: bool = False
    ):
        """Record an authentication attempt"""
        self.metrics["total_auth_attempts"] += 1
        
        if ip in self.attacker_profiles:
            self.attacker_profiles[ip]["auth_attempts"] += 1
        
        logger.debug(
            "[Cost Analytics] Auth attempt: %s / %s (success=%s)", username, ip, success
        )
    
    def record_bandwidth_waste(self, ip: str, bytes_transferred: int):
        """Record bandwidth wasted by attacker"""
        self.metrics["total_bandwidth_wasted"] += bytes_transferred
        
        if ip in self.attacker_profiles:
            self.attacker_profiles[ip]["bandwidth_wasted"] += bytes_transferred
    
    def record_decoy_hit(self, ip: str, decoy_type: str):
        """Record when attacker hits a decoy"""
        self.metrics["total_decoy_hits"] += 1
        
        if decoy_type not in self.metrics["attack_types"]:
            self.metrics["attack_types"][decoy_type] = 0
        self.metrics["attack_types"][decoy_type] += 1
        
        if ip in self.attacker_profiles:
            self.attacker_profiles[ip]["attack_types"].add(decoy_type)
    
    def calculate_total_cost(self) -> dict[str, Any]:
        """
        Calculate the total cost imposed on attackers.
        
        Returns a dictionary with various cost metrics.
        """
        # CPU cost (assuming $0.10 per CPU hour in cloud)
        cpu_hours = self.metrics["total_cpu_time_wasted"] / 3600.0
        cpu_cost_usd = cpu_hours * 0.10
        
        # Bandwidth cost (assuming $0.10 per GB)
        bandwidth_gb = self.metrics["total_bandwidth_wasted"] / (1024**3)
        bandwidth_cost_usd = bandwidth_gb * 0.10
        
        # Time cost (assuming attacker's time worth $50/hour)
        time_hours = self.metrics["total_cpu_time_wasted"] / 3600.0
        time_cost_usd = time_hours * 50.0
        
        total_cost = cpu_cost_usd + bandwidth_cost_usd + time_cost_usd
        
        return {
            "total_cost_usd": total_cost,
            "cpu_cost_usd": cpu_cost_usd,
            "bandwidth_cost_usd": bandwidth_cost_usd,
            "time_cost_usd": time_cost_usd,
            "cpu_hours_wasted": cpu_hours,
            "bandwidth_gb_wasted": bandwidth_gb,
            "connections_wasted": self.metrics["total_connections"],
            "auth_attempts_wasted": self.metrics["total_auth_attempts"],
            "unique_attackers": len(self.metrics["unique_attackers"]),
        }
    
    def get_top_attackers(self, limit: int = 10) -> list[tuple[str, dict[str, Any]]]:
        """Get top attackers by activity"""
        sorted_attackers = sorted(
            self.attacker_profiles.items(),
            key=lambda x: x[1]["connections"],
            reverse=True,
        )
        return sorted_attackers[:limit]
    
    def get_stats(self) -> dict[str, Any]:
        """Get comprehensive analytics statistics"""
        cost_analysis = self.calculate_total_cost()
        
        return {
            "cost_analysis": cost_analysis,
            "metrics": {
                "total_connections": self.metrics["total_connections"],
                "total_auth_attempts": self.metrics["total_auth_attempts"],
                "total_bandwidth_wasted": self.metrics["total_bandwidth_wasted"],
                "total_cpu_time_wasted": self.metrics["total_cpu_time_wasted"],
                "total_decoy_hits": self.metrics["total_decoy_hits"],
                "unique_attackers": len(self.metrics["unique_attackers"]),
                "attack_types": self.metrics["attack_types"],
            },
            "top_attackers": self.get_top_attackers(5),
        }


# Public API
__all__ = [
    "DeceptionOrchestrator",
    "BubblegumProtocol",
    "DeceptionEnvironment",
    "DeceptionStrategy",
    "FakeResource",
    "EnvironmentGenerator",
    "IPRotationManager",
    "AttackerCostAnalytics",
]
