# Perplexity API Integration

## Overview
Perplexity AI provides web-enhanced language models with real-time search capabilities, serving as a tertiary fallback provider in the AI orchestrator.

## Models
- pplx-70b-online: Web-enhanced 70B parameter model
- pplx-7b-online: Faster 7B parameter model with search

## Configuration
`ash
PERPLEXITY_API_KEY=pplx-...  # From https://www.perplexity.ai/settings/api
`

## Implementation (via AI Orchestrator)
`python
# src/app/core/ai/orchestrator.py
def _call_perplexity(request: AIRequest) -> AIResponse:
    import requests
    
    url = 'https://api.perplexity.ai/chat/completions'
    headers = {
        'Authorization': f\"Bearer {os.getenv('PERPLEXITY_API_KEY')}\",
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': request.model or 'pplx-70b-online',
        'messages': [{'role': 'user', 'content': request.prompt}],
        **(request.config or {})
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    return AIResponse(
        status='success',
        result=data['choices'][0]['message']['content'],
        provider_used='perplexity',
        metadata={'model': data['model'], 'citations': data.get('citations', [])}
    )
`

## Usage
`python
from app.core.ai.orchestrator import run_ai, AIRequest

# Perplexity provides web-enhanced responses with citations
request = AIRequest(
    task_type='chat',
    prompt='What are the latest developments in quantum computing?',
    provider='perplexity',
    model='pplx-70b-online'
)

response = run_ai(request)
print(response.result)
print(f\"Citations: {response.metadata.get('citations', [])}\")
`

## References
- Perplexity API: https://docs.perplexity.ai


---

## Related Documentation

- **12 Email Integration**: [[relationships\integrations\12-email-integration.md]]


- **Relationship Map**: [[relationships\integrations\README.md]]
