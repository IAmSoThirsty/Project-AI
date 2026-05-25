"""PSIA plane contracts — separation of concerns between system planes."""
from __future__ import annotations

from enum import Enum


class Plane(str, Enum):
    CANONICAL = "canonical"
    SHADOW = "shadow"
    INGRESS = "ingress"
    REFLEX = "reflex"
    LEGISLATIVE = "legislative"
    AUDIT = "audit"


class PlaneCapability(str, Enum):
    WRITE_CANONICAL = "write_canonical"
    READ_CANONICAL = "read_canonical"
    ACCEPT_REQUEST = "accept_request"
    EMIT_PROPOSAL = "emit_proposal"
    COMPILE_POLICY = "compile_policy"
    EMIT_SHADOW = "emit_shadow"
    READ_SHADOW = "read_shadow"
    AUDIT_LOG = "audit_log"
    EMIT_REFLEX = "emit_reflex"


PLANE_CONTRACTS: dict[Plane, set[PlaneCapability]] = {
    Plane.CANONICAL: {
        PlaneCapability.WRITE_CANONICAL,
        PlaneCapability.READ_CANONICAL,
        PlaneCapability.AUDIT_LOG,
    },
    Plane.SHADOW: {
        PlaneCapability.READ_CANONICAL,
        PlaneCapability.EMIT_SHADOW,
        PlaneCapability.READ_SHADOW,
    },
    Plane.INGRESS: {
        PlaneCapability.ACCEPT_REQUEST,
        PlaneCapability.READ_CANONICAL,
    },
    Plane.REFLEX: {
        PlaneCapability.READ_CANONICAL,
        PlaneCapability.EMIT_REFLEX,
        PlaneCapability.AUDIT_LOG,
    },
    Plane.LEGISLATIVE: {
        PlaneCapability.EMIT_PROPOSAL,
        PlaneCapability.COMPILE_POLICY,
        PlaneCapability.READ_CANONICAL,
        PlaneCapability.AUDIT_LOG,
    },
    Plane.AUDIT: {
        PlaneCapability.READ_CANONICAL,
        PlaneCapability.READ_SHADOW,
        PlaneCapability.AUDIT_LOG,
    },
}


def validate_plane_action(plane: Plane, capability: PlaneCapability) -> bool:
    return capability in PLANE_CONTRACTS.get(plane, set())
