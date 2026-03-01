"""
Sovereign Data Vault - Service Layer
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from .logging_config import logger
from .models import VaultAccessRequest, VaultObject, VaultUpload
from .repository import VaultRepository


class DataVaultService:
    """Service for managing self-sovereign encrypted storage"""

    def __init__(self):
        self.repository = VaultRepository()

    async def upload_data(self, data: VaultUpload) -> VaultObject:
        """Store encrypted blob with integrity metadata"""
        logger.info(f"Vault: Uploading object for owner {data.owner_id}")

        # Verify integrity hash (simulated)

        obj = VaultObject(**data.model_dump(), access_control_list=[data.owner_id])
        return await self.repository.store_object(obj)

    async def get_data(self, object_id: UUID, requester_id: str) -> VaultObject:
        """Retrieve encrypted blob if authorized"""
        obj = await self.repository.get_object(object_id)
        if not obj:
            raise Exception("Object not found")

        if requester_id not in obj.access_control_list:
            logger.error(
                f"Vault: Unauthorized access attempt by {requester_id} on {object_id}"
            )
            raise Exception("Unauthorized access")

        logger.info(f"Vault: Authorized access to {object_id} by {requester_id}")
        return obj

    async def list_vault(self, owner_id: str) -> List[VaultObject]:
        return await self.repository.list_objects_for_owner(owner_id)
