"""
Accountability System
=====================

Human accountability interfaces for build overrides, waivers, and digital signatures.
Ensures all policy overrides are traceable to responsible humans.
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AccountabilityRecord:
    """Record of human accountability action."""

    def __init__(
        self,
        record_id: str,
        action_type: str,
        actor: str,
        justification: str,
        signature: str,
        metadata: dict[str, Any]
    ):
        """
        Initialize accountability record.

        Args:
            record_id: Unique record identifier
            action_type: Type of action (override, waiver, approval)
            actor: Human actor identifier
            justification: Required justification text
            signature: Digital signature
            metadata: Additional metadata
        """
        self.record_id = record_id
        self.action_type = action_type
        self.actor = actor
        self.justification = justification
        self.signature = signature
        self.metadata = metadata
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "record_id": self.record_id,
            "action_type": self.action_type,
            "actor": self.actor,
            "justification": self.justification,
            "signature": self.signature,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }

    def verify_signature(self, expected_actor: str) -> bool:
        """
        Verify digital signature.

        Args:
            expected_actor: Expected actor identifier

        Returns:
            True if signature valid
        """
        # Recompute signature
        content = f"{self.action_type}:{self.actor}:{self.justification}:{self.timestamp}"
        computed_sig = hashlib.sha256(content.encode()).hexdigest()

        return (
            self.signature == computed_sig and
            self.actor == expected_actor
        )


class AccountabilitySystem:
    """
    Human accountability system for policy overrides and waivers.
    Ensures all deviations from policy are traceable and justified.
    """

    def __init__(self, records_dir: Path | None = None):
        """
        Initialize accountability system.

        Args:
            records_dir: Directory for accountability records
        """
        self.records_dir = records_dir or Path("data/accountability")
        self.records_dir.mkdir(parents=True, exist_ok=True)
        self.records: dict[str, AccountabilityRecord] = {}
        self.pending_approvals: dict[str, dict[str, Any]] = {}
        self._load_records()
        logger.info("Accountability system initialized: %s", self.records_dir)

    def request_policy_override(
        self,
        actor: str,
        policy_id: str,
        reason: str,
        affected_actions: list[str],
        duration_hours: int = 24
    ) -> str:
        """
        Request a policy override with justification.

        Args:
            actor: Human requesting override
            policy_id: Policy to override
            reason: Justification for override
            affected_actions: Actions affected by override
            duration_hours: Duration of override

        Returns:
            Override request ID
        """
        try:
            request_id = self._generate_request_id(actor, policy_id)

            # Create signature
            content = f"override:{actor}:{reason}:{datetime.utcnow().isoformat()}"
            signature = hashlib.sha256(content.encode()).hexdigest()

            # Create accountability record
            record = AccountabilityRecord(
                record_id=request_id,
                action_type="policy_override",
                actor=actor,
                justification=reason,
                signature=signature,
                metadata={
                    "policy_id": policy_id,
                    "affected_actions": affected_actions,
                    "duration_hours": duration_hours,
                    "status": "pending_approval",
                }
            )

            self.records[request_id] = record
            self.pending_approvals[request_id] = {
                "record": record,
                "requires_approvals": 1,  # Could be configurable
                "approvals": [],
            }

            self._persist_record(record)

            logger.info("Policy override requested: %s by %s", request_id, actor)
            return request_id

        except Exception as e:
            logger.error("Error requesting policy override: %s", e, exc_info=True)
            raise

    def request_waiver(
        self,
        actor: str,
        requirement: str,
        reason: str,
        scope: dict[str, Any]
    ) -> str:
        """
        Request a requirement waiver.

        Args:
            actor: Human requesting waiver
            requirement: Requirement to waive
            reason: Justification
            scope: Scope of waiver

        Returns:
            Waiver request ID
        """
        try:
            request_id = self._generate_request_id(actor, requirement)

            content = f"waiver:{actor}:{reason}:{datetime.utcnow().isoformat()}"
            signature = hashlib.sha256(content.encode()).hexdigest()

            record = AccountabilityRecord(
                record_id=request_id,
                action_type="requirement_waiver",
                actor=actor,
                justification=reason,
                signature=signature,
                metadata={
                    "requirement": requirement,
                    "scope": scope,
                    "status": "pending_approval",
                }
            )

            self.records[request_id] = record
            self.pending_approvals[request_id] = {
                "record": record,
                "requires_approvals": 2,  # Waivers require more approvals
                "approvals": [],
            }

            self._persist_record(record)

            logger.info("Waiver requested: %s by %s", request_id, actor)
            return request_id

        except Exception as e:
            logger.error("Error requesting waiver: %s", e, exc_info=True)
            raise

    def approve_request(
        self,
        request_id: str,
        approver: str,
        comments: str | None = None
    ) -> bool:
        """
        Approve a pending request.

        Args:
            request_id: Request to approve
            approver: Human approver
            comments: Optional approval comments

        Returns:
            True if request fully approved
        """
        try:
            if request_id not in self.pending_approvals:
                logger.warning("Request not found: %s", request_id)
                return False

            approval_data = self.pending_approvals[request_id]

            # Add approval
            approval = {
                "approver": approver,
                "timestamp": datetime.utcnow().isoformat(),
                "comments": comments,
            }
            approval_data["approvals"].append(approval)

            # Check if fully approved
            if len(approval_data["approvals"]) >= approval_data["requires_approvals"]:
                record = approval_data["record"]
                record.metadata["status"] = "approved"
                record.metadata["approvals"] = approval_data["approvals"]

                del self.pending_approvals[request_id]
                self._persist_record(record)

                logger.info("Request approved: %s", request_id)
                return True

            logger.info(
                f"Approval added: {request_id}, "
                f"{len(approval_data['approvals'])}/{approval_data['requires_approvals']}"
            )
            return False

        except Exception as e:
            logger.error("Error approving request: %s", e, exc_info=True)
            return False

    def deny_request(
        self,
        request_id: str,
        denier: str,
        reason: str
    ) -> None:
        """
        Deny a pending request.

        Args:
            request_id: Request to deny
            denier: Human denying request
            reason: Reason for denial
        """
        try:
            if request_id not in self.pending_approvals:
                logger.warning("Request not found: %s", request_id)
                return

            approval_data = self.pending_approvals[request_id]
            record = approval_data["record"]

            record.metadata["status"] = "denied"
            record.metadata["denied_by"] = denier
            record.metadata["denial_reason"] = reason
            record.metadata["denial_timestamp"] = datetime.utcnow().isoformat()

            del self.pending_approvals[request_id]
            self._persist_record(record)

            logger.info("Request denied: %s by %s", request_id, denier)

        except Exception as e:
            logger.error("Error denying request: %s", e, exc_info=True)

    def sign_action(
        self,
        actor: str,
        action_type: str,
        action_data: dict[str, Any],
        justification: str
    ) -> str:
        """
        Create signed record of action.

        Args:
            actor: Human actor
            action_type: Type of action
            action_data: Action data
            justification: Justification

        Returns:
            Record ID
        """
        try:
            record_id = self._generate_request_id(actor, action_type)

            content = f"{action_type}:{actor}:{justification}:{datetime.utcnow().isoformat()}"
            signature = hashlib.sha256(content.encode()).hexdigest()

            record = AccountabilityRecord(
                record_id=record_id,
                action_type=action_type,
                actor=actor,
                justification=justification,
                signature=signature,
                metadata={
                    "action_data": action_data,
                    "status": "signed",
                }
            )

            self.records[record_id] = record
            self._persist_record(record)

            logger.info("Action signed: %s by %s", record_id, actor)
            return record_id

        except Exception as e:
            logger.error("Error signing action: %s", e, exc_info=True)
            raise

    def get_record(self, record_id: str) -> AccountabilityRecord | None:
        """
        Get accountability record.

        Args:
            record_id: Record identifier

        Returns:
            Record or None
        """
        return self.records.get(record_id)

    def get_records_by_actor(self, actor: str) -> list[AccountabilityRecord]:
        """
        Get all records for actor.

        Args:
            actor: Actor identifier

        Returns:
            List of records
        """
        return [
            record for record in self.records.values()
            if record.actor == actor
        ]

    def get_pending_approvals(self) -> list[dict[str, Any]]:
        """
        Get all pending approval requests.

        Returns:
            List of pending requests
        """
        return [
            {
                "request_id": request_id,
                "record": data["record"].to_dict(),
                "approvals_needed": data["requires_approvals"],
                "approvals_received": len(data["approvals"]),
            }
            for request_id, data in self.pending_approvals.items()
        ]

    def generate_accountability_report(self) -> dict[str, Any]:
        """
        Generate accountability report.

        Returns:
            Report dictionary
        """
        try:
            by_actor = {}
            by_type = {}

            for record in self.records.values():
                # By actor
                if record.actor not in by_actor:
                    by_actor[record.actor] = []
                by_actor[record.actor].append(record.action_type)

                # By type
                by_type[record.action_type] = by_type.get(record.action_type, 0) + 1

            return {
                "total_records": len(self.records),
                "pending_approvals": len(self.pending_approvals),
                "by_actor": {
                    actor: {
                        "action_count": len(actions),
                        "action_types": list(set(actions)),
                    }
                    for actor, actions in by_actor.items()
                },
                "by_type": by_type,
            }

        except Exception as e:
            logger.error("Error generating report: %s", e, exc_info=True)
            return {"error": str(e)}

    def _generate_request_id(self, actor: str, identifier: str) -> str:
        """Generate unique request ID."""
        content = f"{actor}:{identifier}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _persist_record(self, record: AccountabilityRecord) -> None:
        """Persist record to disk."""
        try:
            filepath = self.records_dir / f"{record.record_id}.json"
            with open(filepath, "w") as f:
                json.dump(record.to_dict(), f, indent=2)
        except Exception as e:
            logger.error("Error persisting record: %s", e, exc_info=True)

    def _load_records(self) -> None:
        """Load records from disk."""
        try:
            for filepath in self.records_dir.glob("*.json"):
                with open(filepath) as f:
                    data = json.load(f)

                record = AccountabilityRecord(
                    record_id=data["record_id"],
                    action_type=data["action_type"],
                    actor=data["actor"],
                    justification=data["justification"],
                    signature=data["signature"],
                    metadata=data["metadata"]
                )

                self.records[record.record_id] = record

                # Restore pending approvals
                if data["metadata"].get("status") == "pending_approval":
                    self.pending_approvals[record.record_id] = {
                        "record": record,
                        "requires_approvals": data["metadata"].get("requires_approvals", 1),
                        "approvals": data["metadata"].get("approvals", []),
                    }

            logger.info("Loaded %s accountability records", len(self.records))
        except Exception as e:
            logger.error("Error loading records: %s", e, exc_info=True)


__all__ = ["AccountabilitySystem", "AccountabilityRecord"]
