"""
Trust Graph Engine - Repository
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from .logging_config import logger
from .models import TrustIdentity, TrustRelation


class Database:
    def __init__(self):
        self.data: Dict[str, Any] = {"identities": {}, "relations": []}
        self.connected = False

    async def connect(self):
        self.connected = True
        logger.info("In-memory database initialized for Trust Graph")


database = Database()


class TrustRepository:
    def __init__(self):
        self.db = database

    async def get_identity(self, identity_id: UUID) -> Optional[TrustIdentity]:
        return self.db.data["identities"].get(str(identity_id))

    async def create_identity(self, identity: TrustIdentity) -> TrustIdentity:
        self.db.data["identities"][str(identity.id)] = identity
        return identity

    async def list_identities(
        self, offset: int = 0, limit: int = 20
    ) -> Tuple[List[TrustIdentity], int]:
        items = list(self.db.data["identities"].values())
        return items[offset : offset + limit], len(items)

    async def add_relation(self, relation: TrustRelation):
        self.db.data["relations"].append(relation)
        return relation

    async def get_relations_for_target(self, target_id: UUID) -> List[TrustRelation]:
        return [r for r in self.db.data["relations"] if r.target_id == target_id]
