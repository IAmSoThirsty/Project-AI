"""
Cerberus Lockdown Controller
=============================

Manages progressive system lockdown in response to security breaches.
Implements 25 lockable sections with deterministic stage mapping (1-25).
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class LockdownController:
    """
    Manages progressive system lockdown for Cerberus Defense.

    Features:
    - 25 lockable system sections with staged lockdown (1-25)
    - Deterministic stage computation based on risk score and bypass depth
    - Idempotent lockdown operations
    - Track locked sections and current stage
    - Query interface for lockdown status
    - Persistent state across restarts
    """

    # 25 lockable system sections
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

    def __init__(self, data_dir: str = "data"):
        """
        Initialize LockdownController.

        Args:
            data_dir: Base data directory for state persistence
        """
        self.data_dir = Path(data_dir)
        self.lockdown_dir = self.data_dir / "cerberus" / "lockdown"

        # Lockdown state
        self.current_stage = 0  # 0-25
        self.locked_sections: set[str] = set()
        self.lockdown_history: list[dict[str, Any]] = []

        # Initialize directories
        self.lockdown_dir.mkdir(parents=True, exist_ok=True)

        # Load existing state
        self._load_state()

    def _load_state(self) -> None:
        """Load lockdown state from disk."""
        state_file = self.lockdown_dir / "lockdown_state.json"

        if not state_file.exists():
            logger.debug("No existing lockdown state found")
            return

        try:
            with open(state_file, encoding="utf-8") as f:
                state = json.load(f)

            self.current_stage = state.get("current_stage", 0)
            self.locked_sections = set(state.get("locked_sections", []))
            self.lockdown_history = state.get("lockdown_history", [])

            logger.info(
                f"Loaded lockdown state: stage {self.current_stage}, "
                f"{len(self.locked_sections)} sections locked"
            )

        except Exception as e:
            logger.error(f"Failed to load lockdown state: {e}")

    def _save_state(self) -> None:
        """Persist lockdown state to disk."""
        state_file = self.lockdown_dir / "lockdown_state.json"

        state = {
            "current_stage": self.current_stage,
            "locked_sections": list(self.locked_sections),
            "lockdown_history": self.lockdown_history,
            "last_updated": datetime.now().isoformat(),
        }

        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save lockdown state: {e}")

    def compute_lockdown_stage(
        self, risk_score: float, bypass_depth: int
    ) -> int:
        """
        Compute deterministic lockdown stage based on risk and bypass depth.

        Formula: stage = min(25, ceil(risk_score * 10) + bypass_depth)

        Args:
            risk_score: Risk score from 0.0 to 1.0
            bypass_depth: Number of security layers bypassed

        Returns:
            Lockdown stage from 0 to 25
        """
        import math

        # Validate inputs
        risk_score = max(0.0, min(1.0, risk_score))
        bypass_depth = max(0, bypass_depth)

        # Compute stage
        stage = math.ceil(risk_score * 10) + bypass_depth
        stage = min(25, max(0, stage))

        logger.debug(
            f"Computed lockdown stage: risk={risk_score:.2f}, "
            f"depth={bypass_depth} → stage {stage}"
        )

        return stage

    def apply_lockdown(self, stage: int, reason: str = "security_breach") -> dict[str, Any]:
        """
        Apply lockdown to specified stage (idempotent).

        Locks sections 0 through stage-1 (e.g., stage 5 locks sections 0-4).

        Args:
            stage: Target lockdown stage (0-25)
            reason: Reason for lockdown

        Returns:
            Dictionary with lockdown results
        """
        # Validate stage
        stage = max(0, min(25, stage))

        # Check if already at or above this stage
        if stage <= self.current_stage:
            logger.debug(
                f"Already at or above stage {stage} (current: {self.current_stage})"
            )
            return {
                "success": True,
                "previous_stage": self.current_stage,
                "new_stage": self.current_stage,
                "newly_locked": [],
                "total_locked": len(self.locked_sections),
                "action": "no_change",
            }

        # Determine sections to lock
        sections_to_lock = self.LOCKABLE_SECTIONS[:stage]
        newly_locked = [s for s in sections_to_lock if s not in self.locked_sections]

        # Lock sections
        previous_stage = self.current_stage
        self.locked_sections.update(sections_to_lock)
        self.current_stage = stage

        # Log lockdown event
        lockdown_event = {
            "timestamp": datetime.now().isoformat(),
            "previous_stage": previous_stage,
            "new_stage": stage,
            "reason": reason,
            "newly_locked": newly_locked,
            "total_locked": len(self.locked_sections),
        }
        self.lockdown_history.append(lockdown_event)

        # Persist state
        self._save_state()

        # Log event
        logger.warning(
            f"🔒 LOCKDOWN ESCALATION: Stage {previous_stage} → {stage} "
            f"(locked {len(newly_locked)} new sections: {', '.join(newly_locked[:3])}{'...' if len(newly_locked) > 3 else ''})"
        )

        return {
            "success": True,
            "previous_stage": previous_stage,
            "new_stage": stage,
            "newly_locked": newly_locked,
            "total_locked": len(self.locked_sections),
            "action": "escalated",
        }

    def is_section_locked(self, section: str) -> bool:
        """
        Check if a specific section is locked.

        Args:
            section: Section name to check

        Returns:
            True if section is locked, False otherwise
        """
        return section in self.locked_sections

    def get_lockdown_status(self) -> dict[str, Any]:
        """
        Get comprehensive lockdown status.

        Returns:
            Dictionary with lockdown status information
        """
        total_sections = len(self.LOCKABLE_SECTIONS)
        locked_count = len(self.locked_sections)
        remaining_count = total_sections - locked_count

        # Compute severity level
        if self.current_stage >= 20:
            severity = "critical"
        elif self.current_stage >= 15:
            severity = "high"
        elif self.current_stage >= 10:
            severity = "elevated"
        elif self.current_stage >= 5:
            severity = "moderate"
        else:
            severity = "low"

        return {
            "current_stage": self.current_stage,
            "max_stage": 25,
            "severity": severity,
            "locked_sections": list(self.locked_sections),
            "locked_count": locked_count,
            "remaining_count": remaining_count,
            "total_sections": total_sections,
            "lockdown_percentage": (locked_count / total_sections * 100) if total_sections > 0 else 0,
            "recent_events": self.lockdown_history[-10:],
        }

    def get_available_sections(self) -> list[str]:
        """
        Get list of sections that are not yet locked.

        Returns:
            List of unlocked section names
        """
        return [s for s in self.LOCKABLE_SECTIONS if s not in self.locked_sections]

    def release_lockdown(self, stage: int | None = None) -> dict[str, Any]:
        """
        Release lockdown to a lower stage or completely.

        Args:
            stage: Target stage to release to (None = release all)

        Returns:
            Dictionary with release results
        """
        previous_stage = self.current_stage

        if stage is None:
            # Release all lockdowns
            self.current_stage = 0
            released_sections = list(self.locked_sections)
            self.locked_sections.clear()

        else:
            # Release to specified stage
            stage = max(0, min(25, stage))

            if stage >= self.current_stage:
                logger.debug(f"Cannot release to higher stage {stage}")
                return {
                    "success": False,
                    "reason": "target_stage_higher",
                    "current_stage": self.current_stage,
                }

            # Unlock sections beyond target stage
            sections_to_keep = self.LOCKABLE_SECTIONS[:stage]
            released_sections = [s for s in self.locked_sections if s not in sections_to_keep]

            self.locked_sections = set(sections_to_keep)
            self.current_stage = stage

        # Log release event
        release_event = {
            "timestamp": datetime.now().isoformat(),
            "previous_stage": previous_stage,
            "new_stage": self.current_stage,
            "reason": "manual_release",
            "released_sections": released_sections,
            "total_locked": len(self.locked_sections),
        }
        self.lockdown_history.append(release_event)

        # Persist state
        self._save_state()

        logger.info(
            f"🔓 LOCKDOWN RELEASE: Stage {previous_stage} → {self.current_stage} "
            f"(released {len(released_sections)} sections)"
        )

        return {
            "success": True,
            "previous_stage": previous_stage,
            "new_stage": self.current_stage,
            "released_sections": released_sections,
            "total_locked": len(self.locked_sections),
        }

    def get_lockdown_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """
        Get lockdown history.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of lockdown events
        """
        return self.lockdown_history[-limit:]
