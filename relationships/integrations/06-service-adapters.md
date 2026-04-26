# Service Adapters Relationship Map

**Status**: 🟢 Production | **Type**: Internal Abstraction Layer  
**Priority**: P1 Critical | **Governance**: Interface-Driven

---


## Navigation

**Location**: `relationships\integrations\06-service-adapters.md`

**Parent**: [[relationships\integrations\README.md]]


## Overview

Service Adapters provide abstraction layers that decouple core systems from external dependencies. They enable:
- Easy swapping of implementations (mock vs. production)
- Testing without external services
- Unified interfaces across diverse backends
- Graceful degradation when services unavailable

---

## Adapter Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CONSUMER SYSTEMS                          │
│   (Intelligence Engine, Memory Engine, Image Gen, etc.)     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 SERVICE ADAPTER LAYER                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Model       │  │ Memory      │  │ Desktop     │        │
│  │ Adapter     │  │ Adapter     │  │ Adapter     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└───────┬───────────────────┬───────────────────┬─────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ External    │     │ External    │     │ External    │
│ AI Services │     │ Vector DB   │     │ UI Systems  │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## Core Adapters

### 1. Model Adapter (`src/cognition/adapters/model_adapter.py` [[src/cognition/adapters/model_adapter.py]])

**Purpose**: Abstract ML model backends (PyTorch, TensorFlow, HuggingFace, OpenAI)

**Interface**:
```python
class ModelAdapter(ABC):
    @abstractmethod
    def load_model(self, model_path: str, **kwargs) -> Any:
        """Load model from path or identifier."""
        pass
    
    @abstractmethod
    def predict(self, input_data: Any, **kwargs) -> Any:
        """Run inference on input data."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if model backend is available."""
        pass
```

**Implementations**:
- `OpenAIAdapter`: Wraps OpenAI API
- `HuggingFaceAdapter`: Wraps HF Inference API
- `LocalPyTorchAdapter`: Loads local PyTorch models
- `MockAdapter`: Returns pre-defined responses for testing

**Usage**:
```python
# Production: Use OpenAI
adapter = OpenAIAdapter(api_key=os.getenv("OPENAI_API_KEY"))
if adapter.is_available():
    response = adapter.predict("What is AI?")

# Testing: Use mock
adapter = MockAdapter(responses={"What is AI?": "AI is intelligence by machines"})
response = adapter.predict("What is AI?")
```

### 2. Memory Adapter (`src/cognition/adapters/memory_adapter.py` [[src/cognition/adapters/memory_adapter.py]])

**Purpose**: Abstract vector database backends (Chroma, FAISS, Pinecone)

**Interface**:
```python
class MemoryAdapter(ABC):
    @abstractmethod
    def store(self, key: str, value: Any, metadata: dict = None) -> bool:
        """Store data with optional metadata."""
        pass
    
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list:
        """Retrieve top-k similar items."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete item by key."""
        pass
```

**Implementations**:
- `ChromaAdapter`: Uses ChromaDB for vector storage
- `FAISSAdapter`: Uses Facebook FAISS for fast similarity search
- `InMemoryAdapter`: Simple dict-based storage (testing)

**Usage**:
```python
# Production: Use ChromaDB
adapter = ChromaAdapter(collection_name="memories")
adapter.store("memory_1", "Alice loves pizza", metadata={"user": "alice"})
results = adapter.retrieve("What does Alice like?", top_k=3)

# Testing: Use in-memory
adapter = InMemoryAdapter()
adapter.store("memory_1", "Test data")
```

### 3. Desktop Adapter (`src/app/interfaces/desktop/adapter.py` [[src/app/interfaces/desktop/adapter.py]])

**Purpose**: Abstract UI frameworks (PyQt6, Tkinter, web browser)

**Interface**:
```python
class DesktopAdapter(ABC):
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize UI framework."""
        pass
    
    @abstractmethod
    def create_window(self, title: str, width: int, height: int) -> Any:
        """Create main window."""
        pass
    
    @abstractmethod
    def show_message(self, message: str, level: str = "info") -> None:
        """Show message to user."""
        pass
```

**Implementations**:
- `PyQt6Adapter`: Production desktop UI
- `WebAdapter`: Browser-based UI (future)
- `MockAdapter`: Headless for testing

### 4. Kernel Adapters (`src/app/core/kernel_adapters.py` [[src/app/core/kernel_adapters.py]])

**Purpose**: Unify non-standard kernel interfaces for SuperKernel

**Interface**:
```python
class KernelInterface(ABC):
    @abstractmethod
    def process(self, input_data: Any, **kwargs) -> Any:
        """Process input and return output."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if kernel is available."""
        pass
```

**Implementations**:
- `ReflectionCycleAdapter`: Wraps `ReflectionCycle` (daily/weekly/triggered reflections)
- `BondingProtocolAdapter`: Wraps `BondingProtocol` (identity system)
- `GovernanceAdapter`: Wraps `Triumvirate` (ethics council)

**Usage**:
```python
# Unified interface for diverse kernels
reflection_kernel = ReflectionCycleAdapter(reflection_cycle)
result = reflection_kernel.process("daily", memory_engine=memory)

bonding_kernel = BondingProtocolAdapter(bonding_protocol)
result = bonding_kernel.process({"action": "check_phase"})
```

### 5. Cerberus Adapter (`src/app/plugins/cerberus_adapter.py` [[src/app/plugins/cerberus_adapter.py]])

**Purpose**: Expose Cerberus Guard Bot to main application

**Interface**:
```python
class CerberusAdapter:
    def initialize(self) -> bool:
        """Initialize Cerberus HubCoordinator."""
        pass
    
    def analyze(self, content: str) -> dict:
        """Analyze content for threats."""
        pass
    
    def is_enabled(self) -> bool:
        """Check if Cerberus is enabled."""
        pass
```

**Usage**:
```python
# Initialize Cerberus
adapter = CerberusAdapter(enabled=True)
if adapter.initialize():
    result = adapter.analyze("User input text")
    if result["threat_detected"]:
        logger.warning(f"Threat: {result['threat_type']}")
```

### 6. Codex Adapter (`src/app/plugins/codex_adapter.py` [[src/app/plugins/codex_adapter.py]])

**Purpose**: Adapt Codex code generation system to plugin interface

**Features**:
- Code generation
- Code analysis
- Syntax checking
- Language detection

---

## Integration Patterns

### Pattern 1: Dependency Injection

**Benefit**: Swap implementations at runtime

```python
class IntelligenceEngine:
    def __init__(self, model_adapter: ModelAdapter, memory_adapter: MemoryAdapter):
        """Inject adapters instead of hardcoding dependencies."""
        self.model = model_adapter
        self.memory = memory_adapter
    
    def answer_question(self, question: str):
        """Use adapters for external calls."""
        # Retrieve context from memory
        context = self.memory.retrieve(question, top_k=3)
        
        # Get answer from model
        prompt = f"Context: {context}\nQuestion: {question}"
        answer = self.model.predict(prompt)
        
        return answer

# Production
engine = IntelligenceEngine(
    model_adapter=OpenAIAdapter(),
    memory_adapter=ChromaAdapter()
)

# Testing
engine = IntelligenceEngine(
    model_adapter=MockAdapter({"test": "mock response"}),
    memory_adapter=InMemoryAdapter()
)
```

### Pattern 2: Graceful Degradation

**Benefit**: Continue operating when services unavailable

```python
def get_ai_response(prompt: str):
    """Try multiple adapters in priority order."""
    adapters = [
        OpenAIAdapter(),
        HuggingFaceAdapter(),
        LocalAdapter(),
        MockAdapter()  # Always works
    ]
    
    for adapter in adapters:
        if adapter.is_available():
            try:
                return adapter.predict(prompt)
            except Exception as e:
                logger.warning(f"{adapter.__class__.__name__} failed: {e}")
                continue
    
    return "All AI services unavailable"
```

### Pattern 3: Adapter Registry

**Benefit**: Discover adapters dynamically

```python
# Global registry
ADAPTER_REGISTRY = {
    "model": {
        "openai": OpenAIAdapter,
        "huggingface": HuggingFaceAdapter,
        "local": LocalPyTorchAdapter,
        "mock": MockAdapter
    },
    "memory": {
        "chroma": ChromaAdapter,
        "faiss": FAISSAdapter,
        "inmemory": InMemoryAdapter
    }
}

def get_adapter(adapter_type: str, impl_name: str, **kwargs):
    """Get adapter by type and implementation name."""
    if adapter_type not in ADAPTER_REGISTRY:
        raise ValueError(f"Unknown adapter type: {adapter_type}")
    
    if impl_name not in ADAPTER_REGISTRY[adapter_type]:
        raise ValueError(f"Unknown {adapter_type} adapter: {impl_name}")
    
    adapter_class = ADAPTER_REGISTRY[adapter_type][impl_name]
    return adapter_class(**kwargs)

# Usage
model = get_adapter("model", "openai", api_key=os.getenv("OPENAI_API_KEY"))
memory = get_adapter("memory", "chroma", collection_name="test")
```

---

## Configuration

### Environment Variables

```bash
# Model adapter selection
DEFAULT_MODEL_ADAPTER=openai  # or huggingface, local, mock
DEFAULT_MEMORY_ADAPTER=chroma  # or faiss, inmemory

# Cerberus adapter
ENABLE_CERBERUS=1  # 1=enabled, 0=disabled
```

---

## Testing

### Unit Tests

```python
# tests/test_adapters.py
def test_model_adapter_interface():
    """Test that all model adapters implement interface."""
    adapters = [OpenAIAdapter(), HuggingFaceAdapter(), MockAdapter()]
    
    for adapter in adapters:
        # Check interface methods exist
        assert hasattr(adapter, "load_model")
        assert hasattr(adapter, "predict")
        assert hasattr(adapter, "is_available")
        
        # Check is_available works
        is_available = adapter.is_available()
        assert isinstance(is_available, bool)

def test_mock_adapter():
    """Test mock adapter for testing."""
    adapter = MockAdapter(responses={"hello": "world"})
    
    assert adapter.is_available() is True
    assert adapter.predict("hello") == "world"
    assert adapter.predict("unknown") is None
```

### Integration Tests

```python
def test_intelligence_engine_with_adapters():
    """Test intelligence engine with different adapters."""
    # Test with mock adapters
    engine = IntelligenceEngine(
        model_adapter=MockAdapter({"test": "response"}),
        memory_adapter=InMemoryAdapter()
    )
    
    answer = engine.answer_question("test")
    assert answer == "response"
    
    # Test with real adapters (if available)
    if os.getenv("OPENAI_API_KEY"):
        engine = IntelligenceEngine(
            model_adapter=OpenAIAdapter(),
            memory_adapter=ChromaAdapter()
        )
        answer = engine.answer_question("What is AI?")
        assert len(answer) > 0
```

---

## Performance

### Overhead Comparison

| Adapter | Overhead | Benefit |
|---------|----------|---------|
| Model Adapter | <1ms | Unified interface, swappable backends |
| Memory Adapter | <5ms | Vector DB abstraction |
| Kernel Adapter | <0.1ms | SuperKernel integration |
| Desktop Adapter | <10ms (startup) | UI framework swapping |

**Conclusion**: Adapter overhead is negligible compared to benefits.

---

## Best Practices

### 1. Keep Adapters Thin

**❌ Bad**: Business logic in adapter
```python
class ModelAdapter:
    def predict(self, prompt):
        # BAD: Adapter contains business logic
        if len(prompt) > 1000:
            prompt = prompt[:1000]
        if "unsafe" in prompt:
            return "I cannot answer that"
        return self._call_api(prompt)
```

**✅ Good**: Adapter only translates interfaces
```python
class ModelAdapter:
    def predict(self, prompt):
        # GOOD: Adapter just calls external service
        return self._call_api(prompt)

# Business logic in consumer
class IntelligenceEngine:
    def answer_question(self, question):
        # Business logic here
        if len(question) > 1000:
            question = question[:1000]
        if not self._is_safe(question):
            return "I cannot answer that"
        
        # Adapter just translates call
        return self.model_adapter.predict(question)
```

### 2. Document Interface Contracts

Every adapter interface should specify:
- Input/output types
- Error conditions
- Thread safety
- Resource management

### 3. Test Adapters Independently

Each adapter should have:
- Unit tests for interface compliance
- Integration tests with real backend (optional, gated by env var)
- Mock adapter for consumer testing

---

## Future Enhancements

### Phase 1: Auto-Discovery ⏳ PLANNED
- Scan `adapters/` directory for adapter classes
- Auto-register in `ADAPTER_REGISTRY`
- Plugin system for third-party adapters

### Phase 2: Performance Monitoring 🔮 FUTURE
- Track adapter latency, error rates
- Auto-switch to faster adapter if available
- Dashboard showing adapter health

---

## Related Systems

- **[01-openai-integration.md](01-openai-integration.md)**: Model adapter wraps OpenAI
- **[03-huggingface-integration.md](03-huggingface-integration.md)**: Model adapter wraps HF
- **[04-database-connectors.md](04-database-connectors.md)**: Memory adapter uses DBs

---

**Last Updated**: 2025-01-26  
**Maintained By**: AGENT-060  
**Review Cycle**: Quarterly


---

## See Also

### Related Source Documentation

- **08 Location Services**: [[source-docs\integrations\08-location-services.md]]
- **Documentation Index**: [[source-docs\integrations\README.md]]
