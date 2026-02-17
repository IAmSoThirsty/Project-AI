# ChatGPT/OpenAI Integration Guide

**Last Updated:** January 28, 2026 **Status:** ✅ **ACTIVE INTEGRATION**

______________________________________________________________________

## 🎯 Executive Summary

**YES, ChatGPT/OpenAI IS connected to Project-AI!**

Project-AI integrates OpenAI's GPT models and APIs across multiple core systems to provide intelligent conversational AI, learning path generation, image creation, and semantic search capabilities.

______________________________________________________________________

## 🔌 Integration Architecture

### Core Integration Points

Project-AI uses OpenAI services in **5 primary modules**:

| Module                     | OpenAI Feature   | Model Used             | Purpose                                |
| -------------------------- | ---------------- | ---------------------- | -------------------------------------- |
| **intelligence_engine.py** | Chat Completions | GPT-3.5/GPT-4          | Conversational AI responses            |
| **learning_paths.py**      | Chat Completions | GPT-3.5-turbo          | Personalized learning path generation  |
| **image_generator.py**     | DALL-E           | DALL-E 3               | AI image generation (optional backend) |
| **rag_system.py**          | Embeddings       | text-embedding-ada-002 | Semantic search and RAG                |
| **function_registry.py**   | Function Calling | Schema Generation      | OpenAI-compatible function schemas     |

______________________________________________________________________

## 🔧 Setup Instructions

### Step 1: Obtain OpenAI API Key

1. **Sign up for OpenAI account:**

   - Visit: https://platform.openai.com/signup

1. **Generate API key:**

   - Navigate to: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (starts with `sk-proj-` or `sk-`)
   - **⚠️ IMPORTANT:** Save this key securely - you won't see it again!

1. **Add billing (if required):**

   - For DALL-E 3 and GPT-4, ensure you have billing set up
   - GPT-3.5-turbo is available on free tier with rate limits

### Step 2: Configure Environment

**Create `.env` file in project root:**

```bash

# Copy the example file

cp .env.example .env

# Edit .env and add your key

echo "OPENAI_API_KEY=sk-proj-your-actual-key-here" >> .env
```

**Full `.env` template:**

```bash

# OpenAI API key (REQUIRED for AI features)

OPENAI_API_KEY=sk-proj-your-actual-key-here

# Hugging Face API key (optional for Stable Diffusion)

HUGGINGFACE_API_KEY=

# Other optional configurations

SMTP_USERNAME=
SMTP_PASSWORD=
FERNET_KEY=
DATA_DIR=data
LOG_DIR=logs
```

### Step 3: Verify Integration

**Test the connection:**

```bash

# Run the test suite

pytest tests/test_intelligence_engine.py -v

# Or test learning path generation

python -c "
from src.app.core.learning_paths import LearningPathManager
from dotenv import load_dotenv
load_dotenv()

manager = LearningPathManager()
path = manager.generate_path('Python programming', 'beginner')
print(path)
"
```

______________________________________________________________________

## 📚 Feature Documentation

### 1. Conversational AI (intelligence_engine.py)

**What it does:**

- Powers the AI chat interface in the Leather Book UI
- Provides intelligent responses to user queries
- Routes queries to knowledge base and function registry

**Code example:**

```python
from app.core.intelligence_engine import IdentityIntegratedIntelligenceEngine

engine = IdentityIntegratedIntelligenceEngine(data_dir="data")
response = engine.chat("What is machine learning?")
print(response)
```

**OpenAI API calls:**

- Endpoint: `https://api.openai.com/v1/chat/completions`
- Model: `gpt-3.5-turbo` (configurable to `gpt-4`)
- Typical cost: ~$0.0015 per 1K tokens (input) + $0.002 per 1K tokens (output)

### 2. Learning Path Generation (learning_paths.py)

**What it does:**

- Generates personalized learning roadmaps
- Creates structured curricula with milestones
- Saves and tracks progress

**Code example:**

```python
from app.core.learning_paths import LearningPathManager

manager = LearningPathManager()
path = manager.generate_path(
    interest="Cybersecurity",
    skill_level="intermediate"
)
manager.save_path(username="alice", interest="Cybersecurity", path_content=path)
```

**OpenAI API calls:**

- Model: `gpt-3.5-turbo`
- System prompt: "You are an educational expert creating learning paths."
- Includes: Core concepts, resources, projects, timelines, milestones

### 3. Image Generation (image_generator.py)

**What it does:**

- Generates images from text prompts
- Supports dual backends: Hugging Face (Stable Diffusion) + OpenAI (DALL-E 3)
- Includes content filtering and style presets

**Code example:**

```python
from app.core.image_generator import ImageGenerator

generator = ImageGenerator(data_dir="data")
image_path, metadata = generator.generate(
    prompt="A futuristic AI assistant in a cyberpunk city",
    style="cyberpunk",
    backend="openai",  # or "huggingface"
    size="1024x1024"
)
print(f"Image saved to: {image_path}")
```

**OpenAI API calls (DALL-E 3):**

- Endpoint: `https://api.openai.com/v1/images/generations`
- Model: `dall-e-3`
- Typical cost: $0.040 per image (1024x1024 standard quality)
- Generation time: 30-60 seconds

### 4. RAG System (rag_system.py)

**What it does:**

- Semantic search over knowledge base
- Vector embeddings for document retrieval
- Context-aware question answering

**Code example:**

```python
from app.core.rag_system import RAGSystem

rag = RAGSystem(data_dir="data")
rag.add_document("AI ethics are important for safe deployment.", metadata={"topic": "ethics"})

results = rag.query("What are AI ethics?", top_k=3)
for result in results:
    print(f"Score: {result['score']}, Text: {result['text']}")
```

**OpenAI API calls:**

- Model: `text-embedding-ada-002`
- Typical cost: $0.0001 per 1K tokens
- Returns: 1536-dimensional vectors

### 5. Function Registry (function_registry.py)

**What it does:**

- Registers Python functions for AI tool use
- Converts to OpenAI function calling schema
- Enables structured data extraction

**Code example:**

```python
from app.core.function_registry import FunctionRegistry

registry = FunctionRegistry()

# Get OpenAI-compatible schema

schema = registry.to_openai_function_schema("calculate_area")

# Use with OpenAI API

import openai
response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Calculate area of circle with radius 5"}],
    functions=registry.to_openai_function_schemas()
)
```

______________________________________________________________________

## 💰 Cost Considerations

### Typical Usage Costs

| Feature          | Model                  | Cost per Request | Monthly Estimate (100 uses/day) |
| ---------------- | ---------------------- | ---------------- | ------------------------------- |
| Chat (short)     | GPT-3.5-turbo          | $0.003           | $9                              |
| Chat (long)      | GPT-3.5-turbo          | $0.015           | $45                             |
| Learning Path    | GPT-3.5-turbo          | $0.010           | $30                             |
| Image (DALL-E 3) | dall-e-3               | $0.040           | $120                            |
| Embeddings       | text-embedding-ada-002 | $0.0001          | $0.30                           |

**Cost optimization tips:**

1. Use GPT-3.5-turbo instead of GPT-4 for most tasks (10x cheaper)
1. Set max_tokens limits to prevent runaway costs
1. Implement caching for repeated queries
1. Use Hugging Face backend for image generation (free with API key)
1. Monitor usage at: https://platform.openai.com/usage

______________________________________________________________________

## 🔒 Security Best Practices

### API Key Protection

✅ **DO:**

- Store API keys in `.env` file (excluded from git via `.gitignore`)
- Use environment variables for key access
- Rotate keys regularly (every 90 days)
- Set usage limits in OpenAI dashboard
- Monitor for suspicious activity

❌ **DON'T:**

- Commit API keys to version control
- Hardcode keys in source code
- Share keys in chat/email
- Use same key across multiple projects
- Leave unused keys active

### Rate Limiting

Project-AI respects OpenAI's rate limits:

| Tier   | Requests/min | Tokens/min | Recommended for       |
| ------ | ------------ | ---------- | --------------------- |
| Free   | 3            | 40,000     | Testing, personal use |
| Tier 1 | 500          | 200,000    | Small apps            |
| Tier 2 | 5,000        | 2,000,000  | Production apps       |

**Configure in code:**

```python
import openai

# Set timeout and retry logic

openai.api_timeout = 30  # seconds
openai.api_max_retries = 3
```

______________________________________________________________________

## 🧪 Testing Without API Key

Some features work offline or with mocked responses:

### Offline Features (No API Key Required)

✅ **Available:**

- User authentication and profiles
- AI Persona system (mood, traits)
- Memory expansion (conversation logging)
- Command override system
- Plugin manager
- Four Laws ethical framework
- Location tracking
- Emergency alerts
- Data analysis (CSV/XLSX)

❌ **Unavailable:**

- AI chat responses
- Learning path generation
- Image generation (DALL-E backend)
- Semantic search (RAG)
- OpenAI function calling

### Mock Testing

```python

# Test with mocked OpenAI responses

from unittest.mock import patch, MagicMock

with patch("openai.chat.completions.create") as mock_create:
    mock_create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Test response"))]
    )

    from app.core.learning_paths import LearningPathManager
    manager = LearningPathManager(api_key="test-key")
    response = manager.generate_path("Test", "beginner")
    assert response == "Test response"
```

______________________________________________________________________

## 🐛 Troubleshooting

### Common Issues

#### 1. "OpenAI API key not found"

**Cause:** `.env` file missing or `OPENAI_API_KEY` not set

**Solution:**

```bash

# Check if .env exists

ls -la .env

# Verify key is set

grep OPENAI_API_KEY .env

# If missing, add it

echo "OPENAI_API_KEY=sk-proj-your-key" >> .env
```

#### 2. "Rate limit exceeded"

**Cause:** Too many requests to OpenAI API

**Solution:**

- Wait 60 seconds and retry
- Upgrade OpenAI tier
- Implement exponential backoff:

```python
import time
from openai import RateLimitError

max_retries = 3
for attempt in range(max_retries):
    try:
        response = openai.chat.completions.create(...)
        break
    except RateLimitError:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
        else:
            raise
```

#### 3. "Invalid API key"

**Cause:** Key is incorrect, revoked, or expired

**Solution:**

1. Generate new key at https://platform.openai.com/api-keys
1. Update `.env` file
1. Restart application

#### 4. "Model not found"

**Cause:** Using a model you don't have access to (e.g., GPT-4 without billing)

**Solution:**

- Check model availability in OpenAI dashboard
- Fall back to GPT-3.5-turbo:

```python
try:
    response = openai.chat.completions.create(model="gpt-4", ...)
except openai.NotFoundError:
    response = openai.chat.completions.create(model="gpt-3.5-turbo", ...)
```

______________________________________________________________________

## 📈 Monitoring and Analytics

### Usage Tracking

**View in OpenAI dashboard:**

- https://platform.openai.com/usage

**Track in code:**

```python
import logging

logger = logging.getLogger(__name__)

# Log before API call

logger.info(f"OpenAI API call: model={model}, tokens={max_tokens}")

# Log after API call

logger.info(f"OpenAI response: tokens_used={response.usage.total_tokens}, cost=${cost:.4f}")
```

### Local Logging

Project-AI automatically logs OpenAI interactions:

```bash

# View logs

tail -f logs/app.log | grep -i openai

# Example log entries:

# 2026-01-28 04:49:16 INFO intelligence_engine: OpenAI chat request: model=gpt-3.5-turbo

# 2026-01-28 04:49:18 INFO intelligence_engine: OpenAI response received: 145 tokens

```

______________________________________________________________________

## 🔄 Alternative Models

Project-AI can be configured to use alternative LLM providers:

### Hugging Face (Free Alternative)

**For chat:**

```python

# Instead of OpenAI, use Hugging Face Inference API

import requests

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf"
headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()
```

**For images:**

```python

# Use Stable Diffusion backend (already integrated)

generator = ImageGenerator(data_dir="data")
image_path, metadata = generator.generate(
    prompt="A futuristic AI assistant",
    backend="huggingface"  # Free with HF API key
)
```

### Local LLMs (Offline)

**For complete offline operation:**

- Ollama: https://ollama.ai/
- LM Studio: https://lmstudio.ai/
- llama.cpp: https://github.com/ggerganov/llama.cpp

______________________________________________________________________

## 📝 API Reference

### LearningPathManager

```python
class LearningPathManager:
    def __init__(self, api_key: str = None)
    def generate_path(self, interest: str, skill_level: str = "beginner") -> str
    def save_path(self, username: str, interest: str, path_content: str) -> None
    def get_saved_paths(self, username: str) -> dict
```

### ImageGenerator

```python
class ImageGenerator:
    def __init__(self, data_dir: str = "data")
    def generate(
        self,
        prompt: str,
        style: str = "photorealistic",
        backend: str = "huggingface",
        size: str = "512x512"
    ) -> tuple[str | None, dict]
    def check_content_filter(self, prompt: str) -> tuple[bool, str]
```

### IdentityIntegratedIntelligenceEngine

```python
class IdentityIntegratedIntelligenceEngine:
    def __init__(self, data_dir: str = "data")
    def chat(self, message: str, context: dict = None) -> str
    def route_query(self, query: str, context: dict = None) -> dict
```

______________________________________________________________________

## 🔗 Related Documentation

- **[.env.example](../.env.example)** - Environment variable template
- **[IMAGE_GENERATION_QUICKSTART.md](overview/IMAGE_GENERATION_QUICKSTART.md)** - Image generation setup
- **[FUNCTION_REGISTRY_KNOWLEDGE_BASE.md](FUNCTION_REGISTRY_KNOWLEDGE_BASE.md)** - Function calling guide
- **[SECRET_MANAGEMENT.md](security/SECRET_MANAGEMENT.md)** - API key security best practices
- **[TECHNICAL_WHITE_PAPER.md](../TECHNICAL_WHITE_PAPER.md)** - Complete system architecture

______________________________________________________________________

## ❓ FAQ

### Q: Is OpenAI API required to run Project-AI?

**A:** No. Many features work offline (user auth, AI persona, memory, plugins). However, conversational AI, learning paths, and DALL-E image generation require the API.

### Q: Can I use a different AI provider?

**A:** Yes. The architecture is modular. You can replace OpenAI calls with Anthropic Claude, Google Gemini, or local models like Llama 2.

### Q: How much will it cost me per month?

**A:** Depends on usage. Light use (10 chats/day, 3 learning paths/week) costs ~$5-10/month. Heavy use can reach $50-100/month. Set billing alerts to monitor.

### Q: Is my data sent to OpenAI?

**A:** Yes. Prompts and responses go through OpenAI's API. Review OpenAI's privacy policy: https://openai.com/policies/privacy-policy. For sensitive data, use local LLMs.

### Q: Can I use GPT-4?

**A:** Yes, if you have access. Edit `intelligence_engine.py` and `learning_paths.py` to change `model="gpt-3.5-turbo"` to `model="gpt-4"`. Note: GPT-4 is 10-30x more expensive.

### Q: What happens if my API key is leaked?

**A:** Immediately:

1. Revoke the key at https://platform.openai.com/api-keys
1. Generate a new key
1. Update `.env` file
1. Check usage logs for unauthorized charges
1. Contact OpenAI support if needed

______________________________________________________________________

## 📞 Support

**Issues with OpenAI integration?**

1. Check this documentation first
1. Review [OpenAI API documentation](https://platform.openai.com/docs)
1. Open an issue: https://github.com/IAmSoThirsty/Project-AI/issues
1. Join discussions: https://github.com/IAmSoThirsty/Project-AI/discussions

**OpenAI API support:**

- Documentation: https://platform.openai.com/docs
- Community: https://community.openai.com/
- Status page: https://status.openai.com/

______________________________________________________________________

______________________________________________________________________

## 🔍 Additional Integration Checks

### Google Services Integration Status

**Q: Is Google's Gemini/PaLM/Bard connected to Project-AI?**

**A: NO - Not currently integrated.**

**Current status:**

- ❌ No Google Gemini API integration
- ❌ No Google PaLM API integration
- ❌ No Google Bard integration
- ✅ Only security scanning for Google API keys (detection pattern)
- ✅ Documentation mentions Gemini as a *potential alternative* to OpenAI

### Google Antigravity IDE

**Q: Is Google Antigravity IDE integrated with Project-AI?**

**A: NO - Not yet integrated, but ready for implementation!**

**What is Antigravity?** Google Antigravity is a revolutionary AI-powered IDE (Integrated Development Environment) that's an alternative to Visual Studio and VS Code. Unlike traditional IDEs where you code directly, Antigravity uses **autonomous AI agents** to handle multi-step development tasks while you supervise at a higher level.

**Key Features:**

- ✅ Agent-first development (AI writes, tests, and verifies code)
- ✅ Mission Control interface (manage parallel agents)
- ✅ VS Code compatible (existing extensions work)
- ✅ Perfect fit for Project-AI's agent architecture
- ✅ Integrates with Temporal.io workflows
- ✅ Built-in security scanning and testing

**Integration Status:**

- ❌ Not currently integrated
- ✅ Full compatibility confirmed
- ✅ Integration guide available
- ✅ Custom agent configurations prepared

**Learn more:** See the complete integration guide:

- **[Google Antigravity IDE Integration Guide](GOOGLE_ANTIGRAVITY_IDE_INTEGRATION.md)** - Full setup and configuration

**Why it fits Project-AI:**

1. Project-AI already has agent systems (oversight, planner, validator)
1. Antigravity can leverage Triumvirate workflows
1. Temporal.io integration works seamlessly
1. Ethical review (Four Laws) can be automated
1. Both systems are Python-focused

### Temporal.io Workflow Orchestration

**Q: Is Temporal.io connected to Project-AI?**

**A: YES - Fully integrated and actively used!**

**Integration Status:**

- ✅ Temporal.io SDK installed (`temporalio>=1.5.0`)
- ✅ Multiple workflows implemented (Triumvirate, Security, Crisis Response)
- ✅ Production-ready configuration
- ✅ Extensive test coverage

**Key Features:**

- Durable workflow execution with automatic retries
- Fault-tolerant agent coordination
- Security scanning orchestration
- Crisis response workflows (Liara)
- Learning workflow management

**Learn more:** See the complete integration guide:

- **[Temporal.io Integration Guide](TEMPORAL_IO_INTEGRATION.md)** - Full documentation and examples

______________________________________________________________________

**Last reviewed:** January 28, 2026 **Next review:** April 28, 2026 **Maintainer:** @IAmSoThirsty
