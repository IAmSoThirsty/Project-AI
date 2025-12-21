"""
Integration example: RAG + Optical Flow + Local FBO

This example demonstrates how to use all three new systems together
for a complete offline-first AI assistant experience.
"""

from app.core.local_fbo import LocalFBOSystem
from app.core.optical_flow import OpticalFlowDetector
from app.core.rag_system import RAGSystem


def setup_offline_ai_assistant():
    """
    Set up a complete offline-first AI assistant with RAG and optical flow.
    """
    print("🚀 Setting up Offline-First AI Assistant...\n")

    # 1. Initialize Local FBO System (main orchestrator)
    print("1️⃣ Initializing Local FBO System...")
    fbo = LocalFBOSystem(
        data_dir="data/local_fbo", enable_rag=True, enable_reflection=True
    )
    print("✅ FBO System ready\n")

    # 2. Initialize RAG for knowledge management
    print("2️⃣ Setting up RAG Knowledge Base...")
    rag = RAGSystem(data_dir="data/rag_index")

    # Ingest sample knowledge
    sample_knowledge = """
    Project-AI is an offline-first AI assistant designed for mobile and desktop.
    It uses RAG (Retrieval-Augmented Generation) for intelligent information retrieval.
    The system includes optical flow detection for video analysis.
    All data is stored locally for privacy and offline operation.
    """
    rag.ingest_text(
        sample_knowledge,
        source="system_documentation",
        metadata={"category": "core_features"},
    )
    print(f"✅ Ingested knowledge: {rag.get_statistics()['total_chunks']} chunks\n")

    # 3. Initialize Optical Flow Detector
    print("3️⃣ Setting up Optical Flow Detector...")
    flow_detector = OpticalFlowDetector(data_dir="data/optical_flow")
    print("✅ Optical Flow ready\n")

    # 4. Add offline knowledge to FBO
    print("4️⃣ Populating offline knowledge base...")
    fbo.add_offline_knowledge(
        "rag_system", "RAG provides intelligent document retrieval", "systems"
    )
    fbo.add_offline_knowledge(
        "optical_flow",
        "Detects motion epicenters in video streams",
        "systems",
    )
    fbo.add_offline_knowledge(
        "offline_mode", "Full functionality without internet", "features"
    )
    print("✅ Offline knowledge populated\n")

    # 5. Check system status
    print("5️⃣ System Status:")
    context = fbo.get_context()
    print(f"   • Online: {context.is_online}")
    print(f"   • Knowledge Entries: {context.local_knowledge_size}")
    print(f"   • Reflections: {context.reflection_count}")
    print(f"   • Cached Responses: {context.cached_responses}")
    print()

    return fbo, rag, flow_detector


def demonstrate_offline_query(fbo, rag):
    """Demonstrate offline query with RAG integration."""
    print("📝 Demonstrating Offline Query...\n")

    # Query using FBO (which can use RAG internally)
    query = "What is Project-AI?"
    print(f"Query: {query}")

    result = fbo.query_offline(query, use_rag=True)
    print(f"Answer: {result['answer'][:200]}...")
    print(f"Source: {result['source']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"From Cache: {result['from_cache']}\n")

    # Add reflection about the query
    fbo.add_reflection(
        f"User asked about: {query}",
        category="user_interest",
        tags=["query", "documentation"],
    )


def demonstrate_reflection_system(fbo):
    """Demonstrate the reflection and pattern analysis system."""
    print("🧠 Demonstrating AI Reflection System...\n")

    # Add various reflections
    reflections_data = [
        ("User prefers offline mode", "preference", ["offline", "privacy"]),
        ("Interest in video analysis", "interest", ["optical_flow", "video"]),
        ("Asked about RAG multiple times", "pattern", ["rag", "learning"]),
        ("Prefers Python examples", "preference", ["python", "code"]),
        ("Active during evening hours", "observation", ["usage", "time"]),
    ]

    for content, category, tags in reflections_data:
        fbo.add_reflection(
            content, category=category, confidence=0.8, tags=tags
        )

    print(f"✅ Added {len(reflections_data)} reflections\n")

    # Analyze patterns
    print("🔍 Pattern Analysis:")
    patterns = fbo.reflect_on_patterns()
    for i, pattern in enumerate(patterns, 1):
        print(f"   {i}. {pattern}")
    print()

    # Search reflections
    print("🔎 Searching reflections for 'offline':")
    results = fbo.search_reflections(query="offline", limit=3)
    for r in results:
        print(f"   • [{r.category}] {r.content}")
    print()


def demonstrate_optical_flow_integration(flow_detector):
    """Demonstrate optical flow analysis (if video available)."""
    print("🎥 Optical Flow Detector Available\n")

    # Show capabilities
    stats = flow_detector.get_statistics()
    print(f"   • Algorithm: {stats['algorithm']}")
    print(f"   • Sensitivity: {stats['sensitivity']}")
    print(f"   • Data Directory: {stats['data_directory']}")
    print(
        f"   • Previous Analyses: {stats['total_analyses']}"
    )
    print()

    print("   Note: To analyze a video, use:")
    print("   ```python")
    print("   result = flow_detector.analyze_video('path/to/video.mp4')")
    print("   flow_detector.visualize_flow('video.mp4', 'output.mp4')")
    print("   ```")
    print()


def demonstrate_offline_preparation(fbo):
    """Demonstrate preparing the system for offline use."""
    print("💾 Preparing System for Offline Operation...\n")

    # Prepare for offline
    fbo.prepare_for_offline()

    # Get final statistics
    stats = fbo.get_statistics()
    print("📊 Final System Statistics:")
    print(f"   • Local Knowledge: {stats['local_knowledge_entries']} categories")
    print(f"   • Reflections: {stats['reflections']}")
    print(f"   • Cached Responses: {stats['cached_responses']}")
    print(f"   • RAG Enabled: {stats['rag_enabled']}")

    if stats["rag_enabled"]:
        rag_stats = stats["rag_statistics"]
        print(f"   • RAG Chunks: {rag_stats['total_chunks']}")
        print(f"   • RAG Sources: {rag_stats['unique_sources']}")

    print("\n✅ System ready for offline operation!")


def main():
    """Run the complete integration example."""
    print("=" * 60)
    print("Project-AI: Offline-First Integration Example")
    print("RAG + Optical Flow + Local FBO")
    print("=" * 60)
    print()

    # Setup
    fbo, rag, flow_detector = setup_offline_ai_assistant()

    # Demonstrate features
    demonstrate_offline_query(fbo, rag)
    demonstrate_reflection_system(fbo)
    demonstrate_optical_flow_integration(flow_detector)
    demonstrate_offline_preparation(fbo)

    print()
    print("=" * 60)
    print("🎉 Integration Example Complete!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Add your own knowledge: rag.ingest_directory('your_docs/')")
    print("2. Query offline: fbo.query_offline('your question')")
    print("3. Analyze videos: flow_detector.analyze_video('your_video.mp4')")
    print("4. Review patterns: fbo.reflect_on_patterns()")


if __name__ == "__main__":
    main()
