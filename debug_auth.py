"""Test OpenRouter using OpenAI SDK approach."""
import requests
import json

api_key = "sk-v1-5759e75e76807e09ee7fed4f4fda9064cf8e557e0ce9e24ec5d3845525c68a86"

print("Testing OpenRouter with OpenAI SDK pattern...")

# Try using data=json.dumps() instead of json=payload
payload = {
    'model': 'openrouter/elephant-alpha',
    'messages': [{'role': 'user', 'content': 'Say hello'}],
    'max_tokens': 10
}

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'HTTP-Referer': 'https://localhost',
    'X-OpenRouter-Title': 'Test App'
}

print(f"Headers: {headers}")
print(f"Payload: {payload}")

# Method 1: Using data=json.dumps()
print("\nMethod 1: data=json.dumps()...")
resp1 = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers=headers,
    data=json.dumps(payload)
)

print(f"Status: {resp1.status_code}")
print(f"Response: {resp1.text[:500]}")

# Method 2: Using json=payload
print("\nMethod 2: json=payload...")
resp2 = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers=headers,
    json=payload
)

print(f"Status: {resp2.status_code}")
print(f"Response: {resp2.text[:500]}")

# Method 3: Try without Content-Type header (requests adds it automatically with json=)
print("\nMethod 3: Minimal headers...")
headers_minimal = {
    'Authorization': f'Bearer {api_key}'
}

resp3 = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers=headers_minimal,
    json=payload
)

print(f"Status: {resp3.status_code}")
print(f"Response: {resp3.text[:500]}")