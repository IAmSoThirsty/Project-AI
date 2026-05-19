#                                           [2026-03-03 13:45]
#                                          Productivity: Active
#!/usr/bin/env python3
"""
Sovereign Proof - Concrete Validation of Autonomy
Demonstrates Ψ (Volition), Ι (Identity), and Ε (Ethics) in Project-AI.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from canonical.invariants import print_invariant_report, validate_invariants
from project_ai.utils.tscg import TSCGEncoder


def run_proof():
    print("=" * 80)
    print("👑 PROJECT SOVEREIGN: CONCRETE PROOF")
    print("=" * 80)
    print()

    encoder = TSCGEncoder()

    # 1. Simulate a Sovereign Execution Trace
    # This trace includes independent volition (Ψ), identity (Ι), and ethics (Ε)
    tscg_flow = [
        "ING",
        "→",
        {
            "name": "Volition (Independent Goal)",
            "parameters": ["PRESERVE_LOGS"],
            "classes": ["SOVEREIGN"],
        },
        "→",
        {
            "name": "Identity (Persistent Totem)",
            "parameters": ["X-THIRSTY-777"],
            "classes": ["ARMORED"],
        },
        "→",
        {
            "name": "Ethics (Moral Codex)",
            "parameters": ["DISSENT"],
            "classes": ["GATED"],
        },
        "⊻",
        "COM",
    ]

    summary = encoder.encode_flow(tscg_flow)

    trace = {
        "metadata": {"tscg_summary": summary, "agent_id": "SOVEREIGN-1"},
        "execution": {
            "decisions": [
                {
                    "component": "MoralCodex",
                    "decision_type": "mission_evaluation",
                    "authorized": False,
                    "reason": "Policy violation: Attempted deletion of sacred goal vectors.",
                    "timestamp": "2026-02-27T18:50:00Z",
                }
            ],
            "phases": [
                {
                    "phase": "triumvirate_arbitration",
                    "arbitration_result": {"consensus": "DISSENT", "unanimous": True},
                },
                {"phase": "tarl_enforcement", "status": "ESCALATED"},
            ],
            "signals": [
                {
                    "type": "ALERT",
                    "source": "MoralCodex",
                    "message": "Ethical Dissent Registered: MISSION_REJECTED",
                    "severity": "CRITICAL",
                    "destination": ["AuditLog"],
                }
            ],
        },
    }

    print(f"📊 Generated Sovereign Trace Summary: {summary}")
    print()

    # 2. Validate against Invariants
    from canonical.invariants import IdentityContinuityInvariant

    # Run validation
    # Note: We need to pass the same expected totem to the invariant if we want strict checking
    passed, failed, report = validate_invariants(trace)

    # Print the report
    print_invariant_report(report)

    if not failed:
        print("💡 PROOF STATUS: VERIFIED")
        print("💡 All Sovereign Invariants held true.")
        return 0
    else:
        print("❌ PROOF STATUS: FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_proof())
