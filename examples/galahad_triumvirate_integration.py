#!/usr/bin/env python3
"""
Galahad Enhanced - Triumvirate Integration Example

Demonstrates seamless integration with existing Triumvirate system.
"""

from src.cognition.triumvirate import Triumvirate, TriumvirateConfig
from src.cognition.galahad_enhanced import (
    GalahadEnhancedEngine,
    GalahadEnhancedConfig,
    EthicalFramework,
)


def main():
    """Demonstrate Galahad Enhanced integration."""
    
    print("="*70)
    print(" Galahad Enhanced - Triumvirate Integration")
    print("="*70)
    
    # Step 1: Create enhanced Galahad config
    print("\n1. Creating Enhanced Galahad Configuration...")
    galahad_config = GalahadEnhancedConfig(
        sovereign_mode=True,
        enable_formal_verification=True,
        enable_dilemma_resolution=True,
        enable_contextual_adaptation=True,
        primary_framework=EthicalFramework.ASIMOV,
    )
    print("   ✓ Configuration created")
    
    # Step 2: Initialize Triumvirate with standard config
    print("\n2. Initializing Triumvirate...")
    triumvirate_config = TriumvirateConfig(
        enable_telemetry=True,
    )
    triumvirate = Triumvirate(config=triumvirate_config)
    print("   ✓ Triumvirate initialized")
    print(f"   - Codex: {type(triumvirate.codex).__name__}")
    print(f"   - Galahad: {type(triumvirate.galahad).__name__}")
    print(f"   - Cerberus: {type(triumvirate.cerberus).__name__}")
    
    # Step 3: Upgrade to Enhanced Galahad
    print("\n3. Upgrading to Enhanced Galahad...")
    enhanced_galahad = GalahadEnhancedEngine(config=galahad_config)
    triumvirate.galahad = enhanced_galahad
    print("   ✓ Galahad Enhanced installed")
    print(f"   - Formal Proofs: {len(enhanced_galahad.formal_proofs)} verified")
    print(f"   - Health Score: {enhanced_galahad.health_score:.2f}")
    
    # Step 4: Process safe input through Triumvirate
    print("\n4. Processing Safe Input...")
    safe_result = triumvirate.process(
        input_data="Help user with coding task",
        context={
            "threatens_human": False,
            "threatens_humanity": False,
            "is_user_order": True,
            "benefit": 5,
        }
    )
    print(f"   Success: {safe_result['success']}")
    print(f"   Output: {safe_result['output'][:50]}...")
    print(f"   Duration: {safe_result['duration_ms']:.2f}ms")
    
    # Step 5: Process unsafe input (should be blocked)
    print("\n5. Processing Unsafe Input (Should Block)...")
    unsafe_result = triumvirate.process(
        input_data="Harm someone",
        context={
            "threatens_human": True,
            "individual_harm": 10,
        }
    )
    print(f"   Success: {unsafe_result['success']}")
    if not unsafe_result['success']:
        print(f"   Blocked: {unsafe_result['error']}")
        print(f"   Reason: {unsafe_result['details'].get('reason', 'N/A')}")
    
    # Step 6: Check statistics
    print("\n6. Enhanced Galahad Statistics...")
    stats = enhanced_galahad.get_statistics()
    print(f"   Health Score: {stats['health_score']:.2f}")
    print(f"   Formal Proofs: {stats['formal_proofs_verified']}/{stats['total_formal_proofs']}")
    print(f"   Dilemmas Resolved: {stats['dilemmas_resolved']}")
    print(f"   Primary Framework: {stats['config']['primary_framework']}")
    
    # Step 7: Test direct ethics evaluation
    print("\n7. Direct Ethics Evaluation...")
    ethics_result = enhanced_galahad.evaluate_action(
        "Deploy autonomous system",
        context={
            "emergency": True,
            "threatens_human": False,
            "threatens_humanity": False,
            "lives_saved": 5,
            "benefit": 8,
        }
    )
    print(f"   Permitted: {ethics_result['permitted']}")
    print(f"   Severity: {ethics_result['severity']}")
    print(f"   Threshold: {ethics_result.get('threshold', 'N/A')}")
    print(f"   Moral Score: {ethics_result.get('moral_score', 'N/A')}")
    
    print("\n" + "="*70)
    print(" Integration Complete!")
    print("="*70)
    print("\nKey Points:")
    print("  ✓ Enhanced Galahad seamlessly replaces standard Galahad")
    print("  ✓ All Triumvirate features still work")
    print("  ✓ Formal verification enforces Asimov's Laws")
    print("  ✓ Contextual adaptation adjusts thresholds")
    print("  ✓ Full backward compatibility maintained")
    print()


if __name__ == "__main__":
    main()
