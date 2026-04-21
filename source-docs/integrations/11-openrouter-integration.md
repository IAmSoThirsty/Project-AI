# OpenRouter API Integration

## Overview
OpenRouterProvider (src/app/core/openrouter_provider.py) integrates with OpenRouter's unified LLM API, providing access to models from multiple providers through a single interface.

## Supported Models
- OpenAI: gpt-4, gpt-3.5-turbo
- Anthropic: claude-3-opus, claude-3-sonnet
- Google: gemini-pro
- Meta: llama-2-70b
- Mistral: mistral-medium

## Configuration
`ash
OPENROUTER_API_KEY=sk-or-v1-...  # From https://openrouter.ai/keys
`

## Implementation
`python
# src/app/core/openrouter_provider.py
import openai

class OpenRouterProvider:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        
        if self.api_key:
            self._client = openai.OpenAI(
                api_key=self.api_key,
                base_url='https://openrouter.ai/api/v1'
            )
    
    def chat_completion(
        self,
        messages: list[dict],
        model: str = 'openai/gpt-3.5-turbo',
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers={
                'HTTP-Referer': 'https://project-ai.local',
                'X-Title': 'Project-AI'
            },
            **kwargs
        )
        return response.choices[0].message.content
`

## Usage
`python
from app.core.openrouter_provider import OpenRouterProvider

provider = OpenRouterProvider()

# Chat with Claude 3 Opus
response = provider.chat_completion(
    messages=[{'role': 'user', 'content': 'Explain quantum computing'}],
    model='anthropic/claude-3-opus'
)

# Chat with GPT-4
response = provider.chat_completion(
    messages=[{'role': 'user', 'content': 'What is AI?'}],
    model='openai/gpt-4'
)
`

## References
- OpenRouter: https://openrouter.ai
- Model list: https://openrouter.ai/models


---

## Related Documentation

- **Relationship Map**: [[relationships\integrations\README.md]]
