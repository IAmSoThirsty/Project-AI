"""
API routes
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, status

from .logging_config import logger
from .models import (
    Item,
    ItemCreate,
    ItemUpdate,
    PaginatedResponse,
    PaginationParams,
)
from .services import ItemService

router = APIRouter()


# Dependency injection
def get_item_service() -> ItemService:
    """Get item service instance"""
    return ItemService()


@router.get("/items", response_model=PaginatedResponse, status_code=status.HTTP_200_OK)
async def list_items(
    pagination: PaginationParams = Depends(),
    service: ItemService = Depends(get_item_service),
):
    """
    List all items with pagination

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    """
    logger.info(
        f"Listing items: page={pagination.page}, page_size={pagination.page_size}"
    )

    items, total = await service.list_items(
        offset=pagination.offset,
        limit=pagination.page_size,
    )

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


@router.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate = Body(...),
    service: ItemService = Depends(get_item_service),
):
    """
    Create a new item

    - **name**: Item name (required)
    - **description**: Item description (optional)
    """
    logger.info(f"Creating item: {item_data.name}")

    item = await service.create_item(item_data)

    logger.info(f"Item created: {item.id}")
    return item


@router.get("/items/{item_id}", response_model=Item, status_code=status.HTTP_200_OK)
async def get_item(
    item_id: UUID = Path(..., description="Item ID"),
    service: ItemService = Depends(get_item_service),
):
    """
    Get a specific item by ID

    - **item_id**: UUID of the item
    """
    logger.info(f"Fetching item: {item_id}")

    item = await service.get_item(item_id)
    return item


@router.put("/items/{item_id}", response_model=Item, status_code=status.HTTP_200_OK)
async def update_item(
    item_id: UUID = Path(..., description="Item ID"),
    item_data: ItemUpdate = Body(...),
    service: ItemService = Depends(get_item_service),
):
    """
    Update an existing item

    - **item_id**: UUID of the item
    - **name**: New name (optional)
    - **description**: New description (optional)
    """
    logger.info(f"Updating item: {item_id}")

    item = await service.update_item(item_id, item_data)

    logger.info(f"Item updated: {item_id}")
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID = Path(..., description="Item ID"),
    service: ItemService = Depends(get_item_service),
):
    """
    Delete an item

    - **item_id**: UUID of the item
    """
    logger.info(f"Deleting item: {item_id}")

    await service.delete_item(item_id)

    logger.info(f"Item deleted: {item_id}")
    return None
