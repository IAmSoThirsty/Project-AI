"""
Learning Engine - Attack Pattern Extraction & Defense Evolution

Learns from attacks to improve defenses:
- Attack pattern extraction from logged activity
- Playbook generation for known attack types
- Defense strategy evolution
- Model retraining pipeline
"""

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AttackPattern:
    """Extracted attack pattern"""

    pattern_id: str
    attack_type: str
    command_sequence: list[str]
    indicators: list[str]
    success_rate: float
    frequency: int
    first_seen: float
    last_seen: float
    threat_level: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DefensePlaybook:
    """Defense playbook for specific attack pattern"""

    playbook_id: str
    pattern_id: str
    detection_rules: list[str]
    response_strategy: str
    deception_template: dict[str, Any]
    success_rate: float
    times_used: int
    created_at: float
    updated_at: float


class AttackPatternExtractor:
    """
    Extracts patterns from attack logs

    Uses sequence analysis and statistical methods to identify
    recurring attack patterns.
    """

    def __init__(self, min_frequency: int = 3, min_confidence: float = 0.6):
        self.min_frequency = min_frequency
        self.min_confidence = min_confidence
        self.patterns: dict[str, AttackPattern] = {}

        logger.info("Attack Pattern Extractor initialized")
        logger.info("  Min frequency: %s", min_frequency)
        logger.info("  Min confidence: %s", min_confidence)

    def extract_from_attack(self, attack_data: dict[str, Any]) -> list[AttackPattern]:
        """Extract patterns from single attack"""
        commands = attack_data.get("commands", [])
        threat_type = attack_data.get("threat_type", "unknown")

        if len(commands) < 2:
            return []

        # Extract command sequences (sliding window)
        patterns = []
        for window_size in [2, 3, 4, 5]:
            if len(commands) < window_size:
                continue

            for i in range(len(commands) - window_size + 1):
                sequence = commands[i : i + window_size]

                # Create pattern signature
                pattern_sig = self._create_signature(sequence)

                # Check if pattern already exists
                if pattern_sig in self.patterns:
                    pattern = self.patterns[pattern_sig]
                    pattern.frequency += 1
                    pattern.last_seen = time.time()
                else:
                    # New pattern
                    pattern = AttackPattern(
                        pattern_id=pattern_sig,
                        attack_type=threat_type,
                        command_sequence=sequence,
                        indicators=self._extract_indicators(sequence),
                        success_rate=0.0,
                        frequency=1,
                        first_seen=time.time(),
                        last_seen=time.time(),
                        threat_level=attack_data.get("threat_level", "medium"),
                    )
                    self.patterns[pattern_sig] = pattern

                patterns.append(pattern)

        return patterns

    def _create_signature(self, commands: list[str]) -> str:
        """Create unique signature for command sequence"""
        # Normalize commands (remove arguments, keep structure)
        normalized = []
        for cmd in commands:
            parts = cmd.split()
            if parts:
                base_cmd = parts[0]
                # Keep important flags/patterns
                if "sudo" in cmd or "su" in cmd:
                    base_cmd += "_PRIV"
                if any(x in cmd for x in ["/etc/", "/root/", "/sys/"]):
                    base_cmd += "_SENS"
                if any(x in cmd for x in ["curl", "wget", "nc", "scp"]):
                    base_cmd += "_NET"

                normalized.append(base_cmd)

        return "::".join(normalized)

    def _extract_indicators(self, commands: list[str]) -> list[str]:
        """Extract threat indicators from command sequence"""
        indicators = []

        for cmd in commands:
            cmd_lower = cmd.lower()

            if "sudo" in cmd_lower or "su " in cmd_lower:
                indicators.append("privilege_escalation")

            if any(x in cmd_lower for x in ["/etc/shadow", "/etc/passwd"]):
                indicators.append("credential_access")

            if any(x in cmd_lower for x in ["curl", "wget", "nc", "scp"]):
                indicators.append("network_activity")

            if any(x in cmd_lower for x in ["tar", "zip", "gzip"]):
                indicators.append("data_compression")

            if any(x in cmd_lower for x in ["cron", "systemctl", "service"]):
                indicators.append("persistence_attempt")

        return list(set(indicators))

    def get_significant_patterns(self) -> list[AttackPattern]:
        """Get patterns that meet significance threshold"""
        return [p for p in self.patterns.values() if p.frequency >= self.min_frequency]

    def export_patterns(self) -> list[dict[str, Any]]:
        """Export patterns for storage"""
        return [
            {
                "pattern_id": p.pattern_id,
                "attack_type": p.attack_type,
                "command_sequence": p.command_sequence,
                "indicators": p.indicators,
                "frequency": p.frequency,
                "first_seen": p.first_seen,
                "last_seen": p.last_seen,
                "threat_level": p.threat_level,
            }
            for p in self.get_significant_patterns()
        ]


class PlaybookGenerator:
    """
    Generates defense playbooks from attack patterns

    Creates specific response strategies for known attack patterns.
    """

    def __init__(self):
        self.playbooks: dict[str, DefensePlaybook] = {}
        logger.info("Playbook Generator initialized")

    def generate_playbook(self, pattern: AttackPattern) -> DefensePlaybook:
        """Generate defense playbook for pattern"""
        playbook_id = f"playbook_{pattern.pattern_id}"

        # Generate detection rules
        detection_rules = self._generate_detection_rules(pattern)

        # Generate response strategy
        response_strategy = self._generate_response_strategy(pattern)

        # Generate deception template
        deception_template = self._generate_deception_template(pattern)

        playbook = DefensePlaybook(
            playbook_id=playbook_id,
            pattern_id=pattern.pattern_id,
            detection_rules=detection_rules,
            response_strategy=response_strategy,
            deception_template=deception_template,
            success_rate=0.0,
            times_used=0,
            created_at=time.time(),
            updated_at=time.time(),
        )

        self.playbooks[playbook_id] = playbook

        logger.info("Generated playbook: %s", playbook_id)
        logger.info("  Pattern: %s", pattern.attack_type)
        logger.info("  Rules: %s", len(detection_rules))

        return playbook

    def _generate_detection_rules(self, pattern: AttackPattern) -> list[str]:
        """Generate detection rules from pattern"""
        rules = []

        # Sequence-based rule
        sequence_rule = {
            "type": "sequence",
            "commands": pattern.command_sequence,
            "window": len(pattern.command_sequence),
            "threshold": 0.8,  # 80% match
        }
        rules.append(json.dumps(sequence_rule))

        # Indicator-based rules
        for indicator in pattern.indicators:
            indicator_rule = {
                "type": "indicator",
                "indicator": indicator,
                "weight": 0.3,
            }
            rules.append(json.dumps(indicator_rule))

        return rules

    def _generate_response_strategy(self, pattern: AttackPattern) -> str:
        """Generate response strategy"""
        # Based on threat level
        if pattern.threat_level == "critical":
            return "IMMEDIATE_ISOLATION"
        elif pattern.threat_level == "high":
            return "RAPID_DECEPTION"
        else:
            return "MONITORED_DECEPTION"

    def _generate_deception_template(self, pattern: AttackPattern) -> dict[str, Any]:
        """Generate deception environment template"""
        template = {
            "strategy": "adaptive",
            "fake_resources": [],
            "fake_responses": {},
            "confidence_triggers": [],
        }

        # Add fake resources based on indicators
        if "credential_access" in pattern.indicators:
            template["fake_resources"].append(
                {
                    "type": "file",
                    "path": "/etc/shadow",
                    "content": "fake_password_hashes",
                }
            )

        if "network_activity" in pattern.indicators:
            template["fake_resources"].append(
                {"type": "network", "service": "fake_external_server", "responds": True}
            )

        # Add confidence triggers
        if "data_compression" in pattern.indicators:
            template["confidence_triggers"].append(
                {"action": "archive_creation", "threshold": 0.9}
            )

        return template

    def export_playbooks(self) -> list[dict[str, Any]]:
        """Export playbooks for storage"""
        return [
            {
                "playbook_id": p.playbook_id,
                "pattern_id": p.pattern_id,
                "detection_rules": p.detection_rules,
                "response_strategy": p.response_strategy,
                "deception_template": p.deception_template,
                "success_rate": p.success_rate,
                "times_used": p.times_used,
            }
            for p in self.playbooks.values()
        ]


class DefenseEvolutionEngine:
    """
    Main learning engine that coordinates pattern extraction and playbook generation

    Continuously improves defenses based on observed attacks.
    """

    def __init__(self, storage_dir: str = "data/learning"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.pattern_extractor = AttackPatternExtractor()
        self.playbook_generator = PlaybookGenerator()

        self.attack_history: list[dict[str, Any]] = []
        self.evolution_cycles = 0

        # Load existing knowledge
        self._load_knowledge()

        logger.info("=" * 70)
        logger.info("DEFENSE EVOLUTION ENGINE - Initialized")
        logger.info("  Storage: %s", self.storage_dir)
        logger.info("  Known patterns: %s", len(self.pattern_extractor.patterns))
        logger.info("  Active playbooks: %s", len(self.playbook_generator.playbooks))
        logger.info("=" * 70)

    def learn_from_attack(self, attack_data: dict[str, Any]):
        """Learn from a completed attack"""
        logger.info("Learning from attack: %s", attack_data.get('attack_id', 'unknown'))

        # Add to history
        self.attack_history.append(attack_data)

        # Extract patterns
        patterns = self.pattern_extractor.extract_from_attack(attack_data)

        logger.info("  Extracted %s pattern(s)", len(patterns))

        # Generate playbooks for new significant patterns
        for pattern in patterns:
            if pattern.frequency >= self.pattern_extractor.min_frequency:
                playbook_id = f"playbook_{pattern.pattern_id}"

                if playbook_id not in self.playbook_generator.playbooks:
                    playbook = self.playbook_generator.generate_playbook(pattern)
                    logger.info("  Generated new playbook: %s", playbook_id)

    def evolve_defenses(self):
        """Trigger defense evolution cycle"""
        self.evolution_cycles += 1

        logger.info("")
        logger.info("=" * 70)
        logger.info("EVOLUTION CYCLE %s", self.evolution_cycles)
        logger.info("=" * 70)

        # Get significant patterns
        significant = self.pattern_extractor.get_significant_patterns()

        logger.info("Significant patterns: %s", len(significant))

        # Ensure playbooks exist for all significant patterns
        new_playbooks = 0
        for pattern in significant:
            playbook_id = f"playbook_{pattern.pattern_id}"
            if playbook_id not in self.playbook_generator.playbooks:
                self.playbook_generator.generate_playbook(pattern)
                new_playbooks += 1

        logger.info("New playbooks generated: %s", new_playbooks)
        logger.info("Total playbooks: %s", len(self.playbook_generator.playbooks))

        # Save knowledge
        self._save_knowledge()

        logger.info("Evolution cycle complete")
        logger.info("=" * 70)
        logger.info("")

    def get_playbook_for_attack(
        self, command_sequence: list[str]
    ) -> DefensePlaybook | None:
        """Get best playbook for command sequence"""
        # Try to match against known patterns
        for window_size in [5, 4, 3, 2]:
            if len(command_sequence) < window_size:
                continue

            recent = command_sequence[-window_size:]
            sig = self.pattern_extractor._create_signature(recent)

            playbook_id = f"playbook_{sig}"
            if playbook_id in self.playbook_generator.playbooks:
                playbook = self.playbook_generator.playbooks[playbook_id]
                playbook.times_used += 1
                return playbook

        return None

    def _save_knowledge(self):
        """Save patterns and playbooks"""
        # Save patterns
        patterns_file = self.storage_dir / "patterns.json"
        with open(patterns_file, "w") as f:
            json.dump(self.pattern_extractor.export_patterns(), f, indent=2)

        # Save playbooks
        playbooks_file = self.storage_dir / "playbooks.json"
        with open(playbooks_file, "w") as f:
            json.dump(self.playbook_generator.export_playbooks(), f, indent=2)

        logger.info("Knowledge saved: %s, %s", patterns_file, playbooks_file)

    def _load_knowledge(self):
        """Load existing patterns and playbooks"""
        patterns_file = self.storage_dir / "patterns.json"
        playbooks_file = self.storage_dir / "playbooks.json"

        # Load patterns
        if patterns_file.exists():
            with open(patterns_file) as f:
                patterns_data = json.load(f)

            for p_data in patterns_data:
                pattern = AttackPattern(**p_data)
                self.pattern_extractor.patterns[pattern.pattern_id] = pattern

            logger.info("Loaded %s patterns", len(patterns_data))

        # Load playbooks
        if playbooks_file.exists():
            with open(playbooks_file) as f:
                playbooks_data = json.load(f)

            for pb_data in playbooks_data:
                playbook = DefensePlaybook(**pb_data)
                self.playbook_generator.playbooks[playbook.playbook_id] = playbook

            logger.info("Loaded %s playbooks", len(playbooks_data))

    def get_statistics(self) -> dict[str, Any]:
        """Get learning engine statistics"""
        return {
            "evolution_cycles": self.evolution_cycles,
            "attacks_analyzed": len(self.attack_history),
            "patterns_learned": len(self.pattern_extractor.patterns),
            "significant_patterns": len(
                self.pattern_extractor.get_significant_patterns()
            ),
            "active_playbooks": len(self.playbook_generator.playbooks),
            "total_playbook_uses": sum(
                p.times_used for p in self.playbook_generator.playbooks.values()
            ),
        }


# Public API
__all__ = [
    "DefenseEvolutionEngine",
    "AttackPatternExtractor",
    "PlaybookGenerator",
    "AttackPattern",
    "DefensePlaybook",
]
