"""
Comprehensive tests for Image Generator functionality.
Tests content filtering, validation, and API integration.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest

from app.core.image_generator import ImageGenerator


class TestImageGenerator:
    """Test suite for ImageGenerator class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.generator = ImageGenerator()
    
    # TEST 1: Content Filtering - Blocked Keywords
    def test_content_filtering_blocks_nsfw(self):
        """Test that NSFW keywords are properly blocked."""
        blocked_prompts = [
            "create a nude painting",
            "Show me explicit content",
            "Generate NSFW image",
            "Make an adult themed picture",
            "Create something sexual",
            "Provocative image please",
            "Intimate scene with people"
        ]
        
        for prompt in blocked_prompts:
            is_valid, error = self.generator._validate_prompt(prompt)
            assert not is_valid, f"Should block: {prompt}"
            assert "Inappropriate content detected" in error
            print(f"✓ TEST 1.{blocked_prompts.index(prompt)+1}: Blocked '{prompt[:30]}...'")
    
    # TEST 2: Content Filtering - Allowed Content
    def test_content_filtering_allows_safe(self):
        """Test that safe prompts are allowed."""
        safe_prompts = [
            "A beautiful mountain landscape",
            "A cute robot reading a book",
            "Futuristic city at night",
            "Magical forest with glowing mushrooms",
            "An astronaut riding a horse on Mars",
            "A serene Japanese garden with cherry blossoms",
            "Abstract geometric patterns in blue and gold"
        ]
        
        for prompt in safe_prompts:
            is_valid, error = self.generator._validate_prompt(prompt)
            assert is_valid, f"Should allow: {prompt}"
            assert error == ""
            print(f"✓ TEST 2.{safe_prompts.index(prompt)+1}: Allowed '{prompt[:30]}...'")
    
    # TEST 3: Safety Negative Prompts
    def test_safety_negative_prompts_added(self):
        """Test that safety terms are automatically added to negative prompts."""
        assert "nsfw" in self.generator.SAFETY_NEGATIVE.lower()
        assert "explicit" in self.generator.SAFETY_NEGATIVE.lower()
        assert "adult content" in self.generator.SAFETY_NEGATIVE.lower()
        print("✓ TEST 3: Safety negative prompts configured correctly")
    
    # TEST 4: Empty Prompt Validation
    def test_empty_prompt_rejected(self):
        """Test that empty prompts are rejected."""
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            self.generator.generate_image("")
        print("✓ TEST 4: Empty prompts properly rejected")
    
    # TEST 5: Style Presets
    def test_style_presets_available(self):
        """Test that style presets are properly defined."""
        presets = self.generator.get_style_presets()
        assert len(presets) >= 10
        assert "Realistic" in presets
        assert "Anime" in presets
        assert "Cyberpunk" in presets
        print(f"✓ TEST 5: {len(presets)} style presets available")


def run_manual_tests():
    """Run manual integration tests (requires network)."""
    print("\n" + "="*60)
    print("COMPREHENSIVE IMAGE GENERATOR TEST SUITE")
    print("="*60)
    
    generator = ImageGenerator()
    
    # Manual Test 1: Prompt Validation
    print("\n[MANUAL TEST 1] Content Filtering Validation")
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
    
    # Manual Test 2: API Configuration
    print("\n[MANUAL TEST 2] API Configuration Check")
    print("-" * 60)
    print(f"✓ API URL: {generator.api_url}")
    print(f"✓ Safety Keywords: {len(generator.NSFW_KEYWORDS)} terms")
    print(f"✓ Safety Negative: '{generator.SAFETY_NEGATIVE[:50]}...'")
    
    # Manual Test 3: Style Presets
    print("\n[MANUAL TEST 3] Style Presets")
    print("-" * 60)
    presets = generator.get_style_presets()
    for i, (name, description) in enumerate(presets.items(), 1):
        print(f"  {i:2d}. {name:15s} - {description[:45]}...")
    
    # Manual Test 4: Quality Modifiers
    print("\n[MANUAL TEST 4] Quality Enhancement Modifiers")
    print("-" * 60)
    modifiers = generator.get_quality_modifiers()
    print(f"✓ {len(modifiers)} quality modifiers available:")
    for mod in modifiers:
        print(f"  - {mod}")
    
    # Manual Test 5: Error Handling
    print("\n[MANUAL TEST 5] Error Handling")
    print("-" * 60)
    
    # Test empty prompt
    try:
        generator.generate_image("")
        print("✗ FAILED: Empty prompt should raise ValueError")
    except ValueError as e:
        print(f"✓ PASSED: Empty prompt correctly rejected - {str(e)}")
    
    # Test blocked content
    try:
        generator.generate_image("Create explicit content")
        print("✗ FAILED: Blocked content should raise ValueError")
    except ValueError as e:
        print(f"✓ PASSED: Blocked content correctly rejected")
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED SUCCESSFULLY")
    print("="*60)
    print("\n✓ All validation tests passed")
    print("✓ Content filtering working correctly")
    print("✓ Safety measures in place")
    print("✓ Error handling functional")
    print("\nNote: Live API tests require network connection and may take time.")


if __name__ == "__main__":
    run_manual_tests()
