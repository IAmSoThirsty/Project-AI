"""
Autonomous Incident Reflex System - Repository
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from .logging_config import logger
from .models import SecurityIncident


class Database:
    def __init__(self):
        self.data: Dict[str, Any] = {"incidents": {}}
        self.connected = False

    async def connect(self):
        self.connected = True
        logger.info("In-memory database initialized for Reflex System")

    async def disconnect(self):
        self.connected = False
        self.data["incidents"].clear()


database = Database()


class IncidentRepository:
    def __init__(self):
        self.db = database

    async def list(
        self, offset: int = 0, limit: int = 20
    ) -> Tuple[List[SecurityIncident], int]:
        items = list(self.db.data["incidents"].values())
        items.sort(key=lambda x: x.created_at, reverse=True)
        return items[offset : offset + limit], len(items)

    async def get(self, incident_id: UUID) -> Optional[SecurityIncident]:
        return self.db.data["incidents"].get(str(incident_id))

    async def create(self, incident: SecurityIncident) -> SecurityIncident:
        self.db.data["incidents"][str(incident.id)] = incident
        return incident

    async def update(
        self, incident_id: UUID, updates: Dict[str, Any]
    ) -> SecurityIncident:
        incident = await self.get(incident_id)
        if incident:
            for key, value in updates.items():
                if hasattr(incident, key):
                    setattr(incident, key, value)
            incident.updated_at = datetime.now()
        return incident
