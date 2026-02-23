"""
PSIA Canonical Schemas — Pydantic v2 models for all PSIA data types.

All schemas are strict, immutable, and include cryptographic signature fields.
"""

from psia.schemas.capability import (
    CapabilityScope,
    CapabilityToken,
    DelegationPolicy,
    ScopeConstraints,
    TokenBinding,
)
from psia.schemas.cerberus_decision import (
    CerberusDecision,
    CerberusVote,
    CommitPolicy,
    ConstraintsApplied,
    DenyReason,
    QuorumInfo,
)
from psia.schemas.identity import (
    IdentityAttributes,
    IdentityDocument,
    PublicKeyEntry,
    RevocationStatus,
    Signature,
)
from psia.schemas.invariant import (
    InvariantDefinition,
    InvariantEnforcement,
    InvariantExpression,
    InvariantScope,
    InvariantSeverity,
    InvariantTestCase,
)
from psia.schemas.ledger import (
    ExecutionRecord,
    LedgerBlock,
    RecordTimestamps,
    TimeProof,
)
from psia.schemas.policy import PolicyEdge, PolicyGraph, PolicyNode
from psia.schemas.request import (
    Intent,
    RequestContext,
    RequestEnvelope,
    RequestTimestamps,
)
from psia.schemas.shadow_report import (
    DeterminismProof,
    InvariantViolation,
    PrivilegeAnomaly,
    ResourceEnvelope,
    ShadowReport,
    ShadowResults,
    SideEffectSummary,
)

__all__ = [
    # identity
    "PublicKeyEntry",
    "IdentityAttributes",
    "RevocationStatus",
    "Signature",
    "IdentityDocument",
    # capability
    "ScopeConstraints",
    "CapabilityScope",
    "DelegationPolicy",
    "TokenBinding",
    "CapabilityToken",
    # request
    "Intent",
    "RequestContext",
    "RequestTimestamps",
    "RequestEnvelope",
    # policy
    "PolicyNode",
    "PolicyEdge",
    "PolicyGraph",
    # invariant
    "InvariantScope",
    "InvariantSeverity",
    "InvariantEnforcement",
    "InvariantExpression",
    "InvariantTestCase",
    "InvariantDefinition",
    # shadow_report
    "DeterminismProof",
    "ResourceEnvelope",
    "InvariantViolation",
    "PrivilegeAnomaly",
    "SideEffectSummary",
    "ShadowResults",
    "ShadowReport",
    # cerberus_decision
    "DenyReason",
    "ConstraintsApplied",
    "CerberusVote",
    "QuorumInfo",
    "CommitPolicy",
    "CerberusDecision",
    # ledger
    "RecordTimestamps",
    "ExecutionRecord",
    "TimeProof",
    "LedgerBlock",
]
