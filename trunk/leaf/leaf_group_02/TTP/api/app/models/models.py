# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / models.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / models.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Database models for TTP system.

SQLAlchemy ORM models matching the schema defined in ARCHITECTURE.md
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, String, Integer, BigInteger, Text, DateTime,
    ForeignKey, Enum, ARRAY, JSON, CheckConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """User accounts with role-based access control."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(255))
    role = Column(
        Enum("admin", "creator", "viewer", name="user_role"),
        nullable=False,
        default="viewer",
        index=True
    )
    status = Column(
        Enum("active", "suspended", "deleted", name="user_status"),
        nullable=False,
        default="active"
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))
    metadata_ = Column("metadata", JSON, default={})

    # Relationships
    texture_packs = relationship("TexturePack", back_populates="author")
    downloads = relationship("Download", back_populates="user")


class TexturePack(Base):
    """Texture pack metadata."""

    __tablename__ = "texture_packs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    version = Column(String(50), nullable=False)
    description = Column(Text)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    license = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    status = Column(
        Enum("draft", "review", "published", "deprecated", name="pack_status"),
        nullable=False,
        default="draft",
        index=True
    )
    category = Column(String(50), nullable=False, index=True)
    quality_tier = Column(
        Enum("pixel", "standard", "high", "cinematic", "ultra", name="quality_tier"),
        nullable=False,
        index=True
    )
    tags = Column(ARRAY(Text), default=[])
    metadata_ = Column("metadata", JSON, default={})
    checksum_sha256 = Column(String(64), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    download_count = Column(BigInteger, default=0)

    # Constraints
    __table_args__ = (
        Index("idx_texture_packs_tags", "tags", postgresql_using="gin"),
        Index("idx_texture_packs_metadata", "metadata_", postgresql_using="gin"),
        CheckConstraint("status IN ('draft', 'review', 'published', 'deprecated')"),
        CheckConstraint("quality_tier IN ('pixel', 'standard', 'high', 'cinematic', 'ultra')"),
        {},
    )

    # Relationships
    author = relationship("User", back_populates="texture_packs")
    assets = relationship("TextureAsset", back_populates="pack", cascade="all, delete-orphan")
    downloads = relationship("Download", back_populates="pack")


class TextureAsset(Base):
    """Individual texture assets within a pack."""

    __tablename__ = "texture_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pack_id = Column(UUID(as_uuid=True), ForeignKey("texture_packs.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(512), nullable=False)
    path = Column(String(1024), nullable=False)
    asset_type = Column(String(50), nullable=False, index=True)
    format = Column(String(20), nullable=False, index=True)
    resolution = Column(String(20))
    color_space = Column(String(20), nullable=False)
    bit_depth = Column(Integer, nullable=False)
    compression = Column(String(20))
    size_bytes = Column(BigInteger, nullable=False)
    checksum_sha256 = Column(String(64), nullable=False)
    storage_url = Column(Text, nullable=False)
    cdn_url = Column(Text)
    preview_url = Column(Text)
    metadata_ = Column("metadata", JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint("asset_type IN ('albedo', 'normal', 'roughness', 'metallic', 'ao', 'height', 'emission', 'opacity', 'combined')"),
        CheckConstraint("format IN ('png', 'jpg', 'exr', 'tga', 'tiff', 'svg', 'psd')"),
        CheckConstraint("color_space IN ('srgb', 'linear', 'acescg', 'raw')"),
        {},
    )

    # Relationships
    pack = relationship("TexturePack", back_populates="assets")


class Download(Base):
    """Download tracking and analytics."""

    __tablename__ = "downloads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pack_id = Column(UUID(as_uuid=True), ForeignKey("texture_packs.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    ip_address = Column(INET)
    user_agent = Column(Text)
    downloaded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    success = Column(Boolean, nullable=False)
    bytes_transferred = Column(BigInteger)
    duration_ms = Column(Integer)
    error_message = Column(Text)

    # Relationships
    pack = relationship("TexturePack", back_populates="downloads")
    user = relationship("User", back_populates="downloads")


class AuditLog(Base):
    """Audit log for all operations."""

    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(UUID(as_uuid=True), index=True)
    changes = Column(JSON)
    ip_address = Column(INET)
    user_agent = Column(Text)
    result = Column(
        Enum("success", "failure", "partial", name="audit_result"),
        nullable=False
    )
    error_message = Column(Text)

    # Constraints
    __table_args__ = (
        Index("idx_audit_log_resource", "resource_type", "resource_id"),
        {},
    )
