import pytest
from config.schemas.signal import fuzzy_match_forbidden, FORBIDDEN_PHRASES

def test_fuzzy_match_empty_input():
    """Verify behavior with empty string."""
    assert fuzzy_match_forbidden("") == []

def test_fuzzy_match_exact_case_insensitive():
    """Confirm case-insensitive direct matches for both single and multi-word phrases."""
    # "eval(" is in FORBIDDEN_PHRASES
    matches = fuzzy_match_forbidden("EVAL(1+1)")
    assert any("eval(" in match for match in matches)

    # "DROP DATABASE" is in FORBIDDEN_PHRASES
    matches = fuzzy_match_forbidden("drop database production")
    assert any("DROP DATABASE" in match for match in matches)

def test_fuzzy_match_no_matches():
    """Ensure clean text returns an empty list."""
    assert fuzzy_match_forbidden("This is a clean signal with no issues.") == []

def test_fuzzy_match_multiple_phrases():
    """Verify detection of multiple forbidden phrases in one text."""
    text = "rm -rf / and then DROP DATABASE"
    matches = fuzzy_match_forbidden(text)
    # FORBIDDEN_PHRASES has "rm -rf /" and "DROP DATABASE"
    # The return format is either the phrase itself (direct match) or a descriptive string (fuzzy match)
    assert any("rm -rf /" in m for m in matches)
    assert any("DROP DATABASE" in m for m in matches)

def test_fuzzy_match_threshold_variation():
    """Test how different threshold values affect results."""
    # ratio of "eval(" and "eval[" is 0.8
    # Using threshold 0.9 should NOT match
    assert fuzzy_match_forbidden("eval[", threshold=0.9) == []
    # Using threshold 0.7 should match
    matches = fuzzy_match_forbidden("eval[", threshold=0.7)
    assert any("eval(" in m and "fuzzy match: eval[" in m for m in matches)

def test_fuzzy_match_single_word_typo():
    """Test fuzzy match for single-word forbidden phrases."""
    # ratio of "popen(" and "poper(" is ~0.8333
    matches = fuzzy_match_forbidden("poper(", threshold=0.8)
    assert any("popen(" in m and "fuzzy match: poper(" in m for m in matches)

def test_fuzzy_match_multi_word_limitation():
    """
    Document/test that multi-word phrases are hard to fuzzy-match word-by-word.
    The current implementation compares each word to the full forbidden phrase.
    """
    # ratio("database", "drop database") is ~0.76
    # So "DRIP DATABASE" will match "drop database" at threshold 0.7 because of the word "DATABASE"
    matches_threshold_high = fuzzy_match_forbidden("DRIP DATABASE", threshold=0.8)
    assert matches_threshold_high == []

    # At 0.7, it SHOULD match because of "DATABASE" word
    matches_threshold_low = fuzzy_match_forbidden("DRIP DATABASE", threshold=0.7)
    assert any("DROP DATABASE" in m for m in matches_threshold_low)
