# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / __init__.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / __init__.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
API route definitions.
"""

from fastapi import APIRouter

from app.routes import packs, auth, users

api_router = APIRouter()

# Include route modules
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(packs.router, prefix="/packs", tags=["packs"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
