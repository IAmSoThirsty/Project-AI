"""Regression tests for ratified-manifest internal consistency.

The 1.1.0 ratified artifact asserts `standard.status: ratified` and
`implementation_status.owner_ratification_verified: true` while simultaneously
carrying `lifecycle.ratification.status: pending_owner_signature` and prose saying
ratification "remains pending". `prepare_ratified_manifest()` updated five fields
and left every field that *describes* ratification status untouched.

Because the Ed25519 record binds the raw file bytes, that contradiction cannot be
corrected in place -- editing one character invalidates the signature. The defect
had to be caught before signing, so these tests pin the preparation contract.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from thirstys_standard_runtime.authority import AuthorityError
from thirstys_standard_runtime.ratification import (
    RATIFIED_IMPLEMENTATION_STATEMENT,
    prepare_ratified_manifest,
)

PACKAGE_ROOT = Path(__file__).parents[1]
DRAFT = PACKAGE_ROOT / "thirstys-standard-v3q.manifest.yaml"
RATIFIED = PACKAGE_ROOT / "thirstys-standard-v3q.ratified.manifest.yaml"
SUCCESSOR = PACKAGE_ROOT / "thirstys-standard-v3q.successor.manifest.yaml"

EFFECTIVE_DATE = "2026-07-21"


def _load(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _is_contradictory(manifest: dict[str, Any]) -> bool:
    ratified = manifest["standard"]["status"] == "ratified"
    still_pending = (
        manifest.get("lifecycle", {}).get("ratification", {}).get("status")
        == "pending_owner_signature"
    )
    return ratified and still_pending


def test_prepare_clears_pending_ratification_status() -> None:
    result = prepare_ratified_manifest(_load(DRAFT), EFFECTIVE_DATE)
    assert result["standard"]["status"] == "ratified"
    assert result["lifecycle"]["ratification"]["status"] == "owner_signed"
    assert not _is_contradictory(result)


def test_prepare_replaces_stale_pending_prose() -> None:
    result = prepare_ratified_manifest(_load(DRAFT), EFFECTIVE_DATE)
    statement = result["implementation_status"]["statement"]
    assert statement == RATIFIED_IMPLEMENTATION_STATEMENT
    assert "remains pending" not in statement
    assert "pending" not in statement.lower()


def test_prepare_is_idempotent() -> None:
    once = prepare_ratified_manifest(_load(DRAFT), EFFECTIVE_DATE)
    twice = prepare_ratified_manifest(once, EFFECTIVE_DATE)
    assert once == twice


def test_prepare_does_not_mutate_its_input() -> None:
    manifest = _load(DRAFT)
    before = manifest["lifecycle"]["ratification"]["status"]
    prepare_ratified_manifest(manifest, EFFECTIVE_DATE)
    assert manifest["lifecycle"]["ratification"]["status"] == before


def test_prepare_raises_when_ratification_block_is_absent() -> None:
    """Fail loudly rather than freeze the defect into a signed artifact."""
    manifest = _load(DRAFT)
    del manifest["lifecycle"]["ratification"]
    with pytest.raises(AuthorityError, match=r"lifecycle\.ratification"):
        prepare_ratified_manifest(manifest, EFFECTIVE_DATE)


def test_prepare_raises_when_statement_is_absent() -> None:
    manifest = _load(DRAFT)
    del manifest["implementation_status"]["statement"]
    with pytest.raises(AuthorityError, match=r"implementation_status\.statement"):
        prepare_ratified_manifest(manifest, EFFECTIVE_DATE)


def test_successor_manifest_exists_and_is_unsigned() -> None:
    """The successor is a draft. It must not claim ratification it does not have."""
    successor = _load(SUCCESSOR)
    assert successor["standard"]["status"] == "draft_unratified"
    assert successor["implementation_status"]["owner_ratification_verified"] is False
    assert successor["standard"]["effective_date"] is None
    assert not _is_contradictory(successor)


def test_successor_supersedes_the_ratified_revision_by_hash() -> None:
    successor = _load(SUCCESSOR)
    supersedes = successor["standard"]["supersedes"]
    assert supersedes is not None
    assert "urn:thirsty:standard:v3q:manifest@1.1.0" in supersedes
    assert "sha256:" in supersedes


def test_successor_ratifies_into_a_consistent_artifact() -> None:
    """The whole point of the successor: ratifying it must not reproduce the defect."""
    result = prepare_ratified_manifest(_load(SUCCESSOR), EFFECTIVE_DATE)
    assert not _is_contradictory(result)
    assert result["lifecycle"]["ratification"]["status"] == "owner_signed"
    assert "pending" not in result["implementation_status"]["statement"].lower()


def test_signed_revision_remains_untouched_as_historical_evidence() -> None:
    """The signed 1.1.0 artifact is preserved exactly, defect included.

    It is historical evidence. Correcting it in place would invalidate the owner's
    signature and destroy the record of what was actually ratified.
    """
    ratified = _load(RATIFIED)
    assert ratified["manifest_version"] == "1.1.0"
    assert ratified["standard"]["status"] == "ratified"
    assert _is_contradictory(ratified), (
        "the signed 1.1.0 artifact must retain its original contents, including the "
        "known contradiction; it is superseded, not edited"
    )
