#!/usr/bin/env python3
"""
Standalone Legion API Test
Tests the OpenClaw integration endpoints without requiring OpenClaw installation
"""

import json
from datetime import datetime

import requests

API_BASE = "http://localhost:8001"


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_health():
    """Test health endpoint"""
    print_section("Testing Health Endpoint")

    try:
        response = requests.get(f"{API_BASE}/openclaw/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_capabilities():
    """Test capabilities endpoint"""
    print_section("Testing Capabilities Endpoint")

    try:
        response = requests.get(f"{API_BASE}/openclaw/capabilities", timeout=5)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Available Capabilities: {len(data.get('capabilities', []))}")
        print(json.dumps(data, indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_message():
    """Test message processing endpoint"""
    print_section("Testing Message Endpoint")

    message_data = {
        "content": "What is your threat status?",
        "sender": "test_user",
        "platform": "openclaw",
        "timestamp": datetime.now().isoformat(),
    }

    try:
        response = requests.post(
            f"{API_BASE}/openclaw/message", json=message_data, timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Request: {json.dumps(message_data, indent=2)}")
        print(f"\nResponse: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_status():
    """Test status endpoint"""
    print_section("Testing Status Endpoint")

    try:
        response = requests.get(f"{API_BASE}/openclaw/status", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print_section("Legion API Standalone Test Suite")
    print(f"Target: {API_BASE}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n⚠️  Make sure the Legion API is running:")
    print("   python scripts/start_api.py")
    print("\nPress Enter to start tests...")
    input()

    results = {
        "Health Check": test_health(),
        "Capabilities": test_capabilities(),
        "Message Processing": test_message(),
        "Status": test_status(),
    }

    print_section("Test Results Summary")

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {test_name}")

    total = len(results)
    passed = sum(results.values())

    print(f"\n{'='*60}")
    print(f"Total: {passed}/{total} tests passed")
    print(f"{'='*60}\n")

    if passed == total:
        print("🎉 All tests passed! Legion API is ready for OpenClaw integration.")
    else:
        print("⚠️  Some tests failed. Check the API server logs.")


if __name__ == "__main__":
    main()
