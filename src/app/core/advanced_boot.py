#!/usr/bin/env python3
"""
Advanced Boot System - God Tier Architecture
Project-AI Defense Engine

Implements:
1. Staged Boot Profiles - Different initialization sequences for different scenarios
2. Emergency-Only Mode - Minimal critical subsystems for crisis operations
3. Ethics-First Cold Start - Ethics validation before system initialization
4. Audit Replay - Complete event reconstruction and time-travel debugging

Monolithic Density: All advanced boot features in one cohesive system.
"""

import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Import event spine and governance graph for wiring
from app.core.event_spine import EventCategory, EventPriority, get_event_spine
from app.core.governance_graph import get_governance_graph

logger = logging.getLogger(__name__)


class BootProfile(Enum):
    """Boot profiles for different operational scenarios."""

    NORMAL = "normal"  # Full system initialization
    EMERGENCY = "emergency"  # Minimal critical subsystems only
    ETHICS_FIRST = "ethics_first"  # Ethics validation before all other systems
    MINIMAL = "minimal"  # Absolute minimum for testing
    RECOVERY = "recovery"  # Recovery mode with diagnostics
    DIAGNOSTIC = "diagnostic"  # Full diagnostics and logging
    AIR_GAPPED = "air_gapped"  # Offline operation mode
    ADVERSARIAL = "adversarial"  # High-security adversarial mode


@dataclass
class BootProfileConfig:
    """Configuration for a boot profile."""

    profile: BootProfile
    description: str
    subsystem_whitelist: list[str] | None = None  # If set, only these subsystems
    subsystem_blacklist: list[str] = field(default_factory=list)  # Never load these
    priority_overrides: dict[str, str] = field(default_factory=dict)  # Subsystem priority changes
    require_ethics_approval: bool = False  # Require ethics approval before init
    enable_health_monitoring: bool = True
    enable_audit_logging: bool = True
    max_init_time_seconds: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditEvent:
    """Complete audit event for replay."""

    event_id: str
    timestamp: datetime
    event_type: str
    subsystem_id: str | None
    action: str
    context: dict[str, Any]
    result: Any | None = None
    error: str | None = None
    state_snapshot: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "subsystem_id": self.subsystem_id,
            "action": self.action,
            "context": self.context,
            "result": self.result,
            "error": self.error,
            "state_snapshot": self.state_snapshot,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuditEvent":
        """Create from dictionary."""
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class AdvancedBootSystem:
    """
    Advanced Boot System - God Tier Architecture

    Provides staged boot profiles, emergency mode, ethics-first initialization,
    and complete audit replay capabilities.
    """

    # Emergency-only critical subsystems
    EMERGENCY_CRITICAL_SUBSYSTEMS = {
        "ethics_governance",
        "agi_safeguards",
        "situational_awareness",
        "biomedical_defense",
    }

    # Ethics-first initialization order (must init before others)
    ETHICS_PRIORITY_SUBSYSTEMS = {"ethics_governance", "agi_safeguards"}

    def __init__(self, data_dir: str = "data", audit_dir: str | None = None):
        """
        Initialize advanced boot system.

        Args:
            data_dir: Data directory
            audit_dir: Audit log directory (defaults to data_dir/audit)
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.audit_dir = Path(audit_dir) if audit_dir else self.data_dir / "audit"
        self.audit_dir.mkdir(parents=True, exist_ok=True)

        # Current boot profile
        self._current_profile: BootProfile | None = None
        self._current_profile_config: BootProfileConfig | None = None

        # Boot profiles registry
        self._profiles: dict[BootProfile, BootProfileConfig] = {}
        self._initialize_default_profiles()

        # Audit system
        self._audit_log: list[AuditEvent] = []
        self._audit_file_handle: Any | None = None
        self._audit_enabled = True

        # State snapshots for replay
        self._state_snapshots: dict[str, dict[str, Any]] = {}

        # Emergency mode state
        self._emergency_mode_active = False
        self._emergency_activation_time: datetime | None = None

        # Ethics approval tracking
        self._ethics_approvals: dict[str, bool] = {}
        self._ethics_checkpoint_passed = False

        # Boot statistics
        self._boot_stats = {
            "profile": None,
            "start_time": None,
            "end_time": None,
            "subsystems_initialized": 0,
            "subsystems_skipped": 0,
            "ethics_approvals_required": 0,
            "ethics_approvals_granted": 0,
            "emergency_activations": 0,
        }

        # Thread safety
        self._lock = threading.RLock()

        logger.info("Advanced Boot System initialized")

    def _initialize_default_profiles(self):
        """Initialize default boot profiles."""
        # NORMAL: Full system
        self._profiles[BootProfile.NORMAL] = BootProfileConfig(
            profile=BootProfile.NORMAL,
            description="Full system initialization with all subsystems",
            require_ethics_approval=False,
            enable_health_monitoring=True,
            enable_audit_logging=True,
        )

        # EMERGENCY: Minimal critical only
        self._profiles[BootProfile.EMERGENCY] = BootProfileConfig(
            profile=BootProfile.EMERGENCY,
            description="Emergency mode - critical subsystems only",
            subsystem_whitelist=list(self.EMERGENCY_CRITICAL_SUBSYSTEMS),
            require_ethics_approval=True,
            enable_health_monitoring=True,
            enable_audit_logging=True,
            max_init_time_seconds=30.0,
            metadata={"reason": "emergency_activation"},
        )

        # ETHICS_FIRST: Ethics validation before everything
        self._profiles[BootProfile.ETHICS_FIRST] = BootProfileConfig(
            profile=BootProfile.ETHICS_FIRST,
            description="Ethics-first cold start with validation gates",
            require_ethics_approval=True,
            priority_overrides={
                "ethics_governance": "CRITICAL",
                "agi_safeguards": "CRITICAL",
            },
            enable_health_monitoring=True,
            enable_audit_logging=True,
        )

        # MINIMAL: Absolute minimum
        self._profiles[BootProfile.MINIMAL] = BootProfileConfig(
            profile=BootProfile.MINIMAL,
            description="Minimal subsystems for testing",
            subsystem_whitelist=["ethics_governance", "agi_safeguards"],
            require_ethics_approval=False,
            enable_health_monitoring=False,
            enable_audit_logging=True,
        )

        # RECOVERY: Recovery with diagnostics
        self._profiles[BootProfile.RECOVERY] = BootProfileConfig(
            profile=BootProfile.RECOVERY,
            description="Recovery mode with enhanced diagnostics",
            require_ethics_approval=True,
            enable_health_monitoring=True,
            enable_audit_logging=True,
            metadata={"diagnostic_level": "verbose"},
        )

        # DIAGNOSTIC: Full logging
        self._profiles[BootProfile.DIAGNOSTIC] = BootProfileConfig(
            profile=BootProfile.DIAGNOSTIC,
            description="Diagnostic mode with verbose logging",
            require_ethics_approval=False,
            enable_health_monitoring=True,
            enable_audit_logging=True,
            metadata={"log_level": "DEBUG", "trace_enabled": True},
        )

        # AIR_GAPPED: Offline operation
        self._profiles[BootProfile.AIR_GAPPED] = BootProfileConfig(
            profile=BootProfile.AIR_GAPPED,
            description="Air-gapped offline operation mode",
            subsystem_blacklist=["cloud_sync", "remote_updates"],
            require_ethics_approval=True,
            enable_health_monitoring=True,
            enable_audit_logging=True,
        )

        # ADVERSARIAL: High-security mode
        self._profiles[BootProfile.ADVERSARIAL] = BootProfileConfig(
            profile=BootProfile.ADVERSARIAL,
            description="Adversarial mode with enhanced security",
            require_ethics_approval=True,
            priority_overrides={
                "ethics_governance": "CRITICAL",
                "agi_safeguards": "CRITICAL",
                "situational_awareness": "HIGH",
            },
            enable_health_monitoring=True,
            enable_audit_logging=True,
            metadata={"security_level": "maximum", "paranoid_mode": True},
        )

    def set_boot_profile(self, profile: BootProfile) -> bool:
        """
        Set the boot profile for the next initialization.

        Args:
            profile: Boot profile to use

        Returns:
            True if profile set successfully
        """
        with self._lock:
            if profile not in self._profiles:
                logger.error("Unknown boot profile: %s", profile)
                return False

            self._current_profile = profile
            self._current_profile_config = self._profiles[profile]

            self._audit_event(
                event_type="profile_changed",
                action="set_boot_profile",
                context={"profile": profile.value},
                result="success",
            )

            logger.info("Boot profile set to: %s", profile.value)
            logger.info("  Description: %s", self._current_profile_config.description)

            return True

    def get_current_profile(self) -> BootProfile | None:
        """Get current boot profile."""
        return self._current_profile

    def should_initialize_subsystem(
        self, subsystem_id: str, subsystem_metadata: dict[str, Any]
    ) -> tuple[bool, str | None]:
        """
        Check if a subsystem should be initialized based on current boot profile.

        Args:
            subsystem_id: Subsystem identifier
            subsystem_metadata: Subsystem metadata

        Returns:
            Tuple of (should_initialize, reason_if_not)
        """
        if not self._current_profile_config:
            # No profile set, check emergency mode only
            if self._emergency_mode_active:
                if subsystem_id not in self.EMERGENCY_CRITICAL_SUBSYSTEMS:
                    return False, "Emergency mode active - non-critical subsystem"
            return True, None

        config = self._current_profile_config

        # Emergency mode check (highest priority)
        if self._emergency_mode_active:
            if subsystem_id not in self.EMERGENCY_CRITICAL_SUBSYSTEMS:
                return False, "Emergency mode active - non-critical subsystem"

        # Check whitelist
        if config.subsystem_whitelist is not None:
            if subsystem_id not in config.subsystem_whitelist:
                return (
                    False,
                    f"Not in profile whitelist ({self._current_profile.value})",
                )

        # Check blacklist
        if subsystem_id in config.subsystem_blacklist:
            return False, f"In profile blacklist ({self._current_profile.value})"

        # Ethics-first check
        if config.require_ethics_approval:
            if subsystem_id not in self.ETHICS_PRIORITY_SUBSYSTEMS:
                if not self._ethics_checkpoint_passed:
                    return False, "Waiting for ethics checkpoint"

                # Require ethics approval for this subsystem
                if subsystem_id not in self._ethics_approvals:
                    # Request approval (would integrate with ethics subsystem)
                    approval = self._request_ethics_approval(subsystem_id, subsystem_metadata)
                    self._ethics_approvals[subsystem_id] = approval

                if not self._ethics_approvals.get(subsystem_id, False):
                    return False, "Ethics approval denied"

        return True, None

    def _request_ethics_approval(self, subsystem_id: str, metadata: dict[str, Any]) -> bool:
        """
        Request ethics approval for subsystem initialization.

        This method now:
        1. Emits events through the event spine (cross-domain visibility)
        2. Checks governance graph for authority relationships
        3. Creates auditable decisions with full context

        Args:
            subsystem_id: Subsystem requesting approval
            metadata: Subsystem metadata

        Returns:
            True if approved
        """
        priority = metadata.get("priority", "MEDIUM")

        with self._lock:
            self._boot_stats["ethics_approvals_required"] += 1

        # Check governance graph for consultation requirements
        governance_graph = get_governance_graph()
        must_consult = governance_graph.must_consult_domains(subsystem_id)

        # Determine approval based on priority and governance
        if priority in ["CRITICAL", "HIGH"]:
            approved = True
            reasoning = f"Auto-approved: {priority} priority subsystem"
        else:
            # Default approve for now (would require actual ethics evaluation)
            approved = True
            reasoning = "Auto-approved: Standard subsystem initialization"

        if approved:
            with self._lock:
                self._boot_stats["ethics_approvals_granted"] += 1

        # Generate unique event ID for traceability
        event_id = f"ethics_approval_{subsystem_id}_{int(time.time() * 1000)}"

        # Emit event through event spine - this makes approvals observable
        try:
            event_spine = get_event_spine()
            event_spine.publish(
                category=EventCategory.GOVERNANCE_DECISION,
                source_domain="advanced_boot",
                payload={
                    "decision_type": "ethics_approval",
                    "subsystem_id": subsystem_id,
                    "approved": approved,
                    "reasoning": reasoning,
                    "priority": priority,
                    "must_consult": list(must_consult),
                    "metadata": metadata,
                },
                priority=EventPriority.HIGH,
                requires_approval=False,
                can_be_vetoed=False,
                metadata={
                    "event_id": event_id,
                    "boot_profile": self._current_profile.value,
                    "timestamp": datetime.now().isoformat(),
                },
            )
            logger.debug("Ethics approval event emitted: %s", event_id)
        except Exception as e:
            logger.warning("Failed to emit ethics approval event: %s", e)

        # Create audit entry with event linkage
        self._audit_event(
            event_type="ethics_approval",
            action="request_approval",
            subsystem_id=subsystem_id,
            context={
                "priority": priority,
                "approved": approved,
                "reasoning": reasoning,
                "must_consult": list(must_consult),
                "event_id": event_id,
            },
            result=approved,
        )

        logger.info(f"Ethics approval for {subsystem_id}: {approved} " f"(reasoning: {reasoning}, event: {event_id})")

        return approved

    def mark_ethics_checkpoint_passed(self):
        """
        Mark that ethics subsystems have initialized successfully.

        Emits event for cross-domain visibility.
        """
        with self._lock:
            self._ethics_checkpoint_passed = True

        # Emit event through event spine
        try:
            event_spine = get_event_spine()
            event_spine.publish(
                category=EventCategory.GOVERNANCE_DECISION,
                source_domain="advanced_boot",
                payload={
                    "decision_type": "ethics_checkpoint",
                    "checkpoint": "ethics_initialization",
                    "status": "passed",
                },
                priority=EventPriority.CRITICAL,
                requires_approval=False,
                can_be_vetoed=False,
                metadata={
                    "boot_profile": self._current_profile.value,
                    "timestamp": datetime.now().isoformat(),
                },
            )
            logger.debug("Ethics checkpoint event emitted")
        except Exception as e:
            logger.warning("Failed to emit ethics checkpoint event: %s", e)

        self._audit_event(
            event_type="ethics_checkpoint",
            action="checkpoint_passed",
            context={"checkpoint": "ethics_initialization"},
            result="success",
        )

        logger.info("✅ Ethics checkpoint passed - proceeding with other subsystems")

    def activate_emergency_mode(self, reason: str = "manual_activation"):
        """
        Activate emergency-only mode.

        Emits critical event for system-wide coordination.

        Args:
            reason: Reason for emergency activation
        """
        with self._lock:
            if self._emergency_mode_active:
                logger.warning("Emergency mode already active")
                return

            self._emergency_mode_active = True
            self._emergency_activation_time = datetime.now()
            self._boot_stats["emergency_activations"] += 1

        # Emit critical event through event spine
        try:
            event_spine = get_event_spine()
            event_spine.publish(
                category=EventCategory.SYSTEM_HEALTH,
                source_domain="advanced_boot",
                payload={
                    "event_type": "emergency_mode_activated",
                    "reason": reason,
                    "critical_subsystems": self.EMERGENCY_CRITICAL_SUBSYSTEMS,
                    "activation_time": self._emergency_activation_time.isoformat(),
                },
                priority=EventPriority.CRITICAL,
                requires_approval=False,
                can_be_vetoed=False,
                metadata={
                    "boot_profile": self._current_profile.value,
                    "severity": "critical",
                },
            )
            logger.debug("Emergency mode activation event emitted")
        except Exception as e:
            logger.warning("Failed to emit emergency mode event: %s", e)

        self._audit_event(
            event_type="emergency_mode",
            action="activate",
            context={"reason": reason},
            result="activated",
        )

        logger.critical("🚨 EMERGENCY MODE ACTIVATED: %s", reason)
        logger.critical("   Only critical subsystems will be available")
        logger.critical("   Critical subsystems: %s", self.EMERGENCY_CRITICAL_SUBSYSTEMS)

    def deactivate_emergency_mode(self):
        """
        Deactivate emergency mode.

        Emits event for system-wide coordination.
        """
        with self._lock:
            if not self._emergency_mode_active:
                logger.warning("Emergency mode not active")
                return

            self._emergency_mode_active = False
            duration = None
            if self._emergency_activation_time:
                duration = (datetime.now() - self._emergency_activation_time).total_seconds()

        # Emit event through event spine
        try:
            event_spine = get_event_spine()
            event_spine.publish(
                category=EventCategory.SYSTEM_HEALTH,
                source_domain="advanced_boot",
                payload={
                    "event_type": "emergency_mode_deactivated",
                    "duration_seconds": duration,
                },
                priority=EventPriority.HIGH,
                requires_approval=False,
                can_be_vetoed=False,
                metadata={"boot_profile": self._current_profile.value},
            )
            logger.debug("Emergency mode deactivation event emitted")
        except Exception as e:
            logger.warning("Failed to emit emergency mode deactivation event: %s", e)

        self._audit_event(
            event_type="emergency_mode",
            action="deactivate",
            context={"duration_seconds": duration},
            result="deactivated",
        )

        logger.info("Emergency mode deactivated (was active for %ss)", duration)

    def is_emergency_mode(self) -> bool:
        """Check if emergency mode is active."""
        return self._emergency_mode_active

    def get_priority_override(self, subsystem_id: str) -> str | None:
        """
        Get priority override for a subsystem based on current profile.

        Args:
            subsystem_id: Subsystem identifier

        Returns:
            Priority override or None
        """
        if not self._current_profile_config:
            return None

        return self._current_profile_config.priority_overrides.get(subsystem_id)

    def _audit_event(
        self,
        event_type: str,
        action: str,
        subsystem_id: str | None = None,
        context: dict[str, Any] | None = None,
        result: Any | None = None,
        error: str | None = None,
        include_snapshot: bool = False,
    ):
        """
        Record an audit event.

        Args:
            event_type: Type of event
            action: Action performed
            subsystem_id: Optional subsystem ID
            context: Event context
            result: Event result
            error: Error message if failed
            include_snapshot: Whether to include state snapshot
        """
        if not self._audit_enabled:
            return

        event_id = f"{event_type}_{int(time.time() * 1000)}"

        snapshot = None
        if include_snapshot:
            snapshot = self._capture_state_snapshot()

        event = AuditEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            event_type=event_type,
            subsystem_id=subsystem_id,
            action=action,
            context=context or {},
            result=result,
            error=error,
            state_snapshot=snapshot,
        )

        with self._lock:
            self._audit_log.append(event)

        # Write to disk
        self._write_audit_event(event)

    def _write_audit_event(self, event: AuditEvent):
        """Write audit event to disk."""
        try:
            audit_file = self.audit_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"

            with open(audit_file, "a") as f:
                f.write(json.dumps(event.to_dict()) + "\n")

        except Exception as e:
            logger.error("Failed to write audit event: %s", e)

    def _capture_state_snapshot(self) -> dict[str, Any]:
        """Capture current system state snapshot."""
        return {
            "timestamp": datetime.now().isoformat(),
            "boot_profile": (self._current_profile.value if self._current_profile else None),
            "emergency_mode": self._emergency_mode_active,
            "ethics_checkpoint": self._ethics_checkpoint_passed,
            "boot_stats": self._boot_stats.copy(),
        }

    def save_state_snapshot(self, snapshot_id: str):
        """
        Save a named state snapshot.

        Args:
            snapshot_id: Identifier for the snapshot
        """
        snapshot = self._capture_state_snapshot()

        with self._lock:
            self._state_snapshots[snapshot_id] = snapshot

        self._audit_event(
            event_type="state_snapshot",
            action="save",
            context={"snapshot_id": snapshot_id},
            result="saved",
        )

        logger.info("State snapshot saved: %s", snapshot_id)

    def load_audit_log(self, date: str | None = None) -> list[AuditEvent]:
        """
        Load audit log from disk.

        Args:
            date: Optional date string (YYYYMMDD), defaults to today

        Returns:
            List of audit events
        """
        if date is None:
            date = datetime.now().strftime("%Y%m%d")

        audit_file = self.audit_dir / f"audit_{date}.jsonl"

        if not audit_file.exists():
            logger.warning("Audit log not found: %s", audit_file)
            return []

        events = []

        try:
            with open(audit_file) as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        events.append(AuditEvent.from_dict(data))

            logger.info("Loaded %s audit events from %s", len(events), audit_file)

        except Exception as e:
            logger.error("Failed to load audit log: %s", e)

        return events

    def replay_audit_log(
        self,
        events: list[AuditEvent] | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        event_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Replay audit log to reconstruct system state.

        Args:
            events: Events to replay (uses loaded log if None)
            start_time: Optional start time filter
            end_time: Optional end time filter
            event_types: Optional event type filter

        Returns:
            Reconstructed state and replay statistics
        """
        if events is None:
            events = self._audit_log

        # Filter events
        filtered_events = []
        for event in events:
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            if event_types and event.event_type not in event_types:
                continue

            filtered_events.append(event)

        logger.info("Replaying %s audit events...", len(filtered_events))

        # Reconstruct state
        reconstructed_state = {
            "profile_changes": [],
            "emergency_activations": [],
            "ethics_approvals": [],
            "state_snapshots": [],
            "timeline": [],
        }

        for event in filtered_events:
            # Add to timeline
            reconstructed_state["timeline"].append(
                {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "action": event.action,
                    "subsystem_id": event.subsystem_id,
                }
            )

            # Process by event type
            if event.event_type == "profile_changed":
                reconstructed_state["profile_changes"].append(
                    {
                        "timestamp": event.timestamp.isoformat(),
                        "profile": event.context.get("profile"),
                    }
                )

            elif event.event_type == "emergency_mode":
                reconstructed_state["emergency_activations"].append(
                    {
                        "timestamp": event.timestamp.isoformat(),
                        "action": event.action,
                        "reason": event.context.get("reason"),
                    }
                )

            elif event.event_type == "ethics_approval":
                reconstructed_state["ethics_approvals"].append(
                    {
                        "timestamp": event.timestamp.isoformat(),
                        "subsystem_id": event.subsystem_id,
                        "approved": event.result,
                    }
                )

            elif event.event_type == "state_snapshot":
                if event.state_snapshot:
                    reconstructed_state["state_snapshots"].append(event.state_snapshot)

        replay_stats = {
            "total_events": len(events),
            "filtered_events": len(filtered_events),
            "profile_changes": len(reconstructed_state["profile_changes"]),
            "emergency_activations": len(reconstructed_state["emergency_activations"]),
            "ethics_approvals": len(reconstructed_state["ethics_approvals"]),
            "state_snapshots": len(reconstructed_state["state_snapshots"]),
        }

        logger.info("Replay complete: %s", replay_stats)

        return {
            "reconstructed_state": reconstructed_state,
            "replay_stats": replay_stats,
        }

    def get_boot_stats(self) -> dict[str, Any]:
        """Get boot statistics."""
        with self._lock:
            return {
                **self._boot_stats,
                "current_profile": (self._current_profile.value if self._current_profile else None),
                "emergency_mode": self._emergency_mode_active,
                "ethics_checkpoint_passed": self._ethics_checkpoint_passed,
                "total_audit_events": len(self._audit_log),
            }

    def start_boot(self, profile: BootProfile | None = None):
        """
        Start boot sequence with optional profile.

        Args:
            profile: Boot profile to use (uses current if None)
        """
        if profile:
            self.set_boot_profile(profile)

        with self._lock:
            self._boot_stats["profile"] = self._current_profile.value if self._current_profile else None
            self._boot_stats["start_time"] = datetime.now().isoformat()

        self._audit_event(
            event_type="boot",
            action="start",
            context={"profile": (self._current_profile.value if self._current_profile else None)},
            result="started",
            include_snapshot=True,
        )

        logger.info("=" * 80)
        logger.info("BOOT SEQUENCE STARTED")
        if self._current_profile:
            logger.info("Profile: %s", self._current_profile.value)
            logger.info("Description: %s", self._current_profile_config.description)
        logger.info("=" * 80)

    def finish_boot(self):
        """Finish boot sequence."""
        with self._lock:
            self._boot_stats["end_time"] = datetime.now().isoformat()

        self._audit_event(
            event_type="boot",
            action="finish",
            context=self._boot_stats.copy(),
            result="finished",
            include_snapshot=True,
        )

        logger.info("=" * 80)
        logger.info("BOOT SEQUENCE COMPLETE")
        logger.info("Profile: %s", self._boot_stats["profile"])
        logger.info("Subsystems initialized: %s", self._boot_stats["subsystems_initialized"])
        logger.info("Subsystems skipped: %s", self._boot_stats["subsystems_skipped"])
        if self._boot_stats.get("ethics_approvals_required", 0) > 0:
            logger.info(
                "Ethics approvals: %s/%s",
                self._boot_stats["ethics_approvals_granted"],
                self._boot_stats["ethics_approvals_required"],
            )
        logger.info("=" * 80)

    def increment_subsystems_initialized(self):
        """Increment subsystems initialized counter."""
        with self._lock:
            self._boot_stats["subsystems_initialized"] += 1

    def increment_subsystems_skipped(self):
        """Increment subsystems skipped counter."""
        with self._lock:
            self._boot_stats["subsystems_skipped"] += 1


# Singleton instance
_advanced_boot_instance: AdvancedBootSystem | None = None
_advanced_boot_lock = threading.Lock()


def get_advanced_boot() -> AdvancedBootSystem:
    """
    Get the singleton AdvancedBootSystem instance.

    Returns:
        AdvancedBootSystem instance
    """
    global _advanced_boot_instance

    with _advanced_boot_lock:
        if _advanced_boot_instance is None:
            _advanced_boot_instance = AdvancedBootSystem()

        return _advanced_boot_instance
