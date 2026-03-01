"""
Autonomous Incident Reflex System - Service Layer
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from .errors import NotFoundError
from .logging_config import logger
from .models import IncidentCreate, IncidentUpdate, SecurityIncident
from .repository import IncidentRepository


class IncidentReflexService:
    """Service to handle security incidents and trigger automated reflex actions"""

    def __init__(self):
        self.repository = IncidentRepository()

    async def report_incident(self, data: IncidentCreate) -> SecurityIncident:
        """Report a new incident and trigger reflex assessment"""
        logger.warning(
            f"SECURITY INCIDENT reported from {data.source}: {data.incident_type}"
        )

        incident = SecurityIncident(**data.model_dump(), status="analyzing")

        created = await self.repository.create(incident)

        # Trigger reflex based on severity
        if data.severity in ["high", "critical"]:
            asyncio.create_task(self._trigger_reflex_action(created.id))

        return created

    async def _trigger_reflex_action(self, incident_id: UUID):
        """Execute reflex action via OctoReflex bridge"""
        incident = await self.repository.get(incident_id)
        if not incident:
            return

        logger.critical(f"TRIGGERING REFLEX for incident {incident_id}")

        # In production, this imports and calls octoreflex.bridge_from_emergent
        # For now, we simulate the bridge call
        reflex_action = "KERNEL_ISOLATION_RESTART"

        await self.repository.update(
            incident_id,
            {
                "status": "reflex_triggered",
                "reflex_actions_taken": [reflex_action],
                "evidence_hash": "SHA256:d57f9...",
            },
        )

        logger.info(f"Reflex action {reflex_action} successful for {incident_id}")

    async def list_incidents(
        self, offset: int = 0, limit: int = 20
    ) -> Tuple[List[SecurityIncident], int]:
        return await self.repository.list(offset, limit)

    async def get_incident(self, incident_id: UUID) -> SecurityIncident:
        incident = await self.repository.get(incident_id)
        if not incident:
            raise NotFoundError("Incident", incident_id)
        return incident
