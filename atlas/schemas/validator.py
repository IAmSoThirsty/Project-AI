"""
Schema Validator for PROJECT ATLAS

Validates all data objects against canonical JSON schemas with full error
reporting and audit logging.

Production-grade with comprehensive validation and security checks.
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft7Validator

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when data validation fails."""
    pass


class SchemaValidator:
    """
    Production-grade schema validator for PROJECT ATLAS.
    
    Loads and caches JSON schemas, validates data objects, and provides
    detailed error reporting.
    """

    def __init__(self, schema_dir: Path | None = None):
        """
        Initialize schema validator.
        
        Args:
            schema_dir: Path to schema directory (defaults to atlas/schemas)
        """
        if schema_dir is None:
            # Default to atlas/schemas (this file is already in schemas directory)
            schema_dir = Path(__file__).parent

        self.schema_dir = Path(schema_dir)
        if not self.schema_dir.exists():
            raise ValidationError(f"Schema directory not found: {self.schema_dir}")

        self._schemas: dict[str, dict[str, Any]] = {}
        self._validators: dict[str, Draft7Validator] = {}
        self._schema_hashes: dict[str, str] = {}

        logger.info(f"Initializing SchemaValidator with directory: {self.schema_dir}")

        # Load all schemas
        self._load_all_schemas()

        logger.info(f"Loaded {len(self._schemas)} schemas successfully")

    def _load_all_schemas(self) -> None:
        """Load all JSON schema files."""
        schema_files = {
            "organization": "organization.schema.json",
            "claim": "claim.schema.json",
            "opinion": "opinion.schema.json",
            "world_state": "world_state.schema.json",
            "influence_graph": "influence_graph.schema.json",
            "projection_pack": "projection_pack.schema.json"
        }

        for schema_name, filename in schema_files.items():
            filepath = self.schema_dir / filename
            try:
                self._load_schema(schema_name, filepath)
            except Exception as e:
                logger.error(f"Failed to load schema {filename}: {e}")
                raise ValidationError(f"Failed to load schema {filename}: {e}") from e

    def _load_schema(self, name: str, filepath: Path) -> None:
        """
        Load a single JSON schema.
        
        Args:
            name: Schema name (e.g., 'organization')
            filepath: Path to schema file
        """
        logger.debug(f"Loading schema: {name} from {filepath}")

        if not filepath.exists():
            raise ValidationError(f"Schema file not found: {filepath}")

        try:
            with open(filepath, encoding='utf-8') as f:
                content = f.read()

            # Compute hash for integrity
            schema_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            self._schema_hashes[name] = schema_hash

            # Parse JSON
            schema = json.loads(content)

            # Validate that it's a valid JSON Schema
            Draft7Validator.check_schema(schema)

            # Create validator
            validator = Draft7Validator(schema)

            self._schemas[name] = schema
            self._validators[name] = validator

            logger.debug(f"Loaded schema {name} (hash: {schema_hash[:16]}...)")

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error in {filepath}: {e}")
            raise ValidationError(f"JSON parse error in {filepath}: {e}") from e
        except jsonschema.SchemaError as e:
            logger.error(f"Invalid JSON schema in {filepath}: {e}")
            raise ValidationError(f"Invalid JSON schema in {filepath}: {e}") from e
        except Exception as e:
            logger.error(f"Error loading schema {filepath}: {e}")
            raise ValidationError(f"Error loading schema {filepath}: {e}") from e

    def validate(self, schema_name: str, data: dict[str, Any],
                 strict: bool = True) -> tuple[bool, list[str] | None]:
        """
        Validate data against a schema.
        
        Args:
            schema_name: Name of schema to validate against
            data: Data object to validate
            strict: If True, raise exception on validation failure
            
        Returns:
            Tuple of (is_valid, error_messages)
            
        Raises:
            ValidationError: If schema not found or validation fails (strict mode)
        """
        if schema_name not in self._validators:
            raise ValidationError(f"Schema not found: {schema_name}")

        validator = self._validators[schema_name]
        errors = list(validator.iter_errors(data))

        if errors:
            error_messages = []
            for error in errors:
                path = " -> ".join(str(p) for p in error.path) if error.path else "root"
                message = f"{path}: {error.message}"
                error_messages.append(message)
                logger.debug(f"Validation error in {schema_name}: {message}")

            if strict:
                error_summary = "\n".join(error_messages)
                raise ValidationError(
                    f"Validation failed for {schema_name}:\n{error_summary}"
                )

            return False, error_messages

        return True, None

    def validate_organization(self, org: dict[str, Any], strict: bool = True) -> bool:
        """Validate an Organization object."""
        is_valid, errors = self.validate("organization", org, strict)
        return is_valid

    def validate_claim(self, claim: dict[str, Any], strict: bool = True) -> bool:
        """Validate a Claim object."""
        is_valid, errors = self.validate("claim", claim, strict)
        return is_valid

    def validate_opinion(self, opinion: dict[str, Any], strict: bool = True) -> bool:
        """Validate an Opinion object."""
        is_valid, errors = self.validate("opinion", opinion, strict)
        return is_valid

    def validate_world_state(self, world_state: dict[str, Any], strict: bool = True) -> bool:
        """Validate a WorldState object."""
        is_valid, errors = self.validate("world_state", world_state, strict)
        return is_valid

    def validate_influence_graph(self, graph: dict[str, Any], strict: bool = True) -> bool:
        """Validate an InfluenceGraph object."""
        is_valid, errors = self.validate("influence_graph", graph, strict)
        return is_valid

    def validate_projection_pack(self, pack: dict[str, Any], strict: bool = True) -> bool:
        """Validate a ProjectionPack object."""
        is_valid, errors = self.validate("projection_pack", pack, strict)
        return is_valid

    def get_schema(self, schema_name: str) -> dict[str, Any]:
        """
        Get a schema by name.
        
        Args:
            schema_name: Name of schema
            
        Returns:
            Schema dictionary
            
        Raises:
            ValidationError: If schema not found
        """
        if schema_name not in self._schemas:
            raise ValidationError(f"Schema not found: {schema_name}")

        # Return a copy to prevent modification
        return dict(self._schemas[schema_name])

    def get_schema_hash(self, schema_name: str) -> str:
        """
        Get the SHA-256 hash of a schema.
        
        Args:
            schema_name: Name of schema
            
        Returns:
            Hex-encoded SHA-256 hash
        """
        if schema_name not in self._schema_hashes:
            raise ValidationError(f"Schema not found: {schema_name}")

        return self._schema_hashes[schema_name]

    def get_all_schema_names(self) -> list[str]:
        """Get names of all loaded schemas."""
        return list(self._schemas.keys())

    def get_all_schema_hashes(self) -> dict[str, str]:
        """Get hashes of all schemas for audit trail."""
        return dict(self._schema_hashes)

    def verify_integrity(self) -> bool:
        """
        Verify that schemas have not been modified.
        
        Returns:
            True if all schemas are unchanged, False otherwise
        """
        for schema_name, original_hash in self._schema_hashes.items():
            filename = f"{schema_name}.schema.json"
            filepath = self.schema_dir / filename

            try:
                with open(filepath, encoding='utf-8') as f:
                    content = f.read()

                current_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

                if current_hash != original_hash:
                    logger.error(
                        f"Schema {schema_name} has been modified! "
                        f"Original: {original_hash}, Current: {current_hash}"
                    )
                    return False

            except Exception as e:
                logger.error(f"Error verifying schema {schema_name}: {e}")
                return False

        return True

    def compute_data_hash(self, data: dict[str, Any]) -> str:
        """
        Compute SHA-256 hash of data object for provenance.
        
        Args:
            data: Data object
            
        Returns:
            Hex-encoded SHA-256 hash
        """
        # Serialize deterministically (sorted keys)
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    def add_metadata(self, data: dict[str, Any], schema_name: str) -> dict[str, Any]:
        """
        Add metadata fields to data object.
        
        Args:
            data: Data object
            schema_name: Schema being validated against
            
        Returns:
            Data object with metadata added
        """
        now = datetime.utcnow().isoformat()

        if "metadata" not in data:
            data["metadata"] = {}

        metadata = data["metadata"]

        # Add timestamps if not present
        if "created_at" not in metadata:
            metadata["created_at"] = now

        metadata["updated_at"] = now

        # Add version if not present
        if "version" not in metadata:
            metadata["version"] = 1

        # Compute and add hash
        # Temporarily remove hash to compute it
        old_hash = metadata.pop("hash", None)
        data_hash = self.compute_data_hash(data)
        metadata["hash"] = data_hash

        return data

    def get_metadata(self) -> dict[str, Any]:
        """Get metadata about loaded schemas."""
        return {
            "schema_dir": str(self.schema_dir),
            "schemas_loaded": self.get_all_schema_names(),
            "schema_hashes": self._schema_hashes,
            "integrity_verified": self.verify_integrity()
        }


# Singleton instance for application-wide access
_global_schema_validator: SchemaValidator | None = None


def get_schema_validator(schema_dir: Path | None = None) -> SchemaValidator:
    """
    Get the global schema validator instance.
    
    Args:
        schema_dir: Schema directory (only used on first call)
        
    Returns:
        SchemaValidator instance
    """
    global _global_schema_validator

    if _global_schema_validator is None:
        _global_schema_validator = SchemaValidator(schema_dir)

    return _global_schema_validator


def reset_schema_validator() -> None:
    """Reset the global schema validator (for testing)."""
    global _global_schema_validator
    _global_schema_validator = None


if __name__ == "__main__":
    # Test schema loading and validation
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    try:
        validator = SchemaValidator()
        print("Schemas loaded successfully!")
        print("\nLoaded schemas:", validator.get_all_schema_names())
        print("\nMetadata:")
        print(json.dumps(validator.get_metadata(), indent=2))

    except Exception as e:
        print(f"Error: {e}")
        raise
