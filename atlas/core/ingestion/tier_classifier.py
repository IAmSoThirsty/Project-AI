"""
Tier Classification System for PROJECT ATLAS Ω

Implements the four-tier data classification system (TierA/B/C/D) with
confidence weighting, source validation, and provenance tracking.

Layer 1 Component - Production-Grade Implementation
"""

import hashlib
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field

from atlas.audit.trail import get_audit_trail, AuditCategory, AuditLevel

logger = logging.getLogger(__name__)


class DataTier(Enum):
    """
    Four-tier data classification system.
    
    Each tier has specific confidence weights and validation requirements.
    """
    TIER_A = "TierA"  # Peer-reviewed / official audited
    TIER_B = "TierB"  # Government statistical archives
    TIER_C = "TierC"  # Reputable institutional reporting
    TIER_D = "TierD"  # Media / secondary analysis
    
    def get_confidence_weight(self) -> float:
        """Get confidence weight for this tier."""
        weights = {
            DataTier.TIER_A: 1.0,   # Full confidence
            DataTier.TIER_B: 0.85,  # High confidence
            DataTier.TIER_C: 0.65,  # Medium confidence
            DataTier.TIER_D: 0.40   # Lower confidence
        }
        return weights[self]
    
    def get_requirements(self) -> Dict[str, Any]:
        """Get validation requirements for this tier."""
        return {
            DataTier.TIER_A: {
                "requires_peer_review": True,
                "requires_audit_trail": True,
                "requires_methodology": True,
                "requires_raw_data": True,
                "min_citation_count": 1
            },
            DataTier.TIER_B: {
                "requires_official_source": True,
                "requires_audit_trail": True,
                "requires_methodology": True,
                "requires_raw_data": False,
                "min_citation_count": 0
            },
            DataTier.TIER_C: {
                "requires_institutional_source": True,
                "requires_audit_trail": False,
                "requires_methodology": True,
                "requires_raw_data": False,
                "min_citation_count": 0
            },
            DataTier.TIER_D: {
                "requires_source_attribution": True,
                "requires_audit_trail": False,
                "requires_methodology": False,
                "requires_raw_data": False,
                "min_citation_count": 0
            }
        }[self]


@dataclass
class TierMetadata:
    """
    Complete metadata for tiered data.
    
    Tracks all required information for tier validation and provenance.
    """
    tier: DataTier
    source_hash: str
    confidence_weight: float
    timestamp: datetime
    geographic_scope: str
    source_type: str
    source_name: str
    
    # Optional metadata
    peer_reviewed: bool = False
    audit_trail_present: bool = False
    methodology_documented: bool = False
    raw_data_available: bool = False
    citation_count: int = 0
    doi: Optional[str] = None
    url: Optional[str] = None
    
    # Provenance tracking
    ingestion_timestamp: datetime = field(default_factory=datetime.utcnow)
    validation_passed: bool = False
    validation_errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/transmission."""
        return {
            "tier": self.tier.value,
            "source_hash": self.source_hash,
            "confidence_weight": self.confidence_weight,
            "timestamp": self.timestamp.isoformat(),
            "geographic_scope": self.geographic_scope,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "peer_reviewed": self.peer_reviewed,
            "audit_trail_present": self.audit_trail_present,
            "methodology_documented": self.methodology_documented,
            "raw_data_available": self.raw_data_available,
            "citation_count": self.citation_count,
            "doi": self.doi,
            "url": self.url,
            "ingestion_timestamp": self.ingestion_timestamp.isoformat(),
            "validation_passed": self.validation_passed,
            "validation_errors": self.validation_errors
        }


class TierClassifier:
    """
    Production-grade tier classification system.
    
    Enforces the four-tier data classification with complete validation,
    confidence weighting, and "No hash → no inclusion" rule.
    """
    
    def __init__(self):
        """Initialize tier classifier."""
        self.audit = get_audit_trail()
        
        # Known source registries (expandable)
        self.tier_a_sources: Set[str] = {
            "nature", "science", "cell", "lancet", "nejm",
            "pnas", "arxiv_verified", "cochrane", "nber",
            "world_bank_official", "imf_official", "who_official"
        }
        
        self.tier_b_sources: Set[str] = {
            "bls", "census", "fed", "oecd", "eurostat",
            "national_statistics", "government_archives"
        }
        
        self.tier_c_sources: Set[str] = {
            "pew_research", "gallup", "reuters_institute",
            "brookings", "rand", "csis", "carnegie"
        }
        
        # All others default to Tier D unless upgraded
        
        logger.info("Initialized TierClassifier with source registries")
        
        self.audit.log_event(
            category=AuditCategory.SYSTEM,
            level=AuditLevel.INFORMATIONAL,
            operation="tier_classifier_initialized",
            actor="TIER_CLASSIFIER",
            details={
                "tier_a_sources": len(self.tier_a_sources),
                "tier_b_sources": len(self.tier_b_sources),
                "tier_c_sources": len(self.tier_c_sources)
            }
        )
    
    def classify_source(
        self,
        source_name: str,
        source_type: str,
        metadata: Dict[str, Any]
    ) -> DataTier:
        """
        Classify data source into appropriate tier.
        
        Args:
            source_name: Name of data source
            source_type: Type of source (journal, government, institution, media)
            metadata: Additional metadata for classification
            
        Returns:
            Classified tier
        """
        source_lower = source_name.lower()
        
        # Check explicit registries first
        if source_lower in self.tier_a_sources:
            return DataTier.TIER_A
        if source_lower in self.tier_b_sources:
            return DataTier.TIER_B
        if source_lower in self.tier_c_sources:
            return DataTier.TIER_C
        
        # Check metadata-based classification
        if source_type == "peer_reviewed_journal":
            # Requires additional validation
            if metadata.get("peer_reviewed") and metadata.get("citation_count", 0) > 0:
                return DataTier.TIER_A
        
        if source_type == "government_statistical":
            return DataTier.TIER_B
        
        if source_type == "institutional_research":
            if metadata.get("methodology_documented"):
                return DataTier.TIER_C
        
        # Default to Tier D
        return DataTier.TIER_D
    
    def compute_source_hash(self, content: str) -> str:
        """
        Compute canonical hash of source content.
        
        Args:
            content: Raw content to hash
            
        Returns:
            SHA-256 hash as hex string
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def validate_tier_requirements(
        self,
        tier: DataTier,
        metadata: TierMetadata
    ) -> tuple[bool, List[str]]:
        """
        Validate that metadata meets tier requirements.
        
        Args:
            tier: Claimed tier
            metadata: Metadata to validate
            
        Returns:
            (valid, list of validation errors)
        """
        requirements = tier.get_requirements()
        errors = []
        
        # Check each requirement
        if requirements.get("requires_peer_review") and not metadata.peer_reviewed:
            errors.append(f"{tier.value} requires peer review")
        
        if requirements.get("requires_audit_trail") and not metadata.audit_trail_present:
            errors.append(f"{tier.value} requires audit trail")
        
        if requirements.get("requires_methodology") and not metadata.methodology_documented:
            errors.append(f"{tier.value} requires documented methodology")
        
        if requirements.get("requires_raw_data") and not metadata.raw_data_available:
            errors.append(f"{tier.value} requires raw data availability")
        
        min_citations = requirements.get("min_citation_count", 0)
        if metadata.citation_count < min_citations:
            errors.append(
                f"{tier.value} requires at least {min_citations} citations "
                f"(found {metadata.citation_count})"
            )
        
        # Check source hash presence (CRITICAL: "No hash → no inclusion")
        if not metadata.source_hash:
            errors.append("CRITICAL: No source hash - data cannot be included")
        
        valid = len(errors) == 0
        
        # Log validation result
        self.audit.log_event(
            category=AuditCategory.DATA,
            level=AuditLevel.INFORMATIONAL if valid else AuditLevel.HIGH_PRIORITY,
            operation="tier_validation",
            actor="TIER_CLASSIFIER",
            details={
                "tier": tier.value,
                "valid": valid,
                "errors": errors,
                "source_name": metadata.source_name
            }
        )
        
        return valid, errors
    
    def create_tier_metadata(
        self,
        content: str,
        source_name: str,
        source_type: str,
        timestamp: datetime,
        geographic_scope: str,
        **kwargs
    ) -> TierMetadata:
        """
        Create complete tier metadata for data.
        
        Args:
            content: Raw content (for hashing)
            source_name: Name of source
            source_type: Type of source
            timestamp: Data timestamp
            geographic_scope: Geographic scope of data
            **kwargs: Additional metadata fields
            
        Returns:
            Complete tier metadata object
        """
        # Compute source hash
        source_hash = self.compute_source_hash(content)
        
        # Classify tier
        tier = self.classify_source(source_name, source_type, kwargs)
        
        # Get confidence weight
        confidence_weight = tier.get_confidence_weight()
        
        # Create metadata object
        metadata = TierMetadata(
            tier=tier,
            source_hash=source_hash,
            confidence_weight=confidence_weight,
            timestamp=timestamp,
            geographic_scope=geographic_scope,
            source_type=source_type,
            source_name=source_name,
            peer_reviewed=kwargs.get("peer_reviewed", False),
            audit_trail_present=kwargs.get("audit_trail_present", False),
            methodology_documented=kwargs.get("methodology_documented", False),
            raw_data_available=kwargs.get("raw_data_available", False),
            citation_count=kwargs.get("citation_count", 0),
            doi=kwargs.get("doi"),
            url=kwargs.get("url")
        )
        
        # Validate requirements
        valid, errors = self.validate_tier_requirements(tier, metadata)
        metadata.validation_passed = valid
        metadata.validation_errors = errors
        
        # Log metadata creation
        self.audit.log_event(
            category=AuditCategory.DATA,
            level=AuditLevel.INFORMATIONAL,
            operation="tier_metadata_created",
            actor="TIER_CLASSIFIER",
            details={
                "tier": tier.value,
                "confidence_weight": confidence_weight,
                "source_hash": source_hash[:16] + "...",
                "validation_passed": valid
            }
        )
        
        return metadata
    
    def enforce_inclusion_rule(self, metadata: TierMetadata) -> bool:
        """
        Enforce "No hash → no inclusion" rule.
        
        Args:
            metadata: Tier metadata to check
            
        Returns:
            True if data can be included, False otherwise
        """
        if not metadata.source_hash:
            logger.error(
                f"EXCLUSION: No source hash for {metadata.source_name} - "
                "data cannot be included per constitutional rule"
            )
            self.audit.log_event(
                category=AuditCategory.GOVERNANCE,
                level=AuditLevel.CRITICAL,
                operation="data_excluded_no_hash",
                actor="TIER_CLASSIFIER",
                details={
                    "source_name": metadata.source_name,
                    "reason": "No hash → no inclusion (constitutional rule)"
                }
            )
            return False
        
        if not metadata.validation_passed:
            logger.warning(
                f"EXCLUSION: Validation failed for {metadata.source_name} - "
                f"errors: {metadata.validation_errors}"
            )
            self.audit.log_event(
                category=AuditCategory.GOVERNANCE,
                level=AuditLevel.HIGH_PRIORITY,
                operation="data_excluded_validation_failed",
                actor="TIER_CLASSIFIER",
                details={
                    "source_name": metadata.source_name,
                    "tier": metadata.tier.value,
                    "errors": metadata.validation_errors
                }
            )
            return False
        
        return True
    
    def get_tier_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about tier classification.
        
        Returns:
            Dictionary with tier statistics
        """
        return {
            "tier_a_sources": len(self.tier_a_sources),
            "tier_b_sources": len(self.tier_b_sources),
            "tier_c_sources": len(self.tier_c_sources),
            "confidence_weights": {
                tier.value: tier.get_confidence_weight()
                for tier in DataTier
            }
        }


# Singleton instance
_tier_classifier: Optional[TierClassifier] = None


def get_tier_classifier() -> TierClassifier:
    """Get singleton tier classifier instance."""
    global _tier_classifier
    if _tier_classifier is None:
        _tier_classifier = TierClassifier()
    return _tier_classifier
