"""
Test OpenRouter API connectivity.
"""
import requests
import os

# Load API key from .env
api_key = os.getenv('OPENROUTER_API_KEY')
if not api_key:
    # Try reading from .env file
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith('OPENROUTER_API_KEY='):
                    api_key = line.strip().split('=')[1]
                    break

print(f"API Key loaded: {api_key[:20]}...")

# Test models endpoint
print("\nTesting OpenRouter API...")
resp = requests.get(
    'https://openrouter.ai/api/v1/models',
    headers={'Authorization': f'Bearer {api_key}'}
)

print(f"Status Code: {resp.status_code}")

if resp.status_code == 200:
    models = resp.json().get('data', [])
    print(f"Success! {len(models)} models available")
    print("\nFirst 5 models:")
    for model in models[:5]:
        model_id = model.get('id', 'unknown')
        print(f"  - {model_id}")
else:
    print(f"Error: {resp.status_code}")
    print(resp.text[:500])

# Test a simple completion - use chat/completions endpoint
print("\n\nTesting chat completion endpoint...")
test_payload = {
    'model': 'openai/gpt-3.5-turbo',
    'messages': [{'role': 'user', 'content': 'Say hello'}],
    'max_tokens': 10
}

print(f"Headers being sent: Authorization: Bearer {api_key[:20]}...")

resp2 = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    },
    json=test_payload
)

print(f"Completion Status: {resp2.status_code}")
if resp2.status_code == 200:
    result = resp2.json()
    choice = result.get('choices', [{}])[0]
    message = choice.get('message', {})
    print(f"Response: {message.get('content', 'N/A')}")
else:
    print(f"Error: {resp2.status_code}")
    print(resp2.text[:500])