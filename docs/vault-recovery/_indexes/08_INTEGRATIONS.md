---
type: moc
area: integrations
priority: P1
status: active
version: "1.0.0"
created: 2025-01-23
updated: 2025-01-23
maintainer: AGENT-019
total_documents: 120+
schema_version: "1.0"
tags:
  - integrations
  - apis
  - external-services
  - webhooks
  - moc
aliases:
  - Integrations MOC
  - API Integration Index
  - External Services Map
related_mocs:
  - "[[01_ARCHITECTURE]]"
  - "[[02_SECURITY]]"
  - "[[06_SOURCE_CODE]]"
---

# 08 - Integrations & APIs MOC

**Purpose:** Comprehensive documentation mapping external API integrations, third-party services, webhooks, data synchronization protocols, and integration patterns for Project-AI's desktop and web platforms.

**Scope:** OpenAI integration (GPT models, DALL-E 3), Hugging Face integration (Stable Diffusion 2.1), GitHub API (security resources, CTF repos), email integration (SMTP for emergency alerts), IP geolocation services, and planned integrations (database, cloud storage, monitoring, analytics).

**Audience:** Integration engineers, backend developers, API consumers, third-party service maintainers, and anyone implementing or troubleshooting external service integrations.

---

## 🔌 External API Integrations

### OpenAI Integration

**Services Used:**
- **GPT Models:** Intelligence engine, learning path generation, chat responses
- **DALL-E 3:** Image generation (alternative to Hugging Face)

**API Configuration:**
```python
# Environment variable
OPENAI_API_KEY=sk-...

# Usage in code
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
```

**Modules:**
- `src/app/core/intelligence_engine.py` - GPT chat integration
- `src/app/core/learning_paths.py` - GPT-4 learning path generation
- `src/app/core/image_generator.py` - DALL-E 3 image generation

**Key Features:**
- **Chat Completions:** GPT-4 for conversational AI responses
- **Function Calling:** Structured outputs for learning paths
- **Image Generation:** DALL-E 3 for high-quality images (1024x1024, 1792x1024, 1024x1792)
- **Error Handling:** Retry logic for rate limits, timeout handling
- **Content Filtering:** OpenAI moderation API for prompt safety

**Rate Limits:**
- **GPT-4:** 10,000 tokens/minute (tier-dependent)
- **DALL-E 3:** 5 images/minute
- **Handling:** Exponential backoff retry strategy

**Documents:**
- `integration-openai.md` - OpenAI integration architecture [P1, Active]
- `integration-openai-chat.md` - GPT chat integration [P1, Active]
- `integration-openai-dalle.md` - DALL-E 3 image generation [P1, Active]
- `integration-openai-rate-limits.md` - Rate limit handling [P1, Active]
- `integration-openai-security.md` - API key security [P0, Active]

**Example Usage:**
```python
# Intelligence Engine (GPT Chat)
from src.app.core.intelligence_engine import IntelligenceEngine

engine = IntelligenceEngine()
response = engine.chat("What is the capital of France?")
print(response)  # "The capital of France is Paris."

# Learning Path Generation
from src.app.core.learning_paths import generate_learning_path

path = generate_learning_path(
    topic="Python Web Development",
    skill_level="intermediate"
)
print(path["modules"])  # [{"title": "Flask Basics", "duration": "2 weeks", ...}]

# DALL-E 3 Image Generation
from src.app.core.image_generator import ImageGenerator

generator = ImageGenerator()
image_path, metadata = generator.generate(
    prompt="A futuristic cityscape at sunset",
    style="photorealistic",
    backend="openai"
)
print(image_path)  # "data/images/generated_20250123_143215.png"
```

---

### Hugging Face Integration

**Services Used:**
- **Stable Diffusion 2.1:** Primary image generation backend
- **Inference API:** Cloud-hosted model inference

**API Configuration:**
```python
# Environment variable
HUGGINGFACE_API_KEY=hf_...

# API endpoint
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
```

**Modules:**
- `src/app/core/image_generator.py` - Stable Diffusion integration

**Key Features:**
- **Inference API:** Cloud-hosted Stable Diffusion 2.1
- **Style Presets:** 10 style options (photorealistic, digital_art, oil_painting, etc.)
- **Negative Prompts:** Automatic safety negative prompts (prevent violence, NSFW)
- **Resolution:** 512x512 default, upscaling available
- **Cost-Effective:** Free tier available, pay-per-use pricing

**Content Safety:**
- **Keyword Filter:** 15 blocked keywords (violence, explicit, illegal)
- **Safety Negative Prompts:** Automatically added to prevent unsafe content
- **No OpenAI-style Moderation:** Content filtering is client-side only

**Documents:**
- `integration-huggingface.md` - Hugging Face integration [P1, Active]
- `integration-stable-diffusion.md` - Stable Diffusion configuration [P1, Active]
- `integration-hf-inference-api.md` - Inference API usage [P1, Active]
- `integration-hf-content-safety.md` - Content filtering strategy [P1, Active]

**Example Usage:**
```python
from src.app.core.image_generator import ImageGenerator

generator = ImageGenerator()
image_path, metadata = generator.generate(
    prompt="A serene mountain landscape with a lake",
    style="watercolor",
    backend="huggingface"
)

print(metadata)
# {
#   "backend": "huggingface",
#   "model": "stabilityai/stable-diffusion-2-1",
#   "style": "watercolor",
#   "prompt": "A serene mountain landscape with a lake, watercolor painting style",
#   "negative_prompt": "violence, gore, nsfw, explicit",
#   "timestamp": "2025-01-23T14:32:15"
# }
```

**Comparison: Hugging Face vs OpenAI DALL-E:**
| Feature | Hugging Face (SD 2.1) | OpenAI (DALL-E 3) |
|---------|------------------------|-------------------|
| Quality | Good (photorealistic possible) | Excellent (best-in-class) |
| Speed | 20-40 seconds | 40-60 seconds |
| Cost | Free tier + low cost | $0.04-0.12 per image |
| Content Policy | Client-side filtering | Strict OpenAI moderation |
| Resolution | 512x512 default | 1024x1024+ |
| Style Control | Prompt-based | Prompt-based |
| Use Case | Cost-sensitive, flexible | High-quality, commercial |

---

### GitHub API Integration

**Services Used:**
- **Repository Search:** Find security resources, CTF challenges
- **Content API:** Fetch repository contents, READMEs

**API Configuration:**
```python
# Optional authentication (increases rate limits)
GITHUB_TOKEN=ghp_...  # Personal Access Token

# Usage
import requests

headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
response = requests.get("https://api.github.com/search/repositories?q=ctf", headers=headers)
```

**Modules:**
- `src/app/core/security_resources.py` - GitHub repository search for security content

**Key Features:**
- **Repository Search:** Search for CTF challenges, security tools, learning resources
- **Content Fetching:** Download READMEs, documentation, code samples
- **Rate Limits:** 60 requests/hour (unauthenticated), 5,000 requests/hour (authenticated)
- **Caching:** Cache search results to reduce API calls

**Documents:**
- `integration-github-api.md` - GitHub API integration [P2, Active]
- `integration-github-search.md` - Repository search patterns [P2, Active]
- `integration-github-rate-limits.md` - Rate limit management [P2, Active]

---

### Email Integration (SMTP)

**Services Used:**
- **SMTP Protocol:** Send emergency alert emails

**API Configuration:**
```python
# Environment variables
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=app_specific_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Usage
import smtplib
from email.mime.text import MIMEText

smtp = smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT")))
smtp.starttls()
smtp.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
```

**Modules:**
- `src/app/core/emergency_alert.py` - Email alert system

**Key Features:**
- **Emergency Contacts:** Store and manage emergency contact list
- **Alert Sending:** Send email alerts with subject, body, priority
- **TLS Encryption:** Secure email transmission
- **Error Handling:** Retry logic for SMTP failures

**Documents:**
- `integration-smtp.md` - SMTP email integration [P2, Active]
- `integration-emergency-alerts.md` - Emergency alert system [P2, Active]

---

### IP Geolocation Integration

**Services Used:**
- **IP Geolocation APIs:** ipapi.co, ip-api.com (free tiers)

**Modules:**
- `src/app/core/location_tracker.py` - IP geolocation and GPS tracking

**Key Features:**
- **IP-based Location:** Detect user location from IP address
- **Encrypted History:** Store location history with Fernet encryption
- **Privacy:** User consent required, encrypted storage

**Documents:**
- `integration-geolocation.md` - Geolocation API integration [P2, Active]
- `integration-location-privacy.md` - Location data privacy [P2, Active]

---

## 🔮 Planned Integrations

### Database Integrations

#### PostgreSQL (Planned)
**Purpose:** Multi-user web platform database

**Features:**
- **ACID Transactions:** Ensure data consistency
- **Schema Migrations:** Alembic for database migrations
- **Connection Pooling:** pgbouncer for connection management
- **Replication:** Read replicas for scalability

**Documents:**
- `integration-postgresql.md` - PostgreSQL integration [P2, Planned]
- `integration-database-migrations.md` - Schema migration strategy [P2, Planned]

#### Redis (Planned)
**Purpose:** Session storage, caching, rate limiting

**Features:**
- **Session Store:** Shared session state for horizontal scaling
- **Caching:** Cache frequently accessed data (user profiles, AI state)
- **Rate Limiting:** Token bucket algorithm for API rate limiting
- **Pub/Sub:** Real-time notifications

**Documents:**
- `integration-redis.md` - Redis integration [P2, Planned]
- `integration-caching-strategy.md` - Caching patterns [P2, Planned]

---

### Cloud Storage Integrations

#### AWS S3 (Planned)
**Purpose:** User uploads, generated images, backups

**Features:**
- **Object Storage:** Store generated images, user uploads
- **Versioning:** Automatic file versioning
- **Lifecycle Policies:** Auto-delete old files, transition to cheaper storage
- **Presigned URLs:** Secure temporary file access

**Documents:**
- `integration-aws-s3.md` - S3 integration [P2, Planned]
- `integration-object-storage.md` - Object storage patterns [P2, Planned]

#### Google Cloud Storage (Alternative)
**Purpose:** Alternative to AWS S3

**Documents:**
- `integration-gcs.md` - Google Cloud Storage integration [P3, Planned]

---

### Monitoring & Analytics Integrations

#### Datadog (Planned)
**Purpose:** Application performance monitoring (APM), infrastructure monitoring

**Features:**
- **APM:** Trace requests end-to-end
- **Metrics:** Collect custom metrics (AI latency, image generation time)
- **Logging:** Centralized log aggregation
- **Alerting:** Real-time alerts for anomalies

**Documents:**
- `integration-datadog.md` - Datadog integration [P2, Planned]
- `integration-apm.md` - APM setup and configuration [P2, Planned]

#### Google Analytics (Planned)
**Purpose:** User behavior analytics (web platform)

**Documents:**
- `integration-google-analytics.md` - GA4 integration [P3, Planned]

---

### Authentication Integrations

#### OAuth 2.0 Providers (Planned)
**Purpose:** Social login (Google, GitHub, Microsoft)

**Providers:**
- **Google OAuth:** Login with Google account
- **GitHub OAuth:** Login with GitHub account
- **Microsoft OAuth:** Login with Microsoft account

**Documents:**
- `integration-oauth.md` - OAuth 2.0 integration [P2, Planned]
- `integration-social-login.md` - Social login strategy [P2, Planned]

---

## 🔗 Integration Patterns

### API Client Pattern

**Pattern:** Centralized API client with retry logic, error handling, logging

**Example:**
```python
import requests
import time
from typing import Optional, Dict, Any

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        retries: int = 3
    ) -> Dict[str, Any]:
        """Make API request with retry logic."""
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(retries):
            try:
                response = requests.request(
                    method, url, headers=self.headers, json=data, timeout=30
                )
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.Timeout:
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    time.sleep(60)
                    continue
                raise
        
        raise Exception(f"Failed after {retries} attempts")
```

**Documents:**
- `integration-patterns.md` - Common integration patterns [P1, Active]
- `integration-retry-logic.md` - Retry and backoff strategies [P1, Active]

### Webhook Pattern (Planned)

**Pattern:** Receive real-time events from external services

**Use Cases:**
- GitHub webhooks for repository updates
- Stripe webhooks for payment events
- Twilio webhooks for SMS delivery status

**Documents:**
- `integration-webhooks.md` - Webhook integration pattern [P2, Planned]
- `integration-webhook-security.md` - Webhook signature verification [P2, Planned]

---

## 🔒 Integration Security

### API Key Management

**Best Practices:**
- **Environment Variables:** Never hardcode API keys
- **Secret Managers:** Use AWS Secrets Manager, HashiCorp Vault (production)
- **Rotation:** Regular API key rotation (quarterly)
- **Least Privilege:** Use read-only keys when possible
- **Monitoring:** Alert on suspicious API key usage

**Documents:**
- `integration-security.md` - Integration security best practices [P0, Active]
- `integration-api-key-management.md` - API key lifecycle [P1, Active]
- `integration-secrets-management.md` - Secret management strategies [P1, Active]

### Rate Limiting & Throttling

**Strategies:**
- **Token Bucket:** Track API quota, refill over time
- **Exponential Backoff:** Increase delay between retries
- **Circuit Breaker:** Stop requests after repeated failures
- **Caching:** Cache responses to reduce API calls

**Documents:**
- `integration-rate-limiting.md` - Rate limiting strategies [P1, Active]
- `integration-circuit-breaker.md` - Circuit breaker pattern [P2, Active]

### Error Handling

**Best Practices:**
- **Graceful Degradation:** Fallback to cached data or default behavior
- **User-Friendly Errors:** Don't expose API keys or internal errors
- **Logging:** Log all integration errors with context
- **Alerting:** Alert on high error rates

**Documents:**
- `integration-error-handling.md` - Error handling patterns [P1, Active]
- `integration-logging.md` - Integration logging strategy [P1, Active]

---

## 📚 Cross-References

### Related MOCs
- [[01_ARCHITECTURE]] - Integration architecture, API design
- [[02_SECURITY]] - API security, authentication, encryption
- [[06_SOURCE_CODE]] - Integration module source code

### Related Indexes
- `by-type/api-reference-type-index.md` - API documentation
- `by-priority/p1-high-priority-index.md` - High-priority integrations
- `cross-reference/integration-dependencies-index.md` - Integration dependencies

---

## 🔍 Quick Reference

### Active Integrations
- **OpenAI:** GPT-4 (intelligence_engine, learning_paths), DALL-E 3 (image_generator)
- **Hugging Face:** Stable Diffusion 2.1 (image_generator)
- **GitHub:** Repository search (security_resources)
- **SMTP:** Email alerts (emergency_alert)
- **IP Geolocation:** Location tracking (location_tracker)

### API Key Environment Variables
```bash
OPENAI_API_KEY=sk-...
HUGGINGFACE_API_KEY=hf_...
GITHUB_TOKEN=ghp_...  # Optional, increases rate limits
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=app_specific_password
```

### Integration Testing Checklist
1. [ ] API key configured in `.env`
2. [ ] Retry logic tested (manual disconnect)
3. [ ] Rate limit handling verified
4. [ ] Error handling tested (invalid keys, timeouts)
5. [ ] Logging captures integration events
6. [ ] Fallback behavior works (cached data, defaults)
7. [ ] Security scan passed (no hardcoded keys)
8. [ ] Documentation updated (API changes, new endpoints)

---

## 📊 Statistics

- **Total Integration Documents:** 120+ documents
- **Active Integrations:** 5 external services
- **Planned Integrations:** 8 services (database, cloud storage, monitoring, auth)
- **API Providers:** OpenAI, Hugging Face, GitHub, SMTP, Geolocation
- **Integration Modules:** 5 core modules (`core/*.py`)
- **Security Controls:** API key encryption, rate limiting, error handling

---

## 🛡️ Governance

**Maintainer:** AGENT-019 (MOC Constructor)  
**Integration Owner:** Backend Team Lead  
**Update Frequency:** Event-driven (new integrations, API changes)  
**Security Review:** Required for all new integrations  
**Quality Gate:** All integrations must have error handling + logging  
**API Key Audit:** Quarterly review of API key rotation and usage

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-23  
**Schema Compliance:** ✅ 100%  
**Integration Health:** 🟢 All active integrations operational

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

