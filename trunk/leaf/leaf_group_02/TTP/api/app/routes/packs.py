# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / packs.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / packs.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Texture pack endpoints.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import TexturePack, User
from app.schemas.schemas import PackResponse, PackCreate, PackUpdate, PackListResponse
from app.services.auth import get_current_user, require_role

router = APIRouter()


@router.get("", response_model=PackListResponse)
def list_packs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    quality_tier: Optional[str] = None,
    status: str = Query("published"),
    db: Session = Depends(get_db),
) -> PackListResponse:
    """
    List texture packs with pagination and filtering.

    - **page**: Page number (1-indexed)
    - **per_page**: Items per page (max 100)
    - **category**: Filter by category
    - **quality_tier**: Filter by quality tier
    - **status**: Filter by status (default: published)
    """
    query = db.query(TexturePack).filter(TexturePack.status == status)

    if category:
        query = query.filter(TexturePack.category == category)
    if quality_tier:
        query = query.filter(TexturePack.quality_tier == quality_tier)

    total_items = query.count()
    total_pages = (total_items + per_page - 1) // per_page

    offset = (page - 1) * per_page
    packs = query.offset(offset).limit(per_page).all()

    return PackListResponse(
        data=[PackResponse.model_validate(pack) for pack in packs],
        pagination={
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_items": total_items,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        links={
            "self": f"/api/v1/packs?page={page}&per_page={per_page}",
            "first": f"/api/v1/packs?page=1&per_page={per_page}",
            "last": f"/api/v1/packs?page={total_pages}&per_page={per_page}",
        }
    )


@router.get("/{pack_id}", response_model=PackResponse)
def get_pack(pack_id: UUID, db: Session = Depends(get_db)) -> PackResponse:
    """Get detailed information about a specific pack."""
    pack = db.query(TexturePack).filter(TexturePack.id == pack_id).first()
    if not pack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pack {pack_id} not found"
        )
    return PackResponse.model_validate(pack)


@router.post("", response_model=PackResponse, status_code=status.HTTP_201_CREATED)
def create_pack(
    pack_data: PackCreate,
    current_user: User = Depends(require_role("creator")),
    db: Session = Depends(get_db),
) -> PackResponse:
    """
    Create a new texture pack.

    Requires 'creator' or 'admin' role.
    """
    # Generate slug from name
    slug = pack_data.name.lower().replace(" ", "-").replace("_", "-")

    # Check if slug already exists
    existing = db.query(TexturePack).filter(TexturePack.slug == slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Pack with slug '{slug}' already exists"
        )

    pack = TexturePack(
        name=pack_data.name,
        slug=slug,
        version=pack_data.version,
        description=pack_data.description,
        author_id=current_user.id,
        license=pack_data.license,
        category=pack_data.category,
        quality_tier=pack_data.quality_tier,
        tags=pack_data.tags,
        metadata_=pack_data.metadata,
        checksum_sha256="0" * 64,  # Placeholder, calculated during upload
        size_bytes=0,  # Calculated during upload
        status="draft",
    )

    db.add(pack)
    db.commit()
    db.refresh(pack)

    return PackResponse.model_validate(pack)


@router.put("/{pack_id}", response_model=PackResponse)
def update_pack(
    pack_id: UUID,
    pack_data: PackUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PackResponse:
    """Update an existing pack."""
    pack = db.query(TexturePack).filter(TexturePack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pack not found")

    # Authorization check
    if pack.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if pack_data.description:
        pack.description = pack_data.description
    if pack_data.tags:
        pack.tags = pack_data.tags
    if pack_data.status and current_user.role == "admin":
        pack.status = pack_data.status

    db.commit()
    db.refresh(pack)

    return PackResponse.model_validate(pack)


@router.delete("/{pack_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pack(
    pack_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """
    Delete a texture pack.

    Requires 'admin' role.
    """
    pack = db.query(TexturePack).filter(TexturePack.id == pack_id).first()
    if not pack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pack not found")

    db.delete(pack)
    db.commit()

    return None
