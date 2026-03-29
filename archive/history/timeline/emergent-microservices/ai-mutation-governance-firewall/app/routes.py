# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-10 | TIME: 21:02               #
# COMPLIANCE: Regulator-Ready / UTF-8                                          #
# ============================================================================ #

# Date: 2026-03-10 | Time: 20:37 | Status: Active | Tier: Master
#                                           [2026-03-10 18:58]
#                                          Productivity: Active
# ============================================================================ #
#                                                            DATE: 2026-03-10 #
#                                                          TIME: 15:01:55 PST #
#                                                        PRODUCTIVITY: Active #
# ============================================================================ #

#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
API routes for AI Mutation Governance Firewall
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, status

from .logging_config import logger
from .models import (
    MutationProposal,
    PaginatedProposals,
    ProposalCreate,
    ProposalUpdate,
)
from .services import MutationGovernanceService

router = APIRouter()


# Dependency injection
def get_governance_service() -> MutationGovernanceService:
    """Get governance service instance"""
    return MutationGovernanceService()


@router.get("/proposals", response_model=PaginatedProposals, status_code=status.HTTP_200_OK)
async def list_proposals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: MutationGovernanceService = Depends(get_governance_service),
):
    """List all mutation proposals with pagination"""
    logger.info(f"Listing proposals: page={page}, page_size={page_size}")

    offset = (page - 1) * page_size
    items, total = await service.list_proposals(offset=offset, limit=page_size)

    total_pages = (total + page_size - 1) // page_size

    return PaginatedProposals(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/proposals", response_model=MutationProposal, status_code=status.HTTP_201_CREATED)
async def intake_proposal(
    proposal_data: ProposalCreate = Body(...),
    service: MutationGovernanceService = Depends(get_governance_service),
):
    """Submits a new AI mutation proposal for gating and simulation"""
    logger.info(f"Intaking mutation proposal from {proposal_data.proposer_id}")
    return await service.process_proposal(proposal_data)


@router.get(
    "/proposals/{proposal_id}",
    response_model=MutationProposal,
    status_code=status.HTTP_200_OK,
)
async def get_proposal(
    proposal_id: UUID = Path(..., description="Proposal UUID"),
    service: MutationGovernanceService = Depends(get_governance_service),
):
    """Fetch status and simulation results of a specific proposal"""
    return await service.get_proposal(proposal_id)
