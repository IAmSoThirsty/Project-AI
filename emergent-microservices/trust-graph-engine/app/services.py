"""
Trust Graph Engine - Service Layer
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from .logging_config import logger
from .models import IdentityCreate, ReputationUpdate, TrustIdentity, TrustRelation
from .repository import TrustRepository


class TrustGraphService:
    """Service for managing distributed reputation and trust proofs"""

    def __init__(self):
        self.repository = TrustRepository()

    async def register_identity(self, data: IdentityCreate) -> TrustIdentity:
        """Register a new sovereign identity with Ed25519 provenance"""
        logger.info(f"Registering trust identity for alias: {data.alias}")

        identity = TrustIdentity(**data.model_dump())
        return await self.repository.create_identity(identity)

    async def add_trust_rating(
        self, source_id: UUID, target_id: UUID, weight: float, rationale: str
    ):
        """Add a weighted trust rating between two identities"""
        logger.info(
            f"Adding trust rating: {source_id} -> {target_id} (weight: {weight})"
        )

        relation = TrustRelation(
            source_id=source_id, target_id=target_id, weight=weight, rationale=rationale
        )
        await self.repository.add_relation(relation)

        # Trigger reputation recalc
        await self._recalculate_reputation(target_id)
        return {"status": "success"}

    async def _recalculate_reputation(self, identity_id: UUID):
        """Calculate weighted average reputation based on graph relations"""
        relations = await self.repository.get_relations_for_target(identity_id)
        if not relations:
            return

        # Simple weighted average for scaffold
        total_weight = sum(r.weight for r in relations)
        new_score = (total_weight / len(relations) + 1.0) / 2.0  # Scale to 0..1

        identity = await self.repository.get_identity(identity_id)
        if identity:
            identity.reputation_score = max(0.0, min(1.0, new_score))
            identity.updated_at = datetime.now()
            logger.info(
                f"Updated reputation for {identity.alias}: {identity.reputation_score}"
            )

    async def get_identity(self, identity_id: UUID) -> TrustIdentity:
        return await self.repository.get_identity(identity_id)
