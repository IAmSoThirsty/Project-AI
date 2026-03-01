"""
API routes for Autonomous Incident Reflex System
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, status

from .logging_config import logger
from .models import (
    IncidentCreate,
    IncidentUpdate,
    PaginatedIncidents,
    SecurityIncident,
)
from .services import IncidentReflexService

router = APIRouter()


def get_reflex_service() -> IncidentReflexService:
    return IncidentReflexService()


@router.get(
    "/incidents", response_model=PaginatedIncidents, status_code=status.HTTP_200_OK
)
async def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: IncidentReflexService = Depends(get_reflex_service),
):
    """List security incidents with pagination"""
    offset = (page - 1) * page_size
    items, total = await service.list_incidents(offset=offset, limit=page_size)
    total_pages = (total + page_size - 1) // page_size

    return PaginatedIncidents(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post(
    "/incidents", response_model=SecurityIncident, status_code=status.HTTP_201_CREATED
)
async def report_incident(
    data: IncidentCreate = Body(...),
    service: IncidentReflexService = Depends(get_reflex_service),
):
    """Report a new security incident for reflex processing"""
    return await service.report_incident(data)


@router.get(
    "/incidents/{incident_id}",
    response_model=SecurityIncident,
    status_code=status.HTTP_200_OK,
)
async def get_incident(
    incident_id: UUID = Path(..., description="Incident UUID"),
    service: IncidentReflexService = Depends(get_reflex_service),
):
    """Fetch status and evidence of a specific incident"""
    return await service.get_incident(incident_id)
