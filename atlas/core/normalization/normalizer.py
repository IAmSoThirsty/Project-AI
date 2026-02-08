"""
Normalization Module for PROJECT ATLAS

Standardizes raw data formats, applies cleaning and transformation,
ensures consistency across data sources, deduplicates and merges entities.

Production-grade with full error handling, logging, and audit trail integration.
"""

import hashlib
import json
import logging
import re
from datetime import datetime
from typing import Any

from atlas.audit.trail import AuditCategory, AuditLevel, AuditTrail, get_audit_trail
from atlas.config.loader import ConfigLoader, get_config_loader
from atlas.schemas.validator import SchemaValidator, get_schema_validator

logger = logging.getLogger(__name__)


class NormalizationError(Exception):
    """Raised when normalization fails."""
    pass


class DataQualityError(Exception):
    """Raised when data quality is insufficient."""
    pass


class Normalizer:
    """
    Production-grade data normalizer for PROJECT ATLAS.
    
    Standardizes raw data, applies transformations, deduplicates entities,
    and ensures consistency across all data sources.
    """

    def __init__(self,
                 config_loader: ConfigLoader | None = None,
                 schema_validator: SchemaValidator | None = None,
                 audit_trail: AuditTrail | None = None):
        """
        Initialize normalizer.
        
        Args:
            config_loader: Configuration loader (uses global if None)
            schema_validator: Schema validator (uses global if None)
            audit_trail: Audit trail (uses global if None)
        """
        self.config = config_loader or get_config_loader()
        self.validator = schema_validator or get_schema_validator()
        self.audit = audit_trail or get_audit_trail()

        # Load normalization configuration from thresholds
        self.thresholds = self.config.get("thresholds")
        self.data_quality_thresholds = self.thresholds.get("data_quality", {})

        # Track normalization statistics
        self._stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "duplicates_removed": 0,
            "entities_merged": 0
        }

        logger.info("Normalizer initialized successfully")

        self.audit.log_event(
            category=AuditCategory.SYSTEM,
            level=AuditLevel.INFORMATIONAL,
            operation="normalizer_initialized",
            actor="NORMALIZATION_MODULE",
            details={"config_hashes": self.config.get_all_hashes()}
        )

    def normalize_organization(self, raw_org: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize a raw organization object.
        
        Args:
            raw_org: Raw organization data
            
        Returns:
            Normalized organization object
            
        Raises:
            NormalizationError: If normalization fails
            DataQualityError: If data quality is insufficient
        """
        try:
            self._stats["total_processed"] += 1

            # Log start of normalization
            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.STANDARD,
                operation="normalize_organization_start",
                actor="NORMALIZATION_MODULE",
                details={"raw_id": raw_org.get("id", "unknown")}
            )

            # Validate data quality first
            self._validate_data_quality(raw_org, "organization")

            # Create normalized structure
            normalized = {
                "id": self._normalize_id(raw_org.get("id")),
                "name": self._normalize_text(raw_org.get("name", ""), capitalize=True),
                "type": self._normalize_type(raw_org.get("type", "unknown")),
                "description": self._normalize_text(raw_org.get("description", "")),
                "founded": self._normalize_date(raw_org.get("founded")),
                "jurisdiction": self._normalize_jurisdiction(raw_org.get("jurisdiction")),
                "attributes": self._normalize_attributes(raw_org.get("attributes", {})),
                "relationships": self._normalize_relationships(raw_org.get("relationships", [])),
                "metadata": {
                    "normalized_at": datetime.utcnow().isoformat(),
                    "normalization_version": "1.0.0",
                    "original_source": raw_org.get("source", "unknown"),
                    "quality_score": self._compute_quality_score(raw_org)
                }
            }

            # Add computed hash for deduplication
            normalized["metadata"]["content_hash"] = self._compute_content_hash(normalized)

            # Validate against schema
            self.validator.validate_organization(normalized, strict=True)

            # Log success
            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.STANDARD,
                operation="normalize_organization_success",
                actor="NORMALIZATION_MODULE",
                details={
                    "org_id": normalized["id"],
                    "quality_score": normalized["metadata"]["quality_score"]
                }
            )

            self._stats["successful"] += 1
            return normalized

        except Exception as e:
            self._stats["failed"] += 1
            logger.error(f"Failed to normalize organization: {e}")

            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.HIGH_PRIORITY,
                operation="normalize_organization_failed",
                actor="NORMALIZATION_MODULE",
                details={"error": str(e), "raw_id": raw_org.get("id", "unknown")}
            )

            raise NormalizationError(f"Failed to normalize organization: {e}") from e

    def normalize_claim(self, raw_claim: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize a raw claim object.
        
        Args:
            raw_claim: Raw claim data
            
        Returns:
            Normalized claim object
            
        Raises:
            NormalizationError: If normalization fails
        """
        try:
            self._stats["total_processed"] += 1

            # Validate data quality
            self._validate_data_quality(raw_claim, "claim")

            normalized = {
                "id": self._normalize_id(raw_claim.get("id")),
                "text": self._normalize_text(raw_claim.get("text", ""), strip_html=True),
                "claimant": self._normalize_id(raw_claim.get("claimant")),
                "date": self._normalize_date(raw_claim.get("date")),
                "topics": self._normalize_topics(raw_claim.get("topics", [])),
                "veracity": self._normalize_veracity(raw_claim.get("veracity")),
                "evidence": self._normalize_evidence(raw_claim.get("evidence", [])),
                "metadata": {
                    "normalized_at": datetime.utcnow().isoformat(),
                    "normalization_version": "1.0.0",
                    "original_source": raw_claim.get("source", "unknown"),
                    "quality_score": self._compute_quality_score(raw_claim)
                }
            }

            normalized["metadata"]["content_hash"] = self._compute_content_hash(normalized)

            # Validate against schema
            self.validator.validate_claim(normalized, strict=True)

            self._stats["successful"] += 1
            return normalized

        except Exception as e:
            self._stats["failed"] += 1
            logger.error(f"Failed to normalize claim: {e}")
            raise NormalizationError(f"Failed to normalize claim: {e}") from e

    def normalize_opinion(self, raw_opinion: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize a raw opinion object.
        
        Args:
            raw_opinion: Raw opinion data
            
        Returns:
            Normalized opinion object
            
        Raises:
            NormalizationError: If normalization fails
        """
        try:
            self._stats["total_processed"] += 1

            # Validate data quality
            self._validate_data_quality(raw_opinion, "opinion")

            normalized = {
                "id": self._normalize_id(raw_opinion.get("id")),
                "holder_id": self._normalize_id(raw_opinion.get("holder_id")),
                "target_id": self._normalize_id(raw_opinion.get("target_id")),
                "sentiment": self._normalize_sentiment(raw_opinion.get("sentiment")),
                "confidence": self._normalize_confidence(raw_opinion.get("confidence")),
                "date": self._normalize_date(raw_opinion.get("date")),
                "text": self._normalize_text(raw_opinion.get("text", ""), strip_html=True),
                "metadata": {
                    "normalized_at": datetime.utcnow().isoformat(),
                    "normalization_version": "1.0.0",
                    "original_source": raw_opinion.get("source", "unknown"),
                    "quality_score": self._compute_quality_score(raw_opinion)
                }
            }

            normalized["metadata"]["content_hash"] = self._compute_content_hash(normalized)

            # Validate against schema
            self.validator.validate_opinion(normalized, strict=True)

            self._stats["successful"] += 1
            return normalized

        except Exception as e:
            self._stats["failed"] += 1
            logger.error(f"Failed to normalize opinion: {e}")
            raise NormalizationError(f"Failed to normalize opinion: {e}") from e

    def deduplicate(self, entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Deduplicate entities based on content hash.
        
        Args:
            entities: List of normalized entities
            
        Returns:
            Deduplicated list of entities
        """
        seen_hashes: set[str] = set()
        unique_entities = []
        duplicates_count = 0

        for entity in entities:
            content_hash = entity.get("metadata", {}).get("content_hash")

            if not content_hash:
                # Compute if missing
                content_hash = self._compute_content_hash(entity)
                if "metadata" not in entity:
                    entity["metadata"] = {}
                entity["metadata"]["content_hash"] = content_hash

            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_entities.append(entity)
            else:
                duplicates_count += 1

        self._stats["duplicates_removed"] += duplicates_count

        if duplicates_count > 0:
            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.STANDARD,
                operation="deduplication_performed",
                actor="NORMALIZATION_MODULE",
                details={
                    "total_entities": len(entities),
                    "unique_entities": len(unique_entities),
                    "duplicates_removed": duplicates_count
                }
            )

        return unique_entities

    def merge_entities(self, entity1: dict[str, Any], entity2: dict[str, Any]) -> dict[str, Any]:
        """
        Merge two similar entities into one.
        
        Args:
            entity1: First entity
            entity2: Second entity
            
        Returns:
            Merged entity
        """
        # Use entity with higher quality score as base
        base = entity1 if entity1.get("metadata", {}).get("quality_score", 0) >= \
                         entity2.get("metadata", {}).get("quality_score", 0) else entity2
        other = entity2 if base == entity1 else entity1

        merged = dict(base)

        # Merge attributes (prefer non-empty values)
        for key, value in other.items():
            if key == "metadata":
                continue

            if key not in merged or not merged[key]:
                merged[key] = value
            elif isinstance(value, list) and isinstance(merged.get(key), list):
                # Merge lists and deduplicate
                merged[key] = list(set(merged[key] + value))

        # Update metadata
        merged["metadata"]["merged_at"] = datetime.utcnow().isoformat()
        merged["metadata"]["merged_from"] = [
            entity1.get("id", "unknown"),
            entity2.get("id", "unknown")
        ]
        merged["metadata"]["content_hash"] = self._compute_content_hash(merged)

        self._stats["entities_merged"] += 1

        self.audit.log_event(
            category=AuditCategory.DATA,
            level=AuditLevel.STANDARD,
            operation="entities_merged",
            actor="NORMALIZATION_MODULE",
            details={
                "entity1_id": entity1.get("id"),
                "entity2_id": entity2.get("id"),
                "merged_id": merged.get("id")
            }
        )

        return merged

    def _validate_data_quality(self, data: dict[str, Any], data_type: str) -> None:
        """
        Validate data quality against thresholds.
        
        Args:
            data: Data to validate
            data_type: Type of data (organization, claim, opinion)
            
        Raises:
            DataQualityError: If quality is insufficient
        """
        quality_score = self._compute_quality_score(data)
        min_quality = self.data_quality_thresholds.get("min_quality_score", 0.5)

        if quality_score < min_quality:
            raise DataQualityError(
                f"Data quality insufficient: {quality_score} < {min_quality}"
            )

    def _compute_quality_score(self, data: dict[str, Any]) -> float:
        """
        Compute quality score for data object.
        
        Args:
            data: Data object
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        score = 0.0
        checks = 0

        # Check for required fields
        required_fields = ["id", "name"] if "name" in data else ["id"]
        for field in required_fields:
            checks += 1
            if field in data and data[field]:
                score += 1.0

        # Check for optional enrichment fields
        enrichment_fields = ["description", "type", "attributes", "metadata"]
        for field in enrichment_fields:
            checks += 1
            if field in data and data[field]:
                score += 0.5

        # Check for data completeness
        if data:
            checks += 1
            filled_fields = sum(1 for v in data.values() if v)
            completeness = filled_fields / len(data)
            score += completeness

        return score / checks if checks > 0 else 0.0

    def _normalize_id(self, raw_id: Any) -> str:
        """Normalize ID field."""
        if not raw_id:
            return f"UNKNOWN-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        # Convert to string and clean
        id_str = str(raw_id).strip().upper()
        # Remove invalid characters
        id_str = re.sub(r'[^A-Z0-9_-]', '', id_str)

        return id_str if id_str else f"INVALID-{hash(raw_id)}"

    def _normalize_text(self, text: str, capitalize: bool = False,
                        strip_html: bool = False) -> str:
        """Normalize text field."""
        if not text:
            return ""

        # Strip HTML if requested
        if strip_html:
            text = re.sub(r'<[^>]+>', '', text)

        # Normalize whitespace
        text = ' '.join(text.split())

        # Capitalize if requested
        if capitalize:
            text = text.title()

        return text.strip()

    def _normalize_type(self, raw_type: str) -> str:
        """Normalize entity type."""
        if not raw_type:
            return "unknown"

        # Standardize common type variations
        type_map = {
            "org": "organization",
            "company": "organization",
            "corp": "organization",
            "govt": "government",
            "gov": "government",
            "ngo": "non_governmental",
            "intl": "international"
        }

        normalized = str(raw_type).lower().strip()
        return type_map.get(normalized, normalized)

    def _normalize_date(self, raw_date: Any) -> str | None:
        """Normalize date to ISO 8601 format."""
        if not raw_date:
            return None

        # If already a string in ISO format, return it
        if isinstance(raw_date, str):
            # Basic ISO format validation
            if re.match(r'\d{4}-\d{2}-\d{2}', raw_date):
                return raw_date

        # Try to parse common formats
        try:
            if isinstance(raw_date, datetime):
                return raw_date.isoformat()
            # Add more parsing logic as needed
            return str(raw_date)
        except Exception:
            logger.warning(f"Could not normalize date: {raw_date}")
            return None

    def _normalize_jurisdiction(self, raw_jurisdiction: Any) -> str | None:
        """Normalize jurisdiction/country codes."""
        if not raw_jurisdiction:
            return None

        # Convert to uppercase and clean
        jurisdiction = str(raw_jurisdiction).strip().upper()

        # Validate ISO country code format (2 or 3 letters)
        if re.match(r'^[A-Z]{2,3}$', jurisdiction):
            return jurisdiction

        return jurisdiction

    def _normalize_attributes(self, raw_attributes: dict[str, Any]) -> dict[str, Any]:
        """Normalize attributes dictionary."""
        if not raw_attributes:
            return {}

        normalized = {}
        for key, value in raw_attributes.items():
            # Normalize key
            norm_key = key.lower().strip().replace(' ', '_')

            # Normalize value based on type
            if isinstance(value, str):
                normalized[norm_key] = self._normalize_text(value)
            elif isinstance(value, (int, float, bool)):
                normalized[norm_key] = value
            elif isinstance(value, list):
                normalized[norm_key] = [self._normalize_text(str(v)) for v in value]
            else:
                normalized[norm_key] = str(value)

        return normalized

    def _normalize_relationships(self, raw_relationships: list[Any]) -> list[dict[str, Any]]:
        """Normalize relationships list."""
        if not raw_relationships:
            return []

        normalized = []
        for rel in raw_relationships:
            if isinstance(rel, dict):
                normalized_rel = {
                    "target_id": self._normalize_id(rel.get("target_id")),
                    "type": self._normalize_type(rel.get("type", "unknown")),
                    "strength": self._normalize_confidence(rel.get("strength", 0.5))
                }
                normalized.append(normalized_rel)

        return normalized

    def _normalize_topics(self, raw_topics: list[Any]) -> list[str]:
        """Normalize topics list."""
        if not raw_topics:
            return []

        topics = []
        for topic in raw_topics:
            normalized = self._normalize_text(str(topic)).lower()
            if normalized and normalized not in topics:
                topics.append(normalized)

        return topics

    def _normalize_veracity(self, raw_veracity: Any) -> str:
        """Normalize veracity status."""
        veracity_map = {
            "true": "verified_true",
            "false": "verified_false",
            "disputed": "disputed",
            "unverified": "unverified",
            "unknown": "unverified"
        }

        if not raw_veracity:
            return "unverified"

        normalized = str(raw_veracity).lower().strip()
        return veracity_map.get(normalized, "unverified")

    def _normalize_evidence(self, raw_evidence: list[Any]) -> list[dict[str, Any]]:
        """Normalize evidence list."""
        if not raw_evidence:
            return []

        normalized = []
        for evidence in raw_evidence:
            if isinstance(evidence, dict):
                normalized_ev = {
                    "source": self._normalize_text(evidence.get("source", "")),
                    "credibility": self._normalize_confidence(evidence.get("credibility", 0.5)),
                    "url": evidence.get("url", "")
                }
                normalized.append(normalized_ev)

        return normalized

    def _normalize_sentiment(self, raw_sentiment: Any) -> float:
        """Normalize sentiment to [-1.0, 1.0] range."""
        if raw_sentiment is None:
            return 0.0

        try:
            sentiment = float(raw_sentiment)
            return max(-1.0, min(1.0, sentiment))
        except (ValueError, TypeError):
            # Try to parse text sentiment
            sentiment_map = {
                "positive": 0.7,
                "negative": -0.7,
                "neutral": 0.0,
                "very_positive": 1.0,
                "very_negative": -1.0
            }
            normalized = str(raw_sentiment).lower().strip()
            return sentiment_map.get(normalized, 0.0)

    def _normalize_confidence(self, raw_confidence: Any) -> float:
        """Normalize confidence to [0.0, 1.0] range."""
        if raw_confidence is None:
            return 0.5

        try:
            confidence = float(raw_confidence)
            return max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            return 0.5

    def _compute_content_hash(self, data: dict[str, Any]) -> str:
        """
        Compute SHA-256 hash of content for deduplication.
        
        Args:
            data: Data object
            
        Returns:
            Hex-encoded SHA-256 hash
        """
        # Create copy without metadata for hashing
        hashable = {k: v for k, v in data.items() if k != "metadata"}

        # Serialize deterministically
        json_str = json.dumps(hashable, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    def get_statistics(self) -> dict[str, Any]:
        """Get normalization statistics."""
        return dict(self._stats)

    def reset_statistics(self) -> None:
        """Reset statistics counters."""
        self._stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "duplicates_removed": 0,
            "entities_merged": 0
        }


if __name__ == "__main__":
    # Test normalization module
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    try:
        normalizer = Normalizer()

        # Test organization normalization
        raw_org = {
            "id": "org-001",
            "name": "test organization",
            "type": "company",
            "description": "A test organization for ATLAS",
            "founded": "2020-01-01",
            "jurisdiction": "us",
            "attributes": {
                "Industry": "Technology",
                "Size": "Large"
            },
            "relationships": [
                {"target_id": "org-002", "type": "partner", "strength": 0.8}
            ],
            "source": "test"
        }

        normalized = normalizer.normalize_organization(raw_org)
        print("Normalized Organization:")
        print(json.dumps(normalized, indent=2))

        # Test claim normalization
        raw_claim = {
            "id": "claim-001",
            "text": "Test claim statement",
            "claimant": "org-001",
            "date": "2024-01-01",
            "topics": ["technology", "innovation"],
            "veracity": "unverified",
            "evidence": [],
            "source": "test"
        }

        normalized_claim = normalizer.normalize_claim(raw_claim)
        print("\nNormalized Claim:")
        print(json.dumps(normalized_claim, indent=2))

        # Test deduplication
        entities = [normalized, dict(normalized)]  # Duplicate
        deduplicated = normalizer.deduplicate(entities)
        print(f"\nDeduplication: {len(entities)} -> {len(deduplicated)}")

        # Print statistics
        print("\nStatistics:")
        print(json.dumps(normalizer.get_statistics(), indent=2))

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise
