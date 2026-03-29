import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: dark-fiber-relay / services.py
# ============================================================================ #
"""
Business logic layer
"""
from typing import List, Tuple, Optional
from uuid import UUID
from datetime import datetime, timezone

from .models import Item, ItemCreate, ItemUpdate
from .repository import ItemRepository
from .errors import NotFoundError, ValidationError, ConflictError
from .logging_config import logger
from .metrics import DOMAIN_EVENTS, DOMAIN_FAILURES


class ItemService:
    """Item business logic service"""
    
    def __init__(self):
        self.repository = ItemRepository()
    
    async def list_items(self, offset: int = 0, limit: int = 20) -> Tuple[List[Item], int]:
        """List items with pagination"""
        try:
            items, total = await self.repository.list(offset=offset, limit=limit)
            
            DOMAIN_EVENTS.labels(event_type="items_listed").inc()
            return items, total
        
        except Exception as e:
            DOMAIN_FAILURES.labels(operation="list_items", reason="database_error").inc()
            logger.error(f"Failed to list items: {e}")
            raise
    
    async def get_item(self, item_id: UUID) -> Item:
        """Get item by ID"""
        try:
            item = await self.repository.get(item_id)
            
            if not item:
                raise NotFoundError("Item", item_id)
            
            DOMAIN_EVENTS.labels(event_type="item_fetched").inc()
            return item
        
        except NotFoundError:
            DOMAIN_FAILURES.labels(operation="get_item", reason="not_found").inc()
            raise
        except Exception as e:
            DOMAIN_FAILURES.labels(operation="get_item", reason="database_error").inc()
            logger.error(f"Failed to get item {item_id}: {e}")
            raise
    
    async def create_item(self, item_data: ItemCreate) -> Item:
        """Create new item"""
        try:
            # Business logic validation
            await self._validate_item_creation(item_data)
            
            # Create item
            now = datetime.now(timezone.utc)
            item = Item(
                **item_data.model_dump(),
                created_at=now,
                updated_at=now,
            )
            
            # Persist
            created_item = await self.repository.create(item)
            
            DOMAIN_EVENTS.labels(event_type="item_created").inc()
            logger.info(f"Item created: {created_item.id}")
            
            return created_item
        
        except (ValidationError, ConflictError):
            DOMAIN_FAILURES.labels(operation="create_item", reason="validation_error").inc()
            raise
        except Exception as e:
            DOMAIN_FAILURES.labels(operation="create_item", reason="database_error").inc()
            logger.error(f"Failed to create item: {e}")
            raise
    
    async def update_item(self, item_id: UUID, item_data: ItemUpdate) -> Item:
        """Update existing item"""
        try:
            # Check if item exists
            existing_item = await self.get_item(item_id)
            
            # Apply updates
            update_dict = item_data.model_dump(exclude_unset=True)
            if not update_dict:
                return existing_item
            
            update_dict["updated_at"] = datetime.now(timezone.utc)
            
            # Update in database
            updated_item = await self.repository.update(item_id, update_dict)
            
            DOMAIN_EVENTS.labels(event_type="item_updated").inc()
            logger.info(f"Item updated: {item_id}")
            
            return updated_item
        
        except NotFoundError:
            DOMAIN_FAILURES.labels(operation="update_item", reason="not_found").inc()
            raise
        except Exception as e:
            DOMAIN_FAILURES.labels(operation="update_item", reason="database_error").inc()
            logger.error(f"Failed to update item {item_id}: {e}")
            raise
    
    async def delete_item(self, item_id: UUID) -> None:
        """Delete item"""
        try:
            # Check if item exists
            await self.get_item(item_id)
            
            # Delete
            await self.repository.delete(item_id)
            
            DOMAIN_EVENTS.labels(event_type="item_deleted").inc()
            logger.info(f"Item deleted: {item_id}")
        
        except NotFoundError:
            DOMAIN_FAILURES.labels(operation="delete_item", reason="not_found").inc()
            raise
        except Exception as e:
            DOMAIN_FAILURES.labels(operation="delete_item", reason="database_error").inc()
            logger.error(f"Failed to delete item {item_id}: {e}")
            raise
    
    async def _validate_item_creation(self, item_data: ItemCreate) -> None:
        """Business logic validation for item creation"""
        # Example: Check for duplicate names
        # existing = await self.repository.find_by_name(item_data.name)
        # if existing:
        #     raise ConflictError(f"Item with name '{item_data.name}' already exists")
        pass
