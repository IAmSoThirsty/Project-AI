from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from .authority import generate_keypair, load_registry, sign_document, verify_signed_document, write_private_key
from .canonical import sha256_file
from .cel_runtime import CELRuntime
from .evaluator import evaluate_execution_record
from .policy import RuntimePolicyEngine
from .strict_yaml import load as strict_yaml_load


def _load(path: str | Path) -> Any:
    path = Path(path)
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return strict_yaml_load(path)


def _write(path: str | Path, value: Any) -> None:
    path = Path(path)
    if path.suffix.lower() == ".json":
        path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=True), encoding="utf-8")


def cmd_validate(args: argparse.Namespace) -> int:
    document = _load(args.document)
    schema = _load(args.schema)
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document), key=lambda e: list(e.absolute_path))
    if errors:
        for error in errors:
            location = ".".join(str(part) for part in error.absolute_path) or "<root>"
            print(f"FAILED {location}: {error.message}")
        return 1
    print(f"VERIFIED: {args.document} conforms to {Path(args.schema).name}")
    return 0


def cmd_cel_verify(args: argparse.Namespace) -> int:
    manifest = _load(args.manifest)
    expressions = CELRuntime().compile_manifest_conditions(manifest)
    print(f"VERIFIED: compiled {len(expressions)} unique CEL expressions across all controls")
    return 0


def cmd_keygen(args: argparse.Namespace) -> int:
    private_doc, public_doc = generate_keypair(args.key_id, args.principal_id, args.purpose)
    write_private_key(args.private_out, private_doc)
    _write(args.public_out, public_doc)
    print(f"CREATED: {args.private_out} (mode 0600 where supported)")
    print(f"CREATED: {args.public_out}")
    return 0


def cmd_sign(args: argparse.Namespace) -> int:
    document = _load(args.document)
    private_key = _load(args.private_key)
    signed = sign_document(document, private_key, args.purpose)
    _write(args.output, signed)
    print(f"SIGNED: {args.output}")
    return 0


def cmd_verify_signature(args: argparse.Namespace) -> int:
    document = _load(args.document)
    verify_signed_document(document, _load(args.registry), args.purpose, args.principal)
    print(f"VERIFIED: signature on {args.document}")
    return 0


def cmd_gate(args: argparse.Namespace) -> int:
    manifest = _load(args.manifest)
    registry = _load(args.registry)
    engine = RuntimePolicyEngine(manifest, registry)
    decision = engine.gate_action(
        _load(args.task),
        _load(args.action),
        _load(args.authority) if args.authority else None,
        _load(args.approval) if args.approval else None,
    )
    print(json.dumps(decision.as_dict(), indent=2))
    return 0 if decision.allowed else 3


def cmd_evaluate(args: argparse.Namespace) -> int:
    report = evaluate_execution_record(
        _load(args.manifest),
        _load(args.record),
        _load(args.registry),
        _load(args.evaluator_identity),
        _load(args.evaluator_private_key),
    )
    _write(args.output, report)
    print(f"VERIFIED: independent report written to {args.output}")
    return 0


def cmd_hash(args: argparse.Namespace) -> int:
    print(sha256_file(args.path))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="thirstys-standard")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate")
    validate.add_argument("document")
    validate.add_argument("schema")
    validate.set_defaults(func=cmd_validate)

    cel = sub.add_parser("cel-verify")
    cel.add_argument("manifest")
    cel.set_defaults(func=cmd_cel_verify)

    keygen = sub.add_parser("keygen")
    keygen.add_argument("--key-id", required=True)
    keygen.add_argument("--principal-id", required=True)
    keygen.add_argument("--purpose", action="append", required=True)
    keygen.add_argument("--private-out", required=True)
    keygen.add_argument("--public-out", required=True)
    keygen.set_defaults(func=cmd_keygen)

    sign = sub.add_parser("sign")
    sign.add_argument("document")
    sign.add_argument("--private-key", required=True)
    sign.add_argument("--purpose", required=True)
    sign.add_argument("--output", required=True)
    sign.set_defaults(func=cmd_sign)

    verify = sub.add_parser("verify-signature")
    verify.add_argument("document")
    verify.add_argument("--registry", required=True)
    verify.add_argument("--purpose", required=True)
    verify.add_argument("--principal")
    verify.set_defaults(func=cmd_verify_signature)

    gate = sub.add_parser("gate")
    gate.add_argument("--manifest", required=True)
    gate.add_argument("--registry", required=True)
    gate.add_argument("--task", required=True)
    gate.add_argument("--action", required=True)
    gate.add_argument("--authority")
    gate.add_argument("--approval")
    gate.set_defaults(func=cmd_gate)

    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--manifest", required=True)
    evaluate.add_argument("--record", required=True)
    evaluate.add_argument("--registry", required=True)
    evaluate.add_argument("--evaluator-identity", required=True)
    evaluate.add_argument("--evaluator-private-key", required=True)
    evaluate.add_argument("--output", required=True)
    evaluate.set_defaults(func=cmd_evaluate)

    hash_parser = sub.add_parser("hash")
    hash_parser.add_argument("path")
    hash_parser.set_defaults(func=cmd_hash)
    return parser


def main() -> int:
    try:
        parser = build_parser()
        args = parser.parse_args()
        return int(args.func(args))
    except Exception as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
