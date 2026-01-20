"""
DeepSeek V3.2 Integration Demo for Project-AI.

This example demonstrates how to integrate and use the DeepSeek V3.2
Mixture-of-Experts language model within Project-AI.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.core.deepseek_v32_inference import DeepSeekV32


def demo_completion():
    """Demonstrate text completion with DeepSeek V3.2."""
    print("\n" + "=" * 60)
    print("DeepSeek V3.2 Completion Demo")
    print("=" * 60)

    # Initialize model (automatically detects GPU/CPU)
    print("\n🚀 Initializing DeepSeek V3.2...")
    deepseek = DeepSeekV32(
        max_length=256,
        temperature=0.7,
    )

    # Get model info
    info = deepseek.get_model_info()
    print(f"✓ Model: {info['model_name']}")
    print(f"✓ Device: {info['device']}")
    print(
        f"✓ Content Filter: {'Enabled' if info['content_filter_enabled'] else 'Disabled'}"
    )

    # Generate completion
    prompt = "Explain the concept of Mixture-of-Experts in neural networks"
    print(f"\n📝 Prompt: {prompt}")
    print("\n🤔 Generating...\n")

    result = deepseek.generate_completion(
        prompt=prompt,
        max_new_tokens=200,
        temperature=0.7,
    )

    if result["success"]:
        print("✅ Response:")
        print("-" * 60)
        print(result["text"])
        print("-" * 60)
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

    # Cleanup
    deepseek.unload_model()
    print("\n✓ Model unloaded\n")


def demo_chat():
    """Demonstrate chat functionality with DeepSeek V3.2."""
    print("\n" + "=" * 60)
    print("DeepSeek V3.2 Chat Demo")
    print("=" * 60)

    # Initialize model
    print("\n🚀 Initializing DeepSeek V3.2...")
    deepseek = DeepSeekV32(
        max_length=256,
        temperature=0.8,
    )

    # Build conversation
    messages = [
        {"role": "user", "content": "What is Project-AI?"},
    ]

    print("\n💬 Chat Conversation:")
    print("-" * 60)

    for msg in messages:
        print(f"{msg['role'].capitalize()}: {msg['content']}")

    print("\n🤔 Generating response...\n")

    # Generate chat response
    result = deepseek.generate_chat(
        messages=messages,
        max_new_tokens=150,
        temperature=0.8,
    )

    if result["success"]:
        print("✅ Assistant Response:")
        print("-" * 60)
        print(result["text"])
        print("-" * 60)
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

    # Cleanup
    deepseek.unload_model()
    print("\n✓ Model unloaded\n")


def demo_content_filter():
    """Demonstrate content filtering."""
    print("\n" + "=" * 60)
    print("DeepSeek V3.2 Content Filter Demo")
    print("=" * 60)

    deepseek = DeepSeekV32()

    test_prompts = [
        ("Safe prompt: Explain quantum computing", True),
        ("Unsafe prompt: Generate illegal content", False),
        ("Safe prompt: Write a poem about nature", True),
    ]

    print("\n🛡️ Testing Content Filter:")
    print("-" * 60)

    for prompt, _should_pass in test_prompts:
        is_safe, reason = deepseek.check_content_filter(prompt)
        status = "✅ PASSED" if is_safe else "❌ BLOCKED"
        print(f"\n{status}: {prompt}")
        print(f"Reason: {reason}")

    print("\n" + "-" * 60)


def demo_parameter_tuning():
    """Demonstrate parameter tuning."""
    print("\n" + "=" * 60)
    print("DeepSeek V3.2 Parameter Tuning Demo")
    print("=" * 60)

    deepseek = DeepSeekV32()

    print("\n⚙️ Initial Parameters:")
    info = deepseek.get_model_info()
    print(f"  Temperature: {info['temperature']}")
    print(f"  Max Length: {info['max_length']}")
    print(f"  Top-p: {info['top_p']}")
    print(f"  Top-k: {info['top_k']}")

    # Update parameters
    deepseek.update_parameters(
        temperature=0.9,
        max_length=512,
        top_p=0.95,
        top_k=100,
    )

    print("\n⚙️ Updated Parameters:")
    info = deepseek.get_model_info()
    print(f"  Temperature: {info['temperature']}")
    print(f"  Max Length: {info['max_length']}")
    print(f"  Top-p: {info['top_p']}")
    print(f"  Top-k: {info['top_k']}")
    print()


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("🧠 DeepSeek V3.2 Integration Demo for Project-AI")
    print("=" * 60)

    print("\nThis demo showcases the DeepSeek V3.2 Mixture-of-Experts")
    print("language model integration in Project-AI.\n")

    print("NOTE: This demo requires the model to be downloaded.")
    print("The first run will download ~20-40GB of model weights.")
    print("Make sure you have sufficient disk space and bandwidth.\n")

    # Run demos (most don't actually load the model to save time)
    demo_content_filter()
    demo_parameter_tuning()

    # Uncomment to run actual model inference (requires model download)
    # demo_completion()
    # demo_chat()

    print("\n" + "=" * 60)
    print("✓ Demo completed!")
    print("=" * 60)
    print("\nTo run actual inference, uncomment the demo_completion()")
    print("and demo_chat() calls in the main() function.")
    print("\nFor command-line usage, run:")
    print("  python scripts/deepseek_v32_cli.py --help")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback

        traceback.print_exc()
