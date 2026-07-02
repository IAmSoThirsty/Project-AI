"""Integration test: Atlas SchemaValidator (J5.3).

Per docs/internal/J5_DISCOVERY.md Phase J5.3: the
SchemaValidator is a production-grade Draft-07 JSON Schema
validator for PROJECT ATLAS. It loads + caches all canonical
schemas with SHA-256 integrity hashing, validates data
objects with detailed error reporting, and provides
deterministic provenance hashing.

6 JSON schemas:
- claim.schema.json (factual claims)
- influence_graph.schema.json (influence graph)
- opinion.schema.json (opinions)
- organization.schema.json (organizations)
- projection_pack.schema.json (projection packs)
- world_state.schema.json (world state snapshots)

Honest scope:
- Tests the public surface: ValidationError,
  SchemaValidator, get_schema_validator,
  reset_schema_validator.
- Tests schema loading from default + custom directories.
- Tests get_schema/get_schema_hash/get_all_schema_names/
  get_all_schema_hashes for all 6 schemas.
- Tests validate (strict + non-strict), the 6 typed
  validate_* helpers, and validate_any.
- Tests verify_integrity (passes on unmodified canonical
  schema files).
- Tests compute_data_hash determinism (key-order
  insensitive) and add_metadata provenance injection.
- Tests that get_schema() returns a copy (mutation safety).
- Tests singleton factory + reset.
- Does NOT test format-keyword enforcement (date-time, uri):
  the validator is constructed without a FormatChecker, so
  format annotations are NOT enforced - failures are driven
  via required/pattern/enum/additionalProperties instead.
- Does NOT test schema-modification detection paths (would
  require mutating canonical schema files on disk).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from atlas.schemas.validator import (
    SchemaValidator,
    ValidationError,
    get_schema_validator,
    reset_schema_validator,
)

EXPECTED_SCHEMAS = {
    "claim",
    "influence_graph",
    "opinion",
    "organization",
    "projection_pack",
    "world_state",
}


def _valid_claim() -> dict[str, Any]:
    """Minimal claim satisfying claim.schema.json."""
    return {
        "id": "CLM-ABCDEF0123456789",
        "statement": "Test claim statement.",
        "claimant_id": "ORG-ABCDEF0123456789",
        "timestamp": "2026-07-02T00:00:00Z",
        "category": "economic",
        "metadata": {
            "created_at": "2026-07-02T00:00:00Z",
            "updated_at": "2026-07-02T00:00:00Z",
            "version": 1,
            "hash": "a" * 64,
        },
    }


# ── 1. Errors ───────────────────────────────────


def test_validation_error_is_exception() -> None:
    """ValidationError inherits from Exception."""
    assert issubclass(ValidationError, Exception)


# ── 2. SchemaValidator creation ─────────────────


def test_schema_validator_creation_default_dir() -> None:
    """SchemaValidator can be created with default schema dir."""
    validator = SchemaValidator()
    assert validator.schema_dir.exists()
    # Should have loaded all 6 schemas
    assert len(validator._schemas) == 6


def test_schema_validator_creation_with_custom_dir() -> None:
    """SchemaValidator can be created with a custom dir."""
    # Use the default schema dir (already validated)
    default = Path(__file__).parent.parent / "packages" / "atlas" / "src" / "atlas" / "schemas"
    validator = SchemaValidator(schema_dir=default)
    assert validator.schema_dir == default
    assert len(validator._schemas) == 6


def test_schema_validator_creation_missing_dir_raises() -> None:
    """SchemaValidator raises ValidationError on missing dir."""
    with pytest.raises(ValidationError, match="not found"):
        SchemaValidator(schema_dir=Path("/nonexistent/path/xyz"))


# ── 3. Schema access ────────────────────────────


def test_get_all_schema_names() -> None:
    """get_all_schema_names() returns all 6 expected names."""
    validator = SchemaValidator()
    assert set(validator.get_all_schema_names()) == EXPECTED_SCHEMAS


def test_get_schema_returns_dict() -> None:
    """get_schema() returns the parsed Draft-07 schema."""
    validator = SchemaValidator()
    schema = validator.get_schema("claim")
    assert isinstance(schema, dict)
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert "$id" in schema


def test_get_schema_returns_copy() -> None:
    """get_schema() returns a copy (mutation safe)."""
    validator = SchemaValidator()
    s1 = validator.get_schema("claim")
    s1["__mutated__"] = True
    s2 = validator.get_schema("claim")
    assert "__mutated__" not in s2


def test_get_schema_unknown_raises() -> None:
    """get_schema() raises ValidationError for unknown schema."""
    validator = SchemaValidator()
    with pytest.raises(ValidationError, match="not found"):
        validator.get_schema("nonexistent_schema")


# ── 4. Hashes ───────────────────────────────────


def test_get_schema_hash_returns_64_hex() -> None:
    """get_schema_hash() returns 64-char hex string."""
    validator = SchemaValidator()
    h = validator.get_schema_hash("claim")
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_get_all_schema_hashes_returns_all_6() -> None:
    """get_all_schema_hashes() returns hashes for all 6 schemas."""
    validator = SchemaValidator()
    hashes = validator.get_all_schema_hashes()
    assert set(hashes.keys()) == EXPECTED_SCHEMAS


def test_get_schema_hash_unknown_raises() -> None:
    """get_schema_hash() raises ValidationError for unknown schema."""
    validator = SchemaValidator()
    with pytest.raises(ValidationError, match="not found"):
        validator.get_schema_hash("nonexistent")


# ── 5. Validation ───────────────────────────────


def test_validate_claim_valid_passes() -> None:
    """validate_claim() returns True for a valid claim."""
    validator = SchemaValidator()
    assert validator.validate_claim(_valid_claim()) is True


def test_validate_claim_invalid_strict_raises() -> None:
    """validate_claim() raises ValidationError in strict mode."""
    validator = SchemaValidator()
    bad = _valid_claim()
    bad["category"] = "not_a_valid_category"
    with pytest.raises(ValidationError, match="Validation failed"):
        validator.validate_claim(bad)


def test_validate_non_strict_returns_errors() -> None:
    """validate() non-strict returns (False, error messages)."""
    validator = SchemaValidator()
    is_valid, errors = validator.validate("claim", {}, strict=False)
    assert is_valid is False
    assert errors is not None
    assert len(errors) > 0
    assert all(isinstance(e, str) for e in errors)


def test_validate_all_types_reject_empty() -> None:
    """All 6 typed validate_* helpers reject an empty object."""
    validator = SchemaValidator()
    assert validator.validate_organization({}, strict=False) is False
    assert validator.validate_claim({}, strict=False) is False
    assert validator.validate_opinion({}, strict=False) is False
    assert validator.validate_world_state({}, strict=False) is False
    assert validator.validate_influence_graph({}, strict=False) is False
    assert validator.validate_projection_pack({}, strict=False) is False


def test_validate_any_valid_and_unknown() -> None:
    """validate_any() validates by name; unknown schema raises."""
    validator = SchemaValidator()
    assert validator.validate_any("claim", _valid_claim()) is True
    assert validator.validate_any("claim", {}, strict=False) is False
    with pytest.raises(ValidationError, match="not found"):
        validator.validate_any("nonexistent", {})


# ── 6. Integrity ────────────────────────────────


def test_verify_integrity_true() -> None:
    """verify_integrity() returns True when schemas unchanged."""
    validator = SchemaValidator()
    assert validator.verify_integrity() is True


# ── 7. Provenance ───────────────────────────────


def test_compute_data_hash_deterministic() -> None:
    """compute_data_hash() is deterministic + key-order insensitive."""
    validator = SchemaValidator()
    h1 = validator.compute_data_hash({"a": 1, "b": 2})
    h2 = validator.compute_data_hash({"b": 2, "a": 1})
    assert h1 == h2
    assert len(h1) == 64
    assert all(c in "0123456789abcdef" for c in h1)


def test_add_metadata_injects_fields() -> None:
    """add_metadata() injects created_at/updated_at/version/hash."""
    validator = SchemaValidator()
    data: dict[str, Any] = {"payload": "x"}
    result = validator.add_metadata(data, "claim")
    meta = result["metadata"]
    assert "created_at" in meta
    assert "updated_at" in meta
    assert meta["version"] == 1
    assert len(meta["hash"]) == 64
    # Legacy behavior preserved: mutates input in place
    assert result is data


# ── 8. Metadata ─────────────────────────────────


def test_get_metadata_returns_dict() -> None:
    """get_metadata() returns a dict with expected keys."""
    validator = SchemaValidator()
    meta = validator.get_metadata()
    assert "schema_dir" in meta
    assert "schemas_loaded" in meta
    assert "schema_hashes" in meta
    assert "integrity_verified" in meta
    assert set(meta["schemas_loaded"]) == EXPECTED_SCHEMAS
    assert meta["integrity_verified"] is True


# ── 9. Singleton factory ────────────────────────


def test_get_schema_validator_singleton() -> None:
    """get_schema_validator returns the same instance."""
    reset_schema_validator()
    v1 = get_schema_validator()
    v2 = get_schema_validator()
    assert v1 is v2


def test_reset_schema_validator() -> None:
    """reset_schema_validator clears the singleton."""
    reset_schema_validator()
    v1 = get_schema_validator()
    reset_schema_validator()
    v2 = get_schema_validator()
    # After reset, a new instance is created
    assert v1 is not v2


# ── 10. Public surface completeness ─────────────


def test_public_surface_complete() -> None:
    """All 4 public symbols are exported."""
    import atlas.schemas.validator as m

    expected = {
        "SchemaValidator",
        "ValidationError",
        "get_schema_validator",
        "reset_schema_validator",
    }
    assert expected.issubset(set(m.__all__))
