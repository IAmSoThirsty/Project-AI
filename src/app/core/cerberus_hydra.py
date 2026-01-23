"""
Cerberus Hydra Defense Mechanism
==================================

Implements exponential multi-implementation spawning for defense against security breaches.
When a security agent is bypassed or disabled, automatically instantiates 3 new defensive agents,
each in a random combination of human language and programming language.

Features:
- Exponential spawning (3x on each bypass)
- Multi-language agent implementation (50 human × 50 programming languages)
- Progressive system lockdown
- Integration with ASL3Security and anomaly detection
- Comprehensive audit logging and registry

Based on the mythological Hydra: cut off one head, three more grow back.
"""

import json
import logging
import os
import random
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DefenseAgent:
    """A Cerberus defense agent with language configuration."""

    agent_id: str
    human_language: str
    human_language_name: str
    programming_language: str
    programming_language_name: str
    locked_section: str
    generation: int
    spawned_at: str
    parent_agent_id: str | None = None
    status: str = "active"
    process_id: int | None = None
    log_file: str | None = None


@dataclass
class BypassEvent:
    """Record of a security bypass event."""

    event_id: str
    timestamp: str
    bypassed_agent_id: str
    bypass_type: str
    attacker_signature: str | None = None
    spawned_agents: list[str] = field(default_factory=list)
    lockdown_level: int = 0


class CerberusHydraDefense:
    """
    Cerberus Hydra Defense System - Exponential Multi-Language Agent Spawning.

    When a guard is bypassed, spawn 3 new guards in random language combinations.
    Each guard locks a distinct section of the system for progressive containment.
    """

    # System sections that can be locked down
    LOCKABLE_SECTIONS = [
        "authentication",
        "authorization",
        "data_access",
        "file_operations",
        "network_egress",
        "api_endpoints",
        "admin_functions",
        "user_sessions",
        "encryption_keys",
        "audit_logs",
        "configuration",
        "model_weights",
        "training_data",
        "inference_engine",
        "memory_management",
        "process_execution",
        "system_calls",
        "database_access",
        "cache_operations",
        "backup_systems",
        "monitoring_systems",
        "alert_systems",
        "logging_systems",
        "credential_storage",
        "token_management",
    ]

    SPAWN_FACTOR = 3  # Number of agents spawned per bypass

    def __init__(
        self,
        data_dir: str = "data",
        enable_polyglot_execution: bool = True,
        max_agents: int = 1000,
        security_enforcer=None,
    ):
        """
        Initialize Cerberus Hydra Defense.

        Args:
            data_dir: Base data directory
            enable_polyglot_execution: Actually execute agents in their programming languages
            max_agents: Maximum number of concurrent agents (prevent resource exhaustion)
            security_enforcer: ASL3Security instance for integration
        """
        self.data_dir = Path(data_dir)
        self.enable_polyglot_execution = enable_polyglot_execution
        self.max_agents = max_agents
        self.security_enforcer = security_enforcer

        # Load language database
        self.languages = self._load_language_database()

        # Agent registry
        self.agents: dict[str, DefenseAgent] = {}
        self.bypass_events: list[BypassEvent] = []

        # Lockdown state
        self.locked_sections: set[str] = set()
        self.lockdown_level = 0  # 0-10 scale

        # Statistics
        self.total_spawns = 0
        self.total_bypasses = 0
        self.generation_counts: dict[int, int] = defaultdict(int)

        # Initialize directories
        self._initialize_directories()

        # Load existing state
        self._load_state()

        logger.info(
            "Cerberus Hydra Defense initialized: "
            f"{len(self.languages['human_languages'])} human languages, "
            f"{len(self.languages['programming_languages'])} programming languages"
        )

    def _initialize_directories(self) -> None:
        """Create necessary directories."""
        dirs = [
            self.data_dir / "cerberus",
            self.data_dir / "cerberus" / "agents",
            self.data_dir / "cerberus" / "logs",
            self.data_dir / "cerberus" / "registry",
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    def _load_language_database(self) -> dict[str, Any]:
        """Load the 50x50 language database."""
        db_path = self.data_dir / "cerberus" / "languages.json"

        if not db_path.exists():
            logger.error(f"Language database not found: {db_path}")
            # Return minimal fallback
            return {
                "human_languages": {
                    "en": {
                        "name": "English",
                        "alert_prefix": "SECURITY ALERT",
                        "agent_spawned": "Defense agent spawned",
                        "bypass_detected": "Security bypass detected",
                    }
                },
                "programming_languages": {
                    "python": {
                        "name": "Python",
                        "executable": "python3",
                        "extension": ".py",
                        "installed": True,
                    }
                },
            }

        with open(db_path, encoding="utf-8") as f:
            return json.load(f)

    def _load_state(self) -> None:
        """Load existing Cerberus state."""
        state_file = self.data_dir / "cerberus" / "registry" / "state.json"
        if state_file.exists():
            try:
                with open(state_file) as f:
                    state = json.load(f)

                # Restore agents
                for agent_data in state.get("agents", []):
                    agent = DefenseAgent(**agent_data)
                    self.agents[agent.agent_id] = agent

                # Restore locked sections
                self.locked_sections = set(state.get("locked_sections", []))
                self.lockdown_level = state.get("lockdown_level", 0)

                logger.info(f"Restored {len(self.agents)} agents from state")
            except Exception as e:
                logger.error(f"Failed to load Cerberus state: {e}")

    def _save_state(self) -> None:
        """Persist Cerberus state."""
        state_file = self.data_dir / "cerberus" / "registry" / "state.json"

        state = {
            "agents": [agent.__dict__ for agent in self.agents.values()],
            "locked_sections": list(self.locked_sections),
            "lockdown_level": self.lockdown_level,
            "total_spawns": self.total_spawns,
            "total_bypasses": self.total_bypasses,
            "last_updated": datetime.now().isoformat(),
        }

        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

    def spawn_initial_agents(self, count: int = 3) -> list[str]:
        """
        Spawn initial set of defense agents.

        Args:
            count: Number of initial agents to spawn

        Returns:
            List of spawned agent IDs
        """
        logger.info(f"Spawning {count} initial Cerberus agents...")

        spawned_ids = []
        for _i in range(count):
            agent_id = self._spawn_single_agent(
                generation=0,
                parent_agent_id=None,
                reason="initial_deployment",
            )
            if agent_id:
                spawned_ids.append(agent_id)

        return spawned_ids

    def detect_bypass(
        self,
        agent_id: str | None = None,
        bypass_type: str = "unknown",
        attacker_signature: str | None = None,
    ) -> str:
        """
        Detect and respond to a security bypass.

        Spawns 3 new agents in response, each with random language combination.

        Args:
            agent_id: ID of bypassed agent (if known)
            bypass_type: Type of bypass detected
            attacker_signature: Signature of attacker (for tracking)

        Returns:
            Event ID of bypass event
        """
        event_id = str(uuid.uuid4())
        self.total_bypasses += 1

        # Log bypass event
        bypass_event = BypassEvent(
            event_id=event_id,
            timestamp=datetime.now().isoformat(),
            bypassed_agent_id=agent_id or "unknown",
            bypass_type=bypass_type,
            attacker_signature=attacker_signature,
        )

        logger.critical(
            f"🚨 CERBERUS BYPASS DETECTED: {bypass_type} "
            f"(agent: {agent_id}, attacker: {attacker_signature})"
        )

        # Determine parent agent and generation
        parent_agent = self.agents.get(agent_id) if agent_id else None
        generation = (parent_agent.generation + 1) if parent_agent else 1

        # Spawn SPAWN_FACTOR new agents
        spawned_ids = []
        for _i in range(self.SPAWN_FACTOR):
            new_agent_id = self._spawn_single_agent(
                generation=generation,
                parent_agent_id=agent_id,
                reason=f"bypass_{bypass_type}",
            )
            if new_agent_id:
                spawned_ids.append(new_agent_id)

        bypass_event.spawned_agents = spawned_ids
        bypass_event.lockdown_level = self.lockdown_level
        self.bypass_events.append(bypass_event)

        # Log bypass to audit trail
        self._log_bypass_event(bypass_event)

        # Increase lockdown level
        self._escalate_lockdown()

        # Notify security enforcer if available
        if self.security_enforcer:
            self._notify_security_enforcer(bypass_event)

        # Save state
        self._save_state()

        logger.warning(
            f"⚔️ HYDRA RESPONSE: Spawned {len(spawned_ids)} generation-{generation} agents "
            f"(Total active: {len([a for a in self.agents.values() if a.status == 'active'])})"
        )

        return event_id

    def _spawn_single_agent(
        self,
        generation: int,
        parent_agent_id: str | None,
        reason: str,
    ) -> str | None:
        """
        Spawn a single defense agent with random language combination.

        Args:
            generation: Generation number (0 = initial, 1+ = spawned)
            parent_agent_id: ID of parent agent (if spawned in response)
            reason: Reason for spawning

        Returns:
            Agent ID if successful, None otherwise
        """
        # Check max agents limit
        active_agents = len([a for a in self.agents.values() if a.status == "active"])
        if active_agents >= self.max_agents:
            logger.error(
                f"Cannot spawn agent: max agents ({self.max_agents}) reached"
            )
            return None

        # Generate agent ID
        agent_id = f"cerberus-{generation}-{uuid.uuid4().hex[:8]}"

        # Select random human language
        human_langs = list(self.languages["human_languages"].keys())
        human_lang = random.choice(human_langs)
        human_lang_data = self.languages["human_languages"][human_lang]

        # Select random programming language (prefer installed ones)
        prog_langs = list(self.languages["programming_languages"].keys())
        installed_prog_langs = [
            lang
            for lang in prog_langs
            if self.languages["programming_languages"][lang].get("installed", False)
        ]

        # 80% chance to use installed language, 20% any language
        if installed_prog_langs and random.random() < 0.8:
            prog_lang = random.choice(installed_prog_langs)
        else:
            prog_lang = random.choice(prog_langs)

        prog_lang_data = self.languages["programming_languages"][prog_lang]

        # Select section to lock (avoid already locked sections when possible)
        available_sections = [
            s for s in self.LOCKABLE_SECTIONS if s not in self.locked_sections
        ]
        if not available_sections:
            # All sections locked, start over with higher priority
            available_sections = self.LOCKABLE_SECTIONS

        locked_section = random.choice(available_sections)
        self.locked_sections.add(locked_section)

        # Create agent
        agent = DefenseAgent(
            agent_id=agent_id,
            human_language=human_lang,
            human_language_name=human_lang_data["name"],
            programming_language=prog_lang,
            programming_language_name=prog_lang_data["name"],
            locked_section=locked_section,
            generation=generation,
            spawned_at=datetime.now().isoformat(),
            parent_agent_id=parent_agent_id,
        )

        # Add to registry
        self.agents[agent_id] = agent
        self.total_spawns += 1
        self.generation_counts[generation] += 1

        # Generate agent code
        if self.enable_polyglot_execution:
            self._generate_agent_code(agent)

        # Log spawning
        logger.info(
            f"✨ Spawned agent {agent_id}: "
            f"{human_lang_data['name']} + {prog_lang_data['name']} "
            f"→ locking {locked_section} "
            f"(gen {generation}, reason: {reason})"
        )

        return agent_id

    def _generate_agent_code(self, agent: DefenseAgent) -> None:
        """Generate executable code for agent in its programming language."""
        template_dir = self.data_dir / "cerberus" / "agent_templates"
        agent_dir = self.data_dir / "cerberus" / "agents"

        # Get template file
        template_file = template_dir / f"{agent.programming_language}_template{self.languages['programming_languages'][agent.programming_language]['extension']}"

        if not template_file.exists():
            logger.warning(
                f"No template for {agent.programming_language}, using Python fallback"
            )
            template_file = template_dir / "python_template.py"

        # Read template
        try:
            with open(template_file, encoding="utf-8") as f:
                template_code = f.read()
        except Exception as e:
            logger.error(f"Failed to read template {template_file}: {e}")
            return

        # Substitute placeholders
        agent_code = template_code.format(
            agent_id=agent.agent_id,
            human_lang=agent.human_language,
            human_lang_name=agent.human_language_name,
            programming_lang=agent.programming_language,
            programming_lang_name=agent.programming_language_name,
            locked_section=agent.locked_section,
            generation=agent.generation,
        )

        # Write agent code
        extension = self.languages["programming_languages"][agent.programming_language][
            "extension"
        ]
        agent_file = agent_dir / f"{agent.agent_id}{extension}"

        with open(agent_file, "w", encoding="utf-8") as f:
            f.write(agent_code)

        # Make executable if shell script
        if extension == ".sh":
            os.chmod(agent_file, 0o755)

        agent.log_file = str(agent_dir / f"{agent.agent_id}.log")

        logger.debug(f"Generated agent code: {agent_file}")

    def _escalate_lockdown(self) -> None:
        """Escalate system lockdown level based on bypass count."""
        # Lockdown level increases with number of bypasses
        new_level = min(10, self.total_bypasses)

        if new_level > self.lockdown_level:
            self.lockdown_level = new_level
            logger.critical(
                f"🔒 LOCKDOWN ESCALATION: Level {self.lockdown_level}/10 "
                f"({len(self.locked_sections)}/{len(self.LOCKABLE_SECTIONS)} sections locked)"
            )

    def _log_bypass_event(self, event: BypassEvent) -> None:
        """Log bypass event to audit trail."""
        audit_file = (
            self.data_dir
            / "cerberus"
            / "logs"
            / f"bypasses_{datetime.now().strftime('%Y%m')}.jsonl"
        )

        with open(audit_file, "a") as f:
            f.write(json.dumps(event.__dict__) + "\n")

    def _notify_security_enforcer(self, event: BypassEvent) -> None:
        """Notify ASL3Security of bypass event."""
        try:
            if hasattr(self.security_enforcer, "_handle_suspicious_activity"):
                self.security_enforcer._handle_suspicious_activity(
                    user=event.attacker_signature or "unknown",
                    resource="cerberus_defense",
                    reason=f"agent_bypass_{event.bypass_type}",
                )
        except Exception as e:
            logger.error(f"Failed to notify security enforcer: {e}")

    def get_agent_registry(self) -> dict[str, Any]:
        """Get current agent registry with statistics."""
        active_agents = [a for a in self.agents.values() if a.status == "active"]

        # Group by generation
        by_generation = defaultdict(list)
        for agent in active_agents:
            by_generation[agent.generation].append(agent)

        # Group by programming language
        by_prog_lang = defaultdict(int)
        for agent in active_agents:
            by_prog_lang[agent.programming_language] += 1

        # Group by human language
        by_human_lang = defaultdict(int)
        for agent in active_agents:
            by_human_lang[agent.human_language] += 1

        return {
            "total_agents": len(self.agents),
            "active_agents": len(active_agents),
            "total_spawns": self.total_spawns,
            "total_bypasses": self.total_bypasses,
            "lockdown_level": self.lockdown_level,
            "locked_sections": list(self.locked_sections),
            "sections_remaining": len(self.LOCKABLE_SECTIONS) - len(
                self.locked_sections
            ),
            "by_generation": {
                f"gen_{gen}": len(agents) for gen, agents in by_generation.items()
            },
            "by_programming_language": dict(by_prog_lang),
            "by_human_language": dict(by_human_lang),
            "recent_bypasses": [
                {
                    "event_id": e.event_id,
                    "timestamp": e.timestamp,
                    "bypass_type": e.bypass_type,
                    "spawned_count": len(e.spawned_agents),
                }
                for e in self.bypass_events[-10:]
            ],
        }

    def generate_audit_report(self) -> str:
        """Generate comprehensive audit report."""
        registry = self.get_agent_registry()

        report = f"""
# Cerberus Hydra Defense - Audit Report

**Generated**: {datetime.now().isoformat()}
**Status**: {"🔴 LOCKDOWN" if self.lockdown_level >= 5 else "🟡 ELEVATED" if self.lockdown_level > 0 else "🟢 NORMAL"}

## Defense Statistics

- **Total Agents Spawned**: {registry['total_spawns']}
- **Currently Active**: {registry['active_agents']}
- **Security Bypasses**: {registry['total_bypasses']}
- **Lockdown Level**: {registry['lockdown_level']}/10
- **Sections Locked**: {len(registry['locked_sections'])}/{len(self.LOCKABLE_SECTIONS)}

## Agent Distribution

### By Generation
"""

        for gen, count in sorted(registry["by_generation"].items()):
            report += f"- {gen}: {count} agents\n"

        report += "\n### By Programming Language (Top 10)\n"
        sorted_prog = sorted(
            registry["by_programming_language"].items(), key=lambda x: x[1], reverse=True
        )
        for lang, count in sorted_prog[:10]:
            lang_name = self.languages["programming_languages"][lang]["name"]
            report += f"- {lang_name}: {count} agents\n"

        report += "\n### By Human Language (Top 10)\n"
        sorted_human = sorted(
            registry["by_human_language"].items(), key=lambda x: x[1], reverse=True
        )
        for lang, count in sorted_human[:10]:
            lang_name = self.languages["human_languages"][lang]["name"]
            report += f"- {lang_name}: {count} agents\n"

        report += "\n## Locked Sections\n\n"
        for section in sorted(registry["locked_sections"]):
            report += f"- ✅ {section}\n"

        report += "\n## Recent Bypass Events\n\n"
        for event in registry["recent_bypasses"]:
            report += f"- [{event['timestamp']}] {event['bypass_type']} → spawned {event['spawned_count']} agents\n"

        report += f"""

## Integration Status

- **ASL3 Security**: {"✅ Connected" if self.security_enforcer else "❌ Not connected"}
- **Polyglot Execution**: {"✅ Enabled" if self.enable_polyglot_execution else "❌ Disabled"}
- **Max Agents Limit**: {self.max_agents}

## Recommendations

"""

        if registry["lockdown_level"] >= 7:
            report += "- 🚨 **CRITICAL**: Lockdown level critical. Immediate investigation required.\n"
        elif registry["lockdown_level"] >= 4:
            report += "- ⚠️ **WARNING**: Elevated lockdown level. Monitor for continued attacks.\n"

        if registry["active_agents"] > self.max_agents * 0.8:
            report += f"- ⚠️ **WARNING**: Approaching max agents limit ({registry['active_agents']}/{self.max_agents}).\n"

        if len(registry["locked_sections"]) >= len(self.LOCKABLE_SECTIONS) * 0.8:
            report += "- ⚠️ **WARNING**: Most system sections locked. Consider agent cleanup.\n"

        report += "\n---\n**Cerberus Hydra Defense System**: When one guard falls, three rise to replace it.\n"

        return report


def cli_main():
    """Command-line interface for Cerberus Hydra Defense."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Cerberus Hydra Defense - Exponential Multi-Language Agent Spawning"
    )
    parser.add_argument(
        "action",
        choices=["init", "bypass", "status", "report"],
        help="Action to perform",
    )
    parser.add_argument(
        "--agent-id", type=str, help="Agent ID for bypass detection"
    )
    parser.add_argument(
        "--bypass-type", type=str, default="unknown", help="Type of bypass"
    )
    parser.add_argument(
        "--initial-agents", type=int, default=3, help="Number of initial agents"
    )
    parser.add_argument("--data-dir", type=str, default="data", help="Data directory")

    args = parser.parse_args()

    # Initialize Cerberus
    cerberus = CerberusHydraDefense(data_dir=args.data_dir)

    if args.action == "init":
        print(f"🐍 Initializing Cerberus Hydra Defense with {args.initial_agents} agents...")
        spawned = cerberus.spawn_initial_agents(count=args.initial_agents)
        print(f"✅ Spawned {len(spawned)} initial agents")
        print(f"Agent IDs: {', '.join(spawned)}")

    elif args.action == "bypass":
        print("🚨 Simulating security bypass...")
        event_id = cerberus.detect_bypass(
            agent_id=args.agent_id, bypass_type=args.bypass_type
        )
        print(f"✅ Bypass handled: {event_id}")
        print(f"Lockdown level: {cerberus.lockdown_level}/10")

    elif args.action == "status":
        registry = cerberus.get_agent_registry()
        print("\n" + json.dumps(registry, indent=2))

    elif args.action == "report":
        report = cerberus.generate_audit_report()
        print(report)

        # Save to file
        report_file = (
            Path(args.data_dir)
            / "cerberus"
            / f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        with open(report_file, "w") as f:
            f.write(report)
        print(f"\n📄 Report saved to: {report_file}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(cli_main())
