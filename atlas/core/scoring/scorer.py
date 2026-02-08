"""
Scoring Module for PROJECT ATLAS

Calculates entity scores using driver values, applies penalties from configuration,
handles penalty stacking and expiration, implements recovery mechanisms.

Production-grade with full error handling, logging, and audit trail integration.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from atlas.audit.trail import AuditCategory, AuditLevel, AuditTrail, get_audit_trail
from atlas.config.loader import ConfigLoader, get_config_loader
from atlas.schemas.validator import SchemaValidator, get_schema_validator

logger = logging.getLogger(__name__)


class ScoringError(Exception):
    """Raised when scoring calculation fails."""
    pass


class PenaltyError(Exception):
    """Raised when penalty operations fail."""
    pass


class Scorer:
    """
    Production-grade scoring engine for PROJECT ATLAS.
    
    Calculates entity scores, applies penalties, handles stacking and expiration,
    implements recovery mechanisms with full audit trail.
    """

    def __init__(self,
                 config_loader: ConfigLoader | None = None,
                 schema_validator: SchemaValidator | None = None,
                 audit_trail: AuditTrail | None = None):
        """
        Initialize scorer.
        
        Args:
            config_loader: Configuration loader (uses global if None)
            schema_validator: Schema validator (uses global if None)
            audit_trail: Audit trail (uses global if None)
        """
        self.config = config_loader or get_config_loader()
        self.validator = schema_validator or get_schema_validator()
        self.audit = audit_trail or get_audit_trail()

        # Load penalty configurations
        self.penalties_config = self.config.get("penalties")
        self.veracity_penalties = self.penalties_config.get("veracity_penalties", {})
        self.behavioral_penalties = self.penalties_config.get("behavioral_penalties", {})
        self.operational_penalties = self.penalties_config.get("operational_penalties", {})
        self.relationship_penalties = self.penalties_config.get("relationship_penalties", {})
        self.stack_penalties = self.penalties_config.get("stack_penalties", {})
        self.compound_penalties = self.penalties_config.get("compound_penalties", {})
        self.recovery_config = self.penalties_config.get("recovery", {})
        self.application_rules = self.penalties_config.get("application_rules", {})

        # Track active penalties per entity
        self._active_penalties: dict[str, list[dict[str, Any]]] = {}

        # Track statistics
        self._stats = {
            "scores_calculated": 0,
            "penalties_applied": 0,
            "penalties_expired": 0,
            "recoveries_applied": 0
        }

        logger.info("Scorer initialized successfully")

        self.audit.log_event(
            category=AuditCategory.SYSTEM,
            level=AuditLevel.INFORMATIONAL,
            operation="scorer_initialized",
            actor="SCORING_MODULE",
            details={"config_hash": self.config.get_hash("penalties")}
        )

    def calculate_score(self,
                       entity_id: str,
                       base_influence: float,
                       check_expiration: bool = True) -> dict[str, Any]:
        """
        Calculate final score for an entity with penalties applied.
        
        Args:
            entity_id: Entity identifier
            base_influence: Base influence score from drivers
            check_expiration: Whether to check and remove expired penalties
            
        Returns:
            Dictionary with final score and penalty details
            
        Raises:
            ScoringError: If calculation fails
        """
        try:
            self._stats["scores_calculated"] += 1

            # Check for expired penalties
            if check_expiration:
                self._expire_penalties(entity_id)

            # Get active penalties for entity
            active_penalties = self._active_penalties.get(entity_id, [])

            if not active_penalties:
                # No penalties, return base score
                return {
                    "entity_id": entity_id,
                    "base_influence": base_influence,
                    "final_score": base_influence,
                    "penalties_applied": [],
                    "total_penalty_multiplier": 1.0,
                    "calculated_at": datetime.utcnow().isoformat()
                }

            # Apply penalty stacking
            final_multiplier = self._calculate_penalty_multiplier(active_penalties)

            # Apply to base score
            final_score = base_influence * final_multiplier

            # Enforce minimum score from application rules
            min_multiplier = self.application_rules.get("stacking", {}).get("max_total_multiplier", 0.1)
            final_score = max(final_score, base_influence * min_multiplier)

            result = {
                "entity_id": entity_id,
                "base_influence": base_influence,
                "final_score": final_score,
                "penalties_applied": [
                    {
                        "penalty_id": p["penalty_id"],
                        "type": p["type"],
                        "multiplier": p["multiplier"],
                        "applied_at": p["applied_at"],
                        "expires_at": p.get("expires_at")
                    }
                    for p in active_penalties
                ],
                "total_penalty_multiplier": final_multiplier,
                "score_reduction": base_influence - final_score,
                "reduction_percentage": ((base_influence - final_score) / base_influence * 100) if base_influence > 0 else 0,
                "calculated_at": datetime.utcnow().isoformat()
            }

            # Log calculation
            self.audit.log_event(
                category=AuditCategory.OPERATION,
                level=AuditLevel.STANDARD,
                operation="score_calculated",
                actor="SCORING_MODULE",
                details={
                    "entity_id": entity_id,
                    "base_influence": base_influence,
                    "final_score": final_score,
                    "penalties_count": len(active_penalties)
                }
            )

            return result

        except Exception as e:
            logger.error("Failed to calculate score for %s: %s", entity_id, e)
            raise ScoringError(f"Failed to calculate score: {e}") from e

    def apply_penalty(self,
                     entity_id: str,
                     penalty_type: str,
                     category: str,
                     justification: str,
                     metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Apply a penalty to an entity.
        
        Args:
            entity_id: Entity identifier
            penalty_type: Type of penalty (must exist in config)
            category: Category (veracity, behavioral, operational, relationship, stack)
            justification: Justification for penalty
            metadata: Additional metadata
            
        Returns:
            Applied penalty details
            
        Raises:
            PenaltyError: If penalty application fails
        """
        try:
            # Get penalty configuration
            penalty_config = self._get_penalty_config(penalty_type, category)

            if not penalty_config:
                raise PenaltyError(f"Unknown penalty type: {penalty_type} in category: {category}")

            # Check if penalty requires council approval (critical severity)
            severity = penalty_config.get("severity", "medium")
            if severity == "critical":
                requires_council = self.application_rules.get("governance", {}).get("critical_requires_council", True)
                if requires_council and not (metadata or {}).get("council_approved", False):
                    raise PenaltyError(f"Critical penalty {penalty_type} requires council approval")

            # Create penalty record
            penalty_id = f"PEN-{entity_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
            applied_at = datetime.utcnow()

            duration_days = penalty_config.get("duration_days", 0)
            permanent = penalty_config.get("permanent", False)

            expires_at = None if permanent else applied_at + timedelta(days=duration_days)

            penalty_record = {
                "penalty_id": penalty_id,
                "type": penalty_type,
                "category": category,
                "severity": severity,
                "multiplier": penalty_config.get("score_multiplier", 1.0),
                "applied_at": applied_at.isoformat(),
                "expires_at": expires_at.isoformat() if expires_at else None,
                "duration_days": duration_days,
                "permanent": permanent,
                "justification": justification,
                "metadata": metadata or {},
                "config": penalty_config
            }

            # Check stacking rules
            if not penalty_config.get("stackable", False):
                # Remove existing penalties of same type
                self._remove_penalty_by_type(entity_id, penalty_type)
            else:
                # Check max applications
                max_applications = penalty_config.get("max_applications", float("inf"))
                existing_count = self._count_penalty_type(entity_id, penalty_type)
                if existing_count >= max_applications:
                    raise PenaltyError(
                        f"Maximum applications ({max_applications}) reached for penalty {penalty_type}"
                    )

            # Add to active penalties
            if entity_id not in self._active_penalties:
                self._active_penalties[entity_id] = []

            self._active_penalties[entity_id].append(penalty_record)
            self._stats["penalties_applied"] += 1

            # Log penalty application
            self.audit.log_event(
                category=AuditCategory.GOVERNANCE,
                level=AuditLevel.CRITICAL if severity == "critical" else AuditLevel.HIGH_PRIORITY,
                operation="penalty_applied",
                actor="SCORING_MODULE",
                details={
                    "entity_id": entity_id,
                    "penalty_id": penalty_id,
                    "penalty_type": penalty_type,
                    "severity": severity,
                    "multiplier": penalty_record["multiplier"],
                    "justification": justification
                }
            )

            return penalty_record

        except Exception as e:
            logger.error("Failed to apply penalty to %s: %s", entity_id, e)
            raise PenaltyError(f"Failed to apply penalty: {e}") from e

    def remove_penalty(self, entity_id: str, penalty_id: str, reason: str) -> bool:
        """
        Remove a specific penalty from an entity.
        
        Args:
            entity_id: Entity identifier
            penalty_id: Penalty identifier
            reason: Reason for removal
            
        Returns:
            True if penalty was removed
        """
        if entity_id not in self._active_penalties:
            return False

        penalties = self._active_penalties[entity_id]

        for i, penalty in enumerate(penalties):
            if penalty["penalty_id"] == penalty_id:
                removed_penalty = penalties.pop(i)

                # Log removal
                self.audit.log_event(
                    category=AuditCategory.GOVERNANCE,
                    level=AuditLevel.STANDARD,
                    operation="penalty_removed",
                    actor="SCORING_MODULE",
                    details={
                        "entity_id": entity_id,
                        "penalty_id": penalty_id,
                        "penalty_type": removed_penalty["type"],
                        "reason": reason
                    }
                )

                return True

        return False

    def apply_recovery(self,
                      entity_id: str,
                      recovery_type: str,
                      recovery_action: str) -> float:
        """
        Apply recovery mechanism to reduce penalties.
        
        Args:
            entity_id: Entity identifier
            recovery_type: Type of recovery (time_based, action_based, appeal_process)
            recovery_action: Specific recovery action
            
        Returns:
            Recovery amount applied
            
        Raises:
            PenaltyError: If recovery fails
        """
        try:
            if entity_id not in self._active_penalties:
                return 0.0

            recovery_amount = 0.0

            if recovery_type == "action_based":
                action_config = self.recovery_config.get("action_based", {}).get("actions", {})
                recovery_amount = action_config.get(recovery_action, {}).get("recovery_amount", 0.0)

            elif recovery_type == "appeal_process":
                appeal_config = self.recovery_config.get("appeal_process", {})
                if appeal_config.get("enabled", False):
                    recovery_amount = appeal_config.get("success_recovery", 0.5)

            if recovery_amount > 0:
                # Apply recovery by reducing penalty multipliers
                for penalty in self._active_penalties[entity_id]:
                    if not penalty.get("permanent", False):
                        current_multiplier = penalty["multiplier"]
                        # Move multiplier closer to 1.0 (no penalty)
                        new_multiplier = current_multiplier + (1.0 - current_multiplier) * recovery_amount
                        penalty["multiplier"] = min(1.0, new_multiplier)

                self._stats["recoveries_applied"] += 1

                # Log recovery
                self.audit.log_event(
                    category=AuditCategory.GOVERNANCE,
                    level=AuditLevel.STANDARD,
                    operation="recovery_applied",
                    actor="SCORING_MODULE",
                    details={
                        "entity_id": entity_id,
                        "recovery_type": recovery_type,
                        "recovery_action": recovery_action,
                        "recovery_amount": recovery_amount
                    }
                )

            return recovery_amount

        except Exception as e:
            logger.error("Failed to apply recovery for %s: %s", entity_id, e)
            raise PenaltyError(f"Failed to apply recovery: {e}") from e

    def _expire_penalties(self, entity_id: str) -> int:
        """
        Check and remove expired penalties for an entity.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Number of penalties expired
        """
        if entity_id not in self._active_penalties:
            return 0

        now = datetime.utcnow()
        penalties = self._active_penalties[entity_id]

        expired_count = 0
        remaining_penalties = []

        for penalty in penalties:
            if penalty.get("permanent", False):
                remaining_penalties.append(penalty)
                continue

            expires_at_str = penalty.get("expires_at")
            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str)
                if now >= expires_at:
                    expired_count += 1

                    # Log expiration
                    self.audit.log_event(
                        category=AuditCategory.GOVERNANCE,
                        level=AuditLevel.STANDARD,
                        operation="penalty_expired",
                        actor="SCORING_MODULE",
                        details={
                            "entity_id": entity_id,
                            "penalty_id": penalty["penalty_id"],
                            "penalty_type": penalty["type"]
                        }
                    )
                else:
                    remaining_penalties.append(penalty)
            else:
                remaining_penalties.append(penalty)

        self._active_penalties[entity_id] = remaining_penalties
        self._stats["penalties_expired"] += expired_count

        return expired_count

    def _calculate_penalty_multiplier(self, penalties: list[dict[str, Any]]) -> float:
        """
        Calculate combined penalty multiplier from all active penalties.
        
        Args:
            penalties: List of active penalties
            
        Returns:
            Combined multiplier
        """
        stacking_rules = self.application_rules.get("stacking", {})
        stacking_mode = stacking_rules.get("same_type", "multiplicative")
        min_multiplier = stacking_rules.get("max_total_multiplier", 0.1)

        if stacking_mode == "multiplicative":
            # Multiply all penalty multipliers
            combined = 1.0
            for penalty in penalties:
                combined *= penalty["multiplier"]

            # Enforce minimum
            combined = max(combined, min_multiplier)

        else:
            # Additive (not recommended but supported)
            combined = 1.0
            for penalty in penalties:
                combined += (penalty["multiplier"] - 1.0)

            combined = max(combined, min_multiplier)

        return combined

    def _get_penalty_config(self, penalty_type: str, category: str) -> dict[str, Any] | None:
        """Get penalty configuration by type and category."""
        category_map = {
            "veracity": self.veracity_penalties,
            "behavioral": self.behavioral_penalties,
            "operational": self.operational_penalties,
            "relationship": self.relationship_penalties,
            "stack": self.stack_penalties
        }

        penalties = category_map.get(category, {})
        return penalties.get(penalty_type)

    def _remove_penalty_by_type(self, entity_id: str, penalty_type: str) -> int:
        """Remove all penalties of a specific type."""
        if entity_id not in self._active_penalties:
            return 0

        penalties = self._active_penalties[entity_id]
        initial_count = len(penalties)

        self._active_penalties[entity_id] = [
            p for p in penalties if p["type"] != penalty_type
        ]

        return initial_count - len(self._active_penalties[entity_id])

    def _count_penalty_type(self, entity_id: str, penalty_type: str) -> int:
        """Count penalties of a specific type for an entity."""
        if entity_id not in self._active_penalties:
            return 0

        return sum(1 for p in self._active_penalties[entity_id] if p["type"] == penalty_type)

    def get_entity_penalties(self, entity_id: str) -> list[dict[str, Any]]:
        """Get all active penalties for an entity."""
        return self._active_penalties.get(entity_id, []).copy()

    def get_statistics(self) -> dict[str, Any]:
        """Get scoring statistics."""
        return {
            **self._stats,
            "total_entities_with_penalties": len(self._active_penalties),
            "total_active_penalties": sum(len(p) for p in self._active_penalties.values())
        }

    def reset_statistics(self) -> None:
        """Reset statistics counters."""
        self._stats = {
            "scores_calculated": 0,
            "penalties_applied": 0,
            "penalties_expired": 0,
            "recoveries_applied": 0
        }


if __name__ == "__main__":
    # Test scoring module
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    try:
        scorer = Scorer()

        entity_id = "TEST-ORG-001"
        base_influence = 0.85

        # Calculate initial score (no penalties)
        score1 = scorer.calculate_score(entity_id, base_influence)
        print("Initial Score:")
        print(f"  Base: {score1['base_influence']:.4f}")
        print(f"  Final: {score1['final_score']:.4f}")

        # Apply a penalty
        penalty = scorer.apply_penalty(
            entity_id=entity_id,
            penalty_type="false_claim",
            category="veracity",
            justification="Entity made demonstrably false claim",
            metadata={"claim_id": "CLAIM-001"}
        )
        print(f"\nApplied Penalty: {penalty['penalty_id']}")
        print(f"  Type: {penalty['type']}")
        print(f"  Multiplier: {penalty['multiplier']}")
        print(f"  Severity: {penalty['severity']}")

        # Calculate score with penalty
        score2 = scorer.calculate_score(entity_id, base_influence)
        print("\nScore After Penalty:")
        print(f"  Base: {score2['base_influence']:.4f}")
        print(f"  Final: {score2['final_score']:.4f}")
        print(f"  Reduction: {score2['score_reduction']:.4f} ({score2['reduction_percentage']:.2f}%)")

        # Apply recovery
        recovery = scorer.apply_recovery(
            entity_id=entity_id,
            recovery_type="action_based",
            recovery_action="public_retraction"
        )
        print(f"\nApplied Recovery: {recovery:.2f}")

        # Calculate score after recovery
        score3 = scorer.calculate_score(entity_id, base_influence)
        print("\nScore After Recovery:")
        print(f"  Final: {score3['final_score']:.4f}")
        print(f"  Improvement: {score3['final_score'] - score2['final_score']:.4f}")

        # Print statistics
        print("\nStatistics:")
        import json
        print(json.dumps(scorer.get_statistics(), indent=2))

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise
