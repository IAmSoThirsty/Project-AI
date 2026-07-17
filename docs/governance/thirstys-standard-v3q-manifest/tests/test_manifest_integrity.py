from __future__ import annotations

from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from thirstys_standard_runtime.cel_runtime import CELRuntime
from thirstys_standard_runtime.strict_yaml import DuplicateKeyError, loads


def test_manifest_schema_and_references(root: Path, manifest: dict) -> None:
    import json

    schema = json.loads((root / "thirstys-standard-manifest.schema.json").read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(manifest))
    assert not errors, [error.message for error in errors]

    rule_ids = [rule["id"] for rule in manifest["rules"]]
    control_ids = [control["id"] for rule in manifest["rules"] for control in rule["controls"]]
    test_ids = [test["id"] for test in manifest["test_catalog"]]
    assert len(rule_ids) == len(set(rule_ids)) == 53
    assert len(control_ids) == len(set(control_ids)) == 112
    assert len(test_ids) == len(set(test_ids)) == 20
    declared_tests = set(test_ids)
    for rule in manifest["rules"]:
        for control in rule["controls"]:
            assert set(control["test_ids"]) <= declared_tests


def test_duplicate_yaml_keys_are_rejected() -> None:
    with pytest.raises(DuplicateKeyError):
        loads("a: 1\na: 2\n")


def test_all_cel_conditions_compile(manifest: dict) -> None:
    expressions = CELRuntime().compile_manifest_conditions(manifest)
    assert len(expressions) == 8
