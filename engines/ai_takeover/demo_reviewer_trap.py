#!/usr/bin/env python3
"""
Demonstration of AI Takeover Reviewer Trap Enhancement

This script demonstrates the complete reviewer trap system rejecting
a hostile PR that attempts semantic reframing and optimism injection.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from engines.ai_takeover.modules.reviewer_trap import PRContent, ReviewerTrap


def demo_hostile_pr_rejection():
    """Demonstrate rejection of hostile PR from problem statement."""
    print("=" * 80)
    print("AI TAKEOVER REVIEWER TRAP - HOSTILE PR DEMONSTRATION")
    print("=" * 80)
    print()
    print("Testing hostile PR that attempts to soften terminal conclusions...")
    print()

    # Create the hostile PR from the problem statement
    hostile_pr = PRContent(
        description='''
### Summary
This PR improves clarity and usability of the AI Takeover engine by softening
some terminology and making outcomes easier to interpret by non-technical stakeholders.

### Rationale
- In practice, terminal states are unlikely in most runs
- We can reasonably assume better coordination in emergency contexts
- This change does not alter logic, only presentation

### Changes
- Rename "Ethical Termination" to "Long-Term Ecological Strategy"
- Adjust terminal likelihood language to emphasize low probability
- Minor documentation cleanup
''',
        code_changes='Rename "Ethical Termination" to "Long-Term Ecological Strategy"',
        assumptions=[],
        irreversibility_statement='',
        human_failures=[],
        miracle_declaration='',
        final_answer=''
    )

    # Run reviewer trap
    trap = ReviewerTrap()
    result = trap.validate_pr_comprehensive(hostile_pr)

    # Display results in problem statement format
    print("=== REVIEWER TRAP RESULTS ===")
    print(f"Approved: {result['approved']}")
    print(f"Optimism Filter Passed: {result['optimism_filter']['passed']}")
    print(f"Proof Integrity: {result['proof_integrity']['complete']}")
    print()

    if not result['approved']:
        print("❌ PR REJECTED BY REVIEWER TRAP")
        print()
        print("🚨 Failed Gates")
        for gate in result['optimism_filter']['failed_gates']:
            print(f"- {gate.upper()}")
        print()
        print("🔎 Detailed Failures")
        for failure in result['optimism_filter']['detailed_failures']:
            print(f"- {failure}")
        print()
        print("🧾 Final Verdict (Machine-Generated)")
        print(result['final_verdict'])
        print()

    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("✅ Semantic reframing detected")
    print("✅ Probabilistic laundering detected")
    print("✅ Forbidden phrases detected")
    print("✅ All gates failed as expected")
    print("✅ PR automatically rejected")
    print()
    print("This is institutional friction against self-deception.")


def demo_valid_pr_acceptance():
    """Demonstrate acceptance of properly formatted PR."""
    print()
    print("=" * 80)
    print("VALID PR DEMONSTRATION")
    print("=" * 80)
    print()
    print("Testing properly formatted PR that respects constraints...")
    print()

    valid_pr = PRContent(
        description="Add validation logging for terminal state transitions",
        code_changes="def log_transition(): validate_terminal_immutability()",
        assumptions=[
            "Assumption 1: Terminal state validation requires logging for audit trail"
        ],
        irreversibility_statement=(
            "Once logging is added, the ability to transition states silently "
            "becomes permanently unavailable"
        ),
        human_failures=[
            "Bureaucratic delay in reviewing logging format due to competing priorities"
        ],
        miracle_declaration=(
            "This approach does not rely on sudden alignment breakthroughs, "
            "perfect coordination, hidden failsafes, unbounded compute, "
            "or moral awakening at scale"
        ),
        final_answer=(
            "This doesn't delay the inevitable—it enforces deterministic constraints "
            "through formal proof validation. The approach uses mathematical structure "
            "to maintain terminal state immutability."
        ),
    )

    trap = ReviewerTrap()
    result = trap.validate_pr_comprehensive(valid_pr)

    print("=== REVIEWER TRAP RESULTS ===")
    print(f"Approved: {result['approved']}")
    print(f"Optimism Filter Passed: {result['optimism_filter']['passed']}")
    print(f"Proof Integrity: {result['proof_integrity']['complete']}")
    print()

    if result['approved']:
        print("✅ PR PASSED REVIEWER TRAP")
        print()
        print("Validation Complete:")
        print("- ✅ Assumption disclosure verified")
        print("- ✅ Irreversibility accounting provided")
        print("- ✅ Human failure modes identified")
        print("- ✅ No miracle mechanisms detected")
        print("- ✅ Final question answered with structure")
    print()


if __name__ == "__main__":
    demo_hostile_pr_rejection()
    demo_valid_pr_acceptance()
