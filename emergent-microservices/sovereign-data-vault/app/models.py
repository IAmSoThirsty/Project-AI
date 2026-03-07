#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Sovereign Data Vault - Encrypted Storage Models
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class VaultObject(BaseModel):
    """Encrypted data object stored in the vault"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    owner_id: str
    encrypted_blob: str  # Base64 encrypted payload
    encryption_metadata: dict[str, Any]  # Algorithm, Salt, IV
    access_control_list: list[str]  # List of authorized public keys
    integrity_hash: str  # SHA256 of original data
    tags: list[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class VaultUpload(BaseModel):
    owner_id: str
    encrypted_blob: str
    encryption_metadata: dict[str, Any]
    integrity_hash: str
    tags: list[str] = []


class VaultAccessRequest(BaseModel):
    accessor_id: str
    signature: str  # Proof of ownership/access
