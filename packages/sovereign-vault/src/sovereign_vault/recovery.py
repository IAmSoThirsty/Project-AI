"""
sovereign_vault.recovery

Recovery is a constitutional event, not an administrative one.

This module does NOT reconstruct the old RootKEK for the caller — it
never touches it at all. Recovery instead: verifies an m-of-n quorum of
distinct, unexpired, signed approvals from designated security officers,
then authorizes derivation of a NEW RootKEK from freshly supplied factors
under a new key epoch, bumps the epoch counter (which invalidates every
subkey, token binding, and capability derived from the old epoch by
construction, since KeyHierarchy derivation is epoch-scoped), and writes
a RECOVERY_EXECUTED audit event distinct from ordinary operation events.

"Never reveal the original master key" is satisfied structurally: the old
key is simply never an input to this module. There is nothing to redact
because nothing pre-existing is ever read.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .errors import QuorumNotMetError
from .interfaces import AuditChainProvider
from .primitives import combine_factors, verify_signature


@dataclass(frozen=True)
class RecoveryApprover:
    identity: str
    public_key: bytes


@dataclass(frozen=True)
class RecoveryQuorumPolicy:
    approvers: tuple[RecoveryApprover, ...]  # tuple[RecoveryApprover, ...]
    threshold: int

    def __post_init__(self) -> None:
        if self.threshold < 2:
            raise ValueError(
                "recovery threshold must be >= 2 — a single-approver "
                "recovery path is exactly the weak-recovery blind spot "
                "this module exists to close"
            )
        if self.threshold > len(self.approvers):
            raise ValueError("recovery threshold exceeds number of configured approvers")


@dataclass(frozen=True)
class RecoveryApproval:
    approver_identity: str
    signature: bytes
    signed_at_ns: int


@dataclass
class RecoveryRequest:
    request_id: str
    reason: str
    requested_by: str
    requested_at_ns: int
    approvals: list[RecoveryApproval] = field(default_factory=list)  # list[RecoveryApproval]

    def digest(self) -> bytes:
        return (
            f"{self.request_id}|{self.reason}|{self.requested_by}|{self.requested_at_ns}".encode()
        )

    def add_approval(self, approval: RecoveryApproval) -> None:
        if any(a.approver_identity == approval.approver_identity for a in self.approvals):
            raise ValueError(
                f"approver {approval.approver_identity} already approved this request — "
                f"duplicate approvals do not count twice toward quorum"
            )
        self.approvals.append(approval)


def _valid_distinct_approvals(
    request: RecoveryRequest, policy: RecoveryQuorumPolicy, max_age_ns: int
) -> int:
    approver_by_identity = {a.identity: a for a in policy.approvers}
    now = time.time_ns()
    valid = 0
    seen: set[str] = set()
    for approval in request.approvals:
        if approval.approver_identity in seen:
            continue  # defense in depth even though add_approval already blocks this
        approver = approver_by_identity.get(approval.approver_identity)
        if approver is None:
            continue  # not a configured approver — does not count
        if now - approval.signed_at_ns > max_age_ns:
            continue  # stale approval — does not count
        if not verify_signature(approver.public_key, request.digest(), approval.signature):
            continue
        seen.add(approval.approver_identity)
        valid += 1
    return valid


@dataclass(frozen=True)
class RecoveryResult:
    request_id: str
    new_epoch: int
    audit_entry_id: str


def execute_recovery(
    request: RecoveryRequest,
    policy: RecoveryQuorumPolicy,
    audit: AuditChainProvider,
    current_epoch: int,
    fresh_factors: tuple[
        bytes, ...
    ],  # tuple[bytes, ...] — new token/TPM/operator shares, NOT the old ones
    factor_combine_info: bytes,
    max_approval_age_ns: int = 15 * 60 * 1_000_000_000,  # 15 minutes
) -> tuple[bytes, RecoveryResult]:
    """
    Returns (new_root_kek, RecoveryResult). The caller is responsible for
    wrapping new_root_kek in a keys.RootKekSession immediately and never
    persisting it raw. This function never sees or derives from the OLD
    root key — that key's fate (it becomes permanently inaccessible once
    the epoch bumps) is exactly the point.
    """
    valid_count = _valid_distinct_approvals(request, policy, max_approval_age_ns)
    if valid_count < policy.threshold:
        raise QuorumNotMetError(
            f"recovery request {request.request_id}: {valid_count}/{policy.threshold} "
            f"valid distinct approvals — quorum not met"
        )

    if not audit.has_capacity():
        raise QuorumNotMetError(
            f"recovery request {request.request_id}: audit chain unavailable — "
            f"refusing to execute an unaudited recovery, even with quorum met"
        )

    new_epoch = current_epoch + 1
    new_root_kek = combine_factors(
        *fresh_factors, info=factor_combine_info + f":epoch{new_epoch}".encode()
    )

    entry_id = audit.append(
        "RECOVERY_EXECUTED",
        {
            "request_id": request.request_id,
            "reason": request.reason,
            "requested_by": request.requested_by,
            "approvals": [a.approver_identity for a in request.approvals],
            "prior_epoch": current_epoch,
            "new_epoch": new_epoch,
            "note": "prior epoch's keys, tokens, and bindings are invalidated by "
            "epoch-scoped derivation; the prior root key was never read "
            "or reconstructed by this operation",
        },
    )

    return new_root_kek, RecoveryResult(
        request_id=request.request_id, new_epoch=new_epoch, audit_entry_id=entry_id
    )
