# External APIs Overview

## Integration Summary

Project-AI integrates with 15+ external APIs and services for comprehensive functionality:

### AI/ML Services (3)
1. **OpenAI API** - GPT models, DALL-E, embeddings
2. **HuggingFace Inference API** - Stable Diffusion, open-source models  
3. **OpenRouter API** - Unified access to multiple LLM providers
4. **Perplexity API** - Web-enhanced language models

### Data & Analytics (3)
5. **ClickHouse** - OLAP analytics database
6. **RisingWave** - Streaming SQL database
7. **Pandas/NumPy** - Data analysis and scientific computing

### Location & Mapping (2)
8. **ipapi.co** - IP geolocation (1,500 req/day free)
9. **Nominatim/OSM** - Reverse geocoding via geopy

### Communication (1)
10. **SMTP Servers** - Email delivery (Gmail, SendGrid, Mailgun)

### Developer Tools (2)
11. **GitHub REST API** - Repository metadata, security resources
12. **GitHub GraphQL API** - Efficient multi-resource queries

### Security & Encryption (2)
13. **Fernet (cryptography)** - Symmetric encryption for sensitive data
14. **bcrypt/pbkdf2** - Password hashing (passlib)

### Machine Learning (2)
15. **scikit-learn** - Intent classification, clustering, PCA
16. **matplotlib** - Data visualization

### Internal Services (1)
17. **Flask Backend API** - Desktop-to-web synchronization

## API Key Management

### Environment Variables (.env)
`ash
# AI Services
OPENAI_API_KEY=sk-...
HUGGINGFACE_API_KEY=hf_...
OPENROUTER_API_KEY=sk-or-v1-...
PERPLEXITY_API_KEY=pplx-...

# Database (optional)
CLICKHOUSE_HOST=localhost
RISINGWAVE_HOST=localhost

# Email
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Security
FERNET_KEY=<generated-key>

# GitHub (optional, increases rate limit)
GITHUB_TOKEN=ghp_...

# Backend
PROJECT_AI_BACKEND_URL=https://127.0.0.1:5000
`

### Security Best Practices
1. Never commit .env to version control
2. Use .env.example for documentation
3. Rotate keys periodically
4. Use app-specific passwords (Gmail)
5. Implement rate limiting
6. Validate and sanitize all inputs

## API Rate Limits

| Service | Unauthenticated | Authenticated | Billing |
|---------|----------------|---------------|---------|
| OpenAI | N/A | 3,500 TPM (free trial) | Pay-per-token |
| HuggingFace | 30 req/min | 300 req/min | Free tier |
| ipapi.co | 1,500/day | 10,000/day | /mo for 30K |
| GitHub | 60/hour | 5,000/hour | Free |
| Gmail SMTP | 100-500/day | Same | Free |

## Testing Strategy

### Mock External APIs
`python
@pytest.fixture
def mock_openai():
    with patch('openai.OpenAI') as mock:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='Test'))]
        mock_client.chat.completions.create.return_value = mock_response
        mock.return_value = mock_client
        yield mock

def test_with_mock_openai(mock_openai):
    # Test code using OpenAI API
    pass
`

### Integration Tests
`python
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason='API key not set')
def test_real_openai_call():
    # Test with real API (CI/CD only)
    pass
`

## Error Handling Patterns

### Unified Error Response
`python
@dataclass
class APIError:
    service: str
    error_code: int
    message: str
    retry_after: int | None = None

def handle_api_error(service: str, exception: Exception) -> APIError:
    if isinstance(exception, requests.HTTPError):
        return APIError(
            service=service,
            error_code=exception.response.status_code,
            message=exception.response.text,
            retry_after=exception.response.headers.get('Retry-After')
        )
    return APIError(service=service, error_code=500, message=str(exception))
`

### Retry with Exponential Backoff
`python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def api_call_with_retry():
    # API call that may fail transiently
    pass
`

## Monitoring & Observability

### API Usage Tracking
`python
class APIUsageTracker:
    def __init__(self):
        self.usage = defaultdict(list)
    
    def log_call(self, service: str, endpoint: str, status: int, latency_ms: float):
        self.usage[service].append({
            'endpoint': endpoint,
            'status': status,
            'latency_ms': latency_ms,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_stats(self, service: str) -> dict:
        calls = self.usage[service]
        return {
            'total_calls': len(calls),
            'success_rate': sum(1 for c in calls if c['status'] < 400) / len(calls),
            'avg_latency': sum(c['latency_ms'] for c in calls) / len(calls)
        }
`

## References

- [OpenAI Integration](./01-openai-integration.md)
- [HuggingFace Integration](./02-huggingface-integration.md)
- [AI Orchestrator](./03-ai-orchestrator.md)
- [GitHub API](./04-github-api.md)
- [Database Integrations](./05-database-integrations.md)
- [JSON Persistence](./06-json-persistence.md)
- [SMTP/Email](./07-smtp-email.md)
- [Location Services](./08-location-services.md)
- [Encryption (Fernet)](./09-encryption-fernet.md)
- [Backend API Client](./10-backend-api-client.md)
- [OpenRouter](./11-openrouter-integration.md)
- [Perplexity](./12-perplexity-integration.md)
- [Scikit-Learn ML](./13-scikit-learn-ml.md)
- [Pandas Data Analysis](./14-pandas-data-analysis.md)


---

## Related Documentation

- **Relationship Map**: [[relationships\integrations\README.md]]
- **05 External Apis**: [[relationships\integrations\05-external-apis.md]]
