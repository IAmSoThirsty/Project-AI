"""
PSIA Plane Contracts — isolation boundaries and capability constraints.

Implements §2.1 of the PSIA v1.0 specification.

Each PSIA plane operates within a strict contract that defines:
- What capabilities it has (allowed actions)
- What capabilities it must never exercise (forbidden actions)
- Its storage mode (read-only, append-only, read-write)
- Its network access pattern

Plane isolation is the foundation of defense-in-depth: a compromised
Shadow Plane cannot write to canonical state, a compromised Reflex
Plane cannot legislate governance, etc.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


class Plane(str, enum.Enum):
    """The six architectural planes of the PSIA."""

    CANONICAL = "canonical"
    SHADOW = "shadow"
    ADAPTIVE = "adaptive"
    GATE = "gate"
    REFLEX = "reflex"
    INGRESS = "ingress"


class PlaneCapability(str, enum.Enum):
    """Atomic capabilities that a plane may or may not exercise."""

    READ_CANONICAL = "read_canonical"
    WRITE_CANONICAL = "write_canonical"
    READ_SHADOW = "read_shadow"
    WRITE_SHADOW = "write_shadow"
    EMIT_PROPOSAL = "emit_proposal"
    SIGN_DECISION = "sign_decision"
    ENFORCE_CONTAINMENT = "enforce_containment"
    ACCEPT_REQUEST = "accept_request"
    APPEND_LEDGER = "append_ledger"
    READ_LEDGER = "read_ledger"
    STREAM_TELEMETRY = "stream_telemetry"
    COMPILE_POLICY = "compile_policy"
    FETCH_SNAPSHOT = "fetch_snapshot"
    REVOKE_IDENTITY = "revoke_identity"
    ISSUE_TOKEN = "issue_token"


class StorageMode(str, enum.Enum):
    """Storage access pattern for a plane."""

    NONE = "none"
    READ_ONLY = "read_only"
    APPEND_ONLY = "append_only"
    READ_WRITE = "read_write"


class NetworkAccess(str, enum.Enum):
    """Network access pattern for a plane."""

    EDGE_FACING = "edge_facing"
    INTERNAL_ONLY = "internal_only"
    GATE_ONLY = "gate_only"
    TELEMETRY_EXPORT = "telemetry_export"


@dataclass(frozen=True)
class PlaneContract:
    """Isolation contract for a single plane.

    The contract specifies what a plane CAN do, what it MUST NEVER do,
    and its storage/network constraints.  These contracts are enforced
    at the Waterfall and runtime levels.
    """

    plane: Plane
    allowed_capabilities: frozenset[PlaneCapability]
    forbidden_capabilities: frozenset[PlaneCapability]
    storage_mode: StorageMode
    network_access: NetworkAccess
    description: str = ""


# ── Plane Contract Definitions ────────────────────────────────────────

CANONICAL_CONTRACT = PlaneContract(
    plane=Plane.CANONICAL,
    allowed_capabilities=frozenset({
        PlaneCapability.READ_CANONICAL,
        PlaneCapability.WRITE_CANONICAL,
        PlaneCapability.APPEND_LEDGER,
        PlaneCapability.ISSUE_TOKEN,
        PlaneCapability.REVOKE_IDENTITY,
    }),
    forbidden_capabilities=frozenset({
        PlaneCapability.ACCEPT_REQUEST,
        PlaneCapability.ENFORCE_CONTAINMENT,
        PlaneCapability.EMIT_PROPOSAL,
    }),
    storage_mode=StorageMode.READ_WRITE,
    network_access=NetworkAccess.GATE_ONLY,
    description="Authoritative state store; only Gate Plane can invoke mutations",
)

SHADOW_CONTRACT = PlaneContract(
    plane=Plane.SHADOW,
    allowed_capabilities=frozenset({
        PlaneCapability.FETCH_SNAPSHOT,
        PlaneCapability.READ_SHADOW,
        PlaneCapability.WRITE_SHADOW,
        PlaneCapability.STREAM_TELEMETRY,
    }),
    forbidden_capabilities=frozenset({
        PlaneCapability.WRITE_CANONICAL,
        PlaneCapability.APPEND_LEDGER,
        PlaneCapability.SIGN_DECISION,
        PlaneCapability.ISSUE_TOKEN,
        PlaneCapability.REVOKE_IDENTITY,
        PlaneCapability.ENFORCE_CONTAINMENT,
    }),
    storage_mode=StorageMode.READ_ONLY,
    network_access=NetworkAccess.INTERNAL_ONLY,
    description="Read-only canonical snapshot + local shadow diffs; never writes to canonical",
)

ADAPTIVE_CONTRACT = PlaneContract(
    plane=Plane.ADAPTIVE,
    allowed_capabilities=frozenset({
        PlaneCapability.READ_LEDGER,
        PlaneCapability.READ_SHADOW,
        PlaneCapability.EMIT_PROPOSAL,
        PlaneCapability.STREAM_TELEMETRY,
    }),
    forbidden_capabilities=frozenset({
        PlaneCapability.WRITE_CANONICAL,
        PlaneCapability.APPEND_LEDGER,
        PlaneCapability.SIGN_DECISION,
        PlaneCapability.ENFORCE_CONTAINMENT,
        PlaneCapability.ISSUE_TOKEN,
        PlaneCapability.REVOKE_IDENTITY,
    }),
    storage_mode=StorageMode.APPEND_ONLY,
    network_access=NetworkAccess.INTERNAL_ONLY,
    description="Emits proposals only; cannot directly modify governance or canonical state",
)

GATE_CONTRACT = PlaneContract(
    plane=Plane.GATE,
    allowed_capabilities=frozenset({
        PlaneCapability.READ_CANONICAL,
        PlaneCapability.READ_LEDGER,
        PlaneCapability.SIGN_DECISION,
        PlaneCapability.READ_SHADOW,
    }),
    forbidden_capabilities=frozenset({
        PlaneCapability.WRITE_SHADOW,
        PlaneCapability.ENFORCE_CONTAINMENT,
        PlaneCapability.EMIT_PROPOSAL,
        PlaneCapability.ACCEPT_REQUEST,
    }),
    storage_mode=StorageMode.READ_WRITE,
    network_access=NetworkAccess.INTERNAL_ONLY,
    description="Triple-head evaluation; only plane that can call CommitCoordinator",
)

REFLEX_CONTRACT = PlaneContract(
    plane=Plane.REFLEX,
    allowed_capabilities=frozenset({
        PlaneCapability.ENFORCE_CONTAINMENT,
        PlaneCapability.STREAM_TELEMETRY,
    }),
    forbidden_capabilities=frozenset({
        PlaneCapability.WRITE_CANONICAL,
        PlaneCapability.APPEND_LEDGER,
        PlaneCapability.SIGN_DECISION,
        PlaneCapability.EMIT_PROPOSAL,
        PlaneCapability.ISSUE_TOKEN,
        PlaneCapability.REVOKE_IDENTITY,
        PlaneCapability.COMPILE_POLICY,
    }),
    storage_mode=StorageMode.APPEND_ONLY,
    network_access=NetworkAccess.TELEMETRY_EXPORT,
    description="Kernel-level containment (eBPF/LSM); cannot legislate or mutate governance",
)

INGRESS_CONTRACT = PlaneContract(
    plane=Plane.INGRESS,
    allowed_capabilities=frozenset({
        PlaneCapability.ACCEPT_REQUEST,
        PlaneCapability.READ_CANONICAL,
        PlaneCapability.COMPILE_POLICY,
    }),
    forbidden_capabilities=frozenset({
        PlaneCapability.WRITE_CANONICAL,
        PlaneCapability.APPEND_LEDGER,
        PlaneCapability.SIGN_DECISION,
        PlaneCapability.ENFORCE_CONTAINMENT,
        PlaneCapability.EMIT_PROPOSAL,
        PlaneCapability.ISSUE_TOKEN,
    }),
    storage_mode=StorageMode.NONE,
    network_access=NetworkAccess.EDGE_FACING,
    description="Stateless edge-facing ingress; mTLS, WAF-like prechecks",
)

# ── Registry ──────────────────────────────────────────────────────────

PLANE_CONTRACTS: dict[Plane, PlaneContract] = {
    Plane.CANONICAL: CANONICAL_CONTRACT,
    Plane.SHADOW: SHADOW_CONTRACT,
    Plane.ADAPTIVE: ADAPTIVE_CONTRACT,
    Plane.GATE: GATE_CONTRACT,
    Plane.REFLEX: REFLEX_CONTRACT,
    Plane.INGRESS: INGRESS_CONTRACT,
}


def validate_plane_action(plane: Plane, capability: PlaneCapability) -> bool:
    """Check if a plane is allowed to exercise a capability.

    Args:
        plane: The executing plane
        capability: The capability being exercised

    Returns:
        True if the capability is in the plane's allowed set and NOT
        in its forbidden set.  Returns False otherwise.
    """
    contract = PLANE_CONTRACTS.get(plane)
    if contract is None:
        return False
    if capability in contract.forbidden_capabilities:
        return False
    return capability in contract.allowed_capabilities


__all__ = [
    "Plane",
    "PlaneCapability",
    "StorageMode",
    "NetworkAccess",
    "PlaneContract",
    "PLANE_CONTRACTS",
    "validate_plane_action",
    "CANONICAL_CONTRACT",
    "SHADOW_CONTRACT",
    "ADAPTIVE_CONTRACT",
    "GATE_CONTRACT",
    "REFLEX_CONTRACT",
    "INGRESS_CONTRACT",
]
