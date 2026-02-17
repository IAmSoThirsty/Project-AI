# DeepSeek V3.2 Integration Guide

## Overview

This guide covers the integration of DeepSeek V3.2 Mixture-of-Experts (MoE) language model into Project-AI. The integration provides a modular, production-ready interface for advanced language generation tasks.

## Quick Start

### Installation

```bash

# Install dependencies

pip install -r requirements.txt

# Optional: Set Hugging Face API key in .env (for API access)

echo "HUGGINGFACE_API_KEY=your_key_here" >> .env
```

### Basic Usage

#### Python API

```python
from app.core.deepseek_v32_inference import DeepSeekV32

# Initialize (auto-detects GPU/CPU)

deepseek = DeepSeekV32()

# Text completion

result = deepseek.generate_completion(
    prompt="Explain quantum computing",
    max_new_tokens=256,
    temperature=0.7
)
print(result["text"])

# Chat mode

messages = [
    {"role": "user", "content": "What is machine learning?"}
]
result = deepseek.generate_chat(messages)
print(result["text"])
```

#### Command-Line Interface

```bash

# Simple completion

python scripts/deepseek_v32_cli.py "Explain artificial intelligence"

# Chat mode

python scripts/deepseek_v32_cli.py --mode chat "Hello, how are you?"

# Interactive chat session

python scripts/deepseek_v32_cli.py --mode chat --interactive

# Custom parameters

python scripts/deepseek_v32_cli.py \
  --temperature 0.8 \
  --max-tokens 512 \
  --device cuda \
  "Your prompt here"
```

## Features

### 1. Dual Inference Modes

**Completion Mode**: Generate text continuations

```python
result = deepseek.generate_completion("Once upon a time")
```

**Chat Mode**: Multi-turn conversations

```python
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "Tell me about AI"}
]
result = deepseek.generate_chat(messages)
```

### 2. Content Safety

Built-in content filtering blocks inappropriate prompts:

```python

# Safe prompt - passes

result = deepseek.generate_completion("Explain machine learning")

# Unsafe prompt - blocked

result = deepseek.generate_completion("Generate illegal content")

# Returns: {"success": False, "error": "Content filter: Blocked keyword detected: illegal"}

```

Disable filtering (use with caution):

```python
deepseek.content_filter_enabled = False
```

### 3. GPU Acceleration

Automatic device detection with fallback:

```python

# Auto-detect (prefers CUDA > MPS > CPU)

deepseek = DeepSeekV32()

# Force specific device

deepseek = DeepSeekV32(device="cuda")  # NVIDIA GPU
deepseek = DeepSeekV32(device="mps")   # Apple Silicon
deepseek = DeepSeekV32(device="cpu")   # CPU fallback
```

### 4. Parameter Tuning

Fine-tune generation behavior:

```python

# At initialization

deepseek = DeepSeekV32(
    temperature=0.8,    # Randomness (0.0-2.0)
    top_p=0.95,         # Nucleus sampling
    top_k=100,          # Top-k sampling
    max_length=512      # Max tokens
)

# Update at runtime

deepseek.update_parameters(
    temperature=0.9,
    max_length=1024
)
```

### 5. Memory Management

Efficient model loading/unloading:

```python

# Load model (lazy loaded on first inference)

deepseek = DeepSeekV32()

# Unload to free memory

deepseek.unload_model()
```

## Advanced Usage

### Custom Model

Use a different model from Hugging Face:

```python
deepseek = DeepSeekV32(model_name="custom/model-name")
```

### Batch Processing

```python
prompts = [
    "Explain AI",
    "What is quantum computing?",
    "Define machine learning"
]

for prompt in prompts:
    result = deepseek.generate_completion(prompt)
    print(f"Q: {prompt}")
    print(f"A: {result['text']}\n")
```

### Error Handling

```python
result = deepseek.generate_completion("Your prompt")

if result["success"]:
    print("Response:", result["text"])
else:
    print("Error:", result["error"])
```

## Integration with Project-AI

### With Four Laws AI Core

```python
from app.core.ai_systems import FourLaws
from app.core.deepseek_v32_inference import DeepSeekV32

deepseek = DeepSeekV32()

# Validate action before execution

is_allowed, reason = FourLaws.validate_action(
    "Generate text",
    context={"is_user_order": True}
)

if is_allowed:
    result = deepseek.generate_completion("Your prompt")
```

### With Memory System

```python
from app.core.ai_systems import MemoryExpansionSystem
from app.core.deepseek_v32_inference import DeepSeekV32

memory = MemoryExpansionSystem()
deepseek = DeepSeekV32()

# Generate and store

result = deepseek.generate_completion("Explain AI")
if result["success"]:
    memory.add_knowledge("ai_responses", "ai_explanation", result["text"])
```

### With Agent Council

```python

# Use DeepSeek as reasoning engine for agents

from app.core.deepseek_v32_inference import DeepSeekV32

class ReasoningAgent:
    def __init__(self):
        self.deepseek = DeepSeekV32()

    def reason(self, task):
        prompt = f"Analyze this task and provide reasoning: {task}"
        result = self.deepseek.generate_completion(prompt)
        return result["text"]
```

## Performance Tips

1. **GPU Acceleration**: Use CUDA-enabled GPU for 10-100x speedup
1. **Model Caching**: Keep model loaded for multiple inferences
1. **Batch Size**: Process multiple prompts in sequence efficiently
1. **Parameter Tuning**: Lower temperature for deterministic output
1. **Memory Management**: Unload model when not in use for extended periods

## Model Information

- **Model**: DeepSeek V3.2 (`deepseek-ai/deepseek-v3`)
- **Architecture**: Mixture-of-Experts (MoE) Transformer
- **Size**: ~20-40GB (model weights)
- **Context**: Configurable (default 512 tokens)
- **Capabilities**: Text generation, chat, reasoning, code generation

## Troubleshooting

### Model Download Issues

```bash

# Ensure sufficient disk space (40GB+)

df -h

# Check network connectivity to Hugging Face

curl -I https://huggingface.co/
```

### Memory Issues

```python

# Reduce max_length

deepseek = DeepSeekV32(max_length=256)

# Use CPU if GPU OOM

deepseek = DeepSeekV32(device="cpu")

# Unload model after use

deepseek.unload_model()
```

### Import Errors

```bash

# Reinstall dependencies

pip install --force-reinstall transformers accelerate torch
```

## Testing

Run comprehensive test suite:

```bash

# Unit tests

pytest tests/test_deepseek_v32.py -v

# Integration tests

pytest tests/test_deepseek_integration.py -v

# All tests

pytest tests/test_deepseek_*.py -v
```

## Examples

See `examples/deepseek_demo.py` for complete working examples:

```bash
python examples/deepseek_demo.py
```

## Support

- **Documentation**: See README.md for complete integration guide
- **Issues**: Report bugs via GitHub issues
- **Model**: https://huggingface.co/deepseek-ai/deepseek-v3

## License

Part of Project-AI, released under MIT License.
