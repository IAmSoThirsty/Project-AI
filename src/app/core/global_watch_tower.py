"""Global Watch Tower Singleton - Security Command Center.

Provides global access to the Border Patrol Watch Tower system for
system-wide monitoring, verification, and threat detection.

This module implements a singleton pattern for the Watch Tower hierarchy,
allowing any part of the application to access border patrol services
without needing to pass instances through the entire call chain.

Security Command Center Architecture:
    Cerberus (Chief of Security)
        ↓
    Security Command Center (Global Watch Tower)
        ↓
    ┌──────────────┬─────────────────┬──────────────┬──────────────┐
    │              │                 │              │              │
    Border Patrol  Active Defense    Red Team      Oversight &
    Operations     Agents            Agents        Analysis
    │              │                 │              │
    ├ PortAdmin    ├ SafetyGuard     ├ RedTeam     ├ Oversight
    ├ WatchTower   ├ Constitutional  ├ CodeAdv     ├ Validator
    ├ GateGuardian ├ TarlProtector   ├ Jailbreak   └ Explainability
    └ VerifierAgent└ DepAuditor

Usage:
    from app.core.global_watch_tower import GlobalWatchTower

    # Initialize the global watch tower system (Security Command Center)
    GlobalWatchTower.initialize()

    # Access from anywhere in the application
    tower = GlobalWatchTower.get_instance()
    result = tower.verify_file("/path/to/file.py")

    # Access Cerberus (Chief of Security)
    cerberus = tower.get_chief_of_security()
    status = cerberus.get_security_status()

    # Register external security agents
    tower.register_security_agent("active_defense", "safety_guard_1")
    tower.register_security_agent("red_team", "adversary_1")
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any

from app.agents.border_patrol import (
    Cerberus,
    GateGuardian,
    PortAdmin,
    QuarantineBox,
    VerifierAgent,
    WatchTower,
)
from app.core.platform_tiers import (
    AuthorityLevel,
    ComponentRole,
    PlatformTier,
    get_tier_registry,
)

logger = logging.getLogger(__name__)


class GlobalWatchTower:
    """Singleton wrapper for the Border Patrol Watch Tower system - Security Command Center.

    The Global Watch Tower serves as the Security Command Center, operating under
    Cerberus (Chief of Security). All security operations and agents are coordinated
    through this central hub.

    Provides global access to security services including:
    - File verification and quarantine (Border Patrol)
    - Threat detection and escalation (Active Defense)
    - Adversarial testing (Red Team)
    - Security oversight and analysis (Oversight & Analysis)
    - Emergency lockdown coordination (Cerberus Command)

    Security Authority:
    - Cerberus is the Chief of Security
    - All security agents report through the Security Command Center
    - All pre-existing security roles continue to operate

    Thread-safe singleton implementation.
    """

    _instance: GlobalWatchTower | None = None
    _lock = threading.Lock()
    _initialized = False

    def __init__(self) -> None:
        """Private constructor. Use get_instance() or initialize() instead."""
        if GlobalWatchTower._initialized:
            raise RuntimeError(
                "GlobalWatchTower is a singleton. Use get_instance() or initialize()"
            )

        self.cerberus: Cerberus = Cerberus()
        self.port_admins: list[PortAdmin] = []
        self.watch_towers: list[WatchTower] = []
        self.gate_guardians: list[GateGuardian] = []
        self.verifiers: dict[str, VerifierAgent] = {}

        # Statistics
        self.total_verifications = 0
        self.total_quarantined = 0
        self.total_incidents = 0
        self.total_lockdowns = 0

        logger.info("GlobalWatchTower singleton created")

    @classmethod
    def initialize(
        cls,
        num_port_admins: int = 1,
        towers_per_port: int = 10,
        gates_per_tower: int = 5,
        data_dir: str = "data",
        max_workers: int = 2,
        timeout: int = 8,
    ) -> GlobalWatchTower:
        """Initialize the global watch tower system.

        Args:
            num_port_admins: Number of port administrators (default: 1)
            towers_per_port: Number of watch towers per port (default: 10)
            gates_per_tower: Number of gate guardians per tower (default: 5)
            data_dir: Data directory for verification artifacts (default: "data")
            max_workers: Max worker processes for sandboxing (default: 2)
            timeout: Sandbox execution timeout in seconds (default: 8)

        Returns:
            The initialized GlobalWatchTower instance

        Example:
            tower = GlobalWatchTower.initialize(
                num_port_admins=2,
                towers_per_port=5,
                gates_per_tower=3
            )
        """
        with cls._lock:
            if cls._instance is not None:
                logger.warning(
                    "GlobalWatchTower already initialized, returning existing instance"
                )
                return cls._instance

            instance = cls.__new__(cls)
            instance.__init__()

            # Build the hierarchy
            instance.cerberus = Cerberus()

            for admin_idx in range(num_port_admins):
                port_admin = PortAdmin(f"pa-{admin_idx}", instance.cerberus)
                instance.port_admins.append(port_admin)

                for tower_idx in range(towers_per_port):
                    watch_tower = WatchTower(f"wt-{admin_idx}-{tower_idx}", port_admin)
                    port_admin.towers.append(watch_tower)
                    instance.watch_towers.append(watch_tower)

                    for gate_idx in range(gates_per_tower):
                        gate_id = f"gate-{admin_idx}-{tower_idx}-{gate_idx}"
                        verifier_id = f"verifier-{admin_idx}-{tower_idx}-{gate_idx}"

                        verifier = VerifierAgent(
                            agent_id=verifier_id,
                            data_dir=data_dir,
                            max_workers=max_workers,
                            timeout=timeout,
                        )
                        instance.verifiers[verifier_id] = verifier

                        gate_guardian = GateGuardian(
                            gate_id=gate_id,
                            verifier=verifier,
                            watch_tower=watch_tower,
                        )
                        instance.gate_guardians.append(gate_guardian)

            cls._instance = instance
            cls._initialized = True

            # Register border patrol agents with Cerberus (Chief of Security)
            for admin in instance.port_admins:
                instance.cerberus.register_security_agent(
                    "border_patrol", admin.admin_id
                )
            for tower in instance.watch_towers:
                instance.cerberus.register_security_agent(
                    "border_patrol", tower.tower_id
                )
            for gate in instance.gate_guardians:
                instance.cerberus.register_security_agent("border_patrol", gate.gate_id)
            for verifier_id in instance.verifiers:
                instance.cerberus.register_security_agent("border_patrol", verifier_id)

            logger.info(
                "GlobalWatchTower (Security Command Center) initialized under Cerberus (Chief of Security)"
            )
            logger.info(
                "Border Patrol: %d admins, %d towers, %d gates, %d verifiers",
                len(instance.port_admins),
                len(instance.watch_towers),
                len(instance.gate_guardians),
                len(instance.verifiers),
            )

            # Register with Tier Registry as Tier-2 Infrastructure Controller
            try:
                tier_registry = get_tier_registry()
                tier_registry.register_component(
                    component_id="global_watch_tower",
                    component_name="GlobalWatchTower",
                    tier=PlatformTier.TIER_2_INFRASTRUCTURE,
                    authority_level=AuthorityLevel.CONSTRAINED,
                    role=ComponentRole.INFRASTRUCTURE_CONTROLLER,
                    component_ref=instance,
                    dependencies=["cognition_kernel"],  # Depends on kernel for authority
                    can_be_paused=True,  # Can be paused by Tier-1
                    can_be_replaced=False,  # Core security infrastructure
                )
                logger.info("GlobalWatchTower registered as Tier-2 Infrastructure Controller")
            except Exception as e:
                logger.warning("Failed to register GlobalWatchTower in tier registry: %s", e)

            return instance

    @classmethod
    def get_instance(cls) -> GlobalWatchTower:
        """Get the singleton instance of GlobalWatchTower.

        Returns:
            The GlobalWatchTower instance

        Raises:
            RuntimeError: If not initialized. Call initialize() first.

        Example:
            tower = GlobalWatchTower.get_instance()
            result = tower.verify_file("/path/to/file.py")
        """
        if cls._instance is None:
            raise RuntimeError(
                "GlobalWatchTower not initialized. Call GlobalWatchTower.initialize() first"
            )
        return cls._instance

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if the global watch tower system is initialized.

        Returns:
            True if initialized, False otherwise
        """
        return cls._initialized

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (mainly for testing).

        Warning:
            This should only be used in tests. Calling this in production
            code could lead to race conditions and undefined behavior.
        """
        with cls._lock:
            cls._instance = None
            cls._initialized = False
            logger.warning("GlobalWatchTower singleton reset")

    def verify_file(self, file_path: str | Path) -> dict[str, Any]:
        """Verify a file through the border patrol system.

        Args:
            file_path: Path to the file to verify

        Returns:
            Verification report dict with keys:
                - success: bool
                - verdict: str ("clean" or "suspicious")
                - deps: dict (dependency analysis)
                - sandbox: dict (sandbox execution results)

        Example:
            result = tower.verify_file("/path/to/plugin.py")
            if result["success"] and result["verdict"] == "clean":
                print("File is safe to use")
        """
        file_path_str = str(file_path)

        # Round-robin gate selection for load balancing
        gate_idx = self.total_verifications % len(self.gate_guardians)
        gate = self.gate_guardians[gate_idx]

        # Quarantine and process
        self.total_quarantined += 1
        gate.ingest(file_path_str)

        result = gate.process_next(file_path_str)
        self.total_verifications += 1

        if not result.get("success"):
            self.total_incidents += 1

        # Release from quarantine after processing
        gate.release(file_path_str)

        return result

    def quarantine_file(self, file_path: str | Path) -> QuarantineBox:
        """Place a file in quarantine without immediately processing it.

        Args:
            file_path: Path to the file to quarantine

        Returns:
            QuarantineBox instance representing the quarantined file

        Example:
            box = tower.quarantine_file("/suspicious/file.py")
            # Later...
            result = tower.process_quarantined(str(box.path))
        """
        file_path_str = str(file_path)
        gate_idx = self.total_quarantined % len(self.gate_guardians)
        gate = self.gate_guardians[gate_idx]

        self.total_quarantined += 1
        return gate.ingest(file_path_str)

    def process_quarantined(self, file_path: str) -> dict[str, Any]:
        """Process a file that was previously quarantined.

        Args:
            file_path: Path of the quarantined file

        Returns:
            Verification report dict

        Raises:
            KeyError: If the file is not in quarantine
        """
        # Find which gate has this file
        for gate in self.gate_guardians:
            if file_path in gate.quarantine:
                result = gate.process_next(file_path)
                self.total_verifications += 1

                if not result.get("success"):
                    self.total_incidents += 1

                gate.release(file_path)
                return result

        raise KeyError(f"File not found in quarantine: {file_path}")

    def activate_emergency_lockdown(self, reason: str = "unspecified") -> None:
        """Activate emergency lockdown across all gate guardians.

        Args:
            reason: Reason for the lockdown (for logging)

        Example:
            tower.activate_emergency_lockdown("Critical security breach detected")
        """
        logger.critical("EMERGENCY LOCKDOWN ACTIVATED: %s", reason)

        for gate in self.gate_guardians:
            gate.activate_force_field()

        self.total_lockdowns += 1

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the watch tower system.

        Returns:
            Dict containing:
                - total_verifications: Total files verified
                - total_quarantined: Total files quarantined
                - total_incidents: Total security incidents detected
                - total_lockdowns: Total emergency lockdowns
                - num_admins: Number of port administrators
                - num_towers: Number of watch towers
                - num_gates: Number of gate guardians
                - active_quarantine: Number of files currently in quarantine
                - cerberus_incidents: Number of incidents recorded by Cerberus

        Example:
            stats = tower.get_stats()
            print(f"Verified {stats['total_verifications']} files")
        """
        active_quarantine = sum(len(gate.quarantine) for gate in self.gate_guardians)

        return {
            "total_verifications": self.total_verifications,
            "total_quarantined": self.total_quarantined,
            "total_incidents": self.total_incidents,
            "total_lockdowns": self.total_lockdowns,
            "num_admins": len(self.port_admins),
            "num_towers": len(self.watch_towers),
            "num_gates": len(self.gate_guardians),
            "active_quarantine": active_quarantine,
            "cerberus_incidents": len(self.cerberus.incidents),
        }

    def get_cerberus_incidents(self) -> list[Any]:
        """Get all incidents recorded by Cerberus.

        Returns:
            List of incident records

        Example:
            for incident in tower.get_cerberus_incidents():
                print(f"Incident: {incident}")
        """
        return self.cerberus.incidents.copy()

    def get_tower_by_id(self, tower_id: str) -> WatchTower | None:
        """Get a specific watch tower by its ID.

        Args:
            tower_id: The tower identifier

        Returns:
            WatchTower instance or None if not found
        """
        for tower in self.watch_towers:
            if tower.tower_id == tower_id:
                return tower
        return None

    def get_gate_by_id(self, gate_id: str) -> GateGuardian | None:
        """Get a specific gate guardian by its ID.

        Args:
            gate_id: The gate identifier

        Returns:
            GateGuardian instance or None if not found
        """
        for gate in self.gate_guardians:
            if gate.gate_id == gate_id:
                return gate
        return None

    def get_chief_of_security(self) -> Cerberus:
        """Get Cerberus, the Chief of Security.

        Returns:
            Cerberus instance (Chief of Security)

        Example:
            tower = GlobalWatchTower.get_instance()
            cerberus = tower.get_chief_of_security()
            status = cerberus.get_security_status()
        """
        return self.cerberus

    def register_security_agent(
        self, agent_type: str, agent_id: str, agent_instance: Any = None
    ) -> None:
        """Register an external security agent with Cerberus (Chief of Security).

        This allows other security agents in the system to register themselves
        under Cerberus's command through the Security Command Center.

        Args:
            agent_type: Type of security agent (active_defense, red_team, oversight)
            agent_id: Unique identifier for the agent
            agent_instance: Optional agent instance for future reference

        Example:
            tower = GlobalWatchTower.get_instance()
            tower.register_security_agent("active_defense", "safety_guard_1")
            tower.register_security_agent("red_team", "adversary_1")
        """
        self.cerberus.register_security_agent(agent_type, agent_id)
        logger.info(
            "Security Command Center: Registered %s agent '%s' with Cerberus (Chief of Security)",
            agent_type,
            agent_id,
        )

    def get_security_status(self) -> dict[str, Any]:
        """Get comprehensive security status from Cerberus (Chief of Security).

        Returns:
            dict: Complete security status including all registered agents

        Example:
            tower = GlobalWatchTower.get_instance()
            status = tower.get_security_status()
            print(f"Chief: {status['chief_of_security']}")
            print(f"Agents: {status['registered_agents']}")
        """
        return self.cerberus.get_security_status()


# Convenience functions for global access
def get_global_watch_tower() -> GlobalWatchTower:
    """Convenience function to get the global watch tower instance.

    Returns:
        The GlobalWatchTower singleton instance

    Raises:
        RuntimeError: If not initialized

    Example:
        from app.core.global_watch_tower import get_global_watch_tower

        tower = get_global_watch_tower()
        result = tower.verify_file("/path/to/file.py")
    """
    return GlobalWatchTower.get_instance()


def verify_file_globally(file_path: str | Path) -> dict[str, Any]:
    """Convenience function to verify a file through the global watch tower.

    Args:
        file_path: Path to the file to verify

    Returns:
        Verification report dict

    Raises:
        RuntimeError: If GlobalWatchTower not initialized

    Example:
        from app.core.global_watch_tower import verify_file_globally

        result = verify_file_globally("/path/to/file.py")
        if result["verdict"] == "clean":
            print("File verified successfully")
    """
    tower = GlobalWatchTower.get_instance()
    return tower.verify_file(file_path)
