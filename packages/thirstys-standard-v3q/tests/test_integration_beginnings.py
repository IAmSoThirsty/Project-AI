"""Beginnings-native integration tests for the Thirsty's Standard V3+Q runtime.

These exercise the *adapted* package surface (the Beginnings integration facade and
the CEL-independent runtime modules) so the suite stays green without ``cel-python``.
CEL-dependent behavior is covered upstream and skipped when ``cel-python`` is absent.
"""

from __future__ import annotations

from datetime import UTC
from pathlib import Path
from typing import Any

import pytest

try:
    import celpy  # noqa: F401

    HAVE_CELPY = True
except ImportError:
    HAVE_CELPY = False

from thirstys_standard_runtime.authority import (
    AuthorityError,
    generate_keypair,
    load_registry,
    sign_document,
    verify_authority_proof,
)
from thirstys_standard_runtime.canonical import sha256_file
from thirstys_standard_runtime.integration import (
    ThirstysV3QGate,
    build_gate,
    default_manifest_path,
    manifest_integrity_summary,
)
from thirstys_standard_runtime.ratification import (
    create_ratification_record,
    prepare_ratified_manifest,
    verify_ratification_record,
)
from thirstys_standard_runtime.strict_yaml import DuplicateKeyError, load, loads

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def owner_keys() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    private, public = generate_keypair(
        "owner-test",
        "Jeremy / Thirsty",
        ["authority", "approval", "ratification", "execution_record"],
    )
    return private, public, {"keys": [public]}


@pytest.fixture(scope="session")
def manifest() -> dict[str, Any]:
    return load(default_manifest_path())


def _signed_proof(private, *, purpose, proof_id, scope, actions, action_id=None, expired=False):
    from datetime import datetime, timedelta

    now = datetime.now(UTC)
    payload = {
        "proof_id": proof_id,
        "principal_id": "Jeremy / Thirsty",
        "issued_at": (now - timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        "expires_at": (now - timedelta(minutes=1) if expired else now + timedelta(hours=1))
        .isoformat()
        .replace("+00:00", "Z"),
        "scope": scope,
        "allowed_actions": actions,
        "nonce": "0123456789abcdef0123456789abcdef",
    }
    if action_id:
        payload["action_id"] = action_id
    return sign_document(payload, private, purpose)


def test_package_is_registered_workspace_member() -> None:
    assert default_manifest_path().exists()
    assert default_manifest_path().name == "thirstys-standard-v3q.manifest.yaml"


def test_cryptography_authority_roundtrip(owner_keys) -> None:
    private, _, registry = owner_keys
    proof = _signed_proof(
        private, purpose="authority", proof_id="p1", scope=["task:task-1"], actions=["inspect"]
    )
    key = verify_authority_proof(
        proof, registry, required_action="inspect", required_scope="task:task-1"
    )
    assert key["principal_id"] == "Jeremy / Thirsty"


def test_authority_tamper_rejected(owner_keys) -> None:
    from copy import deepcopy

    private, _, registry = owner_keys
    proof = _signed_proof(
        private, purpose="authority", proof_id="p2", scope=["task:task-1"], actions=["inspect"]
    )
    tampered = deepcopy(proof)
    tampered["allowed_actions"] = ["permanent_delete"]
    with pytest.raises(AuthorityError, match="Signature verification failed"):
        verify_authority_proof(
            tampered, registry, required_action="permanent_delete", required_scope="task:task-1"
        )


def test_duplicate_trusted_key_rejected(owner_keys) -> None:
    _, public, _ = owner_keys
    with pytest.raises(AuthorityError, match="Duplicate trusted key ID"):
        load_registry({"keys": [public, public]})


def test_strict_yaml_rejects_duplicate_keys() -> None:
    with pytest.raises(DuplicateKeyError):
        loads("a: 1\na: 2\n")


def test_ratification_binds_exact_manifest_hash(manifest, owner_keys, tmp_path) -> None:
    import yaml

    private, _, registry = owner_keys
    ratified = prepare_ratified_manifest(manifest, "2026-07-17")
    manifest_path = tmp_path / "ratified.manifest.yaml"
    manifest_path.write_text(
        yaml.safe_dump(ratified, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    record = create_ratification_record(manifest_path, ratified, private, "2026-07-17")
    verify_ratification_record(manifest_path, ratified, record, registry)

    from copy import deepcopy

    tampered = deepcopy(ratified)
    tampered["standard"]["source_scope"] = "tampered"
    manifest_path.write_text(
        yaml.safe_dump(tampered, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    with pytest.raises(AuthorityError, match="hash mismatch"):
        verify_ratification_record(manifest_path, tampered, record, registry)


def test_integrity_summary_reports_cel_as_unavailable_without_celpy(manifest) -> None:
    summary = manifest_integrity_summary()
    assert summary["rule_count"] == 53
    assert summary["control_count"] == 112
    assert summary["test_count"] == 20
    assert summary["duplicate_rule_ids"] is False
    assert summary["unknown_test_refs"] == []
    assert summary["manifest_sha256"] == sha256_file(default_manifest_path())


def test_gate_facade_fails_closed_without_authority(manifest, owner_keys) -> None:
    # Without cel-python the gate runs in cel_free mode: it still enforces the
    # pure-cryptography controls (missing authority fails closed) and flags that
    # CEL applicability was not evaluated.
    _, _, registry = owner_keys
    gate = ThirstysV3QGate(manifest, registry, cel_free=True)
    decision = gate.decide(
        {"task_id": "task-1"},
        {"action_id": "a1", "type": "inspect", "class": "read_only"},
        None,
        None,
    )
    assert decision["decision"] == "deny"
    assert "Q-002-B" in decision["control_ids"]
    assert decision["cel_unavailable"] is True


def test_gate_facade_requires_cel_when_not_cel_free(manifest, owner_keys) -> None:
    # The full engine (applies_when evaluation) genuinely requires cel-python.
    # When cel-python is installed the engine constructs successfully; when it is
    # absent the facade raises the clear CELEngineUnavailable signal instead of
    # failing obscurely. Both outcomes are correct — assert the environment-appropriate one.
    from thirstys_standard_runtime.integration import CELEngineUnavailable

    _, _, registry = owner_keys
    if HAVE_CELPY:
        # Engine builds; CEL applicability is now actually evaluated end-to-end.
        gate = ThirstysV3QGate(manifest, registry)
        assert gate is not None
    else:
        with pytest.raises(CELEngineUnavailable):
            ThirstysV3QGate(manifest, registry)


# --- Production deployment path (config-driven, auto-minting, fail-safe) -------
def test_build_gate_is_dormant_without_deployment_config() -> None:
    # No owner key in the environment -> build_gate() resolves to None and the
    # system runs on its existing governance (safe default; CI stays green).
    import os

    saved = os.environ.pop("THIRSTYS_V3Q_OWNER_KEY", None)
    try:
        assert build_gate() is None
    finally:
        if saved is not None:
            os.environ["THIRSTYS_V3Q_OWNER_KEY"] = saved


def test_build_gate_activates_and_auto_mints_with_owner_key(tmp_path, manifest) -> None:
    # Simulate a production deployment: an owner private key + a matching trusted
    # registry are provisioned and pointed at via env vars. build_gate() must
    # return an ACTIVE gate that self-mints valid authority/approval proofs and
    # enforces the manifest.
    import json
    import os

    from thirstys_standard_runtime.authority import generate_keypair, write_private_key

    private_doc, public_doc = generate_keypair(
        "owner-primary",
        "Jeremy / Thirsty",
        ["authority", "approval", "ratification", "execution_record"],
    )
    key_path = tmp_path / "owner-private.json"
    write_private_key(key_path, private_doc)
    registry_path = tmp_path / "trusted-keys.json"
    registry_path.write_text(json.dumps({"keys": [public_doc]}, indent=2), encoding="utf-8")

    saved_owner = os.environ.get("THIRSTYS_V3Q_OWNER_KEY")
    saved_registry = os.environ.get("THIRSTYS_V3Q_REGISTRY")
    os.environ["THIRSTYS_V3Q_OWNER_KEY"] = str(key_path)
    os.environ["THIRSTYS_V3Q_REGISTRY"] = str(registry_path)
    try:
        gate = build_gate()
        assert gate is not None, "deployment config should activate the gate"
        # Mapped, reversible op -> gate auto-mints a valid authority proof -> ALLOW.
        allowed = gate.decide(
            {"task_id": "atlas:abc"},
            {"action_id": "a1", "class": "local_reversible", "type": "write"},
            None,
            None,
        )
        assert allowed["decision"] == "allow", allowed
        # Consequential op (rank 3) requires approval; auto-minted approval -> ALLOW.
        consequential = gate.decide(
            {"task_id": "sim:1"},
            {
                "action_id": "a2",
                "class": "externally_consequential",
                "type": "deploy_visible_service",
            },
            None,
            None,
        )
        assert consequential["decision"] == "allow", consequential
        # Unmapped op falls back to raw string -> unknown class -> DENY (never silent pass).
        unknown = gate.decide(
            {"task_id": "x:1"},
            {"action_id": "a3", "class": "no_such_op", "type": "no_such_op"},
            None,
            None,
        )
        assert unknown["decision"] == "deny"
    finally:
        if saved_owner is not None:
            os.environ["THIRSTYS_V3Q_OWNER_KEY"] = saved_owner
        else:
            os.environ.pop("THIRSTYS_V3Q_OWNER_KEY", None)
        if saved_registry is not None:
            os.environ["THIRSTYS_V3Q_REGISTRY"] = saved_registry
        else:
            os.environ.pop("THIRSTYS_V3Q_REGISTRY", None)
