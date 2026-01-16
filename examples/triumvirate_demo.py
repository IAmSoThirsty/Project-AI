"""
Triumvirate Cognition System - Quick Demo

This script demonstrates the basic usage of the Triumvirate system
for production-ready AI orchestration.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def demo_basic_processing():
    """Demonstrate basic Triumvirate processing."""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Processing")
    print("=" * 60)

    from src.cognition.triumvirate import Triumvirate

    # Initialize Triumvirate
    triumvirate = Triumvirate()

    # Process some inputs
    inputs = [
        "What is artificial intelligence?",
        "Explain machine learning",
        {"query": "Deep learning", "type": "definition"},
    ]

    for inp in inputs:
        print(f"\n📥 Input: {inp}")
        result = triumvirate.process(inp)

        print(f"✅ Success: {result['success']}")
        print(f"🔗 Correlation ID: {result['correlation_id']}")
        print(f"⏱️  Duration: {result['duration_ms']:.2f}ms")

        if result["success"]:
            print(f"📤 Output: {result['output']}")


def demo_contradiction_detection():
    """Demonstrate contradiction detection in reasoning."""
    print("\n" + "=" * 60)
    print("DEMO 2: Contradiction Detection")
    print("=" * 60)

    from src.cognition.galahad.engine import GalahadEngine

    engine = GalahadEngine()

    # Test with contradictory statements
    contradictory_inputs = [
        "The system is safe and secure",
        "The system has critical vulnerabilities",
    ]

    print(f"\n📥 Inputs: {contradictory_inputs}")
    result = engine.reason(contradictory_inputs)

    print(f"✅ Success: {result['success']}")
    print(f"🔍 Contradictions Found: {len(result['contradictions'])}")
    print(f"💭 Explanation: {result['explanation']}")

    if result["contradictions"]:
        for contradiction in result["contradictions"]:
            print(f"   ⚠️  {contradiction['description']}")


def demo_semantic_memory():
    """Demonstrate semantic memory with vector search."""
    print("\n" + "=" * 60)
    print("DEMO 3: Semantic Memory Search")
    print("=" * 60)

    import tempfile

    from src.cognition.adapters.memory_adapter import MemoryAdapter

    # Use temporary directory for demo
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = MemoryAdapter(data_dir=tmpdir)

        # Add some memories
        memories = [
            "Python is a high-level programming language",
            "Machine learning is a subset of artificial intelligence",
            "Neural networks are inspired by biological neurons",
            "Docker is a containerization platform",
            "Kubernetes orchestrates container deployments",
        ]

        print("\n📝 Adding memories...")
        for mem in memories:
            mem_id = memory.add_memory(mem)
            print(f"   ✓ Added: {mem[:50]}... (ID: {mem_id})")

        # Search
        query = "programming languages"
        print(f"\n🔍 Searching for: '{query}'")

        results = memory.search(query, top_k=3)

        print(f"\n📊 Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(
                f"   {i}. [{result['similarity']:.3f}] {result['content']}"
            )


def demo_policy_enforcement():
    """Demonstrate policy enforcement."""
    print("\n" + "=" * 60)
    print("DEMO 4: Policy Enforcement")
    print("=" * 60)

    from src.cognition.cerberus.engine import CerberusConfig, CerberusEngine

    # Production mode (allow-all)
    print("\n🔓 Production Mode (Allow-All):")
    prod_engine = CerberusEngine(CerberusConfig(mode="production"))

    result = prod_engine.enforce_output("Any content here")
    print(f"   ✓ Allowed: {result['allowed']}")
    print(f"   💡 Reason: {result['reason']}")

    # Strict mode
    print("\n🔒 Strict Mode:")
    strict_engine = CerberusEngine(CerberusConfig(mode="strict"))

    # Test with long content
    long_content = "x" * 15000
    result = strict_engine.enforce_output(long_content)

    print(f"   Modified: {result.get('modified', False)}")
    if result.get("modified"):
        original_len = len(long_content)
        modified_len = len(str(result["output"]))
        print(f"   📏 Length: {original_len} → {modified_len} characters")


def demo_gpu_cpu_fallback():
    """Demonstrate GPU/CPU fallback."""
    print("\n" + "=" * 60)
    print("DEMO 5: GPU/CPU Fallback")
    print("=" * 60)

    from src.cognition.codex.engine import CodexConfig, CodexEngine

    # Try GPU first
    config = CodexConfig(
        enable_gpu=True, fallback_to_cpu=True, enable_full_engine=False
    )

    engine = CodexEngine(config)
    status = engine.get_status()

    print(f"🖥️  Device: {status['device']}")
    print(f"🔌 GPU Enabled: {config.enable_gpu}")
    print(f"🔄 CPU Fallback: {config.fallback_to_cpu}")
    print(f"⚡ Full Engine: {status['full_engine']}")

    # Process something
    result = engine.process("test input")
    print(f"✅ Processing: {result['success']}")


def demo_telemetry():
    """Demonstrate telemetry collection."""
    print("\n" + "=" * 60)
    print("DEMO 6: Telemetry Events")
    print("=" * 60)

    from src.cognition.triumvirate import Triumvirate, TriumvirateConfig

    config = TriumvirateConfig(enable_telemetry=True)
    triumvirate = Triumvirate(config)

    # Process something to generate events
    triumvirate.process("Demo input for telemetry")

    # Get telemetry
    events = triumvirate.get_telemetry(limit=10)

    print(f"\n📊 Captured {len(events)} telemetry events:")
    for event in events:
        print(f"   [{event['timestamp']}] {event['event_type']}")


def main():
    """Run all demos."""
    print("\n" + "🚀" * 30)
    print("Triumvirate Cognition System - Demo Suite")
    print("🚀" * 30)

    try:
        demo_basic_processing()
        demo_contradiction_detection()
        demo_semantic_memory()
        demo_policy_enforcement()
        demo_gpu_cpu_fallback()
        demo_telemetry()

        print("\n" + "=" * 60)
        print("✅ All demos completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
