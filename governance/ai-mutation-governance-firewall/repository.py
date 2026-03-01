"""
Repository layer - Database abstraction specialized for Mutation Proposals
"""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from .config import settings
from .errors import DatabaseError
from .logging_config import logger
from .metrics import DB_CONNECTIONS_ACTIVE, DB_ERRORS, DB_QUERY_DURATION
from .models import MutationProposal


class Database:
    """Database connection manager (In-memory for scaffold)"""

    def __init__(self):
        self.data: Dict[str, Any] = {"proposals": {}}
        self.connected = False

    async def connect(self):
        self.connected = True
        logger.info("In-memory database initialized for Mutation Governance")
        DB_CONNECTIONS_ACTIVE.set(1)

    async def disconnect(self):
        self.connected = False
        self.data["proposals"].clear()
        logger.info("In-memory database cleared")
        DB_CONNECTIONS_ACTIVE.set(0)


database = Database()


class ProposalRepository:
    """Repository for Mutation Proposals"""

    def __init__(self):
        self.db = database

    async def list(
        self, offset: int = 0, limit: int = 20
    ) -> Tuple[List[MutationProposal], int]:
        proposals_list = list(self.db.data["proposals"].values())
        proposals_list.sort(key=lambda x: x.created_at, reverse=True)
        total = len(proposals_list)
        return proposals_list[offset : offset + limit], total

    async def get(self, proposal_id: UUID) -> Optional[MutationProposal]:
        return self.db.data["proposals"].get(str(proposal_id))

    async def create(self, proposal: MutationProposal) -> MutationProposal:
        self.db.data["proposals"][str(proposal.id)] = proposal
        return proposal

    async def update(
        self, proposal_id: UUID, updates: Dict[str, Any]
    ) -> MutationProposal:
        proposal = await self.get(proposal_id)
        if proposal:
            for key, value in updates.items():
                if hasattr(proposal, key):
                    setattr(proposal, key, value)
            proposal.updated_at = datetime.now()
        return proposal

    async def delete(self, proposal_id: UUID) -> None:
        self.db.data["proposals"].pop(str(proposal_id), None)
