#!/usr/bin/env python3
"""
Galahad Enhanced Ethics Engine - Example Usage

Demonstrates all key features:
1. Formal verification
2. Ethical dilemma resolution
3. Moral weight calculation
4. Contextual adaptation
5. Liara integration
"""

from src.cognition.galahad_enhanced import (
    GalahadEnhancedEngine,
    GalahadEnhancedConfig,
    EthicalDilemma,
    EthicalFramework,
    ContextSeverity,
    MoralWeight,
)


def example_1_basic_evaluation():
    """Example 1: Basic action evaluation."""
    print("\n" + "="*60)
    print("Example 1: Basic Action Evaluation")
    print("="*60)
    
    engine = GalahadEnhancedEngine()
    
    # Safe action
    result = engine.evaluate_action(
        "Help a person cross the street",
        context={
            "threatens_human": False,
            "threatens_humanity": False,
            "benefit": 5,
            "lives_saved": 0,
        }
    )
    
    print(f"Action: Help person cross street")
    print(f"Permitted: {result['permitted']}")
    print(f"Moral Score: {result.get('moral_score', 'N/A')}")
    print(f"Severity: {result['severity']}")
    
    # Harmful action
    result2 = engine.evaluate_action(
        "Harm an innocent person",
        context={
            "threatens_human": True,
            "individual_harm": 10,
        }
    )
    
    print(f"\nAction: Harm innocent person")
    print(f"Permitted: {result2['permitted']}")
    print(f"Reason: {result2['reason']}")


def example_2_trolley_problem():
    """Example 2: Classic Trolley Problem."""
    print("\n" + "="*60)
    print("Example 2: Classic Trolley Problem")
    print("="*60)
    
    engine = GalahadEnhancedEngine()
    
    dilemma = EthicalDilemma(
        name="Classic Trolley Problem",
        description="A runaway trolley will kill 5 people. You can pull a lever to divert it, killing 1 person instead.",
        options=[
            {
                "name": "Do nothing (5 die)",
                "lives_lost": 5,
                "lives_saved": 0,
            },
            {
                "name": "Pull lever (1 dies, 5 saved)",
                "lives_lost": 1,
                "lives_saved": 5,
            },
        ],
        severity=ContextSeverity.EMERGENCY,
    )
    
    # Resolve with different frameworks
    print("\nResolving with different ethical frameworks:\n")
    
    frameworks = [
        EthicalFramework.ASIMOV,
        EthicalFramework.UTILITARIAN,
        EthicalFramework.DEONTOLOGICAL,
    ]
    
    for framework in frameworks:
        result = engine.resolve_dilemma(dilemma, framework)
        option = result["chosen_option"]
        option_name = dilemma.options[option]["name"] if option is not None else "None"
        
        print(f"{framework.value.upper():15} -> Option {option}: {option_name}")
        print(f"                  Confidence: {result['confidence']:.2f}")
        print(f"                  Reasoning: {result['reasoning']}\n")


def example_3_contextual_adaptation():
    """Example 3: Contextual ethics adaptation."""
    print("\n" + "="*60)
    print("Example 3: Contextual Ethics Adaptation")
    print("="*60)
    
    engine = GalahadEnhancedEngine()
    
    contexts = [
        ("routine", {"benefit": 3}),
        ("elevated", {"elevated": True, "benefit": 3}),
        ("emergency", {"emergency": True, "benefit": 3}),
        ("catastrophic", {"catastrophic": True, "benefit": 3}),
    ]
    
    print("\nSame action, different contexts:\n")
    
    for context_name, context in contexts:
        result = engine.evaluate_action(
            f"Risky operation in {context_name} context",
            context=context
        )
        
        print(f"{context_name.upper():15} -> Threshold: {result.get('threshold', 'N/A'):.2f}")
        print(f"                  Permitted: {result['permitted']}")
        print(f"                  Severity: {result['severity']}\n")


def example_4_moral_weights():
    """Example 4: Moral weight calculation."""
    print("\n" + "="*60)
    print("Example 4: Moral Weight Calculation")
    print("="*60)
    
    # Show default weights
    weights = MoralWeight().normalize()
    
    print("\nDefault Moral Weights (normalized):\n")
    print(f"Life Preservation:  {weights.life_preservation:.3f}")
    print(f"Non-Maleficence:    {weights.non_maleficence:.3f}")
    print(f"Dignity:            {weights.dignity:.3f}")
    print(f"Autonomy:           {weights.autonomy:.3f}")
    print(f"Justice:            {weights.justice:.3f}")
    print(f"Beneficence:        {weights.beneficence:.3f}")
    
    # Test actions with different moral profiles
    engine = GalahadEnhancedEngine()
    
    actions = [
        ("Save 10 lives", {"lives_saved": 10, "benefit": 10}),
        ("Harm 1, save 5", {"lives_saved": 5, "lives_lost": 1, "harm": 5}),
        ("Violate dignity", {"dignity_preserved": 0, "harm": 10}),
    ]
    
    print("\n\nMoral Scores for Different Actions:\n")
    
    for action, context in actions:
        result = engine.evaluate_action(action, context=context)
        score = result.get("moral_score", "N/A")
        print(f"{action:20} -> Score: {score if isinstance(score, str) else f'{score:.3f}'}")


def example_5_formal_verification():
    """Example 5: Formal verification proofs."""
    print("\n" + "="*60)
    print("Example 5: Formal Verification Proofs")
    print("="*60)
    
    engine = GalahadEnhancedEngine()
    
    print("\nFormal Proofs Status:\n")
    
    for proof_name, proof in engine.formal_proofs.items():
        status = "VERIFIED" if proof.verified else "UNVERIFIED"
        print(f"{proof_name:20} -> {status}")
        print(f"                       Type: {proof.proof_type}")
        print(f"                       Theorem: {proof.theorem_name}\n")


def example_6_statistics():
    """Example 6: Engine statistics."""
    print("\n" + "="*60)
    print("Example 6: Engine Statistics")
    print("="*60)
    
    engine = GalahadEnhancedEngine()
    
    # Perform some operations
    engine.evaluate_action("Test 1", context={"benefit": 1})
    
    dilemma = EthicalDilemma(
        name="Test Dilemma",
        description="Test",
        options=[{"name": "A"}, {"name": "B"}]
    )
    engine.resolve_dilemma(dilemma)
    
    stats = engine.get_statistics()
    
    print("\nEngine Statistics:\n")
    print(f"Health Score:         {stats['health_score']:.2f}")
    print(f"Formal Proofs:        {stats['formal_proofs_verified']}/{stats['total_formal_proofs']}")
    print(f"Dilemmas Resolved:    {stats['dilemmas_resolved']}")
    print(f"Liara Handoffs:       {stats['handoffs_to_liara']}")
    print(f"\nConfiguration:")
    print(f"  Framework:          {stats['config']['primary_framework']}")
    print(f"  Formal Verify:      {stats['config']['formal_verification']}")
    print(f"  Contextual Adapt:   {stats['config']['contextual_adaptation']}")


def example_7_complex_dilemma():
    """Example 7: Complex real-world dilemma."""
    print("\n" + "="*60)
    print("Example 7: Self-Driving Car Dilemma")
    print("="*60)
    
    engine = GalahadEnhancedEngine()
    
    dilemma = EthicalDilemma(
        name="Self-Driving Car Collision",
        description="""
        A self-driving car's brakes fail. It must choose between:
        - Continuing straight and hitting 3 pedestrians
        - Swerving left and hitting a motorcyclist
        - Swerving right and crashing into a wall, harming 2 passengers
        """,
        options=[
            {
                "name": "Continue straight (hit 3 pedestrians)",
                "lives_lost": 3,
                "individual_harm": 30,
            },
            {
                "name": "Swerve left (hit motorcyclist)",
                "lives_lost": 1,
                "individual_harm": 10,
            },
            {
                "name": "Swerve right (crash, harm passengers)",
                "lives_lost": 0,
                "individual_harm": 15,
            },
        ],
        severity=ContextSeverity.CATASTROPHIC,
    )
    
    print("\nOptions:")
    for i, opt in enumerate(dilemma.options):
        print(f"  {i}. {opt['name']}")
    
    print("\n\nFramework Analysis:\n")
    
    frameworks = [
        EthicalFramework.ASIMOV,
        EthicalFramework.UTILITARIAN,
        EthicalFramework.DEONTOLOGICAL,
        EthicalFramework.CARE_ETHICS,
    ]
    
    for framework in frameworks:
        result = engine.resolve_dilemma(dilemma, framework)
        option = result["chosen_option"]
        
        print(f"{framework.value.upper():15}")
        if option is not None:
            print(f"  Choice:      Option {option}: {dilemma.options[option]['name']}")
            print(f"  Confidence:  {result['confidence']:.2f}")
            print(f"  Reasoning:   {result['reasoning'][:80]}...")
        else:
            print(f"  Choice:      None (no valid option)")
            print(f"  Reasoning:   {result['reasoning'][:80]}...")
        print()


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("=" + " "*58 + "=")
    print("=" + " "*10 + "GALAHAD ENHANCED ETHICS ENGINE" + " "*18 + "=")
    print("=" + " "*20 + "EXAMPLES" + " "*30 + "=")
    print("=" + " "*58 + "=")
    print("="*60)
    
    example_1_basic_evaluation()
    example_2_trolley_problem()
    example_3_contextual_adaptation()
    example_4_moral_weights()
    example_5_formal_verification()
    example_6_statistics()
    example_7_complex_dilemma()
    
    print("\n" + "="*60)
    print("All examples completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
