"""
Comprehensive tests for Image Generator functionality - NO DEPENDENCIES.
Tests content filtering, validation, and API integration.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.core.image_generator import ImageGenerator


def test_content_filtering_blocks_nsfw():
    """Test that NSFW keywords are properly blocked."""
    generator = ImageGenerator()
    blocked_prompts = [
        "create a nude painting",
        "Show me explicit content",
        "Generate NSFW image",
        "Make an adult themed picture",
        "Create something sexual",
        "Provocative image please",
        "Intimate scene with people"
    ]
    
    passed = 0
    for i, prompt in enumerate(blocked_prompts, 1):
        is_valid, error = generator._validate_prompt(prompt)
        if not is_valid and "Inappropriate content detected" in error:
            print(f"✓ TEST 1.{i}: Blocked '{prompt[:30]}...'")
            passed += 1
        else:
            print(f"✗ FAILED: Should block '{prompt}'")
    
    return passed == len(blocked_prompts)


def test_content_filtering_allows_safe():
    """Test that safe prompts are allowed."""
    generator = ImageGenerator()
    safe_prompts = [
        "A beautiful mountain landscape",
        "A cute robot reading a book",
        "Futuristic city at night",
        "Magical forest with glowing mushrooms",
        "An astronaut riding a horse on Mars",
        "A serene Japanese garden with cherry blossoms",
        "Abstract geometric patterns in blue and gold"
    ]
    
    passed = 0
    for i, prompt in enumerate(safe_prompts, 1):
        is_valid, error = generator._validate_prompt(prompt)
        if is_valid and error == "":
            print(f"✓ TEST 2.{i}: Allowed '{prompt[:30]}...'")
            passed += 1
        else:
            print(f"✗ FAILED: Should allow '{prompt}'")
    
    return passed == len(safe_prompts)


def test_safety_negative_prompts_added():
    """Test that safety terms are automatically added to negative prompts."""
    generator = ImageGenerator()
    safety = generator.SAFETY_NEGATIVE.lower()
    checks = ["nsfw" in safety, "explicit" in safety, "adult content" in safety]
    
    if all(checks):
        print("✓ TEST 3: Safety negative prompts configured correctly")
        return True
    else:
        print("✗ FAILED: Safety prompts not properly configured")
        return False


def test_empty_prompt_rejected():
    """Test that empty prompts are rejected."""
    generator = ImageGenerator()
    try:
        generator.generate_image("")
        print("✗ FAILED: Empty prompt should raise ValueError")
        return False
    except ValueError as e:
        if "Prompt cannot be empty" in str(e):
            print("✓ TEST 4: Empty prompts properly rejected")
            return True
        else:
            print(f"✗ FAILED: Wrong error message: {e}")
            return False


def test_style_presets_available():
    """Test that style presets are properly defined."""
    generator = ImageGenerator()
    presets = generator.get_style_presets()
    required = ["Realistic", "Anime", "Cyberpunk"]
    
    if len(presets) >= 10 and all(r in presets for r in required):
        print(f"✓ TEST 5: {len(presets)} style presets available")
        return True
    else:
        print(f"✗ FAILED: Only {len(presets)} presets found")
        return False


def run_manual_tests():
    """Run manual integration tests."""
    print("\n" + "="*60)
    print("COMPREHENSIVE IMAGE GENERATOR TEST SUITE")
    print("="*60)
    
    generator = ImageGenerator()
    
    # Manual Test: Prompt Validation Details
    print("\n[DETAILED TEST] Content Filtering Validation")
    print("-" * 60)
    test_prompts = {
        "safe": [
            "A peaceful mountain landscape",
            "A cute puppy playing",
            "Abstract art with colors"
        ],
        "blocked": [
            "Create explicit art",
            "Show me nude painting",
            "Generate nsfw content"
        ]
    }
    
    for category, prompts in test_prompts.items():
        print(f"\nTesting {category.upper()} prompts:")
        for prompt in prompts:
            is_valid, error = generator._validate_prompt(prompt)
            status = "✓ ALLOWED" if is_valid else "✗ BLOCKED"
            print(f"  {status}: '{prompt[:40]}...'")
            if error:
                print(f"           Reason: {error[:60]}...")
    
    # API Configuration Check
    print("\n[CONFIG CHECK] API Configuration")
    print("-" * 60)
    print(f"✓ API URL: {generator.api_url}")
    print(f"✓ Safety Keywords: {len(generator.NSFW_KEYWORDS)} terms")
    print(f"✓ Safety Negative: '{generator.SAFETY_NEGATIVE[:50]}...'")
    
    # Style Presets Check
    print("\n[PRESETS CHECK] Style Presets")
    print("-" * 60)
    presets = generator.get_style_presets()
    for i, (name, description) in enumerate(presets.items(), 1):
        print(f"  {i:2d}. {name:15s} - {description[:45]}...")
    
    # Quality Modifiers Check
    print("\n[QUALITY CHECK] Enhancement Modifiers")
    print("-" * 60)
    modifiers = generator.get_quality_modifiers()
    print(f"✓ {len(modifiers)} quality modifiers available:")
    for mod in modifiers:
        print(f"  - {mod}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    print("\n🔍 Running Test Suite...")
    print("="*60)
    
    results = []
    test_functions = [
        ("Content Filtering - Blocked Keywords", test_content_filtering_blocks_nsfw),
        ("Content Filtering - Safe Content", test_content_filtering_allows_safe),
        ("Safety Negative Prompts", test_safety_negative_prompts_added),
        ("Empty Prompt Rejection", test_empty_prompt_rejected),
        ("Style Presets Availability", test_style_presets_available),
    ]
    
    for name, func in test_functions:
        print(f"\n[TEST: {name}]")
        print("-" * 60)
        try:
            result = func()
            results.append(result)
        except Exception as e:
            print(f"✗ EXCEPTION: {e}")
            results.append(False)
    
    # Run detailed manual tests
    run_manual_tests()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n⚠️ {total - passed} TEST(S) FAILED")
    
    print("="*60)
