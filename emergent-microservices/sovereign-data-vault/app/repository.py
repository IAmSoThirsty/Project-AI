"""
Sovereign Data Vault - Repository
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from .logging_config import logger
from .models import VaultObject


class Database:
    def __init__(self):
        self.data: Dict[str, Any] = {"vault": {}}
        self.connected = False

    async def connect(self):
        self.connected = True
        logger.info("In-memory database initialized for Data Vault")


database = Database()


class VaultRepository:
    def __init__(self):
        self.db = database

    async def get_object(self, object_id: UUID) -> Optional[VaultObject]:
        return self.db.data["vault"].get(str(object_id))

    async def store_object(self, obj: VaultObject) -> VaultObject:
        self.db.data["vault"][str(obj.id)] = obj
        return obj

    async def list_objects_for_owner(self, owner_id: str) -> List[VaultObject]:
        return [o for o in self.db.data["vault"].values() if o.owner_id == owner_id]
