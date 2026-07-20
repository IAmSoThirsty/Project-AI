from __future__ import annotations

from copy import deepcopy

import pytest
from thirstys_standard_runtime.authority import AuthorityError, verify_authority_proof
from v3q_test_helpers import signed_proof


def test_valid_ed25519_authority_proof(owner_keys) -> None:
    private, _, registry = owner_keys
    proof = signed_proof(
        private, purpose="authority", proof_id="proof-1", scope=["task:task-1"], actions=["inspect"]
    )
    key = verify_authority_proof(
        proof, registry, required_action="inspect", required_scope="task:task-1"
    )
    assert key["principal_id"] == "Jeremy / Thirsty"


def test_tampering_is_rejected(owner_keys) -> None:
    private, _, registry = owner_keys
    proof = signed_proof(
        private, purpose="authority", proof_id="proof-2", scope=["task:task-1"], actions=["inspect"]
    )
    tampered = deepcopy(proof)
    tampered["allowed_actions"] = ["permanent_delete"]
    with pytest.raises(AuthorityError, match="Signature verification failed"):
        verify_authority_proof(
            tampered, registry, required_action="permanent_delete", required_scope="task:task-1"
        )


def test_expired_proof_is_rejected(owner_keys) -> None:
    private, _, registry = owner_keys
    proof = signed_proof(
        private,
        purpose="authority",
        proof_id="proof-3",
        scope=["task:*"],
        actions=["inspect"],
        expired=True,
    )
    with pytest.raises(AuthorityError, match="expired"):
        verify_authority_proof(
            proof, registry, required_action="inspect", required_scope="task:task-1"
        )


def test_scope_and_action_are_enforced(owner_keys) -> None:
    private, _, registry = owner_keys
    proof = signed_proof(
        private, purpose="authority", proof_id="proof-4", scope=["task:other"], actions=["inspect"]
    )
    with pytest.raises(AuthorityError, match="scope"):
        verify_authority_proof(
            proof, registry, required_action="inspect", required_scope="task:task-1"
        )


def test_duplicate_trusted_key_ids_are_rejected(owner_keys) -> None:
    from thirstys_standard_runtime.authority import load_registry

    _, public, _ = owner_keys
    with pytest.raises(AuthorityError, match="Duplicate trusted key ID"):
        load_registry({"keys": [public, public]})
