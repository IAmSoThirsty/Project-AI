"""
Cerberus Hydra Defense Mechanism
==================================

Implements exponential multi-implementation spawning for defense against security breaches.
When a security agent is bypassed or disabled, automatically instantiates 3 new defensive agents,
each in a random combination of human language and programming language.

Features:
- Exponential spawning (3x on each bypass)
- Multi-language agent implementation (50 human × 50 programming languages)
- Progressive system lockdown with 25 stages
- Deterministic language selection (seeded by incident ID)
- Runtime health verification and management
- Safe template rendering with injection prevention
- Agent process lifecycle management
- Integration with ASL3Security and anomaly detection
- Comprehensive audit logging and registry

Based on the mythological Hydra: cut off one head, three more grow back.
"""

import hashlib
import json
import logging
import os
import random
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from app.core.cerberus_agent_process import AgentProcess
    from app.core.cerberus_lockdown_controller import LockdownController
    from app.core.cerberus_runtime_manager import RuntimeManager
    from app.core.cerberus_template_renderer import TemplateRenderer
except ImportError:
    # For testing/standalone usage
    from src.app.core.cerberus_agent_process import AgentProcess
    from src.app.core.cerberus_lockdown_controller import LockdownController
    from src.app.core.cerberus_runtime_manager import RuntimeManager
    from src.app.core.cerberus_template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


@dataclass
class AgentRecord:
    """Enhanced Cerberus defense agent record with full lifecycle tracking."""

    agent_id: str
    spawn_time: str
    source_event: str
    programming_language: str
    programming_language_name: str
    human_language: str
    human_language_name: str
    runtime_path: str
    locked_section: str
    generation: int
    lockdown_stage_at_spawn: int
    parent_agent_id: str | None = None
    pid: int | None = None
    status: str = "active"
    log_file: str | None = None
    process: AgentProcess | None = None


@dataclass
class BypassEvent:
    """Record of a security bypass event."""

    event_id: str
    timestamp: str
    bypassed_agent_id: str
    bypass_type: str
    risk_score: float = 0.5
    bypass_depth: int = 1
    attacker_signature: str | None = None
    spawned_agents: list[str] = field(default_factory=list)
    lockdown_stage: int = 0


class CerberusHydraDefense:
    """
    Cerberus Hydra Defense System - Exponential Multi-Language Agent Spawning.

    When a guard is bypassed, spawn 3 new guards in random language combinations.
    Each guard locks a distinct section of the system for progressive containment.

    Enhanced with:
    - RuntimeManager for runtime health verification and selection
    - TemplateRenderer for safe code generation
    - LockdownController for deterministic lockdown stages
    - AgentProcess for cross-language process management
    - Deterministic language selection seeded by incident ID
    - Rolling window for language diversity tracking
    """

    SPAWN_FACTOR = 3  # Number of agents spawned per bypass
    LANGUAGE_DIVERSITY_WINDOW = 20  # Track last N agents for diversity

    def __init__(
        self,
        data_dir: str = "data",
        enable_polyglot_execution: bool = True,
        max_agents: int = 50,
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

        # Initialize new subsystems
        self.runtime_manager = RuntimeManager(data_dir=str(self.data_dir))
        self.template_renderer = TemplateRenderer()
        self.lockdown_controller = LockdownController(data_dir=str(self.data_dir))

        # Load language database
        self.languages = self._load_language_database()

        # Agent registry (updated to use AgentRecord)
        self.agents: dict[str, AgentRecord] = {}
        self.bypass_events: list[BypassEvent] = []

        # Language diversity tracking
        self.recent_languages: deque = deque(maxlen=self.LANGUAGE_DIVERSITY_WINDOW)

        # Statistics
        self.total_spawns = 0
        self.total_bypasses = 0
        self.generation_counts: dict[int, int] = defaultdict(int)

        # Initialize directories
        self._initialize_directories()

        # Verify runtimes at startup
        self._verify_runtimes()

        # Load existing state
        self._load_state()

        logger.info(
            "Cerberus Hydra Defense initialized: "
            f"{len(self.languages['human_languages'])} human languages, "
            f"{len(self.languages['programming_languages'])} programming languages, "
            f"{len(self.runtime_manager.runtimes)} runtimes"
        )

    def _verify_runtimes(self) -> None:
        """Verify runtime health at startup."""
        logger.info("Verifying runtime health...")
        summary = self.runtime_manager.verify_runtimes(timeout=5)

        logger.info(
            f"Runtime verification complete: {summary['healthy']} healthy, "
            f"{summary['degraded']} degraded, {summary['unavailable']} unavailable"
        )

        if summary["healthy"] < 3:
            logger.warning(
                "Less than 3 healthy runtimes available. Polyglot execution may be limited."
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
            logger.error("Language database not found: %s", db_path)
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

                # Restore agents (update to use AgentRecord fields)
                for agent_data in state.get("agents", []):
                    # Convert old DefenseAgent format to new AgentRecord format
                    agent = AgentRecord(
                        agent_id=agent_data["agent_id"],
                        spawn_time=agent_data.get(
                            "spawned_at",
                            agent_data.get("spawn_time", datetime.now().isoformat()),
                        ),
                        source_event=agent_data.get(
                            "source_event", "restored_from_state"
                        ),
                        programming_language=agent_data["programming_language"],
                        programming_language_name=agent_data[
                            "programming_language_name"
                        ],
                        human_language=agent_data["human_language"],
                        human_language_name=agent_data["human_language_name"],
                        runtime_path=agent_data.get("runtime_path", "python3"),
                        locked_section=agent_data["locked_section"],
                        generation=agent_data["generation"],
                        lockdown_stage_at_spawn=agent_data.get(
                            "lockdown_stage_at_spawn", 0
                        ),
                        parent_agent_id=agent_data.get("parent_agent_id"),
                        pid=agent_data.get("process_id") or agent_data.get("pid"),
                        status=agent_data.get("status", "active"),
                        log_file=agent_data.get("log_file"),
                    )
                    self.agents[agent.agent_id] = agent

                logger.info("Restored %s agents from state", len(self.agents))
            except Exception as e:
                logger.error("Failed to load Cerberus state: %s", e)

    def _save_state(self) -> None:
        """Persist Cerberus state."""
        state_file = self.data_dir / "cerberus" / "registry" / "state.json"

        # Convert AgentRecord to serializable format
        agents_data = []
        for agent in self.agents.values():
            agent_dict = {
                "agent_id": agent.agent_id,
                "spawn_time": agent.spawn_time,
                "source_event": agent.source_event,
                "programming_language": agent.programming_language,
                "programming_language_name": agent.programming_language_name,
                "human_language": agent.human_language,
                "human_language_name": agent.human_language_name,
                "runtime_path": agent.runtime_path,
                "locked_section": agent.locked_section,
                "generation": agent.generation,
                "lockdown_stage_at_spawn": agent.lockdown_stage_at_spawn,
                "parent_agent_id": agent.parent_agent_id,
                "pid": agent.pid,
                "status": agent.status,
                "log_file": agent.log_file,
            }
            agents_data.append(agent_dict)

        state = {
            "agents": agents_data,
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
        logger.info("Spawning %s initial Cerberus agents...", count)

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

    def on_anomaly(self, event: dict[str, Any]) -> None:
        """
        Handle anomaly detection event.

        API:
            event (dict): Anomaly event with keys:
                - event_id (str): Unique event identifier
                - timestamp (str): ISO format timestamp
                - anomaly_type (str): Type of anomaly detected
                - severity (str): low, medium, high, critical
                - details (dict): Additional context

        Returns:
            None
        """
        event_id = event.get("event_id", str(uuid.uuid4()))
        anomaly_type = event.get("anomaly_type", "unknown")
        severity = event.get("severity", "medium")

        logger.warning("⚠️ ANOMALY DETECTED: %s (severity: %s, event: %s)", anomaly_type, severity, event_id)

        # Map severity to risk score
        severity_map = {
            "low": 0.2,
            "medium": 0.4,
            "high": 0.7,
            "critical": 0.9,
        }
        risk_score = severity_map.get(severity, 0.5)

        # For high/critical anomalies, trigger agent spawning
        if severity in ["high", "critical"]:
            logger.info("High severity anomaly, spawning defensive agents...")
            self.detect_bypass(
                agent_id=None,
                bypass_type=f"anomaly_{anomaly_type}",
                attacker_signature=event.get("source", "anomaly_detector"),
                risk_score=risk_score,
                bypass_depth=1,
            )
        else:
            # Log for monitoring but don't spawn agents
            self._emit_structured_log(
                event_type="anomaly_detected",
                details={
                    "event_id": event_id,
                    "anomaly_type": anomaly_type,
                    "severity": severity,
                    "risk_score": risk_score,
                },
            )

    def on_bypass_detected(self, event: dict[str, Any]) -> str:
        """
        Handle security bypass detection event.

        API:
            event (dict): Bypass event with keys:
                - event_id (str): Unique event identifier
                - timestamp (str): ISO format timestamp
                - agent_id (str, optional): Bypassed agent ID
                - bypass_type (str): Type of bypass
                - risk_score (float): Risk score 0.0-1.0
                - bypass_depth (int): Layers of security bypassed
                - attacker_signature (str, optional): Attacker identifier

        Returns:
            str: Event ID of bypass response
        """
        agent_id = event.get("agent_id")
        bypass_type = event.get("bypass_type", "unknown")
        risk_score = event.get("risk_score", 0.7)
        bypass_depth = event.get("bypass_depth", 1)
        attacker_signature = event.get("attacker_signature")

        logger.critical(
            f"🚨 BYPASS DETECTED via API: {bypass_type} "
            f"(agent: {agent_id}, risk: {risk_score}, depth: {bypass_depth})"
        )

        return self.detect_bypass(
            agent_id=agent_id,
            bypass_type=bypass_type,
            attacker_signature=attacker_signature,
            risk_score=risk_score,
            bypass_depth=bypass_depth,
        )

    def detect_bypass(
        self,
        agent_id: str | None = None,
        bypass_type: str = "unknown",
        attacker_signature: str | None = None,
        risk_score: float = 0.5,
        bypass_depth: int = 1,
    ) -> str:
        """
        Detect and respond to a security bypass.

        Spawns 3 new agents in response, applies lockdown, uses deterministic selection.

        Args:
            agent_id: ID of bypassed agent (if known)
            bypass_type: Type of bypass detected
            attacker_signature: Signature of attacker (for tracking)
            risk_score: Risk score from 0.0 to 1.0
            bypass_depth: Number of security layers bypassed

        Returns:
            Event ID of bypass event
        """
        event_id = str(uuid.uuid4())
        self.total_bypasses += 1

        # Compute lockdown stage based on risk and depth
        lockdown_stage = self.lockdown_controller.compute_lockdown_stage(
            risk_score=risk_score,
            bypass_depth=bypass_depth,
        )

        # Apply lockdown
        self.lockdown_controller.apply_lockdown(
            stage=lockdown_stage,
            reason=f"bypass_{bypass_type}",
        )

        # Log bypass event
        bypass_event = BypassEvent(
            event_id=event_id,
            timestamp=datetime.now().isoformat(),
            bypassed_agent_id=agent_id or "unknown",
            bypass_type=bypass_type,
            risk_score=risk_score,
            bypass_depth=bypass_depth,
            attacker_signature=attacker_signature,
            lockdown_stage=lockdown_stage,
        )

        logger.critical(
            f"🚨 CERBERUS BYPASS DETECTED: {bypass_type} "
            f"(agent: {agent_id}, risk: {risk_score:.2f}, depth: {bypass_depth}, "
            f"lockdown: {lockdown_stage})"
        )

        # Determine parent agent and generation
        parent_agent = self.agents.get(agent_id) if agent_id else None
        generation = (parent_agent.generation + 1) if parent_agent else 1

        # Spawn SPAWN_FACTOR new agents with deterministic selection
        spawned_ids = []
        for i in range(self.SPAWN_FACTOR):
            # Use incident ID + index as seed for deterministic selection
            seed = int(hashlib.sha256(f"{event_id}-{i}".encode()).hexdigest()[:8], 16)

            new_agent_id = self._spawn_single_agent(
                generation=generation,
                parent_agent_id=agent_id,
                reason=f"bypass_{bypass_type}",
                incident_id=event_id,
                lockdown_stage=lockdown_stage,
                seed=seed,
            )
            if new_agent_id:
                spawned_ids.append(new_agent_id)

        bypass_event.spawned_agents = spawned_ids
        self.bypass_events.append(bypass_event)

        # Log bypass to audit trail
        self._log_bypass_event(bypass_event)

        # Emit structured log
        self._emit_structured_log(
            event_type="bypass_detected",
            details={
                "event_id": event_id,
                "bypass_type": bypass_type,
                "risk_score": risk_score,
                "bypass_depth": bypass_depth,
                "lockdown_stage": lockdown_stage,
                "spawned_agents": spawned_ids,
                "generation": generation,
            },
        )

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
        incident_id: str | None = None,
        lockdown_stage: int = 0,
        seed: int | None = None,
    ) -> str | None:
        """
        Spawn a single defense agent with deterministic language selection.

        Uses RuntimeManager, TemplateRenderer, and AgentProcess for enhanced spawning.

        Args:
            generation: Generation number (0 = initial, 1+ = spawned)
            parent_agent_id: ID of parent agent (if spawned in response)
            reason: Reason for spawning
            incident_id: Incident ID for deterministic selection
            lockdown_stage: Lockdown stage at time of spawn
            seed: Random seed for deterministic language selection

        Returns:
            Agent ID if successful, None otherwise
        """
        # Check max agents limit
        active_agents = len([a for a in self.agents.values() if a.status == "active"])
        if active_agents >= self.max_agents:
            logger.error("Cannot spawn agent: max agents (%s) reached", self.max_agents)
            return None

        # Generate agent ID
        agent_id = f"cerberus-{generation}-{uuid.uuid4().hex[:8]}"

        # Select runtime using RuntimeManager with deterministic selection
        runtime = self.runtime_manager.get_random_runtime(
            prefer_verified=True,
            seed=seed,
        )

        if not runtime:
            logger.error("No suitable runtime found for agent spawning")
            return None

        # Select human language (deterministic if seed provided)
        human_langs = list(self.languages["human_languages"].keys())

        if seed is not None:
            random.seed(seed + 1000)  # Different seed for human language

        # Avoid recently used languages for diversity
        recent_human_langs = [
            lang for _, lang in self.recent_languages if lang in human_langs
        ]
        available_human_langs = [
            lang for lang in human_langs if lang not in recent_human_langs[-10:]
        ]

        if not available_human_langs:
            available_human_langs = human_langs

        human_lang = random.choice(available_human_langs)
        human_lang_data = self.languages["human_languages"][human_lang]

        # Track language usage for diversity
        self.recent_languages.append((runtime.language_key, human_lang))

        # Select section to lock from available sections
        available_sections = self.lockdown_controller.get_available_sections()

        if not available_sections:
            # All sections locked, reuse sections
            available_sections = self.lockdown_controller.LOCKABLE_SECTIONS

        if seed is not None:
            random.seed(seed + 2000)  # Different seed for section

        locked_section = random.choice(available_sections)

        # Create agent record
        spawn_time = datetime.now().isoformat()
        agent = AgentRecord(
            agent_id=agent_id,
            spawn_time=spawn_time,
            source_event=incident_id or reason,
            programming_language=runtime.language_key,
            programming_language_name=runtime.name,
            human_language=human_lang,
            human_language_name=human_lang_data["name"],
            runtime_path=runtime.exec_path,
            locked_section=locked_section,
            generation=generation,
            lockdown_stage_at_spawn=lockdown_stage,
            parent_agent_id=parent_agent_id,
        )

        # Add to registry
        self.agents[agent_id] = agent
        self.total_spawns += 1
        self.generation_counts[generation] += 1

        # Generate agent code using TemplateRenderer
        if self.enable_polyglot_execution:
            success = self._generate_agent_code(agent, incident_id or "initial")
            if not success:
                logger.error("Failed to generate agent code for %s", agent_id)
                return None

        # Emit structured log
        self._emit_structured_log(
            event_type="agent_spawned",
            details={
                "agent_id": agent_id,
                "generation": generation,
                "programming_language": runtime.name,
                "human_language": human_lang_data["name"],
                "locked_section": locked_section,
                "lockdown_stage": lockdown_stage,
                "reason": reason,
                "runtime_health": runtime.health_status,
            },
        )

        # Log spawning
        logger.info(
            f"✨ Spawned agent {agent_id}: "
            f"{human_lang_data['name']} + {runtime.name} "
            f"→ locking {locked_section} "
            f"(gen {generation}, lockdown {lockdown_stage}, reason: {reason})"
        )

        return agent_id

    def _generate_agent_code(self, agent: AgentRecord, incident_id: str) -> bool:
        """
        Generate executable code for agent using TemplateRenderer and AgentProcess.

        Args:
            agent: Agent record
            incident_id: Incident ID for logging

        Returns:
            True if successful, False otherwise
        """
        template_dir = self.data_dir / "cerberus" / "agent_templates"
        agent_dir = self.data_dir / "cerberus" / "agents"

        # Get runtime descriptor
        runtime = self.runtime_manager.get_runtime(agent.programming_language)

        if not runtime:
            logger.error("Runtime not found for %s", agent.programming_language)
            return False

        # Get template file based on programming language
        # Try language-specific template first, then fall back to python
        template_candidates = [
            template_dir
            / f"{agent.programming_language}_template{self.languages['programming_languages'].get(agent.programming_language, {}).get('extension', '.py')}",
            template_dir / "python_template.py",
        ]

        template_file = None
        for candidate in template_candidates:
            if candidate.exists():
                template_file = candidate
                break

        if not template_file:
            logger.error("No template found for %s", agent.programming_language)
            return False

        # Prepare template context
        context = {
            "agent_id": agent.agent_id,
            "human_lang": agent.human_language,
            "human_lang_name": agent.human_language_name,
            "programming_lang": agent.programming_language,
            "programming_lang_name": agent.programming_language_name,
            "locked_section": agent.locked_section,
            "generation": str(agent.generation),
            "spawn_time": agent.spawn_time,
            "incident_id": incident_id,
            "runtime_path": agent.runtime_path,
        }

        # Render template using TemplateRenderer
        try:
            rendered_code = self.template_renderer.render_from_file(
                template_path=str(template_file),
                context=context,
                language=agent.programming_language,
                validate_required=False,  # Use flexible validation
                cache=True,
            )

        except Exception as e:
            logger.error("Failed to render template for %s: %s", agent.agent_id, e)
            return False

        # Write agent code
        extension = (
            self.languages["programming_languages"]
            .get(agent.programming_language, {})
            .get("extension", ".py")
        )

        agent_file = agent_dir / f"{agent.agent_id}{extension}"

        try:
            with open(agent_file, "w", encoding="utf-8") as f:
                f.write(rendered_code)

            # Make executable if shell script
            if extension == ".sh":
                os.chmod(agent_file, 0o755)

            agent.log_file = str(agent_dir / f"{agent.agent_id}.log")

            logger.debug("Generated agent code: %s", agent_file)

            # Optionally spawn agent process (disabled by default for safety)
            # self._spawn_agent_process(agent, str(agent_file))

            return True

        except Exception as e:
            logger.error("Failed to write agent code for %s: %s", agent.agent_id, e)
            return False

    def _spawn_agent_process(self, agent: AgentRecord, script_path: str) -> bool:
        """
        Spawn agent as a running process using AgentProcess.

        Args:
            agent: Agent record
            script_path: Path to agent script

        Returns:
            True if spawn successful, False otherwise
        """
        try:
            log_dir = str(self.data_dir / "cerberus" / "logs")

            agent_process = AgentProcess(
                agent_id=agent.agent_id,
                runtime_path=agent.runtime_path,
                script_path=script_path,
                log_dir=log_dir,
            )

            success = agent_process.spawn(timeout=10)

            if success:
                agent.process = agent_process
                agent.pid = agent_process.info.pid
                agent.status = "running"

                logger.info("Agent process spawned: %s (PID: %s)", agent.agent_id, agent.pid)

                return True

            else:
                logger.error("Failed to spawn agent process: %s", agent.agent_id)
                agent.status = "failed"
                return False

        except Exception as e:
            logger.error("Exception spawning agent process %s: %s", agent.agent_id, e)
            agent.status = "failed"
            return False

    def _emit_structured_log(self, event_type: str, details: dict[str, Any]) -> None:
        """
        Emit structured JSON log for lifecycle events.

        Args:
            event_type: Type of event
            details: Event details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "system": "cerberus_hydra",
        }
        log_entry.update(details)

        # Log as JSON
        logger.info(json.dumps(log_entry))

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
            logger.error("Failed to notify security enforcer: %s", e)

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

        # Get lockdown status
        lockdown_status = self.lockdown_controller.get_lockdown_status()

        return {
            "total_agents": len(self.agents),
            "active_agents": len(active_agents),
            "total_spawns": self.total_spawns,
            "total_bypasses": self.total_bypasses,
            "lockdown_stage": lockdown_status["current_stage"],
            "lockdown_severity": lockdown_status["severity"],
            "locked_sections": lockdown_status["locked_sections"],
            "sections_remaining": lockdown_status["remaining_count"],
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
                    "risk_score": e.risk_score,
                    "lockdown_stage": e.lockdown_stage,
                }
                for e in self.bypass_events[-10:]
            ],
        }

    def generate_audit_report(self) -> str:
        """Generate comprehensive audit report."""
        registry = self.get_agent_registry()
        lockdown_status = self.lockdown_controller.get_lockdown_status()
        runtime_health = self.runtime_manager.get_health_summary()

        severity_emoji = {
            "low": "🟢",
            "moderate": "🟡",
            "elevated": "🟡",
            "high": "🟠",
            "critical": "🔴",
        }
        status_emoji = severity_emoji.get(lockdown_status["severity"], "⚪")

        report = f"""
# Cerberus Hydra Defense - Audit Report

**Generated**: {datetime.now().isoformat()}
**Status**: {status_emoji} {lockdown_status["severity"].upper()}

## Defense Statistics

- **Total Agents Spawned**: {registry['total_spawns']}
- **Currently Active**: {registry['active_agents']}
- **Security Bypasses**: {registry['total_bypasses']}
- **Lockdown Stage**: {lockdown_status['current_stage']}/25
- **Sections Locked**: {lockdown_status['locked_count']}/{lockdown_status['total_sections']}
- **Lockdown Percentage**: {lockdown_status['lockdown_percentage']:.1f}%

## Runtime Health

- **Total Runtimes**: {runtime_health['total_runtimes']}
- **Healthy**: {runtime_health['by_status']['healthy']}
- **Degraded**: {runtime_health['by_status']['degraded']}
- **Unavailable**: {runtime_health['by_status']['unavailable']}
- **Verified**: {runtime_health['verified_count']}

## Agent Distribution

### By Generation
"""

        for gen, count in sorted(registry["by_generation"].items()):
            report += f"- {gen}: {count} agents\n"

        report += "\n### By Programming Language (Top 10)\n"
        sorted_prog = sorted(
            registry["by_programming_language"].items(),
            key=lambda x: x[1],
            reverse=True,
        )
        for lang, count in sorted_prog[:10]:
            lang_name = (
                self.languages["programming_languages"].get(lang, {}).get("name", lang)
            )
            report += f"- {lang_name}: {count} agents\n"

        report += "\n### By Human Language (Top 10)\n"
        sorted_human = sorted(
            registry["by_human_language"].items(), key=lambda x: x[1], reverse=True
        )
        for lang, count in sorted_human[:10]:
            lang_name = (
                self.languages["human_languages"].get(lang, {}).get("name", lang)
            )
            report += f"- {lang_name}: {count} agents\n"

        report += "\n## Locked Sections\n\n"
        for section in sorted(registry["locked_sections"]):
            report += f"- ✅ {section}\n"

        report += "\n## Recent Bypass Events\n\n"
        for event in registry["recent_bypasses"]:
            report += (
                f"- [{event['timestamp']}] {event['bypass_type']} "
                f"(risk: {event['risk_score']:.2f}, stage: {event['lockdown_stage']}) "
                f"→ spawned {event['spawned_count']} agents\n"
            )

        report += f"""

## Integration Status

- **ASL3 Security**: {"✅ Connected" if self.security_enforcer else "❌ Not connected"}
- **Polyglot Execution**: {"✅ Enabled" if self.enable_polyglot_execution else "❌ Disabled"}
- **Max Agents Limit**: {self.max_agents}
- **Runtime Manager**: ✅ Active
- **Template Renderer**: ✅ Active
- **Lockdown Controller**: ✅ Active (Stage {lockdown_status['current_stage']})

## Recommendations

"""

        if lockdown_status["severity"] == "critical":
            report += "- 🚨 **CRITICAL**: Lockdown at critical level. Immediate investigation required.\n"
        elif lockdown_status["severity"] == "high":
            report += "- ⚠️ **WARNING**: Elevated lockdown level. Monitor for continued attacks.\n"

        if registry["active_agents"] > self.max_agents * 0.8:
            report += f"- ⚠️ **WARNING**: Approaching max agents limit ({registry['active_agents']}/{self.max_agents}).\n"

        if lockdown_status["lockdown_percentage"] >= 80:
            report += "- ⚠️ **WARNING**: Most system sections locked. Consider agent cleanup.\n"

        if runtime_health["by_status"]["healthy"] < 5:
            report += "- ⚠️ **WARNING**: Few healthy runtimes available. Polyglot diversity limited.\n"

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
    parser.add_argument("--agent-id", type=str, help="Agent ID for bypass detection")
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
        print(
            f"🐍 Initializing Cerberus Hydra Defense with {args.initial_agents} agents..."
        )
        spawned = cerberus.spawn_initial_agents(count=args.initial_agents)
        print(f"✅ Spawned {len(spawned)} initial agents")
        print(f"Agent IDs: {', '.join(spawned)}")

    elif args.action == "bypass":
        print("🚨 Simulating security bypass...")
        event_id = cerberus.detect_bypass(
            agent_id=args.agent_id, bypass_type=args.bypass_type
        )
        lockdown_status = cerberus.lockdown_controller.get_lockdown_status()
        print(f"✅ Bypass handled: {event_id}")
        print(f"Lockdown stage: {lockdown_status['current_stage']}/25")

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
