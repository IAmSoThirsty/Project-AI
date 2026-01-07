# Offline-First Architecture - Project-AI

## Overview

Project-AI now features a comprehensive **Local Fallback Offline (FBO)** system that enables full AI assistant functionality without internet connectivity. This is particularly valuable for mobile and desktop users who need reliable access to their AI assistant regardless of network availability.

## Three Integrated Systems

### 1. RAG System (`src/app/core/rag_system.py`)

**Purpose**: Retrieval-Augmented Generation for intelligent information retrieval

**Key Features**:
- Local text ingestion from multiple sources (.txt, .md files)
- Smart chunking with configurable overlap (default: 500 chars, 50 char overlap)
- Vector embeddings using sentence-transformers (all-MiniLM-L6-v2)
- Cosine similarity-based retrieval
- JSON-based persistence for offline operation
- OpenAI integration for augmented generation (when online)

**Usage**:
```python
from app.core.rag_system import RAGSystem

# Initialize
rag = RAGSystem(data_dir="data/rag_index")

# Ingest knowledge
rag.ingest_directory("knowledge_base/")
rag.ingest_text("Important info", source="manual_entry")

# Query
results = rag.retrieve("What is Python?", top_k=3)
context = rag.build_context("What is Python?")

# With LLM (when online)
response = rag.query_with_llm("Explain Python")
```

### 2. Optical Flow Detector (`src/app/core/optical_flow.py`)

**Purpose**: Motion epicenter detection in video streams for pattern analysis

**Key Features**:
- Farneback and Lucas-Kanade optical flow algorithms
- Epicenter detection (convergent, divergent, vortex)
- Video and image sequence analysis
- Motion magnitude tracking
- Flow visualization with epicenter marking
- JSON-based result persistence

**Usage**:
```python
from app.core.optical_flow import OpticalFlowDetector

# Initialize
detector = OpticalFlowDetector(
    algorithm="farneback",
    sensitivity=0.5
)

# Analyze video
result = detector.analyze_video("video.mp4")
print(f"Detected {len(result.epicenters)} epicenters")

# Visualize
detector.visualize_flow("video.mp4", "output.mp4", show_epicenters=True)
```

### 3. Local FBO System (`src/app/core/local_fbo.py`)

**Purpose**: Offline-first operation with local knowledge and reflection

**Key Features**:
- Offline knowledge base with categorization
- AI reflection system for self-learning
- Smart response caching
- Pattern recognition in interactions
- RAG integration for offline queries
- Automatic online/offline detection
- Sync capabilities when connectivity restored

**Usage**:
```python
from app.core.local_fbo import LocalFBOSystem

# Initialize
fbo = LocalFBOSystem(
    data_dir="data/local_fbo",
    enable_rag=True,
    enable_reflection=True
)

# Add offline knowledge
fbo.add_offline_knowledge("python", "A programming language", "tech")

# Query offline
result = fbo.query_offline("What is Python?")
print(result["answer"])

# Add reflection
fbo.add_reflection(
    "User prefers Python over Java",
    category="preference",
    tags=["python", "programming"]
)

# Analyze patterns
patterns = fbo.reflect_on_patterns()

# Prepare for offline operation
fbo.prepare_for_offline()

# Sync when online
fbo.sync_when_online()
```

## Offline-First Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interaction                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Connectivity Check      │
        │  (Local FBO System)      │
        └────────┬────────┬────────┘
                 │        │
         Online  │        │  Offline
                 │        │
        ┌────────▼──┐  ┌──▼─────────────┐
        │  OpenAI   │  │  Local RAG     │
        │  API      │  │  + Cache       │
        │  (when    │  │  + Knowledge   │
        │  avail.)  │  │                │
        └────────┬──┘  └──┬─────────────┘
                 │        │
                 │        │
        ┌────────▼────────▼─────────────┐
        │  Response Generation           │
        │  + Reflection Logging          │
        │  + Pattern Analysis            │
        └────────────────┬───────────────┘
                         │
                         ▼
                ┌────────────────┐
                │  User Response │
                └────────────────┘
```

## Data Persistence

All three systems use JSON-based persistence for offline reliability:

### RAG System Storage
```
data/rag_index/
├── index.json           # Chunks + embeddings + metadata
└── [auto-generated]
```

### Optical Flow Storage
```
data/optical_flow/
├── analysis_video1.json
├── analysis_video2.json
└── [per-video results]
```

### Local FBO Storage
```
data/local_fbo/
├── offline_knowledge.json  # Categorized knowledge base
├── reflections.json        # AI self-reflections
├── response_cache.json     # Cached query responses
├── last_sync.json          # Sync timestamp
└── rag_index/              # Embedded RAG system
    └── index.json
```

## Mobile Optimization

The offline-first architecture is specifically designed for mobile use:

1. **Low Storage**: Efficient JSON-based storage (~MB not GB)
2. **Fast Queries**: In-memory caching with disk fallback
3. **Battery Friendly**: No constant API calls when offline
4. **Smart Sync**: Background sync when WiFi available
5. **Progressive Loading**: Load knowledge incrementally

## Integration with Existing Systems

### AI Persona Integration
```python
# The Local FBO system can work with AI Persona
from app.core.ai_systems import AIPersona
from app.core.local_fbo import LocalFBOSystem

persona = AIPersona()
fbo = LocalFBOSystem()

# Persona can use FBO for offline queries
response = fbo.query_offline(user_message)

# FBO can store persona reflections
fbo.add_reflection(
    persona.generate_thought(),
    category="persona_reflection"
)
```

### Memory Expansion Integration
```python
# FBO complements the memory system
from app.core.ai_systems import MemoryExpansionSystem
from app.core.local_fbo import LocalFBOSystem

memory = MemoryExpansionSystem()
fbo = LocalFBOSystem()

# Add memory to offline knowledge
for topic, data in memory.knowledge_base.items():
    fbo.add_offline_knowledge(topic, data, category="memory")

# Use RAG to enhance memory retrieval
memory_context = fbo.rag_system.build_context(query)
```

## Testing

Comprehensive test suites ensure reliability:

- `tests/test_rag_system.py`: 25+ tests for RAG functionality
- `tests/test_optical_flow.py`: 30+ tests for motion detection
- `tests/test_local_fbo.py`: 35+ tests for offline operation

Run tests:
```bash
pytest tests/test_rag_system.py -v
pytest tests/test_optical_flow.py -v
pytest tests/test_local_fbo.py -v
```

## Dependencies

New dependencies added to `requirements.txt`:
- `sentence-transformers==3.3.1`: For RAG embeddings
- `opencv-python==4.10.0.84`: For optical flow analysis

## Example: Complete Offline Workflow

```python
from app.core.local_fbo import LocalFBOSystem

# Initialize system
fbo = LocalFBOSystem(enable_rag=True, enable_reflection=True)

# Phase 1: Populate while online
fbo.add_offline_knowledge("Python", "Programming language", "tech")
fbo.add_offline_knowledge("AI", "Artificial Intelligence", "tech")
fbo.ingest_for_offline(
    "Python is widely used in AI development...",
    source="ai_article"
)

# Phase 2: Prepare for offline
fbo.prepare_for_offline()
print("System ready for offline operation")

# Phase 3: Use offline
context = fbo.get_context()
if not context.is_online:
    # Works completely offline
    result = fbo.query_offline("Tell me about Python and AI")
    print(result["answer"])
    
    # AI self-reflection
    fbo.add_reflection(
        "User interested in Python for AI",
        category="preference",
        tags=["python", "ai"]
    )

# Phase 4: Analyze patterns (offline)
patterns = fbo.reflect_on_patterns()
for pattern in patterns:
    print(f"Pattern: {pattern}")

# Phase 5: Sync when back online
if fbo.check_connectivity():
    sync_result = fbo.sync_when_online()
    print(f"Synced {sync_result['synced_items']} items")
```

## Future Enhancements

1. **Mobile App**: Native mobile UI for iOS/Android
2. **P2P Sync**: Device-to-device sync without internet
3. **Compression**: Further reduce storage footprint
4. **Incremental Embeddings**: Generate embeddings on-device
5. **Voice Offline**: Local speech recognition
6. **Multi-language**: Offline translation capabilities

## Architecture Benefits

✅ **Reliability**: Works anywhere, anytime
✅ **Privacy**: Data stays local by default
✅ **Speed**: No API latency when offline
✅ **Cost**: Reduced API costs
✅ **Resilience**: Graceful degradation
✅ **Mobile-First**: Optimized for mobile use cases

## Conclusion

The offline-first architecture transforms Project-AI into a truly mobile-ready AI assistant that provides consistent, intelligent responses regardless of connectivity. The integration of RAG, optical flow detection, and the Local FBO system creates a robust foundation for both online and offline operation.
