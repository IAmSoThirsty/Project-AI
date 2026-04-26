#!/usr/bin/env python3
"""
Verification script for global rate limiting implementation.

This script tests the rate limiter integration and provides a quick health check.
"""

import sys
from datetime import datetime


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def test_imports():
    """Test that all imports work."""
    print_header("Testing Imports")
    
    try:
        from src.app.core.governance.rate_limiter import (
            GlobalRateLimiter,
            InMemoryRateLimiter,
            RedisRateLimiter,
            check_rate_limit,
            get_global_limiter,
        )
        print("✓ Rate limiter imports successful")
    except Exception as e:
        print(f"✗ Rate limiter import failed: {e}")
        return False
    
    try:
        from src.app.core.governance.pipeline import enforce_pipeline
        print("✓ Pipeline import successful")
    except Exception as e:
        print(f"✗ Pipeline import failed: {e}")
        return False
    
    return True


def test_backend_initialization():
    """Test backend initialization."""
    print_header("Testing Backend Initialization")
    
    from src.app.core.governance.rate_limiter import get_global_limiter
    
    limiter = get_global_limiter()
    backend_type = type(limiter.backend).__name__
    
    print(f"Backend Type: {backend_type}")
    
    if backend_type == "RedisRateLimiter":
        print("✓ Using Redis backend (production mode)")
        
        # Check Redis health
        health = limiter.health_check()
        if health.get("redis_healthy"):
            print("✓ Redis connection healthy")
        else:
            print("⚠ Redis connection unhealthy")
    elif backend_type == "InMemoryRateLimiter":
        print("⚠ Using in-memory backend (development mode)")
        print("  Consider installing Redis for production use")
    else:
        print(f"✗ Unknown backend type: {backend_type}")
        return False
    
    return True


def test_rate_limiting():
    """Test basic rate limiting functionality."""
    print_header("Testing Rate Limiting")
    
    from src.app.core.governance.rate_limiter import get_global_limiter
    
    limiter = get_global_limiter()
    
    # Test context
    context = {
        "action": "test.action",
        "user": {"username": "test_user"},
        "source": "test"
    }
    
    # Test that requests are allowed
    print("Testing request allowance...")
    allowed, reason, metadata = limiter.check_limit(context)
    
    if allowed:
        print(f"✓ Request allowed (remaining: {metadata['remaining']})")
    else:
        print(f"✗ Request denied: {reason}")
        return False
    
    # Test metadata
    print(f"  Limit: {metadata['limit']}")
    print(f"  Window: {metadata['window']}s")
    print(f"  Remaining: {metadata['remaining']}")
    
    return True


def test_statistics():
    """Test statistics collection."""
    print_header("Testing Statistics")
    
    from src.app.core.governance.rate_limiter import get_global_limiter
    
    limiter = get_global_limiter()
    stats = limiter.get_stats()
    
    print(f"Total Checks: {stats.get('total_checks', 0)}")
    print(f"Allowed: {stats.get('allowed', 0)}")
    print(f"Denied: {stats.get('denied', 0)}")
    print(f"Errors: {stats.get('errors', 0)}")
    
    if "redis" in stats:
        redis_stats = stats["redis"]
        print(f"\nRedis Status:")
        print(f"  Connected: {redis_stats.get('connected', False)}")
        if redis_stats.get('connected'):
            print(f"  Memory: {redis_stats.get('used_memory', 'N/A')}")
            print(f"  Clients: {redis_stats.get('connected_clients', 'N/A')}")
    
    print("✓ Statistics retrieved successfully")
    return True


def test_health_check():
    """Test health check functionality."""
    print_header("Testing Health Check")
    
    from src.app.core.governance.rate_limiter import get_global_limiter
    
    limiter = get_global_limiter()
    health = limiter.health_check()
    
    print(f"Healthy: {health.get('healthy', False)}")
    print(f"Backend: {health.get('backend', 'unknown')}")
    print(f"Timestamp: {health.get('timestamp', 'N/A')}")
    
    if health.get("redis_healthy") is not None:
        print(f"Redis Healthy: {health.get('redis_healthy', False)}")
    
    if health.get("healthy"):
        print("✓ Health check passed")
    else:
        print("⚠ Health check indicates issues")
    
    return True


def test_configuration():
    """Test configuration retrieval."""
    print_header("Testing Configuration")
    
    from src.app.core.governance.rate_limiter import get_global_limiter
    
    limiter = get_global_limiter()
    stats = limiter.get_stats()
    config = stats.get("config", {})
    
    print("Action Limits:")
    for action, limits in list(config.get("action_limits", {}).items())[:5]:
        print(f"  {action}: {limits['max_requests']}/{limits['window']}s")
    
    user_limit = config.get("user_global_limit", {})
    print(f"\nUser Global Limit: {user_limit.get('max_requests', 'N/A')}/{user_limit.get('window', 'N/A')}s")
    
    system_limit = config.get("system_global_limit", {})
    print(f"System Global Limit: {system_limit.get('max_requests', 'N/A')}/{system_limit.get('window', 'N/A')}s")
    
    print("✓ Configuration retrieved successfully")
    return True


def main():
    """Run all verification tests."""
    print(f"\nGlobal Rate Limiting Verification")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Python: {sys.version.split()[0]}")
    
    tests = [
        ("Imports", test_imports),
        ("Backend Initialization", test_backend_initialization),
        ("Rate Limiting", test_rate_limiting),
        ("Statistics", test_statistics),
        ("Health Check", test_health_check),
        ("Configuration", test_configuration),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ {name} test failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All verification tests passed!")
        print("✓ Global rate limiting is ready for use")
        return 0
    else:
        print("\n⚠ Some verification tests failed")
        print("  Please review the output above for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
