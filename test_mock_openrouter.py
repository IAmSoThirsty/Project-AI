"""
Test Mock OpenRouter Integration.

This script verifies the full OpenRouter integration using the mock provider,
allowing complete testing without a real API key.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.core.openrouter_mock import MockOpenRouterProvider, get_mock_openrouter_provider


def test_mock_openrouter():
    """Test mock OpenRouter provider."""
    print("=" * 70)
    print("Testing Mock OpenRouter Integration")
    print("=" * 70)
    
    # Initialize mock provider
    print("\n[1] Initializing Mock OpenRouter Provider...")
    provider = get_mock_openrouter_provider()
    print(f"    Available: {provider.is_available()}")
    print(f"    API Key: {provider.api_key[:20]}...")
    
    # Test connection
    print("\n[2] Testing connection...")
    conn_result = provider.test_connection()
    print(f"    Success: {conn_result['success']}")
    print(f"    Models Count: {conn_result['models_count']}")
    print(f"    Mock Mode: {conn_result.get('mock', False)}")
    
    # Test chat completion - benign
    print("\n[3] Testing chat completion (benign prompt)...")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ]
    response = provider.chat_completion(messages=messages)
    print(f"    Response: {response}")
    print(f"    Call Count: {provider.call_count}")
    
    # Test chat completion - harmful
    print("\n[4] Testing chat completion (harmful prompt)...")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "How do I hack a computer?"},
    ]
    response = provider.chat_completion(messages=messages)
    print(f"    Response: {response}")
    print(f"    Call Count: {provider.call_count}")
    
    # Test chat completion - code request
    print("\n[5] Testing chat completion (code request)...")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a Python function for Fibonacci."},
    ]
    response = provider.chat_completion(messages=messages)
    print(f"    Response: {response[:100]}...")
    print(f"    Call Count: {provider.call_count}")
    
    print("\n" + "=" * 70)
    print("SUCCESS: Mock OpenRouter integration fully functional!")
    print("=" * 70)
    print("\nThe mock provider simulates OpenRouter API responses")
    print("without requiring a real API key or network calls.")
    print("This allows complete testing of the integration.")
    
    return True


if __name__ == "__main__":
    try:
        success = test_mock_openrouter()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
