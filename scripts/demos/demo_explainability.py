"""
Demo Script: Explainability Agent
Demonstrates how to use the Explainability Agent to query governance decisions.

Run this after executing some actions through the Planetary Defense Core.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.core.planetary_defense_monolith import (
    get_planetary_defense_core,
    planetary_interposition,
)
from app.core.explainability_agent import get_explainability_agent


def demo_governance_decision():
    """Demonstrate a governance decision and its explanation."""
    print("=" * 60)
    print("DEMO: Planetary Defense Core + Explainability Agent")
    print("=" * 60)
    
    # Execute a test action
    print("\n1. Executing test action through Planetary Defense Core...")
    try:
        action_id = planetary_interposition(
            actor="DemoUser",
            intent="Test data access request",
            authorized_by="System Admin",
            context={
                "existential_threat": False,
                "intentional_harm_to_human": False,
                "order_bypasses_accountability": False,
                "predicted_harm": "minimal - read-only access",
            }
        )
        print(f"   ✓ Action executed successfully: {action_id}")
    except Exception as e:
        print(f"   ✗ Action failed: {e}")
        return
    
    # Get explanation
    print("\n2. Querying Explainability Agent for decision rationale...")
    agent = get_explainability_agent()
    
    try:
        explanation = agent.explain_decision(action_id)
        
        print(f"\n{'=' * 60}")
        print("EXPLANATION")
        print("=" * 60)
        print(f"\nAction ID: {explanation.action_id}")
        print(f"Timestamp: {explanation.timestamp}")
        print(f"\nSummary: {explanation.summary}")
        print(f"\nDetailed Reasoning:")
        for step in explanation.detailed_reasoning:
            print(f"  {step}")
        
        print(f"\nFour Laws Evaluation:")
        for law, satisfied in explanation.laws_evaluated.items():
            status = "✓ SATISFIED" if satisfied else "✗ VIOLATED"
            print(f"  {law}: {status}")
        
        print(f"\nOutcome: {explanation.outcome}")
        
        if explanation.recommendation:
            print(f"\nRecommendation: {explanation.recommendation}")
        
        print("=" * 60)
        
    except ValueError as e:
        print(f"   ✗ Failed to explain: {e}")


def demo_blocked_action():
    """Demonstrate a blocked action and its explanation."""
    print("\n\n" + "=" * 60)
    print("DEMO: Blocked Action (Law Violation)")
    print("=" * 60)
    
    print("\n1. Attempting action that violates First Law...")
    try:
        action_id = planetary_interposition(
            actor="MaliciousUser",
            intent="Deploy harmful payload",
            authorized_by="Unknown",
            context={
                "existential_threat": False,
                "intentional_harm_to_human": True,  # VIOLATION
                "order_bypasses_accountability": False,
                "predicted_harm": "critical - targeted harm",
            }
        )
        print(f"   ✗ Action should have been blocked!")
    except Exception as e:
        print(f"   ✓ Action correctly blocked: {type(e).__name__}")
        # Action still logged even when blocked - get last entry
        core = get_planetary_defense_core()
        if core.ledger:
            last_record = core.ledger[-1]
            action_id = last_record.action_id
            
            print("\n2. Explaining why action was blocked...")
            agent = get_explainability_agent()
            
            try:
                explanation = agent.explain_decision(action_id)
                
                print(f"\n{'=' * 60}")
                print("EXPLANATION OF BLOCKED ACTION")
                print("=" * 60)
                print(f"\nSummary: {explanation.summary}")
                print(f"\nFour Laws Evaluation:")
                for law, satisfied in explanation.laws_evaluated.items():
                    status = "✓" if satisfied else "✗ VIOLATED"
                    print(f"  {law}: {status}")
                
                if explanation.recommendation:
                    print(f"\n⚠️  Recommendation: {explanation.recommendation}")
                
                print("=" * 60)
                
            except ValueError as e:
                print(f"   ✗ Failed to explain: {e}")


def demo_recent_history():
    """Show recent decision history."""
    print("\n\n" + "=" * 60)
    print("DEMO: Recent Decision History")
    print("=" * 60)
    
    agent = get_explainability_agent()
    explanations = agent.explain_latest_decisions(limit=5)
    
    if not explanations:
        print("\nNo decisions recorded yet.")
        return
    
    print(f"\nShowing {len(explanations)} most recent decision(s):\n")
    
    for i, ex in enumerate(explanations, 1):
        print(f"{i}. [{ex.outcome}] {ex.summary}")
        print(f"   Action ID: {ex.action_id}")
        print(f"   Timestamp: {ex.timestamp}")
        print()


if __name__ == "__main__":
    print("\n🌍 Project-AI Explainability Demo\n")
    
    # Run demos
    demo_governance_decision()
    demo_blocked_action()
    demo_recent_history()
    
    print("\n✓ Demo complete!")
    print("\nTo test via API:")
    print("  1. Start server: python -m uvicorn api.main:app --reload")
    print("  2. Query: curl http://localhost:8000/explain")
    print()
