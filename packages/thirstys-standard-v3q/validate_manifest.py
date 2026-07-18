#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from thirstys_standard_runtime.cel_runtime import CELRuntime  # noqa: E402
from thirstys_standard_runtime.strict_yaml import load as strict_yaml_load  # noqa: E402


def load_data(path: Path) -> Any:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return strict_yaml_load(path)


def validate_schema(document: Any, schema: Any) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    messages: list[str] = []
    for error in sorted(validator.iter_errors(document), key=lambda err: list(err.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        messages.append(f"{location}: {error.message}")
    return messages


def validate_manifest_integrity(document: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    rules = document.get("rules", [])
    rule_ids = [rule.get("id") for rule in rules]
    control_ids = [control.get("id") for rule in rules for control in rule.get("controls", [])]
    test_ids = [test.get("id") for test in document.get("test_catalog", [])]
    for label, values in (("rule", rule_ids), ("control", control_ids), ("test", test_ids)):
        if len(values) != len(set(values)):
            messages.append(f"Duplicate {label} identifier detected")
    declared_tests = set(test_ids)
    for rule in rules:
        for control in rule.get("controls", []):
            unknown = sorted(set(control.get("test_ids", [])) - declared_tests)
            if unknown:
                messages.append(f"{control.get('id')}: unknown test IDs {unknown}")
    try:
        CELRuntime().compile_manifest_conditions(document)
    except Exception as exc:
        messages.append(f"CEL compilation: {exc}")
    return messages


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Thirsty's Standard manifest or conformance report."
    )
    parser.add_argument("document", type=Path)
    parser.add_argument("--schema", type=Path, default=None)
    args = parser.parse_args()

    if args.schema is not None:
        schema_path = args.schema
    elif args.document.name.endswith(".manifest.yaml") or args.document.name.endswith(
        ".manifest.json"
    ):
        schema_path = ROOT / "thirstys-standard-manifest.schema.json"
    else:
        schema_path = ROOT / "conformance-report.schema.json"

    if not args.document.exists() or not schema_path.exists():
        print("FAILED: document or schema not found", file=sys.stderr)
        return 2

    try:
        document = load_data(args.document)
        schema = load_data(schema_path)
    except Exception as exc:
        print(f"FAILED: {exc}")
        return 1

    errors = validate_schema(document, schema)
    if args.document.name.endswith(".manifest.yaml") or args.document.name.endswith(
        ".manifest.json"
    ):
        errors.extend(validate_manifest_integrity(document))
    if errors:
        print(f"FAILED: {args.document}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"VERIFIED: {args.document} conforms to {schema_path.name}")
    if "rules" in document:
        control_count = sum(len(rule["controls"]) for rule in document["rules"])
        expression_count = len(
            {control["applies_when"] for rule in document["rules"] for control in rule["controls"]}
        )
        print(
            f"VERIFIED: {len(document['rules'])} rules, {control_count} controls, {len(document['test_catalog'])} tests, {expression_count} CEL expressions"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
