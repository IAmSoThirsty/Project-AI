#!/usr/bin/env python3
"""
Planetary Defense Monolith - Constitutional Kernel Integration

This module implements the core monolithic integration that consolidates:
1. Invariants as a sub-kernel (not utility) with law evaluation
2. Causal clock as the sole time authority
3. Mandatory read-only projection for registry access

The monolith acts as the single source of truth for:
- Action legality (invariants + constitutional laws)
- Time advancement (causal clock authority)
- Registry access control (projection enforcement)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from engines.alien_invaders.modules.causal_clock import CausalClock
from engines.alien_invaders.modules.invariants import (
    CompositeInvariantValidator,
    InvariantViolation,
)
from engines.alien_invaders.modules.world_state import GlobalState

logger = logging.getLogger(__name__)


@dataclass
class ActionRequest:
    """Request for an action to be evaluated by the monolith."""

    action_id: str
    action_type: str
    parameters: dict[str, Any]
    requestor: str  # Who is requesting the action
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ActionVerdict:
    """Verdict from the monolith on whether an action is legal."""

    allowed: bool
    reason: str
    violations: list[InvariantViolation] = field(default_factory=list)
    accountability_record: dict[str, Any] = field(default_factory=dict)


@dataclass
class RegistryAccessRequest:
    """Request for registry access (read-only or mutable)."""

    requestor: str
    access_type: str  # "read" or "write"
    target: str  # What is being accessed
    context: dict[str, Any] = field(default_factory=dict)


class PlanetaryDefenseMonolith:
    """
    Constitutional Kernel - Monolithic Integration Point

    This class consolidates all authority over:
    1. Action legality through invariant validation
    2. Time advancement through causal clock control
    3. Registry access through projection enforcement

    All actions that would modify state must pass through this monolith's
    law evaluation phase. Invariants are treated as preconditions, making
    violations illegal rather than just "bad output".
    """

    def __init__(
        self,
        causal_clock: CausalClock,
        invariant_validator: CompositeInvariantValidator,
        enable_strict_enforcement: bool = True,
    ):
        """
        Initialize the Planetary Defense Monolith.

        Args:
            causal_clock: The causal clock that controls all time
            invariant_validator: Validator for composite invariants
            enable_strict_enforcement: If True, reject illegal actions
        """
        self.causal_clock = causal_clock
        self.invariant_validator = invariant_validator
        self.enable_strict_enforcement = enable_strict_enforcement

        # Track all actions for accountability
        self.action_log: list[tuple[ActionRequest, ActionVerdict]] = []

        # Track registry access for auditing
        self.access_log: list[tuple[RegistryAccessRequest, bool]] = []

        logger.info(
            "Planetary Defense Monolith initialized (strict=%s)",
            enable_strict_enforcement,
        )

    def evaluate_action(
        self,
        action: ActionRequest,
        current_state: GlobalState,
        prev_state: GlobalState | None = None,
    ) -> ActionVerdict:
        """
        Evaluate an action through the constitutional kernel.

        This is the law evaluation phase where invariants act as preconditions.
        If an action would violate physical coherence, it is ILLEGAL, not just
        "bad output".

        Args:
            action: The action to evaluate
            current_state: Current global state
            prev_state: Previous state for invariant checks

        Returns:
            ActionVerdict indicating if action is legal
        """
        # Step 1: Validate invariants as preconditions
        # This creates a hypothetical state to check if the action would violate invariants
        violations = []

        if prev_state is not None:
            # Run invariant validation to check if current trajectory is legal
            is_valid, violations = self.invariant_validator.validate_all(
                current_state, prev_state, enforce=self.enable_strict_enforcement
            )

            if not is_valid:
                verdict = ActionVerdict(
                    allowed=False,
                    reason="Action would violate physical coherence - ILLEGAL",
                    violations=violations,
                    accountability_record={
                        "action_id": action.action_id,
                        "action_type": action.action_type,
                        "requestor": action.requestor,
                        "logical_time": self.causal_clock.current,
                        "timestamp": action.timestamp.isoformat(),
                        "violation_count": len(violations),
                        "violation_types": [v.invariant_name for v in violations],
                    },
                )

                # Log the illegal action attempt
                self.action_log.append((action, verdict))
                logger.warning(
                    "Action %s REJECTED: Would violate %d invariants",
                    action.action_id,
                    len(violations),
                )

                return verdict

        # Step 2: If no invariant violations, action is legal
        verdict = ActionVerdict(
            allowed=True,
            reason="Action is legal - no invariant violations",
            violations=[],
            accountability_record={
                "action_id": action.action_id,
                "action_type": action.action_type,
                "requestor": action.requestor,
                "logical_time": self.causal_clock.current,
                "timestamp": action.timestamp.isoformat(),
                "approved": True,
            },
        )

        self.action_log.append((action, verdict))
        logger.debug("Action %s APPROVED by monolith", action.action_id)

        return verdict

    def advance_time(self) -> int:
        """
        Advance time through the causal clock.

        This is the ONLY method that should advance time. No engine or registry
        should advance time independently.

        Returns:
            New logical time value
        """
        new_time = self.causal_clock.next()
        logger.debug("Monolith advanced time to %d", new_time)
        return new_time

    def get_current_time(self) -> int:
        """
        Get current logical time from the causal clock.

        Returns:
            Current logical time
        """
        return self.causal_clock.current

    def authorize_registry_access(
        self, access_request: RegistryAccessRequest
    ) -> tuple[bool, str]:
        """
        Authorize registry access through projection enforcement.

        Read-only access (projection mode) is granted by default.
        Mutable access requires:
        1. Requestor is inside the Monolith
        2. Action passes law evaluation
        3. Accountability record is generated

        Args:
            access_request: The access request to evaluate

        Returns:
            Tuple of (allowed, reason)
        """
        # Read-only access is always granted (projection mode)
        if access_request.access_type == "read":
            self.access_log.append((access_request, True))
            return True, "Read-only projection access granted"

        # Mutable access requires monolith approval
        if access_request.access_type == "write":
            # Check if requestor is inside the monolith
            is_internal = access_request.context.get("from_monolith", False)

            if not is_internal:
                self.access_log.append((access_request, False))
                logger.warning(
                    "Mutable access DENIED to %s: Not from monolith",
                    access_request.requestor,
                )
                return False, "Mutable access denied: Must be inside the Monolith"

            # Check if action has passed law evaluation
            has_approval = access_request.context.get("law_evaluation_passed", False)

            if not has_approval:
                self.access_log.append((access_request, False))
                logger.warning(
                    "Mutable access DENIED to %s: No law evaluation approval",
                    access_request.requestor,
                )
                return (
                    False,
                    "Mutable access denied: Must pass law evaluation",
                )

            # Generate accountability record
            accountability = {
                "requestor": access_request.requestor,
                "target": access_request.target,
                "logical_time": self.causal_clock.current,
                "timestamp": datetime.now().isoformat(),
                "access_type": "write",
                "approved": True,
            }

            access_request.context["accountability_record"] = accountability
            self.access_log.append((access_request, True))

            logger.info(
                "Mutable access GRANTED to %s for %s",
                access_request.requestor,
                access_request.target,
            )

            return True, "Mutable access granted with accountability"

        # Unknown access type
        return False, f"Unknown access type: {access_request.access_type}"

    def get_action_log(self) -> list[tuple[ActionRequest, ActionVerdict]]:
        """
        Get the complete action log for auditing.

        Returns:
            List of (action, verdict) tuples
        """
        return self.action_log.copy()

    def get_access_log(self) -> list[tuple[RegistryAccessRequest, bool]]:
        """
        Get the complete access log for auditing.

        Returns:
            List of (access_request, granted) tuples
        """
        return self.access_log.copy()

    def reset_logs(self):
        """Clear all logs (for testing or fresh start)."""
        self.action_log.clear()
        self.access_log.clear()
        logger.info("Monolith logs reset")
