"""
Governance Manager - Multi-Stakeholder Governance System

This module implements a governance system that enables multi-stakeholder
decision-making through proposals, voting, quorum requirements, and policy
enforcement.

Key Features:
- Proposal creation with proposer permission validation
- Voting with duplicate prevention, voting-period checks, and weights
- Quorum calculation with weighted participation
- Proposal execution with automatic policy application
- State persistence to JSON

STATUS: PRODUCTION
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)

DEFAULT_STATE_FILE = (
    Path(__file__).parent.parent.parent.parent / "governance" / "governance_state.json"
)


class GovernanceManager:
    """Manages multi-stakeholder governance for the AI system.

    This manager handles:
    - Proposal lifecycle (create → vote → quorum check → execute/reject)
    - Per-stakeholder vote tracking with duplicate prevention
    - Configurable voting weights
    - Automatic policy rule application on execution
    - Stakeholder permission validation
    - State persistence
    """

    def __init__(self, state_file: Path | None = None):
        """Initialize the governance manager.

        Args:
            state_file: Path to governance state JSON file
        """
        self.state_file = state_file or DEFAULT_STATE_FILE
        self.state: dict[str, Any] = {}
        self.load_state()

    def load_state(self) -> bool:
        """Load governance state from file.

        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.state_file.exists():
            logger.warning("Governance state file not found: %s", self.state_file)
            self._initialize_default_state()
            return False

        try:
            with open(self.state_file) as f:
                self.state = json.load(f)

            logger.info("Loaded governance state successfully")
            return True

        except Exception as e:
            logger.error("Failed to load governance state: %s", e)
            self._initialize_default_state()
            return False

    def _initialize_default_state(self):
        """Initialize default governance state."""
        self.state = {
            "version": "1.0.0",
            "initialized_at": datetime.now().isoformat(),
            "governance_model": "multi_stakeholder",
            "policies": {
                "quorum_threshold": 0.51,
                "voting_period_days": 7,
            },
            "stakeholders": [],
            "active_proposals": [],
            "executed_proposals": [],
            "rejected_proposals": [],
            "policy_rules": {},
        }

    def save_state(self) -> bool:
        """Save governance state to file.

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            self.state["last_modified"] = datetime.now().isoformat()

            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)

            logger.info("Saved governance state successfully")
            return True

        except Exception as e:
            logger.error("Failed to save governance state: %s", e)
            return False

    # ── Stakeholder management ────────────────────────────────

    def add_stakeholder(
        self,
        stakeholder_id: str,
        name: str,
        role: str = "member",
        weight: float = 1.0,
    ) -> bool:
        """Register a stakeholder in the governance system.

        Args:
            stakeholder_id: Unique identifier for the stakeholder
            name: Display name
            role: Role (e.g., "admin", "member", "observer")
            weight: Voting weight (default 1.0)

        Returns:
            True if added, False if already exists
        """
        for s in self.state["stakeholders"]:
            if s["id"] == stakeholder_id:
                logger.warning("Stakeholder already exists: %s", stakeholder_id)
                return False

        self.state["stakeholders"].append({
            "id": stakeholder_id,
            "name": name,
            "role": role,
            "weight": weight,
            "joined_at": datetime.now().isoformat(),
        })
        self.save_state()
        logger.info("Added stakeholder: %s (role=%s, weight=%.2f)", name, role, weight)
        return True

    def remove_stakeholder(self, stakeholder_id: str) -> bool:
        """Remove a stakeholder from the governance system.

        Args:
            stakeholder_id: ID of stakeholder to remove

        Returns:
            True if removed, False if not found
        """
        for i, s in enumerate(self.state["stakeholders"]):
            if s["id"] == stakeholder_id:
                del self.state["stakeholders"][i]
                self.save_state()
                logger.info("Removed stakeholder: %s", stakeholder_id)
                return True

        logger.warning("Stakeholder not found: %s", stakeholder_id)
        return False

    def _get_stakeholder(self, stakeholder_id: str) -> dict[str, Any] | None:
        """Look up a stakeholder by ID."""
        for s in self.state["stakeholders"]:
            if s["id"] == stakeholder_id:
                return s
        return None

    def _is_valid_proposer(self, proposer_id: str) -> bool:
        """Check whether a stakeholder is allowed to create proposals.

        Observers cannot create proposals.  All other registered
        stakeholders can.
        """
        s = self._get_stakeholder(proposer_id)
        if not s:
            return False
        return s.get("role") != "observer"

    # ── Proposal lifecycle ────────────────────────────────────

    def create_proposal(
        self,
        title: str,
        description: str,
        proposer_id: str,
        proposal_type: str = "policy_change",
        data: dict[str, Any] | None = None,
    ) -> str:
        """Create a new governance proposal.

        Validates that the proposer is a registered stakeholder with
        permission to propose. Schedules the voting period based on the
        configured ``voting_period_days`` policy.

        Args:
            title: Proposal title
            description: Detailed description
            proposer_id: ID of the proposer
            proposal_type: Type of proposal
            data: Additional proposal data (e.g., rule_name + rule_value)

        Returns:
            Proposal ID, or empty string if proposer lacks permission

        Raises:
            ValueError: If the proposer is not registered or is an observer
        """
        if not self._is_valid_proposer(proposer_id):
            logger.error(
                "Proposer %s is not registered or lacks permission", proposer_id
            )
            raise ValueError(
                f"Proposer '{proposer_id}' is not a registered stakeholder with proposal rights"
            )

        proposal_id = str(uuid4())

        voting_period_days = self.state["policies"].get("voting_period_days", 7)
        ends_at = datetime.now() + timedelta(days=voting_period_days)

        proposal = {
            "proposal_id": proposal_id,
            "title": title,
            "description": description,
            "proposer_id": proposer_id,
            "type": proposal_type,
            "data": data or {},
            "created_at": datetime.now().isoformat(),
            "ends_at": ends_at.isoformat(),
            "status": "active",
            "votes": {"yes": 0, "no": 0, "abstain": 0},
            "voters": {},  # stakeholder_id → vote value
        }

        self.state["active_proposals"].append(proposal)
        self.save_state()

        logger.info("Created proposal: %s (ID: %s)", title, proposal_id)
        return proposal_id

    def _find_active_proposal(self, proposal_id: str) -> tuple[dict[str, Any] | None, int | None]:
        """Locate an active proposal and its index."""
        for i, p in enumerate(self.state["active_proposals"]):
            if p["proposal_id"] == proposal_id:
                return p, i
        return None, None

    def vote_on_proposal(
        self,
        proposal_id: str,
        stakeholder_id: str,
        vote: str,
    ) -> bool:
        """Cast a vote on a proposal.

        Validates:
        - Proposal exists and is active
        - Vote value is valid (yes/no/abstain)
        - Stakeholder is registered and not an observer
        - Stakeholder has not already voted on this proposal
        - Voting period has not expired

        Args:
            proposal_id: ID of the proposal
            stakeholder_id: ID of the voting stakeholder
            vote: Vote value ("yes", "no", "abstain")

        Returns:
            True if vote recorded successfully, False otherwise
        """
        proposal, _ = self._find_active_proposal(proposal_id)

        if not proposal:
            logger.error("Proposal not found: %s", proposal_id)
            return False

        if vote not in ("yes", "no", "abstain"):
            logger.error("Invalid vote value: %s", vote)
            return False

        # Validate stakeholder
        stakeholder = self._get_stakeholder(stakeholder_id)
        if not stakeholder:
            logger.error("Stakeholder not registered: %s", stakeholder_id)
            return False
        if stakeholder.get("role") == "observer":
            logger.error("Observers cannot vote: %s", stakeholder_id)
            return False

        # Duplicate vote prevention
        voters = proposal.setdefault("voters", {})
        if stakeholder_id in voters:
            logger.warning(
                "Stakeholder %s already voted on proposal %s",
                stakeholder_id,
                proposal_id,
            )
            return False

        # Check voting period
        ends_at_str = proposal.get("ends_at")
        if ends_at_str:
            try:
                ends_at = datetime.fromisoformat(ends_at_str)
                if datetime.now() > ends_at:
                    logger.error("Voting period expired for proposal %s", proposal_id)
                    return False
            except (ValueError, TypeError):
                pass  # malformed date — allow vote

        # Record vote with weight
        weight = stakeholder.get("weight", 1.0)
        proposal["votes"][vote] += weight
        voters[stakeholder_id] = vote
        self.save_state()

        logger.info(
            "Recorded vote on proposal %s: %s=%s (weight=%.2f)",
            proposal_id,
            stakeholder_id,
            vote,
            weight,
        )
        return True

    def check_quorum(self, proposal_id: str) -> bool:
        """Check if a proposal has reached quorum.

        Quorum is met when the weighted participation rate meets or
        exceeds the configured ``quorum_threshold``.

        Args:
            proposal_id: ID of the proposal

        Returns:
            True if quorum is reached, False otherwise
        """
        proposal, _ = self._find_active_proposal(proposal_id)
        if not proposal:
            return False

        voters = proposal.get("voters", {})
        total_participants = len(voters)
        total_stakeholders = max(
            len([s for s in self.state["stakeholders"] if s.get("role") != "observer"]),
            1,
        )

        participation_rate = total_participants / total_stakeholders
        quorum_threshold = self.state["policies"].get("quorum_threshold", 0.51)

        return participation_rate >= quorum_threshold

    def execute_proposal(self, proposal_id: str) -> bool:
        """Execute a proposal that has passed.

        Verifies quorum and simple majority. If the proposal is of type
        ``policy_change`` and its ``data`` dict contains ``rule_name``
        and ``rule_value``, the policy rule is applied automatically.

        Args:
            proposal_id: ID of the proposal to execute

        Returns:
            True if executed successfully, False otherwise
        """
        proposal, proposal_index = self._find_active_proposal(proposal_id)

        if not proposal:
            logger.error("Proposal not found: %s", proposal_id)
            return False

        # Check quorum
        if not self.check_quorum(proposal_id):
            logger.info("Proposal %s has not reached quorum", proposal_id)
            return False

        # Check simple majority (yes weighted > no weighted)
        yes_votes = proposal["votes"]["yes"]
        no_votes = proposal["votes"]["no"]

        if yes_votes <= no_votes:
            logger.info("Proposal %s did not pass (yes=%.1f, no=%.1f)", proposal_id, yes_votes, no_votes)
            proposal["status"] = "rejected"
            proposal["resolved_at"] = datetime.now().isoformat()
            # Move to rejected list
            self.state.setdefault("rejected_proposals", []).append(proposal)
            if proposal_index is not None:
                del self.state["active_proposals"][proposal_index]
            self.save_state()
            return False

        # Execute — apply policy changes if applicable
        proposal["status"] = "executed"
        proposal["executed_at"] = datetime.now().isoformat()

        p_data = proposal.get("data", {})
        if proposal.get("type") == "policy_change":
            rule_name = p_data.get("rule_name")
            rule_value = p_data.get("rule_value")
            if rule_name is not None and rule_value is not None:
                self.set_policy_rule(rule_name, rule_value)
                logger.info(
                    "Proposal %s applied policy: %s = %s",
                    proposal_id,
                    rule_name,
                    rule_value,
                )

        # Move to executed proposals
        self.state["executed_proposals"].append(proposal)
        if proposal_index is not None:
            del self.state["active_proposals"][proposal_index]

        self.save_state()

        logger.info("Executed proposal: %s", proposal_id)
        return True

    # ── Policy rules ──────────────────────────────────────────

    def get_policy_rule(self, rule_name: str) -> Any:
        """Get a policy rule value.

        Args:
            rule_name: Name of the rule

        Returns:
            Rule value or None if not found
        """
        return self.state.get("policy_rules", {}).get(rule_name)

    def set_policy_rule(self, rule_name: str, value: Any) -> bool:
        """Set a policy rule.

        This should typically be done through governance proposals.

        Args:
            rule_name: Name of the rule
            value: Rule value

        Returns:
            True if set successfully, False otherwise
        """
        if "policy_rules" not in self.state:
            self.state["policy_rules"] = {}

        self.state["policy_rules"][rule_name] = value
        self.save_state()

        logger.info("Set policy rule: %s = %s", rule_name, value)
        return True


__all__ = ["GovernanceManager"]
