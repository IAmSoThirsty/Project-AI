#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Autonomous Negotiation Agent - Repository
"""

from typing import Any
from uuid import UUID

from .logging_config import logger
from .models import AgreedContract, NegotiationSession


class Database:
    def __init__(self):
        self.data: dict[str, Any] = {"sessions": {}, "contracts": {}}
        self.connected = False

    async def connect(self):
        self.connected = True
        logger.info("In-memory database initialized for Negotiation Agent")


database = Database()


class NegotiationRepository:
    def __init__(self):
        self.db = database

    async def get_session(self, session_id: UUID) -> NegotiationSession | None:
        return self.db.data["sessions"].get(str(session_id))

    async def save_session(self, session: NegotiationSession) -> NegotiationSession:
        self.db.data["sessions"][str(session.id)] = session
        return session

    async def save_contract(self, contract: AgreedContract) -> AgreedContract:
        self.db.data["contracts"][str(contract.id)] = contract
        return contract
