# Perplexity API Integration

This document explains how to use Perplexity AI as an alternative model provider in Project-AI.

## Overview

Project-AI now supports multiple AI model providers through a unified interface. You can use either OpenAI or Perplexity AI for:

- Learning path generation
- RAG (Retrieval-Augmented Generation) queries
- General AI-powered features

## Configuration

### 1. Obtain a Perplexity API Key

1. Visit [Perplexity AI](https://www.perplexity.ai/) and sign up for an account
1. Navigate to your API settings to generate an API key
1. Copy your API key for use in the next step

### 2. Set Up Environment Variables

Add your Perplexity API key to your `.env` file:

```bash
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

You can also keep your OpenAI key if you want to use both providers:

```bash
OPENAI_API_KEY=your_openai_api_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

### 3. Configure Default Provider (Optional)

You can set the default AI provider in your `.projectai.toml` configuration file:

```toml
[ai]
model = "llama-3.1-sonar-small-128k-online"  # Perplexity model
provider = "perplexity"  # Use 'openai' for OpenAI
temperature = 0.7
max_tokens = 256
```

## Usage

### Using LearningPathManager

```python
from app.core.learning_paths import LearningPathManager

# Use Perplexity provider

manager = LearningPathManager(provider="perplexity")
path = manager.generate_path("machine learning", skill_level="beginner")

# Or use OpenAI provider

manager = LearningPathManager(provider="openai")
path = manager.generate_path("machine learning", skill_level="beginner")
```

### Using RAG System

```python
from app.core.rag_system import RAGSystem

# Initialize RAG system

rag = RAGSystem(data_dir="data/rag_index")

# Ingest documents

rag.ingest_directory("docs/")

# Query with Perplexity

result = rag.query_with_llm(
    query="What is the main concept?",
    model="llama-3.1-sonar-small-128k-online",
    provider="perplexity"
)

# Query with OpenAI

result = rag.query_with_llm(
    query="What is the main concept?",
    model="gpt-4",
    provider="openai"
)
```

### Direct Provider Usage

```python
from app.core.model_providers import get_provider

# Get Perplexity provider

perplexity = get_provider("perplexity", api_key="your_key")

# Check if available

if perplexity.is_available():
    response = perplexity.chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain quantum computing"}
        ],
        model="llama-3.1-sonar-small-128k-online",
        temperature=0.7
    )
    print(response)
```

## Available Perplexity Models

Perplexity offers several models with different capabilities:

- `llama-3.1-sonar-small-128k-online` - Fast, cost-effective model with online search
- `llama-3.1-sonar-large-128k-online` - More capable model with online search
- `llama-3.1-sonar-huge-128k-online` - Most capable model with online search

Refer to [Perplexity's documentation](https://docs.perplexity.ai/) for the latest model options.

## Benefits of Using Perplexity

1. **Real-time Information**: Perplexity models have access to current information through online search
1. **Citation Support**: Responses include citations to sources
1. **Cost-Effective**: Competitive pricing compared to other providers
1. **Specialized Models**: Purpose-built models for different use cases

## Switching Between Providers

You can easily switch between providers without changing your application code:

1. **Environment Variables**: Set `PERPLEXITY_API_KEY` or `OPENAI_API_KEY`
1. **Configuration File**: Update the `provider` setting in `.projectai.toml`
1. **Code**: Pass `provider="perplexity"` or `provider="openai"` to functions

## Error Handling

The system gracefully handles provider errors:

```python
from app.core.model_providers import get_provider

provider = get_provider("perplexity")

if not provider.is_available():
    print("Perplexity not available. Check your API key.")
else:
    try:
        response = provider.chat_completion(
            messages=[{"role": "user", "content": "Hello"}],
            model="llama-3.1-sonar-small-128k-online"
        )
    except Exception as e:
        print(f"Error: {e}")
```

## Testing

Run tests to verify the Perplexity integration:

```bash
pytest tests/test_model_providers.py -v
```

## Troubleshooting

### "Perplexity not available" Error

- Verify your `PERPLEXITY_API_KEY` is set correctly in `.env`
- Check that the openai package is installed (`pip install openai`)
- Ensure your API key is valid and active

### Rate Limiting

If you encounter rate limits:

- Wait before retrying
- Consider upgrading your Perplexity plan
- Implement exponential backoff in your application

### Model Not Found

If you get a model not found error:

- Check the model name spelling
- Verify the model is available in your Perplexity plan
- Refer to Perplexity's documentation for current model names

## Additional Resources

- [Perplexity AI Documentation](https://docs.perplexity.ai/)
- [Project-AI Documentation](../README.md)
- [Model Provider API Reference](../DEVELOPER_QUICK_REFERENCE.md)
