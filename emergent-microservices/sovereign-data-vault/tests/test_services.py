# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_services.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_services.py


"""Test business logic services"""

from uuid import uuid4

import pytest

from app.errors import NotFoundError
from app.models import ItemCreate, ItemUpdate
from app.services import ItemService


class TestItemService:
    """Test item service"""

    @pytest.mark.asyncio
    async def test_create_item(self, db):
        """Test item creation"""
        service = ItemService()
        item_data = ItemCreate(name="Test", description="Test desc")

        item = await service.create_item(item_data)

        assert item.name == "Test"
        assert item.id is not None

    @pytest.mark.asyncio
    async def test_get_item_not_found(self, db):
        """Test getting non-existent item raises error"""
        service = ItemService()

        with pytest.raises(NotFoundError):
            await service.get_item(uuid4())

    @pytest.mark.asyncio
    async def test_list_items(self, db):
        """Test listing items"""
        service = ItemService()

        items, total = await service.list_items()

        assert isinstance(items, list)
        assert total >= 0
