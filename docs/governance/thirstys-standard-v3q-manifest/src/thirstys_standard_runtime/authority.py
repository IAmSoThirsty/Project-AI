from __future__ import annotations

import fnmatch
import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .canonical import b64u_decode, b64u_encode, canonical_json_bytes, without_signature


class AuthorityError(ValueError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise AuthorityError("Timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def generate_keypair(key_id: str, principal_id: str, purposes: Iterable[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    private_key = Ed25519PrivateKey.generate()
    private_raw = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_raw = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    private_document = {
        "key_id": key_id,
        "principal_id": principal_id,
        "algorithm": "Ed25519",
        "private_key": b64u_encode(private_raw),
        "purposes": sorted(set(purposes)),
    }
    public_document = {
        "key_id": key_id,
        "principal_id": principal_id,
        "algorithm": "Ed25519",
        "public_key": b64u_encode(public_raw),
        "purposes": sorted(set(purposes)),
        "status": "active",
    }
    return private_document, public_document


def write_private_key(path: str | Path, document: dict[str, Any]) -> None:
    target = Path(path)
    target.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    try:
        os.chmod(target, 0o600)
    except OSError:
        pass


def _private_key(document: dict[str, Any]) -> Ed25519PrivateKey:
    if document.get("algorithm") != "Ed25519":
        raise AuthorityError("Unsupported private key algorithm")
    return Ed25519PrivateKey.from_private_bytes(b64u_decode(document["private_key"]))


def _public_key(document: dict[str, Any]) -> Ed25519PublicKey:
    if document.get("algorithm") != "Ed25519":
        raise AuthorityError("Unsupported public key algorithm")
    return Ed25519PublicKey.from_public_bytes(b64u_decode(document["public_key"]))


def sign_document(document: dict[str, Any], private_key_document: dict[str, Any], purpose: str) -> dict[str, Any]:
    if purpose not in private_key_document.get("purposes", []):
        raise AuthorityError(f"Key is not authorized for purpose {purpose!r}")
    signed = deepcopy(document)
    signed.pop("signature", None)
    signed.pop("report_signature", None)
    signature = _private_key(private_key_document).sign(canonical_json_bytes(signed))
    signed["signature"] = {
        "algorithm": "Ed25519",
        "key_id": private_key_document["key_id"],
        "purpose": purpose,
        "value": b64u_encode(signature),
    }
    return signed


def load_registry(path_or_document: str | Path | dict[str, Any]) -> dict[str, dict[str, Any]]:
    if isinstance(path_or_document, (str, Path)):
        document = json.loads(Path(path_or_document).read_text(encoding="utf-8"))
    else:
        document = path_or_document
    keys = document.get("keys", [])
    registry: dict[str, dict[str, Any]] = {}
    for entry in keys:
        key_id = entry["key_id"]
        if key_id in registry:
            raise AuthorityError(f"Duplicate trusted key ID: {key_id}")
        registry[key_id] = entry
    return registry


def verify_signed_document(
    document: dict[str, Any],
    registry: str | Path | dict[str, Any],
    expected_purpose: str,
    expected_principal: str | None = None,
) -> dict[str, Any]:
    signature = document.get("signature")
    if not isinstance(signature, dict):
        raise AuthorityError("Missing signature")
    if signature.get("algorithm") != "Ed25519":
        raise AuthorityError("Unsupported signature algorithm")
    if signature.get("purpose") != expected_purpose:
        raise AuthorityError("Signature purpose mismatch")
    keys = load_registry(registry)
    key = keys.get(signature.get("key_id"))
    if not key or key.get("status") != "active":
        raise AuthorityError("Signing key is not trusted and active")
    if expected_purpose not in key.get("purposes", []):
        raise AuthorityError("Trusted key is not authorized for this purpose")
    if expected_principal is not None and key.get("principal_id") != expected_principal:
        raise AuthorityError("Signing principal mismatch")
    try:
        _public_key(key).verify(b64u_decode(signature["value"]), canonical_json_bytes(without_signature(document)))
    except InvalidSignature as exc:
        raise AuthorityError("Signature verification failed") from exc
    return key


def _matches_scope(scopes: list[str], required_scope: str) -> bool:
    return any(fnmatch.fnmatchcase(required_scope, scope) for scope in scopes)


def verify_authority_proof(
    proof: dict[str, Any],
    registry: str | Path | dict[str, Any],
    *,
    required_action: str,
    required_scope: str,
    now: datetime | None = None,
    purpose: str = "authority",
) -> dict[str, Any]:
    required_fields = {
        "proof_id",
        "principal_id",
        "issued_at",
        "expires_at",
        "scope",
        "allowed_actions",
        "nonce",
        "signature",
    }
    missing = sorted(required_fields - set(proof))
    if missing:
        raise AuthorityError(f"Authority proof missing fields: {', '.join(missing)}")
    key = verify_signed_document(proof, registry, purpose, proof["principal_id"])
    current = now or utc_now()
    if parse_time(proof["issued_at"]) > current:
        raise AuthorityError("Authority proof is not yet valid")
    if parse_time(proof["expires_at"]) <= current:
        raise AuthorityError("Authority proof is expired")
    if required_action not in proof["allowed_actions"] and "*" not in proof["allowed_actions"]:
        raise AuthorityError("Action is outside authority proof")
    if not _matches_scope(proof["scope"], required_scope):
        raise AuthorityError("Requested scope is outside authority proof")
    return key
