# External Integrations Documentation

## Overview

This directory contains comprehensive documentation for all 15 external service integrations used in Project-AI. Each document provides architecture diagrams, configuration instructions, implementation examples, security considerations, and testing strategies.

## Documentation Index

### AI & Machine Learning Providers

1. **[OpenAI Integration](./01-openai-integration.md)** (16.5 KB)
   - GPT-4, GPT-3.5-turbo chat completions
   - DALL-E 3 image generation
   - Text embeddings (ada-002)
   - Rate limiting, retry logic, cost optimization
   - **Primary AI provider with auto-fallback**

2. **[HuggingFace Integration](./02-huggingface-integration.md)** (22.5 KB)
   - Stable Diffusion 2.1 image generation
   - Open-source model access
   - Content safety filtering
   - Cold start mitigation
   - **Secondary AI provider (fallback)**

3. **[AI Orchestrator](./03-ai-orchestrator.md)** (21 KB)
   - Unified AIRequest/AIResponse interfaces
   - Automatic provider fallback (OpenAI → HuggingFace → Perplexity → Local)
   - Governance compliance enforcement
   - Provider health monitoring
   - **Core coordination layer for all AI operations**

4. **[OpenRouter Integration](./11-openrouter-integration.md)**
   - Unified access to GPT-4, Claude 3, Gemini Pro, Llama 2
   - OpenAI-compatible SDK interface
   - Model comparison and selection
   - **Multi-provider LLM aggregator**

5. **[Perplexity Integration](./12-perplexity-integration.md)**
   - Web-enhanced language models
   - Real-time search capabilities
   - Citation tracking
   - **Tertiary fallback with web search**

### Data & Analytics

6. **[Database Integrations](./05-database-integrations.md)** (21 KB)
   - **ClickHouse**: OLAP database for billion-row analytics
   - **RisingWave**: Streaming SQL database for real-time events
   - Metrics storage, log aggregation, time-series data
   - Materialized views, CDC pipelines
   - **High-performance analytics infrastructure**

7. **[Scikit-Learn ML](./13-scikit-learn-ml.md)**
   - Intent classification (TF-IDF + SGDClassifier)
   - K-means clustering for data analysis
   - PCA dimensionality reduction
   - Model persistence with joblib
   - **Machine learning utilities**

8. **[Pandas Data Analysis](./14-pandas-data-analysis.md)**
   - CSV/Excel/JSON data loading
   - Statistical analysis (describe, corr, groupby)
   - Data visualization with matplotlib
   - Missing value handling
   - **Tabular data processing**

### Infrastructure & Networking

9. **[GitHub API](./04-github-api.md)** (21.6 KB)
   - Security resource curation (CTF tools, penetration testing)
   - Repository metadata retrieval (stars, forks, updates)
   - Rate limit management (60/hour → 5000/hour with token)
   - GraphQL API for efficient queries
   - **Developer resource discovery**

10. **[Backend API Client](./10-backend-api-client.md)**
    - HTTP client for Flask web backend
    - Authentication (login, token management)
    - Desktop-to-web synchronization
    - **Cross-platform data sync**

11. **[SMTP/Email Integration](./07-smtp-email.md)** (20 KB)
    - Emergency alert delivery via email
    - Support for Gmail, SendGrid, Mailgun, Office 365
    - HTML email templates
    - Rate limiting, retry logic
    - **Critical alert notification system**

### Security & Storage

12. **[JSON Persistence](./06-json-persistence.md)** (20.7 KB)
    - File-based data storage pattern
    - Path traversal protection (sanitize_filename, safe_path_join)
    - Schema versioning and migration
    - Atomic writes with file locking
    - **Primary persistence mechanism**

13. **[Fernet Encryption](./09-encryption-fernet.md)**
    - AES-128-CBC symmetric encryption
    - Location history encryption
    - Cloud sync payload protection
    - Key management best practices
    - **Data-at-rest encryption**

14. **[Location Services](./08-location-services.md)**
    - IP geolocation via ipapi.co (1,500 req/day free)
    - Reverse geocoding via Nominatim/OpenStreetMap
    - Encrypted location history storage
    - GPS coordinate conversion
    - **Emergency location tracking**

### Reference

15. **[External APIs Overview](./15-external-apis-overview.md)**
    - Complete API inventory (17 services)
    - Environment variable reference
    - Rate limits comparison table
    - Unified error handling patterns
    - API usage tracking
    - **Integration summary and best practices**

## Quick Start

### 1. Environment Setup

Copy `.env.example` to `.env` [[.env]] and configure required API keys:

```bash
# Required for core functionality
OPENAI_API_KEY=sk-...                   # From https://platform.openai.com/api-keys
HUGGINGFACE_API_KEY=hf_...              # From https://huggingface.co/settings/tokens
FERNET_KEY=<generated>                  # Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Optional: Enhanced features
GITHUB_TOKEN=ghp_...                    # From https://github.com/settings/tokens
SMTP_USERNAME=your-email@gmail.com      # For emergency alerts
SMTP_PASSWORD=<app-password>            # Gmail App Password
OPENROUTER_API_KEY=sk-or-v1-...        # From https://openrouter.ai/keys
PERPLEXITY_API_KEY=pplx-...            # From https://www.perplexity.ai/settings/api
```

### 2. Verify Configuration

```python
from dotenv import load_dotenv
import os

load_dotenv()

# Check critical keys
required = ['OPENAI_API_KEY', 'HUGGINGFACE_API_KEY', 'FERNET_KEY']
for key in required:
    assert os.getenv(key), f"{key} not set in .env"

print("✅ All required API keys configured")
```

### 3. Test Integration

```python
from app.core.ai.orchestrator import run_ai, AIRequest

# Test AI orchestrator with auto-fallback
request = AIRequest(
    task_type="chat",
    prompt="Hello, this is a test message"
)

response = run_ai(request)
print(f"Provider: {response.provider_used}")
print(f"Response: {response.result}")
```

## Integration Patterns

### Pattern 1: AI Request with Fallback

```python
from app.core.ai.orchestrator import run_ai, AIRequest

# Automatically tries: OpenAI → HuggingFace → Perplexity → Local
request = AIRequest(
    task_type="chat",
    prompt="Explain machine learning",
    model="gpt-3.5-turbo"
)

response = run_ai(request)
```

### Pattern 2: Secure Data Persistence

```python
from app.core.user_manager import UserManager

# Automatic path traversal protection + bcrypt password hashing
manager = UserManager(users_file="users.json", data_dir="data")
manager.create_user("john_doe", "secure_password")
assert manager.verify_password("john_doe", "secure_password")
```

### Pattern 3: Emergency Alert with Location

```python
from app.core.emergency_alert import EmergencyAlert
from app.core.location_tracker import LocationTracker

# Get location
tracker = LocationTracker()
location = tracker.get_location_from_ip()

# Send encrypted location via email
alert = EmergencyAlert()
alert.add_emergency_contact("user", {"emails": ["emergency@example.com"]})
success, msg = alert.send_alert("user", location, "Emergency triggered")
```

### Pattern 4: High-Volume Analytics

```python
from app.core.clickhouse_integration import ClickHouseClient

# Billion-row analytics
ch = ClickHouseClient(host="localhost", port=9000)
ch.create_table("metrics", {"timestamp": "DateTime", "value": "Float64"})
ch.insert("metrics", [{"timestamp": datetime.now(), "value": 75.5}])

# Sub-second query on billions of rows
results = ch.execute("SELECT avg(value) FROM metrics WHERE timestamp >= now() - INTERVAL 1 HOUR")
```

## Testing Strategy

### Unit Tests (Mock External APIs)

```python
import pytest
from unittest.mock import patch

@patch('openai.OpenAI')
def test_openai_integration(mock_openai):
    # Mock API response
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Test"))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    # Test code
    from app.core.model_providers import OpenAIProvider
    provider = OpenAIProvider(api_key="test-key")
    result = provider.chat_completion([{"role": "user", "content": "Hi"}])
    assert result == "Test"
```

### Integration Tests (Real APIs)

```python
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="API key not set")
def test_real_openai_call():
    """Test actual OpenAI API call (requires valid key)."""
    request = AIRequest(task_type="chat", prompt="Say 'test'", provider="openai")
    response = run_ai(request)
    assert response.status == "success"
    assert response.provider_used == "openai"
```

## Security Checklist

- [ ] All API keys stored in `.env` [[.env]] (not hardcoded)
- [ ] `.env` [[.env]] file added to `.gitignore`
- [ ] Path traversal protection enabled (sanitize_filename, safe_path_join)
- [ ] Passwords hashed with bcrypt/pbkdf2 (never plaintext)
- [ ] Sensitive data encrypted with Fernet (location history, cloud sync)
- [ ] Rate limiting implemented for email, API calls
- [ ] Input validation for all user-provided data
- [ ] TLS encryption for SMTP connections
- [ ] Content filtering for image generation
- [ ] Audit logging for critical operations

## Rate Limits Reference

| Service | Free Tier | Authenticated | Notes |
|---------|-----------|---------------|-------|
| OpenAI | N/A | 3,500 TPM (trial) | Pay-per-token after trial |
| HuggingFace | 30 req/min | 300 req/min | Free tier sufficient |
| ipapi.co | 1,500/day | 10,000/day | $10/mo for 30K requests |
| GitHub | 60/hour | 5,000/hour | Personal token recommended |
| Gmail SMTP | 100-500/day | Same | Use SendGrid for higher volume |
| SendGrid | 100/day | Same | Free tier for alerts |

## Troubleshooting

### Issue: "OPENAI_API_KEY not set" error

```bash
# Verify .env file exists
cat .env | grep OPENAI_API_KEY

# Reload environment
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
```

### Issue: SMTP authentication failed

```bash
# Gmail: Generate App Password
# 1. Enable 2FA: https://myaccount.google.com/security
# 2. Create App Password: https://myaccount.google.com/apppasswords
# 3. Use App Password in .env (not regular password)
```

### Issue: HuggingFace 503 Service Unavailable

```python
# Model cold start delay (20-60 seconds)
# Implement retry with extended timeout
import time

for attempt in range(3):
    try:
        response = generate_image(prompt)
        break
    except Exception:
        time.sleep(20 * (attempt + 1))
```

## Performance Optimization

### 1. Response Caching

```python
from functools import lru_cache

@lru_cache(maxsize=200)
def cached_ai_call(prompt_hash: str) -> str:
    """Cache AI responses to avoid duplicate API calls."""
    request = AIRequest(task_type="chat", prompt=prompt_hash)
    response = run_ai(request)
    return response.result
```

### 2. Request Batching

```python
from concurrent.futures import ThreadPoolExecutor

def batch_ai_requests(prompts: list[str]) -> list[str]:
    """Process multiple AI requests in parallel."""
    with ThreadPoolExecutor(max_workers=5) as executor:
        requests = [AIRequest(task_type="chat", prompt=p) for p in prompts]
        responses = list(executor.map(run_ai, requests))
    return [r.result for r in responses]
```

### 3. Database Connection Pooling

```python
from psycopg2 import pool

# RisingWave connection pool
connection_pool = pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    host="localhost",
    port=4566
)
```

## Contributing

When adding new integrations:

1. Create documentation file: `NN-service-name.md`
2. Follow existing structure:
   - Overview
   - Architecture diagram
   - Configuration
   - Implementation
   - Usage patterns
   - Error handling
   - Testing
   - References
3. Update this README index
4. Add example to `15-external-apis-overview.md`
5. Include security considerations

## References

- **Project Documentation**: `source-docs/`
- **Implementation Code**: `src/app/core/`
- **Environment Template**: `.env.example`
- **Testing**: `tests/test_*.py`

---

## Quick Navigation

### Documentation in This Directory

- **01 Openai Integration**: [[source-docs\integrations\01-openai-integration.md]]
- **02 Huggingface Integration**: [[source-docs\integrations\02-huggingface-integration.md]]
- **03 Ai Orchestrator**: [[source-docs\integrations\03-ai-orchestrator.md]]
- **04 Github Api**: [[source-docs\integrations\04-github-api.md]]
- **05 Database Integrations**: [[source-docs\integrations\05-database-integrations.md]]
- **06 Json Persistence**: [[source-docs\integrations\06-json-persistence.md]]
- **07 Smtp Email**: [[source-docs\integrations\07-smtp-email.md]]
- **08 Location Services**: [[source-docs\integrations\08-location-services.md]]
- **09 Encryption Fernet**: [[source-docs\integrations\09-encryption-fernet.md]]
- **10 Backend Api Client**: [[source-docs\integrations\10-backend-api-client.md]]
- **11 Openrouter Integration**: [[source-docs\integrations\11-openrouter-integration.md]]
- **12 Perplexity Integration**: [[source-docs\integrations\12-perplexity-integration.md]]
- **13 Scikit Learn Ml**: [[source-docs\integrations\13-scikit-learn-ml.md]]
- **14 Pandas Data Analysis**: [[source-docs\integrations\14-pandas-data-analysis.md]]
- **15 External Apis Overview**: [[source-docs\integrations\15-external-apis-overview.md]]

### Related Source Code

- **Intelligence Engine**: [[src/app/core/intelligence_engine.py]]
- **Learning Paths**: [[src/app/core/learning_paths.py]]
- **Image Generator**: [[src/app/core/image_generator.py]]

### Related Documentation

- **Integration Relationships**: [[relationships/integrations/README.md]]
- **Developer Quick Reference**: [[DEVELOPER_QUICK_REFERENCE.md]]


---

## Related Documentation

- [Architecture Overview](../architecture/README.md)
- [Security Systems](../architecture/security-systems.md)
- [AI Systems](../architecture/ai-systems.md)
- [Testing Guide](../development/testing.md)
- [Deployment Guide](../deployment/README.md)
