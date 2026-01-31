"""
God Tier System Demo
Demonstrates the integrated God Tier system with all components.
"""

import logging
import time

import numpy as np

from src.app.core.god_tier_config import load_god_tier_config
from src.app.core.god_tier_integration import (
    GodTierIntegratedSystem,
    get_god_tier_system,
    initialize_god_tier_system,
)

# Setup basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def demo_voice_system(system: GodTierIntegratedSystem):
    """Demonstrate voice system"""
    print("\n" + "=" * 80)
    print("VOICE SYSTEM DEMONSTRATION")
    print("=" * 80)

    if not system.voice_registry:
        print("Voice system not available")
        return

    # List available models
    models = system.voice_registry.list_models()
    print(f"\nAvailable voice models: {len(models)}")
    for metadata in models:
        print(f"  - {metadata.name} ({metadata.model_id})")

    # Test voice synthesis
    if models:
        model_id = models[0].model_id
        model = system.voice_registry.get_model(model_id)
        if model:
            print(f"\nTesting synthesis with {model.metadata.name}...")
            response = model.synthesize("Hello from the God Tier system!")
            print(f"  Success: {response.success}")
            print(f"  Duration: {response.duration_ms:.2f}ms")


def demo_visual_system(system: GodTierIntegratedSystem):
    """Demonstrate visual system"""
    print("\n" + "=" * 80)
    print("VISUAL SYSTEM DEMONSTRATION")
    print("=" * 80)

    if not system.visual_registry:
        print("Visual system not available")
        return

    # List available models
    models = system.visual_registry.list_models()
    print(f"\nAvailable visual models: {len(models)}")
    for model_id in models:
        print(f"  - {model_id}")

    # Test visual detection
    if models:
        model = system.visual_registry.get_model(models[0])
        if model:
            print(f"\nTesting detection with {model.model_name}...")
            # Generate synthetic frame
            frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
            cue_data = model.detect(frame)
            print(f"  Detected: {cue_data.is_present}")
            print(f"  Emotion: {cue_data.emotion.value}")
            print(f"  Confidence: {cue_data.emotion_confidence:.2f}")


def demo_conversation_system(system: GodTierIntegratedSystem):
    """Demonstrate conversation system"""
    print("\n" + "=" * 80)
    print("CONVERSATION SYSTEM DEMONSTRATION")
    print("=" * 80)

    if not system.context_engine:
        print("Conversation system not available")
        return

    # Start session
    user_id = "demo_user"
    session_id = system.context_engine.start_session(user_id)
    print(f"\nStarted session: {session_id}")

    # Add some turns
    conversations = [
        ("What's the weather today?", "The weather is sunny with a high of 75°F."),
        (
            "That's great! What should I wear?",
            "Light clothing would be appropriate for 75°F weather.",
        ),
        ("Thanks for the advice!", "You're welcome! Have a great day!"),
    ]

    for user_input, system_response in conversations:
        turn = system.context_engine.add_turn(session_id, user_input, system_response)
        if turn:
            print(
                f"\nTurn {len(system.context_engine._active_sessions[session_id].turns)}:"
            )
            print(f"  User: {user_input}")
            print(f"  Intent: {turn.detected_intent.value}")
            print(f"  Topics: {turn.topics}")

    # Get context
    context = system.context_engine.get_context(session_id)
    print("\nSession context:")
    print(f"  Total turns: {context.get('turn_count', 0)}")
    print(f"  Active topics: {context.get('active_topics', [])}")

    # End session
    system.context_engine.end_session(session_id)
    print("\nSession ended")


def demo_fusion_system(system: GodTierIntegratedSystem):
    """Demonstrate multi-modal fusion"""
    print("\n" + "=" * 80)
    print("MULTI-MODAL FUSION DEMONSTRATION")
    print("=" * 80)

    if not system.fusion_engine:
        print("Fusion system not available")
        return

    # Process interaction
    user_id = "demo_user"
    text_input = "I'm feeling happy today!"

    # Generate synthetic visual frame
    frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)

    print("\nProcessing user interaction...")
    print(f"  User ID: {user_id}")
    print(f"  Text: {text_input}")
    print(f"  Visual frame: {frame.shape}")

    result = system.process_user_interaction(user_id, text_input, frame)

    if result.get("success"):
        fused = result.get("fused_context", {})
        print("\nFusion results:")
        print(f"  Overall emotion: {fused.get('overall_emotional_state', 'unknown')}")
        print(f"  Engagement level: {fused.get('engagement_level', 0):.2f}")
        print(f"  Confidence: {fused.get('confidence_score', 0):.2f}")
        print(f"  User present: {fused.get('user_present', False)}")
        print(f"  Gaze engaged: {fused.get('gaze_engaged', False)}")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")


def demo_policy_system(system: GodTierIntegratedSystem):
    """Demonstrate adaptive policy system"""
    print("\n" + "=" * 80)
    print("ADAPTIVE POLICY SYSTEM DEMONSTRATION")
    print("=" * 80)

    if not system.policy_manager:
        print("Policy system not available")
        return

    user_id = "demo_user"
    session_id = (
        system.context_engine.start_session(user_id)
        if system.context_engine
        else "test_session"
    )

    # Get adaptive policies
    print(f"\nGetting adaptive policies for {user_id}...")
    policies = system.policy_manager.get_adaptive_policy(user_id, session_id)

    print("\nCurrent policy configuration:")
    for policy_name, value in policies.items():
        print(f"  {policy_name}: {value:.2f}")

    # Simulate feedback
    from app.core.conversation_context_engine import AdaptivePolicy

    print("\nSimulating user feedback (increase empathy)...")
    system.policy_manager.update_policy_from_feedback(
        user_id, AdaptivePolicy.EMPATHY_LEVEL, "increase"
    )

    # Get updated policies
    updated_policies = system.policy_manager.get_adaptive_policy(user_id, session_id)
    print(f"\nUpdated empathy level: {updated_policies.get('empathy_level', 0):.2f}")


def main():
    """Main demo function"""
    print("\n" + "=" * 80)
    print("GOD TIER PROJECT-AI SYSTEM DEMONSTRATION")
    print("=" * 80)
    print("\nThis demo showcases all integrated components:")
    print("  1. Voice Model System")
    print("  2. Visual Cue Recognition")
    print("  3. Conversation Context Engine")
    print("  4. Multi-Modal Fusion")
    print("  5. Adaptive Policy Manager")

    # Load configuration
    print("\n" + "-" * 80)
    print("Loading configuration...")
    config = load_god_tier_config()
    print(f"Configuration loaded: {config.system_name} v{config.version}")
    print(f"Deployment mode: {config.deployment_mode}")

    # Initialize system
    print("\n" + "-" * 80)
    print("Initializing God Tier system...")
    success = initialize_god_tier_system()

    if not success:
        print("ERROR: System initialization failed")
        return

    print("System initialized successfully!")

    # Get system instance
    system = get_god_tier_system()

    # Show system status
    status = system.get_status()
    print("\nSystem Status:")
    print(f"  Initialized: {status.initialized}")
    print(f"  Voice System: {status.voice_system_active}")
    print(f"  Visual System: {status.visual_system_active}")
    print(f"  Conversation System: {status.conversation_system_active}")
    print(f"  Fusion System: {status.fusion_system_active}")

    # Run demonstrations
    try:
        demo_voice_system(system)
        time.sleep(1)

        demo_visual_system(system)
        time.sleep(1)

        demo_conversation_system(system)
        time.sleep(1)

        demo_fusion_system(system)
        time.sleep(1)

        demo_policy_system(system)

    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)

    # Shutdown
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nShutting down system...")
    system.shutdown()
    print("System shutdown complete")

    # Final status
    final_status = system.get_status()
    print("\nFinal Statistics:")
    print(f"  Uptime: {final_status.uptime_seconds:.2f} seconds")
    print(f"  Total interactions: {final_status.total_interactions}")


if __name__ == "__main__":
    main()
