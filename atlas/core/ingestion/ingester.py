"""
Data Ingestion Module for PROJECT ATLAS Ω

Loads raw data from various sources, validates against schemas, and prepares
for normalization and processing. Implements full tier classification system.

Layer 1 Component - Production-Grade Implementation
"""

import csv
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from atlas.audit.trail import AuditCategory, AuditLevel, get_audit_trail
from atlas.core.ingestion.tier_classifier import (
    TierMetadata,
    get_tier_classifier,
)
from atlas.schemas.validator import get_schema_validator

logger = logging.getLogger(__name__)


class IngestionError(Exception):
    """Raised when data ingestion fails."""

    pass


class DataIngester:
    """
    Production-grade data ingestion system.

    Loads, validates, and processes raw data from multiple sources with
    full audit logging and error handling.
    """

    def __init__(self, data_dir: Path | None = None):
        """
        Initialize data ingester.

        Args:
            data_dir: Path to data directory (defaults to atlas/data)
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "data"

        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)

        # Get validator, audit trail, and tier classifier
        self.validator = get_schema_validator()
        self.audit = get_audit_trail()
        self.tier_classifier = get_tier_classifier()

        logger.info("Initialized DataIngester with data dir: %s", self.data_dir)

        # Log initialization
        self.audit.log_event(
            category=AuditCategory.SYSTEM,
            level=AuditLevel.INFORMATIONAL,
            operation="ingester_initialized",
            actor="DATA_INGESTER",
            details={"data_dir": str(self.data_dir)},
        )

    def ingest_json_file(
        self, filepath: Path, schema_type: str
    ) -> list[dict[str, Any]]:
        """
        Ingest data from a JSON file.

        Args:
            filepath: Path to JSON file
            schema_type: Type of schema to validate against
                        ('organization', 'claim', 'opinion', etc.)

        Returns:
            List of validated data objects

        Raises:
            IngestionError: If ingestion or validation fails
        """
        logger.info("Ingesting JSON file: %s (schema: %s)", filepath, schema_type)

        if not filepath.exists():
            error_msg = f"File not found: {filepath}"
            logger.error(error_msg)
            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.HIGH_PRIORITY,
                operation="ingestion_failed",
                actor="DATA_INGESTER",
                details={"file": str(filepath), "error": error_msg},
            )
            raise IngestionError(error_msg)

        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Compute file hash for provenance
            file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

            # Parse JSON
            data = json.loads(content)

            # Handle both single object and list
            if isinstance(data, dict):
                data_list = [data]
            elif isinstance(data, list):
                data_list = data
            else:
                raise IngestionError(f"Expected dict or list, got {type(data)}")

            # Validate each object
            validated_data = []
            errors = []

            for idx, obj in enumerate(data_list):
                try:
                    # Add metadata if not present
                    obj = self.validator.add_metadata(obj, schema_type)

                    # Add source information
                    if "metadata" in obj:
                        obj["metadata"]["source"] = str(filepath)
                        obj["metadata"]["source_hash"] = file_hash

                    # Validate
                    is_valid, error_msgs = self.validator.validate(
                        schema_type, obj, strict=False
                    )

                    if is_valid:
                        validated_data.append(obj)
                    else:
                        errors.append({"index": idx, "errors": error_msgs})

                except Exception as e:
                    errors.append({"index": idx, "errors": [str(e)]})

            # Log ingestion result
            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.STANDARD if not errors else AuditLevel.HIGH_PRIORITY,
                operation="json_file_ingested",
                actor="DATA_INGESTER",
                details={
                    "file": str(filepath),
                    "schema_type": schema_type,
                    "file_hash": file_hash,
                    "total_objects": len(data_list),
                    "validated": len(validated_data),
                    "errors": len(errors),
                    "error_details": errors if errors else None,
                },
            )

            if errors and not validated_data:
                # All objects failed validation
                raise IngestionError(f"All objects failed validation: {errors}")

            if errors:
                logger.warning(
                    "Ingested %s objects with %s failures",
                    len(validated_data),
                    len(errors),
                )

            logger.info(
                "Successfully ingested %s objects from %s",
                len(validated_data),
                filepath,
            )
            return validated_data

        except json.JSONDecodeError as e:
            error_msg = f"JSON parse error in {filepath}: {e}"
            logger.error(error_msg)
            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.HIGH_PRIORITY,
                operation="ingestion_failed",
                actor="DATA_INGESTER",
                details={"file": str(filepath), "error": error_msg},
            )
            raise IngestionError(error_msg) from e

        except Exception as e:
            error_msg = f"Error ingesting {filepath}: {e}"
            logger.error(error_msg)
            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.HIGH_PRIORITY,
                operation="ingestion_failed",
                actor="DATA_INGESTER",
                details={"file": str(filepath), "error": error_msg},
            )
            raise IngestionError(error_msg) from e

    def ingest_csv_file(
        self, filepath: Path, schema_type: str, mapping: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        """
        Ingest data from a CSV file.

        Args:
            filepath: Path to CSV file
            schema_type: Type of schema to validate against
            mapping: Optional column name mapping (csv_col -> schema_field)

        Returns:
            List of validated data objects
        """
        logger.info("Ingesting CSV file: %s (schema: %s)", filepath, schema_type)

        if not filepath.exists():
            raise IngestionError(f"File not found: {filepath}")

        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

            # Parse CSV
            rows = []
            with open(filepath, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Apply mapping if provided
                    if mapping:
                        mapped_row = {}
                        for csv_col, value in row.items():
                            schema_field = mapping.get(csv_col, csv_col)
                            mapped_row[schema_field] = value
                        rows.append(mapped_row)
                    else:
                        rows.append(dict(row))

            # Convert to appropriate types and validate
            validated_data = []
            errors = []

            for idx, row in enumerate(rows):
                try:
                    # Add metadata
                    obj = self.validator.add_metadata(row, schema_type)

                    if "metadata" in obj:
                        obj["metadata"]["source"] = str(filepath)
                        obj["metadata"]["source_hash"] = file_hash

                    # Validate (non-strict to allow conversion)
                    is_valid, error_msgs = self.validator.validate(
                        schema_type, obj, strict=False
                    )

                    if is_valid:
                        validated_data.append(obj)
                    else:
                        errors.append({"row": idx + 1, "errors": error_msgs})

                except Exception as e:
                    errors.append({"row": idx + 1, "errors": [str(e)]})

            # Log ingestion result
            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.STANDARD if not errors else AuditLevel.HIGH_PRIORITY,
                operation="csv_file_ingested",
                actor="DATA_INGESTER",
                details={
                    "file": str(filepath),
                    "schema_type": schema_type,
                    "file_hash": file_hash,
                    "total_rows": len(rows),
                    "validated": len(validated_data),
                    "errors": len(errors),
                },
            )

            logger.info(
                "Successfully ingested %s objects from CSV", len(validated_data)
            )
            return validated_data

        except Exception as e:
            error_msg = f"Error ingesting CSV {filepath}: {e}"
            logger.error(error_msg)
            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.HIGH_PRIORITY,
                operation="ingestion_failed",
                actor="DATA_INGESTER",
                details={"file": str(filepath), "error": error_msg},
            )
            raise IngestionError(error_msg) from e

    def ingest_directory(
        self, directory: Path, schema_type: str, pattern: str = "*.json"
    ) -> list[dict[str, Any]]:
        """
        Ingest all files matching pattern from a directory.

        Args:
            directory: Directory to scan
            schema_type: Type of schema to validate against
            pattern: File pattern to match (e.g., '*.json', '*.csv')

        Returns:
            List of all validated data objects from all files
        """
        logger.info("Ingesting directory: %s (pattern: %s)", directory, pattern)

        if not directory.exists():
            raise IngestionError(f"Directory not found: {directory}")

        files = list(directory.glob(pattern))

        if not files:
            logger.warning("No files matching %s in %s", pattern, directory)
            return []

        all_data = []
        total_files = len(files)
        successful_files = 0
        failed_files = 0

        for filepath in files:
            try:
                if filepath.suffix == ".json":
                    data = self.ingest_json_file(filepath, schema_type)
                elif filepath.suffix == ".csv":
                    data = self.ingest_csv_file(filepath, schema_type)
                else:
                    logger.warning("Unsupported file type: %s", filepath)
                    continue

                all_data.extend(data)
                successful_files += 1

            except Exception as e:
                logger.error("Failed to ingest %s: %s", filepath, e)
                failed_files += 1

        # Log directory ingestion summary
        self.audit.log_event(
            category=AuditCategory.DATA,
            level=AuditLevel.STANDARD,
            operation="directory_ingested",
            actor="DATA_INGESTER",
            details={
                "directory": str(directory),
                "pattern": pattern,
                "total_files": total_files,
                "successful": successful_files,
                "failed": failed_files,
                "total_objects": len(all_data),
            },
        )

        logger.info(
            f"Directory ingestion complete: {successful_files}/{total_files} files, "
            f"{len(all_data)} total objects"
        )

        return all_data

    def save_raw_data(self, data: list[dict[str, Any]], filename: str) -> Path:
        """
        Save raw data to file.

        Args:
            data: Data objects to save
            filename: Output filename

        Returns:
            Path to saved file
        """
        output_path = self.raw_dir / filename

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, sort_keys=True)

            # Compute hash
            with open(output_path, encoding="utf-8") as f:
                content = f.read()
            file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

            # Log save operation
            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.STANDARD,
                operation="raw_data_saved",
                actor="DATA_INGESTER",
                details={
                    "file": str(output_path),
                    "objects": len(data),
                    "file_hash": file_hash,
                },
            )

            logger.info("Saved %s objects to %s", len(data), output_path)
            return output_path

        except Exception as e:
            logger.error("Failed to save data to %s: %s", output_path, e)
            raise IngestionError(f"Failed to save data: {e}") from e

    def ingest_with_tier_classification(
        self,
        filepath: Path,
        schema_type: str,
        source_name: str,
        source_type: str,
        geographic_scope: str = "global",
        **tier_kwargs,
    ) -> tuple[list[dict[str, Any]], list[TierMetadata]]:
        """
        Ingest data with full tier classification and validation.

        This is the production method that enforces:
        - Four-tier classification (TierA/B/C/D)
        - Confidence weighting
        - "No hash → no inclusion" rule
        - Complete provenance tracking

        Args:
            filepath: Path to data file
            schema_type: Schema to validate against
            source_name: Name of data source
            source_type: Type of source (e.g., "peer_reviewed_journal")
            geographic_scope: Geographic scope (e.g., "global", "US", "EU")
            **tier_kwargs: Additional tier metadata (peer_reviewed, citation_count, etc.)

        Returns:
            (validated_data, tier_metadata_list)

        Raises:
            IngestionError: If ingestion fails or data excluded by tier rules
        """
        logger.info(
            f"Ingesting with tier classification: {filepath} "
            f"(source: {source_name}, type: {source_type})"
        )

        # Read file content
        if not filepath.exists():
            raise IngestionError(f"File not found: {filepath}")

        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Create tier metadata
        tier_metadata = self.tier_classifier.create_tier_metadata(
            content=content,
            source_name=source_name,
            source_type=source_type,
            timestamp=datetime.utcnow(),
            geographic_scope=geographic_scope,
            **tier_kwargs,
        )

        # Enforce inclusion rule ("No hash → no inclusion")
        if not self.tier_classifier.enforce_inclusion_rule(tier_metadata):
            error_msg = (
                f"Data from {source_name} excluded by tier classification rules. "
                f"Errors: {tier_metadata.validation_errors}"
            )
            logger.error(error_msg)
            raise IngestionError(error_msg)

        # Ingest the data
        try:
            if filepath.suffix == ".json":
                data = self.ingest_json_file(filepath, schema_type)
            elif filepath.suffix == ".csv":
                data = self.ingest_csv_file(filepath, schema_type)
            else:
                raise IngestionError(f"Unsupported file type: {filepath.suffix}")
        except Exception as e:
            logger.error("Ingestion failed for %s: %s", filepath, e)
            raise

        # Attach tier metadata to each object
        tier_metadata_list = []
        for obj in data:
            if "tier_metadata" not in obj:
                obj["tier_metadata"] = tier_metadata.to_dict()
            tier_metadata_list.append(tier_metadata)

        # Log successful tier-classified ingestion
        self.audit.log_event(
            category=AuditCategory.DATA,
            level=AuditLevel.INFORMATIONAL,
            operation="tier_classified_ingestion",
            actor="DATA_INGESTER",
            details={
                "file": str(filepath),
                "source_name": source_name,
                "source_type": source_type,
                "tier": tier_metadata.tier.value,
                "confidence_weight": tier_metadata.confidence_weight,
                "objects_ingested": len(data),
                "validation_passed": tier_metadata.validation_passed,
            },
        )

        logger.info(
            f"Successfully ingested {len(data)} objects from {filepath} "
            f"(Tier: {tier_metadata.tier.value}, "
            f"Confidence: {tier_metadata.confidence_weight})"
        )

        return data, tier_metadata_list

    def get_statistics(self) -> dict[str, Any]:
        """Get ingestion statistics from audit trail."""
        events = self.audit.get_events(
            category=AuditCategory.DATA, operation="json_file_ingested"
        )

        tier_events = self.audit.get_events(
            category=AuditCategory.DATA, operation="tier_classified_ingestion"
        )

        total_objects = sum(e.details.get("validated", 0) for e in events)
        total_errors = sum(e.details.get("errors", 0) for e in events)

        # Tier statistics
        tier_stats = {}
        for event in tier_events:
            tier = event.details.get("tier", "unknown")
            tier_stats[tier] = tier_stats.get(tier, 0) + event.details.get(
                "objects_ingested", 0
            )

        return {
            "total_ingestions": len(events),
            "total_objects": total_objects,
            "total_errors": total_errors,
            "success_rate": (
                total_objects / (total_objects + total_errors)
                if total_objects + total_errors > 0
                else 0
            ),
            "tier_classified_ingestions": len(tier_events),
            "objects_by_tier": tier_stats,
            "tier_classifier_stats": self.tier_classifier.get_tier_statistics(),
        }


if __name__ == "__main__":
    # Test data ingestion
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    ingester = DataIngester()
    print("DataIngester initialized successfully!")
    print("\nStatistics:")
    print(json.dumps(ingester.get_statistics(), indent=2))
