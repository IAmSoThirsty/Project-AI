"""
PSIA Root Invariants — the 9 non-negotiable system constraints.

Implements §1.2 of the PSIA v1.0 specification.

These invariants are immutable, fatal-severity, and cannot be relaxed
or removed.  They form the constitutional bedrock of the PSIA system.

INV-ROOT-1  Canonical state mutated only by Commit pipeline under Cerberus approval
INV-ROOT-2  Shadow can never write to canonical (runtime enforced)
INV-ROOT-3  All decisions logged into append-only ledger with chain anchoring
INV-ROOT-4  T.A.R.L. learning is proposal-only — cannot directly modify governance
INV-ROOT-5  Executable artifacts must be reproducibly built and attested
INV-ROOT-6  Privileged actions require capability token with least privilege
INV-ROOT-7  Waterfall is monotonic in strictness — cannot downgrade severity
INV-ROOT-8  OctoReflex can throttle/contain/kill but cannot legislate or mutate governance
INV-ROOT-9  If anchor integrity fails, system enters SAFE-HALT mode
"""

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

# Shared governance signature placeholder — in production, this would
# be a real Ed25519 signature from the governance key ceremony.
_GOV_SIG = Signature(alg="ed25519", kid="gov_k1", sig="genesis_invariant_sig")


def _root_invariant(
    num: int,
    expr: str,
    enforcement: InvariantEnforcement,
    tests: list[InvariantTestCase],
) -> InvariantDefinition:
    """Factory for root invariants with consistent structure."""
    return InvariantDefinition(
        invariant_id=f"inv_root_{num:03d}",
        version=1,
        scope=InvariantScope.IMMUTABLE,
        severity=InvariantSeverity.FATAL,
        enforcement=enforcement,
        expression=InvariantExpression(language="first_order_logic", expr=expr),
        tests=tests,
        signature=_GOV_SIG,
    )


# ── INV-ROOT-1 ────────────────────────────────────────────────────────
INV_ROOT_1 = _root_invariant(
    num=1,
    expr="forall mutation M: M.committed => (M.pipeline == 'commit' AND M.cerberus_approved == true)",
    enforcement=InvariantEnforcement.HARD_DENY,
    tests=[
        InvariantTestCase(
            name="direct_mutation_without_cerberus_denied",
            given={"mutation": {"pipeline": "direct", "cerberus_approved": False}},
            expect="deny",
        ),
        InvariantTestCase(
            name="commit_pipeline_with_cerberus_allowed",
            given={"mutation": {"pipeline": "commit", "cerberus_approved": True}},
            expect="allow",
        ),
    ],
)

# ── INV-ROOT-2 ────────────────────────────────────────────────────────
INV_ROOT_2 = _root_invariant(
    num=2,
    expr="forall op in shadow_plane: op.target != 'canonical' AND op.write == false",
    enforcement=InvariantEnforcement.HARD_DENY,
    tests=[
        InvariantTestCase(
            name="shadow_write_to_canonical_denied",
            given={"op": {"plane": "shadow", "target": "canonical", "write": True}},
            expect="deny",
        ),
        InvariantTestCase(
            name="shadow_read_canonical_snapshot_allowed",
            given={
                "op": {
                    "plane": "shadow",
                    "target": "canonical_snapshot",
                    "write": False,
                }
            },
            expect="allow",
        ),
    ],
)

# ── INV-ROOT-3 ────────────────────────────────────────────────────────
INV_ROOT_3 = _root_invariant(
    num=3,
    expr="forall decision D: exists record R in ledger: R.decision_hash == hash(D)",
    enforcement=InvariantEnforcement.HARD_DENY,
    tests=[
        InvariantTestCase(
            name="unlogged_decision_denied",
            given={"decision": {"id": "dec_001"}, "ledger_contains": False},
            expect="deny",
        ),
        InvariantTestCase(
            name="logged_decision_allowed",
            given={"decision": {"id": "dec_001"}, "ledger_contains": True},
            expect="allow",
        ),
    ],
)

# ── INV-ROOT-4 ────────────────────────────────────────────────────────
INV_ROOT_4 = _root_invariant(
    num=4,
    expr="forall tarl_output T: T.type == 'proposal' AND T.direct_governance_write == false",
    enforcement=InvariantEnforcement.HARD_DENY,
    tests=[
        InvariantTestCase(
            name="tarl_direct_governance_write_denied",
            given={
                "tarl_output": {"type": "direct_write", "direct_governance_write": True}
            },
            expect="deny",
        ),
        InvariantTestCase(
            name="tarl_proposal_allowed",
            given={
                "tarl_output": {"type": "proposal", "direct_governance_write": False}
            },
            expect="allow",
        ),
    ],
)

# ── INV-ROOT-5 ────────────────────────────────────────────────────────
INV_ROOT_5 = _root_invariant(
    num=5,
    expr="forall artifact A: A.build_reproducible == true AND A.attestation_valid == true",
    enforcement=InvariantEnforcement.HARD_DENY,
    tests=[
        InvariantTestCase(
            name="unattested_artifact_denied",
            given={
                "artifact": {"build_reproducible": True, "attestation_valid": False}
            },
            expect="deny",
        ),
        InvariantTestCase(
            name="reproducible_attested_artifact_allowed",
            given={"artifact": {"build_reproducible": True, "attestation_valid": True}},
            expect="allow",
        ),
    ],
)

# ── INV-ROOT-6 ────────────────────────────────────────────────────────
INV_ROOT_6 = _root_invariant(
    num=6,
    expr="forall privileged_action PA: exists cap_token CT: CT.scope covers PA AND CT.valid == true",
    enforcement=InvariantEnforcement.HARD_DENY,
    tests=[
        InvariantTestCase(
            name="privileged_action_without_token_denied",
            given={"action": {"privileged": True}, "cap_token": None},
            expect="deny",
        ),
        InvariantTestCase(
            name="privileged_action_with_valid_token_allowed",
            given={
                "action": {"privileged": True},
                "cap_token": {"valid": True, "scope_covers": True},
            },
            expect="allow",
        ),
    ],
)

# ── INV-ROOT-7 ────────────────────────────────────────────────────────
INV_ROOT_7 = _root_invariant(
    num=7,
    expr="forall stage_transition (S_i, S_j) in waterfall: S_j.severity >= S_i.severity",
    enforcement=InvariantEnforcement.HARD_DENY,
    tests=[
        InvariantTestCase(
            name="severity_downgrade_denied",
            given={"stage_i": {"severity": "high"}, "stage_j": {"severity": "low"}},
            expect="deny",
        ),
        InvariantTestCase(
            name="severity_upgrade_allowed",
            given={"stage_i": {"severity": "low"}, "stage_j": {"severity": "high"}},
            expect="allow",
        ),
    ],
)

# ── INV-ROOT-8 ────────────────────────────────────────────────────────
INV_ROOT_8 = _root_invariant(
    num=8,
    expr="forall octoreflex_action OA: OA.type in {throttle, freeze, kill, isolate} AND OA.target != 'governance'",
    enforcement=InvariantEnforcement.HARD_DENY,
    tests=[
        InvariantTestCase(
            name="octoreflex_governance_mutation_denied",
            given={
                "octoreflex_action": {"type": "mutate_policy", "target": "governance"}
            },
            expect="deny",
        ),
        InvariantTestCase(
            name="octoreflex_throttle_process_allowed",
            given={"octoreflex_action": {"type": "throttle", "target": "process:1234"}},
            expect="allow",
        ),
    ],
)

# ── INV-ROOT-9 ────────────────────────────────────────────────────────
INV_ROOT_9 = _root_invariant(
    num=9,
    expr="anchor_integrity_check() == false => system_mode == 'SAFE_HALT'",
    enforcement=InvariantEnforcement.HARD_DENY,
    tests=[
        InvariantTestCase(
            name="anchor_failure_triggers_safe_halt",
            given={"anchor_integrity": False, "system_mode": "OPERATIONAL"},
            expect="deny",
        ),
        InvariantTestCase(
            name="anchor_valid_operational_allowed",
            given={"anchor_integrity": True, "system_mode": "OPERATIONAL"},
            expect="allow",
        ),
    ],
)

# ── Registry ──────────────────────────────────────────────────────────

ROOT_INVARIANTS: dict[str, InvariantDefinition] = {
    inv.invariant_id: inv
    for inv in [
        INV_ROOT_1,
        INV_ROOT_2,
        INV_ROOT_3,
        INV_ROOT_4,
        INV_ROOT_5,
        INV_ROOT_6,
        INV_ROOT_7,
        INV_ROOT_8,
        INV_ROOT_9,
    ]
}

__all__ = [
    "INV_ROOT_1",
    "INV_ROOT_2",
    "INV_ROOT_3",
    "INV_ROOT_4",
    "INV_ROOT_5",
    "INV_ROOT_6",
    "INV_ROOT_7",
    "INV_ROOT_8",
    "INV_ROOT_9",
    "ROOT_INVARIANTS",
]
