from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from thirstys_standard_runtime.authority import AuthorityError
from thirstys_standard_runtime.ratification import create_ratification_record, prepare_ratified_manifest, verify_ratification_record


def test_ratification_signature_binds_exact_manifest_hash(manifest: dict, owner_keys, tmp_path: Path) -> None:
    private, _, registry = owner_keys
    ratified = prepare_ratified_manifest(manifest, "2026-07-17")
    manifest_path = tmp_path / "ratified.manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(ratified, sort_keys=False, allow_unicode=True), encoding="utf-8")
    record = create_ratification_record(manifest_path, ratified, private, "2026-07-17")
    verify_ratification_record(manifest_path, ratified, record, registry)

    tampered = deepcopy(ratified)
    tampered["standard"]["source_scope"] = "tampered"
    manifest_path.write_text(yaml.safe_dump(tampered, sort_keys=False, allow_unicode=True), encoding="utf-8")
    with pytest.raises(AuthorityError, match="hash mismatch"):
        verify_ratification_record(manifest_path, tampered, record, registry)
