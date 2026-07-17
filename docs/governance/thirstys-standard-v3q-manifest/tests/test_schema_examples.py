from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


def test_all_json_schemas_are_valid(root: Path) -> None:
    schema_paths = [
        root / "thirstys-standard-manifest.schema.json",
        root / "conformance-report.schema.json",
        *sorted((root / "schemas").glob("*.schema.json")),
    ]
    for path in schema_paths:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)


def test_example_report_is_schema_valid(root: Path) -> None:
    import yaml

    document = yaml.safe_load((root / "conformance-report.example.yaml").read_text(encoding="utf-8"))
    schema = json.loads((root / "conformance-report.schema.json").read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document))
    assert not errors, [error.message for error in errors]
