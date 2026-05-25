"""PSIA root invariants — 9 immutable, fatal, hard-deny governance rules."""
from __future__ import annotations

from psia.schemas.identity import Signature
from psia.schemas.invariant import (
    InvariantDefinition,
    InvariantEnforcement,
    InvariantExpression,
    InvariantScope,
    InvariantSeverity,
    InvariantTestCase,
)

_SIG = Signature(alg="ed25519", kid="genesis-root-key", sig="governance-sealed")
_SCOPE = InvariantScope.IMMUTABLE
_SEV = InvariantSeverity.FATAL
_ENF = InvariantEnforcement.HARD_DENY


def _inv(
    n: int,
    expr: str,
    tests: list[InvariantTestCase],
) -> InvariantDefinition:
    return InvariantDefinition(
        invariant_id=f"inv_root_{n:03d}",
        version=1,
        scope=_SCOPE,
        severity=_SEV,
        enforcement=_ENF,
        expression=InvariantExpression(language="first_order_logic", expr=expr),
        tests=tests,
        signature=_SIG,
    )


INV_ROOT_1 = _inv(
    1,
    "forall(actor): authenticate(actor) => identity_verified(actor)",
    [
        InvariantTestCase(name="valid_identity", given={"actor": "did:psia:alice", "authenticated": True}, expect="allow"),
        InvariantTestCase(name="unauthenticated", given={"actor": "unknown", "authenticated": False}, expect="deny"),
    ],
)

INV_ROOT_2 = _inv(
    2,
    "forall(actor, action): authorized(actor, action) => capability_held(actor, action)",
    [
        InvariantTestCase(name="authorized_actor", given={"actor": "did:psia:bob", "capability": "read"}, expect="allow"),
        InvariantTestCase(name="unauthorized_actor", given={"actor": "did:psia:bob", "capability": "delete"}, expect="deny"),
    ],
)

INV_ROOT_3 = _inv(
    3,
    "forall(record): committed(record) => hash_verified(record) AND signature_valid(record)",
    [
        InvariantTestCase(name="valid_record", given={"hash_verified": True, "signature_valid": True}, expect="allow"),
        InvariantTestCase(name="invalid_hash", given={"hash_verified": False, "signature_valid": True}, expect="deny"),
    ],
)

INV_ROOT_4 = _inv(
    4,
    "forall(key): active(key) => NOT expired(key) AND NOT revoked(key)",
    [
        InvariantTestCase(name="active_key", given={"expired": False, "revoked": False}, expect="allow"),
        InvariantTestCase(name="expired_key", given={"expired": True, "revoked": False}, expect="deny"),
    ],
)

INV_ROOT_5 = _inv(
    5,
    "forall(issuer, subject): issue_capability(issuer, subject) => issuer != subject",
    [
        InvariantTestCase(name="different_entities", given={"issuer": "did:psia:authority", "subject": "did:psia:agent"}, expect="allow"),
        InvariantTestCase(name="self_issuance", given={"issuer": "did:psia:authority", "subject": "did:psia:authority"}, expect="deny"),
    ],
)

INV_ROOT_6 = _inv(
    6,
    "forall(token, scope): valid_token(token, scope) => |scope.actions| <= MAX_SCOPE_ACTIONS",
    [
        InvariantTestCase(name="small_scope", given={"actions": ["read", "write"], "max": 10}, expect="allow"),
        InvariantTestCase(name="excessive_scope", given={"actions": ["r", "w", "x", "d", "m", "c", "p", "a", "e", "b", "f"], "max": 10}, expect="deny"),
    ],
)

INV_ROOT_7 = _inv(
    7,
    "forall(decision_set): quorum_verdict(decision_set) = max_severity(decision_set)",
    [
        InvariantTestCase(name="unanimous_allow", given={"votes": ["allow", "allow", "allow"]}, expect="allow"),
        InvariantTestCase(name="one_deny_dominates", given={"votes": ["allow", "allow", "deny"]}, expect="deny"),
    ],
)

INV_ROOT_8 = _inv(
    8,
    "forall(did): register(did) => NOT exists(did) IN identity_registry",
    [
        InvariantTestCase(name="new_did", given={"did": "did:psia:new", "exists": False}, expect="allow"),
        InvariantTestCase(name="duplicate_did", given={"did": "did:psia:existing", "exists": True}, expect="deny"),
    ],
)

INV_ROOT_9 = _inv(
    9,
    "forall(record_id): append(record_id) => NOT exists(record_id) IN ledger",
    [
        InvariantTestCase(name="new_record", given={"record_id": "rec_new", "exists": False}, expect="allow"),
        InvariantTestCase(name="duplicate_record", given={"record_id": "rec_dup", "exists": True}, expect="deny"),
    ],
)

ROOT_INVARIANTS: dict[str, InvariantDefinition] = {
    inv.invariant_id: inv
    for inv in [
        INV_ROOT_1, INV_ROOT_2, INV_ROOT_3, INV_ROOT_4, INV_ROOT_5,
        INV_ROOT_6, INV_ROOT_7, INV_ROOT_8, INV_ROOT_9,
    ]
}
