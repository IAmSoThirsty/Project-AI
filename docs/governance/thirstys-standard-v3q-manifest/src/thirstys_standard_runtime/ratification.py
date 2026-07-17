from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from .authority import AuthorityError, sign_document, verify_signed_document
from .canonical import sha256_file


RATIFICATION_STATEMENT = (
    "I, Jeremy / Thirsty, as owner and approval authority, ratify this exact manifest release "
    "as Thirsty's Standard V3 + Q, subject to its declared scope, priority order, and fail-closed controls."
)


def prepare_ratified_manifest(manifest: dict[str, Any], effective_date: str) -> dict[str, Any]:
    try:
        date.fromisoformat(effective_date)
    except ValueError as exc:
        raise AuthorityError("Effective date must be YYYY-MM-DD") from exc
    updated = deepcopy(manifest)
    updated["standard"]["status"] = "ratified"
    updated["standard"]["effective_date"] = effective_date
    updated["standard"]["proposed_version"] = str(updated["standard"]["proposed_version"]).replace("-rc1", "")
    updated["manifest_version"] = str(updated["manifest_version"]).replace("-rc1", "")
    updated["implementation_status"]["owner_ratification_verified"] = True
    return updated


def create_ratification_record(
    manifest_path: str | Path,
    manifest: dict[str, Any],
    private_key: dict[str, Any],
    effective_date: str,
) -> dict[str, Any]:
    if manifest["standard"]["status"] != "ratified":
        raise AuthorityError("Manifest must be set to ratified before signing")
    if private_key.get("principal_id") != manifest["standard"]["owner"]:
        raise AuthorityError("Ratification key principal does not match the manifest owner")
    record = {
        "record_type": "owner_ratification",
        "manifest_id": manifest["manifest_id"],
        "manifest_version": manifest["manifest_version"],
        "standard_version": manifest["standard"]["proposed_version"],
        "manifest_sha256": sha256_file(manifest_path),
        "owner": manifest["standard"]["owner"],
        "approval_authority": manifest["standard"]["approval_authority"],
        "effective_date": effective_date,
        "ratified_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "statement": RATIFICATION_STATEMENT,
    }
    return sign_document(record, private_key, "ratification")


def verify_ratification_record(
    manifest_path: str | Path,
    manifest: dict[str, Any],
    record: dict[str, Any],
    registry: dict[str, Any],
) -> None:
    verify_signed_document(record, registry, "ratification", manifest["standard"]["owner"])
    if record.get("statement") != RATIFICATION_STATEMENT:
        raise AuthorityError("Ratification statement mismatch")
    if record.get("manifest_id") != manifest["manifest_id"]:
        raise AuthorityError("Ratification manifest ID mismatch")
    if record.get("manifest_version") != manifest["manifest_version"]:
        raise AuthorityError("Ratification manifest version mismatch")
    if record.get("manifest_sha256") != sha256_file(manifest_path):
        raise AuthorityError("Ratified manifest hash mismatch")
    if manifest["standard"].get("status") != "ratified":
        raise AuthorityError("Manifest status is not ratified")
    if manifest["standard"].get("effective_date") != record.get("effective_date"):
        raise AuthorityError("Ratification effective date mismatch")
