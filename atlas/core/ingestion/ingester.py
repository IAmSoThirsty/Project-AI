"""
Data Ingestion Module for PROJECT ATLAS

Loads raw data from various sources, validates against schemas, and prepares
for normalization and processing.

Production-grade with comprehensive error handling, validation, and audit logging.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import csv

from atlas.schemas.validator import get_schema_validator, ValidationError
from atlas.audit.trail import get_audit_trail, AuditCategory, AuditLevel

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
    
    def __init__(self, data_dir: Optional[Path] = None):
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
        
        # Get validator and audit trail
        self.validator = get_schema_validator()
        self.audit = get_audit_trail()
        
        logger.info(f"Initialized DataIngester with data dir: {self.data_dir}")
        
        # Log initialization
        self.audit.log_event(
            category=AuditCategory.SYSTEM,
            level=AuditLevel.INFORMATIONAL,
            operation="ingester_initialized",
            actor="DATA_INGESTER",
            details={"data_dir": str(self.data_dir)}
        )
    
    def ingest_json_file(self, filepath: Path, schema_type: str) -> List[Dict[str, Any]]:
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
        logger.info(f"Ingesting JSON file: {filepath} (schema: {schema_type})")
        
        if not filepath.exists():
            error_msg = f"File not found: {filepath}"
            logger.error(error_msg)
            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.HIGH_PRIORITY,
                operation="ingestion_failed",
                actor="DATA_INGESTER",
                details={"file": str(filepath), "error": error_msg}
            )
            raise IngestionError(error_msg)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Compute file hash for provenance
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
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
                    is_valid, error_msgs = self.validator.validate(schema_type, obj, strict=False)
                    
                    if is_valid:
                        validated_data.append(obj)
                    else:
                        errors.append({
                            "index": idx,
                            "errors": error_msgs
                        })
                        
                except Exception as e:
                    errors.append({
                        "index": idx,
                        "errors": [str(e)]
                    })
            
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
                    "error_details": errors if errors else None
                }
            )
            
            if errors and not validated_data:
                # All objects failed validation
                raise IngestionError(f"All objects failed validation: {errors}")
            
            if errors:
                logger.warning(f"Ingested {len(validated_data)} objects with {len(errors)} failures")
            
            logger.info(f"Successfully ingested {len(validated_data)} objects from {filepath}")
            return validated_data
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON parse error in {filepath}: {e}"
            logger.error(error_msg)
            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.HIGH_PRIORITY,
                operation="ingestion_failed",
                actor="DATA_INGESTER",
                details={"file": str(filepath), "error": error_msg}
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
                details={"file": str(filepath), "error": error_msg}
            )
            raise IngestionError(error_msg) from e
    
    def ingest_csv_file(self, filepath: Path, schema_type: str,
                       mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Ingest data from a CSV file.
        
        Args:
            filepath: Path to CSV file
            schema_type: Type of schema to validate against
            mapping: Optional column name mapping (csv_col -> schema_field)
            
        Returns:
            List of validated data objects
        """
        logger.info(f"Ingesting CSV file: {filepath} (schema: {schema_type})")
        
        if not filepath.exists():
            raise IngestionError(f"File not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            # Parse CSV
            rows = []
            with open(filepath, 'r', encoding='utf-8') as f:
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
                    is_valid, error_msgs = self.validator.validate(schema_type, obj, strict=False)
                    
                    if is_valid:
                        validated_data.append(obj)
                    else:
                        errors.append({
                            "row": idx + 1,
                            "errors": error_msgs
                        })
                        
                except Exception as e:
                    errors.append({
                        "row": idx + 1,
                        "errors": [str(e)]
                    })
            
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
                    "errors": len(errors)
                }
            )
            
            logger.info(f"Successfully ingested {len(validated_data)} objects from CSV")
            return validated_data
            
        except Exception as e:
            error_msg = f"Error ingesting CSV {filepath}: {e}"
            logger.error(error_msg)
            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.HIGH_PRIORITY,
                operation="ingestion_failed",
                actor="DATA_INGESTER",
                details={"file": str(filepath), "error": error_msg}
            )
            raise IngestionError(error_msg) from e
    
    def ingest_directory(self, directory: Path, schema_type: str,
                        pattern: str = "*.json") -> List[Dict[str, Any]]:
        """
        Ingest all files matching pattern from a directory.
        
        Args:
            directory: Directory to scan
            schema_type: Type of schema to validate against
            pattern: File pattern to match (e.g., '*.json', '*.csv')
            
        Returns:
            List of all validated data objects from all files
        """
        logger.info(f"Ingesting directory: {directory} (pattern: {pattern})")
        
        if not directory.exists():
            raise IngestionError(f"Directory not found: {directory}")
        
        files = list(directory.glob(pattern))
        
        if not files:
            logger.warning(f"No files matching {pattern} in {directory}")
            return []
        
        all_data = []
        total_files = len(files)
        successful_files = 0
        failed_files = 0
        
        for filepath in files:
            try:
                if filepath.suffix == '.json':
                    data = self.ingest_json_file(filepath, schema_type)
                elif filepath.suffix == '.csv':
                    data = self.ingest_csv_file(filepath, schema_type)
                else:
                    logger.warning(f"Unsupported file type: {filepath}")
                    continue
                
                all_data.extend(data)
                successful_files += 1
                
            except Exception as e:
                logger.error(f"Failed to ingest {filepath}: {e}")
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
                "total_objects": len(all_data)
            }
        )
        
        logger.info(
            f"Directory ingestion complete: {successful_files}/{total_files} files, "
            f"{len(all_data)} total objects"
        )
        
        return all_data
    
    def save_raw_data(self, data: List[Dict[str, Any]], filename: str) -> Path:
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
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, sort_keys=True)
            
            # Compute hash
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            # Log save operation
            self.audit.log_event(
                category=AuditCategory.DATA,
                level=AuditLevel.STANDARD,
                operation="raw_data_saved",
                actor="DATA_INGESTER",
                details={
                    "file": str(output_path),
                    "objects": len(data),
                    "file_hash": file_hash
                }
            )
            
            logger.info(f"Saved {len(data)} objects to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to save data to {output_path}: {e}")
            raise IngestionError(f"Failed to save data: {e}") from e
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get ingestion statistics from audit trail."""
        events = self.audit.get_events(
            category=AuditCategory.DATA,
            operation="json_file_ingested"
        )
        
        total_objects = sum(e.details.get("validated", 0) for e in events)
        total_errors = sum(e.details.get("errors", 0) for e in events)
        
        return {
            "total_ingestions": len(events),
            "total_objects": total_objects,
            "total_errors": total_errors,
            "success_rate": total_objects / (total_objects + total_errors) if total_objects + total_errors > 0 else 0
        }


if __name__ == "__main__":
    # Test data ingestion
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    ingester = DataIngester()
    print("DataIngester initialized successfully!")
    print("\nStatistics:")
    print(json.dumps(ingester.get_statistics(), indent=2))
